"""模板引擎 - Jinja2模板自定义文档样式"""
from pathlib import Path
from typing import Optional
from jinja2 import Environment, FileSystemLoader, Template
from .models import APIDocumentation


DEFAULT_MARKDOWN_TEMPLATE = """# {{ doc.title }}

{% if doc.description %}
{{ doc.description }}
{% endif %}

**Version:** {{ doc.version }}

---

{% for module in doc.modules %}
## {{ module.name }}

{% if module.description %}
{{ module.description }}
{% endif %}

{% for endpoint in module.endpoints %}
### {{ endpoint.method }} {{ endpoint.path }}

**Summary:** {{ endpoint.summary }}

{% if endpoint.description %}
{{ endpoint.description }}
{% endif %}

{% if endpoint.tags %}
**Tags:** {{ endpoint.tags | join(', ') }}
{% endif %}

{% if endpoint.parameters %}
#### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
{% for param in endpoint.parameters %}
| `{{ param.name }}` | `{{ param.type }}` | {{ 'Yes' if param.required else 'No' }} | {{ param.default or '-' }} | {{ param.description }} |
{% endfor %}
{% endif %}

{% if endpoint.responses %}
#### Responses

| Status Code | Type | Description |
|-------------|------|-------------|
{% for resp in endpoint.responses %}
| {{ resp.status_code }} | `{{ resp.type }}` | {{ resp.description }} |
{% endfor %}
{% endif %}

---

{% endfor %}
{% endfor %}
"""

DEFAULT_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ doc.title }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 0; margin-bottom: 30px; }
        header h1 { font-size: 2.5em; }
        header .version { opacity: 0.8; margin-top: 10px; }
        .module { background: white; border-radius: 8px; padding: 30px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .module h2 { color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 10px; margin-bottom: 20px; }
        .endpoint { background: #f8f9fa; border-radius: 6px; padding: 20px; margin-bottom: 15px; border-left: 4px solid #667eea; }
        .endpoint h3 { color: #333; margin-bottom: 10px; }
        .method { display: inline-block; padding: 4px 12px; border-radius: 4px; color: white; font-weight: bold; margin-right: 10px; }
        .method-GET { background: #28a745; }
        .method-POST { background: #007bff; }
        .method-PUT { background: #ffc107; color: #333; }
        .method-DELETE { background: #dc3545; }
        .method-PATCH { background: #17a2b8; }
        .path { font-family: monospace; font-size: 1.1em; }
        .summary { color: #666; margin: 10px 0; }
        .tags { margin: 10px 0; }
        .tag { display: inline-block; background: #e9ecef; padding: 2px 8px; border-radius: 4px; font-size: 0.9em; margin-right: 5px; }
        table { width: 100%; border-collapse: collapse; margin: 15px 0; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #dee2e6; }
        th { background: #f1f3f5; font-weight: 600; }
        code { background: #e9ecef; padding: 2px 6px; border-radius: 4px; font-family: 'SFMono-Regular', Consolas, monospace; }
        .no-params { color: #999; font-style: italic; }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1>{{ doc.title }}</h1>
            {% if doc.description %}
            <p>{{ doc.description }}</p>
            {% endif %}
            <div class="version">Version: {{ doc.version }}</div>
        </div>
    </header>
    <div class="container">
        {% for module in doc.modules %}
        <div class="module">
            <h2>{{ module.name }}</h2>
            {% if module.description %}
            <p>{{ module.description }}</p>
            {% endif %}

            {% for endpoint in module.endpoints %}
            <div class="endpoint">
                <h3>
                    <span class="method method-{{ endpoint.method }}">{{ endpoint.method }}</span>
                    <span class="path">{{ endpoint.path }}</span>
                </h3>
                <p class="summary">{{ endpoint.summary }}</p>

                {% if endpoint.tags %}
                <div class="tags">
                    {% for tag in endpoint.tags %}
                    <span class="tag">{{ tag }}</span>
                    {% endfor %}
                </div>
                {% endif %}

                {% if endpoint.parameters %}
                <h4>Parameters</h4>
                <table>
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Type</th>
                            <th>Required</th>
                            <th>Default</th>
                            <th>Description</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for param in endpoint.parameters %}
                        <tr>
                            <td><code>{{ param.name }}</code></td>
                            <td><code>{{ param.type }}</code></td>
                            <td>{{ 'Yes' if param.required else 'No' }}</td>
                            <td>{{ param.default or '-' }}</td>
                            <td>{{ param.description }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                {% else %}
                <p class="no-params">No parameters</p>
                {% endif %}

                {% if endpoint.responses %}
                <h4>Responses</h4>
                <table>
                    <thead>
                        <tr>
                            <th>Status Code</th>
                            <th>Type</th>
                            <th>Description</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for resp in endpoint.responses %}
                        <tr>
                            <td>{{ resp.status_code }}</td>
                            <td><code>{{ resp.type }}</code></td>
                            <td>{{ resp.description }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                {% endif %}
            </div>
            {% endfor %}
        </div>
        {% endfor %}
    </div>
</body>
</html>
"""


class TemplateEngine:
    """Jinja2模板引擎，支持自定义模板"""

    def __init__(self, template_dir: Optional[str] = None):
        if template_dir:
            self.env = Environment(
                loader=FileSystemLoader(template_dir),
                trim_blocks=True,
                lstrip_blocks=True,
            )
        else:
            self.env = Environment(
                trim_blocks=True,
                lstrip_blocks=True,
            )

    def render_markdown(self, doc: APIDocumentation, template_name: Optional[str] = None) -> str:
        """渲染Markdown文档"""
        if template_name:
            template = self.env.get_template(template_name)
        else:
            template = self.env.from_string(DEFAULT_MARKDOWN_TEMPLATE)
        return template.render(doc=doc)

    def render_html(self, doc: APIDocumentation, template_name: Optional[str] = None) -> str:
        """渲染HTML文档"""
        if template_name:
            template = self.env.get_template(template_name)
        else:
            template = self.env.from_string(DEFAULT_HTML_TEMPLATE)
        return template.render(doc=doc)

    def render_openapi(self, doc: APIDocumentation) -> dict:
        """生成OpenAPI格式文档"""
        openapi = {
            "openapi": "3.0.0",
            "info": {
                "title": doc.title,
                "version": doc.version,
                "description": doc.description,
            },
            "paths": {},
            "tags": [],
        }

        for module in doc.modules:
            openapi["tags"].append({
                "name": module.name,
                "description": module.description,
            })

            for endpoint in module.endpoints:
                if endpoint.path not in openapi["paths"]:
                    openapi["paths"][endpoint.path] = {}

                operation = {
                    "summary": endpoint.summary,
                    "description": endpoint.description,
                    "tags": endpoint.tags or [module.name],
                    "parameters": [],
                    "responses": {},
                }

                for param in endpoint.parameters:
                    operation["parameters"].append({
                        "name": param.name,
                        "in": "query",
                        "required": param.required,
                        "schema": {"type": param.type.lower()},
                        "description": param.description,
                    })

                for resp in endpoint.responses:
                    operation["responses"][str(resp.status_code)] = {
                        "description": resp.description,
                        "content": {
                            "application/json": {
                                "schema": {"type": resp.type}
                            }
                        }
                    }

                openapi["paths"][endpoint.path][endpoint.method.lower()] = operation

        return openapi
