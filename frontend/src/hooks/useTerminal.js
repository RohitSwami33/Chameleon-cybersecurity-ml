import { useState, useCallback, useRef, useEffect } from 'react';
import { executeCommand } from '../services/api';

/**
 * useTerminal — React hook for the honeypot terminal UI.
 *
 * Manages command history, loading state, and API communication
 * with the /trap/execute endpoint.
 *
 * Usage:
 *   const {
 *     history,          // Array of { type, content, timestamp, score?, hash? }
 *     isLoading,        // Boolean — true while waiting for API response
 *     currentInput,     // Current input string
 *     setCurrentInput,  // Setter for controlled input
 *     handleSubmit,     // Call on Enter key press
 *     clearHistory,     // Reset terminal
 *   } = useTerminal();
 */
export default function useTerminal() {
    const [history, setHistory] = useState([
        {
            type: 'system',
            content: 'Chameleon Honeypot Terminal v2.0 — Type a command and press Enter',
            timestamp: new Date().toISOString(),
        },
    ]);
    const [isLoading, setIsLoading] = useState(false);
    const [currentInput, setCurrentInput] = useState('');
    const terminalEndRef = useRef(null);

    // Auto-scroll to bottom when history changes
    useEffect(() => {
        terminalEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [history]);

    /**
     * Submit a command to /trap/execute.
     * Appends the command and response to history.
     */
    const handleSubmit = useCallback(async (commandOverride) => {
        const command = (commandOverride || currentInput).trim();
        if (!command || isLoading) return;

        // Append the user's command to history
        const commandEntry = {
            type: 'command',
            content: command,
            timestamp: new Date().toISOString(),
        };
        setHistory((prev) => [...prev, commandEntry]);
        setCurrentInput('');
        setIsLoading(true);

        try {
            const result = await executeCommand(command);

            // Append the deceptive response
            const responseEntry = {
                type: 'response',
                content: result.response || result.message || 'No output',
                timestamp: new Date().toISOString(),
                predictionScore: result.prediction_score,
                isMalicious: result.is_malicious,
                hash: result.hash,
            };
            setHistory((prev) => [...prev, responseEntry]);

        } catch (error) {
            // Network error — show as system message
            const errorEntry = {
                type: 'error',
                content: `Connection error: ${error.message || 'Failed to reach server'}`,
                timestamp: new Date().toISOString(),
            };
            setHistory((prev) => [...prev, errorEntry]);
        } finally {
            setIsLoading(false);
        }
    }, [currentInput, isLoading]);

    /**
     * Clear all terminal history.
     */
    const clearHistory = useCallback(() => {
        setHistory([
            {
                type: 'system',
                content: 'Terminal cleared.',
                timestamp: new Date().toISOString(),
            },
        ]);
    }, []);

    return {
        history,
        isLoading,
        currentInput,
        setCurrentInput,
        handleSubmit,
        clearHistory,
        terminalEndRef,
    };
}
