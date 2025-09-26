/**
 * Utility functions for EnhancedDataTable data processing and filtering
 */

/**
 * Filter data based on search query
 * @param {Array} data - Data array to filter
 * @param {string} searchQuery - Search term
 * @param {Array} columns - Column definitions
 * @returns {Array} Filtered data
 */
export const filterDataBySearch = (data, searchQuery, columns) => {
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
 * @param {Array} data - Data array to filter
 * @param {Object} columnFilters - Column filter values
 * @param {Array} columns - Column definitions
 * @returns {Array} Filtered data
 */
export const filterDataByColumns = (data, columnFilters, columns) => {
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
 * @param {Array} data - Data array to sort
 * @param {string} sortBy - Column ID to sort by
 * @param {string} sortDirection - Sort direction ('asc' or 'desc')
 * @param {Array} columns - Column definitions
 * @returns {Array} Sorted data
 */
export const sortData = (data, sortBy, sortDirection, columns) => {
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
 * @param {Array} data - Data array to paginate
 * @param {number} page - Current page (0-indexed)
 * @param {number} pageSize - Items per page
 * @returns {Array} Paginated data
 */
export const paginateData = (data, page, pageSize) => {
    const startIndex = page * pageSize;
    const endIndex = startIndex + pageSize;
    return data.slice(startIndex, endIndex);
};

/**
 * Process data through filtering, sorting, and pagination
 * @param {Object} params - Processing parameters
 * @returns {Object} Processed data and metadata
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
}) => {
    // Apply filters
    let filtered = filterDataBySearch(data, searchQuery, columns);
    filtered = filterDataByColumns(filtered, columnFilters, columns);
    
    // Apply sorting
    const sorted = sortData(filtered, sortBy, sortDirection, columns);
    
    // Calculate pagination
    const totalItems = sorted.length;
    const totalPages = Math.ceil(totalItems / pageSize);
    const paginated = paginateData(sorted, page, pageSize);
    
    return {
        processedData: sorted,
        paginatedData: paginated,
        totalItems,
        totalPages,
        currentPage: page,
        pageSize
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