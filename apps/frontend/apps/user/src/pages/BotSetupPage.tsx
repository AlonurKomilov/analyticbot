/**
 * Bot Setup Page
 * Page wrapper for Bot Setup Wizard
 */

import React, { useEffect, useRef, useState } from 'react';
import { Container, Box, CircularProgress, Typography } from '@mui/material';
import { BotSetupWizard } from '@features/bot';
import { useUserBotStore } from '@/store';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';

export const BotSetupPage: React.FC = () => {
  const navigate = useNavigate();
  const { bot, isLoading, fetchBotStatus } = useUserBotStore();
  
  // Track if we've completed the initial status check
  const hasCheckedRef = useRef(false);
  const [hasChecked, setHasChecked] = useState(false);
  
  // Check bot status on mount
  useEffect(() => {
    const checkBotStatus = async () => {
      if (hasCheckedRef.current || isLoading) {
        return;
      }
      
      hasCheckedRef.current = true;
      
      try {
        const fetchedBot = await fetchBotStatus();
        if (fetchedBot) {
          // User already has a bot, redirect to dashboard
          toast.success('✅ You already have a bot configured! Redirecting to dashboard...', {
            duration: 3000,
          });
          setTimeout(() => {
            navigate('/bot/dashboard');
          }, 2000);
        }
      } catch (err) {
        // 404 = no bot configured, this is expected
        console.log('No bot configured yet, showing setup wizard');
      } finally {
        setHasChecked(true);
      }
    };
    
    checkBotStatus();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  
  // Loading state
  if (!hasChecked) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 400 }}>
          <Box sx={{ textAlign: 'center' }}>
            <CircularProgress size={48} sx={{ mb: 2 }} />
            <Typography color="text.secondary">
              Checking bot status...
            </Typography>
          </Box>
        </Box>
      </Container>
    );
  }
  
  // If bot exists, don't show setup (redirect will happen via useEffect)
  if (bot) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 400 }}>
          <Box sx={{ textAlign: 'center' }}>
            <CircularProgress size={48} sx={{ mb: 2 }} />
            <Typography color="text.secondary">
              Redirecting to dashboard...
            </Typography>
          </Box>
        </Box>
      </Container>
    );
  }
  
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <BotSetupWizard />
    </Container>
  );
};

export default BotSetupPage;
