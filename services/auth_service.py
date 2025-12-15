"""
认证服务
"""
from db.database import db
from db.models import User
from werkzeug.security import check_password_hash


def authenticate_user(username, password):
    """
    认证用户
    :param username: 用户名
    :param password: 密码
    :return: 用户对象或None
    """
    user = User.query.filter_by(username=username).first()

    if user is None:
        # 用户不存在
        return {'user': None, 'error': '用户不存在'}
    elif not user.is_active:
        # 用户已被禁用
        return {'user': None, 'error': '账号已被禁用，请联系管理员'}
    elif not user.check_password(password):
        # 密码错误
        return {'user': None, 'error': '密码错误'}
    else:
        # 认证成功
        return {'user': user, 'error': None}


def register_user(username, password, role='viewer'):
    """
    注册新用户
    :param username: 用户名
    :param password: 密码
    :param role: 角色，默认为viewer
    :return: 用户对象和错误信息
    """
    # 检查用户名是否已存在
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return {'user': None, 'error': '用户名已存在'}

    # 创建新用户
    user = User(username=username)
    user.set_password(password)
    user.role = role

    try:
        db.session.add(user)
        db.session.commit()
        return {'user': user, 'error': None}
    except Exception as e:
        db.session.rollback()
        return {'user': None, 'error': str(e)}


def get_user_by_id(user_id):
    """
    根据ID获取用户
    :param user_id: 用户ID
    :return: 用户对象
    """
    return User.query.get(user_id)


def get_user_by_username(username):
    """
    根据用户名获取用户
    :param username: 用户名
    :return: 用户对象
    """
    return User.query.filter_by(username=username).first()
