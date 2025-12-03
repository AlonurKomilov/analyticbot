/**
 * ActionRequiredBanner Component
 *
 * Shows urgent alerts that need user attention at the top of dashboard.
 * Examples: bot not admin, sync failures, pending posts for review
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
} from '@mui/icons-material';

export interface ActionAlert {
  id: string;
  type: 'error' | 'warning' | 'info';
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
      case 'error':
        return {
          icon: <ErrorIcon />,
          color: theme.palette.error.main,
          bgColor: alpha(theme.palette.error.main, 0.1),
        };
      case 'warning':
        return {
          icon: <WarningIcon />,
          color: theme.palette.warning.main,
          bgColor: alpha(theme.palette.warning.main, 0.1),
        };
      default:
        return {
          icon: <InfoIcon />,
          color: theme.palette.info.main,
          bgColor: alpha(theme.palette.info.main, 0.1),
        };
    }
  };

  return (
    <Box sx={{ mb: 3 }}>
      {visibleAlerts.map((alert) => {
        const config = getAlertConfig(alert.type);

        return (
          <Collapse key={alert.id} in={!dismissedAlerts.has(alert.id)}>
            <Paper
              sx={{
                p: 2,
                mb: 1.5,
                display: 'flex',
                alignItems: 'center',
                gap: 2,
                backgroundColor: config.bgColor,
                borderLeft: `4px solid ${config.color}`,
              }}
            >
              <Box sx={{ color: config.color }}>
                {config.icon}
              </Box>

              <Box sx={{ flex: 1 }}>
                <Typography variant="subtitle2" fontWeight="600" color={config.color}>
                  {alert.title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {alert.description}
                </Typography>
              </Box>

              {alert.action_url && (
                <Button
                  variant="outlined"
                  size="small"
                  endIcon={<ArrowIcon />}
                  onClick={() => navigate(alert.action_url!)}
                  sx={{
                    borderColor: config.color,
                    color: config.color,
                    '&:hover': {
                      borderColor: config.color,
                      backgroundColor: alpha(config.color, 0.1),
                    },
                  }}
                >
                  {alert.action_label || 'View'}
                </Button>
              )}

              <IconButton
                size="small"
                onClick={() => handleDismiss(alert.id)}
                sx={{ color: 'text.secondary' }}
              >
                <CloseIcon fontSize="small" />
              </IconButton>
            </Paper>
          </Collapse>
        );
      })}
    </Box>
  );
};

export default ActionRequiredBanner;
