/**
 * Interval Boost Card Component
 * Allows users to purchase faster collection intervals using credits
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Alert,
  AlertTitle,
  CircularProgress,
  Slider,
  Chip,
  Divider,
  Stack,
} from '@mui/material';
import {
  Speed as SpeedIcon,
  CreditScore as CreditIcon,
  Upgrade as UpgradeIcon,
  Timer as TimerIcon,
} from '@mui/icons-material';
import { apiClient } from '@/api/client';

interface BoostInfo {
  current_interval: number;
  min_interval: number;
  can_purchase_boost: boolean;
  credits_per_boost: number;
  boost_reduction_minutes: number;
  max_boosts_available: number;
  active_boost_minutes: number;
  credits_balance: number;
  plan_name: string;
}

interface IntervalBoostCardProps {
  currentInterval: number;
  planName: string;
  onBoostPurchased?: () => void;
}

export const IntervalBoostCard: React.FC<IntervalBoostCardProps> = ({
  currentInterval,
  planName,
  onBoostPurchased,
}) => {
  const [boostInfo, setBoostInfo] = useState<BoostInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [purchasing, setPurchasing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [boostCount, setBoostCount] = useState(1);

  const fetchBoostInfo = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiClient.get<BoostInfo>('/credits/interval-boost/info');
      setBoostInfo(response);
      // Set default boost count to max affordable
      if (response.max_boosts_available > 0) {
        const maxAffordable = Math.min(
          response.max_boosts_available,
          Math.floor(response.credits_balance / response.credits_per_boost)
        );
        setBoostCount(Math.max(1, maxAffordable));
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch boost info');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBoostInfo();
  }, [currentInterval]);

  const handlePurchase = async () => {
    if (!boostInfo) return;

    try {
      setPurchasing(true);
      setError(null);
      setSuccess(null);

      const response = await apiClient.post('/credits/interval-boost/purchase', {
        boost_count: boostCount,
      });

      setSuccess(
        `Successfully purchased ${boostCount} boost(s)! ` +
        `New interval: ${response.new_interval}min. ` +
        `Credits spent: ${response.credits_spent}`
      );

      // Refresh boost info
      await fetchBoostInfo();

      // Notify parent to refresh worker status
      if (onBoostPurchased) {
        onBoostPurchased();
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to purchase boost');
    } finally {
      setPurchasing(false);
    }
  };

  if (loading) {
    return (
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" alignItems="center" justifyContent="center" py={3}>
            <CircularProgress size={24} />
            <Typography sx={{ ml: 2 }}>Loading boost options...</Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  if (!boostInfo) {
    return null;
  }

  // Calculate derived values
  const totalCost = boostCount * boostInfo.credits_per_boost;
  const newInterval = boostInfo.current_interval - (boostCount * boostInfo.boost_reduction_minutes);
  const canAfford = boostInfo.credits_balance >= totalCost;
  const isAtMinimum = boostInfo.current_interval <= boostInfo.min_interval;
  const maxBoosts = Math.min(
    boostInfo.max_boosts_available,
    Math.floor(boostInfo.credits_balance / boostInfo.credits_per_boost)
  );

  return (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Box display="flex" alignItems="center" gap={1} mb={2}>
          <SpeedIcon color="primary" />
          <Typography variant="h6">Speed Up Collection</Typography>
          <Chip 
            label={`${boostInfo.credits_balance} credits`} 
            size="small" 
            icon={<CreditIcon />}
            color="primary"
            variant="outlined"
          />
        </Box>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Purchase interval boosts to collect data more frequently
        </Typography>
        <Divider sx={{ my: 2 }} />

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {success && (
          <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>
            {success}
          </Alert>
        )}

        {/* Plan doesn't allow boosting */}
        {!boostInfo.can_purchase_boost && (
          <Alert severity="info" sx={{ mb: 2 }}>
            <AlertTitle>Boost Not Available</AlertTitle>
            Your current plan ({planName}) does not support interval boosts. 
            Upgrade your plan to unlock this feature.
          </Alert>
        )}

        {/* Already at minimum */}
        {isAtMinimum && boostInfo.can_purchase_boost && (
          <Alert severity="success" sx={{ mb: 2 }}>
            <AlertTitle>Maximum Speed Reached!</AlertTitle>
            Your collection interval is already at the minimum ({boostInfo.min_interval}min) 
            for your {planName} plan.
          </Alert>
        )}

        {/* Show boost options */}
        {boostInfo.can_purchase_boost && !isAtMinimum && (
          <>
            <Stack direction="row" spacing={4} sx={{ mb: 3 }}>
              <Box textAlign="center">
                <Typography variant="body2" color="text.secondary">Current</Typography>
                <Typography variant="h4" color="text.secondary">
                  {boostInfo.current_interval}min
                </Typography>
              </Box>
              <Box display="flex" alignItems="center">
                <Typography variant="h5" color="primary">→</Typography>
              </Box>
              <Box textAlign="center">
                <Typography variant="body2" color="text.secondary">After Boost</Typography>
                <Typography variant="h4" color="success.main">
                  {newInterval}min
                </Typography>
              </Box>
              <Box textAlign="center">
                <Typography variant="body2" color="text.secondary">Minimum</Typography>
                <Typography variant="h4" color="text.disabled">
                  {boostInfo.min_interval}min
                </Typography>
              </Box>
            </Stack>

            {/* Boost slider */}
            {maxBoosts > 1 && (
              <Box sx={{ px: 2, mb: 3 }}>
                <Typography variant="body2" gutterBottom>
                  Number of boosts: <strong>{boostCount}</strong>
                </Typography>
                <Slider
                  value={boostCount}
                  onChange={(_, value) => setBoostCount(value as number)}
                  min={1}
                  max={maxBoosts}
                  marks
                  valueLabelDisplay="auto"
                  disabled={purchasing}
                />
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="caption" color="text.secondary">
                    1 boost = -{boostInfo.boost_reduction_minutes}min
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Max: {maxBoosts} boosts
                  </Typography>
                </Box>
              </Box>
            )}

            {/* Purchase section */}
            <Box 
              sx={{ 
                p: 2, 
                bgcolor: 'action.hover', 
                borderRadius: 1,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between'
              }}
            >
              <Box>
                <Typography variant="body1">
                  <strong>{boostCount}</strong> boost(s) × {boostInfo.credits_per_boost} credits
                </Typography>
                <Typography variant="h5" color="primary.main">
                  Total: {totalCost} credits
                </Typography>
                {!canAfford && (
                  <Typography variant="caption" color="error">
                    Insufficient credits (need {totalCost - boostInfo.credits_balance} more)
                  </Typography>
                )}
              </Box>
              <Button
                variant="contained"
                size="large"
                startIcon={purchasing ? <CircularProgress size={20} color="inherit" /> : <UpgradeIcon />}
                onClick={handlePurchase}
                disabled={purchasing || !canAfford || boostCount === 0}
              >
                {purchasing ? 'Purchasing...' : 'Purchase Boost'}
              </Button>
            </Box>

            {/* Active boost info */}
            {boostInfo.active_boost_minutes > 0 && (
              <Alert severity="info" icon={<TimerIcon />} sx={{ mt: 2 }}>
                You have {boostInfo.active_boost_minutes}min of active boost reduction.
              </Alert>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
};

export default IntervalBoostCard;
