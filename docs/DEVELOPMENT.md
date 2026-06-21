# 开发环境搭建指南

本文档指导开发者从零搭建 api_doc_generator 的开发环境。

---

## 一、环境要求

| 依赖 | 最低版本 | 说明 |
|------|----------|------|
| Python | 3.11+ | 使用了 `list[int]` 等内置泛型语法 |
| Conda | 任意 | 推荐用于管理虚拟环境，也可用 venv |
| Git | 任意 | 版本管理 |

---

## 二、快速搭建

### 2.1 克隆代码

```bash
git clone https://github.com/dirjaker/api_doc_generator.git
cd api_doc_generator
git checkout dev  # 开发在 dev 分支进行
```

### 2.2 创建虚拟环境

**方式一：Conda（推荐）**

```bash
conda create -n api_doc_generator python=3.11 -y
conda activate api_doc_generator
```

**方式二：venv**

```bash
python3.11 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows
```

### 2.3 安装依赖

```bash
pip install -r requirements.txt
```

依赖列表：

| 包名 | 用途 |
|------|------|
| `fastapi>=0.100.0` | Web 服务框架（在线预览） |
| `uvicorn>=0.23.0` | ASGI 服务器 |
| `jinja2>=3.1.0` | 模板引擎 |
| `pyyaml>=6.0` | YAML 配置文件解析 |
| `rich>=13.0.0` | 终端美化输出 |

### 2.4 验证安装

```bash
# 查看帮助
python -m api_doc_generator.cli --help

# 对项目自身生成文档（自举测试）
python -m api_doc_generator.cli info ./
```

---

## 三、项目配置

项目使用 `config.yaml` 进行配置：

```yaml
# 项目信息
project:
  title: "My API Documentation"
  version: "1.0.0"
  description: "自动生成的API文档"

# 源代码配置
source:
  path: "./src"
  exclude:
    - "**/test_*.py"
    - "**/__pycache__/**"
    - "**/venv/**"

# 输出配置
output:
  format: "markdown"        # markdown | html | openapi
  directory: "./docs"
  filename: "api_docs"

# 模板配置
template:
  directory: "./templates"  # 自定义模板目录
  file: ""                  # 为空则使用默认模板

# 服务器配置
server:
  host: "0.0.0.0"
  port: 8000

# 解析配置
parser:
  frameworks:
    - fastapi
    - flask
    - django
  include_private: false
```

---

## 四、开发工作流

### 4.1 常用开发命令

```bash
# 对源代码目录生成 Markdown 文档
python -m api_doc_generator.cli generate ./examples -f markdown -o test_docs.md

# 生成 HTML 文档
python -m api_doc_generator.cli generate ./examples -f html -o test_docs.html

# 生成 OpenAPI JSON
python -m api_doc_generator.cli generate ./examples -f openapi -o test_openapi.json

# 启动在线预览服务器
python -m api_doc_generator.cli serve ./examples --port 8080

# 查看解析结果概要
python -m api_doc_generator.cli info ./examples
```

### 4.2 Python API 调试

```python
from api_doc_generator import DocGenerator, CodeParser, TemplateEngine

# 单独测试解析器
parser = CodeParser()
module = parser.parse_file("./examples/sample_api.py")
print(f"发现 {len(module.endpoints)} 个端点")
for ep in module.endpoints:
    print(f"  {ep.method} {ep.path} - {ep.summary}")
    for p in ep.parameters:
        print(f"    参数: {p.name} ({p.type}) {'必填' if p.required else '可选'}")

# 单独测试文档生成
generator = DocGenerator()
doc = generator.generate_from_directory("./examples", title="Test API")
print(generator.to_markdown(doc))
```

### 4.3 自定义模板开发

创建模板文件 `templates/custom_markdown.md.j2`：

```jinja2
# {{ doc.title }} - {{ doc.version }}

{% for module in doc.modules %}
## 模块: {{ module.name }}

{% for endpoint in module.endpoints %}
- **{{ endpoint.method }}** `{{ endpoint.path }}` — {{ endpoint.summary }}
{% endfor %}
{% endfor %}
```

使用自定义模板：

```bash
python -m api_doc_generator.cli generate ./src --template templates/custom_markdown.md.j2 -o custom_docs.md
```

---

## 五、代码结构详解

```
api_doc_generator/
├── __init__.py          # 包入口，定义 __version__ 和 __all__ 导出列表
├── models.py            # 数据模型层 — 5 个 dataclass 定义 IR
├── code_parser.py       # 解析层 — AST 遍历、装饰器识别、参数提取
├── doc_generator.py     # 生成层 — 协调 parser 和 template_engine
├── template_engine.py   # 渲染层 — Jinja2 模板，内置 Markdown/HTML 模板
├── cli.py               # CLI 入口 — argparse + Rich，3 个子命令
├── api.py               # Web 入口 — FastAPI 服务，4 个端点
├── config.yaml          # 配置文件
├── requirements.txt     # 依赖声明
├── assets/              # 静态资源
│   └── banner.svg       # README banner
├── packaging/           # 打包相关
│   └── py2app_setup.py  # macOS 打包配置
├── src/                 # 示例源码（用于测试）
│   └── __init__.py
└── docs/                # 项目文档
```

### 模块依赖关系

```
cli.py ─────────┐
                ├──▶ doc_generator.py ──┬──▶ code_parser.py ──▶ models.py
api.py ─────────┘                       └──▶ template_engine.py ──▶ models.py
```

---

## 六、测试与调试

### 6.1 手动测试

```bash
# 准备测试用的 API 文件
cat > /tmp/test_api.py << 'EOF'
"""测试 API 模块"""
from fastapi import FastAPI

app = FastAPI()

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    """获取用户信息"""
    return {"user_id": user_id}

@app.post("/users")
async def create_user(name: str, age: int = 18):
    """创建新用户"""
    return {"name": name, "age": age}
EOF

# 测试解析
python -m api_doc_generator.cli info /tmp/test_api.py

# 测试各格式输出
python -m api_doc_generator.cli generate /tmp/test_api.py -f markdown -o /tmp/test.md
python -m api_doc_generator.cli generate /tmp/test_api.py -f html -o /tmp/test.html
python -m api_doc_generator.cli generate /tmp/test_api.py -f openapi -o /tmp/test.json
```

### 6.2 常见问题排查

**问题：`ModuleNotFoundError: No module named 'api_doc_generator'`**

确保在项目根目录运行，或将项目目录加入 `PYTHONPATH`：

```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)
python -m api_doc_generator.cli --help
```

**问题：解析结果为空**

- 检查目标文件是否使用了支持的框架装饰器（FastAPI/Flask/Django）
- 确认文件名不以 `_` 开头（`parse_directory` 会跳过 `_` 开头的文件）
- 检查装饰器语法是否正确

**问题：类型注解显示为 `Any`**

- 确认函数参数有类型注解
- 复杂类型（如自定义类）会回退为 `Any`，这是已知限制

---

## 七、打包与发布

### macOS 应用打包

```bash
# 安装 py2app
pip install py2app

# 执行打包
cd packaging
python py2app_setup.py py2app
```

### pip 包发布（规划中）

```bash
# 构建
python -m build

# 发布到 PyPI
python -m twine upload dist/*
```

---

## 八、Git 工作流

```bash
# 查看当前分支
git branch

# 功能开发
git checkout -b feature/your-feature
# ... 开发 ...
git add .
git commit -m "feat: 描述你的改动"
git push origin feature/your-feature

# 合并到 dev
git checkout dev
git merge feature/your-feature
```

**提交规范**：

| 前缀 | 说明 |
|------|------|
| `feat:` | 新功能 |
| `fix:` | 修复 Bug |
| `docs:` | 文档更新 |
| `refactor:` | 代码重构 |
| `test:` | 测试相关 |
| `chore:` | 构建/工具链 |
