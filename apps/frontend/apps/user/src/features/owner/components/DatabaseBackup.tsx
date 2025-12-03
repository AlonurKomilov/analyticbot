/**
 * Database Backup Management Component
 *
 * Allows owner to create, verify, and manage database backups.
 * Displays list of available backups with actions.
 *
 * Access: OWNER ROLE ONLY (Level 4)
 */

import React, { useEffect, useState } from 'react';
import {
  Box,
  Button,
  Chip,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  IconButton,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tooltip,
  Typography,
  Alert,
  Snackbar,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  VerifiedUser as VerifyIcon,
  Refresh as RefreshIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';
import { ownerApi } from '../services/ownerApi';
import type { BackupInfo } from '../types';

export const DatabaseBackupComponent: React.FC = () => {
  const [backups, setBackups] = useState<BackupInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [verifying, setVerifying] = useState<string | null>(null);
  const [deleting, setDeleting] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Dialog states
  const [deleteDialog, setDeleteDialog] = useState<{ open: boolean; filename: string | null }>({
    open: false,
    filename: null,
  });
  const [verifyDialog, setVerifyDialog] = useState<{
    open: boolean;
    filename: string | null;
    result: string | null;
    success: boolean;
  }>({
    open: false,
    filename: null,
    result: null,
    success: false,
  });

  const loadBackups = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await ownerApi.listBackups();
      setBackups(data.backups);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load backups');
      console.error('Error loading backups:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadBackups();
  }, []);

  const handleCreateBackup = async () => {
    try {
      setCreating(true);
      setError(null);
      const result = await ownerApi.createBackup();

      if (result.success) {
        setSuccess(`Backup created successfully: ${result.backup?.filename || 'unknown'}`);
        await loadBackups();
      } else {
        setError(result.message || 'Failed to create backup');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create backup');
    } finally {
      setCreating(false);
    }
  };

  const handleVerifyBackup = async (filename: string) => {
    try {
      setVerifying(filename);
      setError(null);
      const result = await ownerApi.verifyBackup(filename);

      setVerifyDialog({
        open: true,
        filename,
        result: result.message,
        success: result.verified,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to verify backup');
    } finally {
      setVerifying(null);
    }
  };

  const handleDeleteBackup = async () => {
    if (!deleteDialog.filename) return;

    try {
      setDeleting(deleteDialog.filename);
      setError(null);
      const result = await ownerApi.deleteBackup(deleteDialog.filename);

      if (result.success) {
        setSuccess(`Backup deleted: ${deleteDialog.filename}`);
        await loadBackups();
      } else {
        setError(result.message || 'Failed to delete backup');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete backup');
    } finally {
      setDeleting(null);
      setDeleteDialog({ open: false, filename: null });
    }
  };

  const getAgeColor = (ageDays: number) => {
    if (ageDays === 0) return 'success';
    if (ageDays <= 1) return 'success';
    if (ageDays <= 3) return 'warning';
    return 'error';
  };

  const getAgeLabel = (ageDays: number) => {
    if (ageDays === 0) return 'Today';
    if (ageDays === 1) return '1 day ago';
    return `${ageDays} days ago`;
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5" component="h2" fontWeight="bold">
          Database Backups
        </Typography>
        <Box>
          <Button
            startIcon={<RefreshIcon />}
            onClick={loadBackups}
            disabled={loading}
            sx={{ mr: 1 }}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={creating ? <CircularProgress size={20} /> : <AddIcon />}
            onClick={handleCreateBackup}
            disabled={creating || loading}
          >
            Create Backup
          </Button>
        </Box>
      </Box>

      {backups.length === 0 && !loading && (
        <Alert severity="info">
          No backups found. Create your first backup to protect your data.
        </Alert>
      )}

      {backups.length > 0 && (
        <TableContainer component={Paper} elevation={2}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Filename</TableCell>
                <TableCell>Size</TableCell>
                <TableCell>Created</TableCell>
                <TableCell>Age</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {backups.map((backup) => (
                <TableRow key={backup.filename} hover>
                  <TableCell>
                    <Typography
                      variant="body2"
                      fontFamily="monospace"
                      fontSize="0.875rem"
                    >
                      {backup.filename}
                    </Typography>
                    {backup.database_size && (
                      <Typography variant="caption" color="text.secondary">
                        DB: {backup.database_size}
                      </Typography>
                    )}
                  </TableCell>
                  <TableCell>{backup.size_human}</TableCell>
                  <TableCell>
                    {new Date(backup.created_at).toLocaleString()}
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={getAgeLabel(backup.age_days)}
                      size="small"
                      color={getAgeColor(backup.age_days)}
                    />
                  </TableCell>
                  <TableCell>
                    {backup.verified ? (
                      <Chip
                        icon={<CheckIcon />}
                        label="Verified"
                        size="small"
                        color="success"
                      />
                    ) : (
                      <Chip
                        icon={<WarningIcon />}
                        label="Not verified"
                        size="small"
                        color="default"
                      />
                    )}
                  </TableCell>
                  <TableCell align="right">
                    <Tooltip title="Verify backup integrity">
                      <IconButton
                        size="small"
                        color="primary"
                        onClick={() => handleVerifyBackup(backup.filename)}
                        disabled={verifying === backup.filename}
                      >
                        {verifying === backup.filename ? (
                          <CircularProgress size={20} />
                        ) : (
                          <VerifyIcon />
                        )}
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete backup">
                      <IconButton
                        size="small"
                        color="error"
                        onClick={() =>
                          setDeleteDialog({ open: true, filename: backup.filename })
                        }
                        disabled={deleting === backup.filename || backup.age_days === 0}
                      >
                        {deleting === backup.filename ? (
                          <CircularProgress size={20} />
                        ) : (
                          <DeleteIcon />
                        )}
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {loading && (
        <Box display="flex" justifyContent="center" py={4}>
          <CircularProgress />
        </Box>
      )}

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialog.open}
        onClose={() => setDeleteDialog({ open: false, filename: null })}
      >
        <DialogTitle>Delete Backup?</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete this backup? This action cannot be undone.
          </DialogContentText>
          <Typography
            variant="body2"
            fontFamily="monospace"
            sx={{ mt: 2, p: 1, bgcolor: 'grey.100', borderRadius: 1 }}
          >
            {deleteDialog.filename}
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => setDeleteDialog({ open: false, filename: null })}
            disabled={deleting !== null}
          >
            Cancel
          </Button>
          <Button
            onClick={handleDeleteBackup}
            color="error"
            variant="contained"
            disabled={deleting !== null}
          >
            {deleting ? 'Deleting...' : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Verification Result Dialog */}
      <Dialog
        open={verifyDialog.open}
        onClose={() =>
          setVerifyDialog({ open: false, filename: null, result: null, success: false })
        }
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" alignItems="center">
            {verifyDialog.success ? (
              <CheckIcon color="success" sx={{ mr: 1 }} />
            ) : (
              <ErrorIcon color="error" sx={{ mr: 1 }} />
            )}
            Backup Verification
          </Box>
        </DialogTitle>
        <DialogContent>
          <Alert severity={verifyDialog.success ? 'success' : 'error'} sx={{ mb: 2 }}>
            {verifyDialog.result}
          </Alert>
          <Typography variant="body2" color="text.secondary">
            Backup: {verifyDialog.filename}
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() =>
              setVerifyDialog({ open: false, filename: null, result: null, success: false })
            }
          >
            Close
          </Button>
        </DialogActions>
      </Dialog>

      {/* Success/Error Snackbar */}
      <Snackbar
        open={!!success}
        autoHideDuration={6000}
        onClose={() => setSuccess(null)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert onClose={() => setSuccess(null)} severity="success">
          {success}
        </Alert>
      </Snackbar>

      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={() => setError(null)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert onClose={() => setError(null)} severity="error">
          {error}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default DatabaseBackupComponent;
