#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from typing import List, Dict, Any, Tuple
from datetime import datetime
from pathlib import Path

from core.container import Container
from core.box import Box

class ProjectManager:
    """项目管理器 - 负责项目的保存和加载"""
    
    def __init__(self):
        self.project_version = "1.0"
    
    def save_project(self, containers: List[Container], pending_boxes: List[Box], 
                    file_path: str, project_name: str = None) -> bool:
        """
        保存项目到JSON文件
        
        Args:
            containers: 集装箱列表
            pending_boxes: 待装载箱子列表
            file_path: 保存文件路径
            project_name: 项目名称
            
        Returns:
            bool: 保存是否成功
        """
        try:
            # 准备项目数据
            project_data = {
                "project_info": {
                    "name": project_name or "未命名项目",
                    "version": self.project_version,
                    "created_time": datetime.now().isoformat(),
                    "description": "集装箱装载管理系统项目文件"
                },
                "containers": [],
                "pending_boxes": []
            }
            
            # 序列化集装箱数据
            for container in containers:
                container_data = {
                    "name": container.name,
                    "length": container.length,
                    "width": container.width,
                    "boxes": []
                }
                
                # 序列化箱子数据
                for box in container.boxes:
                    box_data = {
                        "id": box.id,
                        "length": box.length,
                        "width": box.width,
                        "weight": box.weight,
                        "height": box.height,
                        "x": box.x,
                        "y": box.y,
                        "rotated": box.rotated
                    }
                    container_data["boxes"].append(box_data)
                
                project_data["containers"].append(container_data)
            
            # 序列化待装载箱子数据
            for box in pending_boxes:
                box_data = {
                    "id": box.id,
                    "length": box.length,
                    "width": box.width,
                    "weight": box.weight,
                    "height": box.height,
                    "x": box.x,
                    "y": box.y,
                    "rotated": box.rotated
                }
                project_data["pending_boxes"].append(box_data)
            
            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            print(f"保存项目时出错: {str(e)}")
            return False
    
    def load_project(self, file_path: str) -> Tuple[bool, List[Container], List[Box], Dict[str, Any]]:
        """
        从JSON文件加载项目
        
        Args:
            file_path: 项目文件路径
            
        Returns:
            Tuple[bool, List[Container], List[Box], Dict]: 
            (成功标志, 集装箱列表, 待装载箱子列表, 项目信息)
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                print(f"项目文件不存在: {file_path}")
                return False, [], [], {}
            
            # 读取文件
            with open(file_path, 'r', encoding='utf-8') as f:
                project_data = json.load(f)
            
            # 验证项目文件格式
            if not self.validate_project_data(project_data):
                print("项目文件格式无效")
                return False, [], [], {}
            
            containers = []
            pending_boxes = []
            
            # 加载集装箱数据
            for container_data in project_data.get("containers", []):
                container = Container(
                    name=container_data.get("name", "集装箱"),
                    length=container_data.get("length", Container.DEFAULT_LENGTH),
                    width=container_data.get("width", Container.DEFAULT_WIDTH)
                )
                
                # 加载箱子数据
                for box_data in container_data.get("boxes", []):
                    box = self.create_box_from_data(box_data)
                    if box:
                        container.add_box(box)
                
                containers.append(container)
            
            # 加载待装载箱子数据
            for box_data in project_data.get("pending_boxes", []):
                box = self.create_box_from_data(box_data)
                if box:
                    pending_boxes.append(box)
            
            project_info = project_data.get("project_info", {})
            
            return True, containers, pending_boxes, project_info
            
        except Exception as e:
            print(f"加载项目时出错: {str(e)}")
            return False, [], [], {}
    
    def create_box_from_data(self, box_data: Dict[str, Any]) -> Box:
        """从数据字典创建Box对象"""
        try:
            box = Box(
                id=box_data.get("id", ""),
                length=box_data.get("length", 0),
                width=box_data.get("width", 0),
                weight=box_data.get("weight", 0),
                height=box_data.get("height")
            )
            
            # 设置位置和旋转状态
            box.x = box_data.get("x", 0)
            box.y = box_data.get("y", 0)
            box.rotated = box_data.get("rotated", False)
            
            return box
            
        except Exception as e:
            print(f"创建箱子对象时出错: {str(e)}")
            return None
    
    def validate_project_data(self, project_data: Dict[str, Any]) -> bool:
        """验证项目数据格式"""
        try:
            # 检查必需的顶级字段
            required_fields = ["project_info", "containers", "pending_boxes"]
            for field in required_fields:
                if field not in project_data:
                    return False
            
            # 检查项目信息
            project_info = project_data["project_info"]
            if not isinstance(project_info, dict):
                return False
            
            # 检查集装箱数据
            containers = project_data["containers"]
            if not isinstance(containers, list):
                return False
            
            for container in containers:
                if not isinstance(container, dict):
                    return False
                if "name" not in container or "boxes" not in container:
                    return False
                if not isinstance(container["boxes"], list):
                    return False
            
            # 检查待装载箱子数据
            pending_boxes = project_data["pending_boxes"]
            if not isinstance(pending_boxes, list):
                return False
            
            return True
            
        except Exception:
            return False
    
    def export_to_excel(self, containers: List[Container], file_path: str) -> bool:
        """导出数据到Excel文件"""
        try:
            import pandas as pd
            
            # 准备数据
            all_boxes_data = []
            
            for container in containers:
                for box in container.boxes:
                    box_data = {
                        "集装箱": container.name,
                        "箱号": box.id,
                        "长度": box.length,
                        "宽度": box.width,
                        "重量": box.weight,
                        "高度": box.height or "",
                        "X坐标": box.x,
                        "Y坐标": box.y,
                        "是否旋转": "是" if box.rotated else "否"
                    }
                    all_boxes_data.append(box_data)
            
            # 创建DataFrame
            df = pd.DataFrame(all_boxes_data)
            
            # 保存到Excel
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                # 装载清单工作表
                df.to_excel(writer, sheet_name='装载清单', index=False)
                
                # 集装箱统计工作表
                container_stats = []
                for container in containers:
                    balance_info = container.calculate_weight_balance()
                    stats = {
                        "集装箱名称": container.name,
                        "尺寸": f"{container.length/1000:.1f}m × {container.width/1000:.1f}m",
                        "箱子数量": len(container.boxes),
                        "总重量": container.total_weight,
                        "空间利用率": f"{container.area_utilization*100:.1f}%",
                        "左右重量差": balance_info['lr_diff'],
                        "前后重量差": balance_info['fr_diff'],
                        "是否平衡": "是" if balance_info['is_balanced'] else "否"
                    }
                    container_stats.append(stats)
                
                stats_df = pd.DataFrame(container_stats)
                stats_df.to_excel(writer, sheet_name='集装箱统计', index=False)
            
            return True
            
        except Exception as e:
            print(f"导出Excel时出错: {str(e)}")
            return False
    
    def get_recent_projects(self, max_count: int = 10) -> List[Dict[str, str]]:
        """获取最近打开的项目列表"""
        # 这里可以实现最近项目的管理
        # 现在返回空列表
        return []
    
    def add_to_recent_projects(self, file_path: str, project_name: str):
        """添加到最近项目列表"""
        # 这里可以实现最近项目的记录
        pass
    
    def auto_save(self, containers: List[Container], pending_boxes: List[Box], 
                  project_name: str = None) -> bool:
        """自动保存项目"""
        try:
            # 创建自动保存目录
            auto_save_dir = Path.home() / ".container_loader" / "auto_save"
            auto_save_dir.mkdir(parents=True, exist_ok=True)
            
            # 生成自动保存文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"auto_save_{timestamp}.json"
            file_path = auto_save_dir / file_name
            
            # 保存项目
            success = self.save_project(containers, pending_boxes, str(file_path), 
                                      project_name or "自动保存")
            
            if success:
                # 清理旧的自动保存文件（保留最近10个）
                self.cleanup_auto_saves(auto_save_dir, keep_count=10)
            
            return success
            
        except Exception as e:
            print(f"自动保存时出错: {str(e)}")
            return False
    
    def cleanup_auto_saves(self, auto_save_dir: Path, keep_count: int = 10):
        """清理旧的自动保存文件"""
        try:
            # 获取所有自动保存文件
            auto_save_files = list(auto_save_dir.glob("auto_save_*.json"))
            
            # 按修改时间排序
            auto_save_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            
            # 删除多余的文件
            for file_to_delete in auto_save_files[keep_count:]:
                file_to_delete.unlink()
                
        except Exception as e:
            print(f"清理自动保存文件时出错: {str(e)}")