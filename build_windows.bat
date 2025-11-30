@echo off
chcp 65001 >nul
echo === 地牢探索游戏 Windows 打包脚本 ===

:: 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 Python，请先安装 Python
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: 安装依赖
echo 1. 安装依赖...
pip install pygame pyinstaller

:: 切换到脚本所在目录
cd /d "%~dp0"

:: 打包
echo 2. 开始打包...
pyinstaller --clean build_config.spec

:: 检查结果
if exist "dist\DungeonExplorer.exe" (
    echo.
    echo === 打包成功! ===
    echo 可执行文件位置: dist\DungeonExplorer.exe
    echo.
    echo 你可以双击运行 dist\DungeonExplorer.exe
    echo.
    explorer dist
) else (
    echo 打包失败，请检查错误信息
)

pause
