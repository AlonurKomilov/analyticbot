/**
 * Utility functions for TopPostsTable components
 */

// Format number with K/M suffixes
export const formatNumber = (num) => {
    if (!num && num !== 0) return '0';

    const number = parseInt(num);
    if (number >= 1000000) {
        return (number / 1000000).toFixed(1) + 'M';
    }
    if (number >= 1000) {
        return (number / 1000).toFixed(1) + 'K';
    }
    return number.toString();
};

// Format date to relative time
export const formatDate = (dateString) => {
    if (!dateString) return 'Unknown';

    const postDate = new Date(dateString);
    const now = new Date();
    const diffInHours = (now - postDate) / (1000 * 60 * 60);

    if (diffInHours < 1) {
        return `${Math.floor(diffInHours * 60)} min ago`;
    } else if (diffInHours < 24) {
        return `${Math.floor(diffInHours)} hours ago`;
    } else {
        return `${Math.floor(diffInHours / 24)} days ago`;
    }
};

// Calculate engagement rate
export const calculateEngagementRate = (post) => {
    const totalEngagement = (post.likes || 0) + (post.shares || 0) + (post.comments || 0);
    const views = post.views || 1;
    return ((totalEngagement / views) * 100).toFixed(1);
};

// Get performance badge data
export const getPerformanceBadge = (post) => {
    const engagementRate = parseFloat(calculateEngagementRate(post));
    const views = post.views || 0;

    if (engagementRate > 10 && views > 10000) {
        return { label: <><span aria-hidden="true">🔥</span> Viral</>, color: 'error' };
    } else if (engagementRate > 5) {
        return { label: <><span aria-hidden="true">⭐</span> High</>, color: 'warning' };
    } else if (engagementRate > 2) {
        return { label: <><span aria-hidden="true">👍</span> Good</>, color: 'success' };
    } else {
        return { label: <><span aria-hidden="true">📊</span> Average</>, color: 'default' };
    }
};

// Calculate summary statistics
export const calculateSummaryStats = (posts) => {
    if (!posts || !Array.isArray(posts) || posts.length === 0) return null;

    const totalViews = posts.reduce((sum, post) => sum + (post.views || 0), 0);
    const totalLikes = posts.reduce((sum, post) => sum + (post.likes || 0), 0);
    const totalShares = posts.reduce((sum, post) => sum + (post.shares || 0), 0);
    const totalComments = posts.reduce((sum, post) => sum + (post.comments || 0), 0);
    const avgEngagement = posts.reduce((sum, post) => sum + parseFloat(calculateEngagementRate(post)), 0) / posts.length;

    return {
        totalViews,
        totalLikes,
        totalShares,
        totalComments,
        avgEngagement: avgEngagement.toFixed(1),
        topPost: posts[0]
    };
};
