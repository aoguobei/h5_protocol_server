"""
Git 操作服务
"""
import subprocess
import shutil
import platform
import os
from pathlib import Path
from config import FRONTEND_DIR

# Windows 系统需要使用 shell=True 来执行命令
USE_SHELL = platform.system() == 'Windows'


def _check_git_repo():
    """检查前端项目目录和 Git 仓库"""
    frontend_path = Path(FRONTEND_DIR)
    if not frontend_path.exists():
        raise FileNotFoundError('前端项目目录不存在')

    git_dir = frontend_path / '.git'
    if not git_dir.exists():
        raise RuntimeError(f'前端项目目录不是 Git 仓库: {frontend_path}')

    return frontend_path


def _run_git_command(cmd, cwd=None, timeout=None, force_no_shell=False, env=None):
    """执行 Git 命令的公共函数

    Args:
        cmd: 命令，可以是字符串或列表
        cwd: 工作目录，默认为前端项目目录
        timeout: 超时时间（秒）
        force_no_shell: 强制不使用 shell（用于包含 % 符号的命令）
        env: 自定义环境变量字典，如果为 None 则使用当前环境
    """
    if cwd is None:
        cwd = _check_git_repo()
    else:
        cwd = Path(cwd)

    # 确保命令是列表格式
    if isinstance(cmd, str):
        cmd_list = cmd.split()
    else:
        cmd_list = cmd

    # 对于包含 % 符号的命令（如 git log 的 format），必须使用 shell=False
    # 或者在 Windows 上强制不使用 shell
    use_shell = USE_SHELL and not force_no_shell

    # 处理环境变量
    if env is not None:
        # 复制当前环境变量，然后更新
        process_env = os.environ.copy()
        process_env.update(env)
    else:
        process_env = None

    try:
        result = subprocess.run(
            cmd_list,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            encoding='utf-8',
            shell=use_shell,
            timeout=timeout,
            env=process_env
        )
    except FileNotFoundError as e:
        raise RuntimeError(f'Git 命令未找到，请确保 Git 已安装并添加到 PATH 环境变量中: {str(e)}')
    except subprocess.TimeoutExpired:
        raise RuntimeError('Git 命令执行超时')
    except Exception as e:
        raise RuntimeError(f'执行 Git 命令时发生异常: {str(e)}')

    return result


def _get_command_output(result):
    """获取命令输出，合并 stdout 和 stderr"""
    if result.stderr:
        return result.stdout + result.stderr
    return result.stdout or ''


def _format_error(result, default_msg='未知错误'):
    """格式化错误信息"""
    error_details = []
    if result.stderr:
        error_details.append(f'stderr: {result.stderr}')
    if result.stdout:
        error_details.append(f'stdout: {result.stdout}')
    if result.returncode:
        error_details.append(f'返回码: {result.returncode}')

    return ' | '.join(error_details) if error_details else default_msg


def get_git_status():
    """获取 Git 状态和变更文件"""
    frontend_path = _check_git_repo()

    # 检查工作区是否干净
    result = _run_git_command(['git', 'status', '--porcelain'], cwd=frontend_path)

    if result.returncode != 0:
        error_msg = _format_error(result)
        raise RuntimeError(f'Git 命令执行失败: {error_msg}')

    # 解析变更文件
    changed_files = []
    if result.stdout.strip():
        # 保留每行的原始格式，只分割行，不使用strip()去除行首空格
        for line in result.stdout.split('\n'):
            # 确保行不为空
            if line and line.strip():  # 只有当行存在且去除首尾空格后不为空时才处理
                # Git status --porcelain 格式：前两个字符是状态，然后是空格，然后是文件名
                # 例如：' M public/static/notice/test111.html' (index未修改，工作区修改)
                #      'M  public/static/notice/test11.html' (index修改，工作区未修改)
                #      'MM public/static/notice/test11.html' (index和工作区都修改)
                # Git status --porcelain格式：始终是两个字符的状态，然后是空格，然后是文件名
                # ' M' = 工作区修改 (index未修改，工作区修改) - 注意是空格+M，不是M+空格
                # 'M ' = 暂存区修改 (index修改，工作区未修改)
                # 'MM' = 工作区和暂存区都修改
                # '??' = 未跟踪
                status = line[:2]  # 前两个字符始终是状态，保留原始格式
                # 从第3个字符开始（索引2），跳过空格，找到文件名
                pos = 2
                while pos < len(line) and line[pos] == ' ':
                    pos += 1
                filename = line[pos:] if pos < len(line) else ''

                changed_files.append({
                    'status': status,
                    'filename': filename
                })

    is_clean = len(changed_files) == 0

    # 获取当前分支
    try:
        branch_result = _run_git_command(['git', 'branch', '--show-current'], cwd=frontend_path)
        current_branch = branch_result.stdout.strip() if branch_result.returncode == 0 else 'unknown'
    except Exception:
        current_branch = 'unknown'

    return {
        'is_clean': is_clean,
        'current_branch': current_branch,
        'changed_files': changed_files
    }


def get_git_log(limit=15):
    """获取 Git 提交历史"""
    frontend_path = _check_git_repo()

    # 获取提交历史
    # 使用列表方式传递参数，并强制不使用 shell，避免 Windows 命令行解析 % 符号的问题
    result = _run_git_command(
        ['git', 'log', f'-{limit}', '--pretty=format:%H|%an|%ae|%ad|%s', '--date=iso'],
        cwd=frontend_path,
        timeout=30,
        force_no_shell=True  # 强制不使用 shell，避免 % 符号被解析
    )

    if result.returncode != 0:
        error_msg = _format_error(result)
        raise RuntimeError(f'Git log 命令执行失败: {error_msg}')

    commits = []
    if result.stdout:
        for line in result.stdout.strip().split('\n'):
            if line.strip():
                parts = line.split('|', 4)
                if len(parts) == 5:
                    commits.append({
                        'hash': parts[0][:8],  # 只显示前8位
                        'full_hash': parts[0],
                        'author': parts[1],
                        'email': parts[2],
                        'date': parts[3],
                        'message': parts[4]
                    })

    return commits


def get_branch_status():
    """获取分支的领先和落后状态"""
    frontend_path = _check_git_repo()

    # 获取当前分支
    branch_result = _run_git_command(['git', 'branch', '--show-current'], cwd=frontend_path)

    if branch_result.returncode != 0:
        error_msg = _format_error(branch_result)
        raise RuntimeError(f'无法获取当前分支: {error_msg}')

    current_branch = branch_result.stdout.strip()

    # 先执行 git fetch 更新远程分支信息（但不合并）
    _run_git_command(['git', 'fetch'], cwd=frontend_path)

    # 获取本地和远程的提交数差异
    # ahead: 本地领先远程的提交数 (origin/branch..branch)
    ahead_result = _run_git_command(
        ['git', 'rev-list', f'origin/{current_branch}..{current_branch}', '--count'],
        cwd=frontend_path
    )

    # behind: 本地落后远程的提交数 (branch..origin/branch)
    behind_result = _run_git_command(
        ['git', 'rev-list', f'{current_branch}..origin/{current_branch}', '--count'],
        cwd=frontend_path
    )

    # 检查远程分支是否存在
    remote_branch_check = _run_git_command(
        ['git', 'ls-remote', '--heads', 'origin', current_branch],
        cwd=frontend_path
    )

    has_remote = remote_branch_check.returncode == 0 and remote_branch_check.stdout.strip() != ''

    ahead = 0
    behind = 0

    if has_remote:
        try:
            ahead = int(ahead_result.stdout.strip()) if ahead_result.returncode == 0 else 0
            behind = int(behind_result.stdout.strip()) if behind_result.returncode == 0 else 0
        except ValueError:
            pass

    return {
        'current_branch': current_branch,
        'has_remote': has_remote,
        'ahead': ahead,  # 本地领先远程的提交数
        'behind': behind  # 本地落后远程的提交数
    }


def pull_latest():
    """拉取最新代码"""
    frontend_path = _check_git_repo()

    # 检查工作区是否干净
    status_result = _run_git_command(['git', 'status', '--porcelain'], cwd=frontend_path)

    if status_result.stdout.strip():
        raise ValueError('工作区不干净，请先提交或暂存变更')

    # 执行 git pull
    result = _run_git_command(['git', 'pull'], cwd=frontend_path)

    if result.returncode != 0:
        error_msg = _format_error(result)
        raise RuntimeError(f'拉取失败: {error_msg}')

    return {
        'message': '拉取成功',
        'output': result.stdout
    }


def deploy(commit_message):
    """执行部署流程"""
    if not commit_message:
        raise ValueError('提交信息不能为空')

    frontend_path = _check_git_repo()
    steps = []

    # 1. git add .
    result = _run_git_command(['git', 'add', '.'], cwd=frontend_path)
    if result.returncode != 0:
        error_msg = _format_error(result)
        raise RuntimeError(f'git add 失败: {error_msg}')
    output = _get_command_output(result)
    steps.append({'step': 'git add', 'status': 'success', 'output': output or '执行成功'})

    # 2. git commit
    result = _run_git_command(['git', 'commit', '-m', commit_message], cwd=frontend_path)
    if result.returncode != 0:
        error_msg = _format_error(result)
        raise RuntimeError(f'git commit 失败: {error_msg}')
    output = _get_command_output(result)
    steps.append({'step': 'git commit', 'status': 'success', 'output': output or '执行成功'})

    # 3. git push origin master
    result = _run_git_command(['git', 'push', 'origin', 'master'], cwd=frontend_path)
    if result.returncode != 0:
        error_msg = _format_error(result)
        raise RuntimeError(f'git push origin master 失败: {error_msg}')
    output = _get_command_output(result)
    steps.append({'step': 'git push origin master', 'status': 'success', 'output': output or '推送成功'})

    # 4. npm run build
    # 设置 NODE_OPTIONS 环境变量以解决 Node.js 17+ 的 OpenSSL 兼容性问题
    build_env = {'NODE_OPTIONS': '--openssl-legacy-provider'}
    # 打印实际执行的命令
    command_info = f"执行命令: npm run build\n工作目录: {frontend_path}\n环境变量: NODE_OPTIONS={build_env['NODE_OPTIONS']}"
    result = _run_git_command(['npm', 'run', 'build'], cwd=frontend_path, env=build_env)
    if result.returncode != 0:
        error_msg = _format_error(result)
        full_output = f"{command_info}\n\n{error_msg}"
        raise RuntimeError(f'npm run build 失败: {full_output}')
    output = _get_command_output(result)
    full_output = f"{command_info}\n\n{output or '构建成功'}"
    steps.append({'step': 'npm run build', 'status': 'success', 'output': full_output})

    # 5. 备份 dist 目录
    dist_path = frontend_path / 'dist'
    dist_backup_path = frontend_path / 'dist_backup'

    if dist_path.exists():
        if dist_backup_path.exists():
            shutil.rmtree(dist_backup_path)
        shutil.copytree(dist_path, dist_backup_path)
        steps.append({'step': '备份 dist 目录', 'status': 'success', 'output': 'dist_backup'})
    else:
        raise RuntimeError('dist 目录不存在，构建可能失败')

    # 6. 切换到 alpha 分支
    result = _run_git_command(['git', 'checkout', 'alpha'], cwd=frontend_path)
    if result.returncode != 0:
        error_msg = _format_error(result)
        raise RuntimeError(f'切换到 alpha 分支失败: {error_msg}')
    output = _get_command_output(result)
    steps.append({'step': '切换到 alpha 分支', 'status': 'success', 'output': output or '切换成功'})

    # 7. git pull
    result = _run_git_command(['git', 'pull'], cwd=frontend_path)
    if result.returncode != 0:
        error_msg = _format_error(result)
        raise RuntimeError(f'git pull 失败: {error_msg}')
    output = _get_command_output(result)
    steps.append({'step': 'git pull', 'status': 'success', 'output': output or '拉取成功'})

    # 8. 替换 alpha 分支的 dist 目录
    if dist_path.exists():
        shutil.rmtree(dist_path)
    shutil.copytree(dist_backup_path, dist_path)
    steps.append({'step': '替换 dist 目录', 'status': 'success', 'output': '替换完成'})

    # 9. git add dist
    result = _run_git_command(['git', 'add', 'dist'], cwd=frontend_path)
    if result.returncode != 0:
        error_msg = _format_error(result)
        raise RuntimeError(f'git add dist 失败: {error_msg}')
    output = _get_command_output(result)
    steps.append({'step': 'git add dist', 'status': 'success', 'output': output or '执行成功'})

    # 10. git commit (alpha 分支)
    result = _run_git_command(['git', 'commit', '-m', commit_message], cwd=frontend_path)
    # commit 可能失败（如果没有变更），不算错误
    if result.returncode == 0:
        output = _get_command_output(result)
        steps.append({'step': 'git commit (alpha)', 'status': 'success', 'output': output or '提交成功'})
    else:
        output = result.stderr or result.stdout or '无变更，跳过提交'
        steps.append({'step': 'git commit (alpha)', 'status': 'warning', 'output': output})

    # 11. git push origin alpha
    result = _run_git_command(['git', 'push', 'origin', 'alpha'], cwd=frontend_path)
    if result.returncode != 0:
        error_msg = _format_error(result)
        raise RuntimeError(f'git push origin alpha 失败: {error_msg}')
    output = _get_command_output(result)
    steps.append({'step': 'git push origin alpha', 'status': 'success', 'output': output or '推送成功'})

    # 12. 切换回 master 分支
    result = _run_git_command(['git', 'checkout', 'master'], cwd=frontend_path)
    if result.returncode != 0:
        output = _format_error(result, default_msg='切换失败')
        steps.append({'step': '切换回 master', 'status': 'warning', 'output': output})
    else:
        output = _get_command_output(result)
        steps.append({'step': '切换回 master', 'status': 'success', 'output': output or '切换成功'})

    # 清理备份目录
    if dist_backup_path.exists():
        shutil.rmtree(dist_backup_path)

    return {
        'message': '部署成功',
        'steps': steps
    }
