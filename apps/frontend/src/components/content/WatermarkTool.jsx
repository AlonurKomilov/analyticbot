import React, { useState } from 'react';
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
    Divider
} from '@mui/material';
import {
    CloudUpload as UploadIcon,
    Download as DownloadIcon,
    Image as ImageIcon,
    Security as SecurityIcon,
    Palette as PaletteIcon
} from '@mui/icons-material';
import { apiClient } from '../../utils/apiClient';

const WatermarkTool = () => {
    const [file, setFile] = useState(null);
    const [processing, setProcessing] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);
    const [preview, setPreview] = useState(null);
    
    // Watermark configuration
    const [watermarkConfig, setWatermarkConfig] = useState({
        text: 'Copyright © 2025',
        position: 'bottom-right',
        opacity: 70,
        fontSize: 24,
        color: 'white',
        addShadow: true
    });

    const positionOptions = [
        { value: 'top-left', label: 'Top Left' },
        { value: 'top-right', label: 'Top Right' },
        { value: 'bottom-left', label: 'Bottom Left' },
        { value: 'bottom-right', label: 'Bottom Right' },
        { value: 'center', label: 'Center' }
    ];

    const colorOptions = [
        { value: 'white', label: 'White' },
        { value: 'black', label: 'Black' },
        { value: 'red', label: 'Red' },
        { value: 'blue', label: 'Blue' },
        { value: 'green', label: 'Green' }
    ];

    const handleFileChange = (event) => {
        const selectedFile = event.target.files[0];
        if (selectedFile) {
            setFile(selectedFile);
            setError(null);
            setResult(null);
            
            // Create preview
            const reader = new FileReader();
            reader.onload = (e) => setPreview(e.target.result);
            reader.readAsDataURL(selectedFile);
        }
    };

    const handleConfigChange = (field, value) => {
        setWatermarkConfig(prev => ({
            ...prev,
            [field]: value
        }));
    };

    const handleWatermark = async () => {
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

            const response = await fetch('http://localhost:8000/api/v1/content-protection/watermark/image', {
                method: 'POST',
                body: formData,
                headers: {
                    'Authorization': `TWA ${window.Telegram?.WebApp?.initData || ''}`
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

        } catch (error) {
            console.error('Watermarking failed:', error);
            setError(error.message || 'Failed to add watermark');
        } finally {
            setProcessing(false);
        }
    };

    const downloadFile = () => {
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
                        onClick={() => document.getElementById('watermark-file-input').click()}
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
                                    onChange={(e) => handleConfigChange('position', e.target.value)}
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
                                    onChange={(e) => handleConfigChange('color', e.target.value)}
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
                                    onChange={(e, value) => handleConfigChange('opacity', value)}
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
                                    onChange={(e, value) => handleConfigChange('fontSize', value)}
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
