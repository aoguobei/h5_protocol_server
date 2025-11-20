"""
操作日志相关路由
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required
from services.log_service import get_operation_logs
from utils.auth import require_login, require_role

def get_db():
    from db.database import db
    return db

log_bp = Blueprint('log', __name__, url_prefix='/api/logs')


@log_bp.route('', methods=['GET'])
@login_required
@require_role('admin')
def get_logs_api():
    """获取操作日志"""
    try:
        # 支持分页和筛选
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 15, type=int)
        action_filter = request.args.get('action')
        resource_type_filter = request.args.get('resource_type')
        username_filter = request.args.get('username')
        user_id_filter = request.args.get('userId', type=int)

        logs = get_operation_logs(
            page=page,
            limit=limit,
            action_filter=action_filter,
            resource_type_filter=resource_type_filter,
            username_filter=username_filter,
            user_id_filter=user_id_filter
        )

        return jsonify({
            'logs': [log.to_dict() for log in logs.items],
            'pagination': {
                'page': page,
                'limit': limit,
                'total': logs.total,
                'pages': logs.pages
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
