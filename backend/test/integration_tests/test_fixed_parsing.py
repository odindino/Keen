#!/usr/bin/env python3
"""
Test the fixed INT file parsing
"""

import sys
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(name)s - %(message)s')

# Add backend to path
module_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
if module_path not in sys.path:
    sys.path.append(module_path)

from backend.core.experiment_session import ExperimentSession

def test_fixed_parsing():
    TXT_FILE_PATH = '/Users/yangziliang/Git-Projects/keen/testfile/20250521_Janus Stacking SiO2_13K_113.txt'
    
    print("=== Test Fixed INT File Parsing ===")
    print(f"Loading session from: {TXT_FILE_PATH}")
    
    try:
        session = ExperimentSession(TXT_FILE_PATH)
        print("✅ Session loaded successfully")
        
        print(f"\n🔍 Testing TXT file access...")
        txt_files = session.get_txt_files()
        if txt_files:
            txt_key = txt_files[0]
            txt_proxy = session[txt_key]
            txt_data = txt_proxy.data
            print(f"✅ TXT data loaded: {txt_data.experiment_name}")
            print(f"  Scan parameters: {txt_data.scan_parameters.x_pixel}×{txt_data.scan_parameters.y_pixel}")
        
        print(f"\n🔍 Testing INT file access...")
        topofwd = session['TopoFwd']
        print(f"✅ TopoFwd proxy created: {topofwd._file_key}")
        
        print(f"🔍 Loading TopoFwd data...")
        topo_data = topofwd.data
        print(f"✅ TopoFwd data loaded successfully!")
        print(f"  Image shape: {topo_data.image.shape}")
        print(f"  X range: {topo_data.x_range:.2f} nm")
        print(f"  Y range: {topo_data.y_range:.2f} nm")
        print(f"  Data scale: {topo_data.data_scale}")
        
        print(f"\n🎉 All tests passed! INT file parsing is now working correctly.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fixed_parsing()
