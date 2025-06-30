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
    
    def __init__(self, box: Box, scale_factor: float = 0.2):
        self.box = box
        self.scale_factor = scale_factor
        self.last_update_time = 0  # 用于节流更新
        
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
        self.setFlag(QGraphicsRectItem.ItemSendsGeometryChanges, True)
        
        # 设置Z值确保正确的叠加顺序
        self.setZValue(1)
        
        
        # 添加文本标签
        self.text_item = QGraphicsTextItem(self)
        self.update_text()
    
    def setup_appearance(self):
        """设置外观 - 根据重量设置颜色"""
        weight = self.box.weight
        
        # 根据重量范围设置颜色
        if weight >= 800:  # 重箱 - 红色系
            # 线性插值：800kg = 浅红，2000kg+ = 深红
            ratio = min((weight - 800) / 1200, 1.0)
            r = 255
            g = int(200 - ratio * 150)  # 200 -> 50
            b = int(200 - ratio * 150)  # 200 -> 50
            color = QColor(r, g, b)
        elif weight >= 400:  # 中等 - 黄色系
            # 线性插值：400kg = 浅黄，800kg = 深黄
            ratio = (weight - 400) / 400
            r = 255
            g = int(255 - ratio * 55)  # 255 -> 200
            b = int(150 - ratio * 100)  # 150 -> 50
            color = QColor(r, g, b)
        else:  # 轻箱 - 绿色系
            # 线性插值：0kg = 浅绿，400kg = 深绿
            ratio = weight / 400
            r = int(200 - ratio * 100)  # 200 -> 100
            g = 255
            b = int(200 - ratio * 100)  # 200 -> 100
            color = QColor(r, g, b)
        
        self.setBrush(QBrush(color))
        self.setPen(QPen(QColor(0, 0, 0), 1))
    
    def update_text(self):
        """更新文本显示"""
        # 创建富文本格式，调整字号并确保居中
        text = f'<div style="text-align: center; display: flex; flex-direction: column; justify-content: center; height: 100%;">'
        text += f'<p style="margin: 2px 0; font-size: 28px; font-weight: bold; line-height: 1.1;">{self.box.id}</p>'
        text += f'<p style="margin: 2px 0; font-size: 28px; font-weight: bold; line-height: 1.1;">{self.box.weight}kg</p>'
        text += f'<p style="margin: 2px 0; font-size: 28px; font-weight: bold; line-height: 1.1;">{self.box.length}×{self.box.width}</p>'
        text += '</div>'
        
        self.text_item.setHtml(text)
        
        # 设置字体
        font = QFont("Arial", 8)
        self.text_item.setFont(font)
        
        # 居中文本 - 更精确的居中计算
        text_rect = self.text_item.boundingRect()
        item_rect = self.rect()
        
        # 计算居中位置
        center_x = (item_rect.width() - text_rect.width()) / 2
        center_y = (item_rect.height() - text_rect.height()) / 2
        
        # 确保不会超出边界
        center_x = max(0, center_x)
        center_y = max(0, center_y)
        
        self.text_item.setPos(center_x, center_y)
    
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
    
    def itemChange(self, change, value):
        """处理项目变化事件 - 核心的拖动逻辑"""
        if change == QGraphicsRectItem.ItemPositionChange and self.scene():
            # 获取新位置
            new_pos = value
            
            # 网格吸附，提高拖动流畅度
            grid_size = 10  # 10mm网格
            new_x = round(new_pos.x() / self.scale_factor / grid_size) * grid_size
            new_y = round(new_pos.y() / self.scale_factor / grid_size) * grid_size
            
            # 临时更新box位置进行检测
            old_x, old_y = self.box.x, self.box.y
            self.box.x = new_x
            self.box.y = new_y
            
            # 检查新位置是否有效
            is_valid = True
            container = self.get_container()
            
            if container:
                # 检查边界
                if (new_x < 0 or new_y < 0 or 
                    new_x + self.box.actual_length > container.length or
                    new_y + self.box.actual_width > container.width):
                    is_valid = False
                else:
                    # 检查碰撞（排除自身）
                    for other_box in container.boxes:
                        if other_box is not self.box and self.box.overlaps_with(other_box):
                            is_valid = False
                            break
            
            if is_valid:
                # 位置有效，使用绿色边框
                self.setPen(QPen(QColor(0, 200, 0), 2))
                
                # 实时更新重量平衡信息（拖动过程中，限制更新频率）
                import time
                current_time = time.time() * 1000  # 毫秒
                if current_time - self.last_update_time > 50:  # 每50ms最多更新一次
                    self.last_update_time = current_time
                    for view in self.scene().views():
                        if hasattr(view, 'box_moved'):
                            view.box_moved.emit(self.box, new_x, new_y)
                            break
                
                # 返回吸附后的位置
                return QPointF(new_x * self.scale_factor, new_y * self.scale_factor)
            else:
                # 位置无效，恢复原位置
                self.box.x = old_x
                self.box.y = old_y
                self.setPen(QPen(QColor(255, 0, 0), 2))
                # 返回原位置
                return QPointF(old_x * self.scale_factor, old_y * self.scale_factor)
        
        return super().itemChange(change, value)
    
    
    def get_container(self):
        """获取当前的容器对象"""
        if self.scene():
            for view in self.scene().views():
                if hasattr(view, 'container'):
                    return view.container
        return None
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.RightButton:
            # 右键点击显示菜单
            self.show_context_menu(event.pos())
            event.accept()
            return
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        super().mouseReleaseEvent(event)
        # 恢复正常边框
        self.setPen(QPen(QColor(0, 0, 0), 1))
        
        # 更新box的最终位置
        pos = self.pos()
        old_x, old_y = self.box.x, self.box.y
        new_x = pos.x() / self.scale_factor
        new_y = pos.y() / self.scale_factor
        
        # 如果位置发生了变化，发射信号
        if abs(new_x - old_x) > 0.1 or abs(new_y - old_y) > 0.1:
            self.box.x = new_x
            self.box.y = new_y
            
            # 通知主窗口箱子位置已改变
            for view in self.scene().views():
                if hasattr(view, 'box_moved'):
                    view.box_moved.emit(self.box, new_x, new_y)
                    break
    
    def show_context_menu(self, pos):
        """显示右键菜单"""
        from PyQt5.QtWidgets import QMenu, QAction
        
        menu = QMenu()
        
        # 旋转箱子
        rotate_action = QAction("旋转箱子", menu)
        rotate_action.triggered.connect(self.rotate_box)
        menu.addAction(rotate_action)
        
        # 放回列表
        return_action = QAction("放回左侧列表", menu)
        return_action.triggered.connect(self.return_to_list)
        menu.addAction(return_action)
        
        # 显示菜单
        global_pos = self.scene().views()[0].mapToGlobal(
            self.scene().views()[0].mapFromScene(self.pos() + pos)
        )
        menu.exec_(global_pos)
    
    def return_to_list(self):
        """将箱子放回左侧列表"""
        # 获取主窗口
        container = self.get_container()
        if container and self.box in container.boxes:
            # 在移除之前获取视图引用
            parent_view = None
            if self.scene():
                for view in self.scene().views():
                    if hasattr(view, 'parent') and hasattr(view.parent(), 'return_box_to_list'):
                        parent_view = view.parent()
                        break
            
            # 从集装箱移除
            container.remove_box(self.box)
            
            # 从场景移除
            if self.scene():
                self.scene().removeItem(self)
            
            # 通知主窗口更新左侧列表
            if parent_view:
                parent_view.return_box_to_list(self.box)
    
    def rotate_box(self):
        """旋转箱子"""
        if self.box.can_rotate():
            # 保存原始位置和状态
            old_rotated = self.box.rotated
            old_length = self.box.actual_length
            old_width = self.box.actual_width
            
            # 执行旋转
            self.box.rotate()
            
            # 检查旋转后是否有效
            container = self.get_container()
            if container:
                # 检查边界
                if (self.box.x + self.box.actual_length > container.length or
                    self.box.y + self.box.actual_width > container.width):
                    # 旋转后超出边界，撤销
                    self.box.rotated = old_rotated
                    return
                
                # 检查碰撞
                for other_box in container.boxes:
                    if other_box is not self.box and self.box.overlaps_with(other_box):
                        # 旋转后碰撞，撤销
                        self.box.rotated = old_rotated
                        return
            
            # 旋转有效，更新显示
            self.update_from_box()
    
    def mouseDoubleClickEvent(self, event):
        """双击事件 - 旋转箱子"""
        self.rotate_box()

class ContainerGraphicsView(QGraphicsView):
    """集装箱图形视图"""
    
    # 信号定义
    box_moved = pyqtSignal(Box, float, float)
    box_selected = pyqtSignal(Box)
    selection_cleared = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        self.container: Optional[Container] = None
        self.scale_factor = 0.2  # 缩放因子：1mm = 0.2像素（适中显示）
        self.box_items: Dict[Box, BoxGraphicsItem] = {}
        
        
        self.setup_view()
        self.setup_scene()
    
    def setup_view(self):
        """设置视图"""
        # WSL环境兼容性：禁用OpenGL，使用软件渲染
        self.setViewport(QWidget())
        
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setMouseTracking(True)
        
        # 设置滚轮缩放
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        
        # 禁用优化以提高兼容性
        self.setOptimizationFlags(QGraphicsView.DontAdjustForAntialiasing)
    
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
        
        # 调整视图范围（延迟执行确保绘制完成）
        try:
            from PyQt5.QtCore import QTimer
            if hasattr(self, 'scene') and self.scene:
                QTimer.singleShot(100, self.fit_in_view)
        except Exception as e:
            print(f"update_view timer error: {e}")
    
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
        """绘制网格和中心轴线"""
        if not self.container:
            return
        
        width = self.container.length * self.scale_factor
        height = self.container.width * self.scale_factor
        
        # 绘制网格
        grid_size = 100 * self.scale_factor  # 1米网格
        grid_pen = QPen(QColor(200, 200, 200), 1, Qt.DotLine)
        
        # 垂直网格线
        x = grid_size
        while x < width:
            line = self.scene.addLine(x, 0, x, height, grid_pen)
            line.setZValue(-1)
            x += grid_size
        
        # 水平网格线
        y = grid_size
        while y < height:
            line = self.scene.addLine(0, y, width, y, grid_pen)
            line.setZValue(-1)
            y += grid_size
        
        # 绘制中心轴线
        center_x = width / 2
        center_y = height / 2
        
        # 纵向中心线（左右平衡轴）
        center_line_pen = QPen(QColor(255, 0, 0), 2, Qt.DashLine)
        v_center_line = self.scene.addLine(center_x, 0, center_x, height, center_line_pen)
        v_center_line.setZValue(1)
        
        # 横向中心线（前后平衡轴）
        h_center_line = self.scene.addLine(0, center_y, width, center_y, center_line_pen)
        h_center_line.setZValue(1)
        
        # 添加轴线标签
        v_label = self.scene.addText("左右平衡轴", QFont("Arial", 8))
        v_label.setPos(center_x + 5, 5)
        v_label.setDefaultTextColor(QColor(255, 0, 0))
        
        h_label = self.scene.addText("前后平衡轴", QFont("Arial", 8))
        h_label.setPos(5, center_y + 5)
        h_label.setDefaultTextColor(QColor(255, 0, 0))
    
    
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
        if not self.scene or self.scene.sceneRect().isEmpty():
            return
            
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        
        # 添加一些边距
        current_transform = self.transform()
        scale = current_transform.m11()
        if scale > 1:
            self.scale(0.8, 0.8)
    
    def showEvent(self, event):
        """显示事件 - 自动适应窗口"""
        super().showEvent(event)
        # 安全的延迟调用适应视图
        try:
            from PyQt5.QtCore import QTimer
            if hasattr(self, 'scene') and self.scene:
                QTimer.singleShot(200, self.fit_in_view)
        except Exception as e:
            print(f"showEvent error: {e}")
    
    def resizeEvent(self, event):
        """窗口大小改变事件 - 自动适应"""
        super().resizeEvent(event)
        try:
            if hasattr(self, 'container') and self.container and hasattr(self, 'scene') and self.scene:
                # 延迟调用适应视图，确保布局完成
                from PyQt5.QtCore import QTimer
                QTimer.singleShot(100, self.fit_in_view)
        except Exception as e:
            print(f"resizeEvent error: {e}")
    
    def on_selection_changed(self):
        """选择改变事件"""
        try:
            if not self.scene:
                return
            
            selected_items = self.scene.selectedItems()
            
            if selected_items:
                # 找到选中的BoxGraphicsItem
                for item in selected_items:
                    if isinstance(item, BoxGraphicsItem):
                        self.box_selected.emit(item.box)
                        return
            else:
                self.selection_cleared.emit()
        except RuntimeError:
            # 场景已被删除，忽略错误
            pass
    
    def wheelEvent(self, event: QWheelEvent):
        """滚轮事件 - 缩放"""
        factor = 1.2
        
        if event.angleDelta().y() < 0:
            factor = 1.0 / factor
        
        self.scale(factor, factor)
        
        # 同步更新缩放滑块的值
        try:
            # 找到父级容器中的缩放滑块并更新
            for view in self.scene().views():
                if hasattr(view, 'parent') and hasattr(view.parent(), 'update_zoom_slider'):
                    parent_widget = view.parent()
                    parent_widget.update_zoom_slider()
                    break
        except:
            pass
    
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
        
        # 重量平衡信息栏
        self.create_balance_info_bar()
        layout.addWidget(self.balance_widget)
        
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
        zoom_in_action.triggered.connect(self.zoom_in)
        self.toolbar.addAction(zoom_in_action)
        
        # 缩小
        zoom_out_action = QAction("缩小", self)
        zoom_out_action.triggered.connect(self.zoom_out)
        self.toolbar.addAction(zoom_out_action)
        
        self.toolbar.addSeparator()
        
        # 显示网格
        self.grid_action = QAction("显示网格", self)
        self.grid_action.setCheckable(True)
        self.grid_action.setChecked(True)
        self.toolbar.addAction(self.grid_action)
    
    def create_balance_info_bar(self):
        """创建重量平衡信息栏"""
        self.balance_widget = QWidget()
        balance_layout = QHBoxLayout(self.balance_widget)
        balance_layout.setContentsMargins(10, 5, 10, 5)
        
        # 左侧重量
        self.left_weight_label = QLabel("左: 0kg")
        self.left_weight_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px;")
        balance_layout.addWidget(self.left_weight_label)
        
        # 右侧重量
        self.right_weight_label = QLabel("右: 0kg")
        self.right_weight_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px;")
        balance_layout.addWidget(self.right_weight_label)
        
        # 左右重量差
        self.lr_diff_label = QLabel("左右差: 0kg")
        self.lr_diff_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px;")
        balance_layout.addWidget(self.lr_diff_label)
        
        # 分隔符
        separator1 = QLabel(" | ")
        separator1.setStyleSheet("color: #999;")
        balance_layout.addWidget(separator1)
        
        # 前方重量
        self.front_weight_label = QLabel("前: 0kg")
        self.front_weight_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px;")
        balance_layout.addWidget(self.front_weight_label)
        
        # 后方重量
        self.rear_weight_label = QLabel("后: 0kg")
        self.rear_weight_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px;")
        balance_layout.addWidget(self.rear_weight_label)
        
        # 前后重量差
        self.fr_diff_label = QLabel("前后差: 0kg")
        self.fr_diff_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px;")
        balance_layout.addWidget(self.fr_diff_label)
        
        # 分隔符
        separator2 = QLabel(" | ")
        separator2.setStyleSheet("color: #999;")
        balance_layout.addWidget(separator2)
        
        # 平衡状态标签
        self.balance_status_label = QLabel("平衡状态: 良好")
        self.balance_status_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px; color: green;")
        balance_layout.addWidget(self.balance_status_label)
        
        balance_layout.addStretch()
        
        # 设置背景色
        self.balance_widget.setStyleSheet("background-color: #f5f5f5; border: 1px solid #ddd;")
    
    def create_control_bar(self):
        """创建控制栏"""
        self.control_layout = QHBoxLayout()
        
        # 操作提示
        tips_label = QLabel("操作提示: 左键拖动箱子 | 右键/双击旋转箱子 | 滚轮缩放")
        tips_label.setStyleSheet("color: #555; font-style: italic; padding: 5px;")
        self.control_layout.addWidget(tips_label)
        
        self.control_layout.addStretch()
        
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
    
    def return_box_to_list(self, box):
        """将箱子放回左侧列表"""
        # 获取主窗口
        main_window = None
        widget = self.parent()
        while widget:
            if hasattr(widget, 'pending_boxes'):  # 找到主窗口
                main_window = widget
                break
            widget = widget.parent()
        
        if main_window:
            # 添加到待装载列表
            main_window.pending_boxes.append(box)
            # 更新左侧列表显示
            main_window.box_list_panel.set_boxes(main_window.pending_boxes)
            # 更新状态
            main_window.update_status()
    
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
        # 更新后自动适应视图
        try:
            from PyQt5.QtCore import QTimer
            if hasattr(self.graphics_view, 'fit_in_view'):
                QTimer.singleShot(150, self.graphics_view.fit_in_view)
        except Exception as e:
            print(f"ContainerView update timer error: {e}")
    
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
    
    def zoom_in(self):
        """放大"""
        self.graphics_view.scale(1.2, 1.2)
        self.update_zoom_slider()
    
    def zoom_out(self):
        """缩小"""
        self.graphics_view.scale(0.8, 0.8)
        self.update_zoom_slider()
    
    def update_zoom_slider(self):
        """更新缩放滑块的值"""
        current_scale = self.graphics_view.transform().m11()
        slider_value = int(current_scale * 100)
        self.zoom_slider.blockSignals(True)
        self.zoom_slider.setValue(max(10, min(200, slider_value)))
        self.zoom_slider.blockSignals(False)
    
    def on_zoom_changed(self, value):
        """缩放滑块改变"""
        # 计算当前缩放比例和目标缩放比例
        current_transform = self.graphics_view.transform()
        current_scale = current_transform.m11()
        target_scale = value / 100.0
        
        # 计算需要的缩放因子
        if current_scale != 0:
            scale_factor = target_scale / current_scale
            self.graphics_view.scale(scale_factor, scale_factor)
    
    def on_box_selected(self, box: Box):
        """箱子被选中"""
        self.selection_changed.emit(box)
        self.status_label.setText(f"选中箱子: {box.id}")
    
    def on_selection_cleared(self):
        """选择被清除"""
        self.selection_changed.emit(None)
        self.status_label.setText("就绪")
    
    def update_balance_info(self, balance_info):
        """更新重量平衡信息"""
        # 获取重量数据
        left_weight = balance_info['left_weight']
        right_weight = balance_info['right_weight']
        front_weight = balance_info['front_weight']
        rear_weight = balance_info['rear_weight']
        lr_diff = balance_info['lr_diff']
        fr_diff = balance_info['fr_diff']
        
        # 更新各区域重量
        self.left_weight_label.setText(f"左: {left_weight:.1f}kg")
        self.right_weight_label.setText(f"右: {right_weight:.1f}kg")
        self.lr_diff_label.setText(f"左右差: {lr_diff:.1f}kg")
        
        self.front_weight_label.setText(f"前: {front_weight:.1f}kg")
        self.rear_weight_label.setText(f"后: {rear_weight:.1f}kg")
        self.fr_diff_label.setText(f"前后差: {fr_diff:.1f}kg")
        
        # 判断平衡状态
        lr_ok = lr_diff < 500
        fb_ok = fr_diff < 2000
        
        # 设置颜色和状态
        if lr_ok and fb_ok:
            self.balance_status_label.setText("平衡状态: 良好")
            self.balance_status_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px; color: green;")
            self.balance_widget.setStyleSheet("background-color: #e8f5e9; border: 2px solid #4caf50;")
        else:
            self.balance_status_label.setText("平衡状态: 超限")
            self.balance_status_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px; color: red;")
            self.balance_widget.setStyleSheet("background-color: #ffebee; border: 2px solid #f44336;")
            
        # 设置差值标签的颜色
        if not lr_ok:
            self.lr_diff_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px; color: red;")
        else:
            self.lr_diff_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px; color: green;")
            
        if not fb_ok:
            self.fr_diff_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px; color: red;")
        else:
            self.fr_diff_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px; color: green;")