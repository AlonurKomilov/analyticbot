/**
 * Worker MTProto Page
 * Unified page for MTProto management
 * Shows Monitoring/Dashboard if configured, Setup if not
 */

import React, { useEffect } from 'react';
import { Container, Box, CircularProgress, Typography } from '@mui/material';
import { useMTProtoStore } from '@/store/slices/mtproto/useMTProtoStore';
import { MTProtoSetupPage } from '@features/mtproto-setup';
import MTProtoMonitoringPage from '../MTProtoMonitoringPage';

export const WorkerMTProtoPage: React.FC = () => {
  const { status, isLoading, fetchStatus } = useMTProtoStore();

  // Fetch status on mount
  useEffect(() => {
    fetchStatus();
  }, [fetchStatus]);

  // Loading state
  if (isLoading && !status) {
    return (
      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 400 }}>
          <Box sx={{ textAlign: 'center' }}>
            <CircularProgress size={48} sx={{ mb: 2 }} />
            <Typography color="text.secondary">
              Loading MTProto status...
            </Typography>
          </Box>
        </Box>
      </Container>
    );
  }

  // If MTProto is verified and enabled, show monitoring page
  // Otherwise show setup page
  if (status?.verified) {
    return <MTProtoMonitoringPage />;
  }

  // Show setup page if not configured
  return <MTProtoSetupPage />;
};

export default WorkerMTProtoPage;
