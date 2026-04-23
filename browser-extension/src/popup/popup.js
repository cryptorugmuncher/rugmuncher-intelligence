/**
 * Popup Script
 * ============
 * Main logic for the browser extension popup
 */

const API_BASE_URL = 'https://api.cryptorugmunch.com/v1';
const STORAGE_KEY = 'rmi_recent_scans';

// DOM Elements
let addressInput;
let scanBtn;
let chainSelect;
let resultContainer;
let recentScansContainer;
let clearAllBtn;

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
  addressInput = document.getElementById('addressInput');
  scanBtn = document.getElementById('scanBtn');
  chainSelect = document.getElementById('chainSelect');
  resultContainer = document.getElementById('resultContainer');
  recentScansContainer = document.getElementById('recentScans');
  clearAllBtn = document.getElementById('clearAll');

  // Event listeners
  scanBtn.addEventListener('click', handleScan);
  addressInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleScan();
  });
  clearAllBtn.addEventListener('click', clearRecentScans);

  // Quick action buttons
  document.getElementById('portfolioBtn')?.addEventListener('click', () => {
    chrome.tabs.create({ url: 'https://app.cryptorugmunch.com/portfolio' });
  });
  document.getElementById('alertsBtn')?.addEventListener('click', () => {
    chrome.tabs.create({ url: 'https://app.cryptorugmunch.com/alerts' });
  });
  document.getElementById('mapsBtn')?.addEventListener('click', () => {
    chrome.tabs.create({ url: 'https://app.cryptorugmunch.com/munch-maps' });
  });
  document.getElementById('reportBtn')?.addEventListener('click', () => {
    chrome.tabs.create({ url: 'https://app.cryptorugmunch.com/report' });
  });

  // Load recent scans
  loadRecentScans();

  // Try to get address from active tab (if on Etherscan, etc.)
  tryGetAddressFromTab();
});

/**
 * Handle wallet scan
 */
async function handleScan() {
  const address = addressInput.value.trim();
  const chain = chainSelect.value;

  if (!isValidAddress(address, chain)) {
    showError('Please enter a valid wallet address');
    return;
  }

  setLoading(true);
  resultContainer.innerHTML = '';

  try {
    const response = await fetch(`${API_BASE_URL}/analysis/wallet`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        address,
        chain,
        include_patterns: true,
        include_details: true,
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to analyze wallet');
    }

    const data = await response.json();
    displayResults(data, address, chain);
    addToRecentScans(address, chain, data.risk_level);
  } catch (error) {
    showError(error.message || 'Failed to analyze wallet. Please try again.');
  } finally {
    setLoading(false);
  }
}

/**
 * Display scan results
 */
function displayResults(analysis, address, chain) {
  const riskClass = getRiskClass(analysis.risk_level);
  const riskColor = getRiskColor(analysis.risk_level);

  resultContainer.innerHTML = `
    <div class="result-card">
      <div class="risk-header" style="border-color: ${riskColor}">
        <div class="risk-label">Risk Level</div>
        <div class="risk-value" style="color: ${riskColor}">
          ${analysis.risk_level || 'Unknown'}
        </div>
        <div class="risk-score">${analysis.risk_score || 'N/A'}/100</div>
      </div>

      <div style="margin-bottom: 16px;">
        <div style="color: #9ca3af; font-size: 12px; text-transform: uppercase; margin-bottom: 8px;">Address</div>
        <div style="font-family: monospace; font-size: 13px; color: #fff; word-break: break-all;">
          ${address}
        </div>
      </div>

      <div style="margin-bottom: 16px;">
        <div style="color: #9ca3af; font-size: 12px; text-transform: uppercase; margin-bottom: 8px;">Analysis</div>
        <div style="font-size: 13px; color: #fff; line-height: 1.5;">
          ${analysis.analysis || 'No analysis available'}
        </div>
      </div>

      ${analysis.details ? `
        <div style="margin-bottom: 16px;">
          <div style="color: #9ca3af; font-size: 12px; text-transform: uppercase; margin-bottom: 8px;">Details</div>
          <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #374151;">
            <span style="color: #9ca3af;">Balance</span>
            <span style="color: #fff;">${analysis.details.balance} ${getNativeSymbol(chain)}</span>
          </div>
          <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #374151;">
            <span style="color: #9ca3af;">Transactions</span>
            <span style="color: #fff;">${analysis.details.tx_count}</span>
          </div>
          <div style="display: flex; justify-content: space-between; padding: 8px 0;">
            <span style="color: #9ca3af;">First Seen</span>
            <span style="color: #fff;">${formatDate(analysis.details.first_seen)}</span>
          </div>
        </div>
      ` : ''}

      ${analysis.patterns && analysis.patterns.length > 0 ? `
        <div>
          <div style="color: #9ca3af; font-size: 12px; text-transform: uppercase; margin-bottom: 12px;">Detected Patterns</div>
          ${analysis.patterns.map(pattern => `
            <div style="display: flex; align-items: center; gap: 12px; padding: 8px 0; border-bottom: 1px solid #374151;">
              <span class="risk-badge ${getRiskClass(pattern.severity)}">${pattern.severity}</span>
              <span style="color: #fff; flex: 1;">${pattern.type}</span>
              <span style="color: #8b5cf6; font-size: 12px;">${Math.round(pattern.confidence * 100)}%</span>
            </div>
          `).join('')}
        </div>
      ` : ''}

      <div style="margin-top: 16px; padding-top: 16px; border-top: 1px solid #374151;">
        <button
          onclick="chrome.tabs.create({ url: 'https://app.rugmunch.io/wallet/${address}' })"
          style="
            width: 100%;
            background: #8b5cf6;
            border: none;
            border-radius: 8px;
            padding: 12px;
            color: #fff;
            font-weight: 500;
            cursor: pointer;
          "
        >
          View Full Analysis
        </button>
      </div>
    </div>
  `;
}

/**
 * Load recent scans from storage
 */
async function loadRecentScans() {
  try {
    const result = await chrome.storage.local.get([STORAGE_KEY]);
    const scans = result[STORAGE_KEY] || [];
    renderRecentScans(scans);
  } catch (e) {
    console.error('Failed to load recent scans:', e);
  }
}

/**
 * Render recent scans list
 */
function renderRecentScans(scans) {
  if (scans.length === 0) {
    recentScansContainer.innerHTML = `
      <div style="text-align: center; padding: 20px; color: #6b7280; font-size: 13px;">
        No recent scans
      </div>
    `;
    return;
  }

  recentScansContainer.innerHTML = scans.map(scan => `
    <div class="scan-item" style="cursor: pointer;" data-address="${scan.address}" data-chain="${scan.chain}">
      <div class="scan-info">
        <div class="scan-address">${formatAddress(scan.address)}</div>
        <div class="scan-chain">${scan.chain}</div>
      </div>
      <span class="risk-badge ${getRiskClass(scan.riskLevel)}">${scan.riskLevel}</span>
    </div>
  `).join('');

  // Add click handlers
  recentScansContainer.querySelectorAll('.scan-item').forEach(item => {
    item.addEventListener('click', () => {
      addressInput.value = item.dataset.address;
      chainSelect.value = item.dataset.chain;
      handleScan();
    });
  });
}

/**
 * Add scan to recent list
 */
async function addToRecentScans(address, chain, riskLevel) {
  try {
    const result = await chrome.storage.local.get([STORAGE_KEY]);
    let scans = result[STORAGE_KEY] || [];

    // Remove duplicate if exists
    scans = scans.filter(s => s.address !== address);

    // Add to beginning
    scans.unshift({
      address,
      chain,
      riskLevel,
      timestamp: Date.now(),
    });

    // Keep only last 10
    scans = scans.slice(0, 10);

    await chrome.storage.local.set({ [STORAGE_KEY]: scans });
    renderRecentScans(scans);
  } catch (e) {
    console.error('Failed to save scan:', e);
  }
}

/**
 * Clear all recent scans
 */
async function clearRecentScans() {
  try {
    await chrome.storage.local.remove([STORAGE_KEY]);
    renderRecentScans([]);
  } catch (e) {
    console.error('Failed to clear scans:', e);
  }
}

/**
 * Try to get address from current tab
 */
async function tryGetAddressFromTab() {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tab?.url) {
      const url = new URL(tab.url);

      // Etherscan-style URLs
      if (url.hostname.includes('scan')) {
        const address = url.pathname.match(/0x[a-fA-F0-9]{40}/)?.[0];
        if (address) {
          addressInput.value = address;
          // Auto-detect chain
          const chain = detectChainFromUrl(url.hostname);
          if (chain) chainSelect.value = chain;
        }
      }

      // DexTools/DexScreener
      if (url.hostname.includes('dextools') || url.hostname.includes('dexscreener')) {
        const address = url.pathname.match(/0x[a-fA-F0-9]{40}/)?.[0];
        if (address) {
          addressInput.value = address;
        }
      }
    }
  } catch (e) {
    console.error('Failed to get address from tab:', e);
  }
}

/**
 * Detect chain from URL
 */
function detectChainFromUrl(hostname) {
  if (hostname.includes('bscscan')) return 'bsc';
  if (hostname.includes('polygonscan')) return 'polygon';
  if (hostname.includes('arbiscan')) return 'arbitrum';
  if (hostname.includes('optimistic')) return 'optimism';
  if (hostname.includes('basescan')) return 'base';
  if (hostname.includes('solscan')) return 'solana';
  return 'ethereum';
}

/**
 * Validate address
 */
function isValidAddress(address, chain) {
  if (chain === 'solana') {
    return /^[1-9A-HJ-NP-Za-km-z]{32,44}$/.test(address);
  }
  return /^0x[a-fA-F0-9]{40}$/.test(address);
}

/**
 * Get risk CSS class
 */
function getRiskClass(level) {
  const map = {
    'LOW': 'risk-low',
    'MEDIUM': 'risk-medium',
    'HIGH': 'risk-high',
    'CRITICAL': 'risk-critical',
  };
  return map[level] || 'risk-low';
}

/**
 * Get risk color
 */
function getRiskColor(level) {
  const map = {
    'LOW': '#22c55e',
    'MEDIUM': '#f59e0b',
    'HIGH': '#ef4444',
    'CRITICAL': '#dc2626',
  };
  return map[level] || '#9ca3af';
}

/**
 * Format address for display
 */
function formatAddress(address) {
  return `${address.slice(0, 6)}...${address.slice(-4)}`;
}

/**
 * Format date
 */
function formatDate(dateString) {
  if (!dateString) return 'N/A';
  return new Date(dateString).toLocaleDateString();
}

/**
 * Get native symbol for chain
 */
function getNativeSymbol(chain) {
  const map = {
    'ethereum': 'ETH',
    'bsc': 'BNB',
    'polygon': 'MATIC',
    'arbitrum': 'ETH',
    'optimism': 'ETH',
    'base': 'ETH',
    'solana': 'SOL',
  };
  return map[chain] || 'ETH';
}

/**
 * Show error message
 */
function showError(message) {
  resultContainer.innerHTML = `
    <div class="error">
      ${message}
    </div>
  `;
}

/**
 * Set loading state
 */
function setLoading(loading) {
  scanBtn.disabled = loading;
  if (loading) {
    resultContainer.innerHTML = `
      <div class="loading">
        <div class="spinner"></div>
      </div>
    `;
  }
}
