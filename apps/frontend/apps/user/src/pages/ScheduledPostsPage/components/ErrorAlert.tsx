/**
 * ErrorAlert Component
 * Displays error messages with optional retry functionality
 */

import React from 'react';
import { Alert, Button, Box } from '@mui/material';
import { ErrorAlertProps } from '../types';

const ErrorAlert: React.FC<ErrorAlertProps> = ({ error, onRetry }) => {
  return (
    <Alert
      severity="error"
      sx={{ mb: 3 }}
      role="alert"
      action={
        onRetry && (
          <Button
            color="inherit"
            size="small"
            onClick={onRetry}
          >
            Retry
          </Button>
        )
      }
    >
      <Box>
        <strong>Error loading scheduled posts:</strong> {error}
      </Box>
    </Alert>
  );
};

export default ErrorAlert;
