/**
 * Edit Post Page
 * Edit an existing post (text content only - Telegram posts don't have separate title/status)
 */

import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  TextField,
  Button,
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

  const [text, setText] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  // Load post data
  useEffect(() => {
    if (id && posts.length > 0) {
      // Post.id can be string or number, handle both
      const post = posts.find(p => String(p.id) === id);
      if (post) {
        // Post type has [key: string]: any, so text access is safe
        setText((post as any).text || '');
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

    if (!text.trim()) {
      setError('Content cannot be empty');
      return;
    }

    setSaving(true);
    setError(null);

    try {
      // Post type allows any properties via [key: string]: any
      await updatePost(id, { text } as any);

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
            label="Post Content"
            value={text}
            onChange={(e) => setText(e.target.value)}
            multiline
            rows={10}
            sx={{ mb: 3 }}
            required
            disabled={saving}
            error={!text.trim() && !!error}
            helperText={!text.trim() && !!error ? 'Content is required' : ''}
          />

          <Button
            variant="contained"
            startIcon={saving ? <CircularProgress size={20} /> : <Save />}
            onClick={handleSave}
            disabled={saving || !text.trim()}
          >
            {saving ? 'Saving...' : 'Save Changes'}
          </Button>
        </Box>
      </Paper>
    </Container>
  );
};

export default EditPostPage;
