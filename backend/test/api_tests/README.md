# API 測試檔案說明
# API Test Files Documentation

此資料夾包含與 KEEN SPM 簡化 API 相關的測試檔案。
This folder contains test files related to the KEEN SPM simplified API.

## 📁 檔案清單 / File List

### 🎯 主要測試檔案 / Main Test Files

1. **`test_api_mapping.py`** - API 映射功能測試
   - 測試短鍵到完整檔案名的映射系統
   - 驗證大小寫不敏感功能
   - 不載入實際數據，只測試映射機制

2. **`test_simplified_api.py`** - 簡化 API 基本功能測試
   - 測試 `session['TopoFwd']`, `session['TopoBwd']` 等基本訪問
   - 驗證 FileProxy 物件正確創建
   - 基礎功能驗證

3. **`test_complete_simplified_api.py`** - 完整簡化 API 演示
   - 完整的使用流程演示
   - 包含所有簡化 API 功能展示
   - 用於用戶教學和文檔參考

4. **`test_short_keys.py`** - 短鍵生成系統測試
   - 分析短鍵生成邏輯
   - 測試檔案名到短鍵的轉換
   - 調試映射系統

5. **`quick_test.py`** - 快速驗證腳本
   - 簡單的功能驗證
   - 用於快速測試 API 是否正常工作

## 🚀 使用方式 / Usage

### 運行單個測試
```bash
# 測試 API 映射功能
python backend/test/api_tests/test_api_mapping.py

# 測試簡化 API
python backend/test/api_tests/test_simplified_api.py

# 運行完整演示
python backend/test/api_tests/test_complete_simplified_api.py
```

### 快速驗證
```bash
# 快速檢查 API 是否工作
python backend/test/api_tests/quick_test.py
```

## 📋 測試範圍 / Test Coverage

- ✅ 短鍵映射系統 (Short key mapping system)
- ✅ 大小寫不敏感訪問 (Case-insensitive access)
- ✅ FileProxy 物件創建 (FileProxy object creation)
- ✅ 便利方法 (Convenience methods)
- ✅ 錯誤處理 (Error handling)

## 🔧 維護說明 / Maintenance Notes

這些測試檔案主要用於驗證 ExperimentSession 類中的簡化 API 功能：
- `__getitem__` 方法
- `_short_key_to_full_key_map` 映射系統
- `_normalize_key()` 大小寫處理
- 各種 `get_*_files()` 便利方法

當修改 ExperimentSession 類的相關功能時，請運行這些測試以確保向後兼容性。

---
📅 **最後更新**: 2025年6月10日  
🎯 **版本**: v1.0  
📝 **相關文件**: [實現報告](../../../IMPLEMENTATION_REPORT.md)
