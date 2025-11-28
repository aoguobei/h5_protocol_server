# 后端部署指南（Linux 服务器）

### 1. 上传文件到服务器
```bash
# 将整个项目上传到服务器
scp -r h5_protocol_server user@server:/var/www/
```

### 2. 服务器上安装依赖
```bash
cd /var/www/h5_protocol_server
pip3 install -r requirements.txt
pip3 install gunicorn
```

### 3. 配置环境变量
```bash
# 复制并修改配置文件
cp .env.production .env
nano .env  # 修改 SECRET_KEY 和 FRONTEND_DIR
```

### 4. 初始化数据库
```bash
python3 init_db.py
```

### 5. 启动服务
```bash
# 方式1：使用脚本（推荐）
chmod +x scripts/*.sh
./scripts/start.sh

# 方式2：后台运行
nohup ./scripts/start.sh > logs/server.log 2>&1 &

# 方式3：使用部署脚本（自动化）
./scripts/deploy.sh
```

### 6. 停止服务
```bash
./scripts/stop.sh
```

### 7. 查看日志
```bash
tail -f logs/server.log
```

---

## Nginx 配置（推荐）

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location /protocol/ {
        alias /var/www/h5_protocol_front/dist/;
        try_files $uri $uri/ /protocol/index.html;
    }

    # 后端 API
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

---

## 常用命令

```bash
# 查看进程
ps aux | grep gunicorn

# 重启服务
pkill -f gunicorn && gunicorn -c gunicorn_config.py app:app

# 查看端口占用
netstat -tlnp | grep 5000

# 查看日志
tail -f logs/error.log
tail -f logs/access.log
```
