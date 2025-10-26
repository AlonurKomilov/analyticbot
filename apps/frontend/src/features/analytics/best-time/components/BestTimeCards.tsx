import React from 'react';
import {
    Box,
    Grid,
    Card,
    CardContent,
    Typography,
    Chip,
    LinearProgress
} from '@mui/material';
import { daysOfWeek, formatHour, getConfidenceColor } from '../utils/timeUtils.js';

interface BestTime {
    day: number;
    hour: number;
    confidence: number;
    avg_engagement: number;
}

interface Recommendations {
    best_times?: BestTime[];
}

interface BestTimeCardsProps {
    recommendations: Recommendations;
}

const BestTimeCards: React.FC<BestTimeCardsProps> = ({ recommendations }) => {
    if (!recommendations?.best_times || recommendations.best_times.length === 0) {
        return null;
    }

    return (
        <Box sx={{ mb: 4 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
                🏆 Eng yaxshi vaqtlar
            </Typography>
            <Grid container spacing={2}>
                {recommendations.best_times.map((time, index) => (
                    <Grid item xs={12} sm={6} md={4} key={index}>
                        <Card
                            sx={{
                                height: '100%',
                                border: index === 0 ? 2 : 1,
                                borderColor: index === 0 ? 'success.main' : 'divider',
                                position: 'relative'
                            }}
                        >
                            <CardContent sx={{ textAlign: 'center', p: 2 }}>
                                {index === 0 && (
                                    <Chip
                                        size="small"
                                        label={<><span aria-hidden="true">🏆</span> TOP</>}
                                        color="success"
                                        sx={{ mb: 1 }}
                                    />
                                )}
                                <Typography variant="h6" sx={{ mb: 1 }}>
                                    {daysOfWeek[time.day]}
                                </Typography>
                                <Typography variant="h5" color="primary" sx={{ mb: 1 }}>
                                    {formatHour(time.hour)}
                                </Typography>
                                <Box sx={{ mb: 2 }}>
                                    <Typography variant="caption" color="text.secondary">
                                        Ishonch darajasi
                                    </Typography>
                                    <LinearProgress
                                        variant="determinate"
                                        value={time.confidence}
                                        color={getConfidenceColor(time.confidence)}
                                        sx={{ mt: 0.5, height: 6, borderRadius: 3 }}
                                    />
                                    <Typography variant="caption" sx={{ mt: 0.5 }}>
                                        {time.confidence}%
                                    </Typography>
                                </Box>
                                <Typography variant="body2" color="text.secondary">
                                    O'rtacha: {time.avg_engagement} faollik
                                </Typography>
                            </CardContent>
                        </Card>
                    </Grid>
                ))}
            </Grid>
        </Box>
    );
};

export default BestTimeCards;
