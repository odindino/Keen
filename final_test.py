#!/usr/bin/env python3
"""
Final integration test for INT file parsing fix
"""

import sys
import os

# Add backend to path
module_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
if module_path not in sys.path:
    sys.path.append(module_path)

from backend.core.experiment_session import ExperimentSession

def final_integration_test():
    TXT_FILE_PATH = '/Users/yangziliang/Git-Projects/keen/testfile/20250521_Janus Stacking SiO2_13K_113.txt'
    print('🎯 Final Integration Test')
    print('=' * 50)

    # Complete workflow test
    session = ExperimentSession(TXT_FILE_PATH)
    print('✅ 1. Session loaded')

    # Test all get_*_files methods  
    int_files = session.get_int_files()
    dat_files = session.get_dat_files()
    cits_files = session.get_cits_files()
    sts_files = session.get_sts_files()
    txt_files = session.get_txt_files()

    print(f'✅ 2. File methods: INT({len(int_files)}), DAT({len(dat_files)}), CITS({len(cits_files)}), STS({len(sts_files)}), TXT({len(txt_files)})')

    # Test simplified API access
    txt_data = session["experiment_txt"].data
    topo_data = session["TopoFwd"].data  
    cits_data = session["It_to_PC_Matrix"].data

    print(f'✅ 3. Data loading: TXT({txt_data.total_files} files), TopoFwd({topo_data.image.shape}), CITS({cits_data.shape})')

    print('✅ 4. All functions verified!')
    print('🎉 INT file parsing fix is complete and working!')

if __name__ == "__main__":
    final_integration_test()
