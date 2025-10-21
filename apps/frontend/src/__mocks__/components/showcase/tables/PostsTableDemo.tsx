/**
 * PostsTableDemo Component
 *
 * Extracted from DataTablesShowcase - showcases the Enhanced Top Posts Table
 * with analytics-focused features and real-time data management
 */

import React from 'react';
import { Box, Typography } from '@mui/material';
import EnhancedTopPostsTable from '../../../../components/EnhancedTopPostsTable';

const PostsTableDemo: React.FC = () => {
    return (
        <>
            <Box sx={{ mb: 2 }}>
                <Typography variant="h5" gutterBottom>
                    Enhanced Top Posts Analytics Table
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                    Advanced analytics table specifically designed for social media post performance
                    data management. Features include advanced sorting, real-time updates, and export capabilities.
                </Typography>
            </Box>
            <EnhancedTopPostsTable />
        </>
    );
};

export default PostsTableDemo;
