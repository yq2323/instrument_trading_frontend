# 校园二手乐器交易平台

## 项目简介

校园二手乐器交易平台是一个专为大学生设计的在线二手乐器交易系统，提供乐器发布、浏览、搜索、交易等功能。

### 主要功能

- **用户系统**：注册、登录、个人中心
- **乐器管理**：发布、编辑、删除乐器
- **浏览搜索**：分类浏览、关键词搜索、高级筛选
- **购物车**：添加商品、管理购物车、结算
- **图片上传**：支持多图上传、音频预览

## 技术栈

- **前端**：HTML5、CSS3、JavaScript、原生AJAX
- **后端**：Python、Flask、SQLAlchemy
- **数据库**：SQLite (开发环境) / MySQL (生产环境)
- **部署**：支持GitHub Pages (前端) + 云平台 (后端)

## 快速开始

### 本地开发

1. **克隆项目**
```bash
git clone https://github.com/yq2323/instrument_trading_frontend.git
cd instrument_trading_frontend
```

2. **启动后端服务**
```bash
cd backend
pip install -r requirements.txt
python run.py
```

3. **启动前端服务**
```bash
cd frontend
python -m http.server 8000
```

4. **访问应用**
- 前端：http://localhost:8000
- 后端：http://localhost:5000
- API文档：http://localhost:5000/api

### 部署说明

#### 前端部署 (GitHub Pages)

1. 项目已配置GitHub Actions自动部署
2. 推送代码到master分支后，GitHub Actions会自动构建并部署前端到GitHub Pages
3. 访问地址：https://yq2323.github.io/instrument_trading_frontend

#### 后端部署 (推荐平台)

1. **Heroku**
   - 注册Heroku账号
   - 安装Heroku CLI
   - 创建应用：`heroku create`
   - 推送代码：`git push heroku master`
   - 设置环境变量：`heroku config:set PORT=5000`

2. **Vercel**
   - 注册Vercel账号
   - 连接GitHub仓库
   - 配置构建命令：`cd backend && pip install -r requirements.txt`
   - 配置启动命令：`cd backend && python run.py`

3. **Railway**
   - 注册Railway账号
   - 导入GitHub仓库
   - 自动检测并配置Python环境
   - 设置环境变量

## 项目结构

```
instrument_trading_frontend/
├── backend/            # 后端代码
│   ├── app/            # Flask应用
│   ├── static/         # 静态文件
│   ├── database.py     # 数据库初始化
│   ├── run.py          # 启动文件
│   └── requirements.txt # 依赖文件
├── frontend/           # 前端代码
│   ├── css/            # 样式文件
│   ├── js/             # JavaScript文件
│   └── index.html      # 首页
└── .github/            # GitHub配置
```

## API文档

### 认证API

- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `GET /api/auth/logout` - 用户登出
- `GET /api/auth/user` - 获取当前用户信息

### 乐器API

- `GET /api/instruments` - 获取乐器列表
- `GET /api/instruments/<id>` - 获取乐器详情
- `POST /api/instruments` - 发布乐器
- `PUT /api/instruments/<id>` - 更新乐器信息
- `DELETE /api/instruments/<id>` - 删除乐器

### 购物车API

- `GET /api/cart` - 获取购物车
- `POST /api/cart` - 添加商品到购物车
- `DELETE /api/cart/<id>` - 从购物车移除商品

### 分类API

- `GET /api/categories` - 获取分类列表

## 环境变量

```
PORT=5000              # 服务器端口
SECRET_KEY=your_secret_key  # 密钥
DEBUG=False            # 调试模式
```

## 许可证

MIT License