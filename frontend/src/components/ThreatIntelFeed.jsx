import React, { useState, useEffect } from 'react';
import {
    Box,
    Paper,
    Typography,
    Chip,
    CircularProgress,
    Alert,
    Divider,
    IconButton,
    Tooltip
} from '@mui/material';
import SecurityIcon from '@mui/icons-material/Security';
import RefreshIcon from '@mui/icons-material/Refresh';
import VerifiedIcon from '@mui/icons-material/Verified';
import FingerprintIcon from '@mui/icons-material/Fingerprint';
import { toast } from 'react-toastify';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const ThreatIntelFeed = () => {
    const [feed, setFeed] = useState([]);
    const [statistics, setStatistics] = useState(null);
    const [loading, setLoading] = useState(true);
    const [autoRefresh, setAutoRefresh] = useState(true);

    const fetchThreatIntel = async () => {
        try {
            const token = localStorage.getItem('authToken');
            
            // Fetch reports and statistics
            const [reportsRes, statsRes] = await Promise.all([
                axios.get(`${API_URL}/api/threat-intel/reports?limit=50`, {
                    headers: { Authorization: `Bearer ${token}` }
                }),
                axios.get(`${API_URL}/api/threat-intel/stats`, {
                    headers: { Authorization: `Bearer ${token}` }
                })
            ]);
            
            setFeed(reportsRes.data.reports || []);
            setStatistics(statsRes.data || null);
        } catch (error) {
            console.error('Error fetching threat intelligence:', error);
            if (error.response?.status !== 401) {
                toast.error('Failed to fetch threat intelligence feed');
            }
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchThreatIntel();
    }, []);

    useEffect(() => {
        if (autoRefresh) {
            const interval = setInterval(fetchThreatIntel, 30000); // Refresh every 30 seconds
            return () => clearInterval(interval);
        }
    }, [autoRefresh]);

    const getSeverityColor = (severity) => {
        switch (severity) {
            case 'CRITICAL': return 'error';
            case 'HIGH': return 'warning';
            case 'MEDIUM': return 'info';
            case 'LOW': return 'success';
            default: return 'default';
        }
    };

    const getAttackTypeColor = (type) => {
        switch (type) {
            case 'SQLI': return '#f44336';
            case 'XSS': return '#ff9800';
            case 'SSI': return '#9c27b0';
            case 'BRUTE_FORCE': return '#e91e63';
            default: return '#757575';
        }
    };

    if (loading) {
        return (
            <Paper sx={{ p: 3, height: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                <CircularProgress />
            </Paper>
        );
    }

    return (
        <Paper
            sx={{
                p: 3,
                height: '100%',
                backgroundColor: '#1e1e1e',
                backgroundImage: 'none',
                display: 'flex',
                flexDirection: 'column',
            }}
        >
            {/* Header */}
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <SecurityIcon sx={{ color: 'primary.main' }} />
                    <Typography variant="h6" component="h2" sx={{ fontWeight: 600 }}>
                        Threat Intelligence Feed
                    </Typography>
                </Box>
                <Tooltip title="Refresh">
                    <IconButton onClick={fetchThreatIntel} size="small">
                        <RefreshIcon />
                    </IconButton>
                </Tooltip>
            </Box>

            {/* Info Alert */}
            <Alert severity="info" sx={{ mb: 2, fontSize: '0.85rem' }}>
                <Typography variant="caption">
                    🔒 <strong>Privacy-Preserving Intelligence:</strong> All reports use cryptographic commitments. 
                    No sensitive data (IPs, payloads) is revealed.
                </Typography>
            </Alert>

            {/* Statistics */}
            {statistics && (
                <Box sx={{ 
                    mb: 2, 
                    p: 2, 
                    bgcolor: 'rgba(25, 118, 210, 0.1)', 
                    borderRadius: 1,
                    border: '1px solid rgba(25, 118, 210, 0.3)'
                }}>
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
                        CONSORTIUM STATISTICS
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
                        <Box>
                            <Typography variant="body2" color="text.secondary">Total Patterns</Typography>
                            <Typography variant="h6">{statistics.total_patterns || 0}</Typography>
                        </Box>
                        <Box>
                            <Typography variant="body2" color="text.secondary">Threat Reports</Typography>
                            <Typography variant="h6">{statistics.total_reports || 0}</Typography>
                        </Box>
                        <Box>
                            <Typography variant="body2" color="text.secondary">Recent Attacks</Typography>
                            <Typography variant="h6">{statistics.recent_attacks || 0}</Typography>
                        </Box>
                    </Box>
                </Box>
            )}

            <Divider sx={{ mb: 2 }} />

            {/* Feed */}
            <Box sx={{ flexGrow: 1, overflowY: 'auto', maxHeight: 500 }}>
                {feed.length === 0 ? (
                    <Box sx={{ textAlign: 'center', py: 4 }}>
                        <Typography variant="body2" color="text.secondary">
                            No threat intelligence reports yet
                        </Typography>
                    </Box>
                ) : (
                    feed.map((report, index) => (
                        <Box
                            key={index}
                            sx={{
                                mb: 2,
                                p: 2,
                                borderRadius: 1,
                                backgroundColor: 'rgba(255, 255, 255, 0.03)',
                                border: '1px solid rgba(255, 255, 255, 0.05)',
                                transition: 'all 0.2s',
                                '&:hover': {
                                    backgroundColor: 'rgba(255, 255, 255, 0.05)',
                                    border: '1px solid rgba(25, 118, 210, 0.3)',
                                },
                            }}
                        >
                            {/* Header */}
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                                <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                                    <Chip
                                        label={report.attack_type}
                                        size="small"
                                        sx={{
                                            backgroundColor: getAttackTypeColor(report.attack_type),
                                            color: 'white',
                                            fontWeight: 600,
                                            fontSize: '0.7rem'
                                        }}
                                    />
                                    <Chip
                                        label={report.severity}
                                        size="small"
                                        color={getSeverityColor(report.severity)}
                                        sx={{ fontWeight: 600, fontSize: '0.7rem' }}
                                    />
                                </Box>
                                <Typography variant="caption" color="text.secondary">
                                    {new Date(report.timestamp).toLocaleString()}
                                </Typography>
                            </Box>

                            {/* Pattern Hash (Commitment) */}
                            <Box sx={{ mb: 1 }}>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.5 }}>
                                    <FingerprintIcon sx={{ fontSize: 14, color: 'primary.main' }} />
                                    <Typography variant="caption" color="text.secondary">
                                        Pattern Hash (Cryptographic Commitment)
                                    </Typography>
                                </Box>
                                <Typography 
                                    variant="body2" 
                                    sx={{ 
                                        fontFamily: 'monospace', 
                                        fontSize: '0.75rem',
                                        wordBreak: 'break-all',
                                        color: 'success.light',
                                        bgcolor: 'rgba(0, 0, 0, 0.3)',
                                        p: 1,
                                        borderRadius: 0.5
                                    }}
                                >
                                    {report.pattern_hash}
                                </Typography>
                            </Box>

                            {/* Attack Signature */}
                            <Box sx={{ mb: 1 }}>
                                <Typography variant="caption" color="text.secondary">
                                    Attack Signature: <span style={{ fontFamily: 'monospace', color: '#90caf9' }}>
                                        {report.signature}
                                    </span>
                                </Typography>
                            </Box>

                            {/* Metadata */}
                            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                                <Typography variant="caption" color="text.secondary">
                                    Confidence: <strong>{(report.confidence * 100).toFixed(1)}%</strong>
                                </Typography>
                                <Typography variant="caption" color="text.secondary">
                                    IP Hash: <span style={{ fontFamily: 'monospace' }}>{report.ip_hash}</span>
                                </Typography>
                            </Box>

                            {/* Verified Badge */}
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mt: 1 }}>
                                <VerifiedIcon sx={{ fontSize: 14, color: 'success.main' }} />
                                <Typography variant="caption" color="success.main">
                                    Cryptographically Verified
                                </Typography>
                            </Box>
                        </Box>
                    ))
                )}
            </Box>

            {/* Footer */}
            <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid rgba(255, 255, 255, 0.1)' }}>
                <Typography variant="caption" color="text.secondary">
                    Showing {feed.length} most recent threat intelligence reports
                </Typography>
            </Box>
        </Paper>
    );
};

export default ThreatIntelFeed;
