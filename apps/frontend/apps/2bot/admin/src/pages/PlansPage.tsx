import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Tooltip,
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Switch,
  FormControlLabel,
  Chip,
} from '@mui/material';
import {
  Edit as EditIcon,
  Refresh as RefreshIcon,
  Speed as SpeedIcon,
  Timer as TimerIcon,
} from '@mui/icons-material';
import { apiClient } from '../api/client';

interface Plan {
  id: number;
  name: string;
  slug: string;
  description: string;
  price: number;
  duration_days: number;
  is_active: boolean;
  features: Record<string, any>;
  mtproto_interval_minutes: number;
  min_mtproto_interval_minutes: number;
  credits_per_interval_boost: number;
  interval_boost_minutes: number;
  can_purchase_boost: boolean;
}

interface EditPlanRequest {
  mtproto_interval_minutes: number;
  min_mtproto_interval_minutes: number;
  credits_per_interval_boost: number;
  interval_boost_minutes: number;
  can_purchase_boost: boolean;
}

const PlansPage: React.FC = () => {
  const [plans, setPlans] = useState<Plan[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState<Plan | null>(null);
  const [editForm, setEditForm] = useState<EditPlanRequest>({
    mtproto_interval_minutes: 60,
    min_mtproto_interval_minutes: 30,
    credits_per_interval_boost: 5,
    interval_boost_minutes: 10,
    can_purchase_boost: true,
  });

  const fetchPlans = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await apiClient.get('/admin/plans');

      if (Array.isArray(response.data)) {
        setPlans(response.data);
      } else if (response.data?.plans) {
        setPlans(response.data.plans);
      } else if (Array.isArray(response)) {
        setPlans(response);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to fetch plans');
      console.error('Error fetching plans:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPlans();
  }, []);

  const handleEditClick = (plan: Plan) => {
    setSelectedPlan(plan);
    setEditForm({
      mtproto_interval_minutes: plan.mtproto_interval_minutes || 60,
      min_mtproto_interval_minutes: plan.min_mtproto_interval_minutes || 30,
      credits_per_interval_boost: plan.credits_per_interval_boost || 5,
      interval_boost_minutes: plan.interval_boost_minutes || 10,
      can_purchase_boost: plan.can_purchase_boost !== false,
    });
    setEditDialogOpen(true);
  };

  const handleSave = async () => {
    if (!selectedPlan) return;

    try {
      setError(null);
      await apiClient.patch(`/admin/plans/${selectedPlan.id}/mtproto-config`, editForm);

      setSuccess(`Successfully updated ${selectedPlan.name} plan configuration`);
      setEditDialogOpen(false);
      fetchPlans();

      setTimeout(() => setSuccess(null), 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update plan');
    }
  };

  const handleClose = () => {
    setEditDialogOpen(false);
    setSelectedPlan(null);
  };

  const getIntervalColor = (minutes: number): string => {
    if (minutes <= 5) return '#4caf50';
    if (minutes <= 10) return '#2196f3';
    if (minutes <= 20) return '#ff9800';
    return '#9e9e9e';
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" gutterBottom>
          <SpeedIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          Subscription Plans & MTProto Configuration
        </Typography>
        <Tooltip title="Refresh">
          <IconButton onClick={fetchPlans} disabled={loading}>
            <RefreshIcon />
          </IconButton>
        </Tooltip>
      </Box>

      {error && (
        <Alert severity="error" onClose={() => setError(null)} sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" onClose={() => setSuccess(null)} sx={{ mb: 2 }}>
          {success}
        </Alert>
      )}

      <Paper elevation={2}>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell><strong>Plan</strong></TableCell>
                <TableCell><strong>Price</strong></TableCell>
                <TableCell align="center"><strong>Base Interval</strong></TableCell>
                <TableCell align="center"><strong>Min Interval</strong></TableCell>
                <TableCell align="center"><strong>Boost Cost</strong></TableCell>
                <TableCell align="center"><strong>Boost Reduction</strong></TableCell>
                <TableCell align="center"><strong>Can Boost</strong></TableCell>
                <TableCell align="center"><strong>Status</strong></TableCell>
                <TableCell align="center"><strong>Actions</strong></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {plans.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={9} align="center">
                    <Typography color="textSecondary">No plans found</Typography>
                  </TableCell>
                </TableRow>
              ) : (
                plans.map((plan) => (
                  <TableRow key={plan.id}>
                    <TableCell>
                      <Box>
                        <Typography variant="subtitle1" fontWeight="bold">
                          {plan.name}
                        </Typography>
                        <Typography variant="body2" color="textSecondary">
                          {plan.description}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      ${plan.price}
                      <Typography variant="caption" display="block" color="textSecondary">
                        /{plan.duration_days} days
                      </Typography>
                    </TableCell>
                    <TableCell align="center">
                      <Chip
                        icon={<TimerIcon />}
                        label={`${plan.mtproto_interval_minutes || 60}min`}
                        size="small"
                        sx={{
                          bgcolor: getIntervalColor(plan.mtproto_interval_minutes || 60),
                          color: 'white',
                        }}
                      />
                      <Typography variant="caption" display="block" color="textSecondary">
                        {Math.floor(1440 / (plan.mtproto_interval_minutes || 60))} runs/day
                      </Typography>
                    </TableCell>
                    <TableCell align="center">
                      {plan.min_mtproto_interval_minutes || 30}min
                    </TableCell>
                    <TableCell align="center">
                      {plan.credits_per_interval_boost || '-'} credits
                    </TableCell>
                    <TableCell align="center">
                      -{plan.interval_boost_minutes || '-'}min
                    </TableCell>
                    <TableCell align="center">
                      <Chip
                        label={plan.can_purchase_boost ? 'Yes' : 'No'}
                        size="small"
                        color={plan.can_purchase_boost ? 'success' : 'default'}
                      />
                    </TableCell>
                    <TableCell align="center">
                      <Chip
                        label={plan.is_active ? 'Active' : 'Inactive'}
                        size="small"
                        color={plan.is_active ? 'success' : 'default'}
                      />
                    </TableCell>
                    <TableCell align="center">
                      <Tooltip title="Edit MTProto Configuration">
                        <IconButton size="small" onClick={() => handleEditClick(plan)} color="primary">
                          <EditIcon />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* Edit Dialog */}
      <Dialog open={editDialogOpen} onClose={handleClose} maxWidth="sm" fullWidth>
        <DialogTitle>
          Edit MTProto Configuration: {selectedPlan?.name}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField
              label="Base Collection Interval (minutes)"
              type="number"
              value={editForm.mtproto_interval_minutes}
              onChange={(e) =>
                setEditForm({ ...editForm, mtproto_interval_minutes: parseInt(e.target.value) })
              }
              fullWidth
              helperText="How often to collect messages for users on this plan"
            />
            <TextField
              label="Minimum Interval (minutes)"
              type="number"
              value={editForm.min_mtproto_interval_minutes}
              onChange={(e) =>
                setEditForm({ ...editForm, min_mtproto_interval_minutes: parseInt(e.target.value) })
              }
              fullWidth
              helperText="Users cannot reduce interval below this limit"
            />
            <TextField
              label="Credits Per Boost"
              type="number"
              value={editForm.credits_per_interval_boost}
              onChange={(e) =>
                setEditForm({ ...editForm, credits_per_interval_boost: parseInt(e.target.value) })
              }
              fullWidth
              helperText="Cost in credits to purchase one interval boost"
            />
            <TextField
              label="Boost Reduction (minutes)"
              type="number"
              value={editForm.interval_boost_minutes}
              onChange={(e) =>
                setEditForm({ ...editForm, interval_boost_minutes: parseInt(e.target.value) })
              }
              fullWidth
              helperText="How many minutes each boost reduces the interval"
            />
            <FormControlLabel
              control={
                <Switch
                  checked={editForm.can_purchase_boost}
                  onChange={(e) =>
                    setEditForm({ ...editForm, can_purchase_boost: e.target.checked })
                  }
                />
              }
              label="Allow users to purchase interval boosts"
            />

            <Alert severity="info" sx={{ mt: 1 }}>
              <Typography variant="body2">
                <strong>Collections per day:</strong> {Math.floor(1440 / editForm.mtproto_interval_minutes)}
                <br />
                <strong>Max boosts available:</strong>{' '}
                {Math.floor((editForm.mtproto_interval_minutes - editForm.min_mtproto_interval_minutes) / editForm.interval_boost_minutes)}
                {editForm.can_purchase_boost && (
                  <>
                    <br />
                    <strong>Cost to reach minimum:</strong>{' '}
                    {Math.floor((editForm.mtproto_interval_minutes - editForm.min_mtproto_interval_minutes) / editForm.interval_boost_minutes) * editForm.credits_per_interval_boost} credits
                  </>
                )}
              </Typography>
            </Alert>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <Button onClick={handleSave} variant="contained" color="primary">
            Save Changes
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default PlansPage;
