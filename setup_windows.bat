@echo off
chcp 65001 >nul
title 集装箱装载管理系统 - Windows环境设置

echo ================================================
echo 集装箱装载管理系统 - Windows环境设置
echo ================================================
echo.

:: 检查Python是否已安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未检测到Python
    echo 请先安装Python 3.8或更高版本
    echo 下载地址: https://www.python.org/downloads/
    echo 安装时请确保勾选 "Add Python to PATH"
    pause
    exit /b 1
)

echo 检测到Python版本:
python --version

:: 检查是否已存在虚拟环境
if exist "venv" (
    echo.
    echo 检测到已存在的虚拟环境
    set /p choice="是否删除并重新创建? (y/N): "
    if /i "!choice!"=="y" (
        echo 删除旧的虚拟环境...
        rmdir /s /q venv
    ) else (
        echo 使用现有虚拟环境
        goto :activate_env
    )
)

:: 创建虚拟环境
echo.
echo 创建Python虚拟环境...
python -m venv venv
if %errorlevel% neq 0 (
    echo 错误: 虚拟环境创建失败
    pause
    exit /b 1
)

:activate_env
:: 激活虚拟环境
echo.
echo 激活虚拟环境...
call venv\Scripts\activate.bat

:: 升级pip
echo.
echo 升级pip...
python -m pip install --upgrade pip

:: 安装依赖
echo.
echo 安装项目依赖...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo 错误: 依赖安装失败
    pause
    exit /b 1
)

:: 测试运行
echo.
echo 环境设置完成！
echo.
set /p test_choice="是否测试运行程序? (Y/n): "
if /i "!test_choice!"=="n" goto :end

echo.
echo 启动测试...
python main.py

:end
echo.
echo ================================================
echo 环境设置完成！
echo.
echo 使用方法:
echo 1. 运行程序: 
echo    - 双击 run_windows.bat
echo    - 或手动: venv\Scripts\activate.bat 然后 python main.py
echo.
echo 2. 打包程序: 
echo    - 双击 build_windows.bat
echo    - 或手动: venv\Scripts\activate.bat 然后 python build_windows.py
echo ================================================
pause