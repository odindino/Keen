"""
CITS (Current Imaging Tunneling Spectroscopy) 數據分析模組

此模組提供專門針對 CITS 數據的分析功能，包括：
- 線段剖面 STS 光譜提取
- STS evolution 分析
- Band alignment 工具
- 數據插值和處理

作者: KEEN 開發團隊
日期: 2025-05-31
"""

import numpy as np
import logging
from typing import List, Tuple, Dict, Optional, Union
from scipy import interpolate
from scipy.ndimage import map_coordinates

logger = logging.getLogger(__name__)


class CITSAnalysis:
    """CITS 數據分析類別"""
    
    @staticmethod
    def extract_line_sts_spectra(
        data_3d: np.ndarray,
        pixel_start: List[int],
        pixel_end: List[int],
        bias_values: np.ndarray,
        physical_length: float,
        interpolation_method: str = 'linear'
    ) -> Dict:
        """
        從3D CITS數據中提取線段上的STS光譜
        
        Args:
            data_3d: 3D CITS數據 shape: (n_bias, grid_y, grid_x)
            pixel_start: 起始像素座標 [row, col]
            pixel_end: 終止像素座標 [row, col]
            bias_values: 偏壓值陣列
            physical_length: 線段物理長度 (nm)
            interpolation_method: 插值方法 ('linear', 'nearest', 'cubic')
            
        Returns:
            dict: 包含線段STS數據的字典
        """
        try:
            logger.info(f"開始提取CITS線段STS光譜: {pixel_start} -> {pixel_end}")
            
            # 計算線段上的採樣點數
            pixel_distance = max(
                abs(pixel_end[0] - pixel_start[0]),
                abs(pixel_end[1] - pixel_start[1]),
                10  # 最少10個點
            )
            n_points = max(pixel_distance, 50)  # 確保足夠的採樣密度
            
            # 生成線段上的座標
            if n_points > 1:
                rows = np.linspace(pixel_start[0], pixel_end[0], n_points)
                cols = np.linspace(pixel_start[1], pixel_end[1], n_points)
            else:
                rows = np.array([pixel_start[0]])
                cols = np.array([pixel_start[1]])
            
            # 確保座標在有效範圍內
            grid_height, grid_width = data_3d.shape[1], data_3d.shape[2]
            rows = np.clip(rows, 0, grid_height - 1)
            cols = np.clip(cols, 0, grid_width - 1)
            
            # 提取每個位置的完整STS光譜
            sts_spectra = []
            line_positions = []
            valid_indices = []
            
            for i, (row, col) in enumerate(zip(rows, cols)):
                try:
                    # 使用不同的插值方法
                    if interpolation_method == 'nearest':
                        # 最近鄰插值
                        row_idx = int(round(row))
                        col_idx = int(round(col))
                        spectrum = data_3d[:, row_idx, col_idx]
                        
                    elif interpolation_method == 'linear':
                        # 雙線性插值
                        spectrum = CITSAnalysis._bilinear_interpolate_spectrum(
                            data_3d, row, col
                        )
                        
                    elif interpolation_method == 'cubic':
                        # 三次插值（使用scipy的map_coordinates）
                        coordinates = np.array([[row], [col]])
                        spectrum = np.zeros(data_3d.shape[0])
                        for bias_idx in range(data_3d.shape[0]):
                            spectrum[bias_idx] = map_coordinates(
                                data_3d[bias_idx], coordinates, 
                                order=3, mode='nearest'
                            )[0]
                    
                    sts_spectra.append(spectrum.tolist())
                    
                    # 計算沿線段的相對位置
                    position_ratio = i / (n_points - 1) if n_points > 1 else 0
                    physical_position = position_ratio * physical_length
                    line_positions.append(physical_position)
                    valid_indices.append(i)
                    
                except Exception as e:
                    logger.warning(f"位置 ({row:.2f}, {col:.2f}) 插值失敗: {e}")
                    continue
            
            if not sts_spectra:
                raise ValueError("無法提取任何有效的STS光譜數據")
            
            # 轉換為numpy陣列以便後續處理
            sts_spectra_array = np.array(sts_spectra)  # shape: (n_positions, n_bias)
            
            # 計算統計資訊
            stats = CITSAnalysis._calculate_sts_statistics(sts_spectra_array, bias_values)
            
            logger.info(f"成功提取 {len(sts_spectra)} 個位置的STS光譜")
            
            return {
                'line_positions': line_positions,           # 沿線段的物理位置 (nm)
                'bias_values': bias_values.tolist(),        # 偏壓軸 (mV)
                'sts_spectra': sts_spectra,                 # STS光譜數據 [position][bias]
                'line_length': float(physical_length),      # 線段總長度 (nm)
                'n_positions': len(line_positions),         # 位置點數
                'n_bias': len(bias_values),                 # 偏壓點數
                'interpolation_method': interpolation_method, # 使用的插值方法
                'pixel_coordinates': {                      # 像素座標記錄
                    'rows': rows[valid_indices].tolist(),
                    'cols': cols[valid_indices].tolist()
                },
                'statistics': stats,                        # 統計資訊
                '_sts_spectra_array': sts_spectra_array     # numpy格式供內部分析使用 (不會序列化)
            }
            
        except Exception as e:
            logger.error(f"提取CITS線段STS光譜失敗: {str(e)}")
            raise
    
    @staticmethod
    def _bilinear_interpolate_spectrum(data_3d: np.ndarray, row: float, col: float) -> np.ndarray:
        """
        對單個位置的完整STS光譜進行雙線性插值
        
        Args:
            data_3d: 3D CITS數據
            row: 行座標（浮點數）
            col: 列座標（浮點數）
            
        Returns:
            np.ndarray: 插值後的STS光譜
        """
        # 獲取四個鄰近像素的整數座標
        row_floor = int(np.floor(row))
        row_ceil = min(row_floor + 1, data_3d.shape[1] - 1)
        col_floor = int(np.floor(col))
        col_ceil = min(col_floor + 1, data_3d.shape[2] - 1)
        
        # 計算權重
        dr = row - row_floor
        dc = col - col_floor
        
        # 雙線性插值
        spectrum = (
            (1 - dr) * (1 - dc) * data_3d[:, row_floor, col_floor] +
            (1 - dr) * dc * data_3d[:, row_floor, col_ceil] +
            dr * (1 - dc) * data_3d[:, row_ceil, col_floor] +
            dr * dc * data_3d[:, row_ceil, col_ceil]
        )
        
        return spectrum
    
    @staticmethod
    def _calculate_sts_statistics(sts_spectra_array: np.ndarray, bias_values: np.ndarray) -> Dict:
        """
        計算STS光譜的統計資訊
        
        Args:
            sts_spectra_array: STS光譜陣列 shape: (n_positions, n_bias)
            bias_values: 偏壓值陣列
            
        Returns:
            dict: 統計資訊
        """
        try:
            # 基本統計
            current_min = np.min(sts_spectra_array)
            current_max = np.max(sts_spectra_array)
            current_mean = np.mean(sts_spectra_array)
            current_std = np.std(sts_spectra_array)
            
            # 沿位置方向的統計（每個偏壓的統計）
            bias_mean = np.mean(sts_spectra_array, axis=0)
            bias_std = np.std(sts_spectra_array, axis=0)
            bias_min = np.min(sts_spectra_array, axis=0)
            bias_max = np.max(sts_spectra_array, axis=0)
            
            # 沿偏壓方向的統計（每個位置的統計）
            position_mean = np.mean(sts_spectra_array, axis=1)
            position_std = np.std(sts_spectra_array, axis=1)
            position_min = np.min(sts_spectra_array, axis=1)
            position_max = np.max(sts_spectra_array, axis=1)
            
            return {
                'global': {
                    'min': float(current_min),
                    'max': float(current_max),
                    'mean': float(current_mean),
                    'std': float(current_std)
                },
                'by_bias': {
                    'mean': bias_mean.tolist(),
                    'std': bias_std.tolist(),
                    'min': bias_min.tolist(),
                    'max': bias_max.tolist()
                },
                'by_position': {
                    'mean': position_mean.tolist(),
                    'std': position_std.tolist(),
                    'min': position_min.tolist(),
                    'max': position_max.tolist()
                }
            }
            
        except Exception as e:
            logger.error(f"計算STS統計資訊失敗: {e}")
            return {}
    
    @staticmethod
    def generate_sts_evolution_data(
        line_positions: List[float],
        bias_values: List[float],
        sts_spectra_array: np.ndarray,
        colormap: str = 'RdBu_r'
    ) -> Dict:
        """
        生成STS evolution圖的數據配置
        
        Args:
            line_positions: 沿線段的位置
            bias_values: 偏壓值
            sts_spectra_array: STS光譜陣列
            colormap: 色彩映射
            
        Returns:
            dict: Plotly heatmap 配置
        """
        try:
            logger.info("生成STS evolution圖數據")
            
            # 數據需要轉置以正確顯示 (bias vs position)
            z_data = sts_spectra_array.T.tolist()  # shape: (n_bias, n_positions)
            
            # 計算數據範圍
            z_min = float(np.min(sts_spectra_array))
            z_max = float(np.max(sts_spectra_array))
            
            # 對稱化colorbar（對於電流數據通常有正負值）
            z_abs_max = max(abs(z_min), abs(z_max))
            
            plotly_data = {
                'type': 'heatmap',
                'z': z_data,
                'x': line_positions,  # X軸：沿線段位置
                'y': bias_values,     # Y軸：偏壓
                'colorscale': colormap,
                'showscale': True,
                'zmin': -z_abs_max,
                'zmax': z_abs_max,
                'colorbar': {
                    'title': {
                        'text': '電流 (A)',
                        'side': 'right'
                    },
                    'thickness': 20,
                    'len': 0.8,
                    'x': 1.02
                },
                'hovertemplate': (
                    '位置: %{x:.2f} nm<br>' +
                    '偏壓: %{y:.1f} mV<br>' +
                    '電流: %{z:.2e} A<br>' +
                    '<extra></extra>'
                )
            }
            
            layout = {
                'title': 'STS Evolution',
                'xaxis': {
                    'title': {'text': '沿線段位置 (nm)'},
                    'showgrid': True,
                    'gridcolor': '#e5e5e5'
                },
                'yaxis': {
                    'title': {'text': '偏壓 (mV)'},
                    'showgrid': True,
                    'gridcolor': '#e5e5e5'
                },
                'margin': {'l': 60, 'r': 80, 't': 50, 'b': 60},
                'autosize': True,
                'plot_bgcolor': 'white',
                'paper_bgcolor': 'white'
            }
            
            logger.info(f"STS evolution數據生成完成: {len(bias_values)} x {len(line_positions)}")
            
            return {
                'data': [plotly_data],
                'layout': layout
            }
            
        except Exception as e:
            logger.error(f"生成STS evolution數據失敗: {e}")
            raise
    
    @staticmethod
    def generate_sts_overlay_data(
        line_positions: List[float],
        bias_values: List[float],
        sts_spectra_array: np.ndarray,
        selected_positions: Optional[List[int]] = None,
        normalize: bool = False
    ) -> Dict:
        """
        生成STS曲線疊加圖的數據配置
        
        Args:
            line_positions: 沿線段的位置
            bias_values: 偏壓值
            sts_spectra_array: STS光譜陣列
            selected_positions: 選擇顯示的位置索引，None則顯示全部
            normalize: 是否標準化曲線
            
        Returns:
            dict: Plotly line plot 配置
        """
        try:
            logger.info("生成STS曲線疊加圖數據")
            
            if selected_positions is None:
                # 如果沒有指定，選擇均勻分佈的幾條曲線
                n_total = len(line_positions)
                n_show = min(10, n_total)  # 最多顯示10條曲線
                selected_positions = np.linspace(0, n_total-1, n_show, dtype=int).tolist()
            
            traces = []
            colors = CITSAnalysis._generate_color_palette(len(selected_positions))
            
            for i, pos_idx in enumerate(selected_positions):
                if pos_idx >= len(line_positions):
                    continue
                
                spectrum = sts_spectra_array[pos_idx]
                
                # 標準化處理
                if normalize:
                    spectrum = (spectrum - np.mean(spectrum)) / np.std(spectrum)
                
                trace = {
                    'type': 'scatter',
                    'mode': 'lines',
                    'x': bias_values,
                    'y': spectrum.tolist(),
                    'name': f'位置 {line_positions[pos_idx]:.1f} nm',
                    'line': {
                        'color': colors[i],
                        'width': 2
                    },
                    'hovertemplate': (
                        '偏壓: %{x:.1f} mV<br>' +
                        ('標準化電流: %{y:.2f}<br>' if normalize else '電流: %{y:.2e} A<br>') +
                        f'位置: {line_positions[pos_idx]:.1f} nm<br>' +
                        '<extra></extra>'
                    )
                }
                traces.append(trace)
            
            layout = {
                'title': 'STS 曲線疊加圖',
                'xaxis': {
                    'title': {'text': '偏壓 (mV)'},
                    'showgrid': True,
                    'gridcolor': '#e5e5e5'
                },
                'yaxis': {
                    'title': {'text': '標準化電流' if normalize else '電流 (A)'},
                    'showgrid': True,
                    'gridcolor': '#e5e5e5'
                },
                'margin': {'l': 60, 'r': 20, 't': 50, 'b': 60},
                'autosize': True,
                'plot_bgcolor': 'white',
                'paper_bgcolor': 'white',
                'showlegend': True,
                'legend': {
                    'x': 1.05,
                    'y': 1,
                    'bgcolor': 'rgba(255,255,255,0.8)'
                }
            }
            
            logger.info(f"STS曲線疊加圖生成完成: {len(traces)} 條曲線")
            
            return {
                'data': traces,
                'layout': layout
            }
            
        except Exception as e:
            logger.error(f"生成STS曲線疊加圖數據失敗: {e}")
            raise
    
    @staticmethod
    def _generate_color_palette(n_colors: int) -> List[str]:
        """
        生成色彩調色板
        
        Args:
            n_colors: 需要的顏色數量
            
        Returns:
            List[str]: 顏色列表（十六進位格式）
        """
        if n_colors <= 10:
            # 預定義的10種不同顏色
            colors = [
                '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
                '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
            ]
            return colors[:n_colors]
        else:
            # 使用HSV色彩空間生成更多顏色
            import colorsys
            colors = []
            for i in range(n_colors):
                hue = i / n_colors
                rgb = colorsys.hsv_to_rgb(hue, 0.8, 0.9)
                hex_color = '#{:02x}{:02x}{:02x}'.format(
                    int(rgb[0] * 255),
                    int(rgb[1] * 255),
                    int(rgb[2] * 255)
                )
                colors.append(hex_color)
            return colors
    
    @staticmethod
    def apply_energy_alignment(
        sts_spectra_array: np.ndarray,
        bias_values: np.ndarray,
        alignment_method: str = 'zero_crossing',
        reference_position: Optional[int] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        應用能帶對齊到STS光譜
        
        Args:
            sts_spectra_array: STS光譜陣列
            bias_values: 偏壓值陣列
            alignment_method: 對齊方法 ('zero_crossing', 'peak', 'manual')
            reference_position: 參考位置索引
            
        Returns:
            Tuple: (對齊後的光譜陣列, 偏移量陣列)
        """
        try:
            logger.info(f"應用能帶對齊: {alignment_method}")
            
            n_positions, n_bias = sts_spectra_array.shape
            energy_shifts = np.zeros(n_positions)
            
            if reference_position is None:
                reference_position = n_positions // 2  # 使用中間位置作為參考
            
            reference_spectrum = sts_spectra_array[reference_position]
            
            for i in range(n_positions):
                if i == reference_position:
                    continue
                
                current_spectrum = sts_spectra_array[i]
                
                if alignment_method == 'zero_crossing':
                    # 尋找零電流交叉點
                    ref_zero = CITSAnalysis._find_zero_crossing(reference_spectrum, bias_values)
                    cur_zero = CITSAnalysis._find_zero_crossing(current_spectrum, bias_values)
                    energy_shifts[i] = ref_zero - cur_zero
                    
                elif alignment_method == 'peak':
                    # 尋找主要峰值位置
                    ref_peak = bias_values[np.argmax(np.abs(reference_spectrum))]
                    cur_peak = bias_values[np.argmax(np.abs(current_spectrum))]
                    energy_shifts[i] = ref_peak - cur_peak
                
                # 其他對齊方法可以在這裡添加
            
            # 應用偏移（這裡返回偏移量，實際的數據偏移需要在前端或後續處理中實現）
            logger.info(f"計算完成能帶對齊偏移量，範圍: {np.min(energy_shifts):.2f} ~ {np.max(energy_shifts):.2f} mV")
            
            return sts_spectra_array, energy_shifts
            
        except Exception as e:
            logger.error(f"能帶對齊失敗: {e}")
            return sts_spectra_array, np.zeros(sts_spectra_array.shape[0])
    
    @staticmethod
    def _find_zero_crossing(spectrum: np.ndarray, bias_values: np.ndarray) -> float:
        """
        尋找光譜的零交叉點
        
        Args:
            spectrum: STS光譜
            bias_values: 偏壓值
            
        Returns:
            float: 零交叉點的偏壓值
        """
        try:
            # 尋找符號變化點
            sign_changes = np.where(np.diff(np.sign(spectrum)) != 0)[0]
            
            if len(sign_changes) == 0:
                # 如果沒有符號變化，返回最接近零的點
                min_idx = np.argmin(np.abs(spectrum))
                return bias_values[min_idx]
            
            # 尋找最接近零偏壓的零交叉點
            zero_crossings = []
            for idx in sign_changes:
                # 線性插值找精確的零交叉點
                x1, x2 = bias_values[idx], bias_values[idx + 1]
                y1, y2 = spectrum[idx], spectrum[idx + 1]
                zero_crossing = x1 - y1 * (x2 - x1) / (y2 - y1)
                zero_crossings.append(zero_crossing)
            
            # 返回最接近零偏壓的零交叉點
            zero_crossings = np.array(zero_crossings)
            closest_idx = np.argmin(np.abs(zero_crossings))
            return zero_crossings[closest_idx]
            
        except Exception as e:
            logger.warning(f"尋找零交叉點失敗: {e}")
            return 0.0
