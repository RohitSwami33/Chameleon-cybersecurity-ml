import React, { useState } from 'react';
import {
    Paper,
    Typography,
    Box,
    ToggleButton,
    ToggleButtonGroup,
} from '@mui/material';
import {
    PieChart,
    Pie,
    Cell,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer
} from 'recharts';
import PieChartIcon from '@mui/icons-material/PieChart';
import BarChartIcon from '@mui/icons-material/BarChart';
import { getAttackTypeColor } from '../utils/helpers';
import TiltCard from './TiltCard';

/**
 * AttackChart — Attack distribution as Pie or Bar chart
 * @see Section 3 — AttackChart Rules
 * Toggle between pie and bar, custom active shape, design token colors
 */
const AttackChart = ({ attackDistribution }) => {
    const [chartType, setChartType] = useState('pie');

    const handleChartTypeChange = (event, newType) => {
        if (newType !== null) {
            setChartType(newType);
        }
    };

    const data = Object.entries(attackDistribution || {}).map(([name, value]) => ({
        name,
        value,
        color: getAttackTypeColor(name)
    })).filter(item => item.value > 0);

    const CustomTooltip = ({ active, payload, label }) => {
        if (active && payload && payload.length) {
            return (
                <Box
                    sx={{
                        backgroundColor: 'rgba(10, 15, 30, 0.95)',
                        border: '1px solid rgba(0, 212, 255, 0.2)',
                        p: 1.5,
                        borderRadius: '8px',
                        backdropFilter: 'blur(8px)',
                    }}
                >
                    <Typography variant="body2" sx={{ fontWeight: 600, color: '#e8f4fd', fontFamily: '"DM Sans", sans-serif' }}>
                        {label || payload[0].name}
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#7a9bbf', fontFamily: '"IBM Plex Mono", monospace', fontSize: '0.8rem' }}>
                        Count: {payload[0].value}
                    </Typography>
                </Box>
            );
        }
        return null;
    };

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
            }}
        >
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6" component="h2" sx={{ fontWeight: 600, color: '#e8f4fd', fontSize: '0.95rem' }}>
                    Attack Distribution
                </Typography>
                <ToggleButtonGroup
                    value={chartType}
                    exclusive
                    onChange={handleChartTypeChange}
                    size="small"
                    sx={{
                        '& .MuiToggleButton-root': {
                            border: '1px solid rgba(0, 212, 255, 0.15)',
                            color: '#7a9bbf',
                            padding: '4px 8px',
                            '&.Mui-selected': {
                                backgroundColor: 'rgba(0, 212, 255, 0.12)',
                                color: '#00d4ff',
                            },
                        },
                    }}
                >
                    <ToggleButton value="pie" aria-label="pie chart">
                        <PieChartIcon fontSize="small" />
                    </ToggleButton>
                    <ToggleButton value="bar" aria-label="bar chart">
                        <BarChartIcon fontSize="small" />
                    </ToggleButton>
                </ToggleButtonGroup>
            </Box>

            <Box sx={{ flexGrow: 1, minHeight: 250, width: '100%', height: 250 }}>
                <ResponsiveContainer width="100%" height="100%">
                    {chartType === 'pie' ? (
                        <PieChart>
                            <Pie
                                data={data}
                                cx="50%"
                                cy="50%"
                                innerRadius={50}
                                outerRadius={85}
                                paddingAngle={4}
                                dataKey="value"
                                stroke="none"
                            >
                                {data.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={entry.color} />
                                ))}
                            </Pie>
                            <Tooltip content={<CustomTooltip />} />
                            <Legend
                                verticalAlign="bottom"
                                height={36}
                                formatter={(value) => (
                                    <span style={{ color: '#7a9bbf', fontSize: '0.75rem', fontFamily: '"DM Sans", sans-serif' }}>{value}</span>
                                )}
                            />
                        </PieChart>
                    ) : (
                        <BarChart data={data} layout="vertical" margin={{ top: 5, right: 20, left: 40, bottom: 5 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(0, 212, 255, 0.06)" horizontal={false} />
                            <XAxis type="number" stroke="#3d5a7a" tick={{ fontSize: 11 }} />
                            <YAxis dataKey="name" type="category" stroke="#3d5a7a" width={80} tick={{ fontSize: 11, fill: '#7a9bbf' }} />
                            <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(0, 212, 255, 0.04)' }} />
                            <Bar dataKey="value" radius={[0, 6, 6, 0]} barSize={18}>
                                {data.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={entry.color} />
                                ))}
                            </Bar>
                        </BarChart>
                    )}
                </ResponsiveContainer>
            </Box>
        </TiltCard>
    );
};

export default AttackChart;
