/**
 * EnhancedCalendarTooltip Component
 *
 * Rich tooltip for calendar days showing:
 * - Content-type breakdown (video/image/text performance)
 * - Day-hour combination recommendations
 * - Engagement metrics and trends
 */

import React from 'react';
import {
    Box,
    Typography,
    Chip,
    Divider,
    LinearProgress
} from '@mui/material';
import {
    TrendingUp as TrendingUpIcon,
    TrendingDown as TrendingDownIcon,
    VideoLibrary as VideoIcon,
    Image as ImageIcon,
    TextFields as TextIcon,
    Schedule as ScheduleIcon
} from '@mui/icons-material';

interface DayPerformance {
    date: number;
    dayOfWeek: number;
    avgEngagement?: number;
    postCount?: number;
    score?: 'excellent' | 'good' | 'average' | 'poor' | 'no-data';
    isToday?: boolean;
    isPast?: boolean;
    isFuture?: boolean;
    recommendationScore?: number;
    confidence?: number;
    recommendedTimes?: string[];
}

interface ContentTypeBreakdown {
    video?: { count: number; avgEngagement: number };
    image?: { count: number; avgEngagement: number };
    text?: { count: number; avgEngagement: number };
}

interface DayHourRecommendation {
    hour: number;
    confidence: number;
    avgEngagement: number;
}

interface EnhancedCalendarTooltipProps {
    day: DayPerformance;
    statusLabel: string;
    contentTypeBreakdown?: ContentTypeBreakdown;
    dayHourRecommendations?: DayHourRecommendation[];
}

const EnhancedCalendarTooltip: React.FC<EnhancedCalendarTooltipProps> = ({
    day,
    statusLabel,
    contentTypeBreakdown,
    dayHourRecommendations
}) => {
    const daysOfWeek = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

    const formatHour = (hour: number): string => {
        if (hour === 0) return '12:00 AM';
        if (hour < 12) return `${hour}:00 AM`;
        if (hour === 12) return '12:00 PM';
        return `${hour - 12}:00 PM`;
    };

    const getConfidenceColor = (confidence: number): 'success' | 'warning' | 'error' => {
        if (confidence >= 75) return 'success';
        if (confidence >= 50) return 'warning';
        return 'error';
    };

    const renderContentTypeIcon = (type: string) => {
        switch (type) {
            case 'video': return <VideoIcon sx={{ fontSize: 14 }} />;
            case 'image': return <ImageIcon sx={{ fontSize: 14 }} />;
            case 'text': return <TextIcon sx={{ fontSize: 14 }} />;
            default: return null;
        }
    };

    return (
        <Box sx={{ p: 1, minWidth: 250, maxWidth: 300 }}>
            {/* Header */}
            <Box sx={{ mb: 1.5 }}>
                <Typography variant="body2" sx={{ fontWeight: 'bold', mb: 0.5 }}>
                    {day.isToday ? 'Today' : daysOfWeek[day.dayOfWeek]}
                    {day.isToday && ' 🎯'}
                    <Typography component="span" sx={{ ml: 1, color: 'text.secondary' }}>
                        Day {day.date}
                    </Typography>
                </Typography>
                <Chip
                    label={statusLabel}
                    size="small"
                    color={
                        day.score === 'excellent' ? 'success' :
                        day.score === 'good' ? 'primary' :
                        day.score === 'average' ? 'warning' :
                        'default'
                    }
                    sx={{ height: 20 }}
                />
            </Box>

            <Divider sx={{ my: 1 }} />

            {/* Historical Data Section */}
            {day.isPast && day.postCount && day.postCount > 0 ? (
                <>
                    <Box sx={{ mb: 1.5 }}>
                        <Typography variant="caption" display="block" sx={{ fontWeight: 'bold', mb: 0.5 }}>
                            📊 Historical Performance
                        </Typography>
                        <Typography variant="caption" display="block" color="text.secondary">
                            {day.postCount} posts • Avg engagement: {day.avgEngagement?.toFixed(2) || 'N/A'}
                        </Typography>
                    </Box>

                    {/* Content Type Breakdown */}
                    {contentTypeBreakdown && (
                        <Box sx={{ mb: 1.5 }}>
                            <Typography variant="caption" display="block" sx={{ fontWeight: 'bold', mb: 0.5 }}>
                                Content Performance
                            </Typography>
                            {contentTypeBreakdown.video && contentTypeBreakdown.video.count > 0 && (
                                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.5 }}>
                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                        {renderContentTypeIcon('video')}
                                        <Typography variant="caption">Video ({contentTypeBreakdown.video.count})</Typography>
                                    </Box>
                                    <Typography variant="caption" fontWeight="bold">
                                        {contentTypeBreakdown.video.avgEngagement.toFixed(1)}
                                    </Typography>
                                </Box>
                            )}
                            {contentTypeBreakdown.image && contentTypeBreakdown.image.count > 0 && (
                                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.5 }}>
                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                        {renderContentTypeIcon('image')}
                                        <Typography variant="caption">Image ({contentTypeBreakdown.image.count})</Typography>
                                    </Box>
                                    <Typography variant="caption" fontWeight="bold">
                                        {contentTypeBreakdown.image.avgEngagement.toFixed(1)}
                                    </Typography>
                                </Box>
                            )}
                            {contentTypeBreakdown.text && contentTypeBreakdown.text.count > 0 && (
                                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.5 }}>
                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                        {renderContentTypeIcon('text')}
                                        <Typography variant="caption">Text ({contentTypeBreakdown.text.count})</Typography>
                                    </Box>
                                    <Typography variant="caption" fontWeight="bold">
                                        {contentTypeBreakdown.text.avgEngagement.toFixed(1)}
                                    </Typography>
                                </Box>
                            )}
                        </Box>
                    )}
                </>
            ) : day.isFuture || day.isToday ? (
                <>
                    {/* Recommendation Section */}
                    <Box sx={{ mb: 1.5 }}>
                        <Typography variant="caption" display="block" sx={{ fontWeight: 'bold', mb: 0.5 }}>
                            🎯 Recommendation
                        </Typography>
                        <Box sx={{ mb: 1 }}>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                                <Typography variant="caption" color="text.secondary">Score</Typography>
                                <Typography variant="caption" fontWeight="bold">
                                    {day.recommendationScore || 'N/A'}/100
                                </Typography>
                            </Box>
                            {day.recommendationScore !== undefined && (
                                <LinearProgress
                                    variant="determinate"
                                    value={day.recommendationScore}
                                    color={
                                        day.recommendationScore >= 80 ? 'success' :
                                        day.recommendationScore >= 60 ? 'primary' :
                                        'warning'
                                    }
                                    sx={{ height: 4, borderRadius: 2 }}
                                />
                            )}
                        </Box>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                            <Typography variant="caption" color="text.secondary">Confidence</Typography>
                            <Chip
                                label={`${day.confidence || 'N/A'}%`}
                                size="small"
                                color={day.confidence ? getConfidenceColor(day.confidence) : 'default'}
                                sx={{ height: 18, fontSize: '0.7rem' }}
                            />
                        </Box>
                    </Box>
                </>
            ) : (
                <Typography variant="caption" display="block" color="text.secondary" sx={{ mb: 1 }}>
                    No posts on this day
                </Typography>
            )}

            {/* Best Times Section */}
            {day.recommendedTimes && day.recommendedTimes.length > 0 && (
                <Box sx={{ mt: 1.5, p: 1, bgcolor: 'action.hover', borderRadius: 1 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.5 }}>
                        <ScheduleIcon sx={{ fontSize: 14 }} />
                        <Typography variant="caption" sx={{ fontWeight: 'bold' }}>
                            Best Times
                        </Typography>
                    </Box>
                    <Typography variant="caption" display="block" color="text.secondary">
                        {day.recommendedTimes.slice(0, 3).join(' • ')}
                    </Typography>
                </Box>
            )}

            {/* Day-Hour Specific Recommendations */}
            {dayHourRecommendations && dayHourRecommendations.length > 0 && (
                <Box sx={{ mt: 1.5 }}>
                    <Typography variant="caption" display="block" sx={{ fontWeight: 'bold', mb: 0.5 }}>
                        ⭐ Top Hour
                    </Typography>
                    {dayHourRecommendations.slice(0, 1).map((rec, index) => (
                        <Box key={index} sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <Typography variant="caption">
                                {formatHour(rec.hour)}
                            </Typography>
                            <Box sx={{ display: 'flex', gap: 0.5, alignItems: 'center' }}>
                                <Typography variant="caption" fontWeight="bold">
                                    {rec.avgEngagement.toFixed(1)}
                                </Typography>
                                <Chip
                                    label={`${rec.confidence.toFixed(0)}%`}
                                    size="small"
                                    color={getConfidenceColor(rec.confidence)}
                                    sx={{ height: 18, fontSize: '0.7rem' }}
                                />
                            </Box>
                        </Box>
                    ))}
                </Box>
            )}

            {/* Trend Indicator */}
            {day.avgEngagement !== undefined && day.isPast && (
                <Box sx={{ mt: 1.5, display: 'flex', alignItems: 'center', gap: 0.5 }}>
                    {day.avgEngagement > 5 ? (
                        <>
                            <TrendingUpIcon sx={{ fontSize: 14, color: 'success.main' }} />
                            <Typography variant="caption" color="success.main">
                                Above average performance
                            </Typography>
                        </>
                    ) : (
                        <>
                            <TrendingDownIcon sx={{ fontSize: 14, color: 'warning.main' }} />
                            <Typography variant="caption" color="warning.main">
                                Below average performance
                            </Typography>
                        </>
                    )}
                </Box>
            )}
        </Box>
    );
};

export default EnhancedCalendarTooltip;
