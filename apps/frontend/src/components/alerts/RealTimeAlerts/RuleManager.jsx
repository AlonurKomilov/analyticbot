import React from 'react';
import {
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  FormControlLabel,
  Switch,
  Box,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import { Button } from '../../common';
import {
  Add as AddIcon
} from '@mui/icons-material';

/**
 * RuleManager - Memoized component for alert rule configuration and management
 *
 * Handles CRUD operations for alert rules, threshold settings, validation,
 * and preview functionality. Optimized for rule management performance.
 *
 * @param {Object} props - Component props
 * @param {Array} props.alertRules - Array of alert rule objects
 * @param {boolean} props.open - Whether the settings dialog is open
 * @param {Function} props.onClose - Callback to close the dialog
 * @param {Function} props.onToggleRule - Callback to toggle rule enabled state
 * @param {Function} props.onAddRule - Callback to open new rule dialog
 */
const RuleManager = React.memo(({
  alertRules = [],
  open = false,
  onClose,
  onToggleRule,
  onAddRule
}) => {
  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>Alert Rules Configuration</DialogTitle>
      <DialogContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Box>
            Configure when and how you want to be alerted about important changes
            in your channel analytics.
          </Box>
          <Button
            variant="primary"
            startIcon={<AddIcon />}
            onClick={onAddRule}
          >
            Add New Rule
          </Button>
        </Box>

        <List>
          {alertRules.map((rule, index) => {
            const IconComponent = rule.icon;
            return (
              <Box key={rule.id}>
                <ListItem>
                  <ListItemIcon>
                    <IconComponent color={rule.color} />
                  </ListItemIcon>
                  <ListItemText
                    primary={rule.name}
                    secondary={rule.description}
                  />
                  <FormControlLabel
                    control={
                      <Switch
                        checked={rule.enabled}
                        onChange={() => onToggleRule?.(rule.id)}
                        color="primary"
                      />
                    }
                    label="Enabled"
                  />
                </ListItem>
                {index < alertRules.length - 1 && <Divider />}
              </Box>
            );
          })}
        </List>
      </DialogContent>
      <DialogActions>
        <Button variant="secondary" onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
});

RuleManager.displayName = 'RuleManager';

export default RuleManager;
