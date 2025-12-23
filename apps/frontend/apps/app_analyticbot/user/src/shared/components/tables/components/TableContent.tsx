import React from 'react';
import {
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    TableSortLabel,
    Checkbox,
    LinearProgress,
    Box
} from '@mui/material';
import { TableChart as TableIcon } from '@mui/icons-material';
import { DENSITY_OPTIONS } from '../utils/tableUtils';
import EmptyState from '@shared/components/feedback/EmptyState';

interface Column {
    id: string;
    header?: string;
    align?: 'left' | 'center' | 'right';
    sortable?: boolean;
    accessor?: (row: any) => any;
    render?: (row: any, rowIndex: number) => React.ReactNode;
    Cell?: React.ComponentType<{ value: any; row: any; rowIndex: number }>;
}

interface RowAction {
    component: React.ComponentType<any>;
    props?: any;
}

interface TableContentProps {
    // Data
    visibleColumns: Column[];
    paginatedData: any[];
    loading?: boolean;

    // Sorting
    sortBy?: string;
    sortDirection?: 'asc' | 'desc';
    onSort?: (columnId: string, direction: 'asc' | 'desc') => void;
    enableSorting?: boolean;

    // Selection
    enableSelection?: boolean;
    selectedRows: Set<number>;
    isAllSelected?: boolean;
    isIndeterminate?: boolean;
    onToggleAllSelection?: () => void;
    onToggleRowSelection?: (rowIndex: number) => void;

    // Styling
    density?: string;
    tableAriaLabel?: string;
    title?: string;

    // Row actions
    onRowClick?: (row: any, index: number) => void;
    rowActions?: RowAction[];
}

/**
 * TableContent Component
 * Renders the main table with headers, body, and sorting
 */
const TableContent: React.FC<TableContentProps> = ({
    // Data
    visibleColumns,
    paginatedData,
    loading,

    // Sorting
    sortBy,
    sortDirection,
    onSort,
    enableSorting,

    // Selection
    enableSelection,
    selectedRows,
    isAllSelected,
    isIndeterminate,
    onToggleAllSelection,
    onToggleRowSelection,

    // Styling
    density,
    tableAriaLabel,
    title,

    // Row actions
    onRowClick,
    rowActions
}) => {
    const currentDensity = DENSITY_OPTIONS.find(opt => opt.key === density);

    const handleSortClick = (columnId: string) => {
        if (!enableSorting) return;

        let newDirection: 'asc' | 'desc' = 'asc';
        if (sortBy === columnId && sortDirection === 'asc') {
            newDirection = 'desc';
        }

        onSort?.(columnId, newDirection);
    };

    const handleRowClick = (row: any, index: number) => {
        if (onRowClick) {
            onRowClick(row, index);
        }
    };

    const renderCellContent = (column: Column, row: any, rowIndex: number): React.ReactNode => {
        // Support both 'render' and 'Cell' properties for flexibility
        if (column.render) {
            return column.render(row, rowIndex);
        }

        if (column.Cell) {
            const value = column.accessor ? column.accessor(row) : row[column.id];
            return <column.Cell value={value} row={row} rowIndex={rowIndex} />;
        }

        const value = column.accessor ? column.accessor(row) : row[column.id];

        // Handle different value types safely
        if (value === null || value === undefined) {
            return '-';
        }

        if (typeof value === 'object') {
            // If it's an object, try to stringify it or return a fallback
            if (Array.isArray(value)) {
                return value.join(', ');
            }
            // For other objects, return a string representation or a fallback
            return JSON.stringify(value);
        }

        return String(value);
    };

    return (
        <TableContainer>
            <Table
                aria-label={tableAriaLabel || title || 'Data table'}
                size={density === 'compact' ? 'small' : 'medium'}
            >
                <TableHead>
                    <TableRow>
                        {/* Selection header */}
                        {enableSelection && (
                            <TableCell padding="checkbox">
                                <Checkbox
                                    indeterminate={isIndeterminate}
                                    checked={isAllSelected}
                                    onChange={onToggleAllSelection}
                                    inputProps={{ 'aria-label': 'Select all rows' }}
                                />
                            </TableCell>
                        )}

                        {/* Column headers */}
                        {visibleColumns.map((column) => (
                            <TableCell
                                key={column.id}
                                align={column.align || 'left'}
                                sortDirection={sortBy === column.id ? sortDirection : false}
                                sx={{
                                    fontWeight: 'bold',
                                    py: (currentDensity?.padding ?? 12) / 8
                                }}
                            >
                                {enableSorting && column.sortable !== false ? (
                                    <TableSortLabel
                                        active={sortBy === column.id}
                                        direction={sortBy === column.id ? sortDirection : 'asc'}
                                        onClick={() => handleSortClick(column.id)}
                                    >
                                        {column.header || column.id}
                                    </TableSortLabel>
                                ) : (
                                    column.header || column.id
                                )}
                            </TableCell>
                        ))}

                        {/* Row actions header */}
                        {rowActions && rowActions.length > 0 && (
                            <TableCell align="right">Actions</TableCell>
                        )}
                    </TableRow>
                </TableHead>

                <TableBody>
                    {loading && (
                        <TableRow>
                            <TableCell
                                colSpan={visibleColumns.length + (enableSelection ? 1 : 0) + ((rowActions?.length ?? 0) > 0 ? 1 : 0)}
                                sx={{ p: 0 }}
                            >
                                <LinearProgress />
                            </TableCell>
                        </TableRow>
                    )}

                    {!loading && paginatedData.length === 0 && (
                        <TableRow>
                            <TableCell
                                colSpan={visibleColumns.length + (enableSelection ? 1 : 0) + ((rowActions?.length ?? 0) > 0 ? 1 : 0)}
                                align="center"
                                sx={{ py: 2 }}
                            >
                                <EmptyState
                                    message="No data available"
                                    icon={<TableIcon sx={{ fontSize: 48, color: 'text.secondary' }} /> as any}
                                />
                            </TableCell>
                        </TableRow>
                    )}

                    {!loading && paginatedData.map((row, rowIndex) => (
                        <TableRow
                            key={rowIndex}
                            hover={!!onRowClick}
                            selected={selectedRows.has(rowIndex)}
                            onClick={() => handleRowClick(row, rowIndex)}
                            sx={{
                                cursor: onRowClick ? 'pointer' : 'default',
                                '&:hover': onRowClick ? { backgroundColor: 'action.hover' } : {}
                            }}
                        >
                            {/* Selection cell */}
                            {enableSelection && (
                                <TableCell padding="checkbox">
                                    <Checkbox
                                        checked={selectedRows.has(rowIndex)}
                                        onChange={() => onToggleRowSelection?.(rowIndex)}
                                        inputProps={{ 'aria-label': `Select row ${rowIndex + 1}` }}
                                    />
                                </TableCell>
                            )}

                            {/* Data cells */}
                            {visibleColumns.map((column) => (
                                <TableCell
                                    key={column.id}
                                    align={column.align || 'left'}
                                    sx={{
                                        py: (currentDensity?.padding ?? 12) / 8
                                    }}
                                >
                                    {renderCellContent(column, row, rowIndex)}
                                </TableCell>
                            ))}

                            {/* Row actions cell */}
                            {rowActions && rowActions.length > 0 && (
                                <TableCell align="right">
                                    <Box sx={{ display: 'flex', gap: 0.5 }}>
                                        {rowActions.map((action, actionIndex) => (
                                            <action.component
                                                key={actionIndex}
                                                row={row}
                                                rowIndex={rowIndex}
                                                {...action.props}
                                            />
                                        ))}
                                    </Box>
                                </TableCell>
                            )}
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </TableContainer>
    );
};

export default TableContent;
