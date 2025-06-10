# 開發紀錄 / Development Log

本文件記錄 KEEN 專案的開發歷程，以便追蹤和了解架構演進。  
This document records the development history of the KEEN project to track and understand architectural evolution.

---

## 2025-June-01

### 新增開發紀錄系統 / Development Logging System Added
- 建立 `docs/` 資料夾存放開發文件
- 創建 `development_log.md` 作為主要開發記錄檔案
- Created `docs/` folder for development documentation
- Created `development_log.md` as the main development log file

### 架構重構 / Architecture Refactoring
- 完成後端架構重構，建立模組化的分析系統
- 新增以下核心模組：
  - `analyzers/`: 各種分析器基礎類別和實作
  - `parsers/`: 檔案解析器（txt, int, dat）
  - `analysis/`: 進階分析功能（CITS, INT, Profile）
  - `visualization/`: 視覺化工具（Plotly圖表生成）
- Completed backend architecture refactoring with modular analysis system
- Added core modules:
  - `analyzers/`: Base classes and implementations for various analyzers
  - `parsers/`: File parsers (txt, int, dat)
  - `analysis/`: Advanced analysis features (CITS, INT, Profile)
  - `visualization/`: Visualization tools (Plotly chart generation)

### 新增架構示範筆記本 / Architecture Demo Notebook Added
- 創建 `backend/test/new_architecture_demo.ipynb` 展示新架構使用方式
- 包含以下示範內容：
  - MainAnalyzer 的初始化和使用
  - 載入和分析 testfile 中的測試數據
  - TXT 參數解析示範
  - INT 拓撲圖處理和視覺化
  - DAT/CITS 數據分析和 I-V 曲線提取
- Created `backend/test/new_architecture_demo.ipynb` to demonstrate new architecture usage
- Includes demos for:
  - MainAnalyzer initialization and usage
  - Loading and analyzing test data from testfile
  - TXT parameter parsing demo
  - INT topography processing and visualization
  - DAT/CITS data analysis and I-V curve extraction

---

## 2025-June-07

### 架構改進提案 V2 / Architecture Improvement Proposal V2
- 基於使用者體驗反饋，提出新的混合式架構方案
- 主要改進點：
  - 使用資料類別（dataclass）提供 IDE 友好的型別提示
  - 採用「型別管理器 + 檔案代理」模式改善資料存取體驗
  - 統一 Parser 輸出格式，建立標準化的 ParseResult
  - 明確劃分職責，每個管理器負責特定類型的檔案
- 新增 `docs/architecture_v2_proposal.md` 記錄詳細設計
- Based on user experience feedback, proposed new hybrid architecture
- Key improvements:
  - Use dataclasses for IDE-friendly type hints
  - Adopt "Type Manager + File Proxy" pattern for better data access
  - Standardize Parser output with unified ParseResult format
  - Clear separation of responsibilities with type-specific managers
- Added `docs/architecture_v2_proposal.md` for detailed design

### 新架構實作完成 / New Architecture Implementation Completed
- 完成新架構的核心實作，解決所有使用者體驗問題
- 新增檔案：
  - `backend/core/data_models.py` - 標準化資料模型，包含完整型別提示
  - `backend/core/type_managers.py` - 型別管理器架構，支援智能快取和延遲載入
  - `backend/core/file_proxy.py` - 檔案代理，提供直覺的屬性存取介面
  - `backend/core/experiment_session.py` - 主要入口類別，整合所有功能
- 修改檔案：
  - 統一所有 Parser 的輸出格式為 `ParseResult`
  - 重構 Type Manager 以適配新的解析結果
- 新增示範腳本：`backend/test/new_architecture_demo_v2.py`
- 實現的新功能：
  - IDE 友好的型別提示：`session['file'].data.attribute`
  - 完整的狀態管理和變數持久化
  - 統一的錯誤處理和資料格式
  - 智能快取和記憶體管理
  - 批次操作和搜尋功能
- Completed core implementation of new architecture, solving all UX issues
- New files:
  - `backend/core/data_models.py` - Standardized data models with full type hints
  - `backend/core/type_managers.py` - Type manager architecture with smart caching
  - `backend/core/file_proxy.py` - File proxy for intuitive property access
  - `backend/core/experiment_session.py` - Main entry class integrating all features
- Modified files:
  - Unified all Parser outputs to `ParseResult` format
  - Refactored Type Managers to adapt to new parse results
- Added demo script: `backend/test/new_architecture_demo_v2.py`
- New features implemented:
  - IDE-friendly type hints: `session['file'].data.attribute`
  - Complete state management and variable persistence
  - Unified error handling and data formats
  - Smart caching and memory management
  - Batch operations and search functionality

### 交互式測試環境創建 / Interactive Testing Environment Created
- 創建完整的 Jupyter notebook 測試環境：`backend/test/interactive_new_architecture_test.ipynb`
- 主要功能：
  - Widget 控制介面，支援檔案選擇和參數調節
  - 拓撲圖分析和 Plotly 視覺化（原始/平坦化圖像）
  - CITS 數據分析（偏壓切片、I-V 曲線繪製）
  - 綜合功能測試（記憶體管理、批次操作、搜尋功能）
- 修復 Plotly API 兼容性問題：
  - 修正 `SPMPlotting.plot_topography()` 中的 `update_yaxis()` 錯誤
  - 改用 `update_layout(yaxis=dict(scaleanchor="x", scaleratio=1))` 語法
- 修復圖像方向問題：
  - 添加 `autorange='reversed'` 修正 Plotly 默認的 Y 軸方向
  - 解決 SPM 圖像上下顛倒的問題
  - 同步修復拓撲圖和 CITS 偏壓切片的方向顯示
- 提供完整的新架構功能驗證環境
- Created complete Jupyter notebook testing environment: `backend/test/interactive_new_architecture_test.ipynb`
- Key features:
  - Widget control interface with file selection and parameter adjustment
  - Topography analysis and Plotly visualization (raw/flattened images)
  - CITS data analysis (bias slices, I-V curve plotting)
  - Comprehensive function testing (memory management, batch operations, search)
- Fixed Plotly API compatibility issues:
  - Corrected `update_yaxis()` error in `SPMPlotting.plot_topography()`
  - Changed to use `update_layout(yaxis=dict(scaleanchor="x", scaleratio=1))` syntax
- Fixed image orientation issues:
  - Added `autorange='reversed'` to correct Plotly's default Y-axis direction
  - Resolved SPM image upside-down display problem
  - Synchronized orientation fix for both topography and CITS bias slice visualization
- Provides complete validation environment for new architecture functionality

### 數據層級圖像方向修正完成 / Data-Level Image Orientation Fix Completed
- 根據用戶反饋，移除了 Plotly 層級的 Y 軸翻轉設定，改為在數據解析階段處理
- 修改內容：
  - `int_parser.py`: 添加 `np.flipud(image_data)` 確保拓撲圖正確方向
  - `dat_parser.py`: 正確集成 `prepare_cits_for_display()` 函數到 CITS 數據處理流程
  - `spm_plots.py`: 移除 Y 軸反轉設定，保持簡潔的 Plotly 配置
- 功能改進：
  - 確保所有 SPM 圖像座標系統統一：(0,0) 在左下角
  - 支援根據掃描方向智能調整 CITS 數據方向（upward/downward）
  - 移除冗餘的 `is_cits_data` 和 `_rotate_coordinates` 函數重複
- Based on user feedback, removed Plotly-level Y-axis reversal settings, changed to handle at data parsing stage
- Modifications:
  - `int_parser.py`: Added `np.flipud(image_data)` to ensure correct topography orientation
  - `dat_parser.py`: Properly integrated `prepare_cits_for_display()` function into CITS data processing flow
  - `smp_plots.py`: Removed Y-axis reversal settings, maintaining clean Plotly configuration
- Feature improvements:
  - Ensures unified SPM image coordinate system: (0,0) at bottom-left corner
  - Supports intelligent CITS data orientation adjustment based on scan direction (upward/downward)
  - Removed redundant `is_cits_data` and `_rotate_coordinates` function duplicates

---

## 2025-June-08

### INT 檔案互動式分析測試改進 / INT File Interactive Analysis Test Improvements
- 針對用戶反饋的 widget 載入問題，創建簡化版測試筆記本
- 移除所有 widget 依賴，改用直接修改程式碼的方式
- 新增檔案：`backend/test/notebooks/int_analysis_simple.ipynb`
- 主要特點：
  - 清晰的設定區域，標註修改位置
  - 正確使用 `ExperimentSession(txt_file_path)` 初始化
  - 保留完整功能：載入檔案、平面化、座標選擇、剖面生成
  - 使用 Plotly 進行所有視覺化
  - 提供雙視圖顯示（像素座標和物理座標）
- 修復的問題：
  - `ExperimentSession` 初始化時缺少必要參數
  - 檔案鍵值查找邏輯改進
  - 添加詳細的錯誤訊息和使用提示
- Created simplified test notebook based on user feedback about widget loading issues
- Removed all widget dependencies, changed to direct code modification approach
- New file: `backend/test/notebooks/int_analysis_simple.ipynb`
- Key features:
  - Clear configuration area with marked modification locations
  - Correct usage of `ExperimentSession(txt_file_path)` initialization
  - Full functionality retained: file loading, flattening, coordinate selection, profile generation
  - Uses Plotly for all visualizations
  - Provides dual-view display (pixel and physical coordinates)
- Fixed issues:
  - Missing required parameter in `ExperimentSession` initialization
  - Improved file key lookup logic
  - Added detailed error messages and usage hints

### CITS 分析與能帶/能譜圖測試筆記本創建 / CITS Analysis with Band/Spectrum Testing Notebooks Created
- 應用戶需求創建 CITS 影像分析和能帶/能譜圖測試工具
- 新增檔案：
  - `backend/test/notebooks/cits_analysis_with_profiles.ipynb` - 完整版（含 widgets）
  - `backend/test/notebooks/cits_analysis_simple.ipynb` - 簡化版（無 widgets）
- 主要功能：
  - CITS 檔案載入和基本資訊顯示
  - 偏壓切片顯示（可調整偏壓索引）
  - 單點能譜提取（I-V 曲線和 dI/dV 計算）
  - 能帶剖面分析（沿線提取光譜數據）
  - dI/dV map 計算和顯示
  - 分析位置標記和可視化
- 技術實現：
  - 直接從 CITS 數據提取能譜，無需額外分析器
  - 使用 Bresenham 算法進行線採樣
  - 數值微分計算 dI/dV
  - 多子圖布局顯示能帶圖、平均能譜和標準差
  - 雙視圖比較電流圖和 dI/dV 圖
- Created CITS image analysis and band/spectrum testing tools per user request
- New files:
  - `backend/test/notebooks/cits_analysis_with_profiles.ipynb` - Full version (with widgets)
  - `backend/test/notebooks/cits_analysis_simple.ipynb` - Simplified version (no widgets)
- Key features:
  - CITS file loading and basic information display
  - Bias slice display (adjustable bias index)
  - Single point spectrum extraction (I-V curves and dI/dV calculation)
  - Band profile analysis (line spectrum extraction)
  - dI/dV map calculation and display
  - Analysis position marking and visualization
- Technical implementation:
  - Direct spectrum extraction from CITS data without additional analyzers
  - Bresenham algorithm for line sampling
  - Numerical differentiation for dI/dV calculation
  - Multi-subplot layout showing band maps, average spectra and standard deviation
  - Dual-view comparison of current maps and dI/dV maps

### CITS 函式庫工作流程實現 / CITS Library Workflow Implementation
- 應用戶需求，完成基於函式庫的 CITS 分析工作流程
- 實現目標：最少自定義程式碼，使用標準化繪圖函數
- 新增檔案：
  - `backend/core/visualization/spectroscopy_plots.py` - 添加三個新繪圖函數
  - `backend/core/analysis/cits_analysis.py` - 添加四個數據提取輔助函數
  - `backend/test/cits_workflow_test.ipynb` - 函式庫導向的測試筆記本
  - `docs/cits_function_specifications.md` - 完整的函數規格說明書
- 新增繪圖函數：
  - `plot_cits_bias_slice()` - CITS 偏壓切片顯示（可調整索引）
  - `plot_band_diagram()` - 線剖面能帶圖（位置 vs 偏壓熱力圖）
  - `plot_stacked_spectra()` - 堆疊光譜圖（可調整偏移係數）
- 新增數據提取函數：
  - `extract_cits_bias_slice()` - 提取特定偏壓切片數據
  - `extract_line_spectra_data()` - 提取線剖面光譜數據（簡化版）
  - `extract_point_spectrum()` - 提取單點光譜數據（含 dI/dV 計算）
  - `prepare_stacked_spectra_data()` - 準備堆疊光譜數據（智能選擇）
- 工作流程特點：
  - 清晰的數據流：載入 → 提取 → 繪圖
  - 統一的函數介面和返回格式
  - 完整的錯誤處理和參數驗證
  - 支援所有主要的 CITS 視覺化需求
- 符合用戶需求：「有繪圖的函數，可以讓我丟進數據就產生圖片」
- Based on user requirements, completed library-based CITS analysis workflow
- Implementation goal: minimal custom code, using standardized plotting functions
- New files:
  - `backend/core/visualization/spectroscopy_plots.py` - Added three new plotting functions
  - `backend/core/analysis/cits_analysis.py` - Added four data extraction helper functions
  - `backend/test/cits_workflow_test.ipynb` - Library-oriented test notebook
  - `docs/cits_function_specifications.md` - Complete function specification document
- New plotting functions:
  - `plot_cits_bias_slice()` - CITS bias slice display (adjustable index)
  - `plot_band_diagram()` - Line profile band diagram (position vs bias heatmap)
  - `plot_stacked_spectra()` - Stacked spectra plot (adjustable offset factor)
- New data extraction functions:
  - `extract_cits_bias_slice()` - Extract specific bias slice data
  - `extract_line_spectra_data()` - Extract line profile spectra data (simplified)
  - `extract_point_spectrum()` - Extract single point spectrum data (with dI/dV calculation)
  - `prepare_stacked_spectra_data()` - Prepare stacked spectra data (intelligent selection)
- Workflow features:
  - Clear data flow: load → extract → plot
  - Unified function interfaces and return formats
  - Complete error handling and parameter validation
  - Support for all major CITS visualization requirements
- Meets user requirement: "functions that can take data and produce plots"

---

## 2025-June-10

### 簡化 API 實現與測試 / Simplified API Implementation and Testing

#### 🎯 主要任務完成 / Main Task Completion
- **問題發現**: 原本以為需要修復 `get_topo_files()` 等缺失方法
- **實際發現**: 簡化 API (`session['TopoFwd']`) 早已實現並正常工作
- **任務轉變**: 從「實現新功能」變為「發現、測試、文檔化現有功能」

#### ✅ 完成的工作 / Completed Work

**1. 便利方法完善 / Convenience Methods Enhancement**
- 添加 `get_int_files()` 方法（重命名自 `get_topo_files()` 以提高直觀性）
- 新增 `get_dat_files()` 方法（結合 CITS + STS 檔案）
- 保留並修復 `get_cits_files()`, `get_sts_files()`, `get_txt_files()` 方法
- 添加 FileProxy 兼容性屬性到 ExperimentSession 類

**2. 簡化 API 驗證 / Simplified API Validation**
- 確認 `session['TopoFwd']`, `session['TopoBwd']`, `session['It_to_PC_Matrix']` 完全可用
- 驗證大小寫不敏感功能：`session['topofwd']`, `session['TOPOBWD']` 等正常工作
- 測試 30+ 個自動生成的短鍵映射
- 驗證 `__getitem__` 方法和 `_short_key_to_full_key_map` 系統

**3. 綜合測試套件創建 / Comprehensive Test Suite Creation**
- 創建多個專門測試腳本驗證 API 功能
- 所有測試檔案已重新組織並移動到 `backend/test/` 適當資料夾

**4. 文檔更新 / Documentation Updates**
- 更新 `integrated_visualization_test.ipynb` 展示簡化 API 用法
- 創建 `IMPLEMENTATION_REPORT.md` 詳細記錄實現過程
- 提供完整的使用範例和最佳實踐指南

#### 📁 檔案組織改進 / File Organization Improvements

**測試檔案重新組織 / Test Files Reorganization**
- 創建 `backend/test/api_tests/` 專門存放 API 相關測試
- 移動檔案：
  - `test_api_mapping.py` → `backend/test/api_tests/`
  - `test_simplified_api.py` → `backend/test/api_tests/`
  - `test_complete_simplified_api.py` → `backend/test/api_tests/`
  - `test_short_keys.py` → `backend/test/api_tests/`
  - `quick_test.py` → `backend/test/api_tests/`
  - `test_session.py` → `backend/test/unit_tests/`
- 更新所有測試檔案的相對路徑導入
- 創建 `backend/test/api_tests/README.md` 說明各測試檔案用途

#### 🚀 技術成果 / Technical Achievements

**核心改進 / Core Improvements**
- **簡化語法**: 從 5-10 行檔案查找代碼縮減到 1 行直接訪問
- **直觀易懂**: 使用實際檔案名稱而非複雜路徑
- **大小寫友好**: 支援各種大小寫組合的訪問方式
- **統一接口**: 所有檔案類型使用相同的訪問模式
- **向後相容**: 不影響現有代碼的使用

**使用範例對比 / Usage Example Comparison**
```python
# 舊方式 (複雜)
int_files = session.get_int_files()
topofwd_file = None
for file_key in int_files:
    if 'TopoFwd' in file_key:
        topofwd_file = session[file_key]
        break

# 新方式 (簡化)
topofwd = session['TopoFwd']  # 一行搞定！
```

#### 📊 測試結果 / Test Results
- ✅ API 映射測試: 所有短鍵正確映射到完整檔案路徑
- ✅ 大小寫不敏感測試: 各種大小寫組合都正常工作
- ✅ 便利方法測試: 所有 `get_*_files()` 方法正常工作
- ✅ FileProxy 創建測試: 物件正確創建且屬性可訪問
- ✅ 向後相容性測試: 現有代碼不受影響

#### 📋 涉及檔案 / Files Involved
- **核心修改**: `backend/core/experiment_session.py`
- **測試檔案**: `backend/test/api_tests/` 下的所有檔案
- **文檔更新**: `integrated_visualization_test.ipynb`, `IMPLEMENTATION_REPORT.md`
- **新增文檔**: `backend/test/api_tests/README.md`

#### 🎉 最終狀態 / Final Status
**KEEN SPM 框架現在具備:**
- 完全功能的簡化 API (從複雜查找變為直接訪問)
- 全面的測試覆蓋 (映射、大小寫、相容性等)
- 完整的使用文檔 (範例、最佳實踐、故障排除)
- 組織良好的測試結構 (按功能分類的測試檔案)
- 向後相容性 (不破壞現有代碼)

**主要發現**: 簡化 API 功能早已存在於現有代碼庫中，通過 `__getitem__` 方法和短鍵映射系統實現。任務的重點從「實現新功能」轉移到「發現和記錄現有功能」，使 API 對用戶更加友好。

---

## 開發規範 / Development Guidelines

### 記錄格式 / Log Format
每個條目應包含：
- 日期
- 簡短標題
- 詳細描述（中英雙語）
- 涉及的檔案或模組
- 重要的決策原因

Each entry should include:
- Date
- Short title
- Detailed description (bilingual)
- Files or modules involved
- Important decision rationale

### 更新頻率 / Update Frequency
- 每次重大功能新增或修改
- 架構變更
- 重要的 bug 修復
- API 變更

- Major feature additions or modifications
- Architecture changes
- Important bug fixes
- API changes