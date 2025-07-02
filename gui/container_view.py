#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGraphicsView, 
                             QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem,
                             QToolBar, QAction, QPushButton, QSlider, QLabel, QMenu,
                             QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, pyqtSignal, QRectF, QPointF
from PyQt5.QtGui import (QPen, QBrush, QColor, QFont, QPainter, QTransform, 
                         QWheelEvent, QMouseEvent)
from typing import Dict, List, Optional
import random
import time

from core.container import Container
from core.box import Box
from core.spatial_index import SpatialGrid, BoundingBox

class BoxGraphicsItem(QGraphicsRectItem):
    """箱子图形项"""
    
    def __init__(self, box: Box, scale_factor: float = 0.2):
        self.box = box
        self.scale_factor = scale_factor
        self.last_update_time = 0  # 用于节流更新
        self._is_dragging = False  # 拖动状态标志
        self._cached_view = None  # 缓存视图引用
        self._cached_container = None  # 缓存容器引用
        self._is_swap_candidate = False  # 是否是交换候选
        self._shadow_effect = None  # 阴影效果
        
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
        self.setAcceptHoverEvents(True)  # 接受悬停事件
        
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
            
            # 先计算原始位置（不带网格吸附）
            raw_x = new_pos.x() / self.scale_factor
            raw_y = new_pos.y() / self.scale_factor
            
            # 动态网格大小：接近其他箱子时使用更细的网格
            grid_size = 10  # 默认10mm网格
            container = self.get_container_cached()
            
            if container:
                # 使用空间索引获取附近的箱子
                view = self.get_view_cached()
                if view and hasattr(view, 'spatial_index'):
                    # 获取100mm范围内的箱子
                    nearby_boxes = view.spatial_index.get_nearby_objects(self.box, 100)
                    
                    if nearby_boxes:
                        # 计算到最近箱子的距离（使用平方距离，避免平方根）
                        min_distance_sq = float('inf')
                        for other_box in nearby_boxes:
                            dx = max(0, max(other_box.x - (raw_x + self.box.actual_length), 
                                           raw_x - (other_box.x + other_box.actual_length)))
                            dy = max(0, max(other_box.y - (raw_y + self.box.actual_width),
                                           raw_y - (other_box.y + other_box.actual_width)))
                            distance_sq = dx*dx + dy*dy
                            min_distance_sq = min(min_distance_sq, distance_sq)
                        
                        # 根据平方距离设置网格大小
                        if min_distance_sq < 50*50:  # 50mm范围内
                            grid_size = 1  # 1mm精细网格
                        elif min_distance_sq < 100*100:  # 100mm范围内
                            grid_size = 5  # 5mm中等网格
            
            # 应用网格吸附
            new_x = round(raw_x / grid_size) * grid_size
            new_y = round(raw_y / grid_size) * grid_size
            
            # 临时更新box位置进行检测
            old_x, old_y = self.box.x, self.box.y
            self.box.x = new_x
            self.box.y = new_y
            
            # 检查新位置是否有效
            is_valid = True
            
            if container:
                # 检查边界
                if (new_x < 0 or new_y < 0 or 
                    new_x + self.box.actual_length > container.length or
                    new_y + self.box.actual_width > container.width):
                    is_valid = False
                else:
                    # 使用空间索引进行碰撞检测
                    view = self.get_view_cached()
                    if view and hasattr(view, 'spatial_index'):
                        # 查询可能碰撞的箱子
                        bbox = BoundingBox(new_x, new_y, 
                                         new_x + self.box.actual_length,
                                         new_y + self.box.actual_width)
                        candidates = view.spatial_index.query(bbox)
                        
                        # 只检查候选箱子
                        for other_box in candidates:
                            if other_box is not self.box and self.box.overlaps_with(other_box):
                                is_valid = False
                                break
                    else:
                        # 备用：全部检查
                        for other_box in container.boxes:
                            if other_box is not self.box and self.box.overlaps_with(other_box):
                                is_valid = False
                                break
            
            if is_valid:
                # 位置有效，使用绿色边框
                self.setPen(QPen(QColor(0, 200, 0), 2))
                
                # 实时更新重量平衡信息（拖动过程中，限制更新频率）
                current_time = time.time() * 1000  # 毫秒
                if current_time - self.last_update_time > 100:  # 改为100ms，减少更新频率
                    self.last_update_time = current_time
                    view = self.get_view_cached()
                    if view and hasattr(view, 'box_moved'):
                        view.box_moved.emit(self.box, new_x, new_y)
                
                # 返回吸附后的位置
                return QPointF(new_x * self.scale_factor, new_y * self.scale_factor)
            else:
                # 位置无效，使用磁吸算法找到最近的有效位置
                valid_x, valid_y = self._find_snap_position(
                    old_x, old_y, raw_x, raw_y, container
                )
                
                if (valid_x, valid_y) != (old_x, old_y):
                    # 找到了更近的有效位置
                    self.box.x = valid_x
                    self.box.y = valid_y
                    self.setPen(QPen(QColor(255, 150, 0), 2))  # 橙色边框
                    return QPointF(valid_x * self.scale_factor, valid_y * self.scale_factor)
                else:
                    # 恢复原位置
                    self.box.x = old_x
                    self.box.y = old_y
                    self.setPen(QPen(QColor(255, 0, 0), 2))
                    return QPointF(old_x * self.scale_factor, old_y * self.scale_factor)
        
        return super().itemChange(change, value)
    
    def _find_snap_position(self, old_x, old_y, target_x, target_y, container):
        """使用磁吸算法找到最接近的有效位置"""
        # 如果目标位置在容器内且不发生碰撞，直接返回
        self.box.x = target_x
        self.box.y = target_y
        
        # 检查边界
        if (target_x >= 0 and target_y >= 0 and 
            target_x + self.box.actual_length <= container.length and
            target_y + self.box.actual_width <= container.width):
            
            # 检查是否与其他箱子碰撞
            collision_box = None
            for other_box in container.boxes:
                if other_box is not self.box and self.box.overlaps_with(other_box):
                    collision_box = other_box
                    break
            
            if collision_box:
                # 计算吸附位置（紧贴碰撞箱子）
                snap_positions = []
                
                # 吸附到碰撞箱子的右侧
                snap_x_right = collision_box.x + collision_box.actual_length + 1
                if (snap_x_right + self.box.actual_length <= container.length and
                    abs(snap_x_right - target_x) < abs(old_x - target_x)):
                    snap_positions.append((snap_x_right, target_y))
                
                # 吸附到碰撞箱子的左侧
                snap_x_left = collision_box.x - self.box.actual_length - 1
                if (snap_x_left >= 0 and
                    abs(snap_x_left - target_x) < abs(old_x - target_x)):
                    snap_positions.append((snap_x_left, target_y))
                
                # 吸附到碰撞箱子的上方
                snap_y_top = collision_box.y - self.box.actual_width - 1
                if (snap_y_top >= 0 and
                    abs(snap_y_top - target_y) < abs(old_y - target_y)):
                    snap_positions.append((target_x, snap_y_top))
                
                # 吸附到碰撞箱子的下方
                snap_y_bottom = collision_box.y + collision_box.actual_width + 1
                if (snap_y_bottom + self.box.actual_width <= container.width and
                    abs(snap_y_bottom - target_y) < abs(old_y - target_y)):
                    snap_positions.append((target_x, snap_y_bottom))
                
                # 选择最近的吸附位置
                best_snap = None
                min_distance = float('inf')
                
                for snap_x, snap_y in snap_positions:
                    self.box.x = snap_x
                    self.box.y = snap_y
                    
                    # 检查这个位置是否有效（不与其他箱子碰撞）
                    valid = True
                    view = self.get_view_cached()
                    if view and hasattr(view, 'spatial_index'):
                        # 使用空间索引检查
                        bbox = BoundingBox(snap_x, snap_y,
                                         snap_x + self.box.actual_length,
                                         snap_y + self.box.actual_width)
                        candidates = view.spatial_index.query(bbox)
                        for other_box in candidates:
                            if other_box is not self.box and self.box.overlaps_with(other_box):
                                valid = False
                                break
                    else:
                        # 备用方法
                        for other_box in container.boxes:
                            if other_box is not self.box and self.box.overlaps_with(other_box):
                                valid = False
                                break
                    
                    if valid:
                        distance = ((snap_x - target_x)**2 + (snap_y - target_y)**2)**0.5
                        if distance < min_distance:
                            min_distance = distance
                            best_snap = (snap_x, snap_y)
                
                if best_snap:
                    return best_snap
        
        # 如果没有找到合适的吸附位置，返回原位置
        return old_x, old_y
    
    
    def get_container(self):
        """获取当前的容器对象"""
        if self.scene():
            for view in self.scene().views():
                if hasattr(view, 'container'):
                    return view.container
        return None
    
    def get_container_cached(self):
        """获取缓存的容器对象"""
        if self._cached_container is None:
            self._cached_container = self.get_container()
        return self._cached_container
    
    def get_view_cached(self):
        """获取缓存的视图对象"""
        if self._cached_view is None and self.scene():
            views = self.scene().views()
            if views:
                self._cached_view = views[0]
        return self._cached_view
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.RightButton:
            # 右键点击显示菜单
            self.show_context_menu(event.pos())
            event.accept()
            return
        elif event.button() == Qt.LeftButton:
            self._is_dragging = True
            # 清空缓存
            self._cached_view = None
            self._cached_container = None
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        super().mouseReleaseEvent(event)
        
        if event.button() == Qt.LeftButton:
            self._is_dragging = False
            # 清空缓存
            self._cached_view = None
            self._cached_container = None
            
            # 更新空间索引
            view = self.get_view_cached()
            if view and hasattr(view, 'spatial_index'):
                bbox = BoundingBox(self.box.x, self.box.y,
                                 self.box.x + self.box.actual_length,
                                 self.box.y + self.box.actual_width)
                view.spatial_index.update(self.box, bbox)
        
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
        menu = QMenu()
        
        # 查找可交换的相邻箱子
        swap_candidates = self.find_adjacent_boxes()
        
        # 调试信息：记录相邻检测结果
        container = self.get_container_cached()
        if container:
            total_boxes = len(container.boxes)
            print(f"箱子 {self.box.id} 右键菜单: 总箱子数={total_boxes}, 找到相邻箱子数={len(swap_candidates)}")
            if swap_candidates:
                for candidate in swap_candidates:
                    direction = self.get_direction_to_box(candidate)
                    print(f"  - {direction}箱子 {candidate.id}")
        
        if swap_candidates:
            swap_menu = menu.addMenu("与相邻箱子互换")
            for candidate in swap_candidates:
                direction = self.get_direction_to_box(candidate)
                action = QAction(f"与{direction}箱子 {candidate.id} 互换", menu)
                action.triggered.connect(lambda checked, box=candidate: self.swap_with_box(box))
                swap_menu.addAction(action)
            menu.addSeparator()
        
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
            
            # 从容器视图的box_items字典中移除
            for view in self.scene().views():
                if hasattr(view, 'box_items') and self.box in view.box_items:
                    del view.box_items[self.box]
                    break
            
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
    
    def find_adjacent_boxes(self):
        """查找相邻的箱子"""
        adjacent_boxes = []
        container = self.get_container_cached()
        if not container:
            return adjacent_boxes
        
        gap_threshold = 100  # 间隙阈值(mm) - 放宽到100mm
        overlap_threshold = 200  # 重叠阈值(mm) - 需要有一定重叠才算相邻
        
        for other_box in container.boxes:
            if other_box is self.box:
                continue
            
            # 计算两个箱子的边界
            self_left = self.box.x
            self_right = self.box.x + self.box.actual_length
            self_top = self.box.y
            self_bottom = self.box.y + self.box.actual_width
            
            other_left = other_box.x
            other_right = other_box.x + other_box.actual_length
            other_top = other_box.y
            other_bottom = other_box.y + other_box.actual_width
            
            # 检查左右相邻（需要在Y方向有重叠）
            y_overlap = min(self_bottom, other_bottom) - max(self_top, other_top)
            if y_overlap > overlap_threshold:
                # 右侧相邻：self的右边接近other的左边
                if abs(self_right - other_left) <= gap_threshold:
                    adjacent_boxes.append(other_box)
                # 左侧相邻：self的左边接近other的右边
                elif abs(self_left - other_right) <= gap_threshold:
                    adjacent_boxes.append(other_box)
            
            # 检查上下相邻（需要在X方向有重叠）
            x_overlap = min(self_right, other_right) - max(self_left, other_left)
            if x_overlap > overlap_threshold:
                # 下方相邻：self的下边接近other的上边
                if abs(self_bottom - other_top) <= gap_threshold:
                    adjacent_boxes.append(other_box)
                # 上方相邻：self的上边接近other的下边
                elif abs(self_top - other_bottom) <= gap_threshold:
                    adjacent_boxes.append(other_box)
        
        return adjacent_boxes
    
    def get_direction_to_box(self, other_box):
        """获取到另一个箱子的方向"""
        # 计算两个箱子的中心点
        self_center_x = self.box.x + self.box.actual_length / 2
        self_center_y = self.box.y + self.box.actual_width / 2
        other_center_x = other_box.x + other_box.actual_length / 2
        other_center_y = other_box.y + other_box.actual_width / 2
        
        # 计算相对位置
        dx = other_center_x - self_center_x
        dy = other_center_y - self_center_y
        
        # 根据哪个方向的距离更大来判断主要方向
        if abs(dx) > abs(dy):
            # 主要是左右方向
            if dx > 0:
                return "右侧"
            else:
                return "左侧"
        else:
            # 主要是上下方向
            if dy > 0:
                return "下方"
            else:
                return "上方"
    
    def can_swap_with(self, other_box):
        """检查是否可以与另一个箱子互换位置"""
        container = self.get_container_cached()
        if not container:
            return False
        
        # 临时保存当前位置
        self_old_x, self_old_y = self.box.x, self.box.y
        other_old_x, other_old_y = other_box.x, other_box.y
        
        # 尝试交换位置
        self.box.x, self.box.y = other_old_x, other_old_y
        other_box.x, other_box.y = self_old_x, self_old_y
        
        # 检查交换后是否都在边界内
        if (self.box.x < 0 or self.box.y < 0 or 
            self.box.x + self.box.actual_length > container.length or
            self.box.y + self.box.actual_width > container.width or
            other_box.x < 0 or other_box.y < 0 or
            other_box.x + other_box.actual_length > container.length or
            other_box.y + other_box.actual_width > container.width):
            # 恢复位置
            self.box.x, self.box.y = self_old_x, self_old_y
            other_box.x, other_box.y = other_old_x, other_old_y
            return False
        
        # 检查交换后是否与其他箱子碰撞
        for box in container.boxes:
            if box is self.box or box is other_box:
                continue
            
            if self.box.overlaps_with(box) or other_box.overlaps_with(box):
                # 恢复位置
                self.box.x, self.box.y = self_old_x, self_old_y
                other_box.x, other_box.y = other_old_x, other_old_y
                return False
        
        # 恢复位置（只是检查）
        self.box.x, self.box.y = self_old_x, self_old_y
        other_box.x, other_box.y = other_old_x, other_old_y
        return True
    
    def swap_with_box(self, other_box):
        """与另一个箱子互换位置"""
        if not self.can_swap_with(other_box):
            return
        
        # 保存当前位置
        self_old_x, self_old_y = self.box.x, self.box.y
        other_old_x, other_old_y = other_box.x, other_box.y
        
        # 交换位置
        self.box.x, self.box.y = other_old_x, other_old_y
        other_box.x, other_box.y = self_old_x, self_old_y
        
        # 更新图形项位置
        self.setPos(self.box.x * self.scale_factor, self.box.y * self.scale_factor)
        
        # 更新另一个箱子的图形项
        view = self.get_view_cached()
        if view and hasattr(view, 'box_items'):
            if other_box in view.box_items:
                other_item = view.box_items[other_box]
                other_item.setPos(other_box.x * self.scale_factor, other_box.y * self.scale_factor)
        
        # 更新空间索引
        if view and hasattr(view, 'spatial_index'):
            bbox1 = BoundingBox(self.box.x, self.box.y,
                              self.box.x + self.box.actual_length,
                              self.box.y + self.box.actual_width)
            bbox2 = BoundingBox(other_box.x, other_box.y,
                              other_box.x + other_box.actual_length,
                              other_box.y + other_box.actual_width)
            view.spatial_index.update(self.box, bbox1)
            view.spatial_index.update(other_box, bbox2)
        
        # 通知主窗口更新
        if view and hasattr(view, 'box_moved'):
            view.box_moved.emit(self.box, self.box.x, self.box.y)
            view.box_moved.emit(other_box, other_box.x, other_box.y)
    
    def set_swap_candidate(self, is_candidate):
        """设置是否为交换候选"""
        if self._is_swap_candidate != is_candidate:
            self._is_swap_candidate = is_candidate
            if is_candidate:
                # 添加阴影效果
                if not self._shadow_effect:
                    self._shadow_effect = QGraphicsDropShadowEffect()
                    self._shadow_effect.setBlurRadius(15)
                    self._shadow_effect.setColor(QColor(0, 100, 255, 180))
                    self._shadow_effect.setOffset(0, 0)
                    self.setGraphicsEffect(self._shadow_effect)
            else:
                # 移除阴影效果
                self.setGraphicsEffect(None)
    
    def hoverEnterEvent(self, event):
        """鼠标进入事件"""
        super().hoverEnterEvent(event)
        # 检查是否有其他箱子被选中准备交换
        view = self.get_view_cached()
        if view and hasattr(view.parent(), '_preparing_swap') and view.parent()._preparing_swap:
            selected_items = self.scene().selectedItems()
            if selected_items and len(selected_items) == 1:
                selected_item = selected_items[0]
                if isinstance(selected_item, BoxGraphicsItem) and selected_item != self:
                    # 检查是否可以交换
                    if selected_item.can_swap_with(self.box):
                        self.set_swap_candidate(True)
    
    def hoverLeaveEvent(self, event):
        """鼠标离开事件"""
        super().hoverLeaveEvent(event)
        self.set_swap_candidate(False)

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
        self.spatial_index: Optional[SpatialGrid] = None  # 空间索引
        
        
        self.setup_view()
        self.setup_scene()
        
        # 启用放置功能
        self.setAcceptDrops(True)
    
    def setup_view(self):
        """设置视图"""
        # WSL环境兼容性：禁用OpenGL，使用软件渲染
        self.setViewport(QWidget())
        
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        
        # 优化拖动性能
        self.setOptimizationFlag(QGraphicsView.DontSavePainterState, True)
        self.setOptimizationFlag(QGraphicsView.DontAdjustForAntialiasing, True)
        self.setCacheMode(QGraphicsView.CacheBackground)
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
        # 创建空间索引
        if container:
            self.spatial_index = SpatialGrid(container.length, container.width)
        else:
            self.spatial_index = None
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
        
        # 添加方向水印
        self.draw_direction_watermarks(width, height)
    
    def draw_direction_watermarks(self, width, height):
        """绘制方向水印"""
        # 水印参数
        watermark_size = 50
        watermark_font = QFont("Arial", 36, QFont.Bold)  # 增大字体以达到50px效果
        watermark_color = QColor(150, 150, 150, 120)  # 半透明灰色
        
        # 前方水印 (左侧中央，距离中线50px)
        front_text = self.scene.addText("前", watermark_font)
        front_text.setDefaultTextColor(watermark_color)
        front_text.setPos(50, height/2 - 25)  # 距离左边50px，垂直居中
        front_text.setZValue(-0.5)  # 在网格之上，箱子之下
        
        # 后方水印 (右侧中央，距离中线50px)
        rear_text = self.scene.addText("后", watermark_font)
        rear_text.setDefaultTextColor(watermark_color)
        rear_text.setPos(width - 100, height/2 - 25)  # 距离右边50px，垂直居中
        rear_text.setZValue(-0.5)
        
        # 左侧水印 (底部中央，距离中线50px)
        left_text = self.scene.addText("左", watermark_font)
        left_text.setDefaultTextColor(watermark_color)
        left_text.setPos(width/2 - 25, height - 100)  # 水平居中，距离底部50px
        left_text.setZValue(-0.5)
        
        # 右侧水印 (顶部中央，距离中线50px)
        right_text = self.scene.addText("右", watermark_font)
        right_text.setDefaultTextColor(watermark_color)
        right_text.setPos(width/2 - 25, 50)  # 水平居中，距离顶部50px
        right_text.setZValue(-0.5)
    
    def draw_boxes(self):
        """绘制箱子"""
        if not self.container:
            return
        
        # 清空空间索引
        if self.spatial_index:
            self.spatial_index.clear()
        
        for box in self.container.boxes:
            self.add_box_item(box)
            # 添加到空间索引
            if self.spatial_index:
                bbox = BoundingBox(box.x, box.y,
                                 box.x + box.actual_length,
                                 box.y + box.actual_width)
                self.spatial_index.insert(box, bbox)
    
    def add_box_item(self, box: Box):
        """添加箱子图形项"""
        if box in self.box_items:
            return
        
        box_item = BoxGraphicsItem(box, self.scale_factor)
        self.scene.addItem(box_item)
        self.box_items[box] = box_item
        
        # 添加到空间索引
        if self.spatial_index:
            bbox = BoundingBox(box.x, box.y,
                             box.x + box.actual_length,
                             box.y + box.actual_width)
            self.spatial_index.insert(box, bbox)
    
    def remove_box_item(self, box: Box):
        """移除箱子图形项"""
        if box in self.box_items:
            self.scene.removeItem(self.box_items[box])
            del self.box_items[box]
            
            # 从空间索引移除
            if self.spatial_index:
                self.spatial_index.remove(box)
    
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
    
    def dragEnterEvent(self, event):
        """拖入事件"""
        if event.mimeData().hasText() and event.mimeData().text().startswith("box_id:"):
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def dragMoveEvent(self, event):
        """拖动事件"""
        if event.mimeData().hasText() and event.mimeData().text().startswith("box_id:"):
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def dropEvent(self, event):
        """放置事件"""
        if event.mimeData().hasText() and event.mimeData().text().startswith("box_id:"):
            box_id = event.mimeData().text().replace("box_id:", "")
            
            # 获取放置位置（相对于场景的位置）
            scene_pos = self.mapToScene(event.pos())
            drop_x = scene_pos.x() / self.scale_factor
            drop_y = scene_pos.y() / self.scale_factor
            
            # 通知主窗口处理拖放
            if hasattr(self.parent(), 'on_box_dropped'):
                self.parent().on_box_dropped(box_id, drop_x, drop_y)
            
            event.acceptProposedAction()
        else:
            event.ignore()

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
    
    def on_box_dropped(self, box_id, x, y):
        """处理箱子拖放事件"""
        # 检查主窗口是否有处理拖放的方法
        main_window = self.parent()
        while main_window:
            if hasattr(main_window, 'on_box_dropped'):
                main_window.on_box_dropped(box_id, x, y)
                break
            main_window = main_window.parent()
    
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
        tips_label = QLabel("操作提示: 左键拖动箱子 | 右键互换相邻箱子 | 双击旋转 | 滚轮缩放 | 拖拽列表箱子到容器")
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
            # 重置箱子位置，避免影响后续放置
            box.x = 0
            box.y = 0
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
        """更新重量平衡信息（基于扭矩）"""
        # 获取重量和扭矩数据
        left_weight = balance_info['left_weight']
        right_weight = balance_info['right_weight']
        front_weight = balance_info['front_weight']
        rear_weight = balance_info['rear_weight']
        lr_torque = balance_info['lr_torque']
        fr_torque = balance_info['fr_torque']
        lr_torque_limit = balance_info['lr_torque_limit']
        fr_torque_limit = balance_info['fr_torque_limit']
        
        # 更新各区域扭矩
        left_torque = balance_info['left_torque']
        right_torque = balance_info['right_torque']
        front_torque = balance_info['front_torque']
        rear_torque = balance_info['rear_torque']
        
        self.left_weight_label.setText(f"左: {left_torque/1000:.1f}kg·m")
        self.right_weight_label.setText(f"右: {right_torque/1000:.1f}kg·m")
        self.lr_diff_label.setText(f"左右扭矩差距: {lr_torque/1000:.1f}kg·m")
        
        self.front_weight_label.setText(f"前: {front_torque/1000:.1f}kg·m")
        self.rear_weight_label.setText(f"后: {rear_torque/1000:.1f}kg·m")
        self.fr_diff_label.setText(f"前后扭矩差距: {fr_torque/1000:.1f}kg·m")
        
        # 判断平衡状态（基于扭矩）
        lr_ok = lr_torque <= lr_torque_limit
        fb_ok = fr_torque <= fr_torque_limit
        
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