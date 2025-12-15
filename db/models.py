"""
数据库模型定义
"""
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# 从database模块导入db实例
from db.database import db


class User(UserMixin, db.Model):
    """用户模型"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='viewer')  # 'admin', 'editor', 'viewer'
    is_active = db.Column(db.Boolean, nullable=False, default=True)  # 用户是否启用
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                          onupdate=datetime.utcnow)

    def set_password(self, password):
        """设置密码哈希"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """检查密码"""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'is_active': self.is_active,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Protocol(db.Model):
    """协议文件模型"""
    __tablename__ = 'protocols'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), unique=True, nullable=False)  # 协议文件名（唯一）
    description = db.Column(db.Text)  # 文件描述
    app_type = db.Column(db.String(100))  # 应用类型：影视小程序、漫剧小程序、短剧小程序、车机、H5小说
    app_name = db.Column(db.String(100))  # 影视名称：风行视频小程序、车机等

    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'filename': self.filename,
            'description': self.description,
            'app_type': self.app_type,
            'app_name': self.app_name
        }


class OperationLog(db.Model):
    """操作日志模型"""
    __tablename__ = 'operation_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)  # 'create_protocol', 'delete_protocol', etc.
    resource_type = db.Column(db.String(50), nullable=False)  # 'protocol', 'git'
    resource_name = db.Column(db.String(255))
    details = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 关联用户
    user = db.relationship('User', backref=db.backref('logs', lazy=True))

    def to_dict(self):
        """转换为字典格式"""
        # 将UTC时间转换为本地时间（假设本地时区为UTC+8）
        local_time = None
        if self.created_at:
            import pytz
            from datetime import timezone
            # 将UTC时间转换为本地时间（上海时区）
            utc_time = self.created_at.replace(tzinfo=timezone.utc)
            local_tz = pytz.timezone('Asia/Shanghai')
            local_time = utc_time.astimezone(local_tz)
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else None,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_name': self.resource_name,
            'details': self.details,
            'created_at': local_time.strftime('%Y-%m-%d %H:%M:%S') if local_time else None
        }
