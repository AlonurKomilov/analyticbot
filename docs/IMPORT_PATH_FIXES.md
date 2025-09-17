# Import Path Fixes for Moved Mock Components

## Issue
When components were moved from `src/components/` to `src/__mocks__/components/`, their import paths to production components became incorrect, causing build errors.

## Fixed Import Paths

### UsersTableDemo.jsx
**Location**: `src/__mocks__/components/showcase/tables/UsersTableDemo.jsx`

**Before**:
```jsx
import EnhancedUserManagementTable from '../../EnhancedUserManagementTable';
```

**After**:
```jsx
import EnhancedUserManagementTable from '../../../../components/EnhancedUserManagementTable';
```

### GenericTableDemo.jsx
**Location**: `src/__mocks__/components/showcase/tables/GenericTableDemo.jsx`

**Before**:
```jsx
import { EnhancedDataTable } from '../../common/EnhancedDataTable';
```

**After**:
```jsx
import { EnhancedDataTable } from '../../../../components/common/EnhancedDataTable';
```

### AnalyticsAdapterDemo.jsx
**Location**: `src/__mocks__/components/demo/AnalyticsAdapterDemo.jsx`

**Before**:
```jsx
import { useDataSource, useAnalytics } from '../../hooks/useDataSource';
import { DataSourceManager } from '../../utils/dataSourceManager';
```

**After**:
```jsx
import { useDataSource, useAnalytics } from '../../../hooks/useDataSource';
import { DataSourceManager } from '../../../utils/dataSourceManager';
```

## Path Calculation

From `__mocks__/components/` to production paths:

```
__mocks__/components/showcase/tables/ → ../../../../components/
__mocks__/components/demo/           → ../../../hooks/
__mocks__/components/demo/           → ../../../utils/
```

## Status
✅ All import paths fixed
✅ Components can now properly import production dependencies
✅ Build errors resolved