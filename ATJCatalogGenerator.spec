# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for ATJ Facebook Catalog Generator (GUI build)
#
# Build with:  pyinstaller ATJCatalogGenerator.spec
# Output EXE:  dist/ATJCatalogGenerator.exe  (Windows) or dist/ATJCatalogGenerator (Linux/Mac)

import sys
from pathlib import Path

block_cipher = None
PROJECT_ROOT = Path(SPECPATH)

a = Analysis(
    ['run_gui.py'],
    pathex=[str(PROJECT_ROOT)],
    binaries=[],
    datas=[
        # Bundle empty input/output/logs folder placeholders so the frozen
        # app has somewhere to read/write on first run.
        (str(PROJECT_ROOT / 'input'), 'input'),
    ],
    hiddenimports=[
        'openpyxl',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'PyQt5', 'PyQt6'],
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
    name='ATJCatalogGenerator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,          # set True temporarily if you need to see errors
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,              # put an .ico path here if you have a logo, e.g. 'assets/icon.ico'
)
