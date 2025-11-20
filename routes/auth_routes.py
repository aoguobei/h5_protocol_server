"""
认证相关路由
"""
from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from services.auth_service import authenticate_user, register_user

# 在函数内部使用db，避免在模块级别导入导致的循环依赖
def get_db():
    from db.database import db
    return db

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'error': '用户名和密码不能为空'}), 400

        result = register_user(username, password, 'viewer')
        user = result['user']
        error = result['error']

        if error:
            return jsonify({'error': error}), 400

        return jsonify({
            'message': '用户注册成功',
            'user': user.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'error': '用户名和密码不能为空'}), 400

        result = authenticate_user(username, password)
        user = result['user']
        error = result['error']

        if error:
            return jsonify({'error': error}), 401

        login_user(user)

        return jsonify({
            'message': '登录成功',
            'user': user.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """用户登出"""
    logout_user()
    return jsonify({'message': '登出成功'}), 200


@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    """获取当前用户信息"""
    return jsonify(current_user.to_dict()), 200
