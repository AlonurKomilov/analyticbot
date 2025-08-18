import React, { useState, useEffect, useMemo, useCallback } from 'react';
import {
    Paper,
    Typography,
    Box,
    Grid,
    Card,
    CardContent,
    CircularProgress,
    Alert,
    Chip,
    LinearProgress,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Tooltip,
    Avatar,
    List,
    ListItem,
    ListItemAvatar,
    ListItemText,
    ListItemSecondaryAction,
    IconButton,
    Divider
} from '@mui/material';
import {
    AccessTime as TimeIcon,
    TrendingUp as TrendingUpIcon,
    Psychology as AIIcon,
    Schedule as ScheduleIcon,
    Star as StarIcon,
    Lightbulb as BulbIcon,
    CalendarToday as CalendarIcon,
    Notifications as NotifyIcon,
    CheckCircle as CheckIcon
} from '@mui/icons-material';

const BestTimeRecommender = () => {
    const [timeFrame, setTimeFrame] = useState('week');
    const [contentType, setContentType] = useState('all');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [recommendations, setRecommendations] = useState(null);
    const [aiInsights, setAiInsights] = useState([]);

    // Best time recommendations'ni yuklash
    const loadRecommendations = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);
            
            const response = await fetch(`http://localhost:8001/api/analytics/best-posting-time?timeframe=${timeFrame}&content_type=${contentType}`);
            if (!response.ok) throw new Error('Best time recommendations olishda xatolik');
            
            const result = await response.json();
            setRecommendations(result);
            
            // AI insights'ni ham yuklash
            if (result.ai_recommendations) {
                setAiInsights(result.ai_recommendations);
            }
        } catch (err) {
            setError(err.message);
            console.error('Best time malumotlarini olishda xatolik:', err);
        } finally {
            setLoading(false);
        }
    }, [timeFrame, contentType]);

    // Component mount va filter o'zgarganda ma'lumot yuklash
    useEffect(() => {
        loadRecommendations();
    }, [loadRecommendations]);

    // Haftaning kunlari
    const daysOfWeek = ['Dushanba', 'Seshanba', 'Chorshanba', 'Payshanba', 'Juma', 'Shanba', 'Yakshanba'];
    
    // Soat formatini o'zgartirish
    const formatHour = (hour) => {
        if (hour === 0) return '12:00 AM';
        if (hour < 12) return `${hour}:00 AM`;
        if (hour === 12) return '12:00 PM';
        return `${hour - 12}:00 PM`;
    };

    // Confidence level rangini olish
    const getConfidenceColor = (confidence) => {
        if (confidence >= 80) return 'success';
        if (confidence >= 60) return 'warning';
        return 'error';
    };

    // Heat map uchun rang olish
    const getHeatmapColor = (value, max) => {
        const intensity = value / max;
        if (intensity > 0.8) return '#2e7d32'; // Dark green
        if (intensity > 0.6) return '#388e3c'; // Green
        if (intensity > 0.4) return '#66bb6a'; // Light green
        if (intensity > 0.2) return '#a5d6a7'; // Very light green
        return '#e8f5e8'; // Almost white green
    };

    // AI tavsiyalarni formatlash
    const formatAIInsight = (insight) => {
        const icons = {
            time: '⏰',
            content: '📝',
            audience: '👥',
            trend: '📈',
            warning: '⚠️',
            tip: '💡'
        };
        return icons[insight.type] || '🤖';
    };

    // Heatmap ma'lumotlari
    const heatmapData = useMemo(() => {
        if (!recommendations?.hourly_performance) return [];
        
        const maxValue = Math.max(...Object.values(recommendations.hourly_performance));
        return Object.entries(recommendations.hourly_performance).map(([hour, value]) => ({
            hour: parseInt(hour),
            value,
            intensity: value / maxValue,
            color: getHeatmapColor(value, maxValue)
        }));
    }, [recommendations]);

    if (error) {
        return (
            <Paper sx={{ p: 3 }}>
                <Alert severity="error">
                    {error}
                </Alert>
            </Paper>
        );
    }

    return (
        <Paper sx={{ p: 3 }}>
            {/* Header */}
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <AIIcon color="primary" />
                    <Typography variant="h6">
                        AI Best Time Recommendations
                    </Typography>
                </Box>
                
                <Box sx={{ display: 'flex', gap: 2 }}>
                    {/* Time Frame Filter */}
                    <FormControl size="small" sx={{ minWidth: 120 }}>
                        <InputLabel>Vaqt oralig'i</InputLabel>
                        <Select
                            value={timeFrame}
                            label="Vaqt oralig'i"
                            onChange={(e) => setTimeFrame(e.target.value)}
                        >
                            <MenuItem value="week">Bu hafta</MenuItem>
                            <MenuItem value="month">Bu oy</MenuItem>
                            <MenuItem value="quarter">Bu chorak</MenuItem>
                        </Select>
                    </FormControl>

                    {/* Content Type Filter */}
                    <FormControl size="small" sx={{ minWidth: 120 }}>
                        <InputLabel>Kontent turi</InputLabel>
                        <Select
                            value={contentType}
                            label="Kontent turi"
                            onChange={(e) => setContentType(e.target.value)}
                        >
                            <MenuItem value="all">Barchasi</MenuItem>
                            <MenuItem value="photo">Rasm</MenuItem>
                            <MenuItem value="video">Video</MenuItem>
                            <MenuItem value="text">Matn</MenuItem>
                        </Select>
                    </FormControl>
                </Box>
            </Box>

            {loading && (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                    <CircularProgress />
                    <Typography variant="body2" sx={{ ml: 2 }}>
                        AI tavsiyalari tahlil qilinmoqda...
                    </Typography>
                </Box>
            )}

            {!loading && recommendations && (
                <Grid container spacing={3}>
                    {/* Main Recommendations */}
                    <Grid item xs={12} md={8}>
                        <Card variant="outlined">
                            <CardContent>
                                <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                                    <StarIcon color="warning" />
                                    Eng yaxshi vaqtlar
                                </Typography>

                                {/* Best Times Grid */}
                                <Grid container spacing={2} sx={{ mb: 3 }}>
                                    {recommendations.best_times?.slice(0, 3).map((time, index) => (
                                        <Grid item xs={12} sm={4} key={index}>
                                            <Card 
                                                variant="outlined" 
                                                sx={{ 
                                                    bgcolor: index === 0 ? 'success.light' : 'background.default',
                                                    border: index === 0 ? '2px solid' : '1px solid',
                                                    borderColor: index === 0 ? 'success.main' : 'divider'
                                                }}
                                            >
                                                <CardContent sx={{ p: 2, textAlign: 'center' }}>
                                                    {index === 0 && (
                                                        <Chip 
                                                            size="small" 
                                                            label="🏆 TOP" 
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

                                {/* Hourly Heatmap */}
                                <Typography variant="subtitle1" sx={{ mb: 2 }}>
                                    24 soatlik faollik haritasi
                                </Typography>
                                <Box sx={{ display: 'flex', gap: 0.5, mb: 2, flexWrap: 'wrap' }}>
                                    {heatmapData.map((item) => (
                                        <Tooltip 
                                            key={item.hour}
                                            title={`${formatHour(item.hour)}: ${item.value} faollik`}
                                        >
                                            <Box
                                                sx={{
                                                    width: 40,
                                                    height: 40,
                                                    bgcolor: item.color,
                                                    border: '1px solid #ddd',
                                                    borderRadius: 1,
                                                    display: 'flex',
                                                    alignItems: 'center',
                                                    justifyContent: 'center',
                                                    cursor: 'pointer',
                                                    '&:hover': { 
                                                        transform: 'scale(1.1)',
                                                        boxShadow: 2
                                                    }
                                                }}
                                            >
                                                <Typography variant="caption" fontWeight="bold">
                                                    {item.hour}
                                                </Typography>
                                            </Box>
                                        </Tooltip>
                                    ))}
                                </Box>
                            </CardContent>
                        </Card>
                    </Grid>

                    {/* AI Insights Sidebar */}
                    <Grid item xs={12} md={4}>
                        <Card variant="outlined">
                            <CardContent>
                                <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                                    <BulbIcon color="warning" />
                                    AI Tavsiyalari
                                </Typography>

                                {/* Current Recommendations */}
                                <List dense>
                                    {aiInsights.slice(0, 5).map((insight, index) => (
                                        <React.Fragment key={index}>
                                            <ListItem sx={{ px: 0 }}>
                                                <ListItemAvatar>
                                                    <Avatar sx={{ bgcolor: 'primary.light', width: 32, height: 32 }}>
                                                        {formatAIInsight(insight)}
                                                    </Avatar>
                                                </ListItemAvatar>
                                                <ListItemText
                                                    primary={
                                                        <Typography variant="body2" fontWeight="medium">
                                                            {insight.title}
                                                        </Typography>
                                                    }
                                                    secondary={
                                                        <Typography variant="caption" color="text.secondary">
                                                            {insight.description}
                                                        </Typography>
                                                    }
                                                />
                                                <ListItemSecondaryAction>
                                                    <Chip 
                                                        size="small" 
                                                        label={`${insight.confidence}%`}
                                                        color={getConfidenceColor(insight.confidence)}
                                                        variant="outlined"
                                                    />
                                                </ListItemSecondaryAction>
                                            </ListItem>
                                            {index < aiInsights.length - 1 && <Divider />}
                                        </React.Fragment>
                                    ))}
                                </List>

                                {/* Quick Actions */}
                                <Box sx={{ mt: 3 }}>
                                    <Typography variant="subtitle2" sx={{ mb: 1 }}>
                                        Tezkor amallar
                                    </Typography>
                                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                                        <Chip
                                            icon={<ScheduleIcon />}
                                            label="Post rejalash"
                                            clickable
                                            color="primary"
                                            variant="outlined"
                                            size="small"
                                        />
                                        <Chip
                                            icon={<NotifyIcon />}
                                            label="Eslatma o'rnatish"
                                            clickable
                                            color="secondary"
                                            variant="outlined"
                                            size="small"
                                        />
                                        <Chip
                                            icon={<CheckIcon />}
                                            label="Tavsiyani qo'llash"
                                            clickable
                                            color="success"
                                            variant="outlined"
                                            size="small"
                                        />
                                    </Box>
                                </Box>
                            </CardContent>
                        </Card>
                    </Grid>

                    {/* Weekly Performance Summary */}
                    <Grid item xs={12}>
                        <Card variant="outlined">
                            <CardContent>
                                <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                                    <CalendarIcon color="primary" />
                                    Haftalik xulosalar
                                </Typography>

                                <Grid container spacing={2}>
                                    {recommendations.weekly_summary && Object.entries(recommendations.weekly_summary).map(([day, data], index) => (
                                        <Grid item xs={12} sm={6} md={3} lg={2} xl={1.5} key={day}>
                                            <Card variant="outlined" sx={{ textAlign: 'center' }}>
                                                <CardContent sx={{ p: 2 }}>
                                                    <Typography variant="subtitle2" gutterBottom>
                                                        {daysOfWeek[index]}
                                                    </Typography>
                                                    <Typography variant="h6" color="primary">
                                                        {formatHour(data.best_hour)}
                                                    </Typography>
                                                    <LinearProgress 
                                                        variant="determinate" 
                                                        value={data.performance} 
                                                        sx={{ mt: 1, mb: 1 }}
                                                        color={data.performance > 70 ? 'success' : data.performance > 40 ? 'warning' : 'error'}
                                                    />
                                                    <Typography variant="caption" color="text.secondary">
                                                        {data.performance}% samarali
                                                    </Typography>
                                                </CardContent>
                                            </Card>
                                        </Grid>
                                    ))}
                                </Grid>
                            </CardContent>
                        </Card>
                    </Grid>
                </Grid>
            )}

            {!loading && !recommendations && (
                <Box sx={{ 
                    display: 'flex', 
                    flexDirection: 'column', 
                    alignItems: 'center', 
                    justifyContent: 'center', 
                    height: 300,
                    color: 'text.secondary'
                }}>
                    <AIIcon sx={{ fontSize: 64, mb: 2, opacity: 0.5 }} />
                    <Typography variant="h6" gutterBottom>
                        Tavsiyalar mavjud emas
                    </Typography>
                    <Typography variant="body2">
                        AI tavsiyalarini olish uchun ma'lumotlar yetarli emas
                    </Typography>
                </Box>
            )}

            {/* Status Footer */}
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
                        label="🤖 AI Powered" 
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
        </Paper>
    );
};

export default BestTimeRecommender;
