import { Box, Typography, Paper, Grid, Card, CardContent, Chip } from '@mui/material';
import { motion } from 'framer-motion';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import SecurityIcon from '@mui/icons-material/Security';
import BugReportIcon from '@mui/icons-material/BugReport';
import TipsAndUpdatesIcon from '@mui/icons-material/TipsAndUpdates';
import SchoolIcon from '@mui/icons-material/School';
import SearchIcon from '@mui/icons-material/Search';
import Navbar from '../components/Navbar';
import AIChatbot from '../components/AIChatbot';

const ChatbotPage = () => {
  const features = [
    { icon: <SecurityIcon />, title: 'Threat Analysis', description: 'Understand attack patterns and security risks', color: '#ff3d71' },
    { icon: <BugReportIcon />, title: 'Vulnerability Insights', description: 'Get recommendations for hardening systems', color: '#ffab00' },
    { icon: <SchoolIcon />, title: 'Security Training', description: 'Learn about the latest cybersecurity techniques', color: '#00e676' },
    { icon: <SearchIcon />, title: 'Web Search', description: 'Search the web for current threat intelligence', color: '#7c4dff' },
  ];

  return (
    <Box sx={{ flexGrow: 1, minHeight: '100vh', position: 'relative', zIndex: 2 }}>
      <Navbar />

      <Box sx={{ px: 2, py: 3 }}>
        <Typography variant="h4" sx={{
          fontWeight: 700, mb: 3,
          fontFamily: '"Rajdhani", sans-serif',
          color: '#e8f4fd',
          fontSize: 'clamp(1.5rem, 3vw, 2rem)',
        }}>
          AI Security Assistant
        </Typography>

        <Grid container spacing={2}>
          {/* Chatbot */}
          <Grid item xs={12} md={8}>
            <Box sx={{ height: 600 }}>
              <AIChatbot />
            </Box>
          </Grid>

          {/* Features & Tips */}
          <Grid item xs={12} md={4}>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, height: '100%' }}>
              {/* Quick Tips */}
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" sx={{ fontWeight: 600, fontSize: '0.9rem', mb: 1.5, color: '#e8f4fd', display: 'flex', alignItems: 'center', gap: 1 }}>
                  <TipsAndUpdatesIcon sx={{ fontSize: 18, color: '#ffab00' }} />
                  Quick Tips
                </Typography>
                {[
                  'Ask about specific attack types like SQL injection or XSS',
                  'Enable Web Search for current threat intelligence',
                  'Request security hardening recommendations for your stack',
                ].map((tip, i) => (
                  <Typography key={i} variant="body2" sx={{
                    color: '#7a9bbf', fontSize: '0.75rem', mb: 0.8,
                    pl: 2, borderLeft: '2px solid rgba(255, 171, 0, 0.3)',
                  }}>
                    {tip}
                  </Typography>
                ))}
              </Paper>

              {/* Feature Cards */}
              {features.map((feature, i) => (
                <motion.div key={i} initial={{ opacity: 0, x: 10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.08 }}>
                  <Card sx={{
                    background: `linear-gradient(135deg, ${feature.color}08 0%, transparent 100%)`,
                    border: `1px solid ${feature.color}18`,
                  }}>
                    <CardContent sx={{ py: 1.5, '&:last-child': { pb: 1.5 } }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                        <Box sx={{ color: feature.color, display: 'flex', '& > svg': { fontSize: 18 } }}>
                          {feature.icon}
                        </Box>
                        <Typography variant="body2" sx={{ fontWeight: 600, color: '#e8f4fd', fontSize: '0.8rem' }}>
                          {feature.title}
                        </Typography>
                      </Box>
                      <Typography variant="caption" sx={{ color: '#7a9bbf', fontSize: '0.7rem' }}>
                        {feature.description}
                      </Typography>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </Box>
          </Grid>
        </Grid>
      </Box>
    </Box>
  );
};

export default ChatbotPage;
