import { format } from 'date-fns';

export const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'N/A';
    try {
        return format(new Date(timestamp), 'PPpp');
    } catch (error) {
        console.error('Error formatting date:', error);
        return timestamp;
    }
};

export const getAttackTypeColor = (attackType) => {
    switch (attackType?.toLowerCase()) {
        case 'benign':
            return '#4CAF50'; // Green
        case 'sqli':
            return '#F44336'; // Red
        case 'xss':
            return '#FF9800'; // Orange
        case 'ssi':
            return '#E91E63'; // Pink
        case 'brute force':
        case 'brute_force':
            return '#9C27B0'; // Purple
        default:
            return '#757575'; // Grey
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
    return text.substring(0, maxLength) + '...';
};

export const getClientInfo = async () => {
    const userAgent = navigator.userAgent;
    // Ideally we would get the IP from an external service, but for now we'll let the backend handle IP detection
    // or return a placeholder if needed. The backend usually extracts IP from the request headers.
    return {
        user_agent: userAgent,
        // ip_address: '127.0.0.1' // Optional: let backend detect
    };
};
