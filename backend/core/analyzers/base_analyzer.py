"""
分析器基類
Base analyzer class

提供所有分析器的共同基礎功能
Provides common base functionality for all analyzers
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List, Union
import logging
from datetime import datetime

from ..data_models import SPMData, AnalysisState

logger = logging.getLogger(__name__)


class BaseAnalyzer(ABC):
    """
    分析器基類
    Base analyzer class
    
    所有分析器都應該繼承此類並實現必要的方法
    All analyzers should inherit from this class and implement required methods
    """
    
    def __init__(self, data: SPMData):
        """
        初始化分析器
        Initialize analyzer
        
        Args:
            data: SPM 數據實例 / SPM data instance (TopoData, CitsData, StsData, TxtData)
        """
        self.data = data
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # 使用新的分析狀態管理 / Use new analysis state management
        self.state = AnalysisState(analyzer_type=self.__class__.__name__)
        self.state.initialized = True
        
        # 分析歷史 / Analysis history
        self.analysis_history: List[Dict] = []
        
        # 快取數據 / Cached data
        self.cached_results: Dict[str, Any] = {}
        
        self.logger.info(f"{self.__class__.__name__} 初始化完成，數據類型: {type(self.data).__name__}")
    
    @abstractmethod
    def analyze(self, **kwargs) -> Dict[str, Any]:
        """
        核心分析方法（抽象方法）
        Core analysis method (abstract)
        
        子類必須實現此方法，使用 self.data 進行分析
        Subclasses must implement this method, using self.data for analysis
        
        Args:
            **kwargs: 額外參數 / Additional parameters
            
        Returns:
            Dict: 分析結果 / Analysis results
        """
        pass
    
    def get_results(self) -> Dict[str, Any]:
        """
        獲取最新的分析結果
        Get latest analysis results
        
        Returns:
            Dict: 分析結果字典 / Analysis results dictionary
        """
        return self.state.last_analysis or {}
    
    def get_history(self) -> List[Dict]:
        """
        獲取分析歷史
        Get analysis history
        
        Returns:
            List[Dict]: 分析歷史列表 / Analysis history list
        """
        return self.analysis_history.copy()
    
    def clear_cache(self) -> None:
        """
        清理快取數據
        Clear cached data
        """
        self.cached_results.clear()
        self.logger.info("快取已清理")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        獲取快取信息
        Get cache information
        
        Returns:
            Dict: 快取信息 / Cache information
        """
        return {
            'cache_size': len(self.cached_results),
            'cached_keys': list(self.cached_results.keys()),
            'memory_usage_mb': self._estimate_cache_memory()
        }
    
    def _estimate_cache_memory(self) -> float:
        """
        估算快取記憶體使用量（簡單估算）
        Estimate cache memory usage (simple estimation)
        
        Returns:
            float: 記憶體使用量 MB / Memory usage in MB
        """
        import sys
        total_size = 0
        for value in self.cached_results.values():
            total_size += sys.getsizeof(value)
        return total_size / (1024 * 1024)  # Convert to MB
    
    def _record_analysis(self, result: Dict[str, Any], analysis_type: str = "unknown") -> None:
        """
        記錄分析結果到歷史
        Record analysis result to history
        
        Args:
            result: 分析結果 / Analysis result
            analysis_type: 分析類型 / Analysis type
        """
        record = {
            'timestamp': datetime.now().isoformat(),
            'analysis_type': analysis_type,
            'success': result.get('success', True),
            'result_summary': self._create_result_summary(result),
            'analyzer_class': self.__class__.__name__
        }
        
        self.analysis_history.append(record)
        self.state.record_analysis(result, analysis_type)
        
        # 限制歷史記錄數量 / Limit history size
        if len(self.analysis_history) > 50:
            self.analysis_history = self.analysis_history[-50:]
    
    def _create_result_summary(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        創建結果摘要
        Create result summary
        
        Args:
            result: 完整結果 / Full result
            
        Returns:
            Dict: 結果摘要 / Result summary
        """
        summary = {
            'success': result.get('success', True),
            'data_keys': list(result.get('data', {}).keys()) if 'data' in result else [],
            'has_errors': bool(result.get('errors', [])),
            'has_warnings': bool(result.get('warnings', []))
        }
        
        # 添加特定類型的摘要信息 / Add type-specific summary information
        if 'stats' in result:
            summary['stats_available'] = True
        if 'plot_data' in result:
            summary['plot_available'] = True
            
        return summary
    
    def _add_error(self, error_msg: str) -> None:
        """
        添加錯誤信息
        Add error message
        
        Args:
            error_msg: 錯誤信息 / Error message
        """
        self.state.add_error(error_msg)
        self.logger.error(f"{self.__class__.__name__}: {error_msg}")
    
    def _add_warning(self, warning_msg: str) -> None:
        """
        添加警告信息
        Add warning message
        
        Args:
            warning_msg: 警告信息 / Warning message
        """
        self.state.add_warning(warning_msg)
        self.logger.warning(f"{self.__class__.__name__}: {warning_msg}")
    
    def get_status(self) -> Dict[str, Any]:
        """
        獲取分析器狀態
        Get analyzer status
        
        Returns:
            Dict: 狀態信息 / Status information
        """
        return {
            'analyzer_type': self.__class__.__name__,
            'initialized': self.state.initialized,
            'analysis_count': self.state.analysis_count,
            'last_analysis_time': self.analysis_history[-1]['timestamp'] if self.analysis_history else None,
            'error_count': len(self.state.errors),
            'warning_count': len(self.state.warnings),
            'cache_info': self.get_cache_info(),
            'data_type': type(self.data).__name__
        }
    
    def reset(self) -> None:
        """
        重置分析器狀態
        Reset analyzer state
        """
        self.state = AnalysisState(analyzer_type=self.__class__.__name__)
        self.state.initialized = True
        self.analysis_history.clear()
        self.clear_cache()
        self.logger.info(f"{self.__class__.__name__} 已重置")
    
    def validate_input(self, **kwargs) -> bool:
        """
        驗證輸入數據
        Validate input data
        
        Args:
            **kwargs: 額外參數 / Additional parameters
            
        Returns:
            bool: 是否有效 / Whether valid
        """
        if self.data is None:
            self._add_error("數據不能為空")
            return False
        return True
    
    def _create_error_result(self, error_msg: str) -> Dict[str, Any]:
        """
        創建錯誤結果
        Create error result
        
        Args:
            error_msg: 錯誤信息 / Error message
            
        Returns:
            Dict: 錯誤結果 / Error result
        """
        return {
            'success': False,
            'error': error_msg,
            'data': {},
            'plots': {},
            'metadata': {
                'analyzer_type': self.__class__.__name__,
                'data_type': type(self.data).__name__
            }
        }