"""配置加载模块"""

import yaml
from .constants import Colors

def load_config():
    """加载配置文件
    Returns:
        dict: 配置信息
    """
    try:
        with open('config.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            if not config.get('stocks'):
                print(f"{Colors.RED}Error: No stocks found in config file{Colors.END}")
                return None
            return config
    except Exception as e:
        print(f"{Colors.RED}Error loading config file: {str(e)}{Colors.END}")
        return None
