"""
TXT 分析器
TXT analyzer

負責協調 TXT 實驗參數文件的分析工作流和狀態管理
Coordinates TXT experiment parameter file analysis workflow and state management
"""

import os
import re
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from pathlib import Path

from .base_analyzer import BaseAnalyzer
from ..data_models import TxtData


class TxtAnalyzer(BaseAnalyzer):
    """
    TXT 分析器
    TXT analyzer
    
    提供 TXT（實驗參數）文件的完整分析工作流
    Provides complete analysis workflow for TXT (experiment parameter) files
    """
    
    def __init__(self, txt_data: TxtData):
        """
        初始化 TXT 分析器
        Initialize TXT analyzer
        
        Args:
            txt_data: TxtData 實例 / TxtData instance
        """
        super().__init__(txt_data)
        
        # TXT 特定狀態 / TXT-specific state
        self.file_path: Optional[str] = None
        
        # 驗證結果 / Validation results
        self.validation_results: Optional[Dict] = None
        self.file_availability: Optional[Dict] = None
    
    def set_file_path(self, file_path: str) -> None:
        """
        設置 TXT 文件路徑
        Set TXT file path
        
        Args:
            file_path: 文件路徑 / File path
        """
        self.file_path = file_path
    
    def analyze(self, **kwargs) -> Dict[str, Any]:
        """
        分析 TXT 實驗參數數據
        Analyze TXT experiment parameter data
        
        Args:
            **kwargs: 額外參數，可包含 'file_path' / Additional parameters, may include 'file_path'
            
        Returns:
            Dict: 分析結果 / Analysis results
        """
        try:
            if not self.validate_input(**kwargs):
                return self._create_error_result("輸入驗證失敗")
            
            # 更新文件路徑 / Update file path if provided
            if 'file_path' in kwargs:
                self.file_path = kwargs['file_path']
            
            txt_data = self.data
            
            # 分析實驗參數 / Analyze experiment parameters
            param_analysis = self._analyze_experiment_parameters()
            
            # 分析文件描述 / Analyze file descriptions
            file_analysis = self._analyze_file_descriptions()
            
            # 驗證文件可用性 / Validate file availability
            availability_analysis = self._check_file_availability()
            
            # 檢測實驗類型 / Detect experiment type
            experiment_type = self._detect_experiment_type()
            
            # 生成實驗摘要 / Generate experiment summary
            summary = self._generate_experiment_summary()
            
            result = {
                'success': True,
                'data': {
                    'experiment_info': txt_data.experiment_info,
                    'scan_parameters': {
                        'x_pixel': txt_data.scan_parameters.x_pixel,
                        'y_pixel': txt_data.scan_parameters.y_pixel,
                        'x_range': txt_data.scan_parameters.x_range,
                        'y_range': txt_data.scan_parameters.y_range,
                        'pixel_scale_x': txt_data.scan_parameters.pixel_scale_x,
                        'pixel_scale_y': txt_data.scan_parameters.pixel_scale_y,
                        'aspect_ratio': txt_data.scan_parameters.aspect_ratio,
                        'total_pixels': txt_data.scan_parameters.total_pixels
                    },
                    'parameter_analysis': param_analysis,
                    'file_analysis': file_analysis,
                    'availability_analysis': availability_analysis,
                    'experiment_type': experiment_type,
                    'summary': summary
                },
                'plots': {},  # TXT files typically don't have plots
                'metadata': {
                    'analyzer_type': 'TXT',
                    'data_type': 'TxtData',
                    'file_path': self.file_path,
                    'experiment_name': txt_data.experiment_name,
                    'n_int_files': len(txt_data.int_files),
                    'n_dat_files': len(txt_data.dat_files),
                    'total_files': txt_data.total_files
                }
            }
            
            # 記錄分析 / Record analysis
            self._record_analysis(result, "txt_analysis")
            
            return result
            
        except Exception as e:
            error_msg = f"TXT 分析失敗: {str(e)}"
            self._add_error(error_msg)
            return self._create_error_result(error_msg)
    
    def _analyze_experiment_parameters(self) -> Dict[str, Any]:
        """
        分析實驗參數
        Analyze experiment parameters
        """
        try:
            txt_data = self.data
            analysis = {
                'scan_info': {},
                'tunneling_info': {},
                'feedback_info': {},
                'timing_info': {}
            }
            
            # 掃描信息 / Scan information
            scan_params = txt_data.scan_parameters
            analysis['scan_info'] = {
                'resolution': [scan_params.x_pixel, scan_params.y_pixel],
                'total_pixels': scan_params.total_pixels,
                'scan_size': [scan_params.x_range, scan_params.y_range],
                'pixel_size': [scan_params.pixel_scale_x, scan_params.pixel_scale_y],
                'aspect_ratio': scan_params.aspect_ratio
            }
            
            exp_info = txt_data.experiment_info
            
            # 隧道參數 / Tunneling parameters
            if 'Bias' in exp_info:
                analysis['tunneling_info']['bias_voltage'] = float(exp_info['Bias'])
            
            if 'SetPoint' in exp_info:
                analysis['tunneling_info']['setpoint_current'] = float(exp_info['SetPoint'])
            
            # 反饋參數 / Feedback parameters
            if 'Ki' in exp_info and 'Kp' in exp_info:
                analysis['feedback_info']['ki'] = float(exp_info['Ki'])
                analysis['feedback_info']['kp'] = float(exp_info['Kp'])
            
            # 時間信息 / Timing information
            if 'Date' in exp_info and 'Time' in exp_info:
                analysis['timing_info']['date'] = exp_info['Date']
                analysis['timing_info']['time'] = exp_info['Time']
            
            if 'Speed' in exp_info:
                try:
                    # 處理可能包含單位的速度值
                    speed_str = str(exp_info['Speed']).strip()
                    # 移除可能的單位或額外文字
                    speed_num = speed_str.split()[0]  # 取第一個數值部分
                    analysis['timing_info']['scan_speed'] = float(speed_num)
                except (ValueError, IndexError):
                    self.logger.warning(f"無法解析掃描速度: {exp_info['Speed']}")
                    analysis['timing_info']['scan_speed'] = None
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"實驗參數分析失敗: {str(e)}")
            return {}
    
    def _analyze_file_descriptions(self) -> Dict[str, Any]:
        """
        分析文件描述
        Analyze file descriptions
        """
        try:
            txt_data = self.data
            analysis = {
                'int_files_summary': {},
                'dat_files_summary': {},
                'measurement_modes': [],
                'signal_types': txt_data.signal_types
            }
            
            # INT 文件分析 / INT files analysis
            int_captions = [f.get('caption', 'Unknown') for f in txt_data.int_files]
            analysis['int_files_summary'] = {
                'count': len(txt_data.int_files),
                'types': list(set(int_captions)),
                'details': txt_data.int_files
            }
            
            # DAT 文件分析 / DAT files analysis
            measurement_modes = []
            for dat_file in txt_data.dat_files:
                mode = dat_file.get('measurement_mode', 'unknown')
                if mode not in measurement_modes:
                    measurement_modes.append(mode)
            
            analysis['dat_files_summary'] = {
                'count': len(txt_data.dat_files),
                'measurement_modes': measurement_modes,
                'details': txt_data.dat_files
            }
            
            analysis['measurement_modes'] = measurement_modes
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"文件描述分析失敗: {str(e)}")
            return {}
    
    def _check_file_availability(self) -> Dict[str, Any]:
        """
        檢查文件可用性
        Check file availability
        """
        try:
            availability = {
                'all_files_available': True,
                'missing_files': [],
                'available_files': [],
                'file_details': {}
            }
            
            if self.file_path is None:
                availability['all_files_available'] = False
                availability['error'] = "未提供 TXT 文件路徑"
                return availability
            
            base_dir = Path(self.file_path).parent
            txt_data = self.data
            
            # 檢查 INT 文件 / Check INT files
            for int_file in txt_data.int_files:
                filename = int_file['filename']
                file_path = base_dir / filename
                
                if file_path.exists():
                    availability['available_files'].append(filename)
                    availability['file_details'][filename] = {
                        'available': True,
                        'size': file_path.stat().st_size,
                        'type': 'int',
                        'caption': int_file.get('caption', 'Unknown'),
                        'scale': int_file.get('scale', 'Unknown')
                    }
                else:
                    availability['missing_files'].append(filename)
                    availability['file_details'][filename] = {
                        'available': False,
                        'type': 'int',
                        'caption': int_file.get('caption', 'Unknown')
                    }
                    availability['all_files_available'] = False
            
            # 檢查 DAT 文件 / Check DAT files
            for dat_file in txt_data.dat_files:
                filename = dat_file['filename']
                file_path = base_dir / filename
                
                if file_path.exists():
                    availability['available_files'].append(filename)
                    availability['file_details'][filename] = {
                        'available': True,
                        'size': file_path.stat().st_size,
                        'type': 'dat',
                        'measurement_mode': dat_file.get('measurement_mode', 'unknown')
                    }
                else:
                    availability['missing_files'].append(filename)
                    availability['file_details'][filename] = {
                        'available': False,
                        'type': 'dat',
                        'measurement_mode': dat_file.get('measurement_mode', 'unknown')
                    }
                    availability['all_files_available'] = False
            
            self.file_availability = availability
            return availability
            
        except Exception as e:
            self.logger.error(f"文件可用性檢查失敗: {str(e)}")
            return {'all_files_available': False, 'error': str(e)}
    
    def _detect_experiment_type(self) -> Dict[str, Any]:
        """
        檢測實驗類型
        Detect experiment type
        """
        try:
            txt_data = self.data
            exp_type = {
                'primary_type': 'Unknown',
                'secondary_types': [],
                'complexity': 'Simple',
                'description': ''
            }
            
            has_topo = len(txt_data.int_files) > 0
            has_cits = any(f.get('measurement_mode') == 'CITS' for f in txt_data.dat_files)
            has_sts = any(f.get('measurement_mode') == 'STS' for f in txt_data.dat_files)
            
            if has_topo and has_cits:
                exp_type['primary_type'] = 'Combined STM/CITS'
                exp_type['complexity'] = 'Complex'
                exp_type['description'] = '結合形貌和電流成像隧道光譜的綜合測量'
            elif has_cits:
                exp_type['primary_type'] = 'CITS'
                exp_type['complexity'] = 'Moderate'
                exp_type['description'] = '電流成像隧道光譜測量'
            elif has_topo and has_sts:
                exp_type['primary_type'] = 'STM + STS'
                exp_type['complexity'] = 'Moderate'
                exp_type['description'] = '形貌測量配合局域光譜分析'
            elif has_topo:
                exp_type['primary_type'] = 'STM Topography'
                exp_type['complexity'] = 'Simple'
                exp_type['description'] = '掃描隧道顯微鏡形貌測量'
            elif has_sts:
                exp_type['primary_type'] = 'STS'
                exp_type['complexity'] = 'Simple'
                exp_type['description'] = '掃描隧道光譜測量'
            
            # 添加次要類型 / Add secondary types
            if has_topo:
                exp_type['secondary_types'].append('Topography')
            if has_cits:
                exp_type['secondary_types'].append('CITS')
            if has_sts:
                exp_type['secondary_types'].append('STS')
            
            return exp_type
            
        except Exception as e:
            self.logger.error(f"實驗類型檢測失敗: {str(e)}")
            return {'primary_type': 'Unknown', 'error': str(e)}
    
    def _generate_experiment_summary(self) -> Dict[str, Any]:
        """
        生成實驗摘要
        Generate experiment summary
        """
        try:
            txt_data = self.data
            summary = {
                'experiment_id': '',
                'user': '',
                'datetime': '',
                'scan_parameters': {},
                'file_counts': {},
                'estimated_duration': '',
                'data_size_estimate': ''
            }
            
            # 基本信息 / Basic information
            if self.file_path:
                summary['experiment_id'] = Path(self.file_path).stem
            
            exp_info = txt_data.experiment_info
            if 'UserName' in exp_info:
                summary['user'] = exp_info['UserName']
            
            if 'Date' in exp_info and 'Time' in exp_info:
                summary['datetime'] = f"{exp_info['Date']} {exp_info['Time']}"
            
            # 掃描參數摘要 / Scan parameters summary
            scan_params = txt_data.scan_parameters
            summary['scan_parameters'] = {
                'resolution': f"{scan_params.x_pixel}×{scan_params.y_pixel}",
                'size': f"{scan_params.x_range}×{scan_params.y_range} nm",
                'pixel_size': f"{scan_params.pixel_scale_x:.3f}×{scan_params.pixel_scale_y:.3f} nm/pixel"
            }
            
            # 文件統計 / File statistics
            summary['file_counts'] = {
                'int_files': len(txt_data.int_files),
                'dat_files': len(txt_data.dat_files),
                'total_files': txt_data.total_files
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"實驗摘要生成失敗: {str(e)}")
            return {'error': str(e)}
    
    def get_experiment_overview(self) -> Dict[str, Any]:
        """
        獲取實驗概覽
        Get experiment overview
        
        Returns:
            Dict: 實驗概覽 / Experiment overview
        """
        try:
            txt_data = self.data
            overview = {
                'experiment_name': txt_data.experiment_name,
                'total_files': txt_data.total_files,
                'signal_types': txt_data.signal_types,
                'scan_resolution': f"{txt_data.scan_parameters.x_pixel}×{txt_data.scan_parameters.y_pixel}",
                'scan_size': f"{txt_data.scan_parameters.x_range}×{txt_data.scan_parameters.y_range} nm",
                'measurement_modes': list(set(f.get('measurement_mode', 'unknown') 
                                           for f in txt_data.dat_files)),
                'int_file_types': list(set(f.get('caption', 'Unknown') 
                                        for f in txt_data.int_files))
            }
            
            return overview
            
        except Exception as e:
            self.logger.error(f"獲取實驗概覽失敗: {str(e)}")
            return {'error': str(e)}
    
    def validate_input(self, **kwargs) -> bool:
        """
        驗證 TXT 輸入數據
        Validate TXT input data
        """
        if not super().validate_input(**kwargs):
            return False
        
        if not isinstance(self.data, TxtData):
            self._add_error("數據必須是 TxtData 類型")
            return False
        
        if not self.data.experiment_info:
            self._add_error("TxtData 缺少 experiment_info")
            return False
        
        if not self.data.scan_parameters:
            self._add_error("TxtData 缺少 scan_parameters")
            return False
        
        return True