# 測試目錄說明 / Test Directory Documentation

這個目錄包含了 SPM 數據分析系統的所有測試程式，按功能分類管理。

## 📁 目錄結構 / Directory Structure

```
test/
├── README.md                    # 本說明文件
├── unit/                        # 單元測試 / Unit Tests
│   └── test_analyzers_comprehensive.py  # 綜合分析器測試
├── quick/                       # 快速測試 / Quick Tests
│   └── test_basic_functionality.py      # 基本功能快速測試
├── demo/                        # 演示程式 / Demo Programs
│   └── spm_system_demo.py               # 系統功能演示
└── (existing files...)         # 現有的測試檔案
```

## 🧪 測試程式說明 / Test Programs Description

### 1. 綜合分析器測試 (Comprehensive)
**文件**: `unit/test_analyzers_comprehensive.py`

**用途**: 
- 完整測試所有分析器功能
- 生成詳細的測試報告和 JSON 結果
- 適合完整的功能驗證

**特點**:
- ✅ 測試 TXT、INT、DAT 分析器
- ✅ 測試額外功能（平面化、線段剖面等）
- ✅ 整合測試工作流
- ✅ 詳細的錯誤報告
- ✅ JSON 結果輸出

**運行方式**:
```bash
cd backend/test/unit
python test_analyzers_comprehensive.py
```

### 2. 快速基本功能測試 (Quick)
**文件**: `quick/test_basic_functionality.py`

**用途**:
- 快速驗證核心功能是否正常
- 適合開發過程中的快速檢查
- 簡潔的輸出結果

**特點**:
- ⚡ 快速執行
- ✅ 基本功能覆蓋
- 📊 簡潔報告
- 🎯 重點測試

**運行方式**:
```bash
cd backend/test/quick
python test_basic_functionality.py
```

### 3. 系統功能演示 (Demo)
**文件**: `demo/smp_system_demo.py`

**用途**:
- 展示系統完整工作流程
- 適合向用戶演示功能
- 教學和培訓用途

**特點**:
- 🎭 完整工作流演示
- 📖 詳細步驟說明
- 🎯 實際使用案例
- 👥 用戶友好輸出

**運行方式**:
```bash
cd backend/test/demo
python spm_system_demo.py
```

## 🚀 使用建議 / Usage Recommendations

### 開發階段 (Development)
1. **日常開發**: 使用快速測試驗證基本功能
2. **功能完成**: 使用綜合測試進行完整驗證
3. **演示需要**: 使用演示程式展示功能

### 測試順序 (Testing Order)
1. 🏃‍♂️ **快速測試** - 確保基本功能正常
2. 🔬 **綜合測試** - 詳細功能驗證
3. 🎭 **演示程式** - 完整工作流展示

### 測試資料 (Test Data)
所有測試程式都使用 `testfile/` 目錄中的實際 SPM 數據：
- `*.txt` - 實驗參數文件
- `*.int` - 形貌數據文件  
- `*.dat` - 電性測量數據文件

## 📊 測試結果 / Test Results

### 輸出文件 (Output Files)
- `comprehensive_test_results.json` - 綜合測試的詳細結果
- 控制台輸出 - 實時測試狀態和摘要

### 成功標準 (Success Criteria)
- ✅ 所有分析器基本功能正常
- ✅ 檔案解析無錯誤
- ✅ 數據分析結果合理
- ✅ 視覺化功能可用
- ✅ 整合工作流順暢

## 🔧 故障排除 / Troubleshooting

### 常見問題 (Common Issues)
1. **找不到測試文件**: 確保 `testfile/` 目錄存在且包含數據
2. **模組導入失敗**: 檢查 Python 路徑設置
3. **分析器初始化失敗**: 檢查依賴庫是否正確安裝

### 除錯建議 (Debugging Tips)
1. 先運行快速測試檢查基本功能
2. 查看詳細的錯誤日誌
3. 檢查測試數據文件完整性
4. 確認 Python 環境配置正確

## 📝 開發指南 / Development Guide

### 添加新測試 (Adding New Tests)
1. 選擇合適的分類目錄 (`unit/`, `quick/`, `demo/`)
2. 遵循現有的命名規範
3. 包含適當的文檔說明
4. 更新本 README 文件

### 測試最佳實踐 (Testing Best Practices)
- 使用有意義的測試名稱
- 提供清晰的錯誤訊息
- 包含適當的異常處理
- 生成有用的測試報告

---

**最後更新**: 2025-06-06  
**維護者**: Claude Code Assistant  
**聯絡**: 如有問題請查看系統日誌或聯絡開發團隊