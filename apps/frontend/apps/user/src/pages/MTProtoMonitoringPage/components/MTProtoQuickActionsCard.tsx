/**
 * MTProto Quick Actions Card Component
 * Provides quick action buttons similar to the Bot Dashboard
 */

import React from 'react';
import { useTranslation } from 'react-i18next';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Tooltip,
} from '@mui/material';
import {
  Store as MarketplaceIcon,
  Settings as SettingsIcon,
  Delete as RemoveIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';

interface MTProtoQuickActionsCardProps {
  onCheckStatus: () => void;
  onBrowsePowerUps: () => void;
  onOpenSettings: () => void;
  onRemoveMTProto: () => void;
  isCheckingStatus?: boolean;
  isRemoving?: boolean;
}

export const MTProtoQuickActionsCard: React.FC<MTProtoQuickActionsCardProps> = ({
  onCheckStatus,
  onBrowsePowerUps,
  onOpenSettings,
  onRemoveMTProto,
  isCheckingStatus = false,
  isRemoving = false,
}) => {
  const { t } = useTranslation(['mtproto', 'common']);

  return (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          {t('mtproto:quickActions.title', 'Quick Actions')}
        </Typography>
        
        <Box display="flex" gap={2} flexWrap="wrap">
          {/* Check Status Button */}
          <Tooltip title={t('mtproto:quickActions.checkStatusDesc', 'Verify your MTProto session is working')}>
            <Button
              variant="contained"
              color="primary"
              startIcon={<RefreshIcon />}
              onClick={onCheckStatus}
              disabled={isCheckingStatus}
              sx={{
                background: 'linear-gradient(135deg, #4CAF50 0%, #2196F3 100%)',
                '&:hover': {
                  background: 'linear-gradient(135deg, #2196F3 0%, #4CAF50 100%)',
                },
              }}
            >
              {isCheckingStatus 
                ? t('mtproto:quickActions.checking', 'Checking...')
                : t('mtproto:quickActions.checkStatus', 'Check Status')
              }
            </Button>
          </Tooltip>

          {/* Browse Power-Ups Button */}
          <Tooltip title={t('mtproto:quickActions.browsePowerUpsDesc', 'Explore available MTProto services')}>
            <Button
              variant="contained"
              startIcon={<MarketplaceIcon />}
              onClick={onBrowsePowerUps}
              sx={{
                background: 'linear-gradient(135deg, #9C27B0 0%, #E91E63 100%)',
                '&:hover': {
                  background: 'linear-gradient(135deg, #E91E63 0%, #9C27B0 100%)',
                },
              }}
            >
              {t('mtproto:quickActions.browsePowerUps', 'Browse Power-Ups')}
            </Button>
          </Tooltip>

          {/* Settings Button */}
          <Tooltip title={t('mtproto:quickActions.settingsDesc', 'Configure MTProto settings')}>
            <Button
              variant="outlined"
              startIcon={<SettingsIcon />}
              onClick={onOpenSettings}
            >
              {t('mtproto:quickActions.settings', 'Rate Limits')}
            </Button>
          </Tooltip>

          {/* Remove MTProto Button */}
          <Tooltip title={t('mtproto:quickActions.removeDesc', 'Permanently delete your MTProto configuration')}>
            <Button
              variant="outlined"
              color="error"
              startIcon={<RemoveIcon />}
              onClick={onRemoveMTProto}
              disabled={isRemoving}
            >
              {isRemoving 
                ? t('common:removing', 'Removing...')
                : t('mtproto:quickActions.remove', 'Remove MTProto')
              }
            </Button>
          </Tooltip>
        </Box>
      </CardContent>
    </Card>
  );
};

export default MTProtoQuickActionsCard;
