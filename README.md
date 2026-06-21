<div align="center">

<img src="assets/banner.svg" width="100%" alt="API 文档生成器">

<br>

### 📄 API 文档生成器

[![Stars](https://img.shields.io/github/stars/dirjaker/api_doc_generator?style=flat-square&label=Stars&color=FFD700)](https://github.com/dirjaker/api_doc_generator/stargazers)
[![Forks](https://img.shields.io/github/forks/dirjaker/api_doc_generator?style=flat-square&label=Forks&color=4A90D9)](https://github.com/dirjaker/api_doc_generator/network/members)
[![Contributors](https://img.shields.io/github/contributors/dirjaker/api_doc_generator?style=flat-square&label=Contributors&color=8B4513)](https://github.com/dirjaker/api_doc_generator/graphs/contributors)
[![License](https://img.shields.io/github/license/dirjaker/api_doc_generator?style=flat-square&label=License&color=20B2AA)](https://github.com/dirjaker/api_doc_generator/blob/dev/LICENSE)

**基于 Python AST 静态分析，从源代码自动生成 API 文档，支持 FastAPI / Flask / Django 多框架**

</div>

---

## ✨ 功能特性

| 功能 | 描述 |
|------|------|
| 🔍 **AST 解析** | 基于 Python 抽象语法树深度解析代码结构，零侵入、无需注解 |
| 🌐 **多框架支持** | 统一处理 FastAPI、Flask、Django 的路由装饰器语法 |
| 📤 **多格式输出** | 支持 Markdown、HTML（内置 CSS 样式）、OpenAPI 3.0 JSON |
| 👁️ **在线预览** | 内置 FastAPI Web 服务器，实时预览生成的文档 |
| 📝 **注释提取** | 自动提取 docstring、类型注解、参数说明、返回值类型 |
| 🎨 **模板定制** | Jinja2 模板引擎，支持自定义 Markdown / HTML 模板 |
| ⌨️ **CLI 工具** | 命令行一键生成文档，适合 CI/CD 集成 |
| 📊 **Rich 美化** | 终端输出使用 Rich 库美化，表格展示 API 概要信息 |

## 🚀 快速开始

### 安装

```bash
# 克隆项目
git clone https://github.com/dirjaker/api_doc_generator.git
cd api_doc_generator

# 创建虚拟环境
conda create -n api_doc_generator python=3.11 -y
conda activate api_doc_generator

# 安装依赖
pip install -r requirements.txt
```

### 命令行使用

```bash
# 生成 Markdown 文档
python -m api_doc_generator.cli generate ./your_project -f markdown -o api_docs.md

# 生成 HTML 文档（内置样式，可直接浏览器打开）
python -m api_doc_generator.cli generate ./your_project -f html -o api_docs.html

# 生成 OpenAPI 3.0 JSON
python -m api_doc_generator.cli generate ./your_project -f openapi -o openapi.json

# 查看 API 概要信息（终端表格展示）
python -m api_doc_generator.cli info ./your_project

# 启动在线预览服务器
python -m api_doc_generator.cli serve ./your_project --port 8080
```

### Python API 使用

```python
from api_doc_generator import DocGenerator

generator = DocGenerator()

# 从目录生成文档
doc = generator.generate_from_directory("./your_project", title="My API", version="2.0.0")

# 输出为不同格式
markdown = generator.to_markdown(doc)
html = generator.to_html(doc)
openapi = generator.to_openapi(doc)

# 保存到文件
generator.save_html(doc, "api_docs.html")
generator.save_openapi(doc, "openapi.json")
```

### 在线预览

启动服务器后访问：

| 格式 | 地址 |
|------|------|
| HTML | `http://localhost:8000/docs/html?source=./your_project` |
| Markdown | `http://localhost:8000/docs/markdown?source=./your_project` |
| OpenAPI | `http://localhost:8000/docs/openapi?source=./your_project` |

## 🏗️ 项目结构

```
api_doc_generator/
├── __init__.py          # 包入口，导出公共 API
├── models.py            # 数据模型（Parameter, Response, APIEndpoint 等）
├── code_parser.py       # AST 代码解析器（多框架装饰器识别）
├── doc_generator.py     # 文档生成器（协调解析器与模板引擎）
├── template_engine.py   # Jinja2 模板引擎（Markdown/HTML/OpenAPI 渲染）
├── cli.py               # CLI 命令行入口（argparse + Rich）
├── api.py               # FastAPI Web 服务（在线预览）
├── config.yaml          # 项目配置文件
├── requirements.txt     # Python 依赖
├── assets/              # 静态资源
│   └── banner.svg
├── packaging/           # 打包配置
│   └── py2app_setup.py
└── docs/                # 项目文档
    ├── ARCHITECTURE.md  # 架构设计文档
    ├── DEVELOPMENT.md   # 开发环境搭建指南
    ├── API.md           # API 参考文档
    ├── REVIEW.md        # 代码审查报告
    └── CHANGELOG.md     # 变更日志
```

## 🛠️ 技术栈

| 层级 | 技术 |
|------|------|
| **核心解析** | Python `ast` 模块、`inspect` |
| **Web 服务** | FastAPI、Uvicorn |
| **模板引擎** | Jinja2 |
| **CLI** | argparse、Rich |
| **配置** | PyYAML |
| **输出格式** | Markdown、HTML（内置 CSS）、OpenAPI 3.0 |

## 📖 文档

| 文档 | 说明 |
|------|------|
| [架构设计](docs/ARCHITECTURE.md) | 系统架构、模块设计、数据流、技术亮点 |
| [开发指南](docs/DEVELOPMENT.md) | 开发环境搭建、项目配置、测试与调试 |
| [API 参考](docs/API.md) | Python API 与 CLI 命令详细参考 |
| [代码审查](docs/REVIEW.md) | 代码质量审查报告与改进建议 |
| [变更日志](docs/CHANGELOG.md) | 版本变更记录 |

## 📝 开发路线

- [x] AST 代码解析器
- [x] 多格式输出引擎（Markdown / HTML / OpenAPI）
- [x] 在线预览服务
- [x] 注释与类型注解提取
- [x] CLI 命令行工具
- [ ] 支持更多语言（Go、TypeScript、Java）
- [ ] 增量更新（仅解析变更文件）
- [ ] VS Code 插件集成
- [ ] 路径参数自动识别（`/users/{id}`）
- [ ] 请求体模型解析（Pydantic BaseModel）

## 📄 许可证

[MIT License](LICENSE)

---

<div align="center">

🔗 **GitHub**: [dirjaker/api_doc_generator](https://github.com/dirjaker/api_doc_generator)

⭐ 如果这个项目对你有帮助，请给一个 Star 支持一下！

</div>
