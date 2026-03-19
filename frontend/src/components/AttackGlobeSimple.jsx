import React from 'react';
import { Box, Typography, Chip, Paper } from '@mui/material';
import FiberManualRecordIcon from '@mui/icons-material/FiberManualRecord';
import Spline from '@splinetool/react-spline';

const AttackOverlayHUD = ({ attacks = [] }) => {
    const activeThreats = attacks.filter(a => a.classification?.attack_type !== 'BENIGN').length;

    // Get top 5 recent attacks
    const recentAttacks = [...attacks].sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()).slice(0, 5);

    return (
        <Box sx={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', pointerEvents: 'none', zIndex: 10 }}>
            {/* Top-Left: Status */}
            <Box sx={{ position: 'absolute', top: 24, left: 24, display: 'flex', flexDirection: 'column', gap: 1 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Chip
                        icon={<FiberManualRecordIcon sx={{ fontSize: '12px !important', color: '#ff3d71 !important' }} />}
                        label="LIVE"
                        size="small"
                        sx={{
                            backgroundColor: 'rgba(255, 61, 113, 0.15)',
                            color: '#ff3d71',
                            fontWeight: 800,
                            border: '1px solid rgba(255, 61, 113, 0.3)',
                            boxShadow: '0 0 12px rgba(255, 61, 113, 0.4)',
                            '& .MuiChip-icon': { ml: 0.5 },
                        }}
                    />
                </Box>
                <Typography variant="h6" sx={{ color: '#00d4ff', fontFamily: '"IBM Plex Mono", monospace', fontWeight: 600, textShadow: '0 0 10px rgba(0, 212, 255, 0.5)' }}>
                    {activeThreats} ACTIVE THREATS
                </Typography>
            </Box>

            {/* Top-Right: Origin List Card */}
            <Paper sx={{
                position: 'absolute',
                top: 24,
                right: 24,
                width: 250,
                p: 2,
                backgroundColor: 'rgba(10, 15, 30, 0.6)',
                backdropFilter: 'blur(12px)',
                border: '1px solid rgba(0, 212, 255, 0.15)',
                pointerEvents: 'auto'
            }}>
                <Typography variant="overline" sx={{ color: '#7a9bbf', fontWeight: 700, display: 'block', mb: 1 }}>Recent Origins</Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    {recentAttacks.map((attack, i) => (
                        <Box key={i} sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid rgba(255,255,255,0.05)', pb: 0.5 }}>
                            <Box>
                                <Typography variant="caption" sx={{ color: '#e8f4fd', fontFamily: '"IBM Plex Mono", monospace', display: 'block' }}>
                                    {attack.ip_address}
                                </Typography>
                                <Typography variant="caption" sx={{ color: '#3d5a7a', display: 'block', mt: -0.5, fontSize: '0.65rem' }}>
                                    {attack.geo_location?.city || 'Unknown'}
                                </Typography>
                            </Box>
                            <Chip
                                size="small"
                                label={attack.classification?.attack_type === 'BENIGN' ? 'OK' : 'DENY'}
                                sx={{
                                    height: 16,
                                    fontSize: '0.6rem',
                                    fontWeight: 'bold',
                                    color: attack.classification?.attack_type === 'BENIGN' ? '#00e676' : '#ff3d71',
                                    backgroundColor: attack.classification?.attack_type === 'BENIGN' ? 'rgba(0,230,118,0.1)' : 'rgba(255,61,113,0.1)',
                                }}
                            />
                        </Box>
                    ))}
                    {recentAttacks.length === 0 && (
                        <Typography variant="caption" sx={{ color: '#7a9bbf' }}>No recent activity</Typography>
                    )}
                </Box>
            </Paper>

            {/* Bottom-Center: Legend */}
            <Box sx={{
                position: 'absolute',
                bottom: 32,
                left: '50%',
                transform: 'translateX(-50%)',
                display: 'flex',
                gap: 2,
                backgroundColor: 'rgba(5, 8, 16, 0.7)',
                backdropFilter: 'blur(8px)',
                px: 3,
                py: 1,
                borderRadius: '20px',
                border: '1px solid rgba(255, 255, 255, 0.05)'
            }}>
                {[
                    { label: 'SQL Injection', color: '#ff3d71' },
                    { label: 'XSS', color: '#ffa500' },
                    { label: 'Brute Force', color: '#ffea00' },
                    { label: 'Benign', color: '#00e676' },
                    { label: 'Server SF', color: '#00d4ff' }
                ].map(type => (
                    <Box key={type.label} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Box sx={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: type.color, boxShadow: `0 0 8px ${type.color}` }} />
                        <Typography variant="caption" sx={{ color: '#a0b2c6', fontSize: '0.7rem', fontWeight: 600 }}>{type.label}</Typography>
                    </Box>
                ))}
            </Box>
        </Box>
    );
};

export default function AttackGlobeSimple({ attacks = [] }) {
    return (
        <Paper
            sx={{
                width: '100%',
                height: '100%',
                minHeight: 400,
                display: 'flex',
                flexDirection: 'column',
                backgroundColor: '#050810',
                overflow: 'hidden',
                position: 'relative'
            }}
        >
            {/* The 3D Spline Interactive Globe */}
            <Box sx={{
                flexGrow: 1,
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                height: '100%',
                '& canvas': {
                    outline: 'none', // removes the focus outline from the spline canvas
                }
            }}>
                <Spline scene="https://prod.spline.design/4lwqTZL9TrjyqfcH/scene.splinecode" />
            </Box>
            
            {/* Overlay UI elements gracefully layered on top via absolute positioning */}
            <AttackOverlayHUD attacks={attacks} />
        </Paper>
    );
}
