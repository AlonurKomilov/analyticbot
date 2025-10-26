/**
 * useContentProtection Hook
 *
 * Encapsulates business logic and state for content protection features:
 * - Theft detection scans
 * - Text watermarking
 * - Image watermarking
 */

import React, { useState, useCallback } from 'react';
import {
    contentProtectionService,
    type TheftDetectionResult,
} from '@/services/contentProtectionService';

export type UseContentProtectionReturn = {
    // global
    loading: boolean;
    error: string | null;
    success: string | null;
    clearMessages: () => void;

    // theft
    scanResults: TheftDetectionResult | null;
    scanPlatforms: string[];
    setScanPlatforms: React.Dispatch<React.SetStateAction<string[]>>;
    handleScanForTheft: (channelId?: string) => Promise<void>;

    // text watermark
    watermarkedText: string;
    handleApplyTextWatermark: (text: string, type: 'invisible' | 'visible', position: 'top' | 'center' | 'bottom') => Promise<void>;

    // image watermark
    watermarkedImageUrl: string;
    handleApplyImageWatermark: (
        imageUrl: string,
        watermarkText: string,
        opacity: number,
        position: 'top-left' | 'top-right' | 'center' | 'bottom-left' | 'bottom-right'
    ) => Promise<void>;

    // clipboard helper
    copyToClipboard: (text: string) => void;
};

export const useContentProtection = (): UseContentProtectionReturn => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<string | null>(null);

    // Theft detection
    const [scanResults, setScanResults] = useState<TheftDetectionResult | null>(null);
    const [scanPlatforms, setScanPlatforms] = useState<string[]>(['telegram', 'twitter', 'facebook']);

    // Text watermark
    const [watermarkedText, setWatermarkedText] = useState('');

    // Image watermark
    const [watermarkedImageUrl, setWatermarkedImageUrl] = useState('');

    const clearMessages = useCallback(() => {
        setError(null);
        setSuccess(null);
    }, []);

    const handleScanForTheft = useCallback(async (channelId?: string) => {
        if (!channelId) {
            setError('Channel ID is required');
            return;
        }

        setLoading(true);
        setError(null);
        setScanResults(null);

        try {
            const results = await contentProtectionService.scanForTheft(channelId, undefined, scanPlatforms);
            setScanResults(results);

            if (results.detected) {
                setSuccess(`Found ${results.matches.length} potential theft instances`);
            } else {
                setSuccess('No content theft detected. Your content is safe!');
            }
        } catch (err: any) {
            setError(err.message || 'Failed to scan for theft');
        } finally {
            setLoading(false);
        }
    }, [scanPlatforms]);

    const handleApplyTextWatermark = useCallback(async (text: string, type: 'invisible' | 'visible', position: 'top' | 'center' | 'bottom') => {
        if (!text.trim()) {
            setError('Please enter text to watermark');
            return;
        }

        setLoading(true);
        setError(null);
        setWatermarkedText('');

        try {
            const response = await contentProtectionService.applyTextWatermark(text, type, position);
            setWatermarkedText(response.watermarked_text);
            setSuccess('Text watermark applied successfully!');
        } catch (err: any) {
            setError(err.message || 'Failed to apply watermark');
        } finally {
            setLoading(false);
        }
    }, []);

    const handleApplyImageWatermark = useCallback(async (
        imageUrl: string,
        watermarkText: string,
        opacity: number,
        position: 'top-left' | 'top-right' | 'center' | 'bottom-left' | 'bottom-right'
    ) => {
        if (!imageUrl.trim() || !watermarkText.trim()) {
            setError('Please provide both image URL and watermark text');
            return;
        }

        setLoading(true);
        setError(null);
        setWatermarkedImageUrl('');

        try {
            // Map UI position format to service expected format
            const positionMap: Record<string, 'topleft' | 'topright' | 'bottomleft' | 'bottomright' | 'center'> = {
                'top-left': 'topleft',
                'top-right': 'topright',
                'bottom-left': 'bottomleft',
                'bottom-right': 'bottomright',
                'center': 'center',
            };
            const mappedPosition = positionMap[position] || 'bottomright';
            const response = await contentProtectionService.applyImageWatermark(imageUrl, watermarkText, opacity / 100, mappedPosition);
            setWatermarkedImageUrl(response.watermarked_image_url);
            setSuccess('Image watermark applied successfully!');
        } catch (err: any) {
            setError(err.message || 'Failed to apply watermark');
        } finally {
            setLoading(false);
        }
    }, []);

    const copyToClipboard = useCallback((text: string) => {
        navigator.clipboard.writeText(text);
        setSuccess('Copied to clipboard!');
        setTimeout(() => setSuccess(null), 2000);
    }, []);

    return {
        loading,
        error,
        success,
        clearMessages,
        scanResults,
        scanPlatforms,
        setScanPlatforms,
        handleScanForTheft,
        watermarkedText,
        handleApplyTextWatermark,
        watermarkedImageUrl,
        handleApplyImageWatermark,
        copyToClipboard,
    };
};
