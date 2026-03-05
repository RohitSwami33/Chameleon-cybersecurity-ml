import React, { useEffect } from 'react';
import { Card, CardContent, Typography, Box, Tooltip } from '@mui/material';
import { motion, useSpring, useTransform, useMotionValue } from 'framer-motion';
import AssessmentIcon from '@mui/icons-material/Assessment';
import SecurityIcon from '@mui/icons-material/Security';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import VerifiedUserIcon from '@mui/icons-material/VerifiedUser';
import TiltCard from './TiltCard';

/**
 * Animated number counter using Framer Motion useSpring
 * @see Section 7 — Number counters: useSpring + useTransform
 */
const AnimatedNumber = ({ value, color }) => {
    const spring = useSpring(0, { stiffness: 80, damping: 20 });
    const display = useTransform(spring, v => Math.round(v).toLocaleString());

    useEffect(() => {
        if (typeof value === 'number') {
            spring.set(value);
        }
    }, [value, spring]);

    return (
        <Box className="stat-number-container">
            <motion.span style={{
                fontFamily: '"Orbitron", sans-serif',
                fontSize: 'clamp(2rem, 4vw, 3rem)',
                color,
                textShadow: `0 0 20px ${color}66, 0 0 40px ${color}33`,
                display: 'block',
                letterSpacing: '-0.02em',
                lineHeight: 1,
                paddingBottom: '8px', /* give room so textShadow isn't clipped */
                animation: 'glowPulse 4s infinite'
            }}>
                {typeof value === 'number' ? display : value}
            </motion.span>
        </Box>
    );
};

/**
 * StatCard — individual stat card with 3D tilt + count-up
 * @see Section 3 — StatsCards Rules
 * perspective(800px) rotateX(2deg) tilt, translateZ on hover
 */
const StatCard = ({ title, value, icon, color, subtext, tooltip, delay = 0 }) => (
    <TiltCard
        glowColor={color}
        strength={25}
        initial={{ opacity: 0, scale: 0.97 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.4, delay: delay * 0.05 }}
        style={{ height: '100%' }}
    >
        <Card
            sx={{
                height: '100%',
                minHeight: 150,
                backgroundColor: 'transparent',
                backgroundImage: 'none',
                backdropFilter: 'none',
                border: `1px solid ${color}22`,
                position: 'relative',
                transformStyle: 'preserve-3d',
                transition: 'border-color 0.35s cubic-bezier(0.4, 0, 0.2, 1)',
                '&:hover': {
                    borderColor: `${color}44`,
                },
            }}
        >
            {/* Background plane to hold the blur and gradient without flattening 3D children */}
            <Box sx={{
                position: 'absolute',
                inset: 0,
                background: `linear-gradient(145deg, ${color}12 0%, ${color}06 100%)`,
                backgroundColor: 'rgba(10, 15, 30, 0.85)',
                backdropFilter: 'blur(12px)',
                pointerEvents: 'none',
                transform: 'translateZ(0px)',
                borderRadius: 'inherit',
            }} />
            {/* Subtle gradient overlay */}
            <Box sx={{
                position: 'absolute',
                top: 0, right: 0,
                width: '60%', height: '60%',
                background: `radial-gradient(circle at top right, ${color}08, transparent)`,
                pointerEvents: 'none',
                transform: 'translateZ(25px)',
            }} />

            <CardContent sx={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                p: '20px !important',
                transformStyle: 'preserve-3d',
            }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1.5, transform: 'translateZ(100px)' }}>
                    <Box
                        sx={{
                            backgroundColor: `${color}15`,
                            borderRadius: '10px',
                            p: 1,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            border: `1px solid ${color}20`,
                        }}
                    >
                        {icon}
                    </Box>
                    {tooltip && (
                        <Tooltip title={tooltip} arrow>
                            <Box
                                sx={{
                                    fontSize: '0.65rem',
                                    color: '#3d5a7a',
                                    cursor: 'help',
                                    border: '1px solid rgba(0, 212, 255, 0.1)',
                                    borderRadius: '4px',
                                    px: 0.8,
                                    py: 0.2,
                                    fontFamily: '"DM Sans", sans-serif',
                                }}
                            >
                                INFO
                            </Box>
                        </Tooltip>
                    )}
                </Box>
                <Box sx={{ transform: 'translateZ(140px)' }}>
                    <AnimatedNumber value={value} color={color} />
                    <Typography
                        variant="body2"
                        sx={{
                            color: '#7a9bbf',
                            fontWeight: 500,
                            fontFamily: '"DM Sans", sans-serif',
                            fontSize: '0.8rem',
                            transform: 'translateZ(60px)',
                        }}
                    >
                        {title}
                    </Typography>
                    {subtext && (
                        <Typography
                            variant="caption"
                            sx={{
                                color: color,
                                mt: 0.5,
                                display: 'block',
                                fontWeight: 600,
                                fontFamily: '"IBM Plex Mono", monospace',
                                fontSize: '0.7rem',
                                transform: 'translateZ(60px)',
                            }}
                        >
                            {subtext}
                        </Typography>
                    )}
                </Box>
            </CardContent>
        </Card>
    </TiltCard>
);

/**
 * StatsCards — Grid of 4 stat cards
 * Blue (total) / Red (malicious) / Green (benign) / Purple (chain integrity)
 */
const StatsCards = ({ stats }) => {
    const { total_attempts = 0, malicious_attempts = 0, benign_attempts = 0, merkle_root } = stats || {};

    const maliciousPercentage = total_attempts > 0
        ? ((malicious_attempts / total_attempts) * 100).toFixed(1)
        : 0;

    return (
        <Box sx={{
            display: 'grid',
            gridTemplateColumns: { xs: '1fr 1fr', md: 'repeat(4, 1fr)' },
            gap: '16px',
            mb: 2,
            width: '100%',
        }}>
            <StatCard
                title="Total Attempts"
                value={total_attempts}
                icon={<AssessmentIcon sx={{ color: '#00d4ff', fontSize: 28 }} />}
                color="#00d4ff"
                delay={0}
            />
            <StatCard
                title="Malicious Attacks"
                value={malicious_attempts}
                icon={<SecurityIcon sx={{ color: '#ff3d71', fontSize: 28 }} />}
                color="#ff3d71"
                subtext={`${maliciousPercentage}% of total traffic`}
                delay={1}
            />
            <StatCard
                title="Benign Requests"
                value={benign_attempts}
                icon={<CheckCircleIcon sx={{ color: '#00e676', fontSize: 28 }} />}
                color="#00e676"
                delay={2}
            />
            <StatCard
                title="Chain Integrity"
                value={merkle_root ? "Verified" : "Pending"}
                icon={<VerifiedUserIcon sx={{ color: '#7c4dff', fontSize: 28 }} />}
                color="#7c4dff"
                tooltip={merkle_root ? `Merkle Root: ${merkle_root.substring(0, 20)}…` : "No blocks yet"}
                delay={3}
            />
        </Box>
    );
};

export default StatsCards;
