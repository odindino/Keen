# 測試目錄說明 / Test Directory Documentation

**作者 / Author**: Odindino  
**最後更新 / Last Updated**: 2025-06-07  
**版本 / Version**: 2.0 - 重新組織版

這個目錄包含了 KEEN SPM 數據分析系統的所有測試程式，現已重新組織以提供更清晰的結構。

## 📁 目錄結構 / Directory Structure

```
test/
├── README.md                    # 本說明文件
├── notebooks/                  # Jupyter 筆記本 / Jupyter Notebooks
│   ├── interactive_new_architecture_test.ipynb  # 新架構交互式測試
│   ├── IVdataprocess.ipynb                      # IV 數據處理
│   ├── cits_analysis_new.ipynb                  # CITS 分析
│   ├── datanalysis.ipynb                        # 數據分析
│   ├── intanalysis.ipynb                        # INT 分析  
│   ├── interactive_analysis_demo.ipynb          # 交互式分析演示
│   ├── new_architecture_demo.ipynb              # 新架構演示
│   └── new_architecture_demo_v2.ipynb           # 新架構演示 v2
├── demos/                       # 演示程式 / Demo Programs
│   ├── spm_system_demo.py                       # 系統功能演示
│   └── new_architecture_demo_v2.py              # 新架構演示腳本
├── unit_tests/                  # 單元測試 / Unit Tests
│   ├── test_basic_functionality.py              # 基本功能快速測試
│   └── test_analyzers_comprehensive.py          # 綜合分析器測試
├── integration_tests/           # 整合測試 / Integration Tests
│   └── (空 - 待添加)
└── legacy/                      # 舊版測試 / Legacy Tests
    ├── fliptimetest.py                          # 時間翻轉測試 (舊)
    └── sts_enhancement_test.py                  # STS 增強測試 (舊)
```

## 🧪 測試類別說明 / Test Category Description

### 1. 📓 Jupyter Notebooks

**目錄**: `notebooks/`

**用途**: 
- 交互式測試和開發
- 數據分析實驗
- 新功能原型開發
- 架構測試和驗證

**主要檔案**:
- **`interactive_new_architecture_test.ipynb`** - 🌟 新架構完整測試環境
- **`cits_analysis_new.ipynb`** - CITS 數據分析
- **`new_architecture_demo_v2.ipynb`** - 新架構功能演示

**使用方式**:
```bash
cd backend/test/notebooks
jupyter notebook
```

### 2. 🎭 演示程式 (Demos)

**目錄**: `demos/`

**用途**:
- 展示系統完整工作流程
- 用戶培訓和教學
- 功能演示和驗證

**檔案說明**:
- **`spm_system_demo.py`** - 系統功能完整演示
- **`new_architecture_demo_v2.py`** - 新架構功能演示腳本

**運行方式**:
```bash
cd backend/test/demos
python spm_system_demo.py
python new_architecture_demo_v2.py
```

### 3. 🔬 單元測試 (Unit Tests)

**目錄**: `unit_tests/`

**用途**:
- 測試個別組件功能
- 快速驗證核心功能
- 開發過程中的品質檢查

**檔案說明**:
- **`test_basic_functionality.py`** - 基本功能快速測試
- **`test_analyzers_comprehensive.py`** - 完整分析器測試

**運行方式**:
```bash
cd backend/test/unit_tests
python test_basic_functionality.py     # 快速測試
python test_analyzers_comprehensive.py # 完整測試
```

### 4. 🔗 整合測試 (Integration Tests)

**目錄**: `integration_tests/`

**用途**:
- 測試組件間的協作
- 端到端工作流程測試
- API 整合測試

**狀態**: 待開發

### 5. 📦 舊版測試 (Legacy)

**目錄**: `legacy/`

**用途**:
- 保存舊版測試程式
- 向後相容性測試
- 歷史參考

**檔案說明**:
- **`fliptimetest.py`** - 舊版時間翻轉測試
- **`sts_enhancement_test.py`** - 舊版 STS 增強測試

## 🚀 使用建議 / Usage Recommendations

### 日常開發工作流 (Daily Development Workflow)

1. **🏃‍♂️ 快速檢查**: 
   ```bash
   cd unit_tests && python test_basic_functionality.py
   ```

2. **🔬 詳細測試**:
   ```bash
   cd unit_tests && python test_analyzers_comprehensive.py
   ```

3. **📓 交互式開發**:
   ```bash
   cd notebooks && jupyter notebook interactive_new_architecture_test.ipynb
   ```

### 不同使用場景 (Different Use Cases)

| 場景 | 推薦工具 | 說明 |
|------|----------|------|
| 新功能開發 | `notebooks/` | 使用 Jupyter 進行原型開發 |
| 功能驗證 | `unit_tests/` | 快速單元測試 |
| 完整測試 | `unit_tests/` + `notebooks/` | 綜合測試 + 交互式驗證 |
| 用戶演示 | `demos/` | 完整工作流程展示 |
| 故障診斷 | `unit_tests/` → `notebooks/` | 由簡到詳的診斷流程 |

## 🎯 推薦測試順序 / Recommended Testing Order

### 新架構測試流程

1. **基礎功能驗證**:
   ```bash
   cd unit_tests
   python test_basic_functionality.py
   ```

2. **完整功能測試**:
   ```bash
   python test_analyzers_comprehensive.py
   ```

3. **交互式架構測試**:
   ```bash
   cd ../notebooks
   jupyter notebook interactive_new_architecture_test.ipynb
   ```

4. **演示驗證**:
   ```bash
   cd ../demos
   python new_architecture_demo_v2.py
   ```

## 📊 測試資料和結果 / Test Data and Results

### 測試資料來源 (Test Data Sources)
- **主要資料**: `testfile/` 目錄中的真實 SPM 數據
- **格式支援**: `.txt` (參數), `.int` (形貌), `.dat` (電性)

### 輸出結果 (Output Results)
- **JSON 報告**: `comprehensive_test_results.json`
- **Jupyter 輸出**: 交互式視覺化和分析結果
- **控制台日誌**: 實時狀態和錯誤信息

## 🔧 開發指南 / Development Guide

### 添加新測試 (Adding New Tests)

1. **選擇適當分類**:
   - 單元測試 → `unit_tests/`
   - 整合測試 → `integration_tests/`
   - 演示程式 → `demos/`
   - 互動開發 → `notebooks/`

2. **命名規範**:
   - 測試檔案: `test_*.py`
   - 演示檔案: `*_demo.py`
   - 筆記本: `*_analysis.ipynb` 或 `*_test.ipynb`

3. **文檔要求**:
   - 清晰的檔案說明
   - 使用方法範例
   - 更新本 README

### 測試最佳實踐 (Testing Best Practices)

- ✅ 使用有意義的測試和函數名稱
- ✅ 提供清晰的錯誤訊息和日誌
- ✅ 包含適當的異常處理
- ✅ 生成結構化的測試報告
- ✅ 遵循 PEP 8 程式碼風格
- ✅ 包含必要的文檔字串

## 🚨 故障排除 / Troubleshooting

### 常見問題 (Common Issues)

1. **檔案路徑問題**:
   ```bash
   # 確保在正確的目錄執行
   pwd  # 檢查當前目錄
   ls   # 檢查檔案是否存在
   ```

2. **模組導入失敗**:
   ```bash
   # 檢查 Python 路徑
   python -c "import sys; print(sys.path)"
   ```

3. **依賴庫問題**:
   ```bash
   # 重新安裝依賴
   pip install -r requirements.txt
   ```

### 除錯流程 (Debugging Process)

1. **基礎檢查** → 運行快速測試
2. **環境驗證** → 檢查 Python 環境和依賴
3. **數據驗證** → 確認測試數據完整性
4. **詳細診斷** → 使用 Jupyter notebook 進行互動式除錯

## 📝 更新日誌 / Change Log

### 2025-06-07 - v2.0 重新組織版
- 🔄 重新組織目錄結構
- 📁 創建專門的 notebooks, demos, unit_tests, integration_tests, legacy 資料夾
- 📚 完全重寫 README 文檔
- 🎯 明確不同測試類型的用途和使用方法
- ✨ 新增新架構測試支援

### 之前版本
- 基本測試程式和演示
- 初版目錄結構

---

**維護者**: Odindino  
**聯絡**: 如有問題請查看系統日誌或參考 [KEEN 後端架構完整手冊](../docs/BACKEND_MANUAL_COMPLETE.md)