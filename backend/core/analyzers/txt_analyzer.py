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

from .base_analyzer import BaseAnalyzer


class TxtAnalyzer(BaseAnalyzer):
    """
    TXT 分析器
    TXT analyzer
    
    提供 TXT（實驗參數）文件的完整分析工作流
    Provides complete analysis workflow for TXT (experiment parameter) files
    """
    
    def __init__(self, main_analyzer):
        """
        初始化 TXT 分析器
        Initialize TXT analyzer
        
        Args:
            main_analyzer: 主分析器實例 / Main analyzer instance
        """
        super().__init__(main_analyzer)
        
        # TXT 特定狀態 / TXT-specific state
        self.experiment_info: Optional[Dict] = None
        self.int_files_info: List[Dict] = []
        self.dat_files_info: List[Dict] = []
        self.file_path: Optional[str] = None
        
        # 驗證結果 / Validation results
        self.validation_results: Optional[Dict] = None
        self.file_availability: Optional[Dict] = None
    
    def analyze(self, txt_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        分析 TXT 實驗參數數據
        Analyze TXT experiment parameter data
        
        Args:
            txt_data: TXT 數據字典 / TXT data dictionary
                From TxtParser.parse() containing:
                - 'experiment_info': dict of experiment parameters
                - 'int_files': list of int file descriptions
                - 'dat_files': list of dat file descriptions
            **kwargs: 額外參數，包含 'file_path' / Additional parameters including 'file_path'
            
        Returns:
            Dict: 分析結果 / Analysis results
        """
        try:
            if not self.validate_input(txt_data, **kwargs):
                return self._create_error_result("輸入驗證失敗")
            
            # 保存數據 / Save data
            self.experiment_info = txt_data.get('experiment_info', {})
            self.int_files_info = txt_data.get('int_files', [])
            self.dat_files_info = txt_data.get('dat_files', [])
            self.file_path = kwargs.get('file_path')
            
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
                    'experiment_info': self.experiment_info,
                    'parameter_analysis': param_analysis,
                    'file_analysis': file_analysis,
                    'availability_analysis': availability_analysis,
                    'experiment_type': experiment_type,
                    'summary': summary
                },
                'plots': {},  # TXT files typically don't have plots
                'metadata': {
                    'analyzer_type': 'TXT',
                    'file_path': self.file_path,
                    'n_int_files': len(self.int_files_info),
                    'n_dat_files': len(self.dat_files_info)
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
            analysis = {
                'scan_info': {},
                'tunneling_info': {},
                'feedback_info': {},
                'timing_info': {}
            }
            
            # 掃描信息 / Scan information
            if 'xPixel' in self.experiment_info and 'yPixel' in self.experiment_info:
                x_pixels = int(self.experiment_info['xPixel'])
                y_pixels = int(self.experiment_info['yPixel'])
                analysis['scan_info']['resolution'] = [x_pixels, y_pixels]
                analysis['scan_info']['total_pixels'] = x_pixels * y_pixels
            
            if 'XScanRange' in self.experiment_info and 'YScanRange' in self.experiment_info:
                x_range = float(self.experiment_info['XScanRange'])
                y_range = float(self.experiment_info['YScanRange'])
                analysis['scan_info']['scan_size'] = [x_range, y_range]
                
                if 'resolution' in analysis['scan_info']:
                    x_pixels = analysis['scan_info']['resolution'][0]
                    y_pixels = analysis['scan_info']['resolution'][1]
                    analysis['scan_info']['pixel_size'] = [
                        x_range / x_pixels, y_range / y_pixels
                    ]
            
            # 隧道參數 / Tunneling parameters
            if 'Bias' in self.experiment_info:
                analysis['tunneling_info']['bias_voltage'] = float(self.experiment_info['Bias'])
            
            if 'SetPoint' in self.experiment_info:
                analysis['tunneling_info']['setpoint_current'] = float(self.experiment_info['SetPoint'])
            
            # 反饋參數 / Feedback parameters
            if 'Ki' in self.experiment_info and 'Kp' in self.experiment_info:
                analysis['feedback_info']['ki'] = float(self.experiment_info['Ki'])
                analysis['feedback_info']['kp'] = float(self.experiment_info['Kp'])
            
            # 時間信息 / Timing information
            if 'Date' in self.experiment_info and 'Time' in self.experiment_info:
                analysis['timing_info']['date'] = self.experiment_info['Date']
                analysis['timing_info']['time'] = self.experiment_info['Time']
            
            if 'Speed' in self.experiment_info:
                try:
                    # 處理可能包含單位的速度值
                    speed_str = str(self.experiment_info['Speed']).strip()
                    # 移除可能的單位或額外文字
                    speed_num = speed_str.split()[0]  # 取第一個數值部分
                    analysis['timing_info']['scan_speed'] = float(speed_num)
                except (ValueError, IndexError):
                    self.logger.warning(f"無法解析掃描速度: {self.experiment_info['Speed']}")
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
            analysis = {
                'int_files_summary': {},
                'dat_files_summary': {},
                'measurement_modes': []
            }
            
            # INT 文件分析 / INT files analysis
            analysis['int_files_summary'] = {
                'count': len(self.int_files_info),
                'types': list(set(f.get('caption', 'Unknown') for f in self.int_files_info))
            }
            
            # DAT 文件分析 / DAT files analysis
            measurement_modes = []
            for dat_file in self.dat_files_info:
                mode = dat_file.get('measurement_mode', 'unknown')
                if mode not in measurement_modes:
                    measurement_modes.append(mode)
            
            analysis['dat_files_summary'] = {
                'count': len(self.dat_files_info),
                'measurement_modes': measurement_modes
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
            
            base_dir = os.path.dirname(self.file_path)
            
            # 檢查 INT 文件 / Check INT files
            for int_file in self.int_files_info:
                filename = int_file['filename']
                file_path = os.path.join(base_dir, filename)
                
                if os.path.exists(file_path):
                    availability['available_files'].append(filename)
                    availability['file_details'][filename] = {
                        'available': True,
                        'size': os.path.getsize(file_path),
                        'type': 'int'
                    }
                else:
                    availability['missing_files'].append(filename)
                    availability['file_details'][filename] = {
                        'available': False,
                        'type': 'int'
                    }
                    availability['all_files_available'] = False
            
            # 檢查 DAT 文件 / Check DAT files
            for dat_file in self.dat_files_info:
                filename = dat_file['filename']
                file_path = os.path.join(base_dir, filename)
                
                if os.path.exists(file_path):
                    availability['available_files'].append(filename)
                    availability['file_details'][filename] = {
                        'available': True,
                        'size': os.path.getsize(file_path),
                        'type': 'dat'
                    }
                else:
                    availability['missing_files'].append(filename)
                    availability['file_details'][filename] = {
                        'available': False,
                        'type': 'dat'
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
            exp_type = {
                'primary_type': 'Unknown',
                'secondary_types': [],
                'complexity': 'Simple',
                'description': ''
            }
            
            has_topo = len(self.int_files_info) > 0
            has_cits = any(f.get('measurement_mode') == 'CITS' for f in self.dat_files_info)
            has_sts = any(f.get('measurement_mode') == 'STS' for f in self.dat_files_info)
            
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
                summary['experiment_id'] = os.path.basename(self.file_path).replace('.txt', '')
            
            if 'UserName' in self.experiment_info:
                summary['user'] = self.experiment_info['UserName']
            
            if 'Date' in self.experiment_info and 'Time' in self.experiment_info:
                summary['datetime'] = f"{self.experiment_info['Date']} {self.experiment_info['Time']}"
            
            # 掃描參數摘要 / Scan parameters summary
            if 'xPixel' in self.experiment_info and 'yPixel' in self.experiment_info:
                summary['scan_parameters']['resolution'] = f"{self.experiment_info['xPixel']}×{self.experiment_info['yPixel']}"
            
            if 'XScanRange' in self.experiment_info and 'YScanRange' in self.experiment_info:
                summary['scan_parameters']['size'] = f"{self.experiment_info['XScanRange']}×{self.experiment_info['YScanRange']} nm"
            
            # 文件統計 / File statistics
            summary['file_counts'] = {
                'int_files': len(self.int_files_info),
                'dat_files': len(self.dat_files_info),
                'total_files': len(self.int_files_info) + len(self.dat_files_info)
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"實驗摘要生成失敗: {str(e)}")
            return {'error': str(e)}
    
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
        驗證 TXT 輸入數據
        Validate TXT input data
        """
        if not super().validate_input(data, **kwargs):
            return False
        
        if not isinstance(data, dict):
            self._add_error("輸入數據必須是字典")
            return False
        
        # 檢查必要欄位 / Check required fields
        required_fields = ['experiment_info']
        for field in required_fields:
            if field not in data:
                self._add_error(f"缺少必要欄位: {field}")
                return False
        
        return True