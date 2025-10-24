/**
 * TheftDetection component
 * UI for scanning platforms and displaying scan results.
 */

import React from 'react';
import { Box, Typography, Button, Chip, Paper, List, ListItem, ListItemAvatar, Avatar, ListItemText, Divider, CircularProgress } from '@mui/material';
import { Warning as WarningIcon, CheckCircle as SafeIcon, Search as ScanIcon } from '@mui/icons-material';
import type { TheftDetectionResult } from '@/services/contentProtectionService';
import type { Dispatch, SetStateAction } from 'react';

export interface TheftDetectionProps {
    channelId?: string;
    loading: boolean;
    scanResults: TheftDetectionResult | null;
    scanPlatforms: string[];
    setScanPlatforms: Dispatch<SetStateAction<string[]>>;
    onScan: (channelId?: string) => Promise<void>;
}

const TheftDetection: React.FC<TheftDetectionProps> = ({ channelId, loading, scanResults, scanPlatforms, setScanPlatforms, onScan }) => {
    return (
        <Box>
            <Typography variant="body2" color="text.secondary" paragraph>
                Scan for unauthorized use of your content across multiple platforms.
            </Typography>

            <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" gutterBottom>
                    Platforms to scan:
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    {['telegram', 'twitter', 'facebook', 'instagram', 'youtube'].map(platform => (
                        <Chip
                            key={platform}
                            label={platform}
                            onClick={() => {
                                setScanPlatforms(prev => 
                                    prev.includes(platform)
                                        ? prev.filter(p => p !== platform)
                                        : [...prev, platform]
                                );
                            }}
                            color={scanPlatforms.includes(platform) ? 'primary' : 'default'}
                            variant={scanPlatforms.includes(platform) ? 'filled' : 'outlined'}
                        />
                    ))}
                </Box>
            </Box>

            <Button
                variant="contained"
                startIcon={<ScanIcon />}
                onClick={() => onScan(channelId)}
                disabled={loading || !channelId || scanPlatforms.length === 0}
                fullWidth
            >
                {loading ? <CircularProgress size={20} /> : 'Scan for Theft'}
            </Button>

            {scanResults && (
                <Paper elevation={2} sx={{ mt: 3, p: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                        {scanResults.detected ? (
                            <>
                                <WarningIcon color="error" />
                                <Typography variant="h6" color="error">
                                    Theft Detected!
                                </Typography>
                            </>
                        ) : (
                            <>
                                <SafeIcon color="success" />
                                <Typography variant="h6" color="success">
                                    Content is Safe
                                </Typography>
                            </>
                        )}
                    </Box>

                    <Typography variant="body2" color="text.secondary" paragraph>
                        Confidence: {(scanResults.confidence * 100).toFixed(1)}% •
                        Scanned: {new Date(scanResults.scan_date).toLocaleString()}
                    </Typography>

                    {scanResults.matches.length > 0 && (
                        <Box>
                            <Typography variant="subtitle2" gutterBottom>
                                Found {scanResults.matches.length} matches:
                            </Typography>
                            <List>
                                {scanResults.matches.map((match, index) => (
                                    <React.Fragment key={index}>
                                        <ListItem>
                                            <ListItemAvatar>
                                                <Avatar>
                                                    <WarningIcon />
                                                </Avatar>
                                            </ListItemAvatar>
                                            <ListItemText
                                                primary={match.platform}
                                                secondary={(
                                                    <>
                                                        <Typography component="span" variant="body2" color="text.primary">
                                                            {(match.similarity * 100).toFixed(1)}% similar
                                                        </Typography>
                                                        {' — '}
                                                        <a href={match.url} target="_blank" rel="noopener noreferrer">View source</a>
                                                    </>
                                                )}
                                            />
                                        </ListItem>
                                        {index < scanResults.matches.length - 1 && <Divider />}
                                    </React.Fragment>
                                ))}
                            </List>
                        </Box>
                    )}
                </Paper>
            )}
        </Box>
    );
};

export default TheftDetection;
