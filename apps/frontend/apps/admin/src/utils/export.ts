/**
 * Export Utilities
 * 
 * Utilities for exporting data to various formats (CSV, JSON, etc.)
 */

/**
 * Convert array of objects to CSV string
 */
export function arrayToCSV<T extends Record<string, unknown>>(
  data: T[],
  columns?: { key: keyof T; header: string }[]
): string {
  if (data.length === 0) return '';

  // If columns not provided, use all keys from first object
  const cols = columns || Object.keys(data[0]).map((key) => ({
    key: key as keyof T,
    header: String(key),
  }));

  // Create header row
  const headerRow = cols.map((col) => escapeCSVValue(col.header)).join(',');

  // Create data rows
  const dataRows = data.map((row) =>
    cols
      .map((col) => {
        const value = row[col.key];
        return escapeCSVValue(formatValue(value));
      })
      .join(',')
  );

  return [headerRow, ...dataRows].join('\n');
}

/**
 * Escape a value for CSV format
 */
function escapeCSVValue(value: string): string {
  // If value contains comma, newline, or quote, wrap in quotes
  if (value.includes(',') || value.includes('\n') || value.includes('"')) {
    return `"${value.replace(/"/g, '""')}"`;
  }
  return value;
}

/**
 * Format a value for CSV export
 */
function formatValue(value: unknown): string {
  if (value === null || value === undefined) return '';
  if (typeof value === 'boolean') return value ? 'Yes' : 'No';
  if (value instanceof Date) return value.toISOString();
  if (typeof value === 'object') return JSON.stringify(value);
  return String(value);
}

/**
 * Download data as CSV file
 */
export function downloadCSV(csvContent: string, filename: string): void {
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  
  link.setAttribute('href', url);
  link.setAttribute('download', `${filename}.csv`);
  link.style.visibility = 'hidden';
  
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  
  URL.revokeObjectURL(url);
}

/**
 * Download data as JSON file
 */
export function downloadJSON<T>(data: T, filename: string): void {
  const jsonContent = JSON.stringify(data, null, 2);
  const blob = new Blob([jsonContent], { type: 'application/json;charset=utf-8;' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  
  link.setAttribute('href', url);
  link.setAttribute('download', `${filename}.json`);
  link.style.visibility = 'hidden';
  
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  
  URL.revokeObjectURL(url);
}

/**
 * Export table data with automatic formatting
 */
export function exportTableData<T extends Record<string, unknown>>(
  data: T[],
  filename: string,
  format: 'csv' | 'json' = 'csv',
  columns?: { key: keyof T; header: string }[]
): void {
  if (format === 'csv') {
    const csv = arrayToCSV(data, columns);
    downloadCSV(csv, filename);
  } else {
    downloadJSON(data, filename);
  }
}

/**
 * Generate filename with timestamp
 */
export function generateExportFilename(prefix: string): string {
  const date = new Date();
  const timestamp = date.toISOString().split('T')[0]; // YYYY-MM-DD
  return `${prefix}_${timestamp}`;
}

export default {
  arrayToCSV,
  downloadCSV,
  downloadJSON,
  exportTableData,
  generateExportFilename,
};
