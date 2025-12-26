/**
 * AI Settings Card Component
 * Shows and allows editing of AI configuration settings
 */

import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Skeleton,
  alpha,
  useTheme,
  IconButton,
  Tooltip,
  Divider,
} from '@mui/material';
import {
  Settings as SettingsIcon,
  Tune as TuneIcon,
  Speed as SpeedIcon,
  Timer as TimerIcon,
  Storage as TokenIcon,
  LiveTv as ChannelIcon,
} from '@mui/icons-material';
import type { AISettings, AILimits } from '../../types';

interface AISettingsCardProps {
  settings: AISettings | null;
  limits: AILimits | null;
  isLoading: boolean;
  onOpenSettings?: () => void;
}

interface StatItemProps {
  icon: React.ReactElement;
  label: string;
  value: string | number;
  color?: string;
}

const StatItem: React.FC<StatItemProps> = ({ icon, label, value, color }) => {
  const theme = useTheme();
  const iconColor = color || theme.palette.primary.main;
  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        gap: 2,
        py: 1,
      }}
    >
      <Box
        sx={{
          width: 40,
          height: 40,
          borderRadius: 1.5,
          backgroundColor: alpha(iconColor, 0.15),
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: iconColor,
        }}
      >
        {icon}
      </Box>
      <Box sx={{ flex: 1 }}>
        <Typography variant="caption" color="text.secondary" textTransform="uppercase" letterSpacing={0.5} display="block">
          {label}
        </Typography>
        <Typography variant="h6" fontWeight={600}>
          {value}
        </Typography>
      </Box>
    </Box>
  );
};

export const AISettingsCard: React.FC<AISettingsCardProps> = ({
  settings,
  limits,
  isLoading,
  onOpenSettings,
}) => {
  const theme = useTheme();

  if (isLoading) {
    return (
      <Card
        sx={{
          background: `linear-gradient(135deg, ${alpha('#00BCD4', 0.1)} 0%, ${alpha('#009688', 0.1)} 100%)`,
          border: `1px solid ${alpha('#00BCD4', 0.3)}`,
        }}
      >
        <CardContent>
          <Skeleton variant="text" width={180} height={32} />
          <Box sx={{ mt: 2 }}>
            {[1, 2, 3, 4].map((i) => (
              <Skeleton key={i} variant="rounded" height={48} sx={{ mb: 1 }} />
            ))}
          </Box>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card
      sx={{
        background: `linear-gradient(135deg, ${alpha('#00BCD4', 0.1)} 0%, ${alpha('#009688', 0.1)} 100%)`,
        border: `1px solid ${alpha('#00BCD4', 0.3)}`,
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
                background: `linear-gradient(135deg, #00BCD4 0%, #009688 100%)`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <SettingsIcon sx={{ color: 'white', fontSize: 32 }} />
            </Box>
            <Box>
              <Typography variant="h6" fontWeight={700}>
                Configuration & Limits
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Your AI tier limits and settings
              </Typography>
            </Box>
          </Box>
          {onOpenSettings && (
            <Tooltip title="Edit Settings">
              <IconButton onClick={onOpenSettings} size="small">
                <TuneIcon />
              </IconButton>
            </Tooltip>
          )}
        </Box>

        <Divider sx={{ my: 2, opacity: 0.5 }} />

        {/* Limits */}
        {limits ? (
          <Box>
            <StatItem
              icon={<SpeedIcon />}
              label="REQUESTS PER DAY"
              value={limits.requests_per_day}
              color="#00BCD4"
            />
            <StatItem
              icon={<TimerIcon />}
              label="REQUESTS PER HOUR"
              value={limits.requests_per_hour}
              color="#009688"
            />
            <StatItem
              icon={<TokenIcon />}
              label="MAX TOKENS"
              value={limits.max_tokens.toLocaleString()}
              color="#4CAF50"
            />
            <StatItem
              icon={<ChannelIcon />}
              label="MAX CHANNELS"
              value={limits.max_channels}
              color="#FF9800"
            />
          </Box>
        ) : (
          <Box sx={{ py: 2, textAlign: 'center' }}>
            <Typography variant="body2" color="text.secondary">
              No tier limits configured
            </Typography>
          </Box>
        )}

        {/* Settings Summary */}
        {settings && (
          <Box
            sx={{
              mt: 2,
              p: 1.5,
              borderRadius: 2,
              backgroundColor: alpha(theme.palette.background.paper, 0.5),
            }}
          >
            <Typography variant="caption" color="text.secondary" gutterBottom display="block">
              Current Model: <strong>{settings.preferred_model || 'Default'}</strong>
            </Typography>
            <Typography variant="caption" color="text.secondary" display="block">
              Auto-Insights: <strong>{settings.auto_insights_enabled ? 'Enabled' : 'Disabled'}</strong>
              {settings.auto_insights_enabled && ` (${settings.auto_insights_frequency})`}
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default AISettingsCard;
