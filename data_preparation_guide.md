# 股票/ETF 数据准备指南

本文档将指导您如何准备 [股票代码/ETF代码] 的历史数据，以便后续使用 `analyze_pl.py` 脚本进行分析。数据准备过程主要包括使用 Chrome 插件从财经网站导出数据，以及使用 Excel 或类似电子表格软件进行数据调整和 P/L (盈亏百分比) 列的计算。

## 步骤 1: 安装 "Instant Data Scraper" Chrome 插件

1.  打开 Chrome 浏览器。
2.  访问 Chrome 网上应用店：[Instant Data Scraper](https://chromewebstore.google.com/detail/instant-data-scraper/ofaokhiedipichpaobibbnahnkdoiiah) <mcreference link="https://chromewebstore.google.com/detail/instant-data-scraper/ofaokhiedipichpaobibbnahnkdoiiah" index="0"></mcreference>
3.  点击 "添加到 Chrome" (或类似按钮) 来安装该插件。

## 步骤 2: 从财经网站导出 [股票代码/ETF代码] 历史数据

1.  **访问数据源**: 打开一个提供股票历史数据的网站，例如雅虎财经 (Yahoo Finance)。搜索您感兴趣的 [股票代码/ETF代码] (例如：AAPL, SPY) 的股票页面，并导航到历史数据 (Historical Data) 部分。
    *   示例链接 (雅虎财经，将 [股票代码] 替换为实际代码): `https://finance.yahoo.com/quote/[股票代码]/history`
2.  **选择数据范围**: 根据您的分析需求，选择合适的历史数据时间范围。
3.  **启动 Instant Data Scraper**: 
    *   在包含历史数据表格的页面上，点击浏览器工具栏中的 Instant Data Scraper 插件图标。
    *   该插件通常会自动尝试识别页面上的数据表格。 <mcreference link="https://chromewebstore.google.com/detail/instant-data-scraper/ofaokhiedipichpaobibbnahnkdoiiah" index="0"></mcreference>
4.  **调整选择 (如果需要)**: 
    *   如果插件未能准确选中所需数据，您可能需要手动调整选择区域或使用插件提供的高级选项来定位正确的表格。 <mcreference link="https://chromewebstore.google.com/detail/instant-data-scraper/ofaokhiedipichpaobibbnahnkdoiiah" index="0"></mcreference>
    *   确保选中的数据列包括：日期 (Date), 开盘价 (Open), 最高价 (High), 最低价 (Low), 收盘价 (Close), 调整后收盘价 (Adj Close), 成交量 (Volume 不需要)。
5.  **处理分页 (如果适用)**:
    *   如果数据分布在多个页面上，Instant Data Scraper 通常能够处理分页。您可能需要配置插件以点击“下一页”按钮或处理无限滚动。 <mcreference link="https://chromewebstore.google.com/detail/instant-data-scraper/ofaokhiedipichpaobibbnahnkdoiiah" index="0"></mcreference>
6.  **导出数据**: 
    *   当数据被正确选中后，点击插件界面上的 "CSV" 或 "Excel" 按钮将数据导出为 CSV 文件。 <mcreference link="https://chromewebstore.google.com/detail/instant-data-scraper/ofaokhiedipichpaobibbnahnkdoiiah" index="0">0</mcreference>
    *   将文件保存到您的项目目录下的 `[股票代码]_data` 文件夹中 (如果该文件夹不存在，请创建它)，例如命名为 `[股票代码]_raw_data.csv`。

## 步骤 3: 使用 Excel 调整数据并计算 P/L 列

1.  **打开 CSV 文件**: 
    *   使用 Microsoft Excel 打开您刚刚导出的 CSV 文件 (`[股票代码]_raw_data.csv`)。
2.  **数据清洗 (如果需要)**:
    *   检查数据是否有任何异常值、缺失值或格式问题 (清理掉空行)。例如，日期格式可能需要统一，数字列应确保为数值类型。
    *   删除任何不需要的表头、表尾或空行。
3.  **添加 P/L (盈亏百分比) 列**: 
    *   `analyze_pl.py` 脚本期望 CSV 文件中包含一个名为 `P/L` 的列，表示每日的盈亏百分比。
    *   **计算方法**: P/L 通常是根据当日收盘价相对于前一日收盘价的变化来计算的。公式如下：
        `P/L = (当日收盘价/前一日收盘价 - 1) * 100%`
    *   **在 Excel 中实现**:
        1.  假设您的数据从第 2 行开始 (第 1 行为表头)，并且收盘价 (Close) 在 E 列。
        2.  在第一条有数据的行 (例如第 3 行，因为第 2 行没有前一日数据进行比较) 的 P/L 列 (假设为 G 列) 中输入公式。例如，在 G3 单元格中输入：
            `=((E3/E2 - 1)`
        3.  将此单元格的格式设置为百分比 (例如，保留两位小数)。
        4.  向下拖动 G3 单元格的填充柄，将公式应用于所有后续行。
        5.  第一行数据的 P/L (例如 G2) 将无法计算，可以留空或标记为 N/A。
    *   **注意**: 您导出的数据可能已经包含了 `P/L` 列或类似含义的列。请检查其计算方式是否符合您的需求。如果需要重新计算或验证，可以按照上述步骤操作。
4.  **确保列名正确**: 
    *   确保最终的 CSV 文件包含以下列名 (或 `analyze_pl.py` 脚本中配置的列名)：`Date`, `Open`, `High`, `Low`, `Close`, `Adj Close`, `P/L`。
5.  **保存文件**: 
    *   将调整后的数据另存为一个新的 CSV 文件，例如 `[股票代码].csv`，并确保它位于 `[股票代码]_data` 文件夹中，以便 `analyze_pl.py` 脚本可以访问。

## 步骤 4: 准备完成

完成以上步骤后，您的 `[股票代码]_data/[股票代码].csv` 文件就准备好了，可以用于 `analyze_pl.py` 脚本进行盈亏分析。

**重要提示**:
*   不同的财经网站提供的数据格式和列名可能有所不同。您可能需要根据实际导出的数据调整上述步骤。
*   Instant Data Scraper 的功能和界面可能会随着版本更新而变化。 <mcreference link="https://chromewebstore.google.com/detail/instant-data-scraper/ofaokhiedipichpaobibbnahnkdoiiah" index="0">0</mcreference>
*   确保您的 Excel 或电子表格软件在保存 CSV 文件时使用 UTF-8 编码，以避免特殊字符出现问题。