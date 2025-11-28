/**
 * SmartRecommendationsPanel Component
 *
 * Displays top 5 actionable posting recommendations with:
 * - Day-hour combinations
 * - Content-type specific recommendations
 * - Confidence scores and engagement predictions
 */

import React from 'react';
import {
    Box,
    Card,
    CardContent,
    Typography,
    Chip,
    LinearProgress,
    Grid,
    Tooltip,
    IconButton,
    Divider,
    Alert,
    ToggleButtonGroup,
    ToggleButton
} from '@mui/material';
import {
    Event as EventIcon,
    TrendingUp as TrendingUpIcon,
    VideoLibrary as VideoIcon,
    Image as ImageIcon,
    TextFields as TextIcon,
    Link as LinkIcon,
    Info as InfoIcon,
    Schedule as ScheduleIcon
} from '@mui/icons-material';

interface DayHourCombination {
    day: number; // 0-6
    hour: number; // 0-23
    confidence: number;
    avg_engagement: number;
    post_count: number;
}

interface ContentTypeRecommendation {
    content_type: 'video' | 'image' | 'text' | 'link';
    hour: number;
    confidence: number;
    avg_engagement: number;
    post_count: number;
}

interface SmartRecommendationsPanelProps {
    dayHourCombinations?: DayHourCombination[];
    contentTypeRecommendations?: ContentTypeRecommendation[];
    selectedContentType?: 'all' | 'video' | 'image' | 'text' | 'link';
    onContentTypeChange?: (type: 'all' | 'video' | 'image' | 'text' | 'link') => void;
    totalPostsAnalyzed?: number;
}

const SmartRecommendationsPanel: React.FC<SmartRecommendationsPanelProps> = ({
    dayHourCombinations = [],
    contentTypeRecommendations = [],
    selectedContentType = 'all',
    onContentTypeChange,
    totalPostsAnalyzed
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

    const getContentTypeIcon = (type: string) => {
        switch (type) {
            case 'video': return <VideoIcon fontSize="small" />;
            case 'image': return <ImageIcon fontSize="small" />;
            case 'text': return <TextIcon fontSize="small" />;
            case 'link': return <LinkIcon fontSize="small" />;
            default: return <EventIcon fontSize="small" />;
        }
    };

    // Filter content type recommendations if a specific type is selected
    const filteredContentRecs = selectedContentType === 'all'
        ? contentTypeRecommendations
        : contentTypeRecommendations.filter(rec => rec.content_type === selectedContentType);

    // Sort by HIGHEST confidence first and show top 3 combinations + top 3 content insights
    const topDayHour = dayHourCombinations
        .sort((a, b) => b.confidence - a.confidence) // Highest confidence first
        .slice(0, 3); // Show top 3 combinations

    const topContentType = filteredContentRecs
        .sort((a, b) => b.confidence - a.confidence) // Highest confidence first
        .slice(0, 3); // Show top 3 content insights

    const hasRecommendations = topDayHour.length > 0 || topContentType.length > 0;

    if (!hasRecommendations) {
        return (
            <Card>
                <CardContent>
                    <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <TrendingUpIcon color="primary" />
                        Smart Recommendations
                    </Typography>
                    <Alert severity="info">
                        Not enough data for advanced recommendations. Keep posting to build recommendation history!
                    </Alert>
                </CardContent>
            </Card>
        );
    }

    return (
        <Card>
            <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <TrendingUpIcon color="primary" />
                        Smart Recommendations
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {totalPostsAnalyzed && (
                            <Chip 
                                label={`${totalPostsAnalyzed.toLocaleString()} posts analyzed`}
                                size="small"
                                variant="outlined"
                                color="primary"
                            />
                        )}
                        <Tooltip title="Based on advanced analysis of your posting history">
                            <IconButton size="small">
                                <InfoIcon fontSize="small" />
                            </IconButton>
                        </Tooltip>
                    </Box>
                </Box>

                {/* Best Day + Time Combinations - Top 3 by Confidence */}
                {topDayHour.length > 0 && (
                    <>
                        <Typography variant="subtitle2" color="text.secondary" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                            <ScheduleIcon fontSize="small" />
                            Best Day + Time Combinations
                        </Typography>
                        <Grid container spacing={2} sx={{ mb: 3 }}>
                            {topDayHour.map((rec, index) => (
                                <Grid item xs={12} key={index}>
                                    <Box sx={{
                                        p: 2,
                                        bgcolor: 'background.default',
                                        borderRadius: 1,
                                        border: 1,
                                        borderColor: 'divider'
                                    }}>
                                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                <EventIcon color="primary" fontSize="small" />
                                                <Typography variant="body1" fontWeight="bold">
                                                    {daysOfWeek[rec.day]} at {formatHour(rec.hour)}
                                                </Typography>
                                            </Box>
                                            <Chip
                                                label={`${rec.confidence.toFixed(0)}% confidence`}
                                                color={getConfidenceColor(rec.confidence)}
                                                size="small"
                                            />
                                        </Box>
                                        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', mb: 1 }}>
                                            <Typography variant="caption" color="text.secondary">
                                                Avg Engagement: <strong>{rec.avg_engagement.toFixed(1)}</strong>
                                            </Typography>
                                            <Typography variant="caption" color="text.secondary">
                                                Based on {rec.post_count} posts
                                            </Typography>
                                        </Box>
                                        <LinearProgress
                                            variant="determinate"
                                            value={rec.confidence}
                                            color={getConfidenceColor(rec.confidence)}
                                            sx={{ height: 6, borderRadius: 3 }}
                                        />
                                    </Box>
                                </Grid>
                            ))}
                        </Grid>
                    </>
                )}

                {/* Content Type Quick Insights - Always show filter if recommendations exist */}
                {contentTypeRecommendations.length > 0 && (
                    <>
                        <Divider sx={{ my: 2 }} />
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2, flexWrap: 'wrap', gap: 1 }}>
                            <Typography variant="subtitle2" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                {getContentTypeIcon(selectedContentType)}
                                📊 Content Type Insights
                            </Typography>
                            {onContentTypeChange && (
                                <Box sx={{ display: 'flex', gap: 0.5 }}>
                                    <Typography variant="caption" color="text.secondary" sx={{ mr: 1, alignSelf: 'center' }}>
                                        Filter by Content Type
                                    </Typography>
                                    <ToggleButtonGroup
                                        value={selectedContentType}
                                        exclusive
                                        onChange={(_e, newType) => newType && onContentTypeChange(newType)}
                                        size="small"
                                        aria-label="content type filter"
                                    >
                                        <ToggleButton value="all" aria-label="all content">
                                            <EventIcon fontSize="small" sx={{ mr: 0.5 }} />
                                            ALL
                                        </ToggleButton>
                                        <ToggleButton value="video" aria-label="video content">
                                            <VideoIcon fontSize="small" sx={{ mr: 0.5 }} />
                                            VIDEO
                                            {contentTypeRecommendations.filter(r => r.content_type === 'video').length > 0 && (
                                                <Chip label={contentTypeRecommendations.filter(r => r.content_type === 'video').length} size="small" sx={{ ml: 0.5, height: 18 }} />
                                            )}
                                        </ToggleButton>
                                        <ToggleButton value="image" aria-label="image content">
                                            <ImageIcon fontSize="small" sx={{ mr: 0.5 }} />
                                            IMAGE
                                        </ToggleButton>
                                        <ToggleButton value="text" aria-label="text content">
                                            <TextIcon fontSize="small" sx={{ mr: 0.5 }} />
                                            TEXT
                                            {contentTypeRecommendations.filter(r => r.content_type === 'text').length > 0 && (
                                                <Chip label={contentTypeRecommendations.filter(r => r.content_type === 'text').length} size="small" sx={{ ml: 0.5, height: 18 }} />
                                            )}
                                        </ToggleButton>
                                        <ToggleButton value="link" aria-label="link content">
                                            <LinkIcon fontSize="small" sx={{ mr: 0.5 }} />
                                            LINK
                                            {contentTypeRecommendations.filter(r => r.content_type === 'link').length > 0 && (
                                                <Chip label={contentTypeRecommendations.filter(r => r.content_type === 'link').length} size="small" sx={{ ml: 0.5, height: 18 }} />
                                            )}
                                        </ToggleButton>
                                    </ToggleButtonGroup>
                                </Box>
                            )}
                        </Box>
                        {topContentType.length > 0 ? (
                            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                            {topContentType.map((rec, index) => (
                                <Box
                                    key={index}
                                    sx={{
                                        display: 'flex',
                                        justifyContent: 'space-between',
                                        alignItems: 'center',
                                        p: 1.5,
                                        bgcolor: 'background.default',
                                        borderRadius: 1,
                                        border: 1,
                                        borderColor: 'divider',
                                        '&:hover': { bgcolor: 'action.hover' }
                                    }}
                                >
                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                        {getContentTypeIcon(rec.content_type)}
                                        <Typography variant="body2" fontWeight={500} sx={{ textTransform: 'capitalize' }}>
                                            {rec.content_type}
                                        </Typography>
                                        <Typography variant="body2" color="text.secondary">
                                            → {formatHour(rec.hour)}
                                        </Typography>
                                    </Box>
                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                                        <Typography variant="caption" color="text.secondary">
                                            {rec.avg_engagement.toFixed(1)} avg
                                        </Typography>
                                        <Chip
                                            label={`${rec.confidence.toFixed(0)}%`}
                                            color={getConfidenceColor(rec.confidence)}
                                            size="small"
                                            sx={{ minWidth: 60 }}
                                        />
                                    </Box>
                                </Box>
                            ))}
                        </Box>
                        ) : (
                            <Alert severity="info" sx={{ mt: 1 }}>
                                No recommendations available for {selectedContentType === 'all' ? 'any content type' : selectedContentType} posts. Try selecting a different content type.
                            </Alert>
                        )}
                    </>
                )}

                {/* Summary Stats */}
                <Box sx={{ mt: 3, p: 2, bgcolor: 'primary.light', borderRadius: 1 }}>
                    <Typography variant="caption" color="primary.dark">
                        💡 <strong>Pro Tip:</strong> Combine these insights with your content calendar for maximum impact.
                        Try posting {topContentType[0]?.content_type || 'content'} on {topDayHour[0] ? daysOfWeek[topDayHour[0].day] : 'recommended days'} for best results!
                    </Typography>
                </Box>
            </CardContent>
        </Card>
    );
};

export default SmartRecommendationsPanel;
