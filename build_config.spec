# -*- mode: python ; coding: utf-8 -*-
# PyInstaller 打包配置文件

import sys
import os

block_cipher = None

# 获取当前目录
current_dir = os.path.dirname(os.path.abspath(SPEC))

# 需要打包的数据文件
datas = [
    ('中国球.png', '.'),
    ('铁剑.png', '.'),
    ('STHeiti Light.ttc', '.'),
    ('graphics_enhancement.py', '.'),
]

# 过滤掉不存在的文件
datas = [(src, dst) for src, dst in datas if os.path.exists(os.path.join(current_dir, src))]

a = Analysis(
    ['001.py'],
    pathex=[current_dir],
    binaries=[],
    datas=datas,
    hiddenimports=['pygame'],
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
    name='DungeonExplorer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 可以在这里指定图标文件 icon='icon.ico' (Windows) 或 icon='icon.icns' (macOS)
)

# macOS 专用：创建 .app 包
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='DungeonExplorer.app',
        icon=None,  # 可以指定 .icns 图标
        bundle_identifier='com.dungeon.explorer',
        info_plist={
            'CFBundleName': 'Dungeon Explorer',
            'CFBundleDisplayName': 'Dungeon Explorer',
            'CFBundleVersion': '1.0.0',
            'CFBundleShortVersionString': '1.0.0',
            'NSHighResolutionCapable': True,
        },
    )
