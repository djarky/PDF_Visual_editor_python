# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for PDF Visual Editor
# This spec file works for both Windows and Linux builds
# Usage:
#   Windows: pyinstaller pdf_visual_editor.spec
#   Linux:   pyinstaller pdf_visual_editor.spec

from PyInstaller.utils.hooks import copy_metadata

block_cipher = None

# Define all data files to include
datas = [
    ('themes/*.qss', 'themes'),
    ('resources/logo_dark.png', 'resources'),
    ('resources/logo_light.png', 'resources'),
    ('resources/about.html', 'resources'),
    ('resources/help.html', 'resources'),
    ('resources/shortcuts.html', 'resources'),
]

# Include metadata for pikepdf (required for version check)
datas += copy_metadata('pikepdf')
# Also include metadata for pdfminer.six just in case
datas += copy_metadata('pdfminer.six')

# Hidden imports for Qt frameworks and other modules that PyInstaller might miss
# Includes both PyQt6 and PySide2 to support either framework
hiddenimports = [
    # PyQt6 imports (try these first)
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    'PyQt6.QtPrintSupport',
    # PySide6 imports
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'PySide6.QtPrintSupport',
    # PySide2 imports (fallback)
    'PySide2.QtCore',
    'PySide2.QtGui',
    'PySide2.QtWidgets',
    'PySide2.QtPrintSupport',
    # PDF libraries
    'fitz',  # PyMuPDF
    'pikepdf',
    'pdfminer',
    'pdfminer.six',
    # Image library
    'PIL',
    'PIL.Image',
    # Backports for Python < 3.8
    'importlib_metadata',
    'zipp',
]

# Detect available Qt bindings and configure excludes
excludes = []
try:
    import PyQt6
    print("Building with PyQt6")
    excludes.extend(['PySide6', 'PySide2'])
except ImportError:
    try:
        import PySide6
        print("Building with PySide6")
        excludes.extend(['PyQt6', 'PySide2'])
    except ImportError:
        try:
            import PySide2
            print("Building with PySide2")
            excludes.extend(['PyQt6', 'PySide6'])
        except ImportError:
            print("Warning: No Qt bindings found!")

# Filter hiddenimports to remove excluded packages
hiddenimports = [h for h in hiddenimports if not any(h.startswith(e) for e in excludes)]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PDF Visual Editor',
    icon='app_icon.ico',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI application, no console window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    
)
