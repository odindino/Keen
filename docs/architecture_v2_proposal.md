# 架構改進提案 V2 / Architecture Improvement Proposal V2

本文件記錄了基於使用者體驗反饋的架構改進提案，旨在提升系統的易用性和可維護性。  
This document records the architecture improvement proposal based on user experience feedback, aimed at improving system usability and maintainability.

---

## 背景 / Background

### 現有問題 / Current Issues

1. **資料存取不直覺 / Non-intuitive Data Access**
   - 現況：使用字典式存取 `experiment_data['loaded_files']['topofwd']['data']`
   - 問題：缺乏 IDE 智能提示、容易拼寫錯誤、不符合 Python 慣例

2. **狀態管理不完整 / Incomplete State Management**
   - 現況：分析過程中的中間變數未持久化為 `self.` 屬性
   - 問題：變數生命週期不明確、難以追蹤分析狀態

3. **Parser 輸出不一致 / Inconsistent Parser Output**
   - 現況：不同 parser 有不同的輸出結構
   - 問題：增加學習成本、缺乏統一的資料契約

4. **架構職責不清 / Unclear Architecture Responsibilities**
   - 現況：MainAnalyzer 管理所有變數和狀態
   - 問題：違反單一職責原則、擴展性受限

---

## 改進方案 / Improvement Proposal

### 核心概念：混合式架構 / Core Concept: Hybrid Architecture

採用「型別管理器 + 檔案代理」模式，結合以下優點：
- 清晰的職責劃分
- 直覺的存取介面
- 完整的 IDE 支援
- 靈活的擴展性

Adopt a "Type Manager + File Proxy" pattern combining:
- Clear separation of responsibilities
- Intuitive access interface
- Full IDE support
- Flexible extensibility

### 架構設計 / Architecture Design

```
ExperimentSession (主要入口 / Main Entry)
├── TxtManager (文字檔管理器)
├── TopoManager (拓撲圖管理器)
├── CitsManager (CITS 資料管理器)
├── StsManager (STS 資料管理器)
└── FileProxy (檔案代理介面)
```

---

## 實作細節 / Implementation Details

### 1. 資料模型定義 / Data Model Definition

使用 Python 的型別提示和資料類別來建立強型別的資料模型：

```python
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime
import numpy as np

@dataclass
class ParseResult:
    """標準化的解析結果 / Standardized parse result"""
    metadata: Dict[str, Any]      # 元資料 / Metadata
    data: Any                     # 主要資料 / Main data
    derived: Dict[str, Any] = field(default_factory=dict)  # 衍生資料 / Derived data
    errors: List[str] = field(default_factory=list)        # 錯誤訊息 / Error messages
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class FileInfo:
    """檔案資訊 / File information"""
    path: str
    type: str
    size: int
    signal_type: Optional[str] = None
    direction: Optional[str] = None
    loaded: bool = False
    loaded_at: Optional[datetime] = None

@dataclass
class TopoData:
    """拓撲圖資料 / Topography data"""
    image: np.ndarray
    x_range: float  # nm
    y_range: float  # nm
    x_pixels: int
    y_pixels: int
    flattened: Optional[np.ndarray] = None
    profile_lines: Dict[str, Any] = field(default_factory=dict)
```

### 2. 型別管理器實作 / Type Manager Implementation

每個型別管理器負責管理特定類型的所有檔案：

```python
from typing import Dict, List, Optional
from abc import ABC, abstractmethod

class TypeManager(ABC):
    """型別管理器基類 / Base class for type managers"""
    
    def __init__(self):
        self._files: Dict[str, FileInfo] = {}
        self._data: Dict[str, ParseResult] = {}
        self._analyzers: Dict[str, Any] = {}
    
    def add_file(self, key: str, info: FileInfo) -> None:
        """添加檔案資訊 / Add file information"""
        self._files[key] = info
    
    def load(self, key: str) -> ParseResult:
        """載入檔案 / Load file"""
        if key not in self._data:
            self._data[key] = self._parse_file(self._files[key])
        return self._data[key]
    
    @abstractmethod
    def _parse_file(self, info: FileInfo) -> ParseResult:
        """解析檔案（子類實作）/ Parse file (implemented by subclass)"""
        pass
    
    def get_analyzer(self, key: str):
        """獲取或創建分析器 / Get or create analyzer"""
        if key not in self._analyzers:
            self._analyzers[key] = self._create_analyzer(key)
        return self._analyzers[key]
    
    @abstractmethod
    def _create_analyzer(self, key: str):
        """創建分析器（子類實作）/ Create analyzer (implemented by subclass)"""
        pass

class TopoManager(TypeManager):
    """拓撲圖管理器 / Topography manager"""
    
    def _parse_file(self, info: FileInfo) -> ParseResult:
        from backend.core.parsers import IntParser
        parser = IntParser(info.path)
        raw_data = parser.parse()
        
        # 轉換為標準格式
        topo_data = TopoData(
            image=raw_data['image_data'],
            x_range=raw_data['physical_dimensions'][0],
            y_range=raw_data['physical_dimensions'][1],
            x_pixels=raw_data['scan_parameters']['x_pixel'],
            y_pixels=raw_data['scan_parameters']['y_pixel']
        )
        
        return ParseResult(
            metadata={
                'signal_type': info.signal_type,
                'direction': info.direction,
                'path': info.path
            },
            data=topo_data
        )
    
    def _create_analyzer(self, key: str):
        from backend.core.analyzers import IntAnalyzer
        return IntAnalyzer(self._data[key].data)
```

### 3. 檔案代理介面 / File Proxy Interface

提供直覺的屬性訪問方式：

```python
class FileProxy:
    """檔案代理，提供直覺的存取介面 / File proxy for intuitive access"""
    
    def __init__(self, session: 'ExperimentSession', file_key: str):
        self._session = session
        self._file_key = file_key
        self._type = self._determine_type()
        self._manager = self._get_manager()
    
    def _determine_type(self) -> str:
        """判斷檔案類型 / Determine file type"""
        # 從 file_key 或其他資訊判斷類型
        if 'topo' in self._file_key.lower():
            return 'topo'
        elif 'matrix' in self._file_key.lower():
            return 'cits'
        # ... 其他類型
    
    def _get_manager(self) -> TypeManager:
        """獲取對應的管理器 / Get corresponding manager"""
        return getattr(self._session, self._type)
    
    @property
    def data(self) -> Any:
        """獲取資料 / Get data"""
        result = self._manager.load(self._file_key)
        return result.data
    
    @property
    def metadata(self) -> Dict[str, Any]:
        """獲取元資料 / Get metadata"""
        result = self._manager.load(self._file_key)
        return result.metadata
    
    @property
    def analyzer(self) -> Any:
        """獲取分析器 / Get analyzer"""
        return self._manager.get_analyzer(self._file_key)
    
    @property
    def image(self) -> Optional[np.ndarray]:
        """快捷存取圖像資料 / Shortcut for image data"""
        if hasattr(self.data, 'image'):
            return self.data.image
        return None
    
    def __repr__(self) -> str:
        return f"<FileProxy: {self._file_key} ({self._type})>"
```

### 4. 主要入口類別 / Main Entry Class

整合所有管理器的主要類別：

```python
class ExperimentSession:
    """實驗會話，整合所有資料管理 / Experiment session integrating all data management"""
    
    def __init__(self, txt_file_path: str):
        # 初始化管理器
        self.txt = TxtManager()
        self.topo = TopoManager()
        self.cits = CitsManager()
        self.sts = StsManager()
        
        # 載入並解析 TXT 檔案
        self._load_experiment(txt_file_path)
    
    def _load_experiment(self, txt_file_path: str):
        """載入實驗資料 / Load experiment data"""
        # 解析 TXT 檔案
        txt_result = self.txt.parse_main_file(txt_file_path)
        
        # 根據 TXT 內容註冊其他檔案
        for int_file in txt_result.data.int_files:
            file_info = FileInfo(
                path=int_file['path'],
                type='int',
                size=int_file['size'],
                signal_type=int_file['signal_type'],
                direction=int_file['direction']
            )
            
            if 'topo' in int_file['signal_type'].lower():
                self.topo.add_file(int_file['key'], file_info)
            # ... 其他類型
    
    def get_file(self, file_key: str) -> FileProxy:
        """獲取檔案代理 / Get file proxy"""
        return FileProxy(self, file_key)
    
    def __getitem__(self, key: str) -> FileProxy:
        """支援索引存取 / Support index access"""
        return self.get_file(key)
    
    @property
    def available_files(self) -> Dict[str, List[str]]:
        """列出所有可用檔案 / List all available files"""
        return {
            'txt': list(self.txt._files.keys()),
            'topo': list(self.topo._files.keys()),
            'cits': list(self.cits._files.keys()),
            'sts': list(self.sts._files.keys())
        }
```

### 5. 使用範例 / Usage Examples

展示新架構的使用方式：

```python
# 初始化實驗會話
session = ExperimentSession('path/to/experiment.txt')

# 方式一：使用 get_file 方法
topo_file = session.get_file('topofwd')
print(topo_file.data.x_range)  # IDE 會提示 TopoData 的屬性
print(topo_file.metadata['signal_type'])

# 方式二：使用索引存取
topo_file = session['topofwd']

# 方式三：透過型別管理器
topo_data = session.topo.load('topofwd')

# 使用分析器
analyzer = topo_file.analyzer
flattened = analyzer.flatten_plane()
profile = analyzer.extract_profile(x1=0, y1=0, x2=100, y2=100)

# 跨檔案分析
cits_file = session['It_to_PC_Matrix']
iv_curve = cits_file.analyzer.extract_iv_curve(x=50, y=50)

# 批次操作
for key in session.available_files['topo']:
    file = session[key]
    print(f"{key}: {file.data.x_range} x {file.data.y_range} nm")
```

---

## 遷移策略 / Migration Strategy

### 第一階段：並行支援 / Phase 1: Parallel Support
- 保留現有 API
- 新增新架構介面
- 提供轉換工具

### 第二階段：逐步遷移 / Phase 2: Gradual Migration
- 更新範例和文件
- 標記舊 API 為 deprecated
- 協助使用者遷移

### 第三階段：完全切換 / Phase 3: Complete Switch
- 移除舊 API
- 完成所有測試更新
- 發布新版本

---

## 優勢總結 / Advantages Summary

1. **IDE 友好**：完整的型別提示和自動完成
2. **直覺操作**：符合 Python 慣例的屬性訪問
3. **狀態管理**：清晰的物件生命週期
4. **統一介面**：標準化的資料結構
5. **職責分離**：模組化的架構設計
6. **易於擴展**：新增檔案類型只需新增管理器

---

## 下一步 / Next Steps

1. 建立原型實作
2. 撰寫單元測試
3. 收集使用者反饋
4. 逐步實施遷移計畫