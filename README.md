# h5协议自动化后端

基于 Flask 的协议管理 API 服务。

## 功能特性

- ✅ 协议文件的 CRUD 操作
- ✅ HTML 格式验证
- ✅ 文件列表查询
- ✅ CORS 支持

## 技术栈

- Python 3.8+
- Flask
- BeautifulSoup4（HTML 解析和验证）
- Flask-CORS

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置

在 `app.py` 中修改 `PROTOCOL_DIR` 变量，指向实际的协议文件目录：

```python
PROTOCOL_DIR = r'C:\F_explorer\miniprogram\h5_miniapp1\h5_miniapp\public\static\notice'
```

## 运行

```bash
python app.py
```

服务将在 http://localhost:5000 启动

## API 接口

### GET /api/protocols
获取协议列表

### GET /api/protocols/:filename
获取指定协议内容

### POST /api/protocols
创建新协议
- Body: `{ "filename": "xxx.html", "content": "<html>..." }`

### PUT /api/protocols/:filename
更新协议
- Body: `{ "content": "<html>..." }`

### DELETE /api/protocols/:filename
删除协议
