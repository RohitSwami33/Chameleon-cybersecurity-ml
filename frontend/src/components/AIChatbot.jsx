import { useState, useRef, useEffect } from 'react';
import {
  Box,
  Paper,
  TextField,
  IconButton,
  Typography,
  Avatar,
  Chip,
  Switch,
  FormControlLabel,
  CircularProgress,
  Tooltip,
  Link,
  Divider,
  Button
} from '@mui/material';
import {
  Send as SendIcon,
  SmartToy as BotIcon,
  Person as PersonIcon,
  Search as SearchIcon,
  Clear as ClearIcon,
  ContentCopy as CopyIcon
} from '@mui/icons-material';
import { toast } from 'react-toastify';
import api from '../services/api';

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

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    
    // Add user message
    setMessages(prev => [...prev, {
      role: 'user',
      content: userMessage,
      timestamp: new Date().toISOString()
    }]);

    setLoading(true);

    try {
      const response = await api.post('/api/chatbot/chat', {
        message: userMessage,
        use_search: useSearch
      });

      // Add bot response
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
      
      setMessages(prev => [...prev, {
        role: 'bot',
        content: 'I apologize, but I encountered an error. Please try again.',
        timestamp: new Date().toISOString(),
        error: true
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleClearHistory = async () => {
    try {
      await api.post('/api/chatbot/clear-history');
      setMessages([{
        role: 'bot',
        content: 'Chat history cleared. How can I help you today?',
        timestamp: new Date().toISOString()
      }]);
      toast.success('Chat history cleared');
    } catch (error) {
      console.error('Clear history error:', error);
      toast.error('Failed to clear history');
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard');
  };

  const quickQuestions = [
    'What is SQL injection?',
    'Explain XSS attacks',
    'How to prevent brute force attacks?',
    'Latest cybersecurity threats',
    'What is a honeypot?'
  ];

  const handleQuickQuestion = (question) => {
    setInput(question);
    inputRef.current?.focus();
  };

  return (
    <Paper
      elevation={3}
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        borderRadius: 2,
        overflow: 'hidden'
      }}
    >
      {/* Header */}
      <Box
        sx={{
          p: 2,
          background: 'rgba(0,0,0,0.2)',
          backdropFilter: 'blur(10px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Avatar sx={{ bgcolor: '#fff', color: '#667eea' }}>
            <BotIcon />
          </Avatar>
          <Box>
            <Typography variant="h6" sx={{ color: '#fff', fontWeight: 600 }}>
              AI Security Assistant
            </Typography>
            <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.8)' }}>
              Powered by Gemini AI
            </Typography>
          </Box>
        </Box>
        
        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
          <FormControlLabel
            control={
              <Switch
                checked={useSearch}
                onChange={(e) => setUseSearch(e.target.checked)}
                sx={{
                  '& .MuiSwitch-switchBase.Mui-checked': {
                    color: '#fff',
                  },
                  '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                    backgroundColor: '#fff',
                  },
                }}
              />
            }
            label={
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <SearchIcon sx={{ fontSize: 16, color: '#fff' }} />
                <Typography variant="caption" sx={{ color: '#fff' }}>
                  Web Search
                </Typography>
              </Box>
            }
          />
          <Tooltip title="Clear History">
            <IconButton onClick={handleClearHistory} sx={{ color: '#fff' }}>
              <ClearIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Quick Questions */}
      {messages.length === 1 && (
        <Box sx={{ p: 2, background: 'rgba(255,255,255,0.1)' }}>
          <Typography variant="caption" sx={{ color: '#fff', mb: 1, display: 'block' }}>
            Quick Questions:
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            {quickQuestions.map((question, idx) => (
              <Chip
                key={idx}
                label={question}
                onClick={() => handleQuickQuestion(question)}
                sx={{
                  bgcolor: 'rgba(255,255,255,0.2)',
                  color: '#fff',
                  '&:hover': {
                    bgcolor: 'rgba(255,255,255,0.3)',
                  },
                  cursor: 'pointer'
                }}
                size="small"
              />
            ))}
          </Box>
        </Box>
      )}

      {/* Messages */}
      <Box
        sx={{
          flex: 1,
          overflowY: 'auto',
          p: 2,
          display: 'flex',
          flexDirection: 'column',
          gap: 2,
          background: 'rgba(255,255,255,0.05)',
          '&::-webkit-scrollbar': {
            width: '8px',
          },
          '&::-webkit-scrollbar-track': {
            background: 'rgba(255,255,255,0.1)',
          },
          '&::-webkit-scrollbar-thumb': {
            background: 'rgba(255,255,255,0.3)',
            borderRadius: '4px',
          },
        }}
      >
        {messages.map((message, idx) => (
          <Box
            key={idx}
            sx={{
              display: 'flex',
              gap: 1,
              alignItems: 'flex-start',
              flexDirection: message.role === 'user' ? 'row-reverse' : 'row'
            }}
          >
            <Avatar
              sx={{
                bgcolor: message.role === 'user' ? '#4caf50' : '#fff',
                color: message.role === 'user' ? '#fff' : '#667eea',
                width: 32,
                height: 32
              }}
            >
              {message.role === 'user' ? <PersonIcon /> : <BotIcon />}
            </Avatar>
            
            <Box sx={{ flex: 1, maxWidth: '80%' }}>
              <Paper
                elevation={2}
                sx={{
                  p: 1.5,
                  bgcolor: message.role === 'user' 
                    ? 'rgba(76, 175, 80, 0.2)' 
                    : message.error 
                    ? 'rgba(244, 67, 54, 0.2)'
                    : 'rgba(255,255,255,0.95)',
                  color: message.role === 'user' || message.error ? '#fff' : '#000',
                  borderRadius: 2,
                  position: 'relative'
                }}
              >
                <Typography
                  variant="body2"
                  sx={{
                    whiteSpace: 'pre-wrap',
                    wordBreak: 'break-word',
                    lineHeight: 1.6
                  }}
                >
                  {message.content}
                </Typography>
                
                {message.search_results && message.search_results.length > 0 && (
                  <Box sx={{ mt: 2 }}>
                    <Divider sx={{ mb: 1, borderColor: 'rgba(0,0,0,0.1)' }} />
                    <Typography variant="caption" sx={{ fontWeight: 600, color: '#667eea' }}>
                      Sources:
                    </Typography>
                    {message.search_results.slice(0, 3).map((result, i) => (
                      <Box key={i} sx={{ mt: 0.5 }}>
                        <Link
                          href={result.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          sx={{
                            fontSize: '0.75rem',
                            color: '#667eea',
                            textDecoration: 'none',
                            '&:hover': { textDecoration: 'underline' }
                          }}
                        >
                          {result.title}
                        </Link>
                      </Box>
                    ))}
                  </Box>
                )}
                
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 1 }}>
                  <Typography variant="caption" sx={{ opacity: 0.7, fontSize: '0.65rem' }}>
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </Typography>
                  {message.role === 'bot' && !message.error && (
                    <Tooltip title="Copy">
                      <IconButton
                        size="small"
                        onClick={() => copyToClipboard(message.content)}
                        sx={{ opacity: 0.6, '&:hover': { opacity: 1 } }}
                      >
                        <CopyIcon sx={{ fontSize: 14 }} />
                      </IconButton>
                    </Tooltip>
                  )}
                </Box>
              </Paper>
            </Box>
          </Box>
        ))}
        
        {loading && (
          <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
            <Avatar sx={{ bgcolor: '#fff', color: '#667eea', width: 32, height: 32 }}>
              <BotIcon />
            </Avatar>
            <Paper
              elevation={2}
              sx={{
                p: 1.5,
                bgcolor: 'rgba(255,255,255,0.95)',
                borderRadius: 2,
                display: 'flex',
                alignItems: 'center',
                gap: 1
              }}
            >
              <CircularProgress size={16} />
              <Typography variant="body2">Thinking...</Typography>
            </Paper>
          </Box>
        )}
        
        <div ref={messagesEndRef} />
      </Box>

      {/* Input */}
      <Box
        sx={{
          p: 2,
          background: 'rgba(0,0,0,0.2)',
          backdropFilter: 'blur(10px)',
        }}
      >
        <Box sx={{ display: 'flex', gap: 1 }}>
          <TextField
            inputRef={inputRef}
            fullWidth
            multiline
            maxRows={4}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about cybersecurity threats, attacks, or best practices..."
            disabled={loading}
            sx={{
              '& .MuiOutlinedInput-root': {
                bgcolor: 'rgba(255,255,255,0.95)',
                borderRadius: 2,
                color: '#000',
                '& fieldset': {
                  borderColor: 'transparent',
                },
                '&:hover fieldset': {
                  borderColor: 'rgba(255,255,255,0.5)',
                },
                '&.Mui-focused fieldset': {
                  borderColor: '#fff',
                },
              },
              '& .MuiOutlinedInput-input': {
                color: '#000',
              },
              '& .MuiInputBase-input::placeholder': {
                color: 'rgba(0,0,0,0.5)',
                opacity: 1,
              },
            }}
          />
          <IconButton
            onClick={handleSend}
            disabled={!input.trim() || loading}
            sx={{
              bgcolor: '#fff',
              color: '#667eea',
              '&:hover': {
                bgcolor: 'rgba(255,255,255,0.9)',
              },
              '&:disabled': {
                bgcolor: 'rgba(255,255,255,0.3)',
              },
            }}
          >
            <SendIcon />
          </IconButton>
        </Box>
      </Box>
    </Paper>
  );
};

export default AIChatbot;
