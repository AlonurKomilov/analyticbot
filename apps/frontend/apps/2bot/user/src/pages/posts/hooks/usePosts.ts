/**
 * usePosts Hook
 * Handles posts data fetching and state management
 */

import { useState, useEffect } from 'react';
import { apiClient } from '@api/client';
import type { Post, PostsResponse, PostsFilters } from '../types/Post';

interface UsePostsReturn {
  posts: Post[];
  isLoading: boolean;
  error: string | null;
  total: number;
  totalPages: number;
  refetch: () => Promise<void>;
}

const PAGE_SIZE = 50;

export const usePosts = (filters: PostsFilters): UsePostsReturn => {
  const [posts, setPosts] = useState<Post[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);

  const fetchPosts = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const params: any = {
        page: filters.page,
        page_size: PAGE_SIZE
      };

      if (filters.selectedChannel !== 'all') {
        params.channel_id = filters.selectedChannel;
      }

      if (filters.searchQuery.trim()) {
        params.search = filters.searchQuery.trim();
      }

      console.log('📡 API Request params:', params);
      const response = await apiClient.get<PostsResponse>('/posts', { params });
      console.log('📥 API Response:', {
        total: response.total,
        postsCount: response.posts.length,
        firstPostId: response.posts[0]?.msg_id
      });

      setPosts(response.posts);
      setTotal(response.total);
      setTotalPages(Math.ceil(response.total / PAGE_SIZE));
    } catch (err: any) {
      console.error('Error fetching posts:', err);
      setError(err.response?.data?.detail || 'Failed to fetch posts');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    console.log('🔄 Fetching posts - page:', filters.page, 'selectedChannel:', filters.selectedChannel, 'search:', filters.searchQuery);
    void fetchPosts();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters.page, filters.selectedChannel, filters.searchQuery]);

  return {
    posts,
    isLoading,
    error,
    total,
    totalPages,
    refetch: fetchPosts
  };
};
