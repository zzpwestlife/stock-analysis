import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os
from typing import Tuple

# ANSI color codes
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def calculate_rsi(data: pd.DataFrame, period=14):
    """计算RSI指标"""
    delta = data['Close'].diff()
    
    gain = (delta.where(delta > 0, 0)).fillna(0)
    loss = (-delta.where(delta < 0, 0)).fillna(0)
    
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi.round(2)

def get_rsi_signal(rsi):
    """根据RSI值返回信号和颜色"""
    if rsi <= 30:
        return "严重超卖", Colors.GREEN
    elif rsi <= 40:
        return "超卖", Colors.BLUE
    elif rsi >= 70:
        return "严重超买", Colors.RED
    elif rsi >= 60:
        return "超买", Colors.YELLOW
    else:
        return "中性", Colors.END

def detect_ema_cross(data):
    """检测金叉和死叉
    Returns:
        tuple: (cross_type, days_since_cross)
            cross_type: 'golden' for golden cross, 'death' for death cross, None if no cross
            days_since_cross: number of days since the last cross
    """
    # Get the 50 and 200 day EMAs
    ema50 = data['EMA50']
    ema200 = data['EMA200']
    
    # Create cross signals
    golden_cross = (ema50 > ema200) & (ema50.shift(1) <= ema200.shift(1))
    death_cross = (ema50 < ema200) & (ema50.shift(1) >= ema200.shift(1))
    
    # Find the last cross
    last_golden = data.index[golden_cross].max() if golden_cross.any() else None
    last_death = data.index[death_cross].max() if death_cross.any() else None
    
    # If we have both types of crosses, use the most recent one
    if last_golden and last_death:
        if last_golden > last_death:
            cross_type = 'golden'
            last_cross = last_golden
        else:
            cross_type = 'death'
            last_cross = last_death
    elif last_golden:
        cross_type = 'golden'
        last_cross = last_golden
    elif last_death:
        cross_type = 'death'
        last_cross = last_death
    else:
        return None, None
    
    # Calculate days since cross
    days_since_cross = (data.index[-1] - last_cross).days
    
    return cross_type, days_since_cross

def generate_markdown_report(data, symbol, output_dir):
    """生成Markdown格式的分析报告"""
    latest_data = data.iloc[-1]
    prev_data = data.iloc[-2]
    latest_rsi = data['RSI'].iloc[-1]
    rsi_signal, _ = get_rsi_signal(latest_rsi)
    
    # Detect EMA cross
    cross_type, days_since_cross = detect_ema_cross(data)
    
    report = f"""# {symbol} 股票分析报告 ({latest_data.name.strftime('%Y-%m-%d')})

## 价格信息
- 当前收盘价: ${latest_data['Close']:.2f}
- 前一日收盘价: ${prev_data['Close']:.2f}
- 价格变动: ${latest_data['Price_Change']:.2f} ({latest_data['Price_Change_Pct']:.2f}%)

## RSI分析
- 14日RSI: {latest_rsi:.2f}
- 信号: {rsi_signal}

## 均线分析
### 短期均线
"""
    
    for period in [5, 10, 20]:
        diff = latest_data['Close'] - latest_data[f'EMA{period}']
        report += f"- EMA{period}: ${latest_data[f'EMA{period}']:.2f} (差值: ${diff:.2f})\n"
    
    report += "\n### 中期均线\n"
    for period in [50, 60]:
        diff = latest_data['Close'] - latest_data[f'EMA{period}']
        report += f"- EMA{period}: ${latest_data[f'EMA{period}']:.2f} (差值: ${diff:.2f})\n"
    
    report += "\n### 长期均线\n"
    for period in [120, 200]:
        diff = latest_data['Close'] - latest_data[f'EMA{period}']
        report += f"- EMA{period}: ${latest_data[f'EMA{period}']:.2f} (差值: ${diff:.2f})\n"
    
    if cross_type:
        report += "\n## EMA交叉分析\n"
        if cross_type == 'golden':
            report += f"🌟 Golden Cross detected {days_since_cross} days ago!\n"
            report += "50日均线从下方穿过200日均线，这通常是强烈的看涨信号\n"
        else:
            report += f"💀 Death Cross detected {days_since_cross} days ago!\n"
            report += "50日均线从上方穿过200日均线，这通常是强烈的看跌信号\n"
    
    if latest_data['Alert']:
        report += "\n## ⚠️ 警告\n"
        report += "股票价格下跌且低于短期均线\n"
        report += f"跌幅: {((latest_data['Close'] - prev_data['Close']) / prev_data['Close'] * 100):.2f}%\n"
        
        if latest_data['Close'] < latest_data['EMA5']:
            report += f"收盘价低于EMA5: ${latest_data['Close'] - latest_data['EMA5']:.2f}\n"
        if latest_data['Close'] < latest_data['EMA10']:
            report += f"收盘价低于EMA10: ${latest_data['Close'] - latest_data['EMA10']:.2f}\n"
        if latest_data['Close'] < latest_data['EMA20']:
            report += f"收盘价低于EMA20: ${latest_data['Close'] - latest_data['EMA20']:.2f}\n"
    
    # Save report
    report_file = os.path.join(output_dir, f'{symbol}_report.md')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)

def analyze_stock(symbol, start_date, end_date, output_dir):
    """分析单个股票并保存结果"""
    try:
        # Get stock data
        stock = yf.download(symbol, start=start_date, end=end_date, progress=False)
        if stock.empty:
            print(f"无法获取{symbol}的数据")
            return False
        
        # Create a DataFrame with Close prices
        data = pd.DataFrame()
        data['Close'] = stock['Close']
        
        # Calculate EMAs
        for period in [5, 10, 20, 50, 60, 120, 200]:
            data[f'EMA{period}'] = data['Close'].ewm(span=period, adjust=False).mean()
        
        # Calculate price changes
        data['Price_Change'] = data['Close'].diff()
        data['Price_Change_Pct'] = (data['Close'].pct_change() * 100).round(2)
        
        # Calculate RSI
        data['RSI'] = calculate_rsi(data)
        
        # Generate alerts
        data['Alert'] = (
            (data['Close'] < data['Close'].shift(1)) & 
            ((data['Close'] < data['EMA5']) |
             (data['Close'] < data['EMA10']) |
             (data['Close'] < data['EMA20']))
        )
        
        # Get latest data points
        latest_data = data.iloc[-1]
        prev_data = data.iloc[-2]
        latest_rsi = data['RSI'].iloc[-1]
        rsi_signal, rsi_color = get_rsi_signal(latest_rsi)
        
        # Detect EMA cross
        cross_type, days_since_cross = detect_ema_cross(data)
        
        # Generate terminal output with colors
        print(f"\n{Colors.BOLD}{symbol} 股票分析报告 ({latest_data.name.strftime('%Y-%m-%d')}){Colors.END}")
        print("-" * 50)
        
        # Price information with colors
        price_change = latest_data['Close'] - prev_data['Close']
        price_color = Colors.GREEN if price_change >= 0 else Colors.RED
        print(f"当前收盘价: {price_color}${latest_data['Close']:.2f}{Colors.END}")
        print(f"前一日收盘价: ${prev_data['Close']:.2f}")
        print(f"价格变动: {price_color}${price_change:.2f} ({(price_change/prev_data['Close']*100):.2f}%){Colors.END}")
        
        # RSI Analysis
        print(f"\nRSI分析:")
        print(f"14日RSI: {rsi_color}{latest_rsi:.2f}{Colors.END} ({rsi_signal})")
        
        # Print EMAs
        print("\n均线分析:")
        print(f"{Colors.BOLD}短期均线:{Colors.END}")
        for period in [5, 10, 20]:
            diff = latest_data['Close'] - latest_data[f'EMA{period}']
            color = Colors.GREEN if diff >= 0 else Colors.RED
            print(f"- EMA{period}: {color}${latest_data[f'EMA{period}']:.2f} (差值: ${diff:.2f}){Colors.END}")
        
        print(f"\n{Colors.BOLD}中期均线:{Colors.END}")
        for period in [50, 60]:
            diff = latest_data['Close'] - latest_data[f'EMA{period}']
            color = Colors.GREEN if diff >= 0 else Colors.RED
            print(f"- EMA{period}: {color}${latest_data[f'EMA{period}']:.2f} (差值: ${diff:.2f}){Colors.END}")
        
        print(f"\n{Colors.BOLD}长期均线:{Colors.END}")
        for period in [120, 200]:
            diff = latest_data['Close'] - latest_data[f'EMA{period}']
            color = Colors.GREEN if diff >= 0 else Colors.RED
            print(f"- EMA{period}: {color}${latest_data[f'EMA{period}']:.2f} (差值: ${diff:.2f}){Colors.END}")
        
        if cross_type:
            print(f"\n{Colors.BOLD}EMA交叉分析:{Colors.END}")
            if cross_type == 'golden':
                print(f"{Colors.YELLOW}🌟 Golden Cross detected {days_since_cross} days ago!{Colors.END}")
                print(f"{Colors.GREEN}50日均线从下方穿过200日均线，这通常是强烈的看涨信号{Colors.END}")
            else:
                print(f"{Colors.RED}💀 Death Cross detected {days_since_cross} days ago!{Colors.END}")
                print(f"{Colors.RED}50日均线从上方穿过200日均线，这通常是强烈的看跌信号{Colors.END}")
        
        if latest_data['Alert']:
            print(f"\n{Colors.RED}⚠️ 警告！{Colors.END}")
            print(f"{Colors.YELLOW}股票价格下跌且低于短期均线{Colors.END}")
            print(f"跌幅: {Colors.RED}{((latest_data['Close'] - prev_data['Close']) / prev_data['Close'] * 100):.2f}%{Colors.END}")
            
            if latest_data['Close'] < latest_data['EMA5']:
                print(f"收盘价低于EMA5: {Colors.RED}${latest_data['Close'] - latest_data['EMA5']:.2f}{Colors.END}")
            if latest_data['Close'] < latest_data['EMA10']:
                print(f"收盘价低于EMA10: {Colors.RED}${latest_data['Close'] - latest_data['EMA10']:.2f}{Colors.END}")
            if latest_data['Close'] < latest_data['EMA20']:
                print(f"收盘价低于EMA20: {Colors.RED}${latest_data['Close'] - latest_data['EMA20']:.2f}{Colors.END}")
        
        # Generate markdown report
        generate_markdown_report(data, symbol, output_dir)
        
        # Plot chart
        plt.figure(figsize=(15, 8))
        
        # Plot price
        plt.plot(data.index, data['Close'], label='Close Price', alpha=0.5)
        
        # Plot EMAs with different colors
        plt.plot(data.index, data['EMA5'], label='EMA5', linestyle='--', alpha=0.8, color='#FF9999')
        plt.plot(data.index, data['EMA10'], label='EMA10', linestyle='--', alpha=0.8, color='#66B2FF')
        plt.plot(data.index, data['EMA20'], label='EMA20', linestyle='--', alpha=0.8, color='#99FF99')
        plt.plot(data.index, data['EMA50'], label='EMA50', linestyle='-.', alpha=0.7, color='#FFCC99')
        plt.plot(data.index, data['EMA60'], label='EMA60', linestyle='-.', alpha=0.7, color='#FF99FF')
        plt.plot(data.index, data['EMA120'], label='EMA120', linewidth=1.5, alpha=0.6, color='#99FFFF')
        plt.plot(data.index, data['EMA200'], label='EMA200', linewidth=2, alpha=0.6, color='#FFB366')
        
        # Mark alert points
        alert_days = data[data['Alert']].index
        if len(alert_days) > 0:
            plt.scatter(alert_days, data.loc[alert_days, 'Close'], 
                       color='red', marker='v', s=100, label='Alert')
        
        plt.title(f"{symbol} Stock Price with EMAs ({start_date} to {end_date})")
        plt.xlabel("Date")
        plt.ylabel("Price ($)")
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Save chart
        plt.savefig(os.path.join(output_dir, f'{symbol}_analysis_plot.png'), 
                   dpi=300, bbox_inches='tight')
        plt.close()
        
        # Save analysis data
        analysis_data = data[[
            'Close', 'Price_Change', 'Price_Change_Pct',
            'EMA5', 'EMA10', 'EMA20',
            'EMA50', 'EMA60',
            'EMA120', 'EMA200',
            'Alert', 'RSI'
        ]].copy()
        
        # Calculate differences from EMAs
        for ma in ['EMA5', 'EMA10', 'EMA20', 'EMA50', 'EMA60', 'EMA120', 'EMA200']:
            analysis_data[f'{ma}_Diff'] = (analysis_data['Close'] - analysis_data[ma]).round(2)
        
        # Format date index
        analysis_data.index = analysis_data.index.strftime('%Y-%m-%d')
        analysis_data.index.name = '日期'
        
        # Rename columns
        columns_rename = {
            'Close': '收盘价',
            'Price_Change': '价格变动',
            'Price_Change_Pct': '价格变动百分比',
            'Alert': '警报',
            'RSI': 'RSI'
        }
        for ma in ['EMA5', 'EMA10', 'EMA20', 'EMA50', 'EMA60', 'EMA120', 'EMA200']:
            columns_rename[ma] = ma
            columns_rename[f'{ma}_Diff'] = f'{ma}差值'
        
        analysis_data.rename(columns=columns_rename, inplace=True)
        
        # Save full data
        full_data_file = os.path.join(output_dir, f'{symbol}_full_analysis.csv')
        analysis_data.to_csv(full_data_file, encoding='utf-8-sig')
        
        # Save alert data
        alert_data = analysis_data[analysis_data['警报'] == True].copy()
        if not alert_data.empty:
            alert_file = os.path.join(output_dir, f'{symbol}_alerts.csv')
            alert_data.to_csv(alert_file, encoding='utf-8-sig')
        
        return True
    except Exception as e:
        print(f"分析{symbol}出错：{e}")
        return False

def main():
    """主函数"""
    # 设置起止日期
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    # 创建输出目录
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", timestamp)
    os.makedirs(output_dir, exist_ok=True)
    
    # 股票列表
    stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA', 'SOFI', 'PLTR']
    
    # 分析每只股票
    success_count = 0
    for symbol in stocks:
        if analyze_stock(symbol, start_date, end_date, output_dir):
            success_count += 1
    
    print("\n分析完成！")
    print(f"成功分析的股票数量: {success_count}/{len(stocks)}")
    print(f"分析结果已保存到目录: {output_dir}")
    print("每只股票都生成了以下文件：")
    print("- XXX_full_analysis.csv：完整分析数据")
    print("- XXX_alerts.csv：警报数据（如果有警报的话）")
    print("- XXX_analysis_plot.png：分析图表")
    print("- XXX_report.md：分析报告")

if __name__ == "__main__":
    main()
