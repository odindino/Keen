# Keen

SPM (Scanning Probe Microscopy) 數據分析框架 / SPM Data Analysis Framework

## 概述 / Overview

Keen 是一個專為掃描探針顯微鏡（SPM）數據分析設計的高性能框架，採用模組化架構，## 授權 / License

本專案採用 MIT 授權條款，詳情請參閱 [LICENSE](LICENSE) 檔案。

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 聯絡方式 / Contact

如有任何問題或建議，歡迎透過以下方式聯絡：

For any questions or suggestions, please contact us through:

- GitHub Issues: [提交問題](https://github.com/yangziliang04/keen/issues)
- Email: yangziliang04@gmail.com數據處理能力。

Keen is a high-performance framework designed for Scanning Probe Microscopy (SPM) data analysis, featuring a modular architecture that provides professional scientific data processing capabilities.

## 特色功能 / Key Features

- **模組化設計** / **Modular Design**: 清晰的職責分離，易於維護和擴展 / Clear separation of responsibilities, easy to maintain and extend
- **高性能計算** / **High Performance**: 智能快取和記憶體管理 / Intelligent caching and memory management
- **多格式支援** / **Multi-format Support**: 
  - 目前支援 Anfatec Instruments AG SXM 系統的 TXT、INT、DAT、CITS、STS 等格式
  - Currently supports TXT, INT, DAT, CITS, STS formats from Anfatec Instruments AG SXM systems
  - 未來計劃支援 Nanonis、Bruker、Asylum(Oxford)、Park System 等 SPM 系統格式
  - Future support planned for Nanonis, Bruker, Asylum(Oxford), Park System SPM formats
- **專業視覺化** / **Professional Visualization**: SPM 專用的數據視覺化工具 / SPM-specific data visualization tools
- **雙語言支援** / **Bilingual Support**: 程式碼和文件提供中英文版本 / Code and documentation in both Chinese and English

## 文件 / Documentation

### 架構文件 / Architecture Documents
- [架構設計 (正體中文)](backend/ARCHITECTURE.md) - 完整的系統架構說明
- [Architecture Design (English)](backend/ARCHITECTURE_EN.md) - Complete system architecture documentation

### 環境配置 / Environment Setup
詳細的環境配置請參考：
For detailed environment setup, please refer to:
- [environment.yml](backend/environment.yml) - Conda 環境配置
- [requirements.txt](backend/requirements.txt) - 額外的 Python 套件

## 快速開始 / Quick Start

### 環境設置 / Environment Setup

```bash
# 創建 conda 環境 / Create conda environment
conda env create -f backend/environment.yml

# 激活環境 / Activate environment
conda activate keen

# 安裝額外依賴 / Install additional dependencies
pip install -r backend/requirements.txt
```

### 基本使用 / Basic Usage

```python
from core.analysis_service import AnalysisService

# 創建分析服務 / Create analysis service
service = AnalysisService()

# 創建分析器 / Create analyzer
analyzer = service.create_analyzer("path/to/experiment.txt")

# 分析數據檔案 / Analyze data file
result = analyzer.analyze_file("data.dat")
```

## 專案結構 / Project Structure

```
keen/
├── backend/                    # 後端核心 / Backend core
│   ├── core/                  # 核心模組 / Core modules
│   ├── test/                  # 測試套件 / Test suite
│   ├── ARCHITECTURE.md        # 架構文件 (中文)
│   ├── ARCHITECTURE_EN.md     # Architecture docs (English)
│   └── environment.yml        # 環境配置 / Environment config
├── frontend/                  # 前端介面 / Frontend interface
└── testfile/                  # 測試數據 / Test data
```

## 開發指南 / Development Guide

### 程式碼規範 / Code Standards

本專案採用雙語言註解規範：
This project uses bilingual comment standards:

```python
class SPMAnalyzer:
    """
    SPM 數據分析器
    SPM data analyzer
    
    負責協調 SPM 數據分析流程
    Coordinates SPM data analysis workflows
    """
    
    def process_data(self, data):
        """
        處理 SPM 數據
        Process SPM data
        """
        # 數據預處理 / Data preprocessing
        cleaned_data = self._clean_data(data)
        
        # 執行分析 / Execute analysis
        result = self._analyze(cleaned_data)
        
        return result
```

### 測試 / Testing

```bash
# 執行所有測試 / Run all tests
pytest backend/test/

# 執行單元測試 / Run unit tests
pytest backend/test/unit/

# 執行集成測試 / Run integration tests
pytest backend/test/integration/
```

## 貢獻 / Contributing

歡迎各界開發者貢獻！無論您使用正體中文或英文，都能參與開發：

Welcome developers to contribute! Whether you use Traditional Chinese or English, you can participate in development:

1. Fork 本專案 / Fork the project
2. 創建功能分支 / Create a feature branch
3. 提交變更 / Commit your changes
4. 推送到分支 / Push to the branch
5. 創建 Pull Request / Create a Pull Request

### 開發環境 / Development Environment

請確保您的開發環境包含：
Please ensure your development environment includes:

- Python >= 3.12
- 所有在 environment.yml 中列出的依賴 / All dependencies listed in environment.yml
- 適當的程式碼編輯器 / Appropriate code editor (VS Code recommended)

## 授權 / License

本專案採用 MIT 授權條款，詳情請參閱 [LICENSE](LICENSE) 檔案。

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 聯絡方式 / Contact

如有任何問題或建議，歡迎透過以下方式聯絡：

For any questions or suggestions, please contact us through:

- GitHub Issues: [提交問題](https://github.com/odindino/keen/issues)