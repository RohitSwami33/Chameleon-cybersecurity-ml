import React, { useState, useEffect } from 'react';
import {
    Box, Paper, Typography, Chip, CircularProgress, Alert, Divider, IconButton, Tooltip
} from '@mui/material';
import { motion, AnimatePresence } from 'framer-motion';
import SecurityIcon from '@mui/icons-material/Security';
import RefreshIcon from '@mui/icons-material/Refresh';
import VerifiedIcon from '@mui/icons-material/Verified';
import FingerprintIcon from '@mui/icons-material/Fingerprint';
import { toast } from 'react-toastify';
import axios from 'axios';
import TiltCard from './TiltCard';
import ThreatRadar3D from './ThreatRadar3D';

const isDevelopment = import.meta.env.DEV;
const API_URL = isDevelopment ? 'http://localhost:8000' : '';

/**
 * ThreatIntelFeed — Privacy-preserving threat intelligence
 * @see Section 3 — ThreatIntelFeed Rules
 * Left-border severity cards, privacy banner, new design tokens
 */
const ThreatIntelFeed = () => {
    const [feed, setFeed] = useState([]);
    const [statistics, setStatistics] = useState(null);
    const [loading, setLoading] = useState(true);
    const [autoRefresh, setAutoRefresh] = useState(true);

    const fetchThreatIntel = async () => {
        try {
            const token = localStorage.getItem('authToken');
            const [reportsRes, statsRes] = await Promise.all([
                axios.get(`${API_URL}/api/threat-intel/reports?limit=50`, { headers: { Authorization: `Bearer ${token}` } }),
                axios.get(`${API_URL}/api/threat-intel/stats`, { headers: { Authorization: `Bearer ${token}` } })
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

    useEffect(() => { fetchThreatIntel(); }, []);

    useEffect(() => {
        if (autoRefresh) {
            const interval = setInterval(fetchThreatIntel, 30000);
            return () => clearInterval(interval);
        }
    }, [autoRefresh]);

    const getSeverityColor = (severity) => {
        switch (severity) {
            case 'CRITICAL': return '#ff3d71';
            case 'HIGH': return '#ff6584';
            case 'MEDIUM': return '#ffab00';
            case 'LOW': return '#00e676';
            default: return '#3d5a7a';
        }
    };

    const getAttackTypeColor = (type) => {
        switch (type) {
            case 'SQLI': return '#ff3d71';
            case 'XSS': return '#ffab00';
            case 'SSI': return '#ff6584';
            case 'BRUTE_FORCE': return '#7c4dff';
            default: return '#3d5a7a';
        }
    };

    if (loading) {
        return (
            <Paper sx={{ p: 3, height: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                <CircularProgress size={24} sx={{ color: '#00d4ff' }} />
            </Paper>
        );
    }

    return (
        <TiltCard
            glowColor="#00d4ff"
            sx={{
                p: '20px',
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                backgroundColor: 'rgba(10, 15, 30, 0.85)',
                backdropFilter: 'blur(12px)',
                border: '1px solid rgba(0, 212, 255, 0.08)',
                borderRadius: '12px',
            }}>
            {/* Top Container grouping Stats & Radar */}
            <Box sx={{ display: 'flex', gap: 3, mb: 1 }}>
                <Box sx={{ flexGrow: 1, minWidth: 0 }}>
                    {/* Header */}
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <SecurityIcon sx={{ color: '#00d4ff' }} />
                            <Typography variant="h6" component="h2" sx={{ fontWeight: 600, fontSize: '0.95rem', color: '#e8f4fd' }}>
                                Threat Intelligence Feed
                            </Typography>
                        </Box>
                        <Tooltip title="Refresh">
                            <IconButton onClick={fetchThreatIntel} size="small" sx={{ color: '#7a9bbf' }}>
                                <RefreshIcon />
                            </IconButton>
                        </Tooltip>
                    </Box>

                    {/* Privacy Banner */}
                    <Alert
                        severity="info"
                        sx={{
                            mb: 2,
                            backgroundColor: 'rgba(124, 77, 255, 0.08)',
                            border: '1px solid rgba(124, 77, 255, 0.2)',
                            borderRadius: '8px',
                            '& .MuiAlert-icon': { color: '#7c4dff' },
                        }}
                    >
                        <Typography variant="caption" sx={{ color: '#e8f4fd', fontSize: '0.75rem' }}>
                            🔒 <strong>Privacy-Preserving Intelligence:</strong> All reports use cryptographic commitments. No sensitive data revealed.
                        </Typography>
                    </Alert>

                    {/* Statistics */}
                    {statistics && (
                        <Box sx={{
                            mb: 2, p: 2,
                            backgroundColor: 'rgba(0, 212, 255, 0.04)',
                            borderRadius: '8px',
                            border: '1px solid rgba(0, 212, 255, 0.1)',
                        }}>
                            <Typography variant="caption" sx={{ color: '#3d5a7a', display: 'block', mb: 1, textTransform: 'uppercase', letterSpacing: 1, fontWeight: 600, fontSize: '0.65rem' }}>
                                CONSORTIUM STATISTICS
                            </Typography>
                            <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
                                {[
                                    { label: 'Total Patterns', value: statistics.total_patterns || 0 },
                                    { label: 'Threat Reports', value: statistics.total_reports || 0 },
                                    { label: 'Recent Attacks', value: statistics.recent_attacks || 0 },
                                ].map((stat, i) => (
                                    <Box key={i}>
                                        <Typography variant="body2" sx={{ color: '#7a9bbf', fontSize: '0.75rem' }}>{stat.label}</Typography>
                                        <Typography variant="h6" sx={{ fontFamily: '"Rajdhani", sans-serif', fontWeight: 700, color: '#e8f4fd' }}>{stat.value}</Typography>
                                    </Box>
                                ))}
                            </Box>
                        </Box>
                    )}
                </Box>

                {/* 3D Radar positioned top-right of the feed header card */}
                <Box sx={{ display: { xs: 'none', lg: 'flex' }, alignItems: 'center', justifyContent: 'center', pb: 2 }}>
                    <ThreatRadar3D feed={feed} />
                </Box>
            </Box>

            <Divider sx={{ mb: 2, borderColor: 'rgba(0, 212, 255, 0.06)' }} />

            {/* Feed */}
            <Box sx={{ flexGrow: 1, overflowY: 'auto', maxHeight: 500 }}>
                {feed.length === 0 ? (
                    <Box sx={{ textAlign: 'center', py: 4 }}>
                        <Typography variant="body2" sx={{ color: '#3d5a7a' }}>No threat intelligence reports yet</Typography>
                    </Box>
                ) : (
                    <AnimatePresence>
                        {feed.map((report, index) => (
                            <motion.div
                                key={index}
                                initial={{ opacity: 0, x: -8 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: index * 0.03 }}
                            >
                                <Box sx={{
                                    mb: 1.5, p: 2,
                                    borderRadius: '8px',
                                    backgroundColor: 'rgba(10, 15, 30, 0.5)',
                                    borderLeft: `3px solid ${getSeverityColor(report.severity)}`,
                                    border: '1px solid rgba(0, 212, 255, 0.04)',
                                    borderLeftWidth: 3,
                                    borderLeftColor: getSeverityColor(report.severity),
                                    transition: 'all 0.2s',
                                    '&:hover': {
                                        backgroundColor: 'rgba(0, 212, 255, 0.03)',
                                        borderColor: 'rgba(0, 212, 255, 0.12)',
                                        borderLeftColor: getSeverityColor(report.severity),
                                    },
                                }}>
                                    {/* Header */}
                                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                                        <Box sx={{ display: 'flex', gap: 1 }}>
                                            <Chip label={report.attack_type} size="small" sx={{
                                                backgroundColor: `${getAttackTypeColor(report.attack_type)}15`,
                                                color: getAttackTypeColor(report.attack_type),
                                                fontWeight: 700, fontSize: '0.65rem', height: 20,
                                                border: `1px solid ${getAttackTypeColor(report.attack_type)}30`,
                                            }} />
                                            <Chip label={report.severity} size="small" sx={{
                                                backgroundColor: `${getSeverityColor(report.severity)}15`,
                                                color: getSeverityColor(report.severity),
                                                fontWeight: 700, fontSize: '0.65rem', height: 20,
                                            }} />
                                        </Box>
                                        <Typography variant="caption" sx={{ color: '#3d5a7a', fontFamily: '"IBM Plex Mono", monospace', fontSize: '0.65rem' }}>
                                            {new Date(report.timestamp).toLocaleString()}
                                        </Typography>
                                    </Box>

                                    {/* Pattern Hash */}
                                    <Box sx={{ mb: 1 }}>
                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.5 }}>
                                            <FingerprintIcon sx={{ fontSize: 13, color: '#00d4ff' }} />
                                            <Typography variant="caption" sx={{ color: '#3d5a7a', fontSize: '0.65rem' }}>Pattern Hash</Typography>
                                        </Box>
                                        <Typography variant="body2" sx={{
                                            fontFamily: '"IBM Plex Mono", monospace',
                                            fontSize: '0.7rem',
                                            wordBreak: 'break-all',
                                            color: '#00e676',
                                            backgroundColor: 'rgba(0, 0, 0, 0.3)',
                                            p: 1, borderRadius: '4px',
                                        }}>
                                            {report.pattern_hash}
                                        </Typography>
                                    </Box>

                                    {/* Signature */}
                                    <Typography variant="caption" sx={{ color: '#3d5a7a', fontSize: '0.65rem' }}>
                                        Signature: <span style={{ fontFamily: '"IBM Plex Mono", monospace', color: '#00d4ff' }}>{report.signature}</span>
                                    </Typography>

                                    {/* Metadata */}
                                    <Box sx={{ display: 'flex', gap: 2, mt: 1, flexWrap: 'wrap' }}>
                                        <Typography variant="caption" sx={{ color: '#7a9bbf', fontSize: '0.65rem' }}>
                                            Confidence: <strong>{(report.confidence * 100).toFixed(1)}%</strong>
                                        </Typography>
                                        <Typography variant="caption" sx={{ color: '#7a9bbf', fontSize: '0.65rem' }}>
                                            IP Hash: <span style={{ fontFamily: '"IBM Plex Mono", monospace' }}>{report.ip_hash}</span>
                                        </Typography>
                                    </Box>

                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mt: 1 }}>
                                        <VerifiedIcon sx={{ fontSize: 12, color: '#00e676' }} />
                                        <Typography variant="caption" sx={{ color: '#00e676', fontSize: '0.6rem' }}>Cryptographically Verified</Typography>
                                    </Box>
                                </Box>
                            </motion.div>
                        ))}
                    </AnimatePresence>
                )}
            </Box>

            <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid rgba(0, 212, 255, 0.06)' }}>
                <Typography variant="caption" sx={{ color: '#3d5a7a', fontSize: '0.7rem' }}>
                    Showing {feed.length} most recent threat intelligence reports
                </Typography>
            </Box>
        </TiltCard>
    );
};

export default ThreatIntelFeed;
