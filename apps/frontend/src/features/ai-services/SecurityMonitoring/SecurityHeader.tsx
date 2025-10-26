/**
 * Security Header Component
 * Displays service title and status
 */

import React from 'react';
import { Box, Typography, Chip } from '@mui/material';
import SecurityIcon from '@mui/icons-material/Security';

interface SecurityHeaderProps {
  status: 'excellent' | 'good' | 'needs-attention' | 'poor';
}

export const SecurityHeader: React.FC<SecurityHeaderProps> = ({ status }) => {
  const statusConfig = {
    excellent: { label: 'Excellent', color: 'success' as const },
    good: { label: 'Active', color: 'success' as const },
    'needs-attention': { label: 'Needs Attention', color: 'warning' as const },
    poor: { label: 'Critical', color: 'error' as const }
  };

  const currentStatus = statusConfig[status] || statusConfig.good;

  return (
    <Box sx={{ mb: 4 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
        <SecurityIcon sx={{ fontSize: 32, color: 'primary.main' }} />
        <Typography variant="h4" component="h1" fontWeight={600}>
          Security Monitoring
        </Typography>
        <Chip
          label={currentStatus.label}
          color={currentStatus.color}
          variant="filled"
          sx={{ ml: 'auto' }}
        />
      </Box>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Real-time security analysis and threat detection for comprehensive platform protection
      </Typography>
    </Box>
  );
};

export default SecurityHeader;
