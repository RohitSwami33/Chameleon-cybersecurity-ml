/**
 * Export Utilities for Threat Hunter
 * Handles CSV export of filtered attack data
 */

/**
 * Converts attack data to CSV format
 * @param {Array} attacks - Array of attack objects
 * @param {Object} filters - Active filters
 * @returns {string} - CSV formatted string
 */
export function attacksToCSV(attacks, filters = {}) {
  if (!attacks || attacks.length === 0) {
    return '';
  }

  // CSV Headers
  const headers = [
    'Timestamp',
    'IP Address',
    'Attack Type',
    'Confidence',
    'Country',
    'City',
    'Latitude',
    'Longitude',
    'Method',
    'Path',
  ];

  // Convert attacks to CSV rows
  const rows = attacks.map((attack) => {
    return [
      attack.timestamp || '',
      attack.ip_address || '',
      attack.classification?.attack_type || '',
      attack.classification?.confidence || '',
      attack.geo_location?.country || '',
      attack.geo_location?.city || '',
      attack.geo_location?.latitude || '',
      attack.geo_location?.longitude || '',
      attack.request_data?.method || '',
      attack.request_data?.path || '',
    ];
  });

  // Combine headers and rows
  const csvContent = [
    headers.join(','),
    ...rows.map((row) =>
      row.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(',')
    ),
  ].join('\n');

  return csvContent;
}

/**
 * Generates a filename for the export
 * @param {Object} filters - Active filters
 * @returns {string} - Filename with timestamp and filters
 */
export function generateExportFilename(filters = {}) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
  const filterParts = [];

  if (filters.ip) {
    filterParts.push(`ip-${filters.ip.replace(/\./g, '-')}`);
  }
  if (filters.type) {
    filterParts.push(`type-${filters.type.toLowerCase()}`);
  }
  if (filters.country) {
    filterParts.push(`country-${filters.country}`);
  }
  if (filters.afterDate) {
    const now = new Date();
    const diff = now - new Date(filters.afterDate);
    const hours = Math.floor(diff / (1000 * 60 * 60));
    filterParts.push(`last-${hours}h`);
  }

  const filterString = filterParts.length > 0 ? `_${filterParts.join('_')}` : '';
  return `chameleon_attacks_${timestamp}${filterString}.csv`;
}

/**
 * Triggers a browser download of CSV data
 * @param {string} csvContent - CSV formatted string
 * @param {string} filename - Filename for download
 */
export function downloadCSV(csvContent, filename) {
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');

  if (link.download !== undefined) {
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }
}

/**
 * Main export function - converts attacks to CSV and triggers download
 * @param {Array} attacks - Array of attack objects
 * @param {Object} filters - Active filters
 * @returns {boolean} - True if export succeeded
 */
export function exportAttacksToCSV(attacks, filters = {}) {
  try {
    if (!attacks || attacks.length === 0) {
      throw new Error('No data to export');
    }

    const csvContent = attacksToCSV(attacks, filters);
    const filename = generateExportFilename(filters);

    downloadCSV(csvContent, filename);

    return true;
  } catch (error) {
    console.error('Export failed:', error);
    return false;
  }
}
