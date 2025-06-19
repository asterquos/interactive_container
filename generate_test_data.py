#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
生成测试数据Excel文件
"""

import pandas as pd
import random
from pathlib import Path

def generate_test_data():
    """生成测试用的Excel数据文件"""
    
    # 创建测试数据目录
    test_dir = Path("test_data")
    test_dir.mkdir(exist_ok=True)
    
    # 生成基础测试数据
    basic_data = {
        "箱号": [f"BOX{i:03d}" for i in range(1, 21)],
        "长度": [random.randint(800, 1500) for _ in range(20)],
        "宽度": [random.randint(600, 1000) for _ in range(20)],
        "重量": [random.randint(200, 800) for _ in range(20)]
    }
    
    # 保存基础测试数据
    basic_df = pd.DataFrame(basic_data)
    basic_file = test_dir / "basic_test_data.xlsx"
    basic_df.to_excel(basic_file, index=False)
    print(f"✅ 生成基础测试数据: {basic_file}")
    
    # 生成英文字段测试数据
    english_data = {
        "ID": [f"CONT{i:03d}" for i in range(1, 16)],
        "Length": [random.randint(900, 1400) for _ in range(15)],
        "Width": [random.randint(700, 1200) for _ in range(15)],
        "Weight": [random.randint(300, 900) for _ in range(15)],
        "Height": [random.randint(1800, 2400) for _ in range(15)]
    }
    
    english_df = pd.DataFrame(english_data)
    english_file = test_dir / "english_test_data.xlsx"
    english_df.to_excel(english_file, index=False)
    print(f"✅ 生成英文字段测试数据: {english_file}")
    
    # 生成多工作表测试数据
    with pd.ExcelWriter(test_dir / "multi_sheet_test_data.xlsx") as writer:
        # 第一个工作表：标准货物
        standard_data = {
            "箱号": [f"STD{i:03d}" for i in range(1, 11)],
            "长": [1200] * 10,  # 标准尺寸
            "宽": [800] * 10,
            "重量": [random.randint(400, 600) for _ in range(10)]
        }
        pd.DataFrame(standard_data).to_excel(writer, sheet_name="标准货物", index=False)
        
        # 第二个工作表：大件货物
        large_data = {
            "编号": [f"LARGE{i:02d}" for i in range(1, 6)],
            "长度": [random.randint(1400, 1600) for _ in range(5)],
            "宽度": [random.randint(1000, 1200) for _ in range(5)],
            "重量": [random.randint(700, 1000) for _ in range(5)]
        }
        pd.DataFrame(large_data).to_excel(writer, sheet_name="大件货物", index=False)
        
        # 第三个工作表：轻货
        light_data = {
            "箱号": [f"LIGHT{i:02d}" for i in range(1, 8)],
            "长度": [random.randint(800, 1200) for _ in range(7)],
            "宽度": [random.randint(600, 900) for _ in range(7)],
            "重量": [random.randint(100, 300) for _ in range(7)]
        }
        pd.DataFrame(light_data).to_excel(writer, sheet_name="轻货", index=False)
    
    print(f"✅ 生成多工作表测试数据: {test_dir / 'multi_sheet_test_data.xlsx'}")
    
    # 生成带错误数据的测试文件
    error_data = {
        "箱号": ["ERR001", "ERR002", "", "ERR004", "ERR005"],
        "长度": [1000, "abc", 1200, 0, 1100],  # 包含无效数据
        "宽度": [800, 900, 1000, 800, ""],     # 包含空值
        "重量": [500, 600, 700, -100, 550]    # 包含负数
    }
    
    error_df = pd.DataFrame(error_data)
    error_file = test_dir / "error_test_data.xlsx"
    error_df.to_excel(error_file, index=False)
    print(f"✅ 生成带错误的测试数据: {error_file}")
    
    # 生成大数据量测试文件
    large_data = {
        "箱号": [f"BULK{i:04d}" for i in range(1, 101)],
        "长度": [random.randint(800, 1500) for _ in range(100)],
        "宽度": [random.randint(600, 1200) for _ in range(100)],
        "重量": [random.randint(200, 1000) for _ in range(100)],
        "高度": [random.randint(1800, 2500) for _ in range(100)]
    }
    
    large_df = pd.DataFrame(large_data)
    large_file = test_dir / "large_test_data.xlsx"
    large_df.to_excel(large_file, index=False)
    print(f"✅ 生成大数据量测试数据: {large_file} (100个箱子)")
    
    # 生成真实场景测试数据
    realistic_data = {
        "箱号": [
            "CONTAINER001", "CONTAINER002", "CONTAINER003", "CONTAINER004", "CONTAINER005",
            "CONTAINER006", "CONTAINER007", "CONTAINER008", "CONTAINER009", "CONTAINER010",
            "CONTAINER011", "CONTAINER012", "CONTAINER013", "CONTAINER014", "CONTAINER015"
        ],
        "长度": [1200, 1000, 1500, 800, 1100, 1300, 900, 1400, 1050, 1250, 1150, 1350, 950, 1450, 1080],
        "宽度": [800, 700, 1000, 600, 900, 850, 750, 1100, 780, 820, 880, 950, 720, 1050, 800],
        "重量": [520, 380, 690, 290, 560, 610, 420, 750, 480, 580, 540, 630, 410, 720, 500],
        "备注": [
            "标准货物", "轻货", "重货", "小件", "中等货物",
            "大件货物", "标准货物", "超重货物", "轻货", "标准货物",
            "中等货物", "重货", "轻货", "超重货物", "标准货物"
        ]
    }
    
    realistic_df = pd.DataFrame(realistic_data)
    realistic_file = test_dir / "realistic_test_data.xlsx"
    realistic_df.to_excel(realistic_file, index=False)
    print(f"✅ 生成真实场景测试数据: {realistic_file}")
    
    # 生成README文件说明测试数据
    readme_content = """# 测试数据说明

本目录包含了集装箱装载管理系统的测试数据文件：

## 文件列表

1. **basic_test_data.xlsx** - 基础测试数据（20个箱子）
   - 包含中文字段名：箱号、长度、宽度、重量
   - 适合基本功能测试

2. **english_test_data.xlsx** - 英文字段测试数据（15个箱子）
   - 包含英文字段名：ID、Length、Width、Weight、Height
   - 测试多语言字段识别功能

3. **multi_sheet_test_data.xlsx** - 多工作表测试数据
   - 包含3个工作表：标准货物、大件货物、轻货
   - 测试多工作表处理功能

4. **error_test_data.xlsx** - 错误数据测试（5个箱子）
   - 包含各种数据错误：空值、无效格式、负数等
   - 测试数据验证和错误处理功能

5. **large_test_data.xlsx** - 大数据量测试（100个箱子）
   - 测试系统在大量数据下的性能
   - 包含高度字段

6. **realistic_test_data.xlsx** - 真实场景测试数据（15个箱子）
   - 模拟真实的货物装载场景
   - 包含备注字段

## 使用方法

1. 启动集装箱装载管理系统
2. 点击"文件"菜单 → "导入Excel文件"
3. 选择相应的测试文件进行导入
4. 或者使用"测试"菜单 → "加载示例数据"加载内置测试数据

## 测试建议

- 从basic_test_data.xlsx开始测试基本功能
- 使用english_test_data.xlsx测试字段识别
- 使用error_test_data.xlsx测试错误处理
- 使用large_test_data.xlsx测试性能
- 使用realistic_test_data.xlsx进行完整场景测试
"""

    readme_file = test_dir / "README.md"
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"✅ 生成测试数据说明: {readme_file}")
    
    print(f"\n🎉 所有测试数据已生成完成！")
    print(f"📁 测试数据目录: {test_dir.absolute()}")
    print(f"📊 共生成 6 个测试Excel文件")

if __name__ == "__main__":
    generate_test_data()