#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QSplitter, QMenuBar, QStatusBar, QAction, QFileDialog,
                             QMessageBox, QTabWidget, QDockWidget, QTextEdit, QLabel)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QKeySequence
import os
from datetime import datetime

from .container_view import ContainerView
from .box_list_panel import BoxListPanel
from .info_panel import InfoPanel
from utils.excel_reader import ExcelReader
from utils.project_manager import ProjectManager
from core.container import Container
from core.box import Box
from data.sample_boxes import get_sample_boxes

class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.containers = []  # 集装箱列表
        self.current_container_index = 0
        self.pending_boxes = []  # 待装载箱子列表
        self.excel_reader = ExcelReader()
        self.project_manager = ProjectManager()
        self.current_project_path = None
        
        self.init_ui()
        self.create_menus()
        self.create_status_bar()
        self.setup_connections()
        
        # 创建默认集装箱
        self.add_new_container()
    
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("集装箱装载管理系统 v1.0")
        self.setGeometry(100, 100, 1400, 800)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QHBoxLayout(central_widget)
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # 左侧面板 - 箱子列表
        self.box_list_panel = BoxListPanel()
        splitter.addWidget(self.box_list_panel)
        
        # 中央区域 - 集装箱视图和标签页
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        
        # 集装箱标签页
        self.container_tabs = QTabWidget()
        self.container_tabs.setTabsClosable(True)
        self.container_tabs.tabCloseRequested.connect(self.close_container_tab)
        self.container_tabs.currentChanged.connect(self.on_container_tab_changed)
        center_layout.addWidget(self.container_tabs)
        
        # 集装箱视图
        self.container_view = ContainerView()
        center_layout.addWidget(self.container_view)
        
        splitter.addWidget(center_widget)
        
        # 右侧面板 - 信息面板
        self.info_panel = InfoPanel()
        splitter.addWidget(self.info_panel)
        
        # 设置分割器比例
        splitter.setSizes([300, 800, 300])
        
        # 创建底部停靠窗口用于日志
        self.create_log_dock()
    
    def create_menus(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu('文件(&F)')
        
        # 导入Excel
        import_action = QAction('导入Excel文件(&I)', self)
        import_action.setShortcut(QKeySequence.Open)
        import_action.triggered.connect(self.import_excel)
        file_menu.addAction(import_action)
        
        file_menu.addSeparator()
        
        # 保存项目
        save_action = QAction('保存项目(&S)', self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.save_project)
        file_menu.addAction(save_action)
        
        # 另存为
        save_as_action = QAction('另存为(&A)', self)
        save_as_action.setShortcut(QKeySequence.SaveAs)
        save_as_action.triggered.connect(self.save_project_as)
        file_menu.addAction(save_as_action)
        
        # 加载项目
        load_action = QAction('加载项目(&L)', self)
        load_action.setShortcut(QKeySequence.Open)
        load_action.triggered.connect(self.load_project)
        file_menu.addAction(load_action)
        
        file_menu.addSeparator()
        
        # 导出PDF
        export_action = QAction('导出PDF报告(&E)', self)
        export_action.triggered.connect(self.export_pdf)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        # 退出
        exit_action = QAction('退出(&Q)', self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 编辑菜单
        edit_menu = menubar.addMenu('编辑(&E)')
        
        # 撤销
        undo_action = QAction('撤销(&U)', self)
        undo_action.setShortcut(QKeySequence.Undo)
        undo_action.triggered.connect(self.undo)
        edit_menu.addAction(undo_action)
        
        # 重做
        redo_action = QAction('重做(&R)', self)
        redo_action.setShortcut(QKeySequence.Redo)
        redo_action.triggered.connect(self.redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        # 清空当前集装箱
        clear_action = QAction('清空当前集装箱(&C)', self)
        clear_action.triggered.connect(self.clear_current_container)
        edit_menu.addAction(clear_action)
        
        # 集装箱菜单
        container_menu = menubar.addMenu('集装箱(&C)')
        
        # 新建集装箱
        new_container_action = QAction('新建集装箱(&N)', self)
        new_container_action.setShortcut('Ctrl+N')
        new_container_action.triggered.connect(self.add_new_container)
        container_menu.addAction(new_container_action)
        
        # 测试菜单
        test_menu = menubar.addMenu('测试(&T)')
        
        # 加载示例数据
        load_sample_action = QAction('加载示例数据(&S)', self)
        load_sample_action.triggered.connect(self.load_sample_data)
        test_menu.addAction(load_sample_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu('帮助(&H)')
        
        # 关于
        about_action = QAction('关于(&A)', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("就绪")
        
        # 添加状态信息标签
        self.container_status_label = QLabel("集装箱: 0/0")
        self.box_status_label = QLabel("箱子: 0")
        self.utilization_label = QLabel("利用率: 0%")
        
        self.status_bar.addPermanentWidget(self.container_status_label)
        self.status_bar.addPermanentWidget(self.box_status_label)
        self.status_bar.addPermanentWidget(self.utilization_label)
    
    def create_log_dock(self):
        """创建日志停靠窗口"""
        self.log_dock = QDockWidget("日志", self)
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        self.log_text.setReadOnly(True)
        self.log_dock.setWidget(self.log_text)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.log_dock)
    
    def setup_connections(self):
        """设置信号连接"""
        # 箱子列表面板信号
        self.box_list_panel.box_selected.connect(self.on_box_selected)
        self.box_list_panel.box_double_clicked.connect(self.on_box_double_clicked)
        
        # 集装箱视图信号
        self.container_view.box_moved.connect(self.on_box_moved)
        self.container_view.box_placed.connect(self.on_box_placed)
        self.container_view.selection_changed.connect(self.on_selection_changed)
    
    def import_excel(self):
        """导入Excel文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "导入Excel文件", "", 
            "Excel Files (*.xlsx *.xls);;All Files (*)"
        )
        
        if file_path:
            self.log_message(f"正在导入Excel文件: {file_path}")
            
            try:
                boxes, errors = self.excel_reader.read_excel(file_path)
                
                if errors:
                    error_msg = "\\n".join(errors)
                    QMessageBox.warning(self, "导入警告", f"导入过程中发现问题:\\n{error_msg}")
                
                if boxes:
                    self.pending_boxes = boxes
                    self.box_list_panel.set_boxes(boxes)
                    self.log_message(f"成功导入 {len(boxes)} 个箱子")
                    self.update_status()
                else:
                    QMessageBox.warning(self, "导入失败", "没有找到有效的箱子数据")
                    
            except Exception as e:
                QMessageBox.critical(self, "导入错误", f"导入Excel文件时出错:\\n{str(e)}")
                self.log_message(f"导入错误: {str(e)}")
    
    def save_project(self):
        """保存项目"""
        if self.current_project_path:
            # 直接保存到当前路径
            self.save_project_to_path(self.current_project_path)
        else:
            # 另存为
            self.save_project_as()
    
    def save_project_as(self):
        """另存为项目"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存项目", 
            f"集装箱项目_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "项目文件 (*.json);;所有文件 (*)"
        )
        
        if file_path:
            self.save_project_to_path(file_path)
    
    def save_project_to_path(self, file_path: str):
        """保存项目到指定路径"""
        try:
            project_name = os.path.splitext(os.path.basename(file_path))[0]
            success = self.project_manager.save_project(
                self.containers, self.pending_boxes, file_path, project_name
            )
            
            if success:
                self.current_project_path = file_path
                self.setWindowTitle(f"集装箱装载管理系统 - {project_name}")
                QMessageBox.information(self, "保存成功", f"项目已保存到:\\n{file_path}")
                self.log_message(f"项目保存成功: {file_path}")
            else:
                QMessageBox.critical(self, "保存失败", "保存项目时出现错误")
                
        except Exception as e:
            QMessageBox.critical(self, "保存错误", f"保存项目时出错:\\n{str(e)}")
            self.log_message(f"项目保存错误: {str(e)}")
    
    def load_project(self):
        """加载项目"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "加载项目", "",
            "项目文件 (*.json);;所有文件 (*)"
        )
        
        if file_path:
            self.load_project_from_path(file_path)
    
    def load_project_from_path(self, file_path: str):
        """从指定路径加载项目"""
        try:
            success, containers, pending_boxes, project_info = self.project_manager.load_project(file_path)
            
            if success:
                # 清空当前数据
                self.containers.clear()
                self.container_tabs.clear()
                
                # 加载新数据
                self.containers = containers
                self.pending_boxes = pending_boxes
                self.current_project_path = file_path
                
                # 更新界面
                for container in self.containers:
                    tab_index = self.container_tabs.addTab(QWidget(), container.name)
                
                if self.containers:
                    self.current_container_index = 0
                    self.container_tabs.setCurrentIndex(0)
                    self.container_view.set_container(self.containers[0])
                
                self.box_list_panel.set_boxes(self.pending_boxes)
                
                # 更新窗口标题
                project_name = project_info.get("name", os.path.splitext(os.path.basename(file_path))[0])
                self.setWindowTitle(f"集装箱装载管理系统 - {project_name}")
                
                self.update_status()
                QMessageBox.information(self, "加载成功", f"项目已加载:\\n{file_path}")
                self.log_message(f"项目加载成功: {file_path}")
                
            else:
                QMessageBox.critical(self, "加载失败", "项目文件格式错误或文件损坏")
                
        except Exception as e:
            QMessageBox.critical(self, "加载错误", f"加载项目时出错:\\n{str(e)}")
            self.log_message(f"项目加载错误: {str(e)}")
    
    def export_pdf(self):
        """导出PDF报告"""
        if not self.containers or not any(container.boxes for container in self.containers):
            QMessageBox.warning(self, "导出失败", "没有装载数据可以导出")
            return
        
        # 选择保存位置
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出PDF报告", 
            f"集装箱装载报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            "PDF Files (*.pdf);;All Files (*)"
        )
        
        if file_path:
            try:
                from utils.pdf_generator import PDFGenerator
                from datetime import datetime
                
                generator = PDFGenerator()
                success = generator.generate_report(self.containers, file_path, True)
                
                if success:
                    QMessageBox.information(self, "导出成功", f"PDF报告已保存到:\\n{file_path}")
                    self.log_message(f"PDF报告导出成功: {file_path}")
                else:
                    QMessageBox.critical(self, "导出失败", "生成PDF报告时出现错误")
                    
            except Exception as e:
                QMessageBox.critical(self, "导出错误", f"导出PDF时出错:\\n{str(e)}")
                self.log_message(f"PDF导出错误: {str(e)}")
    
    def undo(self):
        """撤销操作"""
        # TODO: 实现撤销功能
        self.log_message("撤销操作")
    
    def redo(self):
        """重做操作"""
        # TODO: 实现重做功能
        self.log_message("重做操作")
    
    def clear_current_container(self):
        """清空当前集装箱"""
        if self.current_container:
            self.current_container.clear()
            self.container_view.update_view()
            self.update_status()
            self.log_message("已清空当前集装箱")
    
    def add_new_container(self):
        """添加新集装箱"""
        container = Container(name=f"集装箱 {len(self.containers) + 1}")
        self.containers.append(container)
        
        # 添加标签页
        tab_index = self.container_tabs.addTab(QWidget(), container.name)
        self.container_tabs.setCurrentIndex(tab_index)
        
        self.current_container_index = len(self.containers) - 1
        self.container_view.set_container(container)
        self.update_status()
        self.log_message(f"添加新集装箱: {container.name}")
    
    def close_container_tab(self, index):
        """关闭集装箱标签页"""
        if len(self.containers) > 1:
            # 确认关闭
            container = self.containers[index]
            if container.boxes:
                reply = QMessageBox.question(self, "确认关闭", 
                    f"集装箱 '{container.name}' 中还有 {len(container.boxes)} 个箱子。\\n确定要关闭吗？",
                    QMessageBox.Yes | QMessageBox.No)
                if reply != QMessageBox.Yes:
                    return
            
            # 移除标签页和集装箱
            self.container_tabs.removeTab(index)
            
            # 将箱子返回到待装载列表
            for box in container.boxes:
                self.pending_boxes.append(box)
            
            del self.containers[index]
            
            # 调整当前索引
            if self.current_container_index >= index:
                self.current_container_index = max(0, self.current_container_index - 1)
            
            # 更新显示
            self.box_list_panel.set_boxes(self.pending_boxes)
            if self.current_container:
                self.container_view.set_container(self.current_container)
            
            self.update_status()
            self.log_message(f"已关闭集装箱: {container.name}")
    
    def on_container_tab_changed(self, index):
        """集装箱标签页切换"""
        if 0 <= index < len(self.containers):
            self.current_container_index = index
            self.container_view.set_container(self.containers[index])
            self.update_status()
    
    def on_box_selected(self, box):
        """箱子被选中"""
        self.info_panel.show_box_info(box)
        self.container_view.highlight_box(box)
    
    def on_box_double_clicked(self, box):
        """箱子被双击"""
        if self.current_container:
            # 尝试自动放置箱子
            position = self.current_container.find_placement_position(box)
            if position:
                box.move_to(*position)
                if self.current_container.add_box(box):
                    self.pending_boxes.remove(box)
                    self.box_list_panel.remove_box(box)
                    self.container_view.add_box(box)
                    self.update_status()
                    self.log_message(f"自动放置箱子: {box.id}")
                else:
                    self.log_message(f"无法放置箱子: {box.id}")
            else:
                self.log_message(f"找不到合适位置放置箱子: {box.id}")
    
    def on_box_moved(self, box, new_x, new_y):
        """箱子被移动"""
        box.move_to(new_x, new_y)
        self.update_status()
    
    def on_box_placed(self, box):
        """箱子被放置"""
        self.update_status()
        self.log_message(f"箱子 {box.id} 已放置")
    
    def on_selection_changed(self, selected_box):
        """选择发生变化"""
        if selected_box:
            self.info_panel.show_box_info(selected_box)
        else:
            self.info_panel.show_container_info(self.current_container)
    
    def load_sample_data(self):
        """加载示例数据"""
        try:
            sample_boxes = get_sample_boxes()
            self.pending_boxes = sample_boxes
            self.box_list_panel.set_boxes(sample_boxes)
            self.log_message(f"已加载 {len(sample_boxes)} 个示例箱子")
            self.update_status()
            QMessageBox.information(self, "加载示例数据", f"成功加载 {len(sample_boxes)} 个示例箱子")
        except Exception as e:
            QMessageBox.critical(self, "加载失败", f"加载示例数据时出错:\\n{str(e)}")
            self.log_message(f"加载示例数据错误: {str(e)}")
    
    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(self, "关于", 
            "集装箱装载管理系统 v1.0\\n\\n"
            "用于优化集装箱装载过程的专业工具\\n"
            "支持Excel导入、可视化布局、重量平衡分析等功能")
    
    def log_message(self, message):
        """记录日志消息"""
        self.log_text.append(message)
        self.log_text.ensureCursorVisible()
    
    def update_status(self):
        """更新状态栏"""
        container_count = len(self.containers)
        current_index = self.current_container_index + 1 if self.containers else 0
        
        self.container_status_label.setText(f"集装箱: {current_index}/{container_count}")
        
        if self.current_container:
            box_count = len(self.current_container.boxes)
            utilization = self.current_container.area_utilization * 100
            
            self.box_status_label.setText(f"箱子: {box_count}")
            self.utilization_label.setText(f"利用率: {utilization:.1f}%")
            
            # 更新信息面板
            self.info_panel.show_container_info(self.current_container)
        else:
            self.box_status_label.setText("箱子: 0")
            self.utilization_label.setText("利用率: 0%")
    
    @property
    def current_container(self):
        """获取当前集装箱"""
        if 0 <= self.current_container_index < len(self.containers):
            return self.containers[self.current_container_index]
        return None