# Telegram Channel Storage Implementation

## Overview
Use Telegram channels as cloud storage instead of local server storage. This saves server space and gives users control over their media.

## Architecture

### Database Schema

```sql
-- User storage channels table
CREATE TABLE user_storage_channels (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    channel_id BIGINT NOT NULL,
    channel_title VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, channel_id)
);

-- Media stored in Telegram
CREATE TABLE telegram_media (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    storage_channel_id INTEGER REFERENCES user_storage_channels(id),
    telegram_file_id VARCHAR(255) NOT NULL,
    telegram_message_id INTEGER NOT NULL,
    file_type VARCHAR(50), -- 'photo', 'video', 'document'
    file_name VARCHAR(255),
    file_size BIGINT,
    mime_type VARCHAR(100),
    thumbnail_file_id VARCHAR(255),
    caption TEXT,
    uploaded_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB
);

-- Index for fast lookups
CREATE INDEX idx_telegram_media_user ON telegram_media(user_id);
CREATE INDEX idx_telegram_media_channel ON telegram_media(storage_channel_id);
CREATE INDEX idx_telegram_media_file_id ON telegram_media(telegram_file_id);
```

### API Endpoints

#### 1. Storage Channel Management

```python
# POST /api/storage-channels/connect
# Connect user's storage channel to the system
{
    "channel_username": "@my_storage_channel",
    "channel_id": -1001234567890  # Optional, will be validated
}

# GET /api/storage-channels
# List user's storage channels

# DELETE /api/storage-channels/{channel_id}
# Disconnect storage channel
```

#### 2. Media Upload (via Telegram)

```python
# POST /api/media/upload-telegram
# Upload file to user's storage channel
{
    "file": <binary>,
    "storage_channel_id": 123,
    "caption": "Optional caption",
    "file_type": "photo" | "video" | "document"
}

# Response:
{
    "id": 456,
    "telegram_file_id": "AgACAgIAAxkBAAI...",
    "telegram_message_id": 789,
    "preview_url": "https://t.me/storage_channel/789",
    "storage_channel_id": 123
}
```

#### 3. Media Management

```python
# GET /api/media/telegram-storage
# List files from user's Telegram storage
{
    "files": [
        {
            "id": 123,
            "telegram_file_id": "AgACAgIAAxkBAAI...",
            "file_name": "photo.jpg",
            "file_size": 1234567,
            "uploaded_at": "2025-11-14T12:00:00Z",
            "preview_url": "https://t.me/storage_channel/789"
        }
    ],
    "total": 50
}

# POST /api/media/forward-from-storage
# Forward/use file from storage in a post
{
    "telegram_media_id": 123,
    "target_channel_id": -1001234567890,
    "caption": "New caption"
}
```

## Implementation Steps

### Step 1: Create Storage Channel Service

```python
# File: apps/api/services/telegram_storage_service.py

from telethon import TelegramClient
from telethon.tl.types import Channel, InputChannel

class TelegramStorageService:
    def __init__(self, user_bot_client: TelegramClient):
        self.client = user_bot_client

    async def validate_storage_channel(self, channel_id: int) -> dict:
        """Validate bot has admin access to storage channel"""
        try:
            channel = await self.client.get_entity(channel_id)

            # Check if it's a channel
            if not isinstance(channel, Channel):
                raise ValueError("Must be a channel, not a group")

            # Check bot is admin
            permissions = await self.client.get_permissions(channel, 'me')
            if not permissions.is_admin:
                raise ValueError("Bot must be admin in the storage channel")

            return {
                "channel_id": channel.id,
                "title": channel.title,
                "username": channel.username,
                "is_valid": True
            }
        except Exception as e:
            return {
                "is_valid": False,
                "error": str(e)
            }

    async def upload_to_storage(
        self,
        file_path: str,
        storage_channel_id: int,
        caption: str = None,
        file_type: str = 'document'
    ) -> dict:
        """Upload file to user's storage channel"""
        try:
            if file_type == 'photo':
                message = await self.client.send_file(
                    storage_channel_id,
                    file_path,
                    caption=caption,
                    force_document=False
                )
            elif file_type == 'video':
                message = await self.client.send_file(
                    storage_channel_id,
                    file_path,
                    caption=caption,
                    force_document=False,
                    supports_streaming=True
                )
            else:
                message = await self.client.send_file(
                    storage_channel_id,
                    file_path,
                    caption=caption,
                    force_document=True
                )

            # Extract file info
            file_id = None
            file_size = 0
            mime_type = None
            thumbnail_file_id = None

            if message.photo:
                file_id = message.photo.id
                file_size = message.photo.sizes[-1].size if message.photo.sizes else 0
                mime_type = "image/jpeg"
            elif message.video:
                file_id = message.video.id
                file_size = message.video.size
                mime_type = message.video.mime_type
                if message.video.thumbs:
                    thumbnail_file_id = message.video.thumbs[0].file_reference
            elif message.document:
                file_id = message.document.id
                file_size = message.document.size
                mime_type = message.document.mime_type
                if message.document.thumbs:
                    thumbnail_file_id = message.document.thumbs[0].file_reference

            return {
                "success": True,
                "telegram_file_id": str(file_id),
                "telegram_message_id": message.id,
                "file_size": file_size,
                "mime_type": mime_type,
                "thumbnail_file_id": str(thumbnail_file_id) if thumbnail_file_id else None,
                "channel_id": storage_channel_id,
                "preview_link": f"https://t.me/c/{str(storage_channel_id)[4:]}/{message.id}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def download_from_storage(
        self,
        storage_channel_id: int,
        message_id: int,
        download_path: str = None
    ) -> str:
        """Download file from storage channel (for processing)"""
        try:
            message = await self.client.get_messages(storage_channel_id, ids=message_id)

            if not message or not message.media:
                raise ValueError("Message not found or has no media")

            # Download file
            file_path = await message.download_media(file=download_path)
            return file_path
        except Exception as e:
            raise Exception(f"Failed to download from storage: {e}")

    async def forward_from_storage(
        self,
        storage_channel_id: int,
        message_id: int,
        target_channel_id: int,
        new_caption: str = None
    ) -> dict:
        """Forward file from storage to target channel"""
        try:
            # Get original message
            message = await self.client.get_messages(storage_channel_id, ids=message_id)

            if not message:
                raise ValueError("Message not found in storage")

            # Forward or send with new caption
            if new_caption:
                # Send as new message with new caption
                new_message = await self.client.send_file(
                    target_channel_id,
                    message.media,
                    caption=new_caption
                )
            else:
                # Simple forward
                new_message = await self.client.forward_messages(
                    target_channel_id,
                    message
                )

            return {
                "success": True,
                "target_message_id": new_message.id,
                "target_channel_id": target_channel_id
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def list_storage_files(
        self,
        storage_channel_id: int,
        limit: int = 100,
        offset_id: int = 0
    ) -> list:
        """List all media files in storage channel"""
        try:
            messages = await self.client.get_messages(
                storage_channel_id,
                limit=limit,
                offset_id=offset_id,
                filter=InputMessagesFilterPhotosVideos()  # Only media
            )

            files = []
            for msg in messages:
                if msg.media:
                    file_info = self._extract_file_info(msg)
                    files.append(file_info)

            return files
        except Exception as e:
            raise Exception(f"Failed to list storage files: {e}")

    def _extract_file_info(self, message) -> dict:
        """Extract file information from message"""
        info = {
            "message_id": message.id,
            "date": message.date,
            "caption": message.message or ""
        }

        if message.photo:
            info.update({
                "file_type": "photo",
                "file_id": str(message.photo.id),
                "file_size": message.photo.sizes[-1].size if message.photo.sizes else 0
            })
        elif message.video:
            info.update({
                "file_type": "video",
                "file_id": str(message.video.id),
                "file_size": message.video.size,
                "duration": message.video.duration,
                "mime_type": message.video.mime_type
            })
        elif message.document:
            info.update({
                "file_type": "document",
                "file_id": str(message.document.id),
                "file_size": message.document.size,
                "file_name": next((attr.file_name for attr in message.document.attributes if hasattr(attr, 'file_name')), None),
                "mime_type": message.document.mime_type
            })

        return info
```

### Step 2: Create API Router

```python
# File: apps/api/routers/telegram_storage_router.py

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from apps.api.middleware.auth import get_current_user
from apps.api.services.telegram_storage_service import TelegramStorageService

router = APIRouter(prefix="/storage", tags=["Telegram Storage"])

class ConnectStorageChannelRequest(BaseModel):
    channel_id: int
    channel_title: str = None

class UploadToStorageRequest(BaseModel):
    storage_channel_id: int
    caption: str = None
    file_type: str = "document"

@router.post("/channels/connect")
async def connect_storage_channel(
    request: ConnectStorageChannelRequest,
    current_user: dict = Depends(get_current_user)
):
    """Connect user's Telegram channel as storage"""
    # Get user's MTProto client
    # ... (use existing MTProto service)

    # Validate channel
    storage_service = TelegramStorageService(user_client)
    validation = await storage_service.validate_storage_channel(request.channel_id)

    if not validation["is_valid"]:
        raise HTTPException(status_code=400, detail=validation["error"])

    # Save to database
    # ... save user_storage_channels

    return {
        "success": True,
        "channel": validation
    }

@router.get("/channels")
async def list_storage_channels(
    current_user: dict = Depends(get_current_user)
):
    """List user's connected storage channels"""
    # Query database for user's storage channels
    # ...

    return {
        "channels": [...]
    }

@router.post("/upload")
async def upload_to_telegram_storage(
    file: UploadFile = File(...),
    storage_channel_id: int = Form(...),
    caption: str = Form(None),
    file_type: str = Form("document"),
    current_user: dict = Depends(get_current_user)
):
    """Upload file to user's Telegram storage channel"""
    # Save file temporarily
    temp_path = f"/tmp/{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(await file.read())

    # Upload to Telegram
    storage_service = TelegramStorageService(user_client)
    result = await storage_service.upload_to_storage(
        temp_path,
        storage_channel_id,
        caption,
        file_type
    )

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])

    # Save metadata to database
    # ... save to telegram_media table

    # Clean up temp file
    os.remove(temp_path)

    return result

@router.get("/files")
async def list_telegram_storage_files(
    storage_channel_id: int = None,
    limit: int = 20,
    offset: int = 0,
    current_user: dict = Depends(get_current_user)
):
    """List files from Telegram storage"""
    # Query telegram_media table
    # ...

    return {
        "files": [...],
        "total": 123
    }

@router.post("/forward")
async def forward_from_storage(
    telegram_media_id: int,
    target_channel_id: int,
    new_caption: str = None,
    current_user: dict = Depends(get_current_user)
):
    """Forward file from storage to target channel"""
    # Get file info from database
    # ...

    storage_service = TelegramStorageService(user_client)
    result = await storage_service.forward_from_storage(
        storage_channel_id,
        message_id,
        target_channel_id,
        new_caption
    )

    return result
```

### Step 3: Update Frontend

```typescript
// File: apps/frontend/src/store/slices/storage/useTelegramStorageStore.ts

import { create } from 'zustand';
import { apiClient } from '@/api/client';

interface StorageChannel {
  id: number;
  channel_id: number;
  channel_title: string;
  is_active: boolean;
}

interface TelegramMediaFile {
  id: number;
  telegram_file_id: string;
  telegram_message_id: number;
  file_name: string;
  file_size: number;
  file_type: string;
  uploaded_at: string;
  preview_link: string;
}

interface TelegramStorageState {
  storageChannels: StorageChannel[];
  telegramFiles: TelegramMediaFile[];
  isLoading: boolean;
  error: string | null;

  // Actions
  fetchStorageChannels: () => Promise<void>;
  connectStorageChannel: (channelId: number) => Promise<void>;
  uploadToTelegram: (file: File, storageChannelId: number, caption?: string) => Promise<void>;
  fetchTelegramFiles: (storageChannelId?: number) => Promise<void>;
  forwardFromStorage: (telegramMediaId: number, targetChannelId: number) => Promise<void>;
}

export const useTelegramStorageStore = create<TelegramStorageState>((set) => ({
  storageChannels: [],
  telegramFiles: [],
  isLoading: false,
  error: null,

  fetchStorageChannels: async () => {
    set({ isLoading: true });
    try {
      const channels = await apiClient.get('/storage/channels');
      set({ storageChannels: channels, isLoading: false });
    } catch (error) {
      set({ error: error.message, isLoading: false });
    }
  },

  connectStorageChannel: async (channelId: number) => {
    set({ isLoading: true });
    try {
      await apiClient.post('/storage/channels/connect', { channel_id: channelId });
      // Refresh list
      await get().fetchStorageChannels();
    } catch (error) {
      set({ error: error.message, isLoading: false });
    }
  },

  uploadToTelegram: async (file: File, storageChannelId: number, caption?: string) => {
    set({ isLoading: true });
    const formData = new FormData();
    formData.append('file', file);
    formData.append('storage_channel_id', String(storageChannelId));
    if (caption) formData.append('caption', caption);

    try {
      await apiClient.post('/storage/upload', formData);
      // Refresh files
      await get().fetchTelegramFiles(storageChannelId);
    } catch (error) {
      set({ error: error.message, isLoading: false });
    }
  },

  fetchTelegramFiles: async (storageChannelId?: number) => {
    set({ isLoading: true });
    try {
      const params = storageChannelId ? { storage_channel_id: storageChannelId } : {};
      const result = await apiClient.get('/storage/files', { params });
      set({ telegramFiles: result.files, isLoading: false });
    } catch (error) {
      set({ error: error.message, isLoading: false });
    }
  }
}));
```

## Setup Guide for Users

### 1. Create Storage Channel
```
1. Open Telegram
2. Create new channel (any name, e.g., "My Storage")
3. Make it private (important!)
4. Add your analyticbot as admin
5. Give it all permissions
```

### 2. Connect to System
```
In your app:
1. Go to Settings → Storage
2. Click "Connect Storage Channel"
3. Enter channel ID or username
4. Bot will validate access
5. Start uploading!
```

### 3. Usage
```
- All uploads go to your storage channel
- Files never expire
- You own all your data
- Can access via Telegram anytime
- Forward to any of your channels
```

## Migration Strategy

### Phase 1: Implement (Week 1)
- Add database tables
- Create TelegramStorageService
- Add API endpoints
- Test with one user

### Phase 2: Frontend (Week 2)
- Update upload components
- Add storage channel management UI
- Update file browser to show Telegram files
- Add migration tool for existing files

### Phase 3: Migrate (Week 3)
- Offer users to connect storage channel
- Auto-upload existing server files to their Telegram storage
- Delete from server after confirmation
- Monitor storage savings

### Phase 4: Optimize (Week 4)
- Add file deduplication (same file_id)
- Implement thumbnail caching
- Add bulk operations
- Performance monitoring

## Cost Savings

```
Current: 1000 users × 500MB average = 500GB server storage
Cost: ~$50/month for storage + bandwidth

With Telegram Storage: 0GB server storage
Cost: $0/month
Savings: 100%!
```

## Security Considerations

1. **Private Channels Only** - Users must use private channels
2. **Bot Verification** - Validate bot has admin access
3. **User Data Isolation** - Each user has their own storage channel
4. **No Cross-Access** - Bot can only access user's own storage
5. **Audit Logging** - Log all storage operations

## Future Enhancements

1. **Multi-Storage Support** - Connect multiple storage channels
2. **Smart Categories** - Auto-organize by file type
3. **Storage Analytics** - Show usage statistics
4. **Backup & Export** - Easy data export
5. **Shared Storage** - Team storage channels

## Conclusion

This implementation:
- ✅ Saves 100% server storage costs
- ✅ Gives users full data ownership
- ✅ Uses Telegram's reliable infrastructure
- ✅ Scales infinitely
- ✅ Easy to implement with existing MTProto setup

Ready to implement! 🚀
