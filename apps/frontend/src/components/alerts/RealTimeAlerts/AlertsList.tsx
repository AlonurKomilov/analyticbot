/**
 * AlertsList Component
 *
 * Displays a list of active alerts with expandable/collapsible UI.
 * Optimized with React.memo to prevent unnecessary re-renders.
 */

import React from 'react';
import {
    Box,
    Paper,
    Typography,
    IconButton,
    Chip,
    Tooltip,
    Collapse
} from '@mui/material';
import {
    Error as ErrorIcon,
    Warning as WarningIcon,
    Info as InfoIcon,
    Delete as DeleteIcon
} from '@mui/icons-material';

interface Alert {
    id: string;
    severity: 'error' | 'warning' | 'info';
    title: string;
    message: string;
    timestamp: string;
}

interface AlertsListProps {
    alerts: Alert[];
    isExpanded: boolean;
    onDeleteAlert: (id: string) => void;
    maxAlerts?: number;
}

const severityConfig = {
    error: { icon: ErrorIcon, color: 'error' as const },
    warning: { icon: WarningIcon, color: 'warning' as const },
    info: { icon: InfoIcon, color: 'info' as const }
};

const AlertsList: React.FC<AlertsListProps> = React.memo(({
    alerts,
    isExpanded,
    onDeleteAlert,
    maxAlerts = 5
}) => {
    const displayedAlerts = alerts.slice(0, maxAlerts);

    return (
        <Collapse in={isExpanded}>
            <Box sx={{ mt: 2 }}>
                {displayedAlerts.map((alert) => {
                    const { icon: Icon, color } = severityConfig[alert.severity];

                    return (
                        <Paper
                            key={alert.id}
                            elevation={1}
                            sx={{
                                p: 2,
                                mb: 1,
                                display: 'flex',
                                alignItems: 'flex-start',
                                gap: 2
                            }}
                        >
                            <Icon color={color} />
                            <Box sx={{ flex: 1 }}>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                                    <Typography variant="subtitle2" fontWeight={600}>
                                        {alert.title}
                                    </Typography>
                                    <Chip
                                        label={alert.severity.toUpperCase()}
                                        size="small"
                                        color={color}
                                    />
                                </Box>
                                <Typography variant="body2" color="text.secondary" paragraph>
                                    {alert.message}
                                </Typography>
                                <Typography variant="caption" color="text.disabled">
                                    {alert.timestamp}
                                </Typography>
                            </Box>
                            <Tooltip title="Dismiss alert">
                                <IconButton
                                    size="small"
                                    onClick={() => onDeleteAlert(alert.id)}
                                    aria-label={`Delete alert: ${alert.title}`}
                                >
                                    <DeleteIcon fontSize="small" />
                                </IconButton>
                            </Tooltip>
                        </Paper>
                    );
                })}
            </Box>
        </Collapse>
    );
});

AlertsList.displayName = 'AlertsList';

export default AlertsList;
