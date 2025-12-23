/**
 * Posts Page - Main entry point for posts feature
 * Clean, focused page using microservice-style architecture
 */

import React, { useEffect, useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Button,
  CircularProgress,
  Alert,
  Pagination,
} from '@mui/material';
import { TrendingUp, Add } from '@mui/icons-material';
import { Link } from 'react-router-dom';
import { ROUTES } from '@config/routes';
import { useChannelStore } from '@store';
import { usePosts } from './hooks/usePosts';
import { usePostFilters } from './hooks/usePostFilters';
import { useColumnVisibility } from './hooks/useColumnVisibility';
import { PostsFilters } from './components/PostsFilters';
import { PostsViewControls } from './components/PostsViewControls';
import { PostsTable } from './components/PostsTable';
import { PostsGrid } from './components/PostsGrid';
import type { Post, ViewMode } from './types/Post';

const PostsPage: React.FC = () => {
  const [viewMode, setViewMode] = useState<ViewMode>('table');
  const { channels, fetchChannels } = useChannelStore();

  // Custom hooks for state management
  const filters = usePostFilters();
  const { posts, isLoading, error, total, totalPages } = usePosts(filters);
  const columnVisibility = useColumnVisibility();

  // Fetch channels on mount if not already loaded
  useEffect(() => {
    if (channels.length === 0) {
      void fetchChannels();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Utility functions
  const formatDate = (date: string) => {
    if (!date) return '-';
    return new Date(date).toLocaleString();
  };

  const getTelegramLink = (post: Post) => {
    const channelIdentifier = post.channel_username || `c/${post.channel_id}`;
    return `https://t.me/${channelIdentifier}/${post.msg_id}`;
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        {/* Header with Create Post Button */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 3 }}>
          <Box>
            <Typography variant="h4" component="h1" gutterBottom>
              All Posts
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Real-time posts collected from your Telegram channels via MTProto
            </Typography>
          </Box>
          <Button
            component={Link}
            to={ROUTES.CREATE_POST}
            variant="contained"
            startIcon={<Add />}
            size="large"
          >
            Create Post
          </Button>
        </Box>

        {/* Error Alert */}
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {/* Loading State */}
        {isLoading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
            <CircularProgress />
          </Box>
        )}

        {/* Filters */}
        <PostsFilters
          selectedChannel={filters.selectedChannel}
          searchQuery={filters.searchQuery}
          total={total}
          channels={channels}
          onChannelChange={filters.setSelectedChannel}
          onSearchChange={filters.setSearchQuery}
          onSearchClear={() => filters.setSearchQuery('')}
        />

        {/* Empty State */}
        {!isLoading && posts.length === 0 && (
          <Paper sx={{ p: 8, textAlign: 'center' }}>
            <TrendingUp sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" gutterBottom color="text.secondary">
              No posts collected yet
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              MTProto worker is collecting channel data automatically.
              Posts will appear here once data is available.
            </Typography>
          </Paper>
        )}

        {/* Posts View */}
        {!isLoading && posts.length > 0 && (
          <>
            {/* View Controls Header */}
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6" component="h2" sx={{ fontWeight: 600 }}>
                Posts
              </Typography>
              <PostsViewControls
                viewMode={viewMode}
                visibleColumns={columnVisibility.visibleColumns}
                visibleCount={columnVisibility.visibleCount}
                totalCount={columnVisibility.totalCount}
                onViewModeChange={setViewMode}
                onColumnToggle={columnVisibility.toggleColumn}
                onShowAllColumns={columnVisibility.showAllColumns}
                onHideAllColumns={columnVisibility.hideAllColumns}
              />
            </Box>

            {/* Table or Grid View */}
            {viewMode === 'table' ? (
              <PostsTable
                posts={posts}
                visibleColumns={columnVisibility.visibleColumns}
                formatDate={formatDate}
                getTelegramLink={getTelegramLink}
              />
            ) : (
              <PostsGrid
                posts={posts}
                formatDate={formatDate}
                getTelegramLink={getTelegramLink}
              />
            )}

            {/* Pagination */}
            {totalPages > 1 && (
              <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
                <Pagination
                  count={totalPages}
                  page={filters.page}
                  onChange={(_, value) => filters.setPage(value)}
                  color="primary"
                />
              </Box>
            )}
          </>
        )}
      </Box>
    </Container>
  );
};

export default PostsPage;
