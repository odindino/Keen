"""
STS �h
STS analyzer

��T� STS I\xڄ��\A��K�
Coordinates STS spectroscopy data analysis workflow and state management
"""

import numpy as np
from typing import Dict, Any, Optional, Tuple, List

from .base_analyzer import BaseAnalyzer
from ..data_models import StsData
from ..visualization.spectroscopy_plots import SpectroscopyPlotting


class StsAnalyzer(BaseAnalyzer):
    """
    STS �h
    STS analyzer
    
    Л STS�ϧSI\	xڄ�t��\A
    Provides complete analysis workflow for STS (Scanning Tunneling Spectroscopy) data
    """
    
    def __init__(self, sts_data: StsData):
        """
        � STS �h
        Initialize STS analyzer
        
        Args:
            sts_data: StsData � / StsData instance
        """
        super().__init__(sts_data)
        
        # STS y��K / STS-specific state
        self.peak_analysis: Optional[Dict] = None
        self.gap_analysis: Optional[Dict] = None
        self.conductance_analysis: Optional[Dict] = None
        
        # �w� / Analysis history
        self.spectral_processing_steps: List[Dict] = []
    
    def analyze(self, **kwargs) -> Dict[str, Any]:
        """
        � STS x�
        Analyze STS data
        
        Args:
            **kwargs: M�x / Additional parameters
                - smooth: /&s�x� / Whether to smooth data
                - normalize: /&c� / Whether to normalize
            
        Returns:
            Dict: �P� / Analysis results
        """
        try:
            if not self.validate_input(**kwargs):
                return self._create_error_result("8eWI1W")
            
            sts_data = self.data
            
            # ��,q / Calculate basic statistics
            stats = self._calculate_sts_stats()
            
            # �I\y� / Analyze spectral features
            spectral_features = self._analyze_spectral_features(**kwargs)
            
            # u��,� / Create basic visualization
            plots = self._create_basic_plots()
            
            result = {
                'success': True,
                'data': {
                    'sts_data_info': {
                        'shape': sts_data.shape,
                        'n_points': sts_data.n_points,
                        'n_bias_points': sts_data.n_bias_points,
                        'measurement_mode': sts_data.measurement_mode
                    },
                    'bias_info': {
                        'bias_values': sts_data.bias_values.tolist(),
                        'bias_range': [float(np.min(sts_data.bias_values)), 
                                     float(np.max(sts_data.bias_values))],
                        'bias_step': float(np.mean(np.diff(sts_data.bias_values))) if len(sts_data.bias_values) > 1 else 0.0
                    },
                    'coordinates': {
                        'x_coords': sts_data.x_coords.tolist() if hasattr(sts_data.x_coords, 'tolist') else sts_data.x_coords,
                        'y_coords': sts_data.y_coords.tolist() if hasattr(sts_data.y_coords, 'tolist') else sts_data.y_coords
                    },
                    'stats': stats,
                    'spectral_features': spectral_features
                },
                'plots': plots,
                'metadata': {
                    'analyzer_type': 'STS',
                    'data_type': 'StsData',
                    'measurement_mode': sts_data.measurement_mode,
                    'n_points': sts_data.n_points,
                    'processing_steps_count': len(self.spectral_processing_steps)
                }
            }
            
            # � / Record analysis
            self._record_analysis(result, "sts_basic_analysis")
            
            return result
            
        except Exception as e:
            error_msg = f"STS �1W: {str(e)}"
            self._add_error(error_msg)
            return self._create_error_result(error_msg)
    
    def detect_peaks(self, point_index: Optional[int] = None, 
                    threshold_ratio: float = 0.1) -> Dict[str, Any]:
        """
        �,I\�<
        Detect spectral peaks
        
        Args:
            point_index: ���"None h:�@	� / Point index to analyze, None for all points
            threshold_ratio: �<�,�<ԋ / Threshold ratio for peak detection
            
        Returns:
            Dict: �<�P� / Peak analysis results
        """
        try:
            sts_data = self.data
            
            if point_index is not None:
                if point_index < 0 or point_index >= sts_data.n_points:
                    return self._create_error_result(f"�"���: {point_index}")
                
                # ��� / Analyze single point
                spectrum = sts_data.data_2d[:, point_index]
                coords = (sts_data.x_coords[point_index], sts_data.y_coords[point_index])
                analysis_type = 'single_point'
            else:
                # �sGI\ / Analyze average spectrum
                spectrum = np.mean(sts_data.data_2d, axis=1)
                coords = None
                analysis_type = 'average'
            
            # �,�< / Detect peaks
            peak_info = self._find_peaks(spectrum, sts_data.bias_values, threshold_ratio)
            
            # u��<� / Create peak visualization
            plots = self._create_peak_plots(spectrum, sts_data.bias_values, peak_info, analysis_type)
            
            self.peak_analysis = {
                'peaks': peak_info,
                'spectrum': spectrum.tolist(),
                'bias_values': sts_data.bias_values.tolist(),
                'analysis_type': analysis_type,
                'point_index': point_index,
                'coordinates': coords
            }
            
            result = {
                'success': True,
                'data': self.peak_analysis,
                'plots': plots,
                'metadata': {
                    'operation': 'peak_detection',
                    'analysis_type': analysis_type,
                    'point_index': point_index,
                    'threshold_ratio': threshold_ratio
                }
            }
            
            # � / Record analysis
            self._record_analysis(result, f"peak_detection_{analysis_type}")
            
            return result
            
        except Exception as e:
            error_msg = f"�<�,1W: {str(e)}"
            self._add_error(error_msg)
            return self._create_error_result(error_msg)
    
    def analyze_gap(self, point_index: Optional[int] = None,
                   gap_method: str = 'zero_crossing') -> Dict[str, Any]:
        """
        ���
        Analyze energy gap
        
        Args:
            point_index: ���"None h:�sGI\ / Point index, None for average spectrum
            gap_method: ����� / Gap analysis method
                - 'zero_crossing': �ޤ��
                - 'minimum':  <�
                - 'derivative': x�
            
        Returns:
            Dict: ���P� / Gap analysis results
        """
        try:
            sts_data = self.data
            
            if point_index is not None:
                if point_index < 0 or point_index >= sts_data.n_points:
                    return self._create_error_result(f"�"���: {point_index}")
                
                spectrum = sts_data.data_2d[:, point_index]
                analysis_type = 'single_point'
            else:
                spectrum = np.mean(sts_data.data_2d, axis=1)
                analysis_type = 'average'
            
            # ��� / Analyze gap
            gap_info = self._analyze_energy_gap(spectrum, sts_data.bias_values, gap_method)
            
            # u���� / Create gap visualization
            plots = self._create_gap_plots(spectrum, sts_data.bias_values, gap_info, analysis_type)
            
            self.gap_analysis = {
                'gap_info': gap_info,
                'spectrum': spectrum.tolist(),
                'bias_values': sts_data.bias_values.tolist(),
                'analysis_type': analysis_type,
                'point_index': point_index,
                'method': gap_method
            }
            
            result = {
                'success': True,
                'data': self.gap_analysis,
                'plots': plots,
                'metadata': {
                    'operation': 'gap_analysis',
                    'analysis_type': analysis_type,
                    'point_index': point_index,
                    'method': gap_method
                }
            }
            
            # � / Record analysis
            self._record_analysis(result, f"gap_analysis_{gap_method}")
            
            return result
            
        except Exception as e:
            error_msg = f"���1W: {str(e)}"
            self._add_error(error_msg)
            return self._create_error_result(error_msg)
    
    def calculate_conductance(self, point_index: Optional[int] = None) -> Dict[str, Any]:
        """
        ���
        Calculate differential conductance
        
        Args:
            point_index: ���"None h:�@	� / Point index, None for all points
            
        Returns:
            Dict: ��P� / Conductance analysis results
        """
        try:
            sts_data = self.data
            
            if point_index is not None:
                if point_index < 0 or point_index >= sts_data.n_points:
                    return self._create_error_result(f"�"���: {point_index}")
                
                current = sts_data.data_2d[:, point_index]
                analysis_type = 'single_point'
            else:
                # �@	ބsG / Calculate average of all points
                current = np.mean(sts_data.data_2d, axis=1)
                analysis_type = 'average'
            
            # ��� dI/dV / Calculate differential conductance dI/dV
            conductance = np.gradient(current, sts_data.bias_values)
            
            # �c�� (dI/dV)/(I/V) / Calculate normalized conductance
            voltage_nonzero = sts_data.bias_values[sts_data.bias_values != 0]
            current_nonzero = current[sts_data.bias_values != 0]
            conductance_nonzero = conductance[sts_data.bias_values != 0]
            
            normalized_conductance = np.zeros_like(conductance)
            valid_indices = sts_data.bias_values != 0
            normalized_conductance[valid_indices] = conductance_nonzero / (current_nonzero / voltage_nonzero)
            
            # u��� / Create conductance visualization
            plots = self._create_conductance_plots(sts_data.bias_values, current, 
                                                 conductance, normalized_conductance, analysis_type)
            
            self.conductance_analysis = {
                'current': current.tolist(),
                'conductance': conductance.tolist(),
                'normalized_conductance': normalized_conductance.tolist(),
                'bias_values': sts_data.bias_values.tolist(),
                'analysis_type': analysis_type,
                'point_index': point_index
            }
            
            result = {
                'success': True,
                'data': self.conductance_analysis,
                'plots': plots,
                'metadata': {
                    'operation': 'conductance_calculation',
                    'analysis_type': analysis_type,
                    'point_index': point_index
                }
            }
            
            # � / Record analysis
            self._record_analysis(result, f"conductance_{analysis_type}")
            
            return result
            
        except Exception as e:
            error_msg = f"��1W: {str(e)}"
            self._add_error(error_msg)
            return self._create_error_result(error_msg)
    
    def _calculate_sts_stats(self) -> Dict[str, Any]:
        """
        � STS x�q
        Calculate STS data statistics
        """
        try:
            sts_data = self.data
            data_2d = sts_data.data_2d
            bias_values = sts_data.bias_values
            
            stats = {
                'data_range': [float(np.min(data_2d)), float(np.max(data_2d))],
                'bias_statistics': {
                    'min_bias': float(np.min(bias_values)),
                    'max_bias': float(np.max(bias_values)),
                    'bias_step': float(np.mean(np.diff(bias_values))) if len(bias_values) > 1 else 0.0
                },
                'spectral_statistics': {
                    'avg_spectrum_min': float(np.min(np.mean(data_2d, axis=1))),
                    'avg_spectrum_max': float(np.max(np.mean(data_2d, axis=1))),
                    'avg_spectrum_mean': float(np.mean(data_2d)),
                    'point_variability': float(np.std(np.mean(data_2d, axis=0)))
                }
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"STS q�1W: {str(e)}")
            return {}
    
    def _analyze_spectral_features(self, **kwargs) -> Dict[str, Any]:
        """
        �I\y�
        Analyze spectral features
        """
        try:
            sts_data = self.data
            avg_spectrum = np.mean(sts_data.data_2d, axis=1)
            
            features = {
                'zero_bias_conductance': float(avg_spectrum[np.argmin(np.abs(sts_data.bias_values))]),
                'asymmetry': self._calculate_asymmetry(avg_spectrum, sts_data.bias_values),
                'spectral_width': self._calculate_spectral_width(avg_spectrum, sts_data.bias_values)
            }
            
            return features
            
        except Exception as e:
            self.logger.error(f"I\y��1W: {str(e)}")
            return {}
    
    def _find_peaks(self, spectrum: np.ndarray, bias_values: np.ndarray, 
                   threshold_ratio: float) -> Dict[str, Any]:
        """
        ~I\�<
        Find spectral peaks
        """
        from scipy.signal import find_peaks
        
        # -��<�,�x / Set peak detection parameters
        height_threshold = np.max(spectrum) * threshold_ratio
        peaks, properties = find_peaks(spectrum, height=height_threshold, distance=5)
        
        peak_info = {
            'peak_indices': peaks.tolist(),
            'peak_biases': bias_values[peaks].tolist(),
            'peak_heights': spectrum[peaks].tolist(),
            'n_peaks': len(peaks),
            'threshold_used': float(height_threshold)
        }
        
        return peak_info
    
    def _analyze_energy_gap(self, spectrum: np.ndarray, bias_values: np.ndarray, 
                          method: str) -> Dict[str, Any]:
        """
        ���
        Analyze energy gap
        """
        if method == 'minimum':
            gap_index = np.argmin(spectrum)
            gap_bias = bias_values[gap_index]
            gap_width = self._estimate_gap_width(spectrum, bias_values, gap_index)
        elif method == 'zero_crossing':
            # !��ޤ��
            zero_index = np.argmin(np.abs(bias_values))
            gap_bias = bias_values[zero_index]
            gap_width = self._estimate_gap_width(spectrum, bias_values, zero_index)
        else:
            gap_bias = 0.0
            gap_width = 0.0
        
        gap_info = {
            'gap_center': float(gap_bias),
            'gap_width': float(gap_width),
            'method': method
        }
        
        return gap_info
    
    def _estimate_gap_width(self, spectrum: np.ndarray, bias_values: np.ndarray, 
                           center_index: int) -> float:
        """
        0����
        Estimate gap width
        """
        # !����0�
        half_max = spectrum[center_index] + (np.max(spectrum) - spectrum[center_index]) / 2
        
        # ~J '<�Mn
        left_indices = np.where((spectrum[:center_index] > half_max))[0]
        right_indices = np.where((spectrum[center_index:] > half_max))[0] + center_index
        
        if len(left_indices) > 0 and len(right_indices) > 0:
            left_bias = bias_values[left_indices[-1]]
            right_bias = bias_values[right_indices[0]]
            gap_width = right_bias - left_bias
        else:
            gap_width = 0.0
        
        return gap_width
    
    def _calculate_asymmetry(self, spectrum: np.ndarray, bias_values: np.ndarray) -> float:
        """
        �I\1'
        Calculate spectral asymmetry
        """
        zero_index = np.argmin(np.abs(bias_values))
        
        if zero_index == 0 or zero_index == len(spectrum) - 1:
            return 0.0
        
        positive_part = spectrum[zero_index:]
        negative_part = spectrum[:zero_index+1][::-1]  # �I�O��
        
        # ��w��2L�
        min_length = min(len(positive_part), len(negative_part))
        pos_avg = np.mean(positive_part[:min_length])
        neg_avg = np.mean(negative_part[:min_length])
        
        if pos_avg + neg_avg != 0:
            asymmetry = (pos_avg - neg_avg) / (pos_avg + neg_avg)
        else:
            asymmetry = 0.0
        
        return float(asymmetry)
    
    def _calculate_spectral_width(self, spectrum: np.ndarray, bias_values: np.ndarray) -> float:
        """
        �I\�
        Calculate spectral width
        """
        # (��\�I\즄��
        weights = spectrum - np.min(spectrum)  # �d��
        if np.sum(weights) == 0:
            return 0.0
        
        weighted_mean = np.average(bias_values, weights=weights)
        weighted_var = np.average((bias_values - weighted_mean)**2, weights=weights)
        spectral_width = np.sqrt(weighted_var)
        
        return float(spectral_width)
    
    def _create_basic_plots(self) -> Dict[str, Any]:
        """
        u��,�h
        Create basic visualization plots
        """
        try:
            plots = {}
            
            sts_data = self.data
            
            # � STS I\ / Multiple STS spectra
            plots['sts_spectra'] = SpectroscopyPlotting.plot_multiple_sts_spectra(
                sts_data.bias_values, sts_data.data_2d, 
                title=f"STS Spectra - {sts_data.measurement_mode}"
            )
            
            # sGI\ / Average spectrum
            avg_spectrum = np.mean(sts_data.data_2d, axis=1)
            plots['average_spectrum'] = SpectroscopyPlotting.plot_sts_spectrum(
                sts_data.bias_values, avg_spectrum, title="Average STS Spectrum"
            )
            
            return plots
            
        except Exception as e:
            self.logger.error(f"u��,h1W: {str(e)}")
            return {}
    
    def _create_peak_plots(self, spectrum: np.ndarray, bias_values: np.ndarray,
                          peak_info: Dict, analysis_type: str) -> Dict[str, Any]:
        """
        u��<�h
        Create peak analysis plots
        """
        try:
            plots = {}
            
            # �<�I\ / Spectrum with peak markers
            plots['spectrum_with_peaks'] = SpectroscopyPlotting.plot_sts_spectrum_with_markers(
                bias_values, spectrum, peak_info['peak_biases'],
                title=f"Peak Analysis ({analysis_type})"
            )
            
            return plots
            
        except Exception as e:
            self.logger.error(f"u��<h1W: {str(e)}")
            return {}
    
    def _create_gap_plots(self, spectrum: np.ndarray, bias_values: np.ndarray,
                         gap_info: Dict, analysis_type: str) -> Dict[str, Any]:
        """
        u����h
        Create gap analysis plots
        """
        try:
            plots = {}
            
            # ���I\ / Spectrum with gap markers
            plots['spectrum_with_gap'] = SpectroscopyPlotting.plot_sts_spectrum_with_gap(
                bias_values, spectrum, gap_info['gap_center'], gap_info['gap_width'],
                title=f"Gap Analysis ({analysis_type})"
            )
            
            return plots
            
        except Exception as e:
            self.logger.error(f"u���h1W: {str(e)}")
            return {}
    
    def _create_conductance_plots(self, bias_values: np.ndarray, current: np.ndarray,
                                conductance: np.ndarray, normalized_conductance: np.ndarray,
                                analysis_type: str) -> Dict[str, Any]:
        """
        u���h
        Create conductance analysis plots
        """
        try:
            plots = {}
            
            # I-V �� / I-V curve
            plots['iv_curve'] = SpectroscopyPlotting.plot_sts_spectrum(
                bias_values, current, title=f"I-V Curve ({analysis_type})"
            )
            
            # dI/dV �� / dI/dV curve
            plots['conductance'] = SpectroscopyPlotting.plot_sts_spectrum(
                bias_values, conductance, title=f"Differential Conductance ({analysis_type})"
            )
            
            # c�� / Normalized conductance
            plots['normalized_conductance'] = SpectroscopyPlotting.plot_sts_spectrum(
                bias_values, normalized_conductance, title=f"Normalized Conductance ({analysis_type})"
            )
            
            return plots
            
        except Exception as e:
            self.logger.error(f"u��h1W: {str(e)}")
            return {}
    
    def validate_input(self, **kwargs) -> bool:
        """
        WI STS 8ex�
        Validate STS input data
        """
        if not super().validate_input(**kwargs):
            return False
        
        if not isinstance(self.data, StsData):
            self._add_error("x��/ StsData ^�")
            return False
        
        if self.data.data_2d is None:
            self._add_error("StsData : data_2d x�")
            return False
        
        if not isinstance(self.data.data_2d, np.ndarray):
            self._add_error("data_2d �/ numpy xD")
            return False
        
        if self.data.data_2d.ndim != 2:
            self._add_error("data_2d �/ 2D xD")
            return False
        
        if self.data.bias_values is None:
            self._add_error("StsData : bias_values")
            return False
        
        if len(self.data.bias_values) != self.data.data_2d.shape[0]:
            self._add_error("bias_values w� data_2d , �9M")
            return False
        
        return True