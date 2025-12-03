# Mock Components

This directory contains demonstration and example components that use mock data for testing and showcasing purposes.

## Demo Pages

### MicroInteractionsDemoPage.jsx
- **Purpose**: Comprehensive showcase of all micro-interaction components
- **Contains**: Mock interaction statistics, demo controls, sample data
- **Usage**: Development testing and feature demonstration
- **Mock Data**: User interaction counters, animation controls, sample metrics

### MicroInteractionsDashboard.jsx
- **Purpose**: Full dashboard implementation with micro-interactions
- **Contains**: Mock analytics metrics, sample dashboard data
- **Usage**: Testing complete dashboard functionality with animations
- **Mock Data**: Analytics metrics, performance indicators, sample charts

## Demo Components

### demo/AnalyticsAdapterDemo.jsx
- **Purpose**: Demo component for testing data source switching functionality
- **Contains**: Mock analytics data, performance testing, adapter comparison
- **Usage**: Development testing of real vs mock data switching
- **Mock Data**: Demo channel data, adapter performance metrics, test results

## Showcase Components with Mock Data

### showcase/tables/UsersTableDemo.jsx
- **Purpose**: Showcases Enhanced User Management Table functionality
- **Contains**: Mock user data for table demonstration
- **Usage**: Table component feature demonstration
- **Mock Data**: Sample user records with various attributes and statuses

### showcase/tables/GenericTableDemo.jsx
- **Purpose**: Showcases Generic Enhanced Data Table capabilities
- **Contains**: Mock generic table data for demonstration
- **Usage**: Generic table component testing and showcase
- **Mock Data**: Sample tabular data with sorting, filtering examples

## Usage Guidelines

These components are for:
- ✅ Development testing and demonstration
- ✅ Feature showcasing and documentation
- ✅ Animation and interaction testing
- ✅ Component integration verification

These components should NOT be used for:
- ❌ Production deployments
- ❌ Real user interfaces
- ❌ Live data displays
- ❌ Actual business logic

## Integration

To use these demo components in development:

```jsx
// Demo pages
import MicroInteractionsDemoPage from '../__mocks__/components/pages/MicroInteractionsDemoPage.jsx';
import MicroInteractionsDashboard from '../__mocks__/components/pages/MicroInteractionsDashboard.jsx';

// Demo components
import AnalyticsAdapterDemo from '../__mocks__/components/demo/AnalyticsAdapterDemo.jsx';

// Showcase components with mock data
import UsersTableDemo from '../__mocks__/components/showcase/tables/UsersTableDemo.jsx';
import GenericTableDemo from '../__mocks__/components/showcase/tables/GenericTableDemo.jsx';
```

## Related Production Components

The production-ready components are located in:
- `src/components/animations/` - Core animation components
- `src/components/pages/EnhancedDashboardPage.jsx` - Production dashboard
- `src/components/layout/` - Layout components with micro-interactions
