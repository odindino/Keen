#!/usr/bin/env python3
"""
STS Position-Energy 強度圖增強測試和優化
根據對話摘要，繼續改進已實作的 STS 分析函數
"""

import numpy as np
import pandas as pd
from pathlib import Path
import sys
import time
from typing import Dict, List, Tuple, Optional

# Plotly for visualizations
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

# Add parent directory to path for imports
sys.path.append(str(Path.cwd().parent))

# Import custom parsers
from core.parsers.txt_parser import TxtParser
from core.parsers.dat_parser import DatParser

def separate_forward_backward_scans(line_sts: np.ndarray, position_coords: np.ndarray) -> Dict:
    """
    分離正向和反向掃描的 STS 數據
    根據位置座標變化檢測掃描方向改變
    """
    print("🔍 分析掃描模式...")
    
    n_bias, n_positions = line_sts.shape
    print(f"輸入數據: {n_bias} 偏壓點 × {n_positions} 位置點")
    
    # 計算位置變化率來檢測方向改變
    if len(position_coords) < 2:
        print("⚠️  位置點太少，無法檢測掃描方向")
        return {
            'pattern': 'forward_only_1',
            'forward_scans': [line_sts],
            'backward_scans': [],
            'scan_info': {
                'forward_count': 1,
                'backward_count': 0,
                'direction_changes': 0
            }
        }
    
    # 計算位置差分來檢測方向變化
    position_diff = np.diff(position_coords)
    direction_sign = np.sign(position_diff)
    
    # 檢測方向改變點
    direction_changes = np.where(np.diff(direction_sign) != 0)[0] + 1
    
    forward_scans = []
    backward_scans = []
    scan_segments = []
    
    if len(direction_changes) == 0:
        # 單一方向掃描
        if np.mean(direction_sign) > 0:
            forward_scans.append(line_sts)
            pattern = 'forward_only_1'
        else:
            backward_scans.append(line_sts)
            pattern = 'backward_only_1'
        scan_segments = [{'type': 'forward' if np.mean(direction_sign) > 0 else 'backward', 
                         'start': 0, 'end': n_positions-1}]
    else:
        # 多段掃描
        start_idx = 0
        current_direction = direction_sign[0] if len(direction_sign) > 0 else 1
        
        for change_idx in np.append(direction_changes, n_positions-1):
            end_idx = min(change_idx, n_positions-1)
            segment_data = line_sts[:, start_idx:end_idx+1]
            
            if current_direction > 0:
                forward_scans.append(segment_data)
                scan_segments.append({'type': 'forward', 'start': start_idx, 'end': end_idx})
            else:
                backward_scans.append(segment_data)
                scan_segments.append({'type': 'backward', 'start': start_idx, 'end': end_idx})
            
            start_idx = end_idx
            current_direction *= -1  # 切換方向
        
        # 生成模式描述
        fwd_count = len(forward_scans)
        bwd_count = len(backward_scans)
        if fwd_count > 0 and bwd_count > 0:
            pattern = f'bidirectional_{fwd_count}f_{bwd_count}b'
        elif fwd_count > 0:
            pattern = f'forward_only_{fwd_count}'
        else:
            pattern = f'backward_only_{bwd_count}'
    
    result = {
        'pattern': pattern,
        'forward_scans': forward_scans,
        'backward_scans': backward_scans,
        'scan_segments': scan_segments,
        'scan_info': {
            'forward_count': len(forward_scans),
            'backward_count': len(backward_scans),
            'direction_changes': len(direction_changes),
            'total_segments': len(scan_segments)
        }
    }
    
    print(f"✅ 掃描模式檢測完成:")
    print(f"   模式: {pattern}")
    print(f"   正向掃描: {len(forward_scans)} 段")
    print(f"   反向掃描: {len(backward_scans)} 段")
    print(f"   方向改變: {len(direction_changes)} 次")
    
    return result

def normalize_scan_length(scans_data: List[np.ndarray], target_length: int) -> List[np.ndarray]:
    """
    標準化所有掃描段到相同長度
    使用線性插值進行重新取樣
    """
    if not scans_data:
        return []
    
    print(f"🔧 標準化掃描長度至 {target_length} 點...")
    
    normalized_scans = []
    for i, scan in enumerate(scans_data):
        n_bias, n_positions = scan.shape
        
        if n_positions == target_length:
            normalized_scans.append(scan)
            print(f"   段 {i+1}: 長度已正確 ({n_positions} 點)")
        else:
            # 創建插值座標
            old_coords = np.linspace(0, 1, n_positions)
            new_coords = np.linspace(0, 1, target_length)
            
            # 對每個偏壓點進行插值
            normalized_scan = np.zeros((n_bias, target_length))
            for bias_idx in range(n_bias):
                normalized_scan[bias_idx] = np.interp(new_coords, old_coords, scan[bias_idx])
            
            normalized_scans.append(normalized_scan)
            print(f"   段 {i+1}: {n_positions} → {target_length} 點 (插值)")
    
    print("✅ 長度標準化完成")
    return normalized_scans

def create_position_energy_map_enhanced(separated_scans: Dict, bias_voltages: np.ndarray, 
                                       line_length_nm: float) -> go.Figure:
    """
    創建增強版 Position-Energy 強度圖
    支援多段掃描並優化視覺化效果
    """
    print("🎨 創建增強版 Position-Energy 強度圖...")
    
    scan_info = separated_scans['scan_info']
    forward_scans = separated_scans['forward_scans']
    backward_scans = separated_scans['backward_scans']
    
    total_scans = len(forward_scans) + len(backward_scans)
    
    if total_scans == 0:
        print("❌ 沒有可用的掃描數據")
        return go.Figure()
    
    # 決定子圖布局
    if total_scans == 1:
        rows, cols = 1, 1
        subplot_titles = ["Position-Energy Intensity Map"]
    elif total_scans == 2:
        rows, cols = 1, 2
        subplot_titles = ["Forward Scan", "Backward Scan"] if len(forward_scans) > 0 and len(backward_scans) > 0 else ["Scan 1", "Scan 2"]
    elif total_scans <= 4:
        rows, cols = 2, 2
        subplot_titles = [f"Segment {i+1}" for i in range(total_scans)]
    else:
        rows = int(np.ceil(total_scans / 3))
        cols = 3
        subplot_titles = [f"Segment {i+1}" for i in range(total_scans)]
    
    # 創建子圖
    fig = make_subplots(
        rows=rows, cols=cols,
        subplot_titles=subplot_titles[:total_scans],
        shared_xaxes=True,
        shared_yaxes=True,
        vertical_spacing=0.1,
        horizontal_spacing=0.1
    )
    
    all_scans = []
    scan_labels = []
    
    # 處理正向掃描
    for i, scan in enumerate(forward_scans):
        all_scans.append(scan)
        scan_labels.append(f"Forward {i+1}")
    
    # 處理反向掃描
    for i, scan in enumerate(backward_scans):
        all_scans.append(scan)
        scan_labels.append(f"Backward {i+1}")
    
    # 計算全局數據範圍以保持一致的顏色映射
    all_data = np.concatenate([scan.flatten() for scan in all_scans])
    abs_data = np.abs(all_data[all_data != 0])  # 排除零值
    
    if len(abs_data) > 0:
        data_min, data_max = np.min(abs_data), np.max(abs_data)
        dynamic_range = data_max / data_min if data_min > 0 else 1
        
        # 根據動態範圍選擇縮放方式
        if dynamic_range > 1000:
            print(f"   動態範圍大 ({dynamic_range:.0f})，使用對數縮放")
            use_log_scale = True
            vmin, vmax = np.log10(data_min), np.log10(data_max)
        else:
            print(f"   動態範圍適中 ({dynamic_range:.0f})，使用線性縮放")
            use_log_scale = False
            vmin, vmax = -data_max, data_max  # 對稱範圍
    else:
        use_log_scale = False
        vmin, vmax = -1, 1
    
    # 繪製每個掃描段
    for scan_idx, (scan, label) in enumerate(zip(all_scans, scan_labels)):
        n_bias, n_positions = scan.shape
        
        # 計算子圖位置
        row = (scan_idx // cols) + 1
        col = (scan_idx % cols) + 1
        
        # 準備數據
        position_axis = np.linspace(0, line_length_nm, n_positions)
        
        if use_log_scale:
            # 對數縮放
            scan_abs = np.abs(scan)
            scan_abs[scan_abs == 0] = data_min  # 避免 log(0)
            z_data = np.sign(scan) * np.log10(scan_abs)
            colorscale = 'RdBu_r'
        else:
            # 線性縮放
            z_data = scan
            colorscale = 'RdBu_r'
        
        # 添加熱圖
        fig.add_trace(
            go.Heatmap(
                z=z_data,
                x=position_axis,
                y=bias_voltages,
                colorscale=colorscale,
                zmin=vmin,
                zmax=vmax,
                showscale=(scan_idx == 0),  # 只在第一個子圖顯示顏色條
                hovertemplate=
                '<b>%s</b><br>' % label +
                'Position: %{x:.2f} nm<br>' +
                'Bias: %{y:.3f} V<br>' +
                'Current: %{z:.2e} A<br>' +
                '<extra></extra>'
            ),
            row=row, col=col
        )
        
        print(f"   {label}: {n_bias}×{n_positions} 數據點")
    
    # 更新布局
    fig.update_layout(
        title={
            'text': f'Enhanced Position-Energy Intensity Maps<br>'
                   f'<span style="font-size:14px">Pattern: {separated_scans["pattern"]}, '
                   f'Line Length: {line_length_nm:.2f} nm</span>',
            'x': 0.5,
            'xanchor': 'center'
        },
        height=400 * rows,
        width=500 * cols,
        showlegend=False
    )
    
    # 更新軸標籤
    for i in range(rows):
        for j in range(cols):
            if i == rows - 1:  # 底部行
                fig.update_xaxes(title_text="Position (nm)", row=i+1, col=j+1)
            if j == 0:  # 左側列
                fig.update_yaxes(title_text="Bias Voltage (V)", row=i+1, col=j+1)
    
    print("✅ 增強版強度圖創建完成")
    return fig

def test_with_sample_data():
    """使用範例數據測試增強功能"""
    print("🧪 使用範例數據測試增強功能")
    print("=" * 50)
    
    # 創建模擬的雙向掃描數據
    n_bias = 201
    n_positions = 150
    bias_voltages = np.linspace(-1.0, 1.0, n_bias)
    
    # 模擬掃描位置座標 (前進-後退-前進模式)
    segment1 = np.linspace(0, 1, 50)  # 前進
    segment2 = np.linspace(1, 0, 50)  # 後退
    segment3 = np.linspace(0, 1, 50)  # 前進
    position_coords = np.concatenate([segment1, segment2, segment3])
    
    # 創建模擬 STS 數據
    line_sts = np.zeros((n_bias, n_positions))
    
    # 添加一些特徵
    for i, bias in enumerate(bias_voltages):
        for j, pos in enumerate(position_coords):
            # 基本電流-電壓特性
            current = 1e-9 * np.tanh(bias * 10) * (1 + 0.5 * np.sin(pos * 10))
            # 添加噪聲
            noise_scale = abs(current * 0.1) + 1e-12  # 確保非負
            current += np.random.normal(0, noise_scale)
            line_sts[i, j] = current
    
    line_length_nm = 12.5  # 模擬線長
    
    print(f"模擬數據創建完成:")
    print(f"  偏壓範圍: {bias_voltages[0]:.2f} ~ {bias_voltages[-1]:.2f} V")
    print(f"  位置點數: {n_positions}")
    print(f"  線長: {line_length_nm} nm")
    
    # 測試掃描分離
    separated_scans = separate_forward_backward_scans(line_sts, position_coords)
    
    # 測試長度標準化
    all_scans = separated_scans['forward_scans'] + separated_scans['backward_scans']
    if all_scans:
        target_length = 60  # 標準化長度
        normalized_scans = normalize_scan_length(all_scans, target_length)
        
        # 更新分離結果
        fwd_count = len(separated_scans['forward_scans'])
        separated_scans['forward_scans'] = normalized_scans[:fwd_count]
        separated_scans['backward_scans'] = normalized_scans[fwd_count:]
    
    # 創建增強視覺化
    enhanced_fig = create_position_energy_map_enhanced(
        separated_scans, bias_voltages, line_length_nm
    )
    
    # 顯示結果
    enhanced_fig.show()
    
    return separated_scans, enhanced_fig

def test_optimization_features():
    """測試優化功能"""
    print("\n🔧 測試優化功能")
    print("=" * 50)
    
    # 測試不同掃描模式
    test_patterns = [
        "單一正向掃描",
        "雙向掃描",
        "多段正向掃描",
        "複雜多段掃描"
    ]
    
    for pattern in test_patterns:
        print(f"\n測試模式: {pattern}")
        
        if pattern == "單一正向掃描":
            n_pos = 80
            pos_coords = np.linspace(0, 1, n_pos)
        elif pattern == "雙向掃描":
            n_pos = 120
            seg1 = np.linspace(0, 1, 60)
            seg2 = np.linspace(1, 0, 60)
            pos_coords = np.concatenate([seg1, seg2])
        elif pattern == "多段正向掃描":
            n_pos = 180
            seg1 = np.linspace(0, 1, 60)
            seg2 = np.linspace(0, 1, 60)
            seg3 = np.linspace(0, 1, 60)
            pos_coords = np.concatenate([seg1, seg2, seg3])
        else:  # 複雜多段
            n_pos = 240
            seg1 = np.linspace(0, 1, 60)
            seg2 = np.linspace(1, 0, 60)
            seg3 = np.linspace(0, 1, 60)
            seg4 = np.linspace(1, 0, 60)
            pos_coords = np.concatenate([seg1, seg2, seg3, seg4])
        
        # 創建模擬數據
        n_bias = 101
        bias_voltages = np.linspace(-0.5, 0.5, n_bias)
        line_sts = np.random.normal(1e-10, 1e-11, (n_bias, n_pos))
        
        # 測試分離
        separated = separate_forward_backward_scans(line_sts, pos_coords)
        print(f"  結果: {separated['pattern']}")
        print(f"  正向段: {separated['scan_info']['forward_count']}")
        print(f"  反向段: {separated['scan_info']['backward_count']}")

if __name__ == "__main__":
    print("STS Position-Energy 強度圖增強測試")
    print("=" * 60)
    
    # 執行測試
    separated_scans, enhanced_fig = test_with_sample_data()
    
    # 測試優化功能
    test_optimization_features()
    
    print("\n✅ 所有測試完成！")
    print("增強功能已準備好進行實際數據測試")
