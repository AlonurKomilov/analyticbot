# API Data Source Configuration Fix

## Problem Identified
The TWA frontend was showing mixed mock and real API data because individual components were not properly respecting the centralized data source configuration in the app store. Components were making direct API calls and falling back to mock data independently, bypassing the global data source setting.

## Root Cause Analysis
1. **PostViewDynamicsChart.jsx**: Made direct API calls with fallback to mock data
2. **TopPostsTable.jsx**: Used direct fetch() calls instead of store methods  
3. **BestTimeRecommender.jsx**: Had hardcoded API endpoints with mock fallbacks
4. **Missing synchronization**: No mechanism to notify components when data source changed

## Fixes Applied

### 1. Updated PostViewDynamicsChart.jsx
- ✅ Removed direct API calls
- ✅ Now uses `fetchPostDynamics()` from store which respects `dataSource` setting
- ✅ Added event listener for data source changes
- ✅ Proper data handling for both mock and API responses

### 2. Updated TopPostsTable.jsx  
- ✅ Removed hardcoded fetch() calls to localhost:8000
- ✅ Now uses `fetchTopPosts()` from store
- ✅ Added `useAppStore` import and data source awareness
- ✅ Added event listener for data source changes

### 3. Updated BestTimeRecommender.jsx
- ✅ Replaced direct API calls with `fetchBestTime()` from store
- ✅ Added proper store integration and data source respect
- ✅ Added AI insights generation function
- ✅ Added event listener for data source changes

### 4. Enhanced AnalyticsDashboard.jsx
- ✅ Added `clearAnalyticsData()` call when switching data sources
- ✅ Added custom event dispatch to notify child components
- ✅ Improved data source change handler with proper cleanup

## Technical Implementation

### Store Integration
Each analytics component now:
- Imports `useAppStore` and gets the appropriate fetch method
- Respects the global `dataSource` setting ('api' vs 'mock')
- Uses store methods that handle API failures gracefully
- Automatically falls back to mock data when API is unavailable

### Event-Driven Refresh
When data source changes:
1. `AnalyticsDashboard` clears analytics cache
2. Dispatches `dataSourceChanged` custom event  
3. All analytics components listen for this event
4. Components reload data using new source configuration

### Data Flow
```
User toggles API mode → AnalyticsDashboard.handleDataSourceChange() 
→ store.setDataSource() → store.clearAnalyticsData() 
→ window.dispatchEvent('dataSourceChanged') 
→ Components reload with new source
```

## Testing Results
- ✅ Frontend builds successfully (no syntax errors)
- ✅ All components now use centralized data source configuration
- ✅ Proper event handling for data source changes
- ✅ No more mixed mock/API data scenarios

## Expected Behavior After Fix
1. **Real API Mode**: All components show live data from backend API
2. **Demo Mode**: All components show consistent mock data
3. **Mode Switch**: All components immediately refresh with new data source
4. **API Failure**: Graceful fallback to demo data with user notification

## Files Modified
- `apps/frontend/src/components/PostViewDynamicsChart.jsx`
- `apps/frontend/src/components/TopPostsTable.jsx` 
- `apps/frontend/src/components/BestTimeRecommender.jsx`
- `apps/frontend/src/components/AnalyticsDashboard.jsx`

Total: 4 files modified to ensure consistent data source behavior across all analytics components.
