# backend/core/analysis/int_analysis.py
import numpy as np
import logging
from scipy import ndimage, fftpack
import matplotlib.pyplot as plt
import io
import base64
import plotly.graph_objects as go
from plotly.io import to_image
import plotly.io as pio

# 導入我們的算法工具 / Import our algorithm tools
from ..utils.algorithms import AlgorithmUtils
from ..mathematics.geometry import GeometryUtils

# 設置預設輸出格式為網頁
pio.templates.default = "plotly_white"

logger = logging.getLogger(__name__)

class IntAnalysis:
    """
    提供SPM .int檔案的各種分析功能
    
    這個類提供各種形貌圖的分析工具，包括平面化、傾斜調整、線性剖面等功能。
    所有方法都設計為不改變原始數據，而是返回處理後的新數據。
    """
    
    @staticmethod
    def linewise_flatten_mean(image_data):
        """
        按行減去均值進行平面化
        
        Args:
            image_data: 2D numpy數組，形貌數據
            
        Returns:
            2D numpy數組，平面化後的數據
        """
        try:
            result = image_data.copy()
            for i in range(len(result)):
                result[i] -= np.mean(result[i])
            return result
        except Exception as e:
            logger.error(f"線性平面化(均值)失敗: {str(e)}")
            return image_data
    
    @staticmethod
    def linewise_flatten_polyfit(image_data, deg=1):
        """
        按行使用多項式擬合進行平面化
        
        Args:
            image_data: 2D numpy數組，形貌數據
            deg: 多項式階數
            
        Returns:
            2D numpy數組，平面化後的數據
        """
        try:
            result = image_data.copy()
            y_size, x_size = result.shape
            x = np.arange(x_size)
            
            for i in range(y_size):
                fit = np.polyfit(x, result[i], deg)
                poly = np.poly1d(fit)
                result[i] -= poly(x)
            
            return result
        except Exception as e:
            logger.error(f"線性平面化(多項式)失敗: {str(e)}")
            return image_data
    
    @staticmethod
    def plane_flatten(image_data):
        """
        全局平面擬合並去除平面
        
        Args:
            image_data: 2D numpy數組，形貌數據
            
        Returns:
            2D numpy數組，平面化後的數據
        """
        try:
            result = image_data.copy()
            y_size, x_size = result.shape
            
            # 創建坐標網格
            x, y = np.meshgrid(np.arange(x_size), np.arange(y_size))
            x = x.flatten()
            y = y.flatten()
            z = result.flatten()
            
            # 擬合平面 z = ax + by + c
            A = np.column_stack((x, y, np.ones_like(x)))
            coeffs, _, _, _ = np.linalg.lstsq(A, z, rcond=None)
            
            # 根據擬合結果創建平面
            plane = coeffs[0] * x.reshape(y_size, x_size) + coeffs[1] * y.reshape(y_size, x_size) + coeffs[2]
            
            # 從原始數據中減去平面
            result -= plane
            
            return result
        except Exception as e:
            logger.error(f"平面擬合失敗: {str(e)}")
            return image_data
    
    @staticmethod
    def tilt_image(image_data, direction, step_size=10, fine_tune=False):
        """
        調整影像傾斜
        
        Args:
            image_data: 2D numpy數組，形貌數據
            direction: 傾斜方向 ('up', 'down', 'left', 'right')
            step_size: 調整步長
            fine_tune: 是否為微調模式
            
        Returns:
            2D numpy數組，調整後的數據
        """
        try:
            result = image_data.copy()
            y_size, x_size = result.shape
            
            # 計算調整變化量
            zmin, zmax = np.min(result), np.max(result)
            dh = (zmax - zmin) / (50 if fine_tune else 10)
            
            # 創建坐標網格
            y, x = np.meshgrid(np.arange(x_size), np.arange(y_size))
            
            # 計算中心點
            center_x = (x_size - 1) / 2
            center_y = (y_size - 1) / 2
            
            # 創建調整矩陣
            if direction in ('up', 'down'):
                dhMatrix = dh * (x - center_y) / center_y
                if direction == 'up':
                    result += dhMatrix
                else:  # direction == 'down'
                    result -= dhMatrix
            elif direction in ('left', 'right'):
                dhMatrix = dh * (y - center_x) / center_x
                if direction == 'left':
                    result += dhMatrix
                else:  # direction == 'right'
                    result -= dhMatrix
            
            return result
        except Exception as e:
            logger.error(f"傾斜調整失敗: {str(e)}")
            return image_data
    
    @staticmethod
    def get_line_profile(image_data, start_point, end_point, physical_scale=1.0):
        """
        獲取兩點間的線性剖面
        
        Args:
            image_data: 2D numpy數組，形貌數據
            start_point: 起始點座標 (y, x)
            end_point: 終止點座標 (y, x)
            physical_scale: 物理單位尺度 (nm/pixel)
            
        Returns:
            dict: 包含剖面數據的字典
                - 'distance': 距離數組
                - 'height': 高度數組
                - 'length': 剖面總長度
                - 'stats': 統計數據
        """
        try:
            # 確保點座標在圖像範圍內
            y_size, x_size = image_data.shape
            start_y, start_x = max(0, min(start_point[0], y_size-1)), max(0, min(start_point[1], x_size-1))
            end_y, end_x = max(0, min(end_point[0], y_size-1)), max(0, min(end_point[1], x_size-1))
            
            # 計算剖面點數 (適當密度)
            length = np.sqrt((end_x - start_x)**2 + (end_y - start_y)**2)
            num_points = int(np.ceil(length)) * 2  # 確保足夠的取樣點
            
            # 生成剖面點
            y_indices = np.linspace(start_y, end_y, num_points)
            x_indices = np.linspace(start_x, end_x, num_points)
            
            # 用雙線性插值獲取對應高度值
            zi = ndimage.map_coordinates(image_data, [y_indices, x_indices], order=1)
            
            # 物理距離
            physical_length = length * physical_scale
            distances = np.linspace(0, physical_length, num_points)
            
            # 計算統計數據
            stats = {
                'min': float(np.min(zi)),
                'max': float(np.max(zi)),
                'mean': float(np.mean(zi)),
                'median': float(np.median(zi)),
                'std': float(np.std(zi)),
                'range': float(np.max(zi) - np.min(zi)),
                'rms': float(np.sqrt(np.mean(np.square(zi - np.mean(zi)))))
            }
            
            return {
                'distance': distances.tolist(),
                'height': zi.tolist(),
                'length': float(physical_length),
                'stats': stats
            }
        except Exception as e:
            logger.error(f"獲取剖面失敗: {str(e)}")
            return {
                'distance': [],
                'height': [],
                'length': 0,
                'stats': {}
            }
    
    @staticmethod
    def generate_profile_image(profile_data, shift_zero=False, title="Line Profile"):
        """
        生成剖面圖像
        
        Args:
            profile_data: 剖面數據字典
            shift_zero: 是否將最小值歸零
            title: 圖像標題
            
        Returns:
            base64編碼的PNG圖像
        """
        try:
            x = np.array(profile_data['distance'])
            z = np.array(profile_data['height'])
            
            # 是否將最小值歸零
            if shift_zero and len(z) > 0:
                z = z - np.min(z)
            
            # 使用Plotly創建圖像
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=x,
                y=z,
                mode='lines',
                name='Height Profile',
                line=dict(color='royalblue', width=2)
            ))
            
            # 設置佈局
            fig.update_layout(
                title=title,
                xaxis_title=f'Distance (nm)',
                yaxis_title=f'Height (nm)',
                autosize=True,
                width=800,
                height=400,
                margin=dict(l=50, r=50, t=50, b=50),
                showlegend=False,
                plot_bgcolor='white'
            )
            
            # 添加網格線
            fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
            
            # 添加統計信息
            if 'stats' in profile_data and profile_data['stats']:
                stats = profile_data['stats']
                annotation_text = f"Range: {stats['range']:.2f} nm, RMS: {stats['rms']:.2f} nm"
                fig.add_annotation(
                    x=0.02,
                    y=0.02,
                    xref="paper",
                    yref="paper",
                    text=annotation_text,
                    showarrow=False,
                    align="left",
                    bgcolor="rgba(255, 255, 255, 0.8)",
                    bordercolor="gray",
                    borderwidth=1,
                    borderpad=4,
                    font=dict(size=10)
                )
            
            # 將圖像轉換為PNG並進行base64編碼
            img_bytes = to_image(fig, format='png', width=800, height=400)
            img_base64 = base64.b64encode(img_bytes).decode('utf-8')
            
            return img_base64
        except Exception as e:
            logger.error(f"生成剖面圖像失敗: {str(e)}")
            return ""
            
    @staticmethod
    def generate_topo_plot(image_data, dimensions=None, title="Topography", colormap="Oranges", phys_unit="nm"):
        """
        使用Plotly生成SPM形貌圖
        
        Args:
            image_data: 2D numpy數組，形貌數據
            dimensions: 掃描尺寸 (x_range, y_range) 或 None
            title: 圖像標題
            colormap: 顏色映射名稱
            phys_unit: 物理單位
            
        Returns:
            plotly.graph_objects.Figure對象
        """
        try:
            # 獲取數據尺寸
            y_size, x_size = image_data.shape
            
            # 如果提供了尺寸信息，創建對應的坐標軸
            if dimensions and len(dimensions) == 2:
                x_range, y_range = dimensions
                x = np.linspace(0, x_range, x_size)
                y = np.linspace(0, y_range, y_size)
            else:
                x = np.arange(x_size)
                y = np.arange(y_size)
            
            # 創建heatmap圖
            fig = go.Figure(data=go.Heatmap(
                z=image_data,
                x=x,
                y=y,
                colorscale=colormap,
                colorbar=dict(
                    title=f'Height ({phys_unit})',
                    titleside='right',
                    titlefont=dict(size=14)
                )
            ))
            
            # 設置佈局
            fig.update_layout(
                title=title,
                xaxis_title=f'X ({phys_unit})',
                yaxis_title=f'Y ({phys_unit})',
                xaxis=dict(
                    scaleanchor="y",
                    constrain='domain'
                ),
                autosize=True,
                width=700,
                height=600,
                margin=dict(l=65, r=50, t=90, b=65)
            )
            
            return fig
        except Exception as e:
            logger.error(f"生成形貌圖失敗: {str(e)}")
            raise
            
    @staticmethod
    def generate_topo_image(image_data, dimensions=None, title="Topography", colormap="Oranges", phys_unit="nm"):
        """
        使用Plotly生成SPM形貌圖並轉換為base64圖像
        
        Args:
            image_data: 2D numpy數組，形貌數據
            dimensions: 掃描尺寸 (x_range, y_range) 或 None
            title: 圖像標題
            colormap: 顏色映射名稱
            phys_unit: 物理單位
            
        Returns:
            base64編碼的PNG圖像
        """
        try:
            # 使用generate_topo_plot生成圖形
            fig = IntAnalysis.generate_topo_plot(
                image_data, dimensions, title, colormap, phys_unit
            )
            
            # 轉換為PNG並進行base64編碼
            img_bytes = to_image(fig, format='png', width=700, height=600, scale=1.5)
            img_base64 = base64.b64encode(img_bytes).decode('utf-8')
            
            return img_base64
        except Exception as e:
            logger.error(f"生成形貌圖圖像失敗: {str(e)}")
            return ""
            
    @staticmethod
    def get_topo_stats(image_data):
        """
        計算形貌數據的基本統計信息
        
        Args:
            image_data: 2D numpy數組，形貌數據
            
        Returns:
            dict: 包含統計數據的字典
        """
        try:
            # 移除NaN值進行計算
            valid_data = image_data[~np.isnan(image_data)]
            
            stats = {
                "min": float(np.min(valid_data)),
                "max": float(np.max(valid_data)),
                "mean": float(np.mean(valid_data)),
                "median": float(np.median(valid_data)),
                "std": float(np.std(valid_data)),
                "rms": float(np.sqrt(np.mean(np.square(valid_data - np.mean(valid_data)))))
            }
            
            return stats
        except Exception as e:
            logger.error(f"計算統計數據失敗: {str(e)}")
            return {
                "min": 0.0,
                "max": 0.0,
                "mean": 0.0,
                "median": 0.0,
                "std": 0.0,
                "rms": 0.0
            }

    @staticmethod
    def calculate_surface_roughness(image_data, mask=None):
        """
        計算表面粗糙度參數
        Calculate surface roughness parameters
        
        使用我們的算法庫計算標準粗糙度參數
        Uses our algorithm library to calculate standard roughness parameters
        
        Args:
            image_data: 2D numpy數組，形貌數據 / 2D numpy array, topography data
            mask: 可選遮罩，標記有效區域 / Optional mask for valid regions
            
        Returns:
            dict: 包含各種粗糙度參數 / Contains various roughness parameters
        """
        try:
            return AlgorithmUtils.calculate_roughness(image_data, mask)
        except Exception as e:
            logger.error(f"粗糙度計算失敗: {str(e)}")
            return {
                'Ra': 0.0, 'Rq': 0.0, 'Rz': 0.0, 
                'Rp': 0.0, 'Rv': 0.0, 'mean': 0.0, 'std': 0.0
            }

    @staticmethod
    def get_line_profile_bresenham(image_data, start_point, end_point, physical_scale=1.0, method='bresenham'):
        """
        使用 Bresenham 算法或插值獲取線性剖面
        Get line profile using Bresenham algorithm or interpolation
        
        Args:
            image_data: 2D numpy數組，形貌數據 / 2D numpy array, topography data
            start_point: 起始點座標 (y, x) / Start point coordinates (y, x)
            end_point: 終止點座標 (y, x) / End point coordinates (y, x)
            physical_scale: 物理單位尺度 (nm/pixel) / Physical scale (nm/pixel)
            method: 採樣方法 ('bresenham', 'interpolation') / Sampling method
            
        Returns:
            dict: 包含剖面數據的字典 / Dictionary containing profile data
        """
        try:
            # 確保點座標在圖像範圍內 / Ensure points are within image bounds
            y_size, x_size = image_data.shape
            start_y, start_x = max(0, min(start_point[0], y_size-1)), max(0, min(start_point[1], x_size-1))
            end_y, end_x = max(0, min(end_point[0], y_size-1)), max(0, min(end_point[1], x_size-1))
            
            if method == 'bresenham':
                # 使用 Bresenham 算法獲取離散像素點 / Use Bresenham algorithm for discrete pixels
                x_coords, y_coords = GeometryUtils.bresenham_line_numpy((start_x, start_y), (end_x, end_y))
                
                # 確保座標在範圍內 / Ensure coordinates are within bounds
                x_coords = np.clip(x_coords, 0, x_size-1)
                y_coords = np.clip(y_coords, 0, y_size-1)
                
                # 直接從像素點獲取高度值 / Get height values directly from pixels
                heights = image_data[y_coords, x_coords]
                
                # 計算距離 / Calculate distances
                pixel_distances = np.sqrt(np.diff(x_coords.astype(float))**2 + np.diff(y_coords.astype(float))**2)
                distances = np.concatenate([[0], np.cumsum(pixel_distances)]) * physical_scale
                
            else:  # 使用插值方法 / Use interpolation method
                length = np.sqrt((end_x - start_x)**2 + (end_y - start_y)**2)
                num_points = max(int(np.ceil(length)) * 2, 10)  # 確保足夠的取樣點
                
                y_indices = np.linspace(start_y, end_y, num_points)
                x_indices = np.linspace(start_x, end_x, num_points)
                
                # 雙線性插值 / Bilinear interpolation
                heights = ndimage.map_coordinates(image_data, [y_indices, x_indices], order=1)
                
                # 物理距離 / Physical distances
                physical_length = length * physical_scale
                distances = np.linspace(0, physical_length, num_points)
            
            # 計算統計數據 / Calculate statistics
            stats = {
                'min': float(np.min(heights)),
                'max': float(np.max(heights)),
                'mean': float(np.mean(heights)),
                'median': float(np.median(heights)),
                'std': float(np.std(heights)),
                'range': float(np.max(heights) - np.min(heights)),
                'rms': float(np.sqrt(np.mean(np.square(heights - np.mean(heights)))))
            }
            
            return {
                'distance': distances.tolist(),
                'height': heights.tolist(),
                'length': float(distances[-1]),
                'stats': stats,
                'method': method,
                'num_points': len(heights)
            }
            
        except Exception as e:
            logger.error(f"獲取剖面失敗 ({method}): {str(e)}")
            return {
                'distance': [],
                'height': [],
                'length': 0,
                'stats': {},
                'method': method,
                'num_points': 0
            }

    @staticmethod
    def apply_advanced_flatten(image_data, method='polynomial_2d', order=1):
        """
        應用高級平面化方法
        Apply advanced flattening methods
        
        使用我們的算法庫進行高級平面校正
        Uses our algorithm library for advanced plane correction
        
        Args:
            image_data: 2D numpy數組，形貌數據 / 2D numpy array, topography data
            method: 平面化方法 ('polynomial_2d', 'median_filter') / Flattening method
            order: 多項式階數（當 method='polynomial_2d' 時）/ Polynomial order
            
        Returns:
            dict: 包含處理結果的字典 / Dictionary containing processing results
        """
        try:
            result = image_data.copy()
            y_size, x_size = result.shape
            
            if method == 'polynomial_2d':
                # 創建座標網格 / Create coordinate grids
                x, y = np.meshgrid(np.arange(x_size), np.arange(y_size))
                
                # 使用 2D 多項式擬合 / Use 2D polynomial fitting
                fit_result = AlgorithmUtils.polynomial_fit_2d(x, y, result, order=order)
                
                # 從原始數據中減去擬合面 / Subtract fitted surface from original data
                result = result - fit_result['fitted_surface']
                
                return {
                    'flattened_data': result,
                    'fitted_surface': fit_result['fitted_surface'],
                    'coefficients': fit_result['coefficients'].tolist(),
                    'method': method,
                    'order': order
                }
                
            elif method == 'median_filter':
                # 使用中值濾波去除尖峰噪聲 / Use median filter to remove spike noise
                filtered = AlgorithmUtils.median_filter_2d(result, size=3)
                
                return {
                    'flattened_data': filtered,
                    'method': method
                }
                
            else:
                raise ValueError(f"不支援的平面化方法: {method}")
                
        except Exception as e:
            logger.error(f"高級平面化失敗 ({method}): {str(e)}")
            return {
                'flattened_data': image_data,
                'method': method,
                'error': str(e)
            }

    @staticmethod
    def detect_surface_features(image_data, feature_type='peaks', **kwargs):
        """
        檢測表面特徵
        Detect surface features
        
        Args:
            image_data: 2D numpy數組，形貌數據 / 2D numpy array, topography data
            feature_type: 特徵類型 ('peaks', 'valleys') / Feature type
            **kwargs: 檢測參數 / Detection parameters
            
        Returns:
            dict: 檢測結果 / Detection results
        """
        try:
            if feature_type == 'peaks':
                # 對每一行檢測峰值 / Detect peaks in each row
                all_peaks = []
                for i, row in enumerate(image_data):
                    peaks, properties = AlgorithmUtils.find_peaks(
                        row if feature_type == 'peaks' else -row,
                        prominence=kwargs.get('prominence', None),
                        distance=kwargs.get('distance', None),
                        height=kwargs.get('height', None)
                    )
                    
                    # 添加行信息 / Add row information
                    for peak in peaks:
                        all_peaks.append({
                            'row': i,
                            'col': peak,
                            'height': float(image_data[i, peak])
                        })
                
                return {
                    'features': all_peaks,
                    'count': len(all_peaks),
                    'type': feature_type
                }
                
            else:
                raise ValueError(f"不支援的特徵類型: {feature_type}")
                
        except Exception as e:
            logger.error(f"特徵檢測失敗: {str(e)}")
            return {
                'features': [],
                'count': 0,
                'type': feature_type,
                'error': str(e)
            }