/**
 * QuickActionsPanel Component
 *
 * Shows contextual quick actions based on user's current state.
 * Actions change based on whether user has channels, bot, MTProto etc.
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Paper,
  Typography,
  Button,
  alpha,
  useTheme,
} from '@mui/material';
import {
  AddCircle as AddIcon,
  SmartToy as BotIcon,
  Analytics as AnalyticsIcon,
  Edit as EditIcon,
  Settings as SettingsIcon,
  BarChart as ChartIcon,
  Schedule as ScheduleIcon,
} from '@mui/icons-material';

export interface QuickAction {
  id: string;
  title: string;
  description: string;
  icon: string;
  url: string;
  priority: number;
}

interface QuickActionsPanelProps {
  actions: QuickAction[];
  hasChannels: boolean;
}

const QuickActionsPanel: React.FC<QuickActionsPanelProps> = ({ actions, hasChannels }) => {
  const theme = useTheme();
  const navigate = useNavigate();

  const getIcon = (iconName: string) => {
    switch (iconName) {
      case 'add_circle':
        return <AddIcon />;
      case 'smart_toy':
        return <BotIcon />;
      case 'analytics':
        return <AnalyticsIcon />;
      case 'edit':
        return <EditIcon />;
      case 'bar_chart':
        return <ChartIcon />;
      case 'settings':
        return <SettingsIcon />;
      case 'schedule':
        return <ScheduleIcon />;
      default:
        return <AddIcon />;
    }
  };

  const getColor = (iconName: string) => {
    switch (iconName) {
      case 'add_circle':
        return theme.palette.primary.main;
      case 'smart_toy':
        return theme.palette.secondary.main;
      case 'analytics':
        return theme.palette.info.main;
      case 'edit':
        return theme.palette.success.main;
      case 'bar_chart':
        return theme.palette.warning.main;
      case 'settings':
        return theme.palette.grey[600];
      default:
        return theme.palette.primary.main;
    }
  };

  // If no channels and no actions, show onboarding
  if (!hasChannels && actions.length === 0) {
    return (
      <Paper
        sx={{
          p: 4,
          textAlign: 'center',
          background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.05)} 0%, ${alpha(theme.palette.primary.main, 0.02)} 100%)`,
          border: `2px dashed ${alpha(theme.palette.primary.main, 0.3)}`,
        }}
      >
        <AddIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
        <Typography variant="h6" fontWeight="bold" gutterBottom>
          Get Started with AnalyticBot
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3, maxWidth: 400, mx: 'auto' }}>
          Add your first Telegram channel to start tracking analytics,
          engagement metrics, and grow your audience.
        </Typography>
        <Button
          variant="contained"
          size="large"
          startIcon={<AddIcon />}
          onClick={() => navigate('/channels')}
        >
          Add Your First Channel
        </Button>
      </Paper>
    );
  }

  return (
    <Paper sx={{ p: 2.5 }}>
      <Typography variant="h6" fontWeight="600" sx={{ mb: 2 }}>
        ⚡ Quick Actions
      </Typography>

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
        {actions.map((action) => {
          const color = getColor(action.icon);

          return (
            <Button
              key={action.id}
              variant="outlined"
              fullWidth
              onClick={() => navigate(action.url)}
              sx={{
                justifyContent: 'flex-start',
                py: 1.5,
                px: 2,
                borderColor: alpha(color, 0.3),
                '&:hover': {
                  borderColor: color,
                  backgroundColor: alpha(color, 0.05),
                },
              }}
            >
              <Box
                sx={{
                  width: 36,
                  height: 36,
                  borderRadius: 1.5,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  backgroundColor: alpha(color, 0.1),
                  color: color,
                  mr: 2,
                }}
              >
                {getIcon(action.icon)}
              </Box>
              <Box sx={{ textAlign: 'left' }}>
                <Typography variant="body2" fontWeight="600" color="text.primary">
                  {action.title}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {action.description}
                </Typography>
              </Box>
            </Button>
          );
        })}
      </Box>
    </Paper>
  );
};

export default QuickActionsPanel;
