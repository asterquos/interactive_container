# 测试数据说明

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
