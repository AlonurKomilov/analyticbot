import React from 'react';
import { StatusChip } from '../../../common';
import { getPerformanceBadge } from '../utils/postTableUtils.js';

const PostMetricBadge = ({ post }) => {
    const badge = getPerformanceBadge(post);
    
    return (
        <StatusChip 
            size="small" 
            label={badge.label} 
            variant={badge.color}
        />
    );
};

export default PostMetricBadge;