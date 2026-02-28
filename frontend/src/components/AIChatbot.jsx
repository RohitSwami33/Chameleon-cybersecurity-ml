import { useState, useRef, useEffect } from 'react';
import {
  Box, Paper, TextField, IconButton, Typography, Avatar, Chip,
  Switch, FormControlLabel, CircularProgress, Tooltip, Link, Divider
} from '@mui/material';
import {
  Send as SendIcon,
  SmartToy as BotIcon,
  Person as PersonIcon,
  Search as SearchIcon,
  Clear as ClearIcon,
  ContentCopy as CopyIcon
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'react-toastify';
import api from '../services/api';
import AIOrb3D from './AIOrb3D';

/**
 * AIChatbot — Gemini-powered security assistant
 * @see Section 3 — AIChatbot Rules
 * Purple gradient header, typing indicator, quick questions, new colors
 */
const AIChatbot = () => {
  const [messages, setMessages] = useState([
    {
      role: 'bot',
      content: 'Hello! I\'m your cybersecurity AI assistant. I can help you understand threats, analyze attacks, and provide security insights. Ask me anything about cybersecurity!',
      timestamp: new Date().toISOString()
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [useSearch, setUseSearch] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const [orbState, setOrbState] = useState('IDLE');

  const scrollToBottom = () => { messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }); };
  useEffect(() => { scrollToBottom(); }, [messages]);

  useEffect(() => {
    if (loading) {
      setOrbState('THINKING');
    } else {
      const lastMsg = messages[messages.length - 1];
      if (lastMsg?.error) {
        setOrbState('ERROR');
      } else if (lastMsg?.role === 'bot' && messages.length > 1) {
        setOrbState('SPEAKING');
        const timer = setTimeout(() => setOrbState('IDLE'), 3000); // Emulate speaking for 3 seconds
        return () => clearTimeout(timer);
      } else {
        setOrbState('IDLE');
      }
    }
  }, [loading, messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;
    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage, timestamp: new Date().toISOString() }]);
    setLoading(true);

    try {
      const response = await api.post('/api/chatbot/chat', { message: userMessage, use_search: useSearch });
      setMessages(prev => [...prev, {
        role: 'bot',
        content: response.data.response,
        timestamp: response.data.timestamp,
        search_results: response.data.search_results || []
      }]);
      if (useSearch && response.data.search_results?.length > 0) {
        toast.success(`Found ${response.data.search_results.length} relevant sources`);
      }
    } catch (error) {
      console.error('Chat error:', error);
      toast.error('Failed to get response from AI assistant');
      setMessages(prev => [...prev, { role: 'bot', content: 'I apologize, but I encountered an error. Please try again.', timestamp: new Date().toISOString(), error: true }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); } };

  const handleClearHistory = async () => {
    try {
      await api.post('/api/chatbot/clear-history');
      setMessages([{ role: 'bot', content: 'Chat history cleared. How can I help you today?', timestamp: new Date().toISOString() }]);
      toast.success('Chat history cleared');
    } catch (error) { toast.error('Failed to clear history'); }
  };

  const copyToClipboard = (text) => { navigator.clipboard.writeText(text); toast.success('Copied to clipboard'); };

  const quickQuestions = [
    'What is SQL injection?',
    'Explain XSS attacks',
    'How to prevent brute force attacks?',
    'Latest cybersecurity threats',
    'What is a honeypot?'
  ];

  return (
    <Paper elevation={0} sx={{
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
      background: 'linear-gradient(135deg, rgba(124, 77, 255, 0.05) 0%, rgba(0, 212, 255, 0.03) 100%)',
      backdropFilter: 'blur(8px)',
      borderRadius: '12px',
      border: '1px solid rgba(124, 77, 255, 0.10)',
      overflow: 'hidden',
    }}>
      {/* Header */}
      <Box sx={{
        p: 2,
        background: 'linear-gradient(135deg, rgba(124, 77, 255, 0.2), rgba(0, 212, 255, 0.1))',
        backdropFilter: 'blur(10px)',
        borderBottom: '1px solid rgba(124, 77, 255, 0.15)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Avatar sx={{ bgcolor: 'rgba(124, 77, 255, 0.3)', color: '#7c4dff', width: 36, height: 36, border: '1px solid rgba(124, 77, 255, 0.3)' }}>
            <BotIcon sx={{ fontSize: 20 }} />
          </Avatar>
          <Box>
            <Typography variant="h6" sx={{ color: '#e8f4fd', fontWeight: 600, fontSize: '0.9rem', fontFamily: '"DM Sans", sans-serif' }}>
              AI Security Assistant
            </Typography>
            <Typography variant="caption" sx={{ color: '#7a9bbf', fontSize: '0.65rem' }}>
              Powered by Gemini AI
            </Typography>
          </Box>
        </Box>
        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
          <FormControlLabel
            control={
              <Switch checked={useSearch} onChange={(e) => setUseSearch(e.target.checked)} size="small"
                sx={{ '& .MuiSwitch-switchBase.Mui-checked': { color: '#7c4dff' }, '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': { backgroundColor: '#7c4dff' } }} />
            }
            label={
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <SearchIcon sx={{ fontSize: 14, color: '#7a9bbf' }} />
                <Typography variant="caption" sx={{ color: '#7a9bbf', fontSize: '0.7rem' }}>Web</Typography>
              </Box>
            }
          />
          <Tooltip title="Clear History">
            <IconButton onClick={handleClearHistory} sx={{ color: '#7a9bbf' }} size="small">
              <ClearIcon sx={{ fontSize: 18 }} />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* AI Orb Status Context */}
      <AIOrb3D state={orbState} />

      {/* Quick Questions */}
      {messages.length === 1 && (
        <Box sx={{ p: 2, background: 'rgba(124, 77, 255, 0.05)' }}>
          <Typography variant="caption" sx={{ color: '#7a9bbf', mb: 1, display: 'block', fontSize: '0.7rem' }}>
            Quick Questions:
          </Typography>
          <Box sx={{ display: 'flex', gap: 0.8, flexWrap: 'wrap' }}>
            {quickQuestions.map((q, i) => (
              <Chip key={i} label={q} onClick={() => { setInput(q); inputRef.current?.focus(); }} size="small"
                sx={{
                  backgroundColor: 'rgba(124, 77, 255, 0.1)',
                  color: '#e8f4fd',
                  border: '1px solid rgba(124, 77, 255, 0.2)',
                  fontSize: '0.7rem',
                  cursor: 'pointer',
                  '&:hover': { backgroundColor: 'rgba(124, 77, 255, 0.2)' },
                }} />
            ))}
          </Box>
        </Box>
      )}

      {/* Messages */}
      <Box sx={{
        flex: 1,
        overflowY: 'auto',
        p: 2,
        display: 'flex',
        flexDirection: 'column',
        gap: 1.5,
        background: 'rgba(5, 8, 16, 0.1)',
      }}>
        <AnimatePresence>
          {messages.map((message, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2 }}
            >
              <Box sx={{
                display: 'flex',
                gap: 1,
                alignItems: 'flex-start',
                flexDirection: message.role === 'user' ? 'row-reverse' : 'row',
              }}>
                <Avatar sx={{
                  bgcolor: message.role === 'user' ? 'rgba(0, 212, 255, 0.2)' : 'rgba(124, 77, 255, 0.2)',
                  color: message.role === 'user' ? '#00d4ff' : '#7c4dff',
                  width: 28, height: 28,
                  border: `1px solid ${message.role === 'user' ? 'rgba(0, 212, 255, 0.3)' : 'rgba(124, 77, 255, 0.3)'}`,
                }}>
                  {message.role === 'user' ? <PersonIcon sx={{ fontSize: 16 }} /> : <BotIcon sx={{ fontSize: 16 }} />}
                </Avatar>
                <Box sx={{ flex: 1, maxWidth: '80%' }}>
                  <Paper elevation={0} sx={{
                    p: 1.5,
                    bgcolor: message.role === 'user'
                      ? 'rgba(0, 212, 255, 0.08)'
                      : message.error
                        ? 'rgba(255, 61, 113, 0.1)'
                        : 'rgba(10, 15, 30, 0.2)',
                    border: `1px solid ${message.role === 'user' ? 'rgba(0, 212, 255, 0.15)' : message.error ? 'rgba(255, 61, 113, 0.2)' : 'rgba(0, 212, 255, 0.06)'}`,
                    borderRadius: '10px',
                    backdropFilter: 'blur(4px)',
                  }}>
                    <Typography variant="body2" sx={{
                      whiteSpace: 'pre-wrap',
                      wordBreak: 'break-word',
                      lineHeight: 1.6,
                      color: '#e8f4fd',
                      fontSize: '0.8rem',
                    }}>
                      {message.content}
                    </Typography>

                    {message.search_results?.length > 0 && (
                      <Box sx={{ mt: 1.5 }}>
                        <Divider sx={{ mb: 1, borderColor: 'rgba(0, 212, 255, 0.08)' }} />
                        <Typography variant="caption" sx={{ fontWeight: 600, color: '#7c4dff', fontSize: '0.7rem' }}>Sources:</Typography>
                        {message.search_results.slice(0, 3).map((result, i) => (
                          <Box key={i} sx={{ mt: 0.5 }}>
                            <Link href={result.url} target="_blank" rel="noopener noreferrer"
                              sx={{ fontSize: '0.7rem', color: '#00d4ff', textDecoration: 'none', '&:hover': { textDecoration: 'underline' } }}>
                              {result.title}
                            </Link>
                          </Box>
                        ))}
                      </Box>
                    )}

                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 0.8 }}>
                      <Typography variant="caption" sx={{ opacity: 0.5, fontSize: '0.6rem', color: '#3d5a7a' }}>
                        {new Date(message.timestamp).toLocaleTimeString()}
                      </Typography>
                      {message.role === 'bot' && !message.error && (
                        <Tooltip title="Copy">
                          <IconButton size="small" onClick={() => copyToClipboard(message.content)} sx={{ color: '#3d5a7a', p: 0.3, '&:hover': { color: '#00d4ff' } }}>
                            <CopyIcon sx={{ fontSize: 12 }} />
                          </IconButton>
                        </Tooltip>
                      )}
                    </Box>
                  </Paper>
                </Box>
              </Box>
            </motion.div>
          ))}
        </AnimatePresence>

        {/* Typing indicator */}
        {loading && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
              <Avatar sx={{ bgcolor: 'rgba(124, 77, 255, 0.2)', color: '#7c4dff', width: 28, height: 28, border: '1px solid rgba(124, 77, 255, 0.3)' }}>
                <BotIcon sx={{ fontSize: 16 }} />
              </Avatar>
              <Paper elevation={0} sx={{ p: 1.5, bgcolor: 'rgba(10, 15, 30, 0.2)', border: '1px solid rgba(0, 212, 255, 0.06)', borderRadius: '10px', display: 'flex', alignItems: 'center', gap: 0.8, backdropFilter: 'blur(4px)' }}>
                {[0, 1, 2].map(i => (
                  <Box key={i} sx={{
                    width: 6, height: 6, borderRadius: '50%',
                    backgroundColor: '#7c4dff',
                    animation: 'typing-dot 1.4s infinite',
                    animationDelay: `${i * 0.2}s`,
                  }} />
                ))}
              </Paper>
            </Box>
          </motion.div>
        )}
        <div ref={messagesEndRef} />
      </Box>

      {/* Input */}
      <Box sx={{
        p: 2,
        background: 'linear-gradient(135deg, rgba(124, 77, 255, 0.08), rgba(0, 212, 255, 0.04))',
        borderTop: '1px solid rgba(124, 77, 255, 0.1)',
      }}>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <TextField
            inputRef={inputRef}
            fullWidth
            multiline
            maxRows={4}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="Ask about cybersecurity threats…"
            disabled={loading}
            sx={{
              '& .MuiOutlinedInput-root': {
                bgcolor: 'rgba(10, 15, 30, 0.7)',
                borderRadius: '10px',
                color: '#e8f4fd',
                fontSize: '0.85rem',
                '& fieldset': { borderColor: 'rgba(124, 77, 255, 0.15)' },
                '&:hover fieldset': { borderColor: 'rgba(124, 77, 255, 0.3)' },
                '&.Mui-focused fieldset': { borderColor: '#7c4dff' },
              },
              '& .MuiInputBase-input::placeholder': { color: '#3d5a7a', opacity: 1 },
            }}
          />
          <IconButton
            onClick={handleSend}
            disabled={!input.trim() || loading}
            sx={{
              bgcolor: 'rgba(124, 77, 255, 0.2)',
              color: '#7c4dff',
              border: '1px solid rgba(124, 77, 255, 0.3)',
              borderRadius: '10px',
              width: 44, height: 44,
              '&:hover': { bgcolor: 'rgba(124, 77, 255, 0.3)' },
              '&:disabled': { bgcolor: 'rgba(124, 77, 255, 0.05)', color: '#3d5a7a' },
            }}
          >
            <SendIcon sx={{ fontSize: 20 }} />
          </IconButton>
        </Box>
      </Box>
    </Paper>
  );
};

export default AIChatbot;
