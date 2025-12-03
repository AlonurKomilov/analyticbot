/**
 * VacuumDialog Component
 * Confirmation dialog for manual vacuum operations
 */

import React from 'react';
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  CircularProgress
} from '@mui/material';
import { CleaningServices as CleaningServicesIcon } from '@mui/icons-material';
import type { VacuumDialogState } from './types';

interface VacuumDialogProps {
  dialogState: VacuumDialogState;
  vacuuming: boolean;
  onClose: () => void;
  onConfirm: () => void;
}

export const VacuumDialog: React.FC<VacuumDialogProps> = ({
  dialogState,
  vacuuming,
  onClose,
  onConfirm
}) => {
  return (
    <Dialog open={dialogState.open} onClose={() => !vacuuming && onClose()}>
      <DialogTitle>
        Confirm Manual {dialogState.full ? 'VACUUM FULL' : 'VACUUM'}
      </DialogTitle>
      <DialogContent>
        <DialogContentText>
          {dialogState.full ? (
            <>
              <strong>⚠️ WARNING: VACUUM FULL</strong>
              <br /><br />
              This will perform a full vacuum on table <code><strong>{dialogState.tableName}</strong></code>.
              <br /><br />
              <strong>VACUUM FULL:</strong>
              <ul>
                <li>Requires an <strong>exclusive lock</strong> on the table</li>
                <li>Blocks all reads and writes during operation</li>
                <li>Can take significant time on large tables</li>
                <li>Reclaims maximum disk space</li>
                <li>Should be used during maintenance windows</li>
              </ul>
              <br />
              Are you sure you want to proceed?
            </>
          ) : (
            <>
              This will perform a standard vacuum on table <code><strong>{dialogState.tableName}</strong></code>.
              <br /><br />
              <strong>Standard VACUUM:</strong>
              <ul>
                <li>Runs concurrently with normal operations</li>
                <li>Does not block reads or writes</li>
                <li>Removes dead tuples</li>
                <li>Updates table statistics (ANALYZE)</li>
                <li>Safe to run during business hours</li>
              </ul>
            </>
          )}
        </DialogContentText>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={vacuuming}>
          Cancel
        </Button>
        <Button
          onClick={onConfirm}
          color={dialogState.full ? 'warning' : 'primary'}
          variant="contained"
          disabled={vacuuming}
          startIcon={vacuuming ? <CircularProgress size={20} /> : <CleaningServicesIcon />}
        >
          {vacuuming ? 'Running...' : `Run ${dialogState.full ? 'VACUUM FULL' : 'VACUUM'}`}
        </Button>
      </DialogActions>
    </Dialog>
  );
};
