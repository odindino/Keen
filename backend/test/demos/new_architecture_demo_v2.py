#!/usr/bin/env python3
"""
新架構示範腳本 V2
New Architecture Demo Script V2

展示 KEEN 新架構的使用方式，包含 IDE 友好的介面和直覺的資料存取
Demonstrates the usage of KEEN's new architecture with IDE-friendly interface and intuitive data access
"""

import sys
from pathlib import Path

# 添加後端路徑到 Python 路徑 / Add backend path to Python path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from core.experiment_session import ExperimentSession
from core.data_models import TopoData, CitsData

def demo_new_architecture():
    """
    示範新架構的使用方式
    Demonstrate new architecture usage
    """
    print("🚀 KEEN 新架構示範 / New Architecture Demo")
    print("=" * 60)
    
    # 檢查測試檔案是否存在 / Check if test files exist
    testfile_dir = backend_path.parent / "testfile"
    txt_files = list(testfile_dir.glob("*.txt"))
    
    if not txt_files:
        print("❌ 未找到測試檔案，請確保 testfile 目錄中有 .txt 檔案")
        print("❌ No test files found, please ensure .txt files exist in testfile directory")
        return
    
    txt_file = txt_files[0]
    print(f"📁 使用測試檔案: {txt_file.name}")
    print(f"📁 Using test file: {txt_file.name}")
    
    try:
        # ========== 1. 初始化實驗會話 / Initialize Experiment Session ==========
        print("\n1️⃣  初始化實驗會話 / Initializing Experiment Session")
        print("-" * 40)
        
        session = ExperimentSession(str(txt_file))
        print(f"✅ 會話建立成功: {session.experiment_name}")
        print(f"✅ Session created successfully: {session.experiment_name}")
        
        # 顯示會話摘要 / Show session summary
        summary = session.get_session_summary()
        print(f"📊 總檔案數: {summary['files_summary']['total_available']}")
        print(f"📊 Total files: {summary['files_summary']['total_available']}")
        print(f"   - TXT: {summary['files_summary']['available']['txt']}")
        print(f"   - TOPO: {summary['files_summary']['available']['topo']}")
        print(f"   - CITS: {summary['files_summary']['available']['cits']}")
        print(f"   - STS: {summary['files_summary']['available']['sts']}")
        
        # ========== 2. 展示新的檔案存取方式 / Demonstrate New File Access ==========
        print("\n2️⃣  新的檔案存取方式 / New File Access Methods")
        print("-" * 40)
        
        # 列出可用檔案 / List available files
        available_files = session.available_files
        print("📋 可用檔案列表 / Available Files:")
        
        # 顯示拓撲檔案 / Show topography files
        if available_files['topo']:
            topo_key = available_files['topo'][0]
            print(f"🔍 以 {topo_key} 為例展示新介面")
            print(f"🔍 Using {topo_key} to demonstrate new interface")
            
            # 舊方式（不再使用）/ Old way (deprecated)
            print("\n❌ 舊方式 (已棄用):")
            print("   data = analyzer.experiment_data['loaded_files']['topofwd']['data']['image_data']")
            
            # 新方式（IDE 友好）/ New way (IDE-friendly)
            print("\n✅ 新方式 (IDE 友好):")
            print(f"   topo = session['{topo_key}']")
            print("   data = topo.data.image      # IDE 會自動提示所有屬性")
            print("   range_x = topo.data.x_range # 型別安全的存取")
            print("   analyzer = topo.analyzer    # 直接獲取分析器")
            
            # 實際示範存取 / Actual access demonstration
            try:
                topo = session[topo_key]
                print(f"\n📊 檔案資訊 / File Information:")
                print(f"   - 類型: {topo.file_type}")
                print(f"   - 已載入: {topo.is_loaded}")
                print(f"   - 檔案大小: {topo.file_info.human_readable_size if topo.file_info else 'Unknown'}")
                
                # 載入數據 / Load data
                if isinstance(topo.data, TopoData):
                    print(f"   - 圖像尺寸: {topo.data.shape}")
                    print(f"   - X 範圍: {topo.data.x_range:.2f} nm")
                    print(f"   - Y 範圍: {topo.data.y_range:.2f} nm")
                    print(f"   - X 像素尺度: {topo.data.pixel_scale_x:.4f} nm/pixel")
                    print(f"   - Y 像素尺度: {topo.data.pixel_scale_y:.4f} nm/pixel")
                    print(f"   - 數值 Scale: {topo.data.data_scale}")
                
            except Exception as e:
                print(f"⚠️  載入時發生錯誤: {str(e)}")
                print(f"⚠️  Error during loading: {str(e)}")
        
        # ========== 3. 展示 CITS 檔案存取 / Demonstrate CITS File Access ==========
        if available_files['cits']:
            print("\n3️⃣  CITS 檔案存取示範 / CITS File Access Demo")
            print("-" * 40)
            
            cits_key = available_files['cits'][0]
            print(f"🔬 CITS 檔案: {cits_key}")
            
            try:
                cits = session[cits_key]
                print(f"📊 CITS 檔案資訊:")
                print(f"   - 已載入: {cits.is_loaded}")
                
                if isinstance(cits.data, CitsData):
                    print(f"   - 3D 數據形狀: {cits.data.shape}")
                    print(f"   - 偏壓點數: {cits.data.n_bias_points}")
                    print(f"   - 偏壓範圍: {cits.data.bias_range}")
                    print(f"   - 網格大小: {cits.data.grid_size}")
                
            except Exception as e:
                print(f"⚠️  CITS 載入錯誤: {str(e)}")
        
        # ========== 4. 展示分析功能 / Demonstrate Analysis Features ==========
        print("\n4️⃣  分析功能示範 / Analysis Features Demo")
        print("-" * 40)
        
        if available_files['topo']:
            topo_key = available_files['topo'][0]
            topo = session[topo_key]
            
            print("🔧 可用的分析方法:")
            print("   - topo.flatten_plane()      # 平面平坦化")
            print("   - topo.extract_profile()    # 提取剖面線")
            print("   - topo.analyzer             # 獲取完整分析器")
            
            # 示範分析器的使用 / Demonstrate analyzer usage
            try:
                analyzer = topo.analyzer
                print(f"✅ 分析器類型: {type(analyzer).__name__}")
                print(f"✅ Analyzer type: {type(analyzer).__name__}")
                
                # 這裡可以調用分析方法（如果分析器已實作）
                # analyzer methods can be called here (if implemented)
                
            except Exception as e:
                print(f"⚠️  分析器初始化錯誤: {str(e)}")
        
        # ========== 5. 展示批次操作 / Demonstrate Batch Operations ==========
        print("\n5️⃣  批次操作示範 / Batch Operations Demo")
        print("-" * 40)
        
        # 列出所有拓撲檔案 / List all topography files
        topo_files = session.get_topo_files()
        if topo_files:
            print(f"📁 拓撲檔案列表 ({len(topo_files)} 個):")
            for i, file_key in enumerate(topo_files[:3]):  # 只顯示前3個
                file_proxy = session[file_key]
                info = file_proxy.file_info
                signal_type = info.signal_type if info else "Unknown"
                direction = info.direction if info else ""
                print(f"   {i+1}. {file_key} ({signal_type} {direction})")
        
        # 展示記憶體使用資訊 / Show memory usage information
        print("\n📊 記憶體使用資訊 / Memory Usage Information:")
        memory_info = session.get_memory_info()
        total_loaded = memory_info['total_loaded']
        total_files = memory_info['total_files']
        print(f"   已載入檔案: {total_loaded}/{total_files}")
        print(f"   Loaded files: {total_loaded}/{total_files}")
        
        # ========== 6. 展示搜尋功能 / Demonstrate Search Features ==========
        print("\n6️⃣  搜尋功能示範 / Search Features Demo")
        print("-" * 40)
        
        # 根據訊號類型搜尋 / Search by signal type
        topo_files = session.find_files_by_signal_type("Topo")
        print(f"🔍 Topo 訊號檔案: {len(topo_files)} 個")
        
        # 根據方向搜尋 / Search by direction
        fwd_files = session.find_files_by_direction("Fwd")
        bwd_files = session.find_files_by_direction("Bwd")
        print(f"🔍 正向掃描檔案: {len(fwd_files)} 個")
        print(f"🔍 反向掃描檔案: {len(bwd_files)} 個")
        
        # ========== 7. 總結 / Summary ==========
        print("\n✨ 新架構優勢總結 / New Architecture Advantages")
        print("=" * 60)
        print("✅ IDE 友好的型別提示")
        print("✅ IDE-friendly type hints")
        print("✅ 直覺的屬性存取: session['file'].data.attribute")
        print("✅ Intuitive property access: session['file'].data.attribute")
        print("✅ 完整的狀態管理和變數持久化")
        print("✅ Complete state management and variable persistence")
        print("✅ 統一的資料格式和錯誤處理")
        print("✅ Unified data format and error handling")
        print("✅ 清晰的職責分離和模組化設計")
        print("✅ Clear separation of concerns and modular design")
        
    except Exception as e:
        print(f"❌ 示範過程中發生錯誤: {str(e)}")
        print(f"❌ Error during demonstration: {str(e)}")
        import traceback
        traceback.print_exc()


def demo_comparison():
    """
    新舊架構對比示範
    Old vs New Architecture Comparison Demo
    """
    print("\n🔄 新舊架構對比 / Old vs New Architecture Comparison")
    print("=" * 60)
    
    print("📋 舊架構存取方式 / Old Architecture Access:")
    print("""
    # 複雜的字典式存取，無 IDE 支援
    analyzer = MainAnalyzer()
    result = analyzer.load_experiment('experiment.txt')
    data = analyzer.experiment_data['loaded_files']['topofwd']['data']['image_data']
    scale = analyzer.experiment_data['txt_data']['scan_parameters']['x_range']
    
    # 需要手動管理狀態
    # 容易拼寫錯誤
    # 沒有型別提示
    """)
    
    print("✨ 新架構存取方式 / New Architecture Access:")
    print("""
    # 直覺的屬性存取，完整 IDE 支援
    session = ExperimentSession('experiment.txt')
    topo = session['topofwd']           # FileProxy with full type hints
    data = topo.data.image              # TopoData.image: np.ndarray
    scale = topo.data.x_range           # TopoData.x_range: float
    
    # 自動狀態管理
    # 型別安全
    # IDE 自動完成
    # 統一錯誤處理
    """)


if __name__ == "__main__":
    demo_new_architecture()
    demo_comparison()