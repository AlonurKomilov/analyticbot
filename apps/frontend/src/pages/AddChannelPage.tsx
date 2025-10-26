/**
 * Add Channel Page
 * Add a new channel to the platform
 */

import React, { useState } from 'react';
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
import { Add, ArrowBack } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { ROUTES } from '@config/routes';
import { useChannelStore } from '@store';

const AddChannelPage: React.FC = () => {
  const navigate = useNavigate();
  const { addChannel, isLoading } = useChannelStore();
  const [channelUsername, setChannelUsername] = useState('');
  const [description, setDescription] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSubmit = async () => {
    if (!channelUsername.trim()) {
      setError('Channel username is required');
      return;
    }

    if (!channelUsername.startsWith('@')) {
      setError('Channel username must start with @');
      return;
    }

    setError('');
    setSuccess(false);

    try {
      await addChannel({
        name: channelUsername.trim(),
        username: channelUsername.trim(),
        description: description.trim()
      });
      setSuccess(true);
      setTimeout(() => navigate(ROUTES.CHANNELS), 1500);
    } catch (err: any) {
      setError(err.message || 'Failed to add channel');
    }
  };

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Button
        startIcon={<ArrowBack />}
        onClick={() => navigate(ROUTES.CHANNELS)}
        sx={{ mb: 2 }}
      >
        Back to Channels
      </Button>

      <Paper sx={{ p: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Add New Telegram Channel
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {success && (
          <Alert severity="success" sx={{ mb: 3 }}>
            Channel added successfully! Redirecting...
          </Alert>
        )}

        <Box component="form" sx={{ mt: 3 }} onSubmit={(e) => { e.preventDefault(); handleSubmit(); }}>
          <TextField
            fullWidth
            label="Channel Username"
            placeholder="@your_channel_name"
            value={channelUsername}
            onChange={(e) => setChannelUsername(e.target.value)}
            sx={{ mb: 3 }}
            required
            helperText="Enter your Telegram channel username starting with @"
          />

          <TextField
            fullWidth
            label="Description (optional)"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            multiline
            rows={4}
            sx={{ mb: 3 }}
          />

          <Button
            variant="contained"
            startIcon={isLoading ? <CircularProgress size={20} color="inherit" /> : <Add />}
            onClick={handleSubmit}
            disabled={!channelUsername || isLoading}
            fullWidth
          >
            {isLoading ? 'Adding Channel...' : 'Add Channel'}
          </Button>
        </Box>
      </Paper>
    </Container>
  );
};

export default AddChannelPage;
