"""
INT 分析器
INT analyzer

負責協調 INT 形貌數據的分析工作流和狀態管理
Coordinates INT topography data analysis workflow and state management
"""

import numpy as np
from typing import Dict, Any, Optional, Tuple, List

from .base_analyzer import BaseAnalyzer
from ..analysis.int_analysis import IntAnalysis
from ..visualization.spm_plots import SPMPlotting


class IntAnalyzer(BaseAnalyzer):
    """
    INT 分析器
    INT analyzer
    
    提供 INT（形貌）數據的完整分析工作流
    Provides complete analysis workflow for INT (topography) data
    """
    
    def __init__(self, main_analyzer):
        """
        初始化 INT 分析器
        Initialize INT analyzer
        
        Args:
            main_analyzer: 主分析器實例 / Main analyzer instance
        """
        super().__init__(main_analyzer)
        
        # INT 特定狀態 / INT-specific state
        self.current_topo_data: Optional[np.ndarray] = None
        self.original_data: Optional[np.ndarray] = None
        self.scan_parameters: Optional[Dict] = None
        self.physical_dimensions: Optional[Tuple[float, float]] = None
        
        # 處理歷史 / Processing history
        self.processing_steps: List[Dict] = []
        
        # 快取處理結果 / Cache processing results
        self.flattened_data: Optional[np.ndarray] = None
        self.current_line_profile: Optional[Dict] = None
    
    def analyze(self, int_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        分析 INT 形貌數據
        Analyze INT topography data
        
        Args:
            int_data: INT 數據字典 / INT data dictionary
                - 'image_data': 2D numpy array
                - 'scan_parameters': scan parameters dict
                - 'physical_dimensions': (x_range, y_range) in nm
            **kwargs: 額外參數 / Additional parameters
            
        Returns:
            Dict: 分析結果 / Analysis results
        """
        try:
            if not self.validate_input(int_data, **kwargs):
                return self._create_error_result("輸入驗證失敗")
            
            # 保存原始數據 / Save original data
            self.original_data = int_data['image_data'].copy()
            self.current_topo_data = int_data['image_data'].copy()
            self.scan_parameters = int_data.get('scan_parameters', {})
            self.physical_dimensions = int_data.get('physical_dimensions', None)
            
            # 計算基本統計 / Calculate basic statistics
            stats = IntAnalysis.get_topo_stats(self.current_topo_data)
            
            # 創建基本可視化 / Create basic visualization
            plots = self._create_basic_plots()
            
            # 計算表面粗糙度 / Calculate surface roughness
            roughness = IntAnalysis.calculate_surface_roughness(self.current_topo_data)
            
            result = {
                'success': True,
                'data': {
                    'topo_info': {
                        'shape': self.current_topo_data.shape,
                        'data_range': [float(np.min(self.current_topo_data)), 
                                     float(np.max(self.current_topo_data))],
                        'physical_dimensions': self.physical_dimensions
                    },
                    'stats': stats,
                    'roughness': roughness,
                    'scan_parameters': self.scan_parameters
                },
                'plots': plots,
                'metadata': {
                    'analyzer_type': 'INT',
                    'has_original_data': True,
                    'processing_steps_count': len(self.processing_steps)
                }
            }
            
            # 記錄分析 / Record analysis
            self._record_analysis(result, "int_basic_analysis")
            
            return result
            
        except Exception as e:
            error_msg = f"INT 分析失敗: {str(e)}"
            self._add_error(error_msg)
            return self._create_error_result(error_msg)
    
    def apply_flattening(self, method: str = 'linewise_mean', **kwargs) -> Dict[str, Any]:
        """
        應用平面化處理
        Apply flattening processing
        
        Args:
            method: 平面化方法 / Flattening method
                - 'linewise_mean': 按行減去均值
                - 'linewise_polyfit': 按行多項式擬合
                - 'plane_flatten': 全局平面擬合
                - 'polynomial_2d': 2D多項式擬合
            **kwargs: 方法特定參數 / Method-specific parameters
            
        Returns:
            Dict: 處理結果 / Processing results
        """
        try:
            if self.current_topo_data is None:
                return self._create_error_result("未載入形貌數據")
            
            if method == 'linewise_mean':
                flattened = IntAnalysis.linewise_flatten_mean(self.current_topo_data)
            elif method == 'linewise_polyfit':
                deg = kwargs.get('degree', 1)
                flattened = IntAnalysis.linewise_flatten_polyfit(self.current_topo_data, deg=deg)
            elif method == 'plane_flatten':
                flattened = IntAnalysis.plane_flatten(self.current_topo_data)
            elif method == 'polynomial_2d':
                order = kwargs.get('order', 1)
                result = IntAnalysis.apply_advanced_flatten(
                    self.current_topo_data, method='polynomial_2d', order=order
                )
                flattened = result['flattened_data']
            else:
                return self._create_error_result(f"不支援的平面化方法: {method}")
            
            # 更新當前數據 / Update current data
            self.current_topo_data = flattened
            self.flattened_data = flattened
            
            # 記錄處理步驟 / Record processing step
            step = {
                'type': 'flattening',
                'method': method,
                'parameters': kwargs
            }
            self.processing_steps.append(step)
            
            # 重新計算統計 / Recalculate statistics
            stats = IntAnalysis.get_topo_stats(flattened)
            
            # 創建對比圖 / Create comparison plots
            plots = self._create_flattening_comparison_plots(flattened, method)
            
            result = {
                'success': True,
                'data': {
                    'flattened_data': flattened,
                    'stats': stats,
                    'method': method,
                    'parameters': kwargs
                },
                'plots': plots,
                'metadata': {
                    'operation': 'flattening',
                    'method': method,
                    'shape': flattened.shape
                }
            }
            
            # 記錄分析 / Record analysis
            self._record_analysis(result, f"flattening_{method}")
            
            return result
            
        except Exception as e:
            error_msg = f"平面化處理失敗: {str(e)}"
            self._add_error(error_msg)
            return self._create_error_result(error_msg)
    
    def apply_tilt_correction(self, direction: str, step_size: int = 10, 
                            fine_tune: bool = False) -> Dict[str, Any]:
        """
        應用傾斜校正
        Apply tilt correction
        
        Args:
            direction: 傾斜方向 ('up', 'down', 'left', 'right')
            step_size: 調整步長
            fine_tune: 是否微調模式
            
        Returns:
            Dict: 處理結果 / Processing results
        """
        try:
            if self.current_topo_data is None:
                return self._create_error_result("未載入形貌數據")
            
            # 應用傾斜校正 / Apply tilt correction
            corrected = IntAnalysis.tilt_image(
                self.current_topo_data, direction, step_size, fine_tune
            )
            
            # 更新當前數據 / Update current data
            self.current_topo_data = corrected
            
            # 記錄處理步驟 / Record processing step
            step = {
                'type': 'tilt_correction',
                'direction': direction,
                'step_size': step_size,
                'fine_tune': fine_tune
            }
            self.processing_steps.append(step)
            
            # 重新計算統計 / Recalculate statistics
            stats = IntAnalysis.get_topo_stats(corrected)
            
            # 創建對比圖 / Create comparison plots
            plots = self._create_tilt_comparison_plots(corrected, direction)
            
            result = {
                'success': True,
                'data': {
                    'corrected_data': corrected,
                    'stats': stats,
                    'direction': direction,
                    'step_size': step_size,
                    'fine_tune': fine_tune
                },
                'plots': plots,
                'metadata': {
                    'operation': 'tilt_correction',
                    'direction': direction,
                    'shape': corrected.shape
                }
            }
            
            # 記錄分析 / Record analysis
            self._record_analysis(result, f"tilt_{direction}")
            
            return result
            
        except Exception as e:
            error_msg = f"傾斜校正失敗: {str(e)}"
            self._add_error(error_msg)
            return self._create_error_result(error_msg)
    
    def extract_line_profile(self, start_point: Tuple[int, int], 
                           end_point: Tuple[int, int],
                           method: str = 'interpolation') -> Dict[str, Any]:
        """
        提取線段剖面
        Extract line profile
        
        Args:
            start_point: 起始點座標 (y, x) / Start point coordinates (y, x)
            end_point: 終點座標 (y, x) / End point coordinates (y, x)
            method: 採樣方法 ('interpolation', 'bresenham')
            
        Returns:
            Dict: 線段剖面數據 / Line profile data
        """
        try:
            if self.current_topo_data is None:
                return self._create_error_result("未載入形貌數據")
            
            # 計算物理尺度 / Calculate physical scale
            physical_scale = self._get_physical_scale()
            
            # 提取線段剖面 / Extract line profile
            if method == 'bresenham':
                profile_data = IntAnalysis.get_line_profile_bresenham(
                    self.current_topo_data, start_point, end_point, 
                    physical_scale, method='bresenham'
                )
            else:
                profile_data = IntAnalysis.get_line_profile(
                    self.current_topo_data, start_point, end_point, physical_scale
                )
            
            self.current_line_profile = profile_data
            
            # 創建剖面圖 / Create profile plots
            plots = self._create_line_profile_plots(profile_data)
            
            result = {
                'success': True,
                'data': profile_data,
                'plots': plots,
                'metadata': {
                    'start_point': start_point,
                    'end_point': end_point,
                    'method': method,
                    'physical_scale': physical_scale
                }
            }
            
            # 記錄分析 / Record analysis
            self._record_analysis(result, f"line_profile_{method}")
            
            return result
            
        except Exception as e:
            error_msg = f"線段剖面提取失敗: {str(e)}"
            self._add_error(error_msg)
            return self._create_error_result(error_msg)
    
    def detect_features(self, feature_type: str = 'peaks', **kwargs) -> Dict[str, Any]:
        """
        檢測表面特徵
        Detect surface features
        
        Args:
            feature_type: 特徵類型 ('peaks', 'valleys')
            **kwargs: 檢測參數
            
        Returns:
            Dict: 特徵檢測結果 / Feature detection results
        """
        try:
            if self.current_topo_data is None:
                return self._create_error_result("未載入形貌數據")
            
            # 檢測特徵 / Detect features
            features = IntAnalysis.detect_surface_features(
                self.current_topo_data, feature_type, **kwargs
            )
            
            # 創建特徵標記圖 / Create feature annotation plots
            plots = self._create_feature_plots(features)
            
            result = {
                'success': True,
                'data': features,
                'plots': plots,
                'metadata': {
                    'feature_type': feature_type,
                    'detection_parameters': kwargs,
                    'feature_count': features['count']
                }
            }
            
            # 記錄分析 / Record analysis
            self._record_analysis(result, f"feature_detection_{feature_type}")
            
            return result
            
        except Exception as e:
            error_msg = f"特徵檢測失敗: {str(e)}"
            self._add_error(error_msg)
            return self._create_error_result(error_msg)
    
    def reset_to_original(self) -> Dict[str, Any]:
        """
        重置到原始數據
        Reset to original data
        
        Returns:
            Dict: 重置結果 / Reset results
        """
        try:
            if self.original_data is None:
                return self._create_error_result("無原始數據可重置")
            
            # 重置數據 / Reset data
            self.current_topo_data = self.original_data.copy()
            self.flattened_data = None
            self.current_line_profile = None
            self.processing_steps.clear()
            
            # 重新計算統計 / Recalculate statistics
            stats = IntAnalysis.get_topo_stats(self.current_topo_data)
            
            # 創建重置後的可視化 / Create reset visualization
            plots = self._create_basic_plots()
            
            result = {
                'success': True,
                'data': {
                    'topo_data': self.current_topo_data,
                    'stats': stats
                },
                'plots': plots,
                'metadata': {
                    'operation': 'reset_to_original',
                    'shape': self.current_topo_data.shape
                }
            }
            
            # 記錄分析 / Record analysis
            self._record_analysis(result, "reset_to_original")
            
            return result
            
        except Exception as e:
            error_msg = f"重置失敗: {str(e)}"
            self._add_error(error_msg)
            return self._create_error_result(error_msg)
    
    def _create_basic_plots(self) -> Dict[str, Any]:
        """
        創建基本可視化圖表
        Create basic visualization plots
        """
        try:
            plots = {}
            
            if self.current_topo_data is not None:
                # 形貌圖 / Topography plot
                plots['topography'] = SPMPlotting.plot_topography(
                    self.current_topo_data, 
                    physical_scale=self.physical_dimensions,
                    title="Topography"
                )
            
            return plots
            
        except Exception as e:
            self.logger.error(f"創建基本圖表失敗: {str(e)}")
            return {}
    
    def _create_flattening_comparison_plots(self, flattened_data: np.ndarray, 
                                          method: str) -> Dict[str, Any]:
        """
        創建平面化對比圖表
        Create flattening comparison plots
        """
        try:
            plots = {}
            
            # 平面化後的形貌圖 / Flattened topography
            plots['flattened_topography'] = SPMPlotting.plot_topography(
                flattened_data,
                physical_scale=self.physical_dimensions,
                title=f"Flattened Topography ({method})"
            )
            
            # 如果有原始數據，創建對比圖 / Create comparison if original data exists
            if self.original_data is not None:
                plots['original_topography'] = SPMPlotting.plot_topography(
                    self.original_data,
                    physical_scale=self.physical_dimensions,
                    title="Original Topography"
                )
            
            return plots
            
        except Exception as e:
            self.logger.error(f"創建平面化對比圖失敗: {str(e)}")
            return {}
    
    def _create_tilt_comparison_plots(self, corrected_data: np.ndarray, 
                                    direction: str) -> Dict[str, Any]:
        """
        創建傾斜校正對比圖表
        Create tilt correction comparison plots
        """
        try:
            plots = {}
            
            # 校正後的形貌圖 / Corrected topography
            plots['tilt_corrected'] = SPMPlotting.plot_topography(
                corrected_data,
                physical_scale=self.physical_dimensions,
                title=f"Tilt Corrected ({direction})"
            )
            
            return plots
            
        except Exception as e:
            self.logger.error(f"創建傾斜校正圖失敗: {str(e)}")
            return {}
    
    def _create_line_profile_plots(self, profile_data: Dict) -> Dict[str, Any]:
        """
        創建線段剖面圖表
        Create line profile plots
        """
        try:
            plots = {}
            
            # 線段剖面圖 / Line profile plot
            plots['line_profile'] = SPMPlotting.plot_line_profile(
                profile_data['distance'], profile_data['height'],
                title="Height Profile"
            )
            
            return plots
            
        except Exception as e:
            self.logger.error(f"創建線段剖面圖失敗: {str(e)}")
            return {}
    
    def _create_feature_plots(self, features: Dict) -> Dict[str, Any]:
        """
        創建特徵標記圖表
        Create feature annotation plots
        """
        try:
            plots = {}
            
            if self.current_topo_data is not None and features['features']:
                # 特徵標記的形貌圖 / Topography with feature annotations
                plots['topography_with_features'] = SPMPlotting.plot_topography(
                    self.current_topo_data,
                    physical_scale=self.physical_dimensions,
                    title=f"Surface Features ({features['type']})"
                )
            
            return plots
            
        except Exception as e:
            self.logger.error(f"創建特徵圖失敗: {str(e)}")
            return {}
    
    def _get_physical_scale(self) -> float:
        """
        獲取物理尺度轉換因子
        Get physical scale conversion factor
        
        Returns:
            float: nm/pixel
        """
        if self.physical_dimensions and self.current_topo_data is not None:
            x_range, y_range = self.physical_dimensions
            _, x_pixels = self.current_topo_data.shape
            return x_range / x_pixels
        return 1.0  # 預設尺度 / Default scale
    
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
        驗證 INT 輸入數據
        Validate INT input data
        """
        if not super().validate_input(data, **kwargs):
            return False
        
        if not isinstance(data, dict):
            self._add_error("輸入數據必須是字典")
            return False
        
        if 'image_data' not in data:
            self._add_error("缺少 image_data 欄位")
            return False
        
        image_data = data['image_data']
        if not isinstance(image_data, np.ndarray):
            self._add_error("image_data 必須是 numpy 數組")
            return False
        
        if image_data.ndim != 2:
            self._add_error("image_data 必須是 2D 數組")
            return False
        
        return True