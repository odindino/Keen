# SPM 數據分析系統測試指南
# SPM Data Analysis System Testing Guide

本指南說明如何測試和使用 SPM 數據分析系統
This guide explains how to test and use the SPM data analysis system

## 測試程式概覽 / Test Programs Overview

### 1. 快速演示 (demo.py)
快速展示系統的主要功能，適合初次了解系統
Quick demonstration of main system features, suitable for first-time users

### 2. 完整測試 (test_system.py)  
全面的系統功能測試，驗證所有組件的正確性
Comprehensive system functionality test, validates all components

## 環境準備 / Environment Setup

### 前置條件 / Prerequisites
```bash
# 確保已安裝 Python 3.12+ / Ensure Python 3.12+ is installed
python --version

# 安裝依賴套件 / Install dependencies
cd backend
pip install -r requirements.txt

# 或使用 conda 環境 / Or use conda environment
conda env create -f environment.yml
conda activate keen
```

## 運行測試 / Running Tests

### 方法 1: 快速演示 / Method 1: Quick Demo
```bash
cd backend
python demo.py
```

**預期輸出** / **Expected Output**:
```
🚀 SPM 數據分析系統演示
==================================================

📋 步驟 1: 初始化系統
✅ 系統初始化完成
   - 載入的分析器: ['int', 'cits']

📋 步驟 2: 載入實驗數據
   - 載入檔案: 20250521_Janus Stacking SiO2_13K_113.txt
✅ 實驗載入成功
   - INT 檔案數量: 8
   - DAT 檔案數量: 4

... (更多詳細輸出)

🎉 演示完成！
```

### 方法 2: 完整測試 / Method 2: Full Test
```bash
cd backend
python test_system.py
```

**預期輸出** / **Expected Output**:
```
🎯 SPM 數據分析系統測試報告
============================================================
總測試數: 6
通過測試: 6
失敗測試: 0
成功率: 100.0%
------------------------------------------------------------
✅ PASS initialization
✅ PASS load_experiment
✅ PASS int_analysis
✅ PASS cits_analysis
✅ PASS visualization
✅ PASS system_status
============================================================
🎉 所有測試都通過了！系統運行正常。
```

## 測試項目詳細說明 / Detailed Test Items

### 1. 系統初始化測試 / System Initialization Test
- 驗證 MainAnalyzer 正確初始化
- 確認所有分析器 (INT, CITS) 可用
- 檢查 AnalysisService 可用性

### 2. 實驗載入測試 / Experiment Loading Test  
- 自動載入 testfile 中的 TXT 檔案
- 解析關聯的 INT 和 DAT 檔案
- 驗證檔案關聯性和數據完整性

### 3. INT 分析測試 / INT Analysis Test
- **基本分析**: 地形數據統計和視覺化
- **平面化處理**: linewise_mean 方法
- **剖面提取**: 線段剖面分析
- **粗糙度計算**: Ra, Rq, Rz 等參數

### 4. CITS 分析測試 / CITS Analysis Test
- **基本分析**: 3D 光譜數據處理
- **線段剖面**: Bresenham 算法採樣
- **數據切割**: 偏壓段分離
- **光譜平滑**: 移動平均濾波
- **特徵檢測**: 峰值自動識別

### 5. 視覺化測試 / Visualization Test
- INT 數據的地形圖、剖面圖、統計圖
- CITS 數據的光譜圖、能帶圖、概覽圖
- 綜合分析儀表板生成

### 6. 系統狀態測試 / System Status Test
- 系統健康狀態檢查
- 實驗管理功能
- 分析器狀態監控

## 測試數據說明 / Test Data Description

系統使用 `testfile/` 目錄中的真實 SPM 數據進行測試：
The system uses real SPM data in the `testfile/` directory for testing:

```
testfile/
├── 20250521_Janus Stacking SiO2_13K_113.txt      # 主實驗參數檔案
├── *Topo*.int                                      # 地形數據檔案
├── *Lia1R*.int, *Lia1X*.int, *Lia1Y*.int         # 其他通道數據
├── *It_to_PC*.int                                 # 電流圖像
└── *_Matrix.dat                                   # CITS 光譜數據
```

## 故障排除 / Troubleshooting

### 常見問題 / Common Issues

#### 1. 導入錯誤 / Import Errors
```bash
ModuleNotFoundError: No module named 'core'
```
**解決方案** / **Solution**: 確保在 `backend/` 目錄下運行測試

#### 2. 數據檔案未找到 / Data Files Not Found
```bash
沒有找到 TXT 檔案
```
**解決方案** / **Solution**: 確認 `testfile/` 目錄存在且包含測試數據

#### 3. 依賴套件錯誤 / Dependency Errors
```bash
ImportError: No module named 'plotly'
```
**解決方案** / **Solution**: 安裝缺失的依賴套件
```bash
pip install plotly numpy scipy matplotlib
```

#### 4. 記憶體不足 / Memory Issues
如果處理大型數據時出現記憶體問題：
If memory issues occur when processing large data:
- 減少可視化的數據點數量
- 使用 `cache_enabled: false` 配置
- 分批處理大型數據集

### 調試模式 / Debug Mode

啟用詳細日誌輸出：
Enable verbose logging output:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

或修改 demo.py / test_system.py 中的日誌級別設定。

## 性能基準 / Performance Benchmarks

在標準測試環境中的預期性能：
Expected performance on standard test environment:

- **系統初始化**: < 2 秒
- **實驗載入**: < 5 秒 (8個 INT + 4個 DAT 檔案)
- **INT 分析**: < 3 秒 (512x512 圖像)
- **CITS 分析**: < 10 秒 (取決於光譜數據大小)
- **總測試時間**: < 30 秒

## 下一步 / Next Steps

測試通過後，您可以：
After tests pass, you can:

1. **自定義分析參數** - 修改 demo.py 中的分析參數
2. **載入自己的數據** - 將 SPM 數據放入 testfile 目錄
3. **擴展分析功能** - 基於現有架構添加新的分析方法
4. **整合到前端** - 將後端 API 與 Vue 前端整合

## 技術支援 / Technical Support

如有問題，請檢查：
If you encounter issues, please check:

1. 日誌檔案：`test_system.log`
2. 錯誤堆疊追蹤
3. 系統環境配置
4. 測試數據完整性

---

**版本**: v1.0  
**最後更新**: 2025-06-06  
**維護者**: KEEN 開發團隊