"""
预览服务
"""
import uuid
import time
from datetime import datetime, timedelta

# 内存存储预览内容（格式：{preview_id: {'content': html_content, 'expires_at': datetime}}）
_preview_storage = {}

# 清理过期预览的间隔（秒）
_CLEANUP_INTERVAL = 300  # 5分钟
_last_cleanup = time.time()


def _cleanup_expired_previews():
    """清理过期的预览内容"""
    global _last_cleanup
    current_time = time.time()
    
    # 每5分钟清理一次
    if current_time - _last_cleanup < _CLEANUP_INTERVAL:
        return
    
    _last_cleanup = current_time
    now = datetime.now()
    expired_ids = [
        preview_id for preview_id, data in _preview_storage.items()
        if data['expires_at'] < now
    ]
    for preview_id in expired_ids:
        del _preview_storage[preview_id]


def create_preview(html_content):
    """
    创建预览，返回预览 ID
    
    Args:
        html_content: HTML 内容字符串
        
    Returns:
        str: 预览 ID
        
    Raises:
        ValueError: 如果内容为空
    """
    if not html_content:
        raise ValueError('HTML 内容不能为空')
    
    # 清理过期预览
    _cleanup_expired_previews()
    
    # 生成唯一的预览 ID
    preview_id = str(uuid.uuid4())
    
    # 设置过期时间（1小时后）
    expires_at = datetime.now() + timedelta(hours=1)
    
    # 存储预览内容
    _preview_storage[preview_id] = {
        'content': html_content,
        'expires_at': expires_at
    }
    
    return preview_id


def get_preview_content(preview_id):
    """
    获取预览内容
    
    Args:
        preview_id: 预览 ID
        
    Returns:
        str: HTML 内容
        
    Raises:
        ValueError: 如果预览不存在或已过期
    """
    if preview_id not in _preview_storage:
        raise ValueError('预览不存在或已过期')
    
    data = _preview_storage[preview_id]
    
    # 检查是否过期
    if data['expires_at'] < datetime.now():
        del _preview_storage[preview_id]
        raise ValueError('预览已过期')
    
    return data['content']

