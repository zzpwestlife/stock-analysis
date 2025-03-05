"""常量定义模块"""

class Colors:
    """ANSI 颜色代码"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

# EMA periods for analysis
EMA_PERIODS = [5, 50, 200]  # 短期、中期、长期趋势
