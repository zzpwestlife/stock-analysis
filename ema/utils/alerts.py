"""警报生成模块"""

from .constants import Colors
from .analysis import detect_ema_cross, get_rsi_signal, detect_price_ema_cross, detect_macd_signals

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
        
        # 检查价格与EMA5/EMA10的交叉
        price_ema_alerts = get_price_ema_cross_alerts(data, use_colors)
        alerts.extend(price_ema_alerts)
        
        # 检查MACD信号
        macd_alerts = get_macd_alerts(data, use_colors)
        alerts.extend(macd_alerts)
        
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
        if cross_signal is not None and cross_date is not None:
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

def get_price_ema_cross_alerts(data, use_colors=True):
    """
    检测价格与EMA的交叉并生成警报
    
    Args:
        data (pd.DataFrame): 股票数据
        use_colors (bool): 是否使用颜色标记，默认为True
    
    Returns:
        list: 警报列表
    """
    alerts = []
    latest_date = data.index[-1]
    
    # 检查价格与EMA5/EMA10的交叉
    for period in [5, 10]:
        cross_signal, cross_date = detect_price_ema_cross(data, period)
        if cross_signal is not None and cross_date is not None:
            days_diff = (latest_date - cross_date).days
            
            if cross_signal == "price_up_cross":
                base_msg = f"价格上穿{period}日均线，发生于：{cross_date.strftime('%Y-%m-%d')}"
            else:  # price_down_cross
                base_msg = f"价格下穿{period}日均线，发生于：{cross_date.strftime('%Y-%m-%d')}"
            
            if use_colors and days_diff <= 10:
                if cross_signal == "price_up_cross":
                    alerts.append(f"{Colors.GREEN}{base_msg}{Colors.END}")
                else:  # price_down_cross
                    alerts.append(f"{Colors.RED}{base_msg}{Colors.END}")
            else:
                alerts.append(base_msg)
    
    return alerts

def get_macd_alerts(data, use_colors=True):
    """
    生成MACD相关的警报
    
    Args:
        data (pd.DataFrame): 股票数据
        use_colors (bool): 是否使用颜色标记，默认为True
    
    Returns:
        list: 警报列表
    """
    alerts = []
    
    # 获取MACD信号
    macd_signals = detect_macd_signals(data)
    
    # MACD线与信号线的交叉
    if macd_signals['cross_signal']:
        date_str = macd_signals['cross_date'].strftime('%Y-%m-%d') if macd_signals['cross_date'] else '未知日期'
        msg = f"MACD {macd_signals['cross_signal']}，发生于：{date_str}"
        if use_colors:
            if '买入' in msg:
                alerts.append(f"{Colors.GREEN}{msg}{Colors.END}")
            elif '卖出' in msg:
                alerts.append(f"{Colors.RED}{msg}{Colors.END}")
        else:
            alerts.append(msg)
    
    # MACD线与零线的交叉
    if macd_signals['zero_cross']:
        date_str = macd_signals['zero_date'].strftime('%Y-%m-%d') if macd_signals['zero_date'] else '未知日期'
        msg = f"MACD {macd_signals['zero_cross']}，发生于：{date_str}"
        if use_colors:
            if '看涨' in msg:
                alerts.append(f"{Colors.GREEN}{msg}{Colors.END}")
            elif '看跌' in msg:
                alerts.append(f"{Colors.RED}{msg}{Colors.END}")
        else:
            alerts.append(msg)
    
    # MACD背离
    if macd_signals['divergence']:
        date_str = macd_signals['divergence_date'].strftime('%Y-%m-%d') if macd_signals['divergence_date'] else '未知日期'
        msg = f"MACD {macd_signals['divergence']}，发生于：{date_str}"
        if use_colors:
            if '买入' in msg:
                alerts.append(f"{Colors.GREEN}{msg}{Colors.END}")
            elif '卖出' in msg:
                alerts.append(f"{Colors.RED}{msg}{Colors.END}")
        else:
            alerts.append(msg)
    
    # MACD柱状图趋势
    if macd_signals['histogram_trend']:
        date_str = macd_signals['histogram_date'].strftime('%Y-%m-%d') if macd_signals['histogram_date'] else '未知日期'
        msg = f"MACD {macd_signals['histogram_trend']}，发生于：{date_str}"
        alerts.append(msg)
    
    return alerts
    alerts = []
    latest_date = data.index[-1]
    
    # 检查价格与EMA5和EMA10的交叉
    for period in [5, 10]:
        cross_signal, cross_date = detect_price_ema_cross(data, period)
        if cross_signal is not None and cross_date is not None:
            # 计算交叉日期与最新日期的天数差
            days_diff = (latest_date - cross_date).days
            
            # 构建基本消息
            if cross_signal == "price_up_cross":
                base_msg = f"价格上穿{period}日均线，发生于：{cross_date.strftime('%Y-%m-%d')}"
            else:  # price_down_cross
                base_msg = f"价格下穿{period}日均线，发生于：{cross_date.strftime('%Y-%m-%d')}"
            
            # 只有最近 10 天的交叉才添加颜色
            if use_colors and days_diff <= 10:
                if cross_signal == "price_up_cross":
                    alerts.append(f"{Colors.GREEN}{base_msg}{Colors.END}")
                else:  # price_down_cross
                    alerts.append(f"{Colors.RED}{base_msg}{Colors.END}")
            else:
                alerts.append(base_msg)
    
    return alerts
