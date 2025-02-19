"""技术分析模块"""

import pandas as pd
from .constants import Colors

def calculate_rsi(data: pd.DataFrame, period=14):
    """计算RSI指标
    Args:
        data (pd.DataFrame): 股票数据
        period (int): RSI周期，默认14天
    Returns:
        pd.Series: RSI值
    """
    try:
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    except Exception as e:
        print(f"{Colors.RED}Error calculating RSI: {str(e)}{Colors.END}")
        return pd.Series(index=data.index)

def get_rsi_signal(data):
    """获取RSI信号
    Args:
        data (pd.DataFrame): 股票数据
    Returns:
        str: RSI信号
    """
    try:
        latest_rsi = data['RSI'].iloc[-1]
        
        if latest_rsi >= 70:
            return "超买"
        elif latest_rsi <= 30:
            return "超卖"
        return "正常"
        
    except Exception as e:
        print(f"{Colors.RED}Error getting RSI signal: {str(e)}{Colors.END}")
        return "N/A"

def detect_ema_cross(data, short_period=5, long_period=20):
    """检测EMA交叉
    Args:
        data (pd.DataFrame): 股票数据
        short_period (int): 短期EMA周期
        long_period (int): 长期EMA周期
    Returns:
        str: 交叉信号类型
    """
    if len(data) < max(short_period, long_period) + 1:
        return None
        
    short_ema = data[f'EMA_{short_period}']
    long_ema = data[f'EMA_{long_period}']
    
    # 确保有足够的数据进行比较
    if len(short_ema) < 2 or len(long_ema) < 2:
        return None
        
    # 获取最近两个时间点的数据
    current_short = short_ema.iloc[-1]
    current_long = long_ema.iloc[-1]
    prev_short = short_ema.iloc[-2]
    prev_long = long_ema.iloc[-2]
    
    # 检测金叉
    if prev_short < prev_long and current_short > current_long:
        return "golden_cross"
    # 检测死叉
    elif prev_short > prev_long and current_short < current_long:
        return "death_cross"
    
    return None

def calculate_indicators(data):
    """计算技术指标
    Args:
        data (pd.DataFrame): 股票数据
    Returns:
        pd.DataFrame: 添加了技术指标的股票数据
    """
    try:
        # 计算各种EMA
        for period in [5, 10, 20, 50, 60, 120, 200]:
            data[f'EMA_{period}'] = data['Close'].ewm(span=period, adjust=False).mean()
        
        # 计算RSI
        data['RSI'] = calculate_rsi(data)
        
        return data
    except Exception as e:
        print(f"{Colors.RED}Error calculating indicators: {str(e)}{Colors.END}")
        return data
