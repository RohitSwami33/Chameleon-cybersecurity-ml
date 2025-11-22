import React, { useState } from 'react';
import {
    Paper,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    TablePagination,
    Typography,
    Box,
    IconButton,
    Collapse,
    Chip,
    LinearProgress,
    Tooltip,
    Button,
    TextField,
    MenuItem,
    Select,
    InputLabel,
    FormControl
} from '@mui/material';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';
import VisibilityIcon from '@mui/icons-material/Visibility';
import FilterListIcon from '@mui/icons-material/FilterList';
import { formatTimestamp, getAttackTypeColor, getConfidenceLabel, truncateText } from '../utils/helpers';

const Row = ({ row, onViewDetails, onGenerateReport }) => {
    const [open, setOpen] = useState(false);

    return (
        <React.Fragment>
            <TableRow sx={{ '& > *': { borderBottom: 'unset' }, backgroundColor: open ? 'rgba(255, 255, 255, 0.05)' : 'inherit' }}>
                <TableCell>
                    <IconButton
                        aria-label="expand row"
                        size="small"
                        onClick={() => setOpen(!open)}
                    >
                        {open ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
                    </IconButton>
                </TableCell>
                <TableCell component="th" scope="row">
                    {formatTimestamp(row.timestamp)}
                </TableCell>
                <TableCell>{row.ip_address}</TableCell>
                <TableCell>
                    <Chip
                        label={row.classification?.attack_type || 'Unknown'}
                        size="small"
                        sx={{
                            backgroundColor: `${getAttackTypeColor(row.classification?.attack_type)}22`,
                            color: getAttackTypeColor(row.classification?.attack_type),
                            fontWeight: 600,
                            border: `1px solid ${getAttackTypeColor(row.classification?.attack_type)}`
                        }}
                    />
                </TableCell>
                <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Box sx={{ width: '100%', mr: 1 }}>
                            <LinearProgress
                                variant="determinate"
                                value={(row.classification?.confidence || 0) * 100}
                                color={(row.classification?.confidence || 0) > 0.8 ? "error" : (row.classification?.confidence || 0) > 0.5 ? "warning" : "success"}
                                sx={{ height: 6, borderRadius: 3 }}
                            />
                        </Box>
                        <Box sx={{ minWidth: 35 }}>
                            <Typography variant="body2" color="text.secondary">{Math.round((row.classification?.confidence || 0) * 100)}%</Typography>
                        </Box>
                    </Box>
                </TableCell>
                <TableCell align="right">
                    <Tooltip title="View Details">
                        <IconButton size="small" onClick={() => onViewDetails(row.id)}>
                            <VisibilityIcon fontSize="small" />
                        </IconButton>
                    </Tooltip>
                    <Tooltip title="Generate Report">
                        <IconButton size="small" onClick={() => onGenerateReport(row.ip_address)} color="primary">
                            <PictureAsPdfIcon fontSize="small" />
                        </IconButton>
                    </Tooltip>
                </TableCell>
            </TableRow>
            <TableRow>
                <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={6}>
                    <Collapse in={open} timeout="auto" unmountOnExit>
                        <Box sx={{ margin: 2 }}>
                            <Typography variant="h6" gutterBottom component="div" sx={{ fontSize: '0.9rem', fontWeight: 600 }}>
                                Attack Details
                            </Typography>
                            <Table size="small" aria-label="details">
                                <TableBody>
                                    <TableRow>
                                        <TableCell component="th" scope="row" sx={{ borderBottom: 'none', width: 150, color: 'text.secondary' }}>Raw Input:</TableCell>
                                        <TableCell sx={{ borderBottom: 'none', fontFamily: 'monospace' }}>{row.raw_input || row.input_text}</TableCell>
                                    </TableRow>
                                    <TableRow>
                                        <TableCell component="th" scope="row" sx={{ borderBottom: 'none', color: 'text.secondary' }}>Deception Response:</TableCell>
                                        <TableCell sx={{ borderBottom: 'none', fontFamily: 'monospace', color: '#ffa726' }}>{row.deception_response?.message || row.deception_response}</TableCell>
                                    </TableRow>
                                    <TableRow>
                                        <TableCell component="th" scope="row" sx={{ borderBottom: 'none', color: 'text.secondary' }}>User Agent:</TableCell>
                                        <TableCell sx={{ borderBottom: 'none' }}>{row.user_agent}</TableCell>
                                    </TableRow>
                                    <TableRow>
                                        <TableCell component="th" scope="row" sx={{ borderBottom: 'none', color: 'text.secondary' }}>Blockchain Hash:</TableCell>
                                        <TableCell sx={{ borderBottom: 'none', fontFamily: 'monospace', fontSize: '0.75rem' }}>{row.hash || row.blockchain_hash || 'Pending...'}</TableCell>
                                    </TableRow>
                                </TableBody>
                            </Table>
                        </Box>
                    </Collapse>
                </TableCell>
            </TableRow>
        </React.Fragment>
    );
};

const AttackLogs = ({ logs, onViewDetails, onGenerateReport }) => {
    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(10);
    const [filterType, setFilterType] = useState('All');
    const [searchIp, setSearchIp] = useState('');

    const handleChangePage = (event, newPage) => {
        setPage(newPage);
    };

    const handleChangeRowsPerPage = (event) => {
        setRowsPerPage(+event.target.value);
        setPage(0);
    };

    const filteredLogs = logs.filter(log => {
        const attackType = log.classification?.attack_type || log.attack_type;
        const matchesType = filterType === 'All' || attackType === filterType;
        const matchesIp = log.ip_address.includes(searchIp);
        return matchesType && matchesIp;
    });

    return (
        <Paper sx={{ width: '100%', overflow: 'hidden', mt: 3, p: 2, backgroundColor: '#1e1e1e', backgroundImage: 'none' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2, flexWrap: 'wrap', gap: 2 }}>
                <Typography variant="h6" component="div" sx={{ fontWeight: 600 }}>
                    Recent Attack Logs
                </Typography>

                <Box sx={{ display: 'flex', gap: 2 }}>
                    <TextField
                        label="Search IP"
                        variant="outlined"
                        size="small"
                        value={searchIp}
                        onChange={(e) => setSearchIp(e.target.value)}
                        sx={{ width: 150 }}
                    />
                    <FormControl size="small" sx={{ width: 150 }}>
                        <InputLabel>Attack Type</InputLabel>
                        <Select
                            value={filterType}
                            label="Attack Type"
                            onChange={(e) => setFilterType(e.target.value)}
                        >
                            <MenuItem value="All">All</MenuItem>
                            <MenuItem value="SQLI">SQLi</MenuItem>
                            <MenuItem value="XSS">XSS</MenuItem>
                            <MenuItem value="SSI">SSI</MenuItem>
                            <MenuItem value="BRUTE_FORCE">Brute Force</MenuItem>
                            <MenuItem value="BENIGN">Benign</MenuItem>
                        </Select>
                    </FormControl>
                </Box>
            </Box>

            <TableContainer sx={{ maxHeight: 600 }}>
                <Table stickyHeader aria-label="collapsible table">
                    <TableHead>
                        <TableRow>
                            <TableCell width={50} />
                            <TableCell>Timestamp</TableCell>
                            <TableCell>IP Address</TableCell>
                            <TableCell>Attack Type</TableCell>
                            <TableCell>Confidence</TableCell>
                            <TableCell align="right">Actions</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {filteredLogs
                            .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                            .map((row) => (
                                <Row
                                    key={row.id || Math.random()}
                                    row={row}
                                    onViewDetails={onViewDetails}
                                    onGenerateReport={onGenerateReport}
                                />
                            ))}
                        {filteredLogs.length === 0 && (
                            <TableRow>
                                <TableCell colSpan={6} align="center" sx={{ py: 3 }}>
                                    No logs found matching criteria
                                </TableCell>
                            </TableRow>
                        )}
                    </TableBody>
                </Table>
            </TableContainer>
            <TablePagination
                rowsPerPageOptions={[10, 25, 100]}
                component="div"
                count={filteredLogs.length}
                rowsPerPage={rowsPerPage}
                page={page}
                onPageChange={handleChangePage}
                onRowsPerPageChange={handleChangeRowsPerPage}
            />
        </Paper>
    );
};

export default AttackLogs;
