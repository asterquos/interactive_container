#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
集装箱装载管理系统启动脚本
用于开发和测试环境
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from main import main
    main()
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保安装了所有依赖包:")
    print("pip install -r requirements.txt")
    input("按回车键退出...")
except Exception as e:
    print(f"运行错误: {e}")
    input("按回车键退出...")