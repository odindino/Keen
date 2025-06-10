#!/usr/bin/env python3
import sys
import os
sys.path.append('/Users/yangziliang/Git-Projects/keen')

try:
    from backend.core.experiment_session import ExperimentSession
    
    print("🚀 KEEN Simplified API Quick Test")
    print("=" * 40)
    
    # Initialize session
    session = ExperimentSession("/Users/yangziliang/Git-Projects/keen/testfile/20250521_Janus Stacking SiO2_13K_113.txt")
    print(f"✅ Session created: {session.experiment_name}")
    
    # Test simplified API
    topofwd = session['TopoFwd']
    print(f"✅ session['TopoFwd'] = {type(topofwd).__name__}")
    print(f"   File: {topofwd._file_key}")
    print(f"   Shape: {topofwd.data.image.shape}")
    
    topobwd = session['TopoBwd']
    print(f"✅ session['TopoBwd'] = {type(topobwd).__name__}")
    print(f"   File: {topobwd._file_key}")
    print(f"   Shape: {topobwd.data.image.shape}")
    
    itcits = session['It_to_PC_Matrix']
    print(f"✅ session['It_to_PC_Matrix'] = {type(itcits).__name__}")
    print(f"   File: {itcits._file_key}")
    print(f"   Shape: {itcits.data.shape}")
    
    # Test case insensitive
    topofwd_lower = session['topofwd']
    print(f"✅ session['topofwd'] (lowercase) = {type(topofwd_lower).__name__}")
    print(f"   File: {topofwd_lower._file_key}")
    
    print("\n🎉 All tests passed! Simplified API works perfectly!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
