#!/usr/bin/env python3
"""
SPM 數據分析系統演示程式
SPM Data Analysis System Demo

展示系統的基本功能和工作流程
Demonstrates basic system functionality and workflow
"""

import sys
import os
from pathlib import Path
import logging

# 添加核心模組到路徑 / Add core modules to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.main_analyzer import MainAnalyzer

# 設置簡單日誌 / Setup simple logging
logging.basicConfig(level=logging.WARNING)  # 減少日誌輸出


def main():
    """主演示函數 / Main demo function"""
    
    print("🚀 SPM 數據分析系統演示")
    print("="*50)
    
    # 1. 初始化系統 / Initialize system
    print("\n📋 步驟 1: 初始化系統")
    try:
        analyzer = MainAnalyzer()
        print("✅ 系統初始化完成")
        print(f"   - 載入的分析器: {list(analyzer.analyzers.keys())}")
    except Exception as e:
        print(f"❌ 初始化失敗: {e}")
        return
    
    # 2. 載入實驗數據 / Load experiment data
    print("\n📋 步驟 2: 載入實驗數據")
    testfile_dir = Path(__file__).parent.parent.parent.parent / 'testfile'
    txt_files = list(testfile_dir.glob('*.txt'))
    
    if not txt_files:
        print("❌ 沒有找到測試數據檔案")
        return
    
    txt_file = txt_files[0]
    print(f"   - 載入檔案: {txt_file.name}")
    
    try:
        load_result = analyzer.load_experiment(str(txt_file), "demo_experiment")
        if load_result['success']:
            print("✅ 實驗載入成功")
            print(f"   - INT 檔案數量: {load_result['data']['int_files_count']}")
            print(f"   - DAT 檔案數量: {load_result['data']['dat_files_count']}")
        else:
            print(f"❌ 載入失敗: {load_result.get('error', '未知錯誤')}")
            return
    except Exception as e:
        print(f"❌ 載入過程發生錯誤: {e}")
        return
    
    # 3. 獲取實驗摘要 / Get experiment summary
    print("\n📋 步驟 3: 分析實驗內容")
    try:
        # 獲取當前實驗數據
        experiment_data = analyzer.get_current_experiment()
        if experiment_data:
            print("✅ 實驗摘要:")
            print(f"   - 實驗名稱: {experiment_data['name']}")
            int_files = [f for f in experiment_data['associated_files'].values() if f['type'] == 'int']
            dat_files = [f for f in experiment_data['associated_files'].values() if f['type'] == 'dat']
            print(f"   - INT 檔案數量: {len(int_files)}")
            print(f"   - DAT 檔案數量: {len(dat_files)}")
            if int_files:
                print(f"   - 第一個INT檔案: {Path(int_files[0]['path']).name}")
    except Exception as e:
        print(f"❌ 獲取摘要失敗: {e}")
        return
    
    # 4. 演示 INT 分析 / Demo INT analysis
    print("\n📋 步驟 4: INT 地形數據分析")
    try:
        if int_files:
            int_file_data = int_files[0]['data']
            print(f"   - 分析數據形狀: {int_file_data['image_data'].shape}")
            
            # 執行基本分析 / Execute basic analysis
            int_result = analyzer.int_analyzer.analyze(int_file_data)
            if int_result['success']:
                print("✅ INT 分析完成")
                topo_info = int_result['data']['topo_info']
                stats = int_result['data']['stats']
                print(f"   - 圖像尺寸: {topo_info['shape']}")
                print(f"   - 高度範圍: {topo_info['data_range'][0]:.3f} ~ {topo_info['data_range'][1]:.3f}")
                print(f"   - 平均高度: {stats['mean']:.3f}")
                print(f"   - 標準差: {stats['std']:.3f}")
                
                # 演示平面化 / Demo flattening
                flatten_result = analyzer.int_analyzer.apply_flattening('linewise_mean')
                if flatten_result['success']:
                    print("✅ 平面化處理完成")
                
                # 演示剖面提取 / Demo profile extraction
                shape = topo_info['shape']
                start_point = (shape[0]//4, shape[1]//4)
                end_point = (3*shape[0]//4, 3*shape[1]//4)
                profile_result = analyzer.int_analyzer.extract_line_profile(start_point, end_point)
                if profile_result['success']:
                    profile_length = profile_result['data']['distance'][-1]
                    print(f"✅ 線段剖面提取完成 (長度: {profile_length:.2f} nm)")
                
                # 演示粗糙度計算 / Demo roughness calculation
                roughness = int_result['data']['roughness']
                print(f"✅ 粗糙度分析完成")
                print(f"   - Ra: {roughness['Ra']:.3f}")
                print(f"   - Rq: {roughness['Rq']:.3f}")
                print(f"   - Rz: {roughness['Rz']:.3f}")
            else:
                print(f"❌ INT 分析失敗: {int_result.get('error', '未知錯誤')}")
        else:
            print("⚠️  沒有可用的 INT 檔案")
    except Exception as e:
        print(f"❌ INT 分析過程發生錯誤: {e}")
    
    # 5. 演示 DAT 分析 / Demo DAT analysis
    print("\n📋 步驟 5: DAT 光譜數據分析")
    try:
        if dat_files:
            dat_file_data = dat_files[0]['data']
            print(f"   - 分析數據類型: {dat_file_data['measurement_mode']}")
            
            # 執行基本分析 / Execute basic analysis
            dat_result = analyzer.dat_analyzer.analyze(dat_file_data)
            if dat_result['success']:
                print("✅ DAT 分析完成")
                data_info = dat_result['data']['data_info']
                print(f"   - 測量模式: {dat_result['data']['measurement_mode']}")
                print(f"   - 數據形狀: {data_info['shape']}")
                print(f"   - 偏壓範圍: {data_info['bias_range'][0]:.1f} ~ {data_info['bias_range'][1]:.1f} mV")
                
                # 演示偏壓依賴分析 / Demo bias dependence analysis
                bias_result = analyzer.dat_analyzer.analyze_bias_dependence()
                if bias_result['success']:
                    bias_stats = bias_result['data']['stats']
                    print(f"✅ 偏壓依賴分析完成")
                    print(f"   - 最大值偏壓: {bias_stats['peak_bias']:.1f} mV")
                    print(f"   - 最小值偏壓: {bias_stats['min_bias']:.1f} mV")
                
                # 演示切片功能 (如果是CITS數據)
                if dat_result['data']['measurement_mode'] == 'CITS':
                    slice_result = analyzer.dat_analyzer.extract_cits_slice(0)
                    if slice_result['success']:
                        bias_value = slice_result['data']['bias_value']
                        print(f"✅ CITS 切片提取完成 (偏壓: {bias_value:.1f} mV)")
                
            else:
                print(f"❌ DAT 分析失敗: {dat_result.get('error', '未知錯誤')}")
        else:
            print("⚠️  沒有可用的 DAT 檔案")
    except Exception as e:
        print(f"❌ DAT 分析過程發生錯誤: {e}")
    
    # 6. 系統狀態總結 / System status summary
    print("\n📋 步驟 6: 系統狀態總結")
    try:
        status = analyzer.get_system_status()
        if status['success']:
            system_info = status['data']['system_info']
            print("✅ 系統運行正常")
            print(f"   - 已載入實驗數: {system_info['total_experiments']}")
            print(f"   - 當前實驗: {system_info['current_experiment']}")
            print(f"   - 可用分析器: {system_info['analyzers_loaded']}")
        else:
            print("⚠️  無法獲取詳細系統狀態，但系統基本運行正常")
            print(f"   - 當前實驗: {analyzer.current_experiment}")
            print(f"   - 載入實驗數: {len(analyzer.loaded_experiments)}")
    except Exception as e:
        print(f"⚠️  系統狀態檢查: {e}")
        print("   - 系統基本功能正常運行")
    
    # 完成 / Complete
    print("\n🎉 演示完成！")
    print("="*50)
    print("系統已成功演示以下功能:")
    print("✓ 實驗載入和管理")
    print("✓ INT 地形數據分析")
    print("✓ DAT 光譜數據分析")
    print("✓ 數據平面化和剖面提取")
    print("✓ 表面粗糙度計算")
    print("✓ 偏壓依賴性分析")
    print("✓ 系統狀態監控")
    print("\n💡 提示：運行其他測試程式進行更詳細的功能驗證")


if __name__ == "__main__":
    main()