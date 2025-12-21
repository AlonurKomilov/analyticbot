/**
 * AI Status Card Component
 * Shows AI configuration status, tier, and usage
 */

import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  LinearProgress,
  Skeleton,
  alpha,
  useTheme,
} from '@mui/material';
import {
  Psychology as AIIcon,
  CheckCircle as EnabledIcon,
  Cancel as DisabledIcon,
  Bolt as BoltIcon,
} from '@mui/icons-material';
import type { AIStatus } from '../../types';

interface AIStatusCardProps {
  status: AIStatus | null;
  isLoading: boolean;
}

const getTierColor = (tier: string): string => {
  switch (tier) {
    case 'enterprise': return '#FFD700';
    case 'pro': return '#9C27B0';
    case 'basic': return '#2196F3';
    default: return '#757575';
  }
};

const getTierLabel = (tier: string): string => {
  switch (tier) {
    case 'enterprise': return 'Enterprise';
    case 'pro': return 'Pro';
    case 'basic': return 'Basic';
    default: return 'Free';
  }
};

export const AIStatusCard: React.FC<AIStatusCardProps> = ({ status, isLoading }) => {
  const theme = useTheme();

  if (isLoading) {
    return (
      <Card
        sx={{
          background: `linear-gradient(135deg, ${alpha('#9C27B0', 0.1)} 0%, ${alpha('#673AB7', 0.1)} 100%)`,
          border: `1px solid ${alpha('#9C27B0', 0.3)}`,
        }}
      >
        <CardContent>
          <Skeleton variant="text" width={150} height={32} />
          <Box sx={{ mt: 2 }}>
            <Skeleton variant="rounded" height={80} />
          </Box>
        </CardContent>
      </Card>
    );
  }

  if (!status) {
    return (
      <Card
        sx={{
          background: `linear-gradient(135deg, ${alpha(theme.palette.error.main, 0.1)} 0%, ${alpha(theme.palette.error.dark, 0.1)} 100%)`,
          border: `1px solid ${alpha(theme.palette.error.main, 0.3)}`,
        }}
      >
        <CardContent>
          <Box display="flex" alignItems="center" gap={1} mb={2}>
            <AIIcon sx={{ color: theme.palette.error.main }} />
            <Typography variant="h6">AI Not Available</Typography>
          </Box>
          <Typography color="text.secondary">
            Unable to load AI status. Please try again.
          </Typography>
        </CardContent>
      </Card>
    );
  }

  const usagePercentage = status.usage_limit > 0 
    ? (status.usage_today / status.usage_limit) * 100 
    : 0;

  const tierColor = getTierColor(status.tier);

  return (
    <Card
      sx={{
        background: `linear-gradient(135deg, ${alpha('#9C27B0', 0.15)} 0%, ${alpha('#673AB7', 0.1)} 100%)`,
        border: `1px solid ${alpha('#9C27B0', 0.3)}`,
        height: '100%',
      }}
    >
      <CardContent>
        {/* Header */}
        <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
          <Box display="flex" alignItems="center" gap={2}>
            <Box
              sx={{
                width: 56,
                height: 56,
                borderRadius: 2,
                background: `linear-gradient(135deg, #9C27B0 0%, #673AB7 100%)`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <AIIcon sx={{ color: 'white', fontSize: 32 }} />
            </Box>
            <Box>
              <Typography variant="h6" fontWeight={700}>
                AI Assistant
              </Typography>
              <Typography variant="caption" color="text.secondary">
                AI-powered analytics and insights
              </Typography>
            </Box>
          </Box>
          <Box display="flex" alignItems="center" gap={1}>
            <Chip
              label={getTierLabel(status.tier)}
              size="small"
              sx={{
                backgroundColor: alpha(tierColor, 0.2),
                color: tierColor,
                fontWeight: 600,
                borderRadius: 1,
              }}
            />
            {status.enabled ? (
              <Chip
                icon={<EnabledIcon sx={{ fontSize: 16 }} />}
                label="Enabled"
                size="small"
                color="success"
                variant="outlined"
              />
            ) : (
              <Chip
                icon={<DisabledIcon sx={{ fontSize: 16 }} />}
                label="Disabled"
                size="small"
                color="error"
                variant="outlined"
              />
            )}
          </Box>
        </Box>

        {/* Usage Stats */}
        <Box
          sx={{
            mt: 3,
            p: 2,
            borderRadius: 2,
            backgroundColor: alpha(theme.palette.background.paper, 0.5),
          }}
        >
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
            <Box display="flex" alignItems="center" gap={1}>
              <BoltIcon sx={{ color: '#FFD700', fontSize: 20 }} />
              <Typography variant="body2" fontWeight={500}>
                Daily Usage
              </Typography>
            </Box>
            <Typography variant="body2" fontWeight={600}>
              {status.usage_today} / {status.usage_limit} requests
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={Math.min(usagePercentage, 100)}
            sx={{
              height: 8,
              borderRadius: 1,
              backgroundColor: alpha('#9C27B0', 0.2),
              '& .MuiLinearProgress-bar': {
                borderRadius: 1,
                background: usagePercentage > 80 
                  ? `linear-gradient(90deg, #f44336 0%, #e91e63 100%)`
                  : `linear-gradient(90deg, #9C27B0 0%, #673AB7 100%)`,
              },
            }}
          />
          <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
            {status.remaining_requests} requests remaining today
          </Typography>
        </Box>

        {/* Features Enabled */}
        {status.features_enabled.length > 0 && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="caption" color="text.secondary" gutterBottom display="block">
              Enabled Features
            </Typography>
            <Box display="flex" flexWrap="wrap" gap={0.5}>
              {status.features_enabled.slice(0, 4).map((feature) => (
                <Chip
                  key={feature}
                  label={feature.replace(/_/g, ' ')}
                  size="small"
                  variant="outlined"
                  sx={{ 
                    fontSize: '0.7rem',
                    textTransform: 'capitalize',
                  }}
                />
              ))}
              {status.features_enabled.length > 4 && (
                <Chip
                  label={`+${status.features_enabled.length - 4} more`}
                  size="small"
                  variant="outlined"
                  sx={{ fontSize: '0.7rem' }}
                />
              )}
            </Box>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default AIStatusCard;
