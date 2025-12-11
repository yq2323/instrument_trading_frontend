from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, TextAreaField, DecimalField, SelectField, DateTimeField, IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional, NumberRange
import re

class RegisterForm(FlaskForm):
    """注册表单"""
    username = StringField('用户名', validators=[
        DataRequired(message='请输入用户名'),
        Length(min=4, max=20, message='用户名长度应为4-20个字符')
    ])
    email = StringField('邮箱', validators=[
        DataRequired(message='请输入邮箱'),
        Email(message='邮箱格式不正确')
    ])
    password = PasswordField('密码', validators=[
        DataRequired(message='请输入密码'),
        Length(min=6, message='密码长度至少为6位')
    ])
    confirm_password = PasswordField('确认密码', validators=[
        DataRequired(message='请确认密码'),
        EqualTo('password', message='两次输入的密码不一致')
    ])
    phone = StringField('手机号', validators=[Optional()])
    
    def validate_username(self, field):
        """验证用户名格式"""
        if not re.match(r'^[a-zA-Z0-9_]+$', field.data):
            raise ValidationError('用户名只能包含字母、数字和下划线')
    
    def validate_phone(self, field):
        """验证手机号格式"""
        if field.data:
            if not re.match(r'^1[3-9]\d{9}$', field.data):
                raise ValidationError('手机号格式不正确')

class LoginForm(FlaskForm):
    """登录表单"""
    username = StringField('用户名/邮箱/手机号', validators=[
        DataRequired(message='请输入用户名或邮箱')
    ])
    password = PasswordField('密码', validators=[
        DataRequired(message='请输入密码')
    ])
    remember = SelectField('记住我', choices=[('true', '是'), ('false', '否')], default='false')

class InstrumentForm(FlaskForm):
    """乐器发布表单"""
    title = StringField('标题', validators=[
        DataRequired(message='请输入标题'),
        Length(max=100, message='标题不能超过100个字符')
    ])
    description = TextAreaField('描述', validators=[
        DataRequired(message='请输入描述')
    ])
    price = DecimalField('价格', validators=[
        DataRequired(message='请输入价格'),
        NumberRange(min=0.01, message='价格必须大于0')
    ])
    original_price = DecimalField('原价', validators=[
        Optional(),
        NumberRange(min=0.01, message='原价必须大于0')
    ])
    category_id = SelectField('分类', coerce=int, validators=[
        DataRequired(message='请选择分类')
    ])
    condition = SelectField('成色', choices=[
        ('new', '全新'),
        ('like_new', '几乎全新'),
        ('good', '良好'),
        ('fair', '一般'),
        ('poor', '较差')
    ], default='good')
    brand = StringField('品牌', validators=[Optional(), Length(max=50)])
    model = StringField('型号', validators=[Optional(), Length(max=50)])
    location = StringField('位置', validators=[Optional(), Length(max=200)])
    
    # 图片上传字段
    images = FileField('图片', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], '只允许上传图片文件')
    ])
    main_image_index = IntegerField('主图索引', default=0)
    
    # 音频上传字段
    audio = FileField('音频试听', validators=[
        FileAllowed(['mp3', 'wav'], '只允许上传MP3或WAV文件')
    ])

class ProfileForm(FlaskForm):
    """个人资料表单"""
    real_name = StringField('真实姓名', validators=[
        Optional(),
        Length(max=50, message='真实姓名不能超过50个字符')
    ])
    phone = StringField('手机号', validators=[Optional()])
    student_id = StringField('学号', validators=[Optional()])
    avatar = FileField('头像', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], '只允许上传图片文件')
    ])
    
    def validate_phone(self, field):
        """验证手机号格式"""
        if field.data:
            if not re.match(r'^1[3-9]\d{9}$', field.data):
                raise ValidationError('手机号格式不正确')

class OrderForm(FlaskForm):
    """订单表单"""
    instrument_id = IntegerField('乐器ID', validators=[
        DataRequired(message='请选择乐器')
    ])
    quantity = IntegerField('数量', validators=[
        DataRequired(message='请输入数量'),
        NumberRange(min=1, max=10, message='数量应为1-10')
    ])
    meeting_time = DateTimeField('见面时间', format='%Y-%m-%d %H:%M', validators=[Optional()])
    meeting_place = StringField('见面地点', validators=[
        Optional(),
        Length(max=200, message='地点不能超过200个字符')
    ])
    payment_method = SelectField('支付方式', choices=[
        ('wechat', '微信支付'),
        ('alipay', '支付宝'),
        ('cash', '现金')
    ], default='wechat')