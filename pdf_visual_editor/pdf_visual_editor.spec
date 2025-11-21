# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for PDF Visual Editor
# This spec file works for both Windows and Linux builds
# Usage:
#   Windows: pyinstaller pdf_visual_editor.spec
#   Linux:   pyinstaller pdf_visual_editor.spec

block_cipher = None

# Define all data files to include
datas = [
    ('themes/*.qss', 'themes'),
    ('resources/logo_dark.png', 'resources'),
    ('resources/logo_light.png', 'resources'),
    ('resources/logo_ia.png', 'resources'),
]

# Hidden imports for PyQt6 and other modules that PyInstaller might miss
hiddenimports = [
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    'PyQt6.QtPrintSupport',
    'fitz',  # PyMuPDF
    'pikepdf',
    'pdfminer',
    'pdfminer.six',
    'PIL',
    'PIL.Image',
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
