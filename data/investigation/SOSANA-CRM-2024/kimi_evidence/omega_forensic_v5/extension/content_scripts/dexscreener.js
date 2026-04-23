/**
 * RMI Extension - DexScreener Integration
 * Adds risk scores and warnings to token pages on DexScreener
 */

(function() {
  'use strict';

  // RMI API Configuration
  const RMI_API_BASE = 'https://intel.cryptorugmunch.com/api';
  const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

  // State
  let scannedTokens = new Map(); // Cache for token data
  let observer = null;
  let currentUrl = location.href;

  // Risk level colors
  const RISK_COLORS = {
    critical: { bg: '#ef4444', text: '#ffffff', border: '#dc2626' },
    high: { bg: '#f97316', text: '#ffffff', border: '#ea580c' },
    medium: { bg: '#eab308', text: '#000000', border: '#ca8a04' },
    low: { bg: '#22c55e', text: '#ffffff', border: '#16a34a' },
    safe: { bg: '#10b981', text: '#ffffff', border: '#059669' },
    unknown: { bg: '#6b7280', text: '#ffffff', border: '#4b5563' }
  };

  // Initialize
  function init() {
    console.log('[RMI] DexScreener integration loaded');
    
    // Check user consent
    checkConsent().then(hasConsent => {
      if (!hasConsent) {
        showConsentBanner();
        return;
      }
      
      startMonitoring();
    });
  }

  // Check if user has given consent
  async function checkConsent() {
    const result = await chrome.storage.local.get(['rmi_consent']);
    return result.rmi_consent === true;
  }

  // Show consent banner
  function showConsentBanner() {
    const banner = document.createElement('div');
    banner.id = 'rmi-consent-banner';
    banner.innerHTML = `
      <div class="rmi-consent-content">
        <div class="rmi-consent-icon">🛡️</div>
        <div class="rmi-consent-text">
          <strong>RMI Fraud Protection</strong>
          <p>Enable real-time scam detection on DexScreener? We analyze tokens for rug pull risks, honeypots, and suspicious patterns.</p>
        </div>
        <div class="rmi-consent-buttons">
          <button id="rmi-consent-yes" class="rmi-btn rmi-btn-primary">Enable Protection</button>
          <button id="rmi-consent-no" class="rmi-btn rmi-btn-secondary">Not Now</button>
        </div>
      </div>
    `;
    
    document.body.appendChild(banner);
    
    // Add styles
    const style = document.createElement('style');
    style.textContent = `
      #rmi-consent-banner {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 400px;
        max-width: calc(100vw - 40px);
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid #00d4ff;
        border-radius: 12px;
        padding: 20px;
        z-index: 999999;
        box-shadow: 0 10px 40px rgba(0, 212, 255, 0.3);
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        animation: rmi-slide-in 0.3s ease-out;
      }
      
      @keyframes rmi-slide-in {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
      }
      
      .rmi-consent-content {
        display: flex;
        flex-direction: column;
        gap: 15px;
      }
      
      .rmi-consent-icon {
        font-size: 32px;
        text-align: center;
      }
      
      .rmi-consent-text {
        color: #fff;
      }
      
      .rmi-consent-text strong {
        display: block;
        font-size: 16px;
        margin-bottom: 8px;
        color: #00d4ff;
      }
      
      .rmi-consent-text p {
        margin: 0;
        font-size: 13px;
        line-height: 1.5;
        color: #aaa;
      }
      
      .rmi-consent-buttons {
        display: flex;
        gap: 10px;
      }
      
      .rmi-btn {
        flex: 1;
        padding: 10px 16px;
        border: none;
        border-radius: 8px;
        font-size: 13px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
      }
      
      .rmi-btn-primary {
        background: linear-gradient(90deg, #00d4ff, #0099cc);
        color: #000;
      }
      
      .rmi-btn-primary:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 212, 255, 0.4);
      }
      
      .rmi-btn-secondary {
        background: #333;
        color: #aaa;
      }
      
      .rmi-btn-secondary:hover {
        background: #444;
        color: #fff;
      }
    `;
    document.head.appendChild(style);
    
    // Handle buttons
    document.getElementById('rmi-consent-yes').addEventListener('click', async () => {
      await chrome.storage.local.set({ rmi_consent: true, rmi_consent_date: new Date().toISOString() });
      banner.remove();
      startMonitoring();
    });
    
    document.getElementById('rmi-consent-no').addEventListener('click', () => {
      banner.remove();
    });
  }

  // Start monitoring the page
  function startMonitoring() {
    // Initial scan
    scanPage();
    
    // Watch for URL changes (SPA navigation)
    setInterval(() => {
      if (location.href !== currentUrl) {
        currentUrl = location.href;
        setTimeout(scanPage, 1000); // Delay for page to load
      }
    }, 500);
    
    // Watch for DOM changes
    observer = new MutationObserver((mutations) => {
      const hasNewTokens = mutations.some(m => {
        return Array.from(m.addedNodes).some(node => {
          if (node.nodeType === Node.ELEMENT_NODE) {
            return node.querySelector && (
              node.querySelector('[data-testid="token-link"]') ||
              node.querySelector('a[href*="/solana/"]') ||
              node.querySelector('.ds-dex-table-row')
            );
          }
          return false;
        });
      });
      
      if (hasNewTokens) {
        debouncedScan();
      }
    });
    
    observer.observe(document.body, { childList: true, subtree: true });
  }

  // Debounced scan
  let scanTimeout;
  function debouncedScan() {
    clearTimeout(scanTimeout);
    scanTimeout = setTimeout(scanPage, 500);
  }

  // Main scan function
  async function scanPage() {
    const tokenAddresses = extractTokenAddresses();
    
    for (const address of tokenAddresses) {
      if (!scannedTokens.has(address) || isCacheExpired(address)) {
        const data = await fetchTokenData(address);
        if (data) {
          scannedTokens.set(address, { data, timestamp: Date.now() });
          injectWarning(address, data);
        }
      }
    }
  }

  // Extract token addresses from page
  function extractTokenAddresses() {
    const addresses = new Set();
    
    // From URL
    const urlMatch = location.pathname.match(/\/(solana|ethereum|bsc)\/([a-zA-Z0-9]+)/);
    if (urlMatch) {
      addresses.add(urlMatch[2]);
    }
    
    // From token links
    document.querySelectorAll('a[href*="/solana/"]').forEach(link => {
      const match = link.href.match(/\/solana\/([a-zA-Z0-9]+)/);
      if (match) {
        addresses.add(match[1]);
      }
    });
    
    // From table rows
    document.querySelectorAll('.ds-dex-table-row, [data-testid="token-row"]').forEach(row => {
      const link = row.querySelector('a[href*="/solana/"]');
      if (link) {
        const match = link.href.match(/\/solana\/([a-zA-Z0-9]+)/);
        if (match) {
          addresses.add(match[1]);
        }
      }
    });
    
    return Array.from(addresses);
  }

  // Check if cache is expired
  function isCacheExpired(address) {
    const cached = scannedTokens.get(address);
    if (!cached) return true;
    return Date.now() - cached.timestamp > CACHE_DURATION;
  }

  // Fetch token data from RMI API
  async function fetchTokenData(address) {
    try {
      // Check cache first
      const cached = await chrome.storage.local.get(`token_${address}`);
      if (cached[`token_${address}`]) {
        const data = cached[`token_${address}`];
        if (Date.now() - data.cached_at < CACHE_DURATION) {
          return data;
        }
      }
      
      // Fetch from API
      const response = await fetch(`${RMI_API_BASE}/contract-check/${address}`, {
        headers: {
          'X-Extension-Version': '2.0.0'
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const data = await response.json();
      
      // Cache the result
      data.cached_at = Date.now();
      await chrome.storage.local.set({ [`token_${address}`]: data });
      
      return data;
    } catch (error) {
      console.error('[RMI] Error fetching token data:', error);
      return null;
    }
  }

  // Inject warning badge into page
  function injectWarning(address, data) {
    const riskLevel = data.risk_level || 'unknown';
    const riskScore = data.overall_score || 0;
    
    // Find all elements for this token
    const selectors = [
      `a[href*="/solana/${address}"]`,
      `a[href*="/ethereum/${address}"]`,
      `a[href*="/bsc/${address}"]`
    ];
    
    selectors.forEach(selector => {
      document.querySelectorAll(selector).forEach(element => {
        // Don't inject if already has RMI badge
        if (element.closest('.rmi-badge-container')) return;
        
        // Find the container to inject into
        let container = element.closest('.ds-dex-table-row') ||
                       element.closest('[data-testid="token-row"]') ||
                       element.parentElement;
        
        if (!container) return;
        
        // Create badge
        const badge = createRiskBadge(riskLevel, riskScore, data);
        
        // Find appropriate insertion point
        const target = container.querySelector('.ds-dex-table-row-base-token') ||
                      container.querySelector('.custom-1') ||
                      container.querySelector('div:first-child');
        
        if (target) {
          target.style.position = 'relative';
          target.appendChild(badge);
        }
      });
    });
    
    // Also inject on token detail page
    if (location.pathname.includes(address)) {
      injectDetailPageWarning(address, data);
    }
  }

  // Create risk badge element
  function createRiskBadge(riskLevel, riskScore, data) {
    const colors = RISK_COLORS[riskLevel] || RISK_COLORS.unknown;
    
    const badge = document.createElement('div');
    badge.className = 'rmi-badge-container';
    badge.innerHTML = `
      <div class="rmi-risk-badge rmi-risk-${riskLevel}" data-address="${data.token_address}">
        <span class="rmi-badge-icon">${getRiskIcon(riskLevel)}</span>
        <span class="rmi-badge-text">${riskScore}/100</span>
        <span class="rmi-badge-label">${riskLevel.toUpperCase()}</span>
      </div>
      <div class="rmi-tooltip">
        <div class="rmi-tooltip-header">
          <span class="rmi-tooltip-title">RMI Risk Analysis</span>
          <span class="rmi-tooltip-score rmi-score-${riskLevel}">${riskScore}/100</span>
        </div>
        <div class="rmi-tooltip-content">
          ${generateTooltipContent(data)}
        </div>
        <div class="rmi-tooltip-footer">
          <a href="https://intel.cryptorugmunch.com/scan/${data.token_address}" target="_blank" class="rmi-tooltip-link">
            Full Analysis →
          </a>
        </div>
      </div>
    `;
    
    // Add click handler
    badge.querySelector('.rmi-risk-badge').addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      showDetailedModal(data);
    });
    
    return badge;
  }

  // Get icon for risk level
  function getRiskIcon(level) {
    const icons = {
      critical: '☠️',
      high: '⚠️',
      medium: '⚡',
      low: '✓',
      safe: '✅',
      unknown: '?'
    };
    return icons[level] || icons.unknown;
  }

  // Generate tooltip content
  function generateTooltipContent(data) {
    const flags = data.flags || {};
    const redFlags = flags.red || [];
    const yellowFlags = flags.yellow || [];
    const greenFlags = flags.green || [];
    
    let content = '';
    
    if (redFlags.length > 0) {
      content += `<div class="rmi-flags-red"><strong>🚩 Red Flags:</strong><ul>${redFlags.map(f => `<li>${f}</li>`).join('')}</ul></div>`;
    }
    
    if (yellowFlags.length > 0) {
      content += `<div class="rmi-flags-yellow"><strong>⚡ Warnings:</strong><ul>${yellowFlags.map(f => `<li>${f}</li>`).join('')}</ul></div>`;
    }
    
    if (greenFlags.length > 0) {
      content += `<div class="rmi-flags-green"><strong>✅ Good Signs:</strong><ul>${greenFlags.slice(0, 2).map(f => `<li>${f}</li>`).join('')}</ul></div>`;
    }
    
    if (!content) {
      content = '<p>No detailed analysis available.</p>';
    }
    
    return content;
  }

  // Inject warning on token detail page
  function injectDetailPageWarning(address, data) {
    // Check if already injected
    if (document.getElementById('rmi-detail-warning')) return;
    
    const riskLevel = data.risk_level || 'unknown';
    const colors = RISK_COLORS[riskLevel];
    
    // Find insertion point - try multiple selectors
    const insertionPoints = [
      document.querySelector('.ds-header-title'),
      document.querySelector('h1'),
      document.querySelector('[data-testid="token-header"]'),
      document.querySelector('.custom-2')?.parentElement
    ];
    
    const insertionPoint = insertionPoints.find(el => el !== null);
    if (!insertionPoint) return;
    
    const warning = document.createElement('div');
    warning.id = 'rmi-detail-warning';
    warning.className = `rmi-detail-warning rmi-warning-${riskLevel}`;
    warning.innerHTML = `
      <div class="rmi-warning-header">
        <span class="rmi-warning-icon">${getRiskIcon(riskLevel)}</span>
        <div class="rmi-warning-title">
          <strong>RMI Risk Score: ${data.overall_score || '?'}/100</strong>
          <span class="rmi-warning-level">${riskLevel.toUpperCase()} RISK</span>
        </div>
        <button class="rmi-warning-toggle">View Details</button>
      </div>
      <div class="rmi-warning-details" style="display: none;">
        ${generateDetailContent(data)}
      </div>
    `;
    
    // Insert after the header element
    insertionPoint.parentElement.insertBefore(warning, insertionPoint.nextSibling);
    
    // Add toggle handler
    warning.querySelector('.rmi-warning-toggle').addEventListener('click', () => {
      const details = warning.querySelector('.rmi-warning-details');
      const isVisible = details.style.display !== 'none';
      details.style.display = isVisible ? 'none' : 'block';
      warning.querySelector('.rmi-warning-toggle').textContent = isVisible ? 'View Details' : 'Hide Details';
    });
  }

  // Generate detailed content for modal/detail view
  function generateDetailContent(data) {
    const categoryScores = data.category_scores || {};
    
    return `
      <div class="rmi-detail-grid">
        <div class="rmi-detail-section">
          <h4>Category Scores</h4>
          <div class="rmi-score-bars">
            ${Object.entries(categoryScores).map(([cat, score]) => `
              <div class="rmi-score-bar">
                <span class="rmi-score-label">${cat.replace('_', ' ').toUpperCase()}</span>
                <div class="rmi-score-bar-bg">
                  <div class="rmi-score-bar-fill" style="width: ${score}%; background: ${getScoreColor(score)}"></div>
                </div>
                <span class="rmi-score-value">${score}</span>
              </div>
            `).join('')}
          </div>
        </div>
        
        <div class="rmi-detail-section">
          <h4>Analysis</h4>
          <p>${data.recommendation || 'No detailed analysis available.'}</p>
        </div>
        
        <div class="rmi-detail-actions">
          <a href="https://intel.cryptorugmunch.com/scan/${data.token_address}" target="_blank" class="rmi-btn rmi-btn-primary">
            View Full Analysis
          </a>
          <button class="rmi-btn rmi-btn-secondary" onclick="window.rmiAddToWatchlist('${data.token_address}')">
            Add to Watchlist
          </button>
        </div>
      </div>
    `;
  }

  // Get color for score
  function getScoreColor(score) {
    if (score >= 80) return '#10b981';
    if (score >= 60) return '#22c55e';
    if (score >= 40) return '#eab308';
    if (score >= 20) return '#f97316';
    return '#ef4444';
  }

  // Show detailed modal
  function showDetailedModal(data) {
    // Remove existing modal
    const existing = document.getElementById('rmi-modal');
    if (existing) existing.remove();
    
    const modal = document.createElement('div');
    modal.id = 'rmi-modal';
    modal.className = 'rmi-modal';
    modal.innerHTML = `
      <div class="rmi-modal-overlay"></div>
      <div class="rmi-modal-content">
        <div class="rmi-modal-header">
          <h2>RMI Risk Analysis</h2>
          <button class="rmi-modal-close">&times;</button>
        </div>
        <div class="rmi-modal-body">
          ${generateDetailContent(data)}
        </div>
      </div>
    `;
    
    document.body.appendChild(modal);
    
    // Close handlers
    modal.querySelector('.rmi-modal-close').addEventListener('click', () => modal.remove());
    modal.querySelector('.rmi-modal-overlay').addEventListener('click', () => modal.remove());
    
    // Close on escape
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') modal.remove();
    }, { once: true });
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
