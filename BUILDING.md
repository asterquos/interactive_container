# 构建指南

## 开发环境

- **WSL/Linux/macOS**: 用于开发和测试
- **Windows**: 用于构建Windows可执行文件

## 构建Windows可执行文件

### 方法1：在Windows上构建（推荐）

1. 将项目复制到Windows环境
2. 安装Python 3.8+
3. 运行构建脚本：
   ```cmd
   build_exe_windows.bat
   ```

### 方法2：使用双系统

1. 在WSL中开发
2. 通过Windows文件系统访问项目：
   ```
   cd /mnt/c/Users/你的用户名/projects/interactive_container
   ```
3. 切换到Windows运行构建

### 方法3：使用虚拟机

1. 安装Windows虚拟机（VirtualBox/VMware）
2. 在虚拟机中安装Python和依赖
3. 共享文件夹或复制项目到虚拟机
4. 在虚拟机中运行构建脚本

### 方法4：CI/CD自动构建

1. 将代码推送到GitHub
2. 使用GitHub Actions自动构建
3. 从Actions页面下载构建好的exe文件

## 开发测试

在WSL/Linux/macOS中可以正常开发和测试：

```bash
# 安装依赖
pip install -r requirements.txt

# 运行程序
python main.py

# 运行测试
python -m pytest tests/
```

## 注意事项

1. **路径分隔符**: 代码中使用`pathlib`或`os.path.join`确保跨平台兼容
2. **文件编码**: 所有文件使用UTF-8编码
3. **换行符**: 使用`.gitattributes`确保换行符一致性
4. **依赖版本**: requirements.txt中指定具体版本避免兼容性问题

## 故障排除

### WSL中GUI显示问题

如果在WSL中运行时GUI无法显示：

1. 安装X服务器（如VcXsrv或X410）
2. 设置环境变量：
   ```bash
   export DISPLAY=:0
   ```

### PyQt5导入错误

在WSL中可能需要安装额外依赖：
```bash
sudo apt-get install python3-pyqt5
sudo apt-get install pyqt5-dev-tools
sudo apt-get install qttools5-dev-tools
```