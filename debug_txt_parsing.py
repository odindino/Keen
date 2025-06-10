#!/usr/bin/env python3
"""
Debug script to trace the exact values being processed
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

from backend.core.parsers.txt_parser import TxtParser

def debug_txt_parsing():
    TXT_FILE_PATH = '/Users/yangziliang/Git-Projects/keen/testfile/20250521_Janus Stacking SiO2_13K_113.txt'
    
    print("=== Debug TXT Parsing ===")
    print(f"Parsing: {TXT_FILE_PATH}")
    
    try:
        parser = TxtParser(TXT_FILE_PATH)
        result = parser.parse()
        
        if result.success:
            print("✅ TXT parsing successful")
            raw_data = result.data
            exp_info = raw_data.get('experiment_info', {})
            
            print(f"\n🔍 Raw experiment info values:")
            for key in ['xPixel', 'yPixel', 'XScanRange', 'YScanRange']:
                value = exp_info.get(key, 'NOT_FOUND')
                print(f"  {key}: '{value}' (type: {type(value)})")
            
            print(f"\n🔍 Testing conversions:")
            for key in ['xPixel', 'yPixel']:
                value = exp_info.get(key, 256)
                print(f"  {key}: {value} -> int: ", end='')
                try:
                    converted = int(value) if not isinstance(value, str) else int(float(value.strip()))
                    print(f"{converted} ✅")
                except Exception as e:
                    print(f"❌ {e}")
            
            for key in ['XScanRange', 'YScanRange']:
                value = exp_info.get(key, 100.0)
                print(f"  {key}: {value} -> float: ", end='')
                try:
                    converted = float(value) if not isinstance(value, str) else float(value.strip())
                    print(f"{converted} ✅")
                except Exception as e:
                    print(f"❌ {e}")
            
        else:
            print("❌ TXT parsing failed")
            print(f"Errors: {result.errors}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_txt_parsing()
