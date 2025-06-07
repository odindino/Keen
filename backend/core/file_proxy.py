"""
檔案代理
File Proxy

提供直覺的檔案存取介面，支援 IDE 友好的屬性訪問
Provides intuitive file access interface with IDE-friendly attribute access
"""

from typing import Any, Dict, Optional, TYPE_CHECKING
import logging
import numpy as np

from .data_models import (
    ParseResult, TopoData, CitsData, StsData, TxtData, 
    ProfileLine, SPMData
)

if TYPE_CHECKING:
    from .experiment_session import ExperimentSession


class FileProxy:
    """
    檔案代理類別
    File proxy class
    
    提供直覺的檔案存取介面：session['file_key'].data.attribute
    Provides intuitive file access: session['file_key'].data.attribute
    """
    
    def __init__(self, session: 'ExperimentSession', file_key: str):
        """
        初始化檔案代理
        Initialize file proxy
        
        Args:
            session: 實驗會話實例 / Experiment session instance
            file_key: 檔案鍵值 / File key
        """
        self._session = session
        self._file_key = file_key
        self._logger = logging.getLogger(f"{__name__}.FileProxy")
        
        # 快取的屬性 / Cached properties
        self._file_type: Optional[str] = None
        self._manager = None
        
        # 驗證檔案是否存在 / Validate file exists
        if not self._session.has_file(file_key):
            raise ValueError(f"File key '{file_key}' not found in session")
    
    @property
    def data(self) -> SPMData:
        """
        獲取檔案數據
        Get file data
        
        Returns:
            SPMData: 檔案數據（TopoData, CitsData, StsData, 或 TxtData）
        """
        result = self._get_parse_result()
        if not result.success:
            raise RuntimeError(f"Failed to load file '{self._file_key}': {result.errors}")
        return result.data
    
    @property
    def metadata(self) -> Dict[str, Any]:
        """
        獲取檔案元資料
        Get file metadata
        
        Returns:
            Dict: 元資料字典 / Metadata dictionary
        """
        result = self._get_parse_result()
        return result.metadata
    
    @property
    def analyzer(self) -> Any:
        """
        獲取分析器實例
        Get analyzer instance
        
        Returns:
            分析器實例 / Analyzer instance
        """
        manager = self._get_manager()
        return manager.get_analyzer(self._file_key)
    
    @property
    def file_info(self):
        """
        獲取檔案資訊
        Get file information
        
        Returns:
            FileInfo: 檔案資訊 / File information
        """
        manager = self._get_manager()
        files = manager.get_files()
        return files.get(self._file_key)
    
    @property
    def is_loaded(self) -> bool:
        """
        檢查檔案是否已載入
        Check if file is loaded
        
        Returns:
            bool: 是否已載入 / Whether loaded
        """
        manager = self._get_manager()
        return manager.is_loaded(self._file_key)
    
    @property
    def file_type(self) -> str:
        """
        獲取檔案類型
        Get file type
        
        Returns:
            str: 檔案類型 / File type
        """
        if self._file_type is None:
            self._file_type = self._determine_file_type()
        return self._file_type
    
    # ========== 拓撲圖專用屬性 / Topography-specific properties ==========
    
    @property
    def image(self) -> Optional[np.ndarray]:
        """
        快捷存取圖像資料（適用於拓撲圖）
        Shortcut for image data (for topography files)
        
        Returns:
            Optional[np.ndarray]: 圖像數據 / Image data
        """
        if isinstance(self.data, TopoData):
            return self.data.current_image
        return None
    
    @property
    def flattened(self) -> Optional[np.ndarray]:
        """
        快捷存取平坦化圖像
        Shortcut for flattened image
        
        Returns:
            Optional[np.ndarray]: 平坦化圖像 / Flattened image
        """
        if isinstance(self.data, TopoData):
            return self.data.flattened
        return None
    
    @property
    def x_range(self) -> Optional[float]:
        """
        快捷存取 X 方向範圍
        Shortcut for X range
        
        Returns:
            Optional[float]: X 方向範圍 nm / X range in nm
        """
        data = self.data
        if isinstance(data, (TopoData, CitsData)):
            return data.x_range
        return None
    
    @property
    def y_range(self) -> Optional[float]:
        """
        快捷存取 Y 方向範圍
        Shortcut for Y range
        
        Returns:
            Optional[float]: Y 方向範圍 nm / Y range in nm
        """
        data = self.data
        if isinstance(data, (TopoData, CitsData)):
            return data.y_range
        return None
    
    @property
    def shape(self) -> Optional[tuple]:
        """
        快捷存取數據形狀
        Shortcut for data shape
        
        Returns:
            Optional[tuple]: 數據形狀 / Data shape
        """
        data = self.data
        if hasattr(data, 'shape'):
            return data.shape
        return None
    
    # ========== CITS 專用屬性 / CITS-specific properties ==========
    
    @property
    def bias_values(self) -> Optional[np.ndarray]:
        """
        快捷存取偏壓值（適用於 CITS/STS）
        Shortcut for bias values (for CITS/STS files)
        
        Returns:
            Optional[np.ndarray]: 偏壓值 / Bias values
        """
        data = self.data
        if isinstance(data, (CitsData, StsData)):
            return data.bias_values
        return None
    
    @property
    def data_3d(self) -> Optional[np.ndarray]:
        """
        快捷存取 3D 數據（適用於 CITS）
        Shortcut for 3D data (for CITS files)
        
        Returns:
            Optional[np.ndarray]: 3D 數據 / 3D data
        """
        if isinstance(self.data, CitsData):
            return self.data.data_3d
        return None
    
    def get_bias_slice(self, bias_index: int) -> Optional[np.ndarray]:
        """
        獲取特定偏壓的 2D 切片（適用於 CITS）
        Get 2D slice at specific bias (for CITS files)
        
        Args:
            bias_index: 偏壓索引 / Bias index
            
        Returns:
            Optional[np.ndarray]: 2D 切片 / 2D slice
        """
        if isinstance(self.data, CitsData):
            return self.data.get_bias_slice(bias_index)
        return None
    
    # ========== 分析方法 / Analysis methods ==========
    
    def flatten_plane(self, method: str = 'linear', **kwargs) -> Optional[np.ndarray]:
        """
        執行平面平坦化（適用於拓撲圖）
        Perform plane flattening (for topography files)
        
        Args:
            method: 平坦化方法 / Flattening method
            **kwargs: 額外參數 / Additional parameters
            
        Returns:
            Optional[np.ndarray]: 平坦化結果 / Flattened result
        """
        if isinstance(self.data, TopoData):
            analyzer = self.analyzer
            if hasattr(analyzer, 'flatten_plane'):
                result = analyzer.flatten_plane(method=method, **kwargs)
                # 結果應該自動保存到 data.flattened
                return result
        return None
    
    def extract_profile(self, x1: float, y1: float, x2: float, y2: float, 
                       name: str = "profile") -> Optional[ProfileLine]:
        """
        提取剖面線（適用於拓撲圖）
        Extract profile line (for topography files)
        
        Args:
            x1, y1: 起點座標 / Start coordinates
            x2, y2: 終點座標 / End coordinates  
            name: 剖面名稱 / Profile name
            
        Returns:
            Optional[ProfileLine]: 剖面線數據 / Profile line data
        """
        if isinstance(self.data, TopoData):
            analyzer = self.analyzer
            if hasattr(analyzer, 'extract_profile'):
                result = analyzer.extract_profile(x1, y1, x2, y2, name)
                return result
        return None
    
    def extract_iv_curve(self, x: int, y: int) -> Optional[Dict[str, Any]]:
        """
        提取 I-V 曲線（適用於 CITS）
        Extract I-V curve (for CITS files)
        
        Args:
            x, y: 像素座標 / Pixel coordinates
            
        Returns:
            Optional[Dict]: I-V 曲線數據 / I-V curve data
        """
        if isinstance(self.data, CitsData):
            analyzer = self.analyzer
            if hasattr(analyzer, 'extract_iv_curve'):
                return analyzer.extract_iv_curve(x, y)
        return None
    
    # ========== 內部方法 / Internal methods ==========
    
    def _get_parse_result(self) -> ParseResult:
        """
        獲取解析結果
        Get parse result
        
        Returns:
            ParseResult: 解析結果 / Parse result
        """
        manager = self._get_manager()
        return manager.load(self._file_key)
    
    def _get_manager(self):
        """
        獲取對應的管理器
        Get corresponding manager
        
        Returns:
            TypeManager: 型別管理器 / Type manager
        """
        if self._manager is None:
            file_type = self.file_type
            
            if file_type == 'txt':
                self._manager = self._session.txt
            elif file_type in ['topo', 'int']:
                self._manager = self._session.topo
            elif file_type == 'cits':
                self._manager = self._session.cits
            elif file_type == 'sts':
                self._manager = self._session.sts
            else:
                raise ValueError(f"Unknown file type: {file_type}")
        
        return self._manager
    
    def _determine_file_type(self) -> str:
        """
        判斷檔案類型
        Determine file type
        
        Returns:
            str: 檔案類型 / File type
        """
        # 檢查所有管理器中是否有這個檔案
        if self._session.txt.has_file(self._file_key):
            return 'txt'
        elif self._session.topo.has_file(self._file_key):
            return 'topo'
        elif self._session.cits.has_file(self._file_key):
            return 'cits'
        elif self._session.sts.has_file(self._file_key):
            return 'sts'
        else:
            # 根據檔案名稱推斷
            if 'matrix' in self._file_key.lower():
                return 'cits'
            elif 'topo' in self._file_key.lower():
                return 'topo'
            else:
                return 'unknown'
    
    def reload(self, force: bool = True) -> 'FileProxy':
        """
        重新載入檔案
        Reload file
        
        Args:
            force: 是否強制重載 / Whether to force reload
            
        Returns:
            FileProxy: 自身引用 / Self reference
        """
        manager = self._get_manager()
        manager.load(self._file_key, force_reload=force)
        return self
    
    def unload(self) -> bool:
        """
        卸載檔案
        Unload file
        
        Returns:
            bool: 是否成功卸載 / Whether successfully unloaded
        """
        manager = self._get_manager()
        return manager.unload(self._file_key)
    
    def get_analysis_history(self) -> list:
        """
        獲取分析歷史
        Get analysis history
        
        Returns:
            list: 分析歷史 / Analysis history
        """
        try:
            analyzer = self.analyzer
            if hasattr(analyzer, 'get_history'):
                return analyzer.get_history()
        except:
            pass
        return []
    
    def __repr__(self) -> str:
        """字串表示 / String representation"""
        try:
            status = "loaded" if self.is_loaded else "not loaded"
            return f"<FileProxy: {self._file_key} ({self.file_type}, {status})>"
        except:
            return f"<FileProxy: {self._file_key} (status unknown)>"
    
    def __str__(self) -> str:
        """友好的字串表示 / Friendly string representation"""
        try:
            info = self.file_info
            if info:
                return f"FileProxy({self._file_key}): {info.signal_type or 'Unknown'} {info.direction or ''} - {info.human_readable_size}"
            else:
                return f"FileProxy({self._file_key}): File info not available"
        except:
            return f"FileProxy({self._file_key}): Error getting info"