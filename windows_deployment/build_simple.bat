@echo off
echo 集装箱装载管理系统 - 简单构建脚本
echo =====================================

REM 检查main.py是否存在
if not exist main.py (
    echo 错误: 找不到main.py文件
    echo 请确保在项目根目录下运行此脚本
    pause
    exit /b 1
)

echo.
echo 使用PyInstaller直接构建...
echo.

REM 直接使用pyinstaller命令，不依赖spec文件
pyinstaller --onefile ^
    --windowed ^
    --name="ContainerLoader" ^
    --add-data="data;data" ^
    --hidden-import="pandas" ^
    --hidden-import="numpy" ^
    --hidden-import="openpyxl" ^
    --hidden-import="xlrd" ^
    --hidden-import="matplotlib" ^
    --hidden-import="reportlab" ^
    --hidden-import="PyQt5.QtCore" ^
    --hidden-import="PyQt5.QtGui" ^
    --hidden-import="PyQt5.QtWidgets" ^
    --hidden-import="PyQt5.sip" ^
    --clean ^
    main.py

if errorlevel 1 (
    echo.
    echo 构建失败！
    echo 请检查错误信息
    pause
    exit /b 1
)

echo.
echo =====================================
echo 构建成功！
echo 可执行文件位置: dist\ContainerLoader.exe
echo.
pause