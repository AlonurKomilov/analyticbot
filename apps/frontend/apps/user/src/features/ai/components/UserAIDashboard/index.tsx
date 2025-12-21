/**
 * User AI Dashboard Component
 * Main dashboard for AI features - similar to Bot/MTProto dashboards
 *
 * Shows:
 * - AI Status (tier, usage, enabled features)
 * - AI Configuration & Limits
 * - Active AI Services (purchased from marketplace)
 * - Available AI Upgrades
 */

import React from 'react';
import {
  Box,
  Button,
  Grid,
  IconButton,
  Typography,
  Alert,
  Paper,
  CircularProgress,
  Tooltip,
  alpha,
} from '@mui/material';
import {
  Psychology as AIIcon,
  Refresh as RefreshIcon,
  Settings as SettingsIcon,
  Store as MarketplaceIcon,
  VpnKey as ProvidersIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';

import { useFullAIDashboard } from '../../hooks';
import { AIStatusCard } from './AIStatusCard';
import { AISettingsCard } from './AISettingsCard';
import { ActiveAIServicesCard } from './ActiveAIServicesCard';
import { AvailableAIUpgradesCard } from './AvailableAIUpgradesCard';

export const UserAIDashboard: React.FC = () => {
  const navigate = useNavigate();

  const {
    status,
    settings,
    limits,
    isLoading,
    error,
    clearError,
    refreshAll,
    activeServices,
    availableServices,
    activeServiceKeys,
    isLoadingServices,
  } = useFullAIDashboard();

  const handleRefresh = async () => {
    try {
      await refreshAll();
      toast.success('✅ AI dashboard refreshed');
    } catch (err) {
      toast.error('Failed to refresh');
    }
  };

  const handleOpenSettings = () => {
    navigate('/ai/settings');
  };

  const handleGoToMarketplace = () => {
    navigate('/marketplace?category=ai');
  };

  const handleManageProviders = () => {
    navigate('/workers/ai/providers');
  };

  // Loading state
  if (isLoading && !status) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  // No AI access state
  if (!status && !isLoading) {
    return (
      <Paper
        sx={{
          p: 4,
          textAlign: 'center',
          background: `linear-gradient(135deg, ${alpha('#9C27B0', 0.05)} 0%, ${alpha('#673AB7', 0.05)} 100%)`,
        }}
      >
        <AIIcon sx={{ fontSize: 80, color: 'text.secondary', mb: 2 }} />
        <Typography variant="h5" gutterBottom>
          AI Features Unavailable
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Unable to load AI features. Please try again or contact support.
        </Typography>
        <Button variant="contained" onClick={handleRefresh}>
          Retry
        </Button>
      </Paper>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          mb: 3,
        }}
      >
        <Box display="flex" alignItems="center" gap={2}>
          <Box
            sx={{
              width: 56,
              height: 56,
              borderRadius: 2,
              background: 'linear-gradient(135deg, #9C27B0 0%, #673AB7 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <AIIcon sx={{ color: 'white', fontSize: 32 }} />
          </Box>
          <Box>
            <Typography variant="h4" component="h1" fontWeight={700}>
              AI Assistant
            </Typography>
            <Typography variant="body2" color="text.secondary">
              AI-powered analytics, insights, and automation
            </Typography>
          </Box>
        </Box>

        <Box display="flex" alignItems="center" gap={1}>
          <Tooltip title="Manage AI Providers">
            <Button
              variant="contained"
              startIcon={<ProvidersIcon />}
              onClick={handleManageProviders}
              sx={{
                background: 'linear-gradient(135deg, #9C27B0 0%, #673AB7 100%)',
                '&:hover': {
                  background: 'linear-gradient(135deg, #7B1FA2 0%, #512DA8 100%)',
                },
              }}
            >
              AI Providers
            </Button>
          </Tooltip>
          <Tooltip title="Go to AI Marketplace">
            <Button
              variant="outlined"
              startIcon={<MarketplaceIcon />}
              onClick={handleGoToMarketplace}
              sx={{ borderColor: '#9C27B0', color: '#9C27B0' }}
            >
              Marketplace
            </Button>
          </Tooltip>
          <Tooltip title="AI Settings">
            <IconButton onClick={handleOpenSettings}>
              <SettingsIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Refresh">
            <IconButton onClick={handleRefresh} disabled={isLoading}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={clearError}>
          {error}
        </Alert>
      )}

      {/* Main Content */}
      <Grid container spacing={3}>
        {/* AI Status Card */}
        <Grid item xs={12} md={6}>
          <AIStatusCard status={status} isLoading={isLoading} />
        </Grid>

        {/* AI Settings/Config Card */}
        <Grid item xs={12} md={6}>
          <AISettingsCard
            settings={settings}
            limits={limits}
            isLoading={isLoading}
            onOpenSettings={handleOpenSettings}
          />
        </Grid>

        {/* Active AI Services (Power-Ups) */}
        <Grid item xs={12}>
          <ActiveAIServicesCard
            services={activeServices}
            isLoading={isLoadingServices}
          />
        </Grid>

        {/* Available AI Upgrades */}
        <Grid item xs={12}>
          <AvailableAIUpgradesCard
            services={availableServices}
            activeServiceKeys={activeServiceKeys}
            userTier={status?.tier || 'free'}
            isLoading={isLoadingServices}
          />
        </Grid>
      </Grid>
    </Box>
  );
};

export default UserAIDashboard;
