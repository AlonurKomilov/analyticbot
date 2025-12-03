import React, { useEffect, useRef, useCallback } from 'react';
import {
    Paper,
    Alert,
    Typography,
    Button,
    SxProps,
    Theme
} from '@mui/material';
import {
    Refresh as RefreshIcon
} from '@mui/icons-material';

// Import modular components
import TableToolbar from './components/TableToolbar';
import TableContent from './components/TableContent';
import TablePaginationControls from './components/TablePaginationControls';

// Import custom hooks
import { useTableState } from './hooks/useTableState';
import { useTableData } from './hooks/useTableData';
import { useTableSelection } from './hooks/useTableSelection';

// Import utilities
import { exportToCsv, exportToExcel, exportToPdf } from './utils/exportUtils';

/**
 * Type definitions
 */
export type SortDirection = 'asc' | 'desc';
export type Density = 'compact' | 'standard' | 'comfortable';
export type ExportFormat = 'csv' | 'excel' | 'pdf';

export interface Column<T = any> {
    id: string;
    header?: string;
    accessor?: (row: T) => any;
    sortable?: boolean;
    filterable?: boolean;
    width?: string | number;
    align?: 'left' | 'center' | 'right';
    Cell?: React.ComponentType<{ value: any; row: T }>;
    [key: string]: any;
}

export interface BulkAction {
    label: string;
    icon?: React.ReactNode;
    onClick: (selectedRows: Set<number>) => void;
    disabled?: boolean;
}

export interface RowAction<T = any> {
    label: string;
    icon?: React.ReactNode;
    onClick: (row: T, index: number) => void;
    disabled?: (row: T) => boolean;
    show?: (row: T) => boolean;
}

export interface EnhancedDataTableProps<T = any> {
    // Data props
    data?: T[];
    columns?: Column<T>[];
    loading?: boolean;
    error?: string | null;

    // Table configuration
    title?: string;
    subtitle?: string;

    // Pagination
    enablePagination?: boolean;
    defaultPageSize?: number;

    // Sorting
    enableSorting?: boolean;
    defaultSortBy?: string | null;
    defaultSortDirection?: SortDirection;

    // Searching & Filtering
    enableSearch?: boolean;
    searchPlaceholder?: string;

    // Column management
    enableColumnVisibility?: boolean;

    // Selection
    enableSelection?: boolean;

    // Export
    enableExport?: boolean;
    exportFilename?: string;

    // Refresh
    enableRefresh?: boolean;
    onRefresh?: () => void;

    // Density
    enableDensityToggle?: boolean;
    defaultDensity?: Density;

    // Custom actions
    rowActions?: RowAction<T>[];

    // Event handlers
    onRowClick?: (row: T, index: number) => void;
    onSelectionChange?: (selectedRows: Set<number>) => void;
    onSort?: (columnId: string, direction: SortDirection) => void;

    // Advanced features
    enableRealTimeUpdates?: boolean;
    refreshInterval?: number;

    // Styling
    sx?: SxProps<Theme>;

    // Accessibility
    tableAriaLabel?: string;
}

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
export const EnhancedDataTable = <T extends Record<string, any> = any>({
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
    searchPlaceholder = 'Search all columns...',

    // Column management
    enableColumnVisibility = true,

    // Selection
    enableSelection = true,

    // Export
    enableExport = true,
    exportFilename = 'data-export',

    // Refresh
    enableRefresh = false,

    // Density
    enableDensityToggle = true,
    defaultDensity = 'standard',

    // Custom actions
    rowActions = [],

    // Event handlers
    onRowClick,
    onSelectionChange,
    onSort,

    // Advanced features
    onRefresh,

    // Styling
    sx = {},

    // Accessibility
    tableAriaLabel
}: EnhancedDataTableProps<T>) => {
    // State management using custom hooks
    const tableState = useTableState({
        data: data as any,
        columns: columns as any,
        defaultPageSize,
        defaultSortBy: (defaultSortBy || null) as any,
        defaultSortDirection,
        defaultDensity
    }) as any;

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
        columnFilters: {},
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
        totalRows
    } = tableData as any;

    // Selection management using custom hook
    const tableSelection = useTableSelection({
        paginatedData,
        selectedRows,
        setSelectedRows,
        onSelectionChange: onSelectionChange ? (indices: number[]) => onSelectionChange(new Set(indices)) : undefined
    }) as any;

    const {
        toggleRowSelection,
        toggleAllSelection,
        isAllSelected,
        isIndeterminate
    } = tableSelection;

    // Auto-refresh functionality
    const refreshIntervalRef = useRef<NodeJS.Timeout | null>(null);

    useEffect(() => {
        if (enableRefresh && onRefresh) {
            refreshIntervalRef.current = setInterval(() => {
                onRefresh();
            }, 30000); // 30 second refresh interval

            return () => {
                if (refreshIntervalRef.current) {
                    clearInterval(refreshIntervalRef.current);
                }
            };
        }
        return undefined;
    }, [enableRefresh, onRefresh]);    // Export functionality
    const handleExport = useCallback((format: string) => {
        const headers = visibleColumns.map((col: Column<T>) => col.header || col.id);
        const exportData = selectedRows.size > 0
            ? Array.from(selectedRows).map(index => paginatedData[index as number])
            : processedData;

        const rows = exportData.map((row: T) =>
            visibleColumns.map((col: Column<T>) => {
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
            default:
                break;
        }
    }, [processedData, selectedRows, visibleColumns, paginatedData, exportFilename, title]);

    // Sorting handler
    const handleSort = useCallback((columnId: string, direction: string) => {
        setSortBy(columnId as any);
        setSortDirection(direction as any);
        resetPage();
        onSort?.(columnId, direction as SortDirection);
    }, [setSortBy, setSortDirection, resetPage, onSort]);

    // Search handler with page reset
    const handleSearchChange = useCallback((query: string) => {
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
        <Paper sx={{ width: '100%', ...sx }}>
            {/* Header Toolbar */}
            <TableToolbar
                title={title}
                subtitle={subtitle}
                enableSearch={enableSearch}
                searchQuery={searchQuery}
                setSearchQuery={handleSearchChange}
                searchPlaceholder={searchPlaceholder}
                enableExport={enableExport}
                onExport={handleExport as any}
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
                sortBy={sortBy || undefined}
                sortDirection={sortDirection as 'asc' | 'desc' | undefined}
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
                rowActions={rowActions as any}
            />

            {/* Pagination */}
            <TablePaginationControls
                totalItems={totalRows}
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
