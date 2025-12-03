/**
 * ScheduledPostsList Component
 * Container that renders a list of ScheduledPostCard components
 */

import React from 'react';
import { Paper, Typography, List } from '@mui/material';
import ScheduledPostCard from './ScheduledPostCard';
import { ScheduledPostsListProps } from '../types';

const ScheduledPostsList: React.FC<ScheduledPostsListProps> = ({
  posts,
  onDelete,
  isDeleting = false
}) => {
  return (
    <Paper
      elevation={2}
      sx={{
        mb: 3,
        p: 2,
        bgcolor: 'background.paper',
        borderRadius: 2
      }}
    >
      <Typography
        variant="h6"
        gutterBottom
        sx={{ mb: 2 }}
      >
        Scheduled Posts ({posts.length})
      </Typography>

      <List dense>
        {posts.map((post) => (
          <ScheduledPostCard
            key={post.id}
            post={post}
            onDelete={onDelete}
            isDeleting={isDeleting}
          />
        ))}
      </List>
    </Paper>
  );
};

export default ScheduledPostsList;
