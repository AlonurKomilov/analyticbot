/**
 * Micro-Interactions Demo Page
 * 
 * Comprehensive demonstration of all micro-interaction components:
 * - Interactive buttons with various effects
 * - Animated cards with different entrance animations  
 * - Loading states and skeleton animations
 * - Feedback animations and hover effects
 * - Staggered content animations
 * - Floating elements and pulse effects
 * 
 * This page serves as both a showcase and a testing ground
 * for all micro-interaction components.
 */

import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Container,
  Grid,
  Alert,
  Chip,
  Divider,
  Paper,
  LinearProgress,
  Switch,
  FormControlLabel,
  Slider
} from '@mui/material';
import { 
  Play as PlayIcon,
  Pause as PauseIcon,
  Refresh as RefreshIcon,
  Favorite as FavoriteIcon,
  Star as StarIcon,
  ThumbUp as ThumbUpIcon,
  Download as DownloadIcon,
  Share as ShareIcon,
  Settings as SettingsIcon,
  Analytics as AnalyticsIcon,
  TrendingUp as TrendingIcon
} from '@mui/icons-material';

// Micro-interaction components
import { 
  StaggeredAnimation, 
  FloatingElement,
  FeedbackAnimation,
  PulseAnimation,
  InteractiveCard,
  AnimatedButton,
  TouchRipple,
  SkeletonLoader
} from '../animations/MicroInteractions.jsx';

import { 
  InteractiveButton, 
  InteractiveIconButton,
  AnimatedFab 
} from '../animations/InteractiveButtons.jsx';

import { 
  AnimatedCard, 
  ExpandableCard, 
  AnimatedMetricCard,
  DashboardCard 
} from '../animations/InteractiveCards.jsx';

import { TouchTargetProvider } from '../common/TouchTargetCompliance.jsx';

const MicroInteractionsDemoPage = () => {
  const [animationsEnabled, setAnimationsEnabled] = useState(true);
  const [animationSpeed, setAnimationSpeed] = useState(1);
  const [demoStats, setDemoStats] = useState({
    clicks: 0,
    hovers: 0,
    interactions: 0
  });
  const [loading, setLoading] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [showError, setShowError] = useState(false);
  const [favorited, setFavorited] = useState(false);

  // Demo interaction handlers
  const handleClick = () => {
    setDemoStats(prev => ({ 
      ...prev, 
      clicks: prev.clicks + 1,
      interactions: prev.interactions + 1 
    }));
  };

  const handleHover = () => {
    setDemoStats(prev => ({ 
      ...prev, 
      hovers: prev.hovers + 1 
    }));
  };

  const simulateLoading = async () => {
    setLoading(true);
    setShowSuccess(false);
    setShowError(false);
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    setLoading(false);
    const success = Math.random() > 0.3; // 70% success rate
    
    if (success) {
      setShowSuccess(true);
      setTimeout(() => setShowSuccess(false), 3000);
    } else {
      setShowError(true);
      setTimeout(() => setShowError(false), 3000);
    }
    
    handleClick();
  };

  const toggleFavorite = () => {
    setFavorited(!favorited);
    handleClick();
  };

  // Demo metrics for AnimatedMetricCard
  const demoMetrics = [
    {
      title: 'Total Clicks',
      value: demoStats.clicks,
      previousValue: Math.max(0, demoStats.clicks - 1),
      unit: '',
      trend: 'positive',
      icon: <TrendingIcon />,
      formatValue: (val) => Math.round(val)
    },
    {
      title: 'Hover Events',
      value: demoStats.hovers,
      previousValue: Math.max(0, demoStats.hovers - 1), 
      unit: '',
      trend: 'positive',
      icon: <AnalyticsIcon />,
      formatValue: (val) => Math.round(val)
    },
    {
      title: 'Interactions',
      value: demoStats.interactions,
      previousValue: Math.max(0, demoStats.interactions - 1),
      unit: '',
      trend: 'positive',
      icon: <StarIcon />,
      formatValue: (val) => Math.round(val)
    }
  ];

  return (
    <TouchTargetProvider>
      <Container maxWidth="xl" sx={{ py: 4, minHeight: '100vh' }}>
        {/* Page Header */}
        <StaggeredAnimation delay={100}>
          <Box sx={{ mb: 6, textAlign: 'center' }}>
            <Typography 
              variant="h3" 
              component="h1" 
              sx={{ 
                mb: 2, 
                fontWeight: 700,
                background: 'linear-gradient(45deg, #1976d2, #42a5f5)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent'
              }}
            >
              Micro-Interactions Showcase
            </Typography>
            
            <Typography variant="h6" color="text.secondary" sx={{ mb: 4 }}>
              Experience smooth animations and responsive feedback
            </Typography>

            {/* Controls */}
            <Paper sx={{ p: 3, mb: 4, maxWidth: 600, mx: 'auto' }}>
              <Typography variant="h6" sx={{ mb: 2 }}>Demo Controls</Typography>
              
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={animationsEnabled}
                      onChange={(e) => setAnimationsEnabled(e.target.checked)}
                    />
                  }
                  label="Enable Animations"
                />
                
                <Box>
                  <Typography variant="body2" gutterBottom>
                    Animation Speed: {animationSpeed}x
                  </Typography>
                  <Slider
                    value={animationSpeed}
                    onChange={(_, value) => setAnimationSpeed(value)}
                    min={0.1}
                    max={3}
                    step={0.1}
                    marks={[
                      { value: 0.5, label: '0.5x' },
                      { value: 1, label: '1x' },
                      { value: 2, label: '2x' }
                    ]}
                  />
                </Box>
              </Box>
            </Paper>
          </Box>
        </StaggeredAnimation>

        {/* Demo Stats */}
        <Box sx={{ mb: 6 }}>
          <Typography variant="h5" sx={{ mb: 3, fontWeight: 600 }}>
            Live Demo Statistics
          </Typography>
          <Grid container spacing={3}>
            <StaggeredAnimation delay={150}>
              {demoMetrics.map((metric, index) => (
                <Grid item xs={12} sm={4} key={index}>
                  <AnimatedMetricCard
                    {...metric}
                    entrance="grow"
                    delay={index * 100}
                  />
                </Grid>
              ))}
            </StaggeredAnimation>
          </Grid>
        </Box>

        {/* Interactive Buttons Section */}
        <Box sx={{ mb: 8 }}>
          <Typography variant="h5" sx={{ mb: 3, fontWeight: 600 }}>
            Interactive Buttons
          </Typography>
          
          <Grid container spacing={4}>
            <Grid item xs={12} md={6}>
              <DashboardCard
                title="Button Effects"
                subtitle="Various hover and click effects"
                entrance="fade"
              >
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
                  <InteractiveButton
                    onClick={handleClick}
                    onMouseEnter={handleHover}
                    hoverEffect="glow"
                    startIcon={<PlayIcon />}
                  >
                    Glow Effect
                  </InteractiveButton>
                  
                  <InteractiveButton
                    onClick={handleClick}
                    onMouseEnter={handleHover}
                    hoverEffect="scale"
                    variant="outlined"
                    startIcon={<StarIcon />}
                  >
                    Scale Effect
                  </InteractiveButton>
                  
                  <InteractiveButton
                    onClick={handleClick}
                    onMouseEnter={handleHover}
                    hoverEffect="bounce"
                    color="secondary"
                    startIcon={<FavoriteIcon />}
                  >
                    Bounce Effect
                  </InteractiveButton>
                </Box>
              </DashboardCard>
            </Grid>

            <Grid item xs={12} md={6}>
              <DashboardCard
                title="Loading States"
                subtitle="Interactive loading and feedback"
                entrance="fade"
                delay={200}
              >
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, alignItems: 'center' }}>
                  <InteractiveButton
                    onClick={simulateLoading}
                    loading={loading}
                    success={showSuccess}
                    error={showError}
                    hoverEffect="glow"
                    startIcon={<RefreshIcon />}
                  >
                    Test Loading
                  </InteractiveButton>
                  
                  <FeedbackAnimation type="success" show={showSuccess}>
                    <Chip label="Success!" color="success" />
                  </FeedbackAnimation>
                  
                  <FeedbackAnimation type="error" show={showError}>
                    <Chip label="Error occurred" color="error" />
                  </FeedbackAnimation>
                </Box>
              </DashboardCard>
            </Grid>
          </Grid>
        </Box>

        {/* Interactive Cards Section */}
        <Box sx={{ mb: 8 }}>
          <Typography variant="h5" sx={{ mb: 3, fontWeight: 600 }}>
            Interactive Cards
          </Typography>
          
          <Grid container spacing={4}>
            <Grid item xs={12} md={4}>
              <AnimatedCard
                entrance="grow"
                sx={{ 
                  p: 3,
                  cursor: 'pointer',
                  transition: 'all 0.3s ease-in-out',
                  '&:hover': {
                    transform: 'translateY(-8px)',
                    boxShadow: '0 12px 24px rgba(0, 0, 0, 0.15)'
                  }
                }}
                onClick={handleClick}
                onMouseEnter={handleHover}
              >
                <Box sx={{ textAlign: 'center' }}>
                  <TrendingIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    Hover Card
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Hover to see elevation effect
                  </Typography>
                </Box>
              </AnimatedCard>
            </Grid>

            <Grid item xs={12} md={4}>
              <ExpandableCard
                title="Expandable Content"
                subtitle="Click to expand/collapse"
                defaultExpanded={false}
                entrance="fade"
                delay={200}
              >
                <Typography variant="body2" sx={{ mb: 2 }}>
                  This content is revealed when the card expands with smooth animation.
                </Typography>
                <LinearProgress variant="determinate" value={75} sx={{ mb: 1 }} />
                <Typography variant="caption" color="text.secondary">
                  Progress: 75%
                </Typography>
              </ExpandableCard>
            </Grid>

            <Grid item xs={12} md={4}>
              <DashboardCard
                title="Loading Card"
                subtitle="Toggle loading state"
                loading={loading}
                entrance="grow"
                delay={400}
                actions={
                  <InteractiveIconButton
                    onClick={() => setLoading(!loading)}
                    hoverEffect="bounce"
                  >
                    <RefreshIcon />
                  </InteractiveIconButton>
                }
              >
                <Typography variant="body2">
                  Card content with loading overlay
                </Typography>
              </DashboardCard>
            </Grid>
          </Grid>
        </Box>

        {/* Special Effects Section */}
        <Box sx={{ mb: 8 }}>
          <Typography variant="h5" sx={{ mb: 3, fontWeight: 600 }}>
            Special Effects
          </Typography>
          
          <Grid container spacing={4}>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 4, textAlign: 'center' }}>
                <Typography variant="h6" gutterBottom>
                  Floating Animation
                </Typography>
                <FloatingElement duration={3} intensity="medium">
                  <Box
                    sx={{
                      width: 100,
                      height: 100,
                      bgcolor: 'primary.main',
                      borderRadius: '50%',
                      mx: 'auto',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}
                  >
                    <StarIcon sx={{ color: 'white', fontSize: 40 }} />
                  </Box>
                </FloatingElement>
              </Paper>
            </Grid>

            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 4, textAlign: 'center' }}>
                <Typography variant="h6" gutterBottom>
                  Pulse Animation
                </Typography>
                <PulseAnimation intensity="strong" trigger={favorited}>
                  <InteractiveIconButton
                    onClick={toggleFavorite}
                    size="large"
                    sx={{
                      color: favorited ? 'error.main' : 'text.secondary',
                      fontSize: 48
                    }}
                  >
                    <FavoriteIcon sx={{ fontSize: 48 }} />
                  </InteractiveIconButton>
                </PulseAnimation>
                <Typography variant="body2" sx={{ mt: 2 }}>
                  Click the heart to trigger pulse
                </Typography>
              </Paper>
            </Grid>
          </Grid>
        </Box>

        {/* Tips and Information */}
        <Box sx={{ mb: 4 }}>
          <Alert 
            severity="info"
            sx={{
              bgcolor: 'info.50',
              border: '1px solid',
              borderColor: 'info.200',
              borderRadius: 2
            }}
          >
            <Typography variant="body2">
              <strong>🎨 Implementation Notes:</strong> All animations use CSS transforms and opacity 
              for optimal performance. Hardware acceleration is enabled for smooth 60fps animations. 
              Reduced motion preferences are respected for accessibility.
            </Typography>
          </Alert>
        </Box>

        {/* Floating Action Buttons */}
        <AnimatedFab
          onClick={handleClick}
          icon={<ShareIcon />}
          text="Share Demo"
          extended={true}
          entrance="zoom"
          color="primary"
        />
        
        <AnimatedFab
          onClick={handleClick}
          icon={<DownloadIcon />}
          text="Download"
          extended={false}
          entrance="slide"
          color="secondary"
          sx={{ bottom: 100 }}
        />
      </Container>
    </TouchTargetProvider>
  );
};

export default MicroInteractionsDemoPage;