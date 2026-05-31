# API 文档生成器

从 Python 代码自动生成 API 文档，支持 FastAPI/Flask/Django，支持自定义模板。

## ✨ 特性

- 🔍 **AST 解析** - 使用 Python AST 深度解析源代码，提取路由、参数、类型注解
- 📝 **多格式输出** - 支持 Markdown、HTML、OpenAPI 3.0 格式
- 🎨 **模板自定义** - 基于 Jinja2 的模板引擎，轻松自定义文档样式
- 🌐 **在线预览** - 内置 FastAPI 服务器，实时预览文档
- 🛠️ **CLI 工具** - 命令行一键生成文档
- 🚀 **框架支持** - 支持 FastAPI、Flask、Django 路由解析

## 📦 安装

```bash
# 克隆项目
git clone <repository-url>
cd api_doc_generator

# 安装依赖
pip install -r requirements.txt
```

## 🚀 快速开始

### 命令行使用

```bash
# 生成 Markdown 文档
python -m api_doc_generator.cli generate ./my_api -f markdown -o api_docs.md

# 生成 HTML 文档
python -m api_doc_generator.cli generate ./my_api -f html -o api_docs.html

# 生成 OpenAPI 文档
python -m api_doc_generator.cli generate ./my_api -f openapi -o openapi.json

# 查看 API 信息
python -m api_doc_generator.cli info ./my_api

# 启动在线预览服务器
python -m api_doc_generator.cli serve ./my_api --port 8080
```

### Python API 使用

```python
from api_doc_generator import DocGenerator

# 创建生成器
generator = DocGenerator()

# 从文件生成文档
doc = generator.generate_from_file("my_api.py", title="My API", version="1.0.0")

# 从目录生成文档
doc = generator.generate_from_directory("./src", title="My API")

# 输出为 Markdown
markdown = generator.to_markdown(doc)

# 输出为 HTML
html = generator.to_html(doc)

# 输出为 OpenAPI
openapi = generator.to_openapi(doc)

# 保存到文件
generator.save_markdown(doc, "api_docs.md")
generator.save_html(doc, "api_docs.html")
generator.save_openapi(doc, "openapi.json")
```

## 📖 使用示例

### 示例代码

```python
# example_api.py
from fastapi import FastAPI, Query
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
    id: int
    name: str
    email: str

@app.get("/users", tags=["users"])
async def get_users(
    page: int = Query(1, description="页码"),
    size: int = Query(10, description="每页数量")
) -> list[User]:
    """获取用户列表
    
    分页获取所有用户信息
    """
    pass

@app.post("/users", tags=["users"])
async def create_user(name: str, email: str) -> User:
    """创建新用户"""
    pass

@app.get("/users/{user_id}", tags=["users"])
async def get_user(user_id: int) -> User:
    """根据ID获取用户信息"""
    pass
```

### 生成文档

```bash
python -m api_doc_generator.cli generate example_api.py -f html -o users_api.html
```

### 自定义模板

创建 `templates/custom.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <title>{{ doc.title }}</title>
</head>
<body>
    <h1>{{ doc.title }} v{{ doc.version }}</h1>
    {% for module in doc.modules %}
        <h2>{{ module.name }}</h2>
        {% for endpoint in module.endpoints %}
            <div>
                <span>{{ endpoint.method }}</span>
                <code>{{ endpoint.path }}</code>
                <p>{{ endpoint.summary }}</p>
            </div>
        {% endfor %}
    {% endfor %}
</body>
</html>
```

使用自定义模板：

```bash
python -m api_doc_generator.cli generate ./src --template templates/custom.html -o custom_docs.html
```

## 🌐 在线预览

启动服务器后，可通过以下地址访问：

```
# HTML 文档
http://localhost:8000/docs/html?source=./my_api

# Markdown 文档
http://localhost:8000/docs/markdown?source=./my_api

# OpenAPI 文档
http://localhost:8000/docs/openapi?source=./my_api
```

## 📁 项目结构

```
api_doc_generator/
├── __init__.py          # 包初始化
├── models.py            # 数据模型
├── code_parser.py       # 代码解析器 (AST)
├── doc_generator.py     # 文档生成器
├── template_engine.py   # Jinja2 模板引擎
├── api.py               # FastAPI 服务
├── cli.py               # CLI 入口
├── config.yaml          # 配置文件
├── requirements.txt     # 依赖
└── README.md            # 项目文档
```

## 🛠️ 技术栈

- **Python AST** - 源代码解析
- **FastAPI** - Web 服务框架
- **Jinja2** - 模板引擎
- **PyYAML** - 配置文件解析
- **Rich** - 终端美化输出

## 📄 License

MIT License
