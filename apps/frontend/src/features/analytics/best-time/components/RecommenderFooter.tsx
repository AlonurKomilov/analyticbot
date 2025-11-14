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
    /** Recommendations data containing accuracy */
    recommendations?: {
        accuracy?: number;
    };
}

const RecommenderFooter: React.FC<RecommenderFooterProps> = ({ recommendations }) => {
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
                {recommendations?.accuracy && (
                    <Chip
                        size="small"
                        label={`${recommendations.accuracy}% aniq`}
                        color="success"
                    />
                )}
            </Box>
        </Box>
    );
};

export default RecommenderFooter;
