/**
 * 🏆 Rewards & Achievements Page
 *
 * Gamification center - achievements, referrals, streaks, and leaderboard.
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
    Container,
    Typography,
    Box,
    Grid,
    Card,
    CardContent,
    Button,
    Chip,
    Divider,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
    ListItemSecondaryAction,
    Alert,
    CircularProgress,
    Tabs,
    Tab,
    Paper,
    Avatar,
    Skeleton,
    IconButton,
    Tooltip,
    TextField,
    LinearProgress,
    Snackbar,
} from '@mui/material';
import {
    EmojiEvents as TrophyIcon,
    People as ReferralIcon,
    Leaderboard as LeaderboardIcon,
    LocalFireDepartment as StreakIcon,
    ContentCopy as CopyIcon,
    Share as ShareIcon,
    CheckCircle as CheckIcon,
    Lock as LockIcon,
    Star as StarIcon,
    Whatshot as FireIcon,
    MilitaryTech as MedalIcon,
    WorkspacePremium as PremiumIcon,
    Diamond as DiamondIcon,
    Visibility as ViewsIcon,
    Tv as ChannelIcon,
    PersonAdd as PersonAddIcon,
    Savings as SavingsIcon,
    Rocket as RocketIcon,
} from '@mui/icons-material';
import { useAuth } from '@/contexts/AuthContext';
import { apiClient } from '@/api/client';

// Types
interface Achievement {
    achievement_key: string;
    name: string;
    description: string | null;
    credit_reward: number;
    icon: string | null;
    category: string;
    is_earned: boolean;
    is_claimable: boolean;
    current_value: number;
    required_value: number | null;
    progress_percent: number;
}

interface AchievementProgress {
    total_achievements: number;
    earned_count: number;
    claimable_count: number;
    completion_percent: number;
    achievements: Achievement[];
}

interface ReferralStats {
    referral_code: string | null;
    total_referrals: number;
    total_credits_earned: number;
    referral_link: string;
    bot_referral_link: string;
    recent_referrals: Array<{
        referred_user_id: number;
        username: string;
        credits_awarded: number;
        completed_at: string;
    }>;
}

interface LeaderboardEntry {
    rank: number;
    user_id: number;
    username: string | null;
    achievements_earned: number;
    total_channels: number;
    current_streak: number;
}

// Tab Panel Component
interface TabPanelProps {
    children?: React.ReactNode;
    index: number;
    value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => (
    <div role="tabpanel" hidden={value !== index}>
        {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
);

// Icon mapping for achievements
const getAchievementIcon = (icon: string | null, category: string) => {
    const iconMap: Record<string, React.ReactElement> = {
        rocket_launch: <RocketIcon />,
        person_check: <CheckIcon />,
        verified: <CheckIcon />,
        tv: <ChannelIcon />,
        workspace_premium: <PremiumIcon />,
        castle: <DiamondIcon />,
        visibility: <ViewsIcon />,
        star: <StarIcon />,
        trending_up: <StarIcon />,
        diamond: <DiamondIcon />,
        local_fire_department: <FireIcon />,
        whatshot: <FireIcon />,
        emoji_events: <TrophyIcon />,
        military_tech: <MedalIcon />,
        shopping_cart: <SavingsIcon />,
        savings: <SavingsIcon />,
        paid: <SavingsIcon />,
        person_add: <PersonAddIcon />,
        groups: <ReferralIcon />,
        diversity_3: <ReferralIcon />,
    };
    
    if (icon && iconMap[icon]) {
        return iconMap[icon];
    }
    
    // Fallback by category
    const categoryIcons: Record<string, React.ReactElement> = {
        account: <CheckIcon />,
        channels: <ChannelIcon />,
        engagement: <ViewsIcon />,
        streaks: <FireIcon />,
        credits: <SavingsIcon />,
        referrals: <ReferralIcon />,
    };
    
    return categoryIcons[category] || <TrophyIcon />;
};

const RewardsPage: React.FC = () => {
    const { user, updateUser } = useAuth();
    const [activeTab, setActiveTab] = useState(0);
    const [loading, setLoading] = useState(true);
    const [achievements, setAchievements] = useState<AchievementProgress | null>(null);
    const [referralStats, setReferralStats] = useState<ReferralStats | null>(null);
    const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
    const [referralCode, setReferralCode] = useState('');
    const [applyingCode, setApplyingCode] = useState(false);
    const [claimingAchievement, setClaimingAchievement] = useState<string | null>(null);
    const [dailyStreak, setDailyStreak] = useState(0);
    const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' | 'info' }>({
        open: false,
        message: '',
        severity: 'info',
    });

    // Fetch all rewards data
    const fetchRewardsData = useCallback(async () => {
        setLoading(true);
        try {
            const [achievementsRes, referralRes, leaderboardRes, balanceRes] = await Promise.all([
                apiClient.get('/credits/achievements'),
                apiClient.get('/credits/referral'),
                apiClient.get('/credits/leaderboard?limit=10'),
                apiClient.get('/credits/balance'),
            ]);

            setAchievements(achievementsRes as AchievementProgress);
            setReferralStats(referralRes as ReferralStats);
            setLeaderboard(leaderboardRes as LeaderboardEntry[]);
            
            // Extract daily streak from balance response
            const balance = balanceRes as { daily_streak?: number };
            setDailyStreak(balance.daily_streak || 0);
        } catch (error) {
            console.error('Failed to fetch rewards data:', error);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchRewardsData();
    }, [fetchRewardsData]);

    // Claim achievement handler
    const handleClaimAchievement = async (achievementKey: string) => {
        setClaimingAchievement(achievementKey);
        try {
            const result = await apiClient.post('/credits/achievements/claim', {
                achievement_key: achievementKey,
            }) as { success: boolean; message: string; new_balance?: number };

            if (result.success) {
                setSnackbar({
                    open: true,
                    message: result.message,
                    severity: 'success',
                });
                // Update user balance in context
                if (result.new_balance !== undefined && user) {
                    updateUser({ ...user, credit_balance: result.new_balance });
                }
                // Refresh achievements
                fetchRewardsData();
            } else {
                setSnackbar({
                    open: true,
                    message: result.message || 'Failed to claim achievement',
                    severity: 'error',
                });
            }
        } catch (error: any) {
            setSnackbar({
                open: true,
                message: error.message || 'Failed to claim achievement',
                severity: 'error',
            });
        } finally {
            setClaimingAchievement(null);
        }
    };

    // Apply referral code
    const applyReferralCode = async () => {
        if (!referralCode.trim()) return;
        
        setApplyingCode(true);
        try {
            const result = await apiClient.post('/credits/referral/apply', {
                referral_code: referralCode.trim(),
            }) as any;
            
            setSnackbar({
                open: true,
                message: result.message || 'Referral code applied!',
                severity: 'success',
            });
            setReferralCode('');
            fetchRewardsData(); // Refresh data
        } catch (error: any) {
            setSnackbar({
                open: true,
                message: error.response?.data?.detail || 'Failed to apply referral code',
                severity: 'error',
            });
        } finally {
            setApplyingCode(false);
        }
    };

    // Group achievements by category
    const achievementsByCategory = achievements?.achievements.reduce((acc, ach) => {
        const cat = ach.category || 'other';
        if (!acc[cat]) acc[cat] = [];
        acc[cat].push(ach);
        return acc;
    }, {} as Record<string, Achievement[]>) || {};

    const categoryNames: Record<string, string> = {
        account: '👤 Account',
        channels: '📺 Channels',
        engagement: '📈 Engagement',
        streaks: '🔥 Streaks',
        credits: '💰 Credits',
        referrals: '🤝 Referrals',
    };

    if (loading) {
        return (
            <Container maxWidth="lg" sx={{ py: 4 }}>
                <Skeleton variant="rectangular" height={200} sx={{ mb: 3, borderRadius: 2 }} />
                <Grid container spacing={3}>
                    {[1, 2, 3, 4].map((i) => (
                        <Grid item xs={12} sm={6} key={i}>
                            <Skeleton variant="rectangular" height={150} sx={{ borderRadius: 2 }} />
                        </Grid>
                    ))}
                </Grid>
            </Container>
        );
    }

    return (
        <Container maxWidth="lg" sx={{ py: 4 }}>
            {/* Claimable Alert */}
            {(achievements?.claimable_count || 0) > 0 && (
                <Alert 
                    severity="warning" 
                    sx={{ 
                        mb: 3, 
                        '& .MuiAlert-icon': { fontSize: 28 },
                        animation: 'glow 2s ease-in-out infinite',
                        '@keyframes glow': {
                            '0%, 100%': { boxShadow: '0 0 5px rgba(255, 152, 0, 0.3)' },
                            '50%': { boxShadow: '0 0 20px rgba(255, 152, 0, 0.6)' },
                        },
                    }}
                    icon={<TrophyIcon />}
                >
                    <Typography variant="body1" fontWeight="bold">
                        🎉 You have {achievements?.claimable_count} achievement{(achievements?.claimable_count || 0) > 1 ? 's' : ''} ready to claim!
                    </Typography>
                    <Typography variant="body2">
                        Scroll down and click the "Claim!" button to collect your rewards.
                    </Typography>
                </Alert>
            )}

            {/* Header Stats */}
            <Grid container spacing={3} sx={{ mb: 4 }}>
                <Grid item xs={12} sm={4}>
                    <Paper
                        sx={{
                            p: 3,
                            textAlign: 'center',
                            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                            color: 'white',
                            borderRadius: 2,
                        }}
                    >
                        <TrophyIcon sx={{ fontSize: 48, mb: 1 }} />
                        <Typography variant="h4" fontWeight="bold">
                            {achievements?.earned_count || 0}/{achievements?.total_achievements || 0}
                        </Typography>
                        <Typography variant="body2" sx={{ opacity: 0.9 }}>
                            Achievements Earned
                        </Typography>
                        {(achievements?.claimable_count || 0) > 0 && (
                            <Chip 
                                label={`${achievements?.claimable_count} ready to claim!`} 
                                color="warning" 
                                size="small" 
                                sx={{ mt: 1, fontWeight: 'bold' }} 
                            />
                        )}
                        <LinearProgress
                            variant="determinate"
                            value={achievements?.completion_percent || 0}
                            sx={{ mt: 2, bgcolor: 'rgba(255,255,255,0.2)', '& .MuiLinearProgress-bar': { bgcolor: 'white' } }}
                        />
                    </Paper>
                </Grid>
                <Grid item xs={12} sm={4}>
                    <Paper
                        sx={{
                            p: 3,
                            textAlign: 'center',
                            background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
                            color: 'white',
                            borderRadius: 2,
                        }}
                    >
                        <ReferralIcon sx={{ fontSize: 48, mb: 1 }} />
                        <Typography variant="h4" fontWeight="bold">
                            {referralStats?.total_referrals || 0}
                        </Typography>
                        <Typography variant="body2" sx={{ opacity: 0.9 }}>
                            Friends Referred
                        </Typography>
                        <Typography variant="caption" sx={{ display: 'block', mt: 1 }}>
                            +{referralStats?.total_credits_earned || 0} credits earned
                        </Typography>
                    </Paper>
                </Grid>
                <Grid item xs={12} sm={4}>
                    <Paper
                        sx={{
                            p: 3,
                            textAlign: 'center',
                            background: 'linear-gradient(135deg, #ff9a9e 0%, #fad0c4 100%)',
                            color: '#333',
                            borderRadius: 2,
                        }}
                    >
                        <StreakIcon sx={{ fontSize: 48, mb: 1, color: '#f5576c' }} />
                        <Typography variant="h4" fontWeight="bold">
                            {dailyStreak}
                        </Typography>
                        <Typography variant="body2">
                            Day Streak
                        </Typography>
                        <Typography variant="caption" sx={{ display: 'block', mt: 1 }}>
                            Keep logging in daily!
                        </Typography>
                    </Paper>
                </Grid>
            </Grid>

            {/* Tabs */}
            <Paper sx={{ mb: 3 }}>
                <Tabs
                    value={activeTab}
                    onChange={(_, v) => setActiveTab(v)}
                    variant="fullWidth"
                    sx={{ borderBottom: 1, borderColor: 'divider' }}
                >
                    <Tab icon={<TrophyIcon />} label="Achievements" />
                    <Tab icon={<ReferralIcon />} label="Referrals" />
                    <Tab icon={<LeaderboardIcon />} label="Leaderboard" />
                </Tabs>
            </Paper>

            {/* Achievements Tab */}
            <TabPanel value={activeTab} index={0}>
                {Object.entries(achievementsByCategory).map(([category, categoryAchievements]) => (
                    <Box key={category} sx={{ mb: 4 }}>
                        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            {categoryNames[category] || category}
                            <Chip
                                label={`${categoryAchievements.filter(a => a.is_earned).length}/${categoryAchievements.length}`}
                                size="small"
                                color="primary"
                                variant="outlined"
                            />
                        </Typography>
                        <Grid container spacing={2}>
                            {categoryAchievements.map((achievement) => (
                                <Grid item xs={12} sm={6} md={4} key={achievement.achievement_key}>
                                    <Card
                                        variant="outlined"
                                        sx={{
                                            opacity: achievement.is_earned ? 1 : (achievement.is_claimable ? 1 : 0.7),
                                            bgcolor: achievement.is_earned 
                                                ? 'success.50' 
                                                : achievement.is_claimable 
                                                    ? 'warning.50' 
                                                    : 'background.paper',
                                            border: achievement.is_earned 
                                                ? '2px solid' 
                                                : achievement.is_claimable 
                                                    ? '2px solid' 
                                                    : '1px solid',
                                            borderColor: achievement.is_earned 
                                                ? 'success.main' 
                                                : achievement.is_claimable 
                                                    ? 'warning.main' 
                                                    : 'divider',
                                            transition: 'all 0.2s ease',
                                            '&:hover': achievement.is_claimable ? {
                                                transform: 'translateY(-2px)',
                                                boxShadow: 3,
                                            } : {},
                                        }}
                                    >
                                        <CardContent>
                                            <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
                                                <Avatar
                                                    sx={{
                                                        bgcolor: achievement.is_earned 
                                                            ? 'success.main' 
                                                            : achievement.is_claimable 
                                                                ? 'warning.main' 
                                                                : 'grey.300',
                                                        width: 48,
                                                        height: 48,
                                                    }}
                                                >
                                                    {achievement.is_earned || achievement.is_claimable ? (
                                                        getAchievementIcon(achievement.icon, achievement.category)
                                                    ) : (
                                                        <LockIcon />
                                                    )}
                                                </Avatar>
                                                <Box sx={{ flex: 1 }}>
                                                    <Typography variant="subtitle1" fontWeight="medium">
                                                        {achievement.name}
                                                        {achievement.is_earned && (
                                                            <CheckIcon sx={{ ml: 1, fontSize: 18, color: 'success.main' }} />
                                                        )}
                                                    </Typography>
                                                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                                                        {achievement.description}
                                                    </Typography>
                                                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 1 }}>
                                                        <Chip
                                                            label={`+${achievement.credit_reward} credits`}
                                                            size="small"
                                                            color={achievement.is_earned ? 'success' : achievement.is_claimable ? 'warning' : 'default'}
                                                        />
                                                        {!achievement.is_earned && !achievement.is_claimable && achievement.required_value && (
                                                            <Typography variant="caption" color="text.secondary">
                                                                {achievement.current_value}/{achievement.required_value}
                                                            </Typography>
                                                        )}
                                                        {achievement.is_claimable && (
                                                            <Button
                                                                variant="contained"
                                                                color="warning"
                                                                size="small"
                                                                onClick={() => handleClaimAchievement(achievement.achievement_key)}
                                                                disabled={claimingAchievement === achievement.achievement_key}
                                                                sx={{ 
                                                                    fontWeight: 'bold',
                                                                    animation: 'pulse 2s infinite',
                                                                    '@keyframes pulse': {
                                                                        '0%': { boxShadow: '0 0 0 0 rgba(255, 152, 0, 0.4)' },
                                                                        '70%': { boxShadow: '0 0 0 10px rgba(255, 152, 0, 0)' },
                                                                        '100%': { boxShadow: '0 0 0 0 rgba(255, 152, 0, 0)' },
                                                                    },
                                                                }}
                                                            >
                                                                {claimingAchievement === achievement.achievement_key ? (
                                                                    <CircularProgress size={16} color="inherit" />
                                                                ) : (
                                                                    'Claim!'
                                                                )}
                                                            </Button>
                                                        )}
                                                    </Box>
                                                    {!achievement.is_earned && !achievement.is_claimable && achievement.progress_percent > 0 && (
                                                        <LinearProgress
                                                            variant="determinate"
                                                            value={achievement.progress_percent}
                                                            sx={{ mt: 1 }}
                                                        />
                                                    )}
                                                </Box>
                                            </Box>
                                        </CardContent>
                                    </Card>
                                </Grid>
                            ))}
                        </Grid>
                    </Box>
                ))}
            </TabPanel>

            {/* Referrals Tab */}
            <TabPanel value={activeTab} index={1}>
                <Grid container spacing={3}>
                    <Grid item xs={12} md={6}>
                        <Paper sx={{ p: 3 }}>
                            <Typography variant="h6" gutterBottom>
                                🎁 Your Referral Code
                            </Typography>
                            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                                Share this code with friends and earn 100 credits for each signup!
                            </Typography>
                            
                            <Box sx={{ display: 'flex', gap: 1, mb: 3 }}>
                                <TextField
                                    value={referralStats?.referral_code || ''}
                                    InputProps={{
                                        readOnly: true,
                                        sx: { fontWeight: 'bold', fontSize: '1.2rem', letterSpacing: 2 },
                                    }}
                                    fullWidth
                                />
                                <Tooltip title="Copy code">
                                    <IconButton onClick={() => {
                                        if (referralStats?.referral_code) {
                                            navigator.clipboard.writeText(referralStats.referral_code);
                                            setSnackbar({ open: true, message: 'Code copied!', severity: 'success' });
                                        }
                                    }}>
                                        <CopyIcon />
                                    </IconButton>
                                </Tooltip>
                            </Box>
                            
                            {/* Telegram Bot Link - Primary */}
                            <Button
                                variant="contained"
                                startIcon={<ShareIcon />}
                                onClick={() => {
                                    if (referralStats?.bot_referral_link) {
                                        navigator.clipboard.writeText(referralStats.bot_referral_link);
                                        setSnackbar({ open: true, message: 'Telegram bot link copied!', severity: 'success' });
                                    }
                                }}
                                fullWidth
                                sx={{ 
                                    mb: 1.5,
                                    background: 'linear-gradient(45deg, #0088cc 30%, #00a8e8 90%)',
                                    '&:hover': {
                                        background: 'linear-gradient(45deg, #006699 30%, #0088cc 90%)',
                                    }
                                }}
                            >
                                📱 Copy Telegram Bot Link
                            </Button>
                            
                            {/* Web Link - Secondary */}
                            <Button
                                variant="outlined"
                                startIcon={<ShareIcon />}
                                onClick={() => {
                                    if (referralStats?.referral_link) {
                                        navigator.clipboard.writeText(referralStats.referral_link);
                                        setSnackbar({ open: true, message: 'Web link copied!', severity: 'success' });
                                    }
                                }}
                                fullWidth
                                size="small"
                            >
                                🌐 Copy Web Registration Link
                            </Button>
                            
                            <Alert severity="info" sx={{ mt: 2 }}>
                                <Typography variant="body2">
                                    <strong>You get:</strong> 100 credits per referral<br />
                                    <strong>Friend gets:</strong> 50 bonus credits on signup
                                </Typography>
                            </Alert>
                            
                            {/* Show actual links for reference */}
                            <Box sx={{ mt: 2, p: 1.5, bgcolor: 'action.hover', borderRadius: 1 }}>
                                <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
                                    📱 Telegram: <code style={{ fontSize: '0.75rem' }}>{referralStats?.bot_referral_link || '...'}</code>
                                </Typography>
                                <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                                    🌐 Web: <code style={{ fontSize: '0.75rem' }}>{referralStats?.referral_link || '...'}</code>
                                </Typography>
                            </Box>
                        </Paper>
                    </Grid>
                    
                    <Grid item xs={12} md={6}>
                        <Paper sx={{ p: 3 }}>
                            <Typography variant="h6" gutterBottom>
                                📝 Have a Referral Code?
                            </Typography>
                            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                                If someone referred you, enter their code to get bonus credits!
                            </Typography>
                            
                            <Box sx={{ display: 'flex', gap: 1 }}>
                                <TextField
                                    placeholder="Enter referral code"
                                    value={referralCode}
                                    onChange={(e) => setReferralCode(e.target.value.toUpperCase())}
                                    fullWidth
                                    InputProps={{
                                        sx: { textTransform: 'uppercase', letterSpacing: 2 },
                                    }}
                                />
                                <Button
                                    variant="contained"
                                    onClick={applyReferralCode}
                                    disabled={!referralCode.trim() || applyingCode}
                                >
                                    {applyingCode ? <CircularProgress size={24} /> : 'Apply'}
                                </Button>
                            </Box>
                        </Paper>
                        
                        {/* Recent Referrals */}
                        <Paper sx={{ p: 3, mt: 3 }}>
                            <Typography variant="h6" gutterBottom>
                                👥 Your Referrals
                            </Typography>
                            {referralStats?.recent_referrals && referralStats.recent_referrals.length > 0 ? (
                                <List dense>
                                    {referralStats.recent_referrals.map((ref, index) => (
                                        <ListItem key={index}>
                                            <ListItemIcon>
                                                <Avatar sx={{ width: 32, height: 32, bgcolor: 'primary.main' }}>
                                                    {ref.username?.[0]?.toUpperCase() || '?'}
                                                </Avatar>
                                            </ListItemIcon>
                                            <ListItemText
                                                primary={ref.username || `User #${ref.referred_user_id}`}
                                                secondary={new Date(ref.completed_at).toLocaleDateString()}
                                            />
                                            <ListItemSecondaryAction>
                                                <Chip
                                                    label={`+${ref.credits_awarded}`}
                                                    size="small"
                                                    color="success"
                                                />
                                            </ListItemSecondaryAction>
                                        </ListItem>
                                    ))}
                                </List>
                            ) : (
                                <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 3 }}>
                                    No referrals yet. Share your code to get started!
                                </Typography>
                            )}
                        </Paper>
                    </Grid>
                </Grid>
            </TabPanel>

            {/* Leaderboard Tab */}
            <TabPanel value={activeTab} index={2}>
                <Paper sx={{ p: 3 }}>
                    <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <LeaderboardIcon color="primary" />
                        Top Achievers
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        Rankings based on achievements unlocked
                    </Typography>
                    
                    <List>
                        {leaderboard.map((entry, index) => (
                            <React.Fragment key={entry.user_id}>
                                {index > 0 && <Divider />}
                                <ListItem
                                    sx={{
                                        bgcolor: entry.user_id === Number(user?.id) ? 'action.selected' : 'transparent',
                                        borderRadius: 1,
                                    }}
                                >
                                    <ListItemIcon>
                                        <Avatar
                                            sx={{
                                                bgcolor: index === 0 ? '#FFD700' : index === 1 ? '#C0C0C0' : index === 2 ? '#CD7F32' : 'grey.500',
                                                color: index < 3 ? '#000' : '#fff',
                                                fontWeight: 'bold',
                                            }}
                                        >
                                            {entry.rank}
                                        </Avatar>
                                    </ListItemIcon>
                                    <ListItemText
                                        primary={
                                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                {entry.username || `User #${entry.user_id}`}
                                                {entry.user_id === Number(user?.id) && (
                                                    <Chip label="You" size="small" color="primary" />
                                                )}
                                            </Box>
                                        }
                                        secondary={
                                            <Box sx={{ display: 'flex', gap: 2, mt: 0.5 }}>
                                                {entry.current_streak > 0 && (
                                                    <Typography variant="caption" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                                        🔥 {entry.current_streak} day streak
                                                    </Typography>
                                                )}
                                            </Box>
                                        }
                                    />
                                    <Box sx={{ textAlign: 'right' }}>
                                        <Typography variant="h6" fontWeight="bold" color="primary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                            <TrophyIcon sx={{ fontSize: 20 }} />
                                            {entry.achievements_earned}
                                        </Typography>
                                        <Typography variant="caption" color="text.secondary">
                                            achievements
                                        </Typography>
                                    </Box>
                                </ListItem>
                            </React.Fragment>
                        ))}
                    </List>
                    
                    {leaderboard.length === 0 && (
                        <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 4 }}>
                            No achievers yet. Be the first to unlock achievements!
                        </Typography>
                    )}
                </Paper>
            </TabPanel>

            {/* Snackbar */}
            <Snackbar
                open={snackbar.open}
                autoHideDuration={4000}
                onClose={() => setSnackbar({ ...snackbar, open: false })}
                anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
            >
                <Alert severity={snackbar.severity} onClose={() => setSnackbar({ ...snackbar, open: false })}>
                    {snackbar.message}
                </Alert>
            </Snackbar>
        </Container>
    );
};

export default RewardsPage;
