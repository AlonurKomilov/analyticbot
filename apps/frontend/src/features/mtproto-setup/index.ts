/**
 * MTProto Setup Feature - Main Export
 */

export { MTProtoSetupPage } from './components/MTProtoSetupPage';
export { MTProtoStatusCard } from './components/MTProtoStatusCard';
export { MTProtoCredentialsForm } from './components/MTProtoCredentialsForm';
export { MTProtoVerificationForm } from './components/MTProtoVerificationForm';
export * from './hooks';
export * from './types';
export * from './api';

// Default export for lazy loading
export { MTProtoSetupPage as default } from './components/MTProtoSetupPage';
