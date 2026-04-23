/**
 * RMI Extension - Popup Script
 * Handles user interactions in the popup
 */

const RMI_API_BASE = 'https://intel.cryptorugmunch.com/api';

// DOM Elements
const elements = {
  scanInput: document.getElementById('rmi-scan-input'),
  scanBtn: document.getElementById('rmi-scan-btn'),
  scanResult: document.getElementById('rmi-scan-result'),
  recentList: document.getElementById('rmi-recent-list'),
  clearRecent: document.getElementById('rmi-clear-recent'),
  watchlistPreview: document.getElementById('rmi-watchlist-preview'),
  viewWatchlist: document.getElementById('rmi-view-watchlist'),
  statScans: document.getElementById('rmi-stat-scans'),
  statThreats: document.getElementById('rmi-stat-threats'),
  statSites: document.getElementById('rmi-stat-sites'),
  pageName: document.getElementById('rmi-page-name'),
  pageUrl: document.getElementById('rmi-page-url'),
  pageIcon: document.getElementById('rmi-page-icon'),
  pageRisk: document.getElementById('rmi-page-risk'),
  settingsModal: document.getElementById('rmi-settings-modal'),
  settingsBtn: document.getElementById('rmi-settings-btn'),
  closeSettings: document.getElementById('rmi-close-settings'),
  apiKeyInput: document.getElementById('rmi-api-key'),
  clearDataBtn: document.getElementById('rmi-clear-data'),
  settingWarnings: document.getElementById('rmi-setting-warnings'),
  settingPhishing: document.getElementById('rmi-setting-phishing'),
  settingNotifications: document.getElementById('rmi-setting-notifications')
};

// Initialize popup
document.addEventListener('DOMContentLoaded', async () => {
  await loadSettings();
  await updateStats();
  await loadRecentScans();
  await loadWatchlist();
  await detectCurrentPage();
  setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
  // Quick scan
  elements.scanBtn.addEventListener('click', handleQuickScan);
  elements.scanInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleQuickScan();
  });
  
  // Clear recent
  elements.clearRecent.addEventListener('click', async () => {
    await chrome.storage.local.set({ recentScans: [] });
    await loadRecentScans();
  });
  
  // View watchlist
  elements.viewWatchlist.addEventListener('click', () => {
    chrome.tabs.create({ url: 'https://intel.cryptorugmunch.com/watchlist' });
  });
  
  // Settings modal
  elements.settingsBtn.addEventListener('click', () => {
    elements.settingsModal.classList.remove('hidden');
  });
  
  elements.closeSettings.addEventListener('click', () => {
    elements.settingsModal.classList.add('hidden');
  });
  
  // Clear data
  elements.clearDataBtn.addEventListener('click', async () => {
    if (confirm('This will clear all cached data and preferences. Continue?')) {
      await chrome.storage.local.clear();
      await loadSettings();
      await updateStats();
      await loadRecentScans();
      await loadWatchlist();
      alert('All data cleared!');
    }
  });
  
  // Settings toggles
  elements.settingWarnings.addEventListener('change', async (e) => {
    await chrome.storage.local.set({ settingWarnings: e.target.checked });
    // Notify content scripts
    notifyContentScripts('settingsChanged', { warnings: e.target.checked });
  });
  
  elements.settingPhishing.addEventListener('change', async (e) => {
    await chrome.storage.local.set({ settingPhishing: e.target.checked });
    notifyContentScripts('settingsChanged', { phishing: e.target.checked });
  });
  
  elements.settingNotifications.addEventListener('change', async (e) => {
    await chrome.storage.local.set({ settingNotifications: e.target.checked });
  });
  
  // API key
  elements.apiKeyInput.addEventListener('change', async (e) => {
    await chrome.storage.local.set({ apiKey: e.target.value });
  });
}

// Load settings
async function loadSettings() {
  const settings = await chrome.storage.local.get([
    'settingWarnings',
    'settingPhishing',
    'settingNotifications',
    'apiKey'
  ]);
  
  elements.settingWarnings.checked = settings.settingWarnings !== false;
  elements.settingPhishing.checked = settings.settingPhishing !== false;
  elements.settingNotifications.checked = settings.settingNotifications !== false;
  elements.apiKeyInput.value = settings.apiKey || '';
}

// Update statistics
async function updateStats() {
  const data = await chrome.storage.local.get(['scanCount', 'threatCount', 'protectedSites']);
  
  elements.statScans.textContent = data.scanCount || 0;
  elements.statThreats.textContent = data.threatCount || 0;
  elements.statSites.textContent = data.protectedSites || 0;
}

// Load recent scans
async function loadRecentScans() {
  const data = await chrome.storage.local.get(['recentScans']);
  const scans = data.recentScans || [];
  
  if (scans.length === 0) {
    elements.recentList.innerHTML = '<div class="rmi-empty">No recent scans</div>';
    return;
  }
  
  elements.recentList.innerHTML = scans.slice(0, 5).map(scan => `
    <div class="rmi-recent-item" data-address="${scan.address}">
      <div class="rmi-recent-info">
        <span class="rmi-recent-symbol">${scan.symbol || scan.address.slice(0, 8) + '...'}</span>
        <span class="rmi-recent-time">${formatTime(scan.timestamp)}</span>
      </div>
      <span class="rmi-recent-score rmi-score-${scan.riskLevel}">${scan.score}/100</span>
    </div>
  `).join('');
  
  // Add click handlers
  elements.recentList.querySelectorAll('.rmi-recent-item').forEach(item => {
    item.addEventListener('click', () => {
      const address = item.dataset.address;
      chrome.tabs.create({ url: `https://intel.cryptorugmunch.com/scan/${address}` });
    });
  });
}

// Load watchlist preview
async function loadWatchlist() {
  const data = await chrome.storage.local.get(['watchlist']);
  const watchlist = data.watchlist || [];
  
  if (watchlist.length === 0) {
    elements.watchlistPreview.innerHTML = '<div class="rmi-empty">No tokens in watchlist</div>';
    return;
  }
  
  elements.watchlistPreview.innerHTML = watchlist.slice(0, 3).map(token => `
    <div class="rmi-watchlist-item">
      <div class="rmi-watchlist-info">
        <span class="rmi-watchlist-symbol">${token.symbol}</span>
      </div>
      <span class="rmi-watchlist-change ${token.change24h >= 0 ? 'positive' : 'negative'}">
        ${token.change24h >= 0 ? '+' : ''}${token.change24h.toFixed(2)}%
      </span>
    </div>
  `).join('');
}

// Detect current page
async function detectCurrentPage() {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    if (!tab) return;
    
    const url = new URL(tab.url);
    const hostname = url.hostname.replace('www.', '');
    
    // Set page info
    elements.pageName.textContent = getSiteName(hostname);
    elements.pageUrl.textContent = hostname;
    elements.pageIcon.textContent = getSiteIcon(hostname);
    
    // Check if supported site
    const supportedSites = ['dexscreener.com', 'dextools.io', 'birdeye.so', 'photon-sol.tinyastro.io'];
    const isSupported = supportedSites.some(site => hostname.includes(site));
    
    if (isSupported) {
      elements.pageRisk.innerHTML = '<span class="rmi-risk-indicator rmi-risk-safe">✅ Protection Active</span>';
    } else {
      elements.pageRisk.innerHTML = '<span class="rmi-risk-indicator rmi-risk-unknown">⚠️ Limited Protection</span>';
    }
    
    // Check for token in URL
    const tokenMatch = tab.url.match(/\/(solana|ethereum|bsc)\/([a-zA-Z0-9]+)/);
    if (tokenMatch) {
      elements.scanInput.value = tokenMatch[2];
    }
    
  } catch (error) {
    console.error('Error detecting page:', error);
  }
}

// Handle quick scan
async function handleQuickScan() {
  const address = elements.scanInput.value.trim();
  
  if (!address) {
    showScanError('Please enter a token address');
    return;
  }
  
  if (address.length < 32) {
    showScanError('Invalid address format');
    return;
  }
  
  // Show loading
  elements.scanResult.innerHTML = '<div class="rmi-loading"><div class="rmi-spinner"></div></div>';
  elements.scanResult.classList.remove('hidden');
  
  try {
    const result = await fetchTokenData(address);
    displayScanResult(result);
    await addToRecentScans(result);
    await updateStats();
  } catch (error) {
    showScanError('Failed to scan token. Please try again.');
  }
}

// Fetch token data
async function fetchTokenData(address) {
  // Check cache first
  const cached = await chrome.storage.local.get(`token_${address}`);
  if (cached[`token_${address}`]) {
    const data = cached[`token_${address}`];
    if (Date.now() - data.cached_at < 5 * 60 * 1000) {
      return data;
    }
  }
  
  // Fetch from API
  const response = await fetch(`${RMI_API_BASE}/contract-check/${address}`);
  
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  
  const data = await response.json();
  data.cached_at = Date.now();
  
  // Cache result
  await chrome.storage.local.set({ [`token_${address}`]: data });
  
  // Update scan count
  const stats = await chrome.storage.local.get(['scanCount']);
  await chrome.storage.local.set({ scanCount: (stats.scanCount || 0) + 1 });
  
  return data;
}

// Display scan result
function displayScanResult(data) {
  const riskLevel = data.risk_level || 'unknown';
  const score = data.overall_score || 0;
  const flags = data.flags || {};
  const redFlags = flags.red || [];
  
  elements.scanResult.className = `rmi-scan-result rmi-risk-${riskLevel}`;
  elements.scanResult.innerHTML = `
    <div class="rmi-result-header">
      <span class="rmi-result-symbol">${data.token_symbol || 'Unknown'}</span>
      <span class="rmi-result-score rmi-score-${riskLevel}">${score}/100</span>
    </div>
    <div class="rmi-result-flags">
      ${redFlags.length > 0 ? `🚩 ${redFlags.slice(0, 2).join(', ')}` : 'No major red flags detected'}
    </div>
    <div class="rmi-result-actions">
      <a href="https://intel.cryptorugmunch.com/scan/${data.token_address}" 
         target="_blank" 
         class="rmi-btn rmi-btn-primary">
        Full Analysis
      </a>
      <button class="rmi-btn rmi-btn-secondary" onclick="addToWatchlist('${data.token_address}', '${data.token_symbol}')">
        Watchlist
      </button>
    </div>
  `;
}

// Show scan error
function showScanError(message) {
  elements.scanResult.className = 'rmi-scan-result rmi-risk-high';
  elements.scanResult.innerHTML = `<div style="color: #ef4444; text-align: center;">${message}</div>`;
  elements.scanResult.classList.remove('hidden');
}

// Add to recent scans
async function addToRecentScans(data) {
  const stored = await chrome.storage.local.get(['recentScans']);
  const scans = stored.recentScans || [];
  
  // Add to beginning
  scans.unshift({
    address: data.token_address,
    symbol: data.token_symbol,
    score: data.overall_score,
    riskLevel: data.risk_level,
    timestamp: Date.now()
  });
  
  // Keep only last 20
  const trimmed = scans.slice(0, 20);
  
  await chrome.storage.local.set({ recentScans: trimmed });
  await loadRecentScans();
}

// Add to watchlist
async function addToWatchlist(address, symbol) {
  const stored = await chrome.storage.local.get(['watchlist']);
  const watchlist = stored.watchlist || [];
  
  // Check if already exists
  if (watchlist.some(t => t.address === address)) {
    alert('Token already in watchlist!');
    return;
  }
  
  watchlist.push({
    address,
    symbol,
    addedAt: Date.now(),
    change24h: 0
  });
  
  await chrome.storage.local.set({ watchlist });
  await loadWatchlist();
  
  alert('Added to watchlist!');
}

// Notify content scripts
async function notifyContentScripts(action, data) {
  const tabs = await chrome.tabs.query({});
  
  for (const tab of tabs) {
    try {
      await chrome.tabs.sendMessage(tab.id, { action, data });
    } catch (e) {
      // Tab may not have content script
    }
  }
}

// Format time
function formatTime(timestamp) {
  const diff = Date.now() - timestamp;
  
  if (diff < 60000) return 'Just now';
  if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
  return `${Math.floor(diff / 86400000)}d ago`;
}

// Get site name
function getSiteName(hostname) {
  const names = {
    'dexscreener.com': 'DexScreener',
    'dextools.io': 'DexTools',
    'birdeye.so': 'Birdeye',
    'photon-sol.tinyastro.io': 'Photon',
    'gmgn.ai': 'GMGN',
    'solscan.io': 'Solscan',
    'etherscan.io': 'Etherscan'
  };
  
  return names[hostname] || hostname;
}

// Get site icon
function getSiteIcon(hostname) {
  const icons = {
    'dexscreener.com': '📊',
    'dextools.io': '📈',
    'birdeye.so': '🐦',
    'photon-sol.tinyastro.io': '⚡',
    'gmgn.ai': '🤖',
    'solscan.io': '🔍',
    'etherscan.io': '⛓️'
  };
  
  return icons[hostname] || '🌐';
}

// Make addToWatchlist available globally
window.addToWatchlist = addToWatchlist;
