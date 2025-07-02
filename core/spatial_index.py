#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List, Set, Tuple, Optional
from dataclasses import dataclass
import math

@dataclass
class BoundingBox:
    """边界框"""
    x1: float
    y1: float
    x2: float
    y2: float
    
    def intersects(self, other: 'BoundingBox') -> bool:
        """检查是否相交"""
        return not (self.x2 <= other.x1 or self.x1 >= other.x2 or 
                   self.y2 <= other.y1 or self.y1 >= other.y2)
    
    def contains_point(self, x: float, y: float) -> bool:
        """检查是否包含点"""
        return self.x1 <= x <= self.x2 and self.y1 <= y <= self.y2

class SpatialGrid:
    """空间网格索引，用于加速碰撞检测"""
    
    def __init__(self, width: float, height: float, cell_size: float = 1000):
        """
        初始化空间网格
        
        Args:
            width: 容器宽度
            height: 容器高度
            cell_size: 网格单元大小（默认1000mm = 1m）
        """
        self.width = width
        self.height = height
        self.cell_size = cell_size
        
        # 计算网格尺寸
        self.cols = math.ceil(width / cell_size)
        self.rows = math.ceil(height / cell_size)
        
        # 初始化网格（每个单元格存储一组对象）
        self.grid = [[set() for _ in range(self.cols)] for _ in range(self.rows)]
        
        # 对象到网格单元的映射
        self.object_cells = {}
    
    def _get_cells(self, bbox: BoundingBox) -> List[Tuple[int, int]]:
        """获取边界框覆盖的所有网格单元"""
        col_start = max(0, int(bbox.x1 // self.cell_size))
        col_end = min(self.cols - 1, int(bbox.x2 // self.cell_size))
        row_start = max(0, int(bbox.y1 // self.cell_size))
        row_end = min(self.rows - 1, int(bbox.y2 // self.cell_size))
        
        cells = []
        for row in range(row_start, row_end + 1):
            for col in range(col_start, col_end + 1):
                cells.append((row, col))
        return cells
    
    def insert(self, obj, bbox: BoundingBox):
        """插入对象"""
        cells = self._get_cells(bbox)
        self.object_cells[obj] = cells
        
        for row, col in cells:
            self.grid[row][col].add(obj)
    
    def remove(self, obj):
        """移除对象"""
        if obj in self.object_cells:
            cells = self.object_cells[obj]
            for row, col in cells:
                self.grid[row][col].discard(obj)
            del self.object_cells[obj]
    
    def update(self, obj, new_bbox: BoundingBox):
        """更新对象位置"""
        self.remove(obj)
        self.insert(obj, new_bbox)
    
    def query(self, bbox: BoundingBox) -> Set:
        """查询可能与给定边界框相交的对象"""
        cells = self._get_cells(bbox)
        candidates = set()
        
        for row, col in cells:
            candidates.update(self.grid[row][col])
        
        return candidates
    
    def get_nearby_objects(self, obj, distance: float) -> Set:
        """获取指定距离内的对象"""
        if obj not in self.object_cells:
            return set()
        
        # 获取对象当前位置的网格单元
        cells = self.object_cells[obj]
        if not cells:
            return set()
        
        # 计算需要检查的网格范围
        cell_distance = math.ceil(distance / self.cell_size)
        
        nearby = set()
        for row, col in cells:
            for dr in range(-cell_distance, cell_distance + 1):
                for dc in range(-cell_distance, cell_distance + 1):
                    nr, nc = row + dr, col + dc
                    if 0 <= nr < self.rows and 0 <= nc < self.cols:
                        nearby.update(self.grid[nr][nc])
        
        nearby.discard(obj)  # 移除自身
        return nearby
    
    def clear(self):
        """清空索引"""
        for row in self.grid:
            for cell in row:
                cell.clear()
        self.object_cells.clear()