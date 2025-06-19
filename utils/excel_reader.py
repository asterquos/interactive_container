#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from core.box import Box

class ExcelReader:
    """Excel文件读取器"""
    
    # 支持的文件格式
    SUPPORTED_FORMATS = ['.xlsx', '.xls']
    
    # 字段映射（中英文）
    FIELD_MAPPING = {
        # 中文字段名
        '箱号': 'id',
        'ID': 'id',
        'id': 'id',
        '编号': 'id',
        '长度': 'length',
        '长': 'length',
        'length': 'length',
        'Length': 'length',
        '宽度': 'width',
        '宽': 'width',
        'width': 'width',
        'Width': 'width',
        '重量': 'weight',
        'weight': 'weight',
        'Weight': 'weight',
        '高度': 'height',
        '高': 'height',
        'height': 'height',
        'Height': 'height',
    }
    
    def __init__(self):
        """初始化Excel读取器"""
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def read_excel(self, file_path: str, sheet_name: Optional[str] = None) -> Tuple[List[Box], List[str]]:
        """
        读取Excel文件并返回箱子列表
        
        Args:
            file_path: Excel文件路径
            sheet_name: 工作表名称，如果为None则读取第一个工作表
            
        Returns:
            (boxes_list, errors_list)
        """
        self.errors.clear()
        self.warnings.clear()
        
        file_path = Path(file_path)
        
        # 检查文件格式
        if file_path.suffix.lower() not in self.SUPPORTED_FORMATS:
            self.errors.append(f"不支持的文件格式: {file_path.suffix}")
            return [], self.errors
        
        # 检查文件是否存在
        if not file_path.exists():
            self.errors.append(f"文件不存在: {file_path}")
            return [], self.errors
        
        try:
            # 读取Excel文件
            if sheet_name:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
            else:
                df = pd.read_excel(file_path)
            
            # 预处理数据
            df = self._preprocess_dataframe(df)
            
            # 验证和转换数据
            boxes = self._convert_to_boxes(df)
            
            return boxes, self.errors
            
        except Exception as e:
            self.errors.append(f"读取Excel文件时出错: {str(e)}")
            return [], self.errors
    
    def get_sheet_names(self, file_path: str) -> List[str]:
        """获取Excel文件中的所有工作表名称"""
        try:
            excel_file = pd.ExcelFile(file_path)
            return excel_file.sheet_names
        except Exception as e:
            self.errors.append(f"获取工作表名称时出错: {str(e)}")
            return []
    
    def _preprocess_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """预处理DataFrame"""
        # 删除完全空白的行
        df = df.dropna(how='all')
        
        # 重置索引
        df = df.reset_index(drop=True)
        
        # 统一列名映射
        df = self._map_column_names(df)
        
        return df
    
    def _map_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """映射列名称"""
        new_columns = {}
        
        for col in df.columns:
            # 清理列名（去除空格和换行符）
            clean_col = str(col).strip().replace('\n', '').replace('\r', '')
            
            # 查找映射
            if clean_col in self.FIELD_MAPPING:
                new_columns[col] = self.FIELD_MAPPING[clean_col]
            else:
                # 尝试模糊匹配
                for key, value in self.FIELD_MAPPING.items():
                    if key.lower() in clean_col.lower():
                        new_columns[col] = value
                        break
        
        # 应用列名映射
        if new_columns:
            df = df.rename(columns=new_columns)
        
        return df
    
    def _convert_to_boxes(self, df: pd.DataFrame) -> List[Box]:
        """将DataFrame转换为Box对象列表"""
        boxes = []
        required_fields = ['id', 'length', 'width', 'weight']
        
        # 检查必需字段
        missing_fields = [field for field in required_fields if field not in df.columns]
        if missing_fields:
            self.errors.append(f"缺少必需字段: {', '.join(missing_fields)}")
            return []
        
        # 转换每一行数据
        for index, row in df.iterrows():
            try:
                # 验证必需字段
                box_data = {}
                for field in required_fields:
                    value = row[field]
                    if pd.isna(value) or value == '':
                        self.errors.append(f"行 {index + 1}: 字段 '{field}' 不能为空")
                        continue
                    box_data[field] = value
                
                # 如果必需字段有问题，跳过这一行
                if len(box_data) != len(required_fields):
                    continue
                
                # 数据类型转换和验证
                try:
                    box_id = str(box_data['id'])
                    length = float(box_data['length'])
                    width = float(box_data['width'])
                    weight = float(box_data['weight'])
                    
                    # 验证数值范围
                    if length <= 0 or width <= 0 or weight <= 0:
                        self.errors.append(f"行 {index + 1}: 长度、宽度和重量必须为正数")
                        continue
                    
                    # 处理可选字段
                    height = None
                    if 'height' in df.columns and not pd.isna(row['height']):
                        try:
                            height = float(row['height'])
                            if height <= 0:
                                self.warnings.append(f"行 {index + 1}: 高度必须为正数，已忽略")
                                height = None
                        except (ValueError, TypeError):
                            self.warnings.append(f"行 {index + 1}: 高度格式无效，已忽略")
                    
                    # 创建Box对象
                    box = Box(
                        id=box_id,
                        length=length,
                        width=width,
                        weight=weight,
                        height=height
                    )
                    
                    boxes.append(box)
                    
                except (ValueError, TypeError) as e:
                    self.errors.append(f"行 {index + 1}: 数据类型转换错误 - {str(e)}")
                    continue
                    
            except Exception as e:
                self.errors.append(f"行 {index + 1}: 处理数据时出错 - {str(e)}")
                continue
        
        return boxes
    
    def validate_data(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """验证数据完整性和正确性"""
        validation_result = {
            'errors': [],
            'warnings': [],
            'info': []
        }
        
        # 检查数据行数
        if len(df) == 0:
            validation_result['errors'].append("Excel文件中没有数据")
            return validation_result
        
        validation_result['info'].append(f"共找到 {len(df)} 行数据")
        
        # 检查必需字段
        required_fields = ['id', 'length', 'width', 'weight']
        for field in required_fields:
            if field not in df.columns:
                validation_result['errors'].append(f"缺少必需字段: {field}")
        
        # 检查数据质量
        for field in ['length', 'width', 'weight']:
            if field in df.columns:
                invalid_count = df[field].isna().sum()
                if invalid_count > 0:
                    validation_result['warnings'].append(f"字段 '{field}' 有 {invalid_count} 个无效值")
        
        return validation_result