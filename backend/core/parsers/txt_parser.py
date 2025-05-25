import os
import re
import logging

logger = logging.getLogger(__name__)

class TxtParser:
    """解析 SPM .txt 參數檔案的類別"""
    
    def __init__(self, file_path):
        self.file_path = file_path
        self.metadata = {}
        self.file_descriptions = []
    
    def parse(self):
        """解析 .txt 檔案以提取元數據和檔案描述"""
        try:
            with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 解析基本參數
            self._parse_basic_parameters(content)
            
            # 解析檔案描述
            self._parse_file_descriptions(content)
            
            # 將檔案描述添加到元數據
            self.metadata['fileDescriptions'] = self.file_descriptions
            
            return self.metadata
        except Exception as e:
            logger.error(f"解析 TXT 檔案時出錯: {str(e)}")
            raise
    
    def _parse_basic_parameters(self, content):
        """解析基本參數如掃描範圍、像素數等"""
        # 提取版本資訊
        version_match = re.search(r'Version\s*:\s*([^\n]+)', content)
        if version_match:
            self.metadata['Version'] = version_match.group(1).strip()
        
        # 提取日期和時間
        date_match = re.search(r'Date\s*:\s*([^\n]+)', content)
        if date_match:
            self.metadata['Date'] = date_match.group(1).strip()
        
        time_match = re.search(r'Time\s*:\s*([^\n]+)', content)
        if time_match:
            self.metadata['Time'] = time_match.group(1).strip()
        
        # 提取用戶名
        username_match = re.search(r'UserName\s*:\s*([^\n]+)', content)
        if username_match:
            self.metadata['UserName'] = username_match.group(1).strip()
        
        # 提取掃描參數
        parameters = [
            'SetPoint', 'SetPointPhysUnit', 'FeedBackModus', 'Bias', 'BiasPhysUnit',
            'Ki', 'Kp', 'FeedbackOnCh', 'XScanRange', 'YScanRange', 'XPhysUnit',
            'YPhysUnit', 'Speed', 'LineRate', 'Angle', 'xPixel', 'yPixel',
            'yCenter', 'xCenter', 'LockInFreq', 'LockInFreqPhysUnit', 'LockInAmpl',
            'LockInAmplPhysUnit'
        ]
        
        for param in parameters:
            pattern = fr'{param}\s*:\s*([^\n]+)'
            match = re.search(pattern, content)
            if match:
                self.metadata[param] = match.group(1).strip()
    
    def _parse_file_descriptions(self, content):
        """解析檔案描述區段"""
        file_desc_pattern = r'FileDescBegin(.*?)FileDescEnd'
        file_descs = re.findall(file_desc_pattern, content, re.DOTALL)
        
        for desc_content in file_descs:
            desc = {}
            
            # 提取文件名
            filename_match = re.search(r'FileName\s*:\s*([^\n]+)', desc_content)
            if filename_match:
                desc['FileName'] = filename_match.group(1).strip()
            
            # 提取標題
            caption_match = re.search(r'Caption\s*:\s*([^\n]+)', desc_content)
            if caption_match:
                desc['Caption'] = caption_match.group(1).strip()
            
            # 提取比例因子
            scale_match = re.search(r'Scale\s*:\s*([^\n]+)', desc_content)
            if scale_match:
                desc['Scale'] = scale_match.group(1).strip()
            
            # 提取物理單位
            unit_match = re.search(r'PhysUnit\s*:\s*([^\n]+)', desc_content)
            if unit_match:
                desc['PhysUnit'] = unit_match.group(1).strip()
            
            # 提取偏移量
            offset_match = re.search(r'Offset\s*:\s*([^\n]+)', desc_content)
            if offset_match:
                desc['Offset'] = offset_match.group(1).strip()
            
            self.file_descriptions.append(desc)
    
    def get_file_descriptions(self):
        """返回檔案描述列表"""
        return self.file_descriptions