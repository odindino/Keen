import os
import logging
import webview
import numpy as np

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SPMAnalyzerMVP:
    """SPM 數據分析器 MVP 版本 - 簡化的後端 API"""
    
    def __init__(self):
        self.current_directory = ""
        logger.info("SPM 分析器 MVP 初始化完成")
    
    def select_txt_file(self):
        """選擇 TXT 檔案"""
        try:
            logger.info("開始選擇 TXT 檔案")
            
            # 使用 webview 的檔案選擇器
            result = webview.windows[0].create_file_dialog(
                webview.OPEN_DIALOG,
                allow_multiple=False,
                file_types=('TXT Files (*.txt)',)
            )
            
            if result and len(result) > 0:
                selected_path = result[0]
                logger.info(f"使用者選擇了檔案: {selected_path}")
                
                return {
                    "success": True,
                    "filePath": selected_path
                }
            else:
                logger.info("使用者取消了檔案選擇")
                return {
                    "success": False,
                    "error": "沒有選擇檔案"
                }
                
        except Exception as e:
            logger.error(f"選擇檔案時出錯: {str(e)}")
            return {
                "success": False,
                "error": f"選擇檔案時發生錯誤: {str(e)}"
            }
    
    def load_spm_file(self, txt_file_path):
        """載入 SPM 檔案（TXT + INT）"""
        try:
            logger.info(f"開始載入 SPM 檔案: {txt_file_path}")
            
            # 1. 檢查 TXT 檔案是否存在
            if not os.path.exists(txt_file_path):
                error_msg = f"TXT 檔案不存在: {txt_file_path}"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
            
            # 2. 解析 TXT 檔案
            logger.info("解析 TXT 檔案參數")
            parameters = self._parse_txt_file(txt_file_path)
            
            # 3. 找到對應的 INT 檔案
            logger.info("尋找對應的 INT 檔案")
            int_file_path = self._find_topo_int_file(txt_file_path, parameters)
            if not int_file_path:
                error_msg = "找不到對應的 TopoFwd.int 檔案"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
            
            logger.info(f"找到 INT 檔案: {int_file_path}")
            
            # 4. 獲取基本參數
            scale, phys_unit, x_pixels, y_pixels, x_range, y_range = self._extract_parameters(
                parameters, int_file_path
            )
            
            logger.info(f"提取參數完成: scale={scale}, unit={phys_unit}, pixels={x_pixels}x{y_pixels}")
            
            # 5. 解析 INT 檔案
            logger.info("解析 INT 檔案數據")
            raw_data = self._parse_int_file(int_file_path, scale, x_pixels, y_pixels)
            
            # 6. 計算統計資訊
            logger.info("計算統計資訊")
            statistics = self._calculate_statistics(raw_data)
            
            # 7. 準備回傳數據
            result = {
                "success": True,
                "name": os.path.basename(txt_file_path),
                "intFile": int_file_path,
                "rawData": raw_data.tolist(),
                "colormap": "Oranges",
                "dimensions": {
                    "width": x_pixels,
                    "height": y_pixels,
                    "xRange": x_range,
                    "yRange": y_range
                },
                "physUnit": phys_unit,
                "statistics": statistics
            }
            
            logger.info(f"SPM 檔案載入成功: {result['name']}")
            logger.info(f"數據尺寸: {x_pixels}x{y_pixels}, 範圍: {x_range}x{y_range} {phys_unit}")
            
            return result
            
        except Exception as e:
            error_msg = f"載入 SPM 檔案時出錯: {str(e)}"
            logger.error(error_msg)
            import traceback
            logger.error(f"詳細錯誤: {traceback.format_exc()}")
            return {"success": False, "error": error_msg}
    
    def update_colormap(self, int_file_path, colormap):
        """更新色彩映射（MVP 版本暫不實際處理）"""
        try:
            logger.info(f"收到色彩映射更新請求: {colormap} (MVP 版本僅前端處理)")
            
            # 在 MVP 版本中，色彩映射變更完全由前端處理
            return {
                "success": True,
                "message": "MVP 版本中色彩映射由前端處理"
            }
            
        except Exception as e:
            logger.error(f"處理色彩映射更新時出錯: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _parse_txt_file(self, txt_file_path):
        """解析 TXT 檔案"""
        try:
            with open(txt_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            parameters = {}
            
            # 提取基本參數
            import re
            
            # 掃描參數
            params_to_extract = [
                'xPixel', 'yPixel', 'XScanRange', 'YScanRange', 
                'XPhysUnit', 'YPhysUnit'
            ]
            
            for param in params_to_extract:
                pattern = fr'{param}\s*:\s*([^\n]+)'
                match = re.search(pattern, content)
                if match:
                    parameters[param] = match.group(1).strip()
            
            # 解析檔案描述
            file_descriptions = []
            file_desc_pattern = r'FileDescBegin(.*?)FileDescEnd'
            file_descs = re.findall(file_desc_pattern, content, re.DOTALL)
            
            for desc_content in file_descs:
                desc = {}
                
                # 提取檔案名
                filename_match = re.search(r'FileName\s*:\s*([^\n]+)', desc_content)
                if filename_match:
                    desc['FileName'] = filename_match.group(1).strip()
                
                # 提取比例因子
                scale_match = re.search(r'Scale\s*:\s*([^\n]+)', desc_content)
                if scale_match:
                    desc['Scale'] = scale_match.group(1).strip()
                
                # 提取物理單位
                unit_match = re.search(r'PhysUnit\s*:\s*([^\n]+)', desc_content)
                if unit_match:
                    desc['PhysUnit'] = unit_match.group(1).strip()
                
                file_descriptions.append(desc)
            
            parameters['fileDescriptions'] = file_descriptions
            
            logger.info(f"TXT 檔案解析完成，找到 {len(file_descriptions)} 個檔案描述")
            return parameters
            
        except Exception as e:
            logger.error(f"解析 TXT 檔案時出錯: {str(e)}")
            return {}
    
    def _find_topo_int_file(self, txt_file_path, parameters):
        """找到對應的 TopoFwd.int 檔案"""
        try:
            directory = os.path.dirname(txt_file_path)
            
            # 從檔案描述中找 TopoFwd.int 檔案
            if "fileDescriptions" in parameters:
                for desc in parameters["fileDescriptions"]:
                    if "FileName" in desc:
                        filename = desc["FileName"]
                        if "TopoFwd" in filename and filename.endswith(".int"):
                            int_path = os.path.join(directory, filename)
                            if os.path.exists(int_path):
                                logger.info(f"從檔案描述找到形貌圖檔案: {int_path}")
                                return int_path
            
            # 如果找不到，嘗試按檔名規則找
            txt_basename = os.path.basename(txt_file_path)
            base_name = txt_basename.rsplit('.', 1)[0]
            
            # 嘗試常見的命名模式
            possible_names = [
                f"{base_name}_TopoFwd.int",
                f"{base_name}TopoFwd.int",
                "TopoFwd.int"
            ]
            
            for name in possible_names:
                int_path = os.path.join(directory, name)
                if os.path.exists(int_path):
                    logger.info(f"按命名規則找到形貌圖檔案: {int_path}")
                    return int_path
            
            # 列出目錄中所有 .int 檔案作為參考
            int_files = [f for f in os.listdir(directory) if f.endswith('.int')]
            logger.warning(f"找不到 TopoFwd.int 檔案。目錄中的 .int 檔案: {int_files}")
            
            return None
            
        except Exception as e:
            logger.error(f"尋找 INT 檔案時出錯: {str(e)}")
            return None
    
    def _extract_parameters(self, parameters, int_file_path):
        """從參數中提取必要資訊"""
        try:
            # 預設值
            scale = 1.0
            phys_unit = "nm"
            x_pixels = 512
            y_pixels = 512
            x_range = 100.0
            y_range = 100.0
            
            # 從基本參數中獲取
            if "xPixel" in parameters:
                try:
                    x_pixels = int(parameters["xPixel"])
                except (ValueError, TypeError):
                    logger.warning(f"無法轉換 xPixel: {parameters['xPixel']}")
                    
            if "yPixel" in parameters:
                try:
                    y_pixels = int(parameters["yPixel"])
                except (ValueError, TypeError):
                    logger.warning(f"無法轉換 yPixel: {parameters['yPixel']}")
                    
            if "XScanRange" in parameters:
                try:
                    x_range = float(parameters["XScanRange"])
                except (ValueError, TypeError):
                    logger.warning(f"無法轉換 XScanRange: {parameters['XScanRange']}")
                    
            if "YScanRange" in parameters:
                try:
                    y_range = float(parameters["YScanRange"])
                except (ValueError, TypeError):
                    logger.warning(f"無法轉換 YScanRange: {parameters['YScanRange']}")
                    
            if "XPhysUnit" in parameters:
                phys_unit = parameters["XPhysUnit"]
            
            # 從檔案描述中獲取 scale
            int_filename = os.path.basename(int_file_path)
            if "fileDescriptions" in parameters:
                for desc in parameters["fileDescriptions"]:
                    if desc.get("FileName") == int_filename:
                        if "Scale" in desc:
                            try:
                                scale = float(desc["Scale"])
                            except (ValueError, TypeError):
                                logger.warning(f"無法轉換 scale: {desc['Scale']}")
                        if "PhysUnit" in desc:
                            phys_unit = desc["PhysUnit"]
                        break
            
            logger.info(f"參數提取完成: scale={scale}, unit={phys_unit}, pixels={x_pixels}x{y_pixels}, range={x_range}x{y_range}")
            return scale, phys_unit, x_pixels, y_pixels, x_range, y_range
            
        except Exception as e:
            logger.error(f"提取參數時出錯: {str(e)}")
            # 返回預設值
            return 1.0, "nm", 512, 512, 100.0, 100.0
    
    def _parse_int_file(self, int_file_path, scale, x_pixels, y_pixels):
        """解析 INT 檔案"""
        try:
            import struct
            
            with open(int_file_path, 'rb') as f:
                int_file = f.read()
            
            # 檢查檔案長度
            expected_length = x_pixels * y_pixels * 4  # 每個像素 4 位元組
            if len(int_file) != expected_length:
                logger.warning(f"檔案長度 ({len(int_file)}) 與預期不符 ({expected_length})")
            
            # 解析數據
            image_data = []
            for i in range(int(len(int_file) / 4)):
                try:
                    value = struct.unpack('<i', int_file[4*i:4*i+4])[0]
                    image_data.append(value)
                except struct.error:
                    logger.warning(f"解析第 {i} 個數據點時出錯")
                    image_data.append(0)
            
            # 轉換為 numpy 數組並重塑
            image_data = np.array(image_data)
            image_data = image_data.reshape(y_pixels, x_pixels)
            
            # 應用比例因子
            image_data = image_data * scale
            
            # 上下翻轉
            image_data = np.flipud(image_data)
            
            logger.info(f"INT 檔案解析完成，數據形狀: {image_data.shape}")
            return image_data
            
        except Exception as e:
            logger.error(f"解析 INT 檔案時出錯: {str(e)}")
            # 返回預設數據
            return np.zeros((y_pixels, x_pixels))
    
    def _calculate_statistics(self, raw_data):
        """計算統計資訊"""
        try:
            # 移除無效值
            valid_data = raw_data[~np.isnan(raw_data)]
            
            stats = {
                "min": float(np.min(valid_data)),
                "max": float(np.max(valid_data)),
                "mean": float(np.mean(valid_data)),
                "rms": float(np.sqrt(np.mean(np.square(valid_data - np.mean(valid_data)))))
            }
            
            logger.info(f"統計資訊計算完成: min={stats['min']:.3f}, max={stats['max']:.3f}, mean={stats['mean']:.3f}")
            return stats
            
        except Exception as e:
            logger.error(f"計算統計資訊時出錯: {str(e)}")
            return {"min": 0.0, "max": 0.0, "mean": 0.0, "rms": 0.0}