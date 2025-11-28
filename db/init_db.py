"""
初始化数据库脚本
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app
from db.database import db
from db.models import User

def init_database():
    app = create_app()
    with app.app_context():
        try:
            # 创建所有表
            db.create_all()

            # 检查是否已存在管理员用户
            admin_user = User.query.filter_by(username='admin').first()
            if not admin_user:
                # 创建管理员用户
                admin_user = User(
                    username='admin',
                    role='admin'
                )
                admin_user.set_password('admin123')  # 默认密码
                db.session.add(admin_user)
                db.session.commit()
                print("管理员账户已创建: admin / admin123")
            else:
                print("管理员账户已存在")

            print("数据库初始化完成")
        except Exception as e:
            print(f"数据库初始化失败: {str(e)}")
            print("请检查MySQL连接配置是否正确")
            print("确保MySQL服务器正在运行并且凭据正确")

if __name__ == '__main__':
    init_database()
