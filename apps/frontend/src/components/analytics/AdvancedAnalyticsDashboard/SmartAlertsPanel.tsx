/**
 * SmartAlertsPanel Component
 *
 * Displays intelligent alerts and recommendations based on channel analytics.
 * Features collapsible UI and alert dismissal functionality.
 */

import React, { useState, useEffect } from 'react';
import {
    Box,
    Paper,
    Typography,
    IconButton,
    Tooltip
} from '@mui/material';
import {
    ExpandMore as ExpandMoreIcon,
    ExpandLess as ExpandLessIcon,
    Settings as SettingsIcon
} from '@mui/icons-material';
import AlertsList from '../../alerts/RealTimeAlerts/AlertsList';
import RuleManager from '../../alerts/RealTimeAlerts/RuleManager';

interface Alert {
    id: string;
    severity: 'error' | 'warning' | 'info';
    title: string;
    message: string;
    timestamp: string;
}

// Simple alert generator (replace with actual util later)
const generateSmartAlerts = (): Alert[] => {
    return [];
};

const SmartAlertsPanel: React.FC = () => {
    const [alerts, setAlerts] = useState<Alert[]>([]);
    const [isExpanded, setIsExpanded] = useState(true);
    const [showRuleManager, setShowRuleManager] = useState(false);

    // Generate alerts on mount and periodically
    useEffect(() => {
        const fetchAlerts = () => {
            const newAlerts = generateSmartAlerts();
            setAlerts(newAlerts);
        };

        fetchAlerts();

        // Refresh alerts every 5 minutes
        const interval = setInterval(fetchAlerts, 5 * 60 * 1000);

        return () => clearInterval(interval);
    }, []);

    const handleDeleteAlert = (alertId: string) => {
        setAlerts((prev) => prev.filter((alert) => alert.id !== alertId));
    };

    const handleToggleExpand = () => {
        setIsExpanded((prev) => !prev);
    };

    return (
        <>
            <Paper sx={{ p: 3 }}>
                {/* Header */}
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="h6" fontWeight={600}>
                            Smart Alerts
                        </Typography>
                        {alerts.length > 0 && (
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

                {/* Alerts List */}
                <AlertsList
                    alerts={alerts}
                    isExpanded={isExpanded}
                    onDeleteAlert={handleDeleteAlert}
                    maxAlerts={5}
                />
            </Paper>

            {/* Rule Manager Dialog */}
            <RuleManager
                open={showRuleManager}
                onClose={() => setShowRuleManager(false)}
                rules={[]}
                onToggleRule={() => {}}
                onAddRule={() => {}}
            />
        </>
    );
};

export default SmartAlertsPanel;
