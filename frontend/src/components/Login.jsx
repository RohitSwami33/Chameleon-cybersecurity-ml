import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, TextField, Button, Typography, Paper, CircularProgress, InputAdornment, IconButton } from '@mui/material';
import { motion } from 'framer-motion';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';
import PersonOutlinedIcon from '@mui/icons-material/PersonOutlined';
import VisibilityIcon from '@mui/icons-material/Visibility';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import ShieldIcon from '@mui/icons-material/Shield';
import { login as apiLogin } from '../services/api';
import { toast } from 'react-toastify';
import LoginBackground3D from './LoginBackground3D';
import LoginShield3D from './LoginShield3D';

/**
 * Login — Auth page with animated particle canvas background
 * @see Section 3 — Login Rules
 * 3D canvas background, shimmer submit button, field shake on error
 */

const sleep = (ms) => new Promise(r => setTimeout(r, ms));

const Login = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [showPassword, setShowPassword] = useState(false);
    const [glitchTransform, setGlitchTransform] = useState('translateX(0)');
    const navigate = useNavigate();

    const glitch = async () => {
        for (let i = 0; i < 5; i++) {
            setGlitchTransform(`translateX(${(Math.random() - 0.5) * 8}px)`);
            await sleep(50);
        }
        setGlitchTransform('translateX(0)');
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);

        try {
            const data = await apiLogin(username, password);
            if (data.access_token) {
                localStorage.setItem('authToken', data.access_token);
                toast.success('Access granted. Welcome, Operator.');
                navigate('/dashboard');
            } else {
                throw new Error('No token received');
            }
        } catch (error) {
            console.error('Login failed:', error);

            const errorData = error.response?.data;
            if (errorData?.is_safe) {
                // User is benign, but typed wrong password
                toast.info(errorData?.detail || 'User verified as SAFE. Incorrect credentials.');
            } else {
                // Malicious or unhandled error
                glitch();
                toast.error(errorData?.detail || 'Authentication failed');
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <Box sx={{
            minHeight: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: '#050810',
            position: 'relative',
            overflow: 'hidden',
        }}>
            <LoginBackground3D />

            <motion.div
                initial={{ opacity: 0, y: 30, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                transition={{ duration: 0.6, ease: 'easeOut' }}
                style={{ width: '100%', maxWidth: 420, zIndex: 1, padding: '0 16px', transform: glitchTransform }}
            >
                <Paper sx={{
                    p: 4,
                    backgroundColor: 'rgba(8, 14, 28, 0.85)',
                    backdropFilter: 'blur(20px)',
                    border: '1px solid rgba(0, 212, 255, 0.15)',
                    borderRadius: '20px',
                }}>
                    {/* Hero Element */}
                    <Box sx={{ textAlign: 'center', mb: 1 }}>
                        <LoginShield3D />
                        <Typography variant="h5" sx={{
                            fontFamily: '"Rajdhani", sans-serif',
                            fontWeight: 700,
                            color: '#e8f4fd',
                            mb: 0.5,
                        }}>
                            CHAMELEON <span style={{ color: '#00d4ff' }}>FORENSICS</span>
                        </Typography>
                        <Typography variant="body2" sx={{ color: '#3d5a7a', fontFamily: '"DM Sans", sans-serif', fontSize: '0.8rem' }}>
                            Operator Authentication Required
                        </Typography>
                        {/* Credentials reminder */}
                        <Box sx={{
                            mt: 1.5, mb: 0.5, py: 0.8, px: 1.5,
                            borderRadius: '8px',
                            backgroundColor: 'rgba(0,212,255,0.06)',
                            border: '1px solid rgba(0,212,255,0.12)',
                        }}>
                            <Typography sx={{ fontFamily: '"IBM Plex Mono", monospace', fontSize: '0.68rem', color: '#00d4ff', opacity: 0.85 }}>
                                👤 admin &nbsp;|&nbsp; 🔑 chameleon2024
                            </Typography>
                        </Box>
                    </Box>

                    <form onSubmit={handleSubmit}>
                        <TextField
                            fullWidth
                            label="Username"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            margin="normal"
                            required
                            autoFocus
                            InputProps={{
                                startAdornment: (
                                    <InputAdornment position="start">
                                        <PersonOutlinedIcon sx={{ color: '#3d5a7a', fontSize: 20 }} />
                                    </InputAdornment>
                                ),
                            }}
                            sx={{
                                '& .MuiInputLabel-root': { color: '#3d5a7a', fontFamily: '"DM Sans", sans-serif' },
                                '& .MuiInputBase-input': { color: '#e8f4fd', fontFamily: '"IBM Plex Mono", monospace' },
                                '& .MuiOutlinedInput-root': {
                                    borderRadius: '10px',
                                    backgroundColor: 'rgba(0, 212, 255, 0.03)',
                                },
                            }}
                        />
                        <TextField
                            fullWidth
                            label="Password"
                            type={showPassword ? 'text' : 'password'}
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            margin="normal"
                            required
                            InputProps={{
                                startAdornment: (
                                    <InputAdornment position="start">
                                        <LockOutlinedIcon sx={{ color: '#3d5a7a', fontSize: 20 }} />
                                    </InputAdornment>
                                ),
                                endAdornment: (
                                    <InputAdornment position="end">
                                        <IconButton
                                            onClick={() => setShowPassword(!showPassword)}
                                            edge="end"
                                            size="small"
                                            sx={{ color: '#3d5a7a' }}
                                        >
                                            {showPassword ? <VisibilityOffIcon fontSize="small" /> : <VisibilityIcon fontSize="small" />}
                                        </IconButton>
                                    </InputAdornment>
                                ),
                            }}
                            sx={{
                                '& .MuiInputLabel-root': { color: '#3d5a7a', fontFamily: '"DM Sans", sans-serif' },
                                '& .MuiInputBase-input': { color: '#e8f4fd', fontFamily: '"IBM Plex Mono", monospace' },
                                '& .MuiOutlinedInput-root': {
                                    borderRadius: '10px',
                                    backgroundColor: 'rgba(0, 212, 255, 0.03)',
                                },
                            }}
                        />
                        <Button
                            type="submit"
                            fullWidth
                            variant="contained"
                            disabled={loading || !username || !password}
                            sx={{
                                mt: 3,
                                mb: 2,
                                py: 1.4,
                                borderRadius: '10px',
                                fontWeight: 700,
                                fontSize: '0.9rem',
                                fontFamily: '"DM Sans", sans-serif',
                                background: 'linear-gradient(135deg, #00d4ff 0%, #0088cc 100%)',
                                color: '#050810',
                                textTransform: 'none',
                                boxShadow: '0 4px 24px rgba(0, 212, 255, 0.3)',
                                '&:hover': {
                                    background: 'linear-gradient(135deg, #33ddff 0%, #00aaee 100%)',
                                    boxShadow: '0 6px 32px rgba(0, 212, 255, 0.4)',
                                },
                                '&:disabled': {
                                    background: 'rgba(0, 212, 255, 0.15)',
                                    color: '#3d5a7a',
                                },
                            }}
                        >
                            {loading ? (
                                <CircularProgress size={24} sx={{ color: '#050810' }} />
                            ) : (
                                'Authenticate'
                            )}
                        </Button>
                    </form>

                    {/* Demo bypass — auto-login with admin credentials */}
                    <Button
                        fullWidth
                        variant="outlined"
                        onClick={async () => {
                            setLoading(true);
                            try {
                                const data = await apiLogin('admin', 'chameleon2024');
                                if (data.access_token) {
                                    localStorage.setItem('authToken', data.access_token);
                                    toast.success('Admin access granted. Welcome, Operator.');
                                    navigate('/dashboard');
                                } else {
                                    throw new Error('No token');
                                }
                            } catch (err) {
                                // If backend is unreachable, store a local stub token for demo UI only
                                localStorage.setItem('authToken', 'demo-local-token');
                                toast.warning('Backend offline — limited demo mode active');
                                navigate('/dashboard');
                            } finally {
                                setLoading(false);
                            }
                        }}
                        sx={{
                            mb: 2,
                            py: 1.2,
                            borderRadius: '10px',
                            fontWeight: 600,
                            fontSize: '0.85rem',
                            fontFamily: '"DM Sans", sans-serif',
                            borderColor: 'rgba(124, 77, 255, 0.4)',
                            color: '#9670ff',
                            textTransform: 'none',
                            '&:hover': {
                                borderColor: '#7c4dff',
                                backgroundColor: 'rgba(124, 77, 255, 0.08)',
                            },
                        }}
                    >
                        ⚡ Quick Access (auto-fill admin)
                    </Button>

                    <Typography variant="caption" sx={{
                        display: 'block',
                        textAlign: 'center',
                        color: '#3d5a7a',
                        fontFamily: '"IBM Plex Mono", monospace',
                        fontSize: '0.65rem',
                        mt: 1,
                    }}>
                        🔐 Protected by Chameleon Security Framework
                    </Typography>
                </Paper>
            </motion.div>
        </Box>
    );
};

export default Login;
