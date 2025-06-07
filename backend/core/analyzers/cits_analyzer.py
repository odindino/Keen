"""
CITS 分析器
CITS analyzer

負責協調 CITS 數據的分析工作流和狀態管理
Coordinates CITS data analysis workflow and state management
"""

import numpy as np
from typing import Dict, Any, Optional, Tuple, List

from .base_analyzer import BaseAnalyzer
from ..data_models import CitsData
from ..analysis.cits_analysis import CITSAnalysis
from ..visualization.spectroscopy_plots import SpectroscopyPlotting


class CitsAnalyzer(BaseAnalyzer):
    """
    CITS 分析器
    CITS analyzer
    
    提供 CITS（電流成像隧道光譜）數據的完整分析工作流
    Provides complete analysis workflow for CITS (Current Imaging Tunneling Spectroscopy) data
    """
    
    def __init__(self, cits_data: CitsData):
        """
        初始化 CITS 分析器
        Initialize CITS analyzer
        
        Args:
            cits_data: CitsData 實例 / CitsData instance
        """
        super().__init__(cits_data)
        
        # CITS 特定狀態 / CITS-specific state
        self.cits_analysis: Optional[CITSAnalysis] = None
        self.current_line_profile: Optional[Dict] = None
        self.bias_pattern: Optional[Dict] = None
        
        # 光譜處理歷史 / Spectral processing history
        self.spectral_processing_steps: List[Dict] = []
        
        # 初始化分析 / Initialize analysis
        self._initialize_analysis()
    
    def _initialize_analysis(self) -> None:
        """
        初始化 CITS 分析實例
        Initialize CITS analysis instance
        """
        if isinstance(self.data, CitsData):
            # 轉換為舊格式以適配現有的 CITSAnalysis
            cits_data_dict = {
                'data_3d': self.data.data_3d,
                'bias_values': self.data.bias_values,
                'grid_size': self.data.grid_size,
                'x_range': self.data.x_range,
                'y_range': self.data.y_range
            }
            self.cits_analysis = CITSAnalysis(cits_data_dict)
    
    def analyze(self, **kwargs) -> Dict[str, Any]:
        """
        分析 CITS 數據
        Analyze CITS data
        
        Args:
            **kwargs: 額外參數 / Additional parameters
            
        Returns:
            Dict: 分析結果 / Analysis results
        """
        try:
            if not self.validate_input(**kwargs):
                return self._create_error_result("輸入驗證失敗")
            
            cits_data = self.data
            
            # 檢測偏壓模式 / Detect bias pattern
            if self.cits_analysis:
                self.bias_pattern = self.cits_analysis.detect_bias_pattern()
                
                # 獲取分析摘要 / Get analysis summary
                summary = self.cits_analysis.get_analysis_summary()
            else:
                self.bias_pattern = {'detected': False}
                summary = {'error': 'CITS analysis not initialized'}
            
            # 創建基本可視化 / Create basic visualization
            plots = self._create_basic_plots()
            
            result = {
                'success': True,
                'data': {
                    'cits_data_info': {
                        'shape': cits_data.shape,
                        'bias_range': cits_data.bias_range,
                        'grid_size': cits_data.grid_size,
                        'x_range': cits_data.x_range,
                        'y_range': cits_data.y_range,
                        'n_bias_points': cits_data.n_bias_points,
                        'measurement_mode': cits_data.measurement_mode
                    },
                    'bias_pattern': self.bias_pattern,
                    'summary': summary
                },
                'plots': plots,
                'metadata': {
                    'analyzer_type': 'CITS',
                    'data_type': 'CitsData',
                    'n_bias_points': cits_data.n_bias_points,
                    'measurement_mode': cits_data.measurement_mode,
                    'scan_direction': getattr(self.cits_analysis, 'scan_direction', 'unknown') if self.cits_analysis else 'unknown'
                }
            }
            
            # 記錄分析 / Record analysis
            self._record_analysis(result, "cits_basic_analysis")
            
            return result
            
        except Exception as e:
            error_msg = f"CITS 分析失敗: {str(e)}"
            self._add_error(error_msg)
            return self._create_error_result(error_msg)
    
    def extract_line_profile(self, start_coord: Tuple[int, int], 
                           end_coord: Tuple[int, int],
                           sampling_method: str = 'bresenham') -> Dict[str, Any]:
        """
        提取線段剖面光譜
        Extract line profile spectrum
        
        Args:
            start_coord: 起始座標 (x, y) / Start coordinates (x, y)
            end_coord: 終點座標 (x, y) / End coordinates (x, y)
            sampling_method: 採樣方法 / Sampling method
            
        Returns:
            Dict: 線段剖面數據 / Line profile data
        """
        try:
            if self.cits_analysis is None:
                return self._create_error_result("CITS 分析器未初始化")
            
            # 提取線段剖面 / Extract line profile
            line_profile = self.cits_analysis.extract_line_profile(
                start_coord, end_coord, sampling_method=sampling_method
            )
            
            self.current_line_profile = line_profile
            
            # 創建光譜可視化 / Create spectral visualization
            plots = self._create_line_profile_plots(line_profile)
            
            result = {
                'success': True,
                'data': line_profile,
                'plots': plots,
                'metadata': {
                    'start_coord': start_coord,
                    'end_coord': end_coord,
                    'sampling_method': sampling_method,
                    'n_points': line_profile.get('n_points', 0)
                }
            }
            
            # 記錄分析 / Record analysis
            self._record_analysis(result, f"line_profile_{sampling_method}")
            
            return result
            
        except Exception as e:
            error_msg = f"線段剖面提取失敗: {str(e)}"
            self._add_error(error_msg)
            return self._create_error_result(error_msg)
    
    def get_bias_slice(self, bias_index: int) -> Dict[str, Any]:
        """
        獲取特定偏壓的2D切片
        Get 2D slice at specific bias
        
        Args:
            bias_index: 偏壓索引 / Bias index
            
        Returns:
            Dict: 切片數據 / Slice data
        """
        try:
            cits_data = self.data
            
            # 獲取切片 / Get slice
            slice_data = cits_data.get_bias_slice(bias_index)
            bias_value = cits_data.bias_values[bias_index]
            
            # 創建可視化 / Create visualization
            plots = self._create_bias_slice_plots(slice_data, bias_value, bias_index)
            
            result = {
                'success': True,
                'data': {
                    'slice_data': slice_data,
                    'bias_value': bias_value,
                    'bias_index': bias_index,
                    'shape': slice_data.shape
                },
                'plots': plots,
                'metadata': {
                    'operation': 'bias_slice',
                    'bias_value': bias_value,
                    'bias_index': bias_index
                }
            }
            
            # 記錄分析 / Record analysis
            self._record_analysis(result, f"bias_slice_{bias_index}")
            
            return result
            
        except Exception as e:
            error_msg = f"偏壓切片獲取失敗: {str(e)}"
            self._add_error(error_msg)
            return self._create_error_result(error_msg)
    
    def analyze_conductance_maps(self, **kwargs) -> Dict[str, Any]:
        """
        分析電導圖
        Analyze conductance maps
        
        Args:
            **kwargs: 分析參數 / Analysis parameters
            
        Returns:
            Dict: 電導分析結果 / Conductance analysis results
        """
        try:
            if self.cits_analysis is None:
                return self._create_error_result("CITS 分析器未初始化")
            
            # 計算電導圖 / Calculate conductance maps
            conductance_result = self.cits_analysis.calculate_conductance_maps(**kwargs)
            
            # 將結果存儲到 CitsData / Store results in CitsData
            if conductance_result:
                self.data.conductance_maps.update(conductance_result)
            
            # 創建可視化 / Create visualization
            plots = self._create_conductance_plots(conductance_result)
            
            result = {
                'success': True,
                'data': conductance_result,
                'plots': plots,
                'metadata': {
                    'operation': 'conductance_analysis',
                    'parameters': kwargs
                }
            }
            
            # 記錄分析 / Record analysis
            self._record_analysis(result, "conductance_analysis")
            
            return result
            
        except Exception as e:
            error_msg = f"電導分析失敗: {str(e)}"
            self._add_error(error_msg)
            return self._create_error_result(error_msg)
    
    def _create_basic_plots(self) -> Dict[str, Any]:
        """
        創建基本可視化圖表
        Create basic visualization plots
        """
        try:
            plots = {}
            
            cits_data = self.data
            
            # CITS 概覽圖 / CITS overview plot
            if cits_data.data_3d is not None and cits_data.bias_values is not None:
                plots['cits_overview'] = SpectroscopyPlotting.plot_cits_overview(
                    cits_data.data_3d, cits_data.bias_values, 
                    title=f"CITS Data Overview - {cits_data.measurement_mode}"
                )
            
            return plots
            
        except Exception as e:
            self.logger.error(f"創建基本圖表失敗: {str(e)}")
            return {}
    
    def _create_line_profile_plots(self, line_profile: Dict) -> Dict[str, Any]:
        """
        創建線段剖面圖表
        Create line profile plots
        """
        try:
            plots = {}
            
            # 多光譜圖 / Multiple spectra plot
            line_sts = line_profile.get('line_sts')
            bias_values = line_profile.get('bias_values')
            
            if line_sts is not None and bias_values is not None:
                plots['multiple_spectra'] = SpectroscopyPlotting.plot_multiple_sts_spectra(
                    bias_values, line_sts, title="Line Profile Spectra"
                )
                
                # 能帶圖 / Band map
                positions = np.arange(line_sts.shape[1])
                plots['band_map'] = SpectroscopyPlotting.plot_band_map(
                    line_sts, bias_values, positions, title="Energy Band Map"
                )
            
            return plots
            
        except Exception as e:
            self.logger.error(f"創建線段剖面圖表失敗: {str(e)}")
            return {}
    
    def _create_bias_slice_plots(self, slice_data: np.ndarray, bias_value: float, 
                               bias_index: int) -> Dict[str, Any]:
        """
        創建偏壓切片圖表
        Create bias slice plots
        """
        try:
            plots = {}
            
            # 偏壓切片圖 / Bias slice plot
            plots['bias_slice'] = SpectroscopyPlotting.plot_2d_map(
                slice_data,
                title=f"Bias Slice at {bias_value:.3f} V (index {bias_index})",
                xlabel="X Position",
                ylabel="Y Position"
            )
            
            return plots
            
        except Exception as e:
            self.logger.error(f"創建偏壓切片圖失敗: {str(e)}")
            return {}
    
    def _create_conductance_plots(self, conductance_data: Dict) -> Dict[str, Any]:
        """
        創建電導圖表
        Create conductance plots
        """
        try:
            plots = {}
            
            if conductance_data:
                for key, data in conductance_data.items():
                    if isinstance(data, np.ndarray) and data.ndim == 2:
                        plots[f'conductance_{key}'] = SpectroscopyPlotting.plot_2d_map(
                            data,
                            title=f"Conductance Map - {key}",
                            xlabel="X Position",
                            ylabel="Y Position"
                        )
            
            return plots
            
        except Exception as e:
            self.logger.error(f"創建電導圖失敗: {str(e)}")
            return {}
    
    def validate_input(self, **kwargs) -> bool:
        """
        驗證 CITS 輸入數據
        Validate CITS input data
        """
        if not super().validate_input(**kwargs):
            return False
        
        if not isinstance(self.data, CitsData):
            self._add_error("數據必須是 CitsData 類型")
            return False
        
        if self.data.data_3d is None:
            self._add_error("CitsData 缺少 data_3d 數據")
            return False
        
        if not isinstance(self.data.data_3d, np.ndarray):
            self._add_error("data_3d 必須是 numpy 數組")
            return False
        
        if self.data.data_3d.ndim != 3:
            self._add_error("data_3d 必須是 3D 數組")
            return False
        
        if self.data.bias_values is None:
            self._add_error("CitsData 缺少 bias_values")
            return False
        
        if len(self.data.bias_values) != self.data.data_3d.shape[0]:
            self._add_error("bias_values 長度與 data_3d 第一維不匹配")
            return False
        
        return True