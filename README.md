# 股票 EMA 技术分析工具

这是一个基于 Python 的股票技术分析工具，专注于指数移动平均线（EMA）分析和其他技术指标。该工具可以帮助您跟踪和分析多支股票的技术走势，生成详细的分析报告和可视化图表。

## 功能特点

- 多股票同时分析
- EMA（指数移动平均线）交叉检测
- RSI（相对强弱指数）分析
- 价格趋势分析
- 自动警报系统
- 详细的分析报告（支持中文）
- 技术指标可视化
- 完全可配置的参数

## 安装要求

确保您的系统已安装以下依赖：

```bash
pip install yfinance pandas matplotlib pyyaml
```

## 项目结构

```
EMA/
├── ema.py           # 主程序文件
├── config.yaml      # 配置文件
├── output/          # 输出目录
│   └── YYYYMMDD_HHMMSS/  # 按时间戳组织的输出文件
│       ├── XXX_full_analysis.csv
│       ├── XXX_alerts.csv
│       ├── XXX_analysis_plot.png
│       └── XXX_report.md
└── README.md        # 项目文档
```

## 快速开始

1. 克隆或下载项目到本地
2. 安装所需依赖
3. 运行分析程序：
   ```bash
   python ema.py
   ```

## 配置文件说明

配置文件 `config.yaml` 包含所有可自定义的参数：

```yaml
# 股票列表配置
stocks:
  - AAPL   # 苹果
  - MSFT   # 微软
  # 添加更多股票...

# 分析设置
analysis:
  # 回溯时间（天）
  lookback_days: 365
  
  # RSI 设置
  rsi:
    period: 14
    oversold_threshold: 30    # 超卖阈值
    overbought_threshold: 70  # 超买阈值
  
  # EMA 周期设置
  ema_periods:
    short_term: [5, 10, 20]   # 短期均线
    medium_term: [50, 60]     # 中期均线
    long_term: [120, 200]     # 长期均线

# 输出设置
output:
  # 图表设置
  plot:
    figure_size: [15, 8]  # 图表尺寸
    dpi: 300             # 图表分辨率
```

### 配置项说明

1. **股票列表**
   - 在 `stocks` 下添加或删除股票代码
   - 使用标准的股票代码格式（如 AAPL, GOOGL 等）

2. **分析设置**
   - `lookback_days`: 历史数据回溯天数
   - `rsi`: RSI 相关设置
     - `period`: RSI 计算周期
     - `oversold_threshold`: 超卖阈值
     - `overbought_threshold`: 超买阈值
   - `ema_periods`: EMA 均线周期设置
     - `short_term`: 短期均线周期
     - `medium_term`: 中期均线周期
     - `long_term`: 长期均线周期

3. **输出设置**
   - `plot`: 图表相关设置
     - `figure_size`: 图表尺寸 [宽, 高]
     - `dpi`: 图表分辨率

## 输出文件说明

每次运行程序会在 `output` 目录下创建一个以时间戳命名的新目录，包含以下文件：

1. **完整分析数据** (`XXX_full_analysis.csv`)
   - 包含所有技术指标的详细数据
   - 价格、均线、RSI 等完整历史数据

2. **警报数据** (`XXX_alerts.csv`)
   - 仅在触发警报时生成
   - 记录所有警报触发的具体时间和原因

3. **分析图表** (`XXX_analysis_plot.png`)
   - 价格和均线可视化
   - 包含所有 EMA 线
   - 标记警报点位

4. **分析报告** (`XXX_report.md`)
   - 当前市场状况总结
   - 技术指标分析
   - 警报信息（如果有）
   - EMA 交叉分析

## 使用技巧

1. **添加新股票**
   - 直接在 `config.yaml` 的 `stocks` 列表中添加股票代码
   - 确保使用正确的股票代码格式

2. **调整技术指标**
   - 修改 `config.yaml` 中的相应参数
   - RSI 参数调整可能影响信号灵敏度
   - EMA 周期可根据交易策略调整

3. **自定义输出**
   - 可以修改图表尺寸和分辨率
   - 文件名格式可在配置文件中调整

## 警报系统

程序会在以下情况触发警报：

1. 价格下跌并低于短期均线
2. RSI 进入超买或超卖区域
3. 出现 EMA 金叉或死叉

## 注意事项

1. 数据依赖于 Yahoo Finance API
2. 建议在美股交易时间运行以获取最新数据
3. 首次运行可能需要下载较多历史数据
4. 确保网络连接稳定

## 未来改进计划

1. 添加更多技术指标
2. 实现实时监控功能
3. 添加回测功能
4. 支持更多数据源
5. 开发 Web 界面

## 常见问题

1. **运行错误**
   - 检查网络连接
   - 确认股票代码正确
   - 验证依赖包已正确安装

2. **数据不完整**
   - 可能是由于市场休市
   - 检查股票是否已退市或更改代码
   - 尝试调整回溯时间范围

3. **警报过多**
   - 调整 RSI 阈值
   - 修改警报触发条件
   - 考虑增加过滤条件

## 贡献指南

欢迎提交改进建议和 bug 报告。如果您想贡献代码：

1. Fork 项目
2. 创建新分支
3. 提交更改
4. 发起 Pull Request

## 许可证

MIT License
