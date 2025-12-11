from flask import Flask
from flask_login import LoginManager
from flask_cors import CORS
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from .config import Config
from .models import db, User

# 初始化扩展
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = '请先登录'
login_manager.login_message_category = 'warning'
mail = Mail()
csrf = CSRFProtect()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app(config_class=Config):
    """应用工厂函数"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    
    # 为API环境配置CORS，允许所有域名访问
    CORS(app, supports_credentials=True, origins="*")
    
    # 在API环境中禁用CSRF保护，避免跨域问题
    app.config['WTF_CSRF_ENABLED'] = False
    
    # 注册蓝图
    from .auth import auth_bp
    from .routes import main_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(main_bp, url_prefix='/api')
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
        
        # 确保上传目录存在
        import os
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'avatars'), exist_ok=True)
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'instruments'), exist_ok=True)
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'audios'), exist_ok=True)
    
    # 注册错误处理器
    @app.errorhandler(404)
    def not_found_error(error):
        return {'success': False, 'message': '资源不存在'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {'success': False, 'message': '服务器内部错误'}, 500
    
    @app.errorhandler(413)
    def request_entity_too_large(error):
        return {'success': False, 'message': '文件太大'}, 413
    
    return app