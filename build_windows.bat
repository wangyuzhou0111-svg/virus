@echo off
chcp 65001 >nul
echo === 迷宫大冒险 Windows 打包脚本 ===
echo.

:: 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 Python，请先安装 Python
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: 安装依赖
echo [1/3] 安装依赖...
pip install pygame pyinstaller pillow -q

:: 切换到脚本所在目录
cd /d "%~dp0"

:: 清理旧的构建文件
echo [2/3] 清理旧文件...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build

:: 打包
echo [3/3] 开始打包...
pyinstaller --clean build_config.spec

:: 检查结果
if exist "dist\迷宫大冒险\迷宫大冒险.exe" (
    echo.
    echo ============================================
    echo           打包成功!
    echo ============================================
    echo.
    echo 游戏位置: dist\迷宫大冒险\迷宫大冒险.exe
    echo.
    echo 你可以:
    echo   1. 双击运行 dist\迷宫大冒险\迷宫大冒险.exe
    echo   2. 将整个 dist\迷宫大冒险 文件夹复制给其他人
    echo.
    explorer "dist\迷宫大冒险"
) else (
    echo.
    echo 打包失败，请检查错误信息
)

pause
