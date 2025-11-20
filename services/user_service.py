"""
用户管理服务
"""
from db.database import db
from db.models import User, OperationLog
from werkzeug.security import generate_password_hash
from flask_login import current_user


def get_user_list(page=1, limit=10, role_filter=None):
    """获取用户列表"""
    query = User.query

    if role_filter:
        query = query.filter(User.role == role_filter)

    users = query.paginate(
        page=page,
        per_page=limit,
        error_out=False
    )

    return users


def update_user_role(user_id, new_role):
    """更新用户角色"""
    user = User.query.get_or_404(user_id)
    user.role = new_role
    db.session.commit()


def delete_user(user_id):
    """删除用户"""
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()


def create_user(username, password, role='viewer'):
    """创建用户"""
    # 检查用户名是否已存在
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        raise ValueError('用户名已存在')

    # 创建新用户
    user = User(username=username, role=role)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return user


def log_user_action(action, resource_type, resource_name, details):
    """记录用户操作日志"""
    log = OperationLog(
        user_id=current_user.id,
        action=action,
        resource_type=resource_type,
        resource_name=resource_name,
        details=details
    )
    db.session.add(log)
    db.session.commit()
