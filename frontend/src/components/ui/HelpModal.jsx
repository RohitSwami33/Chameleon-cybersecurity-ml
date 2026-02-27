import { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  Box,
  Typography,
  IconButton,
  Divider,
  Chip,
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import { getCommandExamples } from '../../lib/commandParser';

/**
 * Help Modal Component
 * Displays command documentation and examples
 */
function HelpModal({ open, onClose }) {
  const examples = getCommandExamples();

  const categories = {
    'Filter Commands': examples.filter((ex) =>
      ['ip:', 'type:', 'from:', 'last:'].some((prefix) =>
        ex.command.startsWith(prefix)
      )
    ),
    'Combined Filters': examples.filter((ex) => ex.command.includes(' ')),
    'Action Commands': examples.filter(
      (ex) => ex.command === 'reset' || ex.command === 'export'
    ),
    'Help Commands': examples.filter((ex) => ex.command === 'help'),
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: {
          background: '#1e1e1e',
          color: '#fff',
          borderRadius: '12px',
        },
      }}
    >
      <DialogTitle
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
        }}
      >
        <Box>
          <Typography variant="h5" sx={{ fontWeight: 700 }}>
            Threat Hunter Command Bar
          </Typography>
          <Typography variant="caption" sx={{ opacity: 0.7 }}>
            Quick reference guide for commands and syntax
          </Typography>
        </Box>
        <IconButton onClick={onClose} sx={{ color: '#fff' }}>
          <CloseIcon />
        </IconButton>
      </DialogTitle>

      <DialogContent sx={{ mt: 2 }}>
        {/* Keyboard Shortcuts */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
            Keyboard Shortcuts
          </Typography>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="body2">Open Command Bar</Typography>
              <Box sx={{ display: 'flex', gap: 0.5 }}>
                <Chip label="Cmd" size="small" sx={{ fontFamily: 'monospace' }} />
                <Typography>+</Typography>
                <Chip label="K" size="small" sx={{ fontFamily: 'monospace' }} />
                <Typography sx={{ opacity: 0.5, ml: 1 }}>or</Typography>
                <Chip label="Ctrl" size="small" sx={{ fontFamily: 'monospace', ml: 1 }} />
                <Typography>+</Typography>
                <Chip label="K" size="small" sx={{ fontFamily: 'monospace' }} />
              </Box>
            </Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="body2">Navigate Suggestions</Typography>
              <Box sx={{ display: 'flex', gap: 0.5 }}>
                <Chip label="↑" size="small" sx={{ fontFamily: 'monospace' }} />
                <Chip label="↓" size="small" sx={{ fontFamily: 'monospace' }} />
              </Box>
            </Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="body2">Execute Command</Typography>
              <Chip label="Enter" size="small" sx={{ fontFamily: 'monospace' }} />
            </Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="body2">Close Command Bar</Typography>
              <Chip label="ESC" size="small" sx={{ fontFamily: 'monospace' }} />
            </Box>
          </Box>
        </Box>

        <Divider sx={{ my: 3, borderColor: 'rgba(255, 255, 255, 0.1)' }} />

        {/* Command Examples by Category */}
        {Object.entries(categories).map(([category, commands]) => (
          <Box key={category} sx={{ mb: 4 }}>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
              {category}
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              {commands.map((example, index) => (
                <Box
                  key={index}
                  sx={{
                    p: 2,
                    background: 'rgba(255, 255, 255, 0.03)',
                    borderRadius: '8px',
                    border: '1px solid rgba(255, 255, 255, 0.05)',
                  }}
                >
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                    <Typography
                      variant="body1"
                      sx={{
                        fontFamily: 'monospace',
                        color: '#4a90e2',
                        fontWeight: 600,
                      }}
                    >
                      {example.command}
                    </Typography>
                  </Box>
                  <Typography variant="body2" sx={{ opacity: 0.7 }}>
                    {example.description}
                  </Typography>
                </Box>
              ))}
            </Box>
          </Box>
        ))}

        <Divider sx={{ my: 3, borderColor: 'rgba(255, 255, 255, 0.1)' }} />

        {/* Tips */}
        <Box sx={{ mb: 2 }}>
          <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
            Tips
          </Typography>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            <Typography variant="body2" sx={{ opacity: 0.8 }}>
              • Combine multiple filters using spaces (e.g., <code style={{ background: 'rgba(255,255,255,0.1)', padding: '2px 6px', borderRadius: '4px' }}>type:sqli from:CN last:1h</code>)
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.8 }}>
              • All filters use AND logic - attacks must match all criteria
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.8 }}>
              • Use the <code style={{ background: 'rgba(255,255,255,0.1)', padding: '2px 6px', borderRadius: '4px' }}>reset</code> command to clear all active filters
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.8 }}>
              • Export filtered data with the <code style={{ background: 'rgba(255,255,255,0.1)', padding: '2px 6px', borderRadius: '4px' }}>export</code> command
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.8 }}>
              • Recent commands are saved and can be accessed from the History section
            </Typography>
          </Box>
        </Box>
      </DialogContent>
    </Dialog>
  );
}

export default HelpModal;
