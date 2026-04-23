/**
 * Shared Helpers
 * ==============
 * Common utility functions for the extension
 */

/**
 * Risk level configuration
 */
export const RISK_CONFIG = {
  LOW: { color: '#22c55e', class: 'risk-low', threshold: 0 },
  MEDIUM: { color: '#f59e0b', class: 'risk-medium', threshold: 40 },
  HIGH: { color: '#ef4444', class: 'risk-high', threshold: 60 },
  CRITICAL: { color: '#dc2626', class: 'risk-critical', threshold: 80 }
};

/**
 * Chain configuration
 */
export const CHAIN_CONFIG = {
  ethereum: { name: 'Ethereum', symbol: 'ETH', nativeSymbol: 'ETH', scanDomain: 'etherscan.io' },
  bsc: { name: 'BSC', symbol: 'BNB', nativeSymbol: 'BNB', scanDomain: 'bscscan.com' },
  polygon: { name: 'Polygon', symbol: 'MATIC', nativeSymbol: 'MATIC', scanDomain: 'polygonscan.com' },
  arbitrum: { name: 'Arbitrum', symbol: 'ETH', nativeSymbol: 'ETH', scanDomain: 'arbiscan.io' },
  optimism: { name: 'Optimism', symbol: 'ETH', nativeSymbol: 'ETH', scanDomain: 'optimistic.etherscan.io' },
  base: { name: 'Base', symbol: 'ETH', nativeSymbol: 'ETH', scanDomain: 'basescan.org' },
  solana: { name: 'Solana', symbol: 'SOL', nativeSymbol: 'SOL', scanDomain: 'solscan.io' }
};

/**
 * Validate address format
 * @param {string} address - Wallet address
 * @param {string} chain - Chain identifier
 * @returns {boolean}
 */
export function isValidAddress(address, chain = 'ethereum') {
  if (!address || typeof address !== 'string') return false;

  const trimmed = address.trim();

  if (chain === 'solana') {
    // Solana base58 format
    return /^[1-9A-HJ-NP-Za-km-z]{32,44}$/.test(trimmed);
  }

  // EVM address format
  return /^0x[a-fA-F0-9]{40}$/.test(trimmed);
}

/**
 * Detect chain from URL hostname
 * @param {string} hostname
 * @returns {string|null}
 */
export function detectChainFromUrl(hostname) {
  if (!hostname) return null;

  const domainMap = {
    'bscscan.com': 'bsc',
    'polygonscan.com': 'polygon',
    'arbiscan.io': 'arbitrum',
    'optimistic.etherscan.io': 'optimism',
    'basescan.org': 'base',
    'solscan.io': 'solana',
    'snowtrace.io': 'avalanche',
    'ftmscan.com': 'fantom',
    'celoscan.io': 'celo'
  };

  for (const [domain, chain] of Object.entries(domainMap)) {
    if (hostname.includes(domain)) return chain;
  }

  return 'ethereum';
}

/**
 * Get risk CSS class
 * @param {string} level
 * @returns {string}
 */
export function getRiskClass(level) {
  return RISK_CONFIG[level]?.class || 'risk-low';
}

/**
 * Get risk color
 * @param {string} level
 * @returns {string}
 */
export function getRiskColor(level) {
  return RISK_CONFIG[level]?.color || '#9ca3af';
}

/**
 * Get native token symbol for chain
 * @param {string} chain
 * @returns {string}
 */
export function getNativeSymbol(chain) {
  return CHAIN_CONFIG[chain]?.nativeSymbol || 'ETH';
}

/**
 * Get chain display name
 * @param {string} chain
 * @returns {string}
 */
export function getChainDisplayName(chain) {
  return CHAIN_CONFIG[chain]?.name || chain;
}

/**
 * Format address for display (truncate)
 * @param {string} address
 * @param {number} chars - Characters to show at start/end
 * @returns {string}
 */
export function formatAddress(address, chars = 4) {
  if (!address || typeof address !== 'string') return '';
  if (address.length <= chars * 2 + 2) return address;
  return `${address.slice(0, chars + 2)}...${address.slice(-chars)}`;
}

/**
 * Format date string
 * @param {string} dateString
 * @returns {string}
 */
export function formatDate(dateString) {
  if (!dateString) return 'N/A';
  try {
    return new Date(dateString).toLocaleDateString();
  } catch {
    return 'Invalid';
  }
}

/**
 * Format relative time (e.g., "2h ago")
 * @param {number} timestamp
 * @returns {string}
 */
export function formatRelativeTime(timestamp) {
  if (!timestamp) return 'Unknown';

  const seconds = Math.floor((Date.now() - timestamp) / 1000);

  if (seconds < 60) return 'Just now';
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;
  return new Date(timestamp).toLocaleDateString();
}

/**
 * Debounce function
 * @param {Function} func
 * @param {number} wait - Milliseconds
 * @returns {Function}
 */
export function debounce(func, wait = 300) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

/**
 * Retry a function with exponential backoff
 * @param {Function} fn - Async function to retry
 * @param {number} maxRetries
 * @param {number} baseDelay
 * @returns {Promise}
 */
export async function retryWithBackoff(fn, maxRetries = 3, baseDelay = 1000) {
  let lastError;

  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;
      const delay = baseDelay * Math.pow(2, i);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }

  throw lastError;
}

/**
 * Safe JSON parse with fallback
 * @param {string} str
 * @param {*} fallback
 * @returns {*}
 */
export function safeJsonParse(str, fallback = null) {
  try {
    return JSON.parse(str);
  } catch {
    return fallback;
  }
}

/**
 * Extract address from text
 * @param {string} text
 * @returns {string|null}
 */
export function extractAddress(text) {
  if (!text) return null;

  // Match EVM address
  const evmMatch = text.match(/0x[a-fA-F0-9]{40}/);
  if (evmMatch) return evmMatch[0];

  // Match Solana address (base58, 32-44 chars)
  const solMatch = text.match(/[1-9A-HJ-NP-Za-km-z]{32,44}/);
  if (solMatch && !solMatch[0].match(/^0x/)) return solMatch[0];

  return null;
}

/**
 * Check if WebGL is supported
 * @returns {boolean}
 */
export function isWebGLSupported() {
  try {
    const canvas = document.createElement('canvas');
    return !!(window.WebGLRenderingContext &&
      (canvas.getContext('webgl') || canvas.getContext('experimental-webgl')));
  } catch {
    return false;
  }
}

/**
 * Create a cache with TTL
 * @param {number} defaultTtl - Default TTL in ms
 * @returns {Object}
 */
export function createCache(defaultTtl = 5 * 60 * 1000) {
  const cache = new Map();

  return {
    get(key) {
      const item = cache.get(key);
      if (!item) return null;
      if (Date.now() > item.expires) {
        cache.delete(key);
        return null;
      }
      return item.value;
    },

    set(key, value, ttl = defaultTtl) {
      cache.set(key, {
        value,
        expires: Date.now() + ttl
      });
    },

    delete(key) {
      cache.delete(key);
    },

    clear() {
      cache.clear();
    },

    has(key) {
      const item = cache.get(key);
      if (!item) return false;
      if (Date.now() > item.expires) {
        cache.delete(key);
        return false;
      }
      return true;
    }
  };
}

/**
 * Sanitize HTML to prevent XSS
 * @param {string} str
 * @returns {string}
 */
export function sanitizeHtml(str) {
  if (!str) return '';
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

/**
 * Generate a unique ID
 * @returns {string}
 */
export function generateId() {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}
