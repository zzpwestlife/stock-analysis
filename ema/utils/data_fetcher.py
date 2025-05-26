"""
股票数据获取模块
包含数据下载和缓存功能，以避免API限流
"""

import yfinance as yf
import pandas as pd
import os
from datetime import datetime
import time
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class DataFetcher:
    def __init__(self, cache_dir: str = 'data_cache'):
        """
        初始化数据获取器
        Args:
            cache_dir: 缓存目录路径
        """
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        self.retry_count = 3
        self.retry_delay = 5  # 初始重试延迟（秒）
        self.max_delay = 60   # 最大延迟（秒）

    def _get_cache_filename(self, symbol: str, start_date: str, end_date: str) -> str:
        """生成缓存文件名"""
        return os.path.join(
            self.cache_dir,
            f"{symbol}_{start_date}_{end_date}.pkl"
        )

    def _is_cache_valid(self, filename: str, max_age_days: int = 7) -> bool:
        """检查缓存是否有效"""
        if not os.path.exists(filename):
            return False
            
        file_age = (datetime.now() - datetime.fromtimestamp(os.path.getmtime(filename))).days
        return file_age <= max_age_days

    def fetch_data(self, symbol: str, start_date: str, end_date: str, interval: str = '1d') -> Optional[pd.DataFrame]:
        """
        获取股票数据
        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            interval: 时间间隔
        Returns:
            股票数据DataFrame，如果失败返回None
        """
        cache_file = self._get_cache_filename(symbol, start_date, end_date)
        
        # 尝试使用缓存
        if self._is_cache_valid(cache_file):
            logger.info(f"Using cached data for {symbol}")
            return pd.read_pickle(cache_file)

        # 重试逻辑
        for attempt in range(self.retry_count):
            try:
                logger.info(f"Fetching data for {symbol} (attempt {attempt + 1}/{self.retry_count})")
                data = yf.download(symbol, start=start_date, end=end_date, interval=interval)
                
                if not data.empty:
                    # 保存到缓存
                    data.to_pickle(cache_file)
                    return data
                
                logger.warning(f"No data received for {symbol}")
                return None
                
            except Exception as e:
                if attempt == self.retry_count - 1:  # 最后一次尝试失败
                    logger.error(f"Failed to fetch data for {symbol}: {str(e)}")
                    return None
                    
                # 计算指数退避延迟
                delay = min(self.retry_delay * (2 ** attempt), self.max_delay)
                logger.warning(f"Retrying in {delay} seconds... ({str(e)})")
                time.sleep(delay)

        return None
