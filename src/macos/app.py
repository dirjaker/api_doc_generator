"""
macOS GUI wrapper for API Doc Generator
Provides a tkinter interface for generating API documentation and running the web dashboard.
"""
import sys
import os
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class APIDocGenApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("API Doc Generator")
        self.root.geometry("800x600")
        self.root.configure(bg="#0d1117")

        self.server_thread = None
        self.server_running = False
        self.server_instance = None

        self._build_ui()

    def _build_ui(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#0d1117")
        style.configure("TLabel", background="#0d1117", foreground="#c9d1d9", font=("Helvetica", 12))
        style.configure("Header.TLabel", font=("Helvetica", 18, "bold"), foreground="#58a6ff")
        style.configure("Status.TLabel", font=("Helvetica", 11), foreground="#8b949e")

        # Header
        header = ttk.Frame(self.root)
        header.pack(fill=tk.X, padx=20, pady=(20, 10))
        ttk.Label(header, text="API Doc Generator", style="Header.TLabel").pack(side=tk.LEFT)
        self.status_label = ttk.Label(header, text="Web Server: Stopped", style="Status.TLabel")
        self.status_label.pack(side=tk.RIGHT)

        # Server controls
        ctrl_frame = ttk.Frame(self.root)
        ctrl_frame.pack(fill=tk.X, padx=20, pady=10)

        self.start_btn = ttk.Button(ctrl_frame, text="Start Web Server", command=self.toggle_server)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(ctrl_frame, text="Open in Browser", command=self.open_browser).pack(side=tk.LEFT)

        port_frame = ttk.Frame(self.root)
        port_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        ttk.Label(port_frame, text="Port:").pack(side=tk.LEFT)
        self.port_var = tk.StringVar(value="8080")
        ttk.Entry(port_frame, textvariable=self.port_var, width=8).pack(side=tk.LEFT, padx=8)

        # Generate docs section
        gen_frame = ttk.LabelFrame(self.root, text="Generate Documentation")
        gen_frame.pack(fill=tk.X, padx=20, pady=10)

        path_row = ttk.Frame(gen_frame)
        path_row.pack(fill=tk.X, padx=10, pady=8)
        ttk.Label(path_row, text="Source:").pack(side=tk.LEFT)
        self.src_var = tk.StringVar()
        ttk.Entry(path_row, textvariable=self.src_var, width=50).pack(side=tk.LEFT, padx=8)
        ttk.Button(path_row, text="Browse", command=self.browse_source).pack(side=tk.LEFT)

        opt_row = ttk.Frame(gen_frame)
        opt_row.pack(fill=tk.X, padx=10, pady=(0, 8))
        ttk.Label(opt_row, text="Format:").pack(side=tk.LEFT)
        self.format_var = tk.StringVar(value="markdown")
        ttk.Combobox(opt_row, textvariable=self.format_var, values=["markdown", "html", "openapi"], width=12, state="readonly").pack(side=tk.LEFT, padx=8)
        ttk.Label(opt_row, text="Title:").pack(side=tk.LEFT)
        self.title_var = tk.StringVar(value="API Documentation")
        ttk.Entry(opt_row, textvariable=self.title_var, width=30).pack(side=tk.LEFT, padx=8)
        ttk.Button(opt_row, text="Generate", command=self.generate_docs).pack(side=tk.LEFT, padx=8)

        # Log area
        ttk.Label(self.root, text="Output:").pack(anchor=tk.W, padx=20, pady=(10, 0))
        self.log_area = scrolledtext.ScrolledText(
            self.root, height=12, bg="#161b22", fg="#c9d1d9",
            insertbackground="#c9d1d9", font=("SF Mono", 11), borderwidth=1, relief=tk.FLAT
        )
        self.log_area.pack(fill=tk.BOTH, expand=True, padx=20, pady=(4, 20))

        self.log("API Doc Generator GUI initialized.")

    def log(self, msg):
        self.log_area.insert(tk.END, f"{msg}\n")
        self.log_area.see(tk.END)

    def browse_source(self):
        path = filedialog.askdirectory() or filedialog.askopenfilename(filetypes=[("Python files", "*.py"), ("All files", "*.*")])
        if path:
            self.src_var.set(path)

    def toggle_server(self):
        if self.server_running:
            self.stop_server()
        else:
            self.start_server()

    def start_server(self):
        port = int(self.port_var.get())
        self.log(f"Starting web server on port {port}...")

        def run():
            try:
                import uvicorn
                from src.web.app import app
                self.server_instance = uvicorn.Server(uvicorn.Config(app, host="0.0.0.0", port=port, log_level="warning"))
                self.server_instance.run()
            except Exception as e:
                self.root.after(0, lambda: self.log(f"Server error: {e}"))
                self.root.after(0, lambda: self._set_server_state(False))

        self.server_thread = threading.Thread(target=run, daemon=True)
        self.server_thread.start()
        self._set_server_state(True)
        self.log(f"Web server started at http://localhost:{port}")

    def stop_server(self):
        if self.server_instance:
            self.server_instance.should_exit = True
        self._set_server_state(False)
        self.log("Web server stopped.")

    def _set_server_state(self, running):
        self.server_running = running
        if running:
            self.start_btn.configure(text="Stop Web Server")
            self.status_label.configure(text="Web Server: Running", foreground="#3fb950")
        else:
            self.start_btn.configure(text="Start Web Server")
            self.status_label.configure(text="Web Server: Stopped", foreground="#8b949e")

    def open_browser(self):
        import webbrowser
        port = self.port_var.get()
        webbrowser.open(f"http://localhost:{port}")
        self.log(f"Opened browser at http://localhost:{port}")

    def generate_docs(self):
        source = self.src_var.get().strip()
        if not source:
            messagebox.showwarning("Warning", "Please select a source path.")
            return
        if not Path(source).exists():
            messagebox.showerror("Error", f"Path not found: {source}")
            return

        self.log(f"Generating {self.format_var.get()} documentation from: {source}")
        try:
            from api_doc_generator.doc_generator import DocGenerator
            generator = DocGenerator()
            path = Path(source)
            if path.is_dir():
                doc = generator.generate_from_directory(str(path), title=self.title_var.get())
            else:
                doc = generator.generate_from_file(str(path), title=self.title_var.get())

            total = sum(len(m.endpoints) for m in doc.modules)
            self.log(f"Found {len(doc.modules)} module(s), {total} endpoint(s)")

            fmt = self.format_var.get()
            output_ext = {"markdown": ".md", "html": ".html", "openapi": ".json"}[fmt]
            output_path = str(path.parent / f"api_docs{output_ext}")

            if fmt == "markdown":
                generator.save_markdown(doc, output_path)
            elif fmt == "html":
                generator.save_html(doc, output_path)
            else:
                generator.save_openapi(doc, output_path)

            self.log(f"Documentation saved to: {output_path}")
        except Exception as e:
            self.log(f"Error: {e}")

    def run(self):
        self.root.mainloop()


def main():
    app = APIDocGenApp()
    app.run()


if __name__ == "__main__":
    main()
