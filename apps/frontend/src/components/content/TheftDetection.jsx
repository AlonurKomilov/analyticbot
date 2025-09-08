import React, { useState, useEffect } from 'react';
import {
    Box,
    Card,
    CardContent,
    CardHeader,
    Typography,
    Button,
    TextField,
    Alert,
    LinearProgress,
    Chip,
    List,
    ListItem,
    ListItemText,
    ListItemIcon,
    ListItemSecondaryAction,
    IconButton,
    Divider,
    Grid,
    Paper,
    Tooltip
} from '@mui/material';
import {
    Security as SecurityIcon,
    Warning as WarningIcon,
    Search as SearchIcon,
    Link as LinkIcon,
    Refresh as RefreshIcon,
    CheckCircle as CheckIcon,
    Error as ErrorIcon,
    Info as InfoIcon
} from '@mui/icons-material';
import { apiClient } from '../../utils/apiClient';

const TheftDetection = () => {
    const [contentHash, setContentHash] = useState('');
    const [scanning, setScanning] = useState(false);
    const [scanResults, setScanResults] = useState([]);
    const [error, setError] = useState(null);
    const [scanHistory, setScanHistory] = useState([]);
    const [stats, setStats] = useState({
        totalScans: 0,
        threatsDetected: 0,
        cleanScans: 0
    });

    // Load scan history on component mount
    useEffect(() => {
        loadScanHistory();
        loadStats();
    }, []);

    const loadScanHistory = async () => {
        try {
            // In a real implementation, this would fetch from API
            // For now, using mock data
            setScanHistory([
                {
                    id: 1,
                    contentHash: 'abc123...',
                    timestamp: new Date(Date.now() - 86400000),
                    status: 'clean',
                    matchCount: 0
                },
                {
                    id: 2,
                    contentHash: 'def456...',
                    timestamp: new Date(Date.now() - 172800000),
                    status: 'threat',
                    matchCount: 3
                }
            ]);
        } catch (error) {
            console.error('Failed to load scan history:', error);
        }
    };

    const loadStats = async () => {
        try {
            // In a real implementation, this would fetch from API
            setStats({
                totalScans: 25,
                threatsDetected: 3,
                cleanScans: 22
            });
        } catch (error) {
            console.error('Failed to load stats:', error);
        }
    };

    const scanForTheft = async () => {
        if (!contentHash.trim()) {
            setError('Please enter a content hash to scan');
            return;
        }

        setScanning(true);
        setError(null);
        setScanResults([]);

        try {
            // Mock API call - in real implementation, this would call:
            // const response = await apiClient.post('/api/v1/content-protection/detection/scan', { 
            //     content_hash: contentHash 
            // });
            
            // Simulate API delay
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            // Mock scan results
            const mockResults = [
                {
                    id: 1,
                    url: 'https://example-thief1.com/stolen-content',
                    platform: 'Website',
                    matchPercentage: 95,
                    lastSeen: new Date(Date.now() - 86400000),
                    status: 'confirmed'
                },
                {
                    id: 2,
                    url: 'https://social-platform.com/user/post/123',
                    platform: 'Social Media',
                    matchPercentage: 87,
                    lastSeen: new Date(Date.now() - 172800000),
                    status: 'suspected'
                },
                {
                    id: 3,
                    url: 'https://another-site.com/gallery/image',
                    platform: 'Image Gallery',
                    matchPercentage: 92,
                    lastSeen: new Date(Date.now() - 259200000),
                    status: 'confirmed'
                }
            ];

            setScanResults(mockResults);
            
            // Update scan history
            const newScan = {
                id: Date.now(),
                contentHash: contentHash,
                timestamp: new Date(),
                status: mockResults.length > 0 ? 'threat' : 'clean',
                matchCount: mockResults.length
            };
            
            setScanHistory(prev => [newScan, ...prev.slice(0, 9)]); // Keep last 10
            
            // Update stats
            setStats(prev => ({
                totalScans: prev.totalScans + 1,
                threatsDetected: prev.threatsDetected + (mockResults.length > 0 ? 1 : 0),
                cleanScans: prev.cleanScans + (mockResults.length === 0 ? 1 : 0)
            }));

        } catch (error) {
            console.error('Scan failed:', error);
            setError(error.message || 'Failed to scan for content theft');
        } finally {
            setScanning(false);
        }
    };

    const getSeverityColor = (matchPercentage) => {
        if (matchPercentage >= 90) return 'error';
        if (matchPercentage >= 70) return 'warning';
        return 'info';
    };

    const getStatusIcon = (status) => {
        switch (status) {
            case 'confirmed':
                return <ErrorIcon color="error" />;
            case 'suspected':
                return <WarningIcon color="warning" />;
            case 'clean':
                return <CheckIcon color="success" />;
            default:
                return <InfoIcon color="info" />;
        }
    };

    return (
        <Box sx={{ maxWidth: 1000, mx: 'auto', my: 3 }}>
            {/* Header Card */}
            <Card sx={{ mb: 3 }}>
                <CardHeader
                    avatar={<SecurityIcon color="primary" />}
                    title="Content Theft Detection"
                    subheader="Scan content hashes to detect unauthorized usage across the web"
                />
                
                <CardContent>
                    {/* Stats Overview */}
                    <Grid container spacing={2} sx={{ mb: 3 }}>
                        <Grid item xs={12} md={4}>
                            <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'primary.50' }}>
                                <Typography variant="h4" color="primary">
                                    {stats.totalScans}
                                </Typography>
                                <Typography variant="body2" color="textSecondary">
                                    Total Scans
                                </Typography>
                            </Paper>
                        </Grid>
                        <Grid item xs={12} md={4}>
                            <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'error.50' }}>
                                <Typography variant="h4" color="error">
                                    {stats.threatsDetected}
                                </Typography>
                                <Typography variant="body2" color="textSecondary">
                                    Threats Detected
                                </Typography>
                            </Paper>
                        </Grid>
                        <Grid item xs={12} md={4}>
                            <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'success.50' }}>
                                <Typography variant="h4" color="success">
                                    {stats.cleanScans}
                                </Typography>
                                <Typography variant="body2" color="textSecondary">
                                    Clean Scans
                                </Typography>
                            </Paper>
                        </Grid>
                    </Grid>

                    {/* Scan Input */}
                    <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
                        <TextField
                            fullWidth
                            label="Content Hash"
                            placeholder="Enter SHA-256 hash of your content"
                            value={contentHash}
                            onChange={(e) => setContentHash(e.target.value)}
                            disabled={scanning}
                        />
                        <Button
                            variant="contained"
                            onClick={scanForTheft}
                            disabled={scanning || !contentHash.trim()}
                            startIcon={scanning ? <RefreshIcon /> : <SearchIcon />}
                            sx={{ minWidth: 120 }}
                        >
                            {scanning ? 'Scanning...' : 'Scan'}
                        </Button>
                    </Box>

                    {/* Progress */}
                    {scanning && (
                        <Box sx={{ mb: 3 }}>
                            <Typography variant="body2" color="textSecondary" gutterBottom>
                                Scanning web platforms for unauthorized usage...
                            </Typography>
                            <LinearProgress />
                        </Box>
                    )}

                    {/* Error Display */}
                    {error && (
                        <Alert severity="error" sx={{ mb: 3 }}>
                            {error}
                        </Alert>
                    )}
                </CardContent>
            </Card>

            {/* Scan Results */}
            {scanResults.length > 0 && (
                <Card sx={{ mb: 3 }}>
                    <CardHeader
                        title="Scan Results"
                        subheader={`Found ${scanResults.length} potential matches`}
                        action={
                            <Chip 
                                label="Threats Detected" 
                                color="error" 
                                icon={<WarningIcon />} 
                            />
                        }
                    />
                    
                    <CardContent>
                        <List>
                            {scanResults.map((match, index) => (
                                <React.Fragment key={match.id}>
                                    <ListItem>
                                        <ListItemIcon>
                                            {getStatusIcon(match.status)}
                                        </ListItemIcon>
                                        <ListItemText
                                            primary={
                                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                    <Typography variant="body1">
                                                        {match.url}
                                                    </Typography>
                                                    <Chip 
                                                        label={`${match.matchPercentage}% match`}
                                                        size="small"
                                                        color={getSeverityColor(match.matchPercentage)}
                                                    />
                                                </Box>
                                            }
                                            secondary={
                                                <Box>
                                                    <Typography variant="body2" color="textSecondary">
                                                        Platform: {match.platform} • 
                                                        Last seen: {match.lastSeen.toLocaleDateString()} • 
                                                        Status: {match.status}
                                                    </Typography>
                                                </Box>
                                            }
                                        />
                                        <ListItemSecondaryAction>
                                            <Tooltip title="Open link">
                                                <IconButton 
                                                    onClick={() => window.open(match.url, '_blank')}
                                                    size="small"
                                                >
                                                    <LinkIcon />
                                                </IconButton>
                                            </Tooltip>
                                        </ListItemSecondaryAction>
                                    </ListItem>
                                    {index < scanResults.length - 1 && <Divider />}
                                </React.Fragment>
                            ))}
                        </List>
                    </CardContent>
                </Card>
            )}

            {/* Clean Scan Result */}
            {!scanning && scanResults.length === 0 && contentHash && (
                <Alert severity="success" sx={{ mb: 3 }}>
                    <Typography variant="body1">
                        ✅ No unauthorized usage detected
                    </Typography>
                    <Typography variant="body2">
                        Your content appears to be secure and not stolen.
                    </Typography>
                </Alert>
            )}

            {/* Scan History */}
            <Card>
                <CardHeader
                    title="Recent Scans"
                    subheader="History of your content theft scans"
                />
                
                <CardContent>
                    {scanHistory.length === 0 ? (
                        <Typography variant="body2" color="textSecondary" textAlign="center" py={3}>
                            No scan history available
                        </Typography>
                    ) : (
                        <List>
                            {scanHistory.map((scan, index) => (
                                <React.Fragment key={scan.id}>
                                    <ListItem>
                                        <ListItemIcon>
                                            {getStatusIcon(scan.status)}
                                        </ListItemIcon>
                                        <ListItemText
                                            primary={
                                                <Typography variant="body2" component="code">
                                                    {scan.contentHash.substring(0, 16)}...
                                                </Typography>
                                            }
                                            secondary={
                                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                    <Typography variant="caption">
                                                        {scan.timestamp.toLocaleString()}
                                                    </Typography>
                                                    <Chip 
                                                        label={scan.status === 'clean' ? 'Clean' : `${scan.matchCount} matches`}
                                                        size="small"
                                                        color={scan.status === 'clean' ? 'success' : 'error'}
                                                    />
                                                </Box>
                                            }
                                        />
                                    </ListItem>
                                    {index < scanHistory.length - 1 && <Divider />}
                                </React.Fragment>
                            ))}
                        </List>
                    )}
                </CardContent>
            </Card>
        </Box>
    );
};

export default TheftDetection;
