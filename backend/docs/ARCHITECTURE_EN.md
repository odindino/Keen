# SPM Data Analysis Framework Architecture Document

## Table of Contents
1. [Overview](#overview)
2. [Core Philosophy](#core-philosophy)
3. [Architecture Layers](#architecture-layers)
4. [Layer Design Details](#layer-design-details)
5. [Memory and Performance Optimization](#memory-and-performance-optimization)
6. [Development Guide](#development-guide)
7. [Testing Strategy](#testing-strategy)
8. [API Design Standards](#api-design-standards)
9. [Extension Guide](#extension-guide)
10. [Deployment and Maintenance](#deployment-and-maintenance)

## Overview

This framework is designed based on the "kitchen division of labor" concept, breaking down SPM (Scanning Probe Microscopy) data analysis into multiple specialized components to achieve efficient, scalable, and testable data processing systems.

### Core Objectives
- **Modular Design**: Clear separation of responsibilities, easy to maintain and extend
- **High Performance**: Intelligent caching and memory management, avoiding redundant calculations
- **Testability**: Each component can be independently tested
- **Reusability**: Basic functions can be reused in different scenarios
- **Specialization**: Specialized optimization for SPM data characteristics
- **Internationalization**: Multi-language development environment support with bilingual code comments and documentation
- **Multi-platform Support**: Currently primarily supports Anfatec Instruments AG SXM systems, with future plans to expand support for Nanonis, Bruker, Asylum(Oxford), Park System and other mainstream SPM systems

### Multi-language Support

To ensure international development and maintenance, this project adopts a bilingual support strategy:

#### Code Comment Standards
- **Class and Function Docstrings**: Provide both Traditional Chinese and English versions
- **Important Comments**: Critical logic and algorithms use bilingual comments
- **Variable Naming**: Use English naming with Chinese comment explanations

#### Documentation Internationalization
- **Architecture Documents**: Provide Traditional Chinese version (ARCHITECTURE.md) and English version (ARCHITECTURE_EN.md)
- **API Documentation**: Bilingual descriptions
- **User Manuals**: Multi-language version support

#### Example Format
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

## Core Philosophy

### Division of Labor Analogy: Kitchen Management Model
- **Head Chef (AnalyzerManager)**: Manages the entire project, coordinates multiple datasets
- **Main Chef (MainAnalyzer)**: Responsible for the overall analysis workflow of a single dataset
- **Specialized Chefs (SubAnalyzers)**: Specialized analyzers with specific roles
- **Kitchen Tools (Mathematics/Utils)**: Shared tools and basic functions
- **Plating Chef (Visualization)**: Specialized data visualization
- **Ingredients (Data)**: Raw and processed data
- **Recipes (Analysis Methods)**: Reusable analysis methods

### Design Principles
1. **Single Responsibility Principle**: Each component focuses on specific functionality
2. **Dependency Injection**: Components interact through interfaces, reducing coupling
3. **Open-Closed Principle**: Open for extension, closed for modification
4. **Composition over Inheritance**: Achieve function reuse through composition
5. **Pure Functions First**: Prioritize side-effect-free pure functions

## Architecture Layers

```
Backend Architecture:
├── core/                           # Core Layer
│   ├── __init__.py
│   ├── analysis_service.py         # Main service entry point
│   ├── main_analyzer.py           # Main analyzer
│   │
│   ├── analyzers/                 # Analyzer Layer (State Management + Workflow Coordination)
│   │   ├── __init__.py
│   │   ├── base_analyzer.py       # Analyzer base class
│   │   ├── txt_analyzer.py        # TXT file analyzer
│   │   ├── int_analyzer.py        # INT image analyzer
│   │   ├── dat_analyzer.py        # DAT data analyzer
│   │   ├── cits_analyzer.py       # CITS specialized analyzer
│   │   ├── sts_analyzer.py        # STS specialized analyzer
│   │   └── fft_analyzer.py        # FFT analyzer (future extension)
│   │
│   ├── analysis/                  # Analysis Method Layer (Pure Business Logic)
│   │   ├── __init__.py
│   │   ├── txt_analysis.py        # TXT analysis methods
│   │   ├── int_analysis.py        # INT analysis methods
│   │   ├── dat_analysis.py        # DAT analysis methods
│   │   ├── cits_analysis.py       # CITS analysis methods
│   │   ├── sts_analysis.py        # STS analysis methods
│   │   └── fft_analysis.py        # FFT analysis methods
│   │
│   ├── mathematics/               # Mathematical Library (Pure Mathematical Functions)
│   │   ├── __init__.py
│   │   ├── geometry.py           # Geometric operations (Bresenham, interpolation, etc.)
│   │   ├── transformations.py    # Coordinate transformations (rotation, translation, scaling)
│   │   ├── signal_processing.py  # Signal processing (filtering, peak detection, etc.)
│   │   └── statistics.py         # Statistical analysis
│   │
│   ├── visualization/             # Visualization Library (Plotting Methods)
│   │   ├── __init__.py
│   │   ├── spm_plots.py          # SPM-specific plotting
│   │   ├── spectroscopy_plots.py # Spectroscopy plotting
│   │   ├── analysis_plots.py     # Analysis result plotting
│   │   └── interactive_plots.py  # Interactive plotting
│   │
│   ├── parsers/                   # File Parsers
│   │   ├── __init__.py
│   │   ├── txt_parser.py         # TXT file parsing
│   │   ├── int_parser.py         # INT file parsing
│   │   └── dat_parser.py         # DAT file parsing
│   │
│   └── utils/                     # Utility Functions
│       ├── __init__.py
│       ├── cache_manager.py      # Cache management
│       ├── memory_manager.py     # Memory management
│       ├── data_structures.py    # Data structure definitions
│       ├── file_utils.py         # File operation tools
│       └── config.py             # Configuration management
```

## Layer Design Details

### 1. Core Layer - Core Coordination

**Main Components**:
- `AnalysisService`: Entry point for the entire system
- `MainAnalyzer`: Main coordinator for a single dataset

**Responsibilities**:
- Provide unified API interfaces
- Coordinate various subsystems
- Manage analysis lifecycle

```python
# Usage Example
from core.analysis_service import AnalysisService

service = AnalysisService()
analyzer = service.create_analyzer("path/to/experiment.txt")
result = analyzer.analyze_file("data.dat")
```

### 2. Analyzers Layer - State Management and Workflow

**Design Features**:
- Maintain analysis state and history
- Manage data caching
- Coordinate lower-layer components to complete complex tasks
- Provide high-level APIs

**Base Class Design**:
```python
class BaseAnalyzer:
    """
    分析器基類
    Base analyzer class
    
    所有專門分析器的共同基礎
    Common foundation for all specialized analyzers
    """
    def __init__(self, main_analyzer: 'MainAnalyzer'):
        self.main_analyzer = main_analyzer
        self.cache = main_analyzer.cache_manager
        self.config = main_analyzer.config
```

### 3. Analysis Layer - Pure Business Logic

**Design Principles**:
- Pure function design, stateless
- Focus on core algorithm implementation
- Independently testable and usable
- Highly composable

**Example Design**:
```python
class CITSAnalysis:
    """
    CITS 數據分析方法
    CITS data analysis methods
    
    純函數實現，無狀態依賴
    Pure function implementation with no state dependencies
    """
    @staticmethod
    def extract_spectra(data: np.ndarray, 
                       positions: List[Tuple[int, int]]) -> Dict[str, Any]:
        """
        提取指定位置的光譜
        Extract spectra at specified positions
        
        Args:
            data: CITS 數據陣列 / CITS data array
            positions: 位置列表 / Position list
            
        Returns:
            包含光譜和元數據的字典 / Dictionary containing spectra and metadata
        """
        # Pure function implementation
        pass
```

### 4. Mathematics Layer - Pure Mathematical Operations

**Design Features**:
- Dependency-free pure mathematical functions
- High-performance implementation (can use Numba acceleration)
- Complete unit test coverage
- Rich documentation

**Main Modules**:

#### geometry.py - Geometric Operations
```python
class GeometryUtils:
    """
    幾何運算工具
    Geometric operation utilities
    """
    @staticmethod
    @numba.jit(nopython=True)
    def bresenham_line(start: Tuple[int, int], 
                      end: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Bresenham 直線算法
        Bresenham line algorithm
        
        高效的像素級直線繪製算法
        Efficient pixel-level line drawing algorithm
        """
        pass
```

#### transformations.py - Coordinate Transformations
```python
class CoordinateTransforms:
    """
    座標變換工具
    Coordinate transformation utilities
    """
    @staticmethod
    def rotate_point(point: Tuple[float, float], 
                    angle: float, 
                    center: Tuple[float, float] = (0, 0)) -> Tuple[float, float]:
        """
        旋轉點座標
        Rotate point coordinates
        
        Args:
            point: 原始點座標 / Original point coordinates
            angle: 旋轉角度（弧度）/ Rotation angle (radians)
            center: 旋轉中心 / Rotation center
            
        Returns:
            旋轉後的座標 / Rotated coordinates
        """
        pass
```

### 5. Visualization Layer - Professional Visualization

**Design Philosophy**:
- Standardized SPM data visualization
- Configurable plotting parameters
- Interactive plotting support
- Consistent visual style

**Main Modules**:

#### spm_plots.py - SPM-specific Plotting
```python
class SPMPlotting:
    """
    SPM 專用繪圖工具
    SPM-specific plotting utilities
    """
    @staticmethod
    def plot_topography(data: np.ndarray, 
                       scan_params: Dict[str, Any],
                       **kwargs) -> plt.Figure:
        """
        繪製地形圖
        Plot topography
        
        Args:
            data: 地形數據 / Topography data
            scan_params: 掃描參數 / Scan parameters
            
        Returns:
            matplotlib 圖形對象 / matplotlib Figure object
        """
        pass
```

## Memory and Performance Optimization

### 1. Intelligent Caching System

```python
class CacheManager:
    """
    階層式快取管理
    Hierarchical cache management
    
    智能管理計算結果快取，避免重複計算
    Intelligently manage computation result caching to avoid redundant calculations
    """
    
    def __init__(self, max_memory_mb: int = 1000):
        self.max_memory = max_memory_mb * 1024 * 1024
        self.cache_levels = {
            'memory': {},  # 記憶體快取 / Memory cache
            'disk': {}     # 磁碟快取 / Disk cache
        }
    
    @lru_cache(maxsize=128)
    def get_cached_result(self, key: str, compute_func: Callable):
        """
        獲取快取結果或執行計算
        Get cached result or execute computation
        """
        if key in self.cache_levels['memory']:
            return self.cache_levels['memory'][key]
        
        result = compute_func()
        self._store_in_cache(key, result)
        return result
```

### 2. Lazy Computation and Data Views

```python
class LazyDataView:
    """
    惰性數據視圖，避免不必要的記憶體複製
    Lazy data view to avoid unnecessary memory copying
    """
    
    def __init__(self, data_source: Union[str, np.ndarray]):
        self.data_source = data_source
        self._loaded_data = None
    
    @property
    def data(self) -> np.ndarray:
        """
        惰性載入數據
        Lazy load data
        """
        if self._loaded_data is None:
            self._loaded_data = self._load_data()
        return self._loaded_data
```

## Development Guide

### 1. New Analyzer Development Workflow

#### Step 1: Create Analysis Methods
```python
# core/analysis/new_analysis.py
class NewAnalysis:
    """
    新分析方法
    New analysis methods
    """
    @staticmethod
    def process_data(data: np.ndarray, 
                    params: Dict[str, Any]) -> AnalysisResult:
        """
        處理數據的核心邏輯
        Core logic for data processing
        """
        pass
```

#### Step 2: Create Analyzer Wrapper
```python
# core/analyzers/new_analyzer.py
class NewAnalyzer(BaseAnalyzer):
    """
    新分析器
    New analyzer
    """
    def __init__(self, main_analyzer):
        super().__init__(main_analyzer)
        self.analysis_methods = NewAnalysis()
    
    def analyze(self, data: np.ndarray) -> AnalysisResult:
        """
        分析入口點
        Analysis entry point
        """
        pass
```

### 2. New Mathematical Function Development

```python
# core/mathematics/new_math.py
class NewMathUtils:
    """
    新數學工具
    New mathematical utilities
    """
    @staticmethod
    @numba.jit(nopython=True)
    def advanced_algorithm(data: np.ndarray, **params) -> np.ndarray:
        """
        高級算法實現
        Advanced algorithm implementation
        
        參數 / Parameters:
        -----------
        data : numpy.ndarray
            輸入數據 / Input data
        **params
            算法參數 / Algorithm parameters
            
        返回 / Returns:
        -------
        numpy.ndarray
            處理結果 / Processing result
        """
        # 實現算法邏輯 / Implement algorithm logic
        pass
```

## Testing Strategy

### 1. Test Architecture

```
test/
├── unit/                    # Unit Tests
│   ├── test_mathematics/    # Mathematical function tests
│   ├── test_analysis/       # Analysis method tests
│   ├── test_visualization/  # Visualization tests
│   └── test_utils/         # Utility function tests
├── integration/            # Integration Tests
│   ├── test_analyzers/     # Analyzer integration tests
│   └── test_workflows/     # Workflow tests
├── performance/            # Performance Tests
└── fixtures/              # Test Data
    ├── sample_data/
    └── mock_objects/
```

### 2. Test Examples

#### Unit Test: Pure Function Testing
```python
# test/unit/test_mathematics/test_geometry.py
import pytest
import numpy as np
from core.mathematics.geometry import GeometryUtils

class TestGeometryUtils:
    """
    幾何工具測試
    Geometry utilities tests
    """
    
    def test_bresenham_line_basic(self):
        """
        測試基本 Bresenham 直線算法
        Test basic Bresenham line algorithm
        """
        start = (0, 0)
        end = (3, 3)
        points = GeometryUtils.bresenham_line(start, end)
        
        expected = [(0, 0), (1, 1), (2, 2), (3, 3)]
        assert points == expected
    
    def test_bresenham_line_edge_cases(self):
        """
        測試邊界情況
        Test edge cases
        """
        # 測試水平線 / Test horizontal line
        points = GeometryUtils.bresenham_line((0, 0), (3, 0))
        assert len(points) == 4
        
        # 測試垂直線 / Test vertical line
        points = GeometryUtils.bresenham_line((0, 0), (0, 3))
        assert len(points) == 4
```

#### Integration Test: Analyzer Testing
```python
# test/integration/test_analyzers/test_cits_analyzer.py
import pytest
from core.main_analyzer import MainAnalyzer
from test.fixtures.sample_data import create_mock_cits_data

class TestCITSAnalyzer:
    """
    CITS 分析器集成測試
    CITS analyzer integration tests
    """
    
    @pytest.fixture
    def main_analyzer(self):
        """
        創建主分析器實例
        Create main analyzer instance
        """
        analyzer = MainAnalyzer()
        analyzer._test_mode = True  # 測試模式 / Test mode
        return analyzer
    
    def test_cits_workflow(self, main_analyzer):
        """
        測試完整的 CITS 分析工作流
        Test complete CITS analysis workflow
        """
        # 創建模擬數據 / Create mock data
        mock_data = create_mock_cits_data()
        
        # 執行分析 / Execute analysis
        result = main_analyzer.cits_analyzer.analyze(mock_data)
        
        # 驗證結果 / Verify results
        assert result.success
        assert 'spectra' in result.data
        assert len(result.data['spectra']) > 0
```

## API Design Standards

### 1. Unified Result Format

```python
@dataclass
class AnalysisResult:
    """
    標準分析結果格式
    Standard analysis result format
    """
    success: bool                           # 成功標誌 / Success flag
    data: Dict[str, Any]                   # 結果數據 / Result data
    metadata: Dict[str, Any]               # 元數據 / Metadata
    errors: List[str] = field(default_factory=list)     # 錯誤列表 / Error list
    warnings: List[str] = field(default_factory=list)   # 警告列表 / Warning list
    processing_time: float = 0.0           # 處理時間 / Processing time
    
    def to_dict(self) -> Dict:
        """
        轉換為字典格式
        Convert to dictionary format
        """
        return asdict(self)
    
    def save(self, filepath: str):
        """
        保存結果到檔案
        Save result to file
        """
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
```

### 2. Parameter Class Definitions

```python
@dataclass
class AnalysisParams:
    """
    標準分析參數
    Standard analysis parameters
    """
    method: str = 'default'                # 分析方法 / Analysis method
    num_points: Optional[int] = None       # 點數 / Number of points
    interpolation: str = 'linear'          # 插值方法 / Interpolation method
    smoothing: bool = False                # 平滑化 / Smoothing
    smoothing_factor: float = 1.0          # 平滑因子 / Smoothing factor
    
    def validate(self) -> List[str]:
        """
        參數驗證
        Parameter validation
        """
        errors = []
        if self.num_points is not None and self.num_points <= 0:
            errors.append("num_points must be positive")
        if self.smoothing_factor <= 0:
            errors.append("smoothing_factor must be positive")
        return errors

@dataclass
class PlotParams:
    """
    標準繪圖參數
    Standard plotting parameters
    """
    figsize: tuple = (10, 6)               # 圖形大小 / Figure size
    dpi: int = 100                         # 解析度 / Resolution
    style: str = 'default'                 # 樣式 / Style
    colormap: str = 'viridis'              # 色彩映射 / Colormap
    show_colorbar: bool = True             # 顯示色條 / Show colorbar
    title: Optional[str] = None            # 標題 / Title
```

## Extension Guide

### 1. Adding New Data Type Support

#### Step 1: Create Parser
```python
# core/parsers/new_format_parser.py
class NewFormatParser:
    """
    新格式解析器
    New format parser
    """
    @staticmethod
    def parse(filepath: str) -> Dict[str, Any]:
        """
        解析新格式檔案
        Parse new format file
        """
        # 實現解析邏輯 / Implement parsing logic
        pass
    
    @staticmethod
    def validate(filepath: str) -> bool:
        """
        驗證檔案格式
        Validate file format
        """
        # 實現驗證邏輯 / Implement validation logic
        pass
```

#### Step 2: Create Analysis Methods
```python
# core/analysis/new_format_analysis.py
class NewFormatAnalysis:
    """
    新格式分析方法
    New format analysis methods
    """
    @staticmethod
    def process_data(data: Dict, params: AnalysisParams) -> AnalysisResult:
        """
        處理新格式數據
        Process new format data
        """
        # 實現處理邏輯 / Implement processing logic
        pass
```

## Deployment and Maintenance

### 1. Environment Configuration

#### Conda Environment Configuration (environment.yml)
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
    # Development tools (optional, uncomment when needed)
    - pytest>=7.4.0
    - black>=23.0.0
    - flake8>=6.0.0

    # Jupyter notebook support
    - jupyterlab>=4.0.0
    - ipykernel>=6.20.0
```

#### Additional Pip Dependencies (requirements.txt)
```pip-requirements
pywebview>=4.4.0
```

#### Environment Setup Commands
```bash
# Create conda environment
conda env create -f environment.yml

# Activate environment
conda activate keen

# Install additional dependencies
pip install -r requirements.txt

# Development mode installation (optional)
pip install -e .
```

### 2. Performance Monitoring

```python
# core/utils/performance_monitor.py
class PerformanceMonitor:
    """
    性能監控器
    Performance monitor
    
    監控系統性能和資源使用
    Monitor system performance and resource usage
    """
    def __init__(self):
        self.metrics = defaultdict(list)
    
    @contextmanager
    def measure(self, operation_name: str):
        """
        測量操作性能
        Measure operation performance
        """
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
        """
        獲取性能報告
        Get performance report
        """
        report = {}
        for operation, measurements in self.metrics.items():
            durations = [m['duration'] for m in measurements]
            memory_deltas = [m['memory_delta'] for m in measurements]
            
            report[operation] = {
                'avg_duration': np.mean(durations),
                'max_duration': np.max(durations),
                'avg_memory_delta': np.mean(memory_deltas),
                'call_count': len(measurements)
            }
        return report
```

### 3. Configuration Management

```python
# core/utils/config.py
@dataclass
class SystemConfig:
    """
    系統配置
    System configuration
    """
    max_memory_mb: int = 1000              # 最大記憶體 / Maximum memory
    cache_size_mb: int = 500               # 快取大小 / Cache size
    num_workers: int = 4                   # 工作執行緒數 / Number of workers
    temp_dir: str = "/tmp/spm_analysis"    # 臨時目錄 / Temporary directory
    log_level: str = "INFO"                # 日誌級別 / Log level
    
    @classmethod
    def from_file(cls, filepath: str) -> 'SystemConfig':
        """
        從檔案載入配置
        Load configuration from file
        """
        with open(filepath, 'r') as f:
            config_data = json.load(f)
        return cls(**config_data)
    
    def save(self, filepath: str):
        """
        保存配置到檔案
        Save configuration to file
        """
        with open(filepath, 'w') as f:
            json.dump(asdict(self), f, indent=2)
```

### 4. Logging System

```python
# core/utils/logging_config.py
import logging
from datetime import datetime

def setup_logging(config: SystemConfig):
    """
    設置日誌系統
    Setup logging system
    """
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    logging.basicConfig(
        level=getattr(logging, config.log_level),
        format=log_format,
        handlers=[
            logging.FileHandler(f'spm_analysis_{datetime.now().strftime("%Y%m%d")}.log'),
            logging.StreamHandler()
        ]
    )
    
    root_logger = logging.getLogger('spm_analysis')
    return root_logger
```

## Conclusion

This architecture design provides a sustainable and scalable SPM data analysis solution. Through clear separation of responsibilities, intelligent resource management, and comprehensive testing strategies, it ensures the system is both efficient and reliable when processing complex SPM data.

### Development Roadmap

1. **Implement Core Infrastructure**
   - Basic analyzer framework
   - Mathematics library foundation
   - Caching system

2. **Create Basic Test Suite**
   - Unit tests for mathematical functions
   - Integration tests for analyzers
   - Performance benchmarks

3. **Develop Specialized Analyzers**
   - CITS analyzer
   - STS analyzer
   - Topography analyzer

4. **Enhance Visualization**
   - Interactive plotting
   - Analysis dashboards
   - Export capabilities

5. **Optimization and Deployment**
   - Performance tuning
   - Memory optimization
   - Production deployment

This architecture ensures that the SPM data analysis framework can grow and adapt to future requirements while maintaining code quality and performance standards.
