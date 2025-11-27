/**
 * Edit Post Page
 * Edit an existing post
 */

import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  CircularProgress,
} from '@mui/material';
import { Save, ArrowBack } from '@mui/icons-material';
import { useNavigate, useParams } from 'react-router-dom';
import { ROUTES } from '@config/routes';
import { usePostStore } from '@store';
import { uiLogger } from '@/utils/logger';

const EditPostPage: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();

  const { posts, updatePost, isLoading } = usePostStore();
  
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [status, setStatus] = useState('draft');
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  // Load post data
  useEffect(() => {
    if (id && posts.length > 0) {
      const post = posts.find(p => p.id === id);
      if (post) {
        setTitle(post.title || '');
        setContent(post.content || '');
        setStatus(post.status || 'draft');
      } else {
        setError('Post not found');
      }
    }
  }, [id, posts]);

  const handleSave = async () => {
    if (!id) {
      setError('No post ID provided');
      return;
    }

    if (!content.trim()) {
      setError('Content cannot be empty');
      return;
    }

    setSaving(true);
    setError(null);

    try {
      await updatePost(id, {
        title,
        content,
        status: status as any,
      });
      
      uiLogger.debug('Post updated successfully', { postId: id });
      navigate(ROUTES.POSTS);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to update post';
      setError(errorMessage);
      uiLogger.error('Failed to update post', { error: err, postId: id });
    } finally {
      setSaving(false);
    }
  };

  if (isLoading) {
    return (
      <Container maxWidth="md" sx={{ py: 4, display: 'flex', justifyContent: 'center' }}>
        <CircularProgress />
      </Container>
    );
  }

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Button
        startIcon={<ArrowBack />}
        onClick={() => navigate(ROUTES.POSTS)}
        sx={{ mb: 2 }}
      >
        Back to Posts
      </Button>

      <Paper sx={{ p: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Edit Post
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        <Box component="form" sx={{ mt: 3 }}>
          <TextField
            fullWidth
            label="Title (optional)"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            sx={{ mb: 3 }}
            disabled={saving}
          />

          <TextField
            fullWidth
            label="Content"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            multiline
            rows={10}
            sx={{ mb: 3 }}
            required
            disabled={saving}
            error={!content.trim() && !!error}
            helperText={!content.trim() && !!error ? 'Content is required' : ''}
          />

          <FormControl fullWidth sx={{ mb: 3 }}>
            <InputLabel>Status</InputLabel>
            <Select
              value={status}
              label="Status"
              onChange={(e) => setStatus(e.target.value)}
              disabled={saving}
            >
              <MenuItem value="draft">Draft</MenuItem>
              <MenuItem value="published">Published</MenuItem>
              <MenuItem value="scheduled">Scheduled</MenuItem>
            </Select>
          </FormControl>

          <Button
            variant="contained"
            startIcon={saving ? <CircularProgress size={20} /> : <Save />}
            onClick={handleSave}
            disabled={saving || !content.trim()}
          >
            {saving ? 'Saving...' : 'Save Changes'}
          </Button>
        </Box>
      </Paper>
    </Container>
  );
};

export default EditPostPage;
