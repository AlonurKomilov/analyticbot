/**
 * Posts Page - Unified post management
 * Shows all posts from MTProto collection (real channel data)
 */

import React, { useEffect, useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress,
  Alert,
  Pagination,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
} from '@mui/material';
import { TrendingUp, Visibility, Reply, Share } from '@mui/icons-material';
import { useChannelStore } from '@store';
import { apiClient } from '@api/client';

// MTProto Post interface - matches backend PostResponse
interface PostMetrics {
  views: number;
  forwards: number;
  replies_count: number;
  reactions_count: number;
  snapshot_time?: string;
}

interface Post {
  id: number;
  channel_id: number;
  msg_id: number;
  date: string;
  text: string;
  created_at: string;
  updated_at: string;
  metrics?: PostMetrics;
  channel_name?: string;
}

interface PostsResponse {
  posts: Post[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
}

const PostsPage: React.FC = () => {
  const [posts, setPosts] = useState<Post[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [selectedChannel, setSelectedChannel] = useState<number | 'all'>('all');
  const { channels } = useChannelStore();
  const pageSize = 50;

  const fetchPosts = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const params: any = { page, page_size: pageSize };
      if (selectedChannel !== 'all') {
        params.channel_id = selectedChannel;
      }
      
      const response = await apiClient.get<PostsResponse>('/api/posts', { params });
      setPosts(response.posts);
      setTotal(response.total);
      setTotalPages(Math.ceil(response.total / pageSize));
    } catch (err: any) {
      console.error('Error fetching posts:', err);
      setError(err.response?.data?.detail || 'Failed to fetch posts');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchPosts();
  }, [page, selectedChannel]);

  const formatDate = (date: string) => {
    if (!date) return '-';
    return new Date(date).toLocaleString();
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        {/* Header */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            All Posts
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Real-time posts collected from your Telegram channels via MTProto
          </Typography>
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

        {/* Channel Filter */}
        <Box sx={{ mb: 3, display: 'flex', gap: 2, alignItems: 'center' }}>
          <FormControl sx={{ minWidth: 200 }}>
            <InputLabel>Filter by Channel</InputLabel>
            <Select
              value={selectedChannel}
              label="Filter by Channel"
              onChange={(e) => {
                setSelectedChannel(e.target.value as number | 'all');
                setPage(1);
              }}
            >
              <MenuItem value="all">All Channels</MenuItem>
              {channels.map((channel: any) => (
                <MenuItem key={channel.id} value={channel.id}>
                  {channel.title || channel.username || channel.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <Typography variant="body2" color="text.secondary">
            Total: {total} posts
          </Typography>
        </Box>

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

        {/* Posts Table */}
        {!isLoading && posts.length > 0 && (
          <>
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Date</TableCell>
                    <TableCell>Channel</TableCell>
                    <TableCell>Message ID</TableCell>
                    <TableCell>Content</TableCell>
                    <TableCell align="right">Views</TableCell>
                    <TableCell align="right">Forwards</TableCell>
                    <TableCell align="right">Replies</TableCell>
                    <TableCell align="right">Reactions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {posts.map((post) => (
                    <TableRow key={`${post.channel_id}-${post.msg_id}`} hover>
                      <TableCell>
                        <Typography variant="body2">{formatDate(post.date)}</Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" fontWeight="medium">
                          {post.channel_name || `Channel ${post.channel_id}`}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" color="text.secondary">
                          {post.msg_id}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography
                          variant="body2"
                          sx={{
                            maxWidth: 400,
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap',
                          }}
                        >
                          {post.text || '(Media post)'}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 0.5 }}>
                          <Visibility fontSize="small" color="action" />
                          <Typography variant="body2">{post.metrics?.views || 0}</Typography>
                        </Box>
                      </TableCell>
                      <TableCell align="right">
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 0.5 }}>
                          <Share fontSize="small" color="action" />
                          <Typography variant="body2">{post.metrics?.forwards || 0}</Typography>
                        </Box>
                      </TableCell>
                      <TableCell align="right">
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 0.5 }}>
                          <Reply fontSize="small" color="action" />
                          <Typography variant="body2">{post.metrics?.replies_count || 0}</Typography>
                        </Box>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2">{post.metrics?.reactions_count || 0}</Typography>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>

            {/* Pagination */}
            {totalPages > 1 && (
              <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
                <Pagination
                  count={totalPages}
                  page={page}
                  onChange={(_, value) => setPage(value)}
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
