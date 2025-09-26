import React, { useState, useEffect } from 'react';

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
}) => {
    // Pagination state
    const [page, setPage] = useState(0);
    const [pageSize, setPageSize] = useState(defaultPageSize);
    
    // Sorting state
    const [sortBy, setSortBy] = useState(defaultSortBy);
    const [sortDirection, setSortDirection] = useState(defaultSortDirection);
    
    // Filtering state
    const [searchQuery, setSearchQuery] = useState('');
    const [columnFilters, setColumnFilters] = useState({});
    const [expandedFilters, setExpandedFilters] = useState(false);
    
    // UI state
    const [density, setDensity] = useState(defaultDensity);
    const [columnVisibility, setColumnVisibility] = useState(
        columns.reduce((acc, col) => ({ ...acc, [col.id]: col.visible !== false }), {})
    );
    
    // Selection state
    const [selectedRows, setSelectedRows] = useState(new Set());
    
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