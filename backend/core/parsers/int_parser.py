import numpy as np
import struct
import os
import logging

from ..data_models import ParseResult

logger = logging.getLogger(__name__)

class IntParser:
    """解析 SPM .int 二進位數據檔案的類別"""
    
    def __init__(self, file_path, scale, x_pixel, y_pixel):
        self.file_path = file_path
        self.scale = scale
        self.x_pixel = x_pixel
        self.y_pixel = y_pixel
        self.data = None
    
    def parse(self) -> ParseResult:
        """
        解析 .int 檔案並返回形貌數據
        Parse .int file and return topography data
        
        Returns:
            ParseResult: 標準化的解析結果 / Standardized parse result
        """
        result = ParseResult(
            metadata={'path': self.file_path, 'type': 'int'},
            data=None,
            parser_type='IntParser'
        )
        
        try:
            with open(self.file_path, 'rb') as f:
                int_file = f.read()
            
            # 檢查檔案長度是否符合預期
            expected_length = self.x_pixel * self.y_pixel * 4  # 每個像素 4 位元組
            if len(int_file) != expected_length:
                warning_msg = f"檔案長度 ({len(int_file)}) 與預期不符 ({expected_length})"
                logger.warning(warning_msg)
                result.add_warning(warning_msg)
            
            # 使用 numpy 直接解析數據
            n_pixels = len(int_file) // 4
            image_data = np.frombuffer(int_file, dtype='<i4', count=n_pixels)
            
            # 重塑為二維數組
            image_data = image_data.reshape(self.y_pixel, self.x_pixel)
            
            # 應用比例因子並轉換為浮點數
            image_data = image_data.astype(np.float64) * self.scale
            
            # 構建標準化的結果數據
            parsed_data = {
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
            
            result.data = parsed_data
            result.metadata.update({
                'image_shape': image_data.shape,
                'data_range': (float(image_data.min()), float(image_data.max())),
                'file_size_bytes': len(int_file)
            })
            
            self.data = parsed_data
            logger.info(f"INT 檔案解析成功: {self.file_path}")
            return result
            
        except Exception as e:
            error_msg = f"解析 INT 檔案時出錯: {str(e)}"
            logger.error(error_msg)
            result.add_error(error_msg)
            return result