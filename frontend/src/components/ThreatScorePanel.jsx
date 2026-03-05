import React, { useState, useEffect } from 'react';
import { Paper, Typography, Box, Chip, LinearProgress, Button, CircularProgress } from '@mui/material';
import { motion } from 'framer-motion';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import RefreshIcon from '@mui/icons-material/Refresh';
import api from '../services/api';
import TiltCard from './TiltCard';

/**
 * ThreatScorePanel — scored IP list with gradient bars
 * @see Section 3 — ThreatScorePanel Rules
 * Amber triangle icon, gradient progress bar, reputation levels
 */
const getReputationLevel = (score) => {
    if (score >= 80) return { label: 'CRITICAL', color: '#ff3d71' };
    if (score >= 60) return { label: 'MALICIOUS', color: '#ff6584' };
    if (score >= 40) return { label: 'SUSPICIOUS', color: '#ffab00' };
    if (score >= 20) return { label: 'LOW RISK', color: '#00d4ff' };
    return { label: 'CLEAN', color: '#00e676' };
};

const getBarGradient = (score) => {
    if (score >= 80) return 'linear-gradient(90deg, #ff3d71, #ff6584)';
    if (score >= 60) return 'linear-gradient(90deg, #ff6584, #ffab00)';
    if (score >= 40) return 'linear-gradient(90deg, #ffab00, #00d4ff)';
    return 'linear-gradient(90deg, #00e676, #00d4ff)';
};

const ThreatScorePanel = ({ topThreats, flaggedCount }) => {
    const [scores, setScores] = useState([]);
    const [loading, setLoading] = useState(false);

    const fetchScores = async () => {
        try {
            setLoading(true);
            const response = await api.get('/api/threat-scores/');
            if (response.data && Array.isArray(response.data)) {
                setScores(response.data.slice(0, 6));
            }
        } catch (err) {
            console.error('Failed to fetch threat scores:', err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchScores();
    }, []);

    const displayData = scores.length > 0 ? scores : topThreats.slice(0, 6);

    return (
        <TiltCard
            glowColor="#ffab00"
            sx={{
                p: '20px',
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                backgroundColor: 'rgba(10, 15, 30, 0.85)',
                backdropFilter: 'blur(12px)',
                border: '1px solid rgba(0, 212, 255, 0.08)',
                borderRadius: '12px',
            }}
        >
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <WarningAmberIcon sx={{ color: '#ffab00', fontSize: 22 }} />
                    <Typography variant="h6" component="h2" sx={{ fontWeight: 600, fontSize: '0.95rem', color: '#e8f4fd' }}>
                        Threat Scores
                    </Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    {flaggedCount > 0 && (
                        <Chip
                            label={`${flaggedCount} flagged`}
                            size="small"
                            sx={{
                                backgroundColor: 'rgba(255, 61, 113, 0.12)',
                                color: '#ff3d71',
                                fontWeight: 600,
                                fontSize: '0.7rem',
                                border: '1px solid rgba(255, 61, 113, 0.2)',
                                height: 22,
                            }}
                        />
                    )}
                    <Button size="small" onClick={fetchScores} sx={{ minWidth: 'auto', color: '#7a9bbf', p: 0.5 }}>
                        <RefreshIcon sx={{ fontSize: 18 }} />
                    </Button>
                </Box>
            </Box>

            {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', flexGrow: 1 }}>
                    <CircularProgress size={24} sx={{ color: '#00d4ff' }} />
                </Box>
            ) : displayData.length === 0 ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', flexGrow: 1 }}>
                    <Typography variant="body2" sx={{ color: '#3d5a7a' }}>
                        No threat data available
                    </Typography>
                </Box>
            ) : (
                <Box sx={{ flexGrow: 1, overflowY: 'auto' }}>
                    {displayData.map((item, index) => {
                        const ip = item.ip_address || item.ip;
                        const score = item.score || item.threat_score || 0;
                        const { label, color } = getReputationLevel(score);

                        return (
                            <motion.div
                                key={ip || index}
                                initial={{ opacity: 0, y: 6 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: index * 0.06 }}
                            >
                                <Box
                                    sx={{
                                        mb: 1.5,
                                        p: 1.2,
                                        borderRadius: '8px',
                                        backgroundColor: 'rgba(10, 15, 30, 0.5)',
                                        border: '1px solid rgba(0, 212, 255, 0.04)',
                                    }}
                                >
                                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.8 }}>
                                        <Typography
                                            variant="body2"
                                            sx={{
                                                fontFamily: '"IBM Plex Mono", monospace',
                                                fontWeight: 600,
                                                fontSize: '0.8rem',
                                                color: '#e8f4fd',
                                            }}
                                        >
                                            {ip || 'Unknown'}
                                        </Typography>
                                        <Chip
                                            label={label}
                                            size="small"
                                            sx={{
                                                backgroundColor: `${color}15`,
                                                color: color,
                                                fontWeight: 700,
                                                fontSize: '0.6rem',
                                                border: `1px solid ${color}30`,
                                                height: 20,
                                            }}
                                        />
                                    </Box>
                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                        <Box sx={{ flexGrow: 1, position: 'relative', height: 4, borderRadius: 2, overflow: 'hidden', backgroundColor: 'rgba(0, 212, 255, 0.06)' }}>
                                            <Box sx={{
                                                position: 'absolute',
                                                top: 0,
                                                left: 0,
                                                height: '100%',
                                                width: `${Math.min(score, 100)}%`,
                                                background: getBarGradient(score),
                                                borderRadius: 2,
                                                transition: 'width 0.5s ease',
                                            }} />
                                        </Box>
                                        <Typography
                                            variant="caption"
                                            sx={{
                                                fontFamily: '"Rajdhani", sans-serif',
                                                fontWeight: 700,
                                                fontSize: '0.85rem',
                                                color: color,
                                                minWidth: 24,
                                                textAlign: 'right',
                                            }}
                                        >
                                            {Math.round(score)}
                                        </Typography>
                                    </Box>
                                </Box>
                            </motion.div>
                        );
                    })}
                </Box>
            )}
        </TiltCard>
    );
};

export default ThreatScorePanel;
