/**
 * AI Provider Card Component
 * Displays a single AI provider configuration with spending stats
 */

import React, { useState } from 'react';
import {
  Card,
  CardContent,
  Box,
  Typography,
  Chip,
  IconButton,
  LinearProgress,
  Tooltip,
  Menu,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  alpha,
  useTheme,
} from '@mui/material';
import {
  MoreVert as MoreIcon,
  Star as DefaultIcon,
  StarBorder as NotDefaultIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  TrendingUp as SpendingIcon,
} from '@mui/icons-material';
import type { UserAIProvider, AIProviderSpending } from '../../api/aiProvidersAPI';

interface AIProviderCardProps {
  provider: UserAIProvider;
  spending?: AIProviderSpending;
  onSetDefault: () => void;
  onRemove: () => void;
  onRefreshSpending: () => void;
}

export const AIProviderCard: React.FC<AIProviderCardProps> = ({
  provider,
  spending,
  onSetDefault,
  onRemove,
  onRefreshSpending,
}) => {
  const theme = useTheme();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleSetDefault = () => {
    onSetDefault();
    handleMenuClose();
  };

  const handleRemove = () => {
    setDeleteDialogOpen(true);
    handleMenuClose();
  };

  const confirmRemove = () => {
    onRemove();
    setDeleteDialogOpen(false);
  };

  const usagePercentage = spending
    ? spending.monthly_budget
      ? (spending.current_spending / spending.monthly_budget) * 100
      : 0
    : 0;

  const isNearBudget = usagePercentage > 80;
  const isOverBudget = usagePercentage >= 100;

  const providerColors: Record<string, string> = {
    openai: '#10A37F',
    claude: '#CC785C',
    gemini: '#4285F4',
    grok: '#000000',
  };

  const providerColor = providerColors[provider.provider] || theme.palette.primary.main;

  return (
    <>
      <Card
        sx={{
          position: 'relative',
          borderLeft: `4px solid ${providerColor}`,
          '&:hover': {
            boxShadow: theme.shadows[4],
            transform: 'translateY(-2px)',
            transition: 'all 0.2s',
          },
        }}
      >
        <CardContent>
          {/* Header */}
          <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 2 }}>
            <Box sx={{ flex: 1 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                <Typography variant="h6" component="div">
                  {provider.display_name}
                </Typography>
                {provider.is_default && (
                  <Chip
                    icon={<DefaultIcon />}
                    label="Default"
                    size="small"
                    color="primary"
                    sx={{ height: 20 }}
                  />
                )}
              </Box>
              <Typography variant="caption" color="text.secondary">
                {provider.api_key_preview}
              </Typography>
            </Box>
            <IconButton size="small" onClick={handleMenuOpen}>
              <MoreIcon />
            </IconButton>
          </Box>

          {/* Model */}
          <Box sx={{ mb: 2 }}>
            <Typography variant="caption" color="text.secondary" gutterBottom>
              Model
            </Typography>
            <Chip
              label={provider.model}
              size="small"
              variant="outlined"
              sx={{ mt: 0.5 }}
            />
          </Box>

          {/* Spending Stats */}
          {spending && (
            <Box
              sx={{
                mt: 2,
                p: 1.5,
                bgcolor: alpha(providerColor, 0.05),
                borderRadius: 1,
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  <SpendingIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
                  <Typography variant="caption" color="text.secondary">
                    This Month
                  </Typography>
                </Box>
                <Tooltip title="Refresh spending">
                  <IconButton size="small" onClick={onRefreshSpending}>
                    <RefreshIcon sx={{ fontSize: 16 }} />
                  </IconButton>
                </Tooltip>
              </Box>

              {provider.monthly_budget ? (
                <>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2" fontWeight="bold">
                      ${spending.current_spending.toFixed(4)}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      of ${provider.monthly_budget.toFixed(2)}
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={Math.min(usagePercentage, 100)}
                    sx={{
                      height: 6,
                      borderRadius: 1,
                      bgcolor: alpha(theme.palette.grey[500], 0.2),
                      '& .MuiLinearProgress-bar': {
                        bgcolor: isOverBudget
                          ? theme.palette.error.main
                          : isNearBudget
                          ? theme.palette.warning.main
                          : providerColor,
                      },
                    }}
                  />
                  {isOverBudget && (
                    <Typography variant="caption" color="error" sx={{ mt: 0.5, display: 'block' }}>
                      ⚠️ Budget exceeded
                    </Typography>
                  )}
                  {isNearBudget && !isOverBudget && (
                    <Typography variant="caption" color="warning.main" sx={{ mt: 0.5, display: 'block' }}>
                      ⚠️ Approaching budget limit
                    </Typography>
                  )}
                </>
              ) : (
                <Box>
                  <Typography variant="body2" fontWeight="bold">
                    ${spending.current_spending.toFixed(4)}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    No budget limit set
                  </Typography>
                </Box>
              )}

              <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                {spending.tokens_used.toLocaleString()} tokens used
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Menu */}
      <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={handleMenuClose}>
        {!provider.is_default && (
          <MenuItem onClick={handleSetDefault}>
            <NotDefaultIcon sx={{ mr: 1 }} fontSize="small" />
            Set as Default
          </MenuItem>
        )}
        <MenuItem onClick={handleRemove} sx={{ color: 'error.main' }}>
          <DeleteIcon sx={{ mr: 1 }} fontSize="small" />
          Remove Provider
        </MenuItem>
      </Menu>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Remove Provider?</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to remove <strong>{provider.display_name}</strong>?
            This will delete your API key and all associated data.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button onClick={confirmRemove} color="error" variant="contained">
            Remove
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};
