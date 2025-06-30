#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics import renderPDF
from datetime import datetime
from typing import List
import os

from core.container import Container
from core.box import Box

class PDFGenerator:
    """PDF报告生成器"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """设置自定义样式"""
        # 标题样式
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Title'],
            fontSize=18,
            spaceAfter=20,
            alignment=1,  # 居中
            textColor=colors.darkblue
        )
        
        # 章节标题样式
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.darkblue
        )
        
        # 正文样式
        self.body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6
        )
    
    def generate_report(self, containers: List[Container], output_path: str, 
                       include_visualization: bool = True) -> bool:
        """
        生成PDF报告
        
        Args:
            containers: 集装箱列表
            output_path: 输出文件路径
            include_visualization: 是否包含可视化图表
            
        Returns:
            bool: 生成是否成功
        """
        try:
            # 创建PDF文档
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=20*mm,
                leftMargin=20*mm,
                topMargin=20*mm,
                bottomMargin=20*mm
            )
            
            # 构建内容
            story = []
            
            # 添加标题页
            self.add_title_page(story)
            
            # 添加概览
            self.add_overview(story, containers)
            
            # 为每个集装箱生成详细报告
            for i, container in enumerate(containers):
                if i > 0:
                    story.append(PageBreak())
                self.add_container_report(story, container, include_visualization)
            
            # 添加总结
            self.add_summary(story, containers)
            
            # 生成PDF
            doc.build(story)
            return True
            
        except Exception as e:
            print(f"生成PDF报告时出错: {str(e)}")
            return False
    
    def add_title_page(self, story: List):
        """添加标题页"""
        # 主标题
        title = Paragraph("集装箱装载管理系统报告", self.title_style)
        story.append(title)
        story.append(Spacer(1, 20*mm))
        
        # 生成时间
        now = datetime.now()
        time_text = f"生成时间: {now.strftime('%Y年%m月%d日 %H:%M:%S')}"
        time_para = Paragraph(time_text, self.body_style)
        story.append(time_para)
        story.append(Spacer(1, 10*mm))
        
        # 系统信息
        system_info = [
            "系统版本: 1.0.0",
            "报告类型: 装载方案分析报告",
            "生成方式: 自动生成"
        ]
        
        for info in system_info:
            story.append(Paragraph(info, self.body_style))
        
        story.append(PageBreak())
    
    def add_overview(self, story: List, containers: List[Container]):
        """添加概览"""
        story.append(Paragraph("项目概览", self.heading_style))
        
        # 统计信息
        total_containers = len(containers)
        total_boxes = sum(len(container.boxes) for container in containers)
        total_weight = sum(container.total_weight for container in containers)
        avg_utilization = sum(container.area_utilization for container in containers) / len(containers) if containers else 0
        
        overview_data = [
            ["指标", "数值"],
            ["集装箱总数", f"{total_containers}"],
            ["箱子总数", f"{total_boxes}"],
            ["总重量", f"{total_weight:.1f} kg"],
            ["平均空间利用率", f"{avg_utilization*100:.1f}%"]
        ]
        
        overview_table = Table(overview_data, colWidths=[80*mm, 60*mm])
        overview_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(overview_table)
        story.append(Spacer(1, 20*mm))
    
    def add_container_report(self, story: List, container: Container, include_visualization: bool):
        """添加单个集装箱报告"""
        # 集装箱标题
        title = f"集装箱报告 - {container.name}"
        story.append(Paragraph(title, self.heading_style))
        
        # 基本信息
        basic_info = [
            ["属性", "值"],
            ["名称", container.name],
            ["尺寸", f"{container.length/1000:.1f}m × {container.width/1000:.1f}m"],
            ["总面积", f"{container.area/1000000:.2f} m²"],
            ["箱子数量", f"{len(container.boxes)}"],
            ["总重量", f"{container.total_weight:.1f} kg"],
            ["空间利用率", f"{container.area_utilization*100:.1f}%"]
        ]
        
        basic_table = Table(basic_info, colWidths=[60*mm, 80*mm])
        basic_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(basic_table)
        story.append(Spacer(1, 10*mm))
        
        # 重量平衡分析
        self.add_weight_balance_analysis(story, container)
        
        # 箱子清单
        if container.boxes:
            self.add_box_list(story, container.boxes)
        
        # 可视化图表（如果需要）
        if include_visualization:
            self.add_container_visualization(story, container)
    
    def add_weight_balance_analysis(self, story: List, container: Container):
        """添加重量平衡分析"""
        story.append(Paragraph("重量平衡分析", self.heading_style))
        
        balance_info = container.calculate_weight_balance()
        
        # 创建平衡分析表格
        balance_data = [
            ["项目", "数值", "状态"],
            ["左侧重量", f"{balance_info['left_weight']:.1f} kg", ""],
            ["右侧重量", f"{balance_info['right_weight']:.1f} kg", ""],
            ["左右重量差", f"{balance_info['lr_diff']:.1f} kg", 
             "正常" if balance_info['lr_diff'] < 500 else "超限"],
            ["前部重量", f"{balance_info['front_weight']:.1f} kg", ""],
            ["后部重量", f"{balance_info['rear_weight']:.1f} kg", ""],
            ["前后重量差", f"{balance_info['fr_diff']:.1f} kg", 
             "正常" if balance_info['fr_diff'] < 2000 else "超限"],
            ["重心位置", f"({balance_info['center_x']/1000:.2f}m, {balance_info['center_y']/1000:.2f}m)", ""],
            ["整体平衡", "", "平衡" if balance_info['is_balanced'] else "不平衡"]
        ]
        
        balance_table = Table(balance_data, colWidths=[50*mm, 50*mm, 40*mm])
        balance_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            # 为超限项目设置红色背景
            ('BACKGROUND', (2, 3), (2, 3), colors.red if balance_info['lr_diff'] >= 500 else colors.lightgreen),
            ('BACKGROUND', (2, 6), (2, 6), colors.red if balance_info['fr_diff'] >= 2000 else colors.lightgreen),
            ('BACKGROUND', (2, -1), (2, -1), colors.lightgreen if balance_info['is_balanced'] else colors.red),
        ]))
        
        story.append(balance_table)
        story.append(Spacer(1, 10*mm))
    
    def add_box_list(self, story: List, boxes: List[Box]):
        """添加箱子清单"""
        story.append(Paragraph("箱子装载清单", self.heading_style))
        
        # 创建箱子列表表格
        box_data = [["序号", "箱号", "尺寸(长×宽)", "重量", "位置(X,Y)", "是否旋转"]]
        
        for i, box in enumerate(boxes, 1):
            box_data.append([
                str(i),
                box.id,
                f"{box.length}×{box.width}mm",
                f"{box.weight:.1f}kg",
                f"({box.x:.0f}, {box.y:.0f})",
                "是" if box.rotated else "否"
            ])
        
        box_table = Table(box_data, colWidths=[15*mm, 25*mm, 35*mm, 25*mm, 30*mm, 20*mm])
        box_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(box_table)
        story.append(Spacer(1, 15*mm))
    
    def add_container_visualization(self, story: List, container: Container):
        """添加集装箱可视化"""
        story.append(Paragraph("装载布局图", self.heading_style))
        
        # 创建绘图
        drawing = Drawing(400, 300)
        
        # 计算缩放比例
        scale_x = 380 / container.length
        scale_y = 280 / container.width
        scale = min(scale_x, scale_y)
        
        # 绘制集装箱边界
        container_width = container.length * scale
        container_height = container.width * scale
        
        # 居中
        offset_x = (400 - container_width) / 2
        offset_y = (300 - container_height) / 2
        
        # 集装箱外框
        drawing.add(Rect(offset_x, offset_y, container_width, container_height,
                        strokeColor=colors.black, strokeWidth=2, fillColor=colors.white))
        
        # 绘制箱子
        colors_list = [colors.red, colors.blue, colors.green, colors.orange, 
                      colors.purple, colors.brown, colors.pink, colors.grey]
        
        for i, box in enumerate(container.boxes):
            box_x = offset_x + box.x * scale
            box_y = offset_y + box.y * scale
            box_width = box.actual_length * scale
            box_height = box.actual_width * scale
            
            # 选择颜色
            color = colors_list[i % len(colors_list)]
            
            # 绘制箱子
            drawing.add(Rect(box_x, box_y, box_width, box_height,
                           strokeColor=colors.black, strokeWidth=1, fillColor=color))
            
            # 添加箱号标签（如果空间足够）
            if box_width > 20 and box_height > 15:
                text_x = box_x + box_width / 2
                text_y = box_y + box_height / 2
                drawing.add(String(text_x, text_y, box.id, 
                                 textAnchor='middle', fontSize=6))
        
        story.append(drawing)
        story.append(Spacer(1, 10*mm))
    
    def add_summary(self, story: List, containers: List[Container]):
        """添加总结"""
        story.append(PageBreak())
        story.append(Paragraph("装载方案总结", self.heading_style))
        
        # 计算整体统计
        total_boxes = sum(len(container.boxes) for container in containers)
        total_weight = sum(container.total_weight for container in containers)
        avg_utilization = sum(container.area_utilization for container in containers) / len(containers) if containers else 0
        
        # 分析每个集装箱的平衡状态
        balanced_containers = sum(1 for container in containers 
                                if container.calculate_weight_balance()['is_balanced'])
        
        summary_text = f"""
        <b>装载方案总结:</b><br/>
        • 共使用 {len(containers)} 个集装箱<br/>
        • 装载箱子总数: {total_boxes} 个<br/>
        • 总重量: {total_weight:.1f} kg<br/>
        • 平均空间利用率: {avg_utilization*100:.1f}%<br/>
        • 重量平衡的集装箱: {balanced_containers}/{len(containers)} 个<br/>
        <br/>
        <b>建议:</b><br/>
        """
        
        # 根据情况添加建议
        if avg_utilization < 0.7:
            summary_text += "• 空间利用率偏低，建议优化箱子布局以提高效率<br/>"
        elif avg_utilization > 0.9:
            summary_text += "• 空间利用率很高，装载方案良好<br/>"
        
        if balanced_containers < len(containers):
            summary_text += "• 部分集装箱重量分布不平衡，建议调整箱子位置<br/>"
        else:
            summary_text += "• 所有集装箱重量分布均衡，符合运输要求<br/>"
        
        summary_text += f"<br/>报告生成完成。生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        story.append(Paragraph(summary_text, self.body_style))
    
    def generate_simple_report(self, container: Container, output_path: str) -> bool:
        """生成简化版报告（单个集装箱）"""
        try:
            doc = SimpleDocTemplate(output_path, pagesize=A4)
            story = []
            
            # 标题
            title = Paragraph(f"集装箱装载报告 - {container.name}", self.title_style)
            story.append(title)
            story.append(Spacer(1, 20*mm))
            
            # 基本信息和详细分析
            self.add_container_report(story, container, True)
            
            doc.build(story)
            return True
            
        except Exception as e:
            print(f"生成简化报告时出错: {str(e)}")
            return False