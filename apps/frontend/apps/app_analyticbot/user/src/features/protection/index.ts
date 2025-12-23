/**
 * Content Protection Feature Module
 * Barrel export for protection features
 */

// Main component
export { default as ContentProtectionPanel } from './ContentProtectionPanel';

// Watermark sub-components
export { default as TheftDetection } from './watermark/TheftDetection';
export { default as TextWatermark } from './watermark/TextWatermark';
export { default as ImageWatermark } from './watermark/ImageWatermark';
