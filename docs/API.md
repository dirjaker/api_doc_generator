# API 参考文档

本文档提供 api_doc_generator 的 Python API 和 CLI 命令的详细参考。

---

## 一、Python API

### 1.1 包导入

```python
from api_doc_generator import (
    APIDocumentation,  # 顶层文档容器
    APIEndpoint,       # API 端点模型
    APIModule,         # API 模块模型
    Parameter,         # 参数模型
    Response,          # 响应模型
    CodeParser,        # 代码解析器
    DocGenerator,      # 文档生成器（推荐入口）
    TemplateEngine,    # 模板引擎
)
```

---

### 1.2 数据模型 (`models.py`)

#### `Parameter`

API 参数的数据模型。

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `name` | `str` | 必填 | 参数名称 |
| `type` | `str` | `"Any"` | 参数类型（字符串表示） |
| `required` | `bool` | `True` | 是否为必填参数 |
| `default` | `Optional[Any]` | `None` | 默认值 |
| `description` | `str` | `""` | 参数描述 |

#### `Response`

API 响应的数据模型。

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `status_code` | `int` | `200` | HTTP 状态码 |
| `type` | `str` | `"Any"` | 响应类型 |
| `description` | `str` | `""` | 响应描述 |

#### `APIEndpoint`

API 端点的数据模型。

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `path` | `str` | 必填 | 路由路径 |
| `method` | `str` | `"GET"` | HTTP 方法 |
| `summary` | `str` | `""` | 摘要（取自 docstring 首行） |
| `description` | `str` | `""` | 完整描述（完整 docstring） |
| `parameters` | `list[Parameter]` | `[]` | 参数列表 |
| `responses` | `list[Response]` | `[]` | 响应列表 |
| `tags` | `list[str]` | `[]` | 标签列表 |

#### `APIModule`

API 模块的数据模型，对应一个 Python 源文件。

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `name` | `str` | 必填 | 模块名（文件名去扩展名） |
| `description` | `str` | `""` | 模块描述（取自模块 docstring） |
| `endpoints` | `list[APIEndpoint]` | `[]` | 端点列表 |

#### `APIDocumentation`

顶层 API 文档容器。

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `title` | `str` | `"API Documentation"` | 文档标题 |
| `version` | `str` | `"1.0.0"` | API 版本 |
| `description` | `str` | `""` | 文档描述 |
| `modules` | `list[APIModule]` | `[]` | 模块列表 |

---

### 1.3 文档生成器 (`DocGenerator`)

推荐的使用入口，协调解析器与模板引擎。

#### 构造函数

```python
DocGenerator(template_dir: Optional[str] = None)
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `template_dir` | `Optional[str]` | 自定义模板目录路径，为 `None` 时使用内置模板 |

#### 方法

##### `generate_from_file(file_path, **kwargs) -> APIDocumentation`

从单个 Python 文件生成文档。

| 参数 | 类型 | 说明 |
|------|------|------|
| `file_path` | `str` | Python 文件路径 |
| `title` | `str` | 文档标题（可选） |
| `version` | `str` | API 版本（可选） |
| `description` | `str` | 文档描述（可选） |

```python
generator = DocGenerator()
doc = generator.generate_from_file("./api.py", title="My API", version="2.0.0")
```

##### `generate_from_directory(dir_path, **kwargs) -> APIDocumentation`

从目录递归生成文档（扫描所有 `.py` 文件，跳过 `_` 开头的文件）。

| 参数 | 类型 | 说明 |
|------|------|------|
| `dir_path` | `str` | 源代码目录路径 |
| `title` | `str` | 文档标题（可选） |
| `version` | `str` | API 版本（可选） |
| `description` | `str` | 文档描述（可选） |

```python
doc = generator.generate_from_directory("./src", title="Project API")
```

##### `to_markdown(doc, template=None) -> str`

将文档渲染为 Markdown 字符串。

```python
md = generator.to_markdown(doc)
```

##### `to_html(doc, template=None) -> str`

将文档渲染为 HTML 字符串（内置完整 CSS 样式）。

```python
html = generator.to_html(doc)
```

##### `to_openapi(doc) -> dict`

将文档转换为 OpenAPI 3.0 字典。

```python
openapi = generator.to_openapi(doc)
```

##### `save_markdown(doc, output_path, template=None) -> str`

保存 Markdown 文档到文件。

##### `save_html(doc, output_path, template=None) -> str`

保存 HTML 文档到文件。

##### `save_openapi(doc, output_path) -> str`

保存 OpenAPI JSON 到文件。

---

### 1.4 代码解析器 (`CodeParser`)

底层 AST 解析器，一般通过 `DocGenerator` 间接使用。

```python
parser = CodeParser()

# 解析单个文件
module = parser.parse_file("./api.py")

# 解析目录
modules = parser.parse_directory("./src")
```

#### 支持的框架装饰器

| 框架 | 装饰器 |
|------|--------|
| FastAPI | `@app.get()`, `@app.post()`, `@app.put()`, `@app.delete()`, `@app.patch()` |
| Flask | `@app.route()` |
| Django | `@path()`, `@re_path()` |

#### 自动跳过的参数

解析函数参数时，以下参数名会被自动跳过：
- `self` — 类实例方法
- `cls` — 类方法
- `request` — 请求对象
- `response` — 响应对象

---

### 1.5 模板引擎 (`TemplateEngine`)

底层 Jinja2 模板引擎，一般通过 `DocGenerator` 间接使用。

```python
engine = TemplateEngine(template_dir="./templates")

# 使用内置模板
md = engine.render_markdown(doc)

# 使用自定义模板
md = engine.render_markdown(doc, template_name="custom.md.j2")

# OpenAPI 格式（无自定义模板）
openapi = engine.render_openapi(doc)
```

#### 自定义模板变量

模板中可使用以下变量：

| 变量 | 类型 | 说明 |
|------|------|------|
| `doc` | `APIDocumentation` | 顶层文档对象 |
| `doc.title` | `str` | 文档标题 |
| `doc.version` | `str` | API 版本 |
| `doc.description` | `str` | 文档描述 |
| `doc.modules` | `list[APIModule]` | 模块列表 |
| `module.name` | `str` | 模块名 |
| `module.endpoints` | `list[APIEndpoint]` | 端点列表 |
| `endpoint.method` | `str` | HTTP 方法 |
| `endpoint.path` | `str` | 路由路径 |
| `endpoint.summary` | `str` | 摘要 |
| `endpoint.parameters` | `list[Parameter]` | 参数列表 |
| `param.name` | `str` | 参数名 |
| `param.type` | `str` | 参数类型 |
| `param.required` | `bool` | 是否必填 |

---

## 二、CLI 命令参考

### 入口

```bash
python -m api_doc_generator.cli <command> [options]
```

### 2.1 `generate` — 生成文档

```bash
python -m api_doc_generator.cli generate <source> [options]
```

| 参数 | 缩写 | 类型 | 默认值 | 说明 |
|------|------|------|--------|------|
| `source` | — | `str` | 必填 | 源代码文件或目录路径 |
| `--output` | `-o` | `str` | 自动 | 输出文件路径 |
| `--format` | `-f` | `str` | `markdown` | 输出格式：`markdown` / `html` / `openapi` |
| `--title` | `-t` | `str` | `API Documentation` | 文档标题 |
| `--version` | `-v` | `str` | `1.0.0` | API 版本 |
| `--template` | — | `str` | 无 | 自定义模板文件路径 |

**示例：**

```bash
# 生成 Markdown 文档
python -m api_doc_generator.cli generate ./src -f markdown -o api.md

# 生成 HTML 文档，指定标题和版本
python -m api_doc_generator.cli generate ./src -f html -t "用户服务 API" -v "2.1.0" -o api.html

# 使用自定义模板
python -m api_doc_generator.cli generate ./src --template ./templates/custom.md.j2 -o custom.md
```

### 2.2 `serve` — 启动预览服务器

```bash
python -m api_doc_generator.cli serve <source> [options]
```

| 参数 | 缩写 | 类型 | 默认值 | 说明 |
|------|------|------|--------|------|
| `source` | — | `str` | 必填 | 源代码文件或目录路径 |
| `--host` | — | `str` | `0.0.0.0` | 监听地址 |
| `--port` | — | `int` | `8000` | 监听端口 |
| `--title` | `-t` | `str` | `API Documentation` | 文档标题 |
| `--version` | — | `str` | `1.0.0` | API 版本 |

**示例：**

```bash
python -m api_doc_generator.cli serve ./src --port 8080
```

启动后可访问：
- `http://localhost:8080/docs/html?source=./src`
- `http://localhost:8080/docs/markdown?source=./src`
- `http://localhost:8080/docs/openapi?source=./src`
- `http://localhost:8080/health`

### 2.3 `info` — 查看 API 概要

```bash
python -m api_doc_generator.cli info <source>
```

以 Rich 彩色表格形式在终端展示解析到的 API 端点信息。

---

## 三、Web API 参考

通过 `serve` 命令启动的 FastAPI 服务提供以下端点：

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/` | 使用说明 |
| `GET` | `/health` | 健康检查 |
| `GET` | `/docs/html` | HTML 格式文档 |
| `GET` | `/docs/markdown` | Markdown 格式文档 |
| `GET` | `/docs/openapi` | OpenAPI JSON 文档 |

### 查询参数

所有 `/docs/*` 端点支持以下查询参数：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `source` | `str` | 是 | 源代码文件或目录路径 |
| `title` | `str` | 否 | 文档标题（默认：API Documentation） |
| `version` | `str` | 否 | API 版本（默认：1.0.0） |
| `template` | `str` | 否 | 自定义模板名称（仅 html/markdown） |
