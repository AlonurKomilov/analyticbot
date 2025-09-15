import React from 'react';
import { Chip } from '@mui/material';
import { getPerformanceBadge } from '../utils/postTableUtils.js';

const PostMetricBadge = ({ post }) => {
    const badge = getPerformanceBadge(post);
    
    return (
        <Chip 
            size="small" 
            label={badge.label} 
            color={badge.color}
            variant="outlined"
        />
    );
};

export default PostMetricBadge;