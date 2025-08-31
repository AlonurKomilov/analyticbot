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
import { useAppStore } from '../store/appStore';

const DiagnosticPanel = () => {
    const store = useAppStore();
    const [consoleErrors, setConsoleErrors] = useState([]);
    const [consoleWarnings, setConsoleWarnings] = useState([]);

    // Capture console errors and warnings
    useEffect(() => {
        const originalError = console.error;
        const originalWarn = console.warn;
        
        console.error = (...args) => {
            setConsoleErrors(prev => [...prev.slice(-4), {
                message: args.join(' '),
                timestamp: new Date().toLocaleTimeString()
            }]);
            originalError(...args);
        };

        console.warn = (...args) => {
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

    const getStoreStatus = () => {
        return {
            dataSource: store.dataSource || 'unknown',
            channelsCount: store.channels?.length || 0,
            scheduledPostsCount: store.scheduledPosts?.length || 0,
            user: store.user ? '✅ Loaded' : '❌ Not loaded',
            plan: store.plan ? '✅ Loaded' : '❌ Not loaded',
            analyticsData: store.analytics?.postDynamics ? '✅ Loaded' : '❌ Not loaded',
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
                            <Chip label={`User: ${storeStatus.user}`} size="small" />
                            <Chip label={`Plan: ${storeStatus.plan}`} size="small" />
                            <Chip label={`Analytics: ${storeStatus.analyticsData}`} size="small" />
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
                                <Alert key={index} severity="error" size="small">
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
                                <Alert key={index} severity="warning" size="small">
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
