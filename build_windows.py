#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows打包脚本
使用PyInstaller将项目打包成Windows可执行文件
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def clean_build_dirs():
    """清理之前的构建目录"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"清理目录: {dir_name}")
            shutil.rmtree(dir_name)

def copy_resources():
    """复制资源文件到dist目录"""
    if not os.path.exists('dist'):
        return
    
    # 复制测试数据
    if os.path.exists('test_data'):
        print("复制测试数据...")
        shutil.copytree('test_data', 'dist/test_data', dirs_exist_ok=True)
    
    # 复制README
    if os.path.exists('README.md'):
        shutil.copy2('README.md', 'dist/')
    
    # 复制图标（如果有）
    if os.path.exists('img.png'):
        shutil.copy2('img.png', 'dist/')

def create_spec_file():
    """创建PyInstaller配置文件"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('test_data', 'test_data'),
        ('img.png', '.'),
    ],
    hiddenimports=[
        'PyQt5.QtCore',
        'PyQt5.QtGui', 
        'PyQt5.QtWidgets',
        'pandas',
        'numpy',
        'openpyxl',
        'xlrd',
        'matplotlib',
        'reportlab',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='集装箱装载管理系统',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # 窗口应用，不显示控制台
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='img.png',  # 应用图标
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='集装箱装载管理系统',
)
'''
    
    with open('container_app.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("已创建PyInstaller配置文件: container_app.spec")

def build_executable():
    """构建可执行文件"""
    print("开始构建Windows可执行文件...")
    
    # 使用spec文件构建
    cmd = [sys.executable, '-m', 'PyInstaller', '--clean', 'container_app.spec']
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("构建成功!")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("构建失败!")
        print(f"错误代码: {e.returncode}")
        print(f"错误输出: {e.stderr}")
        return False
    
    return True

def create_launcher_bat():
    """创建启动批处理文件"""
    bat_content = '''@echo off
chcp 65001 >nul
cd /d "%~dp0"
start "" "集装箱装载管理系统\\集装箱装载管理系统.exe"
'''
    
    with open('dist/启动集装箱管理系统.bat', 'w', encoding='utf-8') as f:
        f.write(bat_content)
    
    print("已创建启动批处理文件")

def create_readme():
    """创建用户说明文件"""
    readme_content = '''# 集装箱装载管理系统

## 使用说明

### 启动程序
双击 "启动集装箱管理系统.bat" 或直接运行 "集装箱装载管理系统.exe"

### 基本功能
1. **导入数据**: 文件 → 导入Excel文件
2. **创建集装箱**: 集装箱 → 新建集装箱
3. **拖拽装载**: 从左侧列表拖拽箱子到中央集装箱区域
4. **调整位置**: 直接拖动箱子调整位置
5. **旋转箱子**: 右键点击箱子选择旋转
6. **保存项目**: 文件 → 保存项目

### 示例数据
程序包含示例数据，可通过 "测试 → 加载示例数据" 快速体验功能

### 系统要求
- Windows 7/8/10/11
- 内存: 4GB以上推荐
- 磁盘空间: 500MB

### 技术支持
如遇到问题，请检查：
1. 是否有杀毒软件误报
2. 是否有足够的磁盘空间
3. Excel文件格式是否正确

版本: 1.0.0
'''
    
    with open('dist/使用说明.txt', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("已创建用户说明文件")

def main():
    """主函数"""
    print("=" * 50)
    print("集装箱装载管理系统 - Windows打包工具")
    print("=" * 50)
    
    # 检查是否在虚拟环境中
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("警告: 建议在虚拟环境中运行打包脚本")
        response = input("是否继续? (y/N): ")
        if response.lower() != 'y':
            return
    
    # 检查依赖
    try:
        import PyInstaller
        print(f"检测到PyInstaller版本: {PyInstaller.__version__}")
    except ImportError:
        print("错误: 未安装PyInstaller")
        print("请运行: pip install PyInstaller")
        return
    
    # 步骤1: 清理
    print("\n步骤1: 清理构建目录...")
    clean_build_dirs()
    
    # 步骤2: 创建配置文件
    print("\n步骤2: 创建PyInstaller配置...")
    create_spec_file()
    
    # 步骤3: 构建
    print("\n步骤3: 构建可执行文件...")
    if not build_executable():
        print("构建失败，退出...")
        return
    
    # 步骤4: 复制资源
    print("\n步骤4: 复制资源文件...")
    copy_resources()
    
    # 步骤5: 创建启动文件
    print("\n步骤5: 创建启动文件...")
    create_launcher_bat()
    create_readme()
    
    print("\n" + "=" * 50)
    print("打包完成!")
    print(f"输出目录: {os.path.abspath('dist')}")
    print("可执行文件: dist/集装箱装载管理系统/集装箱装载管理系统.exe")
    print("用户启动: dist/启动集装箱管理系统.bat")
    print("=" * 50)

if __name__ == "__main__":
    main()