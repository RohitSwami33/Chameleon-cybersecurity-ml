import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
    AppBar,
    Toolbar,
    Typography,
    Button,
    Box,
    IconButton,
    Menu,
    MenuItem,
    Chip,
    Switch,
    FormControlLabel
} from '@mui/material';
import SecurityIcon from '@mui/icons-material/Security';
import DashboardIcon from '@mui/icons-material/Dashboard';
import PublicIcon from '@mui/icons-material/Public';
import AssessmentIcon from '@mui/icons-material/Assessment';
import LinkIcon from '@mui/icons-material/Link';
import LogoutIcon from '@mui/icons-material/Logout';
import MenuIcon from '@mui/icons-material/Menu';
import RefreshIcon from '@mui/icons-material/Refresh';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import { CommandBarTrigger } from './ui/CommandBar';
import { toast } from 'react-toastify';

const Navbar = ({ lastUpdated, autoRefresh, setAutoRefresh, onRefresh, useMockGeo, setUseMockGeo }) => {
    const navigate = useNavigate();
    const location = useLocation();
    const [mobileMenuAnchor, setMobileMenuAnchor] = useState(null);

    const handleLogout = () => {
        localStorage.removeItem('authToken');
        toast.info('Logged out successfully');
        navigate('/login');
    };

    const handleMobileMenuOpen = (event) => {
        setMobileMenuAnchor(event.currentTarget);
    };

    const handleMobileMenuClose = () => {
        setMobileMenuAnchor(null);
    };

    const navItems = [
        { path: '/dashboard', label: 'Overview', icon: <DashboardIcon /> },
        { path: '/dashboard/globe', label: 'Attack Globe', icon: <PublicIcon /> },
        { path: '/dashboard/analytics', label: 'Analytics', icon: <AssessmentIcon /> },
        { path: '/dashboard/threat-intel', label: 'Threat Intel', icon: <SecurityIcon /> },
        { path: '/dashboard/chatbot', label: 'AI Assistant', icon: <SmartToyIcon /> },
        { path: '/blockchain', label: 'Blockchain', icon: <LinkIcon /> },
    ];

    const isActive = (path) => location.pathname === path;

    return (
        <AppBar 
            position="sticky" 
            color="transparent" 
            elevation={0} 
            sx={{ 
                borderBottom: '1px solid rgba(255,255,255,0.1)',
                backdropFilter: 'blur(10px)',
                backgroundColor: 'rgba(30, 30, 30, 0.8)'
            }}
        >
            <Toolbar sx={{ px: 2 }}>
                {/* Logo */}
                <SecurityIcon sx={{ mr: 2, color: 'primary.main', fontSize: 32 }} />
                <Typography 
                    variant="h5" 
                    component="div" 
                    sx={{ 
                        flexGrow: { xs: 1, md: 0 },
                        fontWeight: 700, 
                        letterSpacing: 1,
                        mr: 4
                    }}
                >
                    CHAMELEON <Typography component="span" variant="h5" color="primary" sx={{ fontWeight: 700 }}>FORENSICS</Typography>
                </Typography>

                {/* Desktop Navigation */}
                <Box sx={{ display: { xs: 'none', md: 'flex' }, gap: 1, flexGrow: 1 }}>
                    {navItems.map((item) => (
                        <Button
                            key={item.path}
                            startIcon={item.icon}
                            onClick={() => navigate(item.path)}
                            sx={{
                                color: isActive(item.path) ? 'primary.main' : 'text.primary',
                                borderBottom: isActive(item.path) ? '2px solid' : '2px solid transparent',
                                borderBottomColor: 'primary.main',
                                borderRadius: 0,
                                px: 2,
                                '&:hover': {
                                    backgroundColor: 'rgba(25, 118, 210, 0.08)',
                                }
                            }}
                        >
                            {item.label}
                        </Button>
                    ))}
                </Box>

                {/* Right Side Actions */}
                <Box sx={{ display: { xs: 'none', md: 'flex' }, alignItems: 'center', gap: 2 }}>
                    {lastUpdated && (
                        <Typography variant="caption" color="text.secondary">
                            Last updated: {lastUpdated.toLocaleTimeString()}
                        </Typography>
                    )}

                    {setAutoRefresh && (
                        <FormControlLabel
                            control={
                                <Switch
                                    checked={autoRefresh}
                                    onChange={(e) => setAutoRefresh(e.target.checked)}
                                    color="primary"
                                    size="small"
                                />
                            }
                            label={<Typography variant="body2">Live</Typography>}
                        />
                    )}

                    {setUseMockGeo && (
                        <FormControlLabel
                            control={
                                <Switch
                                    checked={useMockGeo}
                                    onChange={(e) => setUseMockGeo(e.target.checked)}
                                    color="secondary"
                                    size="small"
                                />
                            }
                            label={<Typography variant="body2">Mock Geo</Typography>}
                        />
                    )}

                    <CommandBarTrigger />

                    {onRefresh && (
                        <IconButton
                            onClick={onRefresh}
                            size="small"
                            sx={{ color: 'primary.main' }}
                        >
                            <RefreshIcon />
                        </IconButton>
                    )}

                    <Button
                        variant="outlined"
                        color="error"
                        startIcon={<LogoutIcon />}
                        onClick={handleLogout}
                        size="small"
                    >
                        Logout
                    </Button>
                </Box>

                {/* Mobile Menu Button */}
                <Box sx={{ display: { xs: 'flex', md: 'none' } }}>
                    <IconButton
                        size="large"
                        onClick={handleMobileMenuOpen}
                        color="inherit"
                    >
                        <MenuIcon />
                    </IconButton>
                </Box>

                {/* Mobile Menu */}
                <Menu
                    anchorEl={mobileMenuAnchor}
                    open={Boolean(mobileMenuAnchor)}
                    onClose={handleMobileMenuClose}
                    sx={{ display: { xs: 'block', md: 'none' } }}
                >
                    {navItems.map((item) => (
                        <MenuItem
                            key={item.path}
                            onClick={() => {
                                navigate(item.path);
                                handleMobileMenuClose();
                            }}
                            selected={isActive(item.path)}
                        >
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                {item.icon}
                                {item.label}
                            </Box>
                        </MenuItem>
                    ))}
                    <MenuItem onClick={handleLogout}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, color: 'error.main' }}>
                            <LogoutIcon />
                            Logout
                        </Box>
                    </MenuItem>
                </Menu>
            </Toolbar>
        </AppBar>
    );
};

export default Navbar;
