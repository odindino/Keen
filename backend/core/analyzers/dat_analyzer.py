"""
DAT 分析器
DAT analyzer

負責協調 DAT 電性測量數據的分析工作流和狀態管理
Coordinates DAT data analysis workflow and state management
"""

import numpy as np
from typing import Dict, Any, Optional, Tuple, List

from .base_analyzer import BaseAnalyzer
from ..analysis.cits_analysis import CITSAnalysis
from ..visualization.spectroscopy_plots import SpectroscopyPlotting


class DatAnalyzer(BaseAnalyzer):
    """
    DAT 分析器
    DAT analyzer
    
    提供 DAT（電性測量）數據的完整分析工作流
    Provides complete analysis workflow for DAT (electrical measurement) data
    """
    
    def __init__(self, main_analyzer):
        """
        初始化 DAT 分析器
        Initialize DAT analyzer
        
        Args:
            main_analyzer: 主分析器實例 / Main analyzer instance
        """
        super().__init__(main_analyzer)
        
        # DAT 特定狀態 / DAT-specific state
        self.current_dat_data: Optional[Dict] = None
        self.measurement_mode: Optional[str] = None  # 'CITS' or 'STS'
        self.cits_analysis: Optional[CITSAnalysis] = None
        
        # 分析結果快取 / Analysis results cache
        self.bias_analysis: Optional[Dict] = None
        self.spatial_analysis: Optional[Dict] = None
        self.line_profiles: List[Dict] = []
    
    def analyze(self, dat_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        分析 DAT 數據
        Analyze DAT data
        
        Args:
            dat_data: DAT 數據字典 / DAT data dictionary
                From DatParser.parse() containing:
                - 'measurement_mode': 'CITS' or 'STS'
                - 'data_3d' or 'data_2d': measurement data
                - 'bias_values': bias voltage array
                - 'x_coords', 'y_coords': spatial coordinates
                - etc.
            **kwargs: 額外參數 / Additional parameters
            
        Returns:
            Dict: 分析結果 / Analysis results
        """
        try:
            if not self.validate_input(dat_data, **kwargs):
                return self._create_error_result("輸入驗證失敗")
            
            # 保存數據並檢測測量模式 / Save data and detect measurement mode
            self.current_dat_data = dat_data
            self.measurement_mode = dat_data.get('measurement_mode', 'unknown')
            
            if self.measurement_mode == 'CITS':
                return self._analyze_cits_data(dat_data, **kwargs)
            elif self.measurement_mode == 'STS':
                return self._analyze_sts_data(dat_data, **kwargs)
            else:
                return self._create_error_result(f"不支援的測量模式: {self.measurement_mode}")
            
        except Exception as e:
            error_msg = f"DAT 分析失敗: {str(e)}"
            self._add_error(error_msg)
            return self._create_error_result(error_msg)
    
    def _analyze_cits_data(self, cits_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        分析 CITS 數據
        Analyze CITS data
        
        Args:
            cits_data: CITS 數據字典 / CITS data dictionary
            **kwargs: 額外參數 / Additional parameters
            
        Returns:
            Dict: CITS 分析結果 / CITS analysis results
        """
        try:
            # 創建 CITS 分析實例 / Create CITS analysis instance
            self.cits_analysis = CITSAnalysis(cits_data)
            
            # 獲取基本信息 / Get basic information
            data_3d = cits_data['data_3d']
            bias_values = cits_data['bias_values']
            grid_size = cits_data.get('grid_size', [data_3d.shape[2], data_3d.shape[1]])
            
            # 檢測偏壓模式 / Detect bias pattern
            bias_pattern = self.cits_analysis.detect_bias_pattern()
            
            # 計算基本統計 / Calculate basic statistics
            stats = self._calculate_cits_stats(data_3d, bias_values)
            
            # 創建基本視覺化 / Create basic visualization
            plots = self._create_cits_plots(cits_data)
            
            result = {
                'success': True,
                'data': {
                    'measurement_mode': 'CITS',
                    'data_info': {
                        'shape': data_3d.shape,
                        'grid_size': grid_size,
                        'bias_range': [float(np.min(bias_values)), float(np.max(bias_values))],
                        'n_bias_points': len(bias_values)
                    },
                    'bias_pattern': bias_pattern,
                    'stats': stats,
                    'scan_direction': cits_data.get('scan_direction', 'unknown')
                },
                'plots': plots,
                'metadata': {
                    'analyzer_type': 'DAT_CITS',
                    'measurement_mode': 'CITS',
                    'grid_size': grid_size
                }
            }
            
            # 記錄分析 / Record analysis
            self._record_analysis(result, "cits_analysis")
            
            return result
            
        except Exception as e:
            error_msg = f"CITS 數據分析失敗: {str(e)}"
            self._add_error(error_msg)
            return self._create_error_result(error_msg)
    
    def _analyze_sts_data(self, sts_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        分析 STS 數據
        Analyze STS data
        
        Args:
            sts_data: STS 數據字典 / STS data dictionary
            **kwargs: 額外參數 / Additional parameters
            
        Returns:
            Dict: STS 分析結果 / STS analysis results
        """
        try:
            # 獲取基本信息 / Get basic information
            data_2d = sts_data['data_2d']
            bias_values = sts_data['bias_values']
            x_coords = sts_data['x_coords']
            y_coords = sts_data['y_coords']
            n_points = sts_data.get('n_points', data_2d.shape[1])
            
            # 計算基本統計 / Calculate basic statistics
            stats = self._calculate_sts_stats(data_2d, bias_values)
            
            # 創建基本視覺化 / Create basic visualization
            plots = self._create_sts_plots(sts_data)
            
            result = {
                'success': True,
                'data': {
                    'measurement_mode': 'STS',
                    'data_info': {
                        'shape': data_2d.shape,
                        'n_points': n_points,
                        'bias_range': [float(np.min(bias_values)), float(np.max(bias_values))],
                        'n_bias_points': len(bias_values)
                    },
                    'coordinates': {
                        'x_coords': x_coords.tolist() if hasattr(x_coords, 'tolist') else x_coords,
                        'y_coords': y_coords.tolist() if hasattr(y_coords, 'tolist') else y_coords
                    },
                    'stats': stats
                },
                'plots': plots,
                'metadata': {
                    'analyzer_type': 'DAT_STS',
                    'measurement_mode': 'STS',
                    'n_points': n_points
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
            
            if self.current_dat_data is None:
                return self._create_error_result("未載入 DAT 數據")
            
            data_3d = self.current_dat_data['data_3d']
            bias_values = self.current_dat_data['bias_values']
            
            if bias_index < 0 or bias_index >= len(bias_values):
                return self._create_error_result(f"偏壓索引超出範圍: {bias_index}")
            
            # 提取切片 / Extract slice
            slice_data = data_3d[bias_index, :, :]
            bias_value = bias_values[bias_index]
            
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
    
    def analyze_bias_dependence(self, point_coord: Optional[Tuple[int, int]] = None) -> Dict[str, Any]:
        """
        分析偏壓依賴性
        Analyze bias dependence
        
        Args:
            point_coord: 分析點座標，None 表示空間平均 / Analysis point coordinates, None for average
            
        Returns:
            Dict: 偏壓分析結果 / Bias analysis results
        """
        try:
            if self.current_dat_data is None:
                return self._create_error_result("未載入 DAT 數據")
            
            bias_values = self.current_dat_data['bias_values']
            
            if self.measurement_mode == 'CITS':
                data_3d = self.current_dat_data['data_3d']
                
                if point_coord is not None:
                    x, y = point_coord
                    if 0 <= x < data_3d.shape[2] and 0 <= y < data_3d.shape[1]:
                        spectrum = data_3d[:, y, x]
                        analysis_type = 'point'
                    else:
                        return self._create_error_result("座標超出範圍")
                else:
                    # 計算空間平均 / Calculate spatial average
                    spectrum = np.mean(data_3d, axis=(1, 2))
                    analysis_type = 'average'
                    
            elif self.measurement_mode == 'STS':
                data_2d = self.current_dat_data['data_2d']
                
                if point_coord is not None and point_coord[0] < data_2d.shape[1]:
                    spectrum = data_2d[:, point_coord[0]]
                    analysis_type = 'point'
                else:
                    # 計算所有點的平均 / Calculate average of all points
                    spectrum = np.mean(data_2d, axis=1)
                    analysis_type = 'average'
            else:
                return self._create_error_result(f"不支援的測量模式: {self.measurement_mode}")
            
            # 計算偏壓統計 / Calculate bias statistics
            bias_stats = {
                'min_value': float(np.min(spectrum)),
                'max_value': float(np.max(spectrum)),
                'mean_value': float(np.mean(spectrum)),
                'std_value': float(np.std(spectrum)),
                'peak_bias': float(bias_values[np.argmax(spectrum)]),
                'min_bias': float(bias_values[np.argmin(spectrum)])
            }
            
            # 創建偏壓依賴圖 / Create bias dependence plots
            plots = self._create_bias_dependence_plots(bias_values, spectrum, analysis_type)
            
            self.bias_analysis = {
                'spectrum': spectrum.tolist(),
                'bias_values': bias_values.tolist(),
                'stats': bias_stats,
                'analysis_type': analysis_type,
                'point_coord': point_coord
            }
            
            result = {
                'success': True,
                'data': self.bias_analysis,
                'plots': plots,
                'metadata': {
                    'operation': 'bias_dependence',
                    'analysis_type': analysis_type,
                    'point_coord': point_coord
                }
            }
            
            # 記錄分析 / Record analysis
            self._record_analysis(result, f"bias_dependence_{analysis_type}")
            
            return result
            
        except Exception as e:
            error_msg = f"偏壓依賴性分析失敗: {str(e)}"
            self._add_error(error_msg)
            return self._create_error_result(error_msg)
    
    def _calculate_cits_stats(self, data_3d: np.ndarray, bias_values: np.ndarray) -> Dict[str, Any]:
        """
        計算 CITS 數據統計
        Calculate CITS data statistics
        """
        try:
            stats = {
                'data_range': [float(np.min(data_3d)), float(np.max(data_3d))],
                'spatial_average': {
                    'min': float(np.min(np.mean(data_3d, axis=(1, 2)))),
                    'max': float(np.max(np.mean(data_3d, axis=(1, 2)))),
                    'mean': float(np.mean(data_3d))
                },
                'bias_range': [float(np.min(bias_values)), float(np.max(bias_values))],
                'bias_step': float(np.mean(np.diff(bias_values))) if len(bias_values) > 1 else 0.0
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"CITS 統計計算失敗: {str(e)}")
            return {}
    
    def _calculate_sts_stats(self, data_2d: np.ndarray, bias_values: np.ndarray) -> Dict[str, Any]:
        """
        計算 STS 數據統計
        Calculate STS data statistics
        """
        try:
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
    
    def _create_cits_plots(self, cits_data: Dict) -> Dict[str, Any]:
        """
        創建 CITS 視覺化圖表
        Create CITS visualization plots
        """
        try:
            plots = {}
            
            data_3d = cits_data['data_3d']
            bias_values = cits_data['bias_values']
            
            # CITS 概覽圖 / CITS overview plot
            plots['cits_overview'] = SpectroscopyPlotting.plot_cits_overview(
                data_3d, bias_values, title="CITS Data Overview"
            )
            
            # 中間偏壓的空間分佈 / Spatial distribution at middle bias
            mid_bias_idx = len(bias_values) // 2
            from ..visualization.spm_plots import SPMPlotting
            plots['spatial_map'] = SPMPlotting.plot_spatial_map(
                data_3d[mid_bias_idx, :, :], 
                title=f"Spatial Map at {bias_values[mid_bias_idx]:.2f} V"
            )
            
            return plots
            
        except Exception as e:
            self.logger.error(f"創建 CITS 圖表失敗: {str(e)}")
            return {}
    
    def _create_sts_plots(self, sts_data: Dict) -> Dict[str, Any]:
        """
        創建 STS 視覺化圖表
        Create STS visualization plots
        """
        try:
            plots = {}
            
            data_2d = sts_data['data_2d']
            bias_values = sts_data['bias_values']
            
            # 多條 STS 光譜 / Multiple STS spectra
            plots['sts_spectra'] = SpectroscopyPlotting.plot_multiple_sts_spectra(
                bias_values, data_2d, title="STS Spectra"
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
            from ..visualization.spm_plots import SPMPlotting
            plots['slice_map'] = SPMPlotting.plot_spatial_map(
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
    
    def _create_bias_dependence_plots(self, bias_values: np.ndarray, 
                                    spectrum: np.ndarray, 
                                    analysis_type: str) -> Dict[str, Any]:
        """
        創建偏壓依賴圖表
        Create bias dependence plots
        """
        try:
            plots = {}
            
            # 偏壓依賴光譜 / Bias dependence spectrum
            plots['bias_spectrum'] = SpectroscopyPlotting.plot_sts_spectrum(
                bias_values, spectrum, 
                title=f"Bias Dependence ({analysis_type.title()})"
            )
            
            return plots
            
        except Exception as e:
            self.logger.error(f"創建偏壓依賴圖表失敗: {str(e)}")
            return {}
    
    def _create_error_result(self, error_msg: str) -> Dict[str, Any]:
        """
        創建錯誤結果
        Create error result
        """
        return {
            'success': False,
            'error': error_msg,
            'data': {},
            'plots': {}
        }
    
    def validate_input(self, data: Any, **kwargs) -> bool:
        """
        驗證 DAT 輸入數據
        Validate DAT input data
        """
        if not super().validate_input(data, **kwargs):
            return False
        
        if not isinstance(data, dict):
            self._add_error("輸入數據必須是字典")
            return False
        
        # 檢查必要欄位 / Check required fields
        required_fields = ['measurement_mode', 'bias_values']
        for field in required_fields:
            if field not in data:
                self._add_error(f"缺少必要欄位: {field}")
                return False
        
        measurement_mode = data['measurement_mode']
        if measurement_mode not in ['CITS', 'STS']:
            self._add_error(f"不支援的測量模式: {measurement_mode}")
            return False
        
        # 根據測量模式檢查數據結構 / Check data structure based on measurement mode
        if measurement_mode == 'CITS':
            if 'data_3d' not in data:
                self._add_error("CITS 數據缺少: data_3d")
                return False
            data_3d = data['data_3d']
            if not isinstance(data_3d, np.ndarray) or data_3d.ndim != 3:
                self._add_error("CITS data_3d 必須是 3D numpy 數組")
                return False
        elif measurement_mode == 'STS':
            if 'data_2d' not in data:
                self._add_error("STS 數據缺少: data_2d")
                return False
            data_2d = data['data_2d']
            if not isinstance(data_2d, np.ndarray) or data_2d.ndim != 2:
                self._add_error("STS data_2d 必須是 2D numpy 數組")
                return False
        
        return True