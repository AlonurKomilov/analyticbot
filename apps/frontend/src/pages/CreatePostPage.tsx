/**
 * CreatePostPage - Dedicated post creation page
 *
 * Focused page for post creation workflow with media management.
 * Extracted from the tab interface in MainDashboard.
 */

import React, { useState } from 'react';
import { Box, Stack } from '@mui/material';
import { TouchTargetProvider } from '@shared/components/ui';
import { PageContainer, SectionHeader } from '@shared/components/ui';
import { PostCreator } from '@features/posts';
import EnhancedMediaUploader from '@/components/EnhancedMediaUploader.jsx';
import MediaPreview from '@/components/MediaPreview';
import StorageFileBrowser from '@/components/StorageFileBrowser.jsx';
import { usePostStore } from '@store';
import { DESIGN_TOKENS } from '@/theme/designTokens.js';

interface MediaItem {
    id: string;
    url: string;
    type: string;
}

const CreatePostPage: React.FC = () => {
  const [localSelectedMedia, setLocalSelectedMedia] = useState<MediaItem[]>([]);
  const { schedulePost } = usePostStore();

  const handleRemoveMedia = (index: number): void => {
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
              {...{ onSchedule: schedulePost } as any}
            />
          </Box>

          {/* Sidebar - Media Management */}
          <Stack spacing={3}>
            <Box>
              <SectionHeader level={3}>Media Upload</SectionHeader>
              <EnhancedMediaUploader
                {...{ onMediaSelect: setLocalSelectedMedia } as any}
              />
            </Box>

            {localSelectedMedia.length > 0 && (
              <Box>
                <SectionHeader level={3}>Selected Media</SectionHeader>
                <MediaPreview {...{ media: localSelectedMedia, onRemove: handleRemoveMedia } as any} />
              </Box>
            )}

            <Box>
              <SectionHeader level={3}>File Browser</SectionHeader>
              <StorageFileBrowser
                {...{ onFileSelect: setLocalSelectedMedia } as any}
              />
            </Box>
          </Stack>
        </Box>
      </PageContainer>
    </TouchTargetProvider>
  );
};

export default CreatePostPage;
