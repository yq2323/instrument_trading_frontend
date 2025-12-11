import os
import sys
from app import create_app
from database import init_db

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 检查并初始化数据库
print("🔧 正在检查数据库...")
try:
    init_db()
    print("✅ 数据库初始化完成")
except Exception as e:
    print(f"⚠️ 数据库初始化失败: {e}")
    print("尝试继续启动...")

# 创建Flask应用
app = create_app()

@app.route('/')
def home():
    """首页"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>校园二手乐器交易平台</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .container {
                text-align: center;
                background: white;
                padding: 50px;
                border-radius: 10px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
            h1 {
                color: #333;
                margin-bottom: 20px;
            }
            p {
                color: #666;
                margin-bottom: 30px;
            }
            .status {
                background: #f8f9fa;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
                text-align: left;
            }
            .endpoints {
                text-align: left;
                margin-top: 30px;
            }
            .endpoint {
                padding: 8px;
                border-bottom: 1px solid #eee;
            }
            a {
                color: #667eea;
                text-decoration: none;
                margin: 0 10px;
            }
            a:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎵 校园二手乐器交易平台</h1>
            <p>后端API服务正在运行</p>
            
            <div class="status">
                <strong>状态:</strong> ✅ 运行正常<br>
                <strong>端口:</strong> 5000<br>
                <strong>环境:</strong> 开发环境
            </div>
            
            <div>
                <a href="/api/" target="_blank">API文档</a>
                <a href="/api/categories" target="_blank">查看分类</a>
                <a href="/api/instruments" target="_blank">查看乐器</a>
            </div>
            
            <div class="endpoints">
                <h3>主要API端点:</h3>
                <div class="endpoint">GET /api/categories - 获取分类</div>
                <div class="endpoint">GET /api/instruments - 获取乐器列表</div>
                <div class="endpoint">POST /api/auth/register - 用户注册</div>
                <div class="endpoint">POST /api/auth/login - 用户登录</div>
                <div class="endpoint">POST /api/instruments - 发布乐器</div>
                <div class="endpoint">POST /api/orders - 创建订单</div>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/static/<path:filename>')
def serve_static(filename):
    """提供静态文件"""
    from flask import send_from_directory
    static_folder = os.path.join(os.path.dirname(__file__), 'static')
    return send_from_directory(static_folder, filename)

if __name__ == '__main__':
    # 确保上传目录存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'avatars'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'instruments'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'audios'), exist_ok=True)
    
    print("\n" + "="*50)
    print("🎵 校园二手乐器交易平台启动成功!")
    print("="*50)
    print(f"📁 上传目录: {app.config['UPLOAD_FOLDER']}")
    print(f"🔗 后台地址: http://127.0.0.1:{os.environ.get('PORT', 5000)}")
    print(f"🔗 API地址: http://127.0.0.1:{os.environ.get('PORT', 5000)}/api")
    print(f"🔗 静态文件: http://127.0.0.1:{os.environ.get('PORT', 5000)}/static")
    print("="*50)
    print("\n📋 可用命令:")
    print("  • python database.py - 重新初始化数据库")
    print("  • python run.py - 启动服务器")
    print("  • curl http://localhost:5000/api/categories - 测试API")
    print("\n🚀 正在启动服务器...\n")
    
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=app.config['DEBUG'])