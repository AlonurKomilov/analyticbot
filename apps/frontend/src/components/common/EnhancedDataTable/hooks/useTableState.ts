import { useState, useEffect } from 'react';

interface Column {
    id: string;
    visible?: boolean;
    [key: string]: any;
}

interface ColumnFilters {
    [key: string]: any;
}

interface ColumnVisibility {
    [key: string]: boolean;
}

interface UseTableStateParams {
    data?: any[];
    columns?: Column[];
    defaultPageSize?: number;
    defaultSortBy?: string | null;
    defaultSortDirection?: 'asc' | 'desc';
    defaultDensity?: 'compact' | 'standard' | 'comfortable';
}

interface UseTableStateReturn {
    page: number;
    setPage: (page: number) => void;
    pageSize: number;
    setPageSize: (size: number) => void;
    sortBy: string | null;
    setSortBy: (field: string | null) => void;
    sortDirection: 'asc' | 'desc';
    setSortDirection: (direction: 'asc' | 'desc') => void;
    searchQuery: string;
    setSearchQuery: (query: string) => void;
    columnFilters: ColumnFilters;
    setColumnFilters: (filters: ColumnFilters) => void;
    expandedFilters: boolean;
    setExpandedFilters: (expanded: boolean) => void;
    density: 'compact' | 'standard' | 'comfortable';
    setDensity: (density: 'compact' | 'standard' | 'comfortable') => void;
    columnVisibility: ColumnVisibility;
    setColumnVisibility: (visibility: ColumnVisibility) => void;
    selectedRows: Set<number>;
    setSelectedRows: (rows: Set<number>) => void;
    resetPage: () => void;
}

/**
 * Custom hook for managing table state
 * Handles pagination, sorting, filtering, and selection
 */
export const useTableState = ({
    data = [],
    columns = [],
    defaultPageSize = 10,
    defaultSortBy = null,
    defaultSortDirection = 'asc',
    defaultDensity = 'standard'
}: UseTableStateParams = {}): UseTableStateReturn => {
    // Pagination state
    const [page, setPage] = useState<number>(0);
    const [pageSize, setPageSize] = useState<number>(defaultPageSize);

    // Sorting state
    const [sortBy, setSortBy] = useState<string | null>(defaultSortBy);
    const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>(defaultSortDirection);

    // Filtering state
    const [searchQuery, setSearchQuery] = useState<string>('');
    const [columnFilters, setColumnFilters] = useState<ColumnFilters>({});
    const [expandedFilters, setExpandedFilters] = useState<boolean>(false);

    // UI state
    const [density, setDensity] = useState<'compact' | 'standard' | 'comfortable'>(defaultDensity);
    const [columnVisibility, setColumnVisibility] = useState<ColumnVisibility>(
        columns.reduce((acc, col) => ({ ...acc, [col.id]: col.visible !== false }), {})
    );

    // Selection state
    const [selectedRows, setSelectedRows] = useState<Set<number>>(new Set());

    // Reset page when filters change
    const resetPage = () => setPage(0);

    // Reset selections when data changes
    useEffect(() => {
        setSelectedRows(new Set());
        setPage(0);
    }, [data]);

    return {
        // Pagination
        page,
        setPage,
        pageSize,
        setPageSize,

        // Sorting
        sortBy,
        setSortBy,
        sortDirection,
        setSortDirection,

        // Filtering
        searchQuery,
        setSearchQuery,
        columnFilters,
        setColumnFilters,
        expandedFilters,
        setExpandedFilters,

        // UI
        density,
        setDensity,
        columnVisibility,
        setColumnVisibility,

        // Selection
        selectedRows,
        setSelectedRows,

        // Utility
        resetPage
    };
};
