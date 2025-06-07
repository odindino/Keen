#!/usr/bin/env python3
"""
綜合分析器測試程式
Comprehensive Analyzer Test Program

測試所有分析器使用 testfile 資料夾中的實際數據
Test all analyzers using actual data from testfile folder
"""

import sys
import json
import logging
from pathlib import Path

# 添加 backend 路徑到 Python 路徑
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

# 導入必要模組
from core.parsers.txt_parser import TxtParser
from core.parsers.int_parser import IntParser
from core.parsers.dat_parser import DatParser
from core.main_analyzer import MainAnalyzer

# 設置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ComprehensiveAnalyzerTester:
    """
    綜合分析器測試器
    Comprehensive Analyzer Tester
    
    用於系統性測試所有分析器的功能
    For systematically testing all analyzer functionalities
    """
    
    def __init__(self, testfile_dir: str):
        """
        初始化測試器
        Initialize tester
        
        Args:
            testfile_dir: 測試文件目錄 / Test file directory
        """
        self.testfile_dir = Path(testfile_dir)
        self.main_analyzer = MainAnalyzer()
        
        # 測試結果 / Test results
        self.test_results = {
            'txt_tests': [],
            'int_tests': [],
            'dat_tests': [],
            'integration_tests': [],
            'summary': {}
        }
    
    def discover_test_files(self):
        """
        發現測試文件
        Discover test files
        
        Returns:
            Dict: 文件分類結果 / File classification results
        """
        logger.info(f"搜索測試文件於: {self.testfile_dir}")
        
        files = {
            'txt_files': [],
            'int_files': [],
            'dat_files': [],
            'other_files': []
        }
        
        for file_path in self.testfile_dir.iterdir():
            if file_path.is_file():
                suffix = file_path.suffix.lower()
                if suffix == '.txt':
                    files['txt_files'].append(file_path)
                elif suffix == '.int':
                    files['int_files'].append(file_path)
                elif suffix == '.dat':
                    files['dat_files'].append(file_path)
                else:
                    files['other_files'].append(file_path)
        
        logger.info(f"發現文件: TXT={len(files['txt_files'])}, INT={len(files['int_files'])}, DAT={len(files['dat_files'])}")
        return files
    
    def test_txt_analyzer(self, txt_files: list):
        """
        測試 TXT 分析器
        Test TXT analyzer
        
        Args:
            txt_files: TXT 文件列表 / List of TXT files
        """
        logger.info("=== 測試 TXT 分析器 ===")
        
        for txt_file in txt_files:
            test_result = {
                'file': str(txt_file),
                'parser_success': False,
                'analyzer_success': False,
                'errors': [],
                'data_summary': {}
            }
            
            try:
                logger.info(f"測試文件: {txt_file.name}")
                
                # 1. 測試解析器 / Test parser
                parser = TxtParser(str(txt_file))
                parsed_data = parser.parse()
                test_result['parser_success'] = True
                
                # 2. 測試分析器 / Test analyzer
                analyzer_result = self.main_analyzer.txt_analyzer.analyze(parsed_data, file_path=str(txt_file))
                test_result['analyzer_success'] = analyzer_result['success']
                
                if analyzer_result['success']:
                    # 保存數據摘要 / Save data summary
                    test_result['data_summary'] = {
                        'experiment_type': analyzer_result['data'].get('experiment_type', {}),
                        'file_counts': analyzer_result['data'].get('summary', {}).get('file_counts', {}),
                        'availability': analyzer_result['data'].get('availability_analysis', {}).get('all_files_available', False)
                    }
                    logger.info(f"✅ TXT 分析成功: {txt_file.name}")
                else:
                    test_result['errors'].append(analyzer_result.get('error', 'Unknown error'))
                    logger.error(f"❌ TXT 分析失敗: {txt_file.name}")
                
            except Exception as e:
                test_result['errors'].append(str(e))
                logger.error(f"❌ TXT 測試異常: {txt_file.name} - {str(e)}")
            
            self.test_results['txt_tests'].append(test_result)
    
    def test_int_analyzer(self, txt_files: list):
        """
        測試 INT 分析器
        Test INT analyzer
        
        Args:
            txt_files: TXT 文件列表，用於獲取 INT 文件信息 / TXT files for getting INT file info
        """
        logger.info("=== 測試 INT 分析器 ===")
        
        for txt_file in txt_files:
            try:
                # 首先解析 TXT 文件獲取 INT 文件信息 / Parse TXT file to get INT file info
                parser = TxtParser(str(txt_file))
                txt_data = parser.parse()
                
                for int_file_info in txt_data.get('int_files', []):
                    int_filename = int_file_info['filename']
                    int_file_path = txt_file.parent / int_filename
                    
                    test_result = {
                        'file': str(int_file_path),
                        'txt_source': str(txt_file),
                        'parser_success': False,
                        'analyzer_success': False,
                        'errors': [],
                        'data_summary': {}
                    }
                    
                    if not int_file_path.exists():
                        test_result['errors'].append("INT 文件不存在")
                        logger.warning(f"⚠️ INT 文件不存在: {int_filename}")
                        self.test_results['int_tests'].append(test_result)
                        continue
                    
                    try:
                        logger.info(f"測試 INT 文件: {int_filename}")
                        
                        # 獲取掃描參數 / Get scan parameters
                        experiment_info = txt_data.get('experiment_info', {})
                        x_pixel = int(experiment_info.get('xPixel', 256))
                        y_pixel = int(experiment_info.get('yPixel', 256))
                        x_range = float(experiment_info.get('XScanRange', 100.0))
                        scale = x_range / x_pixel
                        
                        int_parser = IntParser(str(int_file_path), scale, x_pixel, y_pixel)
                        int_data = int_parser.parse()
                        test_result['parser_success'] = True
                        
                        # 測試分析器 / Test analyzer
                        analyzer_result = self.main_analyzer.int_analyzer.analyze(int_data)
                        test_result['analyzer_success'] = analyzer_result['success']
                        
                        if analyzer_result['success']:
                            # 測試額外功能 / Test additional features
                            self._test_int_features(test_result)
                            
                            # 保存數據摘要 / Save data summary
                            test_result['data_summary'] = {
                                'shape': analyzer_result['data']['topo_info']['shape'],
                                'data_range': analyzer_result['data']['topo_info']['data_range'],
                                'stats': analyzer_result['data']['stats'],
                                'has_plots': bool(analyzer_result.get('plots', {}))
                            }
                            logger.info(f"✅ INT 分析成功: {int_filename}")
                        else:
                            test_result['errors'].append(analyzer_result.get('error', 'Unknown error'))
                            logger.error(f"❌ INT 分析失敗: {int_filename}")
                        
                    except Exception as e:
                        test_result['errors'].append(str(e))
                        logger.error(f"❌ INT 測試異常: {int_filename} - {str(e)}")
                    
                    self.test_results['int_tests'].append(test_result)
                    
            except Exception as e:
                logger.error(f"❌ INT 測試整體異常: {txt_file.name} - {str(e)}")
    
    def test_dat_analyzer(self, txt_files: list):
        """
        測試 DAT 分析器
        Test DAT analyzer
        
        Args:
            txt_files: TXT 文件列表，用於獲取 DAT 文件信息 / TXT files for getting DAT file info
        """
        logger.info("=== 測試 DAT 分析器 ===")
        
        for txt_file in txt_files:
            try:
                # 首先解析 TXT 文件獲取 DAT 文件信息 / Parse TXT file to get DAT file info
                parser = TxtParser(str(txt_file))
                txt_data = parser.parse()
                
                for dat_file_info in txt_data.get('dat_files', []):
                    dat_filename = dat_file_info['filename']
                    dat_file_path = txt_file.parent / dat_filename
                    
                    test_result = {
                        'file': str(dat_file_path),
                        'txt_source': str(txt_file),
                        'parser_success': False,
                        'analyzer_success': False,
                        'errors': [],
                        'data_summary': {}
                    }
                    
                    if not dat_file_path.exists():
                        test_result['errors'].append("DAT 文件不存在")
                        logger.warning(f"⚠️ DAT 文件不存在: {dat_filename}")
                        self.test_results['dat_tests'].append(test_result)
                        continue
                    
                    try:
                        logger.info(f"測試 DAT 文件: {dat_filename}")
                        
                        # 1. 測試解析器 / Test parser
                        dat_parser = DatParser()
                        parsed_data = dat_parser.parse(str(dat_file_path), dat_file_info)
                        test_result['parser_success'] = True
                        
                        # 2. 測試分析器 / Test analyzer
                        analyzer_result = self.main_analyzer.dat_analyzer.analyze(parsed_data)
                        test_result['analyzer_success'] = analyzer_result['success']
                        
                        if analyzer_result['success']:
                            # 測試額外功能 / Test additional features
                            self._test_dat_features(test_result, parsed_data)
                            
                            # 保存數據摘要 / Save data summary
                            test_result['data_summary'] = {
                                'measurement_mode': analyzer_result['data']['measurement_mode'],
                                'data_info': analyzer_result['data']['data_info'],
                                'has_plots': bool(analyzer_result.get('plots', {}))
                            }
                            logger.info(f"✅ DAT 分析成功: {dat_filename}")
                        else:
                            test_result['errors'].append(analyzer_result.get('error', 'Unknown error'))
                            logger.error(f"❌ DAT 分析失敗: {dat_filename}")
                        
                    except Exception as e:
                        test_result['errors'].append(str(e))
                        logger.error(f"❌ DAT 測試異常: {dat_filename} - {str(e)}")
                    
                    self.test_results['dat_tests'].append(test_result)
                    
            except Exception as e:
                logger.error(f"❌ DAT 測試整體異常: {txt_file.name} - {str(e)}")
    
    def _test_int_features(self, test_result: dict):
        """
        測試 INT 分析器的額外功能
        Test additional features of INT analyzer
        """
        try:
            # 測試平面化 / Test flattening
            flatten_result = self.main_analyzer.int_analyzer.apply_flattening('linewise_mean')
            if flatten_result['success']:
                test_result['data_summary']['flattening_success'] = True
            
            # 測試線段剖面 / Test line profile
            profile_result = self.main_analyzer.int_analyzer.extract_line_profile((10, 10), (50, 50))
            if profile_result['success']:
                test_result['data_summary']['line_profile_success'] = True
                
        except Exception as e:
            test_result['errors'].append(f"額外功能測試失敗: {str(e)}")
    
    def _test_dat_features(self, test_result: dict, parsed_data: dict):
        """
        測試 DAT 分析器的額外功能
        Test additional features of DAT analyzer
        """
        try:
            measurement_mode = parsed_data.get('measurement_mode', '')
            
            if measurement_mode == 'CITS':
                # 測試 CITS 切片 / Test CITS slice
                slice_result = self.main_analyzer.dat_analyzer.extract_cits_slice(0)
                if slice_result['success']:
                    test_result['data_summary']['cits_slice_success'] = True
            
            # 測試偏壓依賴性分析 / Test bias dependence analysis
            bias_result = self.main_analyzer.dat_analyzer.analyze_bias_dependence()
            if bias_result['success']:
                test_result['data_summary']['bias_analysis_success'] = True
                
        except Exception as e:
            test_result['errors'].append(f"DAT 額外功能測試失敗: {str(e)}")
    
    def run_integration_tests(self, txt_files: list):
        """
        運行整合測試
        Run integration tests
        
        Args:
            txt_files: TXT 文件列表 / List of TXT files
        """
        logger.info("=== 運行整合測試 ===")
        
        for txt_file in txt_files:
            test_result = {
                'experiment': str(txt_file),
                'full_workflow_success': False,
                'steps_completed': [],
                'errors': []
            }
            
            try:
                logger.info(f"整合測試: {txt_file.name}")
                
                # 使用主分析器載入實驗 / Use main analyzer to load experiment
                load_result = self.main_analyzer.load_experiment(str(txt_file))
                if load_result['success']:
                    test_result['steps_completed'].append('experiment_loading')
                    test_result['full_workflow_success'] = True
                    test_result['processed_files'] = {
                        'int': load_result['data']['int_files_count'],
                        'dat': load_result['data']['dat_files_count']
                    }
                    logger.info(f"✅ 整合測試成功: {txt_file.name}")
                else:
                    test_result['errors'].append(load_result.get('error', 'Unknown error'))
                    logger.warning(f"⚠️ 整合測試失敗: {txt_file.name}")
                
            except Exception as e:
                test_result['errors'].append(f"整合測試異常: {str(e)}")
                logger.error(f"❌ 整合測試失敗: {txt_file.name} - {str(e)}")
            
            self.test_results['integration_tests'].append(test_result)
    
    def generate_test_summary(self):
        """
        生成測試摘要
        Generate test summary
        """
        logger.info("=== 生成測試摘要 ===")
        
        summary = {
            'txt_analyzer': {
                'total_tests': len(self.test_results['txt_tests']),
                'successful': sum(1 for t in self.test_results['txt_tests'] if t['analyzer_success']),
                'failed': sum(1 for t in self.test_results['txt_tests'] if not t['analyzer_success'])
            },
            'int_analyzer': {
                'total_tests': len(self.test_results['int_tests']),
                'successful': sum(1 for t in self.test_results['int_tests'] if t['analyzer_success']),
                'failed': sum(1 for t in self.test_results['int_tests'] if not t['analyzer_success'])
            },
            'dat_analyzer': {
                'total_tests': len(self.test_results['dat_tests']),
                'successful': sum(1 for t in self.test_results['dat_tests'] if t['analyzer_success']),
                'failed': sum(1 for t in self.test_results['dat_tests'] if not t['analyzer_success'])
            },
            'integration_tests': {
                'total_tests': len(self.test_results['integration_tests']),
                'successful': sum(1 for t in self.test_results['integration_tests'] if t['full_workflow_success']),
                'failed': sum(1 for t in self.test_results['integration_tests'] if not t['full_workflow_success'])
            }
        }
        
        self.test_results['summary'] = summary
        
        # 打印摘要 / Print summary
        print("\n" + "="*60)
        print("測試結果摘要 / Test Results Summary")
        print("="*60)
        
        for analyzer_name, stats in summary.items():
            success_rate = (stats['successful'] / stats['total_tests'] * 100) if stats['total_tests'] > 0 else 0
            print(f"{analyzer_name.replace('_', ' ').title()}:")
            print(f"  總測試數: {stats['total_tests']}")
            print(f"  成功: {stats['successful']}")
            print(f"  失敗: {stats['failed']}")
            print(f"  成功率: {success_rate:.1f}%")
            print()
        
        # 計算總體成功率 / Calculate overall success rate
        total_tests = sum(stats['total_tests'] for stats in summary.values())
        total_successful = sum(stats['successful'] for stats in summary.values())
        overall_rate = (total_successful / total_tests * 100) if total_tests > 0 else 0
        
        print(f"總體成功率: {overall_rate:.1f}% ({total_successful}/{total_tests})")
        print("="*60)
    
    def save_test_results(self, output_file: str = "comprehensive_test_results.json"):
        """
        保存測試結果到文件
        Save test results to file
        
        Args:
            output_file: 輸出文件名 / Output file name
        """
        output_path = Path(__file__).parent / output_file
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"測試結果已保存到: {output_path}")
    
    def run_all_tests(self):
        """
        運行所有測試
        Run all tests
        """
        logger.info("開始運行所有分析器測試")
        
        # 1. 發現測試文件 / Discover test files
        files = self.discover_test_files()
        
        if not files['txt_files']:
            logger.error("未找到 TXT 測試文件")
            return
        
        # 2. 運行各個分析器測試 / Run individual analyzer tests
        self.test_txt_analyzer(files['txt_files'])
        self.test_int_analyzer(files['txt_files'])
        self.test_dat_analyzer(files['txt_files'])
        
        # 3. 運行整合測試 / Run integration tests
        self.run_integration_tests(files['txt_files'])
        
        # 4. 生成摘要 / Generate summary
        self.generate_test_summary()
        
        # 5. 保存結果 / Save results
        self.save_test_results()
        
        logger.info("所有測試完成")


def main():
    """主函數 / Main function"""
    # 獲取測試文件目錄 / Get test file directory
    script_dir = Path(__file__).parent
    testfile_dir = script_dir.parent.parent.parent / "testfile"
    
    if not testfile_dir.exists():
        print(f"錯誤: 測試文件目錄不存在: {testfile_dir}")
        return
    
    # 創建並運行測試器 / Create and run tester
    tester = ComprehensiveAnalyzerTester(str(testfile_dir))
    tester.run_all_tests()


if __name__ == "__main__":
    main()