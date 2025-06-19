#!/bin/bash

echo "使用Wine在WSL中构建Windows可执行文件"
echo "注意：这种方法可能不稳定，推荐在真实Windows环境中构建"
echo "========================================"

# 检查Wine是否安装
if ! command -v wine &> /dev/null; then
    echo "Wine未安装，正在安装..."
    sudo apt update
    sudo apt install wine wine32 wine64 -y
fi

# 检查Python Windows版本是否安装
if [ ! -f "$HOME/.wine/drive_c/Python310/python.exe" ]; then
    echo "需要在Wine中安装Windows版Python"
    echo "请从python.org下载Windows安装程序并使用wine运行"
    exit 1
fi

# 使用Wine运行Python
echo "使用Wine Python安装依赖..."
wine "$HOME/.wine/drive_c/Python310/python.exe" -m pip install -r requirements.txt
wine "$HOME/.wine/drive_c/Python310/python.exe" -m pip install pyinstaller

echo "使用Wine构建..."
wine "$HOME/.wine/drive_c/Python310/Scripts/pyinstaller.exe" --clean container_loader.spec

echo "构建完成（如果成功）"