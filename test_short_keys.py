#!/usr/bin/env python3
"""
測試當前短鍵生成的實際結果
Test current short key generation results
"""

import sys
import os
sys.path.append('/Users/yangziliang/Git-Projects/keen')

from backend.core.experiment_session import ExperimentSession

def test_short_keys():
    """測試短鍵生成"""
    
    txt_file_path = "/Users/yangziliang/Git-Projects/keen/testfile/20250521_Janus Stacking SiO2_13K_113.txt"
    
    try:
        session = ExperimentSession(txt_file_path)
        
        print("=== 可用短鍵 / Available Short Keys ===")
        for key in session.available_short_keys:
            full_key = session._short_key_to_full_key_map[key]
            print(f"短鍵: '{key}' -> 完整鍵: '{full_key}'")
        
        print("\n=== 完整鍵列表 / Full Key List ===")
        for key in session.get_all_full_keys():
            print(f"完整鍵: '{key}'")
        
        print("\n=== 文件類型分組 / Files by Type ===")
        print(f"INT 文件: {session.get_int_files()[:5]}...")  # 只顯示前5個
        print(f"DAT 文件: {session.get_dat_files()}")
        
        print("\n=== 測試期望的鍵值 / Test Expected Keys ===")
        test_keys = ['TopoFwd', 'TopoBwd', 'It_to_PC_Matrix']
        
        for test_key in test_keys:
            try:
                file_proxy = session[test_key]
                print(f"✅ '{test_key}' -> {file_proxy._file_key}")
            except KeyError as e:
                print(f"❌ '{test_key}' 不存在")
                # 嘗試類似的鍵值
                similar_keys = [k for k in session.available_short_keys if test_key.lower() in k or k in test_key.lower()]
                if similar_keys:
                    print(f"   相似鍵值: {similar_keys}")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🔑 測試短鍵生成...")
    success = test_short_keys()
    print(f"🎯 測試結果: {'成功' if success else '失敗'}")
