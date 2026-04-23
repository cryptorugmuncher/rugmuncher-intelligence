/**
 * Content Script
 * ==============
 * Injected into blockchain explorer pages to highlight risks
 */

(function() {
  'use strict';

  // Prevent multiple injections
  if (window.__RMI_EXTENSION_INJECTED__) return;
  window.__RMI_EXTENSION_INJECTED__ = true;

  const API_URL = 'https://api.cryptorugmunch.com/v1';
  const CACHE_TTL = 5 * 60 * 1000; // 5 minutes
  const analyzedAddresses = new Map();

  // Risk level colors
  const RISK_COLORS = {
    LOW: '#22c55e',
    MEDIUM: '#f59e0b',
    HIGH: '#ef4444',
    CRITICAL: '#dc2626',
  };

  // Initialize
  init();

  function init() {
    console.log('RMI Content Script initialized on', window.location.hostname);

    // Analyze page content
    scanAndHighlightAddresses();

    // Watch for dynamic content changes
    observeMutations();

    // Listen for messages from popup/background
    chrome.runtime?.onMessage?.addListener(handleMessage);
  }

  /**
   * Scan page for addresses and highlight them
   */
  async function scanAndHighlightAddresses() {
    const hostname = window.location.hostname;

    // Find all addresses on page
    const addresses = findAddressesOnPage();
    if (addresses.length === 0) return;

    // Batch analyze unique addresses
    const uniqueAddresses = [...new Set(addresses.map(a => a.address))];
    const analysisResults = await batchAnalyzeAddresses(uniqueAddresses);

    // Highlight each found address
    addresses.forEach(({ element, address }) => {
      const analysis = analysisResults[address.toLowerCase()];
      if (analysis && analysis.risk_level !== 'LOW') {
        highlightAddress(element, address, analysis);
      }
    });
  }

  /**
   * Find all Ethereum addresses on the page
   */
  function findAddressesOnPage() {
    const addresses = [];
    const seen = new Set();

    // Common selectors for blockchain explorers
    const selectors = [
      'a[href*="/address/"]',
      'a[href*="/token/"]',
      'span[data-address]',
      '.address-tag',
      '.hash-tag',
      '[data-testid="addressLink"]',
      '.text-truncate', // Common for truncated addresses
    ];

    selectors.forEach(selector => {
      document.querySelectorAll(selector).forEach(element => {
        const address = extractAddress(element);
        if (address && !seen.has(address.toLowerCase())) {
          seen.add(address.toLowerCase());
          addresses.push({ element, address });
        }
      });
    });

    // Also scan text content for addresses
    const walker = document.createTreeWalker(
      document.body,
      NodeFilter.SHOW_TEXT,
      null,
      false
    );

    let node;
    while (node = walker.nextNode()) {
      const text = node.textContent;
      const match = text.match(/0x[a-fA-F0-9]{40}/);
      if (match) {
        const address = match[0];
        if (!seen.has(address.toLowerCase())) {
          seen.add(address.toLowerCase());
          // Find parent element
          const element = node.parentElement;
          if (element) {
            addresses.push({ element, address });
          }
        }
      }
    }

    return addresses;
  }

  /**
   * Extract address from element
   */
  function extractAddress(element) {
    // Check href
    const href = element.getAttribute('href');
    if (href) {
      const match = href.match(/0x[a-fA-F0-9]{40}/);
      if (match) return match[0];
    }

    // Check data attribute
    const dataAddress = element.getAttribute('data-address');
    if (dataAddress && dataAddress.match(/^0x[a-fA-F0-9]{40}$/)) {
      return dataAddress;
    }

    // Check text content
    const text = element.textContent.trim();
    const match = text.match(/0x[a-fA-F0-9]{40}/);
    if (match) return match[0];

    return null;
  }

  /**
   * Batch analyze addresses
   */
  async function batchAnalyzeAddresses(addresses) {
    const results = {};
    const toAnalyze = [];

    // Check cache first
    addresses.forEach(address => {
      const cached = analyzedAddresses.get(address.toLowerCase());
      if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
        results[address.toLowerCase()] = cached.data;
      } else {
        toAnalyze.push(address);
      }
    });

    if (toAnalyze.length === 0) return results;

    try {
      // Batch API call
      const response = await fetch(`${API_URL}/analysis/batch`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          addresses: toAnalyze,
          chain: detectChain(),
        }),
      });

      if (response.ok) {
        const data = await response.json();

        // Cache results
        Object.entries(data.results || {}).forEach(([address, analysis]) => {
          analyzedAddresses.set(address.toLowerCase(), {
            data: analysis,
            timestamp: Date.now(),
          });
          results[address.toLowerCase()] = analysis;
        });
      }
    } catch (e) {
      console.error('Batch analysis failed:', e);
    }

    return results;
  }

  /**
   * Highlight address element with risk indicator
   */
  function highlightAddress(element, address, analysis) {
    // Skip if already highlighted
    if (element.classList.contains('rmi-highlighted')) return;

    const riskLevel = analysis.risk_level;
    const color = RISK_COLORS[riskLevel] || RISK_COLORS.LOW;

    // Add highlight class
    element.classList.add('rmi-highlighted');
    element.style.cssText = `
      position: relative;
      border-left: 3px solid ${color} !important;
      padding-left: 8px !important;
      background: ${color}10 !important;
    `;

    // Add tooltip
    const tooltip = document.createElement('div');
    tooltip.className = 'rmi-tooltip';
    tooltip.innerHTML = `
      <div class="rmi-tooltip-header">
        <span class="rmi-risk-badge" style="background: ${color}20; color: ${color};">${riskLevel}</span>
        <span class="rmi-score">${analysis.risk_score}/100</span>
      </div>
      <div class="rmi-tooltip-body">
        ${analysis.analysis ? `<p>${analysis.analysis.substring(0, 100)}...</p>` : ''}
        <button class="rmi-view-btn" data-address="${address}">View Analysis</button>
      </div>
    `;

    // Position tooltip
    element.style.position = 'relative';
    element.appendChild(tooltip);

    // Add click handler for view button
    const viewBtn = tooltip.querySelector('.rmi-view-btn');
    if (viewBtn) {
      viewBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        const chain = detectChain();
        const baseUrl = 'https://app.cryptorugmunch.com';
        window.open(`${baseUrl}/wallet/${address}?chain=${chain}`, '_blank');
      });
    }

    // Show/hide tooltip on hover
    element.addEventListener('mouseenter', () => {
      tooltip.classList.add('rmi-visible');
    });
    element.addEventListener('mouseleave', () => {
      tooltip.classList.remove('rmi-visible');
    });
  }

  /**
   * Detect current chain from URL
   */
  function detectChain() {
    const hostname = window.location.hostname;

    if (hostname.includes('bscscan')) return 'bsc';
    if (hostname.includes('polygonscan')) return 'polygon';
    if (hostname.includes('arbiscan')) return 'arbitrum';
    if (hostname.includes('optimistic')) return 'optimism';
    if (hostname.includes('basescan')) return 'base';
    if (hostname.includes('solscan')) return 'solana';
    if (hostname.includes('snowtrace')) return 'avalanche';
    if (hostname.includes('ftmscan')) return 'fantom';
    if (hostname.includes('moonscan')) return 'moonbeam';
    if (hostname.includes('celoscan')) return 'celo';

    return 'ethereum';
  }

  /**
   * Observe DOM mutations for dynamic content
   */
  function observeMutations() {
    const observer = new MutationObserver((mutations) => {
      let shouldScan = false;

      mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
          if (node.nodeType === Node.ELEMENT_NODE) {
            // Check if added node contains addresses
            if (node.querySelector?.('a[href*="/address/"]') ||
                node.textContent?.match?.(/0x[a-fA-F0-9]{40}/)) {
              shouldScan = true;
            }
          }
        });
      });

      if (shouldScan) {
        // Debounce scans with longer delay for performance
        clearTimeout(window.__RMI_SCAN_TIMEOUT__);
        window.__RMI_SCAN_TIMEOUT__ = setTimeout(() => {
          // Limit scan frequency
          const now = Date.now();
          if (now - (window.__RMI_LAST_SCAN__ || 0) < 2000) return;
          window.__RMI_LAST_SCAN__ = now;
          scanAndHighlightAddresses();
        }, 800);
      }
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true,
    });
  }

  /**
   * Handle messages from popup/background
   */
  function handleMessage(request, sender, sendResponse) {
    switch (request.action) {
      case 'scanPage':
        scanAndHighlightAddresses().then(() => {
          sendResponse({ success: true, count: analyzedAddresses.size });
        });
        return true;

      case 'getPageAddresses':
        const addresses = findAddressesOnPage();
        sendResponse({ addresses });
        return false;

      case 'highlightAddress':
        const elements = document.querySelectorAll(`a[href*="${request.address}"]`);
        elements.forEach(el => {
          el.style.backgroundColor = '#8b5cf630';
          el.scrollIntoView({ behavior: 'smooth', block: 'center' });
        });
        sendResponse({ found: elements.length > 0 });
        return false;
    }
  }

  // Add floating action button for quick scan
  addFloatingButton();

  function addFloatingButton() {
    // Check if we're on a supported site
    const hostname = window.location.hostname;
    const supportedSites = [
      'etherscan.io',
      'bscscan.com',
      'polygonscan.com',
      'arbiscan.io',
      'optimistic.etherscan.io',
      'basescan.org',
      'solscan.io',
      'dextools.io',
      'dexscreener.com',
    ];

    if (!supportedSites.some(site => hostname.includes(site))) return;

    const fab = document.createElement('div');
    fab.id = 'rmi-fab';
    fab.innerHTML = `
      <button class="rmi-fab-btn" title="Scan Page for Risks">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
        </svg>
      </button>
    `;

    document.body.appendChild(fab);

    // Add click handler
    fab.querySelector('.rmi-fab-btn').addEventListener('click', async () => {
      const btn = fab.querySelector('.rmi-fab-btn');
      btn.classList.add('rmi-scanning');

      await scanAndHighlightAddresses();

      // Show scan complete notification
      const notification = document.createElement('div');
      notification.className = 'rmi-notification';
      notification.textContent = `Scanned ${analyzedAddresses.size} addresses`;
      document.body.appendChild(notification);

      setTimeout(() => {
        notification.remove();
        btn.classList.remove('rmi-scanning');
      }, 3000);
    });
  }
})();
