/**
 * Content Protection Panel Component
 *
 * UI for content theft detection and watermarking.
 * Integrates with contentProtectionService.ts
 */

import React, { useState } from 'react';
import {
    Box,
    Card,
    CardContent,
    Typography,
    Button,
    TextField,
    Tab,
    Tabs,
    Alert,
    CircularProgress,
    Chip,
    List,
    ListItem,
    ListItemText,
    ListItemAvatar,
    Avatar,
    Divider,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Slider,
    Paper
} from '@mui/material';
import {
    Security as SecurityIcon,
    WaterDrop as WatermarkIcon,
    Search as ScanIcon,
    Warning as WarningIcon,
    CheckCircle as SafeIcon,
    Image as ImageIcon,
    TextFields as TextIcon
} from '@mui/icons-material';
import {
    contentProtectionService,
    type TheftDetectionResult
} from '@/services/contentProtectionService';

export interface ContentProtectionPanelProps {
    channelId?: string;
}

interface TabPanelProps {
    children?: React.ReactNode;
    index: number;
    value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => (
    <div role="tabpanel" hidden={value !== index}>
        {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
);

const ContentProtectionPanel: React.FC<ContentProtectionPanelProps> = ({ channelId }) => {
    const [tabValue, setTabValue] = useState(0);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<string | null>(null);

    // Theft Detection State
    const [scanResults, setScanResults] = useState<TheftDetectionResult | null>(null);
    const [scanPlatforms, setScanPlatforms] = useState<string[]>(['telegram', 'twitter', 'facebook']);

    // Text Watermark State
    const [textToWatermark, setTextToWatermark] = useState('');
    const [watermarkType, setWatermarkType] = useState<'invisible' | 'visible'>('invisible');
    const [watermarkPosition, setWatermarkPosition] = useState<'top' | 'bottom' | 'center'>('bottom');
    const [watermarkedText, setWatermarkedText] = useState('');

    // Image Watermark State
    const [imageUrl, setImageUrl] = useState('');
    const [imageWatermarkText, setImageWatermarkText] = useState('');
    const [imageOpacity, setImageOpacity] = useState(0.5);
    const [imagePosition, setImagePosition] = useState<'topleft' | 'topright' | 'bottomleft' | 'bottomright' | 'center'>('bottomright');
    const [watermarkedImageUrl, setWatermarkedImageUrl] = useState('');

    const handleScanForTheft = async () => {
        if (!channelId) {
            setError('Channel ID is required');
            return;
        }

        setLoading(true);
        setError(null);
        setScanResults(null);

        try {
            const results = await contentProtectionService.scanForTheft(
                channelId,
                undefined,
                scanPlatforms
            );
            setScanResults(results);

            if (results.detected) {
                setSuccess(`Found ${results.matches.length} potential theft instances`);
            } else {
                setSuccess('No content theft detected. Your content is safe!');
            }
        } catch (err: any) {
            setError(err.message || 'Failed to scan for theft');
        } finally {
            setLoading(false);
        }
    };

    const handleApplyTextWatermark = async () => {
        if (!textToWatermark.trim()) {
            setError('Please enter text to watermark');
            return;
        }

        setLoading(true);
        setError(null);
        setWatermarkedText('');

        try {
            const response = await contentProtectionService.applyTextWatermark(
                textToWatermark,
                watermarkType,
                watermarkPosition
            );
            setWatermarkedText(response.watermarked_text);
            setSuccess('Text watermark applied successfully!');
        } catch (err: any) {
            setError(err.message || 'Failed to apply watermark');
        } finally {
            setLoading(false);
        }
    };

    const handleApplyImageWatermark = async () => {
        if (!imageUrl.trim() || !imageWatermarkText.trim()) {
            setError('Please provide both image URL and watermark text');
            return;
        }

        setLoading(true);
        setError(null);
        setWatermarkedImageUrl('');

        try {
            const response = await contentProtectionService.applyImageWatermark(
                imageUrl,
                imageWatermarkText,
                imageOpacity,
                imagePosition
            );
            setWatermarkedImageUrl(response.watermarked_image_url);
            setSuccess('Image watermark applied successfully!');
        } catch (err: any) {
            setError(err.message || 'Failed to apply watermark');
        } finally {
            setLoading(false);
        }
    };

    const copyToClipboard = (text: string) => {
        navigator.clipboard.writeText(text);
        setSuccess('Copied to clipboard!');
        setTimeout(() => setSuccess(null), 2000);
    };

    return (
        <Card>
            <CardContent>
                {/* Header */}
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                    <SecurityIcon color="primary" />
                    <Typography variant="h5" component="h2">
                        Content Protection
                    </Typography>
                </Box>

                {/* Alerts */}
                {error && (
                    <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
                        {error}
                    </Alert>
                )}
                {success && (
                    <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>
                        {success}
                    </Alert>
                )}

                {/* Tabs */}
                <Tabs value={tabValue} onChange={(_, v) => setTabValue(v)} sx={{ borderBottom: 1, borderColor: 'divider' }}>
                    <Tab label="Theft Detection" icon={<ScanIcon />} iconPosition="start" />
                    <Tab label="Text Watermark" icon={<TextIcon />} iconPosition="start" />
                    <Tab label="Image Watermark" icon={<ImageIcon />} iconPosition="start" />
                </Tabs>

                {/* Tab 1: Theft Detection */}
                <TabPanel value={tabValue} index={0}>
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
                            onClick={handleScanForTheft}
                            disabled={loading || !channelId || scanPlatforms.length === 0}
                            fullWidth
                        >
                            {loading ? <CircularProgress size={20} /> : 'Scan for Theft'}
                        </Button>

                        {/* Scan Results */}
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
                                                            secondary={
                                                                <>
                                                                    <Typography component="span" variant="body2" color="text.primary">
                                                                        {(match.similarity * 100).toFixed(1)}% similar
                                                                    </Typography>
                                                                    {' — '}
                                                                    <a href={match.url} target="_blank" rel="noopener noreferrer">
                                                                        View source
                                                                    </a>
                                                                </>
                                                            }
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
                </TabPanel>

                {/* Tab 2: Text Watermark */}
                <TabPanel value={tabValue} index={1}>
                    <Box>
                        <Typography variant="body2" color="text.secondary" paragraph>
                            Add invisible or visible watermarks to your text content.
                        </Typography>

                        <TextField
                            fullWidth
                            multiline
                            rows={4}
                            label="Text to Watermark"
                            value={textToWatermark}
                            onChange={(e) => setTextToWatermark(e.target.value)}
                            placeholder="Enter your text here..."
                            sx={{ mb: 2 }}
                        />

                        <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
                            <FormControl fullWidth>
                                <InputLabel>Watermark Type</InputLabel>
                                <Select
                                    value={watermarkType}
                                    label="Watermark Type"
                                    onChange={(e) => setWatermarkType(e.target.value as 'invisible' | 'visible')}
                                >
                                    <MenuItem value="invisible">Invisible (Steganography)</MenuItem>
                                    <MenuItem value="visible">Visible</MenuItem>
                                </Select>
                            </FormControl>

                            <FormControl fullWidth>
                                <InputLabel>Position</InputLabel>
                                <Select
                                    value={watermarkPosition}
                                    label="Position"
                                    onChange={(e) => setWatermarkPosition(e.target.value as any)}
                                >
                                    <MenuItem value="top">Top</MenuItem>
                                    <MenuItem value="center">Center</MenuItem>
                                    <MenuItem value="bottom">Bottom</MenuItem>
                                </Select>
                            </FormControl>
                        </Box>

                        <Button
                            variant="contained"
                            startIcon={<WatermarkIcon />}
                            onClick={handleApplyTextWatermark}
                            disabled={loading || !textToWatermark.trim()}
                            fullWidth
                        >
                            {loading ? <CircularProgress size={20} /> : 'Apply Watermark'}
                        </Button>

                        {watermarkedText && (
                            <Paper elevation={2} sx={{ mt: 3, p: 2 }}>
                                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                                    <Typography variant="subtitle2">
                                        Watermarked Text:
                                    </Typography>
                                    <Button size="small" onClick={() => copyToClipboard(watermarkedText)}>
                                        Copy
                                    </Button>
                                </Box>
                                <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap', bgcolor: 'grey.100', p: 2, borderRadius: 1 }}>
                                    {watermarkedText}
                                </Typography>
                            </Paper>
                        )}
                    </Box>
                </TabPanel>

                {/* Tab 3: Image Watermark */}
                <TabPanel value={tabValue} index={2}>
                    <Box>
                        <Typography variant="body2" color="text.secondary" paragraph>
                            Add watermarks to your images for copyright protection.
                        </Typography>

                        <TextField
                            fullWidth
                            label="Image URL"
                            value={imageUrl}
                            onChange={(e) => setImageUrl(e.target.value)}
                            placeholder="https://example.com/image.jpg"
                            sx={{ mb: 2 }}
                        />

                        <TextField
                            fullWidth
                            label="Watermark Text"
                            value={imageWatermarkText}
                            onChange={(e) => setImageWatermarkText(e.target.value)}
                            placeholder="© Your Channel Name"
                            sx={{ mb: 2 }}
                        />

                        <Box sx={{ mb: 2 }}>
                            <Typography variant="subtitle2" gutterBottom>
                                Opacity: {(imageOpacity * 100).toFixed(0)}%
                            </Typography>
                            <Slider
                                value={imageOpacity}
                                onChange={(_, v) => setImageOpacity(v as number)}
                                min={0.1}
                                max={1}
                                step={0.1}
                                marks
                                valueLabelDisplay="auto"
                                valueLabelFormat={(v) => `${(v * 100).toFixed(0)}%`}
                            />
                        </Box>

                        <FormControl fullWidth sx={{ mb: 2 }}>
                            <InputLabel>Watermark Position</InputLabel>
                            <Select
                                value={imagePosition}
                                label="Watermark Position"
                                onChange={(e) => setImagePosition(e.target.value as any)}
                            >
                                <MenuItem value="topleft">Top Left</MenuItem>
                                <MenuItem value="topright">Top Right</MenuItem>
                                <MenuItem value="center">Center</MenuItem>
                                <MenuItem value="bottomleft">Bottom Left</MenuItem>
                                <MenuItem value="bottomright">Bottom Right</MenuItem>
                            </Select>
                        </FormControl>

                        <Button
                            variant="contained"
                            startIcon={<ImageIcon />}
                            onClick={handleApplyImageWatermark}
                            disabled={loading || !imageUrl.trim() || !imageWatermarkText.trim()}
                            fullWidth
                        >
                            {loading ? <CircularProgress size={20} /> : 'Apply Image Watermark'}
                        </Button>

                        {watermarkedImageUrl && (
                            <Paper elevation={2} sx={{ mt: 3, p: 2 }}>
                                <Typography variant="subtitle2" gutterBottom>
                                    Watermarked Image:
                                </Typography>
                                <Box
                                    component="img"
                                    src={watermarkedImageUrl}
                                    alt="Watermarked"
                                    sx={{ width: '100%', borderRadius: 1, mt: 1 }}
                                />
                                <Button
                                    fullWidth
                                    variant="outlined"
                                    sx={{ mt: 2 }}
                                    onClick={() => window.open(watermarkedImageUrl, '_blank')}
                                >
                                    Download Image
                                </Button>
                            </Paper>
                        )}
                    </Box>
                </TabPanel>
            </CardContent>
        </Card>
    );
};

export default ContentProtectionPanel;
