import os
import re
import logging
import numpy as np
import matplotlib
import base64
import io
matplotlib.use('Agg')  # 設置 matplotlib 為非互動模式
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from .parsers.int_parser import IntParser
from .parsers.txt_parser import TxtParser

logger = logging.getLogger(__name__)

class AnalysisService:
    """提供各種數據分析的服務類"""
    
    @staticmethod
    def analyze_int_file(file_path, file_info=None):
        """分析 .int 檔案並回傳圖像數據和原始數據"""
        try:
            if not os.path.exists(file_path):
                logger.error(f"檔案不存在: {file_path}")
                return {"success": False, "error": f"檔案不存在: {file_path}"}
            
            # 提取參數，從 file_info 或者從檔案名字解析
            scale = None
            x_pixels = None
            y_pixels = None
            phys_unit = "nm"  # 預設單位
            x_scan_range = None
            y_scan_range = None
            
            if file_info:
                if "scale" in file_info:
                    try:
                        scale = float(file_info["scale"])
                        logger.info(f"從參數獲取到縮放比例: {scale}")
                    except (ValueError, TypeError):
                        logger.warning(f"無法轉換縮放比例: {file_info['scale']}")
                
                if "physUnit" in file_info:
                    phys_unit = file_info["physUnit"]
                    logger.info(f"從參數獲取到物理單位: {phys_unit}")
                
                if "parameters" in file_info and file_info["parameters"]:
                    params = file_info["parameters"]
                    if "xPixel" in params:
                        try:
                            x_pixels = int(params["xPixel"])
                            logger.info(f"從參數獲取到 X 像素數: {x_pixels}")
                        except (ValueError, TypeError):
                            logger.warning(f"無法轉換 X 像素數: {params['xPixel']}")
                    if "yPixel" in params:
                        try:
                            y_pixels = int(params["yPixel"])
                            logger.info(f"從參數獲取到 Y 像素數: {y_pixels}")
                        except (ValueError, TypeError):
                            logger.warning(f"無法轉換 Y 像素數: {params['yPixel']}")
                    
                    # 獲取掃描範圍
                    if "XScanRange" in params:
                        try:
                            x_scan_range = float(params["XScanRange"])
                            logger.info(f"從參數獲取到 X 掃描範圍: {x_scan_range}")
                        except (ValueError, TypeError):
                            logger.warning(f"無法轉換 X 掃描範圍: {params['XScanRange']}")
                    
                    if "YScanRange" in params:
                        try:
                            y_scan_range = float(params["YScanRange"])
                            logger.info(f"從參數獲取到 Y 掃描範圍: {y_scan_range}")
                        except (ValueError, TypeError):
                            logger.warning(f"無法轉換 Y 掃描範圍: {params['YScanRange']}")
            
            # 如果沒提供參數，嘗試從檔案名解析對應的 txt 檔案來獲取參數
            if scale is None or x_pixels is None or y_pixels is None:
                txt_path = AnalysisService._find_corresponding_txt_file(file_path)
                if txt_path:
                    logger.info(f"找到對應的 TXT 檔案: {txt_path}")
                    txt_parser = TxtParser(txt_path)
                    try:
                        metadata = txt_parser.parse()
                        
                        # 從 metadata 中獲取 x_pixels 和 y_pixels
                        if x_pixels is None and "xPixel" in metadata:
                            try:
                                x_pixels = int(metadata["xPixel"])
                                logger.info(f"從 TXT 檔案獲取到 X 像素數: {x_pixels}")
                            except (ValueError, TypeError):
                                logger.warning(f"無法轉換 X 像素數: {metadata['xPixel']}")
                        
                        if y_pixels is None and "yPixel" in metadata:
                            try:
                                y_pixels = int(metadata["yPixel"])
                                logger.info(f"從 TXT 檔案獲取到 Y 像素數: {y_pixels}")
                            except (ValueError, TypeError):
                                logger.warning(f"無法轉換 Y 像素數: {metadata['yPixel']}")
                        
                        # 獲取掃描範圍
                        if x_scan_range is None and "XScanRange" in metadata:
                            try:
                                x_scan_range = float(metadata["XScanRange"])
                                logger.info(f"從 TXT 檔案獲取到 X 掃描範圍: {x_scan_range}")
                            except (ValueError, TypeError):
                                logger.warning(f"無法轉換 X 掃描範圍: {metadata['XScanRange']}")
                        
                        if y_scan_range is None and "YScanRange" in metadata:
                            try:
                                y_scan_range = float(metadata["YScanRange"])
                                logger.info(f"從 TXT 檔案獲取到 Y 掃描範圍: {y_scan_range}")
                            except (ValueError, TypeError):
                                logger.warning(f"無法轉換 Y 掃描範圍: {metadata['YScanRange']}")
                        
                        # 查找對應的檔案描述以獲取 scale 和 phys_unit
                        int_filename = os.path.basename(file_path)
                        for desc in metadata.get('fileDescriptions', []):
                            if desc.get('FileName') == int_filename:
                                if scale is None and 'Scale' in desc:
                                    try:
                                        scale_str = desc['Scale']
                                        scale = float(scale_str)
                                        logger.info(f"從 TXT 檔案獲取到縮放比例: {scale}")
                                    except (ValueError, TypeError):
                                        logger.warning(f"無法轉換縮放比例: {scale_str}")
                                
                                if 'PhysUnit' in desc:
                                    phys_unit = desc['PhysUnit']
                                    logger.info(f"從 TXT 檔案獲取到物理單位: {phys_unit}")
                                
                                break
                    except Exception as e:
                        logger.warning(f"解析 TXT 檔案失敗: {str(e)}")
            
            # 如果仍然沒有參數，使用預設值
            if scale is None:
                scale = 1.0
                logger.warning(f"無法獲取縮放比例，使用預設值 1.0")
            
            if x_pixels is None or y_pixels is None:
                # 預設為 512x512
                x_pixels = 512
                y_pixels = 512
                logger.warning(f"無法獲取像素尺寸，使用預設值 512x512")
            
            # 如果沒有掃描範圍，設定預設值
            if x_scan_range is None:
                x_scan_range = 100.0
                logger.warning(f"無法獲取 X 掃描範圍，使用預設值 100 {phys_unit}")
            
            if y_scan_range is None:
                y_scan_range = 100.0
                logger.warning(f"無法獲取 Y 掃描範圍，使用預設值 100 {phys_unit}")
            
            # 使用 IntParser 解析檔案
            logger.info(f"開始解析 INT 檔案: {file_path}")
            parser = IntParser(file_path, scale, x_pixels, y_pixels)
            image_data = parser.parse()
            logger.info(f"INT 檔案解析完成，資料形狀: {image_data.shape}")
            
            # 檔案名稱 (只取基本名稱)
            base_filename = os.path.basename(file_path)
            
            # 生成預覽圖像 (仍保留以相容性)
            logger.info(f"開始生成預覽圖")
            fig, ax = plt.subplots(figsize=(8, 6), dpi=100)
            
            # 創建X和Y坐標網格，用掃描範圍而不是像素數
            x = np.linspace(0, x_scan_range, x_pixels)
            y = np.linspace(0, y_scan_range, y_pixels)
            
            # 畫出圖像，並設置正確的X和Y軸範圍
            im = ax.imshow(image_data, cmap='Oranges', extent=[0, x_scan_range, 0, y_scan_range], origin='lower')
            
            # 設置軸標籤
            ax.set_xlabel(f'X ({phys_unit})')
            ax.set_ylabel(f'Y ({phys_unit})')
            
            # 設置標題 (只使用檔案名)
            ax.set_title(base_filename)
            
            # 設置colorbar
            cbar = plt.colorbar(im, ax=ax)
            cbar.set_label(f'Height ({phys_unit})')
            
            # 將圖像轉為 base64 字符串
            buf = io.BytesIO()
            fig.tight_layout()
            fig.savefig(buf, format='png', dpi=100)
            buf.seek(0)
            img_data = buf.read()
            img_size = len(img_data)
            logger.info(f"預覽圖生成成功，大小: {img_size} bytes")
            img_base64 = base64.b64encode(img_data).decode('utf-8')
            buf.close()
            plt.close(fig)
            
            # 計算一些基本統計數據
            stats = {
                "min": float(np.min(image_data)),
                "max": float(np.max(image_data)),
                "mean": float(np.mean(image_data)),
                "median": float(np.median(image_data)),
                "std": float(np.std(image_data)),
                "rms": float(np.sqrt(np.mean(np.square(image_data))))
            }
            
            # 將原始資料轉換為列表，以便JSON序列化
            raw_data = image_data.tolist()
            
            return {
                "success": True,
                "image": img_base64,  # 保留靜態圖像以相容性
                "rawData": raw_data,  # 添加原始數據
                "statistics": stats,
                "dimensions": {
                    "width": x_pixels,
                    "height": y_pixels,
                    "xRange": x_scan_range,
                    "yRange": y_scan_range
                },
                "physUnit": phys_unit
            }
            
        except Exception as e:
            logger.error(f"分析 INT 檔案時出錯: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def _find_corresponding_txt_file(int_file_path):
        """找到與 .int 檔案對應的 .txt 檔案"""
        directory = os.path.dirname(int_file_path)
        basename = os.path.basename(int_file_path)
        
        # 嘗試找出編號部分
        match = re.search(r'(.+?)_(\d+)([^_]*?)\.(int|dat)$', basename, re.IGNORECASE)
        if match:
            prefix = match.group(1)
            number = match.group(2)
            
            # 在同一目錄中尋找可能的 txt 檔案
            for filename in os.listdir(directory):
                if filename.endswith('.txt') and filename.startswith(f"{prefix}_{number}"):
                    return os.path.join(directory, filename)
        
        return None