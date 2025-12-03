/**
 * ActionRequiredBanner Component
 *
 * Shows CRITICAL alerts that block core functionality.
 * Only critical setup issues appear here - warnings/info go to top bar notifications.
 * 
 * Critical alerts:
 * - Bot not configured
 * - MTProto not configured  
 * - No channels added
 * - Bot not admin in any channel
 * - Data collection disabled
 * - MTProto session expired
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Paper,
  Typography,
  Button,
  IconButton,
  Collapse,
  alpha,
  useTheme,
} from '@mui/material';
import {
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  Close as CloseIcon,
  ArrowForward as ArrowIcon,
  ReportProblem as CriticalIcon,
} from '@mui/icons-material';

export interface ActionAlert {
  id: string;
  type: 'critical' | 'error' | 'warning' | 'info';
  title: string;
  description: string;
  action_url?: string;
  action_label?: string;
  channel_id?: number;
}

interface ActionRequiredBannerProps {
  alerts: ActionAlert[];
  onDismiss?: (alertId: string) => void;
}

const ActionRequiredBanner: React.FC<ActionRequiredBannerProps> = ({ alerts, onDismiss }) => {
  const theme = useTheme();
  const navigate = useNavigate();
  const [dismissedAlerts, setDismissedAlerts] = React.useState<Set<string>>(new Set());

  const visibleAlerts = alerts.filter(a => !dismissedAlerts.has(a.id));

  if (visibleAlerts.length === 0) return null;

  const handleDismiss = (alertId: string) => {
    setDismissedAlerts(prev => new Set([...prev, alertId]));
    onDismiss?.(alertId);
  };

  const getAlertConfig = (type: string) => {
    switch (type) {
      case 'critical':
        return {
          icon: <CriticalIcon />,
          color: '#f44336', // Strong red for critical
          bgColor: alpha('#f44336', 0.12),
          borderWidth: 4,
        };
      case 'error':
        return {
          icon: <ErrorIcon />,
          color: theme.palette.error.main,
          bgColor: alpha(theme.palette.error.main, 0.1),
          borderWidth: 4,
        };
      case 'warning':
        return {
          icon: <WarningIcon />,
          color: theme.palette.warning.main,
          bgColor: alpha(theme.palette.warning.main, 0.1),
          borderWidth: 3,
        };
      default:
        return {
          icon: <InfoIcon />,
          color: theme.palette.info.main,
          bgColor: alpha(theme.palette.info.main, 0.1),
          borderWidth: 3,
        };
    }
  };

  return (
    <Box sx={{ mb: 3 }}>
      {visibleAlerts.map((alert) => {
        const config = getAlertConfig(alert.type);
        const isCritical = alert.type === 'critical';

        return (
          <Collapse key={alert.id} in={!dismissedAlerts.has(alert.id)}>
            <Paper
              elevation={isCritical ? 2 : 0}
              sx={{
                p: 2,
                mb: 1.5,
                display: 'flex',
                alignItems: 'center',
                gap: 2,
                backgroundColor: config.bgColor,
                borderLeft: `${config.borderWidth}px solid ${config.color}`,
                ...(isCritical && {
                  animation: 'pulse 2s ease-in-out infinite',
                  '@keyframes pulse': {
                    '0%, 100%': { boxShadow: `0 0 0 0 ${alpha(config.color, 0.4)}` },
                    '50%': { boxShadow: `0 0 0 4px ${alpha(config.color, 0.1)}` },
                  },
                }),
              }}
            >
              <Box sx={{ color: config.color, display: 'flex', alignItems: 'center' }}>
                {config.icon}
              </Box>

              <Box sx={{ flex: 1 }}>
                <Typography 
                  variant="subtitle2" 
                  fontWeight={isCritical ? 700 : 600} 
                  color={config.color}
                  sx={{ textTransform: isCritical ? 'uppercase' : 'none', letterSpacing: isCritical ? 0.5 : 0 }}
                >
                  {alert.title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {alert.description}
                </Typography>
              </Box>

              {alert.action_url && (
                <Button
                  variant={isCritical ? "contained" : "outlined"}
                  size="small"
                  endIcon={<ArrowIcon />}
                  onClick={() => navigate(alert.action_url!)}
                  sx={{
                    ...(isCritical ? {
                      backgroundColor: config.color,
                      color: '#fff',
                      '&:hover': {
                        backgroundColor: alpha(config.color, 0.85),
                      },
                    } : {
                      borderColor: config.color,
                      color: config.color,
                      '&:hover': {
                        borderColor: config.color,
                        backgroundColor: alpha(config.color, 0.1),
                      },
                    }),
                  }}
                >
                  {alert.action_label || 'View'}
                </Button>
              )}

              {/* Critical alerts shouldn't be dismissable easily */}
              {!isCritical && (
                <IconButton
                  size="small"
                  onClick={() => handleDismiss(alert.id)}
                  sx={{ color: 'text.secondary' }}
                >
                  <CloseIcon fontSize="small" />
                </IconButton>
              )}
            </Paper>
          </Collapse>
        );
      })}
    </Box>
  );
};

export default ActionRequiredBanner;
