# KEEN 後端架構完整使用手冊 / KEEN Backend Architecture Complete Manual

**作者 / Author**: Odindino  
**日期 / Date**: 2025-06-07  
**版本 / Version**: 2.0 Complete Edition

## 目錄 / Table of Contents

1. [概述 / Overview](#概述--overview)
2. [檔案結構 / File Structure](#檔案結構--file-structure)
3. [架構設計 / Architecture Design](#架構設計--architecture-design)
4. [完整 API 參考 / Complete API Reference](#完整-api-參考--complete-api-reference)
5. [核心組件詳解 / Core Components Details](#核心組件詳解--core-components-details)
6. [使用指南 / Usage Guide](#使用指南--usage-guide)
7. [進階功能 / Advanced Features](#進階功能--advanced-features)
8. [範例程式碼 / Example Code](#範例程式碼--example-code)
9. [疑難排解 / Troubleshooting](#疑難排解--troubleshooting)
10. [效能最佳化 / Performance Optimization](#效能最佳化--performance-optimization)

## 概述 / Overview

KEEN 後端採用全新的「**類型管理器 + 檔案代理**」架構（Type Manager + File Proxy），提供統一、高效且擴展性強的 SPM 數據處理系統。此架構支援多種檔案格式（TXT、INT、DAT），並提供完整的數據分析功能。

### 主要特點 / Key Features

- 🔧 **統一的數據模型** - 標準化的數據結構和介面
- ⚡ **智能快取管理** - LRU 快取機制提升性能
- 🎯 **類型安全** - 完整的型別提示和驗證
- 🔄 **靈活的分析器** - 可插拔的分析模組系統
- 📊 **Plotly 視覺化** - 內建高品質圖表生成
- 🔗 **鏈式操作** - 直觀的 API 設計
- 💾 **記憶體最佳化** - 智能載入和卸載機制
- 🔍 **詳細日誌** - 完整的操作追蹤

## 檔案結構 / File Structure

```
backend/
├── core/                           # 核心模組
│   ├── __init__.py
│   ├── experiment_session.py       # 實驗會話（主入口）
│   ├── file_proxy.py              # 檔案代理
│   ├── type_managers.py           # 類型管理器
│   ├── data_models.py             # 資料模型定義
│   │
│   ├── parsers/                   # 解析器模組
│   │   ├── __init__.py
│   │   ├── txt_parser.py          # TXT 檔案解析器
│   │   ├── int_parser.py          # INT 檔案解析器
│   │   └── dat_parser.py          # DAT 檔案解析器
│   │
│   ├── analyzers/                 # 分析器模組
│   │   ├── __init__.py
│   │   ├── base_analyzer.py       # 分析器基類
│   │   ├── txt_analyzer.py        # TXT 分析器
│   │   ├── int_analyzer.py        # INT 分析器
│   │   ├── cits_analyzer.py       # CITS 分析器
│   │   └── dat_analyzer.py        # DAT 分析器
│   │
│   ├── analysis/                  # 分析算法模組
│   │   ├── __init__.py
│   │   ├── cits_analysis.py       # CITS 分析算法
│   │   ├── int_analysis.py        # INT 分析算法
│   │   └── profile_analysis.py    # 剖面分析算法
│   │
│   ├── visualization/             # 視覺化模組
│   │   ├── __init__.py
│   │   ├── spm_plots.py          # SPM 圖表
│   │   └── spectroscopy_plots.py  # 光譜圖表
│   │
│   ├── mathematics/               # 數學工具模組
│   │   ├── __init__.py
│   │   └── geometry.py           # 幾何計算
│   │
│   └── utils/                     # 工具模組
│       ├── __init__.py
│       └── algorithms.py         # 算法工具
│
├── test/                          # 測試模組
│   ├── interactive_new_architecture_test.ipynb  # 交互式測試
│   └── unit/                      # 單元測試
│
├── main.py                        # 主程序入口
├── api_mvp.py                     # API 層
├── requirements.txt               # 依賴清單
├── BACKEND_MANUAL.md             # 基本使用手冊
├── BACKEND_MANUAL_COMPLETE.md    # 完整使用手冊（本文件）
├── architecture_diagram.py       # 架構圖生成器
├── architecture_relationship_diagram.png  # 架構關聯圖
└── data_flow_diagram.png         # 數據流程圖
```

## 架構設計 / Architecture Design

### 核心架構模式 / Core Architecture Pattern

```
ExperimentSession (會話管理)
├── TxtManager (TXT 檔案管理)      ──→  TxtAnalyzer
├── TopoManager (拓撲圖管理)       ──→  IntAnalyzer  
├── CitsManager (CITS 數據管理)    ──→  CitsAnalyzer
└── StsManager (STS 數據管理)      ──→  DatAnalyzer

FileProxy (檔案代理) ──→ 統一存取介面

DataModels (資料模型)
├── ParseResult    (解析結果)
├── FileInfo       (檔案資訊)
├── TopoData       (拓撲圖資料)
├── CitsData       (CITS 資料)
├── StsData        (STS 資料)
└── TxtData        (TXT 資料)
```

### 數據流程 / Data Flow

```
原始檔案           解析器           標準數據           類型管理器         檔案代理          分析器            分析結果
Raw Files    →    Parsers    →    StandardData  →   TypeManager   →   FileProxy   →   Analyzers   →   Results
(.txt/.int/.dat)  (各種Parser)     (ParseResult)     (快取+管理)       (統一介面)      (分析功能)        (含圖表)
```

## 完整 API 參考 / Complete API Reference

### 1. ExperimentSession 類別

**檔案位置**: `backend/core/experiment_session.py`

**類別描述**: 實驗會話類別，整合所有資料管理功能的主要入口點

#### 初始化參數
```python
ExperimentSession(txt_file_path: str = None, cache_size: int = 20)
```
- `txt_file_path` (str, optional): TXT 檔案路徑
- `cache_size` (int, 預設=20): 快取大小

#### 公共屬性
```python
# 類型管理器
session.txt: TxtManager           # TXT 檔案管理器
session.topo: TopoManager         # 拓撲圖管理器
session.cits: CitsManager         # CITS 資料管理器
session.sts: StsManager           # STS 資料管理器

# 基本資訊
session.txt_file_path: Path       # TXT 檔案路徑
session.experiment_name: str      # 實驗名稱
session.creation_time: datetime   # 創建時間
```

#### 主要公共方法

##### 檔案操作
```python
def get_file_proxy(file_key: str) -> FileProxy:
    """獲取檔案代理"""

def has_file(file_key: str) -> bool:
    """檢查是否有指定檔案"""

def load_multiple_files(file_keys: List[str]) -> Dict[str, ParseResult]:
    """批次載入多個檔案"""

def unload_all_files(exclude_txt: bool = True) -> int:
    """卸載所有檔案"""
```

##### 資訊獲取
```python
def get_memory_info() -> Dict[str, Any]:
    """獲取記憶體使用資訊"""

def get_session_summary() -> Dict[str, Any]:
    """獲取會話摘要"""

def clear_all_caches() -> None:
    """清理所有快取"""
```

#### 屬性方法 (Properties)
```python
@property
def available_files(self) -> Dict[str, List[str]]:
    """列出所有可用檔案"""

@property  
def loaded_files(self) -> Dict[str, List[str]]:
    """列出所有已載入檔案"""

@property
def scan_parameters(self) -> ScanParameters:
    """獲取掃描參數"""

@property
def experiment_info(self) -> Dict[str, Any]:
    """獲取實驗資訊"""
```

#### 便利方法
```python
def get_topo_files() -> List[str]:
    """獲取所有拓撲檔案鍵值"""

def get_cits_files() -> List[str]:
    """獲取所有 CITS 檔案鍵值"""

def get_sts_files() -> List[str]:
    """獲取所有 STS 檔案鍵值"""

def find_files_by_signal_type(signal_type: str) -> List[str]:
    """根據訊號類型尋找檔案"""

def find_files_by_direction(direction: str) -> List[str]:
    """根據掃描方向尋找檔案"""
```

### 2. FileProxy 類別

**檔案位置**: `backend/core/file_proxy.py`

**類別描述**: 檔案代理類別，提供直觀的檔案存取介面

#### 初始化參數
```python
FileProxy(session: ExperimentSession, file_key: str)
```

#### 主要公共屬性
```python
# 核心屬性
proxy.data: SPMData              # 獲取檔案數據
proxy.metadata: Dict[str, Any]   # 獲取檔案元資料
proxy.analyzer                   # 獲取分析器實例
proxy.file_info: FileInfo        # 獲取檔案資訊
proxy.is_loaded: bool            # 檢查檔案是否已載入
proxy.file_type: str             # 獲取檔案類型
```

#### 拓撲圖專用屬性
```python
# 快捷存取拓撲圖屬性
proxy.image: Optional[np.ndarray]      # 圖像資料
proxy.flattened: Optional[np.ndarray]  # 平坦化圖像
proxy.x_range: Optional[float]         # X 方向範圍
proxy.y_range: Optional[float]         # Y 方向範圍  
proxy.shape: Optional[tuple]           # 數據形狀
```

#### CITS 專用屬性
```python
# 快捷存取 CITS 屬性
proxy.bias_values: Optional[np.ndarray]  # 偏壓值
proxy.data_3d: Optional[np.ndarray]      # 3D 數據
```

#### 主要公共方法
```python
def get_bias_slice(bias_index: int) -> Optional[np.ndarray]:
    """獲取特定偏壓的 2D 切片"""

def flatten_plane(method: str = 'linear', **kwargs) -> Optional[np.ndarray]:
    """執行平面平坦化"""

def extract_profile(x1: float, y1: float, x2: float, y2: float, 
                   name: str = "profile") -> Optional[ProfileLine]:
    """提取剖面線"""

def extract_iv_curve(x: int, y: int) -> Optional[Dict[str, Any]]:
    """提取 I-V 曲線"""

def reload(force: bool = True) -> 'FileProxy':
    """重新載入檔案"""

def unload() -> bool:
    """卸載檔案"""

def get_analysis_history() -> list:
    """獲取分析歷史"""
```

### 3. TypeManager 基類及其子類

**檔案位置**: `backend/core/type_managers.py`

#### TypeManager (抽象基類)

##### 初始化參數
```python
TypeManager(cache_size: int = 20, session = None)
```

##### 主要公共方法
```python
def add_file(key: str, info: FileInfo) -> None:
    """添加檔案資訊"""

def has_file(key: str) -> bool:
    """檢查是否有指定的檔案"""

def is_loaded(key: str) -> bool:
    """檢查檔案是否已載入"""

def load(key: str, force_reload: bool = False) -> ParseResult:
    """載入檔案"""

def get_analyzer(key: str):
    """獲取或創建分析器"""

def unload(key: str) -> bool:
    """卸載檔案"""

def get_files() -> Dict[str, FileInfo]:
    """獲取所有檔案資訊"""

def get_loaded_files() -> List[str]:
    """獲取已載入的檔案列表"""

def get_cache_info() -> Dict[str, Any]:
    """獲取快取資訊"""

def clear_cache() -> None:
    """清理快取"""
```

##### 抽象方法
```python
@abstractmethod
def _parse_file(info: FileInfo) -> ParseResult:
    """解析檔案（子類實作）"""

@abstractmethod  
def _create_analyzer(key: str):
    """創建分析器（子類實作）"""
```

#### TxtManager / TopoManager / CitsManager / StsManager

這些子類繼承 TypeManager，提供特定檔案類型的管理功能。

### 4. 資料模型 (data_models.py)

**檔案位置**: `backend/core/data_models.py`

#### ParseResult
```python
@dataclass
class ParseResult:
    metadata: Dict[str, Any]      # 元資料
    data: Any                     # 主要資料
    derived: Dict[str, Any]       # 衍生資料
    errors: List[str]             # 錯誤訊息
    warnings: List[str]           # 警告訊息
    timestamp: datetime           # 時間戳
    parser_type: str              # 解析器類型
    
    @property
    def success(self) -> bool:
        """是否成功解析"""
    
    def add_error(message: str) -> None:
        """添加錯誤訊息"""
    
    def add_warning(message: str) -> None:
        """添加警告訊息"""
```

#### FileInfo
```python
@dataclass
class FileInfo:
    path: str                           # 檔案路徑
    type: str                          # 檔案類型
    size: int                          # 檔案大小
    signal_type: Optional[str] = None  # 訊號類型
    direction: Optional[str] = None    # 掃描方向
    loaded: bool = False               # 是否已載入
    loaded_at: Optional[datetime] = None  # 載入時間
    
    @property
    def filename(self) -> str:
        """獲取檔案名稱"""
    
    @property
    def human_readable_size(self) -> str:
        """人類可讀的檔案大小"""
```

#### ScanParameters
```python
@dataclass
class ScanParameters:
    x_pixel: int                    # X 方向像素數
    y_pixel: int                    # Y 方向像素數
    x_range: float                  # X 方向掃描範圍 nm
    y_range: float                  # Y 方向掃描範圍 nm
    
    @property
    def pixel_scale_x(self) -> float:
        """X 方向像素尺度 nm/pixel"""
    
    @property
    def pixel_scale_y(self) -> float:
        """Y 方向像素尺度 nm/pixel"""
    
    @property
    def aspect_ratio(self) -> float:
        """長寬比"""
    
    @property
    def total_pixels(self) -> int:
        """總像素數"""
```

#### TopoData
```python
@dataclass 
class TopoData:
    image: np.ndarray                    # 原始圖像數據
    x_range: float                       # X 方向範圍 nm
    y_range: float                       # Y 方向範圍 nm
    x_pixels: int                        # X 方向像素數
    y_pixels: int                        # Y 方向像素數
    data_scale: float                    # 數據 scale
    signal_type: str = "Topo"           # 訊號類型
    direction: Optional[str] = None      # 掃描方向
    
    # 處理後的資料
    flattened: Optional[np.ndarray] = None
    profile_lines: Dict[str, Any] = field(default_factory=dict)
    statistics: Dict[str, float] = field(default_factory=dict)
    
    @property
    def shape(self) -> tuple:
        """圖像形狀"""
    
    @property
    def pixel_scale_x(self) -> float:
        """X 方向像素尺度"""
    
    @property
    def pixel_scale_y(self) -> float:
        """Y 方向像素尺度"""
    
    @property
    def current_image(self) -> np.ndarray:
        """當前顯示的圖像（平坦化優先）"""
```

#### CitsData
```python
@dataclass
class CitsData:
    data_3d: np.ndarray                      # 3D 數據 (n_bias, y, x)
    bias_values: np.ndarray                  # 偏壓值
    grid_size: List[int]                     # 網格大小 [x, y]
    x_range: float                           # X 方向範圍 nm
    y_range: float                           # Y 方向範圍 nm
    measurement_mode: str = "CITS"           # 量測模式
    
    # 分析結果
    iv_curves: Dict[str, Any] = field(default_factory=dict)
    conductance_maps: Dict[str, np.ndarray] = field(default_factory=dict)
    gap_maps: Dict[str, np.ndarray] = field(default_factory=dict)
    
    @property
    def shape(self) -> tuple:
        """數據形狀"""
    
    @property
    def n_bias_points(self) -> int:
        """偏壓點數"""
    
    @property
    def bias_range(self) -> tuple:
        """偏壓範圍"""
    
    def get_bias_slice(bias_index: int) -> np.ndarray:
        """獲取特定偏壓的2D切片"""
```

#### StsData
```python
@dataclass
class StsData:
    data_2d: np.ndarray                      # 2D 數據 (n_bias, n_points)
    bias_values: np.ndarray                  # 偏壓值
    x_coords: np.ndarray                     # X 座標
    y_coords: np.ndarray                     # Y 座標
    measurement_mode: str = "STS"            # 量測模式
    
    # 分析結果
    gap_values: Dict[str, float] = field(default_factory=dict)
    peak_positions: Dict[str, List[float]] = field(default_factory=dict)
    
    @property
    def shape(self) -> tuple:
        """數據形狀"""
    
    @property
    def n_points(self) -> int:
        """量測點數"""
    
    @property
    def n_bias_points(self) -> int:
        """偏壓點數"""
```

#### TxtData
```python
@dataclass
class TxtData:
    experiment_info: Dict[str, Any]          # 實驗資訊
    scan_parameters: ScanParameters          # 掃描參數
    int_files: List[Dict[str, Any]]         # INT 檔案列表
    dat_files: List[Dict[str, Any]]         # DAT 檔案列表
    signal_types: List[str]                  # 訊號類型列表
    
    @property
    def experiment_name(self) -> str:
        """實驗名稱"""
    
    @property
    def total_files(self) -> int:
        """總檔案數"""
```

### 5. 解析器類別 (Parsers)

#### TxtParser
```python
class TxtParser:
    def __init__(file_path: str):
        """初始化 TXT 解析器"""
    
    def parse() -> ParseResult:
        """解析 TXT 檔案"""
    
    def get_int_files():
        """返回 INT 檔案描述列表"""
    
    def get_dat_files():
        """返回 DAT 檔案描述列表"""
```

#### IntParser
```python
class IntParser:
    def __init__(file_path: str, scale: float, x_pixel: int, y_pixel: int):
        """初始化 INT 解析器"""
    
    def parse() -> ParseResult:
        """解析 INT 檔案並返回形貌數據"""
```

#### DatParser
```python
class DatParser:
    def __init__():
        """初始化 DAT 解析器"""
    
    def parse(file_path: str, dat_info: dict = None) -> ParseResult:
        """解析 DAT 檔案"""
    
    @staticmethod
    def prepare_cits_for_display(data_3d: np.ndarray, scan_direction: str) -> np.ndarray:
        """為顯示準備 CITS 數據方向"""
    
    @staticmethod
    def is_cits_data(data: Dict) -> bool:
        """檢查解析後的數據是否為 CITS 格式"""
```

### 6. 分析器類別 (Analyzers)

#### BaseAnalyzer (抽象基類)
```python
class BaseAnalyzer(ABC):
    def __init__(data: SPMData):
        """初始化分析器"""
    
    # 主要屬性
    data: SPMData                    # SPM 數據
    state: AnalysisState            # 分析狀態
    analysis_history: List[Dict]    # 分析歷史
    cached_results: Dict[str, Any]  # 快取數據
    
    @abstractmethod
    def analyze(**kwargs) -> Dict[str, Any]:
        """核心分析方法（抽象）"""
    
    def get_results() -> Dict[str, Any]:
        """獲取最新的分析結果"""
    
    def get_history() -> List[Dict]:
        """獲取分析歷史"""
    
    def clear_cache() -> None:
        """清理快取數據"""
    
    def get_cache_info() -> Dict[str, Any]:
        """獲取快取信息"""
    
    def get_status() -> Dict[str, Any]:
        """獲取分析器狀態"""
    
    def reset() -> None:
        """重置分析器狀態"""
    
    def validate_input(**kwargs) -> bool:
        """驗證輸入數據"""
```

#### IntAnalyzer
```python
class IntAnalyzer(BaseAnalyzer):
    def analyze(**kwargs) -> Dict[str, Any]:
        """分析 INT 形貌數據"""
    
    def apply_flattening(method: str = 'linewise_mean', **kwargs) -> Dict[str, Any]:
        """應用平面化處理"""
    
    def apply_tilt_correction(direction: str, step_size: int = 10, 
                             fine_tune: bool = False) -> Dict[str, Any]:
        """應用傾斜校正"""
    
    def extract_line_profile(start_point: Tuple[int, int], 
                           end_point: Tuple[int, int], 
                           method: str = 'interpolation') -> Dict[str, Any]:
        """提取線段剖面"""
    
    def detect_features(feature_type: str = 'peaks', **kwargs) -> Dict[str, Any]:
        """檢測表面特徵"""
    
    def reset_to_original() -> Dict[str, Any]:
        """重置到原始數據"""
```

#### CitsAnalyzer
```python
class CitsAnalyzer(BaseAnalyzer):
    def analyze(**kwargs) -> Dict[str, Any]:
        """分析 CITS 數據"""
    
    def extract_line_profile(start_coord: Tuple[int, int], 
                           end_coord: Tuple[int, int],
                           sampling_method: str = 'bresenham') -> Dict[str, Any]:
        """提取線段剖面光譜"""
    
    def get_bias_slice(bias_index: int) -> Dict[str, Any]:
        """獲取特定偏壓的2D切片"""
    
    def analyze_conductance_maps(**kwargs) -> Dict[str, Any]:
        """分析電導圖"""
```

## 核心組件詳解 / Core Components Details

### 實驗會話 (ExperimentSession)

實驗會話是整個系統的核心，提供統一的實驗管理介面。

#### 內部架構
```python
session = ExperimentSession("/path/to/experiment.txt")

# 自動載入 TXT 檔案並發現相關檔案
session._load_experiment()

# 四個管理器自動初始化
session.txt    # TxtManager
session.topo   # TopoManager  
session.cits   # CitsManager
session.sts    # StsManager
```

#### 檔案發現機制
```python
# TXT 解析後自動註冊相關檔案
txt_data = session.txt.load("main_txt")
session._register_associated_files(txt_data.data)

# 自動分類檔案類型
for int_file in txt_data.data.int_files:
    session.topo.add_file(key, file_info)
    
for dat_file in txt_data.data.dat_files:
    if is_cits(dat_file):
        session.cits.add_file(key, file_info)
    else:
        session.sts.add_file(key, file_info)
```

### 檔案代理 (FileProxy)

檔案代理提供統一且直觀的檔案存取介面。

#### 智能屬性存取
```python
proxy = session.get_file_proxy("TopoFwd.int")

# 直接存取數據屬性
image = proxy.image           # 等同於 proxy.data.image
shape = proxy.shape          # 等同於 proxy.data.shape
x_range = proxy.x_range      # 等同於 proxy.data.x_range

# 智能類型判斷
if proxy.file_type == "topo":
    # 提供拓撲圖專用方法
    flattened = proxy.flatten_plane()
    
elif proxy.file_type == "cits":
    # 提供 CITS 專用方法
    slice_data = proxy.get_bias_slice(100)
```

#### 分析器整合
```python
# 延遲載入分析器
analyzer = proxy.analyzer     # 第一次存取時創建

# 執行分析
result = analyzer.analyze()

# 獲取分析歷史
history = proxy.get_analysis_history()
```

### 類型管理器 (TypeManager)

類型管理器提供檔案的載入、快取和分析器管理。

#### LRU 快取機制
```python
manager = session.topo

# 載入檔案（加入快取）
result1 = manager.load("file1")   # 快取 miss
result2 = manager.load("file1")   # 快取 hit

# 查看快取狀態
cache_info = manager.get_cache_info()
print(f"命中率: {cache_info['hit_rate']:.2%}")

# 快取滿時自動移除 LRU 項目
for i in range(25):  # 超過預設快取大小 20
    manager.load(f"file{i}")
```

#### 分析器工廠
```python
# 每個檔案對應一個分析器實例
analyzer1 = manager.get_analyzer("file1")
analyzer2 = manager.get_analyzer("file2")

# 分析器與檔案生命週期綁定
manager.unload("file1")  # 同時移除分析器
```

## 使用指南 / Usage Guide

### 基本工作流程 / Basic Workflow

#### 1. 初始化和載入
```python
from backend.core.experiment_session import ExperimentSession

# 初始化會話
session = ExperimentSession()

# 載入實驗檔案
session.load_txt_file("/path/to/experiment.txt")

# 檢查載入狀態
print("可用檔案:", session.available_files)
print("已載入檔案:", session.loaded_files)
```

#### 2. 拓撲圖分析完整流程
```python
# 獲取拓撲圖檔案
topo_files = session.get_topo_files()
topo_key = topo_files[0]  # 選擇第一個

# 獲取檔案代理
topo = session.get_file_proxy(topo_key)

# 檢查基本資訊
print(f"圖像尺寸: {topo.shape}")
print(f"掃描範圍: {topo.x_range} x {topo.y_range} nm")
print(f"訊號類型: {topo.file_info.signal_type}")

# 執行基本分析
basic_result = topo.analyzer.analyze()
print("基本統計:", basic_result['data']['statistics'])

# 平坦化處理
flatten_result = topo.analyzer.apply_flattening(
    method='polynomial',  # 多項式平坦化
    order=2,             # 二次多項式
    mask_threshold=0.1   # 遮罩閾值
)

# 檢視平坦化效果
original_std = np.std(topo.image)
flattened_std = np.std(flatten_result['data']['flattened_image'])
print(f"平坦化改善: {original_std:.3f} → {flattened_std:.3f}")

# 傾斜校正
tilt_result = topo.analyzer.apply_tilt_correction(
    direction='x',       # X 方向校正
    step_size=10,       # 步長
    fine_tune=True      # 精細調整
)

# 提取剖面線
profile_result = topo.analyzer.extract_line_profile(
    start_point=(10, 50),    # 起點 (x, y)
    end_point=(200, 50),     # 終點 (x, y)
    method='interpolation'   # 插值方法
)

# 檢視剖面數據
profile_data = profile_result['data']['profile_data']
distances = profile_result['data']['distances']
print(f"剖面長度: {profile_result['data']['physical_length']:.2f} nm")

# 特徵檢測
feature_result = topo.analyzer.detect_features(
    feature_type='peaks',    # 檢測峰值
    prominence=1.0,         # 峰值突出度
    distance=10             # 最小距離
)

print(f"檢測到 {len(feature_result['data']['features'])} 個特徵")

# 顯示圖表
for plot_name, fig in basic_result['plots'].items():
    fig.show()
```

#### 3. CITS 數據分析完整流程
```python
# 獲取 CITS 檔案
cits_files = session.get_cits_files()
cits_key = cits_files[0]

# 獲取檔案代理
cits = session.get_file_proxy(cits_key)

# 檢查基本資訊
print(f"CITS 數據尺寸: {cits.shape}")
print(f"偏壓範圍: {cits.bias_values.min():.2f} ~ {cits.bias_values.max():.2f} V")
print(f"偏壓點數: {len(cits.bias_values)}")

# 執行基本分析
basic_result = cits.analyzer.analyze()
bias_pattern = basic_result['data']['bias_pattern']
print(f"偏壓模式: {bias_pattern['pattern_type']}")

# 提取線段剖面光譜
line_result = cits.analyzer.extract_line_profile(
    start_coord=(20, 20),        # 起點 (x, y)
    end_coord=(80, 80),          # 終點 (x, y)
    sampling_method='bresenham'  # 採樣方法
)

line_sts = line_result['data']['line_sts']  # (n_bias, n_points)
print(f"線段剖面形狀: {line_sts.shape}")

# 獲取特定偏壓切片
bias_index = len(cits.bias_values) // 2  # 中間偏壓
slice_result = cits.analyzer.get_bias_slice(bias_index)
slice_data = slice_result['data']['slice_data']
bias_value = slice_result['data']['bias_value']
print(f"偏壓 {bias_value:.3f}V 切片形狀: {slice_data.shape}")

# 電導分析
conductance_result = cits.analyzer.analyze_conductance_maps(
    smoothing=True,      # 啟用平滑
    method='gradient'    # 梯度方法
)

# 顯示所有圖表
for plot_name, fig in basic_result['plots'].items():
    fig.show()
    
for plot_name, fig in line_result['plots'].items():
    fig.show()
    
for plot_name, fig in slice_result['plots'].items():
    fig.show()
```

#### 4. 會話管理和效能監控
```python
# 檢查記憶體使用
memory_info = session.get_memory_info()
print("記憶體使用:", memory_info)

# 檢查快取狀態
for manager_name in ['txt', 'topo', 'cits', 'sts']:
    manager = getattr(session, manager_name)
    cache_info = manager.get_cache_info()
    print(f"{manager_name} 快取命中率: {cache_info['hit_rate']:.2%}")

# 批次載入檔案
file_keys = session.get_topo_files()[:5]  # 前5個檔案
results = session.load_multiple_files(file_keys)
print(f"批次載入 {len(results)} 個檔案")

# 清理快取釋放記憶體
session.clear_all_caches()
print("快取已清理")

# 獲取會話摘要
summary = session.get_session_summary()
print("會話摘要:", summary)
```

## 進階功能 / Advanced Features

### 自訂分析參數

#### 拓撲圖進階平坦化
```python
# 線性平坦化（逐行）
linear_result = topo.analyzer.apply_flattening(
    method='linewise_mean',
    direction='x',           # 平坦化方向
    exclude_borders=True,    # 排除邊界
    border_width=5          # 邊界寬度
)

# 多項式平坦化（整體）
poly_result = topo.analyzer.apply_flattening(
    method='polynomial',
    order=3,                # 三次多項式
    mask_outliers=True,     # 遮罩異常值
    outlier_threshold=3.0   # 異常值閾值（標準差倍數）
)

# 平面平坦化（三點法）
plane_result = topo.analyzer.apply_flattening(
    method='plane',
    corners_only=True,      # 只使用角點
    manual_points=[(10,10), (200,10), (10,200)]  # 手動指定點
)
```

#### CITS 進階光譜分析
```python
# 高密度線段採樣
dense_line = cits.analyzer.extract_line_profile(
    start_coord=(0, 0),
    end_coord=(99, 99),
    sampling_method='interpolate',  # 插值採樣
    num_points=200                 # 指定採樣點數
)

# 多線段並行分析
line_profiles = []
coordinates = [
    ((0, 50), (99, 50)),    # 水平線
    ((50, 0), (50, 99)),    # 垂直線
    ((0, 0), (99, 99)),     # 對角線
]

for start, end in coordinates:
    result = cits.analyzer.extract_line_profile(start, end)
    line_profiles.append(result)

# 偏壓序列分析
bias_slices = []
for i in range(0, len(cits.bias_values), 50):  # 每50個偏壓取一個
    slice_result = cits.analyzer.get_bias_slice(i)
    bias_slices.append(slice_result)
```

### 批次處理和自動化

#### 批次檔案分析
```python
def batch_analyze_topo_files(session, signal_type=None, direction=None):
    """批次分析拓撲檔案"""
    results = {}
    
    # 篩選檔案
    if signal_type:
        files = session.find_files_by_signal_type(signal_type)
    elif direction:
        files = session.find_files_by_direction(direction)
    else:
        files = session.get_topo_files()
    
    for file_key in files:
        try:
            proxy = session.get_file_proxy(file_key)
            
            # 基本分析
            basic = proxy.analyzer.analyze()
            
            # 平坦化
            flattened = proxy.analyzer.apply_flattening(method='polynomial', order=2)
            
            # 統計數據
            stats = {
                'original_std': np.std(proxy.image),
                'flattened_std': np.std(flattened['data']['flattened_image']),
                'signal_type': proxy.file_info.signal_type,
                'direction': proxy.file_info.direction
            }
            
            results[file_key] = {
                'basic': basic,
                'flattened': flattened,
                'stats': stats
            }
            
        except Exception as e:
            print(f"分析 {file_key} 失敗: {e}")
    
    return results

# 使用批次分析
topo_results = batch_analyze_topo_files(session, signal_type='Topo')
```

#### 自動報告生成
```python
def generate_experiment_report(session):
    """生成實驗分析報告"""
    report = {
        'experiment_info': session.experiment_info,
        'scan_parameters': session.scan_parameters,
        'file_summary': {},
        'analysis_results': {}
    }
    
    # 檔案摘要
    for file_type in ['topo', 'cits', 'sts']:
        manager = getattr(session, file_type)
        files = manager.get_files()
        report['file_summary'][file_type] = {
            'count': len(files),
            'total_size': sum(f.size for f in files.values()),
            'signal_types': list(set(f.signal_type for f in files.values() if f.signal_type))
        }
    
    # 分析結果摘要
    # ... 分析邏輯
    
    return report

# 生成報告
report = generate_experiment_report(session)
```

### 記憶體和效能最佳化

#### 智能快取策略
```python
# 大檔案使用小快取
large_file_session = ExperimentSession(cache_size=5)

# 小檔案使用大快取
small_file_session = ExperimentSession(cache_size=50)

# 動態調整快取大小
def adjust_cache_size(session):
    memory_info = session.get_memory_info()
    total_size = memory_info['total_loaded_size']
    
    if total_size > 1e9:  # > 1GB
        session.txt.cache_size = 5
        session.topo.cache_size = 5
        session.cits.cache_size = 3
    elif total_size > 5e8:  # > 500MB
        session.txt.cache_size = 10
        session.topo.cache_size = 10
        session.cits.cache_size = 5
```

#### 選擇性載入
```python
# 只載入需要的檔案類型
session = ExperimentSession()
session.load_txt_file(txt_path)

# 只分析特定訊號類型
topo_files = session.find_files_by_signal_type('Topo')
for file_key in topo_files:
    proxy = session.get_file_proxy(file_key)
    # 只做必要的分析...

# 及時卸載不需要的檔案
for file_key in session.topo.get_loaded_files():
    if file_key not in needed_files:
        session.topo.unload(file_key)
```

## 範例程式碼 / Example Code

### 完整分析工作流程範例

```python
"""
KEEN 後端完整分析工作流程範例
Complete analysis workflow example for KEEN backend
"""

from backend.core.experiment_session import ExperimentSession
import numpy as np
import matplotlib.pyplot as plt

def complete_analysis_workflow(txt_file_path):
    """完整的 SPM 數據分析工作流程"""
    
    # ============ 1. 初始化會話 ============
    print("🚀 初始化實驗會話...")
    session = ExperimentSession()
    
    # 載入實驗
    success = session.load_txt_file(txt_file_path)
    if not success:
        print("❌ 實驗載入失敗")
        return None
    
    print("✅ 實驗載入成功")
    print(f"📁 實驗名稱: {session.experiment_name}")
    
    # ============ 2. 檢視檔案概況 ============
    print("\n📊 檔案概況:")
    available = session.available_files
    for file_type, files in available.items():
        print(f"  {file_type}: {len(files)} 個檔案")
    
    # ============ 3. 拓撲圖分析 ============
    print("\n🗺️  開始拓撲圖分析...")
    topo_files = session.get_topo_files()
    
    if topo_files:
        # 選擇第一個拓撲檔案
        topo_key = topo_files[0]
        topo = session.get_file_proxy(topo_key)
        
        print(f"   檔案: {topo.file_info.filename}")
        print(f"   尺寸: {topo.shape}")
        print(f"   範圍: {topo.x_range:.1f} x {topo.y_range:.1f} nm")
        
        # 基本分析
        print("   執行基本分析...")
        basic_result = topo.analyzer.analyze()
        stats = basic_result['data']['statistics']
        print(f"   高度範圍: {stats['min']:.3f} ~ {stats['max']:.3f} nm")
        print(f"   粗糙度 (RMS): {stats['rms']:.3f} nm")
        
        # 平坦化處理
        print("   執行平坦化處理...")
        flatten_result = topo.analyzer.apply_flattening(
            method='polynomial',
            order=2
        )
        
        # 提取剖面線
        print("   提取剖面線...")
        profile_result = topo.analyzer.extract_line_profile(
            start_point=(10, topo.shape[0]//2),
            end_point=(topo.shape[1]-10, topo.shape[0]//2)
        )
        
        print(f"   剖面長度: {profile_result['data']['physical_length']:.2f} nm")
        
    # ============ 4. CITS 數據分析 ============
    print("\n🔬 開始 CITS 數據分析...")
    cits_files = session.get_cits_files()
    
    if cits_files:
        # 選擇第一個 CITS 檔案
        cits_key = cits_files[0]
        cits = session.get_file_proxy(cits_key)
        
        print(f"   檔案: {cits.file_info.filename}")
        print(f"   數據尺寸: {cits.shape}")
        print(f"   偏壓範圍: {cits.bias_values.min():.2f} ~ {cits.bias_values.max():.2f} V")
        
        # 基本分析
        print("   執行基本分析...")
        cits_basic = cits.analyzer.analyze()
        pattern = cits_basic['data']['bias_pattern']
        print(f"   偏壓模式: {pattern['pattern_type']}")
        
        # 線段剖面光譜
        print("   提取線段剖面光譜...")
        line_result = cits.analyzer.extract_line_profile(
            start_coord=(10, 10),
            end_coord=(cits.shape[2]-10, cits.shape[1]-10)
        )
        
        line_sts = line_result['data']['line_sts']
        print(f"   光譜數據形狀: {line_sts.shape}")
        
        # 偏壓切片
        print("   獲取偏壓切片...")
        mid_bias = len(cits.bias_values) // 2
        slice_result = cits.analyzer.get_bias_slice(mid_bias)
        print(f"   偏壓 {slice_result['data']['bias_value']:.3f}V 切片完成")
        
    # ============ 5. 效能和記憶體監控 ============
    print("\n📈 系統狀態:")
    memory_info = session.get_memory_info()
    print(f"   總載入大小: {memory_info['total_loaded_size']/1e6:.1f} MB")
    print(f"   載入檔案數: {memory_info['total_loaded_files']}")
    
    # 快取效能
    cache_stats = []
    for manager_name in ['txt', 'topo', 'cits', 'sts']:
        manager = getattr(session, manager_name)
        cache_info = manager.get_cache_info()
        cache_stats.append(f"{manager_name}: {cache_info['hit_rate']:.1%}")
    print(f"   快取命中率: {', '.join(cache_stats)}")
    
    # ============ 6. 生成摘要報告 ============
    print("\n📋 生成分析摘要...")
    summary = session.get_session_summary()
    
    report = {
        'experiment_name': session.experiment_name,
        'total_files': sum(len(files) for files in available.values()),
        'analysis_results': {
            'topo_analyzed': len(topo_files) > 0,
            'cits_analyzed': len(cits_files) > 0,
        },
        'system_performance': {
            'memory_usage_mb': memory_info['total_loaded_size']/1e6,
            'cache_performance': cache_stats
        }
    }
    
    print("✅ 分析完成!")
    return report

# ============ 使用範例 ============
if __name__ == "__main__":
    # 設定實驗檔案路徑
    experiment_path = "/path/to/your/experiment.txt"
    
    # 執行完整分析
    try:
        result = complete_analysis_workflow(experiment_path)
        if result:
            print("\n🎉 分析報告:")
            for key, value in result.items():
                print(f"  {key}: {value}")
    except Exception as e:
        print(f"❌ 分析過程發生錯誤: {e}")
```

### 進階自動化分析範例

```python
"""
進階自動化分析範例：批次處理多個實驗
Advanced automation example: batch processing multiple experiments
"""

import os
from pathlib import Path
import pandas as pd

class KeenBatchAnalyzer:
    """KEEN 批次分析器"""
    
    def __init__(self, cache_size=10):
        self.cache_size = cache_size
        self.results = []
    
    def analyze_experiment_folder(self, folder_path):
        """分析整個實驗資料夾"""
        folder = Path(folder_path)
        txt_files = list(folder.glob("*.txt"))
        
        print(f"📁 發現 {len(txt_files)} 個實驗檔案")
        
        for txt_file in txt_files:
            try:
                result = self.analyze_single_experiment(str(txt_file))
                if result:
                    self.results.append(result)
                    print(f"✅ {txt_file.name} 分析完成")
                else:
                    print(f"❌ {txt_file.name} 分析失敗")
            except Exception as e:
                print(f"❌ {txt_file.name} 錯誤: {e}")
    
    def analyze_single_experiment(self, txt_path):
        """分析單個實驗"""
        session = ExperimentSession()
        
        if not session.load_txt_file(txt_path):
            return None
        
        result = {
            'experiment_name': session.experiment_name,
            'txt_path': txt_path,
            'scan_parameters': session.scan_parameters.__dict__,
            'file_counts': {},
            'topo_stats': {},
            'cits_stats': {}
        }
        
        # 檔案統計
        available = session.available_files
        for file_type, files in available.items():
            result['file_counts'][file_type] = len(files)
        
        # 拓撲圖分析
        topo_files = session.get_topo_files()
        if topo_files:
            topo_stats = self._analyze_topo_batch(session, topo_files[:3])  # 只分析前3個
            result['topo_stats'] = topo_stats
        
        # CITS 分析
        cits_files = session.get_cits_files()
        if cits_files:
            cits_stats = self._analyze_cits_batch(session, cits_files[:2])  # 只分析前2個
            result['cits_stats'] = cits_stats
        
        return result
    
    def _analyze_topo_batch(self, session, file_keys):
        """批次拓撲圖分析"""
        stats = {
            'files_analyzed': len(file_keys),
            'roughness_values': [],
            'height_ranges': [],
            'signal_types': []
        }
        
        for key in file_keys:
            proxy = session.get_file_proxy(key)
            basic_result = proxy.analyzer.analyze()
            
            file_stats = basic_result['data']['statistics']
            stats['roughness_values'].append(file_stats['rms'])
            stats['height_ranges'].append(file_stats['max'] - file_stats['min'])
            stats['signal_types'].append(proxy.file_info.signal_type)
        
        # 計算統計摘要
        if stats['roughness_values']:
            stats['avg_roughness'] = np.mean(stats['roughness_values'])
            stats['avg_height_range'] = np.mean(stats['height_ranges'])
        
        return stats
    
    def _analyze_cits_batch(self, session, file_keys):
        """批次 CITS 分析"""
        stats = {
            'files_analyzed': len(file_keys),
            'bias_ranges': [],
            'data_sizes': [],
            'bias_patterns': []
        }
        
        for key in file_keys:
            proxy = session.get_file_proxy(key)
            basic_result = proxy.analyzer.analyze()
            
            bias_range = (float(proxy.bias_values.min()), float(proxy.bias_values.max()))
            stats['bias_ranges'].append(bias_range)
            stats['data_sizes'].append(proxy.shape)
            stats['bias_patterns'].append(basic_result['data']['bias_pattern']['pattern_type'])
        
        return stats
    
    def export_results(self, output_path):
        """匯出分析結果"""
        if not self.results:
            print("❌ 沒有分析結果可匯出")
            return
        
        # 轉換為 DataFrame
        rows = []
        for result in self.results:
            row = {
                'experiment_name': result['experiment_name'],
                'txt_path': result['txt_path'],
                'x_pixels': result['scan_parameters']['x_pixel'],
                'y_pixels': result['scan_parameters']['y_pixel'],
                'x_range': result['scan_parameters']['x_range'],
                'y_range': result['scan_parameters']['y_range'],
                'topo_files': result['file_counts'].get('topo', 0),
                'cits_files': result['file_counts'].get('cits', 0),
                'sts_files': result['file_counts'].get('sts', 0),
            }
            
            # 添加拓撲統計
            if result['topo_stats']:
                row['avg_roughness'] = result['topo_stats'].get('avg_roughness', 0)
                row['avg_height_range'] = result['topo_stats'].get('avg_height_range', 0)
            
            # 添加 CITS 統計
            if result['cits_stats']:
                row['cits_files_analyzed'] = result['cits_stats']['files_analyzed']
            
            rows.append(row)
        
        # 儲存 CSV
        df = pd.DataFrame(rows)
        df.to_csv(output_path, index=False)
        print(f"📊 結果已匯出至: {output_path}")
        
        return df

# 使用範例
def main():
    # 初始化批次分析器
    analyzer = KeenBatchAnalyzer(cache_size=5)
    
    # 分析實驗資料夾
    experiment_folder = "/path/to/experiments"
    analyzer.analyze_experiment_folder(experiment_folder)
    
    # 匯出結果
    output_file = "batch_analysis_results.csv"
    df = analyzer.export_results(output_file)
    
    # 顯示摘要
    if df is not None:
        print(f"\n📈 批次分析摘要:")
        print(f"   總實驗數: {len(df)}")
        print(f"   平均拓撲檔案數: {df['topo_files'].mean():.1f}")
        print(f"   平均 CITS 檔案數: {df['cits_files'].mean():.1f}")
        if 'avg_roughness' in df.columns:
            print(f"   平均粗糙度: {df['avg_roughness'].mean():.3f} nm")

if __name__ == "__main__":
    main()
```

## 疑難排解 / Troubleshooting

### 常見錯誤和解決方案

#### 1. 檔案載入錯誤
```python
# 錯誤: FileNotFoundError
try:
    session.load_txt_file("/path/to/file.txt")
except FileNotFoundError:
    print("檔案不存在，請檢查路徑")

# 錯誤: PermissionError  
try:
    session.load_txt_file("/path/to/file.txt")
except PermissionError:
    print("檔案權限不足，請檢查檔案權限")

# 檢查檔案存在和權限
import os
file_path = "/path/to/file.txt"
if os.path.exists(file_path):
    if os.access(file_path, os.R_OK):
        print("檔案可讀取")
    else:
        print("檔案權限不足")
else:
    print("檔案不存在")
```

#### 2. 記憶體不足錯誤
```python
# 監控記憶體使用
import psutil

def check_memory_usage():
    memory = psutil.virtual_memory()
    print(f"記憶體使用率: {memory.percent}%")
    print(f"可用記憶體: {memory.available / 1e9:.1f} GB")

# 記憶體不足時的處理策略
def handle_memory_pressure(session):
    memory_info = session.get_memory_info()
    
    if memory_info['total_loaded_size'] > 2e9:  # > 2GB
        print("記憶體壓力大，開始清理...")
        
        # 清理最少使用的快取
        session.clear_all_caches()
        
        # 卸載非必要檔案
        for manager_name in ['sts', 'cits', 'topo']:
            manager = getattr(session, manager_name)
            loaded_files = manager.get_loaded_files()
            
            # 只保留最近使用的檔案
            for file_key in loaded_files[5:]:  # 保留前5個
                manager.unload(file_key)
```

#### 3. 分析器錯誤
```python
# 捕獲分析錯誤
def safe_analyze(analyzer, **kwargs):
    try:
        result = analyzer.analyze(**kwargs)
        if not result['success']:
            print(f"分析失敗: {result.get('error', '未知錯誤')}")
            return None
        return result
    except Exception as e:
        print(f"分析器異常: {e}")
        return None

# 檢查分析器狀態
def check_analyzer_status(analyzer):
    status = analyzer.get_status()
    print(f"分析器狀態: {status}")
    
    if status.get('errors'):
        print("錯誤歷史:")
        for error in status['errors'][-3:]:  # 最近3個錯誤
            print(f"  {error['timestamp']}: {error['message']}")
```

#### 4. 數據格式錯誤
```python
# 驗證數據格式
def validate_data_format(proxy):
    try:
        # 檢查基本屬性
        if proxy.data is None:
            return False, "數據為空"
        
        # 檢查拓撲圖數據
        if proxy.file_type == "topo":
            if proxy.image is None:
                return False, "缺少圖像數據"
            if proxy.image.ndim != 2:
                return False, f"圖像維度錯誤: {proxy.image.ndim}"
        
        # 檢查 CITS 數據
        elif proxy.file_type == "cits":
            if proxy.data_3d is None:
                return False, "缺少 3D 數據"
            if proxy.bias_values is None:
                return False, "缺少偏壓數據"
            if proxy.data_3d.shape[0] != len(proxy.bias_values):
                return False, "數據維度不匹配"
        
        return True, "數據格式正確"
        
    except Exception as e:
        return False, f"驗證過程錯誤: {e}"

# 使用驗證
proxy = session.get_file_proxy("some_file")
is_valid, message = validate_data_format(proxy)
print(f"數據驗證: {message}")
```

### 效能問題診斷

#### 載入效能分析
```python
import time

def profile_loading_performance(session, file_keys):
    """分析檔案載入效能"""
    results = {}
    
    for file_key in file_keys:
        start_time = time.time()
        
        # 載入檔案
        proxy = session.get_file_proxy(file_key)
        load_time = time.time() - start_time
        
        # 分析檔案
        start_analysis = time.time()
        result = proxy.analyzer.analyze()
        analysis_time = time.time() - start_analysis
        
        file_size = proxy.file_info.size
        results[file_key] = {
            'load_time': load_time,
            'analysis_time': analysis_time,
            'file_size': file_size,
            'load_speed': file_size / load_time / 1e6,  # MB/s
            'success': result['success']
        }
    
    return results

# 使用效能分析
topo_files = session.get_topo_files()[:5]
perf_results = profile_loading_performance(session, topo_files)

for file_key, stats in perf_results.items():
    print(f"{file_key}:")
    print(f"  載入時間: {stats['load_time']:.2f}s")
    print(f"  分析時間: {stats['analysis_time']:.2f}s") 
    print(f"  載入速度: {stats['load_speed']:.1f} MB/s")
```

## 效能最佳化 / Performance Optimization

### 記憶體管理策略

#### 智能快取配置
```python
def optimize_cache_settings(session, target_memory_gb=4):
    """根據目標記憶體使用量最佳化快取設定"""
    target_bytes = target_memory_gb * 1e9
    
    # 估算每個檔案類型的平均大小
    avg_sizes = {}
    for manager_name in ['txt', 'topo', 'cits', 'sts']:
        manager = getattr(session, manager_name)
        files = manager.get_files()
        
        if files:
            total_size = sum(f.size for f in files.values())
            avg_sizes[manager_name] = total_size / len(files)
        else:
            avg_sizes[manager_name] = 1e6  # 預設 1MB
    
    # 根據檔案大小分配快取
    total_avg_size = sum(avg_sizes.values())
    
    for manager_name in ['txt', 'topo', 'cits', 'sts']:
        manager = getattr(session, manager_name)
        
        # 按比例分配記憶體
        allocated_memory = target_bytes * (avg_sizes[manager_name] / total_avg_size)
        cache_size = max(1, int(allocated_memory / avg_sizes[manager_name]))
        
        # 設定快取大小（最少1，最多50）
        manager._cache_size = min(50, max(1, cache_size))
        
        print(f"{manager_name} 快取大小: {manager._cache_size}")

# 應用最佳化
optimize_cache_settings(session, target_memory_gb=2)
```

#### 載入策略最佳化
```python
def lazy_loading_strategy(session, analysis_type='basic'):
    """延遲載入策略"""
    
    if analysis_type == 'basic':
        # 基本分析：只載入第一個檔案
        for file_type in ['topo', 'cits']:
            manager = getattr(session, file_type)
            files = list(manager.get_files().keys())
            if files:
                proxy = session.get_file_proxy(files[0])
                proxy.analyzer.analyze()
                
    elif analysis_type == 'comprehensive':
        # 全面分析：批次載入，用完即卸載
        for file_type in ['topo', 'cits']:
            manager = getattr(session, file_type)
            files = list(manager.get_files().keys())
            
            for i, file_key in enumerate(files):
                proxy = session.get_file_proxy(file_key)
                proxy.analyzer.analyze()
                
                # 每處理5個檔案，清理一次快取
                if i % 5 == 4:
                    manager.clear_cache()
```

### 並行處理

#### 多執行緒分析
```python
import concurrent.futures
from threading import Lock

class ParallelAnalyzer:
    """並行分析器"""
    
    def __init__(self, session, max_workers=4):
        self.session = session
        self.max_workers = max_workers
        self.results_lock = Lock()
        self.results = {}
    
    def analyze_files_parallel(self, file_keys, analysis_func):
        """並行分析檔案"""
        
        def worker(file_key):
            try:
                proxy = self.session.get_file_proxy(file_key)
                result = analysis_func(proxy)
                
                with self.results_lock:
                    self.results[file_key] = result
                    
                return file_key, True
                
            except Exception as e:
                print(f"分析 {file_key} 失敗: {e}")
                return file_key, False
        
        # 使用執行緒池
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(worker, key) for key in file_keys]
            
            for future in concurrent.futures.as_completed(futures):
                file_key, success = future.result()
                print(f"{'✅' if success else '❌'} {file_key}")
        
        return self.results

# 使用並行分析
def basic_topo_analysis(proxy):
    """基本拓撲分析函數"""
    result = proxy.analyzer.analyze()
    flatten_result = proxy.analyzer.apply_flattening(method='polynomial', order=2)
    return {
        'basic': result,
        'flattened': flatten_result
    }

# 執行並行分析
parallel_analyzer = ParallelAnalyzer(session, max_workers=3)
topo_files = session.get_topo_files()[:10]  # 前10個檔案
results = parallel_analyzer.analyze_files_parallel(topo_files, basic_topo_analysis)
```

---

**作者 / Author**: Odindino  
**最後更新 / Last Updated**: 2025-06-07  
**版本 / Version**: 2.0 Complete Edition

這份完整手冊提供了 KEEN 後端架構的所有詳細資訊，包括完整的 API 參考、使用方法、進階功能和效能最佳化策略。如有問題或需要進一步說明，請聯繫開發團隊。

For questions or further clarification, please contact the development team.