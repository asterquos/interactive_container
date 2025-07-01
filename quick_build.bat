@echo off
echo 快速打包测试
call venv\Scripts\activate
python -m PyInstaller --onefile --windowed --name 集装箱管理系统 main.py
pause