import React from 'react';
import {
    TablePagination
} from '@mui/material';
import { PAGE_SIZE_OPTIONS } from '../utils/tableUtils';

/**
 * TablePaginationControls Component
 * Renders pagination controls with page size selection
 */
const TablePaginationControls = ({
    totalItems,
    page,
    pageSize,
    onPageChange,
    onPageSizeChange,
    enablePagination = true
}) => {
    if (!enablePagination) {
        return null;
    }

    const handleChangePage = (event, newPage) => {
        onPageChange(newPage);
    };

    const handleChangeRowsPerPage = (event) => {
        const newPageSize = parseInt(event.target.value, 10);
        onPageSizeChange(newPageSize);
        onPageChange(0); // Reset to first page
    };

    return (
        <TablePagination
            component="div"
            count={totalItems}
            page={page}
            onPageChange={handleChangePage}
            rowsPerPage={pageSize}
            onRowsPerPageChange={handleChangeRowsPerPage}
            rowsPerPageOptions={PAGE_SIZE_OPTIONS}
            labelRowsPerPage="Rows per page:"
            labelDisplayedRows={({ from, to, count }) =>
                `${from}-${to} of ${count !== -1 ? count : `more than ${to}`}`
            }
        />
    );
};

export default TablePaginationControls;
