@echo off
chcp 65001 >nul
title 集装箱装载管理系统

echo 启动集装箱装载管理系统...

:: 检查虚拟环境是否存在
if not exist "venv\Scripts\activate.bat" (
    echo 错误: 虚拟环境不存在
    echo 请先运行 setup_windows.bat 设置环境
    pause
    exit /b 1
)

:: 激活虚拟环境并运行程序
call venv\Scripts\activate.bat
python main.py

if %errorlevel% neq 0 (
    echo.
    echo 程序运行出错
    pause
)