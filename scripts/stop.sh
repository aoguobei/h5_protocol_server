#!/bin/bash
# 停止脚本

pkill -f "gunicorn.*app:app"
echo "服务已停止"
