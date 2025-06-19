#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGraphicsView, 
                             QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem,
                             QToolBar, QAction, QPushButton, QSlider, QLabel)
from PyQt5.QtCore import Qt, pyqtSignal, QRectF, QPointF
from PyQt5.QtGui import (QPen, QBrush, QColor, QFont, QPainter, QTransform, 
                         QWheelEvent, QMouseEvent)
from typing import Dict, List, Optional
import random

from core.container import Container
from core.box import Box

class BoxGraphicsItem(QGraphicsRectItem):
    """箱子图形项"""
    
    def __init__(self, box: Box, scale_factor: float = 0.1):
        self.box = box
        self.scale_factor = scale_factor
        
        # 创建矩形（按比例缩放）
        super().__init__(0, 0, 
                        box.actual_length * scale_factor, 
                        box.actual_width * scale_factor)
        
        self.setPos(box.x * scale_factor, box.y * scale_factor)
        
        # 设置样式
        self.setup_appearance()
        
        # 设置为可选择和可移动
        self.setFlag(QGraphicsRectItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsRectItem.ItemIsMovable, True)
        
        # 添加文本标签
        self.text_item = QGraphicsTextItem(self)
        self.update_text()
    
    def setup_appearance(self):
        """设置外观"""
        # 根据重量生成颜色
        colors = [
            QColor(255, 182, 193),  # 浅粉色
            QColor(173, 216, 230),  # 浅蓝色
            QColor(144, 238, 144),  # 浅绿色
            QColor(255, 218, 185),  # 桃色
            QColor(221, 160, 221),  # 梅红色
            QColor(255, 255, 224),  # 浅黄色
        ]
        
        # 根据箱子ID生成一致的颜色
        color_index = hash(self.box.id) % len(colors)
        color = colors[color_index]
        
        # 根据重量调整颜色深浅
        if self.box.weight > 1000:
            color = color.darker(130)  # 重箱用深色
        elif self.box.weight < 300:
            color = color.lighter(130)  # 轻箱用浅色
        
        self.setBrush(QBrush(color))
        self.setPen(QPen(QColor(0, 0, 0), 1))
    
    def update_text(self):
        """更新文本显示"""
        text = f"{self.box.id}\\n{self.box.weight}kg"
        self.text_item.setPlainText(text)
        
        # 设置字体大小
        font = QFont()
        font.setPixelSize(max(8, int(min(self.rect().width(), self.rect().height()) / 8)))
        self.text_item.setFont(font)
        
        # 居中文本
        text_rect = self.text_item.boundingRect()
        item_rect = self.rect()
        self.text_item.setPos(
            (item_rect.width() - text_rect.width()) / 2,
            (item_rect.height() - text_rect.height()) / 2
        )
    
    def update_from_box(self):
        """从Box对象更新图形项"""
        # 更新位置
        self.setPos(self.box.x * self.scale_factor, self.box.y * self.scale_factor)
        
        # 更新大小（如果旋转状态改变）
        new_rect = QRectF(0, 0, 
                         self.box.actual_length * self.scale_factor,
                         self.box.actual_width * self.scale_factor)
        self.setRect(new_rect)
        
        # 更新文本
        self.update_text()
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        super().mousePressEvent(event)
        
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        super().mouseMoveEvent(event)
        
        # 更新Box对象的位置
        scene_pos = self.pos()
        self.box.x = scene_pos.x() / self.scale_factor
        self.box.y = scene_pos.y() / self.scale_factor
    
    def mouseDoubleClickEvent(self, event):
        """双击事件 - 旋转箱子"""
        if self.box.can_rotate():
            self.box.rotate()
            self.update_from_box()

class ContainerGraphicsView(QGraphicsView):
    """集装箱图形视图"""
    
    # 信号定义
    box_moved = pyqtSignal(Box, float, float)
    box_selected = pyqtSignal(Box)
    selection_cleared = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        self.container: Optional[Container] = None
        self.scale_factor = 0.1  # 缩放因子：1mm = 0.1像素
        self.box_items: Dict[Box, BoxGraphicsItem] = {}
        
        self.setup_view()
        self.setup_scene()
    
    def setup_view(self):
        """设置视图"""
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setMouseTracking(True)
        
        # 设置滚轮缩放
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
    
    def setup_scene(self):
        """设置场景"""
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        
        # 连接场景信号
        self.scene.selectionChanged.connect(self.on_selection_changed)
    
    def set_container(self, container: Container):
        """设置集装箱"""
        self.container = container
        self.update_view()
    
    def update_view(self):
        """更新视图"""
        if not self.container:
            return
        
        # 清空场景
        self.scene.clear()
        self.box_items.clear()
        
        # 绘制集装箱边界
        self.draw_container_boundary()
        
        # 绘制网格
        self.draw_grid()
        
        # 绘制箱子
        self.draw_boxes()
        
        # 调整视图范围
        self.fit_in_view()
    
    def draw_container_boundary(self):
        """绘制集装箱边界"""
        if not self.container:
            return
        
        width = self.container.length * self.scale_factor
        height = self.container.width * self.scale_factor
        
        # 绘制边界矩形
        boundary = self.scene.addRect(0, 0, width, height,
                                    QPen(QColor(0, 0, 0), 3),
                                    QBrush(QColor(245, 245, 245)))
        boundary.setZValue(-2)  # 置于底层
        
        # 添加标题
        title = self.scene.addText(f"{self.container.name} ({self.container.length/1000:.1f}m × {self.container.width/1000:.1f}m)",
                                 QFont("Arial", 12, QFont.Bold))
        title.setPos(10, -30)
    
    def draw_grid(self):
        """绘制网格"""
        if not self.container:
            return
        
        width = self.container.length * self.scale_factor
        height = self.container.width * self.scale_factor
        
        grid_size = 100 * self.scale_factor  # 1米网格
        
        pen = QPen(QColor(200, 200, 200), 1, Qt.DotLine)
        
        # 垂直线
        x = grid_size
        while x < width:
            line = self.scene.addLine(x, 0, x, height, pen)
            line.setZValue(-1)
            x += grid_size
        
        # 水平线
        y = grid_size
        while y < height:
            line = self.scene.addLine(0, y, width, y, pen)
            line.setZValue(-1)
            y += grid_size
    
    def draw_boxes(self):
        """绘制箱子"""
        if not self.container:
            return
        
        for box in self.container.boxes:
            self.add_box_item(box)
    
    def add_box_item(self, box: Box):
        """添加箱子图形项"""
        if box in self.box_items:
            return
        
        box_item = BoxGraphicsItem(box, self.scale_factor)
        self.scene.addItem(box_item)
        self.box_items[box] = box_item
    
    def remove_box_item(self, box: Box):
        """移除箱子图形项"""
        if box in self.box_items:
            self.scene.removeItem(self.box_items[box])
            del self.box_items[box]
    
    def add_box(self, box: Box):
        """添加箱子"""
        self.add_box_item(box)
    
    def remove_box(self, box: Box):
        """移除箱子"""
        self.remove_box_item(box)
    
    def highlight_box(self, box: Box):
        """高亮显示箱子"""
        if box in self.box_items:
            item = self.box_items[box]
            self.scene.clearSelection()
            item.setSelected(True)
            self.centerOn(item)
    
    def fit_in_view(self):
        """调整视图以适应内容"""
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        
        # 添加一些边距
        current_transform = self.transform()
        scale = current_transform.m11()
        if scale > 1:
            self.scale(0.8, 0.8)
    
    def on_selection_changed(self):
        """选择改变事件"""
        selected_items = self.scene.selectedItems()
        
        if selected_items:
            # 找到选中的BoxGraphicsItem
            for item in selected_items:
                if isinstance(item, BoxGraphicsItem):
                    self.box_selected.emit(item.box)
                    return
        else:
            self.selection_cleared.emit()
    
    def wheelEvent(self, event: QWheelEvent):
        """滚轮事件 - 缩放"""
        factor = 1.2
        
        if event.angleDelta().y() < 0:
            factor = 1.0 / factor
        
        self.scale(factor, factor)
    
    def keyPressEvent(self, event):
        """按键事件"""
        if event.key() == Qt.Key_Delete:
            # 删除选中的箱子
            selected_items = self.scene.selectedItems()
            for item in selected_items:
                if isinstance(item, BoxGraphicsItem):
                    if self.container:
                        self.container.remove_box(item.box)
                    self.remove_box_item(item.box)
        elif event.key() == Qt.Key_R:
            # 旋转选中的箱子
            selected_items = self.scene.selectedItems()
            for item in selected_items:
                if isinstance(item, BoxGraphicsItem):
                    if item.box.can_rotate():
                        item.box.rotate()
                        item.update_from_box()
        else:
            super().keyPressEvent(event)

class ContainerView(QWidget):
    """集装箱视图组件"""
    
    # 信号定义
    box_moved = pyqtSignal(Box, float, float)
    box_placed = pyqtSignal(Box)
    selection_changed = pyqtSignal(object)  # Box or None
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setup_connections()
    
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        
        # 图形视图
        self.graphics_view = ContainerGraphicsView()
        
        # 工具栏
        self.create_toolbar()
        layout.addWidget(self.toolbar)
        
        # 图形视图
        layout.addWidget(self.graphics_view)
        
        # 底部控制栏
        self.create_control_bar()
        layout.addLayout(self.control_layout)
    
    def create_toolbar(self):
        """创建工具栏"""
        self.toolbar = QToolBar()
        
        # 适应视图
        fit_action = QAction("适应视图", self)
        fit_action.triggered.connect(self.graphics_view.fit_in_view)
        self.toolbar.addAction(fit_action)
        
        self.toolbar.addSeparator()
        
        # 放大
        zoom_in_action = QAction("放大", self)
        zoom_in_action.triggered.connect(lambda: self.graphics_view.scale(1.2, 1.2))
        self.toolbar.addAction(zoom_in_action)
        
        # 缩小
        zoom_out_action = QAction("缩小", self)
        zoom_out_action.triggered.connect(lambda: self.graphics_view.scale(0.8, 0.8))
        self.toolbar.addAction(zoom_out_action)
        
        self.toolbar.addSeparator()
        
        # 显示网格
        self.grid_action = QAction("显示网格", self)
        self.grid_action.setCheckable(True)
        self.grid_action.setChecked(True)
        self.toolbar.addAction(self.grid_action)
    
    def create_control_bar(self):
        """创建控制栏"""
        self.control_layout = QHBoxLayout()
        
        # 缩放滑块
        self.control_layout.addWidget(QLabel("缩放:"))
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setRange(10, 200)
        self.zoom_slider.setValue(100)
        self.zoom_slider.valueChanged.connect(self.on_zoom_changed)
        self.control_layout.addWidget(self.zoom_slider)
        
        self.control_layout.addStretch()
        
        # 状态标签
        self.status_label = QLabel("就绪")
        self.control_layout.addWidget(self.status_label)
    
    def setup_connections(self):
        """设置信号连接"""
        self.graphics_view.box_moved.connect(self.box_moved.emit)
        self.graphics_view.box_selected.connect(self.on_box_selected)
        self.graphics_view.selection_cleared.connect(self.on_selection_cleared)
    
    def set_container(self, container: Container):
        """设置集装箱"""
        self.graphics_view.set_container(container)
    
    def update_view(self):
        """更新视图"""
        self.graphics_view.update_view()
    
    def add_box(self, box: Box):
        """添加箱子"""
        self.graphics_view.add_box(box)
        self.box_placed.emit(box)
    
    def remove_box(self, box: Box):
        """移除箱子"""
        self.graphics_view.remove_box(box)
    
    def highlight_box(self, box: Box):
        """高亮箱子"""
        self.graphics_view.highlight_box(box)
    
    def on_zoom_changed(self, value):
        """缩放滑块改变"""
        scale = value / 100.0
        transform = QTransform()
        transform.scale(scale, scale)
        self.graphics_view.setTransform(transform)
    
    def on_box_selected(self, box: Box):
        """箱子被选中"""
        self.selection_changed.emit(box)
        self.status_label.setText(f"选中箱子: {box.id}")
    
    def on_selection_cleared(self):
        """选择被清除"""
        self.selection_changed.emit(None)
        self.status_label.setText("就绪")