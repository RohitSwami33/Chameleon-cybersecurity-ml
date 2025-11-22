import React, { useState } from 'react';
import {
    Box,
    Container,
    Typography,
    TextField,
    Button,
    Paper,
    Checkbox,
    FormControlLabel,
    Link,
    CircularProgress,
    Alert,
    Fade
} from '@mui/material';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';
import { toast } from 'react-toastify';
import { submitInput } from '../services/api';
import { getClientInfo } from '../utils/helpers';

const TrapInterface = () => {
    const [formData, setFormData] = useState({
        username: '',
        password: ''
    });
    const [loading, setLoading] = useState(false);
    const [response, setResponse] = useState(null);

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setResponse(null);

        try {
            const clientInfo = await getClientInfo();

            // Combine username and password into a single input string for the backend analysis
            // or send them as structured data if the backend supports it.
            // The prompt says "submitInput(inputData)" with "input_text".
            // We'll construct an input_text that looks like a login attempt.
            const inputText = `Login attempt - Username: ${formData.username}, Password: ${formData.password}`;

            const payload = {
                input_text: inputText,
                ...clientInfo
            };

            const result = await submitInput(payload);

            // The backend might delay the response (tarpit).
            // We show the response from the deception engine.
            setResponse(result);

            if (result.malicious) {
                // Ideally we don't tell the attacker they are malicious, but the prompt says "Display response message (fake error/success)"
                // The deception engine returns a generated response.
                toast.error("Login failed. Please try again.");
            } else {
                toast.warning("Invalid credentials.");
            }

        } catch (error) {
            console.error('Error submitting input:', error);
            toast.error('An error occurred. Please try again later.');
        } finally {
            setLoading(false);
            // Clear password for security (even though it's a trap)
            setFormData(prev => ({ ...prev, password: '' }));
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
                background: 'linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)',
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
                        // User asked for "Dark theme recommended" in App.jsx, but "Fake Admin Login" usually looks like the target system.
                        // Let's stick to a professional looking dark theme admin panel since the whole app is dark.
                        // Actually, let's override to make it look like a generic enterprise login.
                        backgroundColor: '#1e1e1e',
                        border: '1px solid #333',
                    }}
                >
                    <Box
                        sx={{
                            backgroundColor: 'primary.main',
                            borderRadius: '50%',
                            p: 1,
                            mb: 2,
                            boxShadow: '0 0 15px rgba(25, 118, 210, 0.5)',
                        }}
                    >
                        <LockOutlinedIcon sx={{ color: 'white', fontSize: 32 }} />
                    </Box>

                    <Typography component="h1" variant="h5" sx={{ mb: 3, fontWeight: 600, letterSpacing: 1 }}>
                        ADMIN PORTAL
                    </Typography>

                    <Box component="form" onSubmit={handleSubmit} sx={{ width: '100%' }}>
                        <TextField
                            margin="normal"
                            required
                            fullWidth
                            id="username"
                            label="Username / Email"
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
                            sx={{ mb: 2 }}
                        />

                        <FormControlLabel
                            control={<Checkbox value="remember" color="primary" />}
                            label="Remember me"
                            sx={{ mb: 2 }}
                        />

                        <Button
                            type="submit"
                            fullWidth
                            variant="contained"
                            size="large"
                            disabled={loading}
                            sx={{
                                mt: 1,
                                mb: 2,
                                py: 1.5,
                                fontSize: '1rem',
                                position: 'relative',
                            }}
                        >
                            {loading ? (
                                <CircularProgress size={24} color="inherit" />
                            ) : (
                                'Sign In'
                            )}
                        </Button>

                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
                            <Link href="#" variant="body2" sx={{ color: 'text.secondary' }}>
                                Forgot password?
                            </Link>
                            <Link href="#" variant="body2" sx={{ color: 'text.secondary' }}>
                                System Status
                            </Link>
                        </Box>
                    </Box>

                    {/* Deception Response Display (Hidden or Subtle) */}
                    {response && (
                        <Fade in={!!response}>
                            <Alert
                                severity="error"
                                sx={{ mt: 3, width: '100%', backgroundColor: 'rgba(244, 67, 54, 0.1)' }}
                            >
                                {response.deception_response || "Authentication failed. Access denied."}
                            </Alert>
                        </Fade>
                    )}
                </Paper>

                <Box sx={{ mt: 4, textAlign: 'center' }}>
                    <Typography variant="body2" color="text.secondary">
                        © {new Date().getFullYear()} Enterprise Systems. All rights reserved.
                    </Typography>
                    <Box sx={{ mt: 1 }}>
                        <Link href="#" variant="caption" sx={{ mx: 1, color: 'text.disabled' }}>Privacy Policy</Link>
                        <Link href="#" variant="caption" sx={{ mx: 1, color: 'text.disabled' }}>Terms of Service</Link>
                    </Box>
                </Box>
            </Container>
        </Box>
    );
};

export default TrapInterface;
