"""
CITS (Current Imaging Tunneling Spectroscopy) 數據分析模組

此模組提供專門針對 CITS 數據的分析功能，包括：
- 線段剖面 STS 光譜提取
- STS evolution 分析
- Band alignment 工具
- 數據插值和處理
- 偏壓模式檢測與切割
- 能譜圖和能帶圖生成

作者: KEEN 開發團隊
日期: 2025-06-05
"""

import numpy as np
import logging
from typing import List, Tuple, Dict, Optional, Union
from scipy import interpolate
from scipy.ndimage import map_coordinates
import plotly.graph_objects as go
from plotly.subplots import make_subplots

logger = logging.getLogger(__name__)


class CITSAnalysis:
    """CITS 數據分析類別"""
    
    def __init__(self, cits_data: Dict):
        """
        初始化 CITS 分析器
        
        Args:
            cits_data: 從 DatParser 解析的 CITS 數據
        """
        self.cits_data = cits_data
        self.logger = logging.getLogger(__name__)
        
        # 驗證輸入數據
        if not self._validate_cits_data():
            raise ValueError("輸入的數據不是有效的 CITS 格式")
            
        # 提取基本資訊
        self.data_3d = cits_data['data_3d']  # (n_bias, y, x)
        self.bias_values = cits_data['bias_values']
        self.grid_size = cits_data['grid_size']  # [grid_x, grid_y]
        self.scan_direction = cits_data.get('scan_direction', 'downward')
        
        # 準備顯示用數據
        from ..parsers.dat_parser import DatParser
        self.display_data = DatParser.prepare_cits_for_display(
            self.data_3d, self.scan_direction
        )
        
        self.logger.info(f"CITS 分析器初始化完成：{self.grid_size[0]}×{self.grid_size[1]} 網格，"
                        f"{len(self.bias_values)} 個偏壓點，{self.scan_direction} 掃描")
    
    def _validate_cits_data(self) -> bool:
        """驗證 CITS 數據的有效性"""
        required_keys = ['data_3d', 'bias_values', 'grid_size', 'measurement_mode']
        
        for key in required_keys:
            if key not in self.cits_data:
                self.logger.error(f"缺少必要的鍵：{key}")
                return False
        
        if self.cits_data['measurement_mode'] != 'CITS':
            self.logger.error("不是 CITS 數據")
            return False
            
        data_3d = self.cits_data['data_3d']
        if data_3d.ndim != 3:
            self.logger.error(f"data_3d 維度錯誤：期望 3D，實際 {data_3d.ndim}D")
            return False
            
        return True
    
    def extract_line_profile(self, start_coord: Tuple[int, int], 
                        end_coord: Tuple[int, int],
                        use_display_data: bool = True,
                        sampling_method: str = 'bresenham') -> Dict:
        """
        提取指定線段的 STS 光譜剖面
        
        Args:
            start_coord: 起始座標 (x0, y0)
            end_coord: 終點座標 (x1, y1)
            use_display_data: 是否使用方向修正後的數據
            sampling_method: 採樣方法 'bresenham' 或 'interpolate'
            
        Returns:
            Dict: 包含線段 STS 數據的字典
        """
        try:
            x0, y0 = start_coord
            x1, y1 = end_coord
            
            # 選擇數據源
            data_source = self.display_data if use_display_data else self.data_3d
            
            if sampling_method == 'bresenham':
                # 使用 Bresenham 演算法獲取線段上所有像素點
                x_coords, y_coords = self._bresenham_line(x0, y0, x1, y1)
            else:
                # 使用高密度插值採樣
                x_coords, y_coords = self._dense_sampling(x0, y0, x1, y1)
            
            # 確保座標在範圍內
            x_coords = np.clip(x_coords, 0, data_source.shape[2]-1)
            y_coords = np.clip(y_coords, 0, data_source.shape[1]-1)
            
            # 提取 STS 數據
            sts_curves = []
            for x, y in zip(x_coords, y_coords):
                sts_curves.append(data_source[:, y, x])
            
            line_sts = np.array(sts_curves).T  # (n_bias, n_points)
            positions = np.arange(len(x_coords))
            
            # 計算物理長度
            physical_length = self._calculate_physical_length(start_coord, end_coord)
            
            result = {
                'line_sts': line_sts,
                'bias_values': self.bias_values,
                'positions': positions,
                'x_coords': x_coords,  # 新增：實際採樣的 x 座標
                'y_coords': y_coords,  # 新增：實際採樣的 y 座標
                'physical_length': physical_length,
                'start_coord': start_coord,
                'end_coord': end_coord,
                'n_points': line_sts.shape[1],
                'n_bias': line_sts.shape[0],
                'sampling_method': sampling_method
            }
            
            self.logger.info(f"線段剖面提取完成：({x0},{y0}) → ({x1},{y1})，"
                        f"{result['n_points']} 點，方法：{sampling_method}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"線段剖面提取失敗：{e}")
            raise

    def _bresenham_line(self, x0: int, y0: int, x1: int, y1: int) -> Tuple[np.ndarray, np.ndarray]:
        """
        Bresenham 線段演算法 - 獲取線段上的所有像素點
        
        Returns:
            Tuple[np.ndarray, np.ndarray]: (x_coords, y_coords)
        """
        points_x = []
        points_y = []
        
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        
        x, y = x0, y0
        
        while True:
            points_x.append(x)
            points_y.append(y)
            
            if x == x1 and y == y1:
                break
                
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
        
        return np.array(points_x), np.array(points_y)

    def _dense_sampling(self, x0: int, y0: int, x1: int, y1: int, 
                    density_factor: float = 2.0) -> Tuple[np.ndarray, np.ndarray]:
        """
        高密度採樣方法
        
        Args:
            density_factor: 密度因子，越大採樣點越多
        """
        distance = np.sqrt((x1-x0)**2 + (y1-y0)**2)
        n_points = max(int(distance * density_factor), 2)
        
        x_coords = np.linspace(x0, x1, n_points).astype(int)
        y_coords = np.linspace(y0, y1, n_points).astype(int)
        
        # 去除重複點
        coords = list(zip(x_coords, y_coords))
        unique_coords = []
        seen = set()
        
        for coord in coords:
            if coord not in seen:
                unique_coords.append(coord)
                seen.add(coord)
        
        if unique_coords:
            x_coords, y_coords = zip(*unique_coords)
            return np.array(x_coords), np.array(y_coords)
        else:
            return np.array([x0]), np.array([y0])

    def _calculate_physical_length(self, start_coord: Tuple[int, int], 
                                end_coord: Tuple[int, int]) -> float:
        """計算物理長度"""
        x0, y0 = start_coord
        x1, y1 = end_coord
        
        if 'x_grid' in self.cits_data and 'y_grid' in self.cits_data:
            x_grid = self.cits_data['x_grid']
            y_grid = self.cits_data['y_grid']
            
            x_range = np.max(x_grid) - np.min(x_grid)
            y_range = np.max(y_grid) - np.min(y_grid)
            x_pixel_size = x_range / self.grid_size[0]
            y_pixel_size = y_range / self.grid_size[1]
            
            return np.sqrt(((x1-x0) * x_pixel_size)**2 + ((y1-y0) * y_pixel_size)**2)
        else:
            return np.sqrt((x1-x0)**2 + (y1-y0)**2)
    
    def detect_bias_pattern(self, method: str = 'simple') -> Dict:
        """
        檢測偏壓掃描模式
        
        Args:
            method: 檢測方法，'simple' 或 'complex'
            
        Returns:
            Dict: 偏壓模式檢測結果
        """
        if method == 'simple':
            return self._detect_bias_pattern_simple(self.bias_values)
        else:
            # 可以在此實現更複雜的檢測方法
            self.logger.warning("複雜檢測方法尚未實現，使用簡單方法")
            return self._detect_bias_pattern_simple(self.bias_values)
    
    def _detect_bias_pattern_simple(self, bias_values: np.ndarray) -> Dict:
        """
        簡單的偏壓模式檢測方法 - 基於最大/最小值檢測
        這是 IVCutter 函數的核心邏輯，高效且實用
        
        Args:
            bias_values: 偏壓值數組
        
        Returns:
            Dict: 檢測結果包含前向/後向掃描段
        """
        if len(bias_values) < 2:
            return {
                'method': 'simple_max_min',
                'forward_segments': [(0, len(bias_values)-1)],
                'backward_segments': [],
                'n_cycles': 1,
                'pattern_type': 'single_point' if len(bias_values) == 1 else 'forward_only'
            }
        
        # 找到偏壓的最大值和最小值
        bias_starter = bias_values[0]
        bias_max = np.max(bias_values)
        bias_min = np.min(bias_values)
        
        # 確定掃描的終點值
        if bias_starter == bias_max:
            bias_ender = bias_min
        else:
            bias_ender = bias_max
        
        # 找到起始點和終點的所有索引位置
        start_points = np.where(bias_values == bias_starter)[0]
        end_points = np.where(bias_values == bias_ender)[0]
        
        self.logger.debug(f"偏壓範圍：{bias_min:.3f}V 到 {bias_max:.3f}V")
        self.logger.debug(f"起始偏壓：{bias_starter:.3f}V (索引：{start_points})")
        self.logger.debug(f"終點偏壓：{bias_ender:.3f}V (索引：{end_points})")
        
        # 確定掃描週期數
        ramp_cycle = len(end_points) 
        
        forward_segments = []
        backward_segments = []
        
        # 分析掃描模式
        if len(start_points) == 1 and len(end_points) == 1:
            # 單一前向掃描
            forward_segments.append((start_points[0], end_points[0]))
            pattern_type = 'single_forward'
            
        elif len(start_points) == len(end_points):
            # 多次前向掃描
            for i in range(len(start_points)):
                forward_segments.append((start_points[i], end_points[i]))
            pattern_type = f'multiple_forward_{len(forward_segments)}f'
            
        elif len(start_points) == (len(end_points) + 1):
            # 來回掃描模式
            for i in range(len(end_points)):
                forward_segments.append((start_points[i], end_points[i]))
                backward_segments.append((end_points[i], start_points[i + 1]))
            pattern_type = f'raster_{len(backward_segments)}'
        else:
            # 預設為單一前向掃描
            forward_segments.append((0, len(bias_values)-1))
            pattern_type = 'unknown_forward'

        self.logger.info(f"檢測到偏壓模式：{pattern_type}")
        self.logger.info(f"前向段數：{len(forward_segments)}，後向段數：{len(backward_segments)}")
        
        return {
            'method': 'simple_max_min',
            'forward_segments': forward_segments,
            'backward_segments': backward_segments,
            'n_cycles': ramp_cycle,
            'pattern_type': pattern_type,
            'bias_starter': bias_starter,
            'bias_ender': bias_ender,
            'start_points': start_points.tolist(),
            'end_points': end_points.tolist()
        }
    
    def slice_data_by_bias(self, line_profile: Dict, 
                          bias_pattern: Dict = None,
                          segment_type: str = 'forward') -> Dict:
        """
        根據偏壓模式切割線段數據
        
        Args:
            line_profile: 從 extract_line_profile 獲得的線段數據
            bias_pattern: 偏壓模式檢測結果，如果為 None 則自動檢測
            segment_type: 'forward', 'backward', 或 'all'
            
        Returns:
            Dict: 切割後的數據
        """
        try:
            if bias_pattern is None:
                bias_pattern = self.detect_bias_pattern()
            
            line_sts = line_profile['line_sts']
            bias_values = line_profile['bias_values']
            
            result = {
                'pattern_info': bias_pattern,
                'segments': {}
            }
            
            # 處理前向段
            if segment_type in ['forward', 'all'] and bias_pattern['forward_segments']:
                forward_data = {}
                for i, (start_idx, end_idx) in enumerate(bias_pattern['forward_segments']):
                    segment_bias = bias_values[start_idx:end_idx+1]
                    segment_data = line_sts[start_idx:end_idx+1, :]
                    
                    forward_data[f'forward_{i+1}'] = {
                        'bias_values': segment_bias,
                        'data': segment_data,
                        'bias_range': (segment_bias[0], segment_bias[-1]),
                        'indices': (start_idx, end_idx)
                    }
                result['segments']['forward'] = forward_data
            
            # 處理後向段
            if segment_type in ['backward', 'all'] and bias_pattern['backward_segments']:
                backward_data = {}
                for i, (start_idx, end_idx) in enumerate(bias_pattern['backward_segments']):
                    segment_bias = bias_values[start_idx:end_idx+1]
                    segment_data = line_sts[start_idx:end_idx+1, :]
                    
                    backward_data[f'backward_{i+1}'] = {
                        'bias_values': segment_bias,
                        'data': segment_data,
                        'bias_range': (segment_bias[0], segment_bias[-1]),
                        'indices': (start_idx, end_idx)
                    }
                result['segments']['backward'] = backward_data
            
            self.logger.info(f"偏壓切割完成：{segment_type} 段，"
                           f"前向 {len(result['segments'].get('forward', {}))} 段，"
                           f"後向 {len(result['segments'].get('backward', {}))} 段")
            
            return result
            
        except Exception as e:
            self.logger.error(f"偏壓切割失敗：{e}")
            raise
    
    def plot_spectrum(self, sliced_data: Dict, 
                     segment_key: str = 'forward_1',
                     show_all_positions: bool = False,
                     max_curves: int = 10) -> go.Figure:
        """
        繪製能譜圖（偏壓 vs 強度）
        
        Args:
            sliced_data: 從 slice_data_by_bias 獲得的切割數據
            segment_key: 要繪製的段，例如 'forward_1', 'backward_1'
            show_all_positions: 是否顯示所有位置的曲線
            max_curves: 最大顯示曲線數
            
        Returns:
            go.Figure: Plotly 圖形對象
        """
        try:
            # 解析段類型和索引
            if '_' in segment_key:
                segment_type, segment_idx = segment_key.split('_', 1)
            else:
                segment_type, segment_idx = segment_key, '1'
            
            if segment_type not in sliced_data['segments']:
                raise ValueError(f"找不到段類型：{segment_type}")
            
            segment_data = sliced_data['segments'][segment_type][segment_key]
            bias_values = segment_data['bias_values']
            data = segment_data['data']  # (n_bias, n_positions)
            
            fig = go.Figure()
            
            if show_all_positions:
                # 顯示所有位置，但限制數量
                n_positions = data.shape[1]
                step = max(1, n_positions // max_curves)
                positions_to_plot = range(0, n_positions, step)
            else:
                # 只顯示幾條代表性曲線
                n_positions = data.shape[1]
                positions_to_plot = np.linspace(0, n_positions-1, 
                                              min(max_curves, n_positions), 
                                              dtype=int)
            
            # 添加光譜曲線
            for i, pos_idx in enumerate(positions_to_plot):
                fig.add_trace(go.Scatter(
                    x=bias_values,
                    y=data[:, pos_idx],
                    mode='lines',
                    name=f'位置 {pos_idx+1}',
                    line=dict(width=1.5),
                    hovertemplate='偏壓: %{x:.3f} V<br>電流: %{y:.2e} A<extra></extra>'
                ))
            
            # 更新圖表布局
            bias_range = segment_data['bias_range']
            fig.update_layout(
                title=f"STS 光譜圖 ({segment_key})<br>"
                      f"<sub>偏壓範圍: {bias_range[0]:.3f}V 到 {bias_range[1]:.3f}V</sub>",
                xaxis_title="偏壓電壓 (V)",
                yaxis_title="電流 (A)",
                width=800,
                height=600,
                template="plotly_white",
                hovermode='closest'
            )
            
            self.logger.info(f"能譜圖繪製完成：{segment_key}，{len(positions_to_plot)} 條曲線")
            return fig
            
        except Exception as e:
            self.logger.error(f"能譜圖繪製失敗：{e}")
            raise
    
    def plot_band_map(self, sliced_data: Dict,
                     segment_key: str = 'forward_1',
                     use_log_scale: bool = False,
                     smooth: bool = True) -> go.Figure:
        """
        繪製能帶圖（位置 vs 偏壓的熱力圖）
        
        Args:
            sliced_data: 從 slice_data_by_bias 獲得的切割數據
            segment_key: 要繪製的段
            use_log_scale: 是否使用對數尺度
            smooth: 是否啟用平滑化
            
        Returns:
            go.Figure: Plotly 圖形對象
        """
        try:
            # 解析段類型和索引
            if '_' in segment_key:
                segment_type, segment_idx = segment_key.split('_', 1)
            else:
                segment_type, segment_idx = segment_key, '1'
            
            if segment_type not in sliced_data['segments']:
                raise ValueError(f"找不到段類型：{segment_type}")
            
            segment_data = sliced_data['segments'][segment_type][segment_key]
            bias_values = segment_data['bias_values']
            data = segment_data['data']  # (n_bias, n_positions)
            
            # 準備強度數據
            if use_log_scale:
                # 使用絕對值的對數
                intensity_data = np.log10(np.abs(data) + 1e-15)
                colorbar_title = "log₁₀|電流| (A)"
                colorscale = 'Viridis'
            else:
                # 使用絕對值
                intensity_data = np.abs(data)
                colorbar_title = "|電流| (A)"
                colorscale = 'Viridis'
            
            # 位置軸
            position_axis = list(range(1, data.shape[1] + 1))
            
            fig = go.Figure()
            
            # 添加熱力圖
            fig.add_trace(go.Heatmap(
                z=intensity_data,
                x=position_axis,
                y=bias_values,
                colorscale=colorscale,
                zsmooth='best' if smooth else False,
                colorbar=dict(
                    title=dict(text=colorbar_title, side="right")
                ),
                hovertemplate='位置: %{x}<br>偏壓: %{y:.3f} V<br>強度: %{z:.2e}<extra></extra>'
            ))
            
            # 更新圖表布局
            bias_range = segment_data['bias_range']
            fig.update_layout(
                title=f"能帶圖 ({segment_key})<br>"
                      f"<sub>偏壓範圍: {bias_range[0]:.3f}V 到 {bias_range[1]:.3f}V | "
                      f"{'對數尺度' if use_log_scale else '線性尺度'} | "
                      f"{'平滑' if smooth else '原始'}</sub>",
                xaxis_title="位置 (像素)",
                yaxis_title="偏壓電壓 (V)",
                width=800,
                height=600,
                template="plotly_white"
            )
            
            self.logger.info(f"能帶圖繪製完成：{segment_key}，"
                           f"{'對數' if use_log_scale else '線性'}尺度")
            return fig
            
        except Exception as e:
            self.logger.error(f"能帶圖繪製失敗：{e}")
            raise
    
    def get_analysis_summary(self) -> Dict:
        """
        獲取分析摘要資訊
        
        Returns:
            Dict: 包含各種統計資訊的摘要
        """
        try:
            bias_pattern = self.detect_bias_pattern()
            
            summary = {
                'data_info': {
                    'grid_size': self.grid_size,
                    'n_bias_points': len(self.bias_values),
                    'bias_range': (float(np.min(self.bias_values)), 
                                 float(np.max(self.bias_values))),
                    'scan_direction': self.scan_direction,
                    'data_shape': list(self.data_3d.shape)
                },
                'bias_pattern': bias_pattern,
                'statistics': {
                    'data_min': float(np.min(self.data_3d)),
                    'data_max': float(np.max(self.data_3d)),
                    'data_mean': float(np.mean(self.data_3d)),
                    'data_std': float(np.std(self.data_3d))
                }
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"生成分析摘要失敗：{e}")
            raise


# 便利函數
def analyze_cits_line(cits_data: Dict, 
                     start_coord: Tuple[int, int],
                     end_coord: Tuple[int, int],
                     segment_type: str = 'forward') -> Dict:
    """
    便利函數：完整的 CITS 線段分析流程
    
    Args:
        cits_data: CITS 數據
        start_coord: 起始座標
        end_coord: 終點座標
        segment_type: 分析的段類型
        
    Returns:
        Dict: 完整的分析結果
    """
    # 創建分析器
    analyzer = CITSAnalysis(cits_data)
    
    # 提取線段剖面
    line_profile = analyzer.extract_line_profile(start_coord, end_coord)
    
    # 檢測偏壓模式
    bias_pattern = analyzer.detect_bias_pattern()
    
    # 切割數據
    sliced_data = analyzer.slice_data_by_bias(line_profile, bias_pattern, segment_type)
    
    # 生成摘要
    summary = analyzer.get_analysis_summary()
    
    return {
        'analyzer': analyzer,
        'line_profile': line_profile,
        'bias_pattern': bias_pattern,
        'sliced_data': sliced_data,
        'summary': summary
    }