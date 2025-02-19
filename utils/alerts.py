"""警报生成模块"""

from .constants import Colors
from .analysis import detect_ema_cross, get_rsi_signal

def generate_alerts(symbol, data):
    """
    生成股票警报
    
    Args:
        symbol (str): 股票代码
        data (pd.DataFrame): 股票数据
    
    Returns:
        list: 警报列表
    """
    try:
        alerts = []
        
        # 检查RSI
        rsi = data['RSI'].iloc[-1].item()
        if rsi > 70:
            alerts.append(f"RSI超买: {rsi:.2f}")
        elif rsi < 30:
            alerts.append(f"RSI超卖: {rsi:.2f}")
        
        # 检查价格与均线关系
        latest_close = data['Close'].iloc[-1].item()
        price_alerts = get_price_alerts(data, latest_close)
        alerts.extend(price_alerts)
        
        return alerts
        
    except Exception as e:
        print(f"{Colors.RED}Error generating alerts for {symbol}: {str(e)}{Colors.END}")
        return []

def get_price_alerts(data, latest_close):
    """
    根据价格和均线生成警报
    
    Args:
        data (pd.DataFrame): 股票数据
        latest_close (float): 最新收盘价
    
    Returns:
        list: 警报列表
    """
    alerts = []
    
    # 检查是否跌破各条均线
    for period in [5, 10, 20, 50]:
        ema = data[f'EMA_{period}'].iloc[-1].item()
        if latest_close < ema:
            alerts.append(f"价格 ({latest_close:.2f}) 跌破 {period}日均线 ({ema:.2f})")
    
    # 检查是否形成死叉（短期均线跌破长期均线）
    for short_period, long_period in [(5, 10), (10, 20), (20, 50)]:
        short_ema_prev = data[f'EMA_{short_period}'].iloc[-2].item()
        short_ema_curr = data[f'EMA_{short_period}'].iloc[-1].item()
        long_ema_prev = data[f'EMA_{long_period}'].iloc[-2].item()
        long_ema_curr = data[f'EMA_{long_period}'].iloc[-1].item()
        
        # 检查最近两天的均线关系
        if short_ema_prev > long_ema_prev and short_ema_curr < long_ema_curr:
            alerts.append(f"{short_period}日均线跌破{long_period}日均线，形成死叉")
    
    # 检查是否形成金叉（短期均线突破长期均线）
    for short_period, long_period in [(5, 10), (10, 20), (20, 50)]:
        short_ema_prev = data[f'EMA_{short_period}'].iloc[-2].item()
        short_ema_curr = data[f'EMA_{short_period}'].iloc[-1].item()
        long_ema_prev = data[f'EMA_{long_period}'].iloc[-2].item()
        long_ema_curr = data[f'EMA_{long_period}'].iloc[-1].item()
        
        # 检查最近两天的均线关系
        if short_ema_prev < long_ema_prev and short_ema_curr > long_ema_curr:
            alerts.append(f"{short_period}日均线突破{long_period}日均线，形成金叉")
    
    return alerts
