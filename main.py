#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows专用启动文件
针对Windows环境优化的启动脚本
"""

import sys
import os

# 添加当前目录到Python路径，确保打包后能找到模块
if getattr(sys, 'frozen', False):
    # 如果是PyInstaller打包的exe
    application_path = os.path.dirname(sys.executable)
else:
    # 如果是普通Python脚本
    application_path = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, application_path)

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from gui.main_window import MainWindow

def setup_windows_environment():
    """设置Windows环境变量"""
    # Windows下不需要设置Linux相关的OpenGL环境变量
    # 但保留软件渲染设置以提高兼容性
    os.environ['QT_QUICK_BACKEND'] = 'software'
    
    # Windows高DPI支持
    os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'
    os.environ['QT_SCALE_FACTOR'] = '1'

def main():
    """主函数"""
    # 设置Windows环境
    setup_windows_environment()
    
    # 启用高DPI支持（必须在QApplication创建之前设置）
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # 创建应用程序
    app = QApplication(sys.argv)
    app.setApplicationName("集装箱装载管理系统")
    app.setApplicationVersion("1.0.0")
    app.setApplicationDisplayName("集装箱装载管理系统")
    app.setOrganizationName("Container Management")
    
    # 设置应用程序样式（Windows原生样式）
    app.setStyle('windowsvista')
    
    try:
        # 创建主窗口
        window = MainWindow()
        window.show()
        
        # 确保窗口显示在前台
        window.raise_()
        window.activateWindow()
        
        # 运行应用
        sys.exit(app.exec_())
        
    except Exception as e:
        import traceback
        print(f"应用程序启动失败: {e}")
        print(traceback.format_exc())
        
        # 如果是打包版本，显示错误对话框
        if getattr(sys, 'frozen', False):
            from PyQt5.QtWidgets import QMessageBox
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("启动错误")
            msg.setText(f"程序启动失败：\n{str(e)}")
            msg.setDetailedText(traceback.format_exc())
            msg.exec_()

if __name__ == "__main__":
    main()