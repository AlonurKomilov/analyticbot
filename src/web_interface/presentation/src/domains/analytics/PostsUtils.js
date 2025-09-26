/**
 * Utility functions for Posts data processing and formatting
 */

/**
 * Format numbers with K/M abbreviations
 */
export const formatNumber = (num) => {
    // Handle invalid values
    if (num === null || num === undefined || isNaN(num)) {
        return '0';
    }
    
    const validNum = Number(num);
    if (isNaN(validNum)) {
        return '0';
    }
    
    if (validNum >= 1000000) {
        return (validNum / 1000000).toFixed(1) + 'M';
    } else if (validNum >= 1000) {
        return (validNum / 1000).toFixed(1) + 'K';
    }
    return validNum.toString();
};

/**
 * Format dates with relative time
 */
export const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = (now - date) / (1000 * 60 * 60);
    
    if (diffInHours < 1) {
        return `${Math.floor(diffInHours * 60)} min ago`;
    } else if (diffInHours < 24) {
        return `${Math.floor(diffInHours)} hours ago`;
    } else {
        return `${Math.floor(diffInHours / 24)} days ago`;
    }
};

/**
 * Calculate engagement rate as percentage
 */
export const calculateEngagementRate = (post) => {
    const totalEngagement = (post.likes || 0) + (post.shares || 0) + (post.comments || 0);
    const views = post.views || 1;
    return ((totalEngagement / views) * 100).toFixed(1);
};

/**
 * Get performance score (0-100)
 */
export const getPerformanceScore = (post) => {
    const engagementRate = parseFloat(calculateEngagementRate(post));
    const views = post.views || 0;
    
    // Weight engagement rate and view count
    const engagementScore = Math.min(engagementRate * 10, 70); // Max 70 points for engagement
    const viewScore = Math.min((views / 1000) * 30, 30); // Max 30 points for views
    
    return Math.round(engagementScore + viewScore);
};

/**
 * Get performance level based on score
 */
export const getPerformanceLevel = (score) => {
    if (score >= 80) return { level: 'Excellent', color: 'success' };
    if (score >= 60) return { level: 'Good', color: 'primary' };
    if (score >= 40) return { level: 'Average', color: 'warning' };
    return { level: 'Poor', color: 'error' };
};

/**
 * Mock data generator for development/testing
 */
export const generateMockPosts = (count = 10) => {
    const postTypes = ['Image', 'Video', 'Text', 'Carousel', 'Story'];
    const titles = [
        'Amazing sunset photography tips',
        'Breaking: New AI breakthrough announced',
        'Top 10 productivity hacks for 2024',
        'Healthy meal prep ideas for busy professionals',
        'The future of remote work technology'
    ];

    return Array.from({ length: count }, (_, index) => ({
        id: index + 1,
        title: titles[Math.floor(Math.random() * titles.length)],
        content: `Sample post content ${index + 1}`,
        type: postTypes[Math.floor(Math.random() * postTypes.length)],
        views: Math.floor(Math.random() * 50000) + 100,
        likes: Math.floor(Math.random() * 5000) + 10,
        shares: Math.floor(Math.random() * 1000) + 5,
        comments: Math.floor(Math.random() * 500) + 2,
        date: new Date(Date.now() - Math.floor(Math.random() * 30 * 24 * 60 * 60 * 1000)).toISOString(),
        thumbnail: Math.random() > 0.7 ? `https://picsum.photos/400/300?random=${index}` : null,
        channel: `Channel ${Math.floor(Math.random() * 5) + 1}`,
        status: Math.random() > 0.8 ? 'trending' : 'published'
    }));
};