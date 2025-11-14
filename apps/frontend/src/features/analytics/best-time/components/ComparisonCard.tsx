/**
 * ComparisonCard Component
 * 
 * Shows potential engagement improvement by posting at recommended times
 * Displays "before vs after" comparison
 */

import React from 'react';
import {
    Box,
    Card,
    CardContent,
    Typography,
    Grid,
    Chip
} from '@mui/material';
import {
    TrendingUp as TrendingUpIcon,
    TrendingDown as TrendingDownIcon,
    ArrowForward as ArrowIcon
} from '@mui/icons-material';

interface ComparisonData {
    currentAvgEngagement: number;
    recommendedAvgEngagement: number;
    currentHour?: number;
    recommendedHour: number;
    recommendedDay: string;
    improvementPercentage: number;
}

interface ComparisonCardProps {
    comparison: ComparisonData;
}

const ComparisonCard: React.FC<ComparisonCardProps> = ({ comparison }) => {
    const {
        currentAvgEngagement,
        recommendedAvgEngagement,
        currentHour,
        recommendedHour,
        recommendedDay,
        improvementPercentage
    } = comparison;

    const formatHour = (hour: number): string => {
        if (hour === 0) return '12:00 AM';
        if (hour < 12) return `${hour}:00 AM`;
        if (hour === 12) return '12:00 PM';
        return `${hour - 12}:00 PM`;
    };

    const isImprovement = improvementPercentage > 0;

    return (
        <Card sx={{ mb: 3, border: 2, borderColor: isImprovement ? 'success.main' : 'warning.main' }}>
            <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                    <Typography variant="h6">
                        💡 Potential Improvement
                    </Typography>
                    <Chip
                        icon={isImprovement ? <TrendingUpIcon /> : <TrendingDownIcon />}
                        label={`${improvementPercentage > 0 ? '+' : ''}${improvementPercentage.toFixed(1)}%`}
                        color={isImprovement ? 'success' : 'warning'}
                        size="small"
                    />
                </Box>

                <Grid container spacing={3} alignItems="center">
                    {/* Current Performance */}
                    <Grid item xs={12} sm={5}>
                        <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'action.hover', borderRadius: 1 }}>
                            <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
                                {currentHour !== undefined ? 'Your Usual Time' : 'Current Average'}
                            </Typography>
                            {currentHour !== undefined && (
                                <Typography variant="body2" color="text.secondary" gutterBottom>
                                    {formatHour(currentHour)}
                                </Typography>
                            )}
                            <Typography variant="h4" color="text.secondary">
                                {currentAvgEngagement.toFixed(1)}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                                avg engagement
                            </Typography>
                        </Box>
                    </Grid>

                    {/* Arrow */}
                    <Grid item xs={12} sm={2}>
                        <Box sx={{ display: 'flex', justifyContent: 'center' }}>
                            <ArrowIcon sx={{ fontSize: 40, color: 'primary.main' }} />
                        </Box>
                    </Grid>

                    {/* Recommended Performance */}
                    <Grid item xs={12} sm={5}>
                        <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'success.light', borderRadius: 1, border: 2, borderColor: 'success.main' }}>
                            <Typography variant="caption" fontWeight="bold" display="block" gutterBottom>
                                Recommended Time
                            </Typography>
                            <Typography variant="body2" fontWeight="bold" gutterBottom>
                                {recommendedDay} {formatHour(recommendedHour)}
                            </Typography>
                            <Typography variant="h4" color="success.dark" fontWeight="bold">
                                {recommendedAvgEngagement.toFixed(1)}
                            </Typography>
                            <Typography variant="caption" color="success.dark">
                                avg engagement
                            </Typography>
                        </Box>
                    </Grid>
                </Grid>

                <Box sx={{ mt: 2, p: 2, bgcolor: isImprovement ? 'success.light' : 'warning.light', borderRadius: 1 }}>
                    <Typography variant="body2" textAlign="center">
                        {isImprovement ? (
                            <>
                                📈 By posting at <strong>{recommendedDay} {formatHour(recommendedHour)}</strong>, 
                                you could improve engagement by <strong>{improvementPercentage.toFixed(1)}%</strong>
                            </>
                        ) : (
                            <>
                                ℹ️ Your current posting time is already performing well
                            </>
                        )}
                    </Typography>
                </Box>
            </CardContent>
        </Card>
    );
};

export default ComparisonCard;
