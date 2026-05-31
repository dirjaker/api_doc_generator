"""FastAPI服务 - 在线预览文档"""
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, JSONResponse
from .doc_generator import DocGenerator
from .models import APIDocumentation

app = FastAPI(title="API Doc Generator", version="1.0.0")

# 全局文档缓存
_cached_doc: Optional[APIDocumentation] = None
_cached_source: Optional[str] = None


def get_generator(template_dir: Optional[str] = None) -> DocGenerator:
    return DocGenerator(template_dir)


def get_doc(source: str, title: str = "API Documentation", version: str = "1.0.0") -> APIDocumentation:
    """获取或缓存文档"""
    global _cached_doc, _cached_source
    if _cached_doc and _cached_source == source:
        return _cached_doc

    generator = get_generator()
    path = Path(source)
    if path.is_dir():
        _cached_doc = generator.generate_from_directory(source, title=title, version=version)
    else:
        _cached_doc = generator.generate_from_file(source, title=title, version=version)
    _cached_source = source
    return _cached_doc


@app.get("/")
async def root():
    """根路径 - 使用说明"""
    return {
        "message": "API Doc Generator - 在线文档预览",
        "endpoints": {
            "/docs/markdown": "查看Markdown格式文档",
            "/docs/html": "查看HTML格式文档",
            "/docs/openapi": "查看OpenAPI格式文档",
            "/health": "健康检查",
        }
    }


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "ok"}


@app.get("/docs/html", response_class=HTMLResponse)
async def get_html_docs(
    source: str = Query(..., description="源代码文件或目录路径"),
    title: str = Query("API Documentation", description="文档标题"),
    version: str = Query("1.0.0", description="API版本"),
    template: Optional[str] = Query(None, description="自定义模板名称"),
):
    """获取HTML格式API文档"""
    doc = get_doc(source, title, version)
    generator = get_generator()
    html = generator.to_html(doc, template)
    return HTMLResponse(content=html)


@app.get("/docs/markdown")
async def get_markdown_docs(
    source: str = Query(..., description="源代码文件或目录路径"),
    title: str = Query("API Documentation", description="文档标题"),
    version: str = Query("1.0.0", description="API版本"),
    template: Optional[str] = Query(None, description="自定义模板名称"),
):
    """获取Markdown格式API文档"""
    doc = get_doc(source, title, version)
    generator = get_generator()
    md = generator.to_markdown(doc, template)
    return {"content": md}


@app.get("/docs/openapi")
async def get_openapi_docs(
    source: str = Query(..., description="源代码文件或目录路径"),
    title: str = Query("API Documentation", description="文档标题"),
    version: str = Query("1.0.0", description="API版本"),
):
    """获取OpenAPI格式API文档"""
    doc = get_doc(source, title, version)
    generator = get_generator()
    openapi = generator.to_openapi(doc)
    return JSONResponse(content=openapi)


def run_server(host: str = "0.0.0.0", port: int = 8000):
    """启动服务器"""
    import uvicorn
    uvicorn.run(app, host=host, port=port)
