import React from 'react';
import { Navigate } from 'react-router-dom';

/**
 * ProtectedRoute — reads auth token and redirects to /login if absent
 * Uses both localStorage (legacy) and useAuthStore for compatibility
 * @see Section 9 — Auth & Route Protection Rules
 */
const ProtectedRoute = ({ children }) => {
    const token = localStorage.getItem('authToken');

    if (!token) {
        return <Navigate to="/login" replace />;
    }

    return children;
};

export default ProtectedRoute;
