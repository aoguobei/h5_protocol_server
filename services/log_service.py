"""
日志管理服务
"""
from db.database import db
from db.models import OperationLog


def get_operation_logs(page=1, limit=15, action_filter=None, resource_type_filter=None, username_filter=None, user_id_filter=None):
    """获取操作日志"""
    query = OperationLog.query.join(OperationLog.user).order_by(OperationLog.created_at.desc())

    if action_filter:
        query = query.filter(OperationLog.action == action_filter)
    if resource_type_filter:
        query = query.filter(OperationLog.resource_type == resource_type_filter)
    if username_filter:
        query = query.filter(OperationLog.user.has(username=username_filter))
    if user_id_filter:
        query = query.filter(OperationLog.user_id == user_id_filter)

    logs = query.paginate(
        page=page,
        per_page=limit,
        error_out=False
    )

    return logs


def create_operation_log(user_id, action, resource_type, resource_name, details):
    """创建操作日志"""
    log = OperationLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_name=resource_name,
        details=details
    )
    db.session.add(log)
    db.session.commit()

    return log


def delete_old_logs(older_than_days=30):
    """删除指定天数前的日志"""
    from datetime import datetime, timedelta
    cutoff_date = datetime.now() - timedelta(days=older_than_days)

    deleted_count = db.session.query(OperationLog)\
        .filter(OperationLog.created_at < cutoff_date)\
        .delete()

    db.session.commit()
    return deleted_count
