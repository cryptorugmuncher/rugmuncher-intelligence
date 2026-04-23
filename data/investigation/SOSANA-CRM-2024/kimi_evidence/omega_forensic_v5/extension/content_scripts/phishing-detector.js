/**
 * RMI Extension - Phishing Detector
 * Detects and warns about phishing sites
 */

(function() {
  'use strict';

  // Known phishing patterns
  const PHISHING_PATTERNS = {
    // Fake DEX patterns
    dex: [
      /pancak[e]*swap/i,
      /unis[wv]+ap/i,
      /sush[i]+swap/i,
      /1[i]+nch/i,
      /curve[-_]*fi/i,
      /balancer[-_]*fi/i
    ],
    
    // Fake wallet patterns
    wallet: [
      /metamas[k$]+/i,
      /phant[o]+m/i,
      /solflar[e]+/i,
      /trust[-_]*wallet/i,
      /coinbas[e]+/i,
      /exodus[-_]*wallet/i
    ],
    
    // Fake bridge patterns
    bridge: [
      /wormhol[e]+/i,
      /allbridg[e]+/i,
      /hop[-_]*exchange/i,
      /across[-_]*protocol/i
    ],
    
    // Fake NFT patterns
    nft: [
      /opensea[-_]*market/i,
      /blur[-_]*io/i,
      /magiceden[-_]*io/i
    ]
  };

  // Suspicious TLDs
  const SUSPICIOUS_TLDS = ['.tk', '.ml', '.ga', '.cf', '.gq'];

  // Check if current site is suspicious
  function checkSite() {
    const hostname = window.location.hostname.toLowerCase();
    const fullUrl = window.location.href.toLowerCase();
    
    // Check for suspicious TLDs
    for (const tld of SUSPICIOUS_TLDS) {
      if (hostname.endsWith(tld)) {
        reportSuspicious('suspicious_tld', { tld });
        return;
      }
    }
    
    // Check for phishing patterns
    for (const [category, patterns] of Object.entries(PHISHING_PATTERNS)) {
      for (const pattern of patterns) {
        if (pattern.test(hostname) || pattern.test(fullUrl)) {
          reportSuspicious('phishing_pattern', { 
            category, 
            pattern: pattern.toString(),
            hostname 
          });
          
          // Show warning if enabled
          checkAndShowWarning();
          return;
        }
      }
    }
    
    // Check for wallet connection requests on suspicious sites
    monitorWalletConnections();
  }

  // Monitor for wallet connection attempts
  function monitorWalletConnections() {
    // Override common wallet provider methods
    if (window.ethereum) {
      const originalRequest = window.ethereum.request;
      window.ethereum.request = async function(...args) {
        // Check if this is a connection request
        const method = args[0]?.method;
        if (method === 'eth_requestAccounts' || method === 'wallet_connect') {
          // Verify site is legitimate
          const isLegit = await verifySiteLegitimacy();
          if (!isLegit) {
            showWalletWarning();
          }
        }
        return originalRequest.apply(this, args);
      };
    }
    
    // Monitor for Phantom wallet
    if (window.solana) {
      const originalConnect = window.solana.connect;
      window.solana.connect = async function(...args) {
        const isLegit = await verifySiteLegitimacy();
        if (!isLegit) {
          showWalletWarning();
        }
        return originalConnect.apply(this, args);
      };
    }
  }

  // Verify site legitimacy
  async function verifySiteLegitimacy() {
    const hostname = window.location.hostname;
    
    // Check against known legitimate sites
    const legitSites = [
      'app.uniswap.org',
      'pancakeswap.finance',
      'sushi.com',
      '1inch.io',
      'curve.fi',
      'balancer.fi',
      'metamask.io',
      'phantom.app',
      'solflare.com',
      'trustwallet.com',
      'opensea.io',
      'magiceden.io'
    ];
    
    return legitSites.some(site => hostname === site || hostname.endsWith('.' + site));
  }

  // Report suspicious site to background
  function reportSuspicious(reason, details) {
    chrome.runtime.sendMessage({
      action: 'logThreat',
      details: {
        type: 'suspicious_site',
        reason,
        url: window.location.href,
        ...details
      }
    });
  }

  // Check settings and show warning
  async function checkAndShowWarning() {
    const settings = await chrome.storage.local.get(['settingPhishing']);
    
    if (settings.settingPhishing !== false) {
      showPhishingWarning();
    }
  }

  // Show phishing warning
  function showPhishingWarning() {
    // Don't show if already shown
    if (document.getElementById('rmi-phishing-warning')) return;
    
    const warning = document.createElement('div');
    warning.id = 'rmi-phishing-warning';
    warning.innerHTML = `
      <div class="rmi-phishing-overlay"></div>
      <div class="rmi-phishing-modal">
        <div class="rmi-phishing-icon">⚠️</div>
        <h2>Suspicious Website Detected</h2>
        <p>This website may be attempting to impersonate a legitimate crypto service.</p>
        <div class="rmi-phishing-details">
          <strong>URL:</strong> ${window.location.hostname}<br>
          <strong>Risk:</strong> High
        </div>
        <div class="rmi-phishing-actions">
          <button id="rmi-leave-site" class="rmi-btn rmi-btn-primary">
            Leave Site
          </button>
          <button id="rmi-stay-site" class="rmi-btn rmi-btn-secondary">
            I Understand the Risk
          </button>
        </div>
        <label class="rmi-dont-show">
          <input type="checkbox" id="rmi-dont-show-again">
          Don't show this warning for this site again
        </label>
      </div>
    `;
    
    const style = document.createElement('style');
    style.textContent = `
      #rmi-phishing-warning {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: 2147483647;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      }
      .rmi-phishing-overlay {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.95);
      }
      .rmi-phishing-modal {
        position: relative;
        max-width: 480px;
        margin: 20px;
        padding: 40px;
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border: 2px solid #ef4444;
        border-radius: 16px;
        text-align: center;
        color: #fff;
        animation: rmi-slide-in 0.3s ease-out;
      }
      @keyframes rmi-slide-in {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
      }
      .rmi-phishing-icon {
        font-size: 64px;
        margin-bottom: 20px;
      }
      .rmi-phishing-modal h2 {
        color: #ef4444;
        margin: 0 0 16px 0;
        font-size: 24px;
      }
      .rmi-phishing-modal p {
        color: #aaa;
        margin: 0 0 20px 0;
        font-size: 14px;
        line-height: 1.5;
      }
      .rmi-phishing-details {
        background: rgba(239, 68, 68, 0.1);
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 24px;
        font-size: 13px;
        text-align: left;
      }
      .rmi-phishing-actions {
        display: flex;
        gap: 12px;
        justify-content: center;
        margin-bottom: 20px;
      }
      .rmi-btn {
        padding: 12px 24px;
        border: none;
        border-radius: 8px;
        font-size: 14px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
      }
      .rmi-btn-primary {
        background: linear-gradient(90deg, #ef4444, #dc2626);
        color: #fff;
      }
      .rmi-btn-primary:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4);
      }
      .rmi-btn-secondary {
        background: transparent;
        color: #aaa;
        border: 1px solid #444;
      }
      .rmi-btn-secondary:hover {
        border-color: #666;
        color: #fff;
      }
      .rmi-dont-show {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        font-size: 12px;
        color: #64748b;
        cursor: pointer;
      }
      .rmi-dont-show input {
        cursor: pointer;
      }
    `;
    
    document.head.appendChild(style);
    document.body.appendChild(warning);
    
    // Handle buttons
    document.getElementById('rmi-leave-site').addEventListener('click', () => {
      window.location.href = 'https://intel.cryptorugmunch.com';
    });
    
    document.getElementById('rmi-stay-site').addEventListener('click', async () => {
      const dontShow = document.getElementById('rmi-dont-show-again').checked;
      
      if (dontShow) {
        // Add to whitelist
        const stored = await chrome.storage.local.get(['phishingWhitelist']);
        const whitelist = stored.phishingWhitelist || [];
        whitelist.push(window.location.hostname);
        await chrome.storage.local.set({ phishingWhitelist: whitelist });
      }
      
      warning.remove();
    });
  }

  // Show wallet connection warning
  function showWalletWarning() {
    // Create toast notification
    const toast = document.createElement('div');
    toast.id = 'rmi-wallet-warning';
    toast.innerHTML = `
      <div class="rmi-wallet-warning-content">
        <span class="rmi-wallet-icon">⚠️</span>
        <div class="rmi-wallet-message">
          <strong>Wallet Connection Warning</strong>
          <span>This site is not verified. Proceed with caution.</span>
        </div>
        <button id="rmi-wallet-dismiss">&times;</button>
      </div>
    `;
    
    const style = document.createElement('style');
    style.textContent = `
      #rmi-wallet-warning {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 2147483646;
        max-width: 400px;
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border: 1px solid #f59e0b;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
        animation: rmi-slide-in-right 0.3s ease-out;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      }
      @keyframes rmi-slide-in-right {
        from { opacity: 0; transform: translateX(100%); }
        to { opacity: 1; transform: translateX(0); }
      }
      .rmi-wallet-warning-content {
        display: flex;
        align-items: flex-start;
        gap: 12px;
      }
      .rmi-wallet-icon {
        font-size: 24px;
      }
      .rmi-wallet-message {
        flex: 1;
        display: flex;
        flex-direction: column;
      }
      .rmi-wallet-message strong {
        color: #f59e0b;
        font-size: 14px;
        margin-bottom: 4px;
      }
      .rmi-wallet-message span {
        color: #aaa;
        font-size: 12px;
      }
      #rmi-wallet-dismiss {
        background: none;
        border: none;
        color: #64748b;
        font-size: 20px;
        cursor: pointer;
        padding: 0;
        line-height: 1;
      }
      #rmi-wallet-dismiss:hover {
        color: #fff;
      }
    `;
    
    document.head.appendChild(style);
    document.body.appendChild(toast);
    
    document.getElementById('rmi-wallet-dismiss').addEventListener('click', () => {
      toast.remove();
    });
    
    // Auto-dismiss after 10 seconds
    setTimeout(() => {
      toast.remove();
    }, 10000);
  }

  // Initialize
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', checkSite);
  } else {
    checkSite();
  }
})();
