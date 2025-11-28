#!/bin/bash

# 部署脚本

echo "开始部署后端服务..."

# 1. 停止旧服务
echo "停止旧服务..."
pkill -f gunicorn || true

## 2. 更新代码
#echo "更新代码..."
#git pull

# 3. 安装依赖
echo "安装依赖..."
pip3 install -r requirements.txt

# 4. 创建必要的目录
mkdir -p logs

# 5. 初始化数据库（如果需要）
#手动创建数据库
#CREATE DATABASE h5_protocol_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
#建表
#python3 ../db/init_db.py

# 6. 启动服务
echo "启动服务..."
nohup gunicorn -c gunicorn_config.py app:app > logs/server.log 2>&1 &

echo "部署完成！"
echo "PID: $!"
echo "查看日志: tail -f logs/server.log"
