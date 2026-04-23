/**
 * RMI Extension - Background Service Worker
 * Handles events, notifications, and data sync
 */

const RMI_API_BASE = 'https://intel.cryptorugmunch.com/api';

// Initialize on install
chrome.runtime.onInstalled.addListener((details) => {
  console.log('[RMI] Extension installed:', details.reason);
  
  // Set default settings
  chrome.storage.local.set({
    settingWarnings: true,
    settingPhishing: true,
    settingNotifications: true,
    scanCount: 0,
    threatCount: 0,
    protectedSites: 0,
    recentScans: [],
    watchlist: [],
    installDate: new Date().toISOString()
  });
  
  // Schedule periodic tasks
  chrome.alarms.create('syncWatchlist', { periodInMinutes: 5 });
  chrome.alarms.create('checkThreats', { periodInMinutes: 15 });
  chrome.alarms.create('cleanupCache', { periodInMinutes: 60 });
  
  // Show welcome notification
  if (details.reason === 'install') {
    chrome.notifications.create({
      type: 'basic',
      iconUrl: 'icons/icon128.png',
      title: 'RMI Protection Activated',
      message: 'Your crypto fraud protection is now active. Browse DEXs safely!'
    });
  }
});

// Handle alarms
chrome.alarms.onAlarm.addListener(async (alarm) => {
  switch (alarm.name) {
    case 'syncWatchlist':
      await syncWatchlist();
      break;
    case 'checkThreats':
      await checkThreats();
      break;
    case 'cleanupCache':
      await cleanupCache();
      break;
  }
});

// Handle messages from content scripts and popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  (async () => {
    try {
      switch (message.action) {
        case 'scanToken':
          const result = await scanToken(message.address);
          sendResponse({ success: true, data: result });
          break;
          
        case 'getTokenData':
          const data = await getTokenData(message.address);
          sendResponse({ success: true, data });
          break;
          
        case 'addToWatchlist':
          await addToWatchlist(message.address, message.symbol);
          sendResponse({ success: true });
          break;
          
        case 'removeFromWatchlist':
          await removeFromWatchlist(message.address);
          sendResponse({ success: true });
          break;
          
        case 'reportPhishing':
          await reportPhishingSite(message.url, message.details);
          sendResponse({ success: true });
          break;
          
        case 'getSettings':
          const settings = await chrome.storage.local.get([
            'settingWarnings',
            'settingPhishing',
            'settingNotifications',
            'apiKey'
          ]);
          sendResponse({ success: true, settings });
          break;
          
        case 'updateStats':
          await updateStats(message.updates);
          sendResponse({ success: true });
          break;
          
        case 'logThreat':
          await logThreat(message.details);
          sendResponse({ success: true });
          break;
          
        default:
          sendResponse({ success: false, error: 'Unknown action' });
      }
    } catch (error) {
      console.error('[RMI] Message handler error:', error);
      sendResponse({ success: false, error: error.message });
    }
  })();
  
  return true; // Keep channel open for async
});

// Handle tab updates (for phishing detection)
chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' && tab.url) {
    // Check if phishing site
    const isPhishing = await checkPhishingSite(tab.url);
    
    if (isPhishing) {
      // Show warning
      chrome.scripting.executeScript({
        target: { tabId },
        func: showPhishingWarning,
        args: [tab.url]
      });
      
      // Send notification if enabled
      const settings = await chrome.storage.local.get(['settingNotifications']);
      if (settings.settingNotifications !== false) {
        chrome.notifications.create({
          type: 'basic',
          iconUrl: 'icons/icon128.png',
          title: '⚠️ Phishing Site Detected',
          message: 'This website has been flagged as potentially dangerous.'
        });
      }
    }
  }
});

// Scan token via API
async function scanToken(address) {
  try {
    const response = await fetch(`${RMI_API_BASE}/contract-check/${address}`, {
      headers: {
        'X-Extension-Version': chrome.runtime.getManifest().version
      }
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    
    const data = await response.json();
    
    // Cache result
    data.cached_at = Date.now();
    await chrome.storage.local.set({ [`token_${address}`]: data });
    
    // Update stats
    const stats = await chrome.storage.local.get(['scanCount']);
    await chrome.storage.local.set({ scanCount: (stats.scanCount || 0) + 1 });
    
    // Check if high risk
    if (data.risk_level === 'critical' || data.risk_level === 'high') {
      const threatStats = await chrome.storage.local.get(['threatCount']);
      await chrome.storage.local.set({ threatCount: (threatStats.threatCount || 0) + 1 });
    }
    
    return data;
  } catch (error) {
    console.error('[RMI] Scan error:', error);
    throw error;
  }
}

// Get cached token data
async function getTokenData(address) {
  const cached = await chrome.storage.local.get(`token_${address}`);
  
  if (cached[`token_${address}`]) {
    const data = cached[`token_${address}`];
    
    // Check if cache is still valid (5 minutes)
    if (Date.now() - data.cached_at < 5 * 60 * 1000) {
      return data;
    }
  }
  
  // Fetch fresh data
  return await scanToken(address);
}

// Add to watchlist
async function addToWatchlist(address, symbol) {
  const stored = await chrome.storage.local.get(['watchlist']);
  const watchlist = stored.watchlist || [];
  
  if (watchlist.some(t => t.address === address)) {
    return; // Already exists
  }
  
  watchlist.push({
    address,
    symbol: symbol || address.slice(0, 8),
    addedAt: Date.now(),
    price: 0,
    change24h: 0
  });
  
  await chrome.storage.local.set({ watchlist });
}

// Remove from watchlist
async function removeFromWatchlist(address) {
  const stored = await chrome.storage.local.get(['watchlist']);
  const watchlist = stored.watchlist || [];
  
  const filtered = watchlist.filter(t => t.address !== address);
  await chrome.storage.local.set({ watchlist: filtered });
}

// Sync watchlist prices
async function syncWatchlist() {
  const stored = await chrome.storage.local.get(['watchlist']);
  const watchlist = stored.watchlist || [];
  
  if (watchlist.length === 0) return;
  
  // Update prices for each token
  for (const token of watchlist) {
    try {
      // In production, fetch from price API
      // For now, simulate
      token.change24h = (Math.random() - 0.5) * 20;
    } catch (error) {
      console.error('[RMI] Watchlist sync error:', error);
    }
  }
  
  await chrome.storage.local.set({ watchlist });
}

// Check for new threats
async function checkThreats() {
  try {
    const response = await fetch(`${RMI_API_BASE}/trending-scams?limit=10`);
    
    if (!response.ok) return;
    
    const data = await response.json();
    const scams = data.scams || [];
    
    // Get user's watchlist
    const stored = await chrome.storage.local.get(['watchlist']);
    const watchlist = stored.watchlist || [];
    const watchlistAddresses = watchlist.map(t => t.address.toLowerCase());
    
    // Check if any watchlist tokens are in new scams
    const affectedTokens = scams.filter(scam => 
      watchlistAddresses.includes(scam.token_address?.toLowerCase())
    );
    
    if (affectedTokens.length > 0) {
      const settings = await chrome.storage.local.get(['settingNotifications']);
      
      if (settings.settingNotifications !== false) {
        for (const token of affectedTokens) {
          chrome.notifications.create({
            type: 'basic',
            iconUrl: 'icons/icon128.png',
            title: '🚨 Watchlist Alert',
            message: `${token.token_symbol} has been flagged as potentially dangerous!`
          });
        }
      }
    }
  } catch (error) {
    console.error('[RMI] Threat check error:', error);
  }
}

// Check if site is phishing
async function checkPhishingSite(url) {
  try {
    const hostname = new URL(url).hostname;
    
    // Check against known phishing list
    const stored = await chrome.storage.local.get(['phishingList']);
    const phishingList = stored.phishingList || [];
    
    if (phishingList.some(site => hostname.includes(site))) {
      return true;
    }
    
    // Check for suspicious patterns
    const suspiciousPatterns = [
      /pancakswap/i,
      /unisvvap/i,
      /metamas[k$]/i,
      /phanton/i,
      /solflare-wallet/i,
      /trust-vvallet/i
    ];
    
    if (suspiciousPatterns.some(pattern => pattern.test(hostname))) {
      return true;
    }
    
    return false;
  } catch (error) {
    return false;
  }
}

// Report phishing site
async function reportPhishingSite(url, details) {
  try {
    await fetch(`${RMI_API_BASE}/report/phishing`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        url,
        details,
        reported_at: new Date().toISOString()
      })
    });
  } catch (error) {
    console.error('[RMI] Report error:', error);
  }
}

// Show phishing warning in page
function showPhishingWarning(url) {
  const warning = document.createElement('div');
  warning.id = 'rmi-phishing-warning';
  warning.innerHTML = `
    <div class="rmi-phishing-overlay"></div>
    <div class="rmi-phishing-modal">
      <div class="rmi-phishing-icon">⚠️</div>
      <h2>Phishing Site Detected</h2>
      <p>This website (<strong>${url}</strong>) has been flagged as a potential phishing site.</p>
      <div class="rmi-phishing-actions">
        <button onclick="window.location.href='https://intel.cryptorugmunch.com'" class="rmi-btn rmi-btn-primary">
          Go to Safety
        </button>
        <button onclick="document.getElementById('rmi-phishing-warning').remove()" class="rmi-btn rmi-btn-secondary">
          I Understand the Risk
        </button>
      </div>
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
      z-index: 999999;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .rmi-phishing-overlay {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0, 0, 0, 0.9);
    }
    .rmi-phishing-modal {
      position: relative;
      max-width: 500px;
      padding: 40px;
      background: linear-gradient(135deg, #1a1a2e, #16213e);
      border: 2px solid #ef4444;
      border-radius: 16px;
      text-align: center;
      color: #fff;
    }
    .rmi-phishing-icon {
      font-size: 64px;
      margin-bottom: 20px;
    }
    .rmi-phishing-modal h2 {
      color: #ef4444;
      margin-bottom: 16px;
    }
    .rmi-phishing-modal p {
      color: #aaa;
      margin-bottom: 24px;
    }
    .rmi-phishing-actions {
      display: flex;
      gap: 12px;
      justify-content: center;
    }
    .rmi-btn {
      padding: 12px 24px;
      border: none;
      border-radius: 8px;
      font-size: 14px;
      font-weight: 600;
      cursor: pointer;
    }
    .rmi-btn-primary {
      background: linear-gradient(90deg, #00d4ff, #0099cc);
      color: #000;
    }
    .rmi-btn-secondary {
      background: transparent;
      color: #aaa;
      border: 1px solid #444;
    }
  `;
  
  document.head.appendChild(style);
  document.body.appendChild(warning);
}

// Update statistics
async function updateStats(updates) {
  const stats = await chrome.storage.local.get([
    'scanCount',
    'threatCount',
    'protectedSites'
  ]);
  
  if (updates.scanCount) {
    stats.scanCount = (stats.scanCount || 0) + updates.scanCount;
  }
  
  if (updates.threatCount) {
    stats.threatCount = (stats.threatCount || 0) + updates.threatCount;
  }
  
  if (updates.protectedSites) {
    stats.protectedSites = (stats.protectedSites || 0) + updates.protectedSites;
  }
  
  await chrome.storage.local.set(stats);
}

// Log threat detection
async function logThreat(details) {
  const stored = await chrome.storage.local.get(['threatLog']);
  const threatLog = stored.threatLog || [];
  
  threatLog.unshift({
    ...details,
    timestamp: Date.now()
  });
  
  // Keep only last 100
  const trimmed = threatLog.slice(0, 100);
  
  await chrome.storage.local.set({ threatLog: trimmed });
}

// Cleanup old cache
async function cleanupCache() {
  const allData = await chrome.storage.local.get(null);
  const now = Date.now();
  const ONE_HOUR = 60 * 60 * 1000;
  
  for (const [key, value] of Object.entries(allData)) {
    // Clean up old token cache
    if (key.startsWith('token_') && value.cached_at) {
      if (now - value.cached_at > ONE_HOUR) {
        await chrome.storage.local.remove(key);
      }
    }
  }
  
  console.log('[RMI] Cache cleanup completed');
}

// Fetch phishing list periodically
async function updatePhishingList() {
  try {
    const response = await fetch(`${RMI_API_BASE}/phishing-list`);
    
    if (response.ok) {
      const data = await response.json();
      await chrome.storage.local.set({ phishingList: data.sites || [] });
    }
  } catch (error) {
    console.error('[RMI] Failed to update phishing list:', error);
  }
}

// Initial phishing list update
updatePhishingList();

// Schedule periodic updates
chrome.alarms.create('updatePhishingList', { periodInMinutes: 60 });
chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === 'updatePhishingList') {
    updatePhishingList();
  }
});
