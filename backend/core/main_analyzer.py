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
    
    # 這裡不應該直接對所有的檔案都parse，這樣可能其實有很多檔案我都沒有要用。
    # 應該是先載入有哪些檔案，然後再根據需要載入特定的檔案。
    @property
    def cits_analyzer(self) -> CitsAnalyzer:
        """獲取 CITS 分析器 / Get CITS analyzer"""
        return self.analyzers['cits']
    
    def load_experiment(self, txt_file_path: str, 
                       experiment_name: Optional[str] = None) -> Dict[str, Any]:
        """
        載入 SPM 實驗（只解析 TXT 文件，其他文件按需載入）
        Load SPM experiment (only parse TXT file, load other files on demand)
        
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
            
            if not txt_data:
                return self._create_error_result("TXT 檔案解析失敗")
            
            # 生成實驗名稱 / Generate experiment name
            if experiment_name is None:
                experiment_name = txt_path.stem
            
            # 從 TXT 文件獲取掃描參數（用於後續解析 INT 文件）
            exp_info = txt_data.get('experiment_info', {})
            scan_params = self._extract_scan_parameters(exp_info)
            
            # 建立實驗數據結構 / Create experiment data structure
            experiment_data = {
                'name': experiment_name,
                'txt_file': str(txt_path),
                'txt_data': txt_data,
                'scan_parameters': scan_params,
                'available_files': {},  # 可用但未載入的檔案
                'loaded_files': {},     # 已載入並解析的檔案
                'loaded_analyzers': []
            }
            
            # 掃描可用的關聯檔案（不解析）/ Scan available associated files (without parsing)
            int_files = self._find_associated_files(txt_path, '.int')
            dat_files = self._find_associated_files(txt_path, '.dat')
            
            # 記錄可用檔案資訊 / Record available file information
            for int_file in int_files:
                file_key = int_file.stem
                experiment_data['available_files'][file_key] = {
                    'type': 'int',
                    'path': str(int_file),
                    'size': int_file.stat().st_size,
                    'loaded': False
                }
            
            for dat_file in dat_files:
                file_key = dat_file.stem
                experiment_data['available_files'][file_key] = {
                    'type': 'dat',
                    'path': str(dat_file),
                    'size': dat_file.stat().st_size,
                    'loaded': False
                }
            
            # 自己解析檔案名稱以提取訊號類型和方向
            int_files_info = []
            dat_files_info = []
            signal_types_set = set()
            
            # 解析 INT 檔案
            for file_key, file_info in experiment_data['available_files'].items():
                if file_info['type'] == 'int':
                    # 從檔案名稱提取訊號類型和方向
                    signal_type, direction = self._extract_signal_type_and_direction(file_key)
                    int_files_info.append({
                        'filename': file_key,
                        'signal_type': signal_type,
                        'direction': direction,
                        'path': file_info['path'],
                        'size': file_info['size']
                    })
                    if signal_type:
                        signal_types_set.add(signal_type)
                elif file_info['type'] == 'dat':
                    # 從檔案名稱提取訊號類型
                    signal_type, _ = self._extract_signal_type_and_direction(file_key)
                    dat_files_info.append({
                        'filename': file_key,
                        'signal_type': signal_type,
                        'path': file_info['path'],
                        'size': file_info['size']
                    })
                    if signal_type:
                        signal_types_set.add(signal_type)
            
            signal_types = list(signal_types_set)
            
            # 保存實驗數據 / Save experiment data
            self.loaded_experiments[experiment_name] = experiment_data
            self.current_experiment = experiment_name
            
            # 添加訊號類型和方向到可用檔案詳情中
            # 這樣在客戶端可以看到每個檔案的訊號類型和方向
            for file_key, file_info in experiment_data['available_files'].items():
                if file_info['type'] == 'int':
                    # 找到對應的 INT 檔案詳情
                    for int_info in int_files_info:
                        if int_info['filename'] == file_key:
                            file_info['signal_type'] = int_info['signal_type']
                            file_info['direction'] = int_info['direction']
                            break
                elif file_info['type'] == 'dat':
                    # 找到對應的 DAT 檔案詳情
                    for dat_info in dat_files_info:
                        if dat_info['filename'] == file_key:
                            file_info['signal_type'] = dat_info['signal_type']
                            break
            
            result = {
                'success': True,
                'data': {
                    'experiment_name': experiment_name,
                    'txt_data': txt_data,
                    'scan_parameters': scan_params,
                    'available_files': {
                        'int_files': [k for k, v in experiment_data['available_files'].items() if v['type'] == 'int'],
                        'dat_files': [k for k, v in experiment_data['available_files'].items() if v['type'] == 'dat'],
                        'total_count': len(experiment_data['available_files'])
                    },
                    'int_files': int_files_info,  # 包含訊號類型和方向的詳細 INT 檔案信息
                    'dat_files': dat_files_info,  # 包含訊號類型的詳細 DAT 檔案信息
                    'signal_types': signal_types,  # 實驗中包含的訊號類型列表
                    'loaded_files_count': 0  # 初始時沒有載入任何檔案
                },
                'message': f"實驗 '{experiment_name}' 載入成功（TXT 已解析，{len(experiment_data['available_files'])} 個關聯檔案可按需載入）"
            }
            
            self.logger.info(f"實驗載入成功: {experiment_name}，發現 {len(int_files)} 個 INT 檔案和 {len(dat_files)} 個 DAT 檔案")
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
            
            # 檢查檔案是否存在於可用檔案中 / Check if file exists in available files
            if file_key not in experiment['available_files']:
                return self._create_error_result(f"檔案未找到: {file_key}")
            
            file_info = experiment['available_files'][file_key]
            if file_info['type'] != 'int':
                return self._create_error_result(f"檔案類型錯誤: {file_info['type']}，期望: int")
            
            # 如果檔案尚未載入，先載入它 / If file is not loaded, load it first
            if not file_info['loaded']:
                load_result = self.load_file(file_key, exp_name)
                if not load_result['success']:
                    return load_result
            
            # 獲取已載入的檔案數據 / Get loaded file data
            loaded_file = experiment['loaded_files'][file_key]
            int_data = loaded_file['data']
            
            # 獲取 INT 分析器 / Get INT analyzer
            int_analyzer = self.get_analyzer('int')
            if int_analyzer is None:
                return self._create_error_result("INT 分析器未初始化")
            
            # 執行分析 / Execute analysis
            image_data = int_data.get('image_data')
            if image_data is None:
                return self._create_error_result("INT 檔案中未找到影像數據")
            
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
            
            # 檢查檔案是否存在於可用檔案中 / Check if file exists in available files
            if file_key not in experiment['available_files']:
                return self._create_error_result(f"檔案未找到: {file_key}")
            
            file_info = experiment['available_files'][file_key]
            if file_info['type'] != 'dat':
                return self._create_error_result(f"檔案類型錯誤: {file_info['type']}，期望: dat")
            
            # 如果檔案尚未載入，先載入它 / If file is not loaded, load it first
            if not file_info['loaded']:
                load_result = self.load_file(file_key, exp_name)
                if not load_result['success']:
                    return load_result
            
            # 獲取已載入的檔案數據 / Get loaded file data
            loaded_file = experiment['loaded_files'][file_key]
            dat_data = loaded_file['data']
            
            # 檢查是否為 CITS 數據 / Check if it's CITS data
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
            available_files = experiment['available_files']
            loaded_files = experiment['loaded_files']
            
            int_files = [k for k, v in available_files.items() if v['type'] == 'int']
            dat_files = [k for k, v in available_files.items() if v['type'] == 'dat']
            
            # 統計已載入的檔案 / Count loaded files
            loaded_int_files = [k for k in int_files if k in loaded_files]
            loaded_dat_files = [k for k in dat_files if k in loaded_files]
            
            # 統計 CITS 檔案（需要載入 DAT 檔案才能確定）
            # Count CITS files (need to load DAT files to determine)
            cits_files = []
            for file_key in dat_files:
                if file_key in loaded_files:
                    dat_data = loaded_files[file_key]['data']
                    if dat_data.get('data_type') == 'CITS':
                        cits_files.append(file_key)
            
            summary = {
                'success': True,
                'data': {
                    'experiment_name': exp_name,
                    'txt_file': experiment['txt_file'],
                    'scan_parameters': experiment['scan_parameters'],
                    'files_summary': {
                        'available_files': {
                            'int_files': len(int_files),
                            'dat_files': len(dat_files),
                            'total_files': len(available_files)
                        },
                        'loaded_files': {
                            'int_files': len(loaded_int_files),
                            'dat_files': len(loaded_dat_files),
                            'cits_files': len(cits_files),
                            'total_loaded': len(loaded_files)
                        }
                    },
                    'file_list': {
                        'available_int_files': int_files,
                        'available_dat_files': dat_files,
                        'loaded_int_files': loaded_int_files,
                        'loaded_dat_files': loaded_dat_files,
                        'cits_files': cits_files
                    },
                    'loaded_analyzers': experiment['loaded_analyzers'],
                    'txt_metadata': experiment['txt_data'].get('metadata', {}),
                    'memory_usage': {
                        'available_files_size': sum(v['size'] for v in available_files.values()),
                        'loaded_files_count': len(loaded_files)
                    }
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
                available_count = len(exp_data['available_files'])
                loaded_count = len(exp_data['loaded_files'])
                
                info = {
                    'name': exp_name,
                    'txt_file': exp_data['txt_file'],
                    'available_files_count': available_count,
                    'loaded_files_count': loaded_count,
                    'loaded_analyzers': exp_data['loaded_analyzers'],
                    'is_current': exp_name == self.current_experiment,
                    'scan_parameters': exp_data['scan_parameters']
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
    
    def _extract_scan_parameters(self, exp_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        從實驗資訊中提取掃描參數
        Extract scan parameters from experiment info
        
        Args:
            exp_info: 實驗資訊字典 / Experiment info dictionary
            
        Returns:
            Dict: 掃描參數 / Scan parameters
        """
        try:
            x_pixel = int(exp_info.get('xPixel', 256))
            y_pixel = int(exp_info.get('yPixel', 256))
            x_range = float(exp_info.get('XScanRange', 100.0))
            y_range = float(exp_info.get('YScanRange', 100.0))
            scale = x_range / x_pixel
            
            return {
                'x_pixel': x_pixel,
                'y_pixel': y_pixel,
                'x_range': x_range,
                'y_range': y_range,
                'scale': scale
            }
        except (ValueError, KeyError) as e:
            self.logger.warning(f"無法提取掃描參數，使用默認值: {e}")
            return {
                'x_pixel': 256,
                'y_pixel': 256,
                'x_range': 100.0,
                'y_range': 100.0,
                'scale': 1.0
            }
    
    def _get_int_file_scale(self, file_key: str, txt_data: Dict[str, Any]) -> float:
        """
        從 TXT 解析結果中獲取特定 INT 檔案的 scale factor
        Get scale factor for specific INT file from TXT parsing result
        
        Args:
            file_key: INT 檔案的鍵值 / INT file key
            txt_data: TXT 解析結果 / TXT parsing result
            
        Returns:
            float: 該 INT 檔案的 scale factor
        """
        try:
            # 從 TXT 解析結果中找到對應的 INT 檔案資訊
            int_files = txt_data.get('int_files', [])
            
            # 尋找匹配的檔案名稱（支援檔案名稱可能包含或不包含 .int 副檔名）
            target_filename = file_key if file_key.endswith('.int') else f"{file_key}.int"
            
            for int_file_info in int_files:
                if int_file_info.get('filename') == target_filename:
                    scale_str = int_file_info.get('scale')
                    if scale_str:
                        try:
                            return float(scale_str)
                        except ValueError:
                            self.logger.warning(f"無法解析 INT 檔案 {file_key} 的 scale factor: {scale_str}")
                            break
            
            # 如果找不到或解析失敗，使用預設值
            self.logger.warning(f"未找到 INT 檔案 {file_key} 的 scale factor，使用預設值")
            return 1.0
            
        except Exception as e:
            self.logger.error(f"獲取 INT 檔案 scale factor 時出錯: {str(e)}")
            return 1.0
    
    def _get_dat_file_info(self, file_key: str, txt_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        從 TXT 解析結果中獲取特定 DAT 檔案的資訊
        Get DAT file information from TXT parsing result
        
        Args:
            file_key: DAT 檔案的鍵值 / DAT file key
            txt_data: TXT 解析結果 / TXT parsing result
            
        Returns:
            Dict: 該 DAT 檔案的相關資訊，包含量測模式、網格大小等
        """
        try:
            # 從 TXT 解析結果中找到對應的 DAT 檔案資訊
            dat_files = txt_data.get('dat_files', [])
            
            # 尋找匹配的檔案名稱（支援檔案名稱可能包含或不包含 .dat 副檔名）
            target_filename = file_key if file_key.endswith('.dat') else f"{file_key}.dat"
            
            for dat_file_info in dat_files:
                if dat_file_info.get('filename') == target_filename:
                    # 提取掃描參數資訊
                    scan_info = txt_data.get('scan_info', {})
                    
                    # 組合 DAT 檔案解析需要的資訊
                    dat_info = {
                        'measurement_mode': dat_file_info.get('measurement_type', 'unknown'),
                        'grid_x': scan_info.get('x_pixel', 256),
                        'grid_y': scan_info.get('y_pixel', 256),
                        'header_cols': dat_file_info.get('header_cols'),
                        'header_rows': dat_file_info.get('header_rows'),
                        'average': dat_file_info.get('average'),
                        'delays_raw': dat_file_info.get('delays_raw'),
                        'slewrate_raw': dat_file_info.get('slewrate_raw'),
                        'caption': dat_file_info.get('caption'),
                        'signal_type': dat_file_info.get('signal_type'),
                        'direction': dat_file_info.get('direction')
                    }
                    
                    # 移除值為 None 的鍵
                    dat_info = {k: v for k, v in dat_info.items() if v is not None}
                    
                    return dat_info
            
            # 如果找不到對應的 DAT 檔案資訊，記錄警告並返回基本資訊
            self.logger.warning(f"未找到 DAT 檔案 {file_key} 的詳細資訊，使用基本設定")
            scan_info = txt_data.get('scan_info', {})
            return {
                'measurement_mode': 'unknown',
                'grid_x': scan_info.get('x_pixel', 256),
                'grid_y': scan_info.get('y_pixel', 256)
            }
            
        except Exception as e:
            self.logger.warning(f"提取 DAT 檔案資訊時發生錯誤: {e}，使用基本設定")
            return {
                'measurement_mode': 'unknown',
                'grid_x': 256,
                'grid_y': 256
            }

    def load_file(self, file_key: str, 
                  experiment_name: Optional[str] = None) -> Dict[str, Any]:
        """
        按需載入並解析特定檔案
        Load and parse specific file on demand
        
        Args:
            file_key: 檔案鍵值 / File key
            experiment_name: 實驗名稱（可選）/ Experiment name (optional)
            
        Returns:
            Dict: 載入結果 / Loading result
        """
        try:
            # 確定實驗名稱 / Determine experiment name
            exp_name = experiment_name or self.current_experiment
            if exp_name not in self.loaded_experiments:
                return self._create_error_result(f"實驗未載入: {exp_name}")
            
            experiment = self.loaded_experiments[exp_name]
            
            # 檢查檔案是否存在於可用檔案中 / Check if file exists in available files
            if file_key not in experiment['available_files']:
                return self._create_error_result(f"檔案未找到: {file_key}")
            
            file_info = experiment['available_files'][file_key]
            
            # 檢查檔案是否已經載入 / Check if file is already loaded
            if file_info['loaded']:
                return {
                    'success': True,
                    'data': experiment['loaded_files'][file_key]['data'],
                    'file_type': file_info['type'],
                    'file_size': file_info['size'],
                    'message': f"檔案 '{file_key}' 已經載入",
                    'from_cache': True
                }
            
            # 根據檔案類型選擇解析器 / Choose parser based on file type
            file_path = file_info['path']
            file_type = file_info['type']
            
            if file_type == 'int':
                # 載入 INT 檔案 / Load INT file
                scan_params = experiment['scan_parameters']
                
                # 從 TXT 解析結果中獲取這個 INT 檔案的正確 scale factor
                int_file_scale = self._get_int_file_scale(file_key, experiment['txt_data'])
                
                int_parser = self.parser_classes['int'](
                    file_path, 
                    int_file_scale,  # 使用 TXT 檔案中的 scale factor，不是計算的空間 scale
                    scan_params['x_pixel'], 
                    scan_params['y_pixel']
                )
                parsed_data = int_parser.parse()
                
            elif file_type == 'dat':
                # 載入 DAT 檔案 / Load DAT file
                # 從 TXT 解析結果中獲取這個 DAT 檔案的相關資訊
                dat_info = self._get_dat_file_info(file_key, experiment['txt_data'])
                
                dat_parser = self.parser_classes['dat']()
                parsed_data = dat_parser.parse(file_path, dat_info)
                
            else:
                return self._create_error_result(f"不支援的檔案類型: {file_type}")
            
            if not parsed_data:
                return self._create_error_result(f"檔案解析失敗: {file_key}")
            
            # 將解析後的數據加入已載入檔案 / Add parsed data to loaded files
            experiment['loaded_files'][file_key] = {
                'type': file_type,
                'path': file_path,
                'data': parsed_data,
                'loaded_at': self._get_current_time()
            }
            
            # 更新可用檔案狀態 / Update available file status
            experiment['available_files'][file_key]['loaded'] = True
            
            result = {
                'success': True,
                'data': parsed_data,
                'message': f"檔案 '{file_key}' 載入成功",
                'from_cache': False,
                'file_type': file_type,
                'file_size': file_info['size']
            }
            
            self.logger.info(f"檔案載入成功: {file_key} ({file_type})")
            return result
            
        except Exception as e:
            error_msg = f"檔案載入失敗: {str(e)}"
            self.logger.error(error_msg)
            return self._create_error_result(error_msg)
    
    def unload_file(self, file_key: str, 
                    experiment_name: Optional[str] = None) -> Dict[str, Any]:
        """
        卸載已載入的檔案以釋放記憶體
        Unload loaded file to free memory
        
        Args:
            file_key: 檔案鍵值 / File key
            experiment_name: 實驗名稱（可選）/ Experiment name (optional)
            
        Returns:
            Dict: 卸載結果 / Unload result
        """
        try:
            exp_name = experiment_name or self.current_experiment
            if exp_name not in self.loaded_experiments:
                return self._create_error_result(f"實驗未載入: {exp_name}")
            
            experiment = self.loaded_experiments[exp_name]
            
            if file_key not in experiment['loaded_files']:
                return self._create_error_result(f"檔案未載入: {file_key}")
            
            # 移除已載入的數據 / Remove loaded data
            del experiment['loaded_files'][file_key]
            
            # 更新可用檔案狀態 / Update available file status
            if file_key in experiment['available_files']:
                experiment['available_files'][file_key]['loaded'] = False
            
            return {
                'success': True,
                'message': f"檔案 '{file_key}' 已卸載"
            }
            
        except Exception as e:
            error_msg = f"檔案卸載失敗: {str(e)}"
            self.logger.error(error_msg)
            return self._create_error_result(error_msg)

    def _get_current_time(self) -> str:
        """獲取當前時間字串"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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
    
    def get_file_status(self, experiment_name: Optional[str] = None) -> Dict[str, Any]:
        """
        獲取檔案載入狀態
        Get file loading status
        
        Args:
            experiment_name: 實驗名稱（可選）/ Experiment name (optional)
            
        Returns:
            Dict: 檔案狀態資訊 / File status information
        """
        try:
            exp_name = experiment_name or self.current_experiment
            if exp_name not in self.loaded_experiments:
                return self._create_error_result(f"實驗未載入: {exp_name}")
            
            experiment = self.loaded_experiments[exp_name]
            available_files = experiment['available_files']
            loaded_files = experiment['loaded_files']
            
            file_status = {}
            total_size = 0
            loaded_size = 0
            
            for file_key, file_info in available_files.items():
                file_size = file_info['size']
                total_size += file_size
                
                status = {
                    'type': file_info['type'],
                    'path': file_info['path'],
                    'size': file_size,
                    'loaded': file_info['loaded']
                }
                
                if file_info['loaded']:
                    loaded_size += file_size
                    loaded_file = loaded_files[file_key]
                    status['loaded_at'] = loaded_file.get('loaded_at', 'Unknown')
                
                file_status[file_key] = status
            
            return {
                'success': True,
                'data': {
                    'experiment_name': exp_name,
                    'file_status': file_status,
                    'summary': {
                        'total_files': len(available_files),
                        'loaded_files': len(loaded_files),
                        'total_size_bytes': total_size,
                        'loaded_size_bytes': loaded_size,
                        'loading_percentage': (len(loaded_files) / len(available_files) * 100) if available_files else 0
                    }
                }
            }
            
        except Exception as e:
            error_msg = f"獲取檔案狀態失敗: {str(e)}"
            self.logger.error(error_msg)
            return self._create_error_result(error_msg)

    def load_multiple_files(self, file_keys: List[str], 
                           experiment_name: Optional[str] = None) -> Dict[str, Any]:
        """
        批量載入多個檔案
        Load multiple files in batch
        
        Args:
            file_keys: 檔案鍵值列表 / List of file keys
            experiment_name: 實驗名稱（可選）/ Experiment name (optional)
            
        Returns:
            Dict: 批量載入結果 / Batch loading result
        """
        try:
            exp_name = experiment_name or self.current_experiment
            if exp_name not in self.loaded_experiments:
                return self._create_error_result(f"實驗未載入: {exp_name}")
            
            results = {}
            success_count = 0
            fail_count = 0
            
            for file_key in file_keys:
                result = self.load_file(file_key, exp_name)
                results[file_key] = result
                
                if result['success']:
                    success_count += 1
                else:
                    fail_count += 1
            
            return {
                'success': True,
                'data': {
                    'results': results,
                    'summary': {
                        'total_files': len(file_keys),
                        'success_count': success_count,
                        'fail_count': fail_count,
                        'success_rate': (success_count / len(file_keys) * 100) if file_keys else 0
                    }
                },
                'message': f"批量載入完成：{success_count} 成功，{fail_count} 失敗"
            }
            
        except Exception as e:
            error_msg = f"批量載入失敗: {str(e)}"
            self.logger.error(error_msg)
            return self._create_error_result(error_msg)

    def unload_all_files(self, experiment_name: Optional[str] = None) -> Dict[str, Any]:
        """
        卸載所有已載入的檔案
        Unload all loaded files
        
        Args:
            experiment_name: 實驗名稱（可選）/ Experiment name (optional)
            
        Returns:
            Dict: 卸載結果 / Unload result
        """
        try:
            exp_name = experiment_name or self.current_experiment
            if exp_name not in self.loaded_experiments:
                return self._create_error_result(f"實驗未載入: {exp_name}")
            
            experiment = self.loaded_experiments[exp_name]
            loaded_files = list(experiment['loaded_files'].keys())
            unloaded_count = 0
            
            for file_key in loaded_files:
                result = self.unload_file(file_key, exp_name)
                if result['success']:
                    unloaded_count += 1
            
            return {
                'success': True,
                'data': {
                    'unloaded_files': loaded_files,
                    'unloaded_count': unloaded_count
                },
                'message': f"已卸載 {unloaded_count} 個檔案"
            }
            
        except Exception as e:
            error_msg = f"卸載所有檔案失敗: {str(e)}"
            self.logger.error(error_msg)
            return self._create_error_result(error_msg)

    def get_memory_usage(self, experiment_name: Optional[str] = None) -> Dict[str, Any]:
        """
        獲取記憶體使用情況
        Get memory usage information
        
        Args:
            experiment_name: 實驗名稱（可選）/ Experiment name (optional)
            
        Returns:
            Dict: 記憶體使用資訊 / Memory usage information
        """
        try:
            exp_name = experiment_name or self.current_experiment
            if exp_name not in self.loaded_experiments:
                return self._create_error_result(f"實驗未載入: {exp_name}")
            
            experiment = self.loaded_experiments[exp_name]
            available_files = experiment['available_files']
            loaded_files = experiment['loaded_files']
            
            # 計算檔案大小 / Calculate file sizes
            total_available_size = sum(f['size'] for f in available_files.values())
            loaded_file_size = sum(
                available_files[k]['size'] for k in loaded_files.keys() 
                if k in available_files
            )
            
            return {
                'success': True,
                'data': {
                    'experiment_name': exp_name,
                    'file_counts': {
                        'total_available': len(available_files),
                        'currently_loaded': len(loaded_files)
                    },
                    'size_info': {
                        'total_available_bytes': total_available_size,
                        'currently_loaded_bytes': loaded_file_size,
                        'memory_efficiency': (loaded_file_size / total_available_size * 100) if total_available_size > 0 else 0
                    },
                    'human_readable': {
                        'total_available': self._format_file_size(total_available_size),
                        'currently_loaded': self._format_file_size(loaded_file_size)
                    }
                }
            }
            
        except Exception as e:
            error_msg = f"獲取記憶體使用情況失敗: {str(e)}"
            self.logger.error(error_msg)
            return self._create_error_result(error_msg)

    def _format_file_size(self, size_bytes: int) -> str:
        """
        格式化檔案大小為人類可讀格式
        Format file size to human-readable format
        
        Args:
            size_bytes: 位元組大小 / Size in bytes
            
        Returns:
            str: 格式化的大小字串 / Formatted size string
        """
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
    
    def _extract_signal_type_and_direction(self, filename: str) -> tuple:
        """
        從檔案名稱中提取訊號類型和掃描方向
        Extract signal type and scan direction from filename
        
        Args:
            filename: 檔案名稱 / File name
            
        Returns:
            tuple: (signal_type, direction)
        """
        try:
            # 檢查是否有 Matrix 後綴（表示是 DAT 檔案的 CITS 數據）
            if "_Matrix" in filename:
                # 例如：20250521_Janus Stacking SiO2_13K_113Lia1R_Matrix
                signal_type = filename.split('_Matrix')[0].split('_')[-1]
                if signal_type.startswith('113'):  # 忽略前綴序號
                    signal_type = signal_type[3:]
                direction = None
            else:
                # 尋找常見的訊號類型模式
                signal_patterns = [
                    "Topo", "Lia1X", "Lia1Y", "Lia1R", "Lia2X", "Lia2Y", "Lia2R", 
                    "Lia3X", "Lia3Y", "Lia3R", "It_to_PC", "InA", "QPlus", 
                    "Bias", "Frequency", "Drive", "Phase", "df"
                ]
                
                # 尋找訊號類型
                signal_type = None
                for pattern in signal_patterns:
                    if pattern in filename:
                        signal_type = pattern
                        break
                
                # 如果找不到匹配的訊號類型，嘗試一般性規則
                if signal_type is None:
                    # 取最後一段作為信號類型和方向
                    name_parts = filename.split('_')[-1]
                    # 尋找 Fwd 或 Bwd
                    if "Fwd" in name_parts:
                        signal_type = name_parts.replace("Fwd", "")
                        direction = "Fwd"
                    elif "Bwd" in name_parts:
                        signal_type = name_parts.replace("Bwd", "")
                        direction = "Bwd"
                    else:
                        signal_type = name_parts
                        direction = None
                else:
                    # 如果找到了訊號類型，檢查方向
                    if "Fwd" in filename:
                        direction = "Fwd"
                    elif "Bwd" in filename:
                        direction = "Bwd"
                    else:
                        direction = None
                
            return signal_type, direction
        except Exception as e:
            self.logger.warning(f"解析檔案名稱時出錯: {filename}, 錯誤: {str(e)}")
            return "unknown", None