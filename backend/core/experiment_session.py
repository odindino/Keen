"""
實驗會話
Experiment Session

整合所有型別管理器的主要類別，提供統一的實驗資料管理介面
Main class integrating all type managers, providing unified experiment data management interface
"""

from typing import Dict, List, Optional, Any, Union
import logging
from pathlib import Path
from datetime import datetime

from .data_models import FileInfo, ParseResult, TxtData, SUPPORTED_FILE_TYPES
from .type_managers import TxtManager, TopoManager, CitsManager, StsManager
from .file_proxy import FileProxy


class ExperimentSession:
    """
    實驗會話類別
    Experiment session class
    
    整合所有資料管理功能的主要入口點
    Main entry point integrating all data management functionality
    
    使用方式 / Usage:
        session = ExperimentSession('experiment.txt')
        topo = session['topofwd']
        height_data = topo.data.image
        analyzer = topo.analyzer
    """
    
    def __init__(self, txt_file_path: str, cache_size: int = 20):
        """
        初始化實驗會話
        Initialize experiment session
        
        Args:
            txt_file_path: TXT 檔案路徑 / TXT file path
            cache_size: 快取大小 / Cache size
        """
        self.logger = logging.getLogger(__name__)
        
        # 初始化型別管理器 / Initialize type managers
        self.txt = TxtManager(cache_size=cache_size, session=self)
        self.topo = TopoManager(cache_size=cache_size, session=self)
        self.cits = CitsManager(cache_size=cache_size, session=self)
        self.sts = StsManager(cache_size=cache_size, session=self)
        
        # 實驗基本資訊 / Basic experiment information
        self.txt_file_path = Path(txt_file_path)
        self.experiment_name: Optional[str] = None
        self.creation_time = datetime.now()
        
        # 檔案代理快取 / File proxy cache
        self._proxy_cache: Dict[str, FileProxy] = {}
        
        # 載入實驗 / Load experiment
        self._load_experiment()
        
        self.logger.info(f"實驗會話初始化完成: {self.experiment_name}")
    
    def _load_experiment(self) -> None:
        """
        載入實驗資料
        Load experiment data
        """
        if not self.txt_file_path.exists():
            raise FileNotFoundError(f"TXT file not found: {self.txt_file_path}")
        
        # 載入並解析 TXT 檔案 / Load and parse TXT file
        txt_key = self.txt_file_path.stem
        txt_file_info = FileInfo(
            path=str(self.txt_file_path),
            type='txt',
            size=self.txt_file_path.stat().st_size
        )
        
        self.txt.add_file(txt_key, txt_file_info)
        txt_result = self.txt.load(txt_key)
        
        if not txt_result.success:
            raise RuntimeError(f"Failed to parse TXT file: {txt_result.errors}")
        
        txt_data: TxtData = txt_result.data
        self.experiment_name = txt_data.experiment_name or self.txt_file_path.stem
        
        # 掃描並註冊關聯檔案 / Scan and register associated files
        self._register_associated_files(txt_data)
        
        self.logger.info(f"實驗載入完成: {self.experiment_name}")
    
    def _register_associated_files(self, txt_data: TxtData) -> None:
        """
        註冊關聯檔案
        Register associated files
        
        Args:
            txt_data: TXT 檔案數據 / TXT file data
        """
        base_dir = self.txt_file_path.parent
        
        # 註冊 INT 檔案 / Register INT files
        for int_file_info in txt_data.int_files:
            file_path = base_dir / int_file_info['filename']
            if file_path.exists():
                file_key = file_path.stem
                
                # 提取訊號類型和方向 / Extract signal type and direction
                signal_type, direction = self._extract_signal_type_and_direction(file_key)
                
                file_info = FileInfo(
                    path=str(file_path),
                    type='int',
                    size=file_path.stat().st_size,
                    signal_type=signal_type,
                    direction=direction
                )
                
                # 根據訊號類型決定管理器 / Determine manager based on signal type
                if signal_type and 'topo' in signal_type.lower():
                    self.topo.add_file(file_key, file_info)
                else:
                    # 預設加入拓撲管理器 / Default to topography manager
                    self.topo.add_file(file_key, file_info)
                
                self.logger.debug(f"註冊 INT 檔案: {file_key} ({signal_type} {direction})")
        
        # 註冊 DAT 檔案 / Register DAT files
        for dat_file_info in txt_data.dat_files:
            file_path = base_dir / dat_file_info['filename']
            if file_path.exists():
                file_key = file_path.stem
                
                # 提取訊號類型 / Extract signal type
                signal_type, _ = self._extract_signal_type_and_direction(file_key)
                
                file_info = FileInfo(
                    path=str(file_path),
                    type='dat',
                    size=file_path.stat().st_size,
                    signal_type=signal_type
                )
                
                # 根據檔案名稱決定是 CITS 還是 STS / Determine CITS or STS based on filename
                if '_matrix' in file_key.lower() or 'cits' in file_key.lower():
                    self.cits.add_file(file_key, file_info)
                    self.logger.debug(f"註冊 CITS 檔案: {file_key}")
                else:
                    self.sts.add_file(file_key, file_info)
                    self.logger.debug(f"註冊 STS 檔案: {file_key}")
    
    def _extract_signal_type_and_direction(self, filename: str) -> tuple:
        """
        從檔案名稱提取訊號類型和方向
        Extract signal type and direction from filename
        
        Args:
            filename: 檔案名稱 / Filename
            
        Returns:
            tuple: (signal_type, direction)
        """
        # 訊號類型模式 / Signal type patterns
        signal_patterns = [
            "Topo", "Lia1X", "Lia1Y", "Lia1R", "Lia2X", "Lia2Y", "Lia2R",
            "Lia3X", "Lia3Y", "Lia3R", "It_to_PC", "InA", "QPlus",
            "Bias", "Frequency", "Drive", "Phase", "df"
        ]
        
        # 檢查是否有 Matrix 後綴 / Check for Matrix suffix
        if "_Matrix" in filename:
            signal_type = filename.split('_Matrix')[0].split('_')[-1]
            # 移除前綴序號 / Remove prefix numbers
            for i, char in enumerate(signal_type):
                if char.isalpha():
                    signal_type = signal_type[i:]
                    break
            return signal_type, None
        
        # 尋找訊號類型 / Find signal type
        signal_type = None
        direction = None
        
        for pattern in signal_patterns:
            if pattern in filename:
                signal_type = pattern
                break
        
        # 如果找不到匹配的訊號類型 / If no matching signal type found
        if signal_type is None:
            name_parts = filename.split('_')[-1]
            if "Fwd" in name_parts:
                signal_type = name_parts.replace("Fwd", "")
                direction = "Fwd"
            elif "Bwd" in name_parts:
                signal_type = name_parts.replace("Bwd", "")
                direction = "Bwd"
            else:
                signal_type = name_parts
        else:
            # 檢查方向 / Check direction
            if "Fwd" in filename:
                direction = "Fwd"
            elif "Bwd" in filename:
                direction = "Bwd"
        
        return signal_type or "unknown", direction
    
    def get_file(self, file_key: str) -> FileProxy:
        """
        獲取檔案代理
        Get file proxy
        
        Args:
            file_key: 檔案鍵值 / File key
            
        Returns:
            FileProxy: 檔案代理實例 / File proxy instance
        """
        if file_key not in self._proxy_cache:
            self._proxy_cache[file_key] = FileProxy(self, file_key)
        return self._proxy_cache[file_key]
    
    def __getitem__(self, key: str) -> FileProxy:
        """
        支援索引存取
        Support index access
        
        Args:
            key: 檔案鍵值 / File key
            
        Returns:
            FileProxy: 檔案代理實例 / File proxy instance
        """
        return self.get_file(key)
    
    def has_file(self, file_key: str) -> bool:
        """
        檢查是否有指定的檔案
        Check if file exists
        
        Args:
            file_key: 檔案鍵值 / File key
            
        Returns:
            bool: 是否存在 / Whether exists
        """
        return (self.txt.has_file(file_key) or 
                self.topo.has_file(file_key) or 
                self.cits.has_file(file_key) or 
                self.sts.has_file(file_key))
    
    @property
    def available_files(self) -> Dict[str, List[str]]:
        """
        列出所有可用檔案
        List all available files
        
        Returns:
            Dict: 按類型分組的檔案列表 / Files grouped by type
        """
        return {
            'txt': list(self.txt.get_files().keys()),
            'topo': list(self.topo.get_files().keys()),
            'cits': list(self.cits.get_files().keys()),
            'sts': list(self.sts.get_files().keys())
        }
    
    @property
    def loaded_files(self) -> Dict[str, List[str]]:
        """
        列出所有已載入檔案
        List all loaded files
        
        Returns:
            Dict: 按類型分組的已載入檔案列表 / Loaded files grouped by type
        """
        return {
            'txt': self.txt.get_loaded_files(),
            'topo': self.topo.get_loaded_files(),
            'cits': self.cits.get_loaded_files(),
            'sts': self.sts.get_loaded_files()
        }
    
    @property
    def scan_parameters(self):
        """
        獲取掃描參數
        Get scan parameters
        
        Returns:
            ScanParameters: 掃描參數 / Scan parameters
        """
        txt_files = list(self.txt.get_files().keys())
        if txt_files:
            txt_key = txt_files[0]
            txt_result = self.txt.load(txt_key)
            if txt_result.success:
                return txt_result.data.scan_parameters
        return None
    
    @property
    def experiment_info(self) -> Dict[str, Any]:
        """
        獲取實驗資訊
        Get experiment information
        
        Returns:
            Dict: 實驗資訊 / Experiment information
        """
        txt_files = list(self.txt.get_files().keys())
        if txt_files:
            txt_key = txt_files[0]
            txt_result = self.txt.load(txt_key)
            if txt_result.success:
                return txt_result.data.experiment_info
        return {}
    
    def load_multiple_files(self, file_keys: List[str]) -> Dict[str, ParseResult]:
        """
        批次載入多個檔案
        Load multiple files in batch
        
        Args:
            file_keys: 檔案鍵值列表 / List of file keys
            
        Returns:
            Dict: 載入結果字典 / Loading results dictionary
        """
        results = {}
        
        for file_key in file_keys:
            try:
                proxy = self.get_file(file_key)
                # 觸發載入 / Trigger loading
                _ = proxy.data
                results[file_key] = ParseResult(
                    metadata={'success': True},
                    data=None,
                    parser_type='batch_load'
                )
            except Exception as e:
                result = ParseResult(
                    metadata={'success': False},
                    data=None,
                    parser_type='batch_load'
                )
                result.add_error(str(e))
                results[file_key] = result
        
        return results
    
    def unload_all_files(self, exclude_txt: bool = True) -> int:
        """
        卸載所有檔案
        Unload all files
        
        Args:
            exclude_txt: 是否排除 TXT 檔案 / Whether to exclude TXT files
            
        Returns:
            int: 卸載的檔案數量 / Number of unloaded files
        """
        unloaded_count = 0
        
        # 清理代理快取 / Clear proxy cache
        self._proxy_cache.clear()
        
        # 卸載各類型檔案 / Unload files by type
        if not exclude_txt:
            for key in self.txt.get_loaded_files():
                if self.txt.unload(key):
                    unloaded_count += 1
        
        for key in self.topo.get_loaded_files():
            if self.topo.unload(key):
                unloaded_count += 1
        
        for key in self.cits.get_loaded_files():
            if self.cits.unload(key):
                unloaded_count += 1
        
        for key in self.sts.get_loaded_files():
            if self.sts.unload(key):
                unloaded_count += 1
        
        self.logger.info(f"已卸載 {unloaded_count} 個檔案")
        return unloaded_count
    
    def get_memory_info(self) -> Dict[str, Any]:
        """
        獲取記憶體使用資訊
        Get memory usage information
        
        Returns:
            Dict: 記憶體使用資訊 / Memory usage information
        """
        return {
            'txt_cache': self.txt.get_cache_info(),
            'topo_cache': self.topo.get_cache_info(),
            'cits_cache': self.cits.get_cache_info(),
            'sts_cache': self.sts.get_cache_info(),
            'proxy_cache_size': len(self._proxy_cache),
            'total_files': sum(len(files) for files in self.available_files.values()),
            'total_loaded': sum(len(files) for files in self.loaded_files.values())
        }
    
    def get_session_summary(self) -> Dict[str, Any]:
        """
        獲取會話摘要
        Get session summary
        
        Returns:
            Dict: 會話摘要 / Session summary
        """
        available = self.available_files
        loaded = self.loaded_files
        
        return {
            'experiment_name': self.experiment_name,
            'txt_file': str(self.txt_file_path),
            'creation_time': self.creation_time.isoformat(),
            'files_summary': {
                'available': {k: len(v) for k, v in available.items()},
                'loaded': {k: len(v) for k, v in loaded.items()},
                'total_available': sum(len(v) for v in available.values()),
                'total_loaded': sum(len(v) for v in loaded.values())
            },
            'scan_parameters': self._get_scan_parameters_dict() if self.scan_parameters else None,
            'memory_info': self.get_memory_info()
        }
    
    def _get_scan_parameters_dict(self) -> Dict[str, Any]:
        """
        將 ScanParameters 轉換為字典，包含計算的屬性
        Convert ScanParameters to dictionary, including computed properties
        
        Returns:
            Dict: 掃描參數字典 / Scan parameters dictionary
        """
        if not self.scan_parameters:
            return {}
        
        params = self.scan_parameters
        return {
            'x_pixel': params.x_pixel,
            'y_pixel': params.y_pixel,
            'x_range': params.x_range,
            'y_range': params.y_range,
            'pixel_scale_x': params.pixel_scale_x,
            'pixel_scale_y': params.pixel_scale_y,
            'aspect_ratio': params.aspect_ratio,
            'total_pixels': params.total_pixels
        }
    
    def clear_all_caches(self) -> None:
        """
        清理所有快取
        Clear all caches
        """
        self.txt.clear_cache()
        self.topo.clear_cache()
        self.cits.clear_cache()
        self.sts.clear_cache()
        self._proxy_cache.clear()
        self.logger.info("所有快取已清理")
    
    def __repr__(self) -> str:
        """字串表示 / String representation"""
        available = self.available_files
        total_files = sum(len(v) for v in available.values())
        return f"<ExperimentSession: {self.experiment_name} ({total_files} files)>"
    
    def __str__(self) -> str:
        """友好的字串表示 / Friendly string representation"""
        summary = self.get_session_summary()
        files_info = summary['files_summary']
        return (f"ExperimentSession({self.experiment_name})\n"
                f"  Files: {files_info['total_available']} available, "
                f"{files_info['total_loaded']} loaded\n"
                f"  Types: TXT({files_info['available']['txt']}), "
                f"TOPO({files_info['available']['topo']}), "
                f"CITS({files_info['available']['cits']}), "
                f"STS({files_info['available']['sts']})")
    
    # ========== 便利方法 / Convenience methods ==========
    
    def get_topo_files(self) -> List[str]:
        """獲取所有拓撲檔案鍵值 / Get all topography file keys"""
        return list(self.topo.get_files().keys())
    
    def get_cits_files(self) -> List[str]:
        """獲取所有 CITS 檔案鍵值 / Get all CITS file keys"""
        return list(self.cits.get_files().keys())
    
    def get_sts_files(self) -> List[str]:
        """獲取所有 STS 檔案鍵值 / Get all STS file keys"""
        return list(self.sts.get_files().keys())
    
    def find_files_by_signal_type(self, signal_type: str) -> List[str]:
        """
        根據訊號類型尋找檔案
        Find files by signal type
        
        Args:
            signal_type: 訊號類型 / Signal type
            
        Returns:
            List: 匹配的檔案鍵值列表 / List of matching file keys
        """
        matching_files = []
        
        # 檢查所有管理器的檔案 / Check files in all managers
        for manager in [self.topo, self.cits, self.sts]:
            for key, file_info in manager.get_files().items():
                if file_info.signal_type == signal_type:
                    matching_files.append(key)
        
        return matching_files
    
    def find_files_by_direction(self, direction: str) -> List[str]:
        """
        根據掃描方向尋找檔案
        Find files by scan direction
        
        Args:
            direction: 掃描方向 / Scan direction (Fwd/Bwd)
            
        Returns:
            List: 匹配的檔案鍵值列表 / List of matching file keys
        """
        matching_files = []
        
        # 主要檢查拓撲檔案 / Mainly check topography files
        for key, file_info in self.topo.get_files().items():
            if file_info.direction == direction:
                matching_files.append(key)
        
        return matching_files