"""
py2app setup script for API Doc Generator macOS application.
Build with: python packaging/py2app_setup.py py2app
"""
from setuptools import setup

APP = ['src/macos/app.py']
DATA_FILES = [
    ('src/web/static', ['src/web/static/index.html']),
]
OPTIONS = {
    'argv_emulation': False,
    'plist': {
        'CFBundleName': 'API Doc Generator',
        'CFBundleDisplayName': 'API Doc Generator',
        'CFBundleIdentifier': 'com.apidocgen.app',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHumanReadableCopyright': 'MIT License',
    },
    'packages': [
        'fastapi', 'uvicorn', 'pydantic', 'starlette',
        'jinja2', 'yaml', 'rich',
    ],
    'includes': [
        'tkinter', 'json', 'threading', 'webbrowser',
        'src.web.app', 'api_doc_generator',
    ],
    'excludes': ['numpy', 'torch'],
}

setup(
    name='API Doc Generator',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
