import { create } from 'zustand';

/**
 * Auth Store — Chameleon Forensics
 * In-memory auth state (NOT localStorage for security)
 * @see Section 9 — Auth & Route Protection Rules
 */
const useAuthStore = create((set, get) => ({
    // State
    user: null,
    isAuthenticated: false,

    /**
     * Login — stores user + token in memory
     * @param {Object} userData - { username, token }
     */
    login: (userData) =>
        set({
            user: {
                username: userData.username,
                token: userData.token,
            },
            isAuthenticated: true,
        }),

    /**
     * Logout — clears state, caller should redirect to /login
     */
    logout: () =>
        set({
            user: null,
            isAuthenticated: false,
        }),

    /**
     * Get the JWT token for API requests
     * @returns {string|null}
     */
    getToken: () => {
        const { user } = get();
        return user?.token || null;
    },
}));

export default useAuthStore;
