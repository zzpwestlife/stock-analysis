#!/usr/bin/env python3
"""
股票技术分析工具
用于分析股票的技术指标，包括：
- EMA (指数移动平均线)
- RSI (相对强弱指标)
- 均线交叉信号
- 价格与均线关系
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os
from collections import Counter # 引入Counter

from utils.constants import Colors
from utils.config import load_config
from utils.analysis import calculate_indicators
from utils.alerts import generate_alerts
from utils.report import save_analysis_plot, generate_report

def analyze_stock(symbol, start_date, end_date, output_dir):
    """
    分析单个股票
    
    Args:
        symbol (str): 股票代码
        start_date (str): 开始日期
        end_date (str): 结束日期
        output_dir (str): 输出目录
    
    Returns:
        dict: 分析结果
    """
    try:
        print(f"\n\n分析股票 {symbol}...")

        # 使用DataFetcher获取股票数据
        from utils.data_fetcher import DataFetcher
        fetcher = DataFetcher()
        data = fetcher.fetch_data(symbol, start_date, end_date)
        
        if data is None:
            return {
                'symbol': symbol,
                'error': '无法获取股票数据'
            }
        
        # 计算技术指标
        data = calculate_indicators(data)
        
        # 生成警报（用于终端显示）
        terminal_alerts = generate_alerts(symbol, data, use_colors=True)
        # 打印带颜色的警报
        for alert in terminal_alerts:
            print(alert['message']) # 打印消息本身
            
        # 生成不带颜色的警报（用于报告）
        report_alerts = generate_alerts(symbol, data, use_colors=False)
        
        # 统计警报类型
        alert_counts = Counter(alert['type'] for alert in report_alerts)

        # 获取最新价格和价格变化
        latest_close = data['Close'].iloc[-1].item()
        prev_close = data['Close'].iloc[-2].item()
        price_change = latest_close - prev_close
        price_change_pct = (price_change / prev_close) * 100
        
        # 保存分析图表
        save_analysis_plot(data, symbol, output_dir)
        
        return {
            'symbol': symbol,
            'data': data,
            'price': latest_close,
            'price_change': price_change,
            'price_change_pct': price_change_pct,
            'rsi': data['RSI'].iloc[-1].item(),
            'alert_details': report_alerts,  # 使用不带颜色的警报
            'alert_counts': dict(alert_counts), # 添加警报统计
            'error': None
        }
        
    except Exception as e:
        print(f"{Colors.RED}Error analyzing {symbol}: {str(e)}{Colors.END}")
        return {
            'symbol': symbol,
            'error': str(e)
        }

def main():
    """主函数"""
    # 读取配置文件
    config = load_config()
    if not config:
        return
    
    # 创建输出目录
    output_dir = os.path.join('output', datetime.now().strftime('%Y%m%d_%H%M%S'))
    os.makedirs(output_dir, exist_ok=True)
    
    # 分析所有股票
    results = []
    success_count = 0
    total_alert_counts = Counter() # 用于汇总所有股票的警报统计
    
    for symbol in config['stocks']:
        result = analyze_stock(
            symbol,
            (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'),
            datetime.now().strftime('%Y-%m-%d'),
            output_dir
        )
        results.append(result)
        if not result.get('error'):
            success_count += 1
            if 'alert_counts' in result: # 累加警报统计
                total_alert_counts.update(result['alert_counts'])
    
    # 生成HTML报告
    generate_report(results, output_dir) # 传递包含警报统计的results
    
    # 打印分析完成信息
    print(f"\n分析完成！")
    print(f"成功分析的股票数量: {success_count}/{len(config['stocks'])}")
    print(f"分析结果已保存到目录: {output_dir}")
    print("生成的文件：")
    print("- analysis_results.html：完整分析结果（包含图表和详细信息）")

    # 打印警报统计
    if total_alert_counts:
        print("\n警报类型统计:")
        for alert_type, count in total_alert_counts.items():
            print(f"- {alert_type}: {count}")

if __name__ == '__main__':
    main()