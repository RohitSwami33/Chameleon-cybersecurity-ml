import { Box, Chip, Tooltip, Typography } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import FilterListIcon from '@mui/icons-material/FilterList';
import useAttackStore from '../../stores/useAttackStore';
import { formatFilters } from '../../lib/commandParser';

/**
 * Filter Badges Component
 * Displays active filters as removable badges
 */
function FilterBadges() {
  const { filters, setFilters, resetFilters, getActiveFilterCount } = useAttackStore();
  const activeFilterCount = getActiveFilterCount();

  // Don't render if no filters are active
  if (activeFilterCount === 0) {
    return null;
  }

  const handleRemoveFilter = (filterKey) => {
    const newFilters = { ...filters };
    delete newFilters[filterKey];
    setFilters(newFilters);
  };

  const getFilterLabel = (key, value) => {
    const labels = {
      ip: 'IP',
      type: 'Type',
      country: 'Country',
      afterDate: 'Time',
    };
    return labels[key] || key;
  };

  const getFilterValue = (key, value) => {
    if (key === 'type') {
      const typeNames = {
        SQLI: 'SQL Injection',
        XSS: 'XSS',
        BRUTE_FORCE: 'Brute Force',
        SSI: 'SSI',
        BENIGN: 'Benign',
      };
      return typeNames[value] || value;
    }

    if (key === 'afterDate') {
      const now = new Date();
      const diff = now - new Date(value);
      const hours = Math.floor(diff / (1000 * 60 * 60));
      const days = Math.floor(hours / 24);

      if (days > 0) {
        return `Last ${days}d`;
      } else if (hours > 0) {
        return `Last ${hours}h`;
      } else {
        const minutes = Math.floor(diff / (1000 * 60));
        return `Last ${minutes}m`;
      }
    }

    return value;
  };

  const filterEntries = Object.entries(filters);

  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        gap: 1,
        padding: '8px 16px',
        background: 'rgba(25, 118, 210, 0.08)',
        borderRadius: '8px',
        border: '1px solid rgba(25, 118, 210, 0.2)',
        flexWrap: 'wrap',
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
        <FilterListIcon sx={{ fontSize: 18, color: '#1976d2' }} />
        <Typography
          variant="caption"
          sx={{
            fontWeight: 600,
            color: '#1976d2',
            textTransform: 'uppercase',
            letterSpacing: '0.5px',
          }}
        >
          Active Filters:
        </Typography>
      </Box>

      {filterEntries.map(([key, value]) => (
        <Tooltip
          key={key}
          title={`${getFilterLabel(key)}: ${getFilterValue(key, value)}`}
          arrow
        >
          <Chip
            label={
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <Typography variant="caption" sx={{ fontWeight: 600, fontSize: '11px' }}>
                  {getFilterLabel(key)}:
                </Typography>
                <Typography variant="caption" sx={{ fontSize: '11px' }}>
                  {getFilterValue(key, value)}
                </Typography>
              </Box>
            }
            onDelete={() => handleRemoveFilter(key)}
            deleteIcon={<CloseIcon sx={{ fontSize: 16 }} />}
            size="small"
            sx={{
              background: 'rgba(25, 118, 210, 0.15)',
              color: '#fff',
              border: '1px solid rgba(25, 118, 210, 0.3)',
              '& .MuiChip-deleteIcon': {
                color: 'rgba(255, 255, 255, 0.7)',
                '&:hover': {
                  color: '#fff',
                },
              },
              '&:hover': {
                background: 'rgba(25, 118, 210, 0.25)',
              },
            }}
          />
        </Tooltip>
      ))}

      {activeFilterCount > 1 && (
        <Chip
          label="Clear All"
          onClick={resetFilters}
          size="small"
          sx={{
            background: 'rgba(244, 67, 54, 0.15)',
            color: '#f44336',
            border: '1px solid rgba(244, 67, 54, 0.3)',
            fontWeight: 600,
            fontSize: '11px',
            cursor: 'pointer',
            '&:hover': {
              background: 'rgba(244, 67, 54, 0.25)',
            },
          }}
        />
      )}
    </Box>
  );
}

export default FilterBadges;
