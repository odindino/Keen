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
            
            image_data = []
            
            # 檢查檔案長度是否符合預期
            expected_length = self.x_pixel * self.y_pixel * 4  # 每個像素 4 位元組
            if len(int_file) != expected_length:
                logger.warning(f"檔案長度 ({len(int_file)}) 與預期不符 ({expected_length})")
            
            # 解析數據
            for i in range(int(len(int_file) / 4)):
                image_data_numvalue = struct.unpack('<i', int_file[4*i:4*i+4])[0]
                image_data.append(image_data_numvalue)
            
            # 將數據轉換為 numpy 數組並重塑
            image_data = np.array(image_data)
            image_data = image_data.reshape(self.y_pixel, self.x_pixel)
            
            # 應用比例因子
            image_data = image_data * self.scale
            
            self.data = image_data
            return self.data
        except Exception as e:
            logger.error(f"解析 INT 檔案時出錯: {str(e)}")
            raise