#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QGroupBox, QProgressBar, QTextEdit, QScrollArea)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QPalette
from core.box import Box
from core.container import Container

class InfoPanel(QWidget):
    """信息面板"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # 标题
        title_label = QLabel("信息面板")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        scroll_layout.addWidget(title_label)
        
        # 集装箱信息组
        self.container_info_group = self.create_container_info_group()
        scroll_layout.addWidget(self.container_info_group)
        
        # 重量平衡组
        self.weight_balance_group = self.create_weight_balance_group()
        scroll_layout.addWidget(self.weight_balance_group)
        
        # 空间利用率组
        self.space_utilization_group = self.create_space_utilization_group()
        scroll_layout.addWidget(self.space_utilization_group)
        
        # 选中箱子信息组
        self.selected_box_group = self.create_selected_box_group()
        scroll_layout.addWidget(self.selected_box_group)
        
        # 建议和警告组
        self.suggestions_group = self.create_suggestions_group()
        scroll_layout.addWidget(self.suggestions_group)
        
        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)
    
    def create_container_info_group(self) -> QGroupBox:
        """创建集装箱信息组"""
        group = QGroupBox("集装箱信息")
        layout = QVBoxLayout(group)
        
        self.container_name_label = QLabel("名称: -")
        self.container_size_label = QLabel("尺寸: -")
        self.container_box_count_label = QLabel("箱子数量: -")
        self.container_total_weight_label = QLabel("总重量: -")
        
        layout.addWidget(self.container_name_label)
        layout.addWidget(self.container_size_label)
        layout.addWidget(self.container_box_count_label)
        layout.addWidget(self.container_total_weight_label)
        
        return group
    
    def create_weight_balance_group(self) -> QGroupBox:
        """创建重量平衡组"""
        group = QGroupBox("重量平衡")
        layout = QVBoxLayout(group)
        
        # 左右重量平衡
        lr_layout = QHBoxLayout()
        lr_layout.addWidget(QLabel("左右:"))
        self.lr_balance_label = QLabel("- / -")
        self.lr_diff_label = QLabel("差值: -")
        lr_layout.addWidget(self.lr_balance_label)
        lr_layout.addWidget(self.lr_diff_label)
        layout.addLayout(lr_layout)
        
        # 左右平衡指示器
        self.lr_balance_bar = QProgressBar()
        self.lr_balance_bar.setRange(0, 100)
        self.lr_balance_bar.setValue(50)
        layout.addWidget(self.lr_balance_bar)
        
        # 前后重量平衡
        fr_layout = QHBoxLayout()
        fr_layout.addWidget(QLabel("前后:"))
        self.fr_balance_label = QLabel("- / -")
        self.fr_diff_label = QLabel("差值: -")
        fr_layout.addWidget(self.fr_balance_label)
        fr_layout.addWidget(self.fr_diff_label)
        layout.addLayout(fr_layout)
        
        # 前后平衡指示器
        self.fr_balance_bar = QProgressBar()
        self.fr_balance_bar.setRange(0, 100)
        self.fr_balance_bar.setValue(50)
        layout.addWidget(self.fr_balance_bar)
        
        # 重心位置
        self.center_label = QLabel("重心: -")
        layout.addWidget(self.center_label)
        
        return group
    
    def create_space_utilization_group(self) -> QGroupBox:
        """创建空间利用率组"""
        group = QGroupBox("空间利用率")
        layout = QVBoxLayout(group)
        
        # 面积利用率
        area_layout = QHBoxLayout()
        area_layout.addWidget(QLabel("面积:"))
        self.area_utilization_label = QLabel("0%")
        area_layout.addWidget(self.area_utilization_label)
        layout.addLayout(area_layout)
        
        self.area_utilization_bar = QProgressBar()
        self.area_utilization_bar.setRange(0, 100)
        self.area_utilization_bar.setValue(0)
        layout.addWidget(self.area_utilization_bar)
        
        # 已用/总计面积
        self.area_stats_label = QLabel("已用: 0 m² / 总计: 0 m²")
        layout.addWidget(self.area_stats_label)
        
        return group
    
    def create_selected_box_group(self) -> QGroupBox:
        """创建选中箱子信息组"""
        group = QGroupBox("选中箱子")
        layout = QVBoxLayout(group)
        
        self.selected_box_id_label = QLabel("ID: -")
        self.selected_box_size_label = QLabel("尺寸: -")
        self.selected_box_weight_label = QLabel("重量: -")
        self.selected_box_position_label = QLabel("位置: -")
        self.selected_box_rotated_label = QLabel("旋转: -")
        
        layout.addWidget(self.selected_box_id_label)
        layout.addWidget(self.selected_box_size_label)
        layout.addWidget(self.selected_box_weight_label)
        layout.addWidget(self.selected_box_position_label)
        layout.addWidget(self.selected_box_rotated_label)
        
        return group
    
    def create_suggestions_group(self) -> QGroupBox:
        """创建建议和警告组"""
        group = QGroupBox("建议和警告")
        layout = QVBoxLayout(group)
        
        self.suggestions_text = QTextEdit()
        self.suggestions_text.setMaximumHeight(100)
        self.suggestions_text.setReadOnly(True)
        layout.addWidget(self.suggestions_text)
        
        return group
    
    def show_container_info(self, container: Container):
        """显示集装箱信息"""
        if not container:
            self.clear_container_info()
            return
        
        # 集装箱基本信息
        self.container_name_label.setText(f"名称: {container.name}")
        self.container_size_label.setText(f"尺寸: {container.length/1000:.1f}×{container.width/1000:.1f}m")
        self.container_box_count_label.setText(f"箱子数量: {len(container.boxes)}")
        self.container_total_weight_label.setText(f"总重量: {container.total_weight:.1f}kg")
        
        # 重量平衡信息
        balance_info = container.calculate_weight_balance()
        self.update_weight_balance_display(balance_info)
        
        # 空间利用率信息
        self.update_space_utilization_display(container)
        
        # 生成建议和警告
        self.update_suggestions(container, balance_info)
    
    def show_box_info(self, box: Box):
        """显示箱子信息"""
        if not box:
            self.clear_box_info()
            return
        
        self.selected_box_id_label.setText(f"ID: {box.id}")
        self.selected_box_size_label.setText(f"尺寸: {box.length}×{box.width}mm")
        self.selected_box_weight_label.setText(f"重量: {box.weight}kg")
        self.selected_box_position_label.setText(f"位置: ({box.x:.0f}, {box.y:.0f})")
        self.selected_box_rotated_label.setText(f"旋转: {'是' if box.rotated else '否'}")
    
    def update_weight_balance_display(self, balance_info: dict):
        """更新重量平衡显示"""
        # 左右平衡
        left_weight = balance_info['left_weight']
        right_weight = balance_info['right_weight']
        lr_diff = balance_info['lr_diff']
        
        self.lr_balance_label.setText(f"{left_weight:.1f} / {right_weight:.1f}kg")
        self.lr_diff_label.setText(f"差值: {lr_diff:.1f}kg")
        
        # 设置进度条和颜色
        total_weight = left_weight + right_weight
        if total_weight > 0:
            lr_percentage = int((left_weight / total_weight) * 100)
            self.lr_balance_bar.setValue(lr_percentage)
            
            # 根据差值设置颜色
            if lr_diff > 500:  # 超出限制
                self.lr_balance_bar.setStyleSheet("QProgressBar::chunk { background-color: red; }")
            elif lr_diff > 250:  # 接近限制
                self.lr_balance_bar.setStyleSheet("QProgressBar::chunk { background-color: orange; }")
            else:
                self.lr_balance_bar.setStyleSheet("QProgressBar::chunk { background-color: green; }")
        
        # 前后平衡
        front_weight = balance_info['front_weight']
        rear_weight = balance_info['rear_weight']
        fr_diff = balance_info['fr_diff']
        
        self.fr_balance_label.setText(f"{front_weight:.1f} / {rear_weight:.1f}kg")
        self.fr_diff_label.setText(f"差值: {fr_diff:.1f}kg")
        
        if total_weight > 0:
            fr_percentage = int((front_weight / total_weight) * 100)
            self.fr_balance_bar.setValue(fr_percentage)
            
            # 根据差值设置颜色
            if fr_diff > 2000:  # 超出限制
                self.fr_balance_bar.setStyleSheet("QProgressBar::chunk { background-color: red; }")
            elif fr_diff > 1000:  # 接近限制
                self.fr_balance_bar.setStyleSheet("QProgressBar::chunk { background-color: orange; }")
            else:
                self.fr_balance_bar.setStyleSheet("QProgressBar::chunk { background-color: green; }")
        
        # 重心位置
        center_x = balance_info['center_x']
        center_y = balance_info['center_y']
        self.center_label.setText(f"重心: ({center_x/1000:.2f}, {center_y/1000:.2f})m")
    
    def update_space_utilization_display(self, container: Container):
        """更新空间利用率显示"""
        utilization = container.area_utilization * 100
        self.area_utilization_label.setText(f"{utilization:.1f}%")
        self.area_utilization_bar.setValue(int(utilization))
        
        # 设置进度条颜色
        if utilization < 60:
            self.area_utilization_bar.setStyleSheet("QProgressBar::chunk { background-color: red; }")
        elif utilization < 80:
            self.area_utilization_bar.setStyleSheet("QProgressBar::chunk { background-color: orange; }")
        else:
            self.area_utilization_bar.setStyleSheet("QProgressBar::chunk { background-color: green; }")
        
        # 面积统计
        used_area = container.used_area / 1000000  # 转换为平方米
        total_area = container.area / 1000000
        self.area_stats_label.setText(f"已用: {used_area:.1f} m² / 总计: {total_area:.1f} m²")
    
    def update_suggestions(self, container: Container, balance_info: dict):
        """更新建议和警告"""
        suggestions = []
        
        # 重量平衡警告
        if balance_info['lr_diff'] > 500:
            suggestions.append("⚠️ 左右重量差值超过500kg限制")
        elif balance_info['lr_diff'] > 250:
            suggestions.append("⚡ 左右重量差值接近限制，建议调整")
        
        if balance_info['fr_diff'] > 2000:
            suggestions.append("⚠️ 前后重量差值超过2000kg限制")
        elif balance_info['fr_diff'] > 1000:
            suggestions.append("⚡ 前后重量差值接近限制，建议调整")
        
        # 空间利用率建议
        utilization = container.area_utilization * 100
        if utilization < 60:
            suggestions.append("📦 空间利用率较低，建议优化布局")
        elif utilization > 95:
            suggestions.append("✅ 空间利用率很高，布局良好")
        
        # 平衡状态
        if balance_info['is_balanced']:
            suggestions.append("✅ 重量分布平衡")
        else:
            suggestions.append("⚠️ 重量分布不平衡，需要调整")
        
        # 显示建议
        if suggestions:
            self.suggestions_text.setText("\\n".join(suggestions))
        else:
            self.suggestions_text.setText("暂无建议")
    
    def clear_container_info(self):
        """清空集装箱信息"""
        self.container_name_label.setText("名称: -")
        self.container_size_label.setText("尺寸: -")
        self.container_box_count_label.setText("箱子数量: -")
        self.container_total_weight_label.setText("总重量: -")
        
        self.lr_balance_label.setText("- / -")
        self.lr_diff_label.setText("差值: -")
        self.fr_balance_label.setText("- / -")
        self.fr_diff_label.setText("差值: -")
        self.center_label.setText("重心: -")
        
        self.area_utilization_label.setText("0%")
        self.area_stats_label.setText("已用: 0 m² / 总计: 0 m²")
        
        self.suggestions_text.clear()
    
    def clear_box_info(self):
        """清空箱子信息"""
        self.selected_box_id_label.setText("ID: -")
        self.selected_box_size_label.setText("尺寸: -")
        self.selected_box_weight_label.setText("重量: -")
        self.selected_box_position_label.setText("位置: -")
        self.selected_box_rotated_label.setText("旋转: -")