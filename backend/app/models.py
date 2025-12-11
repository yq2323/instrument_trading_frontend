from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """用户模型"""
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20))
    real_name = db.Column(db.String(50))
    student_id = db.Column(db.String(20))
    avatar = db.Column(db.String(200))
    role = db.Column(db.Enum('user', 'seller', 'admin'), default='user')
    credit_score = db.Column(db.Integer, default=100)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    instruments = db.relationship('Instrument', backref='owner', lazy='dynamic')
    favorites = db.relationship('Favorite', backref='user', lazy='dynamic')
    orders_as_buyer = db.relationship('Order', foreign_keys='Order.buyer_id', backref='buyer', lazy='dynamic')
    orders_as_seller = db.relationship('Order', foreign_keys='Order.seller_id', backref='seller', lazy='dynamic')
    cart_items = db.relationship('Cart', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def get_avatar_url(self):
        """获取头像URL"""
        if self.avatar:
            return f'/static/uploads/{self.avatar}'
        return '/static/images/default-avatar.png'
    
    @property
    def is_seller(self):
        return self.role in ['seller', 'admin']
    
    @property
    def is_admin(self):
        return self.role == 'admin'

class Category(db.Model):
    """分类模型"""
    __tablename__ = 'category'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(100))
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    instruments = db.relationship('Instrument', backref='category_ref', lazy='dynamic')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon
        }

class Instrument(db.Model):
    """乐器模型"""
    __tablename__ = 'instrument'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    original_price = db.Column(db.Numeric(10, 2))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    instrument_condition = db.Column(db.Enum('new', 'like_new', 'good', 'fair', 'poor'), default='good')
    brand = db.Column(db.String(50))
    model = db.Column(db.String(50))
    status = db.Column(db.Enum('available', 'pending', 'sold', 'removed'), default='available')
    view_count = db.Column(db.Integer, default=0)
    favorite_count = db.Column(db.Integer, default=0)
    location = db.Column(db.String(200))
    audio_url = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    images = db.relationship('InstrumentImage', backref='instrument', lazy='dynamic', cascade='all, delete-orphan')
    favorites = db.relationship('Favorite', backref='instrument', lazy='dynamic')
    
    def to_dict(self, include_user=True, include_images=True):
        """转换为字典"""
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'price': float(self.price) if self.price else 0,
            'original_price': float(self.original_price) if self.original_price else None,
            'category_id': self.category_id,
            'condition': self.instrument_condition,
            'brand': self.brand,
            'model': self.model,
            'status': self.status,
            'view_count': self.view_count,
            'favorite_count': self.favorite_count,
            'location': self.location,
            'audio_url': self.audio_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'category_name': self.category_ref.name if self.category_ref else None
        }
        
        if include_user and self.owner:
            data['user'] = {
                'id': self.owner.id,
                'username': self.owner.username,
                'real_name': self.owner.real_name,
                'avatar': self.owner.get_avatar_url(),
                'credit_score': self.owner.credit_score
            }
        
        if include_images:
            data['images'] = [img.to_dict() for img in self.images.order_by(InstrumentImage.is_main.desc(), InstrumentImage.sort_order).all()]
            main_image = self.images.filter_by(is_main=True).first()
            data['main_image'] = main_image.image_url if main_image else None
        
        return data
    
    def increment_view_count(self):
        """增加浏览次数"""
        self.view_count += 1
        db.session.commit()

class InstrumentImage(db.Model):
    """乐器图片模型"""
    __tablename__ = 'instrument_image'
    
    id = db.Column(db.Integer, primary_key=True)
    instrument_id = db.Column(db.Integer, db.ForeignKey('instrument.id'), nullable=False)
    image_url = db.Column(db.String(200), nullable=False)
    is_main = db.Column(db.Boolean, default=False)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'image_url': self.image_url,
            'is_main': self.is_main,
            'full_url': f'/static/uploads/{self.image_url}'
        }

class Favorite(db.Model):
    """收藏模型"""
    __tablename__ = 'favorite'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    instrument_id = db.Column(db.Integer, db.ForeignKey('instrument.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'instrument_id', name='uk_user_instrument'),
    )

class Cart(db.Model):
    """购物车模型"""
    __tablename__ = 'cart'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    instrument_id = db.Column(db.Integer, db.ForeignKey('instrument.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    instrument = db.relationship('Instrument', backref='cart_items_ref')
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'instrument_id', name='uk_user_instrument_cart'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'instrument_id': self.instrument_id,
            'quantity': self.quantity,
            'instrument': self.instrument.to_dict() if self.instrument else None
        }

class Order(db.Model):
    """订单模型"""
    __tablename__ = 'orders'
    
    id = db.Column(db.String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    instrument_id = db.Column(db.Integer, db.ForeignKey('instrument.id'), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.Enum('pending', 'paid', 'shipped', 'completed', 'cancelled'), default='pending')
    payment_method = db.Column(db.String(50))
    meeting_time = db.Column(db.DateTime)
    meeting_place = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    instrument = db.relationship('Instrument', backref='orders')
    
    def to_dict(self):
        return {
            'id': self.id,
            'instrument_id': self.instrument_id,
            'buyer_id': self.buyer_id,
            'seller_id': self.seller_id,
            'total_price': float(self.total_price) if self.total_price else 0,
            'status': self.status,
            'payment_method': self.payment_method,
            'meeting_time': self.meeting_time.isoformat() if self.meeting_time else None,
            'meeting_place': self.meeting_place,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'instrument': self.instrument.to_dict() if self.instrument else None
        }