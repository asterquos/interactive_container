#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集装箱装载管理系统启动文件
支持Windows和Linux环境的启动脚本
"""

import sys
import os
import platform

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

def setup_environment():
    """设置环境变量"""
    system = platform.system().lower()
    
    if system == 'windows':
        # Windows环境设置
        os.environ['QT_QUICK_BACKEND'] = 'software'
        os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'
        os.environ['QT_SCALE_FACTOR'] = '1'
    else:
        # Linux/WSL环境设置 - 修复GLX警告
        os.environ['QT_QUICK_BACKEND'] = 'software'
        os.environ['QT_OPENGL'] = 'software'
        os.environ['QT_XCB_GL_INTEGRATION'] = 'none'
        # 禁用硬件OpenGL加速，使用软件渲染
        os.environ['LIBGL_ALWAYS_SOFTWARE'] = '1'

def main():
    """主函数"""
    # 设置环境
    setup_environment()
    
    # 启用高DPI支持（必须在QApplication创建之前设置）
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # 创建应用程序
    app = QApplication(sys.argv)
    app.setApplicationName("集装箱装载管理系统")
    app.setApplicationVersion("1.1.0")
    app.setApplicationDisplayName("集装箱装载管理系统")
    app.setOrganizationName("Container Management")
    
    # 设置应用程序样式
    try:
        if platform.system().lower() == 'windows':
            app.setStyle('windowsvista')
        else:
            # Linux环境使用默认样式
            app.setStyle('fusion')
    except Exception:
        pass  # 样式设置失败时忽略
    
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
            from PyQt5.QtWidgets import QMessageBox, QDesktopWidget
            
            # 创建应用（如果还没有）
            if not QApplication.instance():
                error_app = QApplication(sys.argv)
            
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("启动错误")
            msg.setText(f"程序启动失败：\n{str(e)}")
            msg.setDetailedText(traceback.format_exc())
            
            # 居中显示错误对话框
            msg.adjustSize()
            desktop = QDesktopWidget()
            screen_geometry = desktop.screenGeometry()
            msg_width = msg.width()
            msg_height = msg.height()
            center_x = (screen_geometry.width() - msg_width) // 2
            center_y = (screen_geometry.height() - msg_height) // 2
            msg.move(center_x, center_y)
            
            msg.exec_()

if __name__ == "__main__":
    main()