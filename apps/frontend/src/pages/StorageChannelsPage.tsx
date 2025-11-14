/**
 * Storage Channels Settings Page
 * 
 * Page for managing Telegram storage channels configuration.
 * Users can connect/disconnect channels for zero-cost file storage.
 */

import React from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Alert,
  Stack
} from '@mui/material';
import { CloudQueue as StorageIcon } from '@mui/icons-material';
import { StorageChannelManager } from '@features/storage';

const StorageChannelsPage: React.FC = () => {
  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Page Header */}
      <Box sx={{ mb: 4 }}>
        <Stack direction="row" alignItems="center" spacing={1} mb={1}>
          <StorageIcon sx={{ fontSize: 32, color: 'primary.main' }} />
          <Typography variant="h4" component="h1">
            Storage Channels
          </Typography>
        </Stack>
        <Typography variant="body1" color="text.secondary">
          Connect your Telegram channels for zero-cost file hosting
        </Typography>
      </Box>

      {/* Info Banner */}
      <Alert severity="info" sx={{ mb: 3 }}>
        <Typography variant="body2">
          <strong>How it works:</strong> Upload files to your private Telegram channels 
          and use them in your posts. All files are stored in Telegram's cloud infrastructure 
          at no cost to you. Simply connect a channel where the bot has admin access.
        </Typography>
      </Alert>

      {/* Storage Channel Manager */}
      <Paper sx={{ p: 3 }}>
        <StorageChannelManager />
      </Paper>

      {/* Help Section */}
      <Paper sx={{ p: 2, mt: 3, bgcolor: 'grey.50' }}>
        <Typography variant="body2" color="text.secondary">
          💡 <strong>Need help?</strong> Make sure your bot has admin rights in the channel 
          with "Post Messages" permission. The channel can be private or public.
        </Typography>
      </Paper>
    </Container>
  );
};

export default StorageChannelsPage;
