"""
型別管理器
Type Managers

提供各種檔案類型的專門管理器，負責載入、快取、分析器管理
Provides specialized managers for different file types, handling loading, caching, and analyzer management
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Type
import logging
from pathlib import Path
from datetime import datetime

from .data_models import (
    FileInfo, ParseResult, TopoData, CitsData, StsData, TxtData,
    AnalysisState, SPMData
)


class TypeManager(ABC):
    """
    型別管理器基類
    Base class for type managers
    
    所有型別管理器都應該繼承此類
    All type managers should inherit from this class
    """
    
    def __init__(self, cache_size: int = 20, session=None):
        """
        初始化型別管理器
        Initialize type manager
        
        Args:
            cache_size: 快取大小 / Cache size
            session: 實驗會話實例（用於獲取 TXT 數據）/ Experiment session for accessing TXT data
        """
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # 會話引用 / Session reference
        self._session = session
        
        # 檔案資訊和數據管理 / File info and data management
        self._files: Dict[str, FileInfo] = {}
        self._data: Dict[str, ParseResult] = {}
        self._analyzers: Dict[str, Any] = {}
        
        # 快取管理 / Cache management
        self._cache_size = cache_size
        self._access_order: List[str] = []  # LRU 順序 / LRU order
        
        # 統計資訊 / Statistics
        self._load_count = 0
        self._cache_hits = 0
        self._cache_misses = 0
        
        self.logger.info(f"{self.__class__.__name__} 初始化完成")
    
    def add_file(self, key: str, info: FileInfo) -> None:
        """
        添加檔案資訊
        Add file information
        
        Args:
            key: 檔案鍵值 / File key
            info: 檔案資訊 / File information
        """
        self._files[key] = info
        self.logger.debug(f"添加檔案: {key} ({info.type})")
    
    def has_file(self, key: str) -> bool:
        """
        檢查是否有指定的檔案
        Check if file exists
        
        Args:
            key: 檔案鍵值 / File key
            
        Returns:
            bool: 是否存在 / Whether exists
        """
        return key in self._files
    
    def is_loaded(self, key: str) -> bool:
        """
        檢查檔案是否已載入
        Check if file is loaded
        
        Args:
            key: 檔案鍵值 / File key
            
        Returns:
            bool: 是否已載入 / Whether loaded
        """
        return key in self._data
    
    def load(self, key: str, force_reload: bool = False) -> ParseResult:
        """
        載入檔案
        Load file
        
        Args:
            key: 檔案鍵值 / File key
            force_reload: 是否強制重載 / Whether to force reload
            
        Returns:
            ParseResult: 解析結果 / Parse result
        """
        if key not in self._files:
            error_result = ParseResult(
                metadata={'key': key},
                data=None,
                parser_type=self.__class__.__name__
            )
            error_result.add_error(f"File key '{key}' not found")
            return error_result
        
        # 檢查快取 / Check cache
        if not force_reload and key in self._data:
            self._update_access_order(key)
            self._cache_hits += 1
            self.logger.debug(f"從快取載入: {key}")
            return self._data[key]
        
        # 載入並解析檔案 / Load and parse file
        try:
            self._cache_misses += 1
            file_info = self._files[key]
            result = self._parse_file(file_info)
            
            # 更新快取 / Update cache
            self._add_to_cache(key, result)
            
            # 更新檔案狀態 / Update file status
            file_info.loaded = True
            file_info.loaded_at = datetime.now()
            
            self._load_count += 1
            self.logger.info(f"檔案載入成功: {key}")
            return result
            
        except Exception as e:
            error_result = ParseResult(
                metadata={'key': key, 'path': self._files[key].path},
                data=None,
                parser_type=self.__class__.__name__
            )
            error_result.add_error(f"Failed to load file: {str(e)}")
            self.logger.error(f"檔案載入失敗: {key}, 錯誤: {str(e)}")
            return error_result
    
    @abstractmethod
    def _parse_file(self, info: FileInfo) -> ParseResult:
        """
        解析檔案（子類實作）
        Parse file (implemented by subclass)
        
        Args:
            info: 檔案資訊 / File information
            
        Returns:
            ParseResult: 解析結果 / Parse result
        """
        pass
    
    def get_analyzer(self, key: str):
        """
        獲取或創建分析器
        Get or create analyzer
        
        Args:
            key: 檔案鍵值 / File key
            
        Returns:
            分析器實例 / Analyzer instance
        """
        if key not in self._analyzers:
            if not self.is_loaded(key):
                # 如果檔案未載入，先載入
                load_result = self.load(key)
                if not load_result.success:
                    raise RuntimeError(f"Failed to load file {key}: {load_result.errors}")
            
            self._analyzers[key] = self._create_analyzer(key)
        
        return self._analyzers[key]
    
    @abstractmethod
    def _create_analyzer(self, key: str):
        """
        創建分析器（子類實作）
        Create analyzer (implemented by subclass)
        
        Args:
            key: 檔案鍵值 / File key
            
        Returns:
            分析器實例 / Analyzer instance
        """
        pass
    
    def unload(self, key: str) -> bool:
        """
        卸載檔案
        Unload file
        
        Args:
            key: 檔案鍵值 / File key
            
        Returns:
            bool: 是否成功卸載 / Whether successfully unloaded
        """
        if key in self._data:
            del self._data[key]
            
            if key in self._access_order:
                self._access_order.remove(key)
            
            if key in self._analyzers:
                del self._analyzers[key]
            
            # 更新檔案狀態 / Update file status
            if key in self._files:
                self._files[key].loaded = False
                self._files[key].loaded_at = None
            
            self.logger.info(f"檔案已卸載: {key}")
            return True
        
        return False
    
    def _add_to_cache(self, key: str, result: ParseResult) -> None:
        """
        添加到快取
        Add to cache
        
        Args:
            key: 檔案鍵值 / File key
            result: 解析結果 / Parse result
        """
        # 檢查快取大小限制 / Check cache size limit
        if len(self._data) >= self._cache_size and key not in self._data:
            # 移除最久未使用的項目 / Remove least recently used item
            if self._access_order:
                lru_key = self._access_order.pop(0)
                if lru_key in self._data:
                    del self._data[lru_key]
                    self.logger.debug(f"從快取移除 LRU 項目: {lru_key}")
        
        self._data[key] = result
        self._update_access_order(key)
    
    def _update_access_order(self, key: str) -> None:
        """
        更新訪問順序
        Update access order
        
        Args:
            key: 檔案鍵值 / File key
        """
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)
    
    def get_files(self) -> Dict[str, FileInfo]:
        """
        獲取所有檔案資訊
        Get all file information
        
        Returns:
            Dict: 檔案資訊字典 / File info dictionary
        """
        return self._files.copy()
    
    def get_loaded_files(self) -> List[str]:
        """
        獲取已載入的檔案列表
        Get list of loaded files
        
        Returns:
            List: 已載入檔案鍵值列表 / List of loaded file keys
        """
        return list(self._data.keys())
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        獲取快取資訊
        Get cache information
        
        Returns:
            Dict: 快取資訊 / Cache information
        """
        hit_rate = self._cache_hits / (self._cache_hits + self._cache_misses) if (self._cache_hits + self._cache_misses) > 0 else 0
        
        return {
            'cache_size': len(self._data),
            'max_cache_size': self._cache_size,
            'cached_files': list(self._data.keys()),
            'access_order': self._access_order.copy(),
            'load_count': self._load_count,
            'cache_hits': self._cache_hits,
            'cache_misses': self._cache_misses,
            'hit_rate': hit_rate
        }
    
    def clear_cache(self) -> None:
        """
        清理快取
        Clear cache
        """
        self._data.clear()
        self._analyzers.clear()
        self._access_order.clear()
        
        # 更新檔案狀態 / Update file status
        for file_info in self._files.values():
            file_info.loaded = False
            file_info.loaded_at = None
        
        self.logger.info("快取已清理")


class TxtManager(TypeManager):
    """
    TXT 檔案管理器
    TXT file manager
    """
    
    def __init__(self, cache_size: int = 20, session=None):
        super().__init__(cache_size, session)
    
    def _parse_file(self, info: FileInfo) -> ParseResult:
        """
        解析 TXT 檔案
        Parse TXT file
        """
        from .parsers.txt_parser import TxtParser
        
        parser = TxtParser(info.path)
        result = parser.parse()
        
        if not result.success:
            return result
        
        # 轉換為標準格式 / Convert to standard format
        from .data_models import ScanParameters
        
        raw_data = result.data
        exp_info = raw_data.get('experiment_info', {})
        
        # 安全地轉換參數值，處理可能的字符串格式
        def safe_int_convert(value, default=256):
            if isinstance(value, str):
                try:
                    return int(float(value.strip()))
                except (ValueError, AttributeError):
                    self.logger.warning(f"無法轉換為整數: {value}, 使用默認值 {default}")
                    return default
            return int(value) if value is not None else default
        
        def safe_float_convert(value, default=100.0):
            if isinstance(value, str):
                try:
                    return float(value.strip())
                except (ValueError, AttributeError):
                    self.logger.warning(f"無法轉換為浮點數: {value}, 使用默認值 {default}")
                    return default
            return float(value) if value is not None else default
        
        try:
            scan_params = ScanParameters(
                x_pixel=safe_int_convert(exp_info.get('xPixel', 256)),
                y_pixel=safe_int_convert(exp_info.get('yPixel', 256)),
                x_range=safe_float_convert(exp_info.get('XScanRange', 100.0)),
                y_range=safe_float_convert(exp_info.get('YScanRange', 100.0))
            )
        except Exception as e:
            self.logger.error(f"創建 ScanParameters 失敗: {e}")
            # 使用默認值創建 ScanParameters
            scan_params = ScanParameters(
                x_pixel=256,
                y_pixel=256,
                x_range=100.0,
                y_range=100.0
            )
        
        txt_data = TxtData(
            experiment_info=exp_info,
            scan_parameters=scan_params,
            int_files=raw_data.get('int_files', []),
            dat_files=raw_data.get('dat_files', []),
            signal_types=raw_data.get('signal_types', [])
        )
        
        # 更新結果數據 / Update result data
        result.data = txt_data
        result.metadata.update({
            'experiment_name': txt_data.experiment_name
        })
        
        return result
    
    def _create_analyzer(self, key: str):
        """創建 TXT 分析器"""
        from .analyzers.txt_analyzer import TxtAnalyzer
        data = self._data[key].data
        return TxtAnalyzer(data)


class TopoManager(TypeManager):
    """
    拓撲圖管理器
    Topography manager
    """
    
    def __init__(self, cache_size: int = 20, session=None):
        super().__init__(cache_size, session)
    
    def _parse_file(self, info: FileInfo) -> ParseResult:
        """
        解析 INT 檔案
        Parse INT file
        """
        from .parsers.int_parser import IntParser
        
        # 從 session 獲取 TXT 數據和掃描參數 / Get TXT data and scan parameters from session
        txt_data = None
        data_scale = 1.0
        x_pixel = 256
        y_pixel = 256
        x_range = 100.0
        y_range = 100.0
        
        if self._session:
            try:
                # 獲取 TXT 數據 / Get TXT data
                txt_files = list(self._session.txt.get_files().keys())
                if txt_files:
                    txt_result = self._session.txt.load(txt_files[0])
                    if txt_result.success:
                        txt_data = txt_result.data
                        scan_params = txt_data.scan_parameters
                        x_pixel = scan_params.x_pixel
                        y_pixel = scan_params.y_pixel
                        x_range = scan_params.x_range
                        y_range = scan_params.y_range
                        
                        # 從 TXT 數據中獲取此檔案的 scale / Get file-specific scale from TXT data
                        from pathlib import Path
                        file_stem = Path(info.path).stem
                        for int_file in txt_data.int_files:
                            if int_file.get('filename', '').replace('.int', '') == file_stem:
                                scale_str = int_file.get('scale')
                                if scale_str:
                                    try:
                                        data_scale = float(scale_str)
                                        break
                                    except (ValueError, TypeError):
                                        self.logger.warning(f"無法解析 scale: {scale_str}")
            except Exception as e:
                self.logger.warning(f"無法獲取 TXT 數據: {e}")
        
        # 使用正確的參數初始化 parser / Initialize parser with correct parameters
        parser = IntParser(info.path, scale=data_scale, x_pixel=x_pixel, y_pixel=y_pixel)
        result = parser.parse()
        
        if not result.success:
            return result
        
        # 轉換為標準格式 / Convert to standard format
        raw_data = result.data
        topo_data = TopoData(
            image=raw_data['image_data'],  # 這已經乘上了正確的 scale
            x_range=x_range,
            y_range=y_range,
            x_pixels=x_pixel,
            y_pixels=y_pixel,
            data_scale=data_scale,  # 記錄使用的 scale
            signal_type=info.signal_type or 'Topo',
            direction=info.direction
        )
        
        # 更新結果數據 / Update result data
        result.data = topo_data
        result.metadata.update({
            'signal_type': info.signal_type,
            'direction': info.direction,
            'data_scale': data_scale
        })
        
        return result
    
    def _create_analyzer(self, key: str):
        """創建拓撲圖分析器"""
        from .analyzers.int_analyzer import IntAnalyzer
        data = self._data[key].data
        return IntAnalyzer(data)


class CitsManager(TypeManager):
    """
    CITS 資料管理器
    CITS data manager
    """
    
    def __init__(self, cache_size: int = 20, session=None):
        super().__init__(cache_size, session)
    
    def _parse_file(self, info: FileInfo) -> ParseResult:
        """
        解析 DAT 檔案（CITS 模式）
        Parse DAT file (CITS mode)
        """
        from .parsers.dat_parser import DatParser
        
        parser = DatParser()
        # TODO: 需要提供正確的 dat_info 參數
        dat_info = {
            'measurement_mode': 'CITS',
            'grid_x': 256,
            'grid_y': 256
        }
        result = parser.parse(info.path, dat_info)
        
        if not result.success:
            return result
        
        # 轉換為標準格式 / Convert to standard format
        raw_data = result.data
        cits_data = CitsData(
            data_3d=raw_data['data_3d'],
            bias_values=raw_data['bias_values'],
            grid_size=raw_data['grid_size'],
            x_range=raw_data.get('x_range', 100.0),
            y_range=raw_data.get('y_range', 100.0),
            measurement_mode='CITS'
        )
        
        # 保存原始解析結果以供分析器使用 / Store raw parse result for analyzer use
        cits_data._raw_parse_result = raw_data
        
        # 更新結果數據 / Update result data
        result.data = cits_data
        result.metadata.update({
            'measurement_mode': 'CITS'
        })
        
        return result
    
    def _create_analyzer(self, key: str):
        """創建 CITS 分析器"""
        from .analyzers.cits_analyzer import CitsAnalyzer
        data = self._data[key].data
        return CitsAnalyzer(data)


class StsManager(TypeManager):
    """
    STS 資料管理器
    STS data manager
    """
    
    def __init__(self, cache_size: int = 20, session=None):
        super().__init__(cache_size, session)
    
    def _parse_file(self, info: FileInfo) -> ParseResult:
        """
        解析 DAT 檔案（STS 模式）
        Parse DAT file (STS mode)
        """
        from .parsers.dat_parser import DatParser
        
        parser = DatParser()
        # TODO: 需要提供正確的 dat_info 參數
        dat_info = {
            'measurement_mode': 'STS',
            'grid_x': 256,
            'grid_y': 256
        }
        result = parser.parse(info.path, dat_info)
        
        if not result.success:
            return result
        
        # 轉換為標準格式 / Convert to standard format
        raw_data = result.data
        sts_data = StsData(
            data_2d=raw_data['data_2d'],
            bias_values=raw_data['bias_values'],
            x_coords=raw_data['x_coords'],
            y_coords=raw_data['y_coords'],
            measurement_mode='STS'
        )
        
        # 更新結果數據 / Update result data
        result.data = sts_data
        result.metadata.update({
            'measurement_mode': 'STS'
        })
        
        return result
    
    def _create_analyzer(self, key: str):
        """創建 STS 分析器"""
        from .analyzers.dat_analyzer import DatAnalyzer
        data = self._data[key].data
        return DatAnalyzer(data)