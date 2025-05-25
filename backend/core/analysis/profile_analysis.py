# backend/core/analysis/profile_analysis.py
import numpy as np
import logging
import matplotlib.pyplot as plt
import io
import base64

logger = logging.getLogger(__name__)

class ProfileAnalysis:
    """
    剖面分析的相關功能
    """
    
    @staticmethod
    def calculate_roughness(height_data):
        """
        計算粗糙度參數
        
        Args:
            height_data: 高度數據數組
            
        Returns:
            dict: 粗糙度參數字典
        """
        try:
            height_array = np.array(height_data)
            
            # 移除趨勢
            x = np.arange(len(height_array))
            fit = np.polyfit(x, height_array, 1)
            trend = np.polyval(fit, x)
            detrended = height_array - trend
            
            # 計算常見粗糙度參數
            Ra = np.mean(np.abs(detrended))  # 算術平均粗糙度
            Rq = np.sqrt(np.mean(np.square(detrended)))  # 均方根粗糙度
            Rz = np.max(detrended) - np.min(detrended)  # 最大高度差
            
            # 峰度和偏度
            Rsk = np.mean(detrended**3) / (np.mean(detrended**2)**1.5)  # 偏度
            Rku = np.mean(detrended**4) / (np.mean(detrended**2)**2)  # 峰度
            
            return {
                'Ra': float(Ra),
                'Rq': float(Rq),
                'Rz': float(Rz),
                'Rsk': float(Rsk),
                'Rku': float(Rku)
            }
        except Exception as e:
            logger.error(f"計算粗糙度失敗: {str(e)}")
            return {}
    
    @staticmethod
    def shift_profile_to_zero(height_data):
        """
        將剖面最小值歸零
        
        Args:
            height_data: 高度數據數組
            
        Returns:
            list: 處理後的高度數據
        """
        try:
            height_array = np.array(height_data)
            min_value = np.min(height_array)
            return (height_array - min_value).tolist()
        except Exception as e:
            logger.error(f"高度歸零處理失敗: {str(e)}")
            return height_data
    
    @staticmethod
    def find_critical_points(profile_data, prominence=0.5, width=None):
        """
        在剖面中尋找關鍵點（峰、谷）
        
        Args:
            profile_data: 剖面數據字典
            prominence: 峰的突出度
            width: 峰的最小寬度
            
        Returns:
            dict: 峰和谷的位置
        """
        try:
            from scipy.signal import find_peaks
            
            x = np.array(profile_data['distance'])
            z = np.array(profile_data['height'])
            
            # 找峰
            peaks, _ = find_peaks(z, prominence=prominence, width=width)
            
            # 找谷（取負值找峰）
            valleys, _ = find_peaks(-z, prominence=prominence, width=width)
            
            # 收集結果
            peak_positions = [float(x[p]) for p in peaks]
            peak_heights = [float(z[p]) for p in peaks]
            valley_positions = [float(x[v]) for v in valleys]
            valley_depths = [float(z[v]) for v in valleys]
            
            return {
                'peaks': {
                    'positions': peak_positions,
                    'heights': peak_heights
                },
                'valleys': {
                    'positions': valley_positions,
                    'depths': valley_depths
                }
            }
        except Exception as e:
            logger.error(f"尋找關鍵點失敗: {str(e)}")
            return {'peaks': {'positions': [], 'heights': []}, 
                   'valleys': {'positions': [], 'depths': []}}
    
    @staticmethod
    def measure_distances(positions, reference=None):
        """
        測量位置之間的距離
        
        Args:
            positions: 位置數組
            reference: 參考位置（如果提供，則計算到此參考點的距離）
            
        Returns:
            list: 距離列表
        """
        try:
            pos_array = np.array(positions)
            
            if reference is not None:
                # 計算到參考點的距離
                distances = np.abs(pos_array - reference)
            else:
                # 計算相鄰點間的距離
                distances = np.diff(np.sort(pos_array))
            
            return distances.tolist()
        except Exception as e:
            logger.error(f"測量距離失敗: {str(e)}")
            return []
        
    @staticmethod
    def generate_profile_image(profile_data, shift_zero=False, auto_scale=True, show_peaks=False, peak_sensitivity=1.0, title="Line Profile"):
        """
        生成剖面圖像
        
        Args:
            profile_data: 剖面數據字典
            shift_zero: 是否將最小值歸零
            auto_scale: 是否自動縮放坐標軸
            show_peaks: 是否顯示峰值
            peak_sensitivity: 峰值檢測敏感度
            title: 圖像標題
            
        Returns:
            base64編碼的PNG圖像
        """
        try:
            from scipy.signal import find_peaks
            
            x = np.array(profile_data['distance'])
            z = np.array(profile_data['height'])
            
            # 是否將最小值歸零
            if shift_zero and len(z) > 0:
                z = z - np.min(z)
            
            # 創建圖像
            fig, ax = plt.subplots(figsize=(8, 4), dpi=100)
            ax.plot(x, z, '-', linewidth=1.5)
            
            # 設置標題和標籤
            ax.set_title(title)
            ax.set_xlabel('Distance (nm)')
            ax.set_ylabel('Height (nm)')
            ax.grid(True, linestyle='--', alpha=0.7)
            
            # 尋找峰值和谷值
            if show_peaks:
                # 使用敏感度調整突出度參數
                prominence = (np.max(z) - np.min(z)) * 0.05 / peak_sensitivity
                
                # 找峰
                peaks, _ = find_peaks(z, prominence=prominence)
                
                # 找谷（取負值找峰）
                valleys, _ = find_peaks(-z, prominence=prominence)
                
                # 繪製峰值和谷值
                ax.plot(x[peaks], z[peaks], 'ro', markersize=4)
                ax.plot(x[valleys], z[valleys], 'go', markersize=4)
                
                # 添加峰值和谷值的標籤
                for i, peak in enumerate(peaks):
                    ax.text(x[peak], z[peak] + (np.max(z) - np.min(z)) * 0.02, 
                        f'P{i+1}', ha='center', fontsize=8)
                
                for i, valley in enumerate(valleys):
                    ax.text(x[valley], z[valley] - (np.max(z) - np.min(z)) * 0.02, 
                        f'V{i+1}', ha='center', fontsize=8)
            
            # 是否自動縮放
            if not auto_scale and 'xlim' in profile_data and 'ylim' in profile_data:
                ax.set_xlim(profile_data['xlim'])
                ax.set_ylim(profile_data['ylim'])
            
            # 添加一些統計信息
            if 'stats' in profile_data and profile_data['stats']:
                stats = profile_data['stats']
                stat_text = f"Range: {stats['range']:.2f} nm, RMS: {stats['rms']:.2f} nm"
                ax.annotate(stat_text, xy=(0.02, 0.02), xycoords='axes fraction', 
                        fontsize=8, bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8))
            
            # 轉換為PNG圖像
            buf = io.BytesIO()
            fig.tight_layout()
            fig.savefig(buf, format='png', dpi=100)
            buf.seek(0)
            img_data = buf.read()
            img_base64 = base64.b64encode(img_data).decode('utf-8')
            buf.close()
            plt.close(fig)
            
            return img_base64
        except Exception as e:
            logger.error(f"生成剖面圖像失敗: {str(e)}")
            return ""