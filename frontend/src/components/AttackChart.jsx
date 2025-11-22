import React, { useState } from 'react';
import {
    Paper,
    Typography,
    Box,
    ToggleButton,
    ToggleButtonGroup,
    useTheme
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

const AttackChart = ({ attackDistribution }) => {
    const [chartType, setChartType] = useState('pie');
    const theme = useTheme();

    const handleChartTypeChange = (event, newType) => {
        if (newType !== null) {
            setChartType(newType);
        }
    };

    // Transform data for Recharts
    const data = Object.entries(attackDistribution || {}).map(([name, value]) => ({
        name,
        value,
        color: getAttackTypeColor(name)
    })).filter(item => item.value > 0);

    // Custom Tooltip
    const CustomTooltip = ({ active, payload, label }) => {
        if (active && payload && payload.length) {
            return (
                <Box
                    sx={{
                        backgroundColor: 'rgba(30, 30, 30, 0.9)',
                        border: '1px solid #444',
                        p: 1.5,
                        borderRadius: 1,
                    }}
                >
                    <Typography variant="body2" sx={{ fontWeight: 600 }}>{label || payload[0].name}</Typography>
                    <Typography variant="body2" color="text.secondary">
                        Count: {payload[0].value}
                    </Typography>
                </Box>
            );
        }
        return null;
    };

    return (
        <Paper
            sx={{
                p: 3,
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                backgroundColor: '#1e1e1e',
                backgroundImage: 'none',
            }}
        >
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6" component="h2" sx={{ fontWeight: 600 }}>
                    Attack Distribution
                </Typography>
                <ToggleButtonGroup
                    value={chartType}
                    exclusive
                    onChange={handleChartTypeChange}
                    size="small"
                    aria-label="chart type"
                >
                    <ToggleButton value="pie" aria-label="pie chart">
                        <PieChartIcon fontSize="small" />
                    </ToggleButton>
                    <ToggleButton value="bar" aria-label="bar chart">
                        <BarChartIcon fontSize="small" />
                    </ToggleButton>
                </ToggleButtonGroup>
            </Box>

            <Box sx={{ flexGrow: 1, minHeight: 300 }}>
                <ResponsiveContainer width="100%" height="100%">
                    {chartType === 'pie' ? (
                        <PieChart>
                            <Pie
                                data={data}
                                cx="50%"
                                cy="50%"
                                innerRadius={60}
                                outerRadius={100}
                                paddingAngle={5}
                                dataKey="value"
                            >
                                {data.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={entry.color} stroke="none" />
                                ))}
                            </Pie>
                            <Tooltip content={<CustomTooltip />} />
                            <Legend verticalAlign="bottom" height={36} />
                        </PieChart>
                    ) : (
                        <BarChart data={data} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#333" horizontal={false} />
                            <XAxis type="number" stroke="#777" />
                            <YAxis dataKey="name" type="category" stroke="#777" width={80} />
                            <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255, 255, 255, 0.05)' }} />
                            <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={20}>
                                {data.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={entry.color} />
                                ))}
                            </Bar>
                        </BarChart>
                    )}
                </ResponsiveContainer>
            </Box>
        </Paper>
    );
};

export default AttackChart;
