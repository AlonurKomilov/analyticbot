/**
 * AI Providers Management Page Component
 * Manage user's AI provider configurations
 */

import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  Skeleton,
  Alert,
  Chip,
  alpha,
  useTheme,
} from '@mui/material';
import {
  Add as AddIcon,
  Psychology as AIIcon,
  AccountBalance as BudgetIcon,
  Speed as PerformanceIcon,
} from '@mui/icons-material';
import { AIProviderCard } from './AIProviderCard';
import { AddAIProviderDialog } from './AddAIProviderDialog';
import { useAIProviders } from '../../hooks/useAIProviders';

export const AIProvidersPage: React.FC = () => {
  const theme = useTheme();
  const [addDialogOpen, setAddDialogOpen] = useState(false);

  const {
    availableProviders,
    userProviders,
    spending,
    isLoading,
    isAdding,
    addProvider,
    setDefaultProvider,
    removeProvider,
    loadSpending,
  } = useAIProviders();

  const totalSpending = Object.values(spending).reduce(
    (sum, s) => sum + s.current_spending,
    0
  );

  const totalBudget = userProviders.reduce(
    (sum, p) => sum + (p.monthly_budget || 0),
    0
  );

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
          <AIIcon sx={{ fontSize: 32, color: 'primary.main' }} />
          <Typography variant="h4" component="h1">
            AI Providers
          </Typography>
        </Box>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
          Connect your AI provider accounts (OpenAI, Claude, Gemini) to use AI-powered features
        </Typography>

        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setAddDialogOpen(true)}
          size="large"
        >
          Add Provider
        </Button>
      </Box>

      {/* Stats */}
      {userProviders.length > 0 && (
        <Grid container spacing={2} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={4}>
            <Card
              sx={{
                bgcolor: alpha(theme.palette.primary.main, 0.05),
                borderLeft: `4px solid ${theme.palette.primary.main}`,
              }}
            >
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <AIIcon sx={{ color: 'primary.main' }} />
                  <Typography variant="h6">{userProviders.length}</Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Connected Providers
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={4}>
            <Card
              sx={{
                bgcolor: alpha(theme.palette.success.main, 0.05),
                borderLeft: `4px solid ${theme.palette.success.main}`,
              }}
            >
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <BudgetIcon sx={{ color: 'success.main' }} />
                  <Typography variant="h6">
                    ${totalSpending.toFixed(4)}
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Total Spending This Month
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={4}>
            <Card
              sx={{
                bgcolor: alpha(theme.palette.info.main, 0.05),
                borderLeft: `4px solid ${theme.palette.info.main}`,
              }}
            >
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <PerformanceIcon sx={{ color: 'info.main' }} />
                  <Typography variant="h6">
                    {totalBudget > 0 ? `$${totalBudget.toFixed(2)}` : 'Unlimited'}
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Total Monthly Budget
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Available Providers Info */}
      {userProviders.length === 0 && !isLoading && (
        <Alert severity="info" sx={{ mb: 3 }}>
          <Typography variant="body2" sx={{ mb: 1 }}>
            <strong>Available AI Providers:</strong>
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {availableProviders.map((provider) => (
              <Chip
                key={provider.name}
                label={provider.display_name}
                size="small"
                variant="outlined"
              />
            ))}
          </Box>
        </Alert>
      )}

      {/* User Providers Grid */}
      {isLoading ? (
        <Grid container spacing={3}>
          {[1, 2, 3].map((i) => (
            <Grid item xs={12} md={6} key={i}>
              <Skeleton variant="rectangular" height={250} />
            </Grid>
          ))}
        </Grid>
      ) : userProviders.length > 0 ? (
        <Grid container spacing={3}>
          {userProviders.map((provider) => (
            <Grid item xs={12} md={6} key={provider.provider}>
              <AIProviderCard
                provider={provider}
                spending={spending[provider.provider]}
                onSetDefault={() => setDefaultProvider(provider.provider)}
                onRemove={() => removeProvider(provider.provider)}
                onRefreshSpending={() => loadSpending(provider.provider)}
              />
            </Grid>
          ))}
        </Grid>
      ) : (
        <Card
          sx={{
            textAlign: 'center',
            py: 8,
            bgcolor: alpha(theme.palette.primary.main, 0.02),
          }}
        >
          <CardContent>
            <AIIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              No AI Providers Connected
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Add your first AI provider to unlock AI-powered channel analysis,
              content optimization, and more
            </Typography>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setAddDialogOpen(true)}
            >
              Add Your First Provider
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Add Provider Dialog */}
      <AddAIProviderDialog
        open={addDialogOpen}
        onClose={() => setAddDialogOpen(false)}
        availableProviders={availableProviders}
        onSubmit={addProvider}
        isLoading={isAdding}
      />

      {/* Help Section */}
      <Box sx={{ mt: 6, p: 3, bgcolor: alpha(theme.palette.info.main, 0.05), borderRadius: 2 }}>
        <Typography variant="h6" gutterBottom>
          💡 How It Works
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          1. <strong>Add Provider:</strong> Connect your AI account (OpenAI, Claude, Gemini)
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          2. <strong>Set Budget:</strong> Optional monthly spending limit to prevent overage
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          3. <strong>Use AI Features:</strong> Channel analysis, content optimization, and more
        </Typography>
        <Typography variant="body2" color="text.secondary">
          🔒 <strong>Security:</strong> All API keys are encrypted with AES-128 before storage
        </Typography>
      </Box>
    </Container>
  );
};
