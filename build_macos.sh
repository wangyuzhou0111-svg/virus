#!/bin/bash
# macOS 打包脚本

echo "=== 地牢探索游戏 macOS 打包脚本 ==="

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 python3，请先安装 Python"
    exit 1
fi

# 安装依赖
echo "1. 安装依赖..."
pip3 install pygame pyinstaller

# 切换到脚本所在目录
cd "$(dirname "$0")"

# 打包
echo "2. 开始打包..."
pyinstaller --clean build_config.spec

# 检查结果
if [ -d "dist/DungeonExplorer.app" ]; then
    echo ""
    echo "=== 打包成功! ==="
    echo "应用位置: dist/DungeonExplorer.app"
    echo ""
    echo "你可以:"
    echo "  1. 双击运行 dist/DungeonExplorer.app"
    echo "  2. 将 DungeonExplorer.app 拖到 Applications 文件夹安装"
    echo ""

    # 打开输出目录
    open dist/
else
    echo "打包失败，请检查错误信息"
    exit 1
fi
