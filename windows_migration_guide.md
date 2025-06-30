# Windows 迁移和打包指南

## 步骤1：将项目迁移到Windows

### 方法1：直接复制文件
1. 将整个 `interactive_container` 文件夹复制到Windows系统
2. 建议放在 `C:\container_app\` 目录下

### 方法2：使用Git（推荐）
```bash
# 在WSL中初始化Git仓库并提交
cd /home/pc/projects/interactive_container
git init
git add .
git commit -m "Initial commit for Windows migration"

# 在Windows中克隆
git clone <repository_url> C:\container_app
```

## 步骤2：Windows环境准备

### 安装Python 3.8+
1. 从 https://www.python.org/ 下载Python 3.8或更高版本
2. 安装时确保勾选 "Add Python to PATH"
3. 验证安装：在命令提示符中运行 `python --version`

### 设置虚拟环境
```cmd
cd C:\container_app
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## 步骤3：测试Windows版本
```cmd
venv\Scripts\activate
python main.py
```

## 步骤4：打包成可执行文件
```cmd
venv\Scripts\activate
python build_windows.py
```

## 步骤5：分发
打包完成后，`dist` 文件夹中将包含可执行文件和所有依赖，可以直接分发给用户。

## 注意事项
- Windows版本已自动处理OpenGL兼容性问题
- 确保杀毒软件不会误报PyInstaller生成的exe文件
- 首次运行可能需要Windows Defender允许