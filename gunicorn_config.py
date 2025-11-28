# Gunicorn 配置文件
import multiprocessing

# 绑定地址和端口
bind = "0.0.0.0:5000"

# 工作进程数（推荐：CPU核心数 * 2 + 1）
workers = multiprocessing.cpu_count() * 2 + 1

# 工作模式
worker_class = "sync"

# 超时时间（秒）
timeout = 120

# 日志
accesslog = "logs/access.log"
errorlog = "logs/error.log"
loglevel = "info"

# 进程名称
proc_name = "h5_protocol_server"
