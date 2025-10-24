/**
 * TextWatermark component
 * UI for applying text watermarks and showing results.
 */

import React from 'react';
import { Box, Typography, TextField, Button, Paper } from '@mui/material';
import { WaterDrop as WatermarkIcon } from '@mui/icons-material';

export interface TextWatermarkProps {
    loading: boolean;
    textToWatermark: string;
    setTextToWatermark: (s: string) => void;
    watermarkType: 'invisible' | 'visible';
    setWatermarkType: (t: 'invisible' | 'visible') => void;
    watermarkPosition: 'top' | 'center' | 'bottom';
    setWatermarkPosition: (p: 'top' | 'center' | 'bottom') => void;
    watermarkedText: string;
    onApply: () => Promise<void>;
    onCopy: (text: string) => void;
}

const TextWatermark: React.FC<TextWatermarkProps> = ({
    loading,
    textToWatermark,
    setTextToWatermark,
    watermarkType,
    setWatermarkType,
    watermarkPosition,
    setWatermarkPosition,
    watermarkedText,
    onApply,
    onCopy,
}) => {
    return (
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
                <TextField
                    select
                    label="Watermark Type"
                    value={watermarkType}
                    onChange={(e) => setWatermarkType(e.target.value as any)}
                    fullWidth
                    helperText="Invisible (steganography) or visible watermark"
                >
                    <option value="invisible">Invisible (Steganography)</option>
                    <option value="visible">Visible</option>
                </TextField>

                <TextField
                    select
                    label="Position"
                    value={watermarkPosition}
                    onChange={(e) => setWatermarkPosition(e.target.value as any)}
                    fullWidth
                >
                    <option value="top">Top</option>
                    <option value="center">Center</option>
                    <option value="bottom">Bottom</option>
                </TextField>
            </Box>

            <Button
                variant="contained"
                startIcon={<WatermarkIcon />}
                onClick={onApply}
                disabled={loading || !textToWatermark.trim()}
                fullWidth
            >
                {loading ? 'Applying...' : 'Apply Watermark'}
            </Button>

            {watermarkedText && (
                <Paper elevation={2} sx={{ mt: 3, p: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                        <Typography variant="subtitle2">Watermarked Text:</Typography>
                        <Button size="small" onClick={() => onCopy(watermarkedText)}>Copy</Button>
                    </Box>
                    <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap', bgcolor: 'grey.100', p: 2, borderRadius: 1 }}>
                        {watermarkedText}
                    </Typography>
                </Paper>
            )}
        </Box>
    );
};

export default TextWatermark;
