import React, { useState, ChangeEvent } from 'react';
import {
    Box,
    Card,
    CardContent,
    CardHeader,
    Typography,
    Button,
    TextField,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Slider,
    Switch,
    FormControlLabel,
    Alert,
    LinearProgress,
    Chip,
    Grid,
    Divider,
    SelectChangeEvent
} from '@mui/material';
import {
    CloudUpload as UploadIcon,
    Download as DownloadIcon,
    Image as ImageIcon,
    Security as SecurityIcon,
    Palette as PaletteIcon
} from '@mui/icons-material';

// ============================================================================
// Type Definitions
// ============================================================================

type WatermarkPosition = 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right' | 'center';
type WatermarkColor = 'white' | 'black' | 'red' | 'blue' | 'green';

interface WatermarkConfig {
    text: string;
    position: WatermarkPosition;
    opacity: number;
    fontSize: number;
    color: WatermarkColor;
    addShadow: boolean;
}

interface ProcessingResult {
    downloadUrl: string;
    filename: string;
    size: number;
}

interface OptionItem {
    value: string;
    label: string;
}

// ============================================================================
// Watermark Tool Component
// ============================================================================

const WatermarkTool: React.FC = () => {
    const [file, setFile] = useState<File | null>(null);
    const [processing, setProcessing] = useState<boolean>(false);
    const [result, setResult] = useState<ProcessingResult | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [preview, setPreview] = useState<string | null>(null);

    // Watermark configuration
    const [watermarkConfig, setWatermarkConfig] = useState<WatermarkConfig>({
        text: 'Copyright © 2025',
        position: 'bottom-right',
        opacity: 70,
        fontSize: 24,
        color: 'white',
        addShadow: true
    });

    const positionOptions: OptionItem[] = [
        { value: 'top-left', label: 'Top Left' },
        { value: 'top-right', label: 'Top Right' },
        { value: 'bottom-left', label: 'Bottom Left' },
        { value: 'bottom-right', label: 'Bottom Right' },
        { value: 'center', label: 'Center' }
    ];

    const colorOptions: OptionItem[] = [
        { value: 'white', label: 'White' },
        { value: 'black', label: 'Black' },
        { value: 'red', label: 'Red' },
        { value: 'blue', label: 'Blue' },
        { value: 'green', label: 'Green' }
    ];

    const handleFileChange = (event: ChangeEvent<HTMLInputElement>): void => {
        const selectedFile = event.target.files?.[0];
        if (selectedFile) {
            setFile(selectedFile);
            setError(null);
            setResult(null);

            // Create preview
            const reader = new FileReader();
            reader.onload = (e) => setPreview(e.target?.result as string);
            reader.readAsDataURL(selectedFile);
        }
    };

    const handleConfigChange = <K extends keyof WatermarkConfig>(
        field: K,
        value: WatermarkConfig[K]
    ): void => {
        setWatermarkConfig(prev => ({
            ...prev,
            [field]: value
        }));
    };

    const handleWatermark = async (): Promise<void> => {
        if (!file) {
            setError('Please select a file first');
            return;
        }

        setProcessing(true);
        setError(null);

        try {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('watermark_text', watermarkConfig.text);
            formData.append('position', watermarkConfig.position);
            formData.append('opacity', (watermarkConfig.opacity / 100).toString());
            formData.append('font_size', watermarkConfig.fontSize.toString());
            formData.append('color', watermarkConfig.color);
            formData.append('add_shadow', watermarkConfig.addShadow.toString());

            // Use API endpoint
            const baseURL = process.env.REACT_APP_API_URL || '';
            const response = await fetch(`${baseURL}/api/v1/content-protection/watermark/image`, {
                method: 'POST',
                body: formData,
                headers: {
                    'Authorization': `TWA ${(window as any).Telegram?.WebApp?.initData || ''}`
                }
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: 'Watermarking failed' }));
                throw new Error(errorData.detail || 'Watermarking failed');
            }

            // Get the watermarked file
            const blob = await response.blob();
            const downloadUrl = URL.createObjectURL(blob);

            setResult({
                downloadUrl,
                filename: `watermarked_${file.name}`,
                size: blob.size
            });

        } catch (err) {
            console.error('Watermarking failed:', err);
            const errorMessage = err instanceof Error ? err.message : 'Failed to add watermark';
            setError(errorMessage);
        } finally {
            setProcessing(false);
        }
    };

    const downloadFile = (): void => {
        if (result) {
            const link = document.createElement('a');
            link.href = result.downloadUrl;
            link.download = result.filename;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    };

    return (
        <Card sx={{ maxWidth: 800, mx: 'auto', my: 3 }}>
            <CardHeader
                avatar={<SecurityIcon color="primary" />}
                title="Image Watermark Tool"
                subheader="Add copyright watermarks to protect your images"
            />

            <CardContent>
                {/* File Upload Section */}
                <Box sx={{ mb: 4 }}>
                    <Typography variant="h6" gutterBottom>
                        <ImageIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                        Upload Image
                    </Typography>

                    <Box
                        sx={{
                            border: '2px dashed',
                            borderColor: file ? 'success.main' : 'grey.300',
                            borderRadius: 2,
                            p: 3,
                            textAlign: 'center',
                            bgcolor: file ? 'success.50' : 'grey.50',
                            cursor: 'pointer',
                            '&:hover': {
                                borderColor: 'primary.main',
                                bgcolor: 'primary.50'
                            }
                        }}
                        onClick={() => document.getElementById('watermark-file-input')?.click()}
                    >
                        <input
                            id="watermark-file-input"
                            type="file"
                            accept="image/*"
                            onChange={handleFileChange}
                            style={{ display: 'none' }}
                        />

                        <UploadIcon sx={{ fontSize: 48, color: 'grey.400', mb: 2 }} />

                        {file ? (
                            <Box>
                                <Typography variant="body1" color="success.main">
                                    {file.name}
                                </Typography>
                                <Chip
                                    label={`${(file.size / 1024 / 1024).toFixed(2)} MB`}
                                    size="small"
                                    color="success"
                                    sx={{ mt: 1 }}
                                />
                            </Box>
                        ) : (
                            <Box>
                                <Typography variant="body1" color="textSecondary">
                                    Click to upload an image
                                </Typography>
                                <Typography variant="body2" color="textSecondary">
                                    Supports: JPG, PNG, GIF (Max 50MB)
                                </Typography>
                            </Box>
                        )}
                    </Box>

                    {/* Image Preview */}
                    {preview && (
                        <Box sx={{ mt: 2, textAlign: 'center' }}>
                            <img
                                src={preview}
                                alt="Preview"
                                style={{
                                    maxWidth: '100%',
                                    maxHeight: 200,
                                    borderRadius: 8,
                                    border: '1px solid #ddd'
                                }}
                            />
                        </Box>
                    )}
                </Box>

                <Divider sx={{ my: 3 }} />

                {/* Watermark Configuration */}
                <Box sx={{ mb: 4 }}>
                    <Typography variant="h6" gutterBottom>
                        <PaletteIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                        Watermark Settings
                    </Typography>

                    <Grid container spacing={3}>
                        <Grid item xs={12} md={6}>
                            <TextField
                                fullWidth
                                label="Watermark Text"
                                value={watermarkConfig.text}
                                onChange={(e) => handleConfigChange('text', e.target.value)}
                                placeholder="Copyright © 2025"
                                sx={{ mb: 2 }}
                            />

                            <FormControl fullWidth sx={{ mb: 2 }}>
                                <InputLabel>Position</InputLabel>
                                <Select
                                    value={watermarkConfig.position}
                                    label="Position"
                                    onChange={(e: SelectChangeEvent) => 
                                        handleConfigChange('position', e.target.value as WatermarkPosition)
                                    }
                                >
                                    {positionOptions.map(option => (
                                        <MenuItem key={option.value} value={option.value}>
                                            {option.label}
                                        </MenuItem>
                                    ))}
                                </Select>
                            </FormControl>

                            <FormControl fullWidth>
                                <InputLabel>Color</InputLabel>
                                <Select
                                    value={watermarkConfig.color}
                                    label="Color"
                                    onChange={(e: SelectChangeEvent) => 
                                        handleConfigChange('color', e.target.value as WatermarkColor)
                                    }
                                >
                                    {colorOptions.map(option => (
                                        <MenuItem key={option.value} value={option.value}>
                                            {option.label}
                                        </MenuItem>
                                    ))}
                                </Select>
                            </FormControl>
                        </Grid>

                        <Grid item xs={12} md={6}>
                            <Box sx={{ mb: 3 }}>
                                <Typography gutterBottom>
                                    Opacity: {watermarkConfig.opacity}%
                                </Typography>
                                <Slider
                                    value={watermarkConfig.opacity}
                                    onChange={(_e, value) => handleConfigChange('opacity', value as number)}
                                    min={10}
                                    max={100}
                                    step={5}
                                    marks
                                    valueLabelDisplay="auto"
                                />
                            </Box>

                            <Box sx={{ mb: 3 }}>
                                <Typography gutterBottom>
                                    Font Size: {watermarkConfig.fontSize}px
                                </Typography>
                                <Slider
                                    value={watermarkConfig.fontSize}
                                    onChange={(_e, value) => handleConfigChange('fontSize', value as number)}
                                    min={12}
                                    max={72}
                                    step={2}
                                    marks
                                    valueLabelDisplay="auto"
                                />
                            </Box>

                            <FormControlLabel
                                control={
                                    <Switch
                                        checked={watermarkConfig.addShadow}
                                        onChange={(e) => handleConfigChange('addShadow', e.target.checked)}
                                    />
                                }
                                label="Add Text Shadow"
                            />
                        </Grid>
                    </Grid>
                </Box>

                {/* Processing */}
                {processing && (
                    <Box sx={{ mb: 3 }}>
                        <Typography variant="body2" color="textSecondary" gutterBottom>
                            Adding watermark...
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

                {/* Result */}
                {result && (
                    <Alert severity="success" sx={{ mb: 3 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                            <Box>
                                <Typography variant="body2">
                                    Watermark added successfully!
                                </Typography>
                                <Typography variant="caption" color="textSecondary">
                                    File: {result.filename} ({(result.size / 1024 / 1024).toFixed(2)} MB)
                                </Typography>
                            </Box>
                            <Button
                                variant="contained"
                                startIcon={<DownloadIcon />}
                                onClick={downloadFile}
                                size="small"
                            >
                                Download
                            </Button>
                        </Box>
                    </Alert>
                )}

                {/* Action Buttons */}
                <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
                    <Button
                        variant="contained"
                        onClick={handleWatermark}
                        disabled={!file || processing}
                        startIcon={<SecurityIcon />}
                        size="large"
                    >
                        {processing ? 'Adding Watermark...' : 'Add Watermark'}
                    </Button>
                </Box>
            </CardContent>
        </Card>
    );
};

export default WatermarkTool;
