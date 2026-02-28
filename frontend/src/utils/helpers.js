import { format } from 'date-fns';

/**
 * Utility Helpers — Chameleon Forensics
 * Uses design token colors from Section 2
 */

export const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'N/A';
    try {
        return format(new Date(timestamp), 'PPpp');
    } catch (error) {
        console.error('Error formatting date:', error);
        return timestamp;
    }
};

/**
 * Attack type → color mapping using design tokens
 * BENIGN=#00e676, SQLI=#ff3d71, SSI=#ff6584, XSS=#ffab00
 */
export const getAttackTypeColor = (attackType) => {
    switch (attackType?.toUpperCase()) {
        case 'BENIGN':
            return '#00e676';
        case 'SQLI':
            return '#ff3d71';
        case 'XSS':
            return '#ffab00';
        case 'SSI':
            return '#ff6584';
        case 'BRUTE_FORCE':
        case 'BRUTE FORCE':
            return '#7c4dff';
        default:
            return '#3d5a7a';
    }
};

export const getConfidenceLabel = (confidence) => {
    if (confidence < 0.5) return 'Low';
    if (confidence < 0.7) return 'Medium';
    if (confidence < 0.9) return 'High';
    return 'Very High';
};

export const downloadPDF = (blob, filename) => {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    link.parentNode.removeChild(link);
    window.URL.revokeObjectURL(url);
};

export const truncateText = (text, maxLength) => {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '…';
};

export const getClientInfo = async () => {
    const userAgent = navigator.userAgent;
    return {
        user_agent: userAgent,
    };
};
