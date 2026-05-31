"""代码解析器 - AST解析、提取路由、参数、类型注解"""
import ast
from pathlib import Path
from .models import APIModule, APIEndpoint, Parameter, Response


class CodeParser:
    """Python代码解析器，使用AST提取API信息"""

    FRAMEWORK_DECORATORS = {
        "fastapi": ["get", "post", "put", "delete", "patch"],
        "flask": ["route"],
        "django": ["path", "re_path"],
    }

    def parse_file(self, file_path: str) -> APIModule:
        """解析单个Python文件"""
        path = Path(file_path)
        with open(path, "r", encoding="utf-8") as f:
            source = f.read()

        tree = ast.parse(source)
        module = APIModule(name=path.stem)
        module.description = self._extract_module_docstring(tree)

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                endpoint = self._parse_function(node)
                if endpoint:
                    module.endpoints.append(endpoint)

        return module

    def parse_directory(self, dir_path: str) -> list[APIModule]:
        """解析目录下所有Python文件"""
        modules = []
        path = Path(dir_path)
        for py_file in path.rglob("*.py"):
            if py_file.name.startswith("_"):
                continue
            try:
                module = self.parse_file(str(py_file))
                if module.endpoints:
                    modules.append(module)
            except Exception as e:
                print(f"Warning: Failed to parse {py_file}: {e}")
        return modules

    def _extract_module_docstring(self, tree: ast.Module) -> str:
        """提取模块docstring"""
        if (tree.body and isinstance(tree.body[0], ast.Expr)
                and isinstance(tree.body[0].value, (ast.Str, ast.Constant))):
            node = tree.body[0].value
            return node.value if isinstance(node, ast.Constant) else node.s
        return ""

    def _parse_function(self, node) -> APIEndpoint | None:
        """解析函数，提取API端点信息"""
        decorators = self._extract_decorators(node)
        if not decorators:
            return None

        method, path = decorators
        docstring = ast.get_docstring(node) or ""

        endpoint = APIEndpoint(
            path=path,
            method=method.upper(),
            summary=docstring.split("\n")[0] if docstring else node.name,
            description=docstring,
            parameters=self._extract_parameters(node),
            responses=self._extract_responses(node),
        )
        return endpoint

    def _extract_decorators(self, node) -> tuple[str, str] | None:
        """提取装饰器信息"""
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

            elif isinstance(dec, ast.Attribute):
                # FastAPI: @app.get (without call)
                if dec.attr in self.FRAMEWORK_DECORATORS["fastapi"]:
                    return dec.attr, "/"

        return None

    def _extract_parameters(self, node) -> list[Parameter]:
        """提取函数参数"""
        params = []
        args = node.args

        # 处理普通参数
        for i, arg in enumerate(args.args):
            if arg.arg in ("self", "cls", "request", "response"):
                continue

            param = Parameter(name=arg.arg)
            if arg.annotation:
                param.type = self._get_annotation_str(arg.annotation)

            # 检查默认值
            defaults_offset = len(args.args) - len(args.defaults)
            default_idx = i - defaults_offset
            if default_idx >= 0 and default_idx < len(args.defaults):
                param.required = False
                param.default = self._get_default_str(args.defaults[default_idx])

            params.append(param)

        return params

    def _extract_responses(self, node) -> list[Response]:
        """提取响应类型"""
        responses = [Response()]
        if node.returns:
            type_str = self._get_annotation_str(node.returns)
            responses[0].type = type_str
        return responses

    def _get_annotation_str(self, node) -> str:
        """将类型注解转换为字符串"""
        if isinstance(node, ast.Constant):
            return str(node.value)
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            return f"{self._get_annotation_str(node.value)}.{node.attr}"
        if isinstance(node, ast.Subscript):
            base = self._get_annotation_str(node.value)
            inner = self._get_annotation_str(node.slice)
            return f"{base}[{inner}]"
        if isinstance(node, ast.Tuple):
            items = [self._get_annotation_str(e) for e in node.elts]
            return ", ".join(items)
        return "Any"

    def _get_default_str(self, node) -> str:
        """将默认值转换为字符串"""
        if isinstance(node, ast.Constant):
            return repr(node.value)
        if isinstance(node, ast.Name):
            return node.id
        return "..."
