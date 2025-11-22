import useAttackStore from '../stores/useAttackStore';
import { parseCommand } from './commandParser';
import { exportAttacksToCSV } from './exportUtils';

/**
 * Command Actions Registry for kbar
 * Defines all available commands and their behaviors
 */

/**
 * Hook to generate dynamic command actions
 * @returns {Array} - Array of kbar action objects
 */
export function useCommandActions() {
  const { setFilters, resetFilters, getTopAttackers, addToHistory, commandHistory, getFilteredAttacks, filters } =
    useAttackStore();
  const topAttackers = getTopAttackers();

  const actions = [
    // Recent Commands (Dynamic)
    ...(commandHistory.length > 0
      ? [
          {
            id: 'recent-commands',
            name: 'Recent Commands',
            keywords: ['recent', 'history', 'previous'],
            section: 'History',
            subtitle: `${commandHistory.length} recent commands`,
          },
          ...commandHistory.slice(0, 5).map((cmd, index) => ({
            id: `recent-${index}`,
            name: cmd,
            parent: 'recent-commands',
            keywords: [cmd],
            subtitle: 'Run this command again',
            perform: () => {
              const parsed = parseCommand(cmd);
              if (parsed.type === 'filter' && Object.keys(parsed.filters).length > 0) {
                setFilters(parsed.filters);
                addToHistory(cmd);
              } else if (parsed.type === 'action' && parsed.action === 'reset') {
                resetFilters();
              }
            },
          })),
        ]
      : []),
    // Filter by IP Address
    {
      id: 'filter-ip',
      name: 'Filter by IP Address',
      keywords: ['ip', 'address', 'filter', 'source'],
      section: 'Filters',
      subtitle: 'Enter an IP address to filter attacks',
      perform: () => {
        // This will be handled by the search input parser
      },
    },

    // Filter by Attack Type (Parent)
    {
      id: 'filter-type',
      name: 'Filter by Attack Type',
      keywords: ['type', 'attack', 'filter', 'category'],
      section: 'Filters',
      subtitle: 'Select an attack type to filter',
    },

    // Attack Type Sub-actions
    {
      id: 'filter-type-sqli',
      name: 'SQL Injection',
      parent: 'filter-type',
      keywords: ['sqli', 'sql', 'injection'],
      perform: () => {
        setFilters({ type: 'SQLI' });
        addToHistory('type:sqli');
      },
    },
    {
      id: 'filter-type-xss',
      name: 'Cross-Site Scripting (XSS)',
      parent: 'filter-type',
      keywords: ['xss', 'cross', 'site', 'scripting'],
      perform: () => {
        setFilters({ type: 'XSS' });
        addToHistory('type:xss');
      },
    },
    {
      id: 'filter-type-brute',
      name: 'Brute Force',
      parent: 'filter-type',
      keywords: ['brute', 'force', 'password'],
      perform: () => {
        setFilters({ type: 'BRUTE_FORCE' });
        addToHistory('type:brute');
      },
    },
    {
      id: 'filter-type-ssi',
      name: 'Server-Side Injection (SSI)',
      parent: 'filter-type',
      keywords: ['ssi', 'server', 'injection'],
      perform: () => {
        setFilters({ type: 'SSI' });
        addToHistory('type:ssi');
      },
    },
    {
      id: 'filter-type-benign',
      name: 'Benign Traffic',
      parent: 'filter-type',
      keywords: ['benign', 'safe', 'normal'],
      perform: () => {
        setFilters({ type: 'BENIGN' });
        addToHistory('type:benign');
      },
    },

    // Filter by Country (Parent)
    {
      id: 'filter-country',
      name: 'Filter by Country',
      keywords: ['country', 'from', 'origin', 'location'],
      section: 'Filters',
      subtitle: 'Filter attacks by country of origin',
    },

    // Common countries as sub-actions
    {
      id: 'filter-country-cn',
      name: 'China (CN)',
      parent: 'filter-country',
      keywords: ['china', 'cn'],
      perform: () => {
        setFilters({ country: 'China' });
        addToHistory('from:CN');
      },
    },
    {
      id: 'filter-country-us',
      name: 'United States (US)',
      parent: 'filter-country',
      keywords: ['united', 'states', 'us', 'usa'],
      perform: () => {
        setFilters({ country: 'United States' });
        addToHistory('from:US');
      },
    },
    {
      id: 'filter-country-ru',
      name: 'Russia (RU)',
      parent: 'filter-country',
      keywords: ['russia', 'ru'],
      perform: () => {
        setFilters({ country: 'Russia' });
        addToHistory('from:RU');
      },
    },

    // Filter by Time Range (Parent)
    {
      id: 'filter-time',
      name: 'Filter by Time Range',
      keywords: ['time', 'last', 'recent', 'date'],
      section: 'Filters',
      subtitle: 'Filter attacks by time period',
    },

    // Time range sub-actions
    {
      id: 'filter-time-1h',
      name: 'Last Hour',
      parent: 'filter-time',
      keywords: ['hour', '1h', '60m'],
      perform: () => {
        const now = new Date();
        setFilters({ afterDate: new Date(now - 60 * 60 * 1000) });
        addToHistory('last:1h');
      },
    },
    {
      id: 'filter-time-30m',
      name: 'Last 30 Minutes',
      parent: 'filter-time',
      keywords: ['30', 'minutes', '30m'],
      perform: () => {
        const now = new Date();
        setFilters({ afterDate: new Date(now - 30 * 60 * 1000) });
        addToHistory('last:30m');
      },
    },
    {
      id: 'filter-time-24h',
      name: 'Last 24 Hours',
      parent: 'filter-time',
      keywords: ['24', 'hours', '24h', 'day'],
      perform: () => {
        const now = new Date();
        setFilters({ afterDate: new Date(now - 24 * 60 * 60 * 1000) });
        addToHistory('last:24h');
      },
    },
    {
      id: 'filter-time-7d',
      name: 'Last 7 Days',
      parent: 'filter-time',
      keywords: ['7', 'days', '7d', 'week'],
      perform: () => {
        const now = new Date();
        setFilters({ afterDate: new Date(now - 7 * 24 * 60 * 60 * 1000) });
        addToHistory('last:7d');
      },
    },

    // Top Attackers (Dynamic)
    ...(topAttackers.length > 0
      ? [
          {
            id: 'top-attackers',
            name: 'Filter by Top Attacker',
            keywords: ['top', 'frequent', 'most', 'attacker'],
            section: 'Quick Filters',
            subtitle: `${topAttackers.length} most active attackers`,
          },
          ...topAttackers.map((attacker, index) => ({
            id: `top-attacker-${index}`,
            name: `${attacker.ip} (${attacker.count} attacks)`,
            parent: 'top-attackers',
            keywords: [attacker.ip],
            perform: () => {
              setFilters({ ip: attacker.ip });
              addToHistory(`ip:${attacker.ip}`);
            },
          })),
        ]
      : []),

    // Reset Filters
    {
      id: 'reset-filters',
      name: 'Reset All Filters',
      keywords: ['reset', 'clear', 'remove', 'all'],
      section: 'Actions',
      subtitle: 'Clear all active filters',
      perform: () => {
        resetFilters();
        addToHistory('reset');
      },
    },

    // Export Data
    {
      id: 'export-data',
      name: 'Export Filtered Data',
      keywords: ['export', 'download', 'csv', 'save'],
      section: 'Actions',
      subtitle: 'Download filtered attacks as CSV',
      perform: () => {
        const filteredAttacks = getFilteredAttacks();
        const success = exportAttacksToCSV(filteredAttacks, filters);
        if (success) {
          addToHistory('export');
        }
      },
    },

    // Help
    {
      id: 'help',
      name: 'Show Help',
      keywords: ['help', '?', 'commands', 'guide'],
      section: 'Help',
      subtitle: 'View available commands and syntax',
      perform: () => {
        // This will be implemented in the help documentation task
        console.log('Help modal to be implemented');
      },
    },
  ];

  return actions;
}

/**
 * Handles natural language command input
 * @param {string} query - User's search query
 * @param {Function} setFilters - Function to update filters
 * @param {Function} addToHistory - Function to add command to history
 * @returns {boolean} - True if command was handled
 */
export function handleNaturalLanguageCommand(query, setFilters, addToHistory) {
  const parsed = parseCommand(query);

  if (parsed.type === 'filter' && Object.keys(parsed.filters).length > 0) {
    setFilters(parsed.filters);
    addToHistory(query);
    return true;
  }

  if (parsed.type === 'action') {
    if (parsed.action === 'reset') {
      useAttackStore.getState().resetFilters();
      addToHistory(query);
      return true;
    }
  }

  return false;
}
