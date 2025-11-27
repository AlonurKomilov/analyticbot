/**
 * ContentTypeFilter Component
 *
 * Allows users to filter recommendations by content type
 * Integrates with advanced recommendation system (Phase 3/4)
 */

import React from 'react';
import {
    Box,
    ToggleButtonGroup,
    ToggleButton,
    Chip,
    Tooltip,
    Typography
} from '@mui/material';
import {
    VideoLibrary as VideoIcon,
    Image as ImageIcon,
    TextFields as TextIcon,
    Link as LinkIcon,
    ViewModule as AllIcon
} from '@mui/icons-material';

export type ContentType = 'all' | 'video' | 'image' | 'text' | 'link';

interface ContentTypeFilterProps {
    selectedType: ContentType;
    onTypeChange: (type: ContentType) => void;
    contentTypeCounts?: {
        video: number;
        image: number;
        text: number;
        link: number;
    };
    disabled?: boolean;
}

const ContentTypeFilter: React.FC<ContentTypeFilterProps> = ({
    selectedType,
    onTypeChange,
    contentTypeCounts,
    disabled = false
}) => {
    const handleChange = (_event: React.MouseEvent<HTMLElement>, newType: ContentType | null) => {
        if (newType !== null) {
            onTypeChange(newType);
        }
    };

    const getTypeColor = (type: ContentType): 'primary' | 'secondary' | 'success' | 'warning' => {
        switch (type) {
            case 'video': return 'secondary';
            case 'image': return 'success';
            case 'text': return 'primary';
            case 'link': return 'warning';
            default: return 'primary';
        }
    };

    return (
        <Box>
            <Typography variant="caption" color="text.secondary" gutterBottom display="block">
                Filter by Content Type
            </Typography>
            <ToggleButtonGroup
                value={selectedType}
                exclusive
                onChange={handleChange}
                aria-label="content type filter"
                disabled={disabled}
                size="small"
                sx={{ flexWrap: 'wrap', gap: 0.5 }}
            >
                <ToggleButton value="all" aria-label="all content">
                    <Tooltip title="All content types">
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                            <AllIcon fontSize="small" />
                            <span>All</span>
                        </Box>
                    </Tooltip>
                </ToggleButton>

                <ToggleButton value="video" aria-label="video content">
                    <Tooltip title={`Video posts${contentTypeCounts ? ` (${contentTypeCounts.video})` : ''}`}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                            <VideoIcon fontSize="small" />
                            <span>Video</span>
                            {contentTypeCounts && contentTypeCounts.video > 0 && (
                                <Chip
                                    label={contentTypeCounts.video}
                                    size="small"
                                    color={getTypeColor('video')}
                                    sx={{ height: 20, fontSize: '0.7rem' }}
                                />
                            )}
                        </Box>
                    </Tooltip>
                </ToggleButton>

                <ToggleButton value="image" aria-label="image content">
                    <Tooltip title={`Image posts${contentTypeCounts ? ` (${contentTypeCounts.image})` : ''}`}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                            <ImageIcon fontSize="small" />
                            <span>Image</span>
                            {contentTypeCounts && contentTypeCounts.image > 0 && (
                                <Chip
                                    label={contentTypeCounts.image}
                                    size="small"
                                    color={getTypeColor('image')}
                                    sx={{ height: 20, fontSize: '0.7rem' }}
                                />
                            )}
                        </Box>
                    </Tooltip>
                </ToggleButton>

                <ToggleButton value="text" aria-label="text content">
                    <Tooltip title={`Text posts${contentTypeCounts ? ` (${contentTypeCounts.text})` : ''}`}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                            <TextIcon fontSize="small" />
                            <span>Text</span>
                            {contentTypeCounts && contentTypeCounts.text > 0 && (
                                <Chip
                                    label={contentTypeCounts.text}
                                    size="small"
                                    color={getTypeColor('text')}
                                    sx={{ height: 20, fontSize: '0.7rem' }}
                                />
                            )}
                        </Box>
                    </Tooltip>
                </ToggleButton>

                <ToggleButton value="link" aria-label="link content">
                    <Tooltip title={`Link posts${contentTypeCounts ? ` (${contentTypeCounts.link})` : ''}`}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                            <LinkIcon fontSize="small" />
                            <span>Link</span>
                            {contentTypeCounts && contentTypeCounts.link > 0 && (
                                <Chip
                                    label={contentTypeCounts.link}
                                    size="small"
                                    color={getTypeColor('link')}
                                    sx={{ height: 20, fontSize: '0.7rem' }}
                                />
                            )}
                        </Box>
                    </Tooltip>
                </ToggleButton>
            </ToggleButtonGroup>
        </Box>
    );
};

export default ContentTypeFilter;
