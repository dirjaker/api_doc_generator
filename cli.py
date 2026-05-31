"""CLI入口 - 命令行一键生成文档"""
import argparse
import sys
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

from .doc_generator import DocGenerator

console = Console()


def create_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        prog="api-doc-gen",
        description="API文档生成器 - 从Python代码自动生成API文档",
    )
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # generate命令
    gen_parser = subparsers.add_parser("generate", help="生成API文档")
    gen_parser.add_argument("source", help="源代码文件或目录路径")
    gen_parser.add_argument("-o", "--output", help="输出文件路径")
    gen_parser.add_argument("-f", "--format", choices=["markdown", "html", "openapi"],
                           default="markdown", help="输出格式 (默认: markdown)")
    gen_parser.add_argument("-t", "--title", default="API Documentation", help="文档标题")
    gen_parser.add_argument("-v", "--version", default="1.0.0", help="API版本")
    gen_parser.add_argument("--template", help="自定义模板文件路径")

    # serve命令
    serve_parser = subparsers.add_parser("serve", help="启动在线预览服务器")
    serve_parser.add_argument("source", help="源代码文件或目录路径")
    serve_parser.add_argument("--host", default="0.0.0.0", help="服务器地址 (默认: 0.0.0.0)")
    serve_parser.add_argument("--port", type=int, default=8000, help="服务器端口 (默认: 8000)")
    serve_parser.add_argument("-t", "--title", default="API Documentation", help="文档标题")
    serve_parser.add_argument("--version", default="1.0.0", help="API版本")

    # info命令
    info_parser = subparsers.add_parser("info", help="查看源代码的API信息")
    info_parser.add_argument("source", help="源代码文件或目录路径")

    return parser


def cmd_generate(args):
    """执行生成命令"""
    source = Path(args.source)
    if not source.exists():
        console.print(f"[red]错误: 路径不存在: {source}[/red]")
        sys.exit(1)

    generator = DocGenerator(template_dir=str(Path(args.template).parent) if args.template else None)

    with console.status("[bold green]正在解析代码..."):
        if source.is_dir():
            doc = generator.generate_from_directory(str(source), title=args.title, version=args.version)
        else:
            doc = generator.generate_from_file(str(source), title=args.title, version=args.version)

    template_name = Path(args.template).name if args.template else None

    with console.status("[bold green]正在生成文档..."):
        if args.format == "markdown":
            output = args.output or "api_docs.md"
            generator.save_markdown(doc, output, template_name)
        elif args.format == "html":
            output = args.output or "api_docs.html"
            generator.save_html(doc, output, template_name)
        elif args.format == "openapi":
            output = args.output or "openapi.json"
            generator.save_openapi(doc, output)

    console.print(f"[green]✓ 文档已生成: {output}[/green]")
    console.print(f"  格式: {args.format}")
    console.print(f"  端点数: {sum(len(m.endpoints) for m in doc.modules)}")


def cmd_serve(args):
    """执行服务命令"""
    from .api import run_server, get_doc

    source = Path(args.source)
    if not source.exists():
        console.print(f"[red]错误: 路径不存在: {source}[/red]")
        sys.exit(1)

    console.print(Panel(
        f"[bold]API文档预览服务器[/bold]\n\n"
        f"源代码: {source}\n"
        f"地址: http://{args.host}:{args.port}\n\n"
        f"[dim]HTML文档: http://{args.host}:{args.port}/docs/html?source={source}[/dim]\n"
        f"[dim]Markdown文档: http://{args.host}:{args.port}/docs/markdown?source={source}[/dim]\n"
        f"[dim]OpenAPI文档: http://{args.host}:{args.port}/docs/openapi?source={source}[/dim]",
        title="启动服务器",
        border_style="green",
    ))

    run_server(host=args.host, port=args.port)


def cmd_info(args):
    """执行信息命令"""
    source = Path(args.source)
    if not source.exists():
        console.print(f"[red]错误: 路径不存在: {source}[/red]")
        sys.exit(1)

    generator = DocGenerator()

    with console.status("[bold green]正在解析代码..."):
        if source.is_dir():
            doc = generator.generate_from_directory(str(source))
        else:
            doc = generator.generate_from_file(str(source))

    console.print(f"\n[bold]源代码: {source}[/bold]\n")

    for module in doc.modules:
        table = Table(title=f"模块: {module.name}", show_header=True, header_style="bold cyan")
        table.add_column("方法", style="bold")
        table.add_column("路径")
        table.add_column("摘要")
        table.add_column("参数数")

        for endpoint in module.endpoints:
            method_color = {
                "GET": "green", "POST": "blue", "PUT": "yellow",
                "DELETE": "red", "PATCH": "cyan"
            }.get(endpoint.method, "white")

            table.add_row(
                f"[{method_color}]{endpoint.method}[/{method_color}]",
                endpoint.path,
                endpoint.summary[:50] + "..." if len(endpoint.summary) > 50 else endpoint.summary,
                str(len(endpoint.parameters)),
            )

        console.print(table)
        console.print()


def main():
    """主入口"""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    commands = {
        "generate": cmd_generate,
        "serve": cmd_serve,
        "info": cmd_info,
    }

    commands[args.command](args)


if __name__ == "__main__":
    main()
