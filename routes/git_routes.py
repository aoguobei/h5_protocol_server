"""
Git 相关路由
"""
from flask import Blueprint, request, jsonify
from services.git_service import get_git_status, pull_latest, deploy, get_git_log, get_branch_status

git_bp = Blueprint('git', __name__, url_prefix='/api/git')


@git_bp.route('/status', methods=['GET'])
def status():
    """获取 Git 状态和变更文件"""
    try:
        data = get_git_status()
        return jsonify(data), 200
    except FileNotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except RuntimeError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@git_bp.route('/log', methods=['GET'])
def log():
    """获取 Git 提交历史"""
    try:
        limit = request.args.get('limit', 15, type=int)
        commits = get_git_log(limit)
        return jsonify(commits), 200
    except FileNotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except RuntimeError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@git_bp.route('/branch-status', methods=['GET'])
def branch_status():
    """获取分支的领先和落后状态"""
    try:
        data = get_branch_status()
        return jsonify(data), 200
    except FileNotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except RuntimeError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@git_bp.route('/pull', methods=['POST'])
def pull():
    """拉取最新代码"""
    try:
        data = pull_latest()
        return jsonify(data), 200
    except FileNotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except RuntimeError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@git_bp.route('/deploy', methods=['POST'])
def deploy_route():
    """执行部署流程"""
    try:
        data = request.json
        commit_message = data.get('commit_message', '')
        
        result = deploy(commit_message)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except FileNotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except RuntimeError as e:
        # 如果部署失败，返回已执行的步骤
        error_message = str(e)
        # 尝试从异常中获取步骤信息（如果有的话）
        steps = getattr(e, 'steps', [])
        return jsonify({'error': error_message, 'steps': steps}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

