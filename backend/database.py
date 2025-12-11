import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

def init_db():
    """初始化数据库和表"""
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='123456',
        charset='utf8mb4'
    )
    
    try:
        with connection.cursor() as cursor:
            # 创建数据库
            cursor.execute("CREATE DATABASE IF NOT EXISTS instrument_trading CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            cursor.execute("USE instrument_trading")
            
            # 删除现有表（如果存在）- 按照依赖关系顺序删除
            cursor.execute("DROP TABLE IF EXISTS instrument_image")
            cursor.execute("DROP TABLE IF EXISTS favorite")
            cursor.execute("DROP TABLE IF EXISTS cart")
            cursor.execute("DROP TABLE IF EXISTS `order`")
            cursor.execute("DROP TABLE IF EXISTS orders")  # 同时删除旧的orders表
            cursor.execute("DROP TABLE IF EXISTS view_history")
            cursor.execute("DROP TABLE IF EXISTS instrument")
            cursor.execute("DROP TABLE IF EXISTS category")
            cursor.execute("DROP TABLE IF EXISTS user")
            
            # 创建用户表
            cursor.execute("""
            CREATE TABLE user (
                id INT PRIMARY KEY AUTO_INCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(200) NOT NULL,
                phone VARCHAR(20),
                real_name VARCHAR(50),
                student_id VARCHAR(20),
                avatar VARCHAR(200),
                role ENUM('user', 'seller', 'admin') DEFAULT 'user',
                credit_score INT DEFAULT 100,
                is_verified BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """)
            
            # 创建乐器分类表
            cursor.execute("""
            CREATE TABLE category (
                id INT PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(50) NOT NULL,
                description TEXT,
                icon VARCHAR(100),
                sort_order INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # 插入默认分类
            cursor.execute("""
            INSERT IGNORE INTO category (name, description, icon) VALUES
            ('吉他', '各种类型吉他', 'fas fa-guitar'),
            ('钢琴', '钢琴及键盘乐器', 'fas fa-music'),
            ('小提琴', '弦乐器', 'fas fa-violin'),
            ('鼓类', '打击乐器', 'fas fa-drum'),
            ('管乐器', '铜管和木管乐器', 'fas fa-trumpet'),
            ('民族乐器', '中国传统乐器', 'fas fa-guitar'),
            ('其他', '其他类型乐器', 'fas fa-question-circle')
            """)
            
            # 创建乐器商品表
            cursor.execute("""
            CREATE TABLE instrument (
                id INT PRIMARY KEY AUTO_INCREMENT,
                title VARCHAR(100) NOT NULL,
                description TEXT,
                price DECIMAL(10,2) NOT NULL,
                original_price DECIMAL(10,2),
                category_id INT,
                user_id INT,
                instrument_condition ENUM('new', 'like_new', 'good', 'fair', 'poor') DEFAULT 'good',
                brand VARCHAR(50),
                model VARCHAR(50),
                status ENUM('available', 'pending', 'sold', 'removed') DEFAULT 'available',
                view_count INT DEFAULT 0,
                favorite_count INT DEFAULT 0,
                location VARCHAR(200),
                audio_url VARCHAR(200),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES category(id) ON DELETE SET NULL,
                FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
                INDEX idx_status_created (status, created_at),
                INDEX idx_category_status (category_id, status),
                INDEX idx_user_status (user_id, status)
            )
            """)
            
            # 创建乐器图片表
            cursor.execute("""
            CREATE TABLE instrument_image (
                id INT PRIMARY KEY AUTO_INCREMENT,
                instrument_id INT NOT NULL,
                image_url VARCHAR(200) NOT NULL,
                is_main BOOLEAN DEFAULT FALSE,
                sort_order INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (instrument_id) REFERENCES instrument(id) ON DELETE CASCADE
            )
            """)
            
            # 创建收藏表
            cursor.execute("""
            CREATE TABLE favorite (
                id INT PRIMARY KEY AUTO_INCREMENT,
                user_id INT NOT NULL,
                instrument_id INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY uk_user_instrument (user_id, instrument_id),
                FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
                FOREIGN KEY (instrument_id) REFERENCES instrument(id) ON DELETE CASCADE
            )
            """)
            
            # 创建订单表
            cursor.execute("""
            CREATE TABLE `order` (
                id VARCHAR(50) PRIMARY KEY,
                instrument_id INT NOT NULL,
                buyer_id INT NOT NULL,
                seller_id INT NOT NULL,
                total_price DECIMAL(10,2) NOT NULL,
                status ENUM('pending', 'paid', 'shipped', 'completed', 'cancelled') DEFAULT 'pending',
                payment_method VARCHAR(50),
                meeting_time DATETIME,
                meeting_place VARCHAR(200),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (instrument_id) REFERENCES instrument(id),
                FOREIGN KEY (buyer_id) REFERENCES user(id),
                FOREIGN KEY (seller_id) REFERENCES user(id)
            )
            """)
            
            # 创建购物车表
            cursor.execute("""
            CREATE TABLE cart (
                id INT PRIMARY KEY AUTO_INCREMENT,
                user_id INT NOT NULL,
                instrument_id INT NOT NULL,
                quantity INT DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
                FOREIGN KEY (instrument_id) REFERENCES instrument(id) ON DELETE CASCADE,
                UNIQUE KEY uk_user_instrument (user_id, instrument_id)
            )
            """)
            
            # 创建浏览历史表
            cursor.execute("""
            CREATE TABLE view_history (
                id INT PRIMARY KEY AUTO_INCREMENT,
                user_id INT NOT NULL,
                instrument_id INT NOT NULL,
                viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
                FOREIGN KEY (instrument_id) REFERENCES instrument(id) ON DELETE CASCADE
            )
            """)
            
        connection.commit()
        print("✅ 数据库初始化完成！")
        
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        connection.rollback()
    finally:
        connection.close()

if __name__ == "__main__":
    init_db()