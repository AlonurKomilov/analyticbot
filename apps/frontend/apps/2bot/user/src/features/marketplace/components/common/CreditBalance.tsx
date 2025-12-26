/**
 * Credit Balance Component
 *
 * Displays user's credit balance with refresh and buy buttons.
 * 
 * @module features/marketplace/components/common/CreditBalance
 */

import React from 'react';
import { Card, CardContent, Box, Typography, Button, IconButton } from '@mui/material';
import { MonetizationOn as CreditsIcon, Refresh as RefreshIcon } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { ROUTES } from '@/config/routes';

interface CreditBalanceProps {
  balance: number;
  onRefresh: () => void;
  refreshing?: boolean;
}

export const CreditBalance: React.FC<CreditBalanceProps> = ({
  balance,
  onRefresh,
  refreshing = false,
}) => {
  const navigate = useNavigate();

  return (
    <Card
      sx={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        mb: 4,
      }}
    >
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <CreditsIcon sx={{ fontSize: 40, color: '#FFD700' }} />
            <Box>
              <Typography variant="h5" sx={{ fontWeight: 600 }}>
                {balance.toLocaleString()} Credits
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.9 }}>
                Your balance
              </Typography>
            </Box>
          </Box>
          <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
            <IconButton
              onClick={onRefresh}
              disabled={refreshing}
              sx={{ color: 'white' }}
              size="small"
            >
              <RefreshIcon sx={{ animation: refreshing ? 'spin 1s linear infinite' : 'none' }} />
            </IconButton>
            <Button
              variant="contained"
              onClick={() => navigate(ROUTES.CREDITS)}
              sx={{
                bgcolor: '#FFD700',
                color: '#000',
                fontWeight: 600,
                '&:hover': { bgcolor: '#FFC700' },
              }}
            >
              Buy Credits
            </Button>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};
