#!/usr/bin/env python3
"""
測試 ExperimentSession 功能
Test ExperimentSession functionality
"""

from backend.core.experiment_session import ExperimentSession
import tempfile
import os

def test_experiment_session():
    """測試 ExperimentSession 的基本功能"""
    
    # 創建臨時測試環境
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"📁 測試目錄: {temp_dir}")
        
        # 創建測試 TXT 文件
        test_txt_file = os.path.join(temp_dir, 'test_experiment.txt')
        with open(test_txt_file, 'w') as f:
            f.write('# Test experiment file\n')
            f.write('experiment_name: Test Experiment\n')
            f.write('scan_x: 100\n')
            f.write('scan_y: 100\n')
            f.write('\n')
            f.write('[INT Files]\n')
            f.write('test_topo.int: Topo Forward scan\n')
        
        # 創建測試 INT 文件
        test_int_file = os.path.join(temp_dir, 'test_topo.int')
        with open(test_int_file, 'wb') as f:
            f.write(b'\x00' * 1024)  # 1KB 的假數據
        
        try:
            # 創建 ExperimentSession
            session = ExperimentSession(test_txt_file)
            print('✅ ExperimentSession 創建成功')
            
            # 測試基本屬性
            print(f'📄 實驗名稱: {session.experiment_name}')
            print(f'📊 可用文件: {session.available_files}')
            
            # 測試短鍵映射
            short_keys = session.available_short_keys
            print(f'🔑 可用短鍵: {short_keys}')
            
            # 測試 FileProxy 創建
            if short_keys:
                first_key = list(short_keys)[0]
                print(f'🧪 測試鍵: {first_key}')
                
                try:
                    file_proxy = session.get_file(first_key)
                    print('✅ FileProxy 創建成功')
                    print(f'📋 FileProxy 文件鍵: {file_proxy.file_key}')
                    print(f'🔗 FileProxy 會話連接: {file_proxy.session is not None}')
                except Exception as e:
                    print(f'❌ FileProxy 創建失敗: {e}')
            
            return True
            
        except Exception as e:
            print(f'❌ 測試失敗: {e}')
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    print("🧪 開始測試 ExperimentSession...")
    success = test_experiment_session()
    print(f"🎯 測試結果: {'成功' if success else '失敗'}")
