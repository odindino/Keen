"""
算法工具模組
Algorithm utility module

提供統一的算法接口，整合各種數學和計算功能
Provides unified algorithm interface, integrating various mathematical and computational functions
"""

import numpy as np
from typing import List, Tuple, Union, Optional, Dict, Any
import logging

# 導入幾何運算模組 / Import geometry module
from ..mathematics.geometry import GeometryUtils

logger = logging.getLogger(__name__)


class AlgorithmUtils:
    """
    算法工具類 - 提供統一的算法接口
    Algorithm utility class - provides unified algorithm interface
    """
    
    # 直接暴露幾何運算功能 / Directly expose geometry functions
    bresenham_line = GeometryUtils.bresenham_line
    bresenham_line_numpy = GeometryUtils.bresenham_line_numpy
    interpolate_line_points = GeometryUtils.interpolate_line_points
    calculate_line_length = GeometryUtils.calculate_line_length
    dense_sampling_with_unique = GeometryUtils.dense_sampling_with_unique
    
    @staticmethod
    def moving_average(data: np.ndarray, window_size: int, 
                       mode: str = 'valid') -> np.ndarray:
        """
        移動平均濾波
        Moving average filter
        
        用於平滑數據，減少噪聲
        Used to smooth data and reduce noise
        
        Args:
            data: 輸入數據 / Input data
            window_size: 窗口大小 / Window size
            mode: 邊界處理模式 ('valid', 'same', 'full') / Boundary mode
            
        Returns:
            np.ndarray: 平滑後的數據 / Smoothed data
        """
        if window_size < 1:
            raise ValueError("窗口大小必須至少為 1 / Window size must be at least 1")
        
        if window_size == 1:
            return data.copy()
        
        # 使用卷積實現移動平均 / Implement moving average using convolution
        kernel = np.ones(window_size) / window_size
        
        if data.ndim == 1:
            return np.convolve(data, kernel, mode=mode)
        elif data.ndim == 2:
            # 對每一行應用移動平均 / Apply moving average to each row
            result = np.zeros_like(data) if mode == 'same' else None
            for i in range(data.shape[0]):
                smoothed = np.convolve(data[i], kernel, mode=mode)
                if mode == 'same':
                    result[i] = smoothed
                else:
                    if result is None:
                        result = np.zeros((data.shape[0], smoothed.shape[0]))
                    result[i] = smoothed
            return result
        else:
            raise ValueError("輸入數據維度必須是 1 或 2 / Input data dimension must be 1 or 2")
    
    @staticmethod
    def find_peaks(data: np.ndarray, 
                   prominence: Optional[float] = None,
                   distance: Optional[int] = None,
                   height: Optional[float] = None) -> Tuple[np.ndarray, Dict[str, np.ndarray]]:
        """
        尋找數據中的峰值
        Find peaks in data
        
        Args:
            data: 一維數據陣列 / 1D data array
            prominence: 峰值突出度閾值 / Peak prominence threshold
            distance: 峰值間最小距離 / Minimum distance between peaks
            height: 峰值最小高度 / Minimum peak height
            
        Returns:
            Tuple[np.ndarray, Dict]: (峰值索引, 峰值屬性) / (peak indices, peak properties)
        """
        from scipy.signal import find_peaks as scipy_find_peaks
        
        peaks, properties = scipy_find_peaks(data, 
                                           prominence=prominence,
                                           distance=distance,
                                           height=height)
        return peaks, properties
    
    @staticmethod
    def polynomial_fit_2d(x: np.ndarray, y: np.ndarray, z: np.ndarray, 
                         order: int = 1) -> Dict[str, Any]:
        """
        二維多項式擬合（用於平面校正）
        2D polynomial fitting (for plane correction)
        
        Args:
            x, y: 座標網格 / Coordinate grids
            z: 高度值 / Height values
            order: 多項式階數 (1=平面, 2=二次曲面) / Polynomial order
            
        Returns:
            Dict: 包含擬合係數和擬合平面 / Contains fit coefficients and fitted plane
        """
        # 將座標展平 / Flatten coordinates
        x_flat = x.flatten()
        y_flat = y.flatten()
        z_flat = z.flatten()
        
        # 構建設計矩陣 / Build design matrix
        if order == 1:
            # 線性：z = a*x + b*y + c
            A = np.column_stack([x_flat, y_flat, np.ones_like(x_flat)])
        elif order == 2:
            # 二次：z = a*x^2 + b*y^2 + c*x*y + d*x + e*y + f
            A = np.column_stack([
                x_flat**2, y_flat**2, x_flat*y_flat,
                x_flat, y_flat, np.ones_like(x_flat)
            ])
        else:
            raise ValueError(f"不支援的多項式階數：{order} / Unsupported polynomial order: {order}")
        
        # 最小二乘擬合 / Least squares fitting
        coeffs, residuals, rank, s = np.linalg.lstsq(A, z_flat, rcond=None)
        
        # 重建擬合平面 / Reconstruct fitted plane
        z_fit = A @ coeffs
        z_fit = z_fit.reshape(z.shape)
        
        return {
            'coefficients': coeffs,
            'fitted_surface': z_fit,
            'residuals': residuals,
            'order': order
        }
    
    @staticmethod
    def median_filter_2d(data: np.ndarray, size: int = 3) -> np.ndarray:
        """
        二維中值濾波
        2D median filter
        
        用於去除椒鹽噪聲
        Used to remove salt-and-pepper noise
        
        Args:
            data: 二維數據 / 2D data
            size: 濾波器大小 / Filter size
            
        Returns:
            np.ndarray: 濾波後的數據 / Filtered data
        """
        from scipy.ndimage import median_filter
        return median_filter(data, size=size)
    
    @staticmethod
    def gaussian_filter_2d(data: np.ndarray, sigma: float = 1.0) -> np.ndarray:
        """
        二維高斯濾波
        2D Gaussian filter
        
        用於平滑圖像
        Used to smooth images
        
        Args:
            data: 二維數據 / 2D data
            sigma: 高斯核標準差 / Gaussian kernel standard deviation
            
        Returns:
            np.ndarray: 濾波後的數據 / Filtered data
        """
        from scipy.ndimage import gaussian_filter
        return gaussian_filter(data, sigma=sigma)
    
    @staticmethod
    def calculate_roughness(data: np.ndarray, mask: Optional[np.ndarray] = None) -> Dict[str, float]:
        """
        計算表面粗糙度參數
        Calculate surface roughness parameters
        
        Args:
            data: 高度數據 / Height data
            mask: 可選的遮罩，標記有效區域 / Optional mask for valid regions
            
        Returns:
            Dict: 包含各種粗糙度參數 / Contains various roughness parameters
        """
        if mask is None:
            valid_data = data.flatten()
        else:
            valid_data = data[mask]
        
        if len(valid_data) == 0:
            return {
                'Ra': 0.0,  # 算術平均粗糙度 / Arithmetic average roughness
                'Rq': 0.0,  # 均方根粗糙度 / Root mean square roughness
                'Rz': 0.0,  # 最大高度差 / Maximum height difference
                'Rp': 0.0,  # 最大峰高 / Maximum peak height
                'Rv': 0.0,  # 最大谷深 / Maximum valley depth
            }
        
        # 計算平均值 / Calculate mean
        mean_height = np.mean(valid_data)
        
        # Ra: 算術平均粗糙度 / Arithmetic average roughness
        Ra = np.mean(np.abs(valid_data - mean_height))
        
        # Rq: 均方根粗糙度 / Root mean square roughness
        Rq = np.sqrt(np.mean((valid_data - mean_height)**2))
        
        # Rz: 最大高度差 / Maximum height difference
        Rz = np.max(valid_data) - np.min(valid_data)
        
        # Rp: 最大峰高 / Maximum peak height
        Rp = np.max(valid_data) - mean_height
        
        # Rv: 最大谷深 / Maximum valley depth
        Rv = mean_height - np.min(valid_data)
        
        return {
            'Ra': float(Ra),
            'Rq': float(Rq),
            'Rz': float(Rz),
            'Rp': float(Rp),
            'Rv': float(Rv),
            'mean': float(mean_height),
            'std': float(np.std(valid_data))
        }
    
    @staticmethod
    def remove_outliers(data: np.ndarray, 
                       method: str = 'iqr',
                       threshold: float = 1.5) -> Tuple[np.ndarray, np.ndarray]:
        """
        去除異常值
        Remove outliers
        
        Args:
            data: 輸入數據 / Input data
            method: 方法 ('iqr', 'zscore', 'percentile') / Method
            threshold: 閾值參數 / Threshold parameter
            
        Returns:
            Tuple[np.ndarray, np.ndarray]: (清理後的數據, 異常值遮罩) / (cleaned data, outlier mask)
        """
        data_flat = data.flatten()
        
        if method == 'iqr':
            # 四分位距方法 / Interquartile range method
            Q1 = np.percentile(data_flat, 25)
            Q3 = np.percentile(data_flat, 75)
            IQR = Q3 - Q1
            lower_bound = Q1 - threshold * IQR
            upper_bound = Q3 + threshold * IQR
            mask = (data >= lower_bound) & (data <= upper_bound)
            
        elif method == 'zscore':
            # Z-score 方法 / Z-score method
            mean = np.mean(data_flat)
            std = np.std(data_flat)
            z_scores = np.abs((data - mean) / std)
            mask = z_scores < threshold
            
        elif method == 'percentile':
            # 百分位數方法 / Percentile method
            lower = np.percentile(data_flat, threshold)
            upper = np.percentile(data_flat, 100 - threshold)
            mask = (data >= lower) & (data <= upper)
            
        else:
            raise ValueError(f"不支援的方法：{method} / Unsupported method: {method}")
        
        # 對異常值進行插值處理 / Interpolate outliers
        cleaned_data = data.copy()
        if not mask.all():
            from scipy.ndimage import binary_dilation
            # 擴展異常值區域以獲得更好的插值效果 / Expand outlier regions for better interpolation
            dilated_mask = binary_dilation(~mask, iterations=1)
            
            # 使用最近鄰插值 / Use nearest neighbor interpolation
            from scipy.interpolate import NearestNDInterpolator
            valid_points = np.argwhere(mask)
            valid_values = data[mask]
            
            if len(valid_points) > 0:
                interp = NearestNDInterpolator(valid_points, valid_values)
                invalid_points = np.argwhere(~mask)
                if len(invalid_points) > 0:
                    cleaned_data[~mask] = interp(invalid_points)
        
        return cleaned_data, mask