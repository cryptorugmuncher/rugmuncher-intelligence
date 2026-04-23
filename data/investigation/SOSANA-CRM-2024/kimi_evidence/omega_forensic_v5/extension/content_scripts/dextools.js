/**
 * RMI Extension - DexTools Integration
 */

(function() {
  'use strict';

  const RMI_API_BASE = 'https://intel.cryptorugmunch.com/api';
  const CACHE_DURATION = 5 * 60 * 1000;
  let scannedTokens = new Map();

  const RISK_COLORS = {
    critical: { bg: '#ef4444', text: '#ffffff' },
    high: { bg: '#f97316', text: '#ffffff' },
    medium: { bg: '#eab308', text: '#000000' },
    low: { bg: '#22c55e', text: '#ffffff' },
    safe: { bg: '#10b981', text: '#ffffff' },
    unknown: { bg: '#6b7280', text: '#ffffff' }
  };

  function init() {
    checkConsent().then(hasConsent => {
      if (hasConsent) {
        startMonitoring();
      }
    });
  }

  async function checkConsent() {
    const result = await chrome.storage.local.get(['rmi_consent']);
    return result.rmi_consent === true;
  }

  function startMonitoring() {
    scanPage();
    
    const observer = new MutationObserver(debouncedScan);
    observer.observe(document.body, { childList: true, subtree: true });
  }

  let scanTimeout;
  function debouncedScan() {
    clearTimeout(scanTimeout);
    scanTimeout = setTimeout(scanPage, 500);
  }

  async function scanPage() {
    const addresses = extractTokenAddresses();
    
    for (const address of addresses) {
      if (!scannedTokens.has(address)) {
        const data = await fetchTokenData(address);
        if (data) {
          scannedTokens.set(address, { data, timestamp: Date.now() });
          injectWarning(address, data);
        }
      }
    }
  }

  function extractTokenAddresses() {
    const addresses = new Set();
    
    // From URL
    const urlMatch = location.pathname.match(/\/app\/(?:\w+)\/(?:\w+)\/([a-zA-Z0-9]+)/);
    if (urlMatch) {
      addresses.add(urlMatch[1]);
    }
    
    // From links
    document.querySelectorAll('a[href*="/app/"]').forEach(link => {
      const match = link.href.match(/\/app\/(?:\w+)\/(?:\w+)\/([a-zA-Z0-9]+)/);
      if (match) {
        addresses.add(match[1]);
      }
    });
    
    return Array.from(addresses);
  }

  async function fetchTokenData(address) {
    try {
      const cached = await chrome.storage.local.get(`token_${address}`);
      if (cached[`token_${address}`]) {
        const data = cached[`token_${address}`];
        if (Date.now() - data.cached_at < CACHE_DURATION) {
          return data;
        }
      }
      
      const response = await fetch(`${RMI_API_BASE}/contract-check/${address}`);
      if (!response.ok) return null;
      
      const data = await response.json();
      data.cached_at = Date.now();
      await chrome.storage.local.set({ [`token_${address}`]: data });
      
      return data;
    } catch (error) {
      return null;
    }
  }

  function injectWarning(address, data) {
    const riskLevel = data.risk_level || 'unknown';
    const riskScore = data.overall_score || 0;
    
    // Find token elements
    document.querySelectorAll(`a[href*="${address}"]`).forEach(link => {
      if (link.closest('.rmi-badge-container')) return;
      
      const container = link.closest('.coin-row') || 
                       link.closest('[data-cy="pair-row"]') ||
                       link.parentElement;
      
      if (container) {
        const badge = createBadge(riskLevel, riskScore, data);
        container.style.position = 'relative';
        container.appendChild(badge);
      }
    });
    
    // Detail page
    if (location.pathname.includes(address)) {
      injectDetailWarning(data);
    }
  }

  function createBadge(level, score, data) {
    const colors = RISK_COLORS[level];
    
    const badge = document.createElement('div');
    badge.className = 'rmi-badge-container';
    badge.innerHTML = `
      <div class="rmi-risk-badge rmi-risk-${level}" 
           style="background: ${colors.bg}; color: ${colors.text};"
           data-address="${data.token_address}">
        <span>${getIcon(level)}</span>
        <span>${score}</span>
      </div>
    `;
    
    badge.querySelector('.rmi-risk-badge').addEventListener('click', (e) => {
      e.preventDefault();
      window.open(`https://intel.cryptorugmunch.com/scan/${data.token_address}`, '_blank');
    });
    
    return badge;
  }

  function getIcon(level) {
    const icons = {
      critical: '☠️', high: '⚠️', medium: '⚡',
      low: '✓', safe: '✅', unknown: '?'
    };
    return icons[level] || icons.unknown;
  }

  function injectDetailWarning(data) {
    if (document.getElementById('rmi-dextools-warning')) return;
    
    const header = document.querySelector('#pair-title') ||
                  document.querySelector('h1');
    
    if (!header) return;
    
    const warning = document.createElement('div');
    warning.id = 'rmi-dextools-warning';
    warning.className = `rmi-dextools-warning rmi-warning-${data.risk_level}`;
    warning.innerHTML = `
      <div class="rmi-warning-content">
        <span>${getIcon(data.risk_level)}</span>
        <span>RMI Score: ${data.overall_score}/100 (${data.risk_level.toUpperCase()})</span>
        <a href="https://intel.cryptorugmunch.com/scan/${data.token_address}" target="_blank">
          View Analysis →
        </a>
      </div>
    `;
    
    header.parentElement.insertBefore(warning, header.nextSibling);
  }

  // Add styles
  const style = document.createElement('style');
  style.textContent = `
    .rmi-badge-container {
      position: absolute;
      top: 4px;
      right: 4px;
      z-index: 1000;
    }
    .rmi-risk-badge {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 4px 8px;
      border-radius: 6px;
      font-size: 11px;
      font-weight: 600;
      cursor: pointer;
      box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }
    .rmi-dextools-warning {
      margin: 10px 0;
      padding: 10px 15px;
      border-radius: 8px;
      font-size: 13px;
    }
    .rmi-dextools-warning.rmi-warning-critical { background: rgba(239,68,68,0.2); border: 1px solid #ef4444; }
    .rmi-dextools-warning.rmi-warning-high { background: rgba(249,115,22,0.2); border: 1px solid #f97316; }
    .rmi-dextools-warning.rmi-warning-medium { background: rgba(234,179,8,0.2); border: 1px solid #eab308; }
    .rmi-dextools-warning.rmi-warning-low { background: rgba(34,197,94,0.2); border: 1px solid #22c55e; }
    .rmi-warning-content {
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .rmi-warning-content a {
      color: #00d4ff;
      text-decoration: none;
      margin-left: auto;
    }
  `;
  document.head.appendChild(style);

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
