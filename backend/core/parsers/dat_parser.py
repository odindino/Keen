import os
import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

class DatParser:
    """解析 SPM .dat 數據檔案的類別"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def parse(self, file_path: str, dat_info: dict = None):
        """
        解析 DAT 檔案
        
        Parameters:
        -----------
        file_path : str
            DAT 檔案路徑
        dat_info : dict
            從 TxtParser 獲得的 DAT 檔案描述資訊
            
        Returns:
        --------
        dict : 解析後的數據
        """
        try:
            self.logger.info(f"開始解析 DAT 檔案: {file_path}")
            
            # 1. 讀取檔案並驗證結構
            df = self._read_file_structure(file_path)
            
            # 2. 解析表頭資訊
            header_info = self._parse_headers(df)
            
            # 3. 解析數據內容
            parsed_data = self._parse_data(df, header_info)
            
            # 4. 根據量測模式處理數據
            if dat_info and dat_info.get('measurement_mode') == 'CITS':
                result = self._process_cits_data(parsed_data, header_info, dat_info)
            else:
                result = self._process_sts_data(parsed_data, header_info, dat_info)
            
            # 5. 添加基本資訊
            result.update({
                'file_path': file_path,
                'measurement_type': dat_info.get('measurement_type', 'unknown') if dat_info else 'unknown',
                'units': {
                    'time': header_info['time_unit'],
                    'distance': header_info['distance_unit'], 
                    'bias': header_info['bias_unit']
                }
            })
            
            self.logger.info(f"DAT 檔案解析完成: {result['measurement_mode']} 模式")
            return result
            
        except Exception as e:
            self.logger.error(f"解析 DAT 檔案失敗: {e}")
            raise
    
    def _read_file_structure(self, file_path):
        """讀取檔案並驗證基本結構"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"DAT 檔案不存在: {file_path}")
        
        try:
            df = pd.read_csv(file_path, sep='\t', header=None)
        except Exception as e:
            raise ValueError(f"無法讀取 DAT 檔案: {e}")
        
        # 基本結構驗證
        if df.shape[0] < 3:
            raise ValueError("DAT 檔案至少需要3行數據（表頭2行 + 數據至少1行）")
        if df.shape[1] < 4:
            raise ValueError("DAT 檔案至少需要4列數據（time, distance, bias + 至少1個測量點）")
        
        self.logger.debug(f"DAT 檔案尺寸: {df.shape}")
        return df
    
    def _parse_headers(self, df):
        """解析前兩行的表頭資訊"""
        try:
            # 第一行：time, distance, bias, x1, x2, x3, ...
            header_row1 = df.iloc[0].dropna().tolist()
            
            # 第二行：s, nm, mV, y1, y2, y3, ...
            header_row2 = df.iloc[1].dropna().tolist()
            
            # 解析座標資訊（從第4列開始）
            x_coords = []
            y_coords = []
            
            for i in range(3, min(len(header_row1), len(header_row2))):
                try:
                    x_val = float(header_row1[i])
                    y_val = float(header_row2[i])
                    x_coords.append(x_val)
                    y_coords.append(y_val)
                except (ValueError, IndexError):
                    self.logger.warning(f"無法解析座標 (列 {i+1}): {header_row1[i] if i < len(header_row1) else 'N/A'}, {header_row2[i] if i < len(header_row2) else 'N/A'}")
                    break
            
            if len(x_coords) == 0:
                raise ValueError("未找到有效的座標數據")
            
            header_info = {
                'time_unit': header_row2[0] if len(header_row2) > 0 else 's',
                'distance_unit': header_row2[1] if len(header_row2) > 1 else 'nm',
                'bias_unit': header_row2[2] if len(header_row2) > 2 else 'mV',
                'x_coords': np.array(x_coords),
                'y_coords': np.array(y_coords),
                'n_points': len(x_coords)
            }
            
            self.logger.debug(f"解析到 {header_info['n_points']} 個測量點")
            self.logger.debug(f"X 座標範圍: {np.min(x_coords):.3f} 到 {np.max(x_coords):.3f}")
            self.logger.debug(f"Y 座標範圍: {np.min(y_coords):.3f} 到 {np.max(y_coords):.3f}")
            
            return header_info
            
        except Exception as e:
            raise ValueError(f"解析表頭失敗: {e}")
    
    def _parse_data(self, df, header_info):
        """解析實際的量測數據"""
        try:
            n_points = header_info['n_points']
            
            # 從第3行開始是數據
            data_rows = df.iloc[2:].copy()
            
            # 移除完全空白的行
            data_rows = data_rows.dropna(how='all')
            
            if len(data_rows) == 0:
                raise ValueError("未找到有效的數據行")
            
            # 解析基本參數（前3列）
            times = data_rows.iloc[:, 0].astype(float)
            distances = data_rows.iloc[:, 1].astype(float)  
            bias_values = data_rows.iloc[:, 2].astype(float)
            
            # 解析量測數值（第4列開始）
            measurement_data = data_rows.iloc[:, 3:3+n_points].astype(float)
            
            # 驗證數據一致性
            if measurement_data.shape[1] != n_points:
                self.logger.warning(f"測量數據列數 ({measurement_data.shape[1]}) 與預期點數 ({n_points}) 不匹配")
                # 調整到較小的值
                n_points = min(n_points, measurement_data.shape[1])
                measurement_data = measurement_data.iloc[:, :n_points]
            
            parsed_data = {
                'times': times.values,
                'distances': distances.values,
                'bias_values': bias_values.values,
                'measurement_data': measurement_data.values,
                'n_bias_points': len(bias_values),
                'n_spatial_points': n_points
            }
            
            self.logger.debug(f"解析到 {parsed_data['n_bias_points']} 個偏壓點")
            self.logger.debug(f"偏壓範圍: {np.min(bias_values):.2f} 到 {np.max(bias_values):.2f} {header_info['bias_unit']}")
            self.logger.debug(f"測量數據形狀: {measurement_data.shape}")
            
            return parsed_data
            
        except Exception as e:
            raise ValueError(f"解析數據失敗: {e}")
    
    def _process_cits_data(self, parsed_data, header_info, dat_info):
        """處理 CITS (矩陣) 量測數據"""
        try:
            grid_size = dat_info.get('grid_size', [100, 100])
            grid_x, grid_y = grid_size
            
            # 驗證數據尺寸
            expected_points = grid_x * grid_y
            actual_points = header_info['n_points']
            
            if actual_points != expected_points:
                self.logger.warning(
                    f"網格尺寸不匹配: 預期 {expected_points} 點 ({grid_x}×{grid_y})，實際 {actual_points} 點"
                )
                # 嘗試從實際數據推斷網格尺寸
                sqrt_points = int(np.sqrt(actual_points))
                if sqrt_points * sqrt_points == actual_points:
                    grid_x = grid_y = sqrt_points
                    self.logger.info(f"自動調整網格尺寸為 {grid_x}×{grid_y}")
                else:
                    # 保持原網格尺寸，但截斷數據
                    self.logger.warning(f"無法自動調整網格尺寸，將截斷數據到 {expected_points} 點")
                    actual_points = min(actual_points, expected_points)
            
            # 判斷掃描方向
            scan_direction = self._determine_scan_direction(
                header_info, dat_info, grid_x, grid_y
            )
            
            # 獲取測量數據
            measurement_data = parsed_data['measurement_data'][:, :actual_points]
            x_coords = header_info['x_coords'][:actual_points]
            y_coords = header_info['y_coords'][:actual_points]
            
            # 重塑座標為2D網格
            try:
                # 嘗試直接重塑
                x_grid = x_coords.reshape(grid_y, grid_x)
                y_grid = y_coords.reshape(grid_y, grid_x)
            except ValueError:
                # 如果無法直接重塑，使用meshgrid
                self.logger.info("使用 meshgrid 重建網格座標")
                unique_x = np.unique(x_coords)
                unique_y = np.unique(y_coords)
                
                # 調整網格尺寸以匹配唯一值數量
                if len(unique_x) != grid_x or len(unique_y) != grid_y:
                    grid_x = len(unique_x)
                    grid_y = len(unique_y)
                    self.logger.info(f"根據唯一座標值調整網格尺寸為 {grid_x}×{grid_y}")
                
                x_grid, y_grid = np.meshgrid(unique_x, unique_y)
            
            # 重塑量測數據為 (n_bias, grid_y, grid_x)
            try:
                data_3d = measurement_data.reshape(
                    parsed_data['n_bias_points'], grid_y, grid_x
                )
            except ValueError as e:
                raise ValueError(f"無法重塑測量數據為 3D 陣列: {e}")
            
            result = {
                'measurement_mode': 'CITS',
                'grid_size': [grid_x, grid_y],
                'x_grid': x_grid,
                'y_grid': y_grid,
                'data_3d': data_3d,  # shape: (n_bias, grid_y, grid_x)
                'bias_values': parsed_data['bias_values'],
                'times': parsed_data['times'],
                'distances': parsed_data['distances'],
                'scan_direction': scan_direction
            }
            
            self.logger.info(f"CITS 數據處理完成: {grid_x}×{grid_y} 網格，{len(parsed_data['bias_values'])} 個偏壓點，{scan_direction} 掃描")
            return result
            
        except Exception as e:
            raise ValueError(f"處理 CITS 數據失敗: {e}")
    
    def _process_sts_data(self, parsed_data, header_info, dat_info):
        """處理 STS (單點或多點離散) 量測數據"""
        try:
            result = {
                'measurement_mode': 'STS',
                'x_coords': header_info['x_coords'],
                'y_coords': header_info['y_coords'], 
                'data_2d': parsed_data['measurement_data'],  # shape: (n_bias, n_points)
                'bias_values': parsed_data['bias_values'],
                'times': parsed_data['times'],
                'distances': parsed_data['distances'],
                'n_points': header_info['n_points']
            }
            
            self.logger.info(f"STS 數據處理完成: {header_info['n_points']} 個測量點，{len(parsed_data['bias_values'])} 個偏壓點")
            return result
            
        except Exception as e:
            raise ValueError(f"處理 STS 數據失敗: {e}")
    
    def _determine_scan_direction(self, header_info, dat_info, grid_x, grid_y):
        """判斷 CITS 掃描方向"""
        try:
            x_coords = header_info['x_coords']
            y_coords = header_info['y_coords']
            
            # 取得起始點和終點
            x_start, y_start = x_coords[0], y_coords[0]
            x_end, y_end = x_coords[-1], y_coords[-1]
            
            # 獲取實驗參數
            angle = dat_info.get('angle', 0)
            x_center = dat_info.get('x_center', 0)
            y_center = dat_info.get('y_center', 0)
            
            self.logger.debug(f"原始座標: 起始點({x_start:.3f}, {y_start:.3f}), 終點({x_end:.3f}, {y_end:.3f})")
            self.logger.debug(f"實驗參數: 角度={angle}°, 中心({x_center:.3f}, {y_center:.3f})")
            
            # 座標旋轉正規化
            x_start_rot, y_start_rot = self._rotate_coordinates(
                x_start, y_start, x_center, y_center, angle
            )
            x_end_rot, y_end_rot = self._rotate_coordinates(
                x_end, y_end, x_center, y_center, angle
            )
            
            # 計算掃描方向向量
            scan_direction_y = y_end_rot - y_start_rot
            scan_direction_x = x_end_rot - x_start_rot
            
            self.logger.debug(f"旋轉後座標: 起始點({x_start_rot:.3f}, {y_start_rot:.3f}), 終點({x_end_rot:.3f}, {y_end_rot:.3f})")
            self.logger.debug(f"掃描方向向量: dx={scan_direction_x:.3f}, dy={scan_direction_y:.3f}")
            
            # 判斷掃描方向（只根據Y方向判斷，與Qt版本一致）
            if scan_direction_y > 0:
                direction = 'upward'  # 終點Y比起始點高，由下往上掃
            else:
                direction = 'downward'  # 終點Y比起始點低，由上往下掃
                
            self.logger.info(f"掃描方向判斷結果: {direction}")
            return direction
            
        except Exception as e:
            self.logger.warning(f"掃描方向判斷失敗，使用預設值 'downward': {e}")
            return 'downward'

    def _rotate_coordinates(self, x, y, x_center, y_center, angle):
        """座標旋轉工具函數"""
        import math
        
        # 平移到原點
        x_shift = x - x_center
        y_shift = y - y_center
        
        # 旋轉（負角度，順時針回轉）
        angle_rad = math.radians(-angle)
        x_rot = math.cos(angle_rad) * x_shift - math.sin(angle_rad) * y_shift
        y_rot = math.sin(angle_rad) * x_shift + math.cos(angle_rad) * y_shift
        
        return x_rot, y_rot
