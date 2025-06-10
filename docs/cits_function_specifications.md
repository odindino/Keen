# CITS 函數規格說明書
# CITS Function Specifications

本文件定義 KEEN 系統中 CITS 數據分析和視覺化函數的統一介面規格。  
This document defines the unified interface specifications for CITS data analysis and visualization functions in the KEEN system.

---

## 設計原則 / Design Principles

### 1. 函式庫導向設計 / Library-Oriented Design
- **最少自定義程式碼**: 使用者只需調用標準函數，無需實現複雜邏輯
- **標準化介面**: 所有函數採用一致的參數命名和返回格式
- **模組化架構**: 分析函數和繪圖函數分離，便於維護和擴展

### 2. 數據流設計 / Data Flow Design
```
原始數據 → 數據提取函數 → 標準化格式 → 繪圖函數 → 視覺化結果
Raw Data → Extraction Functions → Standardized Format → Plotting Functions → Visualization
```

### 3. 錯誤處理 / Error Handling
- 所有函數都包含完整的異常處理
- 提供詳細的錯誤訊息和建議
- 失敗時返回空圖形而非崩潰

---

## 數據提取函數 / Data Extraction Functions

### 1. extract_cits_bias_slice()

**功能**: 提取 CITS 特定偏壓切片數據  
**Purpose**: Extract CITS bias slice data at specific index

```python
def extract_cits_bias_slice(cits_data: Dict, bias_index: int) -> Dict:
```

**輸入參數 / Input Parameters:**
- `cits_data`: CITS 數據字典，必須包含 `data_3d`, `bias_values`
- `bias_index`: 偏壓索引 (0 到 n_bias-1)

**返回格式 / Return Format:**
```python
{
    'slice_data': np.ndarray,      # 2D 切片數據 (y, x)
    'bias_value': float,           # 對應的偏壓值
    'bias_index': int,             # 偏壓索引
    'grid_size': Tuple[int, int],  # 網格大小 [x, y]
    'x_range': float,              # X 方向範圍
    'y_range': float               # Y 方向範圍
}
```

### 2. extract_line_spectra_data()

**功能**: 提取線剖面光譜數據  
**Purpose**: Extract line profile spectra data

```python
def extract_line_spectra_data(cits_data: Dict, 
                             start_coord: Tuple[int, int], 
                             end_coord: Tuple[int, int],
                             sampling_method: str = 'bresenham') -> Dict:
```

**輸入參數 / Input Parameters:**
- `cits_data`: CITS 數據字典
- `start_coord`: 起始座標 (x, y)
- `end_coord`: 終點座標 (x, y)
- `sampling_method`: 採樣方法 ('bresenham' 或 'interpolate')

**返回格式 / Return Format:**
```python
{
    'line_spectra': np.ndarray,    # 線剖面光譜數據 (n_bias, n_points)
    'bias_values': np.ndarray,     # 偏壓值陣列
    'distances': np.ndarray,       # 位置/距離陣列
    'x_coords': np.ndarray,        # 實際採樣的 X 座標
    'y_coords': np.ndarray,        # 實際採樣的 Y 座標
    'n_points': int,               # 採樣點數
    'physical_length': float,      # 物理長度
    'sampling_method': str         # 使用的採樣方法
}
```

### 3. extract_point_spectrum()

**功能**: 提取單點光譜數據  
**Purpose**: Extract single point spectrum data

```python
def extract_point_spectrum(cits_data: Dict, x: int, y: int) -> Dict:
```

**輸入參數 / Input Parameters:**
- `cits_data`: CITS 數據字典
- `x`: X 座標
- `y`: Y 座標

**返回格式 / Return Format:**
```python
{
    'current': np.ndarray,         # 電流光譜
    'conductance': np.ndarray,     # 電導率光譜 (dI/dV)
    'bias_values': np.ndarray,     # 偏壓值陣列
    'position': Tuple[int, int],   # 座標位置
    'n_points': int                # 光譜點數
}
```

### 4. prepare_stacked_spectra_data()

**功能**: 準備堆疊光譜數據  
**Purpose**: Prepare stacked spectra data

```python
def prepare_stacked_spectra_data(line_spectra: np.ndarray, 
                                bias_values: np.ndarray,
                                max_curves: int = 20,
                                step_selection: str = 'uniform') -> Dict:
```

**輸入參數 / Input Parameters:**
- `line_spectra`: 線剖面光譜數據 (n_bias, n_points)
- `bias_values`: 偏壓值陣列
- `max_curves`: 最大顯示曲線數
- `step_selection`: 選擇方式 ('uniform', 'endpoints')

**返回格式 / Return Format:**
```python
{
    'selected_spectra': np.ndarray,    # 選定的光譜數據
    'selected_positions': np.ndarray,  # 選定的位置
    'selected_indices': List[int],     # 選定的索引
    'bias_values': np.ndarray,         # 偏壓值陣列
    'n_selected': int,                 # 選定曲線數
    'total_positions': int,            # 總位置數
    'selection_method': str            # 選擇方法
}
```

---

## 繪圖函數 / Plotting Functions

### 1. plot_cits_bias_slice()

**功能**: 繪製 CITS 偏壓切片  
**Purpose**: Plot CITS bias slice

```python
@staticmethod
def plot_cits_bias_slice(data_3d: np.ndarray,
                        bias_values: np.ndarray,
                        bias_index: int,
                        title: Optional[str] = None,
                        colorscale: str = 'Viridis',
                        **kwargs) -> go.Figure:
```

**標準參數 / Standard Parameters:**
- `width`: 圖形寬度 (預設: 600)
- `height`: 圖形高度 (預設: 600)
- `colorscale`: 顏色方案 (預設: 'Viridis')

**特殊功能 / Special Features:**
- 自動保持長寬比
- 包含偏壓值和索引資訊的標題
- 滑鼠懸停顯示座標和電流值

### 2. plot_band_diagram()

**功能**: 繪製能帶圖  
**Purpose**: Plot band diagram

```python
@staticmethod
def plot_band_diagram(line_spectra: np.ndarray,
                     bias_values: np.ndarray,
                     distances: Optional[np.ndarray] = None,
                     title: str = "Band Diagram",
                     use_log_scale: bool = False,
                     colorscale: str = 'RdBu',
                     **kwargs) -> go.Figure:
```

**標準參數 / Standard Parameters:**
- `width`: 圖形寬度 (預設: 800)
- `height`: 圖形高度 (預設: 600)
- `use_log_scale`: 是否使用對數尺度
- `colorscale`: 顏色方案 (預設: 'RdBu')

**特殊功能 / Special Features:**
- 自動檢測位置軸單位 (像素或奈米)
- 支援線性和對數尺度切換
- 平滑化熱力圖顯示

### 3. plot_stacked_spectra()

**功能**: 繪製堆疊光譜圖  
**Purpose**: Plot stacked spectra

```python
@staticmethod
def plot_stacked_spectra(line_spectra: np.ndarray,
                       bias_values: np.ndarray,
                       offset_factor: float = 1.0,
                       positions: Optional[np.ndarray] = None,
                       max_curves: int = 20,
                       title: str = "Stacked Spectra",
                       **kwargs) -> go.Figure:
```

**標準參數 / Standard Parameters:**
- `width`: 圖形寬度 (預設: 800)
- `height`: 圖形高度 (預設: 700)
- `offset_factor`: 偏移係數 (預設: 1.0)
- `max_curves`: 最大顯示曲線數

**特殊功能 / Special Features:**
- 自動計算適當的垂直偏移
- 彩虹色彩映射
- 智能曲線選擇演算法

---

## 使用範例 / Usage Examples

### 完整工作流程 / Complete Workflow

```python
# 1. 載入數據 / Load data
session = ExperimentSession("path/to/file.txt")
cits_file = session["CITS_file_key"]
cits_data_dict = {
    'data_3d': cits_file.data.data_3d,
    'bias_values': cits_file.data.bias_values,
    'grid_size': cits_file.data.grid_size,
    'measurement_mode': 'CITS'
}

# 2. 偏壓切片 / Bias slice
bias_info = extract_cits_bias_slice(cits_data_dict, bias_index=50)
fig1 = SpectroscopyPlotting.plot_cits_bias_slice(
    cits_data_dict['data_3d'], 
    cits_data_dict['bias_values'], 
    50
)
fig1.show()

# 3. 能帶圖 / Band diagram
line_data = extract_line_spectra_data(cits_data_dict, (10,10), (50,50))
fig2 = SpectroscopyPlotting.plot_band_diagram(
    line_data['line_spectra'],
    line_data['bias_values'],
    line_data['distances']
)
fig2.show()

# 4. 堆疊光譜 / Stacked spectra
stacked_data = prepare_stacked_spectra_data(
    line_data['line_spectra'], 
    line_data['bias_values']
)
fig3 = SpectroscopyPlotting.plot_stacked_spectra(
    stacked_data['selected_spectra'],
    stacked_data['bias_values'],
    offset_factor=1.5
)
fig3.show()
```

---

## 參數調整指南 / Parameter Tuning Guide

### CITS 偏壓切片 / CITS Bias Slice
- **bias_index**: 範圍 0 到 n_bias-1，通常選擇有趣的偏壓點
- **colorscale**: 建議 'Viridis' (通用)、'Hot' (電流強度)、'RdBu' (正負對比)

### 能帶圖 / Band Diagram
- **use_log_scale**: 當電流範圍很大時使用 True
- **colorscale**: 建議 'RdBu' (能帶對比)、'Spectral' (光譜)
- **distances**: 如果有實際物理距離，傳入奈米單位的陣列

### 堆疊光譜 / Stacked Spectra
- **offset_factor**: 0.5-2.0 之間，根據光譜密度調整
- **max_curves**: 10-30 之間，太多會造成視覺混亂
- **step_selection**: 'uniform' 適合一般情況，'endpoints' 強調端點

---

## 性能考量 / Performance Considerations

### 內存使用 / Memory Usage
- CITS 數據通常很大，建議分批處理大型數據集
- 使用 `max_curves` 參數限制同時顯示的曲線數

### 計算效率 / Computational Efficiency
- Bresenham 線採樣比插值方法快，適合互動使用
- 對數尺度計算會增加處理時間，僅在需要時使用

### 顯示性能 / Display Performance
- Plotly 圖形在數據點過多時會變慢
- 建議 CITS 切片不超過 200×200 像素
- 堆疊光譜曲線數控制在 30 條以內

---

## 擴展指南 / Extension Guide

### 添加新的數據提取函數 / Adding New Data Extraction Functions
1. 遵循統一的參數命名規範
2. 返回標準化的字典格式
3. 包含完整的錯誤處理和日誌記錄

### 添加新的繪圖函數 / Adding New Plotting Functions
1. 繼承 `SpectroscopyPlotting` 類別
2. 使用 `@staticmethod` 裝飾器
3. 支援 `**kwargs` 以便自定義參數
4. 返回 `go.Figure` 對象

### 自定義顏色方案 / Custom Color Schemes
- 使用 Plotly 內建顏色方案名稱
- 或定義自己的顏色列表: `['#color1', '#color2', ...]`
- 考慮色盲友好性和科學出版要求