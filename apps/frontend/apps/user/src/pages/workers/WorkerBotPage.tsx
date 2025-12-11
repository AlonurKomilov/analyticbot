/**
 * Worker Bot Page
 * Unified page for Bot management
 * Shows Dashboard if configured, Setup if not
 */

import React, { useEffect, useRef, useState } from 'react';
import { Container, Box, CircularProgress, Typography } from '@mui/material';
import { UserBotDashboard, BotSetupWizard } from '@features/bot';
import { useUserBotStore } from '@/store';

export const WorkerBotPage: React.FC = () => {
  const { bot, isLoading, fetchBotStatus } = useUserBotStore();
  
  // Track if we've completed the initial status check
  const hasCheckedRef = useRef(false);
  const [hasChecked, setHasChecked] = useState(false);
  
  // Fetch bot status on mount (only once)
  useEffect(() => {
    const checkBotStatus = async () => {
      // Skip if already checked or currently loading
      if (hasCheckedRef.current || isLoading) {
        return;
      }
      
      hasCheckedRef.current = true;
      
      try {
        await fetchBotStatus();
      } catch (err) {
        // 404 = no bot configured, this is expected for new users
        console.log('No bot configured yet');
      } finally {
        setHasChecked(true);
      }
    };
    
    checkBotStatus();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Loading state - show spinner until we've completed the initial check
  if (!hasChecked && (isLoading || !hasCheckedRef.current)) {
    return (
      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 400 }}>
          <Box sx={{ textAlign: 'center' }}>
            <CircularProgress size={48} sx={{ mb: 2 }} />
            <Typography color="text.secondary">
              Loading bot status...
            </Typography>
          </Box>
        </Box>
      </Container>
    );
  }
  
  // If bot is configured, show dashboard
  // If not, show setup wizard
  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {bot ? <UserBotDashboard /> : <BotSetupWizard />}
    </Container>
  );
};

export default WorkerBotPage;
