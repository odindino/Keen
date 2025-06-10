#!/usr/bin/env python3
"""
Debug script to trace the '>=' not supported between instances of 'int' and 'str' error
"""

import sys
import os
import logging
import traceback

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(name)s - %(message)s')

# Add backend to path
module_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
if module_path not in sys.path:
    sys.path.append(module_path)

from backend.core.experiment_session import ExperimentSession

def debug_int_parsing():
    TXT_FILE_PATH = '/Users/yangziliang/Git-Projects/keen/testfile/20250521_Janus Stacking SiO2_13K_113.txt'
    
    print("=== Debug INT Parsing Error ===")
    print(f"Loading session from: {TXT_FILE_PATH}")
    
    try:
        session = ExperimentSession(TXT_FILE_PATH)
        print("✅ Session loaded successfully")
        
        # Check TXT file parameters
        txt_files = session.get_txt_files()
        if txt_files:
            txt_key = txt_files[0]
            txt_proxy = session[txt_key]
            txt_data = txt_proxy.data
            
            print(f"\n📊 Scan Parameters:")
            scan_params = txt_data.scan_parameters
            print(f"  x_pixel: {scan_params.x_pixel} (type: {type(scan_params.x_pixel)})")
            print(f"  y_pixel: {scan_params.y_pixel} (type: {type(scan_params.y_pixel)})")
            print(f"  x_range: {scan_params.x_range} (type: {type(scan_params.x_range)})")
            print(f"  y_range: {scan_params.y_range} (type: {type(scan_params.y_range)})")
            
            print(f"\n📁 INT Files (first 3):")
            for i, int_file in enumerate(txt_data.int_files[:3]):
                print(f"  [{i}] {int_file.get('filename', 'N/A')}:")
                print(f"      scale: {int_file.get('scale', 'N/A')} (type: {type(int_file.get('scale'))})")
                print(f"      signal_type: {int_file.get('signal_type', 'N/A')}")
                print(f"      direction: {int_file.get('direction', 'N/A')}")
        
        print(f"\nTrying to access TopoFwd...")
        topofwd = session['TopoFwd']
        print(f"✅ TopoFwd proxy created: {topofwd._file_key}")
        
        print(f"\nTrying to access TopoFwd.data...")
        
        # Add some monkey patching to catch the exact comparison
        original_ge = int.__ge__
        
        def debug_ge(self, other):
            if isinstance(other, str):
                print(f"❌ FOUND THE ERROR! Comparing int({self}) >= str('{other}')")
                print("Stack trace:")
                traceback.print_stack()
                raise TypeError(f"'>=' not supported between instances of 'int' and 'str'")
            return original_ge(self, other)
        
        int.__ge__ = debug_ge
        
        try:
            data = topofwd.data
            print(f"✅ TopoFwd data loaded successfully")
        finally:
            # Restore original method
            int.__ge__ = original_ge
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nFull traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    debug_int_parsing()
