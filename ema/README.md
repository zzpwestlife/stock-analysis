# 股票 EMA 技术分析工具

这是一个基于 Python 的股票技术分析工具，专注于指数移动平均线（EMA）分析和其他技术指标。该工具可以帮助您跟踪和分析多支股票的技术走势，生成详细的分析报告和可视化图表。

## 功能特点

- **多股票同时分析**：批量处理多支股票数据
- **EMA（指数移动平均线）分析**：检测短、中、长期均线交叉信号
- **RSI（相对强弱指数）分析**：识别超买超卖状态
- **价格趋势分析**：确定市场走势方向和强度
- **自动警报系统**：提示重要市场事件和买卖机会
- **详细的分析报告**：HTML 和 Excel 格式，包含全面的分析数据
- **美观的技术指标可视化**：现代简约设计风格的图表
- **完全可配置的参数**：通过 YAML 文件灵活设置分析选项
- **Excel 表格条件格式化**：直观显示关键指标和状态
- **中英文双语支持**：支持中文和英文界面与报告

## 技术架构

本项目采用模块化设计，主要技术栈包括：

- **Python**：核心编程语言
- **Pandas**：数据处理和分析
- **Matplotlib**：数据可视化和图表生成
- **yfinance**：股票数据获取
- **PyYAML**：配置文件解析
- **openpyxl**：Excel 报表生成

系统通过分层架构实现数据获取、分析和可视化的分离，便于维护和扩展。

## 安装要求

确保您的系统已安装 Python 3.6 或更高版本，然后安装以下依赖：

```bash
pip install -r requirements.txt
```

或手动安装各个依赖：

```bash
pip install yfinance pandas matplotlib pyyaml openpyxl
```

## 项目结构

```
stock-ema/
├── ema.py           # 主程序文件
├── config.yaml      # 配置文件
├── utils/           # 工具模块
│   ├── alerts.py    # 警报生成
│   ├── analysis.py  # 技术分析
│   ├── config.py    # 配置加载
│   ├── constants.py # 常量定义
│   ├── report.py    # 报告生成
│   └── styles.py    # 样式定义
├── docs/            # 文档和示例
│   ├── examples/    # 示例报告
│   └── images/      # 示例图片
├── output/          # 输出目录
│   └── YYYYMMDD_HHMMSS/  # 按时间戳组织的输出文件
│       ├── analysis_results.html  # HTML 分析报告
│       ├── stock_analysis.xlsx    # Excel 分析报告
│       └── *_analysis_plot.png    # 技术分析图表
└── README.md        # 项目文档
```

## 快速开始

1. 克隆或下载项目到本地
   ```bash
   git clone https://github.com/yourusername/stock-ema.git
   cd stock-ema
   ```

2. 安装所需依赖
   ```bash
   pip install -r requirements.txt
   ```

3. 在 `config.yaml` 中配置需要分析的股票
   ```yaml
   stocks:
     - AAPL  # 苹果
     - MSFT  # 微软
     # 添加更多股票...
   ```

4. 运行分析程序
   ```bash
   python ema.py
   ```

5. 查看生成的报告
   ```bash
   # 生成的报告位于 output/[时间戳] 目录下
   ```

## 配置文件说明

配置文件 `config.yaml` 包含所有可自定义的参数：

```yaml
# 股票列表配置
stocks:
  - AAPL   # 苹果
  - MSFT   # 微软
  - GOOGL  # 谷歌
  - NVDA   # 英伟达
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
```

## 输出文件说明

每次运行程序会在 `output` 目录下创建一个以时间戳命名的新目录，包含以下文件：

1. **HTML 分析报告** (`analysis_results.html`)
   - 完整的技术分析结果
   - 包含交互式图表
   - 警报信息高亮显示
   - 移动设备友好的响应式设计

2. **Excel 分析报告** (`stock_analysis.xlsx`)
   - 概览表：所有股票的当前状态
     - 价格和涨跌幅（红绿色标注）
     - RSI 值（超买超卖状态标注）
     - 警报数量（橙色标注）
   - 详细数据表：每支股票的历史数据
     - 所有技术指标的完整数据
     - RSI 超买超卖状态标注
     - 数据保留两位小数

3. **技术分析图表** (`*_analysis_plot.png`)
   - 清晰的价格和均线走势
   - 完整的图例说明
   - RSI 指标和超买超卖线
   - 优化的日期显示

## 技术指标详解

### 1. EMA（指数移动平均线）

EMA 是一种给予近期数据更高权重的移动平均线，相比简单移动平均线 (SMA) 对价格变化的反应更为敏感。

**计算方法**：
EMA = 当日收盘价 × K + 昨日 EMA × (1 - K)
其中 K = 2 ÷ (周期数 + 1)

**系统内使用的 EMA 周期**：
- 短期：5、10、20 日（反映短期趋势）
- 中期：50、60 日（反映中期趋势）
- 长期：120、200 日（反映长期趋势）

**应用场景**：
- **均线交叉**：短期均线上穿长期均线形成"金叉"（买入信号）；下穿形成"死叉"（卖出信号）
- **趋势确认**：价格站在均线上方表示上升趋势；站在均线下方表示下降趋势
- **支撑/阻力位**：重要 EMA 线常作为价格支撑或阻力水平

### 2. RSI（相对强弱指数）

RSI 可测量价格变化的速度和幅度，用于判断市场是否超买或超卖。

**计算方法**：
RSI = 100 - [100 ÷ (1 + RS)]
其中 RS = n 日内上涨幅度的平均值 ÷ n 日内下跌幅度的平均值

**系统设置**：
- 默认周期：14 日
- 超买水平：70（表示可能即将下跌）
- 超卖水平：30（表示可能即将上涨）

**应用场景**：
- **超买/超卖判断**：RSI > 70 考虑卖出；RSI < 30 考虑买入
- **背离识别**：价格创新高而 RSI 未创新高（顶背离）；价格创新低而 RSI 未创新低（底背离）
- **中性区域**：RSI 在 30-70 之间表示市场处于中性状态

### 3. MACD（移动平均汇聚/发散）

MACD 是通过比较两条移动平均线的差值来显示价格动量变化的技术指标（未来增强版本中实现）。

**计算方法**：
- MACD 线 = 12 日 EMA - 26 日 EMA
- 信号线 = MACD 线的 9 日 EMA
- 柱状图 = MACD 线 - 信号线

**应用场景**：
- **金叉与死叉**：MACD 线上穿信号线为买入信号；下穿为卖出信号
- **零轴分析**：MACD 线在零轴上方表示上升趋势；在零轴下方表示下降趋势
- **背离分析**：价格与 MACD 柱状图的方向不一致时，可能预示趋势反转

## 警报系统

系统会在以下情况触发警报：

1. **均线相关**
   - 金叉（短期均线向上穿过长期均线）
   - 死叉（短期均线向下穿过长期均线）
   - 价格突破重要均线

2. **RSI 相关**
   - 进入超买区域（>70）
   - 进入超卖区域（<30）
   - 背离信号（价格新高/低但 RSI 未确认）

3. **价格相关**
   - 突破重要价位
   - 跌破支撑位
   - 突破阻力位

## 使用技巧

1. **分析多支股票**
   - 在 `config.yaml` 中添加股票代码
   - 支持同时分析数十支股票
   - 注意网络状况和 API 限制

2. **解读分析报告**
   - HTML 报告适合整体分析和查看可视化图表
   - Excel 报告适合数据筛选和排序
   - 图表适合技术分析和趋势判断

3. **使用警报系统**
   - 关注警报数量的变化
   - 结合多个警报信号进行交叉验证
   - 验证警报的有效性，避免误报

4. **技术分析最佳实践**
   - 结合多个技术指标进行综合判断
   - 不同周期的均线具有不同的参考意义
   - RSI 超买超卖信号在强势市场中可能不准确

## 注意事项

1. **数据来源**
   - 使用 Yahoo Finance API
   - 数据可能有延迟
   - 建议在非交易时段运行以获取完整数据

2. **系统限制**
   - API 调用频率限制
   - 历史数据长度限制
   - 部分股票可能数据不完整

3. **分析建议**
   - 技术分析应结合基本面分析
   - 考虑市场整体环境和行业趋势
   - 不要单一依赖技术分析进行决策

## 常见问题解答

### 安装相关

- **Q: 依赖安装失败怎么办？**
  - A: 请尝试以下解决方案：
    1. 使用国内镜像源：`pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`
    2. 逐个安装依赖，查看具体错误信息
    3. 升级 pip 到最新版本：`pip install --upgrade pip`
    4. 检查 Python 版本是否满足要求（3.6+）

- **Q: 在 macOS/Linux 下出现权限错误怎么办？**
  - A: 尝试使用 `sudo pip install -r requirements.txt` 或创建虚拟环境后安装

- **Q: 我应该使用虚拟环境吗？**
  - A: 推荐使用虚拟环境（如 venv 或 conda）以避免依赖冲突，具体步骤：
    ```bash
    # 使用 venv
    python -m venv stock_env
    source stock_env/bin/activate  # Linux/macOS
    stock_env\Scripts\activate     # Windows
    pip install -r requirements
