#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
为Windows打包准备文件
"""

import os
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

def create_deployment_package():
    """创建部署包"""
    print("📦 准备Windows部署包...")
    
    # 创建部署目录
    deploy_dir = Path("windows_deployment")
    if deploy_dir.exists():
        shutil.rmtree(deploy_dir)
    deploy_dir.mkdir()
    
    # 需要包含的文件和目录
    include_items = [
        # 核心代码
        "main.py",
        "requirements.txt",
        "core/",
        "gui/", 
        "utils/",
        "data/",
        
        # 构建脚本
        "build_fixed.bat",
        "build_simple.bat", 
        "build.ps1",
        "container_loader_stable.spec",
        
        # 文档和配置
        "README.md",
        "BUILDING.md",
        
        # 测试数据（可选）
        "test_data/",
        
        # 项目配置
        "setup.py",
    ]
    
    # 复制文件
    for item in include_items:
        src = Path(item)
        if not src.exists():
            print(f"⚠️  跳过不存在的文件: {item}")
            continue
            
        dst = deploy_dir / item
        
        if src.is_dir():
            shutil.copytree(src, dst)
            print(f"✅ 复制目录: {item}")
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            print(f"✅ 复制文件: {item}")
    
    # 创建Windows部署说明
    readme_content = f"""# 集装箱装载管理系统 - Windows部署包

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 文件说明

### 核心代码
- `main.py` - 程序主入口
- `core/` - 核心业务逻辑（箱子、集装箱类）
- `gui/` - 图形用户界面
- `utils/` - 工具模块（Excel读取、PDF生成、项目管理）
- `data/` - 示例数据

### 构建脚本
- `build_fixed.bat` - 完整的Windows构建脚本（推荐）
- `build_simple.bat` - 简化的构建脚本
- `build.ps1` - PowerShell构建脚本
- `container_loader_stable.spec` - PyInstaller配置文件

### 测试数据
- `test_data/` - 各种测试用Excel文件

## 构建步骤

### 方法1：使用批处理脚本（推荐）
1. 确保安装了Python 3.8+
2. 双击运行 `build_fixed.bat`
3. 等待构建完成
4. 在 `dist/` 目录找到可执行文件

### 方法2：使用PowerShell
1. 右键点击 `build.ps1` → "使用PowerShell运行"
2. 或在PowerShell中运行: `PowerShell -ExecutionPolicy Bypass -File build.ps1`

### 方法3：手动构建
```cmd
pip install -r requirements.txt
pip install pyinstaller
pyinstaller --clean container_loader_stable.spec
```

## 测试建议

在构建之前，可以先运行程序测试：
```cmd
python main.py
```

建议使用测试数据中的Excel文件进行功能测试。

## 常见问题

1. **构建失败**: 确保所有依赖都已安装，尝试在虚拟环境中构建
2. **exe无法运行**: 检查是否被杀毒软件拦截
3. **缺少文件**: 确保所有源代码文件都存在

## 技术支持

如有问题，请检查构建日志中的错误信息。
"""
    
    with open(deploy_dir / "WINDOWS_DEPLOYMENT.md", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"✅ 创建部署说明: WINDOWS_DEPLOYMENT.md")
    
    # 创建ZIP压缩包
    zip_name = f"container_loader_windows_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(deploy_dir):
            for file in files:
                file_path = Path(root) / file
                arc_name = file_path.relative_to(deploy_dir)
                zipf.write(file_path, arc_name)
    
    print(f"✅ 创建压缩包: {zip_name}")
    
    # 输出统计信息
    total_files = sum(1 for _ in deploy_dir.rglob("*") if _.is_file())
    zip_size = os.path.getsize(zip_name) / (1024 * 1024)
    
    print(f"\n📊 部署包统计:")
    print(f"   - 文件数量: {total_files}")
    print(f"   - 压缩包大小: {zip_size:.2f} MB")
    print(f"   - 部署目录: {deploy_dir.absolute()}")
    print(f"   - 压缩包: {Path(zip_name).absolute()}")
    
    print(f"\n🎉 Windows部署包准备完成！")
    print(f"💡 将 {zip_name} 复制到Windows环境中解压并运行构建脚本")

if __name__ == "__main__":
    create_deployment_package()