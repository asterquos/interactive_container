@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
title 集装箱装载管理系统 - 打包工具

echo ================================================
echo 集装箱装载管理系统 v1.2 - 打包工具
echo ================================================

:: 检查虚拟环境是否存在
if not exist "venv\Scripts\activate.bat" (
    echo 错误: 虚拟环境不存在
    echo 请先运行 setup_windows.bat 设置环境
    pause
    exit /b 1
)

:: 激活虚拟环境
call venv\Scripts\activate.bat

:: 运行打包脚本
python build_windows.py

if %errorlevel% equ 0 (
    echo.
    echo ================================================
    echo 打包成功！
    echo 输出目录: dist\
    echo 可执行文件: dist\集装箱装载管理系统\集装箱装载管理系统.exe
    echo ================================================
    echo.
    set /p open_choice="是否打开输出目录? (Y/n): "
    if /i not "!open_choice!"=="n" (
        explorer dist
    )
) else (
    echo.
    echo 打包失败，请检查错误信息
)

pause