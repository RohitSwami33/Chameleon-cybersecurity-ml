import React, { useRef, useEffect, useState, useCallback, useMemo, lazy, Suspense } from 'react';
import { Box, Typography, Chip, Paper, Fade } from '@mui/material';
import { motion } from 'framer-motion';
import FiberManualRecordIcon from '@mui/icons-material/FiberManualRecord';
import LanguageIcon from '@mui/icons-material/Language';

// Lazy load Spline for performance
const Spline = lazy(() => import('@splinetool/react-spline'));

const GlobeLoadingSkeleton = () => (
    <Box sx={{
        width: '100%',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        background: 'radial-gradient(circle at center, #0a1128 0%, #050810 100%)',
        position: 'absolute',
        top: 0,
        left: 0,
        zIndex: 5
    }}>
        
        <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
        >
            <LanguageIcon sx={{ fontSize: 64, color: '#00d4ff', opacity: 0.5 }} />
        </motion.div>
        <Typography variant="body2" sx={{ mt: 2, color: '#7a9bbf', fontFamily: '"IBM Plex Mono", monospace' }}>
            INITIALIZING 3D ENVIRONMENT...
        </Typography>
    </Box>
);

// Map attack types to Spline object nodes if needed
const getSplineNodeForAttack = (attackType) => {
    switch (attackType?.toUpperCase()) {
        case 'SQLI': return 'RedNode';
        case 'XSS': return 'AmberNode';
        case 'BENIGN': return 'GreenNode';
        default: return 'RedNode'; // Default shockwave
    }
};

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

// Fallback Map: The original SVG logic
const geoToSvg = (lat, lon, width = 400, height = 220) => {
    const x = ((lon + 180) / 360) * width;
    const y = ((90 - lat) / 180) * height;
    return { x, y };
};

const SVGWorldMapFallback = ({ attacks = [], serverLocation = { lat: 37.7749, lon: -122.4194 } }) => {
    const svgRef = useRef(null);
    const [dimensions, setDimensions] = useState({ width: 400, height: 220 });

    const serverPoint = useMemo(() => geoToSvg(serverLocation.lat, serverLocation.lon, dimensions.width, dimensions.height), [serverLocation, dimensions]);

    const attackArcs = useMemo(() => {
        return attacks
            .filter(a => a.geo_location?.latitude && a.geo_location?.longitude)
            .slice(0, 50)
            .map((attack, i) => {
                const from = geoToSvg(attack.geo_location.latitude, attack.geo_location.longitude, dimensions.width, dimensions.height);
                const isMalicious = attack.classification?.attack_type !== 'BENIGN';
                return {
                    id: `arc-${i}`,
                    from,
                    to: serverPoint,
                    attack,
                    isMalicious,
                    color: isMalicious ? '#ff3d71' : '#00e676',
                };
            });
    }, [attacks, serverPoint, dimensions]);

    useEffect(() => {
        const container = svgRef.current?.parentElement;
        if (!container) return;

        const observer = new ResizeObserver((entries) => {
            for (const entry of entries) {
                const { width } = entry.contentRect;
                setDimensions({ width: Math.max(300, width), height: Math.max(150, width * 0.55) });
            }
        });
        observer.observe(container);
        return () => observer.disconnect();
    }, []);

    return (
        <Paper
            sx={{
                width: '100%',
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                backgroundColor: '#050810',
                overflow: 'hidden',
                position: 'relative'
            }}
        >
            <Box sx={{
                flexGrow: 1,
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                height: '100%',
                background: 'radial-gradient(ellipse at center, rgba(0, 212, 255, 0.03) 0%, transparent 70%)',
            }}>
                <svg
                    ref={svgRef}
                    viewBox={`0 0 ${dimensions.width} ${dimensions.height}`}
                    style={{ width: '100%', height: '100%' }}
                    preserveAspectRatio="xMidYMid meet"
                >
                    <defs>
                        <filter id="glow-red-fallback">
                            <feGaussianBlur stdDeviation="2" result="blur" />
                            <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
                        </filter>
                        <filter id="glow-green-fallback">
                            <feGaussianBlur stdDeviation="1.5" result="blur" />
                            <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
                        </filter>
                    </defs>

                    {attackArcs.map((arc, i) => {
                        const midX = (arc.from.x + arc.to.x) / 2;
                        const midY = Math.min(arc.from.y, arc.to.y) - 25 - Math.random() * 15;
                        return (
                            <g key={arc.id}>
                                <path
                                    d={`M ${arc.from.x} ${arc.from.y} Q ${midX} ${midY} ${arc.to.x} ${arc.to.y}`}
                                    fill="none"
                                    stroke={arc.color}
                                    strokeWidth={1}
                                    strokeOpacity={0.4}
                                    filter={arc.isMalicious ? 'url(#glow-red-fallback)' : 'url(#glow-green-fallback)'}
                                    strokeDasharray="4,3"
                                >
                                    <animate attributeName="stroke-dashoffset" from="14" to="0" dur={`${2 + Math.random() * 2}s`} repeatCount="indefinite" />
                                </path>
                                <circle cx={arc.from.x} cy={arc.from.y} r={3} fill={arc.color} fillOpacity={0.8} />
                            </g>
                        );
                    })}
                    <circle cx={serverPoint.x} cy={serverPoint.y} r={5} fill="#00d4ff" />
                </svg>
            </Box>
            <AttackOverlayHUD attacks={attacks} />
        </Paper>
    );
};


export default function AttackGlobeSimple({ attacks = [], serverLocation = { lat: 37.7749, lon: -122.4194 } }) {
    const splineRef = useRef(null);
    const [isWebGLSupported, setIsWebGLSupported] = useState(true);
    const [isSplineLoaded, setIsSplineLoaded] = useState(false);
    const previousAttacksLength = useRef(attacks.length);

    useEffect(() => {
        try {
            const canvas = document.createElement('canvas');
            const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
            if (!gl) setIsWebGLSupported(false);
        } catch (e) {
            setIsWebGLSupported(false);
        }
    }, []);

    const onLoad = useCallback((splineApp) => {
        splineRef.current = splineApp;
        setIsSplineLoaded(true);
    }, []);

    useEffect(() => {
        if (isSplineLoaded && splineRef.current && attacks.length > previousAttacksLength.current) {
            const newAttacks = attacks.slice(previousAttacksLength.current);
            newAttacks.forEach(attack => {
                const nodeName = getSplineNodeForAttack(attack.classification?.attack_type);
                try {
                    splineRef.current.emitEvent('mouseDown', nodeName);
                } catch (e) {
                    console.warn('Spline emitEvent failed:', e);
                }
            });
            previousAttacksLength.current = attacks.length;
        } else if (attacks.length < previousAttacksLength.current) {
            previousAttacksLength.current = attacks.length;
        }
    }, [attacks, isSplineLoaded]);

    if (!isWebGLSupported) {
        return <SVGWorldMapFallback attacks={attacks} serverLocation={serverLocation} />;
    }

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            style={{ width: '100%', height: '100%', position: 'relative', overflow: 'hidden', background: '#050810' }}
        >
            <Suspense fallback={<GlobeLoadingSkeleton />}>
                <Spline
                    scene="https://prod.spline.design/4gyZLgu1E43CPGDX/scene.splinecode"
                    onLoad={onLoad}
                    style={{ width: '100%', height: '100%', border: 'none' }}
                />
            </Suspense>

            <Fade in={isSplineLoaded}>
                <Box>
                    <AttackOverlayHUD attacks={attacks} />
                </Box>
            </Fade>
        </motion.div>
    );
}
