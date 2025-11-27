# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all, copy_metadata
import os

block_cipher = None

# 1. Collect standard Streamlit data/binaries
st_datas, st_binaries, st_hiddenimports = collect_all('streamlit')

# 2. Collect metadata, but handle directories manually to avoid IsADirectoryError
raw_metadata = copy_metadata('streamlit')
metadata_datas = []

for src, dest in raw_metadata:
    if os.path.isdir(src):
        # If the metadata entry is a directory, walk it and add files individually
        for root, dirs, files in os.walk(src):
            for f in files:
                file_src = os.path.join(root, f)
                # Calculate relative path to maintain structure in destination
                rel_path = os.path.relpath(file_src, src)
                # dest is the folder name in the bundle (e.g., streamlit-1.45.1.dist-info)
                # We construct the full destination path, then take dirname because
                # PyInstaller datas expects (source_file, dest_directory)
                target_file_path = os.path.join(dest, rel_path)
                target_dir = os.path.dirname(target_file_path)
                metadata_datas.append((file_src, target_dir))
    else:
        # If it's a file, just add it (dest in copy_metadata includes filename, so we take dirname)
        metadata_datas.append((src, os.path.dirname(dest)))

# 3. Combine all data
# Add app.py to the root (.) of the bundle
# Add the 'utils' folder to the 'utils' folder in the bundle
final_datas = st_datas + metadata_datas + [
    ('app.py', '.'),
    ('utils', 'utils'),
    ('assets', 'assets'),
    ('data', 'data'),
    ('pages', 'pages')
]

a = Analysis(
    ['run_app.py'],
    pathex=[os.getcwd()], 
    binaries=st_binaries,
    datas=final_datas,
    # Updated hiddenimports to include specific reportlab submodules
    hiddenimports=[
        'pandas', 
        'plotly', 
        'openpyxl', 
        'reportlab',
        'reportlab.platypus',
        'reportlab.lib.styles',
        'reportlab.lib.pagesizes',
        'reportlab.pdfgen'
    ] + st_hiddenimports,
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Project_METIS',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)