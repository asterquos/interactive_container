#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from gui.main_window import MainWindow

def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setApplicationName("集装箱装载管理系统")
    app.setApplicationVersion("1.0.0")
    
    # 启用高DPI支持
    app.setAttribute(Qt.AA_EnableHighDpiScaling)
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()