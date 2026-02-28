import { create } from 'zustand';
import { persist } from 'zustand/middleware';

/**
 * Attack Store — Chameleon Forensics
 * Centralized state for attacks, filters, live mode, mock geo, and threat scores
 * @see Section 4 — State Management Rules
 */
const useAttackStore = create(
  persist(
    (set, get) => ({
      // State
      attacks: [],
      liveMode: true,
      mockGeo: true,
      filters: { ip: undefined, type: undefined },
      threatScores: {},
      commandHistory: [],
      loading: false,
      error: null,

      // Actions
      setAttacks: (attacks) => set({ attacks: attacks.slice(0, 500) }),

      prependAttacks: (newAttacks) =>
        set((state) => ({
          attacks: [...newAttacks, ...state.attacks].slice(0, 500),
        })),

      setLiveMode: (liveMode) => set({ liveMode }),

      setMockGeo: (mockGeo) => set({ mockGeo }),

      setFilters: (newFilters) =>
        set((state) => ({
          filters: { ...state.filters, ...newFilters },
        })),

      setFilter: (key, value) =>
        set((state) => ({
          filters: { ...state.filters, [key]: value },
        })),

      resetFilters: () => set({ filters: {} }),

      setThreatScores: (scores) => set({ threatScores: scores }),

      addToHistory: (command) =>
        set((state) => ({
          commandHistory: [
            command,
            ...state.commandHistory.filter((c) => c !== command),
          ].slice(0, 50),
        })),

      clearHistory: () => set({ commandHistory: [] }),

      setLoading: (loading) => set({ loading }),

      setError: (error) => set({ error }),

      // Computed selectors
      getFilteredAttacks: () => {
        const { attacks, filters } = get();

        return attacks.filter((attack) => {
          if (filters.ip && attack.ip_address !== filters.ip) {
            return false;
          }

          if (
            filters.type &&
            attack.classification?.attack_type !== filters.type
          ) {
            return false;
          }

          if (
            filters.country &&
            attack.geo_location?.country !== filters.country
          ) {
            return false;
          }

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
        return Object.keys(filters).filter((k) => filters[k] !== undefined).length;
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
