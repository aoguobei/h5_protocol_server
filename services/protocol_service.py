"""
协议文件服务
"""
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import unquote
from config import PROTOCOL_DIR


def get_protocol_list():
    """获取协议列表"""
    files = []
    protocol_path = Path(PROTOCOL_DIR)
    
    if not protocol_path.exists():
        return []
    
    for file in protocol_path.glob('*.html'):
        stat = file.stat()
        
        # 使用正则表达式快速提取 title 标签内容（只读取文件前 50KB）
        title = ''
        try:
            with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                # 只读取前 50KB，title 通常在前面的 head 标签中
                content = f.read(50 * 1024)
                # 使用正则表达式匹配 title 标签
                title_match = re.search(r'<title[^>]*>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
                if title_match:
                    title = title_match.group(1).strip()
                    # 清理 HTML 实体和多余空白
                    title = re.sub(r'\s+', ' ', title)
        except Exception:
            # 如果提取失败，title 保持为空
            pass
        
        files.append({
            'filename': file.name,
            'size': stat.st_size,
            'updateTime': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
            'title': title
        })
    
    # 按更新时间排序
    files.sort(key=lambda x: x['updateTime'], reverse=True)
    return files


def get_protocol(filename):
    """获取协议内容"""
    filename = unquote(filename)
    file_path = Path(PROTOCOL_DIR) / filename
    
    if not file_path.exists():
        raise FileNotFoundError(f'文件不存在: {filename}')
    
    # 使用二进制模式读取，检测原始行结束符
    with open(file_path, 'rb') as f:
        raw_content = f.read()
    
    # 检测行结束符类型
    if b'\r\n' in raw_content:
        newline = '\r\n'
    elif b'\r' in raw_content:
        newline = '\r'
    else:
        newline = '\n'
    
    # 解码内容
    content = raw_content.decode('utf-8')
    
    return {
        'filename': filename,
        'content': content,
        'newline': newline
    }


def create_protocol(filename, content):
    """创建新协议"""
    if not filename:
        raise ValueError('文件名不能为空')
    
    if not filename.endswith('.html'):
        filename += '.html'
    
    file_path = Path(PROTOCOL_DIR) / filename
    
    if file_path.exists():
        raise FileExistsError('文件已存在')
    
    # 统一内容中的行结束符为 \n
    normalized_content = content.replace('\r\n', '\n').replace('\r', '\n')
    
    # 直接保存，不进行任何 HTML 解析或格式化，保持原始格式
    with open(file_path, 'w', encoding='utf-8', newline='') as f:
        f.write(normalized_content)
    
    return filename


def update_protocol(filename, content):
    """更新协议"""
    filename = unquote(filename)
    file_path = Path(PROTOCOL_DIR) / filename
    
    if not file_path.exists():
        raise FileNotFoundError('文件不存在')
    
    # 检测原始文件的行结束符类型
    with open(file_path, 'rb') as f:
        original_content = f.read()
    
    if b'\r\n' in original_content:
        newline = '\r\n'
    elif b'\r' in original_content:
        newline = '\r'
    else:
        newline = '\n'
    
    # 统一内容中的行结束符为原始格式
    # 先统一为 \n，然后替换为原始格式
    normalized_content = content.replace('\r\n', '\n').replace('\r', '\n')
    if newline != '\n':
        normalized_content = normalized_content.replace('\n', newline)
    
    # 直接保存，不进行任何 HTML 解析或格式化，保持原始格式
    with open(file_path, 'w', encoding='utf-8', newline='') as f:
        f.write(normalized_content)


def delete_protocol(filename):
    """删除协议"""
    filename = unquote(filename)
    file_path = Path(PROTOCOL_DIR) / filename
    
    if not file_path.exists():
        raise FileNotFoundError('文件不存在')
    
    file_path.unlink()

