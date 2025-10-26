/**
 * RuleManager Component
 *
 * Dialog for managing alert rules - enable/disable existing rules
 * and add new custom alert rules.
 */

import React from 'react';
import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    List,
    ListItem,
    ListItemText,
    Switch,
    FormControlLabel,
    Box,
    Typography,
    Divider
} from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';

interface AlertRule {
    id: string;
    name: string;
    description: string;
    enabled: boolean;
}

interface RuleManagerProps {
    open: boolean;
    onClose: () => void;
    rules: AlertRule[];
    onToggleRule: (ruleId: string) => void;
    onAddRule: () => void;
}

const RuleManager: React.FC<RuleManagerProps> = React.memo(({
    open,
    onClose,
    rules,
    onToggleRule,
    onAddRule
}) => {
    return (
        <Dialog
            open={open}
            onClose={onClose}
            maxWidth="sm"
            fullWidth
            aria-labelledby="rule-manager-dialog-title"
        >
            <DialogTitle id="rule-manager-dialog-title">
                Manage Alert Rules
            </DialogTitle>
            <DialogContent dividers>
                <List>
                    {rules.map((rule) => (
                        <ListItem key={rule.id} divider>
                            <ListItemText
                                primary={
                                    <Typography variant="subtitle2" fontWeight={600}>
                                        {rule.name}
                                    </Typography>
                                }
                                secondary={rule.description}
                            />
                            <FormControlLabel
                                control={
                                    <Switch
                                        checked={rule.enabled}
                                        onChange={() => onToggleRule(rule.id)}
                                        color="primary"
                                    />
                                }
                                label={rule.enabled ? 'Enabled' : 'Disabled'}
                                labelPlacement="start"
                            />
                        </ListItem>
                    ))}
                </List>

                <Divider sx={{ my: 2 }} />

                <Box sx={{ display: 'flex', justifyContent: 'center' }}>
                    <Button
                        variant="outlined"
                        startIcon={<AddIcon />}
                        onClick={onAddRule}
                    >
                        Add New Rule
                    </Button>
                </Box>
            </DialogContent>
            <DialogActions>
                <Button onClick={onClose} color="primary" variant="contained">
                    Done
                </Button>
            </DialogActions>
        </Dialog>
    );
});

RuleManager.displayName = 'RuleManager';

export default RuleManager;
