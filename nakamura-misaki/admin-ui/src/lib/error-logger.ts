/**
 * Frontend error logging utility
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8010';

interface ErrorLog {
  message: string;
  stack?: string;
  url?: string;
  user_agent?: string;
  timestamp: string;
}

export async function logError(error: Error, additionalInfo?: Record<string, unknown>) {
  try {
    const errorLog: ErrorLog = {
      message: error.message,
      stack: error.stack,
      url: typeof window !== 'undefined' ? window.location.href : undefined,
      user_agent: typeof window !== 'undefined' ? window.navigator.userAgent : undefined,
      timestamp: new Date().toISOString(),
    };

    // Add additional context
    if (additionalInfo) {
      (errorLog as ErrorLog & { context?: Record<string, unknown> }).context = additionalInfo;
    }

    // Send to backend
    await fetch(`${API_BASE_URL}/api/logs/errors`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(errorLog),
    });

    console.error('Error logged to backend:', error);
  } catch (logError) {
    // If logging fails, at least log to console
    console.error('Failed to log error to backend:', logError);
    console.error('Original error:', error);
  }
}

// Global error handlers
if (typeof window !== 'undefined') {
  // Catch unhandled errors
  window.onerror = function (message, source, lineno, colno, error) {
    if (error) {
      logError(error, { source, lineno, colno });
    } else {
      logError(new Error(String(message)), { source, lineno, colno });
    }
    return false; // Let default handler run
  };

  // Catch unhandled promise rejections
  window.onunhandledrejection = function (event) {
    const error = event.reason instanceof Error
      ? event.reason
      : new Error(String(event.reason));

    logError(error, { type: 'unhandled_rejection' });
  };
}
