"""
用户管理相关路由
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from services.user_service import get_user_list, update_user_role, toggle_user_status, create_user
from utils.auth import require_role

def get_db():
    from db.database import db
    return db

user_bp = Blueprint('user', __name__, url_prefix='/api/users')


@user_bp.route('', methods=['GET'])
@login_required
@require_role('admin')
def get_users():
    """获取用户列表"""
    try:
        # 支持分页和筛选
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        role_filter = request.args.get('role')

        users = get_user_list(page=page, limit=limit, role_filter=role_filter)

        return jsonify({
            'users': [user.to_dict() for user in users.items],
            'pagination': {
                'page': page,
                'limit': limit,
                'total': users.total,
                'pages': users.pages
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@user_bp.route('/<int:user_id>/role', methods=['PUT'])
@login_required
@require_role('admin')
def update_user_role_api(user_id):
    """更新用户角色"""
    try:
        if current_user.id == user_id:
            return jsonify({'error': '不能修改自己的角色'}), 400

        data = request.json
        new_role = data.get('role')

        if new_role not in ['admin', 'editor', 'viewer']:
            return jsonify({'error': '无效的角色'}), 400

        update_user_role(user_id, new_role)

        # 记录操作日志
        from services.user_service import log_user_action
        # 获取用户名
        from db.models import User
        target_user = User.query.get_or_404(user_id)
        log_user_action(
            action='update_user_role',
            resource_type='user',
            resource_name=f'user_{target_user.username}',
            details=f'将用户 {target_user.username} 的角色更新为 {new_role}'
        )

        return jsonify({'message': '用户角色更新成功'}), 200
    except Exception as e:
        db = get_db()
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@user_bp.route('/<int:user_id>/toggle', methods=['PUT'])
@login_required
@require_role('admin')
def toggle_user_status_api(user_id):
    """禁用/启用用户"""
    try:
        if current_user.id == user_id:
            return jsonify({'error': '不能禁用自己'}), 400

        # 先获取用户信息
        from db.models import User
        target_user = User.query.get_or_404(user_id)
        username = target_user.username

        # 切换用户状态
        is_active = toggle_user_status(user_id)

        # 记录操作日志
        from services.user_service import log_user_action
        action_text = '启用' if is_active else '禁用'
        log_user_action(
            action='toggle_user_status',
            resource_type='user',
            resource_name=f'user_{username}',
            details=f'{action_text}了用户 {username}'
        )

        return jsonify({
            'message': f'用户{action_text}成功',
            'is_active': is_active
        }), 200
    except Exception as e:
        db = get_db()
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
