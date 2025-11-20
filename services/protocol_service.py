"""
协议文件操作服务
"""
import os
import re
from pathlib import Path
from datetime import datetime
from config import FRONTEND_DIR


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

    for file_path in protocol_dir.glob('*.html'):
        try:
            stat = file_path.stat()
            # 尝试从HTML文件中提取标题，如果失败则使用文件名作为标题
            title = extract_title_from_html(file_path)
            # 将时间戳转换为格式化的日期时间字符串，便于前端显示
            formatted_time = datetime.fromtimestamp(stat.st_mtime if stat else 0).strftime('%Y-%m-%d %H:%M:%S')
            files.append({
                'filename': file_path.name or '',
                'size': int(stat.st_size) if stat else 0,
                'updateTime': formatted_time, # 使用格式化的日期时间字符串
                'title': title  # 直接使用提取的标题，如果提取失败则为已返回的空字符串
            })
        except Exception as e:
            # 如果处理单个文件失败，跳过该文件并记录错误
            print(f"处理协议文件时出错 {file_path}: {str(e)}")
            continue

    # 确保所有条目都包含必需字段并具有有效值
    valid_files = [ensure_valid_protocol_entry(entry) for entry in files]
    # 按修改时间排序，最新的在前 (时间字符串格式为 'YYYY-MM-DD HH:MM:SS', 可以直接比较)
    valid_files.sort(key=lambda x: x['updateTime'], reverse=True)
    return valid_files


def get_protocol(filename):
    """获取协议内容"""
    # 防止路径遍历攻击
    safe_filename = os.path.basename(filename)
    file_path = _get_protocol_dir() / safe_filename

    if not file_path.exists():
        raise FileNotFoundError(f'协议文件不存在: {safe_filename}')

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    return {
        'filename': safe_filename,
        'content': content
    }


def create_protocol(filename, content):
    """创建协议文件"""
    # 验证文件名
    if not filename.endswith('.html'):
        filename += '.html'

    # 防止路径遍历攻击
    safe_filename = os.path.basename(filename)
    file_path = _get_protocol_dir() / safe_filename

    # 检查文件是否已存在
    if file_path.exists():
        raise FileExistsError(f'协议文件已存在: {safe_filename}')

    # 写入文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return safe_filename


def update_protocol(filename, content):
    """更新协议文件"""
    # 防止路径遍历攻击
    safe_filename = os.path.basename(filename)
    file_path = _get_protocol_dir() / safe_filename

    if not file_path.exists():
        raise FileNotFoundError(f'协议文件不存在: {safe_filename}')

    # 写入文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


def delete_protocol(filename):
    """删除协议文件"""
    # 防止路径遍历攻击
    safe_filename = os.path.basename(filename)
    file_path = _get_protocol_dir() / safe_filename

    if not file_path.exists():
        raise FileNotFoundError(f'协议文件不存在: {safe_filename}')

    file_path.unlink()  # 删除文件
