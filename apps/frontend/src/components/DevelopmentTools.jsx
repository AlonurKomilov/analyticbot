import React, { useState, useEffect } from 'react';
import {
    Box,
    Button,
    Card,
    CardContent,
    Typography,
    Switch,
    FormControlLabel,
    Chip,
    Alert,
    Collapse,
    IconButton
} from '@mui/material';
import {
    BugReport as BugIcon,
    Close as CloseIcon,
    Api as ApiIcon,
    Psychology as MockIcon
} from '@mui/icons-material';

/**
 * Development Tools Component
 * 
 * Only visible in development mode.
 * Provides tools for developers to test the TWA functionality.
 */
const DevelopmentTools = () => {
    const [isVisible, setIsVisible] = useState(false);
    const [useMockApi, setUseMockApi] = useState(false);
    
    useEffect(() => {
        // Only show in development
        const isDev = import.meta.env.DEV;
        setIsVisible(isDev);
        
        // Check current mock API setting
        const currentSetting = localStorage.getItem('useMockApi') === 'true';
        setUseMockApi(currentSetting);
    }, []);
    
    const handleToggleMockApi = () => {
        const newValue = !useMockApi;
        setUseMockApi(newValue);
        localStorage.setItem('useMockApi', newValue.toString());
        
        // Reload to apply changes
        setTimeout(() => {
            window.location.reload();
        }, 500);
    };
    
    const handleClearStorage = () => {
        localStorage.clear();
        sessionStorage.clear();
        window.location.reload();
    };
    
    if (!isVisible) return null;
    
    return (
        <Box
            position="fixed"
            bottom={16}
            right={16}
            zIndex={9999}
            sx={{
                '& .MuiCard-root': {
                    minWidth: 280,
                    maxWidth: 320
                }
            }}
        >
            <Collapse in={isVisible}>
                <Card variant="outlined" sx={{ bgcolor: 'rgba(0, 0, 0, 0.8)', color: 'white' }}>
                    <CardContent>
                        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                            <Box display="flex" alignItems="center" gap={1}>
                                <BugIcon color="warning" />
                                <Typography variant="h6" color="warning.main">
                                    Dev Tools
                                </Typography>
                            </Box>
                            <IconButton 
                                size="small" 
                                onClick={() => setIsVisible(false)}
                                sx={{ color: 'white' }}
                            >
                                <CloseIcon />
                            </IconButton>
                        </Box>
                        
                        <Box mb={2}>
                            <FormControlLabel
                                control={
                                    <Switch
                                        checked={useMockApi}
                                        onChange={handleToggleMockApi}
                                        color="warning"
                                    />
                                }
                                label={
                                    <Box display="flex" alignItems="center" gap={1}>
                                        {useMockApi ? <MockIcon /> : <ApiIcon />}
                                        <Typography variant="body2">
                                            {useMockApi ? 'Mock API' : 'Real API'}
                                        </Typography>
                                    </Box>
                                }
                            />
                        </Box>
                        
                        <Box mb={2}>
                            <Chip
                                label={`TWA: ${window.Telegram?.WebApp ? '✅' : '❌'}`}
                                variant="outlined"
                                size="small"
                                sx={{ mr: 1, color: 'white', borderColor: 'white' }}
                            />
                            <Chip
                                label={`API: ${useMockApi ? 'Mock' : 'Live'}`}
                                variant="outlined"
                                size="small"
                                color={useMockApi ? 'warning' : 'success'}
                                sx={{ color: 'white', borderColor: 'white' }}
                            />
                        </Box>
                        
                        <Button
                            fullWidth
                            variant="outlined"
                            size="small"
                            onClick={handleClearStorage}
                            sx={{ 
                                color: 'white', 
                                borderColor: 'white',
                                '&:hover': {
                                    borderColor: 'warning.main',
                                    color: 'warning.main'
                                }
                            }}
                        >
                            Clear Storage
                        </Button>
                        
                        {useMockApi && (
                            <Alert 
                                severity="info" 
                                sx={{ mt: 2, fontSize: '0.75rem' }}
                            >
                                Using mock data. Perfect for testing TWA features!
                            </Alert>
                        )}
                    </CardContent>
                </Card>
            </Collapse>
            
            {!isVisible && (
                <Button
                    variant="contained"
                    color="warning"
                    size="small"
                    onClick={() => setIsVisible(true)}
                    sx={{
                        minWidth: 'auto',
                        p: 1,
                        borderRadius: '50%'
                    }}
                >
                    <BugIcon />
                </Button>
            )}
        </Box>
    );
};

export default DevelopmentTools;
