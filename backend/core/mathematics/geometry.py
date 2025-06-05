"""
幾何運算模組
Geometry calculation module

提供 SPM 數據分析所需的幾何運算功能
Provides geometry calculation functions for SPM data analysis
"""

import numpy as np
from typing import List, Tuple, Union, Optional
import logging

logger = logging.getLogger(__name__)


class GeometryUtils:
    """
    幾何運算工具類
    Geometry calculation utility class
    """
    
    @staticmethod
    def bresenham_line(start: Tuple[int, int], end: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Bresenham 直線算法 - 獲取線段上的所有像素點
        Bresenham line algorithm - get all pixel points on a line segment
        
        此算法用於在離散的像素網格上繪製直線
        This algorithm is used to draw lines on discrete pixel grids
        
        Args:
            start: 起始點座標 (x0, y0) / Start point coordinates (x0, y0)
            end: 終點座標 (x1, y1) / End point coordinates (x1, y1)
            
        Returns:
            List[Tuple[int, int]]: 線段上所有像素點的座標列表 / List of all pixel coordinates on the line
            
        Example:
            >>> points = GeometryUtils.bresenham_line((0, 0), (3, 2))
            >>> print(points)
            [(0, 0), (1, 1), (2, 1), (3, 2)]
        """
        x0, y0 = start
        x1, y1 = end
        
        points = []
        
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        
        x, y = x0, y0
        
        while True:
            points.append((x, y))
            
            if x == x1 and y == y1:
                break
                
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
        
        return points
    
    @staticmethod
    def bresenham_line_numpy(start: Tuple[int, int], end: Tuple[int, int]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Bresenham 直線算法的 NumPy 版本
        NumPy version of Bresenham line algorithm
        
        返回分離的 x, y 座標陣列，適合用於 NumPy 索引
        Returns separate x, y coordinate arrays suitable for NumPy indexing
        
        Args:
            start: 起始點座標 (x0, y0) / Start point coordinates (x0, y0)
            end: 終點座標 (x1, y1) / End point coordinates (x1, y1)
            
        Returns:
            Tuple[np.ndarray, np.ndarray]: (x_coords, y_coords) 座標陣列 / Coordinate arrays
        """
        points = GeometryUtils.bresenham_line(start, end)
        if points:
            x_coords, y_coords = zip(*points)
            return np.array(x_coords), np.array(y_coords)
        else:
            return np.array([]), np.array([])
    
    @staticmethod
    def interpolate_line_points(start: Tuple[float, float], 
                               end: Tuple[float, float], 
                               num_points: int,
                               method: str = 'linear') -> np.ndarray:
        """
        線段插值點生成
        Generate interpolated points along a line segment
        
        用於在線段上生成均勻分布的採樣點
        Used to generate uniformly distributed sampling points along a line
        
        Args:
            start: 起始點座標 (x0, y0) / Start point coordinates (x0, y0)
            end: 終點座標 (x1, y1) / End point coordinates (x1, y1)
            num_points: 採樣點數量 / Number of sampling points
            method: 插值方法，目前支援 'linear' / Interpolation method, currently supports 'linear'
            
        Returns:
            np.ndarray: 形狀為 (num_points, 2) 的座標陣列 / Coordinate array with shape (num_points, 2)
            
        Example:
            >>> points = GeometryUtils.interpolate_line_points((0, 0), (10, 5), 5)
            >>> print(points)
            [[ 0.   0. ]
             [ 2.5  1.25]
             [ 5.   2.5 ]
             [ 7.5  3.75]
             [10.   5. ]]
        """
        if num_points < 2:
            raise ValueError("插值點數必須至少為 2 / Number of points must be at least 2")
        
        x0, y0 = start
        x1, y1 = end
        
        if method == 'linear':
            # 線性插值 / Linear interpolation
            t = np.linspace(0, 1, num_points)
            x_coords = x0 + t * (x1 - x0)
            y_coords = y0 + t * (y1 - y0)
            
            return np.column_stack((x_coords, y_coords))
        else:
            raise ValueError(f"不支援的插值方法：{method} / Unsupported interpolation method: {method}")
    
    @staticmethod
    def calculate_line_length(start: Tuple[float, float], 
                             end: Tuple[float, float]) -> float:
        """
        計算線段長度（歐幾里德距離）
        Calculate line segment length (Euclidean distance)
        
        Args:
            start: 起始點座標 / Start point coordinates
            end: 終點座標 / End point coordinates
            
        Returns:
            float: 線段長度 / Line segment length
        """
        x0, y0 = start
        x1, y1 = end
        return np.sqrt((x1 - x0)**2 + (y1 - y0)**2)
    
    @staticmethod
    def dense_sampling_with_unique(start: Tuple[int, int], 
                                  end: Tuple[int, int], 
                                  density_factor: float = 2.0) -> Tuple[np.ndarray, np.ndarray]:
        """
        高密度採樣方法（去除重複點）
        Dense sampling method with duplicate removal
        
        用於生成比 Bresenham 算法更密集的採樣點
        Used to generate denser sampling points than Bresenham algorithm
        
        Args:
            start: 起始點座標 / Start point coordinates
            end: 終點座標 / End point coordinates
            density_factor: 密度因子，越大採樣點越多 / Density factor, larger means more points
            
        Returns:
            Tuple[np.ndarray, np.ndarray]: (x_coords, y_coords) 唯一座標陣列 / Unique coordinate arrays
        """
        x0, y0 = start
        x1, y1 = end
        
        distance = np.sqrt((x1 - x0)**2 + (y1 - y0)**2)
        n_points = max(int(distance * density_factor), 2)
        
        # 生成插值點 / Generate interpolated points
        x_coords = np.linspace(x0, x1, n_points).astype(int)
        y_coords = np.linspace(y0, y1, n_points).astype(int)
        
        # 去除重複點 / Remove duplicate points
        coords = list(zip(x_coords, y_coords))
        unique_coords = []
        seen = set()
        
        for coord in coords:
            if coord not in seen:
                unique_coords.append(coord)
                seen.add(coord)
        
        if unique_coords:
            x_coords, y_coords = zip(*unique_coords)
            return np.array(x_coords), np.array(y_coords)
        else:
            return np.array([x0]), np.array([y0])
    
    @staticmethod
    def point_to_line_distance(point: Tuple[float, float], 
                              line_start: Tuple[float, float], 
                              line_end: Tuple[float, float]) -> float:
        """
        計算點到線段的最短距離
        Calculate the shortest distance from a point to a line segment
        
        Args:
            point: 點座標 (x, y) / Point coordinates (x, y)
            line_start: 線段起點 / Line segment start point
            line_end: 線段終點 / Line segment end point
            
        Returns:
            float: 最短距離 / Shortest distance
        """
        px, py = point
        x1, y1 = line_start
        x2, y2 = line_end
        
        # 線段長度平方 / Line segment length squared
        line_length_sq = (x2 - x1)**2 + (y2 - y1)**2
        
        if line_length_sq == 0:
            # 線段退化為點 / Line segment degenerates to a point
            return np.sqrt((px - x1)**2 + (py - y1)**2)
        
        # 計算投影參數 t / Calculate projection parameter t
        t = max(0, min(1, ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / line_length_sq))
        
        # 投影點座標 / Projection point coordinates
        proj_x = x1 + t * (x2 - x1)
        proj_y = y1 + t * (y2 - y1)
        
        # 距離 / Distance
        return np.sqrt((px - proj_x)**2 + (py - proj_y)**2)
    
    @staticmethod
    def find_perpendicular_line(point: Tuple[float, float],
                               line_start: Tuple[float, float],
                               line_end: Tuple[float, float],
                               length: float) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        """
        找出通過指定點且垂直於給定線段的線段
        Find a line segment passing through a point and perpendicular to a given line segment
        
        Args:
            point: 垂線通過的點 / Point the perpendicular passes through
            line_start: 原線段起點 / Original line start
            line_end: 原線段終點 / Original line end
            length: 垂線長度 / Perpendicular line length
            
        Returns:
            Tuple[Tuple[float, float], Tuple[float, float]]: 垂線的起點和終點 / Start and end of perpendicular
        """
        x1, y1 = line_start
        x2, y2 = line_end
        px, py = point
        
        # 計算原線段的方向向量 / Calculate direction vector of original line
        dx = x2 - x1
        dy = y2 - y1
        
        # 歸一化 / Normalize
        line_length = np.sqrt(dx**2 + dy**2)
        if line_length == 0:
            # 退化情況，返回水平線 / Degenerate case, return horizontal line
            return ((px - length/2, py), (px + length/2, py))
        
        dx /= line_length
        dy /= line_length
        
        # 垂直向量（逆時針旋轉90度）/ Perpendicular vector (90 degrees counterclockwise)
        perp_dx = -dy
        perp_dy = dx
        
        # 計算垂線的兩個端點 / Calculate endpoints of perpendicular
        half_length = length / 2
        start = (px - perp_dx * half_length, py - perp_dy * half_length)
        end = (px + perp_dx * half_length, py + perp_dy * half_length)
        
        return (start, end)
    
    @staticmethod
    def clip_line_to_rectangle(line_start: Tuple[float, float],
                              line_end: Tuple[float, float],
                              rect_min: Tuple[float, float],
                              rect_max: Tuple[float, float]) -> Optional[Tuple[Tuple[float, float], Tuple[float, float]]]:
        """
        將線段裁剪到矩形區域內（Cohen-Sutherland 算法）
        Clip line segment to rectangle (Cohen-Sutherland algorithm)
        
        Args:
            line_start: 線段起點 / Line start point
            line_end: 線段終點 / Line end point
            rect_min: 矩形左下角 (xmin, ymin) / Rectangle bottom-left (xmin, ymin)
            rect_max: 矩形右上角 (xmax, ymax) / Rectangle top-right (xmax, ymax)
            
        Returns:
            Optional[Tuple]: 裁剪後的線段端點，如果完全在外則返回 None / Clipped endpoints, None if completely outside
        """
        def compute_outcode(x, y, xmin, ymin, xmax, ymax):
            code = 0
            if x < xmin: code |= 1  # LEFT
            elif x > xmax: code |= 2  # RIGHT
            if y < ymin: code |= 4  # BOTTOM
            elif y > ymax: code |= 8  # TOP
            return code
        
        x0, y0 = line_start
        x1, y1 = line_end
        xmin, ymin = rect_min
        xmax, ymax = rect_max
        
        outcode0 = compute_outcode(x0, y0, xmin, ymin, xmax, ymax)
        outcode1 = compute_outcode(x1, y1, xmin, ymin, xmax, ymax)
        
        while True:
            if outcode0 == 0 and outcode1 == 0:
                # 完全在內部 / Completely inside
                return ((x0, y0), (x1, y1))
            elif outcode0 & outcode1 != 0:
                # 完全在外部 / Completely outside
                return None
            else:
                # 部分在內部，需要裁剪 / Partially inside, needs clipping
                if outcode0 != 0:
                    outcode_out = outcode0
                    x, y = x0, y0
                    other_x, other_y = x1, y1
                else:
                    outcode_out = outcode1
                    x, y = x1, y1
                    other_x, other_y = x0, y0
                
                # 計算交點 / Calculate intersection
                if outcode_out & 1:  # LEFT
                    y = y + (other_y - y) * (xmin - x) / (other_x - x)
                    x = xmin
                elif outcode_out & 2:  # RIGHT
                    y = y + (other_y - y) * (xmax - x) / (other_x - x)
                    x = xmax
                elif outcode_out & 4:  # BOTTOM
                    x = x + (other_x - x) * (ymin - y) / (other_y - y)
                    y = ymin
                elif outcode_out & 8:  # TOP
                    x = x + (other_x - x) * (ymax - y) / (other_y - y)
                    y = ymax
                
                # 更新點和重新計算 outcode / Update point and recalculate outcode
                if outcode_out == outcode0:
                    x0, y0 = x, y
                    outcode0 = compute_outcode(x0, y0, xmin, ymin, xmax, ymax)
                else:
                    x1, y1 = x, y
                    outcode1 = compute_outcode(x1, y1, xmin, ymin, xmax, ymax)