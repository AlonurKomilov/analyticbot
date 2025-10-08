import React from 'react';
import {
    Typography,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Paper,
    Chip
} from '@mui/material';
import { formatDate } from '../utils/adminUtils';

/**
 * AuditLogsTab Component
 * Administrative audit trail with action logs
 */
const AuditLogsTab = ({ auditLogs = [] }) => {
    return (
        <>
            <Typography variant="h6" gutterBottom>Administrative Audit Trail</Typography>
            <TableContainer component={Paper}>
                <Table>
                    <TableHead>
                        <TableRow>
                            <TableCell>Timestamp</TableCell>
                            <TableCell>Admin</TableCell>
                            <TableCell>Action</TableCell>
                            <TableCell>Resource</TableCell>
                            <TableCell>IP Address</TableCell>
                            <TableCell>Status</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {auditLogs.map((log) => (
                            <TableRow key={log.id}>
                                <TableCell sx={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>
                                    {formatDate(log.created_at)}
                                </TableCell>
                                <TableCell>{log.admin_username}</TableCell>
                                <TableCell>{log.action}</TableCell>
                                <TableCell>{log.resource_type}</TableCell>
                                <TableCell sx={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>
                                    {log.ip_address}
                                </TableCell>
                                <TableCell>
                                    <Chip
                                        label={log.success ? 'Success' : 'Failed'}
                                        color={log.success ? 'success' : 'error'}
                                        size="small"
                                    />
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </TableContainer>
        </>
    );
};

export default AuditLogsTab;
