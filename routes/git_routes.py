"""
Git 相关路由
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from services.git_service import get_git_status, pull_latest, deploy, get_git_log, get_branch_status
from utils.auth import require_login, require_role
from db.models import OperationLog
from db.database import db

def get_db():
    return db

git_bp = Blueprint('git', __name__, url_prefix='/api/git')


@git_bp.route('/status', methods=['GET'])
@require_login
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
@require_login
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
@require_login
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
@require_role('admin', 'editor')
def pull():
    """拉取最新代码"""
    try:
        data = pull_latest()

        # 记录操作日志
        log = OperationLog(
            user_id=current_user.id,
            action='git_pull',
            resource_type='git',
            resource_name='repository',
            details=f'执行了git pull操作，获取了最新代码'
        )
        database = get_db()
        database.session.add(log)
        database.session.commit()

        return jsonify(data), 200
    except FileNotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except RuntimeError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        database = get_db()
        database.session.rollback()
        return jsonify({'error': str(e)}), 500


@git_bp.route('/deploy', methods=['POST'])
@require_role('admin', 'editor')
def deploy_route():
    """执行部署流程"""
    try:
        data = request.json
        commit_message = data.get('commit_message', '')

        result = deploy(commit_message)

        # 记录操作日志
        log = OperationLog(
            user_id=current_user.id,
            action='git_deploy',
            resource_type='git',
            resource_name='repository',
            details=f'执行了部署操作，提交信息: {commit_message}'
        )
        database = get_db()
        database.session.add(log)
        database.session.commit()

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
        database = get_db()
        database.session.rollback()
        return jsonify({'error': str(e)}), 500
