import numpy as np
import struct
import os
import logging

logger = logging.getLogger(__name__)

class IntParser:
    """解析 SPM .int 二進位數據檔案的類別"""
    
    def __init__(self, file_path, scale, x_pixel, y_pixel):
        self.file_path = file_path
        self.scale = scale
        self.x_pixel = x_pixel
        self.y_pixel = y_pixel
        self.data = None
    
    def parse(self):
        """解析 .int 檔案並返回形貌數據"""
        try:
            with open(self.file_path, 'rb') as f:
                int_file = f.read()
            
            # 檢查檔案長度是否符合預期
            expected_length = self.x_pixel * self.y_pixel * 4  # 每個像素 4 位元組
            if len(int_file) != expected_length:
                logger.warning(f"檔案長度 ({len(int_file)}) 與預期不符 ({expected_length})")
            
            # 使用 numpy 直接解析數據
            n_pixels = len(int_file) // 4
            image_data = np.frombuffer(int_file, dtype='<i4', count=n_pixels)
            
            # 重塑為二維數組
            image_data = image_data.reshape(self.y_pixel, self.x_pixel)
            
            # 應用比例因子並轉換為浮點數
            image_data = image_data.astype(np.float64) * self.scale
            
            # 構建標準返回格式
            result = {
                'image_data': image_data,
                'scan_parameters': {
                    'x_pixel': self.x_pixel,
                    'y_pixel': self.y_pixel,
                    'scale': self.scale
                },
                'physical_dimensions': (
                    self.x_pixel * self.scale,
                    self.y_pixel * self.scale
                )
            }
            
            self.data = result
            return result
        except Exception as e:
            logger.error(f"解析 INT 檔案時出錯: {str(e)}")
            return None