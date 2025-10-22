import { useMemo } from 'react';
import { processTableData } from '../utils/tableUtils';

interface Column {
    id: string;
    [key: string]: any;
}

interface ColumnFilters {
    [key: string]: any;
}

interface ColumnVisibility {
    [key: string]: boolean;
}

interface UseTableDataParams {
    data: any[];
    columns: Column[];
    searchQuery: string;
    columnFilters: ColumnFilters;
    sortBy: string | null;
    sortDirection: 'asc' | 'desc';
    page: number;
    pageSize: number;
    columnVisibility: ColumnVisibility;
}

interface ProcessedData {
    filteredData: any[];
    sortedData: any[];
    paginatedData: any[];
    totalRows: number;
    totalPages: number;
}

interface UseTableDataReturn extends ProcessedData {
    visibleColumns: Column[];
}

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
}: UseTableDataParams): UseTableDataReturn => {
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
