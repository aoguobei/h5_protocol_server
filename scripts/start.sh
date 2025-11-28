#!/bin/bash
# 启动脚本

# 进入项目根目录
cd "$(dirname "$0")/.."

# 创建日志目录
mkdir -p logs

# 后台启动服务
nohup gunicorn -c gunicorn_config.py app:app > logs/server.log 2>&1 &

echo "服务已启动，PID: $!"
echo "查看日志: tail -f logs/server.log"
