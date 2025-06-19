#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List, Tuple, Optional
import numpy as np
from .box import Box

class Container:
    """集装箱类"""
    
    # 标准集装箱尺寸 (mm)
    DEFAULT_LENGTH = 11800
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
    
    def can_place_box(self, box: Box) -> bool:
        """检查箱子是否可以放置在指定位置"""
        # 检查是否超出边界
        if (box.x < 0 or box.y < 0 or 
            box.x + box.actual_length > self.length or 
            box.y + box.actual_width > self.width):
            return False
        
        # 检查是否与其他箱子重叠
        for existing_box in self.boxes:
            if box.overlaps_with(existing_box):
                return False
        
        return True
    
    def find_placement_position(self, box: Box) -> Optional[Tuple[float, float]]:
        """为箱子寻找合适的放置位置"""
        # 简单的左下角优先策略
        step = 50  # 搜索步长 (mm)
        
        max_y = max(0, int(self.width - box.actual_width))
        max_x = max(0, int(self.length - box.actual_length))
        
        for y in range(0, max_y + step, step):
            for x in range(0, max_x + step, step):
                box.move_to(float(x), float(y))
                if self.can_place_box(box):
                    return (float(x), float(y))
        
        return None
    
    def calculate_weight_balance(self) -> dict:
        """计算重量平衡"""
        if not self.boxes:
            return {
                'left_weight': 0,
                'right_weight': 0,
                'front_weight': 0,
                'rear_weight': 0,
                'lr_diff': 0,
                'fr_diff': 0,
                'center_x': self.length / 2,
                'center_y': self.width / 2,
                'is_balanced': True
            }
        
        # 计算重心
        total_weight = self.total_weight
        if total_weight == 0:
            return self.calculate_weight_balance()
        
        center_x = sum(box.center_x * box.weight for box in self.boxes) / total_weight
        center_y = sum(box.center_y * box.weight for box in self.boxes) / total_weight
        
        # 计算左右重量
        left_weight = sum(box.weight for box in self.boxes if box.center_x < self.length / 2)
        right_weight = sum(box.weight for box in self.boxes if box.center_x >= self.length / 2)
        
        # 计算前后重量
        front_weight = sum(box.weight for box in self.boxes if box.center_y < self.width / 2)
        rear_weight = sum(box.weight for box in self.boxes if box.center_y >= self.width / 2)
        
        # 计算重量差值
        lr_diff = abs(left_weight - right_weight)
        fr_diff = abs(front_weight - rear_weight)
        
        # 检查是否平衡（根据需求文档的限制）
        is_balanced = lr_diff < 500 and fr_diff < 2000
        
        return {
            'left_weight': left_weight,
            'right_weight': right_weight,
            'front_weight': front_weight,
            'rear_weight': rear_weight,
            'lr_diff': lr_diff,
            'fr_diff': fr_diff,
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