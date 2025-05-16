"""包含所有样式信息的模块

此模块提供了所有的UI样式定义，遵循Linear App的简约现代设计风格。
提供清晰的视觉层次结构，专业和谐的配色方案，适合长时间阅读。
"""

LINEAR_COLORS = {
    # 主要颜色
    "primary": "#5E6AD2",  # Linear的主色调蓝紫色
    "primary_light": "#8F96E8",
    "primary_dark": "#4954B8",
    
    # 中性色
    "background": "#F7F8FB",  # 淡灰色背景
    "background_alt": "#FFFFFF",  # 白色元素背景
    "border": "#E4E7EC",  # 边框色
    
    # 文本颜色
    "text_primary": "#202124",  # 主文本色
    "text_secondary": "#525866",  # 次要文本
    "text_tertiary": "#8A919E",  # 第三级文本
    
    # 语义颜色
    "positive": "#40B66B",  # 正面/上涨
    "negative": "#D82C0D",  # 负面/下跌
    "warning": "#F2A91B",  # 警告/注意
    "info": "#0070F3",  # 信息

    # 图表颜色
    "chart_colors": [
        "#5E6AD2",  # 主色调
        "#40B66B",  # 绿色
        "#D82C0D",  # 红色
        "#F2A91B",  # 黄色
        "#0070F3",  # 蓝色
    ],
}

# 字体设置
FONTS = {
    "primary": "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, sans-serif",
    "monospace": "'SF Mono', SFMono-Regular, Consolas, 'Liberation Mono', Menlo, Courier, monospace",
    "display": "'SF Pro Display', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, sans-serif"
}

# CSS样式
CSS_STYLES = f"""
    /* 全局样式 */
    body {{
        font-family: {FONTS["primary"]};
        font-size: 15px;
        line-height: 1.6;
        color: {LINEAR_COLORS["text_primary"]};
        background-color: {LINEAR_COLORS["background"]};
        margin: 0;
        padding: 40px;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        max-width: 1200px;
        margin: 0 auto;
    }}
    
    /* 标题样式 */
    h1, h2, h3, h4, h5, h6 {{
        font-family: {FONTS["display"]};
        font-weight: 600;
        margin-top: 1.5em;
        margin-bottom: 0.75em;
        letter-spacing: -0.01em;
    }}
    
    h1 {{
        font-size: 2.5rem;
        color: {LINEAR_COLORS["primary"]};
        border-bottom: 1px solid {LINEAR_COLORS["border"]};
        padding-bottom: 0.5rem;
        margin-bottom: 1.5rem;
        font-weight: 700;
    }}
    
    h2 {{
        font-size: 2rem;
        color: {LINEAR_COLORS["text_primary"]};
        margin-top: 2.5rem;
    }}
    
    h3 {{
        font-size: 1.5rem;
        color: {LINEAR_COLORS["text_primary"]};
    }}
    
    h4 {{
        font-size: 1.25rem;
        color: {LINEAR_COLORS["text_primary"]};
    }}
    
    /* 卡片样式 */
    .card {{
        background-color: {LINEAR_COLORS["background_alt"]};
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05), 0 1px 2px rgba(0,0,0,0.05);
        margin-bottom: 24px;
        overflow: hidden;
        transition: box-shadow 0.2s ease;
    }}
    
    .card:hover {{
        box-shadow: 0 2px 8px rgba(0,0,0,0.08), 0 4px 12px rgba(0,0,0,0.05);
    }}
    
    .card-header {{
        padding: 20px 24px 16px;
        border-bottom: 1px solid {LINEAR_COLORS["border"]};
        display: flex;
        align-items: center;
        justify-content: space-between;
    }}
    
    .card-body {{
        padding: 24px;
    }}
    
    /* 表格样式 */
    table {{
        border-collapse: separate;
        border-spacing: 0;
        width: 100%;
        margin-bottom: 24px;
        border-radius: 8px;
        overflow: hidden;
        background: {LINEAR_COLORS["background_alt"]};
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }}
    
    th {{
        background-color: {LINEAR_COLORS["background"]};
        color: {LINEAR_COLORS["text_primary"]};
        font-weight: 600;
        text-align: left;
        padding: 16px 20px;
        border-bottom: 1px solid {LINEAR_COLORS["border"]};
        font-size: 0.9rem;
    }}
    
    td {{
        padding: 12px 20px;
        border-bottom: 1px solid {LINEAR_COLORS["border"]};
        color: {LINEAR_COLORS["text_primary"]};
        font-size: 0.95rem;
    }}
    
    tr:last-child td {{
        border-bottom: none;
    }}
    
    /* 状态样式 */
    .up {{
        color: {LINEAR_COLORS["positive"]};
        font-weight: 500;
    }}
    
    .down {{
        color: {LINEAR_COLORS["negative"]};
        font-weight: 500;
    }}
    
    .alert {{
        color: {LINEAR_COLORS["warning"]};
        font-weight: 500;
    }}
    
    .golden-cross {{
        color: {LINEAR_COLORS["positive"]};
        font-weight: 500;
        display: flex;
        align-items: center;
    }}
    
    .golden-cross::before {{
        content: "";
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: {LINEAR_COLORS["positive"]};
        margin-right: 10px;
    }}
    
    .death-cross {{
        color: {LINEAR_COLORS["negative"]};
        font-weight: 500;
        display: flex;
        align-items: center;
    }}
    
    .death-cross::before {{
        content: "";
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: {LINEAR_COLORS["negative"]};
        margin-right: 10px;
    }}
    
    /* 图片样式 */
    img {{
        max-width: 100%;
        height: auto;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }}
    
    /* 链接样式 */
    a {{
        color: {LINEAR_COLORS["primary"]};
        text-decoration: none;
        transition: color 0.2s ease;
    }}
    
    a:hover {{
        color: {LINEAR_COLORS["primary_dark"]};
        text-decoration: underline;
    }}
    
    /* 警报列表样式 */
    ul {{
        list-style-type: none;
        padding-left: 0;
    }}
    
    li {{
        padding: 10px 16px;
        border-left: 3px solid transparent;
        margin-bottom: 8px;
        background-color: {LINEAR_COLORS["background"]};
        border-radius: 0 4px 4px 0;
        transition: all 0.2s ease;
    }}
    
    li.golden-cross {{
        border-left-color: {LINEAR_COLORS["positive"]};
        background-color: rgba(64, 182, 107, 0.05);
    }}
    
    li.death-cross {{
        border-left-color: {LINEAR_COLORS["negative"]};
        background-color: rgba(216, 44, 13, 0.05);
    }}
    
    /* 重要指标样式 */
    .metrics-container {{
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
        grid-gap: 16px;
        margin-bottom: 24px;
    }}
    
    .metric-card {{
        background-color: {LINEAR_COLORS["background_alt"]};
        border-radius: 8px;
        padding: 16px;
        display: flex;
        flex-direction: column;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }}
    
    .metric-name {{
        font-size: 0.9rem;
        color: {LINEAR_COLORS["text_tertiary"]};
        margin-bottom: 4px;
    }}
    
    .metric-value {{
        font-size: 1.8rem;
        font-weight: 600;
        color: {LINEAR_COLORS["text_primary"]};
        line-height: 1.2;
        margin-bottom: 4px;
    }}
    
    .metric-change {{
        font-size: 0.9rem;
    }}
    
    /* 响应式设计 */
    @media screen and (max-width: 768px) {{
        body {{
            padding: 20px;
        }}
        
        .metrics-container {{
            grid-template-columns: repeat(2, 1fr);
        }}
        
        h1 {{
            font-size: 2rem;
        }}
        
        h2 {{
            font-size: 1.75rem;
        }}
        
        table {{
            display: block;
            overflow-x: auto;
        }}
    }}
    
    @media screen and (max-width: 480px) {{
        .metrics-container {{
            grid-template-columns: 1fr;
        }}
    }}
"""

# ANSI颜色代码
class Colors:
    """ANSI颜色代码"""
    # 基本颜色
    END = '\033[0m'
    BLACK = '\033[30m'
    BLUE = '\033[34m'
    CYAN = '\033[36m'
    GREEN = '\033[32m'
    MAGENTA = '\033[35m'
    RED = '\033[31m'
    WHITE = '\033[37m'
    YELLOW = '\033[33m'
    
    # 样式
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# 获取CSS样式
def get_css_styles():
    """获取CSS样式"""
    return CSS_STYLES

# 获取配色方案
def get_color_scheme():
    """获取配色方案"""
    return LINEAR_COLORS