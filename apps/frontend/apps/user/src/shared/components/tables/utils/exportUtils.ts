/**
 * Export utility functions for EnhancedDataTable
 * Handles CSV, Excel, and PDF export functionality
 */

type ExportFunction = (headers: string[], rows: (string | number)[][], filename: string, title?: string) => void;

/**
 * Export data to CSV format
 */
export const exportToCsv: ExportFunction = (headers, rows, filename) => {
    const csvContent = [headers, ...rows]
        .map(row => row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(','))
        .join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `${filename}.csv`;
    link.click();
};

/**
 * Export data to Excel format
 */
export const exportToExcel: ExportFunction = (headers, rows, filename) => {
    // Implementation would require a library like xlsx
    console.log('Excel export would be implemented with xlsx library');
    exportToCsv(headers, rows, filename); // Fallback to CSV for now
};

/**
 * Export data to PDF format
 */
export const exportToPdf: ExportFunction = (headers, rows, filename, title) => {
    // Implementation would require a library like jsPDF
    console.log('PDF export would be implemented with jsPDF library', title);
    exportToCsv(headers, rows, filename); // Fallback to CSV for now
};

// Export formats configuration
export const EXPORT_FORMATS = [
    {
        key: 'csv',
        label: 'CSV File',
        mimeType: 'text/csv',
        exportFn: exportToCsv
    },
    {
        key: 'excel',
        label: 'Excel File',
        mimeType: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        exportFn: exportToExcel
    },
    {
        key: 'pdf',
        label: 'PDF File',
        mimeType: 'application/pdf',
        exportFn: exportToPdf
    }
];
