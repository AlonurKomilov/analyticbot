import React, { useState, useEffect, useCallback } from 'react';
import {
    Box,
    Typography,
    Grid,
    Card,
    CardMedia,
    CardContent,
    CardActions,
    Button,
    IconButton,
    Chip,
    Pagination,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    TextField,
    InputAdornment,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Skeleton
} from '@mui/material';
import {
    Search as SearchIcon,
    Refresh as RefreshIcon,
    GetApp as DownloadIcon,
    Share as ShareIcon,
    Info as InfoIcon,
    Image as ImageIcon,
    VideoFile as VideoIcon,
    Description as DocumentIcon,
    Animation as AnimationIcon
} from '@mui/icons-material';
import { useAppStore } from '../store/appStore.js';
import { useTelegramWebApp } from '../hooks/index.js';

const StorageFileBrowser = ({ onFileSelect = null }) => {
    const {
        getStorageFiles,
        storageFiles = { files: [], total: 0, limit: 20, offset: 0 },
        isLoading
    } = useAppStore();
    
    const { hapticFeedback } = useTelegramWebApp();
    
    // Local state
    const [page, setPage] = useState(1);
    const [filterType, setFilterType] = useState('all');
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedFile, setSelectedFile] = useState(null);
    const [detailsOpen, setDetailsOpen] = useState(false);

    // Load files on component mount and filter changes
    useEffect(() => {
        loadFiles();
    }, [page, filterType]);

    // Load files from storage
    const loadFiles = useCallback(async () => {
        try {
            const limit = 20;
            const offset = (page - 1) * limit;
            await getStorageFiles(limit, offset);
        } catch (error) {
            console.error('Failed to load storage files:', error);
        }
    }, [getStorageFiles, page]);

    // Handle page change
    const handlePageChange = useCallback((event, newPage) => {
        setPage(newPage);
        hapticFeedback('light');
    }, [hapticFeedback]);

    // Handle refresh
    const handleRefresh = useCallback(() => {
        setPage(1);
        loadFiles();
        hapticFeedback('medium');
    }, [loadFiles, hapticFeedback]);

    // Handle file selection
    const handleFileSelect = useCallback((file) => {
        if (onFileSelect) {
            onFileSelect(file);
            hapticFeedback('success');
        } else {
            setSelectedFile(file);
            setDetailsOpen(true);
            hapticFeedback('light');
        }
    }, [onFileSelect, hapticFeedback]);

    // Get file icon based on type
    const getFileIcon = (fileType) => {
        if (fileType?.startsWith('image/')) {
            return <ImageIcon />;
        } else if (fileType?.startsWith('video/')) {
            return <VideoIcon />;
        } else if (fileType === 'animation') {
            return <AnimationIcon />;
        } else {
            return <DocumentIcon />;
        }
    };

    // Get file type color
    const getFileTypeColor = (fileType) => {
        if (fileType?.startsWith('image/')) {
            return 'success';
        } else if (fileType?.startsWith('video/')) {
            return 'primary';
        } else if (fileType === 'animation') {
            return 'secondary';
        } else {
            return 'default';
        }
    };

    // Format file size
    const formatFileSize = (bytes) => {
        if (!bytes) return 'Unknown';
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    // Filter files based on search and type
    const filteredFiles = storageFiles.files.filter(file => {
        const matchesSearch = !searchQuery || 
            file.filename?.toLowerCase().includes(searchQuery.toLowerCase()) ||
            file.caption?.toLowerCase().includes(searchQuery.toLowerCase());
        
        const matchesType = filterType === 'all' || 
            (filterType === 'images' && file.media_type?.startsWith('image/')) ||
            (filterType === 'videos' && file.media_type?.startsWith('video/')) ||
            (filterType === 'documents' && !file.media_type?.startsWith('image/') && !file.media_type?.startsWith('video/'));
        
        return matchesSearch && matchesType;
    });

    // Total pages
    const totalPages = Math.ceil(storageFiles.total / storageFiles.limit);

    return (
        <Box>
            {/* Header */}
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="h6">
                    📁 Storage Browser
                </Typography>
                <IconButton onClick={handleRefresh} disabled={isLoading('getStorageFiles')}>
                    <RefreshIcon />
                </IconButton>
            </Box>

            {/* Filters */}
            <Box sx={{ mb: 2 }}>
                <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                        <TextField
                            fullWidth
                            size="small"
                            placeholder="Search files..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            InputProps={{
                                startAdornment: (
                                    <InputAdornment position="start">
                                        <SearchIcon />
                                    </InputAdornment>
                                )
                            }}
                        />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                        <FormControl fullWidth size="small">
                            <InputLabel>Filter by type</InputLabel>
                            <Select
                                value={filterType}
                                label="Filter by type"
                                onChange={(e) => setFilterType(e.target.value)}
                            >
                                <MenuItem value="all">All Files</MenuItem>
                                <MenuItem value="images">Images</MenuItem>
                                <MenuItem value="videos">Videos</MenuItem>
                                <MenuItem value="documents">Documents</MenuItem>
                            </Select>
                        </FormControl>
                    </Grid>
                </Grid>
            </Box>

            {/* Files Grid */}
            {isLoading('getStorageFiles') ? (
                <Grid container spacing={2}>
                    {[...Array(6)].map((_, index) => (
                        <Grid item xs={12} sm={6} md={4} key={index}>
                            <Card>
                                <Skeleton variant="rectangular" height={140} />
                                <CardContent>
                                    <Skeleton width="60%" />
                                    <Skeleton width="40%" />
                                </CardContent>
                            </Card>
                        </Grid>
                    ))}
                </Grid>
            ) : filteredFiles.length === 0 ? (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                    <Typography variant="body1" color="text.secondary">
                        {storageFiles.files.length === 0 ? 
                            'No files in storage yet. Upload some files to see them here.' :
                            'No files match your search criteria.'
                        }
                    </Typography>
                </Box>
            ) : (
                <Grid container spacing={2}>
                    {filteredFiles.map((file) => (
                        <Grid item xs={12} sm={6} md={4} key={file.file_id}>
                            <Card 
                                sx={{ 
                                    cursor: 'pointer',
                                    '&:hover': { elevation: 4 }
                                }}
                                onClick={() => handleFileSelect(file)}
                            >
                                {file.media_type?.startsWith('image/') ? (
                                    <CardMedia
                                        component="img"
                                        height="140"
                                        image={file.thumbnail_url || '/placeholder-image.png'}
                                        alt={file.filename}
                                        sx={{ objectFit: 'cover' }}
                                    />
                                ) : (
                                    <Box 
                                        sx={{ 
                                            height: 140, 
                                            display: 'flex', 
                                            alignItems: 'center', 
                                            justifyContent: 'center',
                                            backgroundColor: 'grey.100'
                                        }}
                                    >
                                        {getFileIcon(file.media_type)}
                                    </Box>
                                )}
                                
                                <CardContent sx={{ pb: 1 }}>
                                    <Typography variant="body2" noWrap>
                                        {file.filename || 'Unnamed file'}
                                    </Typography>
                                    <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                                        <Chip
                                            icon={getFileIcon(file.media_type)}
                                            label={file.media_type || 'unknown'}
                                            size="small"
                                            color={getFileTypeColor(file.media_type)}
                                        />
                                        {file.file_size && (
                                            <Chip
                                                label={formatFileSize(file.file_size)}
                                                size="small"
                                                variant="outlined"
                                            />
                                        )}
                                    </Box>
                                </CardContent>

                                <CardActions sx={{ pt: 0 }}>
                                    <Button size="small" startIcon={<InfoIcon />}>
                                        Details
                                    </Button>
                                    {onFileSelect && (
                                        <Button size="small" startIcon={<ShareIcon />} color="primary">
                                            Use
                                        </Button>
                                    )}
                                </CardActions>
                            </Card>
                        </Grid>
                    ))}
                </Grid>
            )}

            {/* Pagination */}
            {totalPages > 1 && (
                <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
                    <Pagination
                        count={totalPages}
                        page={page}
                        onChange={handlePageChange}
                        color="primary"
                    />
                </Box>
            )}

            {/* File Details Dialog */}
            <Dialog open={detailsOpen} onClose={() => setDetailsOpen(false)} maxWidth="sm" fullWidth>
                <DialogTitle>File Details</DialogTitle>
                <DialogContent>
                    {selectedFile && (
                        <Box>
                            {selectedFile.media_type?.startsWith('image/') && (
                                <Box sx={{ mb: 2, textAlign: 'center' }}>
                                    <img
                                        src={selectedFile.preview_url || '/placeholder-image.png'}
                                        alt={selectedFile.filename}
                                        style={{ maxWidth: '100%', maxHeight: 300, borderRadius: 8 }}
                                    />
                                </Box>
                            )}
                            
                            <Typography variant="subtitle1" gutterBottom>
                                <strong>Filename:</strong> {selectedFile.filename || 'Unnamed'}
                            </Typography>
                            <Typography variant="body2" gutterBottom>
                                <strong>Type:</strong> {selectedFile.media_type || 'Unknown'}
                            </Typography>
                            <Typography variant="body2" gutterBottom>
                                <strong>Size:</strong> {formatFileSize(selectedFile.file_size)}
                            </Typography>
                            <Typography variant="body2" gutterBottom>
                                <strong>File ID:</strong> {selectedFile.file_id}
                            </Typography>
                            {selectedFile.uploaded_at && (
                                <Typography variant="body2" gutterBottom>
                                    <strong>Uploaded:</strong> {new Date(selectedFile.uploaded_at).toLocaleString()}
                                </Typography>
                            )}
                        </Box>
                    )}
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setDetailsOpen(false)}>Close</Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
};

export default StorageFileBrowser;
