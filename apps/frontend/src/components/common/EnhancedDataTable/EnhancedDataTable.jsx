import React, { useEffect, useRef, useCallback } from 'react';
import {
    Paper,
    Alert,
    Typography,
    Button
} from '@mui/material';
import {
    Refresh as RefreshIcon
} from '@mui/icons-material';

// Import modular components
import TableToolbar from './components/TableToolbar.jsx';
import TableContent from './components/TableContent.jsx';
import TablePaginationControls from './components/TablePaginationControls.jsx';

// Import custom hooks
import { useTableState } from './hooks/useTableState.js';
import { useTableData } from './hooks/useTableData.js';
import { useTableSelection } from './hooks/useTableSelection.js';

// Import utilities
import { EXPORT_FORMATS, exportToCsv, exportToExcel, exportToPdf } from './utils/exportUtils.js';

/**
 * Enhanced Data Table Component - Refactored Modular Version
 * 
 * Enterprise-grade data table with advanced features:
 * - Advanced pagination with customizable page sizes
 * - Multi-column sorting with visual indicators
 * - Global search and column-specific filtering
 * - Column visibility management and reordering
 * - Export functionality (CSV, Excel, PDF)
 * - Bulk selection and batch operations
 * - Real-time data refresh capabilities
 * - Responsive design with density controls
 * - Professional loading and error states
 * - Full accessibility compliance
 */
export const EnhancedDataTable = ({
    // Data props
    data = [],
    columns = [],
    loading = false,
    error = null,
    
    // Table configuration
    title = '',
    subtitle = '',
    
    // Pagination
    enablePagination = true,
    defaultPageSize = 10,
    
    // Sorting
    enableSorting = true,
    defaultSortBy = null,
    defaultSortDirection = 'asc',
    
    // Searching & Filtering  
    enableSearch = true,
    enableFiltering = true,
    searchPlaceholder = 'Search all columns...',
    
    // Column management
    enableColumnVisibility = true,
    enableColumnReordering = false,
    
    // Selection
    enableSelection = true,
    enableBulkActions = true,
    
    // Export
    enableExport = true,
    exportFilename = 'data-export',
    
    // Refresh
    enableRefresh = true,
    onRefresh,
    
    // Density
    enableDensityToggle = true,
    defaultDensity = 'standard',
    
    // Custom actions
    bulkActions = [],
    rowActions = [],
    
    // Event handlers
    onRowClick,
    onSelectionChange,
    onSort,
    onFilter,
    
    // Advanced features
    enableRealTimeUpdates = false,
    refreshInterval = 30000,
    
    // Styling
    sx = {},
    
    // Accessibility
    tableAriaLabel,
    
    ...otherProps
}) => {
    // State management using custom hooks
    const tableState = useTableState({
        data,
        columns,
        defaultPageSize,
        defaultSortBy,
        defaultSortDirection,
        defaultDensity
    });
    
    const {
        page,
        setPage,
        pageSize,
        setPageSize,
        sortBy,
        setSortBy,
        sortDirection,
        setSortDirection,
        searchQuery,
        setSearchQuery,
        columnFilters,
        setColumnFilters,
        expandedFilters,
        setExpandedFilters,
        density,
        setDensity,
        columnVisibility,
        setColumnVisibility,
        selectedRows,
        setSelectedRows,
        resetPage
    } = tableState;
    
    // Data processing using custom hook
    const tableData = useTableData({
        data,
        columns,
        searchQuery,
        columnFilters,
        sortBy,
        sortDirection,
        page,
        pageSize,
        columnVisibility
    });
    
    const {
        visibleColumns,
        processedData,
        paginatedData,
        totalItems,
        totalPages
    } = tableData;
    
    // Selection management using custom hook
    const tableSelection = useTableSelection({
        paginatedData,
        selectedRows,
        setSelectedRows,
        onSelectionChange
    });
    
    const {
        toggleRowSelection,
        toggleAllSelection,
        clearSelection,
        isAllSelected,
        isIndeterminate,
        selectedCount,
        hasSelection
    } = tableSelection;
    
    // Auto-refresh functionality
    const refreshIntervalRef = useRef(null);
    
    useEffect(() => {
        if (enableRealTimeUpdates && onRefresh && refreshInterval > 0) {
            refreshIntervalRef.current = setInterval(onRefresh, refreshInterval);
            return () => {
                if (refreshIntervalRef.current) {
                    clearInterval(refreshIntervalRef.current);
                }
            };
        }
    }, [enableRealTimeUpdates, onRefresh, refreshInterval]);
    
    // Export functionality
    const handleExport = useCallback((format) => {
        const headers = visibleColumns.map(col => col.header || col.id);
        const exportData = selectedRows.size > 0 
            ? Array.from(selectedRows).map(index => paginatedData[index])
            : processedData;
        
        const rows = exportData.map(row =>
            visibleColumns.map(col => {
                const value = col.accessor ? col.accessor(row) : row[col.id];
                return value;
            })
        );
        
        switch (format) {
            case 'csv':
                exportToCsv(headers, rows, exportFilename);
                break;
            case 'excel':
                exportToExcel(headers, rows, exportFilename);
                break;
            case 'pdf':
                exportToPdf(headers, rows, exportFilename, title);
                break;
        }
    }, [processedData, selectedRows, visibleColumns, paginatedData, exportFilename, title]);
    
    // Sorting handler
    const handleSort = useCallback((columnId, direction) => {
        setSortBy(columnId);
        setSortDirection(direction);
        resetPage();
        onSort?.(columnId, direction);
    }, [setSortBy, setSortDirection, resetPage, onSort]);
    
    // Search handler with page reset
    const handleSearchChange = useCallback((query) => {
        setSearchQuery(query);
        resetPage();
    }, [setSearchQuery, resetPage]);
    
    // Error state
    if (error) {
        return (
            <Paper sx={sx}>
                <Alert severity="error" sx={{ m: 2 }}>
                    <Typography variant="h6">Error Loading Data</Typography>
                    <Typography variant="body2">{error}</Typography>
                    {enableRefresh && onRefresh && (
                        <Button
                            startIcon={<RefreshIcon />}
                            onClick={onRefresh}
                            sx={{ mt: 1 }}
                        >
                            Retry
                        </Button>
                    )}
                </Alert>
            </Paper>
        );
    }
    
    return (
        <Paper sx={{ width: '100%', ...sx }} {...otherProps}>
            {/* Header Toolbar */}
            <TableToolbar
                title={title}
                subtitle={subtitle}
                enableSearch={enableSearch}
                searchQuery={searchQuery}
                setSearchQuery={handleSearchChange}
                searchPlaceholder={searchPlaceholder}
                enableExport={enableExport}
                onExport={handleExport}
                exportFilename={exportFilename}
                enableColumnVisibility={enableColumnVisibility}
                columns={columns}
                columnVisibility={columnVisibility}
                setColumnVisibility={setColumnVisibility}
                enableDensityToggle={enableDensityToggle}
                density={density}
                setDensity={setDensity}
                enableRefresh={enableRefresh}
                onRefresh={onRefresh}
                loading={loading}
            />
            
            {/* Main Table */}
            <TableContent
                visibleColumns={visibleColumns}
                paginatedData={paginatedData}
                loading={loading}
                sortBy={sortBy}
                sortDirection={sortDirection}
                onSort={handleSort}
                enableSorting={enableSorting}
                enableSelection={enableSelection}
                selectedRows={selectedRows}
                isAllSelected={isAllSelected}
                isIndeterminate={isIndeterminate}
                onToggleAllSelection={toggleAllSelection}
                onToggleRowSelection={toggleRowSelection}
                density={density}
                tableAriaLabel={tableAriaLabel}
                title={title}
                onRowClick={onRowClick}
                rowActions={rowActions}
            />
            
            {/* Pagination */}
            <TablePaginationControls
                totalItems={totalItems}
                page={page}
                pageSize={pageSize}
                onPageChange={setPage}
                onPageSizeChange={setPageSize}
                enablePagination={enablePagination}
            />
        </Paper>
    );
};

export default EnhancedDataTable;