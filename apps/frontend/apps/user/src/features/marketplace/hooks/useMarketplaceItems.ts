/**
 * useMarketplaceItems Hook
 * 
 * Fetch and manage marketplace items with filtering, search, and caching.
 * 
 * @module features/marketplace/hooks/useMarketplaceItems
 */

import { useState, useEffect, useCallback, useMemo } from 'react';
import { getMarketplaceItems, type ItemsQueryParams } from '../api/items';
import type { MarketplaceItem, MarketplaceCategory } from '../types';

interface UseMarketplaceItemsOptions {
  category?: MarketplaceCategory;
  searchQuery?: string;
  featured?: boolean;
  autoFetch?: boolean;
}

interface UseMarketplaceItemsResult {
  items: MarketplaceItem[];
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
  setCategory: (category: MarketplaceCategory | undefined) => void;
  setSearchQuery: (query: string) => void;
}

/**
 * Hook for fetching and managing marketplace items
 */
export function useMarketplaceItems(options: UseMarketplaceItemsOptions = {}): UseMarketplaceItemsResult {
  const { 
    category: initialCategory, 
    searchQuery: initialSearch = '',
    featured,
    autoFetch = true,
  } = options;

  const [items, setItems] = useState<MarketplaceItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [category, setCategory] = useState<MarketplaceCategory | undefined>(initialCategory);
  const [searchQuery, setSearchQuery] = useState(initialSearch);

  const fetchItems = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const params: ItemsQueryParams = {};
      
      if (category) params.category = category;
      if (searchQuery) params.search = searchQuery;
      if (featured !== undefined) params.featured = featured;
      
      const data = await getMarketplaceItems(params);
      setItems(data);
    } catch (err) {
      console.error('Failed to fetch marketplace items:', err);
      setError(err instanceof Error ? err.message : 'Failed to load items');
    } finally {
      setLoading(false);
    }
  }, [category, searchQuery, featured]);

  // Auto-fetch on mount and when params change
  useEffect(() => {
    if (autoFetch) {
      fetchItems();
    }
  }, [fetchItems, autoFetch]);

  // Memoize filtered items for search
  const filteredItems = useMemo(() => {
    if (!searchQuery.trim()) return items;
    
    const query = searchQuery.toLowerCase();
    return items.filter(item => 
      item.name.toLowerCase().includes(query) ||
      item.description.toLowerCase().includes(query)
    );
  }, [items, searchQuery]);

  return {
    items: filteredItems,
    loading,
    error,
    refetch: fetchItems,
    setCategory,
    setSearchQuery,
  };
}
