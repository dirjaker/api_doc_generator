# 变更日志

本文档记录 api_doc_generator 的版本变更历史。格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)。

---

## [1.0.0] - 2026-06-21

### 新增

- **AST 代码解析器** (`code_parser.py`)
  - 基于 Python `ast` 模块的静态分析引擎
  - 支持 FastAPI 装饰器识别：`@app.get()`, `@app.post()`, `@app.put()`, `@app.delete()`, `@app.patch()`
  - 支持 Flask 装饰器识别：`@app.route()`
  - 支持 Django 装饰器识别：`@path()`, `@re_path()`
  - 自动提取函数参数、类型注解、默认值
  - 递归解析泛型类型注解（`list[int]`, `dict[str, Any]`, `Optional[str]` 等）
  - 自动提取 docstring 作为端点描述
  - 提取返回值类型注解
  - 支持同步与异步函数解析

- **数据模型** (`models.py`)
  - `Parameter` — API 参数模型
  - `Response` — API 响应模型
  - `APIEndpoint` — API 端点模型
  - `APIModule` — API 模块模型
  - `APIDocumentation` — API 文档顶层容器
  - 基于 `dataclass` 的轻量级中间表示（IR）

- **文档生成器** (`doc_generator.py`)
  - 从单个文件生成文档 (`generate_from_file`)
  - 从目录递归生成文档 (`generate_from_directory`)
  - 输出为 Markdown / HTML / OpenAPI 3.0 格式
  - 支持保存到文件 (`save_markdown`, `save_html`, `save_openapi`)

- **模板引擎** (`template_engine.py`)
  - 基于 Jinja2 的多格式渲染
  - 内置 Markdown 默认模板
  - 内置 HTML 默认模板（含完整 CSS 样式：渐变色 header、HTTP 方法彩色标签、响应式表格）
  - 支持自定义模板文件
  - OpenAPI 3.0 标准格式输出（含 tags、parameters、responses）

- **CLI 命令行工具** (`cli.py`)
  - `generate` 子命令 — 生成文档文件
  - `serve` 子命令 — 启动在线预览服务器
  - `info` 子命令 — 终端表格展示 API 概要
  - 基于 Rich 的彩色终端输出
  - argparse 参数解析

- **Web 服务** (`api.py`)
  - FastAPI 在线预览服务
  - `/docs/html` — HTML 格式文档端点
  - `/docs/markdown` — Markdown 格式文档端点
  - `/docs/openapi` — OpenAPI JSON 端点
  - `/health` — 健康检查端点
  - 全局文档缓存机制

- **配置** (`config.yaml`)
  - 项目信息配置（title, version, description）
  - 源代码扫描配置（path, exclude patterns）
  - 输出配置（format, directory, filename）
  - 模板配置（directory, file）
  - 服务器配置（host, port）
  - 解析器配置（frameworks, include_private）

- **macOS 打包** (`packaging/py2app_setup.py`)
  - py2app 打包配置

- **项目文档**
  - README.md — 项目介绍与快速开始
  - 技术文档.md — 架构设计与面试准备
  - REVIEW.md — 代码审查报告

---

## [规划中]

### 计划新增

- 支持更多语言：Go、TypeScript、Java
- 增量更新：仅解析变更文件，提升大项目性能
- VS Code 插件：编辑器内实时预览
- 路径参数自动识别：从 `/users/{user_id}` 提取参数
- 请求体模型解析：解析 Pydantic BaseModel 作为请求体文档
- PyPI 发布：支持 `pip install api-doc-generator`
- 单元测试：pytest 测试套件
- 日志系统：统一使用 logging 模块
