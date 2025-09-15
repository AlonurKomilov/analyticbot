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
    Typography,
    Box
} from '@mui/material';
import { DENSITY_OPTIONS } from '../utils/tableUtils';

/**
 * TableContent Component
 * Renders the main table with headers, body, and sorting
 */
const TableContent = ({
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
    
    const handleSortClick = (columnId) => {
        if (!enableSorting) return;
        
        let newDirection = 'asc';
        if (sortBy === columnId && sortDirection === 'asc') {
            newDirection = 'desc';
        }
        
        onSort?.(columnId, newDirection);
    };
    
    const handleRowClick = (row, index) => {
        if (onRowClick) {
            onRowClick(row, index);
        }
    };
    
    const renderCellContent = (column, row, rowIndex) => {
        if (column.render) {
            return column.render(row, rowIndex);
        }
        
        const value = column.accessor ? column.accessor(row) : row[column.id];
        return value;
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
                                    py: currentDensity?.padding / 8 || 1.5
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
                                colSpan={visibleColumns.length + (enableSelection ? 1 : 0) + (rowActions?.length > 0 ? 1 : 0)}
                                sx={{ p: 0 }}
                            >
                                <LinearProgress />
                            </TableCell>
                        </TableRow>
                    )}
                    
                    {!loading && paginatedData.length === 0 && (
                        <TableRow>
                            <TableCell 
                                colSpan={visibleColumns.length + (enableSelection ? 1 : 0) + (rowActions?.length > 0 ? 1 : 0)}
                                align="center"
                                sx={{ py: 4 }}
                            >
                                <Typography variant="body2" color="text.secondary">
                                    No data available
                                </Typography>
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
                                        onChange={() => onToggleRowSelection(rowIndex)}
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
                                        py: currentDensity?.padding / 8 || 1.5
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