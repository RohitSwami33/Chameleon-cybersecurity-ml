/**
 * Command Parser for Threat Hunter Command Bar
 * Parses natural language commands into filter objects
 */

/**
 * Validates an IP address format
 * @param {string} ip - IP address to validate
 * @returns {boolean} - True if valid IP format
 */
function isValidIP(ip) {
  const parts = ip.split('.');
  if (parts.length !== 4) return false;

  return parts.every((part) => {
    const num = parseInt(part, 10);
    return !isNaN(num) && num >= 0 && num <= 255 && part === num.toString();
  });
}

/**
 * Parses a command string into a structured command object
 * @param {string} input - Raw command input from user
 * @returns {Object} - Parsed command with filters and errors
 */
export function parseCommand(input) {
  const result = {
    type: 'filter',
    filters: {},
    errors: [],
  };

  if (!input || input.trim() === '') {
    result.type = 'empty';
    return result;
  }

  const trimmedInput = input.trim().toLowerCase();

  // Check for help command
  if (trimmedInput === 'help' || trimmedInput === '?') {
    result.type = 'help';
    return result;
  }

  // Check for reset/clear command
  if (trimmedInput === 'reset' || trimmedInput === 'clear') {
    result.type = 'action';
    result.action = 'reset';
    return result;
  }

  // Check for export command
  if (trimmedInput === 'export') {
    result.type = 'action';
    result.action = 'export';
    return result;
  }

  // Parse IP filter: ip:1.2.3.4
  const ipMatch = input.match(/ip:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})/);
  if (ipMatch) {
    const ip = ipMatch[1];
    if (isValidIP(ip)) {
      result.filters.ip = ip;
    } else {
      result.errors.push(
        `Invalid IP address: ${ip}. Format should be like 192.168.1.1`
      );
    }
  }

  // Parse type filter: type:sqli, type:xss, etc.
  const typeMatch = input.match(/type:(sqli|xss|brute|ssi|benign)/i);
  if (typeMatch) {
    const typeMap = {
      sqli: 'SQLI',
      xss: 'XSS',
      brute: 'BRUTE_FORCE',
      ssi: 'SSI',
      benign: 'BENIGN',
    };
    result.filters.type = typeMap[typeMatch[1].toLowerCase()];
  }

  // Parse country filter: from:CN, from:US, etc.
  const countryMatch = input.match(/from:([A-Z]{2})/i);
  if (countryMatch) {
    result.filters.country = countryMatch[1].toUpperCase();
  }

  // Parse time filter: last:1h, last:30m, last:7d
  const timeMatch = input.match(/last:(\d+)([hmd])/i);
  if (timeMatch) {
    const value = parseInt(timeMatch[1], 10);
    const unit = timeMatch[2].toLowerCase();
    const now = new Date();

    if (unit === 'h') {
      result.filters.afterDate = new Date(now - value * 60 * 60 * 1000);
    } else if (unit === 'm') {
      result.filters.afterDate = new Date(now - value * 60 * 1000);
    } else if (unit === 'd') {
      result.filters.afterDate = new Date(now - value * 24 * 60 * 60 * 1000);
    }
  }

  // If no filters were parsed and it's not a special command, it might be invalid
  if (
    Object.keys(result.filters).length === 0 &&
    result.type === 'filter' &&
    !result.errors.length
  ) {
    result.type = 'invalid';
    result.errors.push(
      'Unrecognized command. Type "help" for available commands.'
    );
  }

  return result;
}

/**
 * Formats a filter object into a human-readable string
 * @param {Object} filters - Filter object
 * @returns {string} - Formatted filter description
 */
export function formatFilters(filters) {
  const parts = [];

  if (filters.ip) {
    parts.push(`IP: ${filters.ip}`);
  }

  if (filters.type) {
    const typeNames = {
      SQLI: 'SQL Injection',
      XSS: 'Cross-Site Scripting',
      BRUTE_FORCE: 'Brute Force',
      SSI: 'Server-Side Injection',
      BENIGN: 'Benign',
    };
    parts.push(`Type: ${typeNames[filters.type] || filters.type}`);
  }

  if (filters.country) {
    parts.push(`Country: ${filters.country}`);
  }

  if (filters.afterDate) {
    const now = new Date();
    const diff = now - filters.afterDate;
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(hours / 24);

    if (days > 0) {
      parts.push(`Last ${days} day${days > 1 ? 's' : ''}`);
    } else if (hours > 0) {
      parts.push(`Last ${hours} hour${hours > 1 ? 's' : ''}`);
    } else {
      const minutes = Math.floor(diff / (1000 * 60));
      parts.push(`Last ${minutes} minute${minutes > 1 ? 's' : ''}`);
    }
  }

  return parts.join(' • ');
}

/**
 * Gets example commands for help documentation
 * @returns {Array} - Array of command examples
 */
export function getCommandExamples() {
  return [
    {
      command: 'ip:192.168.1.1',
      description: 'Filter attacks from a specific IP address',
    },
    {
      command: 'type:sqli',
      description: 'Filter SQL injection attacks',
    },
    {
      command: 'type:xss',
      description: 'Filter Cross-Site Scripting attacks',
    },
    {
      command: 'from:CN',
      description: 'Filter attacks from China',
    },
    {
      command: 'last:1h',
      description: 'Filter attacks from the last hour',
    },
    {
      command: 'last:30m',
      description: 'Filter attacks from the last 30 minutes',
    },
    {
      command: 'last:7d',
      description: 'Filter attacks from the last 7 days',
    },
    {
      command: 'type:sqli from:CN last:1h',
      description: 'Combine multiple filters (AND logic)',
    },
    {
      command: 'reset',
      description: 'Clear all active filters',
    },
    {
      command: 'export',
      description: 'Export filtered data to CSV',
    },
    {
      command: 'help',
      description: 'Show this help documentation',
    },
  ];
}
