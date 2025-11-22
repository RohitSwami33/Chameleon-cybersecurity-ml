import { create } from 'zustand';
import { persist } from 'zustand/middleware';

/**
 * Attack Store with Filter State Management
 * Centralized state for attacks, filters, and command history
 */
const useAttackStore = create(
  persist(
    (set, get) => ({
      // State
      attacks: [],
      filters: {},
      commandHistory: [],
      loading: false,
      error: null,

      // Actions
      setAttacks: (attacks) => set({ attacks }),

      setFilters: (newFilters) =>
        set((state) => ({
          filters: { ...state.filters, ...newFilters },
        })),

      resetFilters: () => set({ filters: {} }),

      addToHistory: (command) =>
        set((state) => ({
          commandHistory: [
            command,
            ...state.commandHistory.filter((c) => c !== command),
          ].slice(0, 50), // Keep only 50 most recent, remove duplicates
        })),

      clearHistory: () => set({ commandHistory: [] }),

      setLoading: (loading) => set({ loading }),

      setError: (error) => set({ error }),

      // Computed selectors
      getFilteredAttacks: () => {
        const { attacks, filters } = get();

        return attacks.filter((attack) => {
          // IP filter
          if (filters.ip && attack.ip_address !== filters.ip) {
            return false;
          }

          // Attack type filter
          if (
            filters.type &&
            attack.classification?.attack_type !== filters.type
          ) {
            return false;
          }

          // Country filter
          if (
            filters.country &&
            attack.geo_location?.country !== filters.country
          ) {
            return false;
          }

          // Time filter
          if (filters.afterDate) {
            const attackDate = new Date(attack.timestamp);
            if (attackDate < filters.afterDate) {
              return false;
            }
          }

          return true;
        });
      },

      getTopAttackers: () => {
        const { attacks } = get();
        const ipCounts = {};

        attacks.forEach((attack) => {
          const ip = attack.ip_address;
          ipCounts[ip] = (ipCounts[ip] || 0) + 1;
        });

        return Object.entries(ipCounts)
          .sort(([, a], [, b]) => b - a)
          .slice(0, 5)
          .map(([ip, count]) => ({ ip, count }));
      },

      getActiveFilterCount: () => {
        const { filters } = get();
        return Object.keys(filters).length;
      },
    }),
    {
      name: 'attack-store',
      partialize: (state) => ({
        commandHistory: state.commandHistory,
      }),
    }
  )
);

export default useAttackStore;
