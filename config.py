import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 项目根目录
BASE_DIR = Path(__file__).parent.parent  # 返回到项目根目录

# 协议项目目录（从环境变量读取）
FRONTEND_DIR = os.environ.get('FRONTEND_DIR')

class Config:
    # 数据库配置（从环境变量读取）
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_PORT = os.environ.get('MYSQL_PORT') or '3306'
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE') or 'h5_protocol_db'

    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 密钥
    SECRET_KEY = os.environ.get('SECRET_KEY')

    # 前端目录配置
    FRONTEND_DIR = FRONTEND_DIR
