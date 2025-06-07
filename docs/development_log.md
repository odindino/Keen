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