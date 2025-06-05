# 開發者指南 / Developer Guide

## 雙語言開發規範 / Bilingual Development Standards

本文件說明如何在 Keen 專案中進行雙語言開發，確保正體中文和英文使用者都能有效參與專案。

This document explains how to conduct bilingual development in the Keen project, ensuring that both Traditional Chinese and English users can effectively participate in the project.

## 目錄 / Table of Contents

1. [程式碼註解規範](#程式碼註解規範--code-comment-standards)
2. [文件撰寫標準](#文件撰寫標準--documentation-standards)
3. [命名慣例](#命名慣例--naming-conventions)
4. [錯誤訊息處理](#錯誤訊息處理--error-message-handling)
5. [測試撰寫規範](#測試撰寫規範--test-writing-standards)
6. [貢獻流程](#貢獻流程--contribution-workflow)

## 程式碼註解規範 / Code Comment Standards

### 類別文檔字串 / Class Docstrings

每個類別都應該包含雙語言描述：

Every class should include bilingual descriptions:

```python
class DataAnalyzer:
    """
    數據分析器基類
    Base data analyzer class
    
    此類別提供數據分析的基本功能和接口定義
    This class provides basic data analysis functionality and interface definitions
    
    Attributes:
        config (Dict): 配置參數 / Configuration parameters
        cache (Dict): 數據快取 / Data cache
        
    Example:
        analyzer = DataAnalyzer(config={'debug': True})
        result = analyzer.process(data)
    """
```

### 方法文檔字串 / Method Docstrings

所有公開方法都需要雙語言文檔：

All public methods require bilingual documentation:

```python
def process_data(self, data: np.ndarray, method: str = 'default') -> AnalysisResult:
    """
    處理輸入數據
    Process input data
    
    此方法對輸入的數據進行處理並返回分析結果
    This method processes the input data and returns analysis results
    
    Args:
        data (np.ndarray): 輸入數據陣列 / Input data array
        method (str): 處理方法名稱 / Processing method name
                     可選值：'default', 'advanced' / Options: 'default', 'advanced'
    
    Returns:
        AnalysisResult: 分析結果對象 / Analysis result object
                       包含處理後的數據和元數據 / Contains processed data and metadata
    
    Raises:
        ValueError: 當輸入數據格式無效時 / When input data format is invalid
        ProcessingError: 當處理過程發生錯誤時 / When processing encounters an error
        
    Example:
        >>> data = np.random.random((100, 100))
        >>> result = analyzer.process_data(data, method='advanced')
        >>> print(result.success)
        True
    """
```

### 內聯註解 / Inline Comments

重要的程式碼段落應該有雙語言註解：

Important code sections should have bilingual comments:

```python
def complex_calculation(self, data):
    # 第一步：數據正規化 / Step 1: Data normalization
    normalized_data = (data - np.mean(data)) / np.std(data)
    
    # 第二步：應用變換 / Step 2: Apply transformation
    transformed_data = self._apply_fft(normalized_data)
    
    # 第三步：結果後處理 / Step 3: Post-process results
    final_result = self._post_process(transformed_data)
    
    return final_result
```

## 文件撰寫標準 / Documentation Standards

### 文件結構 / Document Structure

所有主要文件都應該提供雙語版本：

All major documents should provide bilingual versions:

- `README.md` - 雙語混合格式 / Bilingual mixed format
- `ARCHITECTURE.md` - 正體中文版 / Traditional Chinese version
- `ARCHITECTURE_EN.md` - 英文版 / English version
- `API_REFERENCE.md` - 雙語混合格式 / Bilingual mixed format

### 標題格式 / Header Format

使用雙語標題格式：

Use bilingual header format:

```markdown
## 核心功能 / Core Features

### 數據載入 / Data Loading

#### 支援格式 / Supported Formats
```

### 程式碼範例 / Code Examples

文件中的程式碼範例應包含雙語註解：

Code examples in documentation should include bilingual comments:

```markdown
```python
# 創建分析器實例 / Create analyzer instance
analyzer = SPMAnalyzer(config={
    'debug': True,          # 啟用除錯模式 / Enable debug mode
    'cache_size': 1000      # 快取大小 / Cache size
})

# 載入數據 / Load data
data = analyzer.load_file('sample.dat')

# 執行分析 / Execute analysis
result = analyzer.analyze(data)
```
```

## 命名慣例 / Naming Conventions

### 變數和函數名稱 / Variable and Function Names

使用英文命名，配合註解說明：

Use English naming with comment explanations:

```python
# 推薦 / Recommended
scan_parameters = {}        # 掃描參數 / Scan parameters
analysis_result = None      # 分析結果 / Analysis result
processing_time = 0.0       # 處理時間 / Processing time

def calculate_roughness(data):  # 計算粗糙度 / Calculate roughness
    pass

def extract_line_profile(image, start, end):  # 提取線性剖面 / Extract line profile
    pass
```

### 類別名稱 / Class Names

使用清晰的英文類別名稱：

Use clear English class names:

```python
class SPMDataProcessor:     # SPM 數據處理器
class TopographyAnalyzer:   # 地形分析器
class SpectroscopyTool:     # 光譜工具
class CacheManager:         # 快取管理器
```

### 常數定義 / Constant Definitions

```python
# 分析類型常數 / Analysis type constants
ANALYSIS_TYPE_TOPOGRAPHY = 'topography'    # 地形分析
ANALYSIS_TYPE_SPECTROSCOPY = 'spectroscopy'  # 光譜分析
ANALYSIS_TYPE_CITS = 'cits'                # CITS 分析

# 檔案格式常數 / File format constants  
FORMAT_DAT = 'dat'          # DAT 格式
FORMAT_INT = 'int'          # INT 格式
FORMAT_TXT = 'txt'          # TXT 格式
```

## 錯誤訊息處理 / Error Message Handling

### 異常類別定義 / Exception Class Definition

```python
class SPMAnalysisError(Exception):
    """
    SPM 分析錯誤基類
    Base SPM analysis error class
    """
    def __init__(self, message_zh: str, message_en: str):
        self.message_zh = message_zh
        self.message_en = message_en
        super().__init__(f"{message_zh} / {message_en}")

class DataFormatError(SPMAnalysisError):
    """
    數據格式錯誤
    Data format error
    """
    pass

class ProcessingError(SPMAnalysisError):
    """
    處理錯誤
    Processing error
    """
    pass
```

### 錯誤訊息範例 / Error Message Examples

```python
def validate_data_format(data):
    if not isinstance(data, np.ndarray):
        raise DataFormatError(
            "輸入數據必須是 NumPy 陣列",
            "Input data must be a NumPy array"
        )
    
    if data.ndim not in [2, 3]:
        raise DataFormatError(
            f"數據維度必須是 2 或 3，得到 {data.ndim}",
            f"Data dimension must be 2 or 3, got {data.ndim}"
        )
```

## 測試撰寫規範 / Test Writing Standards

### 測試類別和方法命名 / Test Class and Method Naming

```python
class TestSPMDataProcessor:
    """
    SPM 數據處理器測試
    SPM data processor tests
    """
    
    def test_load_dat_file_success(self):
        """
        測試成功載入 DAT 檔案
        Test successful DAT file loading
        """
        pass
    
    def test_load_invalid_format_raises_error(self):
        """
        測試載入無效格式時拋出錯誤
        Test loading invalid format raises error
        """
        pass
```

### 測試數據和斷言 / Test Data and Assertions

```python
def test_calculate_roughness(self):
    """
    測試粗糙度計算
    Test roughness calculation
    """
    # 準備測試數據 / Prepare test data
    test_data = np.array([
        [1.0, 2.0, 3.0],
        [2.0, 3.0, 4.0],
        [3.0, 4.0, 5.0]
    ])
    
    # 執行計算 / Execute calculation
    result = self.processor.calculate_roughness(test_data)
    
    # 驗證結果 / Verify results
    assert 'Ra' in result, "結果應包含 Ra 值 / Result should contain Ra value"
    assert 'Rq' in result, "結果應包含 Rq 值 / Result should contain Rq value"
    assert result['Ra'] > 0, "Ra 值應為正數 / Ra value should be positive"
```

## 貢獻流程 / Contribution Workflow

### 1. 準備開發環境 / Setting Up Development Environment

```bash
# 克隆專案 / Clone project
git clone https://github.com/your-repo/keen.git
cd keen

# 創建開發環境 / Create development environment
conda env create -f backend/environment.yml
conda activate keen

# 安裝開發依賴 / Install development dependencies
pip install -r backend/requirements.txt
```

### 2. 分支管理 / Branch Management

```bash
# 創建功能分支 / Create feature branch
git checkout -b feature/your-feature-name

# 或創建修復分支 / Or create fix branch
git checkout -b fix/issue-description
```

### 3. 程式碼撰寫指導原則 / Code Writing Guidelines

1. **雙語註解優先** / **Bilingual comments first**
   - 所有公開 API 必須有雙語文檔 / All public APIs must have bilingual documentation
   - 重要邏輯段落需要雙語註解 / Important logic sections need bilingual comments

2. **測試驅動開發** / **Test-driven development**
   - 新功能必須有對應測試 / New features must have corresponding tests
   - 測試名稱和描述使用雙語 / Test names and descriptions use bilingual format

3. **程式碼品質** / **Code quality**
   - 使用 `black` 進行程式碼格式化 / Use `black` for code formatting
   - 使用 `flake8` 進行程式碼檢查 / Use `flake8` for code linting
   - 保持函數簡潔，單一職責 / Keep functions concise with single responsibility

### 4. 提交訊息格式 / Commit Message Format

使用雙語提交訊息：

Use bilingual commit messages:

```
feat: 新增 CITS 數據分析功能 / Add CITS data analysis functionality

- 實現 CITS 檔案解析 / Implement CITS file parsing
- 新增光譜提取方法 / Add spectrum extraction methods  
- 增加相關測試案例 / Add related test cases

Closes #123
```

### 5. Pull Request 指南 / Pull Request Guidelines

PR 描述應包含：

PR description should include:

```markdown
## 更改摘要 / Change Summary

簡要描述此 PR 的目的和更改內容
Brief description of the purpose and changes in this PR

## 技術細節 / Technical Details

### 新增功能 / Added Features
- 功能 1 描述 / Feature 1 description
- 功能 2 描述 / Feature 2 description

### 修復問題 / Fixed Issues
- 修復的問題描述 / Description of fixed issues

## 測試 / Testing

- [ ] 單元測試通過 / Unit tests pass
- [ ] 集成測試通過 / Integration tests pass
- [ ] 手動測試完成 / Manual testing completed

## 文件更新 / Documentation Updates

- [ ] API 文件已更新 / API documentation updated
- [ ] README 已更新 / README updated
- [ ] 範例程式碼已更新 / Example code updated

## 檢查清單 / Checklist

- [ ] 程式碼遵循雙語註解規範 / Code follows bilingual comment standards
- [ ] 所有測試通過 / All tests pass
- [ ] 文件已更新 / Documentation updated
- [ ] 無程式碼品質問題 / No code quality issues
```

## 工具和資源 / Tools and Resources

### 開發工具 / Development Tools

1. **程式碼編輯器 / Code Editor**
   - VS Code（推薦）/ VS Code (Recommended)
   - PyCharm
   - Vim/Neovim

2. **必要擴展 / Essential Extensions**
   - Python
   - Pylance
   - Black Formatter
   - GitLens

### 參考資源 / Reference Resources

1. **SPM 數據格式文件** / **SPM Data Format Documentation**
2. **NumPy 文件** / **NumPy Documentation**
3. **SciPy 文件** / **SciPy Documentation**
4. **Matplotlib 繪圖指南** / **Matplotlib Plotting Guide**

## 常見問題 / FAQ

### Q: 如何處理只會其中一種語言的情況？
### Q: How to handle cases where I only know one language?

A: 您可以先用您熟悉的語言撰寫，然後在 PR 中請求社群協助翻譯。我們鼓勵所有語言背景的開發者參與！

A: You can write in the language you're familiar with first, then request community help for translation in your PR. We encourage developers of all language backgrounds to participate!

### Q: 測試程式碼是否也需要雙語註解？
### Q: Do test codes also need bilingual comments?

A: 測試方法的文檔字串建議使用雙語，但內部註解可以使用單一語言。

A: Test method docstrings are recommended to be bilingual, but internal comments can use a single language.

### Q: 如何確保我的貢獻符合專案標準？
### Q: How to ensure my contribution meets project standards?

A: 請參考現有程式碼範例，使用專案提供的工具進行程式碼檢查，並在提交前運行所有測試。

A: Please refer to existing code examples, use the project's provided tools for code checking, and run all tests before submitting.

---

## 結語 / Conclusion

感謝您對 Keen 專案的貢獻！通過遵循這些雙語言開發規範，我們可以建立一個真正國際化的開源專案，讓全世界的 SPM 研究者都能受益。

Thank you for contributing to the Keen project! By following these bilingual development standards, we can build a truly internationalized open-source project that benefits SPM researchers worldwide.

如有任何問題，請隨時在 Issues 中提出或聯繫維護團隊。

If you have any questions, please feel free to raise them in Issues or contact the maintenance team.
