import React, { useState, useMemo } from 'react';
import {
    Paper, Typography, Box, Table, TableBody, TableCell, TableContainer,
    TableHead, TableRow, TablePagination, Chip, TextField, Tooltip,
    IconButton, Badge, LinearProgress
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import RefreshIcon from '@mui/icons-material/Refresh';
import ShieldIcon from '@mui/icons-material/Shield';
import BlockIcon from '@mui/icons-material/Block';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { toast } from 'react-toastify';

/**
 * TelemetryTable — 2D Security Telemetry Log
 *
 * Columns: Timestamp | Source IP | Command/Payload | BiLSTM Score | MLX Verdict | Status
 *
 * Accepts `logs` from /api/dashboard/logs (or /api/honeypot/log).
 * No 3D elements, no heavy WebGL — pure React + MUI data table.
 */

const HEADER_STYLE = {
    background: 'rgba(0,212,255,0.06)',
    color: '#7ec8e3',
    fontFamily: '"IBM Plex Mono", monospace',
    fontSize: '0.7rem',
    fontWeight: 700,
    letterSpacing: '0.08em',
    textTransform: 'uppercase',
    borderBottom: '1px solid rgba(0,212,255,0.12)',
    py: 1.5,
    whiteSpace: 'nowrap',
};

const MONO = { fontFamily: '"IBM Plex Mono", monospace' };

/* ── helpers ─────────────────────────────────────────────── */
function fmtTimestamp(ts) {
    if (!ts) return '—';
    try {
        return new Date(ts).toLocaleString('en-GB', {
            dateStyle: 'short', timeStyle: 'medium'
        });
    } catch { return ts; }
}

function BiLSTMBar({ score }) {
    if (score === undefined || score === null) return <Typography sx={{ ...MONO, fontSize: '0.7rem', color: '#3d5a7a' }}>—</Typography>;
    const pct = Math.round(score * 100);
    const color = pct >= 75 ? '#ff3d71' : pct >= 40 ? '#ffa500' : '#00e676';
    return (
        <Box sx={{ minWidth: 80 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.3 }}>
                <Typography sx={{ ...MONO, fontSize: '0.68rem', color }}>{pct}%</Typography>
            </Box>
            <LinearProgress
                variant="determinate"
                value={pct}
                sx={{
                    height: 4,
                    borderRadius: 2,
                    backgroundColor: 'rgba(255,255,255,0.06)',
                    '& .MuiLinearProgress-bar': { backgroundColor: color, borderRadius: 2 }
                }}
            />
        </Box>
    );
}

function MlxVerdictChip({ verdict }) {
    if (!verdict) return <Typography sx={{ ...MONO, fontSize: '0.7rem', color: '#3d5a7a' }}>—</Typography>;
    const isBlock = verdict?.toUpperCase() === 'BLOCK';
    return (
        <Chip
            icon={isBlock
                ? <BlockIcon sx={{ fontSize: '12px !important', color: '#ff3d71 !important' }} />
                : <CheckCircleIcon sx={{ fontSize: '12px !important', color: '#00e676 !important' }} />}
            label={isBlock ? 'BLOCK' : 'ALLOW'}
            size="small"
            sx={{
                height: 22,
                fontSize: '0.65rem',
                fontWeight: 800,
                ...MONO,
                backgroundColor: isBlock ? 'rgba(255,61,113,0.1)' : 'rgba(0,230,118,0.1)',
                color: isBlock ? '#ff3d71' : '#00e676',
                border: `1px solid ${isBlock ? 'rgba(255,61,113,0.25)' : 'rgba(0,230,118,0.25)'}`,
                '& .MuiChip-icon': { ml: 0.5 }
            }}
        />
    );
}

function StatusChip({ status }) {
    if (!status) return <Typography sx={{ ...MONO, fontSize: '0.68rem', color: '#3d5a7a' }}>—</Typography>;
    const isDeception = status?.includes('DECEPTION');
    return (
        <Chip
            label={isDeception ? 'DECEPTION' : 'PASSED'}
            size="small"
            sx={{
                height: 20,
                fontSize: '0.6rem',
                fontWeight: 700,
                ...MONO,
                backgroundColor: isDeception ? 'rgba(255,165,0,0.1)' : 'rgba(0,212,255,0.08)',
                color: isDeception ? '#ffa500' : '#00d4ff',
                border: `1px solid ${isDeception ? 'rgba(255,165,0,0.2)' : 'rgba(0,212,255,0.15)'}`,
            }}
        />
    );
}

/* ── main component ──────────────────────────────────────── */
const TelemetryTable = ({ logs = [], onRefresh, loading = false }) => {
    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(15);
    const [search, setSearch] = useState('');

    const filtered = useMemo(() => {
        if (!search.trim()) return logs;
        const term = search.toLowerCase();
        return logs.filter(log =>
            log.ip_address?.toLowerCase().includes(term) ||
            log.request_data?.payload?.toLowerCase().includes(term) ||
            log.request_data?.path?.toLowerCase().includes(term) ||
            log.classification?.attack_type?.toLowerCase().includes(term) ||
            log.classification?.mlx_verdict?.toLowerCase().includes(term) ||
            log.routing_decision?.toLowerCase().includes(term)
        );
    }, [logs, search]);

    const paginated = filtered.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage);

    const handleCopy = (log) => {
        navigator.clipboard.writeText(JSON.stringify(log, null, 2));
        toast.success('Log entry copied!', { autoClose: 1500 });
    };

    /* Helper to derive the correct payload text from any log shape */
    const getPayload = (log) => {
        return log.request_data?.payload
            || log.request_data?.path
            || log.request_data?.body
            || log.payload
            || '—';
    };

    /* Helper to derive MLX verdict */
    const getMlxVerdict = (log) => {
        return log.classification?.mlx_verdict
            || log.classification?.verdict
            || (log.classification?.is_malicious === true ? 'BLOCK' : log.classification?.is_malicious === false ? 'ALLOW' : null);
    };

    /* Helper to derive BiLSTM anomaly score */
    const getBiLSTMScore = (log) => {
        return log.classification?.bilstm_score
            ?? log.classification?.anomaly_score
            ?? log.classification?.confidence;
    };

    /* Helper to normalise routing/status */
    const getStatus = (log) => {
        return log.routing_decision
            || log.status
            || (log.classification?.attack_type !== 'BENIGN' ? 'ROUTED_TO_DECEPTION' : 'PASSED');
    };

    return (
        <Paper
            id="telemetry-table"
            sx={{
                backgroundColor: 'rgba(6, 10, 24, 0.92)',
                backdropFilter: 'blur(16px)',
                border: '1px solid rgba(0, 212, 255, 0.1)',
                borderRadius: '14px',
                overflow: 'hidden',
            }}
        >
            {/* ── Header bar ── */}
            <Box sx={{
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                px: 3, py: 2, borderBottom: '1px solid rgba(0,212,255,0.08)'
            }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                    <ShieldIcon sx={{ color: '#00d4ff', fontSize: 20 }} />
                    <Typography sx={{
                        fontWeight: 700, fontSize: '0.95rem', color: '#e8f4fd',
                        fontFamily: '"DM Sans", sans-serif', letterSpacing: '-0.01em'
                    }}>
                        Live Telemetry Log
                    </Typography>
                    <Badge
                        badgeContent={filtered.length}
                        sx={{
                            '& .MuiBadge-badge': {
                                backgroundColor: '#00d4ff22',
                                color: '#00d4ff',
                                fontWeight: 700,
                                fontSize: '0.65rem',
                                border: '1px solid rgba(0,212,255,0.3)',
                            }
                        }}
                    />
                </Box>
                <Box sx={{ display: 'flex', gap: 1.5, alignItems: 'center' }}>
                    <TextField
                        id="telemetry-search"
                        placeholder="Filter by IP, payload, verdict…"
                        size="small"
                        value={search}
                        onChange={(e) => { setSearch(e.target.value); setPage(0); }}
                        InputProps={{
                            startAdornment: <SearchIcon sx={{ color: '#3d5a7a', mr: 0.5, fontSize: 16 }} />,
                        }}
                        sx={{
                            width: 260,
                            '& .MuiOutlinedInput-root': {
                                height: 34, fontSize: '0.78rem', ...MONO,
                                color: '#e8f4fd',
                                '& fieldset': { borderColor: 'rgba(0,212,255,0.15)' },
                                '&:hover fieldset': { borderColor: 'rgba(0,212,255,0.3)' },
                                '&.Mui-focused fieldset': { borderColor: '#00d4ff' },
                            },
                        }}
                    />
                    {onRefresh && (
                        <Tooltip title="Refresh">
                            <IconButton onClick={onRefresh} size="small" sx={{ color: '#00d4ff', border: '1px solid rgba(0,212,255,0.2)', borderRadius: '8px', p: 0.7 }}>
                                <RefreshIcon sx={{ fontSize: 16 }} />
                            </IconButton>
                        </Tooltip>
                    )}
                </Box>
            </Box>

            {/* ── Loading bar ── */}
            {loading && <LinearProgress sx={{ '& .MuiLinearProgress-bar': { backgroundColor: '#00d4ff' } }} />}

            {/* ── Table ── */}
            <TableContainer sx={{ maxHeight: 520 }}>
                <Table stickyHeader size="small">
                    <TableHead>
                        <TableRow>
                            <TableCell sx={HEADER_STYLE}>Timestamp</TableCell>
                            <TableCell sx={HEADER_STYLE}>Source IP</TableCell>
                            <TableCell sx={{ ...HEADER_STYLE, minWidth: 160 }}>Command / Payload</TableCell>
                            <TableCell sx={{ ...HEADER_STYLE, minWidth: 100 }}>BiLSTM Score</TableCell>
                            <TableCell sx={HEADER_STYLE}>MLX Verdict</TableCell>
                            <TableCell sx={HEADER_STYLE}>Status</TableCell>
                            <TableCell sx={{ ...HEADER_STYLE, width: 40 }} />
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {paginated.length === 0 ? (
                            <TableRow>
                                <TableCell colSpan={7} sx={{ textAlign: 'center', py: 6 }}>
                                    <Typography sx={{ color: '#3d5a7a', ...MONO, fontSize: '0.8rem' }}>
                                        {search ? 'No matching records' : 'Awaiting telemetry data…'}
                                    </Typography>
                                </TableCell>
                            </TableRow>
                        ) : paginated.map((log, i) => {
                            const payload = getPayload(log);
                            const mlxVerdict = getMlxVerdict(log);
                            const bilstmScore = getBiLSTMScore(log);
                            const status = getStatus(log);
                            const isDeception = status?.includes('DECEPTION');

                            return (
                                <TableRow
                                    key={log._id || log.id || `${log.ip_address}-${log.timestamp}-${i}`}
                                    sx={{
                                        borderLeft: isDeception ? '3px solid #ffa500' : '3px solid transparent',
                                        '&:hover': { backgroundColor: 'rgba(0,212,255,0.04)' },
                                        transition: 'background-color 0.15s',
                                    }}
                                >
                                    {/* Timestamp */}
                                    <TableCell sx={{ py: 1.4, borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                                        <Typography sx={{ ...MONO, fontSize: '0.68rem', color: '#5a7a9a', whiteSpace: 'nowrap' }}>
                                            {fmtTimestamp(log.timestamp)}
                                        </Typography>
                                    </TableCell>

                                    {/* Source IP */}
                                    <TableCell sx={{ py: 1.4, borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                                        <Typography sx={{ ...MONO, fontSize: '0.78rem', fontWeight: 700, color: '#e8f4fd' }}>
                                            {log.ip_address || '—'}
                                        </Typography>
                                    </TableCell>

                                    {/* Command / Payload */}
                                    <TableCell sx={{ py: 1.4, borderBottom: '1px solid rgba(255,255,255,0.04)', maxWidth: 220 }}>
                                        <Tooltip title={payload} placement="top">
                                            <Typography sx={{
                                                ...MONO, fontSize: '0.72rem', color: '#a0b8d0',
                                                whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis'
                                            }}>
                                                {payload}
                                            </Typography>
                                        </Tooltip>
                                    </TableCell>

                                    {/* BiLSTM Score */}
                                    <TableCell sx={{ py: 1.4, borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                                        <BiLSTMBar score={bilstmScore} />
                                    </TableCell>

                                    {/* MLX Verdict */}
                                    <TableCell sx={{ py: 1.4, borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                                        <MlxVerdictChip verdict={mlxVerdict} />
                                    </TableCell>

                                    {/* Status */}
                                    <TableCell sx={{ py: 1.4, borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                                        <StatusChip status={status} />
                                    </TableCell>

                                    {/* Copy action */}
                                    <TableCell sx={{ py: 1.4, borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                                        <Tooltip title="Copy log as JSON">
                                            <IconButton size="small" onClick={() => handleCopy(log)} sx={{ color: '#3d5a7a', p: 0.4, '&:hover': { color: '#00d4ff' } }}>
                                                <ContentCopyIcon sx={{ fontSize: 13 }} />
                                            </IconButton>
                                        </Tooltip>
                                    </TableCell>
                                </TableRow>
                            );
                        })}
                    </TableBody>
                </Table>
            </TableContainer>

            {/* ── Pagination ── */}
            <TablePagination
                component="div"
                count={filtered.length}
                page={page}
                onPageChange={(_, p) => setPage(p)}
                rowsPerPage={rowsPerPage}
                onRowsPerPageChange={(e) => { setRowsPerPage(parseInt(e.target.value, 10)); setPage(0); }}
                rowsPerPageOptions={[10, 15, 25, 50]}
                sx={{
                    borderTop: '1px solid rgba(0,212,255,0.06)',
                    color: '#5a7a9a',
                    '& .MuiTablePagination-toolbar': { minHeight: 44, px: 2 },
                    '& .MuiTypography-root': { fontSize: '0.73rem', ...MONO },
                    '& .MuiSvgIcon-root': { color: '#5a7a9a' },
                }}
            />
        </Paper>
    );
};

export default TelemetryTable;
