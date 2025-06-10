#!/usr/bin/env python3
"""
完整的簡化 API 演示
Complete simplified API demonstration
"""

import sys
import os
# 從 backend/test/api_tests/ 目錄向上導航到 keen/ 根目錄
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from backend.core.experiment_session import ExperimentSession

def main():
    """演示完整的簡化 API 使用流程"""
    
    print("🚀 KEEN 簡化 API 完整演示")
    print("=" * 60)
    
    try:
        # 步驟 1: 使用簡化 API 初始化會話
        print("\n📂 步驟 1: 初始化實驗會話")
        session = ExperimentSession(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'testfile', '20250521_Janus Stacking SiO2_13K_113.txt'))
        print(f"✅ 會話建立成功: {session.experiment_name}")
        
        # 步驟 2: 使用簡化 API 直接訪問文件
        print("\n🎯 步驟 2: 使用簡化 API 直接訪問文件")
        
        # 拓撲文件
        print("\n📊 拓撲文件:")
        topofwd = session['TopoFwd']
        topobwd = session['TopoBwd']
        print(f"  topofwd = session['TopoFwd']")
        print(f"    → 文件: {topofwd._file_key}")
        print(f"    → 類型: {topofwd.file_type}")
        print(f"    → 數據形狀: {topofwd.data.image.shape}")
        
        print(f"  topobwd = session['TopoBwd']")
        print(f"    → 文件: {topobwd._file_key}")
        print(f"    → 類型: {topobwd.file_type}")
        print(f"    → 數據形狀: {topobwd.data.image.shape}")
        
        # CITS 文件
        print("\n🔬 CITS 文件:")
        itcits = session['It_to_PC_Matrix']
        print(f"  itcits = session['It_to_PC_Matrix']")
        print(f"    → 文件: {itcits._file_key}")
        print(f"    → 類型: {itcits.file_type}")
        print(f"    → 數據形狀: {itcits.data.shape}")
        print(f"    → 偏壓範圍: {itcits.data.bias_range[0]:.3f}V ~ {itcits.data.bias_range[1]:.3f}V")
        print(f"    → 偏壓點數: {itcits.data.n_bias_points}")
        
        # 其他可用的 CITS 文件
        print("\n🧪 其他可用的 CITS 文件:")
        try:
            lia1r = session['Lia1R_Matrix']
            print(f"  lia1r = session['Lia1R_Matrix']")
            print(f"    → 文件: {lia1r._file_key}")
            print(f"    → 數據形狀: {lia1r.data.shape}")
        except KeyError:
            print(f"  ❌ 'Lia1R_Matrix' 不可用")
        
        # 步驟 3: 大小寫不敏感測試
        print("\n🔤 步驟 3: 大小寫不敏感測試")
        topofwd_lower = session['topofwd']
        topobwd_upper = session['TOPOBWD']
        itcits_mixed = session['it_to_pc_matrix']
        
        print(f"  session['topofwd'] → {topofwd_lower._file_key}")
        print(f"  session['TOPOBWD'] → {topobwd_upper._file_key}")
        print(f"  session['it_to_pc_matrix'] → {itcits_mixed._file_key}")
        
        # 步驟 4: 與舊 API 的對比
        print("\n📈 步驟 4: 新舊 API 對比")
        print("  舊方式 (複雜):")
        print("    int_files = session.get_int_files()")
        print("    topofwd_file = None")
        print("    for file_key in int_files:")
        print("        if 'TopoFwd' in file_key:")
        print("            topofwd_file = session[file_key]")
        print("            break")
        print("")
        print("  新方式 (簡化):")
        print("    topofwd = session['TopoFwd']  # 一行搞定！")
        
        # 步驟 5: 快速數據訪問示例
        print("\n⚡ 步驟 5: 快速數據訪問示例")
        
        # 訪問拓撲圖像數據
        topo_image = session['TopoFwd'].data.image
        print(f"  拓撲圖像大小: {topo_image.shape}")
        print(f"  拓撲圖像範圍: {session['TopoFwd'].data.x_range:.1f} × {session['TopoFwd'].data.y_range:.1f} nm")
        
        # 訪問 CITS 3D 數據
        cits_3d = session['It_to_PC_Matrix'].data.data_3d
        print(f"  CITS 3D 數據大小: {cits_3d.shape}")
        print(f"  CITS 偏壓值數量: {len(session['It_to_PC_Matrix'].data.bias_values)}")
        
        # 步驟 6: 總結
        print("\n🎉 步驟 6: 總結")
        print("✅ 簡化 API 的優勢:")
        print("  1. 直觀易懂：session['TopoFwd'] vs 複雜的文件查找")
        print("  2. 大小寫不敏感：'TopoFwd' 和 'topofwd' 都可以")
        print("  3. 統一接口：INT、CITS、STS 文件都使用相同方式訪問")
        print("  4. 減少代碼：從多行查找變成一行直接訪問")
        print("  5. 智能映射：自動將簡短名稱映射到完整文件路徑")
        
        print("\n💡 常用的簡化 API 示例:")
        print("  # 拓撲數據")
        print("  topofwd = session['TopoFwd']")
        print("  topobwd = session['TopoBwd']")
        print("  # CITS 光譜數據")
        print("  itcits = session['It_to_PC_Matrix']")
        print("  lia1r_cits = session['Lia1R_Matrix']")
        print("  # 不區分大小寫")
        print("  topo = session['topofwd']  # 等同於 session['TopoFwd']")
        
        return True
        
    except Exception as e:
        print(f"❌ 演示失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    print(f"\n🎯 演示結果: {'成功' if success else '失敗'}")
    if success:
        print("\n🚀 恭喜！您現在可以使用簡化的 API 來訪問 SPM 數據了！")
        print("   不再需要複雜的 get_*_files() 方法調用。")
