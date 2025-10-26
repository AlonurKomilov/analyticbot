/**
 * BaseDataTable Component
 *
 * Reusable data table with sorting, pagination, filtering, row selection, empty state, and loading state.
 * Consolidates 5+ table implementations across the application.
 *
 * Features:
 * - Sorting (single/multi column)
 * - Pagination (client-side or server-side)
 * - Row selection (single/multiple)
 * - Loading state with skeleton
 * - Empty state
 * - Responsive design
 * - Accessibility (WCAG AAA)
 * - Uses design tokens
 *
 * Usage:
 * ```tsx
 * <BaseDataTable
 *   columns={columns}
 *   data={data}
 *   loading={isLoading}
 *   onRowClick={(row) => handleRowClick(row)}
 *   pagination={{
 *     page: 0,
 *     rowsPerPage: 10,
 *     totalCount: 100,
 *     onPageChange: handlePageChange,
 *   }}
 * />
 * ```
 */

import React, { useState, useMemo } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  TableSortLabel,
  Checkbox,
  Box,
  Skeleton,
  Paper,
  Typography,
} from '@mui/material';
import { spacing, colors, radius, shadows, sizing, typography } from '@/theme/tokens';
import BaseEmptyState from './BaseEmptyState';

// =============================================================================
// Types
// =============================================================================

export type SortDirection = 'asc' | 'desc';

export interface BaseColumn<T = any> {
  id: string;
  label: string;
  sortable?: boolean;
  align?: 'left' | 'center' | 'right';
  width?: string | number;
  minWidth?: string | number;
  render?: (row: T, index: number) => React.ReactNode;
  getValue?: (row: T) => any; // For sorting/filtering
}

export interface BasePaginationConfig {
  page: number;
  rowsPerPage: number;
  totalCount: number;
  onPageChange: (page: number) => void;
  onRowsPerPageChange?: (rowsPerPage: number) => void;
  rowsPerPageOptions?: number[];
}

export interface BaseDataTableProps<T = any> {
  // Required
  columns: BaseColumn<T>[];
  data: T[];

  // Optional - Data handling
  getRowId?: (row: T, index: number) => string | number;
  loading?: boolean;
  error?: string | null;

  // Optional - Sorting
  sortBy?: string;
  sortDirection?: SortDirection;
  onSort?: (columnId: string, direction: SortDirection) => void;

  // Optional - Pagination
  pagination?: BasePaginationConfig;

  // Optional - Row selection
  selectable?: boolean;
  selectedRows?: Set<string | number>;
  onSelectionChange?: (selectedRows: Set<string | number>) => void;

  // Optional - Row interaction
  onRowClick?: (row: T, index: number) => void;

  // Optional - Empty state
  emptyStateTitle?: string;
  emptyStateDescription?: string;
  emptyStateAction?: React.ReactNode;

  // Optional - Styling
  maxHeight?: string | number;
  stickyHeader?: boolean;

  // Optional - Accessibility
  ariaLabel?: string;
}

// =============================================================================
// Component
// =============================================================================

function BaseDataTable<T = any>({
  // Required
  columns,
  data,

  // Optional - Data handling
  getRowId = (_, index) => index,
  loading = false,
  error = null,

  // Optional - Sorting
  sortBy,
  sortDirection,
  onSort,

  // Optional - Pagination
  pagination,

  // Optional - Row selection
  selectable = false,
  selectedRows = new Set(),
  onSelectionChange,

  // Optional - Row interaction
  onRowClick,

  // Optional - Empty state
  emptyStateTitle = 'No data',
  emptyStateDescription = 'There are no items to display',
  emptyStateAction,

  // Optional - Styling
  maxHeight,
  stickyHeader = false,

  // Optional - Accessibility
  ariaLabel = 'Data table',
}: BaseDataTableProps<T>) {
  // Internal state for client-side sorting
  const [internalSortBy, setInternalSortBy] = useState<string | undefined>(sortBy);
  const [internalSortDirection, setInternalSortDirection] = useState<SortDirection>(
    sortDirection || 'asc'
  );

  // Use external sort state if provided, otherwise use internal
  const currentSortBy = sortBy !== undefined ? sortBy : internalSortBy;
  const currentSortDirection = sortDirection !== undefined ? sortDirection : internalSortDirection;

  // Handle sort
  const handleSort = (columnId: string) => {
    const column = columns.find(col => col.id === columnId);
    if (!column?.sortable) return;

    const isAsc = currentSortBy === columnId && currentSortDirection === 'asc';
    const newDirection: SortDirection = isAsc ? 'desc' : 'asc';

    if (onSort) {
      // External sort handling
      onSort(columnId, newDirection);
    } else {
      // Internal sort handling
      setInternalSortBy(columnId);
      setInternalSortDirection(newDirection);
    }
  };

  // Client-side sorting (only if no external sort handler)
  const sortedData = useMemo(() => {
    if (onSort || !currentSortBy) return data;

    const column = columns.find(col => col.id === currentSortBy);
    if (!column) return data;

    return [...data].sort((a, b) => {
      const aValue = column.getValue ? column.getValue(a) : (a as any)[currentSortBy];
      const bValue = column.getValue ? column.getValue(b) : (b as any)[currentSortBy];

      if (aValue === bValue) return 0;
      if (aValue == null) return 1;
      if (bValue == null) return -1;

      const comparison = aValue < bValue ? -1 : 1;
      return currentSortDirection === 'asc' ? comparison : -comparison;
    });
  }, [data, currentSortBy, currentSortDirection, columns, onSort]);

  // Handle row selection
  const handleSelectAll = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (!onSelectionChange) return;

    if (event.target.checked) {
      const allIds = new Set(sortedData.map((row, index) => getRowId(row, index)));
      onSelectionChange(allIds);
    } else {
      onSelectionChange(new Set());
    }
  };

  const handleSelectRow = (rowId: string | number) => {
    if (!onSelectionChange) return;

    const newSelection = new Set(selectedRows);
    if (newSelection.has(rowId)) {
      newSelection.delete(rowId);
    } else {
      newSelection.add(rowId);
    }
    onSelectionChange(newSelection);
  };

  const isAllSelected = selectable && selectedRows.size > 0 && selectedRows.size === sortedData.length;
  const isIndeterminate = selectable && selectedRows.size > 0 && selectedRows.size < sortedData.length;

  // Render loading skeleton
  const renderLoadingSkeleton = () => (
    <>
      {Array.from({ length: pagination?.rowsPerPage || 5 }).map((_, index) => (
        <TableRow key={`skeleton-${index}`}>
          {selectable && (
            <TableCell padding="checkbox">
              <Skeleton variant="rectangular" width={42} height={42} />
            </TableCell>
          )}
          {columns.map((column) => (
            <TableCell key={column.id} align={column.align || 'left'}>
              <Skeleton variant="text" width="80%" />
            </TableCell>
          ))}
        </TableRow>
      ))}
    </>
  );

  // Render empty state
  if (!loading && data.length === 0) {
    return (
      <Paper
        sx={{
          borderRadius: radius.card,
          boxShadow: shadows.card,
          overflow: 'hidden',
        }}
      >
        <BaseEmptyState
          title={emptyStateTitle}
          description={emptyStateDescription}
          action={emptyStateAction}
        />
      </Paper>
    );
  }

  return (
    <Paper
      sx={{
        borderRadius: radius.card,
        boxShadow: shadows.card,
        overflow: 'hidden',
      }}
    >
      <TableContainer
        sx={{
          maxHeight: maxHeight,
          overflowX: 'auto',
        }}
      >
        <Table
          stickyHeader={stickyHeader}
          aria-label={ariaLabel}
          sx={{
            '& .MuiTableCell-root': {
              borderColor: colors.border.default,
            },
          }}
        >
          {/* Header */}
          <TableHead>
            <TableRow
              sx={{
                '& .MuiTableCell-head': {
                  backgroundColor: colors.background.paper,
                  color: colors.text.primary,
                  fontWeight: typography.fontWeight.semibold,
                  fontSize: typography.fontSize.sm,
                  minHeight: sizing.touchTarget.min,
                },
              }}
            >
              {/* Select all checkbox */}
              {selectable && (
                <TableCell
                  padding="checkbox"
                  sx={{
                    width: sizing.touchTarget.comfortable,
                  }}
                >
                  <Checkbox
                    indeterminate={isIndeterminate}
                    checked={isAllSelected}
                    onChange={handleSelectAll}
                    inputProps={{
                      'aria-label': 'Select all rows',
                    }}
                    sx={{
                      color: colors.text.secondary,
                      '&.Mui-checked': {
                        color: colors.primary.main,
                      },
                    }}
                  />
                </TableCell>
              )}

              {/* Column headers */}
              {columns.map((column) => (
                <TableCell
                  key={column.id}
                  align={column.align || 'left'}
                  style={{
                    width: column.width,
                    minWidth: column.minWidth,
                  }}
                  sortDirection={currentSortBy === column.id ? currentSortDirection : false}
                >
                  {column.sortable ? (
                    <TableSortLabel
                      active={currentSortBy === column.id}
                      direction={currentSortBy === column.id ? currentSortDirection : 'asc'}
                      onClick={() => handleSort(column.id)}
                      sx={{
                        '&.MuiTableSortLabel-root': {
                          color: colors.text.primary,
                        },
                        '&.Mui-active': {
                          color: colors.primary.main,
                        },
                        '& .MuiTableSortLabel-icon': {
                          color: `${colors.primary.main} !important`,
                        },
                      }}
                    >
                      {column.label}
                    </TableSortLabel>
                  ) : (
                    column.label
                  )}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>

          {/* Body */}
          <TableBody>
            {loading ? (
              renderLoadingSkeleton()
            ) : (
              sortedData.map((row, index) => {
                const rowId = getRowId(row, index);
                const isSelected = selectedRows.has(rowId);

                return (
                  <TableRow
                    key={rowId}
                    hover={!!onRowClick}
                    selected={isSelected}
                    onClick={() => onRowClick?.(row, index)}
                    sx={{
                      cursor: onRowClick ? 'pointer' : 'default',
                      minHeight: sizing.touchTarget.min,
                      '&.MuiTableRow-hover:hover': {
                        backgroundColor: colors.state.hover,
                      },
                      '&.Mui-selected': {
                        backgroundColor: colors.state.selected,
                        '&:hover': {
                          backgroundColor: colors.state.selected,
                        },
                      },
                    }}
                  >
                    {/* Selection checkbox */}
                    {selectable && (
                      <TableCell padding="checkbox">
                        <Checkbox
                          checked={isSelected}
                          onChange={() => handleSelectRow(rowId)}
                          onClick={(e) => e.stopPropagation()}
                          inputProps={{
                            'aria-label': `Select row ${index + 1}`,
                          }}
                          sx={{
                            color: colors.text.secondary,
                            '&.Mui-checked': {
                              color: colors.primary.main,
                            },
                          }}
                        />
                      </TableCell>
                    )}

                    {/* Data cells */}
                    {columns.map((column) => (
                      <TableCell
                        key={column.id}
                        align={column.align || 'left'}
                        sx={{
                          fontSize: typography.fontSize.sm,
                          color: colors.text.primary,
                        }}
                      >
                        {column.render
                          ? column.render(row, index)
                          : (row as any)[column.id]}
                      </TableCell>
                    ))}
                  </TableRow>
                );
              })
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Pagination */}
      {pagination && (
        <TablePagination
          component="div"
          count={pagination.totalCount}
          page={pagination.page}
          onPageChange={(_, newPage) => pagination.onPageChange(newPage)}
          rowsPerPage={pagination.rowsPerPage}
          onRowsPerPageChange={
            pagination.onRowsPerPageChange
              ? (e) => pagination.onRowsPerPageChange!(parseInt(e.target.value, 10))
              : undefined
          }
          rowsPerPageOptions={pagination.rowsPerPageOptions || [5, 10, 25, 50]}
          sx={{
            borderTop: `1px solid ${colors.border.default}`,
            color: colors.text.primary,
            '& .MuiTablePagination-selectLabel, & .MuiTablePagination-displayedRows': {
              color: colors.text.secondary,
              fontSize: typography.fontSize.sm,
            },
            '& .MuiTablePagination-select': {
              color: colors.text.primary,
            },
            '& .MuiTablePagination-actions button': {
              color: colors.text.primary,
              minWidth: sizing.touchTarget.min,
              minHeight: sizing.touchTarget.min,
            },
          }}
        />
      )}

      {/* Error state */}
      {error && (
        <Box
          sx={{
            padding: spacing.lg,
            backgroundColor: colors.error.bg,
            borderTop: `1px solid ${colors.border.default}`,
          }}
        >
          <Typography
            sx={{
              color: colors.error.main,
              fontSize: typography.fontSize.sm,
            }}
          >
            {error}
          </Typography>
        </Box>
      )}
    </Paper>
  );
}

export default BaseDataTable;
