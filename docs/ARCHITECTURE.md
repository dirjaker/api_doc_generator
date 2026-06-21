# 架构设计文档

> 项目定位：基于 Python AST 静态分析，从源代码自动生成 FastAPI/Flask/Django 的 API 文档，支持 Markdown/HTML/OpenAPI 三种输出格式。

---

## 一、项目背景与价值

### 为什么做

在实际项目中，API 文档的维护是一个长期痛点：手写文档容易与代码脱节，Swagger 注解侵入性强，而 FastAPI 虽然自带文档生成但无法覆盖 Flask/Django 项目。本项目实现了一个 **零侵入** 的 API 文档生成工具——只需指向源代码目录，即可通过 AST（抽象语法树）解析自动提取路由、参数、类型注解和 docstring，生成标准化文档。

核心价值：
- **零侵入**：不需要在代码中添加任何注解或装饰器
- **多框架支持**：统一处理 FastAPI、Flask、Django 的路由语法
- **多格式输出**：Markdown（Git 友好）、HTML（可浏览）、OpenAPI 3.0（标准化）
- **在线预览**：内置 FastAPI 服务器，实时预览文档

### 面试话术

> "我实现了一个基于 Python AST 的 API 文档生成器。核心技术是用 `ast.parse` 解析源代码为语法树，然后遍历 AST 节点提取装饰器信息（如 `@app.get("/users")`）、函数参数的类型注解、默认值和 docstring。通过识别不同框架的装饰器模式（FastAPI 的 `get/post`、Flask 的 `route`、Django 的 `path`），实现了多框架统一解析。输出层使用 Jinja2 模板引擎支持自定义样式，同时实现了 OpenAPI 3.0 标准格式输出，可以与 Swagger UI 等工具集成。"

---

## 二、系统架构

```
┌──────────────────────────────────────────────────────────┐
│                    api_doc_generator                      │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────┐    ┌──────────────┐    ┌───────────────┐  │
│  │  入口层   │    │    解析层     │    │    输出层      │  │
│  │          │    │              │    │               │  │
│  │ cli.py   │───▶│ code_parser  │───▶│ doc_generator │  │
│  │ (CLI)    │    │   .py        │    │   .py         │  │
│  │          │    │              │    │               │  │
│  │ api.py   │    │ · AST 解析   │    │ · Markdown    │  │
│  │ (Web)    │    │ · 装饰器识别 │    │ · HTML        │  │
│  │          │    │ · 参数提取   │    │ · OpenAPI 3.0 │  │
│  └──────────┘    │ · 类型解析   │    └───────┬───────┘  │
│                  └──────┬───────┘            │          │
│                         │                    │          │
│                  ┌──────▼───────┐    ┌───────▼───────┐  │
│                  │  models.py   │    │template_engine│  │
│                  │              │    │   .py         │  │
│                  │ · Parameter  │    │               │  │
│                  │ · Response   │    │ · Jinja2 渲染 │  │
│                  │ · Endpoint   │    │ · 自定义模板  │  │
│                  │ · Module     │    │ · 内置模板    │  │
│                  │ · Document   │    │               │  │
│                  └──────────────┘    └───────────────┘  │
└──────────────────────────────────────────────────────────┘

数据流:
  源代码(.py) → AST解析 → 数据模型(APIDocumentation) → 模板渲染 → 文档输出
```

---

## 三、核心模块设计

### 3.1 数据模型层 (`models.py`)

**职责**：定义 API 文档的中间表示（IR），所有模块通过此模型解耦。

```python
from dataclasses import dataclass, field
from typing import Any, Optional

@dataclass
class Parameter:
    """API参数模型"""
    name: str
    type: str = "Any"
    required: bool = True
    default: Optional[Any] = None
    description: str = ""

@dataclass
class Response:
    """API响应模型"""
    status_code: int = 200
    type: str = "Any"
    description: str = ""

@dataclass
class APIEndpoint:
    """API端点模型"""
    path: str
    method: str = "GET"
    summary: str = ""
    description: str = ""
    parameters: list[Parameter] = field(default_factory=list)
    responses: list[Response] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

@dataclass
class APIModule:
    """API模块模型（对应一个Python文件）"""
    name: str
    description: str = ""
    endpoints: list[APIEndpoint] = field(default_factory=list)

@dataclass
class APIDocumentation:
    """API文档模型（顶层容器）"""
    title: str = "API Documentation"
    version: str = "1.0.0"
    description: str = ""
    modules: list[APIModule] = field(default_factory=list)
```

**设计选择**：使用 `dataclass` 而非 Pydantic，因为模型仅作为数据容器，不需要验证逻辑，dataclass 更轻量。

---

### 3.2 代码解析层 (`code_parser.py`)

**职责**：核心模块，使用 Python AST 解析源代码，提取 API 端点信息。

#### 多框架装饰器识别

```python
class CodeParser:
    FRAMEWORK_DECORATORS = {
        "fastapi": ["get", "post", "put", "delete", "patch"],
        "flask": ["route"],
        "django": ["path", "re_path"],
    }

    def _extract_decorators(self, node) -> tuple[str, str] | None:
        """提取装饰器信息，返回 (method, path)"""
        for dec in node.decorator_list:
            if isinstance(dec, ast.Call):
                # FastAPI: @app.get("/path")
                if isinstance(dec.func, ast.Attribute):
                    method = dec.func.attr
                    if method in self.FRAMEWORK_DECORATORS["fastapi"]:
                        path = dec.args[0].value if dec.args else "/"
                        if isinstance(path, ast.Constant):
                            path = path.value
                        return method, str(path)

                # Flask: @app.route("/path", methods=["GET"])
                if isinstance(dec.func, ast.Attribute) and dec.func.attr == "route":
                    path = dec.args[0].value if dec.args else "/"
                    if isinstance(path, ast.Constant):
                        path = path.value
                    method = "GET"
                    for kw in dec.keywords:
                        if kw.arg == "methods" and isinstance(kw.value, ast.List):
                            if kw.value.elts:
                                method = kw.value.elts[0].value
                                if isinstance(method, ast.Constant):
                                    method = method.value
                    return method, str(path)
        return None
```

#### 参数提取与类型解析

```python
def _extract_parameters(self, node) -> list[Parameter]:
    """提取函数参数，包括类型注解和默认值"""
    params = []
    for i, arg in enumerate(node.args.args):
        if arg.arg in ("self", "cls", "request", "response"):
            continue

        param = Parameter(name=arg.arg)
        if arg.annotation:
            param.type = self._get_annotation_str(arg.annotation)

        # 检查默认值 — 通过偏移量计算
        defaults_offset = len(args.args) - len(args.defaults)
        default_idx = i - defaults_offset
        if default_idx >= 0:
            param.required = False
            param.default = self._get_default_str(args.defaults[default_idx])

        params.append(param)
    return params

def _get_annotation_str(self, node) -> str:
    """递归将类型注解 AST 节点转换为字符串"""
    if isinstance(node, ast.Constant):
        return str(node.value)
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return f"{self._get_annotation_str(node.value)}.{node.attr}"
    if isinstance(node, ast.Subscript):
        base = self._get_annotation_str(node.value)
        inner = self._get_annotation_str(node.slice)
        return f"{base}[{inner}]"  # 处理 list[int], dict[str, Any] 等泛型
    if isinstance(node, ast.Tuple):
        items = [self._get_annotation_str(e) for e in node.elts]
        return ", ".join(items)
    return "Any"
```

#### 完整解析流程

```python
def parse_file(self, file_path: str) -> APIModule:
    """解析单个Python文件"""
    path = Path(file_path)
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source)                    # 1. 解析为 AST
    module = APIModule(name=path.stem)
    module.description = self._extract_module_docstring(tree)

    for node in ast.walk(tree):                 # 2. 遍历所有节点
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            endpoint = self._parse_function(node)  # 3. 提取端点信息
            if endpoint:
                module.endpoints.append(endpoint)

    return module
```

---

### 3.3 文档生成层 (`doc_generator.py`)

**职责**：协调解析器和模板引擎，提供统一的文档生成 API。

```python
class DocGenerator:
    def __init__(self, template_dir: Optional[str] = None):
        self.parser = CodeParser()
        self.template_engine = TemplateEngine(template_dir)

    def generate_from_file(self, file_path: str, **kwargs) -> APIDocumentation:
        """从单个文件生成文档"""
        module = self.parser.parse_file(file_path)
        return APIDocumentation(
            title=kwargs.get("title", "API Documentation"),
            version=kwargs.get("version", "1.0.0"),
            description=kwargs.get("description", ""),
            modules=[module],
        )

    def generate_from_directory(self, dir_path: str, **kwargs) -> APIDocumentation:
        """从目录生成文档 — 递归扫描所有 .py 文件"""
        modules = self.parser.parse_directory(dir_path)
        return APIDocumentation(modules=modules, **kwargs)

    # 输出方法 — 委托给模板引擎
    def to_markdown(self, doc, template=None) -> str: ...
    def to_html(self, doc, template=None) -> str: ...
    def to_openapi(self, doc) -> dict: ...

    # 保存到文件
    def save_markdown(self, doc, output_path, template=None): ...
    def save_html(self, doc, output_path, template=None): ...
    def save_openapi(self, doc, output_path): ...
```

---

### 3.4 模板引擎层 (`template_engine.py`)

**职责**：基于 Jinja2 实现多格式渲染，支持自定义模板。

```python
class TemplateEngine:
    def __init__(self, template_dir: Optional[str] = None):
        if template_dir:
            self.env = Environment(loader=FileSystemLoader(template_dir))
        else:
            self.env = Environment()

    def render_markdown(self, doc, template_name=None) -> str:
        if template_name:
            template = self.env.get_template(template_name)
        else:
            template = self.env.from_string(DEFAULT_MARKDOWN_TEMPLATE)
        return template.render(doc=doc)

    def render_html(self, doc, template_name=None) -> str:
        if template_name:
            template = self.env.get_template(template_name)
        else:
            template = self.env.from_string(DEFAULT_HTML_TEMPLATE)
        return template.render(doc=doc)

    def render_openapi(self, doc: APIDocumentation) -> dict:
        """将内部模型转换为 OpenAPI 3.0 标准格式"""
        openapi = {
            "openapi": "3.0.0",
            "info": {"title": doc.title, "version": doc.version, "description": doc.description},
            "paths": {},
            "tags": [],
        }
        for module in doc.modules:
            openapi["tags"].append({"name": module.name, "description": module.description})
            for endpoint in module.endpoints:
                operation = {
                    "summary": endpoint.summary,
                    "description": endpoint.description,
                    "tags": endpoint.tags or [module.name],
                    "parameters": [
                        {"name": p.name, "in": "query", "required": p.required,
                         "schema": {"type": p.type.lower()}, "description": p.description}
                        for p in endpoint.parameters
                    ],
                    "responses": {
                        str(r.status_code): {"description": r.description,
                            "content": {"application/json": {"schema": {"type": r.type}}}}
                        for r in endpoint.responses
                    },
                }
                openapi["paths"].setdefault(endpoint.path, {})[
                    endpoint.method.lower()
                ] = operation
        return openapi
```

**内置模板亮点**：HTML 模板内置了完整的 CSS 样式（渐变色 header、HTTP 方法彩色标签、响应式表格），生成即用。

---

### 3.5 CLI 入口 (`cli.py`)

**职责**：命令行接口，使用 argparse + Rich 美化输出。

```python
# 三个子命令
generate  → 生成文档文件（markdown/html/openapi）
serve     → 启动 FastAPI 在线预览服务器
info      → 终端表格展示 API 概要信息

# 使用示例
python -m api_doc_generator.cli generate ./src -f html -o api_docs.html
python -m api_doc_generator.cli serve ./src --port 8080
python -m api_doc_generator.cli info ./src
```

**`generate` 命令参数：**

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `source` | 源代码文件或目录路径 | 必填 |
| `-o, --output` | 输出文件路径 | 根据格式自动生成 |
| `-f, --format` | 输出格式（markdown/html/openapi） | markdown |
| `-t, --title` | 文档标题 | API Documentation |
| `-v, --version` | API 版本号 | 1.0.0 |
| `--template` | 自定义模板文件路径 | 无（使用内置模板） |

**`serve` 命令参数：**

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `source` | 源代码文件或目录路径 | 必填 |
| `--host` | 服务器监听地址 | 0.0.0.0 |
| `--port` | 服务器端口 | 8000 |
| `-t, --title` | 文档标题 | API Documentation |
| `--version` | API 版本号 | 1.0.0 |

### 3.6 Web 服务 (`api.py`)

**职责**：FastAPI 服务，提供在线文档预览。

```python
app = FastAPI(title="API Doc Generator")

# 全局缓存 — 避免重复解析
_cached_doc: Optional[APIDocumentation] = None
_cached_source: Optional[str] = None

@app.get("/docs/html", response_class=HTMLResponse)
async def get_html_docs(source: str = Query(...)): ...

@app.get("/docs/markdown")
async def get_markdown_docs(source: str = Query(...)): ...

@app.get("/docs/openapi")
async def get_openapi_docs(source: str = Query(...)): ...

@app.get("/health")
async def health(): ...
```

---

## 四、技术亮点

### 4.1 基于 AST 的零侵入解析

不依赖运行时反射或正则匹配，而是使用 Python `ast` 模块进行静态分析：
- **准确性**：AST 是代码的精确语法表示，不会遗漏或误判
- **零侵入**：不需要导入目标模块、不需要运行代码、不需要添加注解
- **深度解析**：递归处理泛型类型（如 `list[int]`、`dict[str, Any]`）、嵌套装饰器
- **安全性**：纯静态分析，不执行目标代码，避免导入副作用

### 4.2 多框架统一抽象

通过 `FRAMEWORK_DECORATORS` 字典定义各框架的装饰器模式，用统一的解析逻辑处理不同框架的路由语法。扩展新框架只需添加装饰器映射。

### 4.3 中间表示（IR）设计

`APIDocumentation → APIModule → APIEndpoint → Parameter/Response` 四层模型将解析和渲染完全解耦。解析层只负责填充 IR，渲染层只负责消费 IR，新增输出格式只需添加渲染方法。

### 4.4 双入口设计

- **CLI 入口**：适合 CI/CD 集成，一键生成文档
- **Web 入口**：适合开发阶段实时预览，支持按需刷新

### 4.5 模板可扩展

Jinja2 模板引擎支持外部自定义模板文件，内置 Markdown 和 HTML 两套默认模板。HTML 模板包含完整的 CSS 样式，生成的文档可直接部署。

---

## 五、面试常见问题

**Q1: 为什么用 AST 解析而不是正则表达式？**

> AST 是代码的精确语法树表示，可以准确提取装饰器参数、函数签名、类型注解等结构化信息。正则表达式容易被多行字符串、注释、嵌套语法干扰，准确率低且难以维护。AST 解析还有个优势：不需要运行代码即可分析，避免了导入目标模块可能带来的副作用。

**Q2: 如何处理不同框架的路由语法差异？**

> 通过 `FRAMEWORK_DECORATORS` 字典定义各框架的装饰器模式（FastAPI 用 `get/post`，Flask 用 `route`，Django 用 `path`）。解析时遍历函数的 `decorator_list`，根据装饰器的 `ast.Attribute` 名称匹配框架，再用框架特定的逻辑提取路径和方法。扩展新框架只需添加一行映射。

**Q3: 如何解析 `list[int]` 这样的泛型类型注解？**

> 使用递归的 `_get_annotation_str` 方法。`list[int]` 在 AST 中是 `ast.Subscript` 节点，其 `value` 是 `ast.Name("list")`，`slice` 是 `ast.Name("int")`。递归拼接为 `"list[int]"`。同样支持 `dict[str, Any]`、`Optional[str]` 等嵌套泛型。

**Q4: 如何判断参数是否有默认值？**

> AST 中 `node.args.args` 是所有参数列表，`node.args.defaults` 是默认值列表。默认值从右往左对齐，所以用偏移量 `len(args) - len(defaults)` 计算每个参数对应的默认值索引。

**Q5: 项目的中间表示（IR）设计有什么好处？**

> IR（APIDocumentation 模型）将解析层和渲染层完全解耦。解析层只负责填充 IR，渲染层只负责消费 IR。这样新增输出格式（如 PDF、AsciiDoc）只需添加渲染方法，不碰解析代码；新增框架支持只需修改解析器，不影响输出逻辑。

**Q6: 如何实现在线预览的性能优化？**

> Web 服务中使用全局缓存（`_cached_doc`）缓存解析结果，相同源代码路径不会重复解析。只有当源代码变化时才重新生成文档。

**Q7: 如果要支持异步函数的解析怎么办？**

> 当前代码已经处理了——`ast.walk` 同时检查 `ast.FunctionDef` 和 `ast.AsyncFunctionDef`。两者的装饰器、参数、返回值结构完全一致，可以用同一套逻辑解析。

**Q8: 和 FastAPI 自带的 /docs 有什么区别？**

> FastAPI 自带文档依赖运行时路由注册，需要启动服务才能生成。本工具是静态分析，不需要运行代码。此外本工具支持 Flask/Django，且生成的文档可以是 Markdown/HTML 文件，适合离线查阅或集成到 CI/CD 文档发布流程。

---

## 六、项目数据

| 指标 | 数据 |
|------|------|
| **代码量** | ~800 行 Python（7 个源文件） |
| **文件数** | 7 个 .py + 1 个 .yaml + 1 个 requirements.txt |
| **技术栈** | Python 3.11, AST, FastAPI, Jinja2, PyYAML, Rich, argparse |
| **支持框架** | FastAPI, Flask, Django |
| **输出格式** | Markdown, HTML（内置 CSS）, OpenAPI 3.0 |
| **入口方式** | CLI 命令行 + Web 在线预览 |
| **核心设计** | AST 静态分析 + 中间表示（IR）+ Jinja2 模板渲染 |
