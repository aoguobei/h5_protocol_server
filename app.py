"""
Flask 应用主文件
"""
from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from config import Config

# 创建扩展实例
from db.database import db
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login' # 指定「登录页面的路由端点（endpoint）」
    login_manager.login_message = '请先登录以访问此页面。' # 设置「未登录用户被重定向时，显示的提示消息」

    CORS(app)

    # 导入并注册蓝图
    from routes.auth_routes import auth_bp
    from routes.protocol_routes import protocol_bp
    from routes.git_routes import git_bp
    from routes.user_routes import user_bp
    from routes.log_routes import log_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(protocol_bp)
    app.register_blueprint(git_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(log_bp)

    return app

# 创建应用实例
app = create_app()

@login_manager.user_loader
def load_user(user_id):
    from db.models import User
    return db.session.get(User, int(user_id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
