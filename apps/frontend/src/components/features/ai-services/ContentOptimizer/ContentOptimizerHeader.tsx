/**
 * Content Optimizer Header Component
 * Displays service title, description, and status badge
 */

import React from 'react';
import { Box, Typography, Chip } from '@mui/material';
import OptimizeIcon from '@mui/icons-material/AutoFixHigh';

interface ContentOptimizerHeaderProps {
  status: 'active' | 'inactive' | 'error';
  onOptimize?: () => void;
  isOptimizing?: boolean;
}

export const ContentOptimizerHeader: React.FC<ContentOptimizerHeaderProps> = ({
  status
}) => {
  const statusConfig = {
    active: { label: 'Active', color: 'success' as const },
    inactive: { label: 'Inactive', color: 'default' as const },
    error: { label: 'Error', color: 'error' as const }
  };

  const currentStatus = statusConfig[status] || statusConfig.inactive;

  return (
    <Box sx={{ mb: 5 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <Box
          sx={{
            p: 2,
            borderRadius: 3,
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            mr: 3
          }}
        >
          <OptimizeIcon sx={{ fontSize: 40 }} />
        </Box>
        <Box sx={{ flexGrow: 1 }}>
          <Typography variant="h3" component="h1" fontWeight={700} sx={{ mb: 0.5 }}>
            Content Optimizer
          </Typography>
          <Typography variant="h6" color="text.secondary" sx={{ fontWeight: 400 }}>
            AI-powered content enhancement for maximum engagement and performance
          </Typography>
        </Box>
        <Chip
          label={currentStatus.label}
          color={currentStatus.color}
          variant="filled"
          sx={{
            fontWeight: 600,
            fontSize: '0.9rem',
            height: 36,
            boxShadow: status === 'active' ? '0 4px 12px rgba(76, 175, 80, 0.3)' : 'none'
          }}
        />
      </Box>
    </Box>
  );
};

export default ContentOptimizerHeader;
