import React, { useMemo } from 'react';
import { Paper, Typography, Box, Chip } from '@mui/material';
import { motion } from 'framer-motion';
import PublicIcon from '@mui/icons-material/Public';

/**
 * WorldMap — SVG map with animated attack markers
 * @see Section 3 — WorldMap/GeoMap Rules
 */

const geoToSvg = (lat, lon, width = 500, height = 280) => {
    const x = ((lon + 180) / 360) * width;
    const y = ((90 - lat) / 180) * height;
    return { x, y };
};

const WorldMap = ({ geoLocations = [] }) => {
    const markers = useMemo(() =>
        geoLocations
            .filter(loc => loc.latitude && loc.longitude)
            .slice(0, 30)
            .map((loc, i) => {
                const pos = geoToSvg(loc.latitude, loc.longitude);
                return { ...loc, ...pos, id: i };
            }),
        [geoLocations]);

    return (
        <Paper sx={{
            p: '20px',
            height: '100%',
            display: 'flex',
            flexDirection: 'column',
            backgroundColor: 'rgba(10, 15, 30, 0.85)',
            backdropFilter: 'blur(12px)',
            border: '1px solid rgba(0, 212, 255, 0.08)',
            borderRadius: '12px',
        }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <PublicIcon sx={{ mr: 1, color: '#00d4ff', fontSize: 22 }} />
                <Typography variant="h6" component="h2" sx={{ fontWeight: 600, fontSize: '0.95rem', color: '#e8f4fd' }}>
                    Attack Origins Map
                </Typography>
            </Box>

            <Box sx={{
                flexGrow: 1,
                borderRadius: '8px',
                overflow: 'hidden',
                background: 'radial-gradient(ellipse at center, rgba(0, 212, 255, 0.03), transparent 70%)',
                position: 'relative',
            }}>
                <svg viewBox="0 0 500 280" style={{ width: '100%', height: '100%' }} preserveAspectRatio="xMidYMid meet">
                    <defs>
                        <filter id="marker-glow">
                            <feGaussianBlur stdDeviation="2" result="blur" />
                            <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
                        </filter>
                    </defs>

                    {/* Grid */}
                    {Array.from({ length: 18 }).map((_, i) => (
                        <line key={`v-${i}`} x1={i * 28} y1={0} x2={i * 28} y2={280} stroke="rgba(0, 212, 255, 0.04)" strokeWidth="0.5" />
                    ))}
                    {Array.from({ length: 10 }).map((_, i) => (
                        <line key={`h-${i}`} x1={0} y1={i * 28} x2={500} y2={i * 28} stroke="rgba(0, 212, 255, 0.04)" strokeWidth="0.5" />
                    ))}

                    {/* Markers */}
                    {markers.map((m) => (
                        <g key={m.id}>
                            <circle cx={m.x} cy={m.y} r={Math.min(3 + m.count * 0.4, 8)} fill="#ff3d71" fillOpacity={0.7} filter="url(#marker-glow)" />
                            <circle cx={m.x} cy={m.y} r={Math.min(3 + m.count * 0.4, 8) + 4} fill="none" stroke="#ff3d71" strokeWidth="0.8" strokeOpacity="0.3">
                                <animate attributeName="r" from={Math.min(3 + m.count * 0.4, 8)} to={Math.min(3 + m.count * 0.4, 8) + 10} dur="2s" repeatCount="indefinite" />
                                <animate attributeName="stroke-opacity" from="0.3" to="0" dur="2s" repeatCount="indefinite" />
                            </circle>
                        </g>
                    ))}
                </svg>
            </Box>

            {markers.length > 0 && (
                <Box sx={{ mt: 1.5, pt: 1.5, borderTop: '1px solid rgba(0, 212, 255, 0.06)', display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="caption" sx={{ color: '#3d5a7a', fontSize: '0.7rem' }}>
                        {markers.length} location{markers.length !== 1 ? 's' : ''} tracked
                    </Typography>
                </Box>
            )}
        </Paper>
    );
};

export default WorldMap;
