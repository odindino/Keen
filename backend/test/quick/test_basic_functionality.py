"""
快速基本功能測試
Quick Basic Functionality Test

簡單快速測試系統核心功能是否正常
Simple and fast test for core system functionality
"""

import os
import sys
import traceback
import numpy as np
from pathlib import Path

# 添加路徑以便導入模組
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir.parent.parent))

from core.main_analyzer import MainAnalyzer
from core.parsers.txt_parser import TxtParser
from core.parsers.int_parser import IntParser
from core.parsers.dat_parser import DatParser


class QuickTester:
    """
    快速測試器
    Quick tester for basic functionality
    """
    
    def __init__(self, test_data_dir: str):
        self.test_data_dir = Path(test_data_dir)
        self.main_analyzer = MainAnalyzer()
        self.test_results = {}
        
    def run_all_tests(self):
        """
        運行所有快速測試
        Run all quick tests
        """
        print("🚀 開始快速測試 / Starting Quick Tests")
        print("="*50)
        
        tests = [
            ('txt_analyzer', self.test_txt_analyzer),
            ('int_analyzer', self.test_int_analyzer), 
            ('dat_analyzer', self.test_dat_analyzer),
            ('main_workflow', self.test_main_workflow)
        ]
        
        for test_name, test_func in tests:
            try:
                print(f"\n📋 {test_name.upper()}...")
                result = test_func()
                if result:
                    print(f"✅ {test_name}: 通過")
                    self.test_results[test_name] = '成功'
                else:
                    print(f"❌ {test_name}: 失敗")
                    self.test_results[test_name] = '失敗'
            except Exception as e:
                print(f"❌ {test_name}: 異常 - {str(e)}")
                self.test_results[test_name] = '異常'
        
        self.print_summary()
    
    def test_txt_analyzer(self):
        """測試 TXT 分析器"""
        txt_files = list(self.test_data_dir.glob("*.txt"))
        if not txt_files:
            return False
            
        txt_file = txt_files[0]
        txt_parser = TxtParser(str(txt_file))
        txt_data = txt_parser.parse()
        
        result = self.main_analyzer.txt_analyzer.analyze(txt_data, file_path=str(txt_file))
        return result['success']
    
    def test_int_analyzer(self):
        """測試 INT 分析器"""
        txt_files = list(self.test_data_dir.glob("*.txt"))
        if not txt_files:
            return False
            
        txt_file = txt_files[0]
        txt_parser = TxtParser(str(txt_file))
        txt_data = txt_parser.parse()
        
        exp_info = txt_data.get('experiment_info', {})
        x_pixel = int(exp_info.get('xPixel', 256))
        y_pixel = int(exp_info.get('yPixel', 256))
        x_range = float(exp_info.get('XScanRange', 100.0))
        scale = x_range / x_pixel
        
        int_files = list(self.test_data_dir.glob("*.int"))
        if not int_files:
            return False
            
        int_file = int_files[0]
        int_parser = IntParser(str(int_file), scale, x_pixel, y_pixel)
        int_data = int_parser.parse()
        
        result = self.main_analyzer.int_analyzer.analyze(int_data)
        return result['success']
    
    def test_dat_analyzer(self):
        """測試 DAT 分析器"""
        dat_files = list(self.test_data_dir.glob("*.dat"))
        if not dat_files:
            return False
            
        dat_file = dat_files[0]
        dat_parser = DatParser()
        dat_data = dat_parser.parse(str(dat_file))
        
        result = self.main_analyzer.dat_analyzer.analyze(dat_data)
        return result['success']
    
    def test_main_workflow(self):
        """測試主工作流"""
        txt_files = list(self.test_data_dir.glob("*.txt"))
        if not txt_files:
            return False
            
        txt_file = txt_files[0]
        result = self.main_analyzer.load_experiment(str(txt_file))
        return result['success']
    
    def print_summary(self):
        """打印測試摘要"""
        print("\n" + "="*50)
        print("📊 快速測試結果摘要")
        print("="*50)
        
        success_count = sum(1 for result in self.test_results.values() if result == '成功')
        total_count = len(self.test_results)
        
        for test_name, result in self.test_results.items():
            status = "✅" if result == '成功' else "❌"
            print(f"  {status} {test_name}: {result}")
        
        print(f"\n總計: {success_count}/{total_count} 個測試成功")
        
        if success_count == total_count:
            print("\n🎉 所有快速測試通過！")
        else:
            print(f"\n⚠️  有 {total_count - success_count} 個測試失敗")


def main():
    """主程式"""
    test_data_dir = Path(__file__).parent.parent.parent.parent / "testfile"
    
    if not test_data_dir.exists():
        print(f"錯誤：測試數據目錄不存在: {test_data_dir}")
        return
    
    tester = QuickTester(str(test_data_dir))
    tester.run_all_tests()


if __name__ == "__main__":
    main()