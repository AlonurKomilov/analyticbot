/**
 * Base Components - Common Reusable Components
 * 
 * Centralized export for all base components.
 * These components consolidate duplicated patterns across the application.
 */

export { default as BaseDataTable } from './BaseDataTable';
export type { BaseColumn, BasePaginationConfig, BaseDataTableProps } from './BaseDataTable';

export { default as BaseDialog } from './BaseDialog';
export type { DialogSize, DialogAction, BaseDialogProps } from './BaseDialog';

export { default as BaseForm } from './BaseForm';
export type { BaseFormProps } from './BaseForm';

export { default as BaseEmptyState } from './BaseEmptyState';
export type { BaseEmptyStateProps } from './BaseEmptyState';

export { default as BaseAlert } from './BaseAlert';
export type { AlertSeverity, AlertAction, BaseAlertProps } from './BaseAlert';
