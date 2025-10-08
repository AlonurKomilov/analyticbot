import { useMemo } from 'react';
import { processTableData } from '../utils/tableUtils';

/**
 * Custom hook for processing table data
 * Handles filtering, sorting, and pagination
 */
export const useTableData = ({
    data,
    columns,
    searchQuery,
    columnFilters,
    sortBy,
    sortDirection,
    page,
    pageSize,
    columnVisibility
}) => {
    // Get visible columns
    const visibleColumns = useMemo(() => {
        return columns.filter(col => columnVisibility[col.id]);
    }, [columns, columnVisibility]);

    // Process data (filter, sort, paginate)
    const processedResult = useMemo(() => {
        return processTableData({
            data,
            columns: visibleColumns,
            searchQuery,
            columnFilters,
            sortBy,
            sortDirection,
            page,
            pageSize
        });
    }, [
        data,
        visibleColumns,
        searchQuery,
        columnFilters,
        sortBy,
        sortDirection,
        page,
        pageSize
    ]);

    return {
        visibleColumns,
        ...processedResult
    };
};
