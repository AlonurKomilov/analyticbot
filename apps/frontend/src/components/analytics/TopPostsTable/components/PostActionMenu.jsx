import React from 'react';
import {
    IconButton,
    Menu,
    MenuItem
} from '@mui/material';
import { MoreVert as MoreVertIcon } from '@mui/icons-material';

const PostActionMenu = ({ 
    post, 
    anchorEl, 
    selectedPostId, 
    onMenuClick, 
    onMenuClose 
}) => {
    const isOpen = Boolean(anchorEl) && selectedPostId === post.id;

    return (
        <>
            <IconButton
                size="small"
                onClick={(e) => onMenuClick(e, post.id)}
                aria-label={`Actions for post: ${post.title || 'Untitled'}`}
                aria-haspopup="menu"
            >
                <MoreVertIcon fontSize="small" />
            </IconButton>
            
            <Menu
                anchorEl={anchorEl}
                open={isOpen}
                onClose={onMenuClose}
                onClick={onMenuClose}
                PaperProps={{
                    elevation: 0,
                    sx: {
                        overflow: 'visible',
                        filter: 'drop-shadow(0px 2px 8px rgba(0,0,0,0.32))',
                        mt: 1.5,
                        '& .MuiAvatar-root': {
                            width: 32,
                            height: 32,
                            ml: -0.5,
                            mr: 1,
                        },
                        '&:before': {
                            content: '""',
                            display: 'block',
                            position: 'absolute',
                            top: 0,
                            right: 14,
                            width: 10,
                            height: 10,
                            bgcolor: 'background.paper',
                            transform: 'translateY(-50%) rotate(45deg)',
                            zIndex: 0,
                        },
                    },
                }}
                transformOrigin={{ horizontal: 'right', vertical: 'top' }}
                anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
            >
                <MenuItem onClick={() => console.log('View details:', post.id)}>
                    View Details
                </MenuItem>
                <MenuItem onClick={() => console.log('Edit post:', post.id)}>
                    Edit Post
                </MenuItem>
                <MenuItem onClick={() => console.log('Share post:', post.id)}>
                    Share
                </MenuItem>
                <MenuItem onClick={() => console.log('Archive post:', post.id)}>
                    Archive
                </MenuItem>
            </Menu>
        </>
    );
};

export default PostActionMenu;