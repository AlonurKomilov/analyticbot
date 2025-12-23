import React, { useState, useEffect, useCallback } from 'react';
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
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Tabs,
  Tab,
  Card,
  CardContent,
  Grid,
} from '@mui/material';
import {
  Settings as SettingsIcon,
  Refresh as RefreshIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
  Lock as LockIcon,
  Save as SaveIcon,
} from '@mui/icons-material';
import { apiClient } from '../api/client';
import { API_ENDPOINTS } from '../config/api';

interface SystemSetting {
  key: string;
  value: string | null;
  description: string | null;
  data_type: string;
  is_system: boolean;
  updated_by: number | null;
  updated_at: string | null;
}

interface SettingsResponse {
  settings: SystemSetting[];
  total: number;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div role="tabpanel" hidden={value !== index} {...other}>
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
}

const DATA_TYPES = ['string', 'number', 'boolean', 'json'];

const formatDate = (dateString: string | null): string => {
  if (!dateString) return 'Never';
  const date = new Date(dateString);
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

const SettingsPage: React.FC = () => {
  const [settings, setSettings] = useState<SystemSetting[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [tabValue, setTabValue] = useState(0);
  const [includeSystem, setIncludeSystem] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);

  // Edit dialog
  const [editDialog, setEditDialog] = useState<SystemSetting | null>(null);
  const [editValue, setEditValue] = useState('');

  // Create dialog
  const [createDialog, setCreateDialog] = useState(false);
  const [newSetting, setNewSetting] = useState({
    key: '',
    value: '',
    description: '',
    data_type: 'string',
  });

  // Delete confirmation
  const [deleteConfirm, setDeleteConfirm] = useState<SystemSetting | null>(null);

  const fetchSettings = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.get<SettingsResponse>(
        `${API_ENDPOINTS.ADMIN.SETTINGS}?include_system=${includeSystem}`
      );
      setSettings(response.data.settings);
    } catch (err) {
      setError('Failed to load settings. Please try again.');
      console.error('Settings fetch error:', err);
    } finally {
      setLoading(false);
    }
  }, [includeSystem]);

  useEffect(() => {
    fetchSettings();
  }, [fetchSettings]);

  const handleEdit = async () => {
    if (!editDialog) return;
    setActionLoading(true);
    try {
      await apiClient.put(API_ENDPOINTS.ADMIN.SETTING_DETAIL(editDialog.key), {
        value: editValue,
      });
      setSuccess(`Setting "${editDialog.key}" updated successfully`);
      setEditDialog(null);
      await fetchSettings();
    } catch (err) {
      setError('Failed to update setting');
      console.error('Update error:', err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleCreate = async () => {
    if (!newSetting.key) return;
    setActionLoading(true);
    try {
      await apiClient.post(API_ENDPOINTS.ADMIN.SETTINGS, {
        key: newSetting.key,
        value: newSetting.value,
        description: newSetting.description,
        data_type: newSetting.data_type,
        is_system: false,
      });
      setSuccess(`Setting "${newSetting.key}" created successfully`);
      setCreateDialog(false);
      setNewSetting({ key: '', value: '', description: '', data_type: 'string' });
      await fetchSettings();
    } catch (err) {
      setError('Failed to create setting');
      console.error('Create error:', err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!deleteConfirm) return;
    setActionLoading(true);
    try {
      await apiClient.delete(API_ENDPOINTS.ADMIN.SETTING_DETAIL(deleteConfirm.key));
      setSuccess(`Setting "${deleteConfirm.key}" deleted successfully`);
      setDeleteConfirm(null);
      await fetchSettings();
    } catch (err) {
      setError('Failed to delete setting');
      console.error('Delete error:', err);
    } finally {
      setActionLoading(false);
    }
  };

  const userSettings = settings.filter((s) => !s.is_system);
  const systemSettings = settings.filter((s) => s.is_system);

  return (
    <Box>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <Box>
          <Typography variant="h4" fontWeight={700} gutterBottom>
            System Settings
          </Typography>
          <Typography color="text.secondary">
            Configure system settings and preferences
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setCreateDialog(true)}
          >
            Add Setting
          </Button>
          <Tooltip title="Refresh">
            <IconButton onClick={fetchSettings} disabled={loading}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

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

      {/* Quick Stats */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={6} sm={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center', py: 2 }}>
              <Typography variant="h4" fontWeight={700} color="primary">
                {settings.length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Settings
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={6} sm={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center', py: 2 }}>
              <Typography variant="h4" fontWeight={700} color="info.main">
                {userSettings.length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Configurable
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={6} sm={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center', py: 2 }}>
              <Typography variant="h4" fontWeight={700} color="warning.main">
                {systemSettings.length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                System (Read-only)
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={6} sm={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center', py: 2 }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={includeSystem}
                    onChange={(e) => setIncludeSystem(e.target.checked)}
                    size="small"
                  />
                }
                label={
                  <Typography variant="body2" color="text.secondary">
                    Show System
                  </Typography>
                }
              />
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Paper>
        <Tabs
          value={tabValue}
          onChange={(_, newValue) => setTabValue(newValue)}
          sx={{ borderBottom: 1, borderColor: 'divider', px: 2 }}
        >
          <Tab label={`Configurable (${userSettings.length})`} />
          {includeSystem && <Tab label={`System (${systemSettings.length})`} />}
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress />
            </Box>
          ) : userSettings.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <SettingsIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 1 }} />
              <Typography color="text.secondary">No configurable settings found</Typography>
              <Button
                variant="outlined"
                startIcon={<AddIcon />}
                onClick={() => setCreateDialog(true)}
                sx={{ mt: 2 }}
              >
                Add First Setting
              </Button>
            </Box>
          ) : (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Key</TableCell>
                    <TableCell>Value</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Description</TableCell>
                    <TableCell>Last Updated</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {userSettings.map((setting) => (
                    <TableRow key={setting.key} hover>
                      <TableCell>
                        <Typography variant="body2" fontWeight={500} fontFamily="monospace">
                          {setting.key}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography
                          variant="body2"
                          sx={{
                            maxWidth: 200,
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap',
                          }}
                        >
                          {setting.value || '—'}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip label={setting.data_type} size="small" variant="outlined" />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" color="text.secondary">
                          {setting.description || '—'}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" color="text.secondary">
                          {formatDate(setting.updated_at)}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', gap: 0.5 }}>
                          <Tooltip title="Edit">
                            <IconButton
                              size="small"
                              onClick={() => {
                                setEditDialog(setting);
                                setEditValue(setting.value || '');
                              }}
                            >
                              <EditIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Delete">
                            <IconButton
                              size="small"
                              color="error"
                              onClick={() => setDeleteConfirm(setting)}
                            >
                              <DeleteIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </TabPanel>

        {includeSystem && (
          <TabPanel value={tabValue} index={1}>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Key</TableCell>
                    <TableCell>Value</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Description</TableCell>
                    <TableCell>Status</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {systemSettings.map((setting) => (
                    <TableRow key={setting.key} hover>
                      <TableCell>
                        <Typography variant="body2" fontWeight={500} fontFamily="monospace">
                          {setting.key}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">{setting.value || '—'}</Typography>
                      </TableCell>
                      <TableCell>
                        <Chip label={setting.data_type} size="small" variant="outlined" />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" color="text.secondary">
                          {setting.description || '—'}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          icon={<LockIcon />}
                          label="System"
                          size="small"
                          color="warning"
                          variant="outlined"
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </TabPanel>
        )}
      </Paper>

      {/* Edit Dialog */}
      <Dialog open={!!editDialog} onClose={() => setEditDialog(null)} maxWidth="sm" fullWidth>
        <DialogTitle>Edit Setting</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Key: <strong>{editDialog?.key}</strong>
            </Typography>
            <TextField
              fullWidth
              label="Value"
              value={editValue}
              onChange={(e) => setEditValue(e.target.value)}
              multiline={editDialog?.data_type === 'json'}
              rows={editDialog?.data_type === 'json' ? 4 : 1}
              helperText={`Data type: ${editDialog?.data_type}`}
            />
            {editDialog?.description && (
              <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                {editDialog.description}
              </Typography>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialog(null)}>Cancel</Button>
          <Button
            onClick={handleEdit}
            variant="contained"
            startIcon={<SaveIcon />}
            disabled={actionLoading}
          >
            Save
          </Button>
        </DialogActions>
      </Dialog>

      {/* Create Dialog */}
      <Dialog open={createDialog} onClose={() => setCreateDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Setting</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1, display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField
              fullWidth
              label="Key"
              value={newSetting.key}
              onChange={(e) => setNewSetting({ ...newSetting, key: e.target.value })}
              placeholder="e.g., feature_flag_name"
              helperText="Unique identifier for the setting"
            />
            <FormControl fullWidth>
              <InputLabel>Data Type</InputLabel>
              <Select
                value={newSetting.data_type}
                label="Data Type"
                onChange={(e) => setNewSetting({ ...newSetting, data_type: e.target.value })}
              >
                {DATA_TYPES.map((type) => (
                  <MenuItem key={type} value={type}>
                    {type}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <TextField
              fullWidth
              label="Value"
              value={newSetting.value}
              onChange={(e) => setNewSetting({ ...newSetting, value: e.target.value })}
              multiline={newSetting.data_type === 'json'}
              rows={newSetting.data_type === 'json' ? 4 : 1}
            />
            <TextField
              fullWidth
              label="Description"
              value={newSetting.description}
              onChange={(e) => setNewSetting({ ...newSetting, description: e.target.value })}
              placeholder="What this setting controls..."
              multiline
              rows={2}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialog(false)}>Cancel</Button>
          <Button
            onClick={handleCreate}
            variant="contained"
            startIcon={<AddIcon />}
            disabled={actionLoading || !newSetting.key}
          >
            Create
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation */}
      <Dialog open={!!deleteConfirm} onClose={() => setDeleteConfirm(null)}>
        <DialogTitle>Delete Setting</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete the setting{' '}
            <strong>"{deleteConfirm?.key}"</strong>?
          </Typography>
          <Typography color="text.secondary" sx={{ mt: 1 }}>
            This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteConfirm(null)}>Cancel</Button>
          <Button
            onClick={handleDelete}
            color="error"
            variant="contained"
            disabled={actionLoading}
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default SettingsPage;
