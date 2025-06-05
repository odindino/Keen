"""
主分析器
Main analyzer

整個 SPM 數據分析系統的統一入口和協調器
Unified entry point and coordinator for the entire SPM data analysis system
"""

import logging
from typing import Dict, Any, Optional, List, Union
from pathlib import Path

from .analyzers.txt_analyzer import TxtAnalyzer
from .analyzers.int_analyzer import IntAnalyzer
from .analyzers.dat_analyzer import DatAnalyzer
from .analyzers.cits_analyzer import CitsAnalyzer
from .parsers.txt_parser import TxtParser
from .parsers.int_parser import IntParser
from .parsers.dat_parser import DatParser


class MainAnalyzer:
    """
    主分析器類
    Main analyzer class
    
    作為整個分析系統的中央協調器，管理多個數據集和分析器
    Acts as central coordinator for the entire analysis system, managing multiple datasets and analyzers
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化主分析器
        Initialize main analyzer
        
        Args:
            config: 配置字典 / Configuration dictionary
        """
        self.logger = logging.getLogger(__name__)
        
        # 配置管理 / Configuration management
        self.config = config or self._get_default_config()
        
        # 初始化分析器 / Initialize analyzers
        self.analyzers: Dict[str, Any] = {}
        self._initialize_analyzers()
        
        # 數據管理 / Data management
        self.loaded_experiments: Dict[str, Dict] = {}
        self.current_experiment: Optional[str] = None
        
        # 解析器類別 / Parser classes  
        self.parser_classes = {
            'txt': TxtParser,
            'int': IntParser,
            'dat': DatParser
        }
        
        self.logger.info("主分析器初始化完成")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        獲取默認配置
        Get default configuration
        
        Returns:
            Dict: 默認配置 / Default configuration
        """
        return {
            'max_experiments': 10,
            'auto_save_results': True,
            'cache_enabled': True,
            'log_level': 'INFO',
            'supported_formats': ['txt', 'int', 'dat'],
            'default_physical_scale': None
        }
    
    def _initialize_analyzers(self) -> None:
        """
        初始化各個分析器
        Initialize all analyzers
        """
        try:
            self.analyzers = {
                'txt': TxtAnalyzer(self),
                'int': IntAnalyzer(self),
                'dat': DatAnalyzer(self),
                'cits': CitsAnalyzer(self)
            }
            self.logger.info("所有分析器初始化完成")
        except Exception as e:
            self.logger.error(f"分析器初始化失敗: {str(e)}")
            raise
    
    @property
    def txt_analyzer(self) -> TxtAnalyzer:
        """獲取 TXT 分析器 / Get TXT analyzer"""
        return self.analyzers['txt']
    
    @property
    def int_analyzer(self) -> IntAnalyzer:
        """獲取 INT 分析器 / Get INT analyzer"""
        return self.analyzers['int']
    
    @property
    def dat_analyzer(self) -> DatAnalyzer:
        """獲取 DAT 分析器 / Get DAT analyzer"""
        return self.analyzers['dat']
    
    @property
    def cits_analyzer(self) -> CitsAnalyzer:
        """獲取 CITS 分析器 / Get CITS analyzer"""
        return self.analyzers['cits']
    
    def load_experiment(self, txt_file_path: str, 
                       experiment_name: Optional[str] = None) -> Dict[str, Any]:
        """
        載入 SPM 實驗
        Load SPM experiment
        
        Args:
            txt_file_path: TXT 檔案路徑 / TXT file path
            experiment_name: 實驗名稱（可選）/ Experiment name (optional)
            
        Returns:
            Dict: 載入結果 / Loading result
        """
        try:
            txt_path = Path(txt_file_path)
            if not txt_path.exists():
                return self._create_error_result(f"檔案不存在: {txt_file_path}")
            
            # 解析 TXT 檔案 / Parse TXT file
            txt_parser = self.parser_classes['txt'](str(txt_path))
            txt_data = txt_parser.parse()
            txt_result = {'success': True, 'data': txt_data}
            if not txt_result['success']:
                return txt_result
            
            txt_data = txt_result['data']
            
            # 生成實驗名稱 / Generate experiment name
            if experiment_name is None:
                experiment_name = txt_path.stem
            
            # 載入關聯的數據檔案 / Load associated data files
            experiment_data = {
                'name': experiment_name,
                'txt_file': str(txt_path),
                'txt_data': txt_data,
                'associated_files': {},
                'loaded_analyzers': []
            }
            
            # 尋找並載入 INT 檔案 / Find and load INT files
            int_files = self._find_associated_files(txt_path, '.int')
            exp_info = txt_data.get('experiment_info', {})
            
            # 從TXT文件獲取掃描參數
            try:
                x_pixel = int(exp_info.get('xPixel', 256))
                y_pixel = int(exp_info.get('yPixel', 256))
                x_range = float(exp_info.get('XScanRange', 100.0))
                scale = x_range / x_pixel
            except (ValueError, KeyError):
                self.logger.warning("使用默認掃描參數")
                x_pixel, y_pixel, scale = 256, 256, 1.0
            
            for int_file in int_files:
                try:
                    int_parser = self.parser_classes['int'](str(int_file), scale, x_pixel, y_pixel)
                    int_data = int_parser.parse()
                    int_result = {'success': True, 'data': int_data} if int_data else {'success': False}
                    if int_result['success']:
                        file_key = int_file.stem
                        experiment_data['associated_files'][file_key] = {
                            'type': 'int',
                            'path': str(int_file),
                            'data': int_result['data']
                        }
                except Exception as e:
                    self.logger.error(f"載入INT文件失敗 {int_file}: {e}")
                    continue
            
            # 尋找並載入 DAT 檔案 / Find and load DAT files
            dat_files = self._find_associated_files(txt_path, '.dat')
            for dat_file in dat_files:
                try:
                    dat_parser = self.parser_classes['dat']()
                    dat_data = dat_parser.parse(str(dat_file))
                    dat_result = {'success': True, 'data': dat_data} if dat_data else {'success': False}
                    if dat_result['success']:
                        file_key = dat_file.stem
                        experiment_data['associated_files'][file_key] = {
                            'type': 'dat',
                            'path': str(dat_file),
                            'data': dat_result['data']
                        }
                except Exception as e:
                    self.logger.error(f"載入DAT文件失敗 {dat_file}: {e}")
                    continue
            
            # 保存實驗數據 / Save experiment data
            self.loaded_experiments[experiment_name] = experiment_data
            self.current_experiment = experiment_name
            
            result = {
                'success': True,
                'data': {
                    'experiment_name': experiment_name,
                    'txt_data': txt_data,
                    'int_files_count': len([f for f in experiment_data['associated_files'].values() if f['type'] == 'int']),
                    'dat_files_count': len([f for f in experiment_data['associated_files'].values() if f['type'] == 'dat']),
                    'associated_files': list(experiment_data['associated_files'].keys())
                },
                'message': f"實驗 '{experiment_name}' 載入成功"
            }
            
            self.logger.info(f"實驗載入成功: {experiment_name}")
            return result
            
        except Exception as e:
            error_msg = f"實驗載入失敗: {str(e)}"
            self.logger.error(error_msg)
            return self._create_error_result(error_msg)
    
    def get_analyzer(self, analyzer_type: str) -> Optional[Any]:
        """
        獲取分析器實例
        Get analyzer instance
        
        Args:
            analyzer_type: 分析器類型 ('int', 'cits') / Analyzer type
            
        Returns:
            分析器實例或 None / Analyzer instance or None
        """
        return self.analyzers.get(analyzer_type)
    
    def analyze_int_data(self, file_key: str, 
                        experiment_name: Optional[str] = None,
                        **kwargs) -> Dict[str, Any]:
        """
        分析 INT 數據
        Analyze INT data
        
        Args:
            file_key: 檔案鍵值 / File key
            experiment_name: 實驗名稱 / Experiment name
            **kwargs: 額外參數 / Additional parameters
            
        Returns:
            Dict: 分析結果 / Analysis result
        """
        try:
            # 確定實驗名稱 / Determine experiment name
            exp_name = experiment_name or self.current_experiment
            if exp_name not in self.loaded_experiments:
                return self._create_error_result(f"實驗未載入: {exp_name}")
            
            experiment = self.loaded_experiments[exp_name]
            
            # 檢查檔案是否存在 / Check if file exists
            if file_key not in experiment['associated_files']:
                return self._create_error_result(f"檔案未找到: {file_key}")
            
            file_info = experiment['associated_files'][file_key]
            if file_info['type'] != 'int':
                return self._create_error_result(f"檔案類型錯誤: {file_info['type']}，期望: int")
            
            # 獲取 INT 分析器 / Get INT analyzer
            int_analyzer = self.get_analyzer('int')
            if int_analyzer is None:
                return self._create_error_result("INT 分析器未初始化")
            
            # 執行分析 / Execute analysis
            image_data = file_info['data']['image_data']
            physical_scale = kwargs.get('physical_scale', self.config['default_physical_scale'])
            
            result = int_analyzer.analyze(image_data, physical_scale, **kwargs)
            
            return result
            
        except Exception as e:
            error_msg = f"INT 數據分析失敗: {str(e)}"
            self.logger.error(error_msg)
            return self._create_error_result(error_msg)
    
    def analyze_cits_data(self, file_key: str,
                         experiment_name: Optional[str] = None,
                         **kwargs) -> Dict[str, Any]:
        """
        分析 CITS 數據
        Analyze CITS data
        
        Args:
            file_key: 檔案鍵值 / File key
            experiment_name: 實驗名稱 / Experiment name
            **kwargs: 額外參數 / Additional parameters
            
        Returns:
            Dict: 分析結果 / Analysis result
        """
        try:
            # 確定實驗名稱 / Determine experiment name
            exp_name = experiment_name or self.current_experiment
            if exp_name not in self.loaded_experiments:
                return self._create_error_result(f"實驗未載入: {exp_name}")
            
            experiment = self.loaded_experiments[exp_name]
            
            # 檢查檔案是否存在 / Check if file exists
            if file_key not in experiment['associated_files']:
                return self._create_error_result(f"檔案未找到: {file_key}")
            
            file_info = experiment['associated_files'][file_key]
            if file_info['type'] != 'dat':
                return self._create_error_result(f"檔案類型錯誤: {file_info['type']}，期望: dat")
            
            # 檢查是否為 CITS 數據 / Check if it's CITS data
            dat_data = file_info['data']
            if dat_data.get('data_type') != 'CITS':
                return self._create_error_result(f"數據類型錯誤: {dat_data.get('data_type')}，期望: CITS")
            
            # 獲取 CITS 分析器 / Get CITS analyzer
            cits_analyzer = self.get_analyzer('cits')
            if cits_analyzer is None:
                return self._create_error_result("CITS 分析器未初始化")
            
            # 執行分析 / Execute analysis
            result = cits_analyzer.analyze(dat_data, **kwargs)
            
            return result
            
        except Exception as e:
            error_msg = f"CITS 數據分析失敗: {str(e)}"
            self.logger.error(error_msg)
            return self._create_error_result(error_msg)
    
    def get_experiment_summary(self, experiment_name: Optional[str] = None) -> Dict[str, Any]:
        """
        獲取實驗摘要
        Get experiment summary
        
        Args:
            experiment_name: 實驗名稱 / Experiment name
            
        Returns:
            Dict: 實驗摘要 / Experiment summary
        """
        try:
            exp_name = experiment_name or self.current_experiment
            if exp_name not in self.loaded_experiments:
                return self._create_error_result(f"實驗未載入: {exp_name}")
            
            experiment = self.loaded_experiments[exp_name]
            
            # 統計檔案資訊 / Count file information
            int_files = [k for k, v in experiment['associated_files'].items() if v['type'] == 'int']
            dat_files = [k for k, v in experiment['associated_files'].items() if v['type'] == 'dat']
            cits_files = [k for k, v in experiment['associated_files'].items() 
                         if v['type'] == 'dat' and v['data'].get('data_type') == 'CITS']
            
            summary = {
                'success': True,
                'data': {
                    'experiment_name': exp_name,
                    'txt_file': experiment['txt_file'],
                    'files_summary': {
                        'int_files': len(int_files),
                        'dat_files': len(dat_files),
                        'cits_files': len(cits_files),
                        'total_files': len(experiment['associated_files'])
                    },
                    'file_list': {
                        'int_files': int_files,
                        'dat_files': dat_files,
                        'cits_files': cits_files
                    },
                    'loaded_analyzers': experiment['loaded_analyzers'],
                    'txt_metadata': experiment['txt_data'].get('metadata', {})
                }
            }
            
            return summary
            
        except Exception as e:
            error_msg = f"獲取實驗摘要失敗: {str(e)}"
            self.logger.error(error_msg)
            return self._create_error_result(error_msg)
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        獲取系統狀態
        Get system status
        
        Returns:
            Dict: 系統狀態 / System status
        """
        try:
            status = {
                'success': True,
                'data': {
                    'system_info': {
                        'total_experiments': len(self.loaded_experiments),
                        'current_experiment': self.current_experiment,
                        'analyzers_loaded': list(self.analyzers.keys()),
                        'supported_formats': self.config['supported_formats']
                    },
                    'config': self.config
                }
            }
            
            return status
            
        except Exception as e:
            error_msg = f"獲取系統狀態失敗: {str(e)}"
            self.logger.error(error_msg)
            return self._create_error_result(error_msg)
    
    def list_experiments(self) -> Dict[str, Any]:
        """
        列出所有載入的實驗
        List all loaded experiments
        
        Returns:
            Dict: 實驗列表 / Experiment list
        """
        try:
            experiments_info = []
            
            for exp_name, exp_data in self.loaded_experiments.items():
                info = {
                    'name': exp_name,
                    'txt_file': exp_data['txt_file'],
                    'file_count': len(exp_data['associated_files']),
                    'loaded_analyzers': exp_data['loaded_analyzers'],
                    'is_current': exp_name == self.current_experiment
                }
                experiments_info.append(info)
            
            return {
                'success': True,
                'data': {
                    'total_experiments': len(self.loaded_experiments),
                    'current_experiment': self.current_experiment,
                    'experiments': experiments_info
                }
            }
            
        except Exception as e:
            error_msg = f"列出實驗失敗: {str(e)}"
            self.logger.error(error_msg)
            return self._create_error_result(error_msg)
    
    def get_current_experiment(self) -> Optional[Dict[str, Any]]:
        """
        獲取當前實驗數據
        Get current experiment data
        
        Returns:
            Optional[Dict]: 當前實驗數據 / Current experiment data
        """
        if self.current_experiment and self.current_experiment in self.loaded_experiments:
            return self.loaded_experiments[self.current_experiment]
        return None
    
    def _find_associated_files(self, txt_path: Path, extension: str) -> List[Path]:
        """
        尋找關聯檔案
        Find associated files
        
        Args:
            txt_path: TXT 檔案路徑 / TXT file path
            extension: 檔案副檔名 / File extension
            
        Returns:
            List[Path]: 關聯檔案列表 / Associated files list
        """
        base_name = txt_path.stem
        parent_dir = txt_path.parent
        
        # 尋找具有相同基礎名稱的檔案 / Find files with same base name
        pattern = f"{base_name}*{extension}"
        associated_files = list(parent_dir.glob(pattern))
        
        return associated_files
    
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
            'data': {}
        }