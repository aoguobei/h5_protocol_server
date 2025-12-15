"""
协议文件操作服务
"""
import os
import re
import uuid
import time
from pathlib import Path
from datetime import datetime, timedelta
from config import FRONTEND_DIR
from db.database import db
from db.models import Protocol

# 内存存储预览内容
_preview_storage = {}
_CLEANUP_INTERVAL = 300
_last_cleanup = time.time()


def _get_protocol_dir():
    """获取协议文件目录"""
    protocol_dir = Path(FRONTEND_DIR) / 'public' / 'static' / 'notice'
    protocol_dir.mkdir(parents=True, exist_ok=True)
    return protocol_dir


def extract_title_from_html(file_path):
    """从HTML文件中提取标题"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # 查找<title>标签中的内容
            title_match = re.search(r'<title[^>]*>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
            if title_match:
                # 移除HTML标签，只保留文本内容，并去除多余的空白字符
                clean_title = re.sub(r'<[^>]+>', '', title_match.group(1)).strip()
                if clean_title:  # 如果提取到的标题不为空
                    return clean_title

            # 如果没有找到title标签或标题为空，尝试查找<h1>标签
            h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', content, re.IGNORECASE | re.DOTALL)
            if h1_match:
                # 移除HTML标签，只保留文本内容，并去除多余的空白字符
                clean_text = re.sub(r'<[^>]+>', '', h1_match.group(1)).strip()
                if clean_text:  # 如果提取到的内容不为空
                    return clean_text

            # 如果都没有找到有效内容，返回空字符串
            return ''
    except Exception:
        # 如果读取或解析失败，返回空字符串
        return ''


def ensure_valid_protocol_entry(entry):
    """确保协议条目包含所有必需字段且值有效"""
    return {
        'filename': entry.get('filename', '') or '',
        'size': int(entry.get('size', 0)) or 0,
        'updateTime': entry.get('updateTime', '') or '1970-01-01 00:00:00',  # 日期时间字符串格式
        'title': entry.get('title', '') or ''  # 没有标题时返回空字符串，而不是默认文本
    }


def get_protocol_list():
    """获取协议文件列表"""
    protocol_dir = _get_protocol_dir()
    files = []
    
    # 获取所有数据库中的协议记录，建立文件名到协议对象的映射
    all_protocols = Protocol.query.all()
    print(f"数据库中查询到 {len(all_protocols)} 条协议记录")
    db_protocols = {p.filename: p for p in all_protocols}
    
    for file_path in protocol_dir.glob('*.html'):
        try:
            stat = file_path.stat()
            filename = file_path.name
            # title = extract_title_from_html(file_path)
            formatted_time = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            
            # 从数据库获取协议属性
            protocol = db_protocols.get(filename)
            
            files.append({
                'id': protocol.id if protocol else None,
                'filename': filename,
                'size': int(stat.st_size),
                'updateTime': formatted_time,
                # 'title': title,
                'description': protocol.description if protocol else None,
                'app_type': protocol.app_type if protocol else None,
                'app_name': protocol.app_name if protocol else None
            })
        except Exception as e:
            print(f"处理协议文件时出错 {file_path}: {str(e)}")
            continue
    
    # 按修改时间排序
    files.sort(key=lambda x: x['updateTime'], reverse=True)
    return files


def get_protocol(filename):
    """获取协议内容"""
    safe_filename = os.path.basename(filename)
    protocol = Protocol.query.filter_by(filename=safe_filename).first()
    if not protocol:
        raise FileNotFoundError(f'协议文件不存在: {safe_filename}')
    
    file_path = _get_protocol_dir() / safe_filename
    if not file_path.exists():
        raise FileNotFoundError(f'协议文件不存在: {safe_filename}')
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    result = protocol.to_dict()
    result['content'] = content
    return result


def create_protocol(filename, content, description=None, app_type=None, app_name=None):
    """创建协议文件"""
    if not filename.endswith('.html'):
        filename += '.html'
    
    safe_filename = os.path.basename(filename)
    
    if Protocol.query.filter_by(filename=safe_filename).first():
        raise FileExistsError(f'协议文件已存在: {safe_filename}')
    
    file_path = _get_protocol_dir() / safe_filename
    if file_path.exists():
        raise FileExistsError(f'协议文件已存在: {safe_filename}')
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    protocol = Protocol(
        filename=safe_filename,
        description=description,
        app_type=app_type,
        app_name=app_name
    )
    db.session.add(protocol)
    db.session.commit()
    
    return safe_filename


def update_protocol(filename, content=None, description=None, app_type=None, app_name=None):
    """更新协议文件"""
    safe_filename = os.path.basename(filename)
    protocol = Protocol.query.filter_by(filename=safe_filename).first()
    if not protocol:
        raise FileNotFoundError(f'协议文件不存在: {safe_filename}')
    
    if content is not None:
        file_path = _get_protocol_dir() / safe_filename
        if not file_path.exists():
            raise FileNotFoundError(f'协议文件不存在: {safe_filename}')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    if description is not None:
        protocol.description = description
    if app_type is not None:
        protocol.app_type = app_type
    if app_name is not None:
        protocol.app_name = app_name
    
    db.session.commit()


def delete_protocol(filename):
    """删除协议文件"""
    safe_filename = os.path.basename(filename)
    protocol = Protocol.query.filter_by(filename=safe_filename).first()
    if not protocol:
        raise FileNotFoundError(f'协议文件不存在: {safe_filename}')
    
    file_path = _get_protocol_dir() / safe_filename
    if file_path.exists():
        file_path.unlink()
    
    db.session.delete(protocol)
    db.session.commit()


def _cleanup_expired_previews():
    """清理过期的预览内容"""
    global _last_cleanup
    current_time = time.time()
    
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
    """创建预览，返回预览 ID"""
    if not html_content:
        raise ValueError('HTML 内容不能为空')
    
    _cleanup_expired_previews()
    preview_id = str(uuid.uuid4())
    expires_at = datetime.now() + timedelta(hours=1)
    
    _preview_storage[preview_id] = {
        'content': html_content,
        'expires_at': expires_at
    }
    
    return preview_id


def get_preview_content(preview_id):
    """获取预览内容"""
    if preview_id not in _preview_storage:
        raise ValueError('预览不存在或已过期')
    
    data = _preview_storage[preview_id]
    
    if data['expires_at'] < datetime.now():
        del _preview_storage[preview_id]
        raise ValueError('预览已过期')
    
    return data['content']
