/**
 * Export utility functions for EnhancedDataTable
 * Handles CSV, Excel, and PDF export functionality
 */

/**
 * Export data to CSV format
 * @param {Array} headers - Column headers
 * @param {Array} rows - Data rows
 * @param {string} filename - Export filename
 */
export const exportToCsv = (headers, rows, filename) => {
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
 * @param {Array} headers - Column headers
 * @param {Array} rows - Data rows
 * @param {string} filename - Export filename
 */
export const exportToExcel = (headers, rows, filename) => {
    // Implementation would require a library like xlsx
    console.log('Excel export would be implemented with xlsx library');
    exportToCsv(headers, rows, filename); // Fallback to CSV for now
};

/**
 * Export data to PDF format
 * @param {Array} headers - Column headers
 * @param {Array} rows - Data rows
 * @param {string} filename - Export filename
 * @param {string} title - Document title
 */
export const exportToPdf = (headers, rows, filename, title) => {
    // Implementation would require a library like jsPDF
    console.log('PDF export would be implemented with jsPDF library');
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