"""
DAT 分析器
DAT analyzer

負責協調 DAT 電性測量數據的分析工作流和狀態管理
Coordinates DAT data analysis workflow and state management

注意：此分析器現在主要用於向後兼容，
新的實現建議使用 CitsAnalyzer 或 StsAnalyzer
Note: This analyzer is now mainly for backward compatibility,
new implementations should use CitsAnalyzer or StsAnalyzer
"""

import numpy as np
from typing import Dict, Any, Optional, Tuple, List, Union

from .base_analyzer import BaseAnalyzer
from ..data_models import CitsData, StsData
from ..analysis.cits_analysis import CITSAnalysis
from ..visualization.spectroscopy_plots import SpectroscopyPlotting


class DatAnalyzer(BaseAnalyzer):
    """
    DAT 分析器
    DAT analyzer
    
    提供 DAT（電性測量）數據的完整分析工作流
    Provides complete analysis workflow for DAT (electrical measurement) data
    """
    
    def __init__(self, dat_data: Union[CitsData, StsData]):
        """
        初始化 DAT 分析器
        Initialize DAT analyzer
        
        Args:
            dat_data: CitsData 或 StsData 實例 / CitsData or StsData instance
        """
        super().__init__(dat_data)
        
        # DAT 特定狀態 / DAT-specific state
        self.measurement_mode: Optional[str] = None
        self.cits_analysis: Optional[CITSAnalysis] = None
        
        # 分析結果快取 / Analysis results cache
        self.bias_analysis: Optional[Dict] = None
        self.spatial_analysis: Optional[Dict] = None
        self.line_profiles: List[Dict] = []
        
        # 初始化 / Initialize
        self._initialize_analyzer()
    
    def _initialize_analyzer(self) -> None:
        """
        初始化分析器狀態
        Initialize analyzer state
        """
        if isinstance(self.data, CitsData):
            self.measurement_mode = 'CITS'
            # 轉換為舊格式以適配現有的 CITSAnalysis
            cits_data_dict = {
                'data_3d': self.data.data_3d,
                'bias_values': self.data.bias_values,
                'grid_size': self.data.grid_size,
                'x_range': self.data.x_range,
                'y_range': self.data.y_range
            }
            self.cits_analysis = CITSAnalysis(cits_data_dict)
        elif isinstance(self.data, StsData):
            self.measurement_mode = 'STS'
        else:
            self.measurement_mode = 'unknown'
    
    def analyze(self, **kwargs) -> Dict[str, Any]:
        """
        分析 DAT 數據
        Analyze DAT data
        
        Args:
            **kwargs: 額外參數 / Additional parameters
            
        Returns:
            Dict: 分析結果 / Analysis results
        """
        try:
            if not self.validate_input(**kwargs):
                return self._create_error_result("輸入驗證失敗")
            
            if self.measurement_mode == 'CITS':
                return self._analyze_cits_data(**kwargs)
            elif self.measurement_mode == 'STS':
                return self._analyze_sts_data(**kwargs)
            else:
                return self._create_error_result(f"不支援的測量模式: {self.measurement_mode}")
            
        except Exception as e:
            error_msg = f"DAT 分析失敗: {str(e)}"
            self._add_error(error_msg)
            return self._create_error_result(error_msg)
    
    def _analyze_cits_data(self, **kwargs) -> Dict[str, Any]:
        """
        分析 CITS 數據
        Analyze CITS data
        
        Args:
            **kwargs: 額外參數 / Additional parameters
            
        Returns:
            Dict: CITS 分析結果 / CITS analysis results
        """
        try:
            cits_data = self.data
            
            # 檢測偏壓模式 / Detect bias pattern
            bias_pattern = self.cits_analysis.detect_bias_pattern() if self.cits_analysis else {}
            
            # 計算基本統計 / Calculate basic statistics
            stats = self._calculate_cits_stats()
            
            # 創建基本視覺化 / Create basic visualization
            plots = self._create_cits_plots()
            
            result = {
                'success': True,
                'data': {
                    'measurement_mode': 'CITS',
                    'data_info': {
                        'shape': cits_data.shape,
                        'grid_size': cits_data.grid_size,
                        'bias_range': cits_data.bias_range,
                        'n_bias_points': cits_data.n_bias_points,
                        'x_range': cits_data.x_range,
                        'y_range': cits_data.y_range
                    },
                    'bias_pattern': bias_pattern,
                    'stats': stats
                },
                'plots': plots,
                'metadata': {
                    'analyzer_type': 'DAT_CITS',
                    'data_type': 'CitsData',
                    'measurement_mode': 'CITS',
                    'grid_size': cits_data.grid_size
                }
            }
            
            # 記錄分析 / Record analysis
            self._record_analysis(result, "cits_analysis")
            
            return result
            
        except Exception as e:
            error_msg = f"CITS 數據分析失敗: {str(e)}"
            self._add_error(error_msg)
            return self._create_error_result(error_msg)
    
    def _analyze_sts_data(self, **kwargs) -> Dict[str, Any]:
        """
        分析 STS 數據
        Analyze STS data
        
        Args:
            **kwargs: 額外參數 / Additional parameters
            
        Returns:
            Dict: STS 分析結果 / STS analysis results
        """
        try:
            sts_data = self.data
            
            # 計算基本統計 / Calculate basic statistics
            stats = self._calculate_sts_stats()
            
            # 創建基本視覺化 / Create basic visualization
            plots = self._create_sts_plots()
            
            result = {
                'success': True,
                'data': {
                    'measurement_mode': 'STS',
                    'data_info': {
                        'shape': sts_data.shape,
                        'n_points': sts_data.n_points,
                        'n_bias_points': sts_data.n_bias_points,
                        'measurement_mode': sts_data.measurement_mode
                    },
                    'coordinates': {
                        'x_coords': sts_data.x_coords.tolist() if hasattr(sts_data.x_coords, 'tolist') else sts_data.x_coords,
                        'y_coords': sts_data.y_coords.tolist() if hasattr(sts_data.y_coords, 'tolist') else sts_data.y_coords
                    },
                    'stats': stats
                },
                'plots': plots,
                'metadata': {
                    'analyzer_type': 'DAT_STS',
                    'data_type': 'StsData',
                    'measurement_mode': 'STS',
                    'n_points': sts_data.n_points
                }
            }
            
            # 記錄分析 / Record analysis
            self._record_analysis(result, "sts_analysis")
            
            return result
            
        except Exception as e:
            error_msg = f"STS 數據分析失敗: {str(e)}"
            self._add_error(error_msg)
            return self._create_error_result(error_msg)
    
    def extract_cits_slice(self, bias_index: int) -> Dict[str, Any]:
        """
        提取特定偏壓的 CITS 切片
        Extract CITS slice at specific bias
        
        Args:
            bias_index: 偏壓索引 / Bias index
            
        Returns:
            Dict: 切片數據 / Slice data
        """
        try:
            if self.measurement_mode != 'CITS':
                return self._create_error_result("此操作只適用於 CITS 數據")
            
            cits_data = self.data
            
            # 提取切片 / Extract slice
            slice_data = cits_data.get_bias_slice(bias_index)
            bias_value = cits_data.bias_values[bias_index]
            
            # 計算切片統計 / Calculate slice statistics
            stats = {
                'min': float(np.min(slice_data)),
                'max': float(np.max(slice_data)),
                'mean': float(np.mean(slice_data)),
                'std': float(np.std(slice_data))
            }
            
            # 創建視覺化 / Create visualization
            plots = self._create_slice_plots(slice_data, bias_value)
            
            result = {
                'success': True,
                'data': {
                    'slice_data': slice_data,
                    'bias_value': float(bias_value),
                    'bias_index': bias_index,
                    'stats': stats
                },
                'plots': plots,
                'metadata': {
                    'operation': 'cits_slice',
                    'bias_index': bias_index,
                    'bias_value': float(bias_value)
                }
            }
            
            # 記錄分析 / Record analysis
            self._record_analysis(result, f"cits_slice_{bias_index}")
            
            return result
            
        except Exception as e:
            error_msg = f"CITS 切片提取失敗: {str(e)}"
            self._add_error(error_msg)
            return self._create_error_result(error_msg)
    
    def extract_cits_line_profile(self, start_coord: Tuple[int, int], 
                                 end_coord: Tuple[int, int],
                                 sampling_method: str = 'bresenham') -> Dict[str, Any]:
        """
        提取 CITS 線段剖面光譜
        Extract CITS line profile spectrum
        
        Args:
            start_coord: 起始座標 (x, y) / Start coordinates (x, y)
            end_coord: 終點座標 (x, y) / End coordinates (x, y)
            sampling_method: 採樣方法 / Sampling method
            
        Returns:
            Dict: 線段剖面數據 / Line profile data
        """
        try:
            if self.measurement_mode != 'CITS':
                return self._create_error_result("此操作只適用於 CITS 數據")
            
            if self.cits_analysis is None:
                return self._create_error_result("CITS 分析器未初始化")
            
            # 提取線段剖面 / Extract line profile
            line_profile = self.cits_analysis.extract_line_profile(
                start_coord, end_coord, sampling_method=sampling_method
            )
            
            # 保存到歷史 / Save to history
            self.line_profiles.append(line_profile)
            
            # 創建光譜視覺化 / Create spectral visualization
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
            self._record_analysis(result, f"cits_line_profile_{sampling_method}")
            
            return result
            
        except Exception as e:
            error_msg = f"CITS 線段剖面提取失敗: {str(e)}"
            self._add_error(error_msg)
            return self._create_error_result(error_msg)
    
    def _calculate_cits_stats(self) -> Dict[str, Any]:
        """
        計算 CITS 數據統計
        Calculate CITS data statistics
        """
        try:
            cits_data = self.data
            data_3d = cits_data.data_3d
            bias_values = cits_data.bias_values
            
            stats = {
                'data_range': [float(np.min(data_3d)), float(np.max(data_3d))],
                'spatial_average': {
                    'min': float(np.min(np.mean(data_3d, axis=(1, 2)))),
                    'max': float(np.max(np.mean(data_3d, axis=(1, 2)))),
                    'mean': float(np.mean(data_3d))
                },
                'bias_range': cits_data.bias_range,
                'bias_step': float(np.mean(np.diff(bias_values))) if len(bias_values) > 1 else 0.0
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"CITS 統計計算失敗: {str(e)}")
            return {}
    
    def _calculate_sts_stats(self) -> Dict[str, Any]:
        """
        計算 STS 數據統計
        Calculate STS data statistics
        """
        try:
            sts_data = self.data
            data_2d = sts_data.data_2d
            bias_values = sts_data.bias_values
            
            stats = {
                'data_range': [float(np.min(data_2d)), float(np.max(data_2d))],
                'point_average': {
                    'min': float(np.min(np.mean(data_2d, axis=0))),
                    'max': float(np.max(np.mean(data_2d, axis=0))),
                    'mean': float(np.mean(data_2d))
                },
                'bias_range': [float(np.min(bias_values)), float(np.max(bias_values))],
                'bias_step': float(np.mean(np.diff(bias_values))) if len(bias_values) > 1 else 0.0
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"STS 統計計算失敗: {str(e)}")
            return {}
    
    def _create_cits_plots(self) -> Dict[str, Any]:
        """
        創建 CITS 視覺化圖表
        Create CITS visualization plots
        """
        try:
            plots = {}
            
            cits_data = self.data
            data_3d = cits_data.data_3d
            bias_values = cits_data.bias_values
            
            # CITS 概覽圖 / CITS overview plot
            plots['cits_overview'] = SpectroscopyPlotting.plot_cits_overview(
                data_3d, bias_values, title=f"CITS Data Overview - {cits_data.measurement_mode}"
            )
            
            # 中間偏壓的空間分佈 / Spatial distribution at middle bias
            mid_bias_idx = len(bias_values) // 2
            plots['spatial_map'] = SpectroscopyPlotting.plot_2d_map(
                data_3d[mid_bias_idx, :, :], 
                title=f"Spatial Map at {bias_values[mid_bias_idx]:.2f} V"
            )
            
            return plots
            
        except Exception as e:
            self.logger.error(f"創建 CITS 圖表失敗: {str(e)}")
            return {}
    
    def _create_sts_plots(self) -> Dict[str, Any]:
        """
        創建 STS 視覺化圖表
        Create STS visualization plots
        """
        try:
            plots = {}
            
            sts_data = self.data
            data_2d = sts_data.data_2d
            bias_values = sts_data.bias_values
            
            # 多條 STS 光譜 / Multiple STS spectra
            plots['sts_spectra'] = SpectroscopyPlotting.plot_multiple_sts_spectra(
                bias_values, data_2d, title=f"STS Spectra - {sts_data.measurement_mode}"
            )
            
            # 平均光譜 / Average spectrum
            avg_spectrum = np.mean(data_2d, axis=1)
            plots['average_spectrum'] = SpectroscopyPlotting.plot_sts_spectrum(
                bias_values, avg_spectrum, title="Average STS Spectrum"
            )
            
            return plots
            
        except Exception as e:
            self.logger.error(f"創建 STS 圖表失敗: {str(e)}")
            return {}
    
    def _create_slice_plots(self, slice_data: np.ndarray, bias_value: float) -> Dict[str, Any]:
        """
        創建 CITS 切片圖表
        Create CITS slice plots
        """
        try:
            plots = {}
            
            # 切片空間分佈 / Slice spatial distribution  
            plots['slice_map'] = SpectroscopyPlotting.plot_2d_map(
                slice_data, title=f"CITS Slice at {bias_value:.2f} V"
            )
            
            return plots
            
        except Exception as e:
            self.logger.error(f"創建切片圖表失敗: {str(e)}")
            return {}
    
    def _create_line_profile_plots(self, line_profile: Dict) -> Dict[str, Any]:
        """
        創建線段剖面圖表
        Create line profile plots
        """
        try:
            plots = {}
            
            line_sts = line_profile.get('line_sts')
            bias_values = line_profile.get('bias_values')
            
            if line_sts is not None and bias_values is not None:
                # 多光譜圖 / Multiple spectra plot
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
    
    def validate_input(self, **kwargs) -> bool:
        """
        驗證 DAT 輸入數據
        Validate DAT input data
        """
        if not super().validate_input(**kwargs):
            return False
        
        if not isinstance(self.data, (CitsData, StsData)):
            self._add_error("數據必須是 CitsData 或 StsData 類型")
            return False
        
        if isinstance(self.data, CitsData):
            if self.data.data_3d is None:
                self._add_error("CitsData 缺少 data_3d 數據")
                return False
            if self.data.bias_values is None:
                self._add_error("CitsData 缺少 bias_values")
                return False
        elif isinstance(self.data, StsData):
            if self.data.data_2d is None:
                self._add_error("StsData 缺少 data_2d 數據")
                return False
            if self.data.bias_values is None:
                self._add_error("StsData 缺少 bias_values")
                return False
        
        return True