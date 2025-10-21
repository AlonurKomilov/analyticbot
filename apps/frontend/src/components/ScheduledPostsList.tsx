import React, { useCallback } from 'react';
import { usePostStore } from '@/stores';
import { Box, Typography, List, ListItem, ListItemText, Paper } from '@mui/material';
import { IconButton } from './common/TouchTargetCompliance';
import { StatusChip } from './common';
import DeleteIcon from '@mui/icons-material/Delete';

interface ScheduledPost {
    id: string | number;
    file_type?: string;
    channel_name: string;
    text?: string;
    schedule_time: string | Date;
}

const ScheduledPostsList: React.FC = React.memo(() => {
    const { scheduledPosts, deletePost } = usePostStore() as any;

    const handleDelete = useCallback((postId: string | number) => {
        deletePost(postId);
    }, [deletePost]);

    return (
        <Paper elevation={2} sx={{ mb: 3, p: 2, bgcolor: 'background.paper', borderRadius: '6px' }}>
            <Typography variant="h6" gutterBottom>Scheduled Posts</Typography>
            {scheduledPosts.length === 0 ? (
                <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', mt: 2 }}>
                    You have no scheduled posts.
                </Typography>
            ) : (
                <List dense>
                    {scheduledPosts.map((post: ScheduledPost) => (
                        <ListItem
                            key={post.id}
                            secondaryAction={
                                <IconButton edge="end" aria-label="delete" onClick={() => handleDelete(post.id)}>
                                    <DeleteIcon />
                                </IconButton>
                            }
                            sx={{ borderBottom: '1px solid #30363d', pb: 1, mb: 1, '&:last-child': { borderBottom: 0, mb: 0 } }}
                        >
                            <ListItemText
                                primary={
                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                                        {post.file_type && <StatusChip label={post.file_type.toUpperCase()} size="small" variant={'info' as any} />}
                                        <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                                            To: {post.channel_name}
                                        </Typography>
                                    </Box>
                                }
                                secondary={
                                    <>
                                        <Typography variant="body1" component="span" sx={{ mb: 0.5, wordBreak: 'break-word', color: 'text.primary', display: 'block' }}>
                                            {post.text || <em>(No caption)</em>}
                                        </Typography>
                                        <Typography variant="caption" color="text.secondary" component="span" sx={{ display: 'block' }}>
                                            At: {new Date(post.schedule_time).toLocaleString()}
                                        </Typography>
                                    </>
                                }
                            />
                        </ListItem>
                    ))}
                </List>
            )}
        </Paper>
    );
});

ScheduledPostsList.displayName = 'ScheduledPostsList';

export default ScheduledPostsList;
