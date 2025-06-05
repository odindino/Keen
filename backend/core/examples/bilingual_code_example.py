"""
雙語言程式碼註解規範範例
Bilingual Code Comment Standards Example

此檔案展示如何在 Keen 專案中撰寫符合雙語言規範的程式碼
This file demonstrates how to write code that follows bilingual standards in the Keen project
"""

import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class AnalysisResult:
    """
    分析結果數據結構
    Analysis result data structure
    
    此類別用於統一化所有分析方法的回傳結果格式
    This class is used to standardize the return result format for all analysis methods
    
    Attributes:
        success (bool): 分析是否成功 / Whether the analysis was successful
        data (Dict): 分析結果數據 / Analysis result data
        metadata (Dict): 元數據信息 / Metadata information
        errors (List[str]): 錯誤訊息列表 / List of error messages
    """
    success: bool
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    errors: List[str] = None
    
    def __post_init__(self):
        """初始化後處理 / Post-initialization processing"""
        if self.errors is None:
            self.errors = []


class SPMDataProcessor:
    """
    SPM 數據處理器
    SPM Data Processor
    
    這個類別提供了 SPM 數據的基本處理功能，包括數據載入、預處理和基本分析
    This class provides basic processing functions for SPM data, including data loading, 
    preprocessing, and basic analysis
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化 SPM 數據處理器
        Initialize SPM data processor
        
        Args:
            config: 配置參數字典 / Configuration parameter dictionary
                   包含處理器的各種設定 / Contains various processor settings
        """
        self.config = config or {}
        self.default_smoothing = self.config.get('smoothing', True)
        self.cache = {}  # 數據快取 / Data cache
    
    def load_data(self, filepath: str) -> np.ndarray:
        """
        載入 SPM 數據檔案
        Load SPM data file
        
        支援多種 SPM 數據格式的載入，包括 .dat, .int, .txt 等
        Supports loading various SPM data formats including .dat, .int, .txt, etc.
        
        Args:
            filepath (str): 檔案路徑 / File path
            
        Returns:
            np.ndarray: 載入的數據陣列 / Loaded data array
            
        Raises:
            FileNotFoundError: 當檔案不存在時 / When file does not exist
            ValueError: 當檔案格式不支援時 / When file format is not supported
        """
        # 檢查檔案是否存在 / Check if file exists
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"找不到檔案 / File not found: {filepath}")
        
        # 根據副檔名選擇解析方法 / Choose parsing method based on file extension
        extension = filepath.split('.')[-1].lower()
        
        if extension == 'dat':
            return self._load_dat_file(filepath)
        elif extension == 'int':
            return self._load_int_file(filepath)
        elif extension == 'txt':
            return self._load_txt_file(filepath)
        else:
            raise ValueError(f"不支援的檔案格式 / Unsupported file format: {extension}")
    
    def preprocess_data(self, data: np.ndarray, 
                       remove_outliers: bool = True,
                       apply_smoothing: bool = None) -> np.ndarray:
        """
        數據預處理
        Data preprocessing
        
        對原始 SPM 數據進行預處理，包括異常值移除、平滑化等操作
        Preprocess raw SPM data including outlier removal, smoothing, etc.
        
        Args:
            data (np.ndarray): 原始數據陣列 / Raw data array
            remove_outliers (bool): 是否移除異常值 / Whether to remove outliers
            apply_smoothing (bool): 是否應用平滑化 / Whether to apply smoothing
                                  預設使用配置中的設定 / Defaults to config setting
        
        Returns:
            np.ndarray: 預處理後的數據 / Preprocessed data
        """
        processed_data = data.copy()
        
        # 移除異常值 / Remove outliers
        if remove_outliers:
            processed_data = self._remove_outliers(processed_data)
        
        # 應用平滑化 / Apply smoothing
        if apply_smoothing or (apply_smoothing is None and self.default_smoothing):
            processed_data = self._apply_smoothing(processed_data)
        
        return processed_data
    
    def analyze_topography(self, data: np.ndarray) -> AnalysisResult:
        """
        地形分析
        Topography analysis
        
        分析 SPM 地形數據，計算表面粗糙度、高度分佈等統計特徵
        Analyze SPM topography data, calculate surface roughness, height distribution, 
        and other statistical features
        
        Args:
            data (np.ndarray): 地形數據陣列 / Topography data array
                              應為 2D 陣列 / Should be a 2D array
                              
        Returns:
            AnalysisResult: 包含分析結果的物件 / Object containing analysis results
                           - roughness: 表面粗糙度 / Surface roughness
                           - height_stats: 高度統計 / Height statistics
                           - gradient_info: 梯度信息 / Gradient information
        """
        try:
            # 輸入驗證 / Input validation
            if data.ndim != 2:
                raise ValueError("地形數據必須是 2D 陣列 / Topography data must be 2D array")
            
            # 計算表面粗糙度 / Calculate surface roughness
            roughness = self._calculate_roughness(data)
            
            # 計算高度統計 / Calculate height statistics  
            height_stats = {
                'mean': np.mean(data),           # 平均高度 / Mean height
                'std': np.std(data),             # 標準差 / Standard deviation
                'min': np.min(data),             # 最小值 / Minimum value
                'max': np.max(data),             # 最大值 / Maximum value
                'range': np.ptp(data)            # 範圍 / Range
            }
            
            # 計算梯度信息 / Calculate gradient information
            gradient_x, gradient_y = np.gradient(data)
            gradient_magnitude = np.sqrt(gradient_x**2 + gradient_y**2)
            
            gradient_info = {
                'mean_gradient': np.mean(gradient_magnitude),    # 平均梯度 / Mean gradient
                'max_gradient': np.max(gradient_magnitude),      # 最大梯度 / Maximum gradient
                'gradient_std': np.std(gradient_magnitude)       # 梯度標準差 / Gradient std
            }
            
            # 組織結果 / Organize results
            result_data = {
                'roughness': roughness,
                'height_statistics': height_stats,
                'gradient_information': gradient_info
            }
            
            metadata = {
                'data_shape': data.shape,        # 數據形狀 / Data shape
                'analysis_type': 'topography',   # 分析類型 / Analysis type
                'processing_date': datetime.now().isoformat()  # 處理日期 / Processing date
            }
            
            return AnalysisResult(
                success=True,
                data=result_data,
                metadata=metadata
            )
            
        except Exception as e:
            # 錯誤處理 / Error handling
            error_msg = f"地形分析失敗 / Topography analysis failed: {str(e)}"
            return AnalysisResult(
                success=False,
                data={},
                metadata={'analysis_type': 'topography'},
                errors=[error_msg]
            )
    
    def _calculate_roughness(self, data: np.ndarray) -> Dict[str, float]:
        """
        計算表面粗糙度參數
        Calculate surface roughness parameters
        
        私有方法，計算多種粗糙度指標
        Private method to calculate various roughness metrics
        """
        # 算術平均粗糙度 Ra / Arithmetic mean roughness Ra
        mean_height = np.mean(data)
        ra = np.mean(np.abs(data - mean_height))
        
        # 均方根粗糙度 Rq / Root mean square roughness Rq  
        rq = np.sqrt(np.mean((data - mean_height)**2))
        
        # 最大高度差 Rt / Maximum height difference Rt
        rt = np.max(data) - np.min(data)
        
        return {
            'Ra': ra,  # 算術平均粗糙度 / Arithmetic mean roughness
            'Rq': rq,  # 均方根粗糙度 / Root mean square roughness
            'Rt': rt   # 最大高度差 / Maximum height difference
        }
    
    def _remove_outliers(self, data: np.ndarray, threshold: float = 3.0) -> np.ndarray:
        """
        移除異常值 (使用 Z-score 方法)
        Remove outliers (using Z-score method)
        """
        z_scores = np.abs((data - np.mean(data)) / np.std(data))
        return np.where(z_scores > threshold, np.median(data), data)
    
    def _apply_smoothing(self, data: np.ndarray) -> np.ndarray:
        """
        應用高斯平滑
        Apply Gaussian smoothing
        """
        from scipy import ndimage
        return ndimage.gaussian_filter(data, sigma=1.0)


# 使用範例 / Usage Example
if __name__ == "__main__":
    """
    使用範例程式碼
    Example usage code
    """
    
    # 創建處理器實例 / Create processor instance
    processor = SPMDataProcessor({
        'smoothing': True,           # 啟用平滑化 / Enable smoothing
        'outlier_threshold': 3.0     # 異常值閾值 / Outlier threshold
    })
    
    # 模擬數據載入 / Simulate data loading
    # 在實際使用中，這裡會載入真實的 SPM 數據檔案
    # In actual use, this would load real SPM data files
    sample_data = np.random.random((100, 100)) * 10  # 模擬地形數據 / Simulated topography data
    
    # 執行分析 / Execute analysis
    result = processor.analyze_topography(sample_data)
    
    # 檢查結果 / Check results
    if result.success:
        print("分析成功 / Analysis successful")
        print(f"表面粗糙度 Ra / Surface roughness Ra: {result.data['roughness']['Ra']:.3f}")
        print(f"平均高度 / Mean height: {result.data['height_statistics']['mean']:.3f}")
    else:
        print("分析失敗 / Analysis failed")
        for error in result.errors:
            print(f"錯誤 / Error: {error}")
