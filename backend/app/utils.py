import os
import uuid
from datetime import datetime, timedelta
import jwt
from werkzeug.utils import secure_filename
from flask import current_app
import re
from PIL import Image
import io

def allowed_file(filename, allowed_extensions=None):
    """检查文件扩展名是否允许"""
    if allowed_extensions is None:
        allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif'})
    
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_uploaded_file(file, subfolder=''):
    """保存上传的文件"""
    if file and allowed_file(file.filename):
        # 生成安全的文件名
        filename = secure_filename(file.filename)
        # 添加UUID防止重名
        ext = filename.rsplit('.', 1)[1].lower()
        new_filename = f"{uuid.uuid4().hex}.{ext}"
        
        # 创建目录
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder)
        os.makedirs(upload_dir, exist_ok=True)
        
        # 保存文件
        file_path = os.path.join(upload_dir, new_filename)
        file.save(file_path)
        
        # 如果是图片，生成缩略图
        if ext in ['jpg', 'jpeg', 'png', 'gif']:
            generate_thumbnail(file_path)
        
        return os.path.join(subfolder, new_filename)
    return None

def generate_thumbnail(file_path, size=(300, 300)):
    """生成缩略图"""
    try:
        img = Image.open(file_path)
        img.thumbnail(size, Image.Resampling.LANCZOS)
        
        # 保存缩略图
        thumb_path = file_path.replace('.', '_thumb.')
        img.save(thumb_path)
        
        return thumb_path
    except Exception as e:
        print(f"生成缩略图失败: {e}")
        return None

def validate_email(email):
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """验证手机号格式"""
    pattern = r'^1[3-9]\d{9}$'
    return re.match(pattern, phone) is not None

def generate_token(user_id, expires_in=3600):
    """生成JWT令牌"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(seconds=expires_in)
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

def verify_token(token):
    """验证JWT令牌"""
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload['user_id']
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

def format_price(price):
    """格式化价格显示"""
    try:
        price = float(price)
        return f'¥{price:,.2f}'.replace(',', ',')
    except (ValueError, TypeError):
        return '¥0.00'

def get_condition_text(condition):
    """获取成色文本"""
    conditions = {
        'new': '全新',
        'like_new': '几乎全新',
        'good': '良好',
        'fair': '一般',
        'poor': '较差'
    }
    return conditions.get(condition, '良好')

def paginate_query(query, page, per_page):
    """分页查询"""
    return query.paginate(page=page, per_page=per_page, error_out=False)

def calculate_distance(lat1, lon1, lat2, lon2):
    """计算两个坐标之间的距离（米）"""
    from math import radians, sin, cos, sqrt, atan2
    
    # 将十进制度数转化为弧度
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine公式
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    r = 6371000  # 地球平均半径，单位为米
    
    return c * r

def send_email(to, subject, template, **kwargs):
    """发送邮件"""
    from flask_mail import Message
    from flask import render_template
    
    msg = Message(
        subject=subject,
        recipients=[to],
        sender=current_app.config['MAIL_DEFAULT_SENDER']
    )
    
    msg.html = render_template(template, **kwargs)
    
    from . import mail
    mail.send(msg)

def generate_verification_code():
    """生成验证码"""
    import random
    return str(random.randint(100000, 999999))

def clean_html_tags(text):
    """清理HTML标签"""
    import re
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def truncate_text(text, length=100):
    """截断文本"""
    if len(text) <= length:
        return text
    return text[:length] + '...'