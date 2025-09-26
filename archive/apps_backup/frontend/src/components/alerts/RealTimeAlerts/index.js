// RealTimeAlerts Component Exports
// Barrel file for all extracted real-time alert system components

export { default as RealTimeAlertsSystem } from './RealTimeAlertsSystem.jsx';
export { default as AlertsList } from './AlertsList.jsx';
export { default as RuleManager } from './RuleManager.jsx';
export { default as NewRuleDialog } from './NewRuleDialog.jsx';
export { default as NotificationEngine } from './NotificationEngine.jsx';

// Re-export the main component as default
export { default } from './RealTimeAlertsSystem.jsx';