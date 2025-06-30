#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# 添加当前目录到Python路径，确保打包后能找到模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from gui.main_window import MainWindow

def main():
    """主函数"""
    # 禁用OpenGL以避免兼容性问题
    os.environ['QT_XCB_GL_INTEGRATION'] = 'none'
    os.environ['LIBGL_ALWAYS_SOFTWARE'] = '1'
    os.environ['QT_QUICK_BACKEND'] = 'software'
    
    # 启用高DPI支持（必须在QApplication创建之前设置）
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    
    # 使用软件渲染而不是硬件加速
    QApplication.setAttribute(Qt.AA_UseSoftwareOpenGL, True)
    
    app = QApplication(sys.argv)
    app.setApplicationName("集装箱装载管理系统")
    app.setApplicationVersion("1.0.0")
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()