import { useMemo, useCallback } from 'react';

interface UseTableSelectionParams {
    paginatedData?: any[];
    selectedRows: Set<number>;
    setSelectedRows: (rows: Set<number>) => void;
    onSelectionChange?: (selectedIndices: number[]) => void;
}

interface UseTableSelectionReturn {
    toggleRowSelection: (rowIndex: number) => void;
    toggleAllSelection: () => void;
    clearSelection: () => void;
    isAllSelected: boolean;
    isIndeterminate: boolean;
    selectedCount: number;
    hasSelection: boolean;
    selectedRows: Set<number>;
}

/**
 * Custom hook for managing table row selection
 * Handles individual row selection, bulk selection, and selection utilities
 */
export const useTableSelection = ({
    paginatedData = [],
    selectedRows,
    setSelectedRows,
    onSelectionChange
}: UseTableSelectionParams): UseTableSelectionReturn => {
    // Selection state calculations
    const isAllSelected = useMemo(() => {
        return paginatedData.length > 0 && selectedRows.size === paginatedData.length;
    }, [paginatedData.length, selectedRows.size]);

    const isIndeterminate = useMemo(() => {
        return selectedRows.size > 0 && selectedRows.size < paginatedData.length;
    }, [selectedRows.size, paginatedData.length]);

    // Selection utilities
    const toggleRowSelection = useCallback((rowIndex: number) => {
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
    }, [isAllSelected, paginatedData, setSelectedRows, onSelectionChange]);

    const clearSelection = useCallback(() => {
        setSelectedRows(new Set());
        onSelectionChange?.([]);
    }, [setSelectedRows, onSelectionChange]);

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
