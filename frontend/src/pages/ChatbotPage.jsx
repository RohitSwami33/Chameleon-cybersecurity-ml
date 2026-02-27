import { Box, Container, Typography, Paper } from '@mui/material';
import Navbar from '../components/Navbar';
import AIChatbot from '../components/AIChatbot';
import SmartToyIcon from '@mui/icons-material/SmartToy';

const ChatbotPage = () => {
  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
      <Navbar />
      
      <Container maxWidth="xl" sx={{ py: 4 }}>
        {/* Page Header */}
        <Box sx={{ mb: 4 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
            <SmartToyIcon sx={{ fontSize: 40, color: 'primary.main' }} />
            <Typography variant="h3" component="h1" sx={{ fontWeight: 700 }}>
              AI Security Assistant
            </Typography>
          </Box>
          <Typography variant="body1" color="text.secondary" sx={{ maxWidth: 800 }}>
            Get instant cybersecurity insights powered by Gemini AI. Ask questions about threats, 
            analyze attacks, search for current threat intelligence, and get expert recommendations 
            for incident response.
          </Typography>
        </Box>

        {/* Features Overview */}
        <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 2, mb: 4 }}>
          <Paper sx={{ p: 2, bgcolor: 'background.paper' }}>
            <Typography variant="h6" gutterBottom sx={{ color: 'primary.main' }}>
              🤖 AI-Powered
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Advanced Gemini 2.5 Pro model for intelligent, context-aware responses
            </Typography>
          </Paper>
          
          <Paper sx={{ p: 2, bgcolor: 'background.paper' }}>
            <Typography variant="h6" gutterBottom sx={{ color: 'primary.main' }}>
              🔍 Web Search
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Real-time threat intelligence from DuckDuckGo with source citations
            </Typography>
          </Paper>
          
          <Paper sx={{ p: 2, bgcolor: 'background.paper' }}>
            <Typography variant="h6" gutterBottom sx={{ color: 'primary.main' }}>
              📊 Attack Analysis
            </Typography>
            <Typography variant="body2" color="text.secondary">
              AI-powered analysis of attack logs with mitigation recommendations
            </Typography>
          </Paper>
          
          <Paper sx={{ p: 2, bgcolor: 'background.paper' }}>
            <Typography variant="h6" gutterBottom sx={{ color: 'primary.main' }}>
              💡 Smart Suggestions
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Get response recommendations based on threat levels and attack types
            </Typography>
          </Paper>
        </Box>

        {/* Chatbot Interface */}
        <Box sx={{ height: 'calc(100vh - 400px)', minHeight: 600 }}>
          <AIChatbot />
        </Box>

        {/* Quick Tips */}
        <Paper sx={{ mt: 4, p: 3, bgcolor: 'background.paper' }}>
          <Typography variant="h6" gutterBottom>
            💡 Quick Tips
          </Typography>
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 2 }}>
            <Box>
              <Typography variant="subtitle2" color="primary.main" gutterBottom>
                Ask About:
              </Typography>
              <Typography variant="body2" color="text.secondary" component="ul" sx={{ pl: 2 }}>
                <li>Attack patterns and techniques (SQL injection, XSS, etc.)</li>
                <li>Latest CVE vulnerabilities and security advisories</li>
                <li>Threat mitigation strategies and best practices</li>
                <li>Security tool usage and configuration</li>
              </Typography>
            </Box>
            <Box>
              <Typography variant="subtitle2" color="primary.main" gutterBottom>
                Pro Tips:
              </Typography>
              <Typography variant="body2" color="text.secondary" component="ul" sx={{ pl: 2 }}>
                <li>Enable "Web Search" for current threat intelligence</li>
                <li>Use quick questions for common security topics</li>
                <li>Copy responses to clipboard for documentation</li>
                <li>Clear history to start fresh conversations</li>
              </Typography>
            </Box>
          </Box>
        </Paper>
      </Container>
    </Box>
  );
};

export default ChatbotPage;
