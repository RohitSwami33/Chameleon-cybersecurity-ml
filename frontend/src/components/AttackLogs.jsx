import React, { useState, useMemo } from 'react';
import {
    Paper, Typography, Box, Table, TableBody, TableCell, TableContainer,
    TableHead, TableRow, TablePagination, Chip, IconButton, Tooltip, TextField, Button
} from '@mui/material';
import { motion, AnimatePresence } from 'framer-motion';
import SearchIcon from '@mui/icons-material/Search';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import DescriptionIcon from '@mui/icons-material/Description';
import { getAttackTypeColor, truncateText } from '../utils/helpers';
import { toast } from 'react-toastify';

/**
 * AttackLogs — scrollable attack log table
 * @see Section 3 — AttackLogs Rules
 * New rows animate in with Framer Motion, copy-to-JSON, pill badges
 */
const AttackLogs = ({ logs = [], onViewDetails, onGenerateReport }) => {
    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(10);
    const [search, setSearch] = useState('');

    const filteredLogs = useMemo(() => {
        if (!search) return logs;
        const term = search.toLowerCase();
        return logs.filter(log =>
            log.ip_address?.toLowerCase().includes(term) ||
            log.classification?.attack_type?.toLowerCase().includes(term) ||
            log.request_data?.path?.toLowerCase().includes(term)
        );
    }, [logs, search]);

    const paginatedLogs = filteredLogs.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage);

    const copyLogAsJson = (log) => {
        navigator.clipboard.writeText(JSON.stringify(log, null, 2));
        toast.success('Log copied to clipboard');
    };

    return (
        <Paper
            sx={{
                backgroundColor: 'rgba(10, 15, 30, 0.85)',
                backdropFilter: 'blur(12px)',
                border: '1px solid rgba(0, 212, 255, 0.08)',
                borderRadius: '12px',
                overflow: 'hidden',
            }}
        >
            {/* Header */}
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', p: '20px', pb: 1 }}>
                <Typography variant="h6" sx={{ fontWeight: 600, fontSize: '0.95rem', color: '#e8f4fd' }}>
                    Attack Logs
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                    <TextField
                        placeholder="Search logs…"
                        size="small"
                        value={search}
                        onChange={(e) => {
                            setSearch(e.target.value);
                            setPage(0);
                        }}
                        InputProps={{
                            startAdornment: <SearchIcon sx={{ color: '#3d5a7a', mr: 0.5, fontSize: 18 }} />,
                        }}
                        sx={{
                            width: 200,
                            '& .MuiOutlinedInput-root': {
                                height: 32,
                                fontSize: '0.8rem',
                                fontFamily: '"DM Sans", sans-serif',
                            },
                        }}
                    />
                </Box>
            </Box>

            <TableContainer sx={{ maxHeight: 480 }}>
                <Table stickyHeader size="small">
                    <TableHead>
                        <TableRow>
                            <TableCell sx={{ py: 1 }}>Timestamp</TableCell>
                            <TableCell sx={{ py: 1 }}>IP Address</TableCell>
                            <TableCell sx={{ py: 1 }}>Attack Type</TableCell>
                            <TableCell sx={{ py: 1 }}>Confidence</TableCell>
                            <TableCell sx={{ py: 1 }}>Path</TableCell>
                            <TableCell sx={{ py: 1 }}>Actions</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        <AnimatePresence>
                            {paginatedLogs.map((log, index) => {
                                const attackType = log.classification?.attack_type || 'UNKNOWN';
                                const confidence = log.classification?.confidence;
                                const isMalicious = attackType !== 'BENIGN';
                                const typeColor = getAttackTypeColor(attackType);

                                return (
                                    <motion.tr
                                        key={log._id || `${log.ip_address}-${log.timestamp}-${index}`}
                                        initial={{ opacity: 0, x: -8 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        exit={{ opacity: 0 }}
                                        transition={{ duration: 0.2, delay: index * 0.02 }}
                                        style={{ display: 'table-row' }}
                                    >
                                        <TableCell sx={{ py: 1.2 }}>
                                            <Typography variant="caption" sx={{
                                                fontFamily: '"IBM Plex Mono", monospace',
                                                fontSize: '0.7rem',
                                                color: '#7a9bbf',
                                            }}>
                                                {log.timestamp ? new Date(log.timestamp).toLocaleString() : 'N/A'}
                                            </Typography>
                                        </TableCell>
                                        <TableCell sx={{ py: 1.2 }}>
                                            <Typography variant="body2" sx={{
                                                fontFamily: '"IBM Plex Mono", monospace',
                                                fontSize: '0.8rem',
                                                fontWeight: 600,
                                                color: '#e8f4fd',
                                            }}>
                                                {log.ip_address || 'Unknown'}
                                            </Typography>
                                        </TableCell>
                                        <TableCell sx={{ py: 1.2 }}>
                                            <Chip
                                                label={attackType}
                                                size="small"
                                                sx={{
                                                    backgroundColor: `${typeColor}18`,
                                                    color: typeColor,
                                                    fontWeight: 700,
                                                    fontSize: '0.65rem',
                                                    height: 22,
                                                    border: `1px solid ${typeColor}30`,
                                                }}
                                            />
                                        </TableCell>
                                        <TableCell sx={{ py: 1.2 }}>
                                            {confidence !== undefined ? (
                                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                                    <Box sx={{
                                                        width: 40, height: 3, borderRadius: 2,
                                                        background: `linear-gradient(90deg, ${typeColor}, ${typeColor}66)`,
                                                        overflow: 'hidden',
                                                    }}>
                                                        <Box sx={{
                                                            width: `${(confidence * 100)}%`,
                                                            height: '100%',
                                                            backgroundColor: typeColor,
                                                            borderRadius: 2,
                                                        }} />
                                                    </Box>
                                                    <Typography variant="caption" sx={{
                                                        color: '#7a9bbf',
                                                        fontFamily: '"IBM Plex Mono", monospace',
                                                        fontSize: '0.7rem',
                                                    }}>
                                                        {(confidence * 100).toFixed(0)}%
                                                    </Typography>
                                                </Box>
                                            ) : '-'}
                                        </TableCell>
                                        <TableCell sx={{ py: 1.2 }}>
                                            <Typography variant="caption" sx={{ color: '#3d5a7a', fontSize: '0.7rem', fontFamily: '"IBM Plex Mono", monospace' }}>
                                                {truncateText(log.request_data?.path || '-', 30)}
                                            </Typography>
                                        </TableCell>
                                        <TableCell sx={{ py: 1.2 }}>
                                            <Box sx={{ display: 'flex', gap: 0.5 }}>
                                                <Tooltip title="Copy as JSON">
                                                    <IconButton size="small" onClick={() => copyLogAsJson(log)} sx={{ color: '#7a9bbf', p: 0.3 }}>
                                                        <ContentCopyIcon sx={{ fontSize: 14 }} />
                                                    </IconButton>
                                                </Tooltip>
                                                {onGenerateReport && isMalicious && (
                                                    <Tooltip title="Generate Report">
                                                        <IconButton size="small" onClick={() => onGenerateReport(log.ip_address)} sx={{ color: '#00d4ff', p: 0.3 }}>
                                                            <DescriptionIcon sx={{ fontSize: 14 }} />
                                                        </IconButton>
                                                    </Tooltip>
                                                )}
                                            </Box>
                                        </TableCell>
                                    </motion.tr>
                                );
                            })}
                        </AnimatePresence>
                    </TableBody>
                </Table>
            </TableContainer>

            <TablePagination
                component="div"
                count={filteredLogs.length}
                page={page}
                onPageChange={(e, newPage) => setPage(newPage)}
                rowsPerPage={rowsPerPage}
                onRowsPerPageChange={(e) => {
                    setRowsPerPage(parseInt(e.target.value, 10));
                    setPage(0);
                }}
                rowsPerPageOptions={[10, 25, 50]}
                sx={{
                    borderTop: '1px solid rgba(0, 212, 255, 0.06)',
                    '& .MuiTablePagination-toolbar': { minHeight: 44 },
                    '& .MuiTypography-root': { fontSize: '0.75rem', color: '#7a9bbf' },
                }}
            />
        </Paper>
    );
};

export default AttackLogs;
