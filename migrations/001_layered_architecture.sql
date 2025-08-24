-- Migration for PR-7: Layered Architecture
-- Create tables for scheduled posts and deliveries

-- Create scheduled_posts table
CREATE TABLE IF NOT EXISTS scheduled_posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL DEFAULT '',
    content TEXT NOT NULL DEFAULT '',
    channel_id VARCHAR(100) NOT NULL,
    user_id VARCHAR(100) NOT NULL,
    
    -- Scheduling timestamps
    scheduled_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    
    -- Status and metadata
    status VARCHAR(50) NOT NULL DEFAULT 'draft',
    tags TEXT[] DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    
    -- Media attachments
    media_urls TEXT[] DEFAULT '{}',
    media_types TEXT[] DEFAULT '{}'
);

-- Create indexes for scheduled_posts
CREATE INDEX IF NOT EXISTS idx_scheduled_posts_user_id ON scheduled_posts(user_id);
CREATE INDEX IF NOT EXISTS idx_scheduled_posts_channel_id ON scheduled_posts(channel_id);
CREATE INDEX IF NOT EXISTS idx_scheduled_posts_status ON scheduled_posts(status);
CREATE INDEX IF NOT EXISTS idx_scheduled_posts_scheduled_at ON scheduled_posts(scheduled_at);
CREATE INDEX IF NOT EXISTS idx_scheduled_posts_ready_delivery ON scheduled_posts(status, scheduled_at) 
    WHERE status = 'scheduled';

-- Create deliveries table
CREATE TABLE IF NOT EXISTS deliveries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID NOT NULL REFERENCES scheduled_posts(id) ON DELETE CASCADE,
    
    -- Delivery tracking
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    attempted_at TIMESTAMP WITH TIME ZONE,
    delivered_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Delivery details
    delivery_channel_id VARCHAR(100) NOT NULL,
    message_id VARCHAR(100), -- Telegram message ID after delivery
    
    -- Error handling
    error_message TEXT,
    retry_count INTEGER NOT NULL DEFAULT 0,
    max_retries INTEGER NOT NULL DEFAULT 3,
    
    -- Delivery metadata
    delivery_metadata JSONB DEFAULT '{}'
);

-- Create indexes for deliveries
CREATE INDEX IF NOT EXISTS idx_deliveries_post_id ON deliveries(post_id);
CREATE INDEX IF NOT EXISTS idx_deliveries_status ON deliveries(status);
CREATE INDEX IF NOT EXISTS idx_deliveries_channel_id ON deliveries(delivery_channel_id);
CREATE INDEX IF NOT EXISTS idx_deliveries_failed_retryable ON deliveries(status, retry_count, max_retries)
    WHERE status IN ('failed', 'retrying');

-- Add comments for documentation
COMMENT ON TABLE scheduled_posts IS 'Stores scheduled posts for delivery via Telegram bot';
COMMENT ON TABLE deliveries IS 'Tracks delivery attempts and status for scheduled posts';

COMMENT ON COLUMN scheduled_posts.status IS 'Post status: draft, scheduled, published, failed, cancelled';
COMMENT ON COLUMN deliveries.status IS 'Delivery status: pending, processing, delivered, failed, retrying';
COMMENT ON COLUMN deliveries.message_id IS 'Telegram message ID returned after successful delivery';
COMMENT ON COLUMN deliveries.retry_count IS 'Number of delivery attempts made';
COMMENT ON COLUMN deliveries.max_retries IS 'Maximum number of retry attempts allowed';

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at on scheduled_posts
CREATE TRIGGER update_scheduled_posts_updated_at 
    BEFORE UPDATE ON scheduled_posts 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();
