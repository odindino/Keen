"""
光譜繪圖模組
Spectroscopy plotting module

提供 STS、CITS 等光譜數據的專業視覺化功能
Provides professional visualization functions for STS, CITS spectroscopy data
"""

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Optional, Dict, Any, List, Tuple
import logging

logger = logging.getLogger(__name__)


class SpectroscopyPlotting:
    """
    光譜繪圖類
    Spectroscopy plotting class
    
    提供標準化的光譜數據視覺化方法
    Provides standardized spectroscopy data visualization methods
    """
    
    # 默認顏色方案 / Default color schemes
    STS_COLORSCALE = 'RdYlBu'      # 適合 STS 數據 / Suitable for STS data
    CITS_COLORSCALE = 'Viridis'    # 適合 CITS 數據 / Suitable for CITS data
    CONDUCTANCE_COLORSCALE = 'RdBu' # 適合電導率數據 / Suitable for conductance data
    
    @staticmethod
    def plot_sts_spectrum(bias_values: np.ndarray, 
                         current: np.ndarray,
                         conductance: Optional[np.ndarray] = None,
                         title: str = "STS Spectrum",
                         show_conductance: bool = True,
                         **kwargs) -> go.Figure:
        """
        繪製 STS 光譜
        Plot STS spectrum
        
        Args:
            bias_values: 偏壓值陣列 / Bias voltage array
            current: 電流值陣列 / Current array
            conductance: 電導率陣列（可選）/ Conductance array (optional)
            title: 圖片標題 / Image title
            show_conductance: 是否顯示電導率 / Whether to show conductance
            **kwargs: 額外參數 / Additional parameters
            
        Returns:
            go.Figure: Plotly 圖形對象 / Plotly figure object
        """
        try:
            # 決定是否創建雙 Y 軸 / Decide whether to create dual Y-axis
            if conductance is not None and show_conductance:
                fig = make_subplots(specs=[[{"secondary_y": True}]])
            else:
                fig = go.Figure()
            
            # 添加電流曲線 / Add current curve
            fig.add_trace(
                go.Scatter(
                    x=bias_values,
                    y=current,
                    mode='lines',
                    name='Current (I)',
                    line=dict(color='blue', width=2),
                    hovertemplate='Bias: %{x:.3f} V<br>Current: %{y:.2e} A<extra></extra>'
                )
            )
            
            # 添加電導率曲線（如果有）/ Add conductance curve (if available)
            if conductance is not None and show_conductance:
                fig.add_trace(
                    go.Scatter(
                        x=bias_values,
                        y=conductance,
                        mode='lines',
                        name='Conductance (dI/dV)',
                        line=dict(color='red', width=2),
                        hovertemplate='Bias: %{x:.3f} V<br>Conductance: %{y:.2e} S<extra></extra>'
                    ),
                    secondary_y=True
                )
                
                # 設置 Y 軸標籤 / Set Y-axis labels
                fig.update_yaxes(title_text="Current (A)", secondary_y=False, title_font_color="blue")
                fig.update_yaxes(title_text="Conductance (S)", secondary_y=True, title_font_color="red")
            else:
                fig.update_yaxes(title_text="Current (A)")
            
            # 更新布局 / Update layout
            fig.update_layout(
                title=title,
                xaxis_title="Bias Voltage (V)",
                width=kwargs.get('width', 800),
                height=kwargs.get('height', 500),
                template="plotly_white",
                hovermode='x unified'
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"STS 光譜繪製失敗: {str(e)}")
            return go.Figure().add_annotation(
                text=f"繪圖錯誤: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
    
    @staticmethod
    def plot_multiple_sts_spectra(bias_values: np.ndarray,
                                 spectra_data: np.ndarray,
                                 position_labels: Optional[List[str]] = None,
                                 title: str = "Multiple STS Spectra",
                                 max_curves: int = 10,
                                 **kwargs) -> go.Figure:
        """
        繪製多條 STS 光譜
        Plot multiple STS spectra
        
        Args:
            bias_values: 偏壓值陣列 / Bias voltage array
            spectra_data: 光譜數據 (n_bias, n_positions) / Spectra data
            position_labels: 位置標籤列表 / Position labels list
            title: 圖片標題 / Image title
            max_curves: 最大顯示曲線數 / Maximum number of curves to display
            **kwargs: 額外參數 / Additional parameters
            
        Returns:
            go.Figure: Plotly 圖形對象 / Plotly figure object
        """
        try:
            fig = go.Figure()
            
            n_positions = spectra_data.shape[1]
            
            # 選擇要顯示的位置 / Select positions to display
            if n_positions > max_curves:
                step = n_positions // max_curves
                positions_to_plot = range(0, n_positions, step)
            else:
                positions_to_plot = range(n_positions)
            
            # 顏色映射 / Color mapping
            colors = [f'hsl({i * 360 / len(positions_to_plot)}, 70%, 50%)' 
                     for i in range(len(positions_to_plot))]
            
            # 添加每條光譜 / Add each spectrum
            for i, pos_idx in enumerate(positions_to_plot):
                label = position_labels[pos_idx] if position_labels else f'Position {pos_idx}'
                
                fig.add_trace(go.Scatter(
                    x=bias_values,
                    y=spectra_data[:, pos_idx],
                    mode='lines',
                    name=label,
                    line=dict(color=colors[i], width=1.5),
                    hovertemplate=f'{label}<br>Bias: %{{x:.3f}} V<br>Current: %{{y:.2e}} A<extra></extra>'
                ))
            
            # 更新布局 / Update layout
            fig.update_layout(
                title=f"{title}<br><sub>Showing {len(positions_to_plot)} of {n_positions} spectra</sub>",
                xaxis_title="Bias Voltage (V)",
                yaxis_title="Current (A)",
                width=kwargs.get('width', 900),
                height=kwargs.get('height', 600),
                template="plotly_white",
                hovermode='closest'
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"多光譜繪製失敗: {str(e)}")
            return go.Figure().add_annotation(
                text=f"繪圖錯誤: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
    
    @staticmethod
    def plot_cits_overview(data_3d: np.ndarray, 
                          bias_values: np.ndarray,
                          selected_biases: Optional[List[float]] = None,
                          title: str = "CITS Overview",
                          **kwargs) -> go.Figure:
        """
        繪製 CITS 多偏壓概覽圖
        Plot CITS multi-bias overview
        
        Args:
            data_3d: 3D CITS 數據 (n_bias, y, x) / 3D CITS data
            bias_values: 偏壓值陣列 / Bias values array
            selected_biases: 選定的偏壓值列表 / Selected bias values list
            title: 圖片標題 / Image title
            **kwargs: 額外參數 / Additional parameters
            
        Returns:
            go.Figure: Plotly 圖形對象 / Plotly figure object
        """
        try:
            # 選擇要顯示的偏壓 / Select biases to display
            if selected_biases is None:
                # 自動選擇均勻分布的偏壓 / Automatically select evenly distributed biases
                n_show = min(6, len(bias_values))
                indices = np.linspace(0, len(bias_values)-1, n_show, dtype=int)
                selected_indices = indices
                selected_bias_values = bias_values[indices]
            else:
                # 根據指定偏壓值找索引 / Find indices based on specified bias values
                selected_indices = []
                selected_bias_values = []
                for bias in selected_biases:
                    idx = np.argmin(np.abs(bias_values - bias))
                    selected_indices.append(idx)
                    selected_bias_values.append(bias_values[idx])
            
            # 創建子圖 / Create subplots
            n_plots = len(selected_indices)
            cols = min(3, n_plots)
            rows = (n_plots + cols - 1) // cols
            
            subplot_titles = [f"Bias: {bias:.3f} V" for bias in selected_bias_values]
            
            fig = make_subplots(
                rows=rows, cols=cols,
                subplot_titles=subplot_titles,
                horizontal_spacing=0.1,
                vertical_spacing=0.1
            )
            
            # 添加每個偏壓的圖像 / Add image for each bias
            for i, idx in enumerate(selected_indices):
                row = (i // cols) + 1
                col = (i % cols) + 1
                
                fig.add_trace(
                    go.Heatmap(
                        z=data_3d[idx],
                        colorscale=SpectroscopyPlotting.CITS_COLORSCALE,
                        showscale=(i == 0),  # 只在第一個圖顯示色條
                        hovertemplate=f'Bias: {selected_bias_values[i]:.3f} V<br>X: %{{x}}<br>Y: %{{y}}<br>Current: %{{z:.2e}} A<extra></extra>'
                    ),
                    row=row, col=col
                )
            
            # 更新布局 / Update layout
            fig.update_layout(
                title=title,
                width=kwargs.get('width', 900),
                height=kwargs.get('height', 600),
                template="plotly_white"
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"CITS 概覽圖繪製失敗: {str(e)}")
            return go.Figure().add_annotation(
                text=f"繪圖錯誤: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
    
    @staticmethod
    def plot_band_map(data_2d: np.ndarray,
                     bias_values: np.ndarray,
                     positions: np.ndarray,
                     title: str = "Energy Band Map",
                     use_log_scale: bool = False,
                     **kwargs) -> go.Figure:
        """
        繪製能帶圖（位置 vs 偏壓）
        Plot energy band map (position vs bias)
        
        Args:
            data_2d: 2D 數據 (n_bias, n_positions) / 2D data
            bias_values: 偏壓值陣列 / Bias values array
            positions: 位置陣列 / Position array
            title: 圖片標題 / Image title
            use_log_scale: 是否使用對數尺度 / Whether to use log scale
            **kwargs: 額外參數 / Additional parameters
            
        Returns:
            go.Figure: Plotly 圖形對象 / Plotly figure object
        """
        try:
            # 處理數據 / Process data
            plot_data = data_2d.copy()
            if use_log_scale:
                # 避免對負值取對數 / Avoid taking log of negative values
                plot_data = np.log10(np.abs(plot_data) + 1e-15)
            
            fig = go.Figure()
            
            # 添加熱力圖 / Add heatmap
            fig.add_trace(go.Heatmap(
                z=plot_data,
                x=positions,
                y=bias_values,
                colorscale=SpectroscopyPlotting.CONDUCTANCE_COLORSCALE,
                showscale=True,
                hovertemplate='Position: %{x:.1f}<br>Bias: %{y:.3f} V<br>Intensity: %{z:.2e}<extra></extra>'
            ))
            
            # 更新布局 / Update layout
            intensity_label = "log10|Current| (A)" if use_log_scale else "Current (A)"
            
            fig.update_layout(
                title=title,
                xaxis_title="Position",
                yaxis_title="Bias Voltage (V)",
                width=kwargs.get('width', 800),
                height=kwargs.get('height', 600),
                template="plotly_white"
            )
            
            # 更新色條標籤 / Update colorbar label
            fig.update_traces(
                colorbar=dict(title=intensity_label)
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"能帶圖繪製失敗: {str(e)}")
            return go.Figure().add_annotation(
                text=f"繪圖錯誤: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
    
    @staticmethod
    def plot_spectral_features(features_data: Dict,
                              title: str = "Spectral Features Analysis",
                              **kwargs) -> go.Figure:
        """
        繪製光譜特徵分析結果
        Plot spectral features analysis results
        
        Args:
            features_data: 特徵數據字典 / Features data dictionary
            title: 圖片標題 / Image title
            **kwargs: 額外參數 / Additional parameters
            
        Returns:
            go.Figure: Plotly 圖形對象 / Plotly figure object
        """
        try:
            features = features_data.get('features', [])
            if not features:
                return go.Figure().add_annotation(
                    text="沒有檢測到光譜特徵",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False
                )
            
            # 提取數據 / Extract data
            positions = [f['position_index'] for f in features]
            bias_values = [f['bias_value'] for f in features]
            intensities = [f['intensity'] for f in features]
            feature_types = [f.get('type', 'unknown') for f in features]
            
            fig = go.Figure()
            
            # 按特徵類型分組繪製 / Plot by feature type groups
            unique_types = list(set(feature_types))
            colors = ['red', 'blue', 'green', 'orange', 'purple']
            
            for i, feature_type in enumerate(unique_types):
                # 過濾該類型的特徵 / Filter features of this type
                type_positions = [pos for pos, typ in zip(positions, feature_types) if typ == feature_type]
                type_biases = [bias for bias, typ in zip(bias_values, feature_types) if typ == feature_type]
                type_intensities = [intensity for intensity, typ in zip(intensities, feature_types) if typ == feature_type]
                
                fig.add_trace(go.Scatter(
                    x=type_positions,
                    y=type_biases,
                    mode='markers',
                    marker=dict(
                        size=[abs(intensity) * 1e12 + 5 for intensity in type_intensities],  # 根據強度調整大小
                        color=colors[i % len(colors)],
                        opacity=0.7,
                        line=dict(width=1, color='black')
                    ),
                    name=f'{feature_type.capitalize()} Features',
                    hovertemplate=f'Type: {feature_type}<br>Position: %{{x}}<br>Bias: %{{y:.3f}} V<br>Intensity: %{{text:.2e}} A<extra></extra>',
                    text=type_intensities
                ))
            
            # 更新布局 / Update layout
            fig.update_layout(
                title=f"{title}<br><sub>Total features: {len(features)}</sub>",
                xaxis_title="Position Index",
                yaxis_title="Bias Voltage (V)",
                width=kwargs.get('width', 800),
                height=kwargs.get('height', 600),
                template="plotly_white",
                hovermode='closest'
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"光譜特徵圖繪製失敗: {str(e)}")
            return go.Figure().add_annotation(
                text=f"繪圖錯誤: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )