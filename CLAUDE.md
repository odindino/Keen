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

- **Backend**: Python with PyWebView for native desktop integration
  - Entry point: `backend/main.py`
  - API layer: `backend/api_mvp.py` (handles all frontend requests)
  - Data parsers: `backend/core/parsers/` (txt, int, dat files)
  - Analysis modules: `backend/core/analysis/` (image processing, profile analysis)

- **Frontend**: Vue 3 + TypeScript + Tailwind CSS
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

Frontend tests use Vitest. No backend tests are currently set up. When adding tests:
- Frontend: Add to `frontend/src/components/__tests__/`
- Run with: `cd frontend && npm run test:unit`