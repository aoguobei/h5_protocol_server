from functools import wraps
from flask import jsonify
from flask_login import current_user


def require_login(f):
    """要求用户登录的装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': '需要登录'}), 401
        return f(*args, **kwargs)
    return decorated_function


def require_role(*roles):
    """要求用户具有特定角色的装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({'error': '需要登录'}), 401
            if current_user.role not in roles:
                return jsonify({'error': '权限不足'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator