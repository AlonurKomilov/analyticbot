/**
 * CreatePostPage - Dedicated post creation page
 *
 * Focused page for post creation workflow with media management.
 * Extracted from the tab interface in MainDashboard.
 */

import React, { useState } from 'react';
import { Box, Stack } from '@mui/material';
import { TouchTargetProvider } from '../common/TouchTargetCompliance.jsx';
import { PageContainer, SectionHeader } from '../common/StandardComponents.jsx';
import PostCreator from '../PostCreator.jsx';
import EnhancedMediaUploader from '../EnhancedMediaUploader.jsx';
import MediaPreview from '../MediaPreview.jsx';
import StorageFileBrowser from '../StorageFileBrowser.jsx';
import { usePostStore } from '@/stores';
import { DESIGN_TOKENS } from '../../theme/designTokens.js';

const CreatePostPage = () => {
  const [localSelectedMedia, setLocalSelectedMedia] = useState([]);
  const { schedulePost } = usePostStore();

  const handleRemoveMedia = (index) => {
    const newMedia = [...localSelectedMedia];
    newMedia.splice(index, 1);
    setLocalSelectedMedia(newMedia);
  };

  return (
    <TouchTargetProvider>
      <PageContainer>
        <SectionHeader level={1}>
          Create New Post
        </SectionHeader>

        <Box sx={{
          display: 'grid',
          gap: DESIGN_TOKENS.layout.grid.gap.md,
          gridTemplateColumns: {
            xs: '1fr',
            md: '2fr 1fr'
          }
        }}>
          {/* Main Content - Post Creator */}
          <Box>
            <PostCreator
              onSchedule={schedulePost}
            />
          </Box>

          {/* Sidebar - Media Management */}
          <Stack spacing={3}>
            <Box>
              <SectionHeader level={3}>Media Upload</SectionHeader>
              <EnhancedMediaUploader
                onMediaSelect={setLocalSelectedMedia}
              />
            </Box>

            {localSelectedMedia.length > 0 && (
              <Box>
                <SectionHeader level={3}>Selected Media</SectionHeader>
                <MediaPreview
                  media={localSelectedMedia}
                  onRemove={handleRemoveMedia}
                />
              </Box>
            )}

            <Box>
              <SectionHeader level={3}>File Browser</SectionHeader>
              <StorageFileBrowser
                onFileSelect={setLocalSelectedMedia}
              />
            </Box>
          </Stack>
        </Box>
      </PageContainer>
    </TouchTargetProvider>
  );
};

export default CreatePostPage;
