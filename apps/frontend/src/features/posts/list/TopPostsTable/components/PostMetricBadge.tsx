import React from 'react';
import { StatusChip } from '@shared/components';
import { getPerformanceBadge } from '../utils/postTableUtils.js';

interface Post {
  id: string;
  views?: number;
  engagement?: number;
  reach?: number;
  [key: string]: any;
}

interface PostMetricBadgeProps {
  /** Post object containing metrics */
  post: Post;
}

/**
 * PostMetricBadge - Displays a performance badge for a post based on its metrics
 *
 * @component
 */
const PostMetricBadge: React.FC<PostMetricBadgeProps> = ({ post }) => {
    const badge = getPerformanceBadge(post);

    // Map color to status (StatusChip uses 'status' prop with 'info' | 'success' | 'warning' | 'error')
    const colorToStatus: Record<string, 'info' | 'success' | 'warning' | 'error'> = {
        'default': 'info',
        'success': 'success',
        'warning': 'warning',
        'error': 'error'
    };

    return (
        <StatusChip
            size="small"
            label={badge.label}
            status={colorToStatus[badge.color] || 'info'}
        />
    );
};

export default PostMetricBadge;
