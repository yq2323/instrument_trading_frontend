from flask import Blueprint, request, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
import re

from . import db
from .models import User
from .utils import validate_email, validate_phone, generate_token, verify_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json() or request.form
    
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    confirm_password = data.get('confirm_password', '').strip()
    phone = data.get('phone', '').strip()
    
    # 验证必填字段
    if not all([username, email, password, confirm_password]):
        return jsonify({'success': False, 'message': '请填写所有必填字段'}), 400
    
    # 验证用户名格式
    if len(username) < 4 or len(username) > 20:
        return jsonify({'success': False, 'message': '用户名长度应为4-20个字符'}), 400
    
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return jsonify({'success': False, 'message': '用户名只能包含字母、数字和下划线'}), 400
    
    # 验证邮箱格式
    if not validate_email(email):
        return jsonify({'success': False, 'message': '邮箱格式不正确'}), 400
    
    # 验证密码
    if len(password) < 6:
        return jsonify({'success': False, 'message': '密码长度至少为6位'}), 400
    
    if password != confirm_password:
        return jsonify({'success': False, 'message': '两次输入的密码不一致'}), 400
    
    # 验证手机号（可选）
    if phone and not validate_phone(phone):
        return jsonify({'success': False, 'message': '手机号格式不正确'}), 400
    
    # 检查用户名和邮箱是否已存在
    if User.query.filter_by(username=username).first():
        return jsonify({'success': False, 'message': '用户名已被使用'}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({'success': False, 'message': '邮箱已被注册'}), 400
    
    if phone and User.query.filter_by(phone=phone).first():
        return jsonify({'success': False, 'message': '手机号已被注册'}), 400
    
    try:
        # 创建新用户
        user = User(
            username=username,
            email=email,
            phone=phone or None
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # 自动登录
        login_user(user, remember=True)
        
        return jsonify({
            'success': True,
            'message': '注册成功',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'avatar': user.get_avatar_url()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'注册失败: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json() or request.form
    
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    remember = data.get('remember', True)
    
    if not username or not password:
        return jsonify({'success': False, 'message': '请输入用户名和密码'}), 400
    
    # 支持用户名、邮箱、手机号登录
    if '@' in username:
        user = User.query.filter_by(email=username).first()
    elif username.isdigit() and len(username) == 11:
        user = User.query.filter_by(phone=username).first()
    else:
        user = User.query.filter_by(username=username).first()
    
    if not user or not user.check_password(password):
        return jsonify({'success': False, 'message': '用户名或密码错误'}), 401
    
    if not user.is_verified and user.role == 'seller':
        return jsonify({'success': False, 'message': '卖家账号需要先验证身份'}), 403
    
    # 登录用户
    login_user(user, remember=remember)
    
    return jsonify({
        'success': True,
        'message': '登录成功',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'avatar': user.get_avatar_url(),
            'is_seller': user.is_seller,
            'is_admin': user.is_admin
        }
    })

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """用户登出"""
    logout_user()
    return jsonify({'success': True, 'message': '已退出登录'})

@auth_bp.route('/csrf_token', methods=['GET'])
def get_csrf_token():
    """获取CSRF token"""
    from flask_wtf.csrf import generate_csrf
    return jsonify({'csrf_token': generate_csrf()})

@auth_bp.route('/check_auth', methods=['GET'])
def check_auth():
    """检查认证状态"""
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'user': {
                'id': current_user.id,
                'username': current_user.username,
                'email': current_user.email,
                'role': current_user.role,
                'avatar': current_user.get_avatar_url(),
                'is_seller': current_user.is_seller,
                'is_admin': current_user.is_admin
            }
        })
    return jsonify({'authenticated': False})

@auth_bp.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    """更新用户资料"""
    data = request.form
    
    real_name = data.get('real_name', '').strip()
    phone = data.get('phone', '').strip()
    student_id = data.get('student_id', '').strip()
    
    # 更新用户信息
    if real_name:
        current_user.real_name = real_name
    
    if phone:
        if not validate_phone(phone):
            return jsonify({'success': False, 'message': '手机号格式不正确'}), 400
        current_user.phone = phone
    
    if student_id:
        current_user.student_id = student_id
    
    # 处理头像上传
    if 'avatar' in request.files:
        avatar = request.files['avatar']
        if avatar.filename:
            from .utils import save_uploaded_file
            filename = save_uploaded_file(avatar, 'avatars')
            if filename:
                current_user.avatar = filename
    
    try:
        db.session.commit()
        return jsonify({'success': True, 'message': '资料更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 500

@auth_bp.route('/change_password', methods=['POST'])
@login_required
def change_password():
    """修改密码"""
    data = request.get_json()
    
    old_password = data.get('old_password', '').strip()
    new_password = data.get('new_password', '').strip()
    confirm_password = data.get('confirm_password', '').strip()
    
    if not old_password or not new_password or not confirm_password:
        return jsonify({'success': False, 'message': '请填写所有密码字段'}), 400
    
    if not current_user.check_password(old_password):
        return jsonify({'success': False, 'message': '原密码错误'}), 400
    
    if len(new_password) < 6:
        return jsonify({'success': False, 'message': '新密码长度至少为6位'}), 400
    
    if new_password != confirm_password:
        return jsonify({'success': False, 'message': '两次输入的新密码不一致'}), 400
    
    if old_password == new_password:
        return jsonify({'success': False, 'message': '新密码不能与原密码相同'}), 400
    
    try:
        current_user.set_password(new_password)
        db.session.commit()
        return jsonify({'success': True, 'message': '密码修改成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'修改失败: {str(e)}'}), 500