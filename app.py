"""
Flask 应用主文件
"""
from flask import Flask
from flask_cors import CORS
from routes.protocol_routes import protocol_bp
from routes.git_routes import git_bp

app = Flask(__name__)
CORS(app)

# 注册蓝图
app.register_blueprint(protocol_bp)
app.register_blueprint(git_bp)

if __name__ == '__main__':
    app.run(debug=True, port=5000)

