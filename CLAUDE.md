# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Frontend (Vue 3 + TypeScript)
```bash
cd frontend
npm install          # Install dependencies
npm run dev          # Start development server (http://localhost:5173)
npm run build        # Build for production
npm run type-check   # Run TypeScript type checking
npm run test:unit    # Run unit tests with Vitest
npm run format       # Format code with Prettier
```

### Backend (Python)
```bash
cd backend
pip install -r requirements.txt  # Install dependencies
python main.py                   # Run the desktop application
```

## Architecture Overview

This is a desktop SPM (Scanning Probe Microscopy) data analysis application with:

### Backend Architecture (V2 - Current)
Python with PyWebView for native desktop integration

**Entry Points:**
- Desktop app: `backend/main.py`
- API layer: `backend/api_mvp.py` (handles all frontend requests)

**Core Architecture (Type Manager + File Proxy Pattern):**
- `backend/core/experiment_session.py` - Main entry point, manages entire experiment
- `backend/core/type_managers.py` - Type-specific managers (TxtManager, TopoManager, CitsManager, StsManager)
- `backend/core/file_proxy.py` - Lazy-loading file access with IDE-friendly interface
- `backend/core/data_models.py` - Standardized data models with type hints

**Data Processing:**
- Parsers: `backend/core/parsers/` (txt_parser, int_parser, dat_parser)
- Analyzers: `backend/core/analyzers/` (base_analyzer, int_analyzer, cits_analyzer, etc.)
- Analysis: `backend/core/analysis/` (int_analysis, cits_analysis, profile_analysis)
- Visualization: `backend/core/visualization/` (spm_plots, spectroscopy_plots)

**Usage Example:**
```python
from backend.core.experiment_session import ExperimentSession

# Load experiment
session = ExperimentSession('path/to/experiment.txt')

# Access files intuitively
topo = session['TopoFwd']  # or session.get_file('TopoFwd')
height_data = topo.data.image
analyzer = topo.analyzer

# Apply processing
result = analyzer.apply_flattening('linewise_mean')
profile = analyzer.extract_line_profile((0,0), (100,100))
```

### Frontend Architecture
Vue 3 + TypeScript + Tailwind CSS
- Entry point: `frontend/src/main.ts`
- Main app: `frontend/src/App-mvp.vue`
- Components: `frontend/src/components/mvp/` (ControlPanel, TopoViewer, ProfileChart, CitsBiasSlider)
- State management: `frontend/src/stores/mvpStore.ts` (reactive store)
- API service: `frontend/src/services/apiService.ts`

### Communication Flow
Frontend ↔ Backend communication uses PyWebView's JavaScript bridge:
1. Vue component → `apiService.ts` → `window.pywebview.api.method()`
2. Python processes request in `api_mvp.py`
3. Returns data (often Plotly configurations) → Updates Vue store → Re-render

### Data Types
- `.txt` files: SPM experiment parameters and metadata
- `.int` files: Binary topography/height map data
- `.dat` files: Electrical measurements (CITS/STS data)

## Key Implementation Notes

1. **Plotly Visualization**: Backend generates complete Plotly configurations. Frontend simply renders them.

2. **File Loading**: Always starts with a .txt file, which references associated .int/.dat files.

3. **State Management**: Uses Vue 3's reactive API. Current data state is managed in `mvpStore.ts`.

4. **Error Handling**: API calls should handle errors gracefully. Check `apiService.ts` for patterns.

5. **Image Processing**: Flattening and tilt correction algorithms are in `backend/core/analysis/int_analysis.py`.

6. **Profile Analysis**: Height profile extraction and statistics in `backend/core/analysis/profile_analysis.py`.

7. **CITS Data**: 3D data (x, y, bias) handled specially. See `CitsBiasSlider.vue` and related backend methods.

## Testing Approach

### Frontend Testing
Frontend tests use Vitest:
- Location: `frontend/src/components/__tests__/`
- Run: `cd frontend && npm run test:unit`

### Backend Testing
Multiple testing approaches available:

**Unit Tests:**
- Location: `backend/test/unit/`
- Example: `test_analyzers_comprehensive.py`

**Interactive Notebooks:**
- Location: `backend/test/notebooks/`
- `int_analysis_simple.ipynb` - Simple INT file analysis without widgets
- `interactive_analysis_demo.ipynb` - Full widget-based interactive testing
- `new_architecture_demo_v2.ipynb` - V2 architecture demonstration

**Quick Tests:**
- Location: `backend/test/quick/`
- `test_basic_functionality.py` - Basic functionality tests

**Demo Scripts:**
- Location: `backend/test/demo/`
- `spm_system_demo.py` - Complete SPM system demonstration

## Current Development Status (June 2024)

### Recently Completed
1. **Backend Architecture V2** - Complete overhaul using Type Manager + File Proxy pattern
   - Improved IDE support with full type hints
   - Lazy loading and smart caching
   - Unified error handling with ParseResult
   - Intuitive file access: `session['filename'].data.attribute`

2. **File Organization** - Restructured backend and test folders for better organization
   - Created proper directory structure with docs/, diagrams/, notebooks/, etc.
   - Updated all import paths and documentation

3. **Interactive Testing Tools** - Created multiple Jupyter notebooks for testing
   - Widget-based and widget-free versions
   - Full Plotly integration for visualization
   - Support for all flattening methods and profile extraction

### Known Issues & Solutions
1. **Jupyter Widget Loading**: Some environments have issues with ipywidgets
   - Solution: Use `int_analysis_simple.ipynb` which doesn't require widgets
   
2. **Image Orientation**: SPM images were displaying upside-down
   - Solution: Applied `np.flipud()` at the data parsing level
   
3. **CITS Display**: Coordinate system consistency issues
   - Solution: Integrated `prepare_cits_for_display()` in dat_parser

### TODO Items (from todo list)
- Test integration with existing API (`api_mvp.py`)
- Update `api_mvp.py` to use new V2 architecture
- Create comprehensive unit tests
- Update documentation and usage guides

## Important Notes for Development

1. **File Loading Sequence**: Always load txt file first, then access associated files
2. **Coordinate System**: SPM images use (0,0) at bottom-left corner
3. **Type Hints**: New architecture provides full IDE support - use it!
4. **Memory Management**: ExperimentSession handles caching automatically
5. **Error Handling**: All operations return ParseResult with success/error info