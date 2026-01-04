#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根据预设规则筛选符合特定技术形态（Setup）的股票。
"""

import yaml
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def load_config():
    """加载配置文件"""
    try:
        with open('config.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            if not config.get('stocks'):
                print("错误：在配置文件中找不到股票列表")
                return None
            return config
    except Exception as e:
        print(f"加载配置文件时出错：{str(e)}")
        return None

def get_stock_data(symbol, start_date, end_date):
    """获取股票数据并重置索引"""
    try:
        data = yf.download(symbol, start=start_date, end=end_date, progress=False)
        if data.empty:
            print(f"无法获取 {symbol} 的股票数据")
            return None
        # 重置索引以使用基于整数的索引
        data.reset_index(inplace=True)
        return data
    except Exception as e:
        print(f"获取 {symbol} 的股票数据时出错：{str(e)}")
        return None

def check_trend_rule(data, rules):
    """Rule 1: Price is above MA50 and shows a linear upward trend."""
    lookback_period = rules.get('trend_lookback_days', rules['min_days_above_ma50'])
    last_days_data = data.iloc[-lookback_period:]
    days_above_ma50 = (last_days_data['Close'].values > last_days_data['MA50'].values).sum()
    required_days_above = lookback_period * rules['min_days_above_ma50_pct']

    if days_above_ma50 < required_days_above:
        return False, f"过去 {lookback_period} 天内仅 {days_above_ma50} 天高于 MA50 (要求：>{required_days_above:.0f}天)"

    last_days_close = last_days_data['Close'].values
    x = np.arange(len(last_days_close))
    slope, _ = np.polyfit(x, last_days_close, 1)
    if slope <= 0:
        return False, f"趋势为非线性上涨 (斜率：{slope:.2f})"
    return True, ""

def check_consolidation_rule(data, rules):
    """Rule 2: Recent consolidation period and at the top of a recent high."""
    last_consolidation_days = data.iloc[-rules['consolidation_days']:]
    high_in_consolidation = last_consolidation_days['High'].max()
    low_in_consolidation = last_consolidation_days['Low'].min()
    consolidation_range_actual = ((high_in_consolidation - low_in_consolidation) / low_in_consolidation).item()

    if low_in_consolidation.item() == 0 or consolidation_range_actual > rules['consolidation_range']:
        return False, 0, f"盘整范围过大 ({consolidation_range_actual:.2%}, 要求：<{rules['consolidation_range']:.2%})"

    lookback_period = rules.get('trend_lookback_days', rules['min_days_above_ma50'])
    recent_high = data['High'].iloc[-lookback_period:].max()
    consolidation_top_ratio = low_in_consolidation.item() / recent_high.item()
    if consolidation_top_ratio < rules['consolidation_top_range']:
        return False, 0, f"盘整位置过低 ({consolidation_top_ratio:.2%}, 要求：>{rules['consolidation_top_range']:.2%})"
    return True, high_in_consolidation, ""

def check_pullback_rule(data, rules):
    """Rule 3: Pullback from a recent high."""
    high_pos = data['High'].iloc[-rules['max_pullback_days']:].idxmax()
    current_pos = data.index[-1]
    days_since_high = current_pos - high_pos
    if not (rules['min_pullback_days'] <= days_since_high.item() <= rules['max_pullback_days']):
        return False, f"回调天数为 {days_since_high.item()} 天 (要求：{rules['min_pullback_days']}-{rules['max_pullback_days']} 天)"
    return True, ""

def check_ma_proximity_rule(data, rules):
    """Rule 4: Close to MA50."""
    last_close = data['Close'].values[-1]
    last_ma50 = data['MA50'].values[-1]
    distance_from_ma50 = (last_close - last_ma50) / last_ma50
    if distance_from_ma50 > rules['max_distance_from_ma50']:
        return False, f"收盘价距离MA50过远 ({distance_from_ma50.item():.2%}, 要求: <{rules['max_distance_from_ma50']:.2%})"
    return True, ""

def check_breakout_rule(data, high_in_consolidation):
    """Rule 5: Breakout from consolidation trendline."""
    last_close = data['Close'].iloc[-1]
    if last_close < high_in_consolidation:
        return False, f"收盘价 {last_close:.2f} 未突破盘整高点 {high_in_consolidation:.2f}"
    return True, ""

def check_setup(data, rules):
    """
    Checks if a stock meets the setup criteria and returns the reason for failure.
    Returns: (bool, str) - (True, "Success") or (False, "Reason for failure")
    """
    lookback_period = rules.get('trend_lookback_days', rules['min_days_above_ma50'])
    if len(data) < lookback_period:
        return False, f"数据不足 (少于 {lookback_period} 天)"

    trend_passed, reason = check_trend_rule(data, rules)
    if not trend_passed:
        return False, f"规则 1 失败：{reason}"

    consolidation_passed, high_in_consolidation, reason = check_consolidation_rule(data, rules)
    if not consolidation_passed:
        return False, f"规则 2 失败：{reason}"

    pullback_passed, reason = check_pullback_rule(data, rules)
    if not pullback_passed:
        return False, f"规则 3 失败：{reason}"

    ma_proximity_passed, reason = check_ma_proximity_rule(data, rules)
    if not ma_proximity_passed:
        return False, f"规则 4 失败：{reason}"

    breakout_passed, reason = check_breakout_rule(data, high_in_consolidation)
    if not breakout_passed:
        return False, f"规则 5 失败：{reason}"

    return True, "符合所有条件"

def calculate_moving_averages(data):
    """计算移动平均线"""
    data['MA10'] = data['Close'].rolling(window=10).mean()
    data['MA20'] = data['Close'].rolling(window=20).mean()
    data['MA50'] = data['Close'].rolling(window=50).mean()
    return data

def main():
    """主函数"""
    config = load_config()
    if not config:
        return

    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)

    for symbol in config['stocks']:
        print(f"分析股票：{symbol}")
        data = get_stock_data(symbol, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        if data is not None:
            data = calculate_moving_averages(data)
            data.dropna(inplace=True)
            data.reset_index(drop=True, inplace=True)
            if data.empty:
                print(f"  - 数据不足，无法分析 {symbol}")
                continue

            is_setup, reason = check_setup(data, config['rules'])
            if is_setup:
                print(f"  - {symbol} 符合 Setup 条件")
            else:
                print(f"  - {symbol} 不符合 Setup 条件。原因：{reason}")

if __name__ == '__main__':
    main()