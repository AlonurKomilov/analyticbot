/**
 * CreatePostPage - Dedicated post creation page
 *
 * Focused page for post creation workflow with media management.
 * Extracted from the tab interface in MainDashboard.
 */

import React, { useState } from 'react';
import { Box, Stack } from '@mui/material';
import { useLocation } from 'react-router-dom';
import { TouchTargetProvider } from '@shared/components/ui';
import { PageContainer, SectionHeader } from '@shared/components/ui';
import { PostCreator } from '@features/posts';
import EnhancedMediaUploader from '@shared/components/ui/EnhancedMediaUploader';
import MediaPreview from '@shared/components/ui/MediaPreview';
import { TelegramStorageBrowser } from '@features/storage';
import { usePostStore, useMediaStore } from '@store';
import { DESIGN_TOKENS } from '@/theme/designTokens';

interface MediaItem {
    id: string;
    url: string;
    type: string;
    telegram_file_id?: string; // For files from Telegram storage
}

const CreatePostPage: React.FC = () => {
  const location = useLocation();
  const [localSelectedMedia, setLocalSelectedMedia] = useState<MediaItem[]>([]);
  const { schedulePost } = usePostStore();
  const { setPendingMedia } = useMediaStore();

  // Extract initial values from navigation state (from Best Time Recommendations)
  const initialChannelId = location.state?.channelId;
  const initialScheduledTime = location.state?.scheduledTime;
  const fromRecommendation = location.state?.fromRecommendation;

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
              {...{
                onSchedule: schedulePost,
                initialChannelId,
                initialScheduledTime,
                fromRecommendation
              } as any}
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
              <SectionHeader level={3}>Storage Browser</SectionHeader>
              <TelegramStorageBrowser
                onSelectFile={(file) => {
                  // Create MediaItem for preview
                  const mediaItem: MediaItem = {
                    id: file.id.toString(),
                    url: file.preview_url || '',
                    type: file.file_type,
                    telegram_file_id: file.telegram_file_id
                  };
                  setLocalSelectedMedia(prev => [...prev, mediaItem]);

                  // Set pending media for posting (use empty File as placeholder)
                  // The telegram_file_id is what actually matters for posting
                  setPendingMedia({
                    id: file.id.toString(),
                    file: new File([], file.file_name || 'telegram-storage-file', { type: file.mime_type || 'application/octet-stream' }),
                    preview: file.preview_url || undefined,
                    status: 'complete',
                    type: file.file_type as 'image' | 'video' | 'document',
                    telegram_file_id: file.telegram_file_id,
                    url: file.preview_url || undefined
                  });
                }}
                selectionMode={true}
              />
            </Box>
          </Stack>
        </Box>
      </PageContainer>
    </TouchTargetProvider>
  );
};

export default CreatePostPage;
