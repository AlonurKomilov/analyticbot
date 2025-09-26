# Components Archive

This folder contains archived components that have been moved during refactoring to maintain clean project structure.

## Directory Structure

### `/backups/`
Contains backup files created during component refactoring phases:
- `AnalyticsDashboard.jsx.backup` - Original 539-line monolith (Phase 3.1)
- `PostViewDynamicsChart.jsx.backup` - Original 623-line monolith (Phase 3.2) 
- `NavigationBar.jsx.backup` - Original navigation component (Phase 2)

### `/unused/`
Contains components that were identified as unused and removed from active codebase:
- `AdvancedDashboard.jsx` - 423-line unused analytics dashboard
- `ModernAdvancedAnalyticsDashboard.jsx` - 451-line unused modern analytics dashboard

### `/old-versions/`
Contains old development versions and intermediate files:
- `PostViewDynamicsChart.new.jsx` - Development version during refactoring

## Archive Policy

- **Backup Files**: Created automatically during refactoring phases
- **Unused Components**: Moved here when confirmed no imports/references exist
- **Old Versions**: Development artifacts and intermediate versions

## Restoration

If any archived component needs to be restored:
1. Check current component structure for conflicts
2. Update import paths as needed
3. Run validation tests
4. Consider if modern refactored version meets requirements

## Refactoring History

- **Phase 2**: NavigationBar extraction (6 components)
- **Phase 3.1**: AnalyticsDashboard extraction (8 components) 
- **Phase 3.2**: PostViewDynamicsChart extraction (6 components)
- **Phase 3.3**: Ready for RealTimeAlertsSystem refactoring

Last Updated: September 14, 2025