#!/usr/bin/env python3
"""
Debug script to isolate the ScanParameters creation issue
"""

import sys
import os
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(name)s - %(message)s')

# Add backend to path
module_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
if module_path not in sys.path:
    sys.path.append(module_path)

from backend.core.data_models import ScanParameters

def debug_scan_parameters():
    print("=== Debug ScanParameters Creation ===")
    
    # Test with known values
    test_values = {
        'x_pixel': '500',
        'y_pixel': '500', 
        'x_range': '10.000',
        'y_range': '10.000'
    }
    
    print(f"Test values: {test_values}")
    
    # Test safe conversion functions
    def safe_int_convert(value, default=256):
        if isinstance(value, str):
            try:
                return int(float(value.strip()))
            except (ValueError, AttributeError):
                print(f"❌ 無法轉換為整數: {value}, 使用默認值 {default}")
                return default
        return int(value) if value is not None else default
    
    def safe_float_convert(value, default=100.0):
        if isinstance(value, str):
            try:
                return float(value.strip())
            except (ValueError, AttributeError):
                print(f"❌ 無法轉換為浮點數: {value}, 使用默認值 {default}")
                return default
        return float(value) if value is not None else default
    
    try:
        print("\n🔍 Converting values:")
        x_pixel = safe_int_convert(test_values['x_pixel'])
        print(f"  x_pixel: {x_pixel} (type: {type(x_pixel)})")
        
        y_pixel = safe_int_convert(test_values['y_pixel'])
        print(f"  y_pixel: {y_pixel} (type: {type(y_pixel)})")
        
        x_range = safe_float_convert(test_values['x_range'])
        print(f"  x_range: {x_range} (type: {type(x_range)})")
        
        y_range = safe_float_convert(test_values['y_range'])
        print(f"  y_range: {y_range} (type: {type(y_range)})")
        
        print("\n🔍 Creating ScanParameters:")
        scan_params = ScanParameters(
            x_pixel=x_pixel,
            y_pixel=y_pixel,
            x_range=x_range,
            y_range=y_range
        )
        
        print(f"✅ ScanParameters created successfully!")
        print(f"  x_pixel: {scan_params.x_pixel}")
        print(f"  y_pixel: {scan_params.y_pixel}")
        print(f"  x_range: {scan_params.x_range}")
        print(f"  y_range: {scan_params.y_range}")
        
        # Test properties
        print(f"\n🔍 Testing properties:")
        print(f"  pixel_scale_x: {scan_params.pixel_scale_x}")
        print(f"  pixel_scale_y: {scan_params.pixel_scale_y}")
        print(f"  aspect_ratio: {scan_params.aspect_ratio}")
        print(f"  total_pixels: {scan_params.total_pixels}")
        
    except Exception as e:
        print(f"❌ Error creating ScanParameters: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_scan_parameters()
