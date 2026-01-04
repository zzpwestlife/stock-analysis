"""警报生成模块"""

from .constants import Colors
from .analysis import detect_ema_cross, get_rsi_signal, detect_price_ema_cross, detect_macd_signals, detect_bollinger_signals

def generate_alerts(symbol, data, use_colors=True):
    """
    生成股票警报
    
    Args:
        symbol (str): 股票代码
        data (pd.DataFrame): 股票数据
        use_colors (bool): 是否使用颜色标记，默认为True
    
    Returns:
        list: 警报列表，每个元素是一个包含 'type' 和 'message' 的字典
    """
    try:
        alerts = []
        
        # 检查RSI
        rsi = data['RSI'].iloc[-1].item()
        if rsi > 70:
            alerts.append({'type': 'RSI超买', 'message': f"RSI超买: {rsi:.2f}"})
        elif rsi < 30:
            alerts.append({'type': 'RSI超卖', 'message': f"RSI超卖: {rsi:.2f}"})
        
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
        
        # 检查布林带信号
        bollinger_alerts = get_bollinger_alerts(data, use_colors)
        alerts.extend(bollinger_alerts)
        
        return alerts
        
    except Exception as e:
        print(f"{Colors.RED}Error generating alerts for {symbol}: {str(e)}{Colors.END}")
        return []

def get_bollinger_alerts(data, use_colors=True):
    """
    生成布林带相关的警报
    
    Args:
        data (pd.DataFrame): 股票数据
        use_colors (bool): 是否使用颜色标记，默认为True
    
    Returns:
        list: 警报列表
    """
    alerts = []
    
    try:
        # 获取布林带信号
        signals = detect_bollinger_signals(data)
        
        # 价格突破上轨
        if signals['upper_cross']:
            date_str = signals['upper_date'].strftime('%Y-%m-%d') if signals['upper_date'] else '未知日期'
            alert_type = "布林带_突破上轨"
            msg = f"布林带 {signals['upper_cross']}，发生于：{date_str}"
            if use_colors:
                alerts.append({'type': alert_type, 'message': f"{Colors.RED}{msg}{Colors.END}"}) # 超买通常用红色表示风险
            else:
                alerts.append({'type': alert_type, 'message': msg})
                
        # 价格跌破下轨
        if signals['lower_cross']:
            date_str = signals['lower_date'].strftime('%Y-%m-%d') if signals['lower_date'] else '未知日期'
            alert_type = "布林带_跌破下轨"
            msg = f"布林带 {signals['lower_cross']}，发生于：{date_str}"
            if use_colors:
                alerts.append({'type': alert_type, 'message': f"{Colors.GREEN}{msg}{Colors.END}"}) # 超卖通常用绿色表示机会
            else:
                alerts.append({'type': alert_type, 'message': msg})
                
        # 布林带收口
        if signals['squeeze']:
            date_str = signals['squeeze_date'].strftime('%Y-%m-%d') if signals['squeeze_date'] else '未知日期'
            alert_type = "布林带_收口"
            msg = f"布林带 {signals['squeeze']}，发生于：{date_str}"
            if use_colors:
                alerts.append({'type': alert_type, 'message': f"{Colors.YELLOW}{msg}{Colors.END}"}) # 变盘用黄色
            else:
                alerts.append({'type': alert_type, 'message': msg})
                
        return alerts
    except Exception as e:
        print(f"{Colors.RED}Error generating Bollinger alerts: {str(e)}{Colors.END}")
        return []

def get_price_alerts(data, latest_close, use_colors=True):
    """
    根据价格和均线生成警报
    
    Args:
        data (pd.DataFrame): 股票数据
        latest_close (float): 最新收盘价
        use_colors (bool): 是否使用颜色标记，默认为True
    
    Returns:
        list: 警报列表，每个元素是一个包含 'type' 和 'message' 的字典
    """
    alerts = []
    
    # 检查是否跌破各条均线
    for period in [5, 10, 20, 50]:
        ema = data[f'EMA_{period}'].iloc[-1].item()
        if latest_close < ema:
            alerts.append({'type': f'价格跌破{period}日均线', 'message': f"价格 ({latest_close:.2f}) 跌破 {period}日均线 ({ema:.2f})"})
    
    # 获取最新日期
    latest_date = data.index[-1]
    
    # 检查是否形成金叉或死叉
    for short_period, long_period in [(5, 10), (10, 20), (20, 50)]:
        cross_signal, cross_date = detect_ema_cross(data, short_period, long_period)
        if cross_signal is not None and cross_date is not None:
            # 计算交叉日期与最新日期的天数差
            days_diff = (latest_date - cross_date).days
            
            alert_type = ""
            # 构建基本消息
            if cross_signal == "golden_cross":
                alert_type = f'{short_period}-{long_period}金叉'
                base_msg = f"{short_period}日均线突破{long_period}日均线，形成金叉，发生于：{cross_date.strftime('%Y-%m-%d')}"
            else:  # death_cross
                alert_type = f'{short_period}-{long_period}死叉'
                base_msg = f"{short_period}日均线跌破{long_period}日均线，形成死叉，发生于：{cross_date.strftime('%Y-%m-%d')}"
            
            # 只有最近 10 天的交叉才添加颜色
            if use_colors and days_diff <= 10:
                if cross_signal == "golden_cross":
                    alerts.append({'type': alert_type, 'message': f"{Colors.GREEN}{base_msg}{Colors.END}"})
                else:  # death_cross
                    alerts.append({'type': alert_type, 'message': f"{Colors.RED}{base_msg}{Colors.END}"})
            else:
                alerts.append({'type': alert_type, 'message': base_msg})
    
    return alerts

def get_price_ema_cross_alerts(data, use_colors=True):
    """
    检测价格与EMA的交叉并生成警报
    
    Args:
        data (pd.DataFrame): 股票数据
        use_colors (bool): 是否使用颜色标记，默认为True
    
    Returns:
        list: 警报列表，每个元素是一个包含 'type' 和 'message' 的字典
    """
    alerts = []
    latest_date = data.index[-1]
    
    # 检查价格与EMA5/EMA10的交叉
    for period in [5, 10]:
        cross_signal, cross_date = detect_price_ema_cross(data, period)
        if cross_signal is not None and cross_date is not None:
            days_diff = (latest_date - cross_date).days
            
            alert_type = ""
            if cross_signal == "price_up_cross":
                alert_type = f'价格上穿{period}日均线'
                base_msg = f"价格上穿{period}日均线，发生于：{cross_date.strftime('%Y-%m-%d')}"
            else:  # price_down_cross
                alert_type = f'价格下穿{period}日均线'
                base_msg = f"价格下穿{period}日均线，发生于：{cross_date.strftime('%Y-%m-%d')}"
            
            if use_colors and days_diff <= 10:
                if cross_signal == "price_up_cross":
                    alerts.append({'type': alert_type, 'message': f"{Colors.GREEN}{base_msg}{Colors.END}"})
                else:  # price_down_cross
                    alerts.append({'type': alert_type, 'message': f"{Colors.RED}{base_msg}{Colors.END}"})
            else:
                alerts.append({'type': alert_type, 'message': base_msg})
    
    return alerts

def get_macd_alerts(data, use_colors=True):
    """
    生成MACD相关的警报
    
    Args:
        data (pd.DataFrame): 股票数据
        use_colors (bool): 是否使用颜色标记，默认为True
    
    Returns:
        list: 警报列表，每个元素是一个包含 'type' 和 'message' 的字典
    """
    alerts = []
    
    # 获取MACD信号
    macd_signals = detect_macd_signals(data)
    
    # MACD线与信号线的交叉
    if macd_signals['cross_signal']:
        date_str = macd_signals['cross_date'].strftime('%Y-%m-%d') if macd_signals['cross_date'] else '未知日期'
        alert_type = f"MACD_{macd_signals['cross_signal']}"
        msg = f"MACD {macd_signals['cross_signal']}，发生于：{date_str}"
        if use_colors:
            if '买入' in msg or '金叉' in msg: # 统一判断条件
                alerts.append({'type': alert_type, 'message': f"{Colors.GREEN}{msg}{Colors.END}"})
            elif '卖出' in msg or '死叉' in msg: # 统一判断条件
                alerts.append({'type': alert_type, 'message': f"{Colors.RED}{msg}{Colors.END}"})
            else:
                alerts.append({'type': alert_type, 'message': msg})
        else:
            alerts.append({'type': alert_type, 'message': msg})
    
    # MACD线与零线的交叉
    if macd_signals['zero_cross']:
        date_str = macd_signals['zero_date'].strftime('%Y-%m-%d') if macd_signals['zero_date'] else '未知日期'
        alert_type = f"MACD_{macd_signals['zero_cross']}"
        msg = f"MACD {macd_signals['zero_cross']}，发生于：{date_str}"
        if use_colors:
            if '看涨' in msg or '上穿零轴' in msg: # 统一判断条件
                alerts.append({'type': alert_type, 'message': f"{Colors.GREEN}{msg}{Colors.END}"})
            elif '看跌' in msg or '下穿零轴' in msg: # 统一判断条件
                alerts.append({'type': alert_type, 'message': f"{Colors.RED}{msg}{Colors.END}"})
            else:
                alerts.append({'type': alert_type, 'message': msg})
        else:
            alerts.append({'type': alert_type, 'message': msg})
    
    # MACD背离
    if macd_signals['divergence']:
        date_str = macd_signals['divergence_date'].strftime('%Y-%m-%d') if macd_signals['divergence_date'] else '未知日期'
        alert_type = f"MACD_{macd_signals['divergence']}"
        msg = f"MACD {macd_signals['divergence']}，发生于：{date_str}"
        if use_colors:
            if '买入' in msg or '底背离' in msg : # 统一判断条件
                alerts.append({'type': alert_type, 'message': f"{Colors.GREEN}{msg}{Colors.END}"})
            elif '卖出' in msg or '顶背离' in msg: # 统一判断条件
                alerts.append({'type': alert_type, 'message': f"{Colors.RED}{msg}{Colors.END}"})
            else:
                alerts.append({'type': alert_type, 'message': msg})
        else:
            alerts.append({'type': alert_type, 'message': msg})
    
    # MACD柱状图趋势
    if macd_signals['histogram_trend']:
        date_str = macd_signals['histogram_date'].strftime('%Y-%m-%d') if macd_signals['histogram_date'] else '未知日期'
        alert_type = f"MACD_{macd_signals['histogram_trend']}"
        msg = f"MACD {macd_signals['histogram_trend']}，发生于：{date_str}"
        alerts.append({'type': alert_type, 'message': msg})
    
    return alerts
