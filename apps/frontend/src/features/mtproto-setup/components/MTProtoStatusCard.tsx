/**
 * MTProto Status Card Component
 * Displays current MTProto configuration status
 */

import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  Button,
  Stack,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  CheckCircle,
  Cancel,
  PhoneAndroid,
  AccountCircle,
  CloudDone,
  CloudOff,
} from '@mui/icons-material';
import { useMTProtoStore } from '../hooks';

export const MTProtoStatusCard: React.FC = () => {
  const { status, isLoading, isDisconnecting, isRemoving, error, disconnect, remove } = useMTProtoStore();

  if (isLoading) {
    return (
      <Card>
        <CardContent>
          <Box display="flex" justifyContent="center" py={3}>
            <CircularProgress />
          </Box>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent>
          <Alert severity="error">
            Failed to load MTProto status: {error}
          </Alert>
        </CardContent>
      </Card>
    );
  }

  if (!status) {
    return null;
  }

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          MTProto Configuration Status
        </Typography>

        <Stack spacing={2} mt={2}>
          {/* Configuration Status */}
          <Box display="flex" alignItems="center" gap={1}>
            {status.configured ? (
              <CheckCircle color="success" />
            ) : (
              <Cancel color="error" />
            )}
            <Typography>
              <strong>Configured:</strong> {status.configured ? 'Yes' : 'No'}
            </Typography>
          </Box>

          {/* Verification Status */}
          <Box display="flex" alignItems="center" gap={1}>
            {status.verified ? (
              <CheckCircle color="success" />
            ) : (
              <Cancel color="error" />
            )}
            <Typography>
              <strong>Verified:</strong> {status.verified ? 'Yes' : 'No'}
            </Typography>
          </Box>

          {/* Phone Number */}
          {status.phone && (
            <Box display="flex" alignItems="center" gap={1}>
              <PhoneAndroid color="action" />
              <Typography>
                <strong>Phone:</strong> {status.phone}
              </Typography>
            </Box>
          )}

          {/* API ID */}
          {status.api_id && (
            <Box display="flex" alignItems="center" gap={1}>
              <AccountCircle color="action" />
              <Typography>
                <strong>API ID:</strong> {status.api_id}
              </Typography>
            </Box>
          )}

          {/* Connection Status */}
          <Box display="flex" alignItems="center" gap={1}>
            {status.connected ? (
              <CloudDone color="success" />
            ) : (
              <CloudOff color="disabled" />
            )}
            <Typography>
              <strong>Connected:</strong> {status.connected ? 'Yes' : 'No'}
            </Typography>
          </Box>

          {/* Last Used */}
          {status.last_used && (
            <Typography variant="body2" color="text.secondary">
              <strong>Last used:</strong>{' '}
              {new Date(status.last_used).toLocaleString()}
            </Typography>
          )}

          {/* Can Read History Badge */}
          <Box>
            <Chip
              label={status.can_read_history ? 'Can read channel history' : 'Cannot read channel history'}
              color={status.can_read_history ? 'success' : 'default'}
              size="small"
            />
          </Box>

          {/* Actions */}
          {status.configured && (
            <Stack direction="row" spacing={1} mt={2}>
              <Button
                variant="outlined"
                color="warning"
                size="small"
                onClick={() => disconnect()}
                disabled={isDisconnecting}
              >
                {isDisconnecting ? 'Disconnecting...' : 'Disconnect'}
              </Button>
              <Button
                variant="outlined"
                color="error"
                size="small"
                onClick={() => {
                  if (window.confirm('Are you sure you want to remove all MTProto configuration?')) {
                    remove();
                  }
                }}
                disabled={isRemoving}
              >
                {isRemoving ? 'Removing...' : 'Remove Configuration'}
              </Button>
            </Stack>
          )}
        </Stack>
      </CardContent>
    </Card>
  );
};
