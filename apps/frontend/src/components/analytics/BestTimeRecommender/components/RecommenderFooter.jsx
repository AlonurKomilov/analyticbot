import React from 'react';
import {
    Box,
    Typography,
    Chip
} from '@mui/material';

const RecommenderFooter = ({ recommendations }) => {
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
                AI tahlili: {new Date().toLocaleTimeString()} da yangilangan
            </Typography>
            <Box sx={{ display: 'flex', gap: 1 }}>
                <Chip
                    size="small"
                    label={<><span aria-hidden="true">🤖</span> AI Powered</>}
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
