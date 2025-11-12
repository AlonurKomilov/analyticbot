/**
 * Utility functions for TopPostsTable components
 */

export interface Post {
    // Backend fields (from analytics_top_posts_router.py)
    msg_id?: number;
    date?: string;
    text?: string;
    views?: number;
    forwards?: number;
    replies_count?: number;
    reactions_count?: number;
    engagement_rate?: number;

    // Legacy fields (for backward compatibility)
    id?: string | number;
    likes?: number;
    shares?: number;
    comments?: number;
    created_at?: string;
    title?: string;
    thumbnail?: string;
    type?: string;
    engagement?: number;
    reach?: number;
    [key: string]: any;
}

export interface PerformanceBadge {
    label: string;
    color: 'error' | 'warning' | 'success' | 'default';
}

export interface SummaryStats {
    totalViews: number;
    totalLikes: number;
    totalShares: number;
    totalComments: number;
    avgEngagement: string;
    topPost: Post;
}

// Format number with K/M suffixes
export const formatNumber = (num: number | string | null | undefined): string => {
    if (!num && num !== 0) return '0';

    const number = typeof num === 'string' ? parseInt(num) : num;
    if (number >= 1000000) {
        return (number / 1000000).toFixed(1) + 'M';
    }
    if (number >= 1000) {
        return (number / 1000).toFixed(1) + 'K';
    }
    return number.toString();
};

// Format date to relative time
export const formatDate = (dateString: string | undefined): string => {
    if (!dateString) return 'Unknown';

    const postDate = new Date(dateString);
    const now = new Date();
    const diffInHours = (now.getTime() - postDate.getTime()) / (1000 * 60 * 60);

    if (diffInHours < 1) {
        return `${Math.floor(diffInHours * 60)} min ago`;
    } else if (diffInHours < 24) {
        return `${Math.floor(diffInHours)} hours ago`;
    } else {
        return `${Math.floor(diffInHours / 24)} days ago`;
    }
};

// Calculate engagement rate
export const calculateEngagementRate = (post: Post): number => {
    // If backend already calculated it, use that value
    if (post.engagement_rate !== undefined) {
        return post.engagement_rate;
    }

    // Otherwise calculate from metrics (supports both old and new field names)
    const reactions = post.reactions_count || post.likes || 0;
    const forwards = post.forwards || post.shares || 0;
    const replies = post.replies_count || post.comments || 0;
    const totalEngagement = reactions + forwards + replies;
    const views = post.views || 1;
    return (totalEngagement / views) * 100;
};

// Get performance badge data
export const getPerformanceBadge = (post: Post): PerformanceBadge => {
    const engagementRate = calculateEngagementRate(post);
    const views = post.views || 0;

    if (engagementRate > 10 && views > 10000) {
        return { label: '🔥 Viral', color: 'error' };
    } else if (engagementRate > 5) {
        return { label: '⭐ High', color: 'warning' };
    } else if (engagementRate > 2) {
        return { label: '👍 Good', color: 'success' };
    } else {
        return { label: '📊 Average', color: 'default' };
    }
};

// Calculate summary statistics
export const calculateSummaryStats = (posts: Post[] | null | undefined): SummaryStats | null => {
    if (!posts || !Array.isArray(posts) || posts.length === 0) return null;

    const totalViews = posts.reduce((sum, post) => sum + (post.views || 0), 0);
    const totalLikes = posts.reduce((sum, post) => sum + (post.reactions_count || post.likes || 0), 0);
    const totalShares = posts.reduce((sum, post) => sum + (post.forwards || post.shares || 0), 0);
    const totalComments = posts.reduce((sum, post) => sum + (post.replies_count || post.comments || 0), 0);
    const avgEngagement = posts.reduce((sum, post) => sum + calculateEngagementRate(post), 0) / posts.length;

    return {
        totalViews,
        totalLikes,
        totalShares,
        totalComments,
        avgEngagement: avgEngagement.toFixed(1),
        topPost: posts[0]
    };
};
