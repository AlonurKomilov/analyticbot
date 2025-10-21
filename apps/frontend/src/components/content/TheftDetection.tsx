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
import { useDemoMode, loadMockData } from '@/__mocks__/utils/demoGuard';

// ============================================================================
// Type Definitions
// ============================================================================

type ScanStatus = 'clean' | 'threat' | 'confirmed' | 'suspected';

interface ScanMatch {
    id: number;
    url: string;
    platform: string;
    matchPercentage: number;
    lastSeen: Date;
    status: ScanStatus;
}

interface ScanHistoryItem {
    id: number;
    contentHash: string;
    timestamp: Date;
    status: 'clean' | 'threat';
    matchCount: number;
}

interface ScanStats {
    totalScans: number;
    threatsDetected: number;
    cleanScans: number;
}

type SeverityColor = 'error' | 'warning' | 'info' | 'success';

// ============================================================================
// Theft Detection Component
// ============================================================================

const TheftDetection: React.FC = () => {
    const isDemo = useDemoMode();
    const [contentHash, setContentHash] = useState<string>('');
    const [scanning, setScanning] = useState<boolean>(false);
    const [scanResults, setScanResults] = useState<ScanMatch[]>([]);
    const [error, setError] = useState<string | null>(null);
    const [scanHistory, setScanHistory] = useState<ScanHistoryItem[]>([]);
    const [stats, setStats] = useState<ScanStats>({
        totalScans: 0,
        threatsDetected: 0,
        cleanScans: 0
    });

    // Load scan history on component mount
    useEffect(() => {
        loadScanHistory();
        loadStats();
    }, [isDemo]);

    const loadScanHistory = async (): Promise<void> => {
        try {
            if (isDemo) {
                // Load mock data dynamically in demo mode
                const mock = await loadMockData(() => import('@/__mocks__/api/theftDetection'));
                if (mock?.generateMockScanHistory) {
                    setScanHistory(mock.generateMockScanHistory());
                }
            } else {
                // Real API implementation
                // const response = await fetch('/api/content-protection/detection/history');
                // const data = await response.json();
                // setScanHistory(data);
                setScanHistory([]); // Empty until real API implemented
            }
        } catch (error) {
            console.error('Failed to load scan history:', error);
        }
    };

    const loadStats = async (): Promise<void> => {
        try {
            if (isDemo) {
                // Load mock data dynamically in demo mode
                const mock = await loadMockData(() => import('@/__mocks__/api/theftDetection'));
                if (mock?.generateMockStats) {
                    setStats(mock.generateMockStats());
                }
            } else {
                // Real API implementation
                // const response = await fetch('/api/content-protection/detection/stats');
                // const data = await response.json();
                // setStats(data);
                setStats({ totalScans: 0, threatsDetected: 0, cleanScans: 0 }); // Empty until real API implemented
            }
        } catch (error) {
            console.error('Failed to load stats:', error);
        }
    };

    const scanForTheft = async (): Promise<void> => {
        if (!contentHash.trim()) {
            setError('Please enter a content hash to scan');
            return;
        }

        setScanning(true);
        setError(null);
        setScanResults([]);

        try {
            if (isDemo) {
                // Load mock data dynamically in demo mode
                const mock = await loadMockData(() => import('@/__mocks__/api/theftDetection'));
                if (mock?.generateMockScanResults && mock?.mockScanDelay) {
                    // Simulate API delay for realistic demo
                    await mock.mockScanDelay(2000);
                    const mockResults = mock.generateMockScanResults(contentHash);
                    setScanResults(mockResults);

                    // Update scan history
                    const newScan: ScanHistoryItem = {
                        id: Date.now(),
                        contentHash: contentHash,
                        timestamp: new Date(),
                        status: mockResults.length > 0 ? 'threat' : 'clean',
                        matchCount: mockResults.length
                    };
                    setScanHistory(prev => [newScan, ...prev]);

                    // Update stats
                    setStats(prev => ({
                        totalScans: prev.totalScans + 1,
                        threatsDetected: prev.threatsDetected + (mockResults.length > 0 ? 1 : 0),
                        cleanScans: prev.cleanScans + (mockResults.length === 0 ? 1 : 0)
                    }));
                } else {
                    throw new Error('Mock data not available');
                }
            } else {
                // Real API implementation
                // const response = await apiClient.post('/api/v1/content-protection/detection/scan', {
                //     content_hash: contentHash
                // });
                // setScanResults(response.data.matches || []);
                
                // For now, show error if real API not implemented
                throw new Error('Real theft detection API not yet implemented. Please use demo mode.');
            }
        } catch (err) {
            console.error('Scan failed:', err);
            const errorMessage = err instanceof Error ? err.message : 'Unknown error';
            setError(`Scan failed: ${errorMessage}`);
        } finally {
            setScanning(false);
        }
    };

    const getSeverityColor = (matchPercentage: number): SeverityColor => {
        if (matchPercentage >= 90) return 'error';
        if (matchPercentage >= 70) return 'warning';
        return 'info';
    };

    const getStatusIcon = (status: ScanStatus | 'clean' | 'threat'): React.ReactElement => {
        switch (status) {
            case 'confirmed':
                return <ErrorIcon color="error" />;
            case 'suspected':
                return <WarningIcon color="warning" />;
            case 'clean':
                return <CheckIcon color="success" />;
            case 'threat':
                return <ErrorIcon color="error" />;
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
