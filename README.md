<div align="center">

<img src="assets/banner.svg" width="100%" alt="API 文档生成器">

<br>

### 📄 API 文档生成器

[![Stars](https://img.shields.io/github/stars/dirjaker/api_doc_generator?style=flat-square&label=Stars&color=FFD700)](https://github.com/dirjaker/api_doc_generator/stargazers)
[![Forks](https://img.shields.io/github/forks/dirjaker/api_doc_generator?style=flat-square&label=Forks&color=4A90D9)](https://github.com/dirjaker/api_doc_generator/network/members)
[![Contributors](https://img.shields.io/github/contributors/dirjaker/api_doc_generator?style=flat-square&label=Contributors&color=8B4513)](https://github.com/dirjaker/api_doc_generator/graphs/contributors)
[![License](https://img.shields.io/github/license/dirjaker/api_doc_generator?style=flat-square&label=License&color=20B2AA)](https://github.com/dirjaker/api_doc_generator/blob/dev/LICENSE)

</div>

---

## ✨ 功能特性

| 功能 | 描述 |
|------|------|
| 🔍 **AST 解析** | 基于抽象语法树深度解析 Python 代码结构 |
| 📤 **多格式输出** | 支持 Markdown、HTML、OpenAPI JSON 多种格式 |
| 👁️ **在线预览** | 内置 Web 服务器，实时预览生成的文档 |
| 🔄 **自动化生成** | 一条命令完成从代码到文档的全流程 |
| 📝 **注释提取** | 自动提取 docstring、类型注解、参数说明 |
| 🎨 **模板定制** | 支持自定义文档模板和样式 |


## 🚀 快速开始

```bash
# 克隆项目
git clone https://github.com/dirjaker/api_doc_generator.git
cd api_doc_generator

# 创建虚拟环境
conda create -n api_doc_generator python=3.12 -y
conda activate api_doc_generator

# 安装依赖
pip install -r requirements.txt

# 运行项目
python main.py
```

## 🛠️ 技术栈

| 层级 | 技术 |
|------|------|
| **后端** | FastAPI, Python AST |
| **解析器** | ast, inspect |
| **输出** | Markdown, HTML, JSON |
| **前端** | Jinja2 |

## 📝 开发日志

- [x] AST 代码解析器
- [x] 多格式输出引擎
- [x] 在线预览服务
- [x] 注释提取器
- [x] CLI 命令行工具
- [ ] 支持更多语言
- [ ] 增量更新
- [ ] VS Code 插件

## 📄 许可证

[MIT License](LICENSE)

---

<div align="center">

🔗 **GitHub**: [dirjaker/api_doc_generator](https://github.com/dirjaker/api_doc_generator)

⭐ 如果这个项目对你有帮助，请给一个 Star 支持一下！

</div>
