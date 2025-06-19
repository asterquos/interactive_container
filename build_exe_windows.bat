@echo off
echo 集装箱装载管理系统 Windows打包脚本
echo =====================================

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

echo.
echo 步骤1: 安装依赖包...
pip install -r requirements.txt
if errorlevel 1 (
    echo 错误: 安装依赖包失败
    pause
    exit /b 1
)

echo.
echo 步骤2: 安装PyInstaller...
pip install pyinstaller
if errorlevel 1 (
    echo 错误: 安装PyInstaller失败
    pause
    exit /b 1
)

echo.
echo 步骤3: 构建可执行文件...
pyinstaller --clean container_loader.spec
if errorlevel 1 (
    echo 错误: 构建失败
    pause
    exit /b 1
)

echo.
echo =====================================
echo 构建成功！
echo 可执行文件位置: dist\ContainerLoader.exe
echo.
pause