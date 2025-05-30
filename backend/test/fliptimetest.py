import numpy as np
import time
from typing import Dict

def flip_y_method1(measurement_data: np.ndarray, grid_x: int, grid_y: int) -> np.ndarray:
    """使用 array_split 方法翻轉 Y 軸"""
    return np.concatenate(
        np.array_split(measurement_data, grid_y, axis=1)[::-1], axis=1
    )

def flip_y_method2(measurement_data: np.ndarray, grid_x: int, grid_y: int) -> np.ndarray:
    """使用索引映射方法翻轉 Y 軸"""
    flip_indices = np.concatenate([
        np.arange(i*grid_x, (i+1)*grid_x) 
        for i in range(grid_y-1, -1, -1)
    ])
    return measurement_data[:, flip_indices]

def flip_y_method3(measurement_data: np.ndarray, grid_x: int, grid_y: int) -> np.ndarray:
    """使用 reshape 和 flip 方法翻轉 Y 軸"""
    return measurement_data.reshape(-1, grid_y, grid_x)[:, ::-1, :].reshape(-1, grid_x * grid_y)

def flip_y_method4(measurement_data: np.ndarray, grid_x: int, grid_y: int) -> np.ndarray:
    """使用預計算索引的向量化方法翻轉 Y 軸"""
    # 預計算索引 - 使用向量化操作
    flip_indices = np.arange(grid_y-1, -1, -1)[:, np.newaxis] * grid_x + np.arange(grid_x)
    flip_indices = flip_indices.ravel()
    return measurement_data[:, flip_indices]

def flip_y_method5(measurement_data: np.ndarray, grid_x: int, grid_y: int) -> np.ndarray:
    """使用 take 方法翻轉 Y 軸"""
    flip_indices = np.empty(grid_x * grid_y, dtype=np.int32)
    for i in range(grid_y):
        flip_indices[i*grid_x:(i+1)*grid_x] = np.arange((grid_y-1-i)*grid_x, (grid_y-i)*grid_x)
    return np.take(measurement_data, flip_indices, axis=1)

def benchmark_flip_methods(grid_x: int = 100, grid_y: int = 100, n_bias: int = 401, 
                          n_iterations: int = 100) -> Dict[str, Dict[str, float]]:
    """
    測試所有翻轉方法的效能
    
    Args:
        grid_x: X 軸網格大小
        grid_y: Y 軸網格大小
        n_bias: 偏壓數量
        n_iterations: 測試迭代次數
        
    Returns:
        包含測試結果的字典
    """
    # 生成測試數據
    measurement_data = np.random.rand(n_bias, grid_x * grid_y)
    
    # 定義所有方法
    methods = {
        "method1_array_split": flip_y_method1,
        "method2_index_mapping": flip_y_method2,
        "method3_reshape_flip": flip_y_method3,
        "method4_vectorized_index": flip_y_method4,
        "method5_take": flip_y_method5
    }
    
    results = {}
    times = {}
    
    # 測試每個方法
    for method_name, method_func in methods.items():
        method_times = []
        for _ in range(n_iterations):
            start_time = time.time()
            result = method_func(measurement_data, grid_x, grid_y)
            method_times.append(time.time() - start_time)
        
        times[method_name] = method_times
        results[method_name] = {
            "mean_time": np.mean(method_times),
            "std_time": np.std(method_times),
            "min_time": np.min(method_times),
            "max_time": np.max(method_times),
            "total_time": np.sum(method_times)
        }
    
    # 驗證所有結果一致性
    base_result = flip_y_method1(measurement_data, grid_x, grid_y)
    all_equal = True
    for method_name, method_func in methods.items():
        if method_name != "method1_array_split":
            test_result = method_func(measurement_data, grid_x, grid_y)
            if not np.array_equal(base_result, test_result):
                all_equal = False
                print(f"警告: {method_name} 的結果與基準方法不一致!")
    
    results["results_equal"] = all_equal
    
    # 找出最快的方法
    fastest_method = min(results.keys() - {"results_equal"}, 
                        key=lambda x: results[x]["mean_time"])
    results["fastest_method"] = fastest_method
    
    return results

def print_benchmark_results(results: Dict[str, Dict[str, float]], n_iterations: int):
    """打印測試結果"""
    print(f"\n=== 翻轉方法效能測試結果 ({n_iterations} 次迭代) ===\n")
    
    method_names = {
        "method1_array_split": "方法1 (array_split)",
        "method2_index_mapping": "方法2 (index_mapping)",
        "method3_reshape_flip": "方法3 (reshape_flip)",
        "method4_vectorized_index": "方法4 (vectorized_index)",
        "method5_take": "方法5 (take)"
    }
    
    # 按照平均時間排序
    sorted_methods = sorted(
        [k for k in results.keys() if k not in ["results_equal", "fastest_method"]], 
        key=lambda x: results[x]["mean_time"]
    )
    
    for idx, method_key in enumerate(sorted_methods):
        method_data = results[method_key]
        print(f"\n{idx+1}. {method_names.get(method_key, method_key)}:")
        print(f"  平均時間: {method_data['mean_time']*1000:.4f} ms")
        print(f"  標準差: {method_data['std_time']*1000:.4f} ms")
        print(f"  最快: {method_data['min_time']*1000:.4f} ms")
        print(f"  最慢: {method_data['max_time']*1000:.4f} ms")
    
    print(f"\n結果一致性: {'✓ 通過' if results['results_equal'] else '✗ 失敗'}")
    
    # 計算加速比
    base_time = results["method1_array_split"]["mean_time"]
    fastest_time = results[results["fastest_method"]]["mean_time"]
    speedup = base_time / fastest_time
    
    print(f"\n💡 最快方法: {method_names.get(results['fastest_method'], results['fastest_method'])}")
    print(f"   相對於方法1的加速比: {speedup:.2f}x")

if __name__ == "__main__":
    # 預設測試參數
    grid_x, grid_y = 100, 100
    n_bias = 401
    n_iterations = 500
    
    print(f"測試參數: grid_x={grid_x}, grid_y={grid_y}, n_bias={n_bias}")
    
    # 執行測試
    results = benchmark_flip_methods(grid_x, grid_y, n_bias, n_iterations)
    print_benchmark_results(results, n_iterations)
    
    # 測試不同大小的數據
    print("\n\n=== 不同數據大小的測試 ===")
    test_sizes = [
        (50, 50, 20),
        (100, 100, 50),
        (200, 200, 100),
        (100, 100, 401),
        (500, 500, 200),
        
    ]
    
    for gx, gy, nb in test_sizes:
        print(f"\n網格大小: {gx}x{gy}, 偏壓數: {nb}")
        results = benchmark_flip_methods(gx, gy, nb, 50)  # 較少迭代次數
        
        # 顯示所有方法的時間，按速度排序
        sorted_methods = sorted(
            [k for k in results.keys() if k not in ["results_equal", "fastest_method"]], 
            key=lambda x: results[x]["mean_time"]
        )
        
        for method in sorted_methods[:3]:  # 顯示前3快的方法
            time_ms = results[method]["mean_time"] * 1000
            method_name = {
                "method1_array_split": "方法1",
                "method2_index_mapping": "方法2", 
                "method3_reshape_flip": "方法3",
                "method4_vectorized_index": "方法4",
                "method5_take": "方法5"
            }.get(method, method)
            print(f"  {method_name}: {time_ms:.4f} ms")
        
        # 顯示最快方法的加速比
        base_time = results["method1_array_split"]["mean_time"]
        fastest_time = results[results["fastest_method"]]["mean_time"]
        print(f"  最快方法加速比: {base_time/fastest_time:.2f}x")