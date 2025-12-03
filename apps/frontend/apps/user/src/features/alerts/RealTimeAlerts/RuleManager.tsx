/**
 * RuleManager Component
 *
 * Dialog for managing alert rules - enable/disable existing rules
 * and add new custom alert rules.
 */

import React, { useState } from 'react';
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
    Divider,
    CircularProgress
} from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';
import AddAlertRuleDialog, { AlertRuleFormData } from './AddAlertRuleDialog';

interface AlertRule {
    id: string;
    name: string;
    description: string;
    enabled: boolean;
    isDefault?: boolean;
    personalized?: boolean;
    baseline_value?: number;
}

interface RuleManagerProps {
    open: boolean;
    onClose: () => void;
    rules: AlertRule[];
    onToggleRule: (ruleId: string) => void;
    onAddRule: (rule: AlertRuleFormData) => Promise<void>;
}

const RuleManager: React.FC<RuleManagerProps> = React.memo(({
    open,
    onClose,
    rules,
    onToggleRule,
    onAddRule
}) => {
    const [showAddDialog, setShowAddDialog] = useState(false);

    const handleAddClick = () => {
        setShowAddDialog(true);
    };

    const handleAddClose = () => {
        setShowAddDialog(false);
    };

    const handleAddSave = async (rule: AlertRuleFormData) => {
        await onAddRule(rule);
        setShowAddDialog(false);
    };

    // Separate default and custom rules
    const defaultRules = rules.filter(r => r.isDefault);
    const customRules = rules.filter(r => !r.isDefault);
    const customRulesCount = customRules.length;
    const maxCustomRules = 10;
    const isPersonalized = defaultRules.some(r => r.personalized);

    return (
        <>
            <Dialog
                open={open}
                onClose={onClose}
                maxWidth="md"
                fullWidth
                aria-labelledby="rule-manager-dialog-title"
            >
                <DialogTitle id="rule-manager-dialog-title">
                    Manage Alert Rules
                </DialogTitle>
                <DialogContent dividers>
                    {/* Default Smart Rules Section */}
                    <Box sx={{ mb: 3 }}>
                        <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
                            🎯 Smart Alert Rules {isPersonalized ? '(Personalized for Your Channel)' : '(Pre-configured)'}
                        </Typography>
                        <Typography variant="caption" color="text.secondary" sx={{ mb: 2, display: 'block' }}>
                            {isPersonalized
                                ? 'Thresholds calculated based on your channel size and performance history'
                                : 'Best practices alert rules - toggle on/off as needed'
                            }
                        </Typography>
                        {defaultRules.length === 0 ? (
                            <Box sx={{ textAlign: 'center', py: 3, bgcolor: 'action.hover', borderRadius: 1 }}>
                                <CircularProgress size={24} />
                                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                                    Loading personalized rules...
                                </Typography>
                            </Box>
                        ) : (
                            <List>
                                {defaultRules.map((rule) => (
                                    <ListItem key={rule.id} divider sx={{ bgcolor: 'action.hover', borderRadius: 1, mb: 1 }}>
                                        <ListItemText
                                            primary={
                                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                    <Typography variant="subtitle2" fontWeight={600}>
                                                        {rule.name}
                                                    </Typography>
                                                    {rule.personalized && (
                                                        <Typography
                                                            variant="caption"
                                                            sx={{
                                                                px: 1,
                                                                py: 0.25,
                                                                bgcolor: 'primary.main',
                                                                color: 'white',
                                                                borderRadius: 0.5,
                                                                fontSize: '0.65rem'
                                                            }}
                                                        >
                                                            PERSONALIZED
                                                        </Typography>
                                                    )}
                                                </Box>
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
                                            label={rule.enabled ? 'ON' : 'OFF'}
                                            labelPlacement="start"
                                        />
                                    </ListItem>
                                ))}
                            </List>
                        )}
                    </Box>

                    <Divider sx={{ my: 3 }} />

                    {/* Custom Rules Section */}
                    <Box>
                        <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
                            ⚙️ Custom Rules ({customRulesCount}/{maxCustomRules})
                        </Typography>
                        <Typography variant="caption" color="text.secondary" sx={{ mb: 2, display: 'block' }}>
                            Create your own alert rules with custom thresholds
                        </Typography>

                        {customRules.length === 0 ? (
                            <Box sx={{ textAlign: 'center', py: 3, bgcolor: 'action.hover', borderRadius: 1 }}>
                                <Typography variant="body2" color="text.secondary">
                                    No custom rules yet. Create your first custom rule below!
                                </Typography>
                            </Box>
                        ) : (
                            <List>
                                {customRules.map((rule) => (
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
                                            label={rule.enabled ? 'ON' : 'OFF'}
                                            labelPlacement="start"
                                        />
                                    </ListItem>
                                ))}
                            </List>
                        )}

                        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
                            <Button
                                variant="outlined"
                                startIcon={<AddIcon />}
                                onClick={handleAddClick}
                                disabled={customRulesCount >= maxCustomRules}
                            >
                                {customRulesCount >= maxCustomRules
                                    ? `Maximum ${maxCustomRules} Rules Reached`
                                    : 'Add Custom Rule'
                                }
                            </Button>
                        </Box>
                    </Box>
                </DialogContent>
                <DialogActions>
                    <Button onClick={onClose} color="primary" variant="contained">
                        Done
                    </Button>
                </DialogActions>
            </Dialog>

            <AddAlertRuleDialog
                open={showAddDialog}
                onClose={handleAddClose}
                onSave={handleAddSave}
            />
        </>
    );
});

RuleManager.displayName = 'RuleManager';

export default RuleManager;
