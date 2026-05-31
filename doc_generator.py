"""文档生成器 - 生成Markdown/HTML/OpenAPI格式文档"""
import json
from pathlib import Path
from typing import Optional
from .models import APIDocumentation
from .code_parser import CodeParser
from .template_engine import TemplateEngine


class DocGenerator:
    """API文档生成器"""

    def __init__(self, template_dir: Optional[str] = None):
        self.parser = CodeParser()
        self.template_engine = TemplateEngine(template_dir)

    def generate_from_file(self, file_path: str, **kwargs) -> APIDocumentation:
        """从单个文件生成文档"""
        module = self.parser.parse_file(file_path)
        doc = APIDocumentation(
            title=kwargs.get("title", "API Documentation"),
            version=kwargs.get("version", "1.0.0"),
            description=kwargs.get("description", ""),
            modules=[module],
        )
        return doc

    def generate_from_directory(self, dir_path: str, **kwargs) -> APIDocumentation:
        """从目录生成文档"""
        modules = self.parser.parse_directory(dir_path)
        doc = APIDocumentation(
            title=kwargs.get("title", "API Documentation"),
            version=kwargs.get("version", "1.0.0"),
            description=kwargs.get("description", ""),
            modules=modules,
        )
        return doc

    def to_markdown(self, doc: APIDocumentation, template: Optional[str] = None) -> str:
        """生成Markdown格式文档"""
        return self.template_engine.render_markdown(doc, template)

    def to_html(self, doc: APIDocumentation, template: Optional[str] = None) -> str:
        """生成HTML格式文档"""
        return self.template_engine.render_html(doc, template)

    def to_openapi(self, doc: APIDocumentation) -> dict:
        """生成OpenAPI格式文档"""
        return self.template_engine.render_openapi(doc)

    def save_markdown(self, doc: APIDocumentation, output_path: str, template: Optional[str] = None):
        """保存Markdown文档到文件"""
        content = self.to_markdown(doc, template)
        Path(output_path).write_text(content, encoding="utf-8")
        return output_path

    def save_html(self, doc: APIDocumentation, output_path: str, template: Optional[str] = None):
        """保存HTML文档到文件"""
        content = self.to_html(doc, template)
        Path(output_path).write_text(content, encoding="utf-8")
        return output_path

    def save_openapi(self, doc: APIDocumentation, output_path: str):
        """保存OpenAPI文档到文件"""
        content = self.to_openapi(doc)
        Path(output_path).write_text(
            json.dumps(content, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        return output_path
