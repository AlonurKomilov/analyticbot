/**
 * BestTimeRecommender - Refactored modular components
 * 
 * This is the new, refactored BestTimeRecommender with separated concerns:
 * - TimeFrameFilters: Time frame and content type filter controls
 * - BestTimeCards: Recommended time cards with confidence scores
 * - HeatmapVisualization: 24-hour activity heatmap
 * - AIInsightsPanel: AI-powered insights and recommendations
 * - RecommenderFooter: Status and metadata display
 * - useRecommenderLogic: Business logic and state management
 * - timeUtils: Time formatting and calculation utilities
 * 
 * Mock data is handled by existing __mocks__/analytics/bestTime.js
 */

export { default } from './BestTimeRecommender.jsx';

// Export individual components for reuse
export { default as TimeFrameFilters } from './components/TimeFrameFilters.jsx';
export { default as BestTimeCards } from './components/BestTimeCards.jsx';
export { default as HeatmapVisualization } from './components/HeatmapVisualization.jsx';
export { default as AIInsightsPanel } from './components/AIInsightsPanel.jsx';
export { default as RecommenderFooter } from './components/RecommenderFooter.jsx';

// Export hooks and utilities
export { useRecommenderLogic } from './hooks/useRecommenderLogic.js';
export * from './utils/timeUtils.js';