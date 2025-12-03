import React, { useState } from 'react';
import { Box, Tabs, Tab, Paper, Alert } from '@mui/material';
import { useContentProtection } from '@features/protection/hooks';
import TheftDetection from './watermark/TheftDetection';
import TextWatermark from './watermark/TextWatermark';
import ImageWatermark from './watermark/ImageWatermark';

interface Props {
    channelId?: string | null;
}

const ContentProtectionPanel: React.FC<Props> = ({ channelId }) => {
    const cp = useContentProtection();
    const [tab, setTab] = useState(0);

    // UI-local state for text watermark
    const [textToWatermark, setTextToWatermark] = useState('');
    const [watermarkType, setWatermarkType] = useState<'invisible' | 'visible'>('invisible');
    const [watermarkPosition, setWatermarkPosition] = useState<'top' | 'center' | 'bottom'>('center');

    // UI-local state for image watermark
    const [imageUrl, setImageUrl] = useState('');
    const [watermarkText, setWatermarkText] = useState('');
    const [opacity, setOpacity] = useState(50);
    const [imagePosition, setImagePosition] = useState<'top-left' | 'top-right' | 'center' | 'bottom-left' | 'bottom-right'>('center');

    const handleChangeTab = (_: any, newVal: number) => setTab(newVal);

    const handleDownload = (url?: string) => {
        if (!url) return;
        window.open(url, '_blank');
    };

    // Show info message if scanning for theft without channel
    const showChannelWarning = tab === 0 && !channelId;

    return (
        <Paper elevation={1} sx={{ p: 2 }}>
            {cp.error && <Alert severity="error" sx={{ mb: 2 }}>{cp.error}</Alert>}
            {cp.success && <Alert severity="success" sx={{ mb: 2 }}>{cp.success}</Alert>}
            {showChannelWarning && (
                <Alert severity="info" sx={{ mb: 2 }}>
                    Please select a channel to scan for content theft
                </Alert>
            )}

            <Tabs value={tab} onChange={handleChangeTab} sx={{ mb: 2 }}>
                <Tab label="Theft detection" />
                <Tab label="Text watermark" />
                <Tab label="Image watermark" />
            </Tabs>

            <Box>
                {tab === 0 && (
                    <TheftDetection
                        channelId={channelId || undefined}
                        loading={cp.loading}
                        scanResults={cp.scanResults}
                        scanPlatforms={cp.scanPlatforms}
                        setScanPlatforms={cp.setScanPlatforms}
                        onScan={() => cp.handleScanForTheft(channelId || undefined)}
                    />
                )}

                {tab === 1 && (
                    <TextWatermark
                        loading={cp.loading}
                        textToWatermark={textToWatermark}
                        setTextToWatermark={setTextToWatermark}
                        watermarkType={watermarkType}
                        setWatermarkType={setWatermarkType}
                        watermarkPosition={watermarkPosition}
                        setWatermarkPosition={setWatermarkPosition}
                        watermarkedText={cp.watermarkedText}
                        onApply={async () => await cp.handleApplyTextWatermark(textToWatermark, watermarkType, watermarkPosition)}
                        onCopy={cp.copyToClipboard}
                    />
                )}

                {tab === 2 && (
                    <ImageWatermark
                        loading={cp.loading}
                        imageUrl={imageUrl}
                        setImageUrl={setImageUrl}
                        watermarkText={watermarkText}
                        setWatermarkText={setWatermarkText}
                        opacity={opacity}
                        setOpacity={setOpacity}
                        position={imagePosition}
                        setPosition={setImagePosition}
                        resultImageUrl={cp.watermarkedImageUrl}
                        onApply={async () => await cp.handleApplyImageWatermark(imageUrl, watermarkText, opacity, imagePosition)}
                        onDownload={handleDownload}
                    />
                )}
            </Box>
        </Paper>
    );
};

export default ContentProtectionPanel;
