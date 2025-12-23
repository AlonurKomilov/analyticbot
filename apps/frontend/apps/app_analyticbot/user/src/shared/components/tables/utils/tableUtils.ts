/**
 * Utility functions for EnhancedDataTable data processing and filtering
 */

interface Column {
    id: string;
    accessor?: (row: any) => any;
    [key: string]: any;
}

interface ColumnFilters {
    [key: string]: string;
}

interface ProcessTableDataParams {
    data: any[];
    columns: Column[];
    searchQuery: string;
    columnFilters: ColumnFilters;
    sortBy: string | null;
    sortDirection: 'asc' | 'desc';
    page: number;
    pageSize: number;
}

interface ProcessedDataReturn {
    filteredData: any[];
    sortedData: any[];
    paginatedData: any[];
    totalRows: number;
    totalPages: number;
}

/**
 * Filter data based on search query
 */
export const filterDataBySearch = (data: any[], searchQuery: string, columns: Column[]): any[] => {
    if (!searchQuery.trim()) return data;

    const query = searchQuery.toLowerCase();
    return data.filter(row =>
        columns.some(col => {
            const value = col.accessor ? col.accessor(row) : row[col.id];
            return String(value).toLowerCase().includes(query);
        })
    );
};

/**
 * Filter data by column-specific filters
 */
export const filterDataByColumns = (data: any[], columnFilters: ColumnFilters, columns: Column[]): any[] => {
    return data.filter(row => {
        return Object.entries(columnFilters).every(([columnId, filterValue]) => {
            if (!filterValue.trim()) return true;

            const column = columns.find(col => col.id === columnId);
            if (!column) return true;

            const value = column.accessor ? column.accessor(row) : row[columnId];
            return String(value).toLowerCase().includes(filterValue.toLowerCase());
        });
    });
};

/**
 * Sort data by column and direction
 */
export const sortData = (data: any[], sortBy: string | null, sortDirection: 'asc' | 'desc', columns: Column[]): any[] => {
    if (!sortBy) return data;

    const column = columns.find(col => col.id === sortBy);
    if (!column) return data;

    return [...data].sort((a, b) => {
        const aValue = column.accessor ? column.accessor(a) : a[sortBy];
        const bValue = column.accessor ? column.accessor(b) : b[sortBy];

        // Handle different data types
        let comparison = 0;
        if (typeof aValue === 'number' && typeof bValue === 'number') {
            comparison = aValue - bValue;
        } else if (aValue instanceof Date && bValue instanceof Date) {
            comparison = aValue.getTime() - bValue.getTime();
        } else {
            comparison = String(aValue).localeCompare(String(bValue));
        }

        return sortDirection === 'desc' ? -comparison : comparison;
    });
};

/**
 * Paginate data array
 */
export const paginateData = (data: any[], page: number, pageSize: number): any[] => {
    const startIndex = page * pageSize;
    const endIndex = startIndex + pageSize;
    return data.slice(startIndex, endIndex);
};

/**
 * Process data through filtering, sorting, and pagination
 */
export const processTableData = ({
    data,
    columns,
    searchQuery,
    columnFilters,
    sortBy,
    sortDirection,
    page,
    pageSize
}: ProcessTableDataParams): ProcessedDataReturn => {
    // Apply filters
    let filtered = filterDataBySearch(data, searchQuery, columns);
    filtered = filterDataByColumns(filtered, columnFilters, columns);

    // Apply sorting
    const sorted = sortData(filtered, sortBy, sortDirection, columns);

    // Calculate pagination
    const totalRows = sorted.length;
    const totalPages = Math.ceil(totalRows / pageSize);
    const paginated = paginateData(sorted, page, pageSize);

    return {
        filteredData: filtered,
        sortedData: sorted,
        paginatedData: paginated,
        totalRows,
        totalPages
    };
};

// Table density options
export const DENSITY_OPTIONS = [
    { key: 'comfortable', label: 'Comfortable', padding: 16 },
    { key: 'standard', label: 'Standard', padding: 12 },
    { key: 'compact', label: 'Compact', padding: 8 }
];

// Page size options
export const PAGE_SIZE_OPTIONS = [5, 10, 25, 50, 100];
