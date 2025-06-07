"""
資料模型定義
Data Models Definition

定義 KEEN 系統中所有標準化的資料結構，提供 IDE 友好的型別提示
Defines all standardized data structures in KEEN system with IDE-friendly type hints
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
import numpy as np


@dataclass
class ParseResult:
    """
    標準化的解析結果
    Standardized parse result
    
    所有 parser 都應該返回這個格式的結果
    All parsers should return results in this format
    """
    metadata: Dict[str, Any]      # 元資料 / Metadata
    data: Any                     # 主要資料 / Main data
    derived: Dict[str, Any] = field(default_factory=dict)  # 衍生資料 / Derived data
    errors: List[str] = field(default_factory=list)        # 錯誤訊息 / Error messages
    warnings: List[str] = field(default_factory=list)      # 警告訊息 / Warning messages
    timestamp: datetime = field(default_factory=datetime.now)
    parser_type: str = "unknown"  # 解析器類型 / Parser type
    
    @property
    def success(self) -> bool:
        """是否成功解析 / Whether parsing was successful"""
        return len(self.errors) == 0
    
    def add_error(self, message: str) -> None:
        """添加錯誤訊息 / Add error message"""
        self.errors.append(message)
    
    def add_warning(self, message: str) -> None:
        """添加警告訊息 / Add warning message"""
        self.warnings.append(message)


@dataclass
class FileInfo:
    """
    檔案資訊
    File information
    """
    path: str                           # 檔案路徑 / File path
    type: str                          # 檔案類型 / File type (txt/int/dat)
    size: int                          # 檔案大小 / File size in bytes
    signal_type: Optional[str] = None  # 訊號類型 / Signal type (Topo, Lia1R, etc.)
    direction: Optional[str] = None    # 掃描方向 / Scan direction (Fwd/Bwd)
    loaded: bool = False               # 是否已載入 / Whether loaded
    loaded_at: Optional[datetime] = None  # 載入時間 / Load timestamp
    
    @property
    def filename(self) -> str:
        """獲取檔案名稱 / Get filename"""
        from pathlib import Path
        return Path(self.path).name
    
    @property
    def human_readable_size(self) -> str:
        """人類可讀的檔案大小 / Human readable file size"""
        if self.size < 1024:
            return f"{self.size} B"
        elif self.size < 1024 * 1024:
            return f"{self.size / 1024:.1f} KB"
        elif self.size < 1024 * 1024 * 1024:
            return f"{self.size / (1024 * 1024):.1f} MB"
        else:
            return f"{self.size / (1024 * 1024 * 1024):.1f} GB"


@dataclass
class ScanParameters:
    """
    掃描參數
    Scan parameters
    """
    x_pixel: int                    # X 方向像素數 / X pixels
    y_pixel: int                    # Y 方向像素數 / Y pixels  
    x_range: float                  # X 方向掃描範圍 nm / X scan range in nm
    y_range: float                  # Y 方向掃描範圍 nm / Y scan range in nm
    
    @property
    def pixel_scale_x(self) -> float:
        """X 方向像素尺度 nm/pixel / X pixel scale in nm/pixel"""
        return self.x_range / self.x_pixel if self.x_pixel != 0 else 1.0
    
    @property
    def pixel_scale_y(self) -> float:
        """Y 方向像素尺度 nm/pixel / Y pixel scale in nm/pixel"""
        return self.y_range / self.y_pixel if self.y_pixel != 0 else 1.0
    
    @property
    def aspect_ratio(self) -> float:
        """長寬比 / Aspect ratio"""
        return self.x_range / self.y_range if self.y_range != 0 else 1.0
    
    @property
    def total_pixels(self) -> int:
        """總像素數 / Total pixels"""
        return self.x_pixel * self.y_pixel


@dataclass 
class TopoData:
    """
    拓撲圖資料
    Topography data
    """
    image: np.ndarray                    # 原始圖像數據（已乘上 scale）/ Raw image data (scaled)
    x_range: float                       # X 方向範圍 nm / X range in nm
    y_range: float                       # Y 方向範圍 nm / Y range in nm
    x_pixels: int                        # X 方向像素數 / X pixels
    y_pixels: int                        # Y 方向像素數 / Y pixels
    data_scale: float                    # 從 TXT 檔案獲取的數值 scale / Data scale from TXT file
    signal_type: str = "Topo"           # 訊號類型 / Signal type
    direction: Optional[str] = None      # 掃描方向 / Scan direction
    
    # 處理後的資料 / Processed data
    flattened: Optional[np.ndarray] = None        # 平坦化後的圖像 / Flattened image
    profile_lines: Dict[str, Any] = field(default_factory=dict)  # 剖面線 / Profile lines
    statistics: Dict[str, float] = field(default_factory=dict)   # 統計資料 / Statistics
    
    @property
    def shape(self) -> tuple:
        """圖像形狀 / Image shape"""
        return self.image.shape
    
    @property
    def pixel_scale_x(self) -> float:
        """X 方向像素尺度 nm/pixel / X pixel scale in nm/pixel"""
        return self.x_range / self.x_pixels if self.x_pixels != 0 else 1.0
    
    @property
    def pixel_scale_y(self) -> float:
        """Y 方向像素尺度 nm/pixel / Y pixel scale in nm/pixel"""
        return self.y_range / self.y_pixels if self.y_pixels != 0 else 1.0
    
    @property
    def current_image(self) -> np.ndarray:
        """當前顯示的圖像（平坦化優先）/ Current display image (flattened if available)"""
        return self.flattened if self.flattened is not None else self.image


@dataclass
class CitsData:
    """
    CITS (Current Imaging Tunneling Spectroscopy) 資料
    CITS data
    """
    data_3d: np.ndarray                      # 3D 數據 (n_bias, y, x) / 3D data
    bias_values: np.ndarray                  # 偏壓值 / Bias values
    grid_size: List[int]                     # 網格大小 [x, y] / Grid size
    x_range: float                           # X 方向範圍 nm / X range in nm  
    y_range: float                           # Y 方向範圍 nm / Y range in nm
    measurement_mode: str = "CITS"           # 量測模式 / Measurement mode
    
    # 分析結果 / Analysis results
    iv_curves: Dict[str, Any] = field(default_factory=dict)      # I-V 曲線 / I-V curves
    conductance_maps: Dict[str, np.ndarray] = field(default_factory=dict)  # 電導圖 / Conductance maps
    gap_maps: Dict[str, np.ndarray] = field(default_factory=dict)  # 能隙圖 / Gap maps
    
    @property
    def shape(self) -> tuple:
        """數據形狀 / Data shape"""
        return self.data_3d.shape
    
    @property
    def n_bias_points(self) -> int:
        """偏壓點數 / Number of bias points"""
        return len(self.bias_values)
    
    @property
    def bias_range(self) -> tuple:
        """偏壓範圍 / Bias range"""
        return (self.bias_values.min(), self.bias_values.max())
    
    def get_bias_slice(self, bias_index: int) -> np.ndarray:
        """獲取特定偏壓的2D切片 / Get 2D slice at specific bias"""
        if 0 <= bias_index < self.n_bias_points:
            return self.data_3d[bias_index, :, :]
        else:
            raise IndexError(f"Bias index {bias_index} out of range [0, {self.n_bias_points-1}]")


@dataclass
class StsData:
    """
    STS (Scanning Tunneling Spectroscopy) 資料
    STS data
    """
    data_2d: np.ndarray                      # 2D 數據 (n_bias, n_points) / 2D data
    bias_values: np.ndarray                  # 偏壓值 / Bias values
    x_coords: np.ndarray                     # X 座標 / X coordinates
    y_coords: np.ndarray                     # Y 座標 / Y coordinates
    measurement_mode: str = "STS"            # 量測模式 / Measurement mode
    
    # 分析結果 / Analysis results
    gap_values: Dict[str, float] = field(default_factory=dict)   # 能隙值 / Gap values
    peak_positions: Dict[str, List[float]] = field(default_factory=dict)  # 峰值位置 / Peak positions
    
    @property
    def shape(self) -> tuple:
        """數據形狀 / Data shape"""
        return self.data_2d.shape
    
    @property
    def n_points(self) -> int:
        """量測點數 / Number of measurement points"""
        return self.data_2d.shape[1]
    
    @property
    def n_bias_points(self) -> int:
        """偏壓點數 / Number of bias points"""
        return len(self.bias_values)


@dataclass
class TxtData:
    """
    TXT 檔案資料
    TXT file data
    """
    experiment_info: Dict[str, Any]          # 實驗資訊 / Experiment information
    scan_parameters: ScanParameters          # 掃描參數 / Scan parameters
    int_files: List[Dict[str, Any]]         # INT 檔案列表 / INT files list
    dat_files: List[Dict[str, Any]]         # DAT 檔案列表 / DAT files list
    signal_types: List[str]                  # 訊號類型列表 / Signal types list
    
    @property
    def experiment_name(self) -> str:
        """實驗名稱 / Experiment name"""
        return self.experiment_info.get('experiment_name', 'Unknown')
    
    @property
    def total_files(self) -> int:
        """總檔案數 / Total number of files"""
        return len(self.int_files) + len(self.dat_files)


@dataclass
class AnalysisState:
    """
    分析狀態
    Analysis state
    
    用於追蹤分析器的狀態和歷史
    Used to track analyzer state and history
    """
    analyzer_type: str                       # 分析器類型 / Analyzer type
    initialized: bool = False                # 是否已初始化 / Whether initialized
    last_analysis: Optional[Dict[str, Any]] = None  # 最後分析結果 / Last analysis result
    analysis_count: int = 0                  # 分析次數 / Analysis count
    errors: List[Dict[str, Any]] = field(default_factory=list)     # 錯誤列表 / Error list
    warnings: List[Dict[str, Any]] = field(default_factory=list)   # 警告列表 / Warning list
    analysis_history: List[Dict[str, Any]] = field(default_factory=list)  # 分析歷史 / Analysis history
    
    def add_error(self, message: str) -> None:
        """添加錯誤 / Add error"""
        self.errors.append({
            'timestamp': datetime.now(),
            'message': message,
            'analyzer': self.analyzer_type
        })
    
    def add_warning(self, message: str) -> None:
        """添加警告 / Add warning"""
        self.warnings.append({
            'timestamp': datetime.now(),
            'message': message,
            'analyzer': self.analyzer_type
        })
    
    def record_analysis(self, result: Dict[str, Any], analysis_type: str = "unknown") -> None:
        """記錄分析結果 / Record analysis result"""
        record = {
            'timestamp': datetime.now(),
            'analysis_type': analysis_type,
            'success': result.get('success', True),
            'analyzer': self.analyzer_type
        }
        
        self.analysis_history.append(record)
        self.last_analysis = result
        self.analysis_count += 1
        
        # 限制歷史記錄數量 / Limit history size
        if len(self.analysis_history) > 50:
            self.analysis_history = self.analysis_history[-50:]


@dataclass
class ProfileLine:
    """
    剖面線資料
    Profile line data
    """
    x1: float                               # 起點 X 座標 / Start X coordinate
    y1: float                               # 起點 Y 座標 / Start Y coordinate
    x2: float                               # 終點 X 座標 / End X coordinate
    y2: float                               # 終點 Y 座標 / End Y coordinate
    profile_data: np.ndarray                # 剖面數據 / Profile data
    distances: np.ndarray                   # 距離數組 / Distance array
    name: str = "profile"                   # 剖面名稱 / Profile name
    
    @property
    def length(self) -> float:
        """剖面線長度 / Profile line length"""
        return np.sqrt((self.x2 - self.x1)**2 + (self.y2 - self.y1)**2)
    
    @property
    def n_points(self) -> int:
        """剖面點數 / Number of profile points"""
        return len(self.profile_data)


# 建立資料類型的聯合類型 / Create union types for data types
SPMData = Union[TopoData, CitsData, StsData, TxtData]
AnalysisResult = Dict[str, Any]

# 常用的常數定義 / Common constants
DEFAULT_SCAN_PARAMETERS = ScanParameters(
    x_pixel=256,
    y_pixel=256,
    x_range=100.0,
    y_range=100.0
)

# 支援的檔案類型 / Supported file types
SUPPORTED_FILE_TYPES = ['txt', 'int', 'dat']

# 支援的訊號類型 / Supported signal types  
SUPPORTED_SIGNAL_TYPES = [
    'Topo', 'Lia1X', 'Lia1Y', 'Lia1R', 'Lia2X', 'Lia2Y', 'Lia2R',
    'Lia3X', 'Lia3Y', 'Lia3R', 'It_to_PC', 'InA', 'QPlus',
    'Bias', 'Frequency', 'Drive', 'Phase', 'df'
]