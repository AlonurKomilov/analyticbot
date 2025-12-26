/**
 * Collection Control Card Component
 * Unified card combining worker status and interval boost controls
 * Provides a clean overview of collection status with boost options
 */
import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
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
  Paper,
  Grid,
  Avatar,
  LinearProgress,
  alpha,
} from '@mui/material';
import {
  Speed as SpeedIcon,
  CreditScore as CreditIcon,
  Upgrade as UpgradeIcon,
  Timer as TimerIcon,
  RocketLaunch as RocketIcon,
  TrendingUp as TrendingUpIcon,
  Star as StarIcon,
  Schedule,
  ErrorOutline,
} from '@mui/icons-material';
import { apiClient } from '@/api/client';
import type { WorkerStatus } from '../types';
import { formatTimeAgo } from '../utils';

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

// Plan intervals configuration (should match backend)
const PLAN_INTERVALS = [
  { name: 'Free', defaultInterval: 60, minInterval: 30, color: '#64748b' },
  { name: 'Pro', defaultInterval: 20, minInterval: 10, color: '#3b82f6' },
  { name: 'Business', defaultInterval: 10, minInterval: 5, color: '#8b5cf6' },
];

interface CollectionControlCardProps {
  workerStatus: WorkerStatus;
  onBoostPurchased?: () => void;
}

interface StatItemProps {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  subtext?: string;
  color?: string;
  badge?: React.ReactNode;
}

const StatItem: React.FC<StatItemProps> = ({ icon, label, value, subtext, color = '#2196F3', badge }) => (
  <Box display="flex" alignItems="center" gap={1.5}>
    <Box
      sx={{
        width: 40,
        height: 40,
        borderRadius: 1.5,
        bgcolor: alpha(color, 0.15),
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: color,
      }}
    >
      {icon}
    </Box>
    <Box>
      <Typography variant="caption" color="text.secondary" textTransform="uppercase" letterSpacing={0.5} fontSize="0.65rem">
        {label}
      </Typography>
      <Box display="flex" alignItems="center" gap={0.5}>
        <Typography variant="subtitle1" fontWeight={600} lineHeight={1.2}>
          {value}
        </Typography>
        {badge}
      </Box>
      {subtext && (
        <Typography variant="caption" color="text.secondary" fontSize="0.65rem">
          {subtext}
        </Typography>
      )}
    </Box>
  </Box>
);

export const CollectionControlCard: React.FC<CollectionControlCardProps> = ({
  workerStatus,
  onBoostPurchased,
}) => {
  const { t } = useTranslation(['mtproto', 'common']);
  const navigate = useNavigate();
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
  }, [workerStatus.worker_interval_minutes]);

  const handlePurchase = async () => {
    if (!boostInfo) return;

    try {
      setPurchasing(true);
      setError(null);
      setSuccess(null);

      const response = await apiClient.post<{ new_interval: number; credits_spent: number }>('/credits/interval-boost/purchase', {
        boost_count: boostCount,
      });

      setSuccess(
        `Successfully purchased ${boostCount} boost(s)! ` +
        `New interval: ${response.new_interval}min. ` +
        `Credits spent: ${response.credits_spent}`
      );

      await fetchBoostInfo();

      if (onBoostPurchased) {
        onBoostPurchased();
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || t('mtproto:boost.purchaseFailed'));
    } finally {
      setPurchasing(false);
    }
  };

  // Calculate derived values
  const totalCost = boostInfo ? boostCount * boostInfo.credits_per_boost : 0;
  const newInterval = boostInfo ? boostInfo.current_interval - (boostCount * boostInfo.boost_reduction_minutes) : 0;
  const canAfford = boostInfo ? boostInfo.credits_balance >= totalCost : false;
  const isAtMinimum = boostInfo ? boostInfo.current_interval <= boostInfo.min_interval : false;
  const maxBoosts = boostInfo ? Math.min(
    boostInfo.max_boosts_available,
    Math.floor(boostInfo.credits_balance / boostInfo.credits_per_boost)
  ) : 0;

  return (
    <Card 
      sx={{ 
        mb: 3,
        background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(139, 92, 246, 0.08) 100%)',
        border: '1px solid rgba(99, 102, 241, 0.2)',
      }}
    >
      <CardContent>
        {/* Header with Status and Credits */}
        <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
          <Box display="flex" alignItems="center" gap={2}>
            <Avatar
              sx={{
                width: 48,
                height: 48,
                bgcolor: alpha('#8b5cf6', 0.2),
                color: '#8b5cf6',
              }}
            >
              <SpeedIcon sx={{ fontSize: 28 }} />
            </Avatar>
            <Box>
              <Typography variant="h6" fontWeight={600}>
                {t('mtproto:boost.title')}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {t('mtproto:boost.description')}
              </Typography>
            </Box>
          </Box>
          <Box display="flex" alignItems="center" gap={1}>
            {boostInfo && (
              <Chip
                label={`${boostInfo.credits_balance.toFixed(1)} ${t('mtproto:boost.credits')}`}
                size="small"
                icon={<CreditIcon />}
                sx={{ 
                  bgcolor: 'rgba(16, 185, 129, 0.15)',
                  color: '#10b981',
                  fontWeight: 600,
                }}
              />
            )}
          </Box>
        </Box>

        {/* Worker Stats Grid */}
        <Paper
          sx={{
            p: 2,
            mb: 2,
            background: 'rgba(0, 0, 0, 0.2)',
            borderRadius: 2,
          }}
        >
          <Grid container spacing={2}>
            <Grid item xs={6} sm={3}>
              <StatItem
                icon={<SpeedIcon sx={{ fontSize: 20 }} />}
                label={t('mtproto:monitoring.interval')}
                value={`${workerStatus.worker_interval_minutes}min`}
                subtext={t('mtproto:worker.betweenRuns')}
                color="#8b5cf6"
              />
            </Grid>
            <Grid item xs={6} sm={3}>
              <StatItem
                icon={<Schedule sx={{ fontSize: 20 }} />}
                label={t('mtproto:worker.runsToday')}
                value={workerStatus.runs_today}
                color="#3b82f6"
                badge={
                  <Chip
                    label={workerStatus.plan_name || 'free'}
                    size="small"
                    sx={{ 
                      height: 18, 
                      fontSize: '0.6rem',
                      textTransform: 'capitalize',
                      bgcolor: 'rgba(59, 130, 246, 0.2)',
                      color: '#3b82f6',
                    }}
                  />
                }
              />
            </Grid>
            <Grid item xs={6} sm={3}>
              <StatItem
                icon={<ErrorOutline sx={{ fontSize: 20 }} />}
                label={t('common:errors')}
                value={workerStatus.errors_today}
                subtext={t('common:today')}
                color={workerStatus.errors_today > 0 ? '#ef4444' : '#10b981'}
              />
            </Grid>
            <Grid item xs={6} sm={3}>
              <StatItem
                icon={<TimerIcon sx={{ fontSize: 20 }} />}
                label={t('mtproto:worker.nextRun')}
                value={formatTimeAgo(workerStatus.next_run)}
                subtext={`${t('mtproto:worker.last')}: ${formatTimeAgo(workerStatus.last_run)}`}
                color="#06b6d4"
              />
            </Grid>
          </Grid>

          {/* Active Collection Progress */}
          {workerStatus.currently_collecting && (
            <Box 
              sx={{ 
                mt: 2, 
                pt: 2, 
                borderTop: '1px solid rgba(255,255,255,0.1)',
              }}
            >
              <Box display="flex" alignItems="center" gap={1} mb={1}>
                <CircularProgress size={14} sx={{ color: '#3b82f6' }} />
                <Typography variant="body2" fontWeight={500}>
                  {t('mtproto:worker.collectionInProgress')}
                </Typography>
              </Box>
              {workerStatus.current_channel && (
                <Typography variant="caption" color="text.secondary">
                  {t('mtproto:worker.currentlyCollecting')}: <strong>{workerStatus.current_channel}</strong>
                </Typography>
              )}
              {workerStatus.channels_total > 0 && (
                <Box mt={1}>
                  <Box display="flex" justifyContent="space-between" mb={0.5}>
                    <Typography variant="caption" color="text.secondary">
                      {workerStatus.channels_processed || 0} / {workerStatus.channels_total} {t('common:channels')}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {((workerStatus.channels_processed || 0) / workerStatus.channels_total * 100).toFixed(0)}%
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={((workerStatus.channels_processed || 0) / workerStatus.channels_total) * 100}
                    sx={{ 
                      height: 4, 
                      borderRadius: 1,
                      bgcolor: alpha('#3b82f6', 0.2),
                      '& .MuiLinearProgress-bar': {
                        bgcolor: '#3b82f6',
                        borderRadius: 1,
                      }
                    }}
                  />
                </Box>
              )}
            </Box>
          )}
        </Paper>

        <Divider sx={{ my: 2, borderColor: 'rgba(255,255,255,0.1)' }} />

        {/* Loading State */}
        {loading && (
          <Box display="flex" alignItems="center" justifyContent="center" py={2}>
            <CircularProgress size={20} />
            <Typography sx={{ ml: 2 }} variant="body2">{t('mtproto:boost.loadingOptions')}</Typography>
          </Box>
        )}

        {/* Error/Success Messages */}
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

        {/* At Maximum Speed - Show Upgrade Options */}
        {!loading && boostInfo && (!boostInfo.can_purchase_boost || isAtMinimum) && (
          <Box>
            <Alert 
              severity="success" 
              icon={<RocketIcon />}
              sx={{ 
                mb: 2,
                background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(59, 130, 246, 0.1) 100%)',
                border: '1px solid rgba(16, 185, 129, 0.3)',
              }}
            >
              <AlertTitle sx={{ fontWeight: 600 }}>
                {t('mtproto:boost.maxSpeedForPlan')}
              </AlertTitle>
              <Typography variant="body2">
                {t('mtproto:boost.reachedMinimumDesc', { 
                  interval: boostInfo.current_interval,
                  plan: boostInfo.plan_name.charAt(0).toUpperCase() + boostInfo.plan_name.slice(1)
                })}
              </Typography>
            </Alert>

            {/* Upgrade Options */}
            {PLAN_INTERVALS.filter(plan => plan.minInterval < boostInfo.min_interval).length > 0 && (
              <Box mb={2}>
                <Box display="flex" alignItems="center" gap={1} mb={1.5}>
                  <TrendingUpIcon sx={{ color: 'warning.main', fontSize: 20 }} />
                  <Typography variant="subtitle2" fontWeight={600}>
                    {t('mtproto:boost.wantFaster')}
                  </Typography>
                </Box>
                
                <Stack spacing={1.5}>
                  {PLAN_INTERVALS.filter(plan => 
                    plan.minInterval < boostInfo.min_interval
                  ).map((plan) => (
                    <Paper
                      key={plan.name}
                      sx={{
                        p: 1.5,
                        cursor: 'pointer',
                        transition: 'all 0.2s ease',
                        border: '1px solid',
                        borderColor: 'rgba(255,255,255,0.1)',
                        borderRadius: 2,
                        background: 'rgba(0,0,0,0.2)',
                        '&:hover': {
                          borderColor: plan.color,
                          transform: 'translateX(4px)',
                          boxShadow: `0 4px 12px ${plan.color}30`,
                        },
                      }}
                      onClick={() => navigate('/subscription')}
                    >
                      <Box display="flex" alignItems="center" justifyContent="space-between">
                        <Box display="flex" alignItems="center" gap={1.5}>
                          <Box
                            sx={{
                              width: 32,
                              height: 32,
                              borderRadius: '50%',
                              background: `linear-gradient(135deg, ${plan.color}40 0%, ${plan.color}20 100%)`,
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                            }}
                          >
                            <StarIcon sx={{ color: plan.color, fontSize: 16 }} />
                          </Box>
                          <Box>
                            <Typography variant="body2" fontWeight={600}>
                              {plan.name} {t('mtproto:boost.plan')}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {t('mtproto:boost.intervalRange', { 
                                default: plan.defaultInterval, 
                                min: plan.minInterval 
                              })}
                            </Typography>
                          </Box>
                        </Box>
                        <Box textAlign="right">
                          <Chip
                            label={`${plan.minInterval} ${t('mtproto:boost.minLabel')}`}
                            size="small"
                            sx={{
                              height: 22,
                              bgcolor: `${plan.color}20`,
                              color: plan.color,
                              fontWeight: 600,
                              fontSize: '0.7rem',
                            }}
                          />
                          <Typography variant="caption" display="block" color="text.secondary" mt={0.5}>
                            {Math.round((boostInfo.current_interval / plan.minInterval - 1) * 100)}% {t('mtproto:boost.faster')}
                          </Typography>
                        </Box>
                      </Box>
                    </Paper>
                  ))}
                </Stack>

                <Button
                  variant="contained"
                  size="medium"
                  fullWidth
                  startIcon={<UpgradeIcon />}
                  onClick={() => navigate('/subscription')}
                  sx={{
                    mt: 2,
                    py: 1,
                    background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                    '&:hover': {
                      background: 'linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)',
                    },
                  }}
                >
                  {t('mtproto:boost.viewPlans')}
                </Button>
              </Box>
            )}
          </Box>
        )}

        {/* Show Boost Purchase Options */}
        {!loading && boostInfo && boostInfo.can_purchase_boost && !isAtMinimum && (
          <>
            <Stack direction="row" spacing={3} sx={{ mb: 2 }} justifyContent="center">
              <Box textAlign="center">
                <Typography variant="caption" color="text.secondary">{t('mtproto:boost.current')}</Typography>
                <Typography variant="h5" color="text.secondary" fontWeight={600}>
                  {boostInfo.current_interval}min
                </Typography>
              </Box>
              <Box display="flex" alignItems="center">
                <Typography variant="h6" color="primary">→</Typography>
              </Box>
              <Box textAlign="center">
                <Typography variant="caption" color="text.secondary">{t('mtproto:boost.afterBoost')}</Typography>
                <Typography variant="h5" color="success.main" fontWeight={600}>
                  {newInterval}min
                </Typography>
              </Box>
              <Box textAlign="center">
                <Typography variant="caption" color="text.secondary">{t('mtproto:boost.minimum')}</Typography>
                <Typography variant="h5" color="text.disabled" fontWeight={600}>
                  {boostInfo.min_interval}min
                </Typography>
              </Box>
            </Stack>

            {/* Boost slider */}
            {maxBoosts > 1 && (
              <Box sx={{ px: 2, mb: 2 }}>
                <Typography variant="body2" gutterBottom>
                  {t('mtproto:boost.numberOfBoosts')}: <strong>{boostCount}</strong>
                </Typography>
                <Slider
                  value={boostCount}
                  onChange={(_, value) => setBoostCount(value as number)}
                  min={1}
                  max={maxBoosts}
                  marks
                  valueLabelDisplay="auto"
                  disabled={purchasing}
                  sx={{
                    '& .MuiSlider-thumb': {
                      bgcolor: '#8b5cf6',
                    },
                    '& .MuiSlider-track': {
                      bgcolor: '#8b5cf6',
                    },
                  }}
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
                bgcolor: 'rgba(0,0,0,0.2)',
                borderRadius: 2,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                gap: 2,
              }}
            >
              <Box>
                <Typography variant="body2">
                  <strong>{boostCount}</strong> {t('mtproto:boost.boosts')} × {boostInfo.credits_per_boost} {t('mtproto:boost.credits')}
                </Typography>
                <Typography variant="h6" color="primary.main" fontWeight={600}>
                  {t('common:total')}: {totalCost} {t('mtproto:boost.credits')}
                </Typography>
                {!canAfford && (
                  <Typography variant="caption" color="error">
                    {t('mtproto:boost.insufficientCredits', { need: totalCost - boostInfo.credits_balance })}
                  </Typography>
                )}
              </Box>
              <Button
                variant="contained"
                size="large"
                startIcon={purchasing ? <CircularProgress size={20} color="inherit" /> : <UpgradeIcon />}
                onClick={handlePurchase}
                disabled={purchasing || !canAfford || boostCount === 0}
                sx={{
                  background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                  '&:hover': {
                    background: 'linear-gradient(135deg, #059669 0%, #047857 100%)',
                  },
                }}
              >
                {purchasing ? t('mtproto:boost.purchasing') : t('mtproto:boost.purchaseButton')}
              </Button>
            </Box>

            {/* Active boost info */}
            {boostInfo.active_boost_minutes > 0 && (
              <Alert severity="info" icon={<TimerIcon />} sx={{ mt: 2 }}>
                {t('mtproto:boost.activeBoost', { minutes: boostInfo.active_boost_minutes })}
              </Alert>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
};

export default CollectionControlCard;
