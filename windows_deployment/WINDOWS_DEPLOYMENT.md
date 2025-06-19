# 集装箱装载管理系统 - Windows部署包

生成时间: 2025-06-19 22:44:44

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
