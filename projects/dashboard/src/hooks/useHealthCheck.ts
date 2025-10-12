/**
 * 🚀 SIMPLE Health Check Hook
 * Optional lightweight health checking without complex proxy logic
 */

'use client';

import { useState, useEffect } from 'react';

export type HealthStatus = 'unknown' | 'online' | 'offline' | 'checking';

export interface UseHealthCheckOptions {
  enabled?: boolean;
  interval?: number; // in milliseconds
  timeout?: number;  // in milliseconds
}

/**
 * Simple health check hook that uses basic fetch with no-cors mode
 * This is a best-effort check - some services may always show as 'unknown'
 * due to CORS restrictions, which is fine for this simple dashboard
 */
export function useHealthCheck(
  url?: string,
  options: UseHealthCheckOptions = {}
): HealthStatus {
  const {
    enabled = true,
    interval = 30000, // 30 seconds
    timeout = 5000     // 5 seconds
  } = options;

  const [status, setStatus] = useState<HealthStatus>('unknown');

  useEffect(() => {
    if (!url || !enabled) {
      setStatus('unknown');
      return;
    }

    let isActive = true;
    let timeoutId: NodeJS.Timeout;

    const checkHealth = async () => {
      if (!isActive) return;

      setStatus('checking');

      try {
        // Create abort controller for timeout
        const controller = new AbortController();
        timeoutId = setTimeout(() => controller.abort(), timeout);

        // Simple fetch with no-cors mode
        // This won't give us detailed status but can detect basic connectivity
        await fetch(url, {
          method: 'HEAD',
          mode: 'no-cors',
          signal: controller.signal,
          cache: 'no-cache'
        });

        clearTimeout(timeoutId);

        if (isActive) {
          // With no-cors, we can't read the actual status
          // If fetch completes without error, assume service is reachable
          setStatus('online');
        }
      } catch (error) {
        clearTimeout(timeoutId);

        if (isActive) {
          if (error instanceof Error && error.name === 'AbortError') {
            setStatus('offline'); // Timeout
          } else {
            setStatus('offline'); // Network error or service down
          }
        }
      }
    };

    // Initial check
    checkHealth();

    // Set up interval for periodic checks
    const intervalId = setInterval(checkHealth, interval);

    // Cleanup function
    return () => {
      isActive = false;
      clearTimeout(timeoutId);
      clearInterval(intervalId);
    };
  }, [url, enabled, interval, timeout]);

  return status;
}

/**
 * Hook for checking multiple services at once
 */
export function useMultipleHealthChecks(
  urls: Array<{ id: string; url?: string }>
): Map<string, HealthStatus> {
  const [statuses, setStatuses] = useState<Map<string, HealthStatus>>(new Map());

  useEffect(() => {
    if (!urls.length) return;

    const healthChecks = new Map<string, HealthStatus>();
    urls.forEach(({ id }) => {
      healthChecks.set(id, 'unknown');
    });
    setStatuses(new Map(healthChecks));

    // This is a simplified approach - in a real app, you might want to
    // use individual useHealthCheck hooks or implement proper batching
    // For now, we'll just set all to unknown and let individual components handle their own checks
  }, [urls]);

  return statuses;
}