"""
协议相关路由
"""
from flask import Blueprint, request, jsonify
from services.protocol_service import (
    get_protocol_list,
    get_protocol,
    create_protocol,
    update_protocol,
    delete_protocol
)
from services.preview_service import create_preview, get_preview_content

protocol_bp = Blueprint('protocol', __name__, url_prefix='/api/protocols')


@protocol_bp.route('', methods=['GET'])
def list_protocols():
    """获取协议列表"""
    try:
        files = get_protocol_list()
        return jsonify(files), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@protocol_bp.route('/<path:filename>', methods=['GET'])
def retrieve_protocol(filename):
    """获取协议内容"""
    try:
        data = get_protocol(filename)
        return jsonify(data), 200
    except FileNotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@protocol_bp.route('', methods=['POST'])
def create():
    """创建新协议"""
    try:
        data = request.json
        filename = data.get('filename')
        content = data.get('content')
        
        created_filename = create_protocol(filename, content)
        return jsonify({'message': '创建成功', 'filename': created_filename}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except FileExistsError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@protocol_bp.route('/<path:filename>', methods=['PUT'])
def update(filename):
    """更新协议"""
    try:
        data = request.json
        content = data.get('content')
        
        update_protocol(filename, content)
        return jsonify({'message': '更新成功'}), 200
    except FileNotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@protocol_bp.route('/<path:filename>', methods=['DELETE'])
def delete(filename):
    """删除协议"""
    try:
        delete_protocol(filename)
        return jsonify({'message': '删除成功'}), 200
    except FileNotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@protocol_bp.route('/preview', methods=['POST'])
def create_preview_route():
    """创建预览，返回预览 ID"""
    try:
        data = request.json
        html_content = data.get('content', '')
        
        if not html_content:
            return jsonify({'error': 'HTML 内容不能为空'}), 400
        
        preview_id = create_preview(html_content)
        # 返回预览 URL（前端可以通过这个 URL 访问预览内容）
        preview_url = f'/api/protocols/preview/{preview_id}'
        return jsonify({'url': preview_url, 'id': preview_id}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@protocol_bp.route('/preview/<preview_id>', methods=['GET'])
def get_preview_route(preview_id):
    """获取预览内容"""
    try:
        html_content = get_preview_content(preview_id)
        # 返回 HTML 内容，设置正确的 Content-Type
        from flask import Response
        return Response(html_content, mimetype='text/html; charset=utf-8')
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

