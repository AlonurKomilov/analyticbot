/**
 * usePostFilters Hook
 * Manages filter state (channel, search, pagination)
 */

import { useState } from 'react';
import type { PostsFilters } from '../types/Post';

interface UsePostFiltersReturn extends PostsFilters {
  setSelectedChannel: (channel: number | 'all') => void;
  setSearchQuery: (query: string) => void;
  setPage: (page: number) => void;
  resetFilters: () => void;
}

export const usePostFilters = (): UsePostFiltersReturn => {
  const [selectedChannel, setSelectedChannel] = useState<number | 'all'>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [page, setPage] = useState(1);

  const handleSetSelectedChannel = (channel: number | 'all') => {
    setSelectedChannel(channel);
    setPage(1); // Reset to first page when changing channel
  };

  const handleSetSearchQuery = (query: string) => {
    setSearchQuery(query);
    setPage(1); // Reset to first page when searching
  };

  const resetFilters = () => {
    setSelectedChannel('all');
    setSearchQuery('');
    setPage(1);
  };

  return {
    selectedChannel,
    searchQuery,
    page,
    setSelectedChannel: handleSetSelectedChannel,
    setSearchQuery: handleSetSearchQuery,
    setPage,
    resetFilters
  };
};
