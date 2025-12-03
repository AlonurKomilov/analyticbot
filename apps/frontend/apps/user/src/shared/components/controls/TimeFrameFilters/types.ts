/**
 * TimeFrameFilters Types
 * Unified type definitions for time frame filter controls
 */

/**
 * Time frame options (standardized format)
 */
export type TimeFrame = '1h' | '6h' | '24h' | '7d' | '30d' | '90d' | '180d' | '1y' | 'all';

/**
 * Content type options
 */
export type ContentType = 'all' | 'text' | 'image' | 'video' | 'poll';

/**
 * Content type breakdown data
 */
export interface ContentTypeBreakdown {
    text?: number;
    video?: number;
    image?: number;
    link?: number;
}

/**
 * Props for TimeFrameFilters component
 */
export interface TimeFrameFiltersProps {
    /** Selected time frame */
    timeFrame: TimeFrame;
    /** Callback to update time frame */
    setTimeFrame: (timeFrame: TimeFrame) => void;
    /** Selected content type */
    contentType?: ContentType;
    /** Callback to update content type */
    setContentType?: (contentType: ContentType) => void;
    /** Total posts analyzed */
    totalPostsAnalyzed?: number;
    /** Content type breakdown */
    contentTypeBreakdown?: ContentTypeBreakdown;
    /** Optional title to display */
    title?: string;
    /** Optional icon to display with title */
    showIcon?: boolean;
}
