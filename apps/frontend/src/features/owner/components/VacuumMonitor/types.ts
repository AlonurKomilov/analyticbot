/**
 * VacuumMonitor Types
 * Shared type definitions for vacuum monitoring components
 */

export interface TableHealth {
  schema: string;
  table_name: string;
  live_tuples: number;
  dead_tuples: number;
  dead_percent: number;
  modifications_since_analyze: number;
  total_size: string;
  total_size_bytes: number;
  last_vacuum: string | null;
  last_autovacuum: string | null;
  last_analyze: string | null;
  last_autoanalyze: string | null;
  vacuum_count: number;
  autovacuum_count: number;
  priority?: string;
}

export interface VacuumSummary {
  database_size: string;
  total_tables: number;
  total_live_tuples: number;
  total_dead_tuples: number;
  overall_dead_percent: number;
}

export interface AutovacuumConfig {
  global_settings: Record<string, { value: string; unit: string; description: string }>;
  table_specific_settings: Array<{
    schema: string;
    table_name: string;
    vacuum_threshold: string;
    vacuum_scale_factor: string;
    analyze_threshold: string;
    analyze_scale_factor: string;
    vacuum_cost_delay: string;
  }>;
}

export interface VacuumDialogState {
  open: boolean;
  tableName: string;
  full: boolean;
}
