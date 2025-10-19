import React, { useEffect, useState } from 'react';
import {
    Paper,
    Typography,
    Box,
    Chip,
    Stack,
    Accordion,
    AccordionSummary,
    AccordionDetails,
    Alert
} from '@mui/material';
import {
    ExpandMore as ExpandMoreIcon,
    BugReport as BugIcon
} from '@mui/icons-material';
import { useAuthStore, useChannelStore, usePostStore, useAnalyticsStore, useUIStore } from '../stores';

interface ConsoleMessage {
    message: string;
    timestamp: string;
}

interface StoreStatus {
    dataSource: string;
    channelsCount: number;
    scheduledPostsCount: number;
    user: JSX.Element;
    plan: JSX.Element;
    analyticsData: JSX.Element;
}

const DiagnosticPanel: React.FC = () => {
    // Access all domain stores for diagnostic purposes
    const { user } = useAuthStore();
    const { channels } = useChannelStore();
    const { scheduledPosts } = usePostStore();
    const { postDynamics } = useAnalyticsStore();
    const { dataSource } = useUIStore();
    const [consoleErrors, setConsoleErrors] = useState<ConsoleMessage[]>([]);
    const [consoleWarnings, setConsoleWarnings] = useState<ConsoleMessage[]>([]);

    // Capture console errors and warnings
    useEffect(() => {
        const originalError = console.error;
        const originalWarn = console.warn;

        console.error = (...args: any[]): void => {
            setConsoleErrors(prev => [...prev.slice(-4), {
                message: args.join(' '),
                timestamp: new Date().toLocaleTimeString()
            }]);
            originalError(...args);
        };

        console.warn = (...args: any[]): void => {
            setConsoleWarnings(prev => [...prev.slice(-4), {
                message: args.join(' '),
                timestamp: new Date().toLocaleTimeString()
            }]);
            originalWarn(...args);
        };

        return () => {
            console.error = originalError;
            console.warn = originalWarn;
        };
    }, []);

    const getStoreStatus = (): StoreStatus => {
        const loadedIcon = <><span aria-hidden="true">✅</span> Loaded</>;
        const notLoadedIcon = <><span aria-hidden="true">❌</span> Not loaded</>;

        return {
            dataSource: dataSource,
            channelsCount: channels?.length || 0,
            scheduledPostsCount: scheduledPosts?.length || 0,
            user: user ? loadedIcon : notLoadedIcon,
            plan: notLoadedIcon, // Plan data not yet in domain stores
            analyticsData: postDynamics ? loadedIcon : notLoadedIcon,
        };
    };

    const storeStatus = getStoreStatus();

    return (
        <Paper sx={{ p: 2, mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <BugIcon color="primary" />
                <Typography variant="h6">System Diagnostics</Typography>
                <Chip
                    label={consoleErrors.length > 0 ? `${consoleErrors.length} Errors` : "No Errors"}
                    color={consoleErrors.length > 0 ? "error" : "success"}
                    size="small"
                />
                <Chip
                    label={consoleWarnings.length > 0 ? `${consoleWarnings.length} Warnings` : "No Warnings"}
                    color={consoleWarnings.length > 0 ? "warning" : "success"}
                    size="small"
                />
            </Box>

            <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography>Store State</Typography>
                </AccordionSummary>
                <AccordionDetails>
                    <Stack spacing={1}>
                        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                            <Chip label={`Data Source: ${storeStatus.dataSource}`} size="small" />
                            <Chip label={`Channels: ${storeStatus.channelsCount}`} size="small" />
                            <Chip label={`Posts: ${storeStatus.scheduledPostsCount}`} size="small" />
                        </Box>
                        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                            <Chip label="User:" size="small" />
                            {storeStatus.user}
                            <Chip label="Plan:" size="small" />
                            {storeStatus.plan}
                            <Chip label="Analytics:" size="small" />
                            {storeStatus.analyticsData}
                        </Box>
                    </Stack>
                </AccordionDetails>
            </Accordion>

            {consoleErrors.length > 0 && (
                <Accordion>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <Typography color="error">Console Errors ({consoleErrors.length})</Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                        <Stack spacing={1}>
                            {consoleErrors.slice(-3).map((error, index) => (
                                <Alert key={index} severity="error" sx={{ '& .MuiAlert-message': { width: '100%' } }}>
                                    <Typography variant="caption" color="text.secondary">
                                        {error.timestamp}
                                    </Typography>
                                    <Typography variant="body2">
                                        {error.message}
                                    </Typography>
                                </Alert>
                            ))}
                        </Stack>
                    </AccordionDetails>
                </Accordion>
            )}

            {consoleWarnings.length > 0 && (
                <Accordion>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <Typography color="warning.main">Console Warnings ({consoleWarnings.length})</Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                        <Stack spacing={1}>
                            {consoleWarnings.slice(-3).map((warning, index) => (
                                <Alert key={index} severity="warning" sx={{ '& .MuiAlert-message': { width: '100%' } }}>
                                    <Typography variant="caption" color="text.secondary">
                                        {warning.timestamp}
                                    </Typography>
                                    <Typography variant="body2">
                                        {warning.message}
                                    </Typography>
                                </Alert>
                            ))}
                        </Stack>
                    </AccordionDetails>
                </Accordion>
            )}

            <Typography variant="caption" color="text.secondary" sx={{ mt: 2, display: 'block' }}>
                React {React.version} • Last updated: {new Date().toLocaleTimeString()}
            </Typography>
        </Paper>
    );
};

export default DiagnosticPanel;
