# -*- mode: python ; coding: utf-8 -*-
# PyInstaller 打包配置文件 - 免疫大作战

import sys
import os

block_cipher = None

# 获取当前目录
current_dir = os.path.dirname(os.path.abspath(SPEC))

# 需要打包的数据文件
datas = [
    ('中国球.png', '.'),
    ('铁剑.png', '.'),
    ('logo.png', '.'),  # 窗口图标
    ('STHeiti Light.ttc', '.'),
    ('graphics_enhancement.py', '.'),
    ('images', 'images'),  # 病毒图片目录
]

# 过滤掉不存在的文件和目录
datas = [(src, dst) for src, dst in datas if os.path.exists(os.path.join(current_dir, src))]

# 根据平台选择图标文件
if sys.platform == 'win32':
    icon_file = 'logo.ico'
elif sys.platform == 'darwin':
    icon_file = 'logo.icns'
else:
    icon_file = None

# 检查图标文件是否存在
if icon_file and not os.path.exists(os.path.join(current_dir, icon_file)):
    icon_file = None

a = Analysis(
    ['main.py'],
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

# 使用 onedir 模式（不合并到单个文件）
exe = EXE(
    pyz,
    a.scripts,
    [],  # 不包含 binaries, zipfiles, datas - 这些放在 COLLECT 中
    exclude_binaries=True,  # 关键：启用 onedir 模式
    name='免疫大作战',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file,  # 可执行文件图标
)

# 收集所有文件到一个目录
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='免疫大作战',
)

# macOS 专用：创建 .app 包
if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='免疫大作战.app',
        icon='logo.icns',
        bundle_identifier='com.immune.battle',
        info_plist={
            'CFBundleName': '免疫大作战',
            'CFBundleDisplayName': '免疫大作战',
            'CFBundleVersion': '1.0.0',
            'CFBundleShortVersionString': '1.0.0',
            'NSHighResolutionCapable': True,
            'LSMinimumSystemVersion': '10.13.0',
        },
    )
