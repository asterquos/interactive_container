@echo off
chcp 65001 >nul 2>&1
echo 集装箱装载管理系统 - 修复版构建脚本
echo ========================================

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

REM 检查main.py是否存在
if not exist main.py (
    echo 错误: 找不到main.py文件
    echo 请确保在项目根目录下运行此脚本
    pause
    exit /b 1
)

echo.
echo 步骤1: 升级pip和安装构建工具...
python -m pip install --upgrade pip setuptools wheel

echo.
echo 步骤2: 安装项目依赖...
if exist requirements.txt (
    python -m pip install -r requirements.txt
) else (
    echo 手动安装核心依赖...
    python -m pip install PyQt5 pandas numpy openpyxl xlrd matplotlib reportlab
)

echo.
echo 步骤3: 安装PyInstaller...
python -m pip install pyinstaller

echo.
echo 步骤4: 清理之前的构建...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__

echo.
echo 步骤5: 使用稳定版spec文件构建...
if exist container_loader_stable.spec (
    echo 使用稳定版spec文件...
    pyinstaller --clean container_loader_stable.spec
) else (
    echo 使用命令行参数构建...
    pyinstaller ^
        --onefile ^
        --windowed ^
        --name="ContainerLoader" ^
        --add-data="data;data" ^
        --hidden-import="gui.main_window" ^
        --hidden-import="gui.container_view" ^
        --hidden-import="gui.box_list_panel" ^
        --hidden-import="gui.info_panel" ^
        --hidden-import="core.box" ^
        --hidden-import="core.container" ^
        --hidden-import="utils.excel_reader" ^
        --hidden-import="utils.pdf_generator" ^
        --hidden-import="utils.project_manager" ^
        --hidden-import="data.sample_boxes" ^
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
)

if errorlevel 1 (
    echo.
    echo 构建失败！请检查上面的错误信息。
    echo.
    echo 常见解决方案:
    echo 1. 确保所有依赖都已正确安装
    echo 2. 检查Python和PyQt5版本兼容性
    echo 3. 尝试在虚拟环境中构建
    pause
    exit /b 1
)

echo.
echo ========================================
echo 构建成功！

if exist "dist\ContainerLoader.exe" (
    for %%I in ("dist\ContainerLoader.exe") do set filesize=%%~zI
    set /a filesizeMB=!filesize!/1048576
    echo 可执行文件: dist\ContainerLoader.exe
    echo 文件大小: !filesizeMB! MB
    
    echo.
    echo 正在测试可执行文件...
    echo 如果程序能正常启动，请关闭它以继续...
    start /wait "测试程序" "dist\ContainerLoader.exe"
    
    echo.
    echo 测试完成！
) else (
    echo 警告: 找不到生成的exe文件
)

echo.
echo 使用说明:
echo 1. 可执行文件位于: dist\ContainerLoader.exe
echo 2. 可以将dist目录整体复制到其他机器运行
echo 3. 如遇到杀毒软件误报，请添加白名单

pause