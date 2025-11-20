import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent.parent  # 返回到项目根目录

# 前端项目目录
FRONTEND_DIR = 'C:\F_explorer\miniprogram\h5_miniapp1\h5_miniapp'

class Config:
    # 数据库配置
    # MySQL数据库配置 - 请根据实际情况修改
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_PORT = os.environ.get('MYSQL_PORT') or '3306'
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or 'aoguobei-otzf'
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE') or 'h5_protocol_db'

    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 密钥
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-for-testing'

    # 前端目录配置
    FRONTEND_DIR = FRONTEND_DIR
