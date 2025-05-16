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
        tuple: (交叉信号类型, 交叉日期), 如果没有交叉信号则返回 (None, None)
    """
    if len(data) < max(short_period, long_period) + 1:
        return None, None
        
    short_ema = data[f'EMA_{short_period}']
    long_ema = data[f'EMA_{long_period}']
    
    # 确保有足够的数据进行比较
    if len(short_ema) < 2 or len(long_ema) < 2:
        return None, None
    
    # 计算所有的交叉点
    cross_dates = []
    cross_types = []
    
    # 从最新的数据向前查找最近的交叉点
    for i in range(len(data) - 1, 0, -1):
        curr_short = short_ema.iloc[i].item()
        curr_long = long_ema.iloc[i].item()
        prev_short = short_ema.iloc[i-1].item()
        prev_long = long_ema.iloc[i-1].item()
        
        # 检测金叉
        if prev_short < prev_long and curr_short > curr_long:
            return "golden_cross", data.index[i]
        # 检测死叉
        elif prev_short > prev_long and curr_short < curr_long:
            return "death_cross", data.index[i]
    
    return None, None

def detect_price_ema_cross(data, period=5):
    """检测价格与EMA交叉
    Args:
        data (pd.DataFrame): 股票数据
        period (int): EMA周期
    Returns:
        tuple: (交叉信号类型, 交叉日期), 如果没有交叉信号则返回 (None, None)
    """
    if len(data) < period + 1:
        return None, None
        
    close_prices = data['Close']
    ema = data[f'EMA_{period}']
    
    # 确保有足够的数据进行比较
    if len(close_prices) < 2 or len(ema) < 2:
        return None, None
    
    # 从最新的数据向前查找最近的交叉点
    for i in range(len(data) - 1, 0, -1):
        curr_price = close_prices.iloc[i].item()
        curr_ema = ema.iloc[i].item()
        prev_price = close_prices.iloc[i-1].item()
        prev_ema = ema.iloc[i-1].item()
        
        # 检测价格上穿EMA
        if prev_price < prev_ema and curr_price > curr_ema:
            return "price_up_cross", data.index[i]
        # 检测价格下穿EMA
        elif prev_price > prev_ema and curr_price < curr_ema:
            return "price_down_cross", data.index[i]
    
    return None, None

def calculate_macd(data, fast_period=12, slow_period=26, signal_period=9):
    """计算MACD指标
    Args:
        data (pd.DataFrame): 股票数据
        fast_period (int): 快线周期
        slow_period (int): 慢线周期
        signal_period (int): 信号线周期
    Returns:
        tuple: (MACD线, 信号线, MACD柱状图)
    """
    try:
        # 计算快线和慢线的EMA
        fast_ema = data['Close'].ewm(span=fast_period, adjust=False).mean()
        slow_ema = data['Close'].ewm(span=slow_period, adjust=False).mean()
        
        # 计算MACD线 (DIF)
        macd_line = fast_ema - slow_ema
        
        # 计算信号线 (DEA)
        signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
        
        # 计算MACD柱状图
        macd_hist = macd_line - signal_line
        
        return macd_line, signal_line, macd_hist
    except Exception as e:
        print(f"{Colors.RED}Error calculating MACD: {str(e)}{Colors.END}")
        return pd.Series(index=data.index), pd.Series(index=data.index), pd.Series(index=data.index)

def detect_macd_signals(data):
    """检测MACD信号
    Args:
        data (pd.DataFrame): 股票数据
    Returns:
        dict: MACD信号字典，包含信号类型和对应的日期
    """
    signals = {
        'cross_signal': None,
        'cross_date': None,
        'zero_cross': None,
        'zero_date': None,
        'divergence': None,
        'divergence_date': None,
        'histogram_trend': None,
        'histogram_date': None
    }
    
    try:
        # 获取最新的MACD值和日期
        latest_date = data.index[-1]
        latest_macd = data['MACD_line'].iloc[-1]
        prev_macd = data['MACD_line'].iloc[-2]
        latest_signal = data['MACD_signal'].iloc[-1]
        prev_signal = data['MACD_signal'].iloc[-2]
        latest_hist = data['MACD_hist'].iloc[-1]
        prev_hist = data['MACD_hist'].iloc[-2]
        
        # 检测MACD线与信号线的交叉
        if prev_macd.item() < prev_signal.item() and latest_macd.item() > latest_signal.item():
            signals['cross_signal'] = '金叉（买入）'
            signals['cross_date'] = latest_date
        elif prev_macd.item() > prev_signal.item() and latest_macd.item() < latest_signal.item():
            signals['cross_signal'] = '死叉（卖出）'
            signals['cross_date'] = latest_date
            
        # 检测MACD线与零线的交叉
        if prev_macd.item() < 0 and latest_macd.item() > 0:
            signals['zero_cross'] = '上穿零线（看涨）'
            signals['zero_date'] = latest_date
        elif prev_macd.item() > 0 and latest_macd.item() < 0:
            signals['zero_cross'] = '下穿零线（看跌）'
            signals['zero_date'] = latest_date
            
        # 检测背离（简单版本）
        price_trend = data['Close'].iloc[-20:].diff().mean()
        macd_trend = data['MACD_line'].iloc[-20:].diff().mean()
        if price_trend.item() > 0 and macd_trend.item() < 0:
            signals['divergence'] = '顶背离（潜在卖出）'
            signals['divergence_date'] = latest_date
        elif price_trend.item() < 0 and macd_trend.item() > 0:
            signals['divergence'] = '底背离（潜在买入）'
            signals['divergence_date'] = latest_date
            
        # 检测MACD柱状图趋势
        if latest_hist.item() > prev_hist.item():
            signals['histogram_trend'] = '柱状图增加（动能增强）'
            signals['histogram_date'] = latest_date
        else:
            signals['histogram_trend'] = '柱状图减少（动能减弱）'
            signals['histogram_date'] = latest_date
            
        return signals
    except Exception as e:
        print(f"{Colors.RED}Error detecting MACD signals: {str(e)}{Colors.END}")
        return signals

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
        
        # 计算MACD
        macd_line, signal_line, macd_hist = calculate_macd(data)
        data['MACD_line'] = macd_line
        data['MACD_signal'] = signal_line
        data['MACD_hist'] = macd_hist
        
        return data
    except Exception as e:
        print(f"{Colors.RED}Error calculating indicators: {str(e)}{Colors.END}")
        return data
