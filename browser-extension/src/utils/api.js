/**
 * API Utilities
 * =============
 * HTTP client for RMI API
 */

const API_BASE_URL = 'https://api.cryptorugmunch.com/v1';
const WS_BASE_URL = 'wss://api.cryptorugmunch.com/ws';

/**
 * Make authenticated API request
 */
async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;

  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  // Add auth token if available
  try {
    const result = await chrome.storage.local.get(['rmi_auth_token']);
    if (result.rmi_auth_token) {
      defaultOptions.headers['Authorization'] = `Bearer ${result.rmi_auth_token}`;
    }
  } catch (e) {
    // No token available
  }

  const response = await fetch(url, {
    ...defaultOptions,
    ...options,
    headers: {
      ...defaultOptions.headers,
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: 'Request failed' }));
    throw new Error(error.message || `HTTP ${response.status}`);
  }

  return response.json();
}

/**
 * Analyze wallet address
 */
export async function analyzeWallet(address, chain = 'ethereum') {
  return apiRequest('/analysis/wallet', {
    method: 'POST',
    body: JSON.stringify({
      address,
      chain,
      include_patterns: true,
      include_details: true,
    }),
  });
}

/**
 * Batch analyze addresses
 */
export async function batchAnalyzeAddresses(addresses, chain = 'ethereum') {
  return apiRequest('/analysis/batch', {
    method: 'POST',
    body: JSON.stringify({ addresses, chain }),
  });
}

/**
 * Get token analysis
 */
export async function analyzeToken(address, chain = 'ethereum') {
  return apiRequest('/analysis/token', {
    method: 'POST',
    body: JSON.stringify({ address, chain }),
  });
}

/**
 * Get recent alerts
 */
export async function getRecentAlerts(limit = 20) {
  return apiRequest(`/alerts/recent?limit=${limit}`);
}

/**
 * Get whale alerts
 */
export async function getWhaleAlerts(limit = 20) {
  return apiRequest(`/alerts/whale?limit=${limit}`);
}

/**
 * Get user profile
 */
export async function getUserProfile() {
  return apiRequest('/user/profile');
}

/**
 * Update user settings
 */
export async function updateUserSettings(settings) {
  return apiRequest('/user/settings', {
    method: 'PUT',
    body: JSON.stringify(settings),
  });
}

/**
 * Get WebSocket URL
 */
export function getWebSocketUrl() {
  return WS_BASE_URL;
}

/**
 * Validate address format
 */
export function isValidAddress(address, chain = 'ethereum') {
  if (chain === 'solana') {
    // Solana base58 format
    return /^[1-9A-HJ-NP-Za-km-z]{32,44}$/.test(address);
  }
  // EVM address format
  return /^0x[a-fA-F0-9]{40}$/.test(address);
}

/**
 * Format address for display
 */
export function formatAddress(address, chars = 4) {
  if (!address) return '';
  if (address.length <= chars * 2 + 2) return address;
  return `${address.slice(0, chars + 2)}...${address.slice(-chars)}`;
}

/**
 * Get chain display name
 */
export function getChainDisplayName(chain) {
  const names = {
    'ethereum': 'Ethereum',
    'bsc': 'BSC',
    'polygon': 'Polygon',
    'arbitrum': 'Arbitrum',
    'optimism': 'Optimism',
    'base': 'Base',
    'solana': 'Solana',
    'avalanche': 'Avalanche',
    'fantom': 'Fantom',
  };
  return names[chain] || chain;
}

/**
 * Get native token symbol
 */
export function getNativeSymbol(chain) {
  const symbols = {
    'ethereum': 'ETH',
    'bsc': 'BNB',
    'polygon': 'MATIC',
    'arbitrum': 'ETH',
    'optimism': 'ETH',
    'base': 'ETH',
    'solana': 'SOL',
    'avalanche': 'AVAX',
    'fantom': 'FTM',
  };
  return symbols[chain] || 'ETH';
}
