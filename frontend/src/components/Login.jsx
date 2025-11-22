import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Box,
    Container,
    Typography,
    TextField,
    Button,
    Paper,
    Alert,
    CircularProgress
} from '@mui/material';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';
import { toast } from 'react-toastify';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_BASE_URL || process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

const Login = () => {
    const [formData, setFormData] = useState({
        username: '',
        password: ''
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
        setError('');
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            const response = await axios.post(`${API_URL}/api/auth/login`, {
                username: formData.username,
                password: formData.password
            });

            // Store token
            localStorage.setItem('authToken', response.data.access_token);

            toast.success('Login successful!');
            navigate('/dashboard');
        } catch (error) {
            console.error('Login error:', error);
            setError(error.response?.data?.detail || 'Invalid username or password');
            toast.error('Login failed');
        } finally {
            setLoading(false);
        }
    };

    return (
        <Box
            sx={{
                minHeight: '100vh',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'center',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                padding: 2,
            }}
        >
            <Container maxWidth="xs">
                <Paper
                    elevation={10}
                    sx={{
                        padding: 4,
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        borderRadius: 4,
                        backgroundColor: '#1e1e1e',
                        border: '1px solid #333',
                    }}
                >
                    <Box
                        sx={{
                            backgroundColor: 'primary.main',
                            borderRadius: '50%',
                            p: 1.5,
                            mb: 2,
                            boxShadow: '0 0 20px rgba(25, 118, 210, 0.6)',
                        }}
                    >
                        <LockOutlinedIcon sx={{ color: 'white', fontSize: 40 }} />
                    </Box>

                    <Typography component="h1" variant="h5" sx={{ mb: 1, fontWeight: 600 }}>
                        DASHBOARD ACCESS
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                        Chameleon Forensic System
                    </Typography>

                    {error && (
                        <Alert severity="error" sx={{ width: '100%', mb: 2 }}>
                            {error}
                        </Alert>
                    )}

                    <Box component="form" onSubmit={handleSubmit} sx={{ width: '100%' }}>
                        <TextField
                            margin="normal"
                            required
                            fullWidth
                            id="username"
                            label="Username"
                            name="username"
                            autoComplete="username"
                            autoFocus
                            value={formData.username}
                            onChange={handleChange}
                            variant="outlined"
                            sx={{ mb: 2 }}
                        />
                        <TextField
                            margin="normal"
                            required
                            fullWidth
                            name="password"
                            label="Password"
                            type="password"
                            id="password"
                            autoComplete="current-password"
                            value={formData.password}
                            onChange={handleChange}
                            variant="outlined"
                            sx={{ mb: 3 }}
                        />

                        <Button
                            type="submit"
                            fullWidth
                            variant="contained"
                            size="large"
                            disabled={loading}
                            sx={{
                                mt: 1,
                                py: 1.5,
                                fontSize: '1rem',
                                fontWeight: 600,
                                position: 'relative',
                            }}
                        >
                            {loading ? (
                                <CircularProgress size={24} color="inherit" />
                            ) : (
                                'ACCESS DASHBOARD'
                            )}
                        </Button>
                    </Box>
                </Paper>

                <Box sx={{ mt: 3, textAlign: 'center' }}>
                    <Typography variant="body2" color="text.secondary">
                        Default credentials: admin / chameleon2024
                    </Typography>
                </Box>
            </Container>
        </Box>
    );
};

export default Login;
