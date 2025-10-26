/**
 * CancelSubscriptionDialog Component
 *
 * Extracted from SubscriptionDashboard - handles subscription cancellation
 * with confirmation, options, and feedback collection
 */

import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Typography,
  Box,
  Alert,
  RadioGroup,
  FormControlLabel,
  Radio,
  TextField
} from '@mui/material';
import {
  Warning,
  Cancel
} from '@mui/icons-material';
import { Button } from '@shared/components';
import { formatDate } from '../utils/paymentUtils';

interface Subscription {
  current_period_end?: string;
}

interface CancellationData {
  reason: string;
  feedback: string;
}

interface CancelSubscriptionDialogProps {
  open: boolean;
  onClose: () => void;
  onConfirm: (immediate: boolean, data: CancellationData) => void;
  subscription?: Subscription;
  canceling?: boolean;
}

type CancelType = 'end_of_period' | 'immediate';

const CancelSubscriptionDialog: React.FC<CancelSubscriptionDialogProps> = ({
  open,
  onClose,
  onConfirm,
  subscription,
  canceling = false
}) => {
  const [cancelType, setCancelType] = useState<CancelType>('end_of_period');
  const [reason, setReason] = useState<string>('');
  const [feedback, setFeedback] = useState<string>('');

  const handleConfirm = (): void => {
    onConfirm(cancelType === 'immediate', { reason, feedback });
  };

  const handleClose = (): void => {
    if (!canceling) {
      setCancelType('end_of_period');
      setReason('');
      setFeedback('');
      onClose();
    }
  };

  const handleCancelTypeChange = (event: React.ChangeEvent<HTMLInputElement>): void => {
    setCancelType(event.target.value as CancelType);
  };

  const handleReasonChange = (event: React.ChangeEvent<HTMLInputElement>): void => {
    setReason(event.target.value);
  };

  const handleFeedbackChange = (event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>): void => {
    setFeedback(event.target.value);
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        <Box display="flex" alignItems="center" gap={1}>
          <Warning sx={{ color: 'warning.main' }} />
          <Typography variant="h6">Cancel Subscription</Typography>
        </Box>
      </DialogTitle>

      <DialogContent>
        <Alert severity="warning" sx={{ mb: 3 }}>
          <Typography variant="body2">
            Are you sure you want to cancel your subscription? This action cannot be undone.
          </Typography>
        </Alert>

        <Box mb={3}>
          <Typography variant="subtitle2" gutterBottom>
            Cancellation Options
          </Typography>
          <RadioGroup
            value={cancelType}
            onChange={handleCancelTypeChange}
          >
            <FormControlLabel
              value="end_of_period"
              control={<Radio />}
              label={
                <Box>
                  <Typography variant="body2">
                    Cancel at end of billing period
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {subscription?.current_period_end
                      ? `Access continues until ${formatDate(subscription.current_period_end)}`
                      : 'Access continues until current period ends'
                    }
                  </Typography>
                </Box>
              }
            />
            <FormControlLabel
              value="immediate"
              control={<Radio />}
              label={
                <Box>
                  <Typography variant="body2">
                    Cancel immediately
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Access ends immediately (no refund)
                  </Typography>
                </Box>
              }
            />
          </RadioGroup>
        </Box>

        <Box mb={3}>
          <Typography variant="subtitle2" gutterBottom>
            Reason for canceling (optional)
          </Typography>
          <RadioGroup
            value={reason}
            onChange={handleReasonChange}
          >
            <FormControlLabel value="too_expensive" control={<Radio />} label="Too expensive" />
            <FormControlLabel value="not_using" control={<Radio />} label="Not using enough" />
            <FormControlLabel value="found_alternative" control={<Radio />} label="Found an alternative" />
            <FormControlLabel value="temporary" control={<Radio />} label="Temporary break" />
            <FormControlLabel value="other" control={<Radio />} label="Other" />
          </RadioGroup>
        </Box>

        <TextField
          fullWidth
          multiline
          rows={3}
          placeholder="Additional feedback (optional)"
          value={feedback}
          onChange={handleFeedbackChange}
          variant="outlined"
        />
      </DialogContent>

      <DialogActions sx={{ p: 3, pt: 1 }}>
        <Button
          variant="secondary"
          onClick={handleClose}
          disabled={canceling}
        >
          Keep Subscription
        </Button>
        <Button
          variant="danger"
          onClick={handleConfirm}
          loading={canceling}
          loadingText="Canceling..."
          startIcon={<Cancel />}
        >
          {cancelType === 'immediate' ? 'Cancel Now' : 'Schedule Cancellation'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default CancelSubscriptionDialog;
