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
        """初始化用户界面（紧凑水平布局，无滚动条）"""
        layout = QVBoxLayout(self)
        layout.setSpacing(2)
        layout.setContentsMargins(8, 5, 8, 5)
        
        # 直接显示选中箱子信息（去掉标题）
        selection_widget = self.create_enlarged_selection_info()
        layout.addWidget(selection_widget)
        layout.addStretch()
    
    def add_separator(self, layout):
        """添加分隔线"""
        from PyQt5.QtWidgets import QFrame
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("color: #bdc3c7;")
        layout.addWidget(line)
    
    def create_compact_container_info(self):
        """创建紧凑的集装箱信息"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(2)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 小标题
        title = QLabel("集装箱状态")
        title.setStyleSheet("font-weight: bold; font-size: 10px; color: #34495e;")
        layout.addWidget(title)
        
        # 信息标签
        self.container_name_label = QLabel("名称: -")
        self.container_size_label = QLabel("尺寸: -")
        self.container_box_count_label = QLabel("箱子: -")
        self.container_total_weight_label = QLabel("重量: -")
        
        # 统一样式
        label_style = "font-size: 9px; color: #2c3e50; margin: 1px 0px;"
        for label in [self.container_name_label, self.container_size_label, 
                     self.container_box_count_label, self.container_total_weight_label]:
            label.setStyleSheet(label_style)
            layout.addWidget(label)
        
        return widget
    
    def create_compact_utilization_info(self):
        """创建紧凑的利用率信息"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(2)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 小标题
        title = QLabel("空间利用率")
        title.setStyleSheet("font-weight: bold; font-size: 10px; color: #34495e;")
        layout.addWidget(title)
        
        # 面积利用率
        self.area_utilization_label = QLabel("面积: -")
        self.area_utilization_label.setStyleSheet("font-size: 9px; color: #2c3e50; margin: 1px 0px;")
        layout.addWidget(self.area_utilization_label)
        
        # 简化的进度条
        self.area_progress = QProgressBar()
        self.area_progress.setMaximumHeight(8)
        self.area_progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                background-color: #ecf0f1;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 2px;
            }
        """)
        layout.addWidget(self.area_progress)
        
        # 已用面积信息
        self.area_stats_label = QLabel("已用: -")
        self.area_stats_label.setStyleSheet("font-size: 9px; color: #2c3e50; margin: 1px 0px;")
        layout.addWidget(self.area_stats_label)
        
        return widget
    
    def create_compact_selection_info(self):
        """创建紧凑的选择信息"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(2)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 小标题
        title = QLabel("当前选中")
        title.setStyleSheet("font-weight: bold; font-size: 10px; color: #34495e;")
        layout.addWidget(title)
        
        # 选中箱子信息
        self.selected_box_id_label = QLabel("箱号: -")
        self.selected_box_size_label = QLabel("尺寸: -")
        self.selected_box_weight_label = QLabel("重量: -")
        self.selected_box_pos_label = QLabel("位置: -")
        
        # 统一样式
        label_style = "font-size: 9px; color: #2c3e50; margin: 1px 0px;"
        for label in [self.selected_box_id_label, self.selected_box_size_label,
                     self.selected_box_weight_label, self.selected_box_pos_label]:
            label.setStyleSheet(label_style)
            layout.addWidget(label)
        
        return widget
    
    def create_enlarged_selection_info(self):
        """创建简洁的选中箱子信息"""
        widget = QWidget()
        widget.setStyleSheet("background-color: #f5f5f5; border: 1px solid #ddd;")
        
        layout = QVBoxLayout(widget)
        layout.setSpacing(5)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 标题
        title = QLabel("当前选中箱子")
        title.setStyleSheet("font-weight: bold; font-size: 13px; color: #2c3e50; padding: 5px;")
        layout.addWidget(title)
        
        # 箱号
        self.selected_box_id_label = QLabel("箱号: 未选择")
        self.selected_box_id_label.setStyleSheet("font-size: 12px; padding: 5px;")
        layout.addWidget(self.selected_box_id_label)
        
        # 尺寸
        self.selected_box_size_label = QLabel("尺寸: -")
        self.selected_box_size_label.setStyleSheet("font-size: 12px; padding: 5px;")
        layout.addWidget(self.selected_box_size_label)
        
        # 重量
        self.selected_box_weight_label = QLabel("重量: -")
        self.selected_box_weight_label.setStyleSheet("font-size: 12px; padding: 5px;")
        layout.addWidget(self.selected_box_weight_label)
        
        # 位置
        self.selected_box_pos_label = QLabel("位置: -")
        self.selected_box_pos_label.setStyleSheet("font-size: 12px; padding: 5px;")
        layout.addWidget(self.selected_box_pos_label)
        
        # 状态
        self.selected_box_rotated_label = QLabel("状态: -")
        self.selected_box_rotated_label.setStyleSheet("font-size: 12px; padding: 5px;")
        layout.addWidget(self.selected_box_rotated_label)
        
        layout.addStretch()
        
        return widget
    
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
        
        # 上下重量平衡
        lr_layout = QHBoxLayout()
        lr_layout.addWidget(QLabel("上下:"))
        self.lr_balance_label = QLabel("- / -")
        self.lr_diff_label = QLabel("扭矩差距: -")
        lr_layout.addWidget(self.lr_balance_label)
        lr_layout.addWidget(self.lr_diff_label)
        layout.addLayout(lr_layout)
        
        # 上下平衡指示器
        self.lr_balance_bar = QProgressBar()
        self.lr_balance_bar.setRange(0, 100)
        self.lr_balance_bar.setValue(50)
        layout.addWidget(self.lr_balance_bar)
        
        # 前后重量平衡
        fr_layout = QHBoxLayout()
        fr_layout.addWidget(QLabel("前后:"))
        self.fr_balance_label = QLabel("- / -")
        self.fr_diff_label = QLabel("扭矩差距: -")
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
        # 由于界面简化，这个方法现在不需要显示集装箱信息
        # 集装箱信息已经移动到集装箱视图的顶部平衡信息栏
        pass
    
    def show_box_info(self, box: Box):
        """显示箱子信息"""
        if not box:
            self.clear_box_info()
            return
        
        self.selected_box_id_label.setText(f"箱号: {box.id}")
        self.selected_box_size_label.setText(f"尺寸: {box.length} × {box.width} mm")
        self.selected_box_weight_label.setText(f"重量: {box.weight} kg")
        self.selected_box_pos_label.setText(f"位置: ({box.x:.0f}, {box.y:.0f}) mm")
        
        # 显示旋转状态
        if hasattr(box, 'rotated') and box.rotated:
            self.selected_box_rotated_label.setText("状态: 已旋转 90°")
        else:
            self.selected_box_rotated_label.setText("状态: 正常方向")
    
    def clear_container_info(self):
        """清除集装箱信息"""
        # 由于界面简化，这个方法现在不需要清除集装箱信息
        pass
    
    def clear_box_info(self):
        """清除箱子信息"""
        self.selected_box_id_label.setText("箱号: 未选择")
        self.selected_box_size_label.setText("尺寸: -")
        self.selected_box_weight_label.setText("重量: -")
        self.selected_box_pos_label.setText("位置: -")
        self.selected_box_rotated_label.setText("状态: -")
    
    def update_weight_balance_display(self, balance_info: dict):
        """更新重量平衡显示（基于扭矩）"""
        # 左右平衡
        left_torque = balance_info['left_torque']
        right_torque = balance_info['right_torque']
        lr_torque = balance_info['lr_torque']
        lr_torque_limit = balance_info['lr_torque_limit']
        
        self.lr_balance_label.setText(f"{left_torque/1000:.1f} / {right_torque/1000:.1f}kg·m")
        self.lr_diff_label.setText(f"扭矩差距: {lr_torque/1000:.1f}kg·m")
        
        # 设置进度条和颜色
        total_torque = left_torque + right_torque
        if total_torque > 0:
            lr_percentage = int((left_torque / total_torque) * 100)
            self.lr_balance_bar.setValue(lr_percentage)
            
            # 根据扭矩设置颜色
            if lr_torque > lr_torque_limit:  # 超出限制
                self.lr_balance_bar.setStyleSheet("QProgressBar::chunk { background-color: red; }")
            elif lr_torque > lr_torque_limit * 0.8:  # 接近限制（80%）
                self.lr_balance_bar.setStyleSheet("QProgressBar::chunk { background-color: orange; }")
            else:
                self.lr_balance_bar.setStyleSheet("QProgressBar::chunk { background-color: green; }")
        
        # 前后平衡
        front_torque = balance_info['front_torque']
        rear_torque = balance_info['rear_torque']
        fr_torque = balance_info['fr_torque']
        fr_torque_limit = balance_info['fr_torque_limit']
        
        self.fr_balance_label.setText(f"{front_torque/1000:.1f} / {rear_torque/1000:.1f}kg·m")
        self.fr_diff_label.setText(f"扭矩差距: {fr_torque/1000:.1f}kg·m")
        
        total_fr_torque = front_torque + rear_torque
        if total_fr_torque > 0:
            fr_percentage = int((front_torque / total_fr_torque) * 100)
            self.fr_balance_bar.setValue(fr_percentage)
            
            # 根据扭矩设置颜色
            if fr_torque > fr_torque_limit:  # 超出限制
                self.fr_balance_bar.setStyleSheet("QProgressBar::chunk { background-color: red; }")
            elif fr_torque > fr_torque_limit * 0.8:  # 接近限制（80%）
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
    
    
