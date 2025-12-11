from app import create_app
from app.models import db, User

# 创建应用实例
app = create_app()

with app.app_context():
    # 检查是否已有测试用户
    existing_user = User.query.filter_by(email='test@example.com').first()
    if not existing_user:
        # 创建测试用户
        test_user = User(
            username='testuser',
            email='test@example.com',
            role='user',
            is_verified=True
        )
        test_user.set_password('password123')
        
        db.session.add(test_user)
        db.session.commit()
        print('测试用户创建成功！')
        print(f'用户名: {test_user.username}')
        print(f'邮箱: {test_user.email}')
        print(f'密码: password123')
    else:
        print('测试用户已存在！')