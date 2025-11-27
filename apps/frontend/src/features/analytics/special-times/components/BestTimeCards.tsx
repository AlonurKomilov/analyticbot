import React from 'react';
import {
    Box,
    Grid,
    Card,
    CardContent,
    Typography,
    Chip,
    LinearProgress,
    Button
} from '@mui/material';
import { Event as EventIcon } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { daysOfWeek, formatHour, getConfidenceColor } from '../utils/timeUtils';

interface BestTime {
    day: number;
    hour: number;
    confidence: number;
    avg_engagement: number;
}

interface Recommendations {
    best_times?: BestTime[];
    total_posts_analyzed?: number;
}

interface BestTimeCardsProps {
    recommendations: Recommendations;
    channelId?: string;
}

const BestTimeCards: React.FC<BestTimeCardsProps> = ({ recommendations, channelId }) => {
    const navigate = useNavigate();

    const handleSchedulePost = (day: number, hour: number) => {
        const now = new Date();
        const targetDate = new Date(now);

        // Calculate next occurrence of the target day/hour
        const currentDay = now.getDay();
        const daysUntilTarget = (day - currentDay + 7) % 7 || 7;
        targetDate.setDate(now.getDate() + daysUntilTarget);
        targetDate.setHours(hour, 0, 0, 0);

        // If the target time is in the past today, schedule for next week
        if (targetDate <= now && daysUntilTarget === 7) {
            targetDate.setDate(targetDate.getDate() + 7);
        }

        // Format as datetime-local string (YYYY-MM-DDTHH:mm) in local timezone
        const year = targetDate.getFullYear();
        const month = String(targetDate.getMonth() + 1).padStart(2, '0');
        const date = String(targetDate.getDate()).padStart(2, '0');
        const hours = String(targetDate.getHours()).padStart(2, '0');
        const minutes = String(targetDate.getMinutes()).padStart(2, '0');
        const datetimeLocal = `${year}-${month}-${date}T${hours}:${minutes}`;

        navigate('/posts/create', {
            state: {
                channelId: channelId,
                scheduledTime: datetimeLocal,
                fromRecommendation: true
            }
        });
    };
    if (!recommendations?.best_times || recommendations.best_times.length === 0) {
        return null;
    }

    // Sort by HIGHEST confidence and show top 5 recommendations
    const topRecommendations = [...recommendations.best_times]
        .sort((a, b) => b.confidence - a.confidence) // Highest confidence first
        .slice(0, 5);

    return (
        <Box sx={{ mb: 4 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                    🏆 Top 5 Best Times
                </Typography>
                <Typography variant="caption" color="text.secondary">
                    {recommendations.total_posts_analyzed ? 
                        `${recommendations.total_posts_analyzed.toLocaleString()} posts analyzed` : 
                        `${recommendations.best_times.length} recommendations`
                    }
                </Typography>
            </Box>
            <Grid container spacing={2}>
                {topRecommendations.map((time, index) => (
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
                                        Confidence Level
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
                                    Average: {time.avg_engagement} engagement
                                </Typography>

                                {channelId && (
                                    <Button
                                        variant="contained"
                                        color="success"
                                        size="small"
                                        fullWidth
                                        startIcon={<EventIcon />}
                                        onClick={() => handleSchedulePost(time.day, time.hour)}
                                        sx={{ mt: 2 }}
                                    >
                                        Schedule Post
                                    </Button>
                                )}
                            </CardContent>
                        </Card>
                    </Grid>
                ))}
            </Grid>
        </Box>
    );
};

export default BestTimeCards;
