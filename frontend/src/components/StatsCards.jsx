import React from 'react';
import { Card, CardContent, Typography, Box, Tooltip } from '@mui/material';
import AssessmentIcon from '@mui/icons-material/Assessment';
import SecurityIcon from '@mui/icons-material/Security';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import VerifiedUserIcon from '@mui/icons-material/VerifiedUser';

const StatCard = ({ title, value, icon, color, subtext, tooltip }) => (
    <Card
        sx={{
            height: '100%',
            minHeight: 160,
            background: `linear-gradient(135deg, ${color}22 0%, ${color}11 100%)`,
            border: `1px solid ${color}44`,
            position: 'relative',
            overflow: 'hidden',
            transition: 'transform 0.3s ease-in-out, box-shadow 0.3s ease-in-out',
            '&:hover': {
                transform: 'translateY(-5px)',
                boxShadow: `0 8px 24px ${color}33`,
            },
        }}
    >
        <CardContent sx={{ height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                <Box
                    sx={{
                        backgroundColor: `${color}22`,
                        borderRadius: '50%',
                        p: 1.5,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                    }}
                >
                    {icon}
                </Box>
                {tooltip && (
                    <Tooltip title={tooltip}>
                        <Box
                            sx={{
                                fontSize: '0.75rem',
                                color: 'text.secondary',
                                cursor: 'help',
                                border: '1px solid #555',
                                borderRadius: '4px',
                                px: 1,
                            }}
                        >
                            Info
                        </Box>
                    </Tooltip>
                )}
            </Box>
            <Box>
                <Typography variant="h3" component="div" sx={{ fontWeight: 700, mb: 1 }}>
                    {value}
                </Typography>
                <Typography variant="body1" color="text.secondary" sx={{ fontWeight: 500 }}>
                    {title}
                </Typography>
                {subtext && (
                    <Typography variant="body2" sx={{ color: color, mt: 1, display: 'block', fontWeight: 600 }}>
                        {subtext}
                    </Typography>
                )}
            </Box>
        </CardContent>
    </Card>
);

const StatsCards = ({ stats }) => {
    const { total_attempts = 0, malicious_attempts = 0, benign_attempts = 0, merkle_root } = stats || {};

    const maliciousPercentage = total_attempts > 0
        ? ((malicious_attempts / total_attempts) * 100).toFixed(1)
        : 0;

    return (
        <Box sx={{ 
            display: 'flex', 
            gap: 1, 
            mb: 2,
            width: '100%'
        }}>
            <Box sx={{ flex: 1 }}>
                <StatCard
                    title="Total Attempts"
                    value={total_attempts}
                    icon={<AssessmentIcon sx={{ color: '#2196f3', fontSize: 32 }} />}
                    color="#2196f3"
                />
            </Box>
            <Box sx={{ flex: 1 }}>
                <StatCard
                    title="Malicious Attacks"
                    value={malicious_attempts}
                    icon={<SecurityIcon sx={{ color: '#f44336', fontSize: 32 }} />}
                    color="#f44336"
                    subtext={`${maliciousPercentage}% of total traffic`}
                />
            </Box>
            <Box sx={{ flex: 1 }}>
                <StatCard
                    title="Benign Requests"
                    value={benign_attempts}
                    icon={<CheckCircleIcon sx={{ color: '#4caf50', fontSize: 32 }} />}
                    color="#4caf50"
                />
            </Box>
            <Box sx={{ flex: 1 }}>
                <StatCard
                    title="Chain Integrity"
                    value={merkle_root ? "Verified" : "Pending"}
                    icon={<VerifiedUserIcon sx={{ color: '#9c27b0', fontSize: 32 }} />}
                    color="#9c27b0"
                    tooltip={merkle_root ? `Merkle Root: ${merkle_root.substring(0, 20)}...` : "No blocks yet"}
                />
            </Box>
        </Box>
    );
};

export default StatsCards;
