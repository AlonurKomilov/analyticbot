import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Grid,
  Typography,
  Slider
} from '@mui/material';

/**
 * NewRuleDialog - Memoized component for creating new alert rules
 * 
 * Provides form interface for creating new alert rules with validation,
 * metric type selection, condition configuration, and threshold settings.
 * 
 * @param {Object} props - Component props
 * @param {boolean} props.open - Whether the dialog is open
 * @param {Function} props.onClose - Callback to close the dialog
 * @param {Function} props.onSubmit - Callback when form is submitted
 * @param {Object} props.newRule - Current new rule object
 * @param {Function} props.onRuleChange - Callback when rule properties change
 */
const NewRuleDialog = React.memo(({ 
  open = false, 
  onClose, 
  onSubmit,
  newRule = {
    name: '',
    type: 'growth',
    condition: 'greater_than',
    threshold: 10,
    enabled: true
  },
  onRuleChange 
}) => {
  const handleFieldChange = (field, value) => {
    onRuleChange?.({ ...newRule, [field]: value });
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Create New Alert Rule</DialogTitle>
      <DialogContent>
        <Grid container spacing={2} sx={{ mt: 1 }}>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Rule Name"
              value={newRule.name}
              onChange={(e) => handleFieldChange('name', e.target.value)}
              placeholder="Enter a descriptive name for this rule"
            />
          </Grid>
          <Grid item xs={6}>
            <TextField
              fullWidth
              select
              label="Metric Type"
              value={newRule.type}
              onChange={(e) => handleFieldChange('type', e.target.value)}
              SelectProps={{ native: true }}
            >
              <option value="growth">Growth Rate</option>
              <option value="engagement">Engagement Rate</option>
              <option value="subscribers">Subscribers</option>
              <option value="views">Views</option>
            </TextField>
          </Grid>
          <Grid item xs={6}>
            <TextField
              fullWidth
              select
              label="Condition"
              value={newRule.condition}
              onChange={(e) => handleFieldChange('condition', e.target.value)}
              SelectProps={{ native: true }}
            >
              <option value="greater_than">Greater Than</option>
              <option value="less_than">Less Than</option>
              <option value="milestone">Milestone</option>
              <option value="surge">Surge Detection</option>
            </TextField>
          </Grid>
          <Grid item xs={12}>
            <Typography gutterBottom>
              Threshold: {newRule.threshold}
              {newRule.type === 'growth' || newRule.type === 'engagement' ? '%' : ''}
            </Typography>
            <Slider
              value={newRule.threshold}
              onChange={(e, value) => handleFieldChange('threshold', value)}
              min={1}
              max={100}
              step={1}
              marks={[
                { value: 1, label: '1' },
                { value: 50, label: '50' },
                { value: 100, label: '100' },
              ]}
            />
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button 
          onClick={onSubmit} 
          variant="contained"
          disabled={!newRule.name.trim()}
        >
          Create Rule
        </Button>
      </DialogActions>
    </Dialog>
  );
});

NewRuleDialog.displayName = 'NewRuleDialog';

export default NewRuleDialog;