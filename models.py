"""数据模型 - API信息、参数、响应"""
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
    """API模块模型"""
    name: str
    description: str = ""
    endpoints: list[APIEndpoint] = field(default_factory=list)


@dataclass
class APIDocumentation:
    """API文档模型"""
    title: str = "API Documentation"
    version: str = "1.0.0"
    description: str = ""
    modules: list[APIModule] = field(default_factory=list)
