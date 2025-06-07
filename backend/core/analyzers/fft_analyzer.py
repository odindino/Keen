"""
FFT h
FFT analyzer

 ¬T¿ FFT ;ß„å\AŒÀK¡
Coordinates FFT frequency domain analysis workflow and state management
"""

import numpy as np
from typing import Dict, Any, Optional, Union
from scipy.fft import fft2, fftfreq, fftshift

from .base_analyzer import BaseAnalyzer
from ..data_models import TopoData


class FFTAnalyzer(BaseAnalyzer):
    """
    FFT h
    FFT analyzer
    
    Ð› 2D xÚ„ FFT ;ßŸý
    Provides FFT frequency domain analysis for 2D data
    """
    
    def __init__(self, data: TopoData):
        """
        Ë FFT h
        Initialize FFT analyzer
        
        Args:
            data: TopoData æ‹ / TopoData instance
        """
        super().__init__(data)
        
        # FFT yšÀK / FFT-specific state
        self.fft_result: Optional[np.ndarray] = None
        self.power_spectrum: Optional[np.ndarray] = None
        self.freq_x: Optional[np.ndarray] = None
        self.freq_y: Optional[np.ndarray] = None
    
    def analyze(self, **kwargs) -> Dict[str, Any]:
        """
        ÷L FFT 
        Perform FFT analysis
        
        Args:
            **kwargs: MÃx / Additional parameters
                - use_current: /&(vMÏsfŒ	Ø True
                - apply_window: /&É(—ýxØ False
                - window_type: —ýx^‹Ø 'hann'
            
        Returns:
            Dict: FFT Pœ / FFT analysis results
        """
        try:
            if not self.validate_input(**kwargs):
                return self._create_error_result("8eWI1W")
            
            topo_data = self.data
            use_current = kwargs.get('use_current', True)
            apply_window = kwargs.get('apply_window', False)
            window_type = kwargs.get('window_type', 'hann')
            
            # xÇ„Ï / Select image to analyze
            if use_current and topo_data.current_image is not None:
                image = topo_data.current_image
                image_type = 'processed'
            else:
                image = topo_data.image
                image_type = 'original'
            
            # É(—ýxïx	/ Apply window function (optional)
            if apply_window:
                image = self._apply_window(image, window_type)
            
            # ÷L 2D FFT / Perform 2D FFT
            self.fft_result = fft2(image)
            self.fft_result = fftshift(self.fft_result)  # ö;‡û0-Ã
            
            # —Ÿ‡\ / Calculate power spectrum
            self.power_spectrum = np.abs(self.fft_result)**2
            
            # ;‡ø / Generate frequency axes
            pixel_scale_x = topo_data.pixel_scale_x
            pixel_scale_y = topo_data.pixel_scale_y
            
            self.freq_x = fftshift(fftfreq(image.shape[1], pixel_scale_x))
            self.freq_y = fftshift(fftfreq(image.shape[0], pixel_scale_y))
            
            # —Pœ / Calculate analysis results
            analysis_results = self._analyze_fft_results()
            
            # uúï– / Create visualization
            plots = self._create_fft_plots()
            
            result = {
                'success': True,
                'data': {
                    'fft_info': {
                        'image_shape': image.shape,
                        'image_type': image_type,
                        'window_applied': apply_window,
                        'window_type': window_type if apply_window else None
                    },
                    'frequency_info': {
                        'freq_range_x': [float(np.min(self.freq_x)), float(np.max(self.freq_x))],
                        'freq_range_y': [float(np.min(self.freq_y)), float(np.max(self.freq_y))],
                        'freq_resolution_x': float(self.freq_x[1] - self.freq_x[0]),
                        'freq_resolution_y': float(self.freq_y[1] - self.freq_y[0])
                    },
                    'analysis_results': analysis_results
                },
                'plots': plots,
                'metadata': {
                    'analyzer_type': 'FFT',
                    'data_type': 'TopoData',
                    'image_type': image_type,
                    'window_applied': apply_window
                }
            }
            
            #  / Record analysis
            self._record_analysis(result, "fft_analysis")
            
            return result
            
        except Exception as e:
            error_msg = f"FFT 1W: {str(e)}"
            self._add_error(error_msg)
            return self._create_error_result(error_msg)
    
    def get_radial_average(self) -> Dict[str, Any]:
        """
        —‘sGŸ‡\
        Calculate radial average power spectrum
        
        Returns:
            Dict: ‘sGPœ / Radial average results
        """
        try:
            if self.power_spectrum is None:
                return self._create_error_result("*÷L FFT ")
            
            # —‘sG / Calculate radial average
            center_x = self.power_spectrum.shape[1] // 2
            center_y = self.power_spectrum.shape[0] // 2
            
            Y, X = np.ogrid[:self.power_spectrum.shape[0], :self.power_spectrum.shape[1]]
            r = np.sqrt((X - center_x)**2 + (Y - center_y)**2)
            
            r_int = r.astype(int)
            max_r = int(np.max(r))
            
            radial_profile = np.zeros(max_r + 1)
            for i in range(max_r + 1):
                mask = (r_int == i)
                if np.any(mask):
                    radial_profile[i] = np.mean(self.power_spectrum[mask])
            
            # —É„;‡ / Calculate corresponding frequencies
            freq_radial = np.arange(max_r + 1) * min(abs(self.freq_x[1] - self.freq_x[0]), 
                                                   abs(self.freq_y[1] - self.freq_y[0]))
            
            # uú‘sG / Create radial average plot
            plots = self._create_radial_plots(freq_radial, radial_profile)
            
            result = {
                'success': True,
                'data': {
                    'frequencies': freq_radial.tolist(),
                    'radial_power': radial_profile.tolist(),
                    'max_frequency': float(np.max(freq_radial)),
                    'dominant_frequency': float(freq_radial[np.argmax(radial_profile[1:])+1])  # ’d DC Ï
                },
                'plots': plots,
                'metadata': {
                    'operation': 'radial_average',
                    'max_radius': max_r
                }
            }
            
            #  / Record analysis
            self._record_analysis(result, "radial_average")
            
            return result
            
        except Exception as e:
            error_msg = f"‘sG—1W: {str(e)}"
            self._add_error(error_msg)
            return self._create_error_result(error_msg)
    
    def _apply_window(self, image: np.ndarray, window_type: str) -> np.ndarray:
        """
        É(—ýx
        Apply window function
        """
        if window_type == 'hann':
            window_x = np.hanning(image.shape[1])
            window_y = np.hanning(image.shape[0])
            window_2d = np.outer(window_y, window_x)
        elif window_type == 'hamming':
            window_x = np.hamming(image.shape[1])
            window_y = np.hamming(image.shape[0])
            window_2d = np.outer(window_y, window_x)
        elif window_type == 'blackman':
            window_x = np.blackman(image.shape[1])
            window_y = np.blackman(image.shape[0])
            window_2d = np.outer(window_y, window_x)
        else:
            # Øºéb—!—ýx	/ Default to rectangular window (no windowing)
            window_2d = np.ones_like(image)
        
        return image * window_2d
    
    def _analyze_fft_results(self) -> Dict[str, Any]:
        """
         FFT Pœ
        Analyze FFT results
        """
        try:
            analysis = {}
            
            if self.power_spectrum is not None:
                # ú,q / Basic statistics
                analysis['power_spectrum_stats'] = {
                    'max_power': float(np.max(self.power_spectrum)),
                    'min_power': float(np.min(self.power_spectrum)),
                    'mean_power': float(np.mean(self.power_spectrum)),
                    'total_power': float(np.sum(self.power_spectrum))
                }
                
                # DC Ï / DC component
                center_x = self.power_spectrum.shape[1] // 2
                center_y = self.power_spectrum.shape[0] // 2
                analysis['dc_component'] = float(self.power_spectrum[center_y, center_x])
                
                # ~ú;;‡Ï / Find dominant frequency components
                # ’d DC ÏDÑ„@ß
                power_copy = self.power_spectrum.copy()
                power_copy[center_y-2:center_y+3, center_x-2:center_x+3] = 0
                
                # ~ú 'Ÿ‡„Mn
                max_indices = np.unravel_index(np.argmax(power_copy), power_copy.shape)
                dominant_freq_x = self.freq_x[max_indices[1]]
                dominant_freq_y = self.freq_y[max_indices[0]]
                
                analysis['dominant_frequencies'] = {
                    'freq_x': float(dominant_freq_x),
                    'freq_y': float(dominant_freq_y),
                    'magnitude': float(dominant_freq_x**2 + dominant_freq_y**2)**0.5,
                    'power': float(power_copy[max_indices])
                }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"FFT Pœ1W: {str(e)}")
            return {}
    
    def _create_fft_plots(self) -> Dict[str, Any]:
        """
        uú FFT ï–h
        Create FFT visualization plots
        """
        try:
            plots = {}
            
            if self.power_spectrum is not None:
                # (x:¦o:Ÿ‡\ / Display power spectrum in log scale
                log_power = np.log10(self.power_spectrum + 1e-10)  # û <M log(0)
                
                # áÉr¿(iv„jýx
                # 1¼’	€„ FFT j!Duúú,„Ïð
                plots['power_spectrum'] = {
                    'type': '2D_log_power_spectrum',
                    'description': 'Log-scale 2D power spectrum',
                    'data_shape': log_power.shape,
                    'freq_range_x': [float(np.min(self.freq_x)), float(np.max(self.freq_x))],
                    'freq_range_y': [float(np.min(self.freq_y)), float(np.max(self.freq_y))]
                }
                
                # FFT øM / FFT phase plot
                phase = np.angle(self.fft_result)
                plots['phase_spectrum'] = {
                    'type': '2D_phase_spectrum',
                    'description': 'Phase spectrum',
                    'data_shape': phase.shape
                }
            
            return plots
            
        except Exception as e:
            self.logger.error(f"uú FFT h1W: {str(e)}")
            return {}
    
    def _create_radial_plots(self, frequencies: np.ndarray, 
                           radial_profile: np.ndarray) -> Dict[str, Any]:
        """
        uú‘sGh
        Create radial average plots
        """
        try:
            plots = {}
            
            plots['radial_average'] = {
                'type': 'radial_power_spectrum',
                'description': 'Radially averaged power spectrum',
                'x_data': frequencies.tolist(),
                'y_data': radial_profile.tolist(),
                'x_label': 'Spatial Frequency (1/nm)',
                'y_label': 'Power'
            }
            
            return plots
            
        except Exception as e:
            self.logger.error(f"uú‘h1W: {str(e)}")
            return {}
    
    def validate_input(self, **kwargs) -> bool:
        """
        WI FFT 8exÚ
        Validate FFT input data
        """
        if not super().validate_input(**kwargs):
            return False
        
        if not isinstance(self.data, TopoData):
            self._add_error("xÚÅ/ TopoData ^‹")
            return False
        
        if self.data.image is None:
            self._add_error("TopoData : image xÚ")
            return False
        
        if not isinstance(self.data.image, np.ndarray):
            self._add_error("image Å/ numpy xD")
            return False
        
        if self.data.image.ndim != 2:
            self._add_error("image Å/ 2D xD")
            return False
        
        return True