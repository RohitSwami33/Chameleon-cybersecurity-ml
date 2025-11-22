import React from 'react';
import { Paper, Typography, Box, Chip, LinearProgress, Tooltip } from '@mui/material';
import WarningIcon from '@mui/icons-material/Warning';
import ShieldIcon from '@mui/icons-material/Shield';
import FlagIcon from '@mui/icons-material/Flag';

const ThreatScorePanel = ({ topThreats, flaggedCount }) => {
    const getScoreColor = (score) => {
        if (score >= 90) return '#4CAF50';  // Green - Trusted
        if (score >= 70) return '#FFC107';  // Yellow - Neutral
        if (score >= 40) return '#FF9800';  // Orange - Suspicious
        if (score >= 20) return '#F44336';  // Red - Malicious
        return '#B71C1C';  // Dark Red - Critical
    };

    const getReputationIcon = (level) => {
        if (level === 'TRUSTED') return <ShieldIcon sx={{ color: '#4CAF50' }} />;
        if (level === 'CRITICAL' || level === 'MALICIOUS') return <WarningIcon sx={{ color: '#F44336' }} />;
        return <FlagIcon sx={{ color: '#FF9800' }} />;
    };

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
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2, justifyContent: 'space-between' }}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <WarningIcon sx={{ mr: 1, color: '#F44336' }} />
                    <Typography variant="h6" component="h2" sx={{ fontWeight: 600 }}>
                        Threat Scores
                    </Typography>
                </Box>
                {flaggedCount > 0 && (
                    <Chip
                        label={`${flaggedCount} Flagged`}
                        size="small"
                        sx={{
                            backgroundColor: 'rgba(244, 67, 54, 0.2)',
                            color: '#F44336',
                            fontWeight: 600,
                            border: '1px solid rgba(244, 67, 54, 0.3)',
                        }}
                    />
                )}
            </Box>

            {!topThreats || topThreats.length === 0 ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', flexGrow: 1 }}>
                    <Typography variant="body2" color="text.secondary">
                        No threats detected
                    </Typography>
                </Box>
            ) : (
                <Box sx={{ flexGrow: 1, overflowY: 'auto' }}>
                    {topThreats.map((threat, index) => (
                        <Box
                            key={index}
                            sx={{
                                py: 2,
                                px: 2,
                                mb: 2,
                                borderRadius: 1,
                                backgroundColor: 'rgba(255, 255, 255, 0.03)',
                                border: `1px solid ${getScoreColor(threat.score)}33`,
                                transition: 'all 0.2s',
                                '&:hover': {
                                    backgroundColor: 'rgba(255, 255, 255, 0.05)',
                                    border: `1px solid ${getScoreColor(threat.score)}66`,
                                },
                            }}
                        >
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                    {getReputationIcon(threat.level)}
                                    <Typography variant="body2" sx={{ fontWeight: 600, fontFamily: 'monospace' }}>
                                        {threat.ip_address}
                                    </Typography>
                                </Box>
                                <Tooltip title={`Reputation: ${threat.level}`}>
                                    <Chip
                                        label={threat.score}
                                        size="small"
                                        sx={{
                                            backgroundColor: `${getScoreColor(threat.score)}22`,
                                            color: getScoreColor(threat.score),
                                            fontWeight: 700,
                                            border: `1px solid ${getScoreColor(threat.score)}`,
                                            minWidth: 45,
                                        }}
                                    />
                                </Tooltip>
                            </Box>

                            <Box sx={{ mb: 1 }}>
                                <LinearProgress
                                    variant="determinate"
                                    value={threat.score}
                                    sx={{
                                        height: 6,
                                        borderRadius: 3,
                                        backgroundColor: 'rgba(255, 255, 255, 0.1)',
                                        '& .MuiLinearProgress-bar': {
                                            backgroundColor: getScoreColor(threat.score),
                                        },
                                    }}
                                />
                            </Box>

                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <Typography variant="caption" color="text.secondary">
                                    {threat.total_attacks} attacks
                                </Typography>
                                <Chip
                                    label={threat.level}
                                    size="small"
                                    sx={{
                                        fontSize: '0.65rem',
                                        height: 20,
                                        backgroundColor: `${getScoreColor(threat.score)}22`,
                                        color: getScoreColor(threat.score),
                                        fontWeight: 600,
                                    }}
                                />
                            </Box>

                            {threat.recent_attacks > 0 && (
                                <Typography variant="caption" sx={{ color: '#F44336', display: 'block', mt: 0.5 }}>
                                    ⚠️ {threat.recent_attacks} attacks in last 24h
                                </Typography>
                            )}
                        </Box>
                    ))}
                </Box>
            )}

            <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid rgba(255, 255, 255, 0.1)' }}>
                <Typography variant="caption" color="text.secondary">
                    Score: 100 (Trusted) → 0 (Critical)
                </Typography>
            </Box>
        </Paper>
    );
};

export default ThreatScorePanel;
