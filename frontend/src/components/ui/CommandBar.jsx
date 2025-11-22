import { useEffect, useCallback, useState } from 'react';
import {
  KBarProvider,
  KBarPortal,
  KBarPositioner,
  KBarAnimator,
  KBarSearch,
  KBarResults,
  useMatches,
  useRegisterActions,
  useKBar,
} from 'kbar';
import { Box, Typography } from '@mui/material';
import { useCommandActions, handleNaturalLanguageCommand } from '../../lib/commandActions';
import useAttackStore from '../../stores/useAttackStore';
import { parseCommand } from '../../lib/commandParser';
import HelpModal from './HelpModal';
import './CommandBar.css';

/**
 * Results Renderer Component
 * Displays filtered command suggestions
 */
function RenderResults() {
  const { results } = useMatches();

  return (
    <KBarResults
      items={results}
      onRender={({ item, active }) =>
        typeof item === 'string' ? (
          <Box
            sx={{
              padding: '8px 16px',
              fontSize: '12px',
              textTransform: 'uppercase',
              opacity: 0.5,
              fontWeight: 600,
              letterSpacing: '0.5px',
            }}
          >
            {item}
          </Box>
        ) : (
          <Box
            sx={{
              padding: '12px 16px',
              background: active ? 'rgba(25, 118, 210, 0.12)' : 'transparent',
              borderLeft: active ? '3px solid #1976d2' : '3px solid transparent',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              transition: 'all 0.2s',
              '&:hover': {
                background: 'rgba(25, 118, 210, 0.08)',
              },
            }}
          >
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
              <Typography
                variant="body2"
                sx={{
                  fontWeight: active ? 600 : 400,
                  color: active ? '#1976d2' : 'inherit',
                }}
              >
                {item.name}
              </Typography>
              {item.subtitle && (
                <Typography
                  variant="caption"
                  sx={{
                    opacity: 0.6,
                    fontSize: '11px',
                  }}
                >
                  {item.subtitle}
                </Typography>
              )}
            </Box>
            {item.shortcut && item.shortcut.length > 0 && (
              <Box
                sx={{
                  display: 'flex',
                  gap: 0.5,
                }}
              >
                {item.shortcut.map((sc) => (
                  <Box
                    key={sc}
                    sx={{
                      padding: '2px 6px',
                      background: 'rgba(255, 255, 255, 0.1)',
                      borderRadius: '4px',
                      fontSize: '11px',
                      fontFamily: 'monospace',
                    }}
                  >
                    {sc}
                  </Box>
                ))}
              </Box>
            )}
          </Box>
        )
      }
    />
  );
}

/**
 * Command Bar Search Component
 * Handles natural language command input
 */
function CommandBarSearch() {
  const { setFilters, addToHistory, resetFilters } = useAttackStore();

  const handleSearch = useCallback(
    (query) => {
      if (!query || query.trim() === '') return;

      const parsed = parseCommand(query);

      // Handle filter commands
      if (parsed.type === 'filter' && Object.keys(parsed.filters).length > 0) {
        setFilters(parsed.filters);
        addToHistory(query);
        return;
      }

      // Handle action commands
      if (parsed.type === 'action') {
        if (parsed.action === 'reset') {
          resetFilters();
          addToHistory(query);
        }
      }

      // Errors are shown in the UI via the parser
      if (parsed.errors && parsed.errors.length > 0) {
        console.warn('Command parsing errors:', parsed.errors);
      }
    },
    [setFilters, addToHistory, resetFilters]
  );

  return (
    <KBarSearch
      className="command-bar-search"
      placeholder="Type a command or search... (e.g., type:sqli from:CN)"
      onKeyDown={(e) => {
        if (e.key === 'Enter' && e.target.value) {
          handleSearch(e.target.value);
        }
      }}
    />
  );
}

/**
 * Command Bar Content Component
 * Contains the search input and results
 */
function CommandBarContent() {
  return (
    <KBarPortal>
      <KBarPositioner
        style={{
          zIndex: 10000,
          background: 'rgba(0, 0, 0, 0.8)',
          backdropFilter: 'blur(8px)',
        }}
      >
        <KBarAnimator
          style={{
            maxWidth: '600px',
            width: '100%',
            background: '#1e1e1e',
            color: '#fff',
            borderRadius: '8px',
            overflow: 'hidden',
            boxShadow: '0 16px 70px rgba(0, 0, 0, 0.5)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
          }}
        >
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
            }}
          >
            {/* Header */}
            <Box
              sx={{
                padding: '12px 16px',
                borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
              }}
            >
              <Typography
                variant="caption"
                sx={{
                  textTransform: 'uppercase',
                  fontWeight: 600,
                  letterSpacing: '1px',
                  opacity: 0.7,
                }}
              >
                Threat Hunter Command Bar
              </Typography>
              <Typography
                variant="caption"
                sx={{
                  opacity: 0.5,
                  fontSize: '10px',
                }}
              >
                Press ESC to close
              </Typography>
            </Box>

            {/* Search Input */}
            <CommandBarSearch />

            {/* Results */}
            <Box
              sx={{
                maxHeight: '400px',
                overflowY: 'auto',
                '&::-webkit-scrollbar': {
                  width: '8px',
                },
                '&::-webkit-scrollbar-track': {
                  background: 'rgba(255, 255, 255, 0.05)',
                },
                '&::-webkit-scrollbar-thumb': {
                  background: 'rgba(255, 255, 255, 0.2)',
                  borderRadius: '4px',
                },
                '&::-webkit-scrollbar-thumb:hover': {
                  background: 'rgba(255, 255, 255, 0.3)',
                },
              }}
            >
              <RenderResults />
            </Box>

            {/* Footer with hints */}
            <Box
              sx={{
                padding: '8px 16px',
                borderTop: '1px solid rgba(255, 255, 255, 0.1)',
                display: 'flex',
                gap: 2,
                fontSize: '11px',
                opacity: 0.6,
              }}
            >
              <Typography variant="caption" sx={{ fontSize: '11px' }}>
                <kbd style={{ padding: '2px 4px', background: 'rgba(255,255,255,0.1)', borderRadius: '2px' }}>↑↓</kbd> Navigate
              </Typography>
              <Typography variant="caption" sx={{ fontSize: '11px' }}>
                <kbd style={{ padding: '2px 4px', background: 'rgba(255,255,255,0.1)', borderRadius: '2px' }}>↵</kbd> Select
              </Typography>
              <Typography variant="caption" sx={{ fontSize: '11px' }}>
                <kbd style={{ padding: '2px 4px', background: 'rgba(255,255,255,0.1)', borderRadius: '2px' }}>ESC</kbd> Close
              </Typography>
            </Box>
          </Box>
        </KBarAnimator>
      </KBarPositioner>
    </KBarPortal>
  );
}

/**
 * Command Bar Provider Component
 * Wraps the application and provides command bar functionality
 */
export function CommandBarProvider({ children }) {
  const [helpOpen, setHelpOpen] = useState(false);
  const actions = useCommandActions();

  // Add help action handler
  const actionsWithHelp = actions.map((action) => {
    if (action.id === 'help') {
      return {
        ...action,
        perform: () => setHelpOpen(true),
      };
    }
    return action;
  });

  return (
    <KBarProvider actions={actionsWithHelp}>
      {children}
      <CommandBarContent />
      <HelpModal open={helpOpen} onClose={() => setHelpOpen(false)} />
    </KBarProvider>
  );
}

/**
 * Command Bar Trigger Button Component
 * Button to open the command bar (alternative to keyboard shortcut)
 */
export function CommandBarTrigger() {
  const { query } = useKBar();

  const handleClick = () => {
    // Toggle the command bar
    query.toggle();
  };

  return (
    <Box
      onClick={handleClick}
      sx={{
        display: 'flex',
        alignItems: 'center',
        gap: 1,
        padding: '6px 12px',
        background: 'rgba(255, 255, 255, 0.05)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        borderRadius: '6px',
        cursor: 'pointer',
        transition: 'all 0.2s',
        '&:hover': {
          background: 'rgba(255, 255, 255, 0.08)',
          border: '1px solid rgba(255, 255, 255, 0.2)',
        },
      }}
    >
      <Typography variant="body2" sx={{ fontSize: '13px' }}>
        Search
      </Typography>
      <Box
        sx={{
          display: 'flex',
          gap: 0.5,
          alignItems: 'center',
        }}
      >
        <Box
          sx={{
            padding: '2px 6px',
            background: 'rgba(255, 255, 255, 0.1)',
            borderRadius: '4px',
            fontSize: '11px',
            fontFamily: 'monospace',
          }}
        >
          {navigator.platform.includes('Mac') ? '⌘' : 'Ctrl'}
        </Box>
        <Box
          sx={{
            padding: '2px 6px',
            background: 'rgba(255, 255, 255, 0.1)',
            borderRadius: '4px',
            fontSize: '11px',
            fontFamily: 'monospace',
          }}
        >
          K
        </Box>
      </Box>
    </Box>
  );
}

/**
 * Hook to register dynamic actions
 * Useful for components that need to add their own actions
 */
export function useRegisterCommandActions(actions) {
  useRegisterActions(actions, [actions]);
}

export default CommandBarProvider;
