/**
 * NewRuleDialog Component
 *
 * Memoized dialog for creating new alert rules with validation,
 * metric type selection, condition configuration, and threshold settings.
 */

import React from 'react';
import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    TextField,
    Grid,
    Typography,
    Slider
} from '@mui/material';
import { Button } from '@shared/components';

interface AlertRule {
    name: string;
    type: 'growth' | 'engagement' | 'subscribers' | 'views';
    condition: 'greater_than' | 'less_than' | 'milestone' | 'surge';
    threshold: number;
    enabled: boolean;
}

interface NewRuleDialogProps {
    open?: boolean;
    onClose: () => void;
    onSubmit: () => void;
    newRule?: AlertRule;
    onRuleChange?: (rule: AlertRule) => void;
}

const NewRuleDialog: React.FC<NewRuleDialogProps> = React.memo(({
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
    const handleFieldChange = (field: keyof AlertRule, value: any) => {
        onRuleChange?.({ ...newRule, [field]: value } as AlertRule);
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
                            onChange={(_e, value) => handleFieldChange('threshold', value)}
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
                <Button variant="secondary" onClick={onClose}>Cancel</Button>
                <Button
                    onClick={onSubmit}
                    variant="primary"
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
