/**
 * EnhancedDataTable - Refactored modular components
 * 
 * Main Component:
 * - EnhancedDataTable: Core table component with all enterprise features
 * 
 * Sub-components:
 * - TableToolbar: Header with title, search, and action controls
 * - TableContent: Main table rendering with sorting and selection
 * - TablePaginationControls: Pagination with page size options
 * - TableSearch: Search input with clear functionality
 * - TableExport: Export menu with format selection
 * - TableColumns: Column visibility management
 * - TableDensity: Table density/padding controls
 * 
 * Hooks:
 * - useTableState: State management for pagination, sorting, filtering
 * - useTableData: Data processing with filtering, sorting, pagination
 * - useTableSelection: Row selection and bulk operations
 * 
 * Utilities:
 * - exportUtils: Export functions for CSV, Excel, PDF
 * - tableUtils: Data processing and filtering utilities
 */

// Main component export
export { default as EnhancedDataTable } from './EnhancedDataTable.jsx';

// Sub-component exports
export { default as TableToolbar } from './components/TableToolbar.jsx';
export { default as TableContent } from './components/TableContent.jsx';
export { default as TablePaginationControls } from './components/TablePaginationControls.jsx';
export { default as TableSearch } from './components/TableSearch.jsx';
export { default as TableExport } from './components/TableExport.jsx';
export { default as TableColumns } from './components/TableColumns.jsx';
export { default as TableDensity } from './components/TableDensity.jsx';

// Hook exports
export { useTableState } from './hooks/useTableState.js';
export { useTableData } from './hooks/useTableData.js';
export { useTableSelection } from './hooks/useTableSelection.js';

// Utility exports
export * from './utils/exportUtils.js';
export * from './utils/tableUtils.js';

// Default export for backward compatibility
export { default } from './EnhancedDataTable.jsx';