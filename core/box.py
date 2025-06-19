#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import Optional, Tuple

@dataclass
class Box:
    """箱子数据类"""
    id: str
    length: float  # 长度 (mm)
    width: float   # 宽度 (mm)
    weight: float  # 重量 (kg)
    height: Optional[float] = None  # 高度 (mm, 可选)
    x: float = 0  # X坐标位置
    y: float = 0  # Y坐标位置
    rotated: bool = False  # 是否旋转90度
    
    @property
    def actual_length(self) -> float:
        """获取实际长度（考虑旋转）"""
        return self.width if self.rotated else self.length
    
    @property
    def actual_width(self) -> float:
        """获取实际宽度（考虑旋转）"""
        return self.length if self.rotated else self.width
    
    @property
    def area(self) -> float:
        """获取箱子面积"""
        return self.length * self.width
    
    @property
    def center_x(self) -> float:
        """获取箱子中心X坐标"""
        return self.x + self.actual_length / 2
    
    @property
    def center_y(self) -> float:
        """获取箱子中心Y坐标"""
        return self.y + self.actual_width / 2
    
    def get_bounds(self) -> Tuple[float, float, float, float]:
        """获取箱子边界 (x1, y1, x2, y2)"""
        return (
            self.x,
            self.y,
            self.x + self.actual_length,
            self.y + self.actual_width
        )
    
    def overlaps_with(self, other: 'Box') -> bool:
        """检查是否与另一个箱子重叠"""
        x1, y1, x2, y2 = self.get_bounds()
        ox1, oy1, ox2, oy2 = other.get_bounds()
        
        return not (x2 <= ox1 or x1 >= ox2 or y2 <= oy1 or y1 >= oy2)
    
    def can_rotate(self) -> bool:
        """检查是否可以旋转"""
        return True  # 默认所有箱子都可以旋转
    
    def rotate(self) -> None:
        """旋转箱子90度"""
        if self.can_rotate():
            self.rotated = not self.rotated
    
    def move_to(self, x: float, y: float) -> None:
        """移动箱子到指定位置"""
        self.x = x
        self.y = y
    
    def __str__(self) -> str:
        return f"Box({self.id}, {self.length}x{self.width}, {self.weight}kg)"