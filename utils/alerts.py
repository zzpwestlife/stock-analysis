"""警报生成模块"""

from .constants import Colors
from .analysis import detect_ema_cross, get_rsi_signal

def generate_alerts(symbol, data, use_colors=True):
    """
    生成股票警报
    
    Args:
        symbol (str): 股票代码
        data (pd.DataFrame): 股票数据
        use_colors (bool): 是否使用颜色标记，默认为True
    
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
        price_alerts = get_price_alerts(data, latest_close, use_colors)
        alerts.extend(price_alerts)
        
        return alerts
        
    except Exception as e:
        print(f"{Colors.RED}Error generating alerts for {symbol}: {str(e)}{Colors.END}")
        return []

def get_price_alerts(data, latest_close, use_colors=True):
    """
    根据价格和均线生成警报
    
    Args:
        data (pd.DataFrame): 股票数据
        latest_close (float): 最新收盘价
        use_colors (bool): 是否使用颜色标记，默认为True
    
    Returns:
        list: 警报列表
    """
    alerts = []
    
    # 检查是否跌破各条均线
    for period in [5, 10, 20, 50]:
        ema = data[f'EMA_{period}'].iloc[-1].item()
        if latest_close < ema:
            alerts.append(f"价格 ({latest_close:.2f}) 跌破 {period}日均线 ({ema:.2f})")
    
    # 获取最新日期
    latest_date = data.index[-1]
    
    # 检查是否形成金叉或死叉
    for short_period, long_period in [(5, 10), (10, 20), (20, 50)]:
        cross_signal, cross_date = detect_ema_cross(data, short_period, long_period)
        if cross_signal:
            # 计算交叉日期与最新日期的天数差
            days_diff = (latest_date - cross_date).days
            
            # 构建基本消息
            if cross_signal == "golden_cross":
                base_msg = f"{short_period}日均线突破{long_period}日均线，形成金叉，发生于：{cross_date.strftime('%Y-%m-%d')}"
            else:  # death_cross
                base_msg = f"{short_period}日均线跌破{long_period}日均线，形成死叉，发生于：{cross_date.strftime('%Y-%m-%d')}"
            
            # 只有最近 10 天的交叉才添加颜色
            if use_colors and days_diff <= 10:
                if cross_signal == "golden_cross":
                    alerts.append(f"{Colors.GREEN}{base_msg}{Colors.END}")
                else:  # death_cross
                    alerts.append(f"{Colors.RED}{base_msg}{Colors.END}")
            else:
                alerts.append(base_msg)
    
    return alerts
