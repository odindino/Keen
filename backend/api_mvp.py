import os
import logging
import webview
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.colors import to_hex
import re
import struct
import traceback

# 導入影像分析功能
from core.analysis.int_analysis import IntAnalysis

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
        self.current_raw_data = None  # 新增：存儲原始 numpy 數據
        self.current_metadata = None  # 新增：存儲元數據
        self.current_processed_data = None  # 新增：存儲處理後的數據
        self.processing_history = []  # 新增：處理歷史記錄
        
        # 新增：檔案選擇功能相關
        self.current_txt_data = None  # 存儲 TXT 檔案解析結果
        self.available_files = []  # 可用檔案清單
        self.selected_file = None  # 當前選中的檔案
        
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
    
    def load_txt_file(self, txt_file_path):
        """載入 TXT 檔案並回傳可用檔案清單"""
        try:
            logger.info(f"開始解析 TXT 檔案: {txt_file_path}")
            
            # 檢查檔案是否存在
            if not os.path.exists(txt_file_path):
                error_msg = f"TXT 檔案不存在: {txt_file_path}"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
            
            # 使用新的 TxtParser 解析檔案
            from core.parsers import TxtParser
            
            parser = TxtParser(txt_file_path)
            result = parser.parse()
            
            # 組合可用檔案清單
            available_files = []
            
            # 處理 .int 檔案
            for int_file in result['int_files']:
                file_info = {
                    'filename': int_file['filename'],
                    'type': 'int',
                    'caption': int_file['caption'],
                    'file_type': 'image',
                    'scale': int_file.get('scale'),
                    'phys_unit': int_file.get('phys_unit'),
                    'offset': int_file.get('offset')
                }
                available_files.append(file_info)
            
            # 處理 .dat 檔案  
            for dat_file in result['dat_files']:
                file_info = {
                    'filename': dat_file['filename'],
                    'type': 'dat',
                    'caption': dat_file['caption'],
                    'measurement_mode': dat_file.get('measurement_mode'),
                    'measurement_type': dat_file.get('measurement_type'),
                    'grid_size': dat_file.get('grid_size')
                }
                available_files.append(file_info)
            
            # 儲存解析結果
            self.current_txt_data = result
            self.available_files = available_files
            self.selected_file = None
            
            logger.info(f"TXT 檔案解析完成: {len(available_files)} 個可用檔案")
            
            return {
                'success': True,
                'txt_path': txt_file_path,
                'experiment_info': result['experiment_info'],
                'available_files': available_files
            }
            
        except Exception as e:
            error_msg = f"解析 TXT 檔案時出錯: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def load_selected_file(self, txt_file_path, selected_filename):
        """載入用戶選擇的特定檔案"""
        try:
            logger.info(f"開始載入選中檔案: {selected_filename}")
            
            # 檢查是否已經解析過 TXT 檔案
            if self.current_txt_data is None:
                # 先解析 TXT 檔案
                txt_result = self.load_txt_file(txt_file_path)
                if not txt_result['success']:
                    return txt_result
            
            # 找到選中檔案的資訊
            selected_file_info = None
            for file_info in self.available_files:
                if file_info['filename'] == selected_filename:
                    selected_file_info = file_info
                    break
            
            if not selected_file_info:
                error_msg = f"找不到檔案: {selected_filename}"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
            
            # 儲存選中檔案資訊
            self.selected_file = selected_file_info
            
            # 根據檔案類型載入
            if selected_file_info['type'] == 'int':
                return self._load_int_file(txt_file_path, selected_filename, selected_file_info)
            elif selected_file_info['type'] == 'dat':
                return self._load_dat_file(txt_file_path, selected_filename, selected_file_info)
            else:
                error_msg = f"不支援的檔案類型: {selected_file_info['type']}"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            error_msg = f"載入選中檔案時出錯: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def load_spm_file(self, txt_file_path):
        """載入 SPM 檔案並生成 Plotly JSON 配置"""
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
            
            # 存儲原始數據和元數據供後續使用
            self.current_raw_data = raw_data
            self.current_processed_data = raw_data.copy()  # 初始化處理後數據為原始數據副本
            self.processing_history = []  # 重置處理歷史
            self.current_metadata = {
                'scale': scale,
                'phys_unit': phys_unit,
                'x_pixels': x_pixels,
                'y_pixels': y_pixels,
                'x_range': x_range,
                'y_range': y_range
            }
            
            # 6. 計算統計資訊
            logger.info("計算統計資訊")
            statistics = self._calculate_statistics(raw_data)
            
            # 7. 生成 Plotly JSON 配置
            logger.info("生成 Plotly 配置")
            plotly_config = self._generate_plotly_config(
                raw_data, x_range, y_range, phys_unit, "Oranges"
            )
            
            # 8. 準備回傳數據
            result = {
                "success": True,
                "name": os.path.basename(txt_file_path),
                "intFile": int_file_path,
                "txtFile": txt_file_path,
                "plotlyConfig": plotly_config,  # Plotly 配置（data + layout）
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
            logger.error(f"詳細錯誤: {traceback.format_exc()}")
            return {"success": False, "error": error_msg}
    
    def update_colormap(self, txt_file_path, int_file_path, colormap):
        """更新色彩映射並重新生成 Plotly 配置"""
        try:
            logger.info(f"更新色彩映射為: {colormap}")
            
            # 使用當前處理後的數據（如果可用），否則使用原始數據
            if self.current_processed_data is not None:
                data_to_use = self.current_processed_data
                logger.info("使用處理後的數據重新生成 Plotly 配置")
            elif self.current_raw_data is not None:
                data_to_use = self.current_raw_data
                logger.info("使用原始數據重新生成 Plotly 配置")
            else:
                # 如果沒有緩存數據，重新解析
                logger.info("重新解析數據")
                parameters = self._parse_txt_file(txt_file_path)
                scale, phys_unit, x_pixels, y_pixels, x_range, y_range = self._extract_parameters(
                    parameters, int_file_path
                )
                data_to_use = self._parse_int_file(int_file_path, scale, x_pixels, y_pixels)
                
                # 更新緩存數據
                self.current_raw_data = data_to_use
                self.current_processed_data = data_to_use.copy()
                self.current_metadata = {
                    'scale': scale,
                    'phys_unit': phys_unit,
                    'x_pixels': x_pixels,
                    'y_pixels': y_pixels,
                    'x_range': x_range,
                    'y_range': y_range
                }
            
            # 使用新的色彩映射生成 Plotly 配置
            logger.info(f"重新生成 Plotly 配置，使用色彩映射: {colormap}")
            plotly_config = self._generate_plotly_config(
                data_to_use, 
                self.current_metadata['x_range'], 
                self.current_metadata['y_range'], 
                self.current_metadata['phys_unit'], 
                colormap
            )
            
            return {
                "success": True,
                "plotlyConfig": plotly_config,
                "colormap": colormap
            }
            
        except Exception as e:
            logger.error(f"更新色彩映射時出錯: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def calculate_height_profile(self, start_point, end_point):
        """
        計算高度剖面數據
        
        Args:
            start_point: 起始點座標 [x, y] (物理單位)
            end_point: 終止點座標 [x, y] (物理單位)
            
        Returns:
            dict: 剖面數據
        """
        try:
            if self.current_raw_data is None or self.current_metadata is None:
                return {"success": False, "error": "沒有載入的數據"}
            
            logger.info(f"開始計算高度剖面: {start_point} -> {end_point}")
            
            # 將物理座標轉換為像素座標
            meta = self.current_metadata
            pixel_start = [
                int(start_point[1] * meta['y_pixels'] / meta['y_range']),  # y -> row
                int(start_point[0] * meta['x_pixels'] / meta['x_range'])   # x -> col
            ]
            pixel_end = [
                int(end_point[1] * meta['y_pixels'] / meta['y_range']),
                int(end_point[0] * meta['x_pixels'] / meta['x_range'])
            ]
            
            # 計算物理單位的實際長度（歐式距離）
            physical_length = np.sqrt(
                (end_point[0] - start_point[0]) ** 2 + 
                (end_point[1] - start_point[1]) ** 2
            )
            
            logger.info(f"轉換為像素座標: {pixel_start} -> {pixel_end}")
            logger.info(f"計算物理長度: {physical_length:.3f} nm")
            
            # 使用 IntAnalysis 計算剖面
            profile_data = IntAnalysis.get_line_profile(
                self.current_raw_data, 
                pixel_start, 
                pixel_end, 
                meta['scale']  # 物理比例因子
            )
            
            # 覆蓋計算得到的長度，使用正確的物理長度
            profile_data['length'] = float(physical_length)
            
            # 重新計算正確的距離數組
            num_points = len(profile_data['distance'])
            correct_distances = np.linspace(0, physical_length, num_points)
            profile_data['distance'] = correct_distances.tolist()
            
            # profile_data 已經包含完整的統計資訊，不需要重新計算
            
            logger.info(f"剖面計算成功，點數: {len(profile_data['distance'])}")
            
            return {
                "success": True,
                "profile_data": profile_data
            }
            
        except Exception as e:
            logger.error(f"計算高度剖面失敗: {str(e)}")
            logger.error(f"詳細錯誤: {traceback.format_exc()}")
            return {"success": False, "error": str(e)}

    def _matplotlib_to_plotly_colorscale(self, cmap_name, reverse=False, n_colors=256):
        """將 matplotlib colormap 轉換為 Plotly colorscale 格式"""
        try:
            # 獲取 matplotlib colormap
            cmap = cm.get_cmap(cmap_name)
            
            # 生成顏色點
            colors = []
            for i in range(n_colors):
                # 計算 0-1 之間的位置
                position = i / (n_colors - 1)
                
                # 如果需要反轉，則反轉位置
                if reverse:
                    color_position = 1.0 - position
                else:
                    color_position = position
                
                # 獲取該位置的顏色 (RGBA)
                rgba = cmap(color_position)
                
                # 轉換為十六進位顏色
                hex_color = to_hex(rgba[:3])  # 只使用 RGB，忽略 Alpha
                
                # Plotly colorscale 格式：[position, color]
                colors.append([position, hex_color])
            
            reverse_info = " (反轉)" if reverse else ""
            logger.info(f"matplotlib colormap '{cmap_name}'{reverse_info} 轉換完成，生成 {len(colors)} 個顏色點")
            return colors
            
        except Exception as e:
            logger.error(f"轉換 matplotlib colormap 失敗: {str(e)}")
            # 回退到簡單的灰階
            return [[0, '#000000'], [1, '#ffffff']]
    
    def _generate_plotly_config(self, raw_data, x_range, y_range, phys_unit, colormap):
        """生成 Plotly 的 data 和 layout 配置"""
        try:
            # 創建坐標軸
            y_pixels, x_pixels = raw_data.shape
            x = np.linspace(0, x_range, x_pixels).tolist()
            y = np.linspace(0, y_range, y_pixels).tolist()
            
            # 擴展的 matplotlib colormap 映射
            matplotlib_colormap_mapping = {
                # 單色系
                'Oranges': 'Oranges',
                'Blues': 'Blues',
                'Reds': 'Reds',
                'Greens': 'Greens',
                'Purples': 'Purples',
                'Greys': 'gray',
                
                # 科學可視化
                'Viridis': 'viridis',
                'Plasma': 'plasma',
                'Inferno': 'inferno',
                'Magma': 'magma',
                'Cividis': 'cividis',
                
                # 分歧色彩映射
                'RdYlBu': 'RdYlBu',
                'RdYlGn': 'RdYlGn',
                'Spectral': 'Spectral',
                'Coolwarm': 'coolwarm',
                
                # 彩虹和經典
                'Rainbow': 'rainbow',
                'Jet': 'jet',
                'Hot': 'hot',
                'Cool': 'cool',
                
                # 地形和其他
                'Terrain': 'terrain',
                'Ocean': 'ocean',
                'Copper': 'copper',
            }
            
            # 檢查是否需要反轉
            reverse = False
            if colormap.endswith('_r'):
                reverse = True
                base_colormap = colormap[:-2]  # 移除 '_r' 後綴
            else:
                base_colormap = colormap
            
            # 獲取對應的 matplotlib colormap 名稱
            mpl_cmap_name = matplotlib_colormap_mapping.get(base_colormap, 'viridis')
            
            logger.info(f"色彩映射轉換: {colormap} -> matplotlib.{mpl_cmap_name} (反轉: {reverse})")
            
            # 轉換 matplotlib colormap 到 Plotly 格式
            plotly_colormap = self._matplotlib_to_plotly_colorscale(mpl_cmap_name, reverse=reverse)
            
            # 計算 Z 值範圍
            z_data = raw_data.tolist()
            flat_z = [val for row in z_data for val in row]
            z_min = min(flat_z)
            z_max = max(flat_z)
            
            logger.info(f"數據範圍: {z_min:.3f} ~ {z_max:.3f}")
            
            # 創建 Plotly data 配置
            data = [{
                'type': 'heatmap',
                'z': z_data,
                'x': x,
                'y': y,
                'colorscale': plotly_colormap,
                'showscale': True,
                'zmin': z_min,
                'zmax': z_max,
                'colorbar': {
                    'title': {
                        'text': f'高度 ({phys_unit})',
                        'side': 'right'
                    },
                    'thickness': 20,
                    'len': 0.8,
                    'x': 1.02
                },
                'hovertemplate': (
                    'X: %{x:.2f} ' + phys_unit + '<br>' +
                    'Y: %{y:.2f} ' + phys_unit + '<br>' +
                    'Z: %{z:.3f} ' + phys_unit + '<br>' +
                    '<extra></extra>'
                )
            }]
            
            # 創建 Plotly layout 配置
            layout = {
                'title': '',
                'xaxis': {
                    'title': {'text': f'X ({phys_unit})'},
                    'constrain': 'domain',
                    'showgrid': True,
                    'gridcolor': '#e5e5e5',
                    'range': [0, x_range]
                },
                'yaxis': {
                    'title': {'text': f'Y ({phys_unit})'},
                    'scaleanchor': 'x',
                    'scaleratio': 1,
                    'constrain': 'domain',
                    'showgrid': True,
                    'gridcolor': '#e5e5e5',
                    'range': [0, y_range]
                },
                'margin': {'l': 60, 'r': 80, 't': 20, 'b': 60},
                'autosize': True,
                'plot_bgcolor': 'white',
                'paper_bgcolor': 'white'
            }
            
            # 創建 config 配置
            config = {
                'responsive': True,
                'displayModeBar': True,
                'displaylogo': False,
                'modeBarButtonsToRemove': [
                    'sendDataToCloud', 
                    'editInChartStudio',
                    'lasso2d',
                    'select2d'
                ]
            }
            
            reverse_info = " (反轉)" if reverse else ""
            logger.info(f"Plotly 配置生成完成，使用 matplotlib colormap: {mpl_cmap_name}{reverse_info}")
            
            return {
                'data': data,
                'layout': layout,
                'config': config
            }
            
        except Exception as e:
            logger.error(f"生成 Plotly 配置時出錯: {str(e)}")
            raise
    
    # 保留原有的解析方法...
    def _parse_txt_file(self, txt_file_path):
        """解析 TXT 檔案"""
        try:
            with open(txt_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            parameters = {}
            
            # 提取基本參數
            
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
    
    def apply_flatten(self, method="plane"):
        """應用平面化處理
        
        Args:
            method: 平面化方法 ('linewise_mean', 'linewise_poly', 'plane')
        """
        try:
            if self.current_raw_data is None:
                return {"success": False, "error": "沒有載入的影像數據"}
            
            logger.info(f"開始應用平面化處理，方法: {method}")
            
            # 使用 IntAnalysis 的平面化功能
            if method == "linewise_mean":
                processed_data = IntAnalysis.linewise_flatten_mean(self.current_processed_data)
            elif method == "linewise_poly":
                processed_data = IntAnalysis.linewise_flatten_polyfit(self.current_processed_data)
            elif method == "plane":
                processed_data = IntAnalysis.plane_flatten(self.current_processed_data)
            else:
                return {"success": False, "error": f"未知的平面化方法: {method}"}
            
            # 更新處理後的數據
            self.current_processed_data = processed_data
            self.processing_history.append(f"flatten_{method}")
            
            # 重新計算統計資訊
            statistics = self._calculate_statistics(processed_data)
            
            # 生成新的 Plotly 配置
            plotly_config = self._generate_plotly_config(
                processed_data, 
                self.current_metadata['x_range'], 
                self.current_metadata['y_range'], 
                self.current_metadata['phys_unit'], 
                "Oranges"
            )
            
            logger.info("影像平面化完成")
            
            return {
                "success": True,
                "statistics": statistics,
                "plotlyConfig": plotly_config
            }
        
        except Exception as e:
            logger.error(f"平面化影像時出錯: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def adjust_tilt(self, direction, fine_tune=False):
        """調整影像傾斜
        
        Args:
            direction: 傾斜方向 ('up', 'down', 'left', 'right')
            fine_tune: 是否為微調模式
        """
        try:
            if self.current_raw_data is None:
                return {"success": False, "error": "沒有載入的影像數據"}
            
            logger.info(f"開始調整影像傾斜，方向: {direction}, 微調: {fine_tune}")
            
            # 使用 IntAnalysis 的傾斜調整功能
            adjusted_data = IntAnalysis.tilt_image(
                self.current_processed_data, 
                direction, 
                step_size=5 if fine_tune else 10, 
                fine_tune=fine_tune
            )
            
            # 更新處理後的數據
            self.current_processed_data = adjusted_data
            self.processing_history.append(f"tilt_{direction}{'_fine' if fine_tune else ''}")
            
            # 重新計算統計資訊
            statistics = self._calculate_statistics(adjusted_data)
            
            # 生成新的 Plotly 配置
            plotly_config = self._generate_plotly_config(
                adjusted_data, 
                self.current_metadata['x_range'], 
                self.current_metadata['y_range'], 
                self.current_metadata['phys_unit'], 
                "Oranges"
            )
            
            logger.info("影像傾斜調整完成")
            
            return {
                "success": True,
                "statistics": statistics,
                "plotlyConfig": plotly_config
            }
        
        except Exception as e:
            logger.error(f"調整影像傾斜時出錯: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def reset_image_processing(self):
        """重置影像處理為原始狀態"""
        try:
            if self.current_raw_data is None:
                return {"success": False, "error": "沒有載入的影像數據"}
            
            logger.info("開始重置影像為原始狀態")
            
            # 重置處理後的數據為原始數據副本
            self.current_processed_data = self.current_raw_data.copy()
            self.processing_history = []
            
            # 重新計算統計資訊
            statistics = self._calculate_statistics(self.current_processed_data)
            
            # 生成新的 Plotly 配置
            plotly_config = self._generate_plotly_config(
                self.current_processed_data, 
                self.current_metadata['x_range'], 
                self.current_metadata['y_range'], 
                self.current_metadata['phys_unit'], 
                "Oranges"
            )
            
            logger.info("影像重置完成")
            
            return {
                "success": True,
                "statistics": statistics,
                "plotlyConfig": plotly_config
            }
        
        except Exception as e:
            logger.error(f"重置影像時出錯: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _load_int_file(self, txt_file_path, selected_filename, file_info):
        """載入 .int 檔案"""
        try:
            logger.info(f"載入 .int 檔案: {selected_filename}")
            
            # 構建完整的檔案路徑
            base_dir = os.path.dirname(txt_file_path)
            int_file_path = os.path.join(base_dir, selected_filename)
            
            if not os.path.exists(int_file_path):
                error_msg = f"INT 檔案不存在: {int_file_path}"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
            
            # 從實驗資訊中獲取基本參數
            exp_info = self.current_txt_data['experiment_info']
            
            # 提取參數
            try:
                scale = float(file_info['scale'])
                phys_unit = file_info['phys_unit']
                x_pixels = int(exp_info.get('xPixel', '256'))
                y_pixels = int(exp_info.get('yPixel', '256'))
                x_range = float(exp_info.get('XScanRange', '10.0'))
                y_range = float(exp_info.get('YScanRange', '10.0'))
            except (ValueError, KeyError) as e:
                error_msg = f"解析參數失敗: {e}"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
            
            # 解析 INT 檔案數據
            raw_data = self._parse_int_file(int_file_path, scale, x_pixels, y_pixels)
            
            # 存儲數據和元數據
            self.current_raw_data = raw_data
            self.current_processed_data = raw_data.copy()
            self.processing_history = []
            self.current_metadata = {
                'scale': scale,
                'phys_unit': phys_unit,
                'x_pixels': x_pixels,
                'y_pixels': y_pixels,
                'x_range': x_range,
                'y_range': y_range
            }
            
            # 計算統計資訊
            statistics = self._calculate_statistics(raw_data)
            
            # 生成 Plotly 配置
            plotly_config = self._generate_plotly_config(
                raw_data, x_range, y_range, phys_unit, "Oranges"
            )
            
            logger.info(f".int 檔案載入成功: {selected_filename}")
            
            return {
                "success": True,
                "name": file_info['caption'],
                "intFile": int_file_path,
                "txtFile": txt_file_path,
                "fileType": "int",
                "plotlyConfig": plotly_config,
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
            
        except Exception as e:
            error_msg = f"載入 .int 檔案時出錯: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def _load_dat_file(self, txt_file_path, selected_filename, file_info):
        """載入 .dat 檔案"""
        try:
            logger.info(f"載入 .dat 檔案: {selected_filename}")
            
            # 構建完整的檔案路徑
            base_dir = os.path.dirname(txt_file_path)
            dat_file_path = os.path.join(base_dir, selected_filename)
            
            if not os.path.exists(dat_file_path):
                error_msg = f"DAT 檔案不存在: {dat_file_path}"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
            
            # 找到對應的 dat_info
            dat_info = None
            for dat_file in self.current_txt_data['dat_files']:
                if dat_file['filename'] == selected_filename:
                    dat_info = dat_file
                    break
            
            if not dat_info:
                error_msg = f"找不到 DAT 檔案資訊: {selected_filename}"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
            
            # 使用 DatParser 解析檔案
            from core.parsers import DatParser
            
            parser = DatParser()
            dat_result = parser.parse(dat_file_path, dat_info)
            
            # 根據量測模式處理結果
            if dat_result['measurement_mode'] == 'CITS':
                return self._process_cits_result(dat_result, file_info, txt_file_path)
            else:
                return self._process_sts_result(dat_result, file_info, txt_file_path)
                
        except Exception as e:
            error_msg = f"載入 .dat 檔案時出錯: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def _process_cits_result(self, dat_result, file_info, txt_file_path):
        """處理 CITS 量測結果"""
        try:
            logger.info("處理 CITS 量測數據")
            
            # 獲取第一個偏壓的數據作為預設顯示
            data_3d = dat_result['data_3d']  # shape: (n_bias, grid_y, grid_x)
            bias_values = dat_result['bias_values']
            
            if len(data_3d) == 0:
                error_msg = "CITS 數據為空"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
            
            # 使用第一個偏壓的數據
            initial_data = data_3d[0]  # shape: (grid_y, grid_x)
            initial_bias = bias_values[0]
            
            # 獲取座標網格
            x_grid = dat_result['x_grid']
            y_grid = dat_result['y_grid']
            
            # 計算座標範圍
            x_range = float(np.max(x_grid) - np.min(x_grid))
            y_range = float(np.max(y_grid) - np.min(y_grid))
            
            # 生成 Plotly 配置
            plotly_config = self._generate_plotly_config(
                initial_data, x_range, y_range, "A", "RdBu_r"  # 使用 RdBu_r 配色更適合電性數據
            )
            
            # 計算統計資訊
            statistics = self._calculate_statistics(initial_data)
            
            logger.info(f"CITS 數據處理完成: {len(bias_values)} 個偏壓點")
            
            return {
                "success": True,
                "name": file_info['caption'],
                "datFile": dat_result['file_path'],
                "txtFile": txt_file_path,
                "fileType": "cits",
                "plotlyConfig": plotly_config,
                "colormap": "RdBu_r",
                "dimensions": {
                    "width": dat_result['grid_size'][0],
                    "height": dat_result['grid_size'][1],
                    "xRange": x_range,
                    "yRange": y_range
                },
                "physUnit": dat_result['units']['bias'],
                "statistics": statistics,
                "cits_data": {
                    "bias_values": bias_values.tolist(),
                    "current_bias_index": 0,
                    "current_bias": float(initial_bias),
                    "measurement_type": dat_result['measurement_type'],
                    "grid_size": dat_result['grid_size']
                }
            }
            
        except Exception as e:
            error_msg = f"處理 CITS 數據時出錯: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def _process_sts_result(self, dat_result, file_info, txt_file_path):
        """處理 STS 量測結果"""
        try:
            logger.info("處理 STS 量測數據")
            
            # STS 數據暫時只識別，不提供視覺化
            return {
                "success": True,
                "name": file_info['caption'],
                "datFile": dat_result['file_path'],
                "txtFile": txt_file_path,
                "fileType": "sts",
                "message": "STS 數據已載入，視覺化功能開發中",
                "sts_data": {
                    "bias_values": dat_result['bias_values'].tolist(),
                    "n_points": dat_result['n_points'],
                    "measurement_type": dat_result['measurement_type']
                }
            }
            
        except Exception as e:
            error_msg = f"處理 STS 數據時出錯: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}