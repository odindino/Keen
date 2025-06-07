"""
INT 分析器
INT analyzer

負責協調 INT 形貌數據的分析工作流和狀態管理
Coordinates INT topography data analysis workflow and state management
"""

import numpy as np
from typing import Dict, Any, Optional, Tuple, List

from .base_analyzer import BaseAnalyzer
from ..data_models import TopoData
from ..analysis.int_analysis import IntAnalysis
from ..visualization.spm_plots import SPMPlotting


class IntAnalyzer(BaseAnalyzer):
    """
    INT 分析器
    INT analyzer
    
    提供 INT（形貌）數據的完整分析工作流
    Provides complete analysis workflow for INT (topography) data
    """
    
    def __init__(self, topo_data: TopoData):
        """
        初始化 INT 分析器
        Initialize INT analyzer
        
        Args:
            topo_data: TopoData 實例 / TopoData instance
        """
        super().__init__(topo_data)
        
        # INT 特定狀態 / INT-specific state
        self.current_topo_data: Optional[np.ndarray] = None
        self.original_data: Optional[np.ndarray] = None
        
        # 處理歷史 / Processing history
        self.processing_steps: List[Dict] = []
        
        # 快取處理結果 / Cache processing results
        self.current_line_profile: Optional[Dict] = None
        
        # 初始化數據 / Initialize data
        self._initialize_data()
    
    def _initialize_data(self) -> None:
        """
        初始化數據狀態
        Initialize data state
        """
        if isinstance(self.data, TopoData):
            self.original_data = self.data.image.copy()
            self.current_topo_data = self.data.image.copy()
    
    def analyze(self, **kwargs) -> Dict[str, Any]:
        """
        分析 INT 形貌數據
        Analyze INT topography data
        
        Args:
            **kwargs: 額外參數 / Additional parameters
            
        Returns:
            Dict: 分析結果 / Analysis results
        """
        try:
            if not self.validate_input(**kwargs):
                return self._create_error_result("輸入驗證失敗")
            
            topo_data = self.data
            
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
                        'physical_dimensions': [topo_data.x_range, topo_data.y_range],
                        'pixel_scale': [topo_data.pixel_scale_x, topo_data.pixel_scale_y],
                        'data_scale': topo_data.data_scale
                    },
                    'stats': stats,
                    'roughness': roughness,
                    'scan_parameters': {
                        'x_pixels': topo_data.x_pixels,
                        'y_pixels': topo_data.y_pixels,
                        'x_range': topo_data.x_range,
                        'y_range': topo_data.y_range
                    }
                },
                'plots': plots,
                'metadata': {
                    'analyzer_type': 'INT',
                    'data_type': 'TopoData',
                    'signal_type': topo_data.signal_type,
                    'direction': topo_data.direction,
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
            
            # 更新當前數據和 TopoData / Update current data and TopoData
            self.current_topo_data = flattened
            self.data.flattened = flattened
            
            # 記錄處理步驟 / Record processing step
            step = {
                'type': 'flattening',
                'method': method,
                'parameters': kwargs,
                'timestamp': str(np.datetime64('now'))
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
                'fine_tune': fine_tune,
                'timestamp': str(np.datetime64('now'))
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
            physical_scale = self.data.pixel_scale_x
            
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
            self.data.flattened = None
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
                    physical_scale=(self.data.x_range, self.data.y_range),
                    title=f"Topography - {self.data.signal_type} {self.data.direction or ''}"
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
                physical_scale=(self.data.x_range, self.data.y_range),
                title=f"Flattened Topography ({method})"
            )
            
            # 如果有原始數據，創建對比圖 / Create comparison if original data exists
            if self.original_data is not None:
                plots['original_topography'] = SPMPlotting.plot_topography(
                    self.original_data,
                    physical_scale=(self.data.x_range, self.data.y_range),
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
                physical_scale=(self.data.x_range, self.data.y_range),
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
            
            if self.current_topo_data is not None and features.get('features'):
                # 特徵標記的形貌圖 / Topography with feature annotations
                plots['topography_with_features'] = SPMPlotting.plot_topography(
                    self.current_topo_data,
                    physical_scale=(self.data.x_range, self.data.y_range),
                    title=f"Surface Features ({features['type']})"
                )
            
            return plots
            
        except Exception as e:
            self.logger.error(f"創建特徵圖失敗: {str(e)}")
            return {}
    
    def validate_input(self, **kwargs) -> bool:
        """
        驗證 INT 輸入數據
        Validate INT input data
        """
        if not super().validate_input(**kwargs):
            return False
        
        if not isinstance(self.data, TopoData):
            self._add_error("數據必須是 TopoData 類型")
            return False
        
        if self.data.image is None:
            self._add_error("TopoData 缺少 image 數據")
            return False
        
        if not isinstance(self.data.image, np.ndarray):
            self._add_error("image 必須是 numpy 數組")
            return False
        
        if self.data.image.ndim != 2:
            self._add_error("image 必須是 2D 數組")
            return False
        
        return True