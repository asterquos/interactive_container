#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                             QListWidgetItem, QLabel, QPushButton, QLineEdit,
                             QComboBox, QGroupBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QBrush
from typing import List
from core.box import Box

class BoxListItem(QListWidgetItem):
    """自定义箱子列表项"""
    
    def __init__(self, box: Box):
        super().__init__()
        self.box = box
        self.update_display()
    
    def update_display(self):
        """更新显示文本"""
        # 显示：箱号、重量和尺寸
        text = f"{self.box.id}: {self.box.weight}kg ({self.box.length}×{self.box.width})"
        self.setText(text)
        
        # 根据重量设置颜色（与箱子颜色统一）
        weight = self.box.weight
        
        if weight >= 800:  # 重箱 - 红色系
            ratio = min((weight - 800) / 1200, 1.0)
            r = 255
            g = int(200 - ratio * 150)  # 200 -> 50
            b = int(200 - ratio * 150)  # 200 -> 50
            color = QColor(r, g, b)
        elif weight >= 400:  # 中等 - 黄色系
            ratio = (weight - 400) / 400
            r = 255
            g = int(255 - ratio * 55)  # 255 -> 200
            b = int(150 - ratio * 100)  # 150 -> 50
            color = QColor(r, g, b)
        else:  # 轻箱 - 绿色系
            ratio = weight / 400
            r = int(200 - ratio * 100)  # 200 -> 100
            g = 255
            b = int(200 - ratio * 100)  # 200 -> 100
            color = QColor(r, g, b)
        
        self.setBackground(QBrush(color))

class BoxListPanel(QWidget):
    """箱子列表面板"""
    
    # 信号定义
    box_selected = pyqtSignal(Box)
    box_double_clicked = pyqtSignal(Box)
    
    def __init__(self):
        super().__init__()
        self.boxes: List[Box] = []
        self.init_ui()
    
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel("待装载箱子")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        layout.addWidget(title_label)
        
        # 搜索和过滤区域
        filter_group = QGroupBox("搜索和过滤")
        filter_layout = QVBoxLayout(filter_group)
        
        # 搜索框
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("搜索:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("输入箱号或尺寸...")
        self.search_edit.textChanged.connect(self.filter_boxes)
        search_layout.addWidget(self.search_edit)
        filter_layout.addLayout(search_layout)
        
        # 重量过滤
        weight_layout = QHBoxLayout()
        weight_layout.addWidget(QLabel("重量:"))
        self.weight_filter = QComboBox()
        self.weight_filter.addItems(["全部", "轻箱(<500kg)", "中等(500-1000kg)", "重箱(>1000kg)"])
        self.weight_filter.currentTextChanged.connect(self.filter_boxes)
        weight_layout.addWidget(self.weight_filter)
        filter_layout.addLayout(weight_layout)
        
        layout.addWidget(filter_group)
        
        # 箱子列表
        self.box_list = QListWidget()
        self.box_list.itemClicked.connect(self.on_item_clicked)
        self.box_list.itemDoubleClicked.connect(self.on_item_double_clicked)
        layout.addWidget(self.box_list)
        
        # 统计信息
        self.stats_label = QLabel("总数: 0 | 总重: 0kg")
        self.stats_label.setStyleSheet("padding: 5px; background-color: #f0f0f0;")
        layout.addWidget(self.stats_label)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        
        self.auto_place_btn = QPushButton("自动放置")
        self.auto_place_btn.clicked.connect(self.auto_place_selected)
        button_layout.addWidget(self.auto_place_btn)
        
        self.clear_selection_btn = QPushButton("清除选择")
        self.clear_selection_btn.clicked.connect(self.clear_selection)
        button_layout.addWidget(self.clear_selection_btn)
        
        layout.addLayout(button_layout)
    
    def set_boxes(self, boxes: List[Box]):
        """设置箱子列表"""
        self.boxes = boxes.copy()
        self.update_display()
    
    def add_box(self, box: Box):
        """添加箱子"""
        self.boxes.append(box)
        self.update_display()
    
    def remove_box(self, box: Box):
        """移除箱子"""
        if box in self.boxes:
            self.boxes.remove(box)
            self.update_display()
    
    def update_display(self):
        """更新显示"""
        self.box_list.clear()
        
        filtered_boxes = self.get_filtered_boxes()
        
        # 按重量排序（从重到轻）
        filtered_boxes.sort(key=lambda b: b.weight, reverse=True)
        
        for box in filtered_boxes:
            item = BoxListItem(box)
            self.box_list.addItem(item)
        
        self.update_stats(filtered_boxes)
    
    def get_filtered_boxes(self) -> List[Box]:
        """获取过滤后的箱子列表"""
        filtered = self.boxes.copy()
        
        # 文本搜索过滤
        search_text = self.search_edit.text().lower()
        if search_text:
            filtered = [box for box in filtered 
                       if (search_text in box.id.lower() or 
                           search_text in f"{box.length}x{box.width}".lower())]
        
        # 重量过滤
        weight_filter = self.weight_filter.currentText()
        if weight_filter == "轻箱(<500kg)":
            filtered = [box for box in filtered if box.weight < 500]
        elif weight_filter == "中等(500-1000kg)":
            filtered = [box for box in filtered if 500 <= box.weight <= 1000]
        elif weight_filter == "重箱(>1000kg)":
            filtered = [box for box in filtered if box.weight > 1000]
        
        return filtered
    
    def filter_boxes(self):
        """过滤箱子"""
        self.update_display()
    
    def update_stats(self, boxes: List[Box]):
        """更新统计信息"""
        total_count = len(boxes)
        total_weight = sum(box.weight for box in boxes)
        
        self.stats_label.setText(f"总数: {total_count} | 总重: {total_weight:.1f}kg")
    
    def on_item_clicked(self, item: QListWidgetItem):
        """列表项被点击"""
        if isinstance(item, BoxListItem):
            self.box_selected.emit(item.box)
    
    def on_item_double_clicked(self, item: QListWidgetItem):
        """列表项被双击"""
        if isinstance(item, BoxListItem):
            self.box_double_clicked.emit(item.box)
    
    def auto_place_selected(self):
        """自动放置选中的箱子"""
        current_item = self.box_list.currentItem()
        if isinstance(current_item, BoxListItem):
            self.box_double_clicked.emit(current_item.box)
    
    def clear_selection(self):
        """清除选择"""
        self.box_list.clearSelection()
    
    def get_selected_box(self) -> Box:
        """获取选中的箱子"""
        current_item = self.box_list.currentItem()
        if isinstance(current_item, BoxListItem):
            return current_item.box
        return None