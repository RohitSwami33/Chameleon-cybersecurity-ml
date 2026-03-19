import { Box, Chip, Tooltip, Typography } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import FilterListIcon from '@mui/icons-material/FilterList';
import useAttackStore from '../../stores/useAttackStore';

/**
 * Filter Badges Component
 * @see Section 5 — FilterBadges Rules
 * Displays active filters as removable badges with design token colors
 */
function FilterBadges() {
  const { filters, setFilters, resetFilters, getActiveFilterCount } = useAttackStore();
  const activeFilterCount = getActiveFilterCount();

  if (activeFilterCount === 0) return null;

  const handleRemoveFilter = (filterKey) => {
    const newFilters = { ...filters };
    delete newFilters[filterKey];
    setFilters(newFilters);
  };

  const getFilterLabel = (key) => {
    const labels = { ip: 'IP', type: 'Type', country: 'Country', afterDate: 'Time' };
    return labels[key] || key;
  };

  const getFilterValue = (key, value) => {
    if (key === 'type') {
      const typeNames = { SQLI: 'SQL Injection', XSS: 'XSS', BRUTE_FORCE: 'Brute Force', SSI: 'SSI', BENIGN: 'Benign' };
      return typeNames[value] || value;
    }
    if (key === 'afterDate') {
      const now = new Date();
      const diff = now - new Date(value);
      const hours = Math.floor(diff / (1000 * 60 * 60));
      const days = Math.floor(hours / 24);
      if (days > 0) return `Last ${days}d`;
      if (hours > 0) return `Last ${hours}h`;
      return `Last ${Math.floor(diff / (1000 * 60))}m`;
    }
    return value;
  };

  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        gap: 1,
        padding: '6px 12px',
        background: 'rgba(0, 212, 255, 0.04)',
        borderRadius: '8px',
        border: '1px solid rgba(0, 212, 255, 0.12)',
        flexWrap: 'wrap',
        mb: 2,
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
        <FilterListIcon sx={{ fontSize: 16, color: '#00d4ff' }} />
        <Typography
          variant="caption"
          sx={{
            fontWeight: 600,
            color: '#00d4ff',
            textTransform: 'uppercase',
            letterSpacing: '0.5px',
            fontSize: '0.65rem',
            fontFamily: '"DM Sans", sans-serif',
          }}
        >
          Active Filters:
        </Typography>
      </Box>

      {Object.entries(filters).map(([key, value]) => (
        <Tooltip key={key} title={`${getFilterLabel(key)}: ${getFilterValue(key, value)}`} arrow>
          <Chip
            label={
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <Typography variant="caption" sx={{ fontWeight: 700, fontSize: '0.7rem', color: '#e8f4fd' }}>
                  {getFilterLabel(key)}:
                </Typography>
                <Typography variant="caption" sx={{ fontSize: '0.7rem', color: '#7a9bbf' }}>
                  {getFilterValue(key, value)}
                </Typography>
              </Box>
            }
            onDelete={() => handleRemoveFilter(key)}
            deleteIcon={<CloseIcon sx={{ fontSize: 14 }} />}
            size="small"
            sx={{
              background: 'rgba(0, 212, 255, 0.1)',
              color: '#e8f4fd',
              border: '1px solid rgba(0, 212, 255, 0.2)',
              '& .MuiChip-deleteIcon': {
                color: 'rgba(0, 212, 255, 0.5)',
                '&:hover': { color: '#00d4ff' },
              },
              '&:hover': {
                background: 'rgba(0, 212, 255, 0.18)',
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
            background: 'rgba(255, 61, 113, 0.1)',
            color: '#ff3d71',
            border: '1px solid rgba(255, 61, 113, 0.25)',
            fontWeight: 600,
            fontSize: '0.7rem',
            cursor: 'pointer',
            '&:hover': {
              background: 'rgba(255, 61, 113, 0.2)',
            },
          }}
        />
      )}
    </Box>
  );
}

export default FilterBadges;
