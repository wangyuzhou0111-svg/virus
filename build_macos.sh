#!/bin/bash
# macOS 打包脚本 - 免疫大作战

echo "=== 免疫大作战 macOS 打包脚本 ==="
echo

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 python3，请先安装 Python"
    exit 1
fi

# 切换到脚本所在目录
cd "$(dirname "$0")"

# 安装依赖
echo "[1/3] 安装依赖..."
pip3 install pygame pyinstaller pillow -q

# 清理旧文件
echo "[2/3] 清理旧文件..."
rm -rf dist build

# 打包
echo "[3/3] 开始打包..."
pyinstaller --clean build_config.spec

# 检查结果
if [ -d "dist/免疫大作战.app" ]; then
    echo
    echo "============================================"
    echo "           打包成功!"
    echo "============================================"
    echo
    echo "应用位置: dist/免疫大作战.app"
    echo
    echo "你可以:"
    echo "  1. 双击运行 dist/免疫大作战.app"
    echo "  2. 将 免疫大作战.app 拖到 Applications 文件夹安装"
    echo

    # 打开输出目录
    open dist/
else
    echo "打包失败，请检查错误信息"
    exit 1
fi
