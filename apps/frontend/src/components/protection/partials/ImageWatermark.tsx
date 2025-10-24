/**
 * ImageWatermark component
 * UI for applying image watermarks and showing preview/results.
 */

import React from 'react';
import { Box, Typography, TextField, Button, Paper, Slider } from '@mui/material';
import PhotoCameraIcon from '@mui/icons-material/PhotoCamera';

export interface ImageWatermarkProps {
    loading: boolean;
    imageUrl: string;
    setImageUrl: (s: string) => void;
    watermarkText: string;
    setWatermarkText: (s: string) => void;
    opacity: number;
    setOpacity: (v: number) => void;
    position: 'top-left' | 'top-right' | 'center' | 'bottom-left' | 'bottom-right';
    setPosition: (p: ImageWatermarkProps['position']) => void;
    resultImageUrl?: string;
    onApply: () => Promise<void>;
    onDownload: (url?: string) => void;
}

const ImageWatermark: React.FC<ImageWatermarkProps> = ({
    loading,
    imageUrl,
    setImageUrl,
    watermarkText,
    setWatermarkText,
    opacity,
    setOpacity,
    position,
    setPosition,
    resultImageUrl,
    onApply,
    onDownload,
}) => {
    return (
        <Box>
            <Typography variant="body2" color="text.secondary" paragraph>
                Add a visible watermark to images. Provide an image URL or upload an image.
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
                value={watermarkText}
                onChange={(e) => setWatermarkText(e.target.value)}
                sx={{ mb: 2 }}
            />

            <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', mb: 2 }}>
                <Box sx={{ width: 180 }}>
                    <Typography variant="caption">Opacity</Typography>
                    <Slider value={opacity} min={0} max={100} onChange={(_, val) => setOpacity(val as number)} />
                </Box>

                <TextField
                    select
                    label="Position"
                    value={position}
                    onChange={(e) => setPosition(e.target.value as any)}
                    sx={{ minWidth: 160 }}
                >
                    <option value="top-left">Top left</option>
                    <option value="top-right">Top right</option>
                    <option value="center">Center</option>
                    <option value="bottom-left">Bottom left</option>
                    <option value="bottom-right">Bottom right</option>
                </TextField>
            </Box>

            <Button
                variant="contained"
                startIcon={<PhotoCameraIcon />}
                onClick={onApply}
                disabled={loading || !imageUrl.trim()}
            >
                {loading ? 'Applying...' : 'Apply Watermark'}
            </Button>

            {resultImageUrl && (
                <Paper elevation={2} sx={{ mt: 3, p: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                        <Typography variant="subtitle2">Result</Typography>
                        <Button size="small" onClick={() => onDownload(resultImageUrl)}>Download</Button>
                    </Box>
                    <Box sx={{ textAlign: 'center' }}>
                        <img src={resultImageUrl} alt="watermarked" style={{ maxWidth: '100%', borderRadius: 8 }} />
                    </Box>
                </Paper>
            )}
        </Box>
    );
};

export default ImageWatermark;
