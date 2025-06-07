"""
KEEN 後端架構關聯圖生成器
KEEN Backend Architecture Relationship Diagram Generator

作者 / Author: Odindino
日期 / Date: 2025-06-07
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np

# 設定中文字體
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

def create_architecture_diagram():
    """創建 KEEN 後端架構關聯圖"""
    
    fig, ax = plt.subplots(figsize=(16, 12))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # 定義顏色方案
    colors = {
        'session': '#4CAF50',      # 綠色 - 會話層
        'manager': '#2196F3',      # 藍色 - 管理器層
        'proxy': '#FF9800',        # 橙色 - 代理層
        'parser': '#9C27B0',       # 紫色 - 解析器層
        'analyzer': '#F44336',     # 紅色 - 分析器層
        'data': '#607D8B',         # 灰藍色 - 數據模型
        'utils': '#795548'         # 棕色 - 工具層
    }
    
    # 組件定義
    components = {
        # 會話層
        'ExperimentSession': (5, 9, colors['session'], 'core/experiment_session.py'),
        
        # 管理器層
        'TxtManager': (1.5, 7.5, colors['manager'], 'core/type_managers.py'),
        'TopoManager': (3.5, 7.5, colors['manager'], 'core/type_managers.py'),
        'CitsManager': (6.5, 7.5, colors['manager'], 'core/type_managers.py'),
        'StsManager': (8.5, 7.5, colors['manager'], 'core/type_managers.py'),
        
        # 代理層
        'FileProxy': (5, 6, colors['proxy'], 'core/file_proxy.py'),
        
        # 解析器層
        'TxtParser': (1.5, 4.5, colors['parser'], 'core/parsers/txt_parser.py'),
        'IntParser': (3.5, 4.5, colors['parser'], 'core/parsers/int_parser.py'),
        'DatParser': (6.5, 4.5, colors['parser'], 'core/parsers/dat_parser.py'),
        
        # 分析器層
        'TxtAnalyzer': (1.5, 3, colors['analyzer'], 'core/analyzers/txt_analyzer.py'),
        'IntAnalyzer': (3.5, 3, colors['analyzer'], 'core/analyzers/int_analyzer.py'),
        'CitsAnalyzer': (6.5, 3, colors['analyzer'], 'core/analyzers/cits_analyzer.py'),
        'DatAnalyzer': (8.5, 3, colors['analyzer'], 'core/analyzers/dat_analyzer.py'),
        
        # 數據模型層
        'DataModels': (5, 1.5, colors['data'], 'core/data_models.py'),
        
        # 工具層
        'Mathematics': (1.5, 0.5, colors['utils'], 'core/mathematics/geometry.py'),
        'Algorithms': (3.5, 0.5, colors['utils'], 'core/utils/algorithms.py'),
        'Visualization': (6.5, 0.5, colors['utils'], 'core/visualization/'),
        'Analysis': (8.5, 0.5, colors['utils'], 'core/analysis/')
    }
    
    # 繪製組件
    boxes = {}
    for name, (x, y, color, path) in components.items():
        # 主要組件框
        box = FancyBboxPatch(
            (x-0.6, y-0.3), 1.2, 0.6,
            boxstyle="round,pad=0.02",
            facecolor=color,
            edgecolor='black',
            alpha=0.8,
            linewidth=1.5
        )
        ax.add_patch(box)
        boxes[name] = (x, y)
        
        # 組件名稱
        ax.text(x, y+0.05, name, ha='center', va='center', 
                fontsize=9, fontweight='bold', color='white')
        
        # 檔案路徑
        ax.text(x, y-0.15, path, ha='center', va='center', 
                fontsize=7, color='white', style='italic')
    
    # 定義連接關係
    connections = [
        # 會話 -> 管理器
        ('ExperimentSession', 'TxtManager'),
        ('ExperimentSession', 'TopoManager'),
        ('ExperimentSession', 'CitsManager'),
        ('ExperimentSession', 'StsManager'),
        
        # 會話 -> 代理
        ('ExperimentSession', 'FileProxy'),
        
        # 管理器 -> 解析器
        ('TxtManager', 'TxtParser'),
        ('TopoManager', 'IntParser'),
        ('CitsManager', 'DatParser'),
        ('StsManager', 'DatParser'),
        
        # 管理器 -> 分析器
        ('TxtManager', 'TxtAnalyzer'),
        ('TopoManager', 'IntAnalyzer'),
        ('CitsManager', 'CitsAnalyzer'),
        ('StsManager', 'DatAnalyzer'),
        
        # 代理 -> 分析器
        ('FileProxy', 'TxtAnalyzer'),
        ('FileProxy', 'IntAnalyzer'),
        ('FileProxy', 'CitsAnalyzer'),
        ('FileProxy', 'DatAnalyzer'),
        
        # 所有組件 -> 數據模型
        ('TxtParser', 'DataModels'),
        ('IntParser', 'DataModels'),
        ('DatParser', 'DataModels'),
        ('TxtAnalyzer', 'DataModels'),
        ('IntAnalyzer', 'DataModels'),
        ('CitsAnalyzer', 'DataModels'),
        ('DatAnalyzer', 'DataModels'),
        
        # 分析器 -> 工具
        ('IntAnalyzer', 'Mathematics'),
        ('CitsAnalyzer', 'Mathematics'),
        ('IntAnalyzer', 'Algorithms'),
        ('CitsAnalyzer', 'Algorithms'),
        ('TxtAnalyzer', 'Visualization'),
        ('IntAnalyzer', 'Visualization'),
        ('CitsAnalyzer', 'Visualization'),
        ('DatAnalyzer', 'Visualization'),
        ('CitsAnalyzer', 'Analysis'),
        ('IntAnalyzer', 'Analysis')
    ]
    
    # 繪製連接線
    for start, end in connections:
        start_pos = boxes[start]
        end_pos = boxes[end]
        
        # 計算連接點
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        
        # 箭頭樣式
        arrow = ConnectionPatch(
            start_pos, end_pos, "data", "data",
            arrowstyle="->", shrinkA=15, shrinkB=15,
            color='gray', alpha=0.6, linewidth=1
        )
        ax.add_patch(arrow)
    
    # 添加圖例
    legend_elements = []
    legend_labels = [
        ('會話管理 / Session', colors['session']),
        ('類型管理器 / Type Managers', colors['manager']),
        ('檔案代理 / File Proxy', colors['proxy']),
        ('解析器 / Parsers', colors['parser']),
        ('分析器 / Analyzers', colors['analyzer']),
        ('數據模型 / Data Models', colors['data']),
        ('工具函式庫 / Utilities', colors['utils'])
    ]
    
    for i, (label, color) in enumerate(legend_labels):
        legend_patch = patches.Patch(color=color, label=label)
        legend_elements.append(legend_patch)
    
    ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0, 1))
    
    # 添加層級標籤
    layer_labels = [
        (0.2, 9, "會話層\nSession Layer", colors['session']),
        (0.2, 7.5, "管理器層\nManager Layer", colors['manager']),
        (0.2, 6, "代理層\nProxy Layer", colors['proxy']),
        (0.2, 4.5, "解析器層\nParser Layer", colors['parser']),
        (0.2, 3, "分析器層\nAnalyzer Layer", colors['analyzer']),
        (0.2, 1.5, "數據模型層\nData Model Layer", colors['data']),
        (0.2, 0.5, "工具層\nUtility Layer", colors['utils'])
    ]
    
    for x, y, label, color in layer_labels:
        ax.text(x, y, label, ha='left', va='center', 
                fontsize=10, fontweight='bold', 
                bbox=dict(boxstyle="round,pad=0.3", facecolor=color, alpha=0.3))
    
    # 添加標題
    ax.text(5, 9.7, 'KEEN 後端架構關聯圖\nKEEN Backend Architecture Relationship Diagram', 
            ha='center', va='center', fontsize=16, fontweight='bold')
    
    # 添加作者資訊
    ax.text(9.8, 0.1, 'Author: Odindino\nDate: 2025-06-07', 
            ha='right', va='bottom', fontsize=8, style='italic')
    
    plt.tight_layout()
    return fig

def create_data_flow_diagram():
    """創建數據流程圖"""
    
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')
    
    # 定義流程步驟
    steps = [
        (1, 5, "原始檔案\nRaw Files\n(.txt/.int/.dat)", '#E91E63'),
        (1, 3.5, "解析器\nParsers\n(TxtParser/IntParser/DatParser)", '#9C27B0'),
        (3, 3.5, "標準數據\nStandardized Data\n(ParseResult)", '#3F51B5'),
        (5, 3.5, "類型管理器\nType Managers\n(TxtManager/TopoManager/CitsManager)", '#2196F3'),
        (7, 3.5, "檔案代理\nFile Proxy\n(統一介面)", '#FF9800'),
        (9, 3.5, "分析器\nAnalyzers\n(各種分析功能)", '#F44336'),
        (9, 2, "分析結果\nAnalysis Results\n(含 Plotly 圖表)", '#4CAF50')
    ]
    
    # 繪製步驟
    for i, (x, y, text, color) in enumerate(steps):
        # 繪製圓形
        circle = plt.Circle((x, y), 0.4, facecolor=color, edgecolor='black', alpha=0.8)
        ax.add_patch(circle)
        
        # 添加文字
        ax.text(x, y, f"{i+1}", ha='center', va='center', 
                fontsize=12, fontweight='bold', color='white')
        
        # 添加說明文字
        ax.text(x, y-0.8, text, ha='center', va='center', 
                fontsize=9, bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.8))
    
    # 繪製箭頭
    arrows = [
        ((1, 4.6), (1, 3.9)),      # 檔案 -> 解析器
        ((1.4, 3.5), (2.6, 3.5)),  # 解析器 -> 標準數據
        ((3.4, 3.5), (4.6, 3.5)),  # 標準數據 -> 類型管理器
        ((5.4, 3.5), (6.6, 3.5)),  # 類型管理器 -> 檔案代理
        ((7.4, 3.5), (8.6, 3.5)),  # 檔案代理 -> 分析器
        ((9, 3.1), (9, 2.4))       # 分析器 -> 結果
    ]
    
    for start, end in arrows:
        arrow = ConnectionPatch(
            start, end, "data", "data",
            arrowstyle="->", shrinkA=5, shrinkB=5,
            color='black', linewidth=2
        )
        ax.add_patch(arrow)
    
    # 添加標題
    ax.text(5, 5.5, 'KEEN 數據處理流程圖\nKEEN Data Processing Flow', 
            ha='center', va='center', fontsize=16, fontweight='bold')
    
    # 添加特性說明
    features = [
        "✓ 統一的數據介面",
        "✓ 智能快取管理",
        "✓ 類型安全保證",
        "✓ 可擴展架構",
        "✓ Plotly 視覺化"
    ]
    
    ax.text(5, 0.8, '\n'.join(features), ha='center', va='center', 
            fontsize=10, bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue', alpha=0.5))
    
    plt.tight_layout()
    return fig

if __name__ == "__main__":
    # 生成架構關聯圖
    fig1 = create_architecture_diagram()
    fig1.savefig('/Users/yangziliang/Git-Projects/keen/backend/architecture_relationship_diagram.png', 
                 dpi=300, bbox_inches='tight')
    
    # 生成數據流程圖
    fig2 = create_data_flow_diagram()
    fig2.savefig('/Users/yangziliang/Git-Projects/keen/backend/data_flow_diagram.png', 
                 dpi=300, bbox_inches='tight')
    
    print("✅ 架構圖已生成:")
    print("📊 architecture_relationship_diagram.png - 架構關聯圖")
    print("🔄 data_flow_diagram.png - 數據流程圖")
    
    plt.show()