# 架構 V2 遷移指南 / Architecture V2 Migration Guide

本文件提供從舊架構遷移到新架構 V2 的完整指南，包含程式碼範例和最佳實踐。  
This document provides a complete guide for migrating from the old architecture to the new architecture V2, including code examples and best practices.

---

## 概述 / Overview

新架構解決了原有系統的四個核心問題：
The new architecture addresses four core issues in the original system:

1. **資料存取不直覺** → **IDE 友好的屬性存取**
2. **變數未持久化** → **完整的狀態管理**
3. **Parser 輸出不一致** → **統一的資料格式**
4. **職責劃分不清** → **型別管理器模式**

---

## 新架構核心概念 / Core Concepts

### 主要組件 / Main Components

```python
# 新架構的核心組件
from backend.core.experiment_session import ExperimentSession
from backend.core.data_models import TopoData, CitsData, StsData, TxtData
from backend.core.file_proxy import FileProxy
```

### 使用流程 / Usage Flow

```python
# 1. 建立實驗會話
session = ExperimentSession('experiment.txt')

# 2. 存取檔案（IDE 完整支援）
topo = session['topofwd']

# 3. 存取資料（型別安全）
image_data = topo.data.image        # np.ndarray
x_range = topo.data.x_range         # float
metadata = topo.metadata            # Dict[str, Any]

# 4. 使用分析器
analyzer = topo.analyzer
result = analyzer.some_analysis()
```

---

## 遷移步驟 / Migration Steps

### 步驟 1：更新匯入 / Step 1: Update Imports

**舊程式碼：**
```python
from backend.core.main_analyzer import MainAnalyzer
from backend.core.analyzers.int_analyzer import IntAnalyzer
```

**新程式碼：**
```python
from backend.core.experiment_session import ExperimentSession
from backend.core.data_models import TopoData, CitsData, StsData
```

### 步驟 2：初始化方式 / Step 2: Initialization

**舊方式：**
```python
analyzer = MainAnalyzer()
result = analyzer.load_experiment('experiment.txt', 'my_experiment')
```

**新方式：**
```python
session = ExperimentSession('experiment.txt')
# 實驗名稱自動從檔案推斷
```

### 步驟 3：資料存取 / Step 3: Data Access

**舊方式：**
```python
# 複雜且容易出錯的字典存取
experiment = analyzer.get_current_experiment()
file_data = experiment['loaded_files']['topofwd']['data']
image_data = file_data['image_data']
x_range = experiment['scan_parameters']['x_range']
```

**新方式：**
```python
# 直覺且型別安全的屬性存取
topo = session['topofwd']
image_data = topo.data.image
x_range = topo.data.x_range
```

### 步驟 4：分析器使用 / Step 4: Analyzer Usage

**舊方式：**
```python
int_analyzer = analyzer.get_analyzer('int')
result = analyzer.analyze_int_data('topofwd')
```

**新方式：**
```python
topo = session['topofwd']
analyzer = topo.analyzer
# 分析結果自動保存到 topo.data 中
result = analyzer.flatten_plane()
```

---

## 詳細對比 / Detailed Comparison

### 1. 檔案載入 / File Loading

**舊架構：**
```python
# 手動管理載入狀態
load_result = analyzer.load_file('topofwd', 'my_experiment')
if not load_result['success']:
    print(f"載入失敗: {load_result['error']}")
    return

# 複雜的資料存取
experiment = analyzer.loaded_experiments['my_experiment']
file_data = experiment['loaded_files']['topofwd']['data']
```

**新架構：**
```python
# 自動載入，統一錯誤處理
try:
    topo = session['topofwd']
    data = topo.data  # 自動觸發載入
except RuntimeError as e:
    print(f"載入失敗: {e}")
    return
```

### 2. 多檔案操作 / Multi-file Operations

**舊架構：**
```python
# 手動批次載入
file_keys = ['topofwd', 'topobwd', 'lia1rfwd']
results = analyzer.load_multiple_files(file_keys)

# 手動檢查每個結果
for key, result in results['data']['results'].items():
    if result['success']:
        # 處理成功的檔案
        pass
```

**新架構：**
```python
# 簡潔的批次操作
topo_files = session.get_topo_files()
for file_key in topo_files:
    file_proxy = session[file_key]
    if file_proxy.file_info.signal_type == 'Topo':
        # 直接使用，自動處理錯誤
        image = file_proxy.data.image
```

### 3. 狀態管理 / State Management

**舊架構：**
```python
# 分析結果可能遺失
int_analyzer = analyzer.get_analyzer('int')
flattened = int_analyzer.some_analysis()
# flattened 只存在於局部變數中
```

**新架構：**
```python
# 分析結果自動持久化
topo = session['topofwd']
flattened = topo.analyzer.flatten_plane()
# 結果自動保存到 topo.data.flattened

# 隨時可以存取歷史結果
previous_result = topo.data.flattened
```

### 4. 錯誤處理 / Error Handling

**舊架構：**
```python
# 分散的錯誤處理
result = analyzer.load_file('nonexistent')
if not result['success']:
    errors = result['error']  # 字串格式，難以程式化處理

analysis_result = analyzer.analyze_int_data('topofwd')
if not analysis_result['success']:
    # 不同的錯誤格式
    pass
```

**新架構：**
```python
# 統一的例外處理
try:
    topo = session['nonexistent']
    data = topo.data
except ValueError as e:
    # 檔案不存在
    pass
except RuntimeError as e:
    # 載入失敗
    pass

# 詳細的錯誤資訊
if not topo.analyzer.some_analysis():
    errors = topo.analyzer.get_analysis_history()
```

---

## 進階功能 / Advanced Features

### 1. 智能快取 / Smart Caching

```python
# 自動快取管理
session = ExperimentSession('experiment.txt', cache_size=20)

# 檢查快取狀態
memory_info = session.get_memory_info()
print(f"快取命中率: {memory_info['topo_cache']['hit_rate']:.2%}")

# 手動管理快取
session.clear_all_caches()  # 清理所有快取
topo.unload()              # 卸載特定檔案
```

### 2. 檔案搜尋 / File Search

```python
# 根據訊號類型搜尋
topo_files = session.find_files_by_signal_type('Topo')
lia_files = session.find_files_by_signal_type('Lia1R')

# 根據掃描方向搜尋
fwd_files = session.find_files_by_direction('Fwd')
bwd_files = session.find_files_by_direction('Bwd')

# 組合條件
for file_key in session.get_topo_files():
    file_proxy = session[file_key]
    info = file_proxy.file_info
    if info.signal_type == 'Topo' and info.direction == 'Fwd':
        # 處理正向拓撲檔案
        pass
```

### 3. 分析流水線 / Analysis Pipeline

```python
# 建立分析流水線
def process_topography(session, file_key):
    """處理拓撲圖的標準流程"""
    topo = session[file_key]
    
    # 1. 平坦化
    flattened = topo.flatten_plane(method='linear')
    
    # 2. 提取剖面線
    profile = topo.extract_profile(x1=0, y1=0, x2=100, y2=100)
    
    # 3. 計算統計
    analyzer = topo.analyzer
    stats = analyzer.calculate_statistics()
    
    return {
        'flattened': flattened,
        'profile': profile,
        'stats': stats
    }

# 批次處理所有拓撲檔案
results = {}
for file_key in session.get_topo_files():
    results[file_key] = process_topography(session, file_key)
```

---

## 最佳實踐 / Best Practices

### 1. 程式碼組織 / Code Organization

```python
# 推薦：使用型別提示
from typing import List, Dict, Optional
from backend.core.experiment_session import ExperimentSession
from backend.core.data_models import TopoData

def analyze_experiment(txt_file: str) -> Dict[str, any]:
    """分析整個實驗的函數"""
    session = ExperimentSession(txt_file)
    
    # IDE 會提供完整的自動完成
    topo_files: List[str] = session.get_topo_files()
    
    results = {}
    for file_key in topo_files:
        topo_proxy = session[file_key]
        topo_data: TopoData = topo_proxy.data  # 明確的型別
        
        # 型別安全的操作
        results[file_key] = {
            'shape': topo_data.shape,
            'range': (topo_data.x_range, topo_data.y_range),
            'scale': topo_data.scale
        }
    
    return results
```

### 2. 錯誤處理 / Error Handling

```python
def safe_file_access(session: ExperimentSession, file_key: str) -> Optional[TopoData]:
    """安全的檔案存取範例"""
    try:
        file_proxy = session[file_key]
        
        # 檢查檔案類型
        if file_proxy.file_type != 'topo':
            print(f"檔案 {file_key} 不是拓撲檔案")
            return None
        
        # 載入資料
        data = file_proxy.data
        if isinstance(data, TopoData):
            return data
        else:
            print(f"資料格式錯誤: {type(data)}")
            return None
            
    except ValueError:
        print(f"檔案 {file_key} 不存在")
        return None
    except RuntimeError as e:
        print(f"載入檔案 {file_key} 時發生錯誤: {e}")
        return None
```

### 3. 效能優化 / Performance Optimization

```python
def efficient_batch_processing(session: ExperimentSession):
    """高效的批次處理範例"""
    
    # 1. 預先載入需要的檔案
    required_files = ['topofwd', 'topobwd', 'lia1rfwd']
    session.load_multiple_files(required_files)
    
    # 2. 使用列表推導式進行批次操作
    topo_data = [
        session[key].data for key in required_files 
        if session[key].file_type == 'topo'
    ]
    
    # 3. 定期清理快取以節省記憶體
    if len(session.loaded_files['topo']) > 10:
        # 保留最近使用的檔案，清理其他
        for key in session.loaded_files['topo'][:-5]:
            session[key].unload()
```

---

## 常見問題 / Common Issues

### Q1: 如何處理檔案不存在的情況？
**A:** 新架構使用例外處理：

```python
try:
    file_proxy = session['nonexistent_file']
    data = file_proxy.data
except ValueError:
    print("檔案不存在")
except RuntimeError:
    print("載入失敗")
```

### Q2: 如何獲取分析歷史？
**A:** 每個 FileProxy 都記錄完整的分析歷史：

```python
topo = session['topofwd']
history = topo.get_analysis_history()
for record in history:
    print(f"{record['timestamp']}: {record['analysis_type']}")
```

### Q3: 如何在新舊架構之間切換？
**A:** 兩套架構可以並行存在：

```python
# 舊架構（仍然可用）
from backend.core.main_analyzer import MainAnalyzer
old_analyzer = MainAnalyzer()

# 新架構
from backend.core.experiment_session import ExperimentSession
new_session = ExperimentSession('experiment.txt')

# 根據需要選擇使用
```

---

## 總結 / Summary

新架構 V2 提供了：
The new architecture V2 provides:

✅ **更好的開發體驗**：IDE 友好的型別提示和自動完成  
✅ **更簡潔的程式碼**：直覺的屬性存取，減少樣板程式碼  
✅ **更可靠的執行**：統一的錯誤處理和狀態管理  
✅ **更高的效能**：智能快取和延遲載入  
✅ **更易維護**：清晰的架構和職責分離  

建議：
- 新專案直接使用新架構
- 現有專案可以漸進式遷移
- 兩套架構可以並行使用

如有任何問題，請參考 `backend/test/new_architecture_demo_v2.py` 中的完整範例。