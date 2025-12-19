/**
 * Service Configuration Page
 * Individual service configuration with detailed info
 */

import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  Paper,
  Button,
  Chip,
  Alert,
  CircularProgress,
  Breadcrumbs,
  Link,
  alpha,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import {
  ArrowBack as BackIcon,
  Extension as ExtensionIcon,
  Settings as SettingsIcon,
  CheckCircle as ActiveIcon,
  Schedule as ExpiringIcon,
  Campaign as ChannelIcon,
  Group as GroupIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import { apiClient } from '@/api/client';
import { useModerationStore } from '@/store';

// Import from central registry
import {
  SERVICE_CONFIG_MAP,
  SERVICE_ICON_MAP,
  SERVICE_DETAILS,
} from '@/features/marketplace';

interface ServiceSubscription {
  id: number;
  service_key: string;
  service_name: string;
  service_description: string | null;
  icon: string | null;
  color: string | null;
  status: string;
  expires_at: string;
  started_at: string;
  auto_renew: boolean;
  usage_quota_daily: number | null;
  usage_quota_monthly: number | null;
  usage_count_daily: number;
  usage_count_monthly: number;
}

const ServiceConfigPage: React.FC = () => {
  const { serviceKey } = useParams<{ serviceKey: string }>();
  const navigate = useNavigate();
  
  const [subscription, setSubscription] = useState<ServiceSubscription | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const {
    selectedChatId,
    configuredChats,
    isLoadingChats,
    setSelectedChat,
    fetchConfiguredChats,
  } = useModerationStore();

  // Fetch user's subscription for this service
  useEffect(() => {
    const fetchSubscription = async () => {
      if (!serviceKey) return;
      
      setIsLoading(true);
      try {
        const response = await apiClient.get<{ subscriptions: ServiceSubscription[] }>('/services/user/active');
        const sub = response.subscriptions?.find(s => s.service_key === serviceKey);
        
        if (sub) {
          setSubscription(sub);
        } else {
          setError('You do not have an active subscription for this service');
        }
      } catch (err: any) {
        setError(err.message || 'Failed to load subscription');
      } finally {
        setIsLoading(false);
      }
    };

    fetchSubscription();
    fetchConfiguredChats();
  }, [serviceKey, fetchConfiguredChats]);

  const getDaysRemaining = (expiresAt: string): number => {
    const now = new Date();
    const expires = new Date(expiresAt);
    const diff = expires.getTime() - now.getTime();
    return Math.ceil(diff / (1000 * 60 * 60 * 24));
  };

  if (isLoading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  // Determine if this is an MTProto service
  const isMTProtoService = serviceKey?.startsWith('mtproto_');
  const backPath = isMTProtoService ? '/workers/mtproto' : '/workers/bot';
  const dashboardName = isMTProtoService ? 'MTProto Dashboard' : 'Bot Dashboard';

  if (error || !subscription || !serviceKey) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error" sx={{ mb: 2 }}>
          {error || 'Service not found'}
        </Alert>
        <Button startIcon={<BackIcon />} onClick={() => navigate(backPath)}>
          Back to {dashboardName}
        </Button>
      </Container>
    );
  }

  const serviceColor = subscription.color || '#667eea';
  const daysRemaining = getDaysRemaining(subscription.expires_at);
  const isExpiringSoon = daysRemaining <= 7 && daysRemaining > 0;
  const details = SERVICE_DETAILS[serviceKey] || { features: [], description: '' };
  const ConfigComponent = SERVICE_CONFIG_MAP[serviceKey];

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Breadcrumbs */}
      <Breadcrumbs sx={{ mb: 3 }}>
        <Link
          component="button"
          underline="hover"
          color="inherit"
          onClick={() => navigate(backPath)}
          sx={{ cursor: 'pointer' }}
        >
          {dashboardName}
        </Link>
        <Typography color="text.primary">{subscription.service_name}</Typography>
      </Breadcrumbs>

      {/* Back Button */}
      <Button
        startIcon={<BackIcon />}
        onClick={() => navigate(backPath)}
        sx={{ mb: 3 }}
      >
        Back to Dashboard
      </Button>

      {/* Service Header */}
      <Paper
        sx={{
          p: 4,
          mb: 4,
          background: `linear-gradient(135deg, ${alpha(serviceColor, 0.15)} 0%, ${alpha(serviceColor, 0.05)} 100%)`,
          border: `1px solid ${alpha(serviceColor, 0.3)}`,
          borderRadius: 3,
        }}
      >
        <Box display="flex" gap={3} flexWrap="wrap">
          {/* Icon */}
          <Box
            sx={{
              width: 80,
              height: 80,
              borderRadius: 2,
              bgcolor: alpha(serviceColor, 0.2),
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: serviceColor,
            }}
          >
            {SERVICE_ICON_MAP[serviceKey] || <ExtensionIcon fontSize="large" />}
          </Box>

          {/* Info */}
          <Box flex={1}>
            <Box display="flex" alignItems="center" gap={2} mb={1}>
              <Typography variant="h4" fontWeight={600}>
                {subscription.service_name}
              </Typography>
              <Chip
                icon={isExpiringSoon ? <ExpiringIcon /> : <ActiveIcon />}
                label={isExpiringSoon ? `Expires in ${daysRemaining} days` : 'Active'}
                color={isExpiringSoon ? 'warning' : 'success'}
                size="small"
              />
              {subscription.auto_renew && (
                <Chip label="Auto-Renew" size="small" variant="outlined" />
              )}
            </Box>
            
            <Typography variant="body1" color="text.secondary" mb={2}>
              {details.description || subscription.service_description}
            </Typography>

            <Box display="flex" gap={2} flexWrap="wrap">
              <Typography variant="caption" color="text.secondary">
                Started: {format(new Date(subscription.started_at), 'MMM d, yyyy')}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Expires: {format(new Date(subscription.expires_at), 'MMM d, yyyy')}
              </Typography>
            </Box>
          </Box>
        </Box>

        {/* Features */}
        {details.features.length > 0 && (
          <Box mt={3}>
            <Typography variant="subtitle2" color="text.secondary" mb={1}>
              Features Included:
            </Typography>
            <Box display="flex" gap={1} flexWrap="wrap">
              {details.features.map((feature, index) => (
                <Chip
                  key={index}
                  label={feature}
                  size="small"
                  sx={{
                    bgcolor: alpha(serviceColor, 0.1),
                    color: serviceColor,
                    border: `1px solid ${alpha(serviceColor, 0.2)}`,
                  }}
                />
              ))}
            </Box>
          </Box>
        )}
      </Paper>

      {/* Chat Selector - Only for bot services with per_chat_config */}
      {!isMTProtoService && (
        <Paper sx={{ p: 3, mb: 4 }}>
          <Typography variant="h6" mb={2}>
            <SettingsIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
            Configure for Channel/Group
          </Typography>
          
          <FormControl fullWidth sx={{ maxWidth: 400 }}>
            <InputLabel>Select Channel/Group</InputLabel>
            <Select
              value={selectedChatId || ''}
              label="Select Channel/Group"
              onChange={(e) => setSelectedChat(Number(e.target.value))}
            >
              {isLoadingChats && (
                <MenuItem disabled>
                  <CircularProgress size={20} sx={{ mr: 1 }} />
                  Loading...
                </MenuItem>
              )}
              {configuredChats.length === 0 && !isLoadingChats && (
                <MenuItem disabled>
                  <em>No channels available. Add channels first.</em>
                </MenuItem>
              )}
              {configuredChats.map((chat) => (
                <MenuItem key={chat.chat_id} value={chat.chat_id}>
                  <Box display="flex" alignItems="center" gap={1}>
                    {chat.chat_type === 'channel' ? (
                      <ChannelIcon fontSize="small" color="primary" />
                    ) : (
                      <GroupIcon fontSize="small" color="secondary" />
                    )}
                    <Typography>{chat.chat_title}</Typography>
                    <Chip label={chat.chat_type} size="small" sx={{ ml: 'auto' }} />
                  </Box>
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          {!selectedChatId && (
            <Alert severity="info" sx={{ mt: 2 }}>
              Select a channel or group to configure this service.
            </Alert>
          )}
        </Paper>
      )}

      {/* Service Configuration */}
      {/* For MTProto services: show config directly (user-level, no chat selection needed) */}
      {/* For Bot services: require chat selection first */}
      {isMTProtoService && ConfigComponent && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" mb={3}>
            Service Settings
          </Typography>
          <ConfigComponent chatId={0} />
        </Paper>
      )}

      {!isMTProtoService && selectedChatId && ConfigComponent && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" mb={3}>
            Service Settings
          </Typography>
          <ConfigComponent chatId={selectedChatId} />
        </Paper>
      )}

      {!isMTProtoService && selectedChatId && !ConfigComponent && (
        <Alert severity="warning">
          Configuration for this service is not yet available.
        </Alert>
      )}

      {isMTProtoService && !ConfigComponent && (
        <Alert severity="warning">
          Configuration for this service is not yet available.
        </Alert>
      )}
    </Container>
  );
};

export default ServiceConfigPage;
