#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List, Tuple, Optional
import numpy as np
from .box import Box

class Container:
    """集装箱类"""
    
    # 标准集装箱尺寸 (mm)
    DEFAULT_LENGTH = 11900
    DEFAULT_WIDTH = 2300
    
    def __init__(self, name: str = "Container", length: float = None, width: float = None):
        """初始化集装箱"""
        self.length = length or self.DEFAULT_LENGTH
        self.width = width or self.DEFAULT_WIDTH
        self.name = name
        self.boxes: List[Box] = []
        
    @property
    def area(self) -> float:
        """获取集装箱总面积"""
        return self.length * self.width
    
    @property
    def used_area(self) -> float:
        """获取已使用面积"""
        return sum(box.area for box in self.boxes)
    
    @property
    def area_utilization(self) -> float:
        """获取面积利用率 (0-1)"""
        return self.used_area / self.area if self.area > 0 else 0
    
    @property
    def total_weight(self) -> float:
        """获取总重量"""
        return sum(box.weight for box in self.boxes)
    
    def add_box(self, box: Box) -> bool:
        """添加箱子到集装箱"""
        if self.can_place_box(box):
            self.boxes.append(box)
            return True
        return False
    
    def remove_box(self, box: Box) -> bool:
        """从集装箱移除箱子"""
        if box in self.boxes:
            self.boxes.remove(box)
            return True
        return False
    
    def can_place_box(self, box: Box, exclude_self: bool = True) -> bool:
        """检查箱子是否可以放置在指定位置"""
        # 检查是否超出边界
        if (box.x < 0 or box.y < 0 or 
            box.x + box.actual_length > self.length or 
            box.y + box.actual_width > self.width):
            return False
        
        # 检查是否与其他箱子重叠
        for existing_box in self.boxes:
            # 如果exclude_self为True且是同一个箱子，跳过检查
            if exclude_self and existing_box is box:
                continue
            if box.overlaps_with(existing_box):
                return False
        
        return True
    
    def find_placement_position(self, box: Box) -> Optional[Tuple[float, float]]:
        """为箱子寻找合适的放置位置"""
        # 保存原始位置
        original_x, original_y = box.x, box.y
        
        # 简单的左下角优先策略
        step = 50  # 搜索步长 (mm)
        
        max_y = max(0, int(self.width - box.actual_width))
        max_x = max(0, int(self.length - box.actual_length))
        
        for y in range(0, max_y + step, step):
            for x in range(0, max_x + step, step):
                box.move_to(float(x), float(y))
                if self.can_place_box(box):
                    # 恢复原始位置后返回找到的位置
                    box.move_to(original_x, original_y)
                    return (float(x), float(y))
        
        # 没找到位置，恢复原始位置
        box.move_to(original_x, original_y)
        return None
    
    def calculate_weight_balance(self) -> dict:
        """计算重量平衡 - 基于箱子质心位置计算扭矩
        坐标系：X轴（length方向）= 前后方向，Y轴（width方向）= 左右方向
        扭矩 = 重量 × 距离（到中心线的距离）
        """
        if not self.boxes:
            lr_torque_limit = 500000  # 500kg·m = 500000kg·mm（左右方向）
            fr_torque_limit = 2000000  # 2000kg·m = 2000000kg·mm（前后方向）
            return {
                'left_weight': 0,
                'right_weight': 0,
                'front_weight': 0,
                'rear_weight': 0,
                'left_torque': 0,
                'right_torque': 0,
                'front_torque': 0,
                'rear_torque': 0,
                'lr_torque': 0,
                'fr_torque': 0,
                'lr_torque_limit': lr_torque_limit,
                'fr_torque_limit': fr_torque_limit,
                'center_x': self.length / 2,
                'center_y': self.width / 2,
                'is_balanced': True
            }
        
        # 集装箱中心线
        center_x_line = self.length / 2  # 前后分界线（X轴方向）
        center_y_line = self.width / 2   # 左右分界线（Y轴方向）
        
        # 初始化区域重量和扭矩
        # 注意：界面显示概念 - 左侧(下方)对应Y<center_y，右侧(上方)对应Y>=center_y
        left_weight = 0    # Y < center_y (界面下方)
        right_weight = 0   # Y >= center_y (界面上方)
        front_weight = 0   # X < center_x (前方)
        rear_weight = 0    # X >= center_x (后方)
        
        left_torque = 0    # 左侧(下方)扭矩
        right_torque = 0   # 右侧(上方)扭矩
        front_torque = 0   # 前侧扭矩
        rear_torque = 0    # 后侧扭矩
        
        # 为每个箱子计算质心位置和扭矩
        for box in self.boxes:
            # 箱子质心位置
            box_center_x = box.x + box.actual_length / 2  # 前后方向质心
            box_center_y = box.y + box.actual_width / 2   # 左右方向质心
            
            # 计算到中心线的距离
            distance_to_lr_line = abs(box_center_y - center_y_line)  # 到左右中心线距离
            distance_to_fr_line = abs(box_center_x - center_x_line)  # 到前后中心线距离
            
            # 计算前后分配和扭矩（沿X轴方向）
            if box_center_x < center_x_line:
                # 质心在前面
                front_weight += box.weight
                front_torque += box.weight * distance_to_fr_line
            else:
                # 质心在后面
                rear_weight += box.weight
                rear_torque += box.weight * distance_to_fr_line
            
            # 计算左右分配和扭矩（沿Y轴方向）
            if box_center_y < center_y_line:
                # 质心在左侧(界面下方)
                left_weight += box.weight
                left_torque += box.weight * distance_to_lr_line
            else:
                # 质心在右侧(界面上方)
                right_weight += box.weight
                right_torque += box.weight * distance_to_lr_line
        
        # 计算净扭矩（左右和前后的扭矩差值）
        lr_torque = abs(left_torque - right_torque)
        fr_torque = abs(front_torque - rear_torque)
        
        # 计算整体重心（用于显示）
        total_weight = self.total_weight
        if total_weight > 0:
            center_x = sum(box.center_x * box.weight for box in self.boxes) / total_weight
            center_y = sum(box.center_y * box.weight for box in self.boxes) / total_weight
        else:
            center_x = center_x_line
            center_y = center_y_line
        
        # 检查是否平衡（根据扭矩限制）
        # 扭矩限制：左右方向更严格，前后方向更宽松
        # 单位：kg·mm (重量kg × 距离mm)
        lr_torque_limit = 500000  # 500kg·m = 500000kg·mm（左右方向）
        fr_torque_limit = 2000000  # 2000kg·m = 2000000kg·mm（前后方向）
        
        is_balanced = lr_torque <= lr_torque_limit and fr_torque <= fr_torque_limit
        
        return {
            'left_weight': left_weight,
            'right_weight': right_weight,
            'front_weight': front_weight,
            'rear_weight': rear_weight,
            'left_torque': left_torque,
            'right_torque': right_torque,
            'front_torque': front_torque,
            'rear_torque': rear_torque,
            'lr_torque': lr_torque,
            'fr_torque': fr_torque,
            'lr_torque_limit': lr_torque_limit,
            'fr_torque_limit': fr_torque_limit,
            'center_x': center_x,
            'center_y': center_y,
            'is_balanced': is_balanced
        }
    
    def get_available_space(self) -> List[Tuple[float, float, float, float]]:
        """获取可用空间区域列表 (x, y, width, height)"""
        # 简化实现：返回整个容器减去已占用区域
        available_spaces = []
        
        if not self.boxes:
            return [(0, 0, self.length, self.width)]
        
        # 这里可以实现更复杂的空间分割算法
        # 现在返回一个简化的结果
        return available_spaces
    
    def clear(self) -> None:
        """清空所有箱子"""
        self.boxes.clear()
    
    def __str__(self) -> str:
        return f"Container({self.name}, {len(self.boxes)} boxes, {self.area_utilization:.1%} utilized)"