/**
 * RMI Extension - Birdeye Integration
 */

(function() {
  'use strict';

  const RMI_API_BASE = 'https://intel.cryptorugmunch.com/api';
  let scannedTokens = new Map();

  const RISK_COLORS = {
    critical: '#ef4444', high: '#f97316', medium: '#eab308',
    low: '#22c55e', safe: '#10b981', unknown: '#6b7280'
  };

  function init() {
    checkConsent().then(hasConsent => {
      if (hasConsent) startMonitoring();
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
          scannedTokens.set(address, data);
          injectBadge(address, data);
        }
      }
    }
  }

  function extractTokenAddresses() {
    const addresses = new Set();
    
    // From URL
    const urlMatch = location.pathname.match(/\/token\/([a-zA-Z0-9]+)/);
    if (urlMatch) addresses.add(urlMatch[1]);
    
    // From token links
    document.querySelectorAll('a[href*="/token/"]').forEach(link => {
      const match = link.href.match(/\/token\/([a-zA-Z0-9]+)/);
      if (match) addresses.add(match[1]);
    });
    
    return Array.from(addresses);
  }

  async function fetchTokenData(address) {
    try {
      const cached = await chrome.storage.local.get(`token_${address}`);
      if (cached[`token_${address}`]) {
        const data = cached[`token_${address}`];
        if (Date.now() - data.cached_at < 5 * 60 * 1000) return data;
      }
      
      const response = await fetch(`${RMI_API_BASE}/contract-check/${address}`);
      if (!response.ok) return null;
      
      const data = await response.json();
      data.cached_at = Date.now();
      await chrome.storage.local.set({ [`token_${address}`]: data });
      return data;
    } catch (e) { return null; }
  }

  function injectBadge(address, data) {
    const level = data.risk_level || 'unknown';
    const color = RISK_COLORS[level];
    
    document.querySelectorAll(`a[href*="${address}"]`).forEach(link => {
      if (link.closest('.rmi-badge')) return;
      
      const container = link.closest('.token-row') || link.parentElement;
      if (!container) return;
      
      const badge = document.createElement('span');
      badge.className = 'rmi-badge';
      badge.style.cssText = `
        display: inline-flex;
        align-items: center;
        gap: 4px;
        margin-left: 8px;
        padding: 2px 8px;
        background: ${color}20;
        border: 1px solid ${color};
        border-radius: 4px;
        font-size: 11px;
        font-weight: 600;
        color: ${color};
        cursor: pointer;
      `;
      badge.innerHTML = `${getIcon(level)} ${data.overall_score}/100`;
      
      badge.addEventListener('click', (e) => {
        e.preventDefault();
        window.open(`https://intel.cryptorugmunch.com/scan/${address}`, '_blank');
      });
      
      link.appendChild(badge);
    });
  }

  function getIcon(level) {
    const icons = { critical: '☠️', high: '⚠️', medium: '⚡', low: '✓', safe: '✅', unknown: '?' };
    return icons[level] || icons.unknown;
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
