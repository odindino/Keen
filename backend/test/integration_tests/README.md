# Integration Tests

This directory contains integration tests for the KEEN SPM framework, specifically focusing on file parsing functionality and INT file error resolution.

## File Descriptions

### INT Parsing Error Debug Files (2025-01-07)
These files were created to diagnose and fix the critical error: `'>=' not supported between instances of 'int' and 'str'` in INT file parsing.

- **`debug_int_error.py`**: Main diagnostic script that identified the root cause in TypeManager initialization
- **`debug_scan_params.py`**: Tests scanning parameter parsing and type conversion
- **`debug_txt_parsing.py`**: Validates TXT file parsing functionality  
- **`debug_txtdata.py`**: Tests TXT data loading and parameter extraction

### Final Integration Tests
- **`final_test.py`**: Comprehensive test that validates all file types (TXT, INT, DAT/CITS) after fixes
- **`test_fixed_parsing.py`**: Focused test confirming the INT parsing error resolution

## Test Results Summary

All tests now pass successfully after fixing the ExperimentSession TypeManager initialization:

✅ **TXT File Parsing**: Working correctly
✅ **INT File Parsing**: Fixed (was the main issue)  
✅ **DAT/CITS File Parsing**: Working correctly
✅ **Simplified API Access**: Working correctly
✅ **All Convenience Methods**: Working correctly

## Key Fix Applied

The critical error was resolved by correcting the TypeManager initialization in `ExperimentSession`:

```python
# Before (incorrect)
self.txt_manager = TxtManager(self.base_path)

# After (correct)  
self.txt_manager = TxtManager(cache_size=20, session=self)
```

## Usage

To run these integration tests:

```bash
cd /Users/yangziliang/Git-Projects/keen/backend/test/integration_tests/

# Run individual tests
python debug_int_error.py
python final_test.py
python test_fixed_parsing.py

# Or run all tests
for file in *.py; do
    echo "Running $file..."
    python "$file"
    echo "---"
done
```

## Related Files

- **Core Fix**: `/backend/core/experiment_session.py` - TypeManager initialization
- **Type Safety**: `/backend/core/type_managers.py` - Enhanced string-to-number conversion
- **Documentation**: `/backend/test/notebooks/integrated_visualization_test.ipynb` - Updated to reflect fixes

---

*These tests document the successful resolution of a critical INT file parsing error that was preventing topographic data visualization in the KEEN framework.*
