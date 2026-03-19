import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Box, Paper, Typography, Table, TableBody, TableCell, TableContainer,
    TableHead, TableRow, TablePagination, Chip, IconButton, Tooltip,
    Button, TextField, Grid, Card, CardContent, Dialog, DialogTitle,
    DialogContent, DialogActions, CircularProgress, Switch
} from '@mui/material';
import Navbar from './Navbar';
import { motion } from 'framer-motion';
import VerifiedIcon from '@mui/icons-material/Verified';
import WarningIcon from '@mui/icons-material/Warning';
import DownloadIcon from '@mui/icons-material/Download';
import SearchIcon from '@mui/icons-material/Search';
import LinkIcon from '@mui/icons-material/Link';
import InfoIcon from '@mui/icons-material/Info';
import { toast } from 'react-toastify';
import api from '../services/api';
import TiltCard from './TiltCard';
import BlockchainViz3D from './BlockchainViz3D';

/**
 * BlockchainExplorer — Immutable threat score blockchain
 * @see Section 3 — BlockchainExplorer Rules
 * Orbitron header, hash truncation, 3D cube icon concept, new colors
 */
const BlockchainExplorer = () => {
    const navigate = useNavigate();
    const [blocks, setBlocks] = useState([]);
    const [analytics, setAnalytics] = useState(null);
    const [loading, setLoading] = useState(true);
    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(25);
    const [total, setTotal] = useState(0);
    const [searchIp, setSearchIp] = useState('');
    const [filterIp, setFilterIp] = useState('');
    const [selectedBlock, setSelectedBlock] = useState(null);
    const [dialogOpen, setDialogOpen] = useState(false);
    const [chainIntegrity, setChainIntegrity] = useState(true);
    const [useMockData, setUseMockData] = useState(false);

    useEffect(() => {
        if (useMockData) {
            generateMockData();
        } else {
            fetchBlockchainData();
            fetchAnalytics();
        }
    }, [page, rowsPerPage, filterIp, useMockData]);

    const fetchBlockchainData = async () => {
        try {
            setLoading(true);
            const params = { skip: page * rowsPerPage, limit: rowsPerPage };
            if (filterIp) params.ip_address = filterIp;
            const response = await api.get('/api/threat-scores/blockchain', { params });
            setBlocks(response.data.records);
            setTotal(response.data.total);
            setChainIntegrity(response.data.chain_integrity);
        } catch (error) {
            console.error('Error fetching blockchain:', error);
            toast.error('Failed to fetch blockchain data');
        } finally {
            setLoading(false);
        }
    };

    const generateMockData = () => {
        setLoading(true);
        const mockBlocks = Array.from({ length: rowsPerPage }).map((_, i) => ({
            timestamp: new Date(Date.now() - i * 3600000).toISOString(),
            ip_address: `192.168.1.${Math.floor(Math.random() * 255)}`,
            attack_type: Math.random() > 0.3 ? (Math.random() > 0.5 ? 'SQLI' : 'XSS') : 'BENIGN',
            new_score: Math.floor(Math.random() * 100),
            old_score: Math.floor(Math.random() * 100),
            hash: Array.from({ length: 64 }, () => Math.floor(Math.random() * 16).toString(16)).join(''),
            previous_hash: Array.from({ length: 64 }, () => Math.floor(Math.random() * 16).toString(16)).join(''),
            is_malicious: Math.random() > 0.3
        }));

        setBlocks(mockBlocks);
        setTotal(1250);
        setChainIntegrity(true);
        setAnalytics({
            total_ips_tracked: 420,
            total_score_changes: 1250,
            score_distribution: { MALICIOUS: 45, CRITICAL: 12, SAFE: 363 }
        });
        setLoading(false);
    };

    const fetchAnalytics = async () => {
        try {
            const response = await api.get('/api/threat-scores/analytics');
            setAnalytics(response.data);
        } catch (error) {
            console.error('Error fetching analytics:', error);
        }
    };

    const handleSearch = () => { setFilterIp(searchIp); setPage(0); };
    const handleClearFilter = () => { setSearchIp(''); setFilterIp(''); setPage(0); };

    const handleExport = async () => {
        try {
            const params = filterIp ? { ip_address: filterIp } : {};
            const response = await api.get('/api/threat-scores/blockchain/export', { params });
            const dataStr = JSON.stringify(response.data, null, 2);
            const dataBlob = new Blob([dataStr], { type: 'application/json' });
            const url = URL.createObjectURL(dataBlob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `blockchain_export_${Date.now()}.json`;
            link.click();
            toast.success('Blockchain data exported');
        } catch (error) {
            console.error('Error exporting:', error);
            toast.error('Failed to export blockchain data');
        }
    };

    const handleBlockClick = (block, index) => { setSelectedBlock({ ...block, index }); setDialogOpen(true); };

    const getScoreChangeColor = (change) => {
        if (change > 0) return '#ff3d71';
        if (change < 0) return '#00e676';
        return '#ffab00';
    };

    return (
        <Box sx={{ minHeight: '100vh', position: 'relative', zIndex: 2 }}>
            <Navbar />

            <Box sx={{ px: 2, py: 2 }}>
                <Typography variant="body2" sx={{ color: '#3d5a7a', mb: 3, fontFamily: '"DM Sans", sans-serif', fontSize: '0.8rem' }}>
                    Immutable threat score tracking system — NFT-style reputation records
                </Typography>

                {/* 3D Blockchain Viz */}
                <BlockchainViz3D blocks={blocks} chainIntegrity={chainIntegrity} />

                {/* Analytics Cards */}
                {analytics && (
                    <Grid container spacing={2} sx={{ mb: 3 }}>
                        {[
                            { label: 'Total IPs Tracked', value: analytics.total_ips_tracked, color: '#00d4ff' },
                            { label: 'Blockchain Blocks', value: analytics.total_score_changes, color: '#7c4dff' },
                            { label: 'Chain Integrity', value: null, color: chainIntegrity ? '#00e676' : '#ff3d71', isIntegrity: true },
                            { label: 'Malicious IPs', value: (analytics.score_distribution?.MALICIOUS || 0) + (analytics.score_distribution?.CRITICAL || 0), color: '#ff3d71' },
                        ].map((stat, i) => (
                            <Grid item xs={12} sm={6} md={3} key={i}>
                                <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }} style={{ height: '100%' }}>
                                    <TiltCard strength={15} glowColor={stat.color} sx={{
                                        background: `linear-gradient(145deg, ${stat.color}08 0%, transparent 100%)`,
                                        border: `1px solid ${stat.color}20`,
                                        height: '100%'
                                    }}>
                                        <CardContent sx={{ py: 2 }}>
                                            <Typography variant="body2" sx={{ color: '#7a9bbf', fontSize: '0.75rem', mb: 0.5 }}>{stat.label}</Typography>
                                            {stat.isIntegrity ? (
                                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                    {chainIntegrity ? (
                                                        <><VerifiedIcon sx={{ color: '#00e676', fontSize: 24 }} /><Typography variant="h6" sx={{ color: '#00e676', fontWeight: 700, fontFamily: '"Rajdhani", sans-serif' }}>Verified</Typography></>
                                                    ) : (
                                                        <><WarningIcon sx={{ color: '#ff3d71', fontSize: 24 }} /><Typography variant="h6" sx={{ color: '#ff3d71', fontWeight: 700, fontFamily: '"Rajdhani", sans-serif' }}>Compromised</Typography></>
                                                    )}
                                                </Box>
                                            ) : (
                                                <Typography variant="h4" sx={{ fontWeight: 700, fontFamily: '"Rajdhani", sans-serif', color: stat.color }}>
                                                    {stat.value?.toLocaleString() || 0}
                                                </Typography>
                                            )}
                                        </CardContent>
                                    </TiltCard>
                                </motion.div>
                            </Grid>
                        ))}
                    </Grid>
                )}

                {/* Search & Export */}
                <Paper sx={{ p: 2, mb: 2, display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
                    <TextField
                        label="Filter by IP Address"
                        size="small"
                        value={searchIp}
                        onChange={(e) => setSearchIp(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                        sx={{ flexGrow: 1, minWidth: 200 }}
                    />
                    <Button variant="contained" startIcon={<SearchIcon />} onClick={handleSearch} sx={{ background: 'linear-gradient(135deg, #00d4ff, #0088cc)', color: '#050810', fontWeight: 600 }}>
                        Search
                    </Button>
                    {filterIp && <Button variant="outlined" onClick={handleClearFilter} sx={{ color: '#7a9bbf', borderColor: 'rgba(0, 212, 255, 0.2)' }}>Clear</Button>}
                    <Button variant="outlined" startIcon={<DownloadIcon />} onClick={handleExport} sx={{ color: '#00e676', borderColor: 'rgba(0, 230, 118, 0.3)', '&:hover': { borderColor: '#00e676', backgroundColor: 'rgba(0, 230, 118, 0.06)' } }}>
                        Export JSON
                    </Button>
                    <Grid component="label" container alignItems="center" spacing={1} sx={{ ml: 'auto', width: 'auto' }}>
                        <Grid item>
                            <Switch
                                checked={useMockData}
                                onChange={(e) => setUseMockData(e.target.checked)}
                                size="small"
                                sx={{ '& .MuiSwitch-switchBase.Mui-checked': { color: '#ffab00' }, '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': { backgroundColor: '#ffab00' } }}
                            />
                        </Grid>
                        <Grid item>
                            <Typography variant="body2" sx={{ color: '#7a9bbf', fontSize: '0.8rem', fontWeight: 600 }}>USE MOCK DATA</Typography>
                        </Grid>
                    </Grid>
                </Paper>

                {filterIp && <Typography variant="caption" sx={{ color: '#00d4ff', mb: 1, display: 'block' }}>Filtering by IP: {filterIp}</Typography>}

                {/* Blockchain Table */}
                <Paper>
                    <TableContainer sx={{ maxHeight: 600 }}>
                        <Table stickyHeader size="small">
                            <TableHead>
                                <TableRow>
                                    <TableCell sx={{ py: 1 }}>Block #</TableCell>
                                    <TableCell sx={{ py: 1 }}>Timestamp</TableCell>
                                    <TableCell sx={{ py: 1 }}>IP Address</TableCell>
                                    <TableCell sx={{ py: 1 }}>Attack Type</TableCell>
                                    <TableCell sx={{ py: 1 }}>Score Change</TableCell>
                                    <TableCell sx={{ py: 1 }}>New Score</TableCell>
                                    <TableCell sx={{ py: 1 }}>Hash</TableCell>
                                    <TableCell sx={{ py: 1 }}>Actions</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {loading ? (
                                    <TableRow><TableCell colSpan={8} align="center" sx={{ py: 4 }}><CircularProgress size={24} sx={{ color: '#00d4ff' }} /></TableCell></TableRow>
                                ) : blocks.length === 0 ? (
                                    <TableRow><TableCell colSpan={8} align="center" sx={{ py: 4, color: '#3d5a7a' }}>No blockchain records found</TableCell></TableRow>
                                ) : (
                                    blocks.map((block, index) => {
                                        const blockIndex = page * rowsPerPage + index;
                                        const scoreChange = block.new_score - block.old_score;
                                        return (
                                            <TableRow key={blockIndex} hover sx={{ '&:hover': { backgroundColor: 'rgba(0, 212, 255, 0.03)' } }}>
                                                <TableCell sx={{ py: 1 }}>
                                                    <Chip label={`#${blockIndex}`} size="small" sx={{ fontFamily: '"IBM Plex Mono", monospace', fontSize: '0.7rem', height: 22, backgroundColor: 'rgba(0, 212, 255, 0.08)', color: '#00d4ff', border: '1px solid rgba(0, 212, 255, 0.15)' }} />
                                                </TableCell>
                                                <TableCell sx={{ py: 1 }}>
                                                    <Typography variant="caption" sx={{ fontFamily: '"IBM Plex Mono", monospace', fontSize: '0.7rem', color: '#7a9bbf' }}>
                                                        {new Date(block.timestamp).toLocaleString()}
                                                    </Typography>
                                                </TableCell>
                                                <TableCell sx={{ py: 1, fontFamily: '"IBM Plex Mono", monospace', fontSize: '0.8rem', color: '#e8f4fd' }}>
                                                    {block.ip_address}
                                                </TableCell>
                                                <TableCell sx={{ py: 1 }}>
                                                    <Chip label={block.attack_type} size="small" sx={{
                                                        backgroundColor: block.is_malicious ? 'rgba(255, 61, 113, 0.12)' : 'rgba(0, 230, 118, 0.12)',
                                                        color: block.is_malicious ? '#ff3d71' : '#00e676',
                                                        fontWeight: 600, fontSize: '0.65rem', height: 22,
                                                        border: `1px solid ${block.is_malicious ? 'rgba(255, 61, 113, 0.25)' : 'rgba(0, 230, 118, 0.25)'}`,
                                                    }} />
                                                </TableCell>
                                                <TableCell sx={{ py: 1 }}>
                                                    <Typography sx={{ color: getScoreChangeColor(scoreChange), fontWeight: 700, fontFamily: '"Rajdhani", sans-serif', fontSize: '0.9rem' }}>
                                                        {scoreChange > 0 ? '+' : ''}{scoreChange}
                                                    </Typography>
                                                </TableCell>
                                                <TableCell sx={{ py: 1 }}>
                                                    <Typography sx={{ fontWeight: 700, fontFamily: '"Rajdhani", sans-serif', fontSize: '0.9rem', color: '#e8f4fd' }}>
                                                        {block.new_score}
                                                    </Typography>
                                                </TableCell>
                                                <TableCell sx={{ py: 1 }}>
                                                    <Tooltip title={block.hash}>
                                                        <Typography sx={{ fontFamily: '"IBM Plex Mono", monospace', fontSize: '0.7rem', color: '#3d5a7a', cursor: 'pointer', '&:hover': { color: '#00d4ff' } }}>
                                                            {block.hash.substring(0, 12)}…
                                                        </Typography>
                                                    </Tooltip>
                                                </TableCell>
                                                <TableCell sx={{ py: 1 }}>
                                                    <Tooltip title="View Block Details">
                                                        <IconButton size="small" onClick={() => handleBlockClick(block, blockIndex)} sx={{ color: '#7a9bbf', '&:hover': { color: '#00d4ff' } }}>
                                                            <InfoIcon sx={{ fontSize: 16 }} />
                                                        </IconButton>
                                                    </Tooltip>
                                                </TableCell>
                                            </TableRow>
                                        );
                                    })
                                )}
                            </TableBody>
                        </Table>
                    </TableContainer>
                    <TablePagination
                        component="div" count={total} page={page}
                        onPageChange={(e, newPage) => setPage(newPage)}
                        rowsPerPage={rowsPerPage}
                        onRowsPerPageChange={(e) => { setRowsPerPage(parseInt(e.target.value, 10)); setPage(0); }}
                        rowsPerPageOptions={[10, 25, 50, 100]}
                        sx={{ borderTop: '1px solid rgba(0, 212, 255, 0.06)', '& .MuiTypography-root': { fontSize: '0.75rem', color: '#7a9bbf' } }}
                    />
                </Paper>

                {/* Block Details Dialog */}
                <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
                    <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1, fontFamily: '"Rajdhani", sans-serif', fontWeight: 600 }}>
                        <LinkIcon sx={{ color: '#00d4ff' }} /> Block #{selectedBlock?.index} Details
                    </DialogTitle>
                    <DialogContent>
                        {selectedBlock && (
                            <Box sx={{ fontFamily: '"IBM Plex Mono", monospace', fontSize: '0.85rem' }}>
                                {[
                                    { label: 'IP Address', value: selectedBlock.ip_address },
                                    { label: 'Timestamp', value: new Date(selectedBlock.timestamp).toLocaleString() },
                                    { label: 'Attack Type', value: selectedBlock.attack_type },
                                    { label: 'Malicious', value: selectedBlock.is_malicious ? 'Yes' : 'No' },
                                    { label: 'Score Change', value: `${selectedBlock.old_score} → ${selectedBlock.new_score} (${selectedBlock.new_score - selectedBlock.old_score > 0 ? '+' : ''}${selectedBlock.new_score - selectedBlock.old_score})` },
                                    { label: 'Block Hash', value: selectedBlock.hash },
                                    { label: 'Previous Hash', value: selectedBlock.previous_hash },
                                ].map((item, i) => (
                                    <Box key={i} sx={{ mb: 2 }}>
                                        <Typography variant="caption" sx={{ color: '#3d5a7a', textTransform: 'uppercase', letterSpacing: 0.5 }}>{item.label}</Typography>
                                        <Typography sx={{ color: '#e8f4fd', wordBreak: 'break-all' }}>{item.value}</Typography>
                                    </Box>
                                ))}
                            </Box>
                        )}
                    </DialogContent>
                    <DialogActions>
                        <Button onClick={() => setDialogOpen(false)} sx={{ color: '#7a9bbf' }}>Close</Button>
                    </DialogActions>
                </Dialog>
            </Box>
        </Box>
    );
};

export default BlockchainExplorer;
