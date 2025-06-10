#!/usr/bin/env python3
"""
測試簡化的 API 用法
Test simplified API usage
"""

import sys
import os
sys.path.append('/Users/yangziliang/Git-Projects/keen')

from backend.core.experiment_session import ExperimentSession

def test_simplified_api():
    """測試簡化的 API"""
    
    print("🚀 測試簡化的 API 用法...")
    
    try:
        # 您期望的簡化用法
        session = ExperimentSession("/Users/yangziliang/Git-Projects/keen/testfile/20250521_Janus Stacking SiO2_13K_113.txt")
        
        print("=== 簡化 API 測試 ===")
        
        # 測試期望的用法
        topofwd = session['TopoFwd']
        topobwd = session['TopoBwd'] 
        itcits = session['It_to_PC_Matrix']
        
        print(f"✅ topofwd = session['TopoFwd']")
        print(f"   文件: {topofwd._file_key}")
        print(f"   類型: {topofwd.file_type}")
        
        print(f"✅ topobwd = session['TopoBwd']")
        print(f"   文件: {topobwd._file_key}")
        print(f"   類型: {topobwd.file_type}")
        
        print(f"✅ itcits = session['It_to_PC_Matrix']")
        print(f"   文件: {itcits._file_key}")
        print(f"   類型: {itcits.file_type}")
        
        print("\n=== 測試其他常用短鍵 ===")
        
        # 測試其他可能有用的短鍵
        common_keys = ['Lia1RFwd', 'Lia1RBwd', 'Lia1R_Matrix']
        
        for key in common_keys:
            try:
                proxy = session[key]
                print(f"✅ session['{key}'] -> {proxy._file_key}")
            except KeyError:
                print(f"❌ session['{key}'] 不存在")
        
        print("\n=== 測試不區分大小寫 ===")
        
        # 測試不區分大小寫
        case_tests = ['topofwd', 'TOPOBWD', 'it_to_pc_matrix']
        
        for key in case_tests:
            try:
                proxy = session[key]
                print(f"✅ session['{key}'] -> {proxy._file_key}")
            except KeyError:
                print(f"❌ session['{key}'] 不存在")
                
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_simplified_api()
    print(f"\n🎯 測試結果: {'成功' if success else '失敗'}")
