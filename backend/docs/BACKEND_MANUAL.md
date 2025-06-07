# KEEN 後端架構使用手冊 / KEEN Backend Architecture Manual

**作者 / Author**: Odindino  
**日期 / Date**: 2025-06-07  
**版本 / Version**: 2.0

## 目錄 / Table of Contents

1. [概述 / Overview](#概述--overview)
2. [架構設計 / Architecture Design](#架構設計--architecture-design)
3. [核心組件 / Core Components](#核心組件--core-components)
4. [使用指南 / Usage Guide](#使用指南--usage-guide)
5. [API 參考 / API Reference](#api-參考--api-reference)
6. [範例程式碼 / Example Code](#範例程式碼--example-code)
7. [疑難排解 / Troubleshooting](#疑難排解--troubleshooting)

## 概述 / Overview

KEEN 後端採用全新的「**類型管理器 + 檔案代理**」架構（Type Manager + File Proxy），提供統一、高效且擴展性強的 SPM 數據處理系統。此架構支援多種檔案格式（TXT、INT、DAT），並提供完整的數據分析功能。

The KEEN backend adopts a new "**Type Manager + File Proxy**" architecture, providing a unified, efficient, and highly extensible SPM data processing system. This architecture supports multiple file formats (TXT, INT, DAT) and provides comprehensive data analysis capabilities.

### 主要特點 / Key Features

- 🔧 **統一的數據模型** - 標準化的數據結構和介面
- ⚡ **智能快取管理** - LRU 快取機制提升性能
- 🎯 **類型安全** - 完整的型別提示和驗證
- 🔄 **靈活的分析器** - 可插拔的分析模組系統
- 📊 **Plotly 視覺化** - 內建高品質圖表生成
- 🔗 **鏈式操作** - 直觀的 API 設計

## 架構設計 / Architecture Design

### 核心架構模式 / Core Architecture Pattern

```
ExperimentSession (會話管理)
├── TxtManager (TXT 檔案管理)
├── TopoManager (拓撲圖管理)  
├── CitsManager (CITS 數據管理)
└── StsManager (STS 數據管理)

FileProxy (檔案代理)
├── txt -> TxtAnalyzer
├── topo -> IntAnalyzer
├── cits -> CitsAnalyzer
└── sts -> DatAnalyzer
```

### 數據流程 / Data Flow

```
文件檔案 -> Parser -> StandardData -> TypeManager -> FileProxy -> Analyzer -> 分析結果
File -> Parser -> StandardData -> TypeManager -> FileProxy -> Analyzer -> Results
```

## 核心組件 / Core Components

### 1. 實驗會話 (ExperimentSession)

**檔案位置**: `backend/core/experiment_session.py`

實驗會話是系統的入口點，負責管理整個 SPM 實驗的檔案和數據。

```python
from backend.core.experiment_session import ExperimentSession

# 初始化會話
session = ExperimentSession()

# 載入 TXT 檔案（會自動發現相關的 INT/DAT 檔案）
session.load_txt_file("/path/to/experiment.txt")

# 取得檔案代理
txt_proxy = session.get_file_proxy("experiment.txt")
topo_proxy = session.get_file_proxy("TopoFwd.int")
cits_proxy = session.get_file_proxy("Matrix.dat")
```

### 2. 檔案代理 (FileProxy)

**檔案位置**: `backend/core/file_proxy.py`

檔案代理提供統一的介面來存取檔案數據和分析器。

```python
# 存取數據
data = proxy.data
metadata = proxy.metadata

# 取得分析器
analyzer = proxy.analyzer

# 執行分析
result = analyzer.analyze()
```

### 3. 類型管理器 (TypeManager)

**檔案位置**: `backend/core/type_managers.py`

各種專門的管理器負責特定類型檔案的解析、快取和分析器管理。

#### TxtManager
```python
# 管理 TXT 檔案
txt_manager = session.txt
txt_data = txt_manager.load("experiment_key")
```

#### TopoManager  
```python
# 管理拓撲圖 (INT 檔案)
topo_manager = session.topo
topo_data = topo_manager.load("TopoFwd_key")
```

#### CitsManager
```python
# 管理 CITS 數據 (DAT 檔案)
cits_manager = session.cits
cits_data = cits_manager.load("Matrix_key")
```

### 4. 數據模型 (Data Models)

**檔案位置**: `backend/core/data_models.py`

標準化的數據結構提供型別安全和 IDE 友好的開發體驗。

```python
from backend.core.data_models import TopoData, CitsData, StsData

# TopoData - 拓撲圖數據
topo_data = TopoData(
    image=image_array,
    x_range=100.0,
    y_range=100.0,
    x_pixels=256,
    y_pixels=256,
    data_scale=1.0
)

# CitsData - CITS 數據
cits_data = CitsData(
    data_3d=data_array,
    bias_values=bias_array,
    grid_size=[100, 100],
    x_range=100.0,
    y_range=100.0
)
```

### 5. 解析器 (Parsers)

**檔案位置**: `backend/core/parsers/`

專門的解析器負責從原始檔案提取數據。

- `TxtParser` - 解析 TXT 實驗參數檔案
- `IntParser` - 解析 INT 二進制圖像檔案  
- `DatParser` - 解析 DAT 光譜數據檔案

### 6. 分析器 (Analyzers)

**檔案位置**: `backend/core/analyzers/`

提供各種數據分析功能。

- `TxtAnalyzer` - 實驗參數分析
- `IntAnalyzer` - 拓撲圖分析（平坦化、統計等）
- `CitsAnalyzer` - CITS 光譜分析（線段剖面、偏壓切片等）
- `DatAnalyzer` - 通用 DAT 數據分析

## 使用指南 / Usage Guide

### 基本工作流程 / Basic Workflow

#### 1. 初始化會話
```python
from backend.core.experiment_session import ExperimentSession

session = ExperimentSession()
```

#### 2. 載入實驗檔案
```python
# 載入 TXT 檔案，會自動發現相關檔案
session.load_txt_file("/path/to/experiment.txt")

# 檢視已載入的檔案
print("TXT 檔案:", list(session.txt.get_files().keys()))
print("拓撲檔案:", list(session.topo.get_files().keys()))
print("CITS 檔案:", list(session.cits.get_files().keys()))
```

#### 3. 分析拓撲圖
```python
# 取得拓撲圖代理
topo_key = list(session.topo.get_files().keys())[0]
topo = session.get_file_proxy(topo_key)

# 執行分析
result = topo.analyzer.analyze()

# 平坦化處理
flattened_result = topo.analyzer.flatten_image(method='polynomial', order=2)

# 提取剖面線
profile_result = topo.analyzer.extract_profile(
    start_coord=(10, 10),
    end_coord=(90, 90)
)
```

#### 4. 分析 CITS 數據
```python
# 取得 CITS 代理
cits_key = list(session.cits.get_files().keys())[0]
cits = session.get_file_proxy(cits_key)

# 執行基本分析
result = cits.analyzer.analyze()

# 提取線段剖面光譜
line_profile = cits.analyzer.extract_line_profile(
    start_coord=(20, 20),
    end_coord=(80, 80),
    sampling_method='bresenham'
)

# 取得特定偏壓的 2D 切片
bias_slice = cits.analyzer.get_bias_slice(bias_index=100)

# 計算電導圖
conductance_maps = cits.analyzer.analyze_conductance_maps()
```

### 進階功能 / Advanced Features

#### 快取管理
```python
# 檢視快取狀態
cache_info = session.topo.get_cache_info()
print(f"快取命中率: {cache_info['hit_rate']:.2%}")

# 清理快取
session.topo.clear_cache()

# 強制重載檔案
data = session.topo.load("file_key", force_reload=True)
```

#### 自訂分析參數
```python
# 拓撲圖平坦化參數
flattened = topo.analyzer.flatten_image(
    method='polynomial',
    order=3,
    mask_threshold=0.1
)

# CITS 線段剖面參數
line_profile = cits.analyzer.extract_line_profile(
    start_coord=(0, 0),
    end_coord=(99, 99),
    sampling_method='interpolate'  # 或 'bresenham'
)
```

#### 視覺化
```python
# 所有分析器都會返回 Plotly 圖表
result = analyzer.analyze()
plots = result['plots']

# 直接顯示圖表（在 Jupyter 中）
plots['topography'].show()

# 或存取圖表配置
fig_config = plots['topography']
```

## API 參考 / API Reference

### ExperimentSession

| 方法 | 說明 | 參數 | 返回值 |
|------|------|------|--------|
| `load_txt_file(path)` | 載入 TXT 檔案並發現相關檔案 | `path: str` | `bool` |
| `get_file_proxy(key)` | 取得檔案代理 | `key: str` | `FileProxy` |
| `get_session_summary()` | 取得會話摘要 | - | `dict` |

### FileProxy

| 屬性/方法 | 說明 | 類型 |
|-----------|------|------|
| `data` | 檔案數據 | `SPMData` |
| `metadata` | 檔案元數據 | `dict` |
| `analyzer` | 分析器實例 | `BaseAnalyzer` |

### TypeManager

| 方法 | 說明 | 參數 | 返回值 |
|------|------|------|--------|
| `load(key, force_reload=False)` | 載入檔案 | `key: str, force_reload: bool` | `ParseResult` |
| `get_analyzer(key)` | 取得分析器 | `key: str` | `BaseAnalyzer` |
| `get_cache_info()` | 取得快取資訊 | - | `dict` |
| `clear_cache()` | 清理快取 | - | `None` |

### BaseAnalyzer

| 方法 | 說明 | 參數 | 返回值 |
|------|------|------|--------|
| `analyze(**kwargs)` | 執行基本分析 | `**kwargs` | `dict` |
| `validate_input(**kwargs)` | 驗證輸入 | `**kwargs` | `bool` |

### IntAnalyzer (拓撲圖分析器)

| 方法 | 說明 | 參數 | 返回值 |
|------|------|------|--------|
| `flatten_image(method, **params)` | 平坦化圖像 | `method: str, **params` | `dict` |
| `extract_profile(start_coord, end_coord)` | 提取剖面線 | `start_coord: tuple, end_coord: tuple` | `dict` |
| `calculate_statistics()` | 計算統計數據 | - | `dict` |

### CitsAnalyzer (CITS 分析器)

| 方法 | 說明 | 參數 | 返回值 |
|------|------|------|--------|
| `extract_line_profile(start_coord, end_coord, sampling_method)` | 提取線段剖面 | `start_coord: tuple, end_coord: tuple, sampling_method: str` | `dict` |
| `get_bias_slice(bias_index)` | 取得偏壓切片 | `bias_index: int` | `dict` |
| `analyze_conductance_maps(**kwargs)` | 分析電導圖 | `**kwargs` | `dict` |

## 範例程式碼 / Example Code

### 完整分析範例

```python
from backend.core.experiment_session import ExperimentSession

# 1. 初始化會話
session = ExperimentSession()

# 2. 載入實驗
txt_path = "/path/to/experiment.txt"
success = session.load_txt_file(txt_path)

if success:
    print("✅ 實驗載入成功")
    
    # 3. 分析拓撲圖
    topo_files = list(session.topo.get_files().keys())
    if topo_files:
        topo = session.get_file_proxy(topo_files[0])
        
        # 基本分析
        topo_result = topo.analyzer.analyze()
        print(f"拓撲圖尺寸: {topo_result['data']['image_info']['shape']}")
        
        # 平坦化
        flattened = topo.analyzer.flatten_image(method='polynomial', order=2)
        
        # 剖面線
        profile = topo.analyzer.extract_profile(
            start_coord=(0, 50),
            end_coord=(255, 50)
        )
    
    # 4. 分析 CITS 數據
    cits_files = list(session.cits.get_files().keys())
    if cits_files:
        cits = session.get_file_proxy(cits_files[0])
        
        # 基本分析
        cits_result = cits.analyzer.analyze()
        print(f"CITS 數據尺寸: {cits_result['data']['cits_data_info']['shape']}")
        
        # 線段剖面光譜
        line_profile = cits.analyzer.extract_line_profile(
            start_coord=(10, 10),
            end_coord=(90, 90)
        )
        
        # 偏壓切片
        bias_slice = cits.analyzer.get_bias_slice(bias_index=200)
    
    # 5. 取得會話摘要
    summary = session.get_session_summary()
    print("會話摘要:", summary)

else:
    print("❌ 實驗載入失敗")
```

### 互動式 Jupyter 範例

參考 `backend/test/interactive_new_architecture_test.ipynb` 中的完整互動式範例。

## 疑難排解 / Troubleshooting

### 常見問題 / Common Issues

1. **檔案載入失敗**
   ```python
   # 檢查檔案路徑和權限
   import os
   print(f"檔案存在: {os.path.exists(file_path)}")
   print(f"檔案大小: {os.path.getsize(file_path)}")
   ```

2. **快取問題**
   ```python
   # 清理快取並重載
   session.topo.clear_cache()
   data = session.topo.load("key", force_reload=True)
   ```

3. **記憶體不足**
   ```python
   # 檢查快取使用情況
   cache_info = session.get_cache_info()
   
   # 調整快取大小
   session = ExperimentSession(cache_size=10)
   ```

4. **分析錯誤**
   ```python
   # 檢查數據有效性
   result = analyzer.analyze()
   if not result['success']:
       print("錯誤:", result['error'])
   ```

### 日誌 / Logging

```python
import logging

# 設定日誌等級
logging.basicConfig(level=logging.INFO)

# 查看詳細日誌
logger = logging.getLogger('backend.core')
logger.setLevel(logging.DEBUG)
```

### 性能最佳化 / Performance Optimization

1. **適當的快取大小**: 根據可用記憶體調整
2. **批次處理**: 一次載入多個相關檔案
3. **選擇性分析**: 只執行需要的分析功能
4. **資料預處理**: 在分析前進行必要的數據清理

---

**作者 / Author**: Odindino  
**最後更新 / Last Updated**: 2025-06-07  
**版本 / Version**: 2.0

如有問題或建議，請聯繫開發團隊。  
For questions or suggestions, please contact the development team.