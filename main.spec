# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['main.pyw'],
    pathex=[],
    binaries=[],
    datas=[('exported_maps\\exported_maps.txt', 'exported_maps'),
    ("mod_data\\mod_data.txt", "mod_data"),
    ("fonts\\*", "fonts"),
    ("graphics\\*", "graphics"),
    ("README.md", '.'),
    ("config.cfg", '.'),
    ("LICENSE.txt", '.'),
    ("midpointlist.csv", '.')],
    hiddenimports=[],
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
    [],
    exclude_binaries=True,
    name='eu4-war-explorer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='eu4-war-explorer-windows',
)
