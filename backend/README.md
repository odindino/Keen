# KEEN 後端系統 / KEEN Backend System

**作者 / Author**: Odindino  
**最後更新 / Last Updated**: 2025-06-07  
**版本 / Version**: 2.0 - 架構重組版

KEEN (Knowledge-Enhanced Exploration and Analysis) 是一個專為 SPM (掃描探針顯微鏡) 數據分析設計的現代化後端系統。

## 🏗️ 架構概述 / Architecture Overview

KEEN 採用「**類型管理器 + 檔案代理**」(Type Manager + File Proxy) 的現代化架構，提供統一、高效且可擴展的 SPM 數據處理能力。

### 核心特點 / Key Features

- 🔧 **統一的數據模型** - 標準化的數據結構和介面
- ⚡ **智能快取管理** - LRU 快取機制提升性能
- 🎯 **類型安全** - 完整的型別提示和驗證
- 🔄 **靈活的分析器** - 可插拔的分析模組系統
- 📊 **Plotly 視覺化** - 內建高品質圖表生成
- 🔗 **鏈式操作** - 直觀的 API 設計

## 📁 目錄結構 / Directory Structure

```
backend/
├── README.md                    # 本說明文件 / This README
├── main.py                      # 主程序入口 / Main program entry
├── api_mvp.py                   # API 層 / API layer
├── requirements.txt             # Python 依賴 / Python dependencies
├── environment.yml              # Conda 環境 / Conda environment
│
├── core/                        # 🧠 核心模組 / Core modules
│   ├── experiment_session.py   # 實驗會話管理 / Experiment session
│   ├── file_proxy.py            # 檔案代理 / File proxy
│   ├── type_managers.py         # 類型管理器 / Type managers
│   ├── data_models.py           # 數據模型 / Data models
│   ├── main_analyzer.py         # 主分析器 / Main analyzer
│   ├── analysis_service.py      # 分析服務 / Analysis service
│   │
│   ├── parsers/                 # 📋 檔案解析器 / File parsers
│   │   ├── txt_parser.py        # TXT 解析器
│   │   ├── int_parser.py        # INT 解析器
│   │   └── dat_parser.py        # DAT 解析器
│   │
│   ├── analyzers/               # 🔬 數據分析器 / Data analyzers
│   │   ├── base_analyzer.py     # 分析器基類
│   │   ├── txt_analyzer.py      # TXT 分析器
│   │   ├── int_analyzer.py      # INT 分析器
│   │   ├── cits_analyzer.py     # CITS 分析器
│   │   ├── dat_analyzer.py      # DAT 分析器
│   │   ├── sts_analyzer.py      # STS 分析器
│   │   └── fft_analyzer.py      # FFT 分析器
│   │
│   ├── analysis/                # 🧮 分析算法 / Analysis algorithms
│   │   ├── int_analysis.py      # INT 分析算法
│   │   ├── cits_analysis.py     # CITS 分析算法
│   │   └── profile_analysis.py  # 剖面分析算法
│   │
│   ├── visualization/           # 📊 視覺化模組 / Visualization
│   │   ├── spm_plots.py         # SPM 圖表
│   │   └── spectroscopy_plots.py # 光譜圖表
│   │
│   ├── mathematics/             # 📐 數學工具 / Math utilities
│   │   └── geometry.py          # 幾何計算
│   │
│   ├── utils/                   # 🔧 工具函數 / Utilities
│   │   └── algorithms.py        # 算法工具
│   │
│   └── examples/                # 📖 範例程式 / Examples
│       └── bilingual_code_example.py
│
├── docs/                        # 📚 文檔 / Documentation
│   ├── BACKEND_MANUAL_COMPLETE.md      # 完整使用手冊
│   ├── BACKEND_MANUAL.md                # 基本使用手冊
│   ├── ARCHITECTURE.md                  # 架構說明 (中文)
│   ├── ARCHITECTURE_EN.md               # 架構說明 (英文)
│   ├── DEVELOPER_GUIDE.md               # 開發者指南
│   └── README_TEST.md                   # 測試說明
│
├── diagrams/                    # 📈 架構圖表 / Architecture diagrams
│   ├── architecture_diagram.py         # 圖表生成器
│   ├── architecture_relationship_diagram.png  # 架構關聯圖
│   └── data_flow_diagram.png            # 數據流程圖
│
└── test/                        # 🧪 測試程式 / Tests
    ├── README.md                # 測試說明
    ├── notebooks/               # Jupyter 筆記本
    ├── demos/                   # 演示程式
    ├── unit_tests/              # 單元測試
    ├── integration_tests/       # 整合測試
    └── legacy/                  # 舊版測試
```

## 🚀 快速開始 / Quick Start

### 1. 環境設置 / Environment Setup

```bash
# 克隆項目 / Clone project
cd /path/to/keen/backend

# 安裝依賴 / Install dependencies
pip install -r requirements.txt

# 或使用 Conda / Or use Conda
conda env create -f environment.yml
conda activate keen
```

### 2. 基本使用 / Basic Usage

```python
from core.experiment_session import ExperimentSession

# 初始化會話 / Initialize session
session = ExperimentSession()

# 載入實驗檔案 / Load experiment file
session.load_txt_file("/path/to/experiment.txt")

# 獲取檔案代理 / Get file proxy
topo = session.get_file_proxy("TopoFwd.int")

# 執行分析 / Perform analysis
result = topo.analyzer.analyze()

# 查看結果 / View results
print(result['data']['statistics'])
```

### 3. 交互式測試 / Interactive Testing

```bash
# 啟動 Jupyter notebook
cd test/notebooks
jupyter notebook interactive_new_architecture_test.ipynb
```

## 📖 文檔指南 / Documentation Guide

| 文檔 | 用途 | 適合對象 |
|------|------|----------|
| [完整使用手冊](docs/BACKEND_MANUAL_COMPLETE.md) | 詳細 API 參考和範例 | 開發者、高級用戶 |
| [基本使用手冊](docs/BACKEND_MANUAL.md) | 基礎使用說明 | 新用戶 |
| [架構說明](docs/ARCHITECTURE.md) | 系統架構設計 | 開發者、架構師 |
| [開發者指南](docs/DEVELOPER_GUIDE.md) | 開發規範和貢獻指南 | 貢獻者 |
| [測試說明](test/README.md) | 測試程式使用指南 | 測試人員、開發者 |

## 🧪 測試和驗證 / Testing and Validation

### 快速測試 / Quick Test
```bash
cd test/unit_tests
python test_basic_functionality.py
```

### 完整測試 / Comprehensive Test
```bash
python test_analyzers_comprehensive.py
```

### 交互式測試 / Interactive Test
```bash
cd test/notebooks
jupyter notebook interactive_new_architecture_test.ipynb
```

## 🔧 支援的檔案格式 / Supported File Formats

| 格式 | 描述 | 解析器 | 分析器 |
|------|------|--------|--------|
| `.txt` | 實驗參數文件 | `TxtParser` | `TxtAnalyzer` |
| `.int` | 形貌數據文件 | `IntParser` | `IntAnalyzer` |
| `.dat` | 電性測量文件 | `DatParser` | `CitsAnalyzer`, `StsAnalyzer` |

## 📊 主要功能 / Main Features

### 🗺️ 形貌分析 (Topography Analysis)
- 平面化處理 (Flattening)
- 傾斜校正 (Tilt correction)
- 線段剖面提取 (Line profile extraction)
- 表面特徵檢測 (Surface feature detection)

### 🔬 光譜分析 (Spectroscopy Analysis)
- CITS 數據處理 (CITS data processing)
- STS 光譜分析 (STS spectrum analysis)
- 電導圖計算 (Conductance mapping)
- 能隙分析 (Band gap analysis)

### 📈 視覺化 (Visualization)
- 高品質 Plotly 圖表
- 交互式數據探索
- 多種圖表類型支援
- 自動化報告生成

## 🛠️ 開發指南 / Development Guide

### 架構原則 / Architecture Principles
1. **分離關注點** - 解析、分析、視覺化分離
2. **類型安全** - 完整的類型提示
3. **可測試性** - 模組化設計便於測試
4. **擴展性** - 易於添加新的檔案格式和分析方法

### 貢獻流程 / Contribution Workflow
1. Fork 項目
2. 創建功能分支
3. 添加測試
4. 更新文檔
5. 提交 Pull Request

## 📞 支援和聯絡 / Support and Contact

- **文檔**: 查看 `docs/` 目錄中的詳細文檔
- **問題報告**: 請提供詳細的錯誤日誌和重現步驟
- **功能請求**: 歡迎提出改進建議

## 📝 更新日誌 / Changelog

### 2025-06-07 - v2.0 架構重組版
- 🔄 重新組織目錄結構
- 📁 創建專門的 docs/ 和 diagrams/ 資料夾
- 📚 完善文檔系統
- 🧪 重新組織測試結構
- ✨ 新架構全面實施

### 之前版本 / Previous Versions
- v1.x - 基礎功能實現
- 早期版本 - 原型開發

---

**維護者**: Odindino  
**授權**: [MIT License]  
**項目首頁**: [KEEN Project](https://github.com/your-repo/keen)

關於更多詳細信息，請參考 [完整使用手冊](docs/BACKEND_MANUAL_COMPLETE.md)。