"""
Web Dashboard for API Doc Generator
Provides a dashboard for generating and previewing API documentation.
"""
import sys
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add project root to path so we can import the api_doc_generator package
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from api_doc_generator.doc_generator import DocGenerator
from api_doc_generator.models import APIDocumentation

STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(
    title="API Doc Generator Dashboard",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cache
_cached_doc: Optional[APIDocumentation] = None
_cached_source: Optional[str] = None


def _get_generator(template_dir: Optional[str] = None) -> DocGenerator:
    return DocGenerator(template_dir)


def _get_doc(source: str, title: str = "API Documentation", version: str = "1.0.0") -> APIDocumentation:
    global _cached_doc, _cached_source
    if _cached_doc and _cached_source == source:
        return _cached_doc
    generator = _get_generator()
    path = Path(source)
    if path.is_dir():
        _cached_doc = generator.generate_from_directory(source, title=title, version=version)
    else:
        _cached_doc = generator.generate_from_file(source, title=title, version=version)
    _cached_source = source
    return _cached_doc


@app.get("/", response_class=HTMLResponse)
async def dashboard():
    html_path = STATIC_DIR / "index.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))


@app.get("/api/health")
async def health():
    return {"status": "ok"}


class GenerateRequest(BaseModel):
    source: str
    title: str = "API Documentation"
    version: str = "1.0.0"
    format: str = "markdown"


@app.post("/api/generate")
async def generate_docs(req: GenerateRequest):
    source = Path(req.source)
    if not source.exists():
        raise HTTPException(404, f"Source path not found: {req.source}")

    generator = _get_generator()
    if source.is_dir():
        doc = generator.generate_from_directory(str(source), title=req.title, version=req.version)
    else:
        doc = generator.generate_from_file(str(source), title=req.title, version=req.version)

    global _cached_doc, _cached_source
    _cached_doc = doc
    _cached_source = req.source

    total_endpoints = sum(len(m.endpoints) for m in doc.modules)
    modules = []
    for m in doc.modules:
        endpoints = []
        for ep in m.endpoints:
            endpoints.append({
                "path": ep.path,
                "method": ep.method,
                "summary": ep.summary,
                "description": ep.description,
                "parameters": [{"name": p.name, "type": p.type, "required": p.required, "default": p.default, "description": p.description} for p in ep.parameters],
                "tags": ep.tags,
            })
        modules.append({"name": m.name, "description": m.description, "endpoints": endpoints})

    result = {
        "title": doc.title,
        "version": doc.version,
        "description": doc.description,
        "total_endpoints": total_endpoints,
        "total_modules": len(doc.modules),
        "modules": modules,
    }

    if req.format == "markdown":
        result["content"] = generator.to_markdown(doc)
    elif req.format == "html":
        result["content"] = generator.to_html(doc)
    elif req.format == "openapi":
        result["content"] = generator.to_openapi(doc)

    return result


@app.get("/api/formats")
async def supported_formats():
    return {"formats": ["markdown", "html", "openapi"]}


def run_dashboard(host: str = "0.0.0.0", port: int = 8080):
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_dashboard()
