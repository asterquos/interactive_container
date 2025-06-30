#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from core.box import Box

def get_sample_boxes():
    """获取示例箱子数据"""
    boxes = [
        Box("BOX001", 1200, 800, 450),
        Box("BOX002", 1000, 600, 320),
        Box("BOX003", 1500, 1000, 680),
        Box("BOX004", 800, 600, 280),
        Box("BOX005", 1100, 900, 520),
        Box("BOX006", 900, 700, 380),
        Box("BOX007", 1300, 800, 590),
        Box("BOX008", 700, 500, 240),
        Box("BOX009", 1400, 1100, 720),
        Box("BOX010", 950, 650, 410),
    ]
    return boxes