# 集装箱装载管理系统 Windows PowerShell 构建脚本

Write-Host "集装箱装载管理系统 - PowerShell构建脚本" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# 检查Python是否安装
try {
    $pythonVersion = python --version 2>$null
    Write-Host "发现Python: $pythonVersion" -ForegroundColor Yellow
} catch {
    Write-Host "错误: 未找到Python，请先安装Python 3.8+" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}

# 检查main.py是否存在
if (-not (Test-Path "main.py")) {
    Write-Host "错误: 找不到main.py文件" -ForegroundColor Red
    Write-Host "请确保在项目根目录下运行此脚本" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}

Write-Host ""
Write-Host "步骤1: 升级pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

Write-Host ""
Write-Host "步骤2: 安装依赖包..." -ForegroundColor Yellow
if (Test-Path "requirements.txt") {
    python -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "错误: 安装依赖包失败" -ForegroundColor Red
        Read-Host "按回车键退出"
        exit 1
    }
} else {
    Write-Host "警告: 找不到requirements.txt，手动安装依赖..." -ForegroundColor Yellow
    python -m pip install PyQt5 pandas numpy openpyxl xlrd matplotlib reportlab
}

Write-Host ""
Write-Host "步骤3: 安装PyInstaller..." -ForegroundColor Yellow
python -m pip install pyinstaller
if ($LASTEXITCODE -ne 0) {
    Write-Host "错误: 安装PyInstaller失败" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}

Write-Host ""
Write-Host "步骤4: 构建可执行文件..." -ForegroundColor Yellow

# 检查是否存在spec文件
if (Test-Path "container_loader.spec") {
    Write-Host "使用现有的spec文件构建..." -ForegroundColor Cyan
    pyinstaller --clean container_loader.spec
} else {
    Write-Host "使用命令行参数构建..." -ForegroundColor Cyan
    
    # 检查data目录是否存在
    $addDataParam = ""
    if (Test-Path "data") {
        $addDataParam = "--add-data=data;data"
    }
    
    # 构建命令
    $buildCmd = @(
        "pyinstaller",
        "--onefile",
        "--windowed", 
        "--name=ContainerLoader",
        $addDataParam,
        "--hidden-import=pandas",
        "--hidden-import=numpy", 
        "--hidden-import=openpyxl",
        "--hidden-import=xlrd",
        "--hidden-import=matplotlib",
        "--hidden-import=reportlab",
        "--hidden-import=PyQt5.QtCore",
        "--hidden-import=PyQt5.QtGui", 
        "--hidden-import=PyQt5.QtWidgets",
        "--hidden-import=PyQt5.sip",
        "--clean",
        "main.py"
    ) | Where-Object { $_ -ne "" }
    
    & $buildCmd[0] $buildCmd[1..$buildCmd.Length]
}

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "构建失败！" -ForegroundColor Red
    Write-Host "请检查上面的错误信息" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "构建成功！" -ForegroundColor Green

# 检查输出文件
if (Test-Path "dist\ContainerLoader.exe") {
    $fileSize = (Get-Item "dist\ContainerLoader.exe").Length / 1MB
    Write-Host "可执行文件: dist\ContainerLoader.exe" -ForegroundColor Yellow
    Write-Host "文件大小: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Yellow
} else {
    Write-Host "警告: 未找到生成的exe文件" -ForegroundColor Red
}

Write-Host ""
Write-Host "使用说明:" -ForegroundColor Cyan
Write-Host "1. 可以直接运行 dist\ContainerLoader.exe" -ForegroundColor White
Write-Host "2. 如需分发，请将整个dist目录复制到目标机器" -ForegroundColor White
Write-Host "3. 建议对exe文件进行数字签名以避免杀毒软件误报" -ForegroundColor White

Read-Host "按回车键退出"