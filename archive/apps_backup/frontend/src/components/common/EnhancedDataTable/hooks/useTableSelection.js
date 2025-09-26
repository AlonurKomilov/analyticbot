import { useMemo, useCallback } from 'react';

/**
 * Custom hook for managing table row selection
 * Handles individual row selection, bulk selection, and selection utilities
 */
export const useTableSelection = ({
    paginatedData = [],
    selectedRows,
    setSelectedRows,
    onSelectionChange
}) => {
    // Selection utilities
    const toggleRowSelection = useCallback((rowIndex) => {
        const newSelection = new Set(selectedRows);
        if (newSelection.has(rowIndex)) {
            newSelection.delete(rowIndex);
        } else {
            newSelection.add(rowIndex);
        }
        setSelectedRows(newSelection);
        onSelectionChange?.(Array.from(newSelection));
    }, [selectedRows, setSelectedRows, onSelectionChange]);
    
    const toggleAllSelection = useCallback(() => {
        if (isAllSelected) {
            setSelectedRows(new Set());
            onSelectionChange?.([]);
        } else {
            const allRowIndices = paginatedData.map((_, index) => index);
            const newSelection = new Set(allRowIndices);
            setSelectedRows(newSelection);
            onSelectionChange?.(allRowIndices);
        }
    }, [paginatedData, setSelectedRows, onSelectionChange]);
    
    const clearSelection = useCallback(() => {
        setSelectedRows(new Set());
        onSelectionChange?.([]);
    }, [setSelectedRows, onSelectionChange]);
    
    // Selection state calculations
    const isAllSelected = useMemo(() => {
        return paginatedData.length > 0 && selectedRows.size === paginatedData.length;
    }, [paginatedData.length, selectedRows.size]);
    
    const isIndeterminate = useMemo(() => {
        return selectedRows.size > 0 && selectedRows.size < paginatedData.length;
    }, [selectedRows.size, paginatedData.length]);
    
    const selectedCount = selectedRows.size;
    const hasSelection = selectedCount > 0;
    
    return {
        // Actions
        toggleRowSelection,
        toggleAllSelection,
        clearSelection,
        
        // State
        isAllSelected,
        isIndeterminate,
        selectedCount,
        hasSelection,
        selectedRows
    };
};