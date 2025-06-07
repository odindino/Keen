import os
import re
import logging
from datetime import datetime

from ..data_models import ParseResult

logger = logging.getLogger(__name__)

class TxtParser:
    """解析 SPM .txt 參數檔案的類別"""
    
    def __init__(self, file_path):
        self.file_path = file_path
        self.metadata = {}
        self.int_files = []
        self.dat_files = []
        self.signal_types = set()  # 存儲實驗中出現的所有訊號類型
    
    def parse(self) -> ParseResult:
        """
        解析 .txt 檔案以提取元數據和檔案描述
        Parse .txt file to extract metadata and file descriptions
        
        Returns:
            ParseResult: 標準化的解析結果 / Standardized parse result
        """
        result = ParseResult(
            metadata={'path': self.file_path, 'type': 'txt'},
            data=None,
            parser_type='TxtParser'
        )
        
        try:
            with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 解析基本參數
            self._parse_basic_parameters(content)
            
            # 解析檔案描述
            self._parse_file_descriptions(content)
            
            # 構建標準化的結果數據
            parsed_data = {
                "experiment_info": self.metadata,
                "int_files": self.int_files,
                "dat_files": self.dat_files,
                "signal_types": list(self.signal_types)  # 轉換為列表返回
            }
            
            result.data = parsed_data
            result.metadata.update({
                'experiment_name': self.metadata.get('experiment_name', 'Unknown'),
                'total_int_files': len(self.int_files),
                'total_dat_files': len(self.dat_files),
                'signal_types_count': len(self.signal_types)
            })
            
            logger.info(f"TXT 檔案解析成功: {self.file_path}")
            return result
            
        except Exception as e:
            error_msg = f"解析 TXT 檔案時出錯: {str(e)}"
            logger.error(error_msg)
            result.add_error(error_msg)
            return result
    
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
        """解析檔案描述區段，分別處理 .int 和 .dat 檔案"""
        file_desc_pattern = r'FileDescBegin(.*?)FileDescEnd'
        file_descs = re.findall(file_desc_pattern, content, re.DOTALL)
        
        for desc_content in file_descs:
            # 先確定檔案名稱
            filename_match = re.search(r'FileName\s*:\s*([^\n]+)', desc_content)
            if not filename_match:
                continue
                
            filename = filename_match.group(1).strip()
            
            if filename.endswith('.int'):
                self._parse_int_file_description(desc_content, filename)
            elif filename.endswith('.dat'):
                self._parse_dat_file_description(desc_content, filename)
    
    def _parse_int_file_description(self, desc_content, filename):
        """解析 .int 檔案描述"""
        desc = {'filename': filename, 'type': 'int'}
        
        # 提取標題
        caption_match = re.search(r'Caption\s*:\s*([^\n]+)', desc_content)
        if caption_match:
            desc['caption'] = caption_match.group(1).strip()
        
        # 提取比例因子
        scale_match = re.search(r'Scale\s*:\s*([^\n]+)', desc_content)
        if scale_match:
            desc['scale'] = scale_match.group(1).strip()
        
        # 提取物理單位
        unit_match = re.search(r'PhysUnit\s*:\s*([^\n]+)', desc_content)
        if unit_match:
            desc['phys_unit'] = unit_match.group(1).strip()
        
        # 提取偏移量
        offset_match = re.search(r'Offset\s*:\s*([^\n]+)', desc_content)
        if offset_match:
            desc['offset'] = offset_match.group(1).strip()
        
        # 提取訊號類型和方向
        signal_type, direction = self._extract_signal_type_and_direction(filename)
        desc['signal_type'] = signal_type
        desc['direction'] = direction
        
        self.int_files.append(desc)
    
    def _parse_dat_file_description(self, desc_content, filename):
        """解析 .dat 檔案描述"""
        desc = {'filename': filename, 'type': 'dat'}
        
        # 提取標題並解析
        caption_match = re.search(r'Caption\s*:\s*([^\n]+)', desc_content)
        if caption_match:
            caption = caption_match.group(1).strip()
            desc['caption'] = caption
            desc.update(self._parse_caption(caption))
        
        # 提取 HeaderCols
        header_cols_match = re.search(r'HeaderCols\s*:\s*([^\n]+)', desc_content)
        if header_cols_match:
            desc['header_cols'] = int(header_cols_match.group(1).strip())
        
        # 提取 HeaderRows  
        header_rows_match = re.search(r'HeaderRows\s*:\s*([^\n]+)', desc_content)
        if header_rows_match:
            desc['header_rows'] = int(header_rows_match.group(1).strip())
        
        # 解析 Delays 行
        delays_match = re.search(r'Delays[^:]*:\s*([^\n]+)', desc_content)
        if delays_match:
            delays_value = delays_match.group(1).strip()
            desc['delays_raw'] = delays_value
            desc.update(self._parse_delays_line(delays_value))
        
        # 解析 Slewrate 行
        slewrate_match = re.search(r'Slewrate\s*:\s*([^\n]+)', desc_content)
        if slewrate_match:
            slewrate_value = slewrate_match.group(1).strip()
            desc['slewrate_raw'] = slewrate_value
            desc.update(self._parse_slewrate_line(slewrate_value))
        
        # 提取 Average
        average_match = re.search(r'Average\s*:\s*([^\n]+)', desc_content)
        if average_match:
            desc['average'] = int(average_match.group(1).strip())
        
        # 提取訊號類型和方向
        signal_type, direction = self._extract_signal_type_and_direction(filename)
        desc['signal_type'] = signal_type
        desc['direction'] = direction
        
        self.dat_files.append(desc)
    
    def _parse_caption(self, caption):
        """
        解析 Caption 欄位來判斷量測類型和模式
        範例: "X(U)-Lia1R(100/100)" 或 "X(U)-It_to_PC(1)"
        """
        try:
            # 提取量測類型 (如 "Lia1R", "It_to_PC")
            if '-' in caption:
                measurement_type = caption.split('-')[1].split('(')[0]
            else:
                measurement_type = "unknown"
            
            # 提取括號內容
            if '(' in caption and ')' in caption:
                bracket_content = caption.split('(')[-1].split(')')[0]
                
                if '/' in bracket_content:
                    # CITS 量測 (如 "100/100")
                    grid_parts = bracket_content.split('/')
                    if len(grid_parts) == 2:
                        grid_x, grid_y = map(int, grid_parts)
                        measurement_mode = "CITS"
                        grid_size = [grid_x, grid_y]
                    else:
                        measurement_mode = "unknown"
                        grid_size = None
                else:
                    # 單點 STS 量測 (如 "1")
                    point_count = int(bracket_content)
                    measurement_mode = "STS"
                    grid_size = None
            else:
                measurement_mode = "unknown"
                grid_size = None
            
            return {
                "measurement_type": measurement_type,
                "measurement_mode": measurement_mode,
                "grid_size": grid_size
            }
        except Exception as e:
            logger.warning(f"解析 Caption 時出錯: {caption}, 錯誤: {str(e)}")
            return {
                "measurement_type": "unknown",
                "measurement_mode": "unknown", 
                "grid_size": None
            }
    
    def _parse_delays_line(self, value):
        """
        解析 Delays 行的特殊格式
        範例: "0.002/0.0069888/1.5E-5/1.5E-5/0"
        對應: "1/Aqu/3/4/dead"
        """
        try:
            delay_values = value.split('/')
            delay_keys = ['delay_1', 'delay_aqu', 'delay_3', 'delay_4', 'delay_dead']
            
            delays = {}
            for i, (key, val) in enumerate(zip(delay_keys, delay_values)):
                try:
                    delays[key] = float(val)
                except ValueError:
                    delays[key] = val  # 保持原始字串如果無法轉換
            
            return delays
        except Exception as e:
            logger.warning(f"解析 Delays 行時出錯: {value}, 錯誤: {str(e)}")
            return {}
    
    def _parse_slewrate_line(self, value):
        """
        解析 Slewrate 行
        範例: "Infinity/Infinity"
        """
        try:
            slewrate_values = value.split('/')
            return {
                'slewrate_1': slewrate_values[0] if len(slewrate_values) > 0 else None,
                'slewrate_2': slewrate_values[1] if len(slewrate_values) > 1 else None
            }
        except Exception as e:
            logger.warning(f"解析 Slewrate 行時出錯: {value}, 錯誤: {str(e)}")
            return {}
    
    def _extract_signal_type_and_direction(self, filename):
        """
        從檔案名稱中提取訊號類型和掃描方向
        範例: '20250521_Janus Stacking SiO2_13K_113Lia1RFwd.int' 
        -> signal_type='Lia1R', direction='Fwd'
        """
        try:
            # 檢查是否有 Matrix 後綴（表示是 DAT 檔案的 CITS 數據）
            if "_Matrix" in filename:
                # 例如：20250521_Janus Stacking SiO2_13K_113Lia1R_Matrix.dat
                signal_type = filename.split('_Matrix')[0].split('_')[-1]
                if signal_type.startswith('113'):  # 忽略前綴序號
                    signal_type = signal_type[3:]
                direction = None
            else:
                # 尋找常見的訊號類型模式
                signal_patterns = [
                    "Topo", "Lia1X", "Lia1Y", "Lia1R", "Lia2X", "Lia2Y", "Lia2R", 
                    "Lia3X", "Lia3Y", "Lia3R", "It_to_PC", "InA", "QPlus", 
                    "Bias", "Frequency", "Drive", "Phase", "df"
                ]
                
                # 尋找訊號類型
                signal_type = None
                for pattern in signal_patterns:
                    if pattern in filename:
                        signal_type = pattern
                        break
                
                # 如果找不到匹配的訊號類型，嘗試一般性規則
                if signal_type is None:
                    # 取最後一段作為信號類型和方向
                    name_parts = filename.split('_')[-1].replace('.int', '').replace('.dat', '')
                    # 尋找 Fwd 或 Bwd
                    if "Fwd" in name_parts:
                        signal_type = name_parts.replace("Fwd", "")
                        direction = "Fwd"
                    elif "Bwd" in name_parts:
                        signal_type = name_parts.replace("Bwd", "")
                        direction = "Bwd"
                    else:
                        signal_type = name_parts
                        direction = None
                else:
                    # 如果找到了訊號類型，檢查方向
                    if "Fwd" in filename:
                        direction = "Fwd"
                    elif "Bwd" in filename:
                        direction = "Bwd"
                    else:
                        direction = None
            
            # 添加到訊號類型集合中
            if signal_type:
                self.signal_types.add(signal_type)
                
            return signal_type, direction
        except Exception as e:
            logger.warning(f"解析檔案名稱時出錯: {filename}, 錯誤: {str(e)}")
            return "unknown", None
    
    def get_int_files(self):
        """返回 .int 檔案描述列表"""
        return self.int_files
    
    def get_dat_files(self):
        """返回 .dat 檔案描述列表"""
        return self.dat_files