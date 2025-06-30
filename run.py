#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import subprocess

def main():
    """安全运行脚本"""
    # 设置环境变量
    env = os.environ.copy()
    env['QT_XCB_GL_INTEGRATION'] = 'none'
    env['LIBGL_ALWAYS_SOFTWARE'] = '1'
    env['QT_QUICK_BACKEND'] = 'software'
    env['XDG_RUNTIME_DIR'] = '/tmp/runtime-' + os.environ.get('USER', 'user')
    
    # 确保运行时目录存在
    if not os.path.exists(env['XDG_RUNTIME_DIR']):
        os.makedirs(env['XDG_RUNTIME_DIR'], 0o700)
    
    # 运行主程序
    python_exe = sys.executable
    main_script = os.path.join(os.path.dirname(__file__), 'main.py')
    
    try:
        subprocess.run([python_exe, main_script], env=env)
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"运行出错: {e}")

if __name__ == "__main__":
    main()