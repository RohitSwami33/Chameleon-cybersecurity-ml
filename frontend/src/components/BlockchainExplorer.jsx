import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Box,
    Paper,
    Typography,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    TablePagination,
    Chip,
    IconButton,
    Tooltip,
    Button,
    TextField,
    Grid,
    Card,
    CardContent,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    CircularProgress,
    AppBar,
    Toolbar
} from '@mui/material';
import VerifiedIcon from '@mui/icons-material/Verified';
import WarningIcon from '@mui/icons-material/Warning';
import DownloadIcon from '@mui/icons-material/Download';
import SearchIcon from '@mui/icons-material/Search';
import InfoIcon from '@mui/icons-material/Info';
import LinkIcon from '@mui/icons-material/Link';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import DashboardIcon from '@mui/icons-material/Dashboard';
import { toast } from 'react-toastify';
import api from '../services/api';

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

    useEffect(() => {
        fetchBlockchainData();
        fetchAnalytics();
    }, [page, rowsPerPage, filterIp]);

    const fetchBlockchainData = async () => {
        try {
            setLoading(true);
            const params = {
                skip: page * rowsPerPage,
                limit: rowsPerPage
            };
            if (filterIp) {
                params.ip_address = filterIp;
            }

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

    const fetchAnalytics = async () => {
        try {
            const response = await api.get('/api/threat-scores/analytics');
            setAnalytics(response.data);
        } catch (error) {
            console.error('Error fetching analytics:', error);
        }
    };

    const handleSearch = () => {
        setFilterIp(searchIp);
        setPage(0);
    };

    const handleClearFilter = () => {
        setSearchIp('');
        setFilterIp('');
        setPage(0);
    };

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
            
            toast.success('Blockchain data exported successfully');
        } catch (error) {
            console.error('Error exporting blockchain:', error);
            toast.error('Failed to export blockchain data');
        }
    };

    const handleBlockClick = (block, index) => {
        setSelectedBlock({ ...block, index });
        setDialogOpen(true);
    };

    const getScoreChangeColor = (change) => {
        if (change > 0) return '#4CAF50';
        if (change < 0) return '#F44336';
        return '#FFC107';
    };

    return (
        <Box sx={{ minHeight: '100vh', backgroundColor: 'background.default' }}>
            <AppBar position="static" color="transparent" elevation={0} sx={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                <Toolbar sx={{ px: 2 }}>
                    <IconButton
                        edge="start"
                        color="inherit"
                        onClick={() => navigate('/dashboard')}
                        sx={{ mr: 2 }}
                    >
                        <ArrowBackIcon />
                    </IconButton>
                    <LinkIcon sx={{ mr: 2, color: 'primary.main', fontSize: 32 }} />
                    <Typography variant="h5" component="div" sx={{ flexGrow: 1, fontWeight: 700 }}>
                        BLOCKCHAIN EXPLORER
                    </Typography>
                    <Button
                        variant="outlined"
                        startIcon={<DashboardIcon />}
                        onClick={() => navigate('/dashboard')}
                        size="small"
                    >
                        Dashboard
                    </Button>
                </Toolbar>
            </AppBar>

            <Box sx={{ p: 2 }}>
                <Box sx={{ mb: 3 }}>
                    <Typography variant="body2" color="text.secondary">
                        Immutable threat score tracking system - NFT-style reputation records
                    </Typography>
                </Box>

            {/* Analytics Cards */}
            {analytics && (
                <Grid container spacing={2} sx={{ mb: 3 }}>
                    <Grid item xs={12} sm={6} md={3}>
                        <Card sx={{ bgcolor: '#1e1e1e' }}>
                            <CardContent>
                                <Typography variant="body2" color="text.secondary">Total IPs Tracked</Typography>
                                <Typography variant="h4" sx={{ fontWeight: 700 }}>
                                    {analytics.total_ips_tracked}
                                </Typography>
                            </CardContent>
                        </Card>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                        <Card sx={{ bgcolor: '#1e1e1e' }}>
                            <CardContent>
                                <Typography variant="body2" color="text.secondary">Blockchain Blocks</Typography>
                                <Typography variant="h4" sx={{ fontWeight: 700 }}>
                                    {analytics.total_score_changes}
                                </Typography>
                            </CardContent>
                        </Card>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                        <Card sx={{ bgcolor: '#1e1e1e' }}>
                            <CardContent>
                                <Typography variant="body2" color="text.secondary">Chain Integrity</Typography>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
                                    {chainIntegrity ? (
                                        <>
                                            <VerifiedIcon sx={{ color: '#4CAF50', fontSize: 32 }} />
                                            <Typography variant="h6" sx={{ color: '#4CAF50' }}>Verified</Typography>
                                        </>
                                    ) : (
                                        <>
                                            <WarningIcon sx={{ color: '#F44336', fontSize: 32 }} />
                                            <Typography variant="h6" sx={{ color: '#F44336' }}>Compromised</Typography>
                                        </>
                                    )}
                                </Box>
                            </CardContent>
                        </Card>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                        <Card sx={{ bgcolor: '#1e1e1e' }}>
                            <CardContent>
                                <Typography variant="body2" color="text.secondary">Malicious IPs</Typography>
                                <Typography variant="h4" sx={{ fontWeight: 700, color: '#F44336' }}>
                                    {analytics.score_distribution.MALICIOUS + analytics.score_distribution.CRITICAL}
                                </Typography>
                            </CardContent>
                        </Card>
                    </Grid>
                </Grid>
            )}

            {/* Search and Export */}
            <Paper sx={{ p: 2, mb: 2, bgcolor: '#1e1e1e' }}>
                <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
                    <TextField
                        label="Filter by IP Address"
                        variant="outlined"
                        size="small"
                        value={searchIp}
                        onChange={(e) => setSearchIp(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                        sx={{ flexGrow: 1, minWidth: 200 }}
                    />
                    <Button
                        variant="contained"
                        startIcon={<SearchIcon />}
                        onClick={handleSearch}
                    >
                        Search
                    </Button>
                    {filterIp && (
                        <Button
                            variant="outlined"
                            onClick={handleClearFilter}
                        >
                            Clear Filter
                        </Button>
                    )}
                    <Button
                        variant="outlined"
                        startIcon={<DownloadIcon />}
                        onClick={handleExport}
                        color="success"
                    >
                        Export JSON
                    </Button>
                </Box>
                {filterIp && (
                    <Typography variant="caption" color="primary" sx={{ mt: 1, display: 'block' }}>
                        Filtering by IP: {filterIp}
                    </Typography>
                )}
            </Paper>

            {/* Blockchain Table */}
            <Paper sx={{ bgcolor: '#1e1e1e' }}>
                <TableContainer sx={{ maxHeight: 600 }}>
                    <Table stickyHeader>
                        <TableHead>
                            <TableRow>
                                <TableCell>Block #</TableCell>
                                <TableCell>Timestamp</TableCell>
                                <TableCell>IP Address</TableCell>
                                <TableCell>Attack Type</TableCell>
                                <TableCell>Score Change</TableCell>
                                <TableCell>New Score</TableCell>
                                <TableCell>Hash</TableCell>
                                <TableCell>Actions</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {loading ? (
                                <TableRow>
                                    <TableCell colSpan={8} align="center" sx={{ py: 4 }}>
                                        <CircularProgress />
                                    </TableCell>
                                </TableRow>
                            ) : blocks.length === 0 ? (
                                <TableRow>
                                    <TableCell colSpan={8} align="center" sx={{ py: 4 }}>
                                        No blockchain records found
                                    </TableCell>
                                </TableRow>
                            ) : (
                                blocks.map((block, index) => {
                                    const blockIndex = page * rowsPerPage + index;
                                    const scoreChange = block.new_score - block.old_score;
                                    return (
                                        <TableRow key={blockIndex} hover>
                                            <TableCell>
                                                <Chip
                                                    label={`#${blockIndex}`}
                                                    size="small"
                                                    sx={{ fontFamily: 'monospace' }}
                                                />
                                            </TableCell>
                                            <TableCell>
                                                {new Date(block.timestamp).toLocaleString()}
                                            </TableCell>
                                            <TableCell sx={{ fontFamily: 'monospace' }}>
                                                {block.ip_address}
                                            </TableCell>
                                            <TableCell>
                                                <Chip
                                                    label={block.attack_type}
                                                    size="small"
                                                    color={block.is_malicious ? 'error' : 'success'}
                                                />
                                            </TableCell>
                                            <TableCell>
                                                <Typography
                                                    sx={{
                                                        color: getScoreChangeColor(scoreChange),
                                                        fontWeight: 600
                                                    }}
                                                >
                                                    {scoreChange > 0 ? '+' : ''}{scoreChange}
                                                </Typography>
                                            </TableCell>
                                            <TableCell>
                                                <Typography sx={{ fontWeight: 600 }}>
                                                    {block.new_score}
                                                </Typography>
                                            </TableCell>
                                            <TableCell>
                                                <Tooltip title={block.hash}>
                                                    <Typography
                                                        sx={{
                                                            fontFamily: 'monospace',
                                                            fontSize: '0.75rem',
                                                            cursor: 'pointer'
                                                        }}
                                                    >
                                                        {block.hash.substring(0, 12)}...
                                                    </Typography>
                                                </Tooltip>
                                            </TableCell>
                                            <TableCell>
                                                <Tooltip title="View Block Details">
                                                    <IconButton
                                                        size="small"
                                                        onClick={() => handleBlockClick(block, blockIndex)}
                                                    >
                                                        <InfoIcon fontSize="small" />
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
                    component="div"
                    count={total}
                    page={page}
                    onPageChange={(e, newPage) => setPage(newPage)}
                    rowsPerPage={rowsPerPage}
                    onRowsPerPageChange={(e) => {
                        setRowsPerPage(parseInt(e.target.value, 10));
                        setPage(0);
                    }}
                    rowsPerPageOptions={[10, 25, 50, 100]}
                />
            </Paper>

            {/* Block Details Dialog */}
            <Dialog
                open={dialogOpen}
                onClose={() => setDialogOpen(false)}
                maxWidth="md"
                fullWidth
            >
                <DialogTitle>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <LinkIcon />
                        Block #{selectedBlock?.index} Details
                    </Box>
                </DialogTitle>
                <DialogContent>
                    {selectedBlock && (
                        <Box sx={{ fontFamily: 'monospace', fontSize: '0.9rem' }}>
                            <Box sx={{ mb: 2 }}>
                                <Typography variant="caption" color="text.secondary">IP Address</Typography>
                                <Typography>{selectedBlock.ip_address}</Typography>
                            </Box>
                            <Box sx={{ mb: 2 }}>
                                <Typography variant="caption" color="text.secondary">Timestamp</Typography>
                                <Typography>{new Date(selectedBlock.timestamp).toLocaleString()}</Typography>
                            </Box>
                            <Box sx={{ mb: 2 }}>
                                <Typography variant="caption" color="text.secondary">Attack Type</Typography>
                                <Typography>{selectedBlock.attack_type}</Typography>
                            </Box>
                            <Box sx={{ mb: 2 }}>
                                <Typography variant="caption" color="text.secondary">Malicious</Typography>
                                <Typography>{selectedBlock.is_malicious ? 'Yes' : 'No'}</Typography>
                            </Box>
                            <Box sx={{ mb: 2 }}>
                                <Typography variant="caption" color="text.secondary">Score Change</Typography>
                                <Typography>
                                    {selectedBlock.old_score} → {selectedBlock.new_score} 
                                    ({selectedBlock.new_score - selectedBlock.old_score > 0 ? '+' : ''}
                                    {selectedBlock.new_score - selectedBlock.old_score})
                                </Typography>
                            </Box>
                            <Box sx={{ mb: 2 }}>
                                <Typography variant="caption" color="text.secondary">Block Hash</Typography>
                                <Typography sx={{ wordBreak: 'break-all' }}>{selectedBlock.hash}</Typography>
                            </Box>
                            <Box sx={{ mb: 2 }}>
                                <Typography variant="caption" color="text.secondary">Previous Hash</Typography>
                                <Typography sx={{ wordBreak: 'break-all' }}>{selectedBlock.previous_hash}</Typography>
                            </Box>
                        </Box>
                    )}
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setDialogOpen(false)}>Close</Button>
                </DialogActions>
            </Dialog>
            </Box>
        </Box>
    );
};

export default BlockchainExplorer;
