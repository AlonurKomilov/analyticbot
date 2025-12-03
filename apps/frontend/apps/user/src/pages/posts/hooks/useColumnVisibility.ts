/**
 * useColumnVisibility Hook
 * Manages table column visibility state
 */

import { useState } from 'react';
import type { VisibleColumns } from '../types/Post';

interface UseColumnVisibilityReturn {
  visibleColumns: VisibleColumns;
  toggleColumn: (column: keyof VisibleColumns) => void;
  showAllColumns: () => void;
  hideAllColumns: () => void;
  visibleCount: number;
  totalCount: number;
}

const DEFAULT_VISIBLE_COLUMNS: VisibleColumns = {
  channel: true,
  messageId: true,
  content: true,
  views: true,
  forwards: true,
  comments: true,
  reactions: true,
  telegram: true,
  date: true,
};

export const useColumnVisibility = (): UseColumnVisibilityReturn => {
  const [visibleColumns, setVisibleColumns] = useState<VisibleColumns>(DEFAULT_VISIBLE_COLUMNS);

  const toggleColumn = (column: keyof VisibleColumns) => {
    setVisibleColumns(prev => ({
      ...prev,
      [column]: !prev[column]
    }));
  };

  const showAllColumns = () => {
    setVisibleColumns(DEFAULT_VISIBLE_COLUMNS);
  };

  const hideAllColumns = () => {
    setVisibleColumns({
      channel: true, // Keep at least channel visible
      messageId: true, // Keep at least message ID visible
      content: false,
      views: false,
      forwards: false,
      comments: false,
      reactions: false,
      telegram: false,
      date: false,
    });
  };

  const visibleCount = Object.values(visibleColumns).filter(Boolean).length;
  const totalCount = Object.keys(visibleColumns).length;

  return {
    visibleColumns,
    toggleColumn,
    showAllColumns,
    hideAllColumns,
    visibleCount,
    totalCount
  };
};
