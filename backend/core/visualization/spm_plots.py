"""
SPM 專用繪圖模組
SPM-specific plotting module

提供標準化的 SPM 數據視覺化功能
Provides standardized SPM data visualization functions
"""

import numpy as np
import plotly.graph_objects as go
import plotly.figure_factory as ff
from plotly.subplots import make_subplots
from typing import Optional, Dict, Any, Tuple, List
import logging

logger = logging.getLogger(__name__)


class SPMPlotting:
    """
    SPM 專用繪圖類
    SPM-specific plotting class
    
    提供標準化的 SPM 數據視覺化方法
    Provides standardized SPM data visualization methods
    """
    
    # 默認顏色方案 / Default color schemes
    DEFAULT_COLORSCALE = 'Viridis'
    HEIGHT_COLORSCALE = 'RdYlBu_r'  # 適合高度數據 / Suitable for height data
    CURRENT_COLORSCALE = 'Blues'     # 適合電流數據 / Suitable for current data
    
    @staticmethod
    def plot_topography(image_data: np.ndarray,
                       physical_scale: Optional[Tuple[float, float]] = None,
                       title: str = "SPM Topography",
                       colorscale: str = None,
                       show_colorbar: bool = True,
                       **kwargs) -> go.Figure:
        """
        繪製 STM/AFM 地形圖
        Plot STM/AFM topography map
        
        Args:
            image_data: 2D 高度數據 / 2D height data
            physical_scale: 物理尺度 (x_range, y_range) in nm / Physical scale in nm
            title: 圖片標題 / Image title
            colorscale: 顏色方案 / Color scheme
            show_colorbar: 是否顯示色條 / Whether to show colorbar
            **kwargs: 額外的 Plotly 參數 / Additional Plotly parameters
            
        Returns:
            go.Figure: Plotly 圖形對象 / Plotly figure object
        """
        try:
            if colorscale is None:
                colorscale = SPMPlotting.HEIGHT_COLORSCALE
            
            # 創建圖形 / Create figure
            fig = go.Figure()
            
            # 設置坐標軸 / Set coordinate axes
            if physical_scale is not None:
                x_range, y_range = physical_scale
                x = np.linspace(0, x_range, image_data.shape[1])
                y = np.linspace(0, y_range, image_data.shape[0])
                x_title = "X (nm)"
                y_title = "Y (nm)"
            else:
                x = np.arange(image_data.shape[1])
                y = np.arange(image_data.shape[0])
                x_title = "X (pixels)"
                y_title = "Y (pixels)"
            
            # 添加熱力圖 / Add heatmap
            fig.add_trace(go.Heatmap(
                z=image_data,
                x=x,
                y=y,
                colorscale=colorscale,
                showscale=show_colorbar,
                hovertemplate='X: %{x}<br>Y: %{y}<br>Height: %{z:.3f}<extra></extra>'
            ))
            
            # 更新布局 / Update layout
            fig.update_layout(
                title=title,
                xaxis_title=x_title,
                yaxis_title=y_title,
                width=kwargs.get('width', 600),
                height=kwargs.get('height', 600),
                template="plotly_white",
                # 保持長寬比 / Maintain aspect ratio
                yaxis=dict(scaleanchor="x", scaleratio=1)
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"地形圖繪製失敗: {str(e)}")
            # 返回空圖 / Return empty figure
            return go.Figure().add_annotation(
                text=f"繪圖錯誤: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
    
    @staticmethod
    def plot_spatial_map(data_2d: np.ndarray,
                        title: str = "Spatial Map",
                        colorscale: str = None,
                        **kwargs) -> go.Figure:
        """
        繪製空間分佈圖
        Plot spatial distribution map
        
        Args:
            data_2d: 2D 數據 / 2D data
            title: 圖片標題 / Image title
            colorscale: 顏色方案 / Color scheme
            **kwargs: 額外參數 / Additional parameters
            
        Returns:
            go.Figure: Plotly 圖片對象 / Plotly figure object
        """
        try:
            if colorscale is None:
                colorscale = SPMPlotting.DEFAULT_COLORSCALE
            
            fig = go.Figure(data=go.Heatmap(
                z=data_2d,
                colorscale=colorscale,
                colorbar=dict(title="Value"),
                **kwargs
            ))
            
            fig.update_layout(
                title=title,
                xaxis_title="X (pixels)",
                yaxis_title="Y (pixels)",
                width=600,
                height=500
            )
            
            return fig
        except Exception as e:
            logger.error(f"空間分佈圖繪製失敗: {str(e)}")
            return go.Figure().add_annotation(
                text=f"繪圖錯誤: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
    
    @staticmethod
    def plot_line_profile(distances: np.ndarray, 
                         heights: np.ndarray,
                         title: str = "Line Profile",
                         x_unit: str = "nm",
                         y_unit: str = "nm",
                         **kwargs) -> go.Figure:
        """
        繪製線段剖面圖
        Plot line profile
        
        Args:
            distances: 距離陣列 / Distance array
            heights: 高度陣列 / Height array
            title: 圖片標題 / Image title
            x_unit: X軸單位 / X-axis unit
            y_unit: Y軸單位 / Y-axis unit
            **kwargs: 額外參數 / Additional parameters
            
        Returns:
            go.Figure: Plotly 圖形對象 / Plotly figure object
        """
        try:
            fig = go.Figure()
            
            # 添加線條 / Add line
            fig.add_trace(go.Scatter(
                x=distances,
                y=heights,
                mode='lines+markers',
                name='Height Profile',
                line=dict(color='royalblue', width=2),
                marker=dict(size=4),
                hovertemplate=f'Distance: %{{x:.2f}} {x_unit}<br>Height: %{{y:.3f}} {y_unit}<extra></extra>'
            ))
            
            # 更新布局 / Update layout
            fig.update_layout(
                title=title,
                xaxis_title=f"Distance ({x_unit})",
                yaxis_title=f"Height ({y_unit})",
                width=kwargs.get('width', 800),
                height=kwargs.get('height', 400),
                template="plotly_white",
                hovermode='x unified'
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"剖面圖繪製失敗: {str(e)}")
            return go.Figure().add_annotation(
                text=f"繪圖錯誤: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
    
    @staticmethod
    def plot_height_distribution(image_data: np.ndarray,
                                title: str = "Height Distribution",
                                bins: int = 50,
                                **kwargs) -> go.Figure:
        """
        繪製高度分佈直方圖
        Plot height distribution histogram
        
        Args:
            image_data: 2D 高度數據 / 2D height data
            title: 圖片標題 / Image title
            bins: 直方圖區間數 / Number of histogram bins
            **kwargs: 額外參數 / Additional parameters
            
        Returns:
            go.Figure: Plotly 圖形對象 / Plotly figure object
        """
        try:
            # 展平數據並移除 NaN / Flatten data and remove NaN
            heights = image_data.flatten()
            heights = heights[~np.isnan(heights)]
            
            if len(heights) == 0:
                raise ValueError("沒有有效的高度數據")
            
            fig = go.Figure()
            
            # 添加直方圖 / Add histogram
            fig.add_trace(go.Histogram(
                x=heights,
                nbinsx=bins,
                name='Height Distribution',
                marker=dict(color='lightblue', line=dict(color='darkblue', width=1)),
                hovertemplate='Height: %{x:.3f}<br>Count: %{y}<extra></extra>'
            ))
            
            # 計算統計數據 / Calculate statistics
            mean_height = np.mean(heights)
            std_height = np.std(heights)
            
            # 添加統計線 / Add statistical lines
            fig.add_vline(x=mean_height, line_dash="dash", line_color="red",
                         annotation_text=f"Mean: {mean_height:.3f}")
            
            # 更新布局 / Update layout
            fig.update_layout(
                title=f"{title}<br><sub>Mean: {mean_height:.3f}, Std: {std_height:.3f}</sub>",
                xaxis_title="Height (nm)",
                yaxis_title="Count",
                width=kwargs.get('width', 600),
                height=kwargs.get('height', 400),
                template="plotly_white"
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"高度分佈圖繪製失敗: {str(e)}")
            return go.Figure().add_annotation(
                text=f"繪圖錯誤: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
    
    @staticmethod
    def plot_roughness_analysis(roughness_data: Dict[str, float],
                               title: str = "Surface Roughness Analysis",
                               **kwargs) -> go.Figure:
        """
        繪製表面粗糙度分析圖
        Plot surface roughness analysis
        
        Args:
            roughness_data: 粗糙度數據字典 / Roughness data dictionary
            title: 圖片標題 / Image title
            **kwargs: 額外參數 / Additional parameters
            
        Returns:
            go.Figure: Plotly 圖形對象 / Plotly figure object
        """
        try:
            # 提取主要粗糙度參數 / Extract main roughness parameters
            params = ['Ra', 'Rq', 'Rz', 'Rp', 'Rv']
            values = [roughness_data.get(param, 0) for param in params]
            labels = [
                'Ra (算術平均粗糙度)',
                'Rq (均方根粗糙度)', 
                'Rz (最大高度差)',
                'Rp (最大峰高)',
                'Rv (最大谷深)'
            ]
            
            fig = go.Figure()
            
            # 添加柱狀圖 / Add bar chart
            fig.add_trace(go.Bar(
                x=labels,
                y=values,
                name='Roughness Parameters',
                marker=dict(color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']),
                text=[f'{v:.3f}' for v in values],
                textposition='auto',
                hovertemplate='%{x}<br>Value: %{y:.3f}<extra></extra>'
            ))
            
            # 更新布局 / Update layout
            fig.update_layout(
                title=title,
                xaxis_title="Roughness Parameters",
                yaxis_title="Value (nm)",
                width=kwargs.get('width', 800),
                height=kwargs.get('height', 500),
                template="plotly_white"
            )
            
            # 旋轉 X 軸標籤 / Rotate X-axis labels
            fig.update_xaxes(tickangle=45)
            
            return fig
            
        except Exception as e:
            logger.error(f"粗糙度分析圖繪製失敗: {str(e)}")
            return go.Figure().add_annotation(
                text=f"繪圖錯誤: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
    
    @staticmethod
    def create_analysis_dashboard(image_data: np.ndarray,
                                 line_profile_data: Optional[Dict] = None,
                                 roughness_data: Optional[Dict] = None,
                                 title: str = "SPM Analysis Dashboard") -> go.Figure:
        """
        創建綜合分析儀表板
        Create comprehensive analysis dashboard
        
        Args:
            image_data: 2D 高度數據 / 2D height data
            line_profile_data: 線段剖面數據 / Line profile data
            roughness_data: 粗糙度數據 / Roughness data
            title: 儀表板標題 / Dashboard title
            
        Returns:
            go.Figure: Plotly 圖形對象 / Plotly figure object
        """
        try:
            # 創建子圖 / Create subplots
            subplot_titles = ["Topography", "Height Distribution"]
            if line_profile_data:
                subplot_titles.append("Line Profile")
            if roughness_data:
                subplot_titles.append("Roughness Analysis")
            
            rows = 2 if len(subplot_titles) <= 2 else 2
            cols = 2 if len(subplot_titles) > 2 else len(subplot_titles)
            
            fig = make_subplots(
                rows=rows, cols=cols,
                subplot_titles=subplot_titles,
                specs=[[{"type": "heatmap"}, {"type": "histogram"}]] + 
                      ([[{"type": "scatter"}, {"type": "bar"}]] if len(subplot_titles) > 2 else [])
            )
            
            # 添加地形圖 / Add topography
            fig.add_trace(
                go.Heatmap(
                    z=image_data,
                    colorscale=SPMPlotting.HEIGHT_COLORSCALE,
                    showscale=True,
                    name="Height"
                ),
                row=1, col=1
            )
            
            # 添加高度分佈 / Add height distribution
            heights = image_data.flatten()
            heights = heights[~np.isnan(heights)]
            fig.add_trace(
                go.Histogram(
                    x=heights,
                    nbinsx=30,
                    name="Height Distribution",
                    marker=dict(color='lightblue')
                ),
                row=1, col=2
            )
            
            # 添加線段剖面（如果有）/ Add line profile (if available)
            if line_profile_data and rows > 1:
                fig.add_trace(
                    go.Scatter(
                        x=line_profile_data['distance'],
                        y=line_profile_data['height'],
                        mode='lines',
                        name="Line Profile",
                        line=dict(color='royalblue')
                    ),
                    row=2, col=1
                )
            
            # 添加粗糙度分析（如果有）/ Add roughness analysis (if available)
            if roughness_data and rows > 1:
                params = ['Ra', 'Rq', 'Rz']
                values = [roughness_data.get(param, 0) for param in params]
                fig.add_trace(
                    go.Bar(
                        x=params,
                        y=values,
                        name="Roughness",
                        marker=dict(color=['#1f77b4', '#ff7f0e', '#2ca02c'])
                    ),
                    row=2, col=2
                )
            
            # 更新布局 / Update layout
            fig.update_layout(
                title=title,
                height=800,
                template="plotly_white",
                showlegend=False
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"儀表板創建失敗: {str(e)}")
            return go.Figure().add_annotation(
                text=f"儀表板創建錯誤: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )