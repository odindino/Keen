#!/usr/bin/env python3
"""
Debug script to isolate the TxtData creation issue
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

from backend.core.data_models import ScanParameters, TxtData
from backend.core.parsers.txt_parser import TxtParser

def debug_txt_data_creation():
    print("=== Debug TxtData Creation ===")
    
    TXT_FILE_PATH = '/Users/yangziliang/Git-Projects/keen/testfile/20250521_Janus Stacking SiO2_13K_113.txt'
    
    try:
        # Parse TXT file first
        parser = TxtParser(TXT_FILE_PATH)
        result = parser.parse()
        
        if not result.success:
            print(f"❌ TXT parsing failed: {result.errors}")
            return
        
        raw_data = result.data
        exp_info = raw_data.get('experiment_info', {})
        
        print("✅ TXT parsing successful")
        
        # Create ScanParameters
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
        
        scan_params = ScanParameters(
            x_pixel=safe_int_convert(exp_info.get('xPixel', 256)),
            y_pixel=safe_int_convert(exp_info.get('yPixel', 256)),
            x_range=safe_float_convert(exp_info.get('XScanRange', 100.0)),
            y_range=safe_float_convert(exp_info.get('YScanRange', 100.0))
        )
        
        print("✅ ScanParameters created successfully")
        
        # Now try to create TxtData
        print("\n🔍 Creating TxtData...")
        txt_data = TxtData(
            experiment_info=exp_info,
            scan_parameters=scan_params,
            int_files=raw_data.get('int_files', []),
            dat_files=raw_data.get('dat_files', []),
            signal_types=raw_data.get('signal_types', [])
        )
        
        print("✅ TxtData created successfully")
        print(f"  experiment_name: {txt_data.experiment_name}")
        print(f"  total_files: {txt_data.total_files}")
        
        # Test properties that might cause issues
        print(f"\n🔍 Testing TxtData properties:")
        print(f"  scan_parameters.x_pixel: {txt_data.scan_parameters.x_pixel}")
        print(f"  scan_parameters.y_pixel: {txt_data.scan_parameters.y_pixel}")
        print(f"  scan_parameters.x_range: {txt_data.scan_parameters.x_range}")
        print(f"  scan_parameters.y_range: {txt_data.scan_parameters.y_range}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_txt_data_creation()
