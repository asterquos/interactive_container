#!/bin/bash
# 后台启动脚本，避免超时问题

# 激活虚拟环境
source ~/.virtualenvs/interactive_container/bin/activate

# 设置必要的环境变量
export QT_XCB_GL_INTEGRATION=none
export LIBGL_ALWAYS_SOFTWARE=1
export QT_QUICK_BACKEND=software

# 后台运行程序并将输出重定向到日志文件
nohup python main.py > container_app.log 2>&1 &

# 获取进程ID
PID=$!
echo "集装箱装载管理系统已启动，进程ID: $PID"
echo "日志文件: container_app.log"
echo "停止程序请运行: kill $PID"