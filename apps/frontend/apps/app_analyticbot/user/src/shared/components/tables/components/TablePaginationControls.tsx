import React from 'react';
import {
    TablePagination
} from '@mui/material';
import { PAGE_SIZE_OPTIONS } from '../utils/tableUtils';

interface TablePaginationControlsProps {
    totalItems: number;
    page: number;
    pageSize: number;
    onPageChange: (page: number) => void;
    onPageSizeChange: (pageSize: number) => void;
    enablePagination?: boolean;
}

/**
 * TablePaginationControls Component
 * Renders pagination controls with page size selection
 */
const TablePaginationControls: React.FC<TablePaginationControlsProps> = ({
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

    const handleChangePage = (_event: unknown, newPage: number) => {
        onPageChange(newPage);
    };

    const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
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
