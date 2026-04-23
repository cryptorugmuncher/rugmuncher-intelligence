/**
 * Sentry Error Tracking (Stub)
 * =============================
 * Stub implementation - Sentry dependencies not installed
 * To enable: npm install @sentry/react @sentry/tracing
 */

const SENTRY_DSN = import.meta.env.VITE_SENTRY_DSN;
const ENVIRONMENT = import.meta.env.MODE || 'development';

// Stub Sentry object
type SeverityLevel = 'fatal' | 'error' | 'warning' | 'log' | 'info' | 'debug';

const stubSentry = {
  init: () => {},
  captureException: (error: Error) => console.error('Sentry:', error),
  captureMessage: (message: string) => console.log('Sentry:', message),
  setUser: () => {},
  startTransaction: () => null,
  getCurrentHub: () => ({
    getScope: () => ({
      getTransaction: () => null,
    }),
  }),
};

// Initialize Sentry only in production with DSN configured
export function initSentry() {
  if (!SENTRY_DSN || ENVIRONMENT === 'development') {
    console.log('Sentry disabled (no DSN or in development)');
    return;
  }
  console.log('Sentry stub - install @sentry/react to enable full functionality');
}

// Error boundary fallback component
export function SentryFallback({ error, resetError }: { error: Error; resetError: () => void }) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-[#12121a] p-4">
      <div className="max-w-md w-full text-center">
        <h2 className="text-2xl font-bold text-white mb-4">Something went wrong</h2>
        <p className="text-gray-400 mb-6">
          We've been notified and are working to fix the issue.
        </p>
        <div className="space-x-4">
          <button
            onClick={resetError}
            className="px-6 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg"
          >
            Try Again
          </button>
          <button
            onClick={() => window.location.reload()}
            className="px-6 py-2 bg-[#2a2a3e] hover:bg-[#3a3a4e] text-white rounded-lg"
          >
            Reload Page
          </button>
        </div>
        {import.meta.env.DEV && (
          <pre className="mt-6 text-left text-xs text-red-400 bg-[#0f0f1a] p-4 rounded-lg overflow-auto">
            {error.stack}
          </pre>
        )}
      </div>
    </div>
  );
}

// Manual error capture helpers
export const captureError = (error: Error, context?: Record<string, any>) => {
  console.error('Error:', error, context);
};

export const captureMessage = (message: string, _level: SeverityLevel = 'info') => {
  console.log(`[${_level}]`, message);
};

// Set user context
export const setUser = (user: { id: string; email?: string; tier?: string } | null) => {
  if (user) {
    console.log('Sentry setUser:', user.id);
  }
};

// Performance monitoring helpers (stubs)
export const startTransaction = (_name: string, _op: string) => {
  return null;
};

export const startSpan = (_name: string, _op: string) => {
  return null;
};

export { stubSentry as Sentry };
