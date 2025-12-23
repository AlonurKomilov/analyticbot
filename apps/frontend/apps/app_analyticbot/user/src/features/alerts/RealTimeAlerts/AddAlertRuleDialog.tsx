/**
 * AddAlertRuleDialog Component
 *
 * Dialog for creating new alert rules with form validation.
 */

import React, { useState } from 'react';
import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    TextField,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    FormControlLabel,
    Switch,
    Box,
    Alert,
    CircularProgress
} from '@mui/material';

interface AddAlertRuleDialogProps {
    open: boolean;
    onClose: () => void;
    onSave: (rule: AlertRuleFormData) => Promise<void>;
}

export interface AlertRuleFormData {
    rule_name: string;
    metric_type: string;
    threshold_value: number;
    comparison: string;
    enabled: boolean;
    notification_channels: string[];
}

const metricTypes = [
    { value: 'engagement', label: 'Engagement Rate' },
    { value: 'growth', label: 'Subscriber Growth' },
    { value: 'views', label: 'Views' },
    { value: 'likes', label: 'Likes' },
    { value: 'comments', label: 'Comments' },
    { value: 'shares', label: 'Shares' },
    { value: 'reach', label: 'Reach' },
];

const comparisonTypes = [
    { value: 'above', label: 'Above (>)' },
    { value: 'below', label: 'Below (<)' },
    { value: 'equals', label: 'Equals (=)' },
];

const AddAlertRuleDialog: React.FC<AddAlertRuleDialogProps> = ({ open, onClose, onSave }) => {
    const [formData, setFormData] = useState<AlertRuleFormData>({
        rule_name: '',
        metric_type: 'engagement',
        threshold_value: 0,
        comparison: 'below',
        enabled: true,
        notification_channels: []
    });

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleChange = (field: keyof AlertRuleFormData) => (
        event: React.ChangeEvent<HTMLInputElement> | { target: { value: unknown } }
    ) => {
        let value: any;

        // Handle different event types
        if ('target' in event) {
            if ('type' in event.target && event.target.type === 'checkbox') {
                value = (event.target as HTMLInputElement).checked;
            } else {
                value = event.target.value;
            }
        }

        setFormData(prev => ({
            ...prev,
            [field]: value
        }));
        setError(null);
    };

    const validateForm = (): boolean => {
        if (!formData.rule_name.trim()) {
            setError('Rule name is required');
            return false;
        }
        if (formData.threshold_value === undefined || formData.threshold_value === null) {
            setError('Threshold value is required');
            return false;
        }
        return true;
    };

    const handleSave = async () => {
        if (!validateForm()) {
            return;
        }

        setLoading(true);
        setError(null);

        try {
            await onSave(formData);

            // Reset form
            setFormData({
                rule_name: '',
                metric_type: 'engagement',
                threshold_value: 0,
                comparison: 'below',
                enabled: true,
                notification_channels: []
            });

            onClose();
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to create rule');
        } finally {
            setLoading(false);
        }
    };

    const handleCancel = () => {
        setError(null);
        setFormData({
            rule_name: '',
            metric_type: 'engagement',
            threshold_value: 0,
            comparison: 'below',
            enabled: true,
            notification_channels: []
        });
        onClose();
    };

    return (
        <Dialog
            open={open}
            onClose={handleCancel}
            maxWidth="sm"
            fullWidth
            aria-labelledby="add-rule-dialog-title"
        >
            <DialogTitle id="add-rule-dialog-title">
                Add New Alert Rule
            </DialogTitle>
            <DialogContent dividers>
                {error && (
                    <Alert severity="error" sx={{ mb: 2 }}>
                        {error}
                    </Alert>
                )}

                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
                    <TextField
                        label="Rule Name"
                        value={formData.rule_name}
                        onChange={handleChange('rule_name')}
                        fullWidth
                        required
                        placeholder="e.g., Low Engagement Alert"
                        helperText="Give your rule a descriptive name"
                    />

                    <FormControl fullWidth>
                        <InputLabel id="metric-type-label">Metric Type</InputLabel>
                        <Select
                            labelId="metric-type-label"
                            value={formData.metric_type}
                            onChange={handleChange('metric_type') as any}
                            label="Metric Type"
                        >
                            {metricTypes.map(type => (
                                <MenuItem key={type.value} value={type.value}>
                                    {type.label}
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>

                    <FormControl fullWidth>
                        <InputLabel id="comparison-label">Comparison</InputLabel>
                        <Select
                            labelId="comparison-label"
                            value={formData.comparison}
                            onChange={handleChange('comparison') as any}
                            label="Comparison"
                        >
                            {comparisonTypes.map(type => (
                                <MenuItem key={type.value} value={type.value}>
                                    {type.label}
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>

                    <TextField
                        label="Threshold Value"
                        type="number"
                        value={formData.threshold_value}
                        onChange={handleChange('threshold_value')}
                        fullWidth
                        required
                        helperText="Alert triggers when metric crosses this value"
                        inputProps={{
                            step: "0.01"
                        }}
                    />

                    <FormControlLabel
                        control={
                            <Switch
                                checked={formData.enabled}
                                onChange={handleChange('enabled') as any}
                                color="primary"
                            />
                        }
                        label="Enable rule immediately"
                    />
                </Box>
            </DialogContent>
            <DialogActions>
                <Button
                    onClick={handleCancel}
                    disabled={loading}
                    color="inherit"
                >
                    Cancel
                </Button>
                <Button
                    onClick={handleSave}
                    variant="contained"
                    color="primary"
                    disabled={loading}
                    startIcon={loading && <CircularProgress size={16} />}
                >
                    {loading ? 'Creating...' : 'Create Rule'}
                </Button>
            </DialogActions>
        </Dialog>
    );
};

export default AddAlertRuleDialog;
