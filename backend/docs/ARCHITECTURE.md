# SPM 數據分析框架架構設計文件

## 目錄
1. [概述](#概述)
2. [核心理念](#核心理念)
3. [架構層次](#架構層次)
4. [分層設計詳解](#分層設計詳解)
5. [記憶體與性能優化](#記憶體與性能優化)
6. [開發指南](#開發指南)
7. [測試策略](#測試策略)
8. [API 設計規範](#api-設計規範)
9. [擴展指南](#擴展指南)
10. [部署與維護](#部署與維護)

## 概述

本框架基於「廚房分工」的概念設計，將 SPM（掃描探針顯微鏡）數據分析拆分為多個專門的組件，實現高效、可擴展、可測試的數據處理系統。

### 核心目標
- **模組化設計**：清晰的職責分離，易於維護和擴展
- **高性能**：智能快取和記憶體管理，避免重複計算
- **可測試性**：每個組件都可以獨立測試
- **可重用性**：基礎功能可在不同場景中重複使用
- **專業化**：針對 SPM 數據特性的專門優化
- **國際化**：支援多語言開發環境，程式碼註解和文件提供正體中文和英文版本
- **多平台支援**：目前主要支援 Anfatec Instruments AG SXM 系統，未來計劃擴展支援 Nanonis、Bruker、Asylum(Oxford)、Park System 等主流 SPM 系統

### 多語言支援說明

為確保國際化開發和維護，本專案採用雙語言支援策略：

#### 程式碼註解規範
- **類別和函數文檔字串**：提供正體中文和英文版本
- **重要註解**：關鍵邏輯和算法使用雙語註解
- **變數命名**：使用英文命名，配合中文註解說明

#### 文件國際化
- **架構文件**：提供正體中文版 (ARCHITECTURE.md) 和英文版 (ARCHITECTURE_EN.md)
- **API 文件**：雙語言說明
- **使用手冊**：支援多語言版本

#### 範例格式
```python
class SPMAnalyzer:
    """
    SPM 數據分析器主類別
    Main SPM data analyzer class
    
    這個類別負責協調所有的 SPM 數據分析流程
    This class coordinates all SPM data analysis workflows
    """
    
    def analyze_data(self, data: np.ndarray) -> AnalysisResult:
        """
        分析 SPM 數據
        Analyze SPM data
        
        Args:
            data: SPM 原始數據矩陣 / Raw SPM data matrix
            
        Returns:
            分析結果 / Analysis results
        """
        # 數據預處理 / Data preprocessing
        processed_data = self._preprocess(data)
        
        # 執行主要分析 / Execute main analysis
        result = self._main_analysis(processed_data)
        
        return result
```

## 核心理念

### 分工比喻：廚房管理模式
- **總廚（AnalyzerManager）**：管理整個專案，協調多個數據集
- **主廚（MainAnalyzer）**：負責單一數據集的整體分析流程
- **專門廚師（SubAnalyzers）**：各司其職的專門分析器
- **廚具（Mathematics/Utils）**：共享的工具和基礎功能
- **擺盤師（Visualization）**：專門的數據視覺化
- **食材（Data）**：原始和處理後的數據
- **食譜（Analysis Methods）**：可重用的分析方法

### 設計原則
1. **單一責任原則**：每個組件專注於特定功能
2. **依賴注入**：組件間通過接口交互，降低耦合
3. **開放封閉原則**：對擴展開放，對修改封閉
4. **組合優於繼承**：通過組合實現功能複用
5. **純函數優先**：優先使用無副作用的純函數

## 架構層次

```
Backend Architecture:
├── core/                           # 核心層
│   ├── __init__.py
│   ├── analysis_service.py         # 主要服務入口
│   ├── main_analyzer.py           # 主分析器
│   │
│   ├── analyzers/                 # 分析器層（狀態管理 + 工作流協調）
│   │   ├── __init__.py
│   │   ├── base_analyzer.py       # 分析器基類
│   │   ├── txt_analyzer.py        # TXT 檔案分析器
│   │   ├── int_analyzer.py        # INT 影像分析器
│   │   ├── dat_analyzer.py        # DAT 數據分析器
│   │   ├── cits_analyzer.py       # CITS 專門分析器
│   │   ├── sts_analyzer.py        # STS 專門分析器
│   │   └── fft_analyzer.py        # FFT 分析器（未來擴展）
│   │
│   ├── analysis/                  # 分析方法層（純業務邏輯）
│   │   ├── __init__.py
│   │   ├── txt_analysis.py        # TXT 分析方法
│   │   ├── int_analysis.py        # INT 分析方法
│   │   ├── dat_analysis.py        # DAT 分析方法
│   │   ├── cits_analysis.py       # CITS 分析方法
│   │   ├── sts_analysis.py        # STS 分析方法
│   │   └── fft_analysis.py        # FFT 分析方法
│   │
│   ├── mathematics/               # 數學運算庫（純數學函數）
│   │   ├── __init__.py
│   │   ├── geometry.py           # 幾何運算（Bresenham、插值等）
│   │   ├── transformations.py    # 座標變換（旋轉、平移、縮放）
│   │   ├── signal_processing.py  # 信號處理（濾波、峰值檢測等）
│   │   └── statistics.py         # 統計分析
│   │
│   ├── visualization/             # 視覺化庫（繪圖方法）
│   │   ├── __init__.py
│   │   ├── spm_plots.py          # SPM 專用繪圖
│   │   ├── spectroscopy_plots.py # 光譜繪圖
│   │   ├── analysis_plots.py     # 分析結果繪圖
│   │   └── interactive_plots.py  # 互動式繪圖
│   │
│   ├── parsers/                   # 檔案解析器
│   │   ├── __init__.py
│   │   ├── txt_parser.py         # TXT 檔案解析
│   │   ├── int_parser.py         # INT 檔案解析
│   │   └── dat_parser.py         # DAT 檔案解析
│   │
│   └── utils/                     # 工具函數
│       ├── __init__.py
│       ├── cache_manager.py      # 快取管理
│       ├── memory_manager.py     # 記憶體管理
│       ├── data_structures.py    # 數據結構定義
│       ├── file_utils.py         # 檔案操作工具
│       └── config.py             # 配置管理
```

## 分層設計詳解

### 1. Core 層 - 核心協調

**主要組件**：
- `AnalysisService`：整個系統的入口點
- `MainAnalyzer`：單一數據集的主要協調器

**職責**：
- 提供統一的 API 接口
- 協調各個子系統
- 管理分析生命週期

```python
# 使用範例
from core.analysis_service import AnalysisService

service = AnalysisService()
analyzer = service.create_analyzer("path/to/experiment.txt")
result = analyzer.analyze_file("data.dat")
```

### 2. Analyzers 層 - 狀態管理與工作流

**設計特點**：
- 維護分析狀態和歷史
- 管理數據快取
- 協調下層組件完成複雜任務
- 提供高級 API

**基類設計**：
```python
class BaseAnalyzer:
    def __init__(self, main_analyzer: 'MainAnalyzer'):
        self.main_analyzer = main_analyzer
        self.cache = CacheManager()
        self.state = {}
    
    @abstractmethod
    def analyze(self, data: Any) -> AnalysisResult:
        """核心分析方法"""
        pass
    
    def get_results(self) -> Dict[str, Any]:
        """獲取分析結果"""
        return self.state.get('results', {})
    
    def clear_cache(self) -> None:
        """清理快取"""
        self.cache.clear()
```

### 3. Analysis 層 - 純業務邏輯

**設計原則**：
- 純函數設計，無狀態
- 專注於核心算法實現
- 可獨立測試和使用
- 高度可組合

**範例設計**：
```python
class CITSAnalysis:
    @staticmethod
    def extract_line_spectra(data_3d: np.ndarray, 
                           start_pixel: tuple, 
                           end_pixel: tuple,
                           params: AnalysisParams) -> AnalysisResult:
        """提取線段光譜（純函數）"""
        # 使用 mathematics 層的工具
        from mathematics.geometry import GeometryUtils
        
        pixel_points = GeometryUtils.bresenham_line(start_pixel, end_pixel)
        # ... 算法實現
        
        return AnalysisResult(
            success=True,
            data={'spectra': spectra, 'positions': positions},
            metadata={'method': 'bresenham', 'num_points': len(pixel_points)}
        )
```

### 4. Mathematics 層 - 純數學運算

**設計特點**：
- 無依賴的純數學函數
- 高性能實現（可使用 Numba 加速）
- 完整的單元測試覆蓋
- 豐富的文檔說明

**主要模組**：

#### geometry.py - 幾何運算
```python
class GeometryUtils:
    @staticmethod
    @numba.jit(nopython=True)  # 性能優化
    def bresenham_line(start: tuple, end: tuple) -> List[tuple]:
        """Bresenham 直線算法"""
        
    @staticmethod
    def wu_line(start: tuple, end: tuple) -> List[tuple]:
        """Wu's 抗鋸齒線段算法"""
        
    @staticmethod
    def interpolate_line_points(start: tuple, end: tuple, 
                               num_points: int, 
                               method: str = 'linear') -> np.ndarray:
        """線段插值點生成"""
```

#### transformations.py - 座標變換
```python
class CoordinateTransforms:
    @staticmethod
    def rotate_point(point: tuple, angle: float, 
                    center: tuple = (0, 0)) -> tuple:
        """點旋轉變換"""
        
    @staticmethod
    def translate_points(points: np.ndarray, offset: tuple) -> np.ndarray:
        """點集平移"""
        
    @staticmethod
    def scale_points(points: np.ndarray, scale: tuple, 
                    center: tuple = (0, 0)) -> np.ndarray:
        """點集縮放"""
        
    @staticmethod
    def pixel_to_physical(pixel_coords: tuple, 
                         origin: tuple, 
                         scale: float) -> tuple:
        """像素座標轉物理座標"""
```

### 5. Visualization 層 - 專業視覺化

**設計理念**：
- 標準化的 SPM 數據視覺化
- 可配置的繪圖參數
- 支援互動式繪圖
- 一致的視覺風格

**主要模組**：

#### spm_plots.py - SPM 專用繪圖
```python
class SPMPlotting:
    @staticmethod
    def plot_topography(image_data: np.ndarray,
                       physical_scale: tuple = None,
                       title: str = None,
                       **kwargs) -> plt.Figure:
        """STM/AFM 地形圖標準繪製"""
        
    @staticmethod
    def plot_line_profile(distances: np.ndarray, 
                         values: np.ndarray,
                         **kwargs) -> plt.Figure:
        """線段剖面圖"""
        
    @staticmethod
    def plot_height_distribution(image_data: np.ndarray,
                                **kwargs) -> plt.Figure:
        """高度分佈直方圖"""
```

#### spectroscopy_plots.py - 光譜繪圖
```python
class SpectroscopyPlotting:
    @staticmethod
    def plot_sts_spectrum(bias: np.ndarray, 
                         current: np.ndarray,
                         conductance: np.ndarray = None,
                         **kwargs) -> plt.Figure:
        """STS 光譜標準繪製"""
        
    @staticmethod
    def plot_cits_overview(data_3d: np.ndarray, 
                          bias_values: np.ndarray,
                          selected_biases: List[float] = None,
                          **kwargs) -> plt.Figure:
        """CITS 多偏壓概覽圖"""
```

## 記憶體與性能優化

### 1. 智能快取系統

```python
class CacheManager:
    """階層式快取管理"""
    
    def __init__(self, max_memory_mb: int = 1000):
        self.max_memory = max_memory_mb * 1024 * 1024
        self.cache_levels = {
            'hot': {},      # 頻繁訪問的數據
            'warm': {},     # 中等頻率數據
            'cold': {}      # 低頻率數據
        }
        self.access_count = defaultdict(int)
        self.memory_usage = 0
    
    def get_or_compute(self, key: str, compute_func: Callable, 
                      *args, **kwargs) -> Any:
        """獲取或計算數據"""
        # 檢查各級快取
        for level in ['hot', 'warm', 'cold']:
            if key in self.cache_levels[level]:
                self._promote_data(key, level)
                return self.cache_levels[level][key]
        
        # 計算新數據
        result = compute_func(*args, **kwargs)
        self._store_data(key, result)
        return result
    
    def _promote_data(self, key: str, current_level: str):
        """數據提升策略"""
        self.access_count[key] += 1
        
        # 根據訪問頻率調整快取級別
        if self.access_count[key] > 10 and current_level != 'hot':
            data = self.cache_levels[current_level].pop(key)
            self.cache_levels['hot'][key] = data
```

### 2. 惰性計算與數據視圖

```python
class LazyDataView:
    """惰性數據視圖，避免不必要的記憶體複製"""
    
    def __init__(self, data_source: Any, transform_chain: List = None):
        self.data_source = data_source
        self.transform_chain = transform_chain or []
        self._computed_result = None
        self._is_computed = False
    
    def apply_transform(self, transform_func: Callable, 
                       *args, **kwargs) -> 'LazyDataView':
        """添加變換而不立即計算"""
        new_chain = self.transform_chain + [(transform_func, args, kwargs)]
        return LazyDataView(self.data_source, new_chain)
    
    def compute(self) -> Any:
        """只在需要時才計算"""
        if not self._is_computed:
            result = self.data_source
            for func, args, kwargs in self.transform_chain:
                result = func(result, *args, **kwargs)
            self._computed_result = result
            self._is_computed = True
        return self._computed_result
    
    @property
    def shape(self):
        """提供形狀訊息而不觸發計算"""
        # 實現形狀推斷邏輯
        pass
```

### 3. 記憶體監控與管理

```python
class MemoryManager:
    """記憶體使用監控與管理"""
    
    def __init__(self, warning_threshold: float = 0.8, 
                 critical_threshold: float = 0.9):
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold
        self.monitored_objects = weakref.WeakSet()
    
    def register_object(self, obj: Any):
        """註冊需要監控的對象"""
        self.monitored_objects.add(obj)
    
    def check_memory_usage(self) -> MemoryStatus:
        """檢查記憶體使用狀況"""
        process = psutil.Process()
        memory_percent = process.memory_percent()
        
        status = MemoryStatus(
            usage_percent=memory_percent,
            total_mb=process.memory_info().rss / 1024 / 1024,
            is_warning=memory_percent > self.warning_threshold * 100,
            is_critical=memory_percent > self.critical_threshold * 100
        )
        
        if status.is_critical:
            self._emergency_cleanup()
        elif status.is_warning:
            self._gentle_cleanup()
        
        return status
    
    def _emergency_cleanup(self):
        """緊急記憶體清理"""
        for obj in self.monitored_objects:
            if hasattr(obj, 'clear_cache'):
                obj.clear_cache()
        gc.collect()
```

## 開發指南

### 1. 新 Analyzer 開發流程

#### 步驟 1：創建 Analysis 方法
```python
# core/analysis/new_analysis.py
class NewAnalysis:
    @staticmethod
    def core_algorithm(data: np.ndarray, params: Dict) -> AnalysisResult:
        """核心算法實現（純函數）"""
        # 1. 使用 mathematics 層的工具
        # 2. 實現核心邏輯
        # 3. 返回標準化結果
        pass
```

#### 步驟 2：創建 Analyzer 包裝
```python
# core/analyzers/new_analyzer.py
class NewAnalyzer(BaseAnalyzer):
    def __init__(self, main_analyzer):
        super().__init__(main_analyzer)
        self.analysis_history = []
    
    def analyze_data(self, **kwargs) -> AnalysisResult:
        """狀態管理 + 調用 Analysis 方法"""
        # 1. 參數驗證
        # 2. 快取檢查
        # 3. 調用純函數
        # 4. 狀態更新
        # 5. 結果快取
        pass
```

#### 步驟 3：註冊到 MainAnalyzer
```python
# core/main_analyzer.py
class MainAnalyzer:
    def _initialize_analyzers(self):
        self.analyzers = {
            'txt': TxtAnalyzer(self),
            'int': IntAnalyzer(self),
            'dat': DatAnalyzer(self),
            'cits': CITSAnalyzer(self),
            'sts': STSAnalyzer(self),
            'new': NewAnalyzer(self),  # 新增
        }
```

### 2. 新數學函數開發

```python
# core/mathematics/new_math.py
class NewMathUtils:
    @staticmethod
    @numba.jit(nopython=True, cache=True)  # 性能優化
    def advanced_algorithm(data: np.ndarray, 
                          param1: float, 
                          param2: int) -> np.ndarray:
        """
        高級算法實現
        
        Parameters:
        -----------
        data : np.ndarray
            輸入數據
        param1 : float
            參數說明
        param2 : int
            參數說明
            
        Returns:
        --------
        np.ndarray
            處理結果
            
        Examples:
        ---------
        >>> result = NewMathUtils.advanced_algorithm(data, 1.0, 5)
        """
        # 實現算法邏輯
        pass
```

### 3. 新視覺化功能開發

```python
# core/visualization/new_plots.py
class NewPlotting:
    @staticmethod
    def specialized_plot(data: np.ndarray, 
                        params: Dict = None,
                        **kwargs) -> plt.Figure:
        """
        專門繪圖功能
        
        Parameters:
        -----------
        data : np.ndarray
            繪圖數據
        params : Dict, optional
            繪圖參數
        **kwargs
            額外的 matplotlib 參數
            
        Returns:
        --------
        plt.Figure
            圖形對象
        """
        fig, ax = plt.subplots(figsize=kwargs.get('figsize', (10, 6)))
        
        # 實現繪圖邏輯
        # 確保統一的視覺風格
        
        return fig
```

## 測試策略

### 1. 測試架構

```
test/
├── unit/                    # 單元測試
│   ├── test_mathematics/    # 數學函數測試
│   ├── test_analysis/       # 分析方法測試
│   ├── test_visualization/  # 視覺化測試
│   └── test_utils/         # 工具函數測試
├── integration/            # 集成測試
│   ├── test_analyzers/     # 分析器集成測試
│   └── test_workflows/     # 工作流測試
├── performance/            # 性能測試
└── fixtures/              # 測試數據
    ├── sample_data/
    └── mock_objects/
```

### 2. 測試範例

#### 單元測試：純函數測試
```python
# test/unit/test_mathematics/test_geometry.py
import pytest
import numpy as np
from core.mathematics.geometry import GeometryUtils

class TestGeometryUtils:
    def test_bresenham_line_basic(self):
        """測試基本 Bresenham 算法"""
        points = GeometryUtils.bresenham_line((0, 0), (3, 3))
        expected = [(0, 0), (1, 1), (2, 2), (3, 3)]
        assert points == expected
    
    def test_bresenham_line_steep(self):
        """測試陡峭線段"""
        points = GeometryUtils.bresenham_line((0, 0), (1, 3))
        assert len(points) == 4
        assert points[0] == (0, 0)
        assert points[-1] == (1, 3)
    
    @pytest.mark.parametrize("start,end", [
        ((0, 0), (10, 5)),
        ((5, 5), (0, 0)),
        ((-1, -1), (1, 1)),
    ])
    def test_bresenham_various_cases(self, start, end):
        """測試各種情況"""
        points = GeometryUtils.bresenham_line(start, end)
        assert isinstance(points, list)
        assert len(points) > 0
        assert points[0] == start
        assert points[-1] == end
```

#### 集成測試：Analyzer 測試
```python
# test/integration/test_analyzers/test_cits_analyzer.py
import pytest
from core.main_analyzer import MainAnalyzer
from test.fixtures.sample_data import create_mock_cits_data

class TestCITSAnalyzer:
    @pytest.fixture
    def analyzer(self):
        """創建測試用的分析器"""
        main_analyzer = MainAnalyzer()
        main_analyzer._test_mode = True  # 測試模式
        main_analyzer.load_mock_data(create_mock_cits_data())
        return main_analyzer.get_analyzer('cits')
    
    def test_line_profile_extraction(self, analyzer):
        """測試線段剖面提取"""
        result = analyzer.extract_line_profile((0, 0), (10, 10))
        
        assert result.success
        assert 'spectra' in result.data
        assert 'positions' in result.data
        assert len(result.data['spectra']) > 0
    
    def test_caching_behavior(self, analyzer):
        """測試快取行為"""
        # 第一次調用
        result1 = analyzer.extract_line_profile((0, 0), (5, 5))
        cache_size_before = len(analyzer.cache.cache_levels['hot'])
        
        # 第二次相同調用
        result2 = analyzer.extract_line_profile((0, 0), (5, 5))
        cache_size_after = len(analyzer.cache.cache_levels['hot'])
        
        # 驗證快取行為
        assert cache_size_after >= cache_size_before
        np.testing.assert_array_equal(result1.data['spectra'], 
                                     result2.data['spectra'])
```

#### 性能測試
```python
# test/performance/test_performance.py
import time
import pytest
from core.mathematics.geometry import GeometryUtils

class TestPerformance:
    def test_bresenham_performance(self):
        """測試 Bresenham 算法性能"""
        start_time = time.time()
        
        for _ in range(1000):
            GeometryUtils.bresenham_line((0, 0), (100, 100))
        
        elapsed = time.time() - start_time
        assert elapsed < 1.0  # 應該在 1 秒內完成 1000 次調用
    
    @pytest.mark.memory
    def test_memory_usage(self):
        """測試記憶體使用量"""
        import psutil
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        # 執行記憶體密集操作
        large_data = np.random.rand(1000, 1000, 100)
        result = SomeAnalysis.process_large_data(large_data)
        
        peak_memory = process.memory_info().rss
        memory_increase = (peak_memory - initial_memory) / 1024 / 1024  # MB
        
        # 記憶體增長應該合理
        assert memory_increase < 500  # 不應超過 500MB
```

## API 設計規範

### 1. 統一結果格式

```python
@dataclass
class AnalysisResult:
    """標準分析結果格式"""
    success: bool
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    processing_time: float = 0.0
    
    def to_dict(self) -> Dict:
        """轉換為字典格式"""
        return asdict(self)
    
    def save(self, filepath: str):
        """保存結果到檔案"""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
```

### 2. 參數類別定義

```python
@dataclass
class AnalysisParams:
    """標準分析參數"""
    method: str = 'default'
    num_points: Optional[int] = None
    interpolation: str = 'linear'
    smoothing: bool = False
    smoothing_factor: float = 1.0
    
    def validate(self) -> List[str]:
        """參數驗證"""
        errors = []
        if self.num_points is not None and self.num_points <= 0:
            errors.append("num_points must be positive")
        return errors

@dataclass
class PlotParams:
    """標準繪圖參數"""
    figsize: tuple = (10, 6)
    dpi: int = 100
    style: str = 'default'
    colormap: str = 'viridis'
    show_colorbar: bool = True
    title: Optional[str] = None
```

### 3. 錯誤處理標準

```python
class SPMAnalysisError(Exception):
    """SPM 分析基礎錯誤類"""
    pass

class DataFormatError(SPMAnalysisError):
    """數據格式錯誤"""
    pass

class AnalysisParameterError(SPMAnalysisError):
    """分析參數錯誤"""
    pass

class InsufficientDataError(SPMAnalysisError):
    """數據不足錯誤"""
    pass

# 使用範例
def safe_analysis_wrapper(func):
    """分析方法的安全包裝器"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return AnalysisResult(
                success=False,
                data={},
                metadata={},
                errors=[str(e)]
            )
    return wrapper
```

## 擴展指南

### 1. 添加新的數據類型支援

#### 步驟 1：創建解析器
```python
# core/parsers/new_format_parser.py
class NewFormatParser:
    @staticmethod
    def parse(filepath: str) -> Dict[str, Any]:
        """解析新格式檔案"""
        pass
    
    @staticmethod
    def validate(filepath: str) -> bool:
        """驗證檔案格式"""
        pass
```

#### 步驟 2：創建分析方法
```python
# core/analysis/new_format_analysis.py
class NewFormatAnalysis:
    @staticmethod
    def process_data(data: Dict, params: AnalysisParams) -> AnalysisResult:
        """處理新格式數據"""
        pass
```

#### 步驟 3：創建分析器
```python
# core/analyzers/new_format_analyzer.py
class NewFormatAnalyzer(BaseAnalyzer):
    def analyze(self, filepath: str) -> AnalysisResult:
        """分析新格式檔案"""
        pass
```

### 2. 添加新的分析算法

```python
# core/mathematics/advanced_algorithms.py
class AdvancedAlgorithms:
    @staticmethod
    @numba.jit(nopython=True)
    def new_algorithm(data: np.ndarray, **params) -> np.ndarray:
        """新的高級算法"""
        pass
    
    @staticmethod
    def algorithm_with_validation(data: np.ndarray, **params) -> AnalysisResult:
        """帶驗證的算法包裝"""
        # 參數驗證
        # 調用核心算法
        # 結果驗證
        pass
```

### 3. 自定義視覺化

```python
# core/visualization/custom_plots.py
class CustomPlotting:
    @staticmethod
    def create_dashboard(analyzers: List[BaseAnalyzer], 
                        **kwargs) -> plt.Figure:
        """創建分析儀表板"""
        pass
    
    @staticmethod
    def interactive_explorer(data_3d: np.ndarray) -> Any:
        """互動式數據探索器"""
        # 使用 plotly 或 bokeh 創建互動圖表
        pass
```

## 部署與維護

### 1. 環境配置

#### Conda 環境配置 (environment.yml)
```yaml
# environment.yml
name: keen
channels:
  - conda-forge
  - defaults
  - anaconda
dependencies:
  - python>=3.12
  - numpy>=1.24.0
  - plotly>=5.17.0
  - scipy>=1.10.0
  - matplotlib>=3.7.0
  - pandas>=2.0.0
  - pip
  - pip:
    # 開發工具 (可選，需要時取消註解)
    - pytest>=7.4.0
    - black>=23.0.0
    - flake8>=6.0.0

    # jupyter notebook 支持
    - jupyterlab>=4.0.0
    - ipykernel>=6.20.0
```

#### Pip 額外依賴 (requirements.txt)
```pip-requirements
pywebview>=4.4.0
```

#### 環境設置指令
```bash
# 創建 conda 環境
conda env create -f environment.yml

# 激活環境
conda activate keen

# 安裝額外依賴
pip install -r requirements.txt

# 開發模式安裝 (可選)
pip install -e .
```

### 2. 性能監控

```python
# core/utils/performance_monitor.py
class PerformanceMonitor:
    def __init__(self):
        self.metrics = defaultdict(list)
    
    @contextmanager
    def measure(self, operation_name: str):
        """測量操作性能"""
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss
        
        try:
            yield
        finally:
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss
            
            self.metrics[operation_name].append({
                'duration': end_time - start_time,
                'memory_delta': end_memory - start_memory,
                'timestamp': datetime.now()
            })
    
    def get_report(self) -> Dict:
        """獲取性能報告"""
        report = {}
        for operation, measurements in self.metrics.items():
            durations = [m['duration'] for m in measurements]
            memory_deltas = [m['memory_delta'] for m in measurements]
            
            report[operation] = {
                'count': len(measurements),
                'avg_duration': np.mean(durations),
                'max_duration': np.max(durations),
                'avg_memory_delta': np.mean(memory_deltas),
                'max_memory_delta': np.max(memory_deltas)
            }
        
        return report
```

### 3. 配置管理

```python
# core/utils/config.py
@dataclass
class SystemConfig:
    """系統配置"""
    max_memory_mb: int = 1000
    cache_size_mb: int = 500
    num_workers: int = 4
    temp_dir: str = "/tmp/spm_analysis"
    log_level: str = "INFO"
    
    @classmethod
    def from_file(cls, filepath: str) -> 'SystemConfig':
        """從檔案載入配置"""
        with open(filepath, 'r') as f:
            config_dict = json.load(f)
        return cls(**config_dict)
    
    def save(self, filepath: str):
        """保存配置到檔案"""
        with open(filepath, 'w') as f:
            json.dump(asdict(self), f, indent=2)
```

### 4. 日誌系統

```python
# core/utils/logging_config.py
import logging
from datetime import datetime

def setup_logging(config: SystemConfig):
    """設置日誌系統"""
    
    # 創建自定義格式器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 檔案處理器
    file_handler = logging.FileHandler(
        f'spm_analysis_{datetime.now().strftime("%Y%m%d")}.log'
    )
    file_handler.setFormatter(formatter)
    
    # 控制台處理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # 設置根日誌器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, config.log_level))
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    return root_logger
```

## 最佳實踐

### 1. 代碼風格
- 遵循 PEP 8 標準
- 使用類型提示 (Type Hints)
- 編寫清晰的文檔字符串
- 保持函數簡潔 (< 50 行)

### 2. 性能優化
- 優先使用 NumPy 向量化操作
- 合理使用 Numba JIT 編譯
- 實施智能快取策略
- 監控記憶體使用量

### 3. 錯誤處理
- 使用具體的異常類型
- 提供有用的錯誤訊息
- 實施優雅的錯誤恢復
- 記錄所有錯誤事件

### 4. 測試覆蓋
- 單元測試覆蓋率 > 90%
- 包含邊界條件測試
- 實施性能回歸測試
- 定期進行集成測試

---

## 總結

## 結論

本架構設計提供了一個可持續、可擴展的 SPM 數據分析解決方案。通過清晰的職責分離、智能的資源管理和完善的測試策略，確保系統在處理複雜 SPM 數據時既高效又可靠。

### 開發路線圖

1. **實施核心基礎架構**
   - 基本分析器框架
   - 數學庫基礎
   - 快取系統

2. **創建基本的測試套件**
   - 數學函數單元測試
   - 分析器集成測試
   - 性能基準測試

3. **開發專門分析器**
   - CITS 分析器
   - STS 分析器
   - 地形分析器

4. **增強視覺化功能**
   - 互動式繪圖
   - 分析儀表板
   - 匯出功能

5. **優化和部署**
   - 性能調優
   - 記憶體優化
   - 生產部署

### 國際化開發支援

本框架特別注重國際化開發環境：

#### 文件語言支援
- **架構文件**：提供 [正體中文版](ARCHITECTURE.md) 和 [英文版](ARCHITECTURE_EN.md)
- **API 文件**：所有公開 API 都有雙語描述
- **開發指南**：提供詳細的 [雙語言開發規範](DEVELOPER_GUIDE.md)

#### 程式碼國際化
- **函數與類別**：所有公開接口都有中英文文檔字串
- **註解標準**：重要邏輯使用雙語註解，參考 [程式碼範例](core/examples/bilingual_code_example.py)
- **錯誤訊息**：提供多語言錯誤描述

#### 開發者資源
- **[開發者指南](DEVELOPER_GUIDE.md)**：詳細的雙語言開發規範和最佳實踐
- **[程式碼範例](core/examples/bilingual_code_example.py)**：展示如何撰寫符合規範的雙語註解
- **貢獻流程**：支援不同語言背景的開發者參與

這種設計確保無論開發者的語言背景如何，都能有效參與專案的開發和維護工作。

開發者應按照本文件的指導原則進行開發，確保系統的一致性和可維護性。隨著需求的變化，可以通過添加新的分析器、數學函數或視覺化組件來擴展系統功能。

**下一步行動**：
1. 實施核心基礎架構
2. 創建基本的測試套件
3. 實現第一個完整的分析器
4. 建立 CI/CD 流程
5. 完善文檔和使用範例
