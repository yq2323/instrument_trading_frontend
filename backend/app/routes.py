from flask import Blueprint, request, jsonify, render_template, send_from_directory
from flask_login import login_required, current_user
from sqlalchemy import desc, asc, or_
from datetime import datetime, timedelta
import os

from . import db
from .models import User, Category, Instrument, InstrumentImage, Favorite, Cart, Order
from .utils import save_uploaded_file, allowed_file

main_bp = Blueprint('main', __name__)

# ========== 首页和静态页面 ==========
@main_bp.route('/')
def index():
    """首页"""
    return jsonify({
        'message': '欢迎使用校园二手乐器交易平台 API',
        'success': True,
        'endpoints': {
            'categories': '/api/categories',
            'instruments': '/api/instruments',
            'auth': '/api/auth'
        }
    })

@main_bp.route('/')
def api_index():
    """API首页"""
    return jsonify({
        'name': '校园二手乐器交易平台 API',
        'version': '1.0.0',
        'endpoints': {
            'auth': ['/api/auth/register', '/api/auth/login', '/api/auth/logout'],
            'instruments': ['/api/instruments', '/api/instruments/<id>'],
            'categories': '/api/categories',
            'users': '/api/users/profile',
            'orders': '/api/orders',
            'cart': '/api/cart'
        }
    })

# ========== 分类相关API ==========
@main_bp.route('/categories', methods=['GET'])
def get_categories():
    """获取所有分类"""
    categories = Category.query.order_by(Category.sort_order, Category.name).all()
    return jsonify({
        'success': True,
        'categories': [cat.to_dict() for cat in categories]
    })

# ========== 乐器相关API ==========
@main_bp.route('/instruments', methods=['GET'])
def get_instruments():
    """获取乐器列表（支持分页、搜索、筛选）"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 12, type=int)
    keyword = request.args.get('keyword', '').strip()
    category_id = request.args.get('category_id', type=int)
    condition = request.args.get('condition')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')
    
    # 构建查询
    query = Instrument.query.filter_by(status='available')
    
    # 搜索条件
    if keyword:
        query = query.filter(
            or_(
                Instrument.title.ilike(f'%{keyword}%'),
                Instrument.description.ilike(f'%{keyword}%'),
                Instrument.brand.ilike(f'%{keyword}%'),
                Instrument.model.ilike(f'%{keyword}%')
            )
        )
    
    # 筛选条件
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    if condition:
        query = query.filter_by(instrument_condition=condition)
    
    if min_price is not None:
        query = query.filter(Instrument.price >= min_price)
    
    if max_price is not None:
        query = query.filter(Instrument.price <= max_price)
    
    # 排序
    sort_column = getattr(Instrument, sort_by, Instrument.created_at)
    if sort_order == 'asc':
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))
    
    # 分页
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)
    
    instruments = pagination.items
    
    return jsonify({
        'success': True,
        'instruments': [inst.to_dict() for inst in instruments],
        'pagination': {
            'page': pagination.page,
            'page_size': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    })

@main_bp.route('/instruments/hot', methods=['GET'])
def get_hot_instruments():
    """获取热门乐器"""
    limit = request.args.get('limit', 6, type=int)
    
    # 获取最近7天的热门乐器（浏览量+收藏数）
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    
    instruments = Instrument.query.filter(
        Instrument.status == 'available',
        Instrument.created_at >= seven_days_ago
    ).order_by(
        desc(Instrument.view_count + Instrument.favorite_count * 2)
    ).limit(limit).all()
    
    return jsonify({
        'success': True,
        'instruments': [inst.to_dict() for inst in instruments]
    })

@main_bp.route('/instruments/<int:instrument_id>', methods=['GET'])
def get_instrument_detail(instrument_id):
    """获取乐器详情"""
    instrument = Instrument.query.get_or_404(instrument_id)
    
    # 增加浏览次数
    instrument.increment_view_count()
    
    # 记录浏览历史（如果用户已登录）
    if current_user.is_authenticated:
        from .models import ViewHistory
        history = ViewHistory(
            user_id=current_user.id,
            instrument_id=instrument_id
        )
        db.session.add(history)
        db.session.commit()
    
    # 检查是否收藏
    is_favorited = False
    if current_user.is_authenticated:
        is_favorited = Favorite.query.filter_by(
            user_id=current_user.id,
            instrument_id=instrument_id
        ).first() is not None
    
    result = instrument.to_dict()
    result['is_favorited'] = is_favorited
    
    return jsonify({
        'success': True,
        'instrument': result
    })

@main_bp.route('/instruments', methods=['POST'])
@login_required
def create_instrument():
    """发布新乐器"""
    data = request.form
    
    # 验证必填字段
    title = data.get('title', '').strip()
    description = data.get('description', '').strip()
    price = data.get('price', '').strip()
    category_id = data.get('category_id', '').strip()
    
    if not all([title, description, price, category_id]):
        return jsonify({'success': False, 'message': '请填写所有必填字段'}), 400
    
    try:
        price = float(price)
        if price <= 0:
            return jsonify({'success': False, 'message': '价格必须大于0'}), 400
    except ValueError:
        return jsonify({'success': False, 'message': '价格格式不正确'}), 400
    
    # 创建乐器
    instrument = Instrument(
        title=title,
        description=description,
        price=price,
        original_price=data.get('original_price'),
        category_id=int(category_id),
        user_id=current_user.id,
        condition=data.get('condition', 'good'),
        brand=data.get('brand', '').strip(),
        model=data.get('model', '').strip(),
        location=data.get('location', '').strip()
    )
    
    db.session.add(instrument)
    db.session.flush()  # 获取instrument.id
    
    # 处理图片上传
    images = request.files.getlist('images')
    main_image_index = int(data.get('main_image_index', 0))
    
    for i, image_file in enumerate(images):
        if image_file and allowed_file(image_file.filename):
            filename = save_uploaded_file(image_file, 'instruments')
            if filename:
                instrument_image = InstrumentImage(
                    instrument_id=instrument.id,
                    image_url=filename,
                    is_main=(i == main_image_index)
                )
                db.session.add(instrument_image)
    
    # 处理音频上传
    audio_file = request.files.get('audio')
    if audio_file and allowed_file(audio_file.filename, {'mp3', 'wav'}):
        filename = save_uploaded_file(audio_file, 'audios')
        if filename:
            instrument.audio_url = filename
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '乐器发布成功',
        'instrument_id': instrument.id
    })

@main_bp.route('/instruments/<int:instrument_id>', methods=['PUT'])
@login_required
def update_instrument(instrument_id):
    """更新乐器信息"""
    instrument = Instrument.query.get_or_404(instrument_id)
    
    # 检查权限
    if instrument.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'success': False, 'message': '无权修改此乐器'}), 403
    
    data = request.form
    
    # 更新字段
    if 'title' in data:
        instrument.title = data['title'].strip()
    if 'description' in data:
        instrument.description = data['description'].strip()
    if 'price' in data:
        try:
            instrument.price = float(data['price'])
        except ValueError:
            pass
    if 'condition' in data:
        instrument.condition = data['condition']
    if 'brand' in data:
        instrument.brand = data['brand'].strip()
    if 'model' in data:
        instrument.model = data['model'].strip()
    if 'location' in data:
        instrument.location = data['location'].strip()
    if 'status' in data and current_user.is_admin:
        instrument.status = data['status']
    
    # 处理新图片
    images = request.files.getlist('images')
    if images and any(img.filename for img in images):
        # 删除旧图片
        InstrumentImage.query.filter_by(instrument_id=instrument_id).delete()
        
        for i, image_file in enumerate(images):
            if image_file and allowed_file(image_file.filename):
                filename = save_uploaded_file(image_file, 'instruments')
                if filename:
                    instrument_image = InstrumentImage(
                        instrument_id=instrument.id,
                        image_url=filename,
                        is_main=(i == 0)  # 第一张为主图
                    )
                    db.session.add(instrument_image)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '乐器信息更新成功'
    })

@main_bp.route('/instruments/<int:instrument_id>', methods=['DELETE'])
@login_required
def delete_instrument(instrument_id):
    """删除乐器"""
    instrument = Instrument.query.get_or_404(instrument_id)
    
    # 检查权限
    if instrument.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'success': False, 'message': '无权删除此乐器'}), 403
    
    # 标记为已下架（软删除）
    instrument.status = 'removed'
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '乐器已下架'
    })

# ========== 收藏相关API ==========
@main_bp.route('/instruments/<int:instrument_id>/favorite', methods=['POST'])
@login_required
def toggle_favorite(instrument_id):
    """收藏/取消收藏乐器"""
    instrument = Instrument.query.get_or_404(instrument_id)
    
    # 检查乐器状态
    if instrument.status != 'available':
        return jsonify({'success': False, 'message': '该乐器不可用'}), 400
    
    favorite = Favorite.query.filter_by(
        user_id=current_user.id,
        instrument_id=instrument_id
    ).first()
    
    if favorite:
        # 取消收藏
        db.session.delete(favorite)
        instrument.favorite_count = max(0, instrument.favorite_count - 1)
        is_favorited = False
        message = '已取消收藏'
    else:
        # 添加收藏
        favorite = Favorite(
            user_id=current_user.id,
            instrument_id=instrument_id
        )
        db.session.add(favorite)
        instrument.favorite_count += 1
        is_favorited = True
        message = '收藏成功'
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': message,
        'is_favorited': is_favorited,
        'favorite_count': instrument.favorite_count
    })

@main_bp.route('/users/favorites', methods=['GET'])
@login_required
def get_user_favorites():
    """获取用户的收藏列表"""
    favorites = Favorite.query.filter_by(user_id=current_user.id).all()
    
    instruments = []
    for fav in favorites:
        if fav.instrument and fav.instrument.status == 'available':
            instruments.append(fav.instrument.to_dict())
    
    return jsonify({
        'success': True,
        'instruments': instruments
    })

# ========== 购物车相关API ==========
@main_bp.route('/cart', methods=['GET'])
@login_required
def get_cart():
    """获取购物车"""
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    
    total_price = 0
    items = []
    
    for item in cart_items:
        if item.instrument and item.instrument.status == 'available':
            instrument_data = item.instrument.to_dict()
            item_total = instrument_data['price'] * item.quantity
            total_price += item_total
            
            items.append({
                'id': item.id,
                'instrument': instrument_data,
                'quantity': item.quantity,
                'item_total': item_total
            })
    
    return jsonify({
        'success': True,
        'items': items,
        'total_price': total_price,
        'item_count': len(items)
    })

@main_bp.route('/cart/add', methods=['POST'])
@login_required
def add_to_cart():
    """添加到购物车"""
    data = request.get_json()
    instrument_id = data.get('instrument_id')
    quantity = data.get('quantity', 1)
    
    if not instrument_id:
        return jsonify({'success': False, 'message': '请选择乐器'}), 400
    
    instrument = Instrument.query.get_or_404(instrument_id)
    
    # 检查乐器状态
    if instrument.status != 'available':
        return jsonify({'success': False, 'message': '该乐器不可用'}), 400
    
    # 检查是否是自己的乐器
    if instrument.user_id == current_user.id:
        return jsonify({'success': False, 'message': '不能购买自己的乐器'}), 400
    
    # 检查是否已在购物车
    cart_item = Cart.query.filter_by(
        user_id=current_user.id,
        instrument_id=instrument_id
    ).first()
    
    if cart_item:
        cart_item.quantity += quantity
        message = '购物车数量已更新'
    else:
        cart_item = Cart(
            user_id=current_user.id,
            instrument_id=instrument_id,
            quantity=quantity
        )
        db.session.add(cart_item)
        message = '已添加到购物车'
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': message,
        'cart_item_id': cart_item.id
    })

@main_bp.route('/cart/<int:item_id>', methods=['DELETE'])
@login_required
def remove_from_cart(item_id):
    """从购物车移除"""
    cart_item = Cart.query.get_or_404(item_id)
    
    # 检查权限
    if cart_item.user_id != current_user.id:
        return jsonify({'success': False, 'message': '无权操作'}), 403
    
    db.session.delete(cart_item)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '已从购物车移除'
    })

# ========== 订单相关API ==========
@main_bp.route('/orders', methods=['POST'])
@login_required
def create_order():
    """创建订单"""
    data = request.get_json()
    instrument_id = data.get('instrument_id')
    quantity = data.get('quantity', 1)
    
    if not instrument_id:
        return jsonify({'success': False, 'message': '请选择乐器'}), 400
    
    instrument = Instrument.query.get_or_404(instrument_id)
    
    # 检查乐器状态
    if instrument.status != 'available':
        return jsonify({'success': False, 'message': '该乐器不可用'}), 400
    
    # 检查是否是自己的乐器
    if instrument.user_id == current_user.id:
        return jsonify({'success': False, 'message': '不能购买自己的乐器'}), 400
    
    # 计算总价
    total_price = float(instrument.price) * quantity
    
    # 创建订单
    order = Order(
        instrument_id=instrument_id,
        buyer_id=current_user.id,
        seller_id=instrument.user_id,
        total_price=total_price,
        meeting_time=data.get('meeting_time'),
        meeting_place=data.get('meeting_place')
    )
    
    # 更新乐器状态
    instrument.status = 'pending'
    
    # 从购物车移除（如果存在）
    cart_item = Cart.query.filter_by(
        user_id=current_user.id,
        instrument_id=instrument_id
    ).first()
    if cart_item:
        db.session.delete(cart_item)
    
    db.session.add(order)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '订单创建成功',
        'order_id': order.id
    })

@main_bp.route('/orders', methods=['GET'])
@login_required
def get_user_orders():
    """获取用户订单"""
    # 作为买家
    orders_as_buyer = Order.query.filter_by(buyer_id=current_user.id).all()
    # 作为卖家
    orders_as_seller = Order.query.filter_by(seller_id=current_user.id).all()
    
    orders = []
    for order in orders_as_buyer + orders_as_seller:
        orders.append(order.to_dict())
    
    return jsonify({
        'success': True,
        'orders': orders
    })

@main_bp.route('/orders/<order_id>', methods=['PUT'])
@login_required
def update_order_status(order_id):
    """更新订单状态"""
    order = Order.query.get_or_404(order_id)
    
    # 检查权限（只有买卖双方可以更新）
    if order.buyer_id != current_user.id and order.seller_id != current_user.id:
        return jsonify({'success': False, 'message': '无权操作此订单'}), 403
    
    data = request.get_json()
    new_status = data.get('status')
    
    if not new_status:
        return jsonify({'success': False, 'message': '请提供状态'}), 400
    
    # 验证状态转换
    valid_transitions = {
        'pending': ['paid', 'cancelled'],
        'paid': ['shipped', 'cancelled'],
        'shipped': ['completed'],
        'completed': [],
        'cancelled': []
    }
    
    if new_status not in valid_transitions.get(order.status, []):
        return jsonify({'success': False, 'message': '无效的状态转换'}), 400
    
    # 更新状态
    order.status = new_status
    
    # 如果订单完成或取消，恢复乐器状态
    if new_status in ['completed', 'cancelled']:
        instrument = order.instrument
        instrument.status = 'sold' if new_status == 'completed' else 'available'
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '订单状态已更新'
    })

# ========== 用户相关API ==========
@main_bp.route('/users/profile', methods=['GET'])
@login_required
def get_user_profile():
    """获取用户资料"""
    return jsonify({
        'success': True,
        'user': {
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
            'phone': current_user.phone,
            'real_name': current_user.real_name,
            'student_id': current_user.student_id,
            'avatar': current_user.get_avatar_url(),
            'role': current_user.role,
            'credit_score': current_user.credit_score,
            'is_verified': current_user.is_verified,
            'created_at': current_user.created_at.isoformat() if current_user.created_at else None
        }
    })

@main_bp.route('/users/instruments', methods=['GET'])
@login_required
def get_user_instruments():
    """获取用户发布的乐器"""
    instruments = Instrument.query.filter_by(user_id=current_user.id).order_by(
        desc(Instrument.created_at)
    ).all()
    
    return jsonify({
        'success': True,
        'instruments': [inst.to_dict() for inst in instruments]
    })

# ========== 静态文件服务 ==========
@main_bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """提供上传的文件"""
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
    # 在已有的routes.py基础上添加以下路由

@main_bp.route('/search/suggestions', methods=['GET'])
def get_search_suggestions():
    """获取搜索建议"""
    keyword = request.args.get('q', '').strip()
    
    if not keyword or len(keyword) < 2:
        return jsonify({'success': True, 'suggestions': []})
    
    # 搜索乐器标题和品牌
    instruments = Instrument.query.filter(
        Instrument.status == 'available',
        Instrument.title.ilike(f'%{keyword}%')
    ).limit(10).all()
    
    # 搜索分类
    categories = Category.query.filter(
        Category.name.ilike(f'%{keyword}%')
    ).limit(5).all()
    
    suggestions = []
    
    # 添加乐器建议
    for inst in instruments:
        suggestions.append({
            'type': 'instrument',
            'id': inst.id,
            'title': inst.title,
            'price': float(inst.price) if inst.price else 0
        })
    
    # 添加分类建议
    for cat in categories:
        suggestions.append({
            'type': 'category',
            'id': cat.id,
            'name': cat.name
        })
    
    return jsonify({
        'success': True,
        'suggestions': suggestions
    })

@main_bp.route('/instruments/<int:instrument_id>/images', methods=['POST'])
@login_required
def upload_instrument_images(instrument_id):
    """上传乐器图片"""
    instrument = Instrument.query.get_or_404(instrument_id)
    
    # 检查权限
    if instrument.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'success': False, 'message': '无权上传图片'}), 403
    
    if 'images' not in request.files:
        return jsonify({'success': False, 'message': '没有选择文件'}), 400
    
    files = request.files.getlist('images')
    is_main = request.form.get('is_main', 'false').lower() == 'true'
    
    uploaded_files = []
    
    for file in files:
        if file and allowed_file(file.filename):
            filename = save_uploaded_file(file, 'instruments')
            if filename:
                instrument_image = InstrumentImage(
                    instrument_id=instrument_id,
                    image_url=filename,
                    is_main=is_main and len(uploaded_files) == 0  # 第一个文件为主图
                )
                db.session.add(instrument_image)
                uploaded_files.append(filename)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'成功上传 {len(uploaded_files)} 张图片',
        'files': uploaded_files
    })

@main_bp.route('/users/<int:user_id>/instruments', methods=['GET'])
def get_user_instruments_list(user_id):
    """获取指定用户的乐器列表"""
    user = User.query.get_or_404(user_id)
    
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 12, type=int)
    
    query = Instrument.query.filter_by(
        user_id=user_id,
        status='available'
    ).order_by(desc(Instrument.created_at))
    
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)
    instruments = pagination.items
    
    return jsonify({
        'success': True,
        'instruments': [inst.to_dict() for inst in instruments],
        'user': {
            'id': user.id,
            'username': user.username,
            'avatar': user.get_avatar_url(),
            'credit_score': user.credit_score
        },
        'pagination': {
            'page': pagination.page,
            'page_size': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages
        }
    })

@main_bp.route('/statistics/dashboard', methods=['GET'])
@login_required
def get_dashboard_statistics():
    """获取仪表板统计数据（仅管理员）"""
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': '需要管理员权限'}), 403
    
    # 统计信息
    total_users = User.query.count()
    total_instruments = Instrument.query.count()
    total_orders = Order.query.count()
    
    # 今日新增
    today = datetime.utcnow().date()
    today_users = User.query.filter(
        db.func.date(User.created_at) == today
    ).count()
    
    today_instruments = Instrument.query.filter(
        db.func.date(Instrument.created_at) == today
    ).count()
    
    today_orders = Order.query.filter(
        db.func.date(Order.created_at) == today
    ).count()
    
    # 销售额统计
    total_sales = db.session.query(
        db.func.sum(Order.total_price)
    ).filter(
        Order.status == 'completed'
    ).scalar() or 0
    
    return jsonify({
        'success': True,
        'statistics': {
            'users': {
                'total': total_users,
                'today': today_users
            },
            'instruments': {
                'total': total_instruments,
                'today': today_instruments
            },
            'orders': {
                'total': total_orders,
                'today': today_orders
            },
            'sales': {
                'total': float(total_sales) if total_sales else 0
            }
        }
    })

@main_bp.route('/instruments/<int:instrument_id>/contact', methods=['POST'])
@login_required
def contact_seller(instrument_id):
    """联系卖家"""
    instrument = Instrument.query.get_or_404(instrument_id)
    
    # 检查是否自己的乐器
    if instrument.user_id == current_user.id:
        return jsonify({'success': False, 'message': '不能联系自己'}), 400
    
    data = request.get_json()
    message = data.get('message', '').strip()
    
    if not message:
        return jsonify({'success': False, 'message': '请输入消息内容'}), 400
    
    # 这里可以集成消息系统或邮件通知
    # 暂时返回卖家联系方式
    seller = instrument.owner
    
    contact_info = {
        'seller_id': seller.id,
        'seller_name': seller.real_name or seller.username,
        'contact_methods': []
    }
    
    if seller.phone:
        contact_info['contact_methods'].append({
            'type': 'phone',
            'value': seller.phone
        })
    
    if seller.email:
        contact_info['contact_methods'].append({
            'type': 'email',
            'value': seller.email
        })
    
    return jsonify({
        'success': True,
        'message': '联系方式已获取',
        'contact_info': contact_info
    })