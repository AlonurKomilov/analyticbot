/**
 * MTProto Setup Notice Component
 * Shows helpful information before user proceeds with MTProto setup
 * Friendly reminder to use a secondary account (recommended, not required)
 */

import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Alert,
  AlertTitle,
  Button,
  Checkbox,
  FormControlLabel,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import {
  CheckCircle,
  Lightbulb,
  Security,
  TipsAndUpdates,
  ArrowForward,
} from '@mui/icons-material';

interface MTProtoRiskWarningProps {
  onAccept: () => void;
  onDecline: () => void;
}

export const MTProtoRiskWarning: React.FC<MTProtoRiskWarningProps> = ({
  onAccept,
  onDecline,
}) => {
  const [understood, setUnderstood] = useState(false);

  return (
    <Box>
      {/* Info Header */}
      <Alert
        severity="error"
        sx={{ mb: 3 }}
      >
        <AlertTitle sx={{ fontSize: '1.1rem', fontWeight: 'bold' }}>
          Attention: MTProto Telegram Account Setup
        </AlertTitle>
        <Typography variant="body1">
          MTProto provides powerful analytics by accessing your channel history directly.
          For your Telegram account's security and best results, please read the recommendations below before proceeding.
        </Typography>
      </Alert>

      {/* Recommendation Section */}
      <Paper sx={{ p: 3, mb: 3, border: '1px solid', borderColor: 'warning.main' }}>
        <Typography variant="h6" color="warning.main" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Lightbulb color="warning" /> Recommended: Use a Secondary Telegram Account
        </Typography>

        <Typography variant="body2" sx={{ color: 'text.secondary', mb: 2 }}>
          For the best experience, we recommend using a dedicated Telegram account for analytics:
        </Typography>

        <List dense>
          <ListItem>
            <ListItemIcon>
              <CheckCircle color="success" fontSize="small" />
            </ListItemIcon>
            <ListItemText
              primary="Create a secondary Telegram account for analytics"
              secondary="This keeps your personal account separate"
            />
          </ListItem>

          <ListItem>
            <ListItemIcon>
              <CheckCircle color="success" fontSize="small" />
            </ListItemIcon>
            <ListItemText
              primary="Add this account as admin to your channels"
              secondary="So it can access channel history"
            />
          </ListItem>

          <ListItem>
            <ListItemIcon>
              <CheckCircle color="success" fontSize="small" />
            </ListItemIcon>
            <ListItemText
              primary="Use any spare phone number"
              secondary="You can get a virtual number if needed"
            />
          </ListItem>
        </List>
      </Paper>

      {/* Why Section */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <TipsAndUpdates color="primary" /> Why We Recommend Using a Secondary Telegram Account
        </Typography>

        <Typography variant="body2" paragraph>
          Telegram has rate limits on API requests. Using a dedicated account means:
        </Typography>

        <List dense>
          <ListItem>
            <ListItemIcon>
              <Security color="primary" fontSize="small" />
            </ListItemIcon>
            <ListItemText
              primary="Your personal chats stay completely private"
            />
          </ListItem>

          <ListItem>
            <ListItemIcon>
              <Security color="primary" fontSize="small" />
            </ListItemIcon>
            <ListItemText
              primary="If Telegram applies any rate limits, only the analytics account is affected"
            />
          </ListItem>

          <ListItem>
            <ListItemIcon>
              <Security color="primary" fontSize="small" />
            </ListItemIcon>
            <ListItemText
              primary="You can easily manage permissions for different channels"
            />
          </ListItem>

          <ListItem>
            <ListItemIcon>
              <Security color="warning" fontSize="small" />
            </ListItemIcon>
            <ListItemText
              primary="In rare cases, Telegram may temporarily restrict accounts with high API usage"
              secondary="Using a secondary account keeps your main account safe from any restrictions"
            />
          </ListItem>
        </List>

        <Alert severity="warning" sx={{ mt: 2 }}>
          <Typography variant="body2">
            <strong>Note:</strong> If you choose to use your main Telegram account instead of a secondary one,
            you accept full responsibility for any potential restrictions. We strongly recommend using
            a dedicated Telegram account for analytics purposes.
          </Typography>
        </Alert>
      </Paper>

      <Divider sx={{ my: 3 }} />

      {/* Simple Confirmation */}
      <Paper sx={{ p: 3, mb: 3, bgcolor: 'background.paper' }}>
        <FormControlLabel
          control={
            <Checkbox
              checked={understood}
              onChange={(e) => setUnderstood(e.target.checked)}
              color="primary"
            />
          }
          label={
            <Typography variant="body2">
              I understand it's recommended to use a secondary Telegram account for analytics
            </Typography>
          }
        />
      </Paper>

      {/* Action Buttons */}
      <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
        <Button
          variant="outlined"
          color="inherit"
          size="large"
          onClick={onDecline}
        >
          Maybe Later
        </Button>

        <Button
          variant="contained"
          color="primary"
          size="large"
          disabled={!understood}
          onClick={onAccept}
          endIcon={<ArrowForward />}
        >
          Continue Setup
        </Button>
      </Box>

      {!understood && (
        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', textAlign: 'center', mt: 2 }}>
          Please check the box above to continue
        </Typography>
      )}
    </Box>
  );
};
