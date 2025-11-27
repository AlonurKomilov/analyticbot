import React from 'react';
import {
    Box,
    Typography,
    Chip
} from '@mui/material';

/**
 * Props for the RecommenderFooter component
 */
interface RecommenderFooterProps {
    /** Recommendations data containing accuracy/confidence */
    recommendations?: {
        accuracy?: number;
        confidence?: number;
    };
}

const RecommenderFooter: React.FC<RecommenderFooterProps> = ({ recommendations }) => {
    // Get accuracy value - handle both percentage (already 0-100) and decimal (0-1) formats
    const getAccuracyValue = (): number | null => {
        // Priority: accuracy > confidence
        const value = recommendations?.accuracy ?? recommendations?.confidence;
        if (!value) return null;
        
        // If value is between 0 and 1, it's a decimal that needs to be converted to percentage
        // If value is between 1 and 100, it's already a percentage
        return value <= 1 ? value * 100 : value;
    };

    const accuracyValue = getAccuracyValue();

    return (
        <Box sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            mt: 3,
            pt: 2,
            borderTop: '1px solid',
            borderColor: 'divider'
        }}>
            <Typography variant="caption" color="text.secondary">
                Analysis updated at {new Date().toLocaleTimeString()}
            </Typography>
            <Box sx={{ display: 'flex', gap: 1 }}>
                <Chip
                    size="small"
                    label={<><span aria-hidden="true">📊</span> Performance Analytics</>}
                    color="primary"
                    variant="outlined"
                />
                {accuracyValue !== null && (
                    <Chip
                        size="small"
                        label={`${Math.round(accuracyValue)}% accuracy`}
                        color="success"
                    />
                )}
            </Box>
        </Box>
    );
};

export default RecommenderFooter;
