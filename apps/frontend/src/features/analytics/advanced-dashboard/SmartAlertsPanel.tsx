/**
 * SmartAlertsPanel Component
 *
 * ✅ UPDATED (Nov 21, 2025): Now connected to real alert system via useAlerts hook
 * ✅ UPDATED (Nov 21, 2025): Added full alert rule management with backend integration
 *
 * Displays intelligent alerts and recommendations based on channel analytics.
 * Features collapsible UI, alert dismissal, real-time updates, and rule management.
 */

import React, { useState, useEffect } from 'react';
import {
    Box,
    Paper,
    Typography,
    IconButton,
    Tooltip,
    CircularProgress
} from '@mui/material';
import {
    ExpandMore as ExpandMoreIcon,
    ExpandLess as ExpandLessIcon,
    Settings as SettingsIcon,
    Refresh as RefreshIcon
} from '@mui/icons-material';
import { AlertsList } from '@features/alerts';
import { RuleManager } from '@features/alerts';
import { useAlerts } from '@features/alerts/hooks';
import { AlertsAPI } from '@features/ai-services/api';
import { AlertRuleFormData } from '@features/alerts/RealTimeAlerts/AddAlertRuleDialog';

interface SmartAlertsPanelProps {
    channelId?: string;
}

interface AlertRule {
    id: string;
    name: string;
    description: string;
    enabled: boolean;
    isDefault?: boolean;
    personalized?: boolean;
    baseline_value?: number;
    threshold?: number;
}

const MAX_CUSTOM_RULES = 10;

const SmartAlertsPanel: React.FC<SmartAlertsPanelProps> = ({ channelId }) => {
    const [isExpanded, setIsExpanded] = useState(true);
    const [showRuleManager, setShowRuleManager] = useState(false);
    const [rules, setRules] = useState<AlertRule[]>([]);
    const [rulesLoading, setRulesLoading] = useState(false);
    const [rulesPersonalized, setRulesPersonalized] = useState(false);

    // Connect to real alert system
    const {
        alerts,
        loading,
        error,
        refresh
    } = useAlerts({
        channelId: channelId || '',
        autoFetch: !!channelId,
        refreshInterval: 5 * 60 * 1000  // 5 minutes
    });

    // Load alert rules when panel opens or channelId changes
    useEffect(() => {
        if (channelId && showRuleManager) {
            loadRules();
        }
    }, [channelId, showRuleManager]);

    const loadRules = async () => {
        if (!channelId) return;

        setRulesLoading(true);
        try {
            // Fetch smart personalized rules
            const smartResult = await AlertsAPI.getSmartAlertRules(channelId);
            const smartRules = (smartResult.rules || []).map((r: any) => ({
                ...r,
                isDefault: true,  // Smart rules act as defaults
                personalized: r.personalized || false,
            }));

            // Fetch custom user-created rules
            const customResult = await AlertsAPI.getAlertRules(channelId);
            const customRules = (customResult.rules || []).map((r: any) => ({
                ...r,
                isDefault: false,
                personalized: false,
            }));

            // Merge smart rules with custom rules
            const allRules = [...smartRules, ...customRules];

            setRules(allRules);
            setRulesPersonalized(smartResult.personalized || false);
        } catch (err) {
            console.error('Failed to load alert rules:', err);
            // Fallback to empty rules on error
            setRules([]);
            setRulesPersonalized(false);
        } finally {
            setRulesLoading(false);
        }
    };

    const handleDeleteAlert = (alertId: string) => {
        // Alert dismissed - in production, you might want to acknowledge it in backend
        console.log('Alert dismissed:', alertId);
    };

    const handleToggleExpand = () => {
        setIsExpanded((prev) => !prev);
    };

    const handleRefresh = async () => {
        if (channelId) {
            await refresh();
            await loadRules();
        }
    };

    const handleToggleRule = async (ruleId: string) => {
        if (!channelId) return;

        try {
            // Find current rule state
            const rule = rules.find(r => r.id === ruleId);
            if (!rule) return;

            // Toggle in backend
            await AlertsAPI.updateAlertRule(channelId, ruleId, !rule.enabled);

            // Update local state
            setRules(prev => prev.map(r =>
                r.id === ruleId ? { ...r, enabled: !r.enabled } : r
            ));

            // Refresh alerts
            await refresh();
        } catch (err) {
            console.error('Failed to toggle rule:', err);
        }
    };

    const handleAddRule = async (rule: AlertRuleFormData) => {
        if (!channelId) return;

        // Check custom rule limit (excluding default rules)
        const customRulesCount = rules.filter(r => !r.isDefault).length;
        if (customRulesCount >= MAX_CUSTOM_RULES) {
            throw new Error(`Maximum ${MAX_CUSTOM_RULES} custom rules allowed. Delete existing rules to add new ones.`);
        }

        try {
            // Create rule in backend
            const result = await AlertsAPI.createAlertRule(channelId, rule);

            // Add to local state
            const newRule: AlertRule = {
                id: result.rule?.id || `${Date.now()}`,
                name: rule.rule_name,
                description: result.rule?.description || `${rule.metric_type} ${rule.comparison} ${rule.threshold_value}`,
                enabled: rule.enabled,
                isDefault: false,
            };
            setRules(prev => [...prev, newRule]);

            // Refresh alerts
            await refresh();
        } catch (err) {
            console.error('Failed to create rule:', err);
            throw err; // Re-throw to show error in dialog
        }
    };

    // Show message if no channel selected
    if (!channelId) {
        return (
            <Paper sx={{ p: 3 }}>
                <Typography variant="body2" color="text.secondary">
                    Select a channel to view smart alerts
                </Typography>
            </Paper>
        );
    }

    return (
        <>
            <Paper sx={{ p: 3 }}>
                {/* Header */}
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="h6" fontWeight={600}>
                            Smart Alerts
                        </Typography>
                        {loading && (
                            <CircularProgress size={16} sx={{ ml: 1 }} />
                        )}
                        {alerts.length > 0 && !loading && (
                            <Typography
                                variant="caption"
                                sx={{
                                    px: 1,
                                    py: 0.5,
                                    bgcolor: 'error.main',
                                    color: 'white',
                                    borderRadius: 1,
                                    fontWeight: 600
                                }}
                            >
                                {alerts.length}
                            </Typography>
                        )}
                    </Box>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                        <Tooltip title="Refresh alerts">
                            <IconButton
                                size="small"
                                onClick={handleRefresh}
                                disabled={loading}
                                aria-label="Refresh alerts"
                            >
                                <RefreshIcon />
                            </IconButton>
                        </Tooltip>
                        <Tooltip title="Manage alert rules">
                            <IconButton
                                size="small"
                                onClick={() => setShowRuleManager(true)}
                                aria-label="Manage alert rules"
                            >
                                <SettingsIcon />
                            </IconButton>
                        </Tooltip>
                        <Tooltip title={isExpanded ? 'Collapse' : 'Expand'}>
                            <IconButton
                                size="small"
                                onClick={handleToggleExpand}
                                aria-label={isExpanded ? 'Collapse alerts' : 'Expand alerts'}
                            >
                                {isExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                            </IconButton>
                        </Tooltip>
                    </Box>
                </Box>

                {/* Error message */}
                {error && (
                    <Box sx={{ mb: 2 }}>
                        <Typography variant="body2" color="error">
                            {error}
                        </Typography>
                    </Box>
                )}

                {/* Empty state */}
                {!loading && alerts.length === 0 && !error && (
                    <Box sx={{ textAlign: 'center', py: 3 }}>
                        <Typography variant="body2" color="text.secondary">
                            No active alerts - your channel is performing well! 🎉
                        </Typography>
                    </Box>
                )}

                {/* Alerts List */}
                {alerts.length > 0 && (
                    <AlertsList
                        alerts={alerts}
                        isExpanded={isExpanded}
                        onDeleteAlert={handleDeleteAlert}
                        maxAlerts={5}
                    />
                )}
            </Paper>

            {/* Rule Manager Dialog */}
            <RuleManager
                open={showRuleManager}
                onClose={() => setShowRuleManager(false)}
                rules={rules}
                onToggleRule={handleToggleRule}
                onAddRule={handleAddRule}
            />
        </>
    );
};

export default SmartAlertsPanel;
