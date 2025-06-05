"""
CITS 分析器
CITS analyzer

負責協調 CITS 數據的分析工作流和狀態管理
Coordinates CITS data analysis workflow and state management
"""

import numpy as np
from typing import Dict, Any, Optional, Tuple, List

from .base_analyzer import BaseAnalyzer
from ..analysis.cits_analysis import CITSAnalysis
from ..visualization.spectroscopy_plots import SpectroscopyPlotting


class CitsAnalyzer(BaseAnalyzer):
    """
    CITS 分析器
    CITS analyzer
    
    提供 CITS（電流成像隧道光譜）數據的完整分析工作流
    Provides complete analysis workflow for CITS (Current Imaging Tunneling Spectroscopy) data
    """
    
    def __init__(self, main_analyzer):
        """
        初始化 CITS 分析器
        Initialize CITS analyzer
        
        Args:
            main_analyzer: 主分析器實例 / Main analyzer instance
        """
        super().__init__(main_analyzer)
        
        # CITS 特定狀態 / CITS-specific state
        self.cits_analysis: Optional[CITSAnalysis] = None
        self.current_line_profile: Optional[Dict] = None
        self.bias_pattern: Optional[Dict] = None
        
        # 光譜處理歷史 / Spectral processing history
        self.spectral_processing_steps: List[Dict] = []
    
    def analyze(self, cits_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        分析 CITS 數據
        Analyze CITS data
        
        Args:
            cits_data: CITS 數據字典 / CITS data dictionary
            **kwargs: 額外參數 / Additional parameters
            
        Returns:
            Dict: 分析結果 / Analysis results
        """
        try:
            if not self.validate_input(cits_data, **kwargs):
                return self._create_error_result("輸入驗證失敗")
            
            # 創建 CITS 分析實例 / Create CITS analysis instance
            self.cits_analysis = CITSAnalysis(cits_data)
            
            # 檢測偏壓模式 / Detect bias pattern
            self.bias_pattern = self.cits_analysis.detect_bias_pattern()
            
            # 創建基本可視化 / Create basic visualization
            plots = self._create_basic_plots(cits_data)
            
            # 獲取分析摘要 / Get analysis summary
            summary = self.cits_analysis.get_analysis_summary()
            
            result = {
                'success': True,
                'data': {
                    'cits_data_info': {
                        'shape': self.cits_analysis.data_3d.shape,
                        'bias_range': [
                            float(np.min(self.cits_analysis.bias_values)),
                            float(np.max(self.cits_analysis.bias_values))
                        ],
                        'grid_size': self.cits_analysis.grid_size
                    },
                    'bias_pattern': self.bias_pattern,
                    'summary': summary
                },
                'plots': plots,
                'metadata': {
                    'analyzer_type': 'CITS',
                    'n_bias_points': len(self.cits_analysis.bias_values),
                    'scan_direction': self.cits_analysis.scan_direction
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
                    'n_points': line_profile['n_points']
                }
            }
            
            # 記錄分析 / Record analysis
            self._record_analysis(result, f"line_profile_{sampling_method}")
            
            return result
            
        except Exception as e:
            error_msg = f"線段剖面提取失敗: {str(e)}"
            self._add_error(error_msg)
            return self._create_error_result(error_msg)
    
    def _create_basic_plots(self, cits_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        創建基本可視化圖表
        Create basic visualization plots
        
        Args:
            cits_data: CITS 數據 / CITS data
            
        Returns:
            Dict: 圖表字典 / Plots dictionary
        """
        try:
            plots = {}
            
            # CITS 概覽圖 / CITS overview plot
            data_3d = cits_data.get('data_3d')
            bias_values = cits_data.get('bias_values')
            
            if data_3d is not None and bias_values is not None:
                plots['cits_overview'] = SpectroscopyPlotting.plot_cits_overview(
                    data_3d, bias_values, title="CITS Data Overview"
                )
            
            return plots
            
        except Exception as e:
            self.logger.error(f"創建基本圖表失敗: {str(e)}")
            return {}
    
    def _create_line_profile_plots(self, line_profile: Dict) -> Dict[str, Any]:
        """
        創建線段剖面圖表
        Create line profile plots
        
        Args:
            line_profile: 線段剖面數據 / Line profile data
            
        Returns:
            Dict: 圖表字典 / Plots dictionary
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
    
    def _create_error_result(self, error_msg: str) -> Dict[str, Any]:
        """
        創建錯誤結果
        Create error result
        
        Args:
            error_msg: 錯誤信息 / Error message
            
        Returns:
            Dict: 錯誤結果 / Error result
        """
        return {
            'success': False,
            'error': error_msg,
            'data': {},
            'plots': {}
        }