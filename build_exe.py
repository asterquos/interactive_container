#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
集装箱装载管理系统打包脚本
使用PyInstaller将Python项目打包为Windows可执行文件
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def create_spec_file():
    """创建PyInstaller配置文件"""
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('data', 'data'),
        ('resources', 'resources'),
    ],
    hiddenimports=[
        'pandas',
        'numpy',
        'openpyxl',
        'xlrd',
        'matplotlib',
        'reportlab',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'PyQt5.sip',
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='集装箱装载管理系统',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/app.ico'  # 如果有图标文件
)
'''
    
    with open('container_loader.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("已创建PyInstaller配置文件: container_loader.spec")

def install_dependencies():
    """安装依赖包"""
    print("正在安装依赖包...")
    
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
        print("依赖包安装完成")
    except subprocess.CalledProcessError as e:
        print(f"安装依赖包时出错: {e}")
        return False
    
    return True

def build_executable():
    """构建可执行文件"""
    print("开始构建可执行文件...")
    
    try:
        # 使用spec文件构建
        subprocess.check_call(['pyinstaller', '--clean', 'container_loader.spec'])
        print("可执行文件构建完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"构建可执行文件时出错: {e}")
        return False

def copy_additional_files():
    """复制额外的文件到dist目录"""
    dist_dir = Path('dist')
    if not dist_dir.exists():
        return
    
    # 复制示例文件
    sample_files = ['README.md']
    for file_name in sample_files:
        src_file = Path(file_name)
        if src_file.exists():
            dst_file = dist_dir / file_name
            shutil.copy2(src_file, dst_file)
            print(f"已复制 {file_name} 到输出目录")

def create_installer_script():
    """创建Inno Setup安装脚本"""
    installer_script = '''
[Setup]
AppName=集装箱装载管理系统
AppVersion=1.0.0
AppPublisher=集装箱装载管理系统开发团队
DefaultDirName={autopf}\\ContainerLoader
DefaultGroupName=集装箱装载管理系统
OutputDir=installer
OutputBaseFilename=ContainerLoader_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "chinesesimp"; MessagesFile: "compiler:Languages\\ChineseSimplified.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\\集装箱装载管理系统.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\\集装箱装载管理系统"; Filename: "{app}\\集装箱装载管理系统.exe"
Name: "{group}\\{cm:UninstallProgram,集装箱装载管理系统}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\\集装箱装载管理系统"; Filename: "{app}\\集装箱装载管理系统.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\\集装箱装载管理系统.exe"; Description: "{cm:LaunchProgram,集装箱装载管理系统}"; Flags: nowait postinstall skipifsilent
'''
    
    with open('container_loader_setup.iss', 'w', encoding='utf-8') as f:
        f.write(installer_script)
    
    print("已创建Inno Setup安装脚本: container_loader_setup.iss")

def main():
    """主函数"""
    print("集装箱装载管理系统打包工具")
    print("=" * 50)
    
    # 检查当前目录
    if not Path('main.py').exists():
        print("错误: 找不到main.py文件，请在项目根目录下运行此脚本")
        return
    
    # 1. 安装依赖包
    if not install_dependencies():
        print("依赖包安装失败，打包终止")
        return
    
    # 2. 创建spec文件
    create_spec_file()
    
    # 3. 构建可执行文件
    if not build_executable():
        print("构建失败")
        return
    
    # 4. 复制额外文件
    copy_additional_files()
    
    # 5. 创建安装脚本
    create_installer_script()
    
    print("\\n" + "=" * 50)
    print("打包完成！")
    print("可执行文件位置: dist/集装箱装载管理系统.exe")
    print("安装脚本位置: container_loader_setup.iss")
    print("\\n使用说明:")
    print("1. 可以直接运行 dist/集装箱装载管理系统.exe")
    print("2. 使用Inno Setup编译 container_loader_setup.iss 创建安装程序")
    print("3. 建议对exe文件进行数字签名以避免杀毒软件误报")

if __name__ == '__main__':
    main()