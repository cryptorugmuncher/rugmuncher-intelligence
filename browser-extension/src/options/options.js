/**
 * Options Page Script
 * ===================
 * Settings management for the extension
 */

document.addEventListener('DOMContentLoaded', async () => {
  // Load saved settings
  await loadSettings();

  // Setup event listeners
  setupEventListeners();

  // Load alert history
  loadAlertHistory();

  // Check connection status
  checkConnectionStatus();
});

/**
 * Load settings from storage
 */
async function loadSettings() {
  try {
    const result = await chrome.storage.local.get(['rmi_settings']);
    const settings = result.rmi_settings || {
      notificationsEnabled: true,
      riskAlertsEnabled: true,
      whaleAlertsEnabled: true,
      scamAlertsEnabled: true,
      priceAlertsEnabled: false,
      badgeAlertsEnabled: true,
      soundEnabled: false,
    };

    // Apply settings to form
    document.getElementById('notificationsEnabled').checked = settings.notificationsEnabled;
    document.getElementById('riskAlertsEnabled').checked = settings.riskAlertsEnabled;
    document.getElementById('whaleAlertsEnabled').checked = settings.whaleAlertsEnabled;
    document.getElementById('scamAlertsEnabled').checked = settings.scamAlertsEnabled;
    document.getElementById('priceAlertsEnabled').checked = settings.priceAlertsEnabled;
    document.getElementById('badgeAlertsEnabled').checked = settings.badgeAlertsEnabled;
    document.getElementById('soundEnabled').checked = settings.soundEnabled;
  } catch (e) {
    console.error('Failed to load settings:', e);
  }
}

/**
 * Setup event listeners for settings changes
 */
function setupEventListeners() {
  const settings = [
    'notificationsEnabled',
    'riskAlertsEnabled',
    'whaleAlertsEnabled',
    'scamAlertsEnabled',
    'priceAlertsEnabled',
    'badgeAlertsEnabled',
    'soundEnabled',
  ];

  settings.forEach(id => {
    document.getElementById(id)?.addEventListener('change', async (e) => {
      await saveSettings();
    });
  });

  // Alert history buttons
  document.getElementById('clearAlertsBtn')?.addEventListener('click', clearAlertHistory);
  document.getElementById('markAllReadBtn')?.addEventListener('click', markAllAlertsRead);
}

/**
 * Save settings to storage
 */
async function saveSettings() {
  const settings = {
    notificationsEnabled: document.getElementById('notificationsEnabled').checked,
    riskAlertsEnabled: document.getElementById('riskAlertsEnabled').checked,
    whaleAlertsEnabled: document.getElementById('whaleAlertsEnabled').checked,
    scamAlertsEnabled: document.getElementById('scamAlertsEnabled').checked,
    priceAlertsEnabled: document.getElementById('priceAlertsEnabled').checked,
    badgeAlertsEnabled: document.getElementById('badgeAlertsEnabled').checked,
    soundEnabled: document.getElementById('soundEnabled').checked,
  };

  try {
    await chrome.storage.local.set({ 'rmi_settings': settings });

    // Notify background script of settings change
    await chrome.runtime.sendMessage({
      action: 'updateSettings',
      settings: settings,
    });

    showSaveIndicator();
  } catch (e) {
    console.error('Failed to save settings:', e);
  }
}

/**
 * Show save confirmation
 */
function showSaveIndicator() {
  const indicator = document.createElement('div');
  indicator.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: #22c55e;
    color: #fff;
    padding: 12px 20px;
    border-radius: 8px;
    font-weight: 500;
    z-index: 10000;
    animation: slideIn 0.3s ease;
  `;
  indicator.textContent = 'Settings saved';
  document.body.appendChild(indicator);

  setTimeout(() => {
    indicator.style.animation = 'slideOut 0.3s ease';
    setTimeout(() => indicator.remove(), 300);
  }, 2000);
}

/**
 * Load alert history
 */
async function loadAlertHistory() {
  try {
    const result = await chrome.runtime.sendMessage({ action: 'getAlerts' });
    renderAlerts(result.alerts || []);
  } catch (e) {
    console.error('Failed to load alerts:', e);
  }
}

/**
 * Render alert history
 */
function renderAlerts(alerts) {
  const container = document.getElementById('alertHistory');

  if (alerts.length === 0) {
    container.innerHTML = '<div class="empty-state">No recent alerts</div>';
    return;
  }

  container.innerHTML = alerts.slice(0, 50).map(alert => `
    <div class="alert-item ${alert.read ? '' : 'unread'}">
      <div class="alert-icon ${getAlertTypeClass(alert.type)}">
        ${getAlertIcon(alert.type)}
      </div>
      <div class="alert-content">
        <div class="alert-title">${getAlertTitle(alert)}</div>
        <div class="alert-message">${alert.message || alert.description || 'No details'}</div>
        <div class="alert-time">${formatTime(alert.receivedAt || alert.created_at)}</div>
      </div>
    </div>
  `).join('');
}

function getAlertTypeClass(type) {
  const map = {
    'WHALE': 'whale',
    'RISK': 'risk',
    'SCAM': 'scam',
    'PRICE': 'whale',
  };
  return map[type] || 'risk';
}

function getAlertIcon(type) {
  const icons = {
    'WHALE': '🐋',
    'RISK': '⚠️',
    'SCAM': '🚨',
    'PRICE': '📈',
  };
  return icons[type] || '🔔';
}

function getAlertTitle(alert) {
  const titles = {
    'WHALE': 'Whale Alert',
    'RISK': 'Risk Alert',
    'SCAM': 'Scam Detected',
    'PRICE': 'Price Alert',
  };
  return titles[alert.type] || 'Alert';
}

function formatTime(timestamp) {
  if (!timestamp) return 'Unknown';
  const date = new Date(timestamp);
  const now = new Date();
  const diff = now - date;

  if (diff < 60000) return 'Just now';
  if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
  return date.toLocaleDateString();
}

/**
 * Clear alert history
 */
async function clearAlertHistory() {
  try {
    await chrome.storage.local.set({ 'rmi_alerts': [] });
    await chrome.runtime.sendMessage({ action: 'clearBadge' });
    loadAlertHistory();
  } catch (e) {
    console.error('Failed to clear alerts:', e);
  }
}

/**
 * Mark all alerts as read
 */
async function markAllAlertsRead() {
  try {
    await chrome.runtime.sendMessage({ action: 'markAllRead' });
    loadAlertHistory();
  } catch (e) {
    console.error('Failed to mark alerts read:', e);
  }
}

/**
 * Check WebSocket connection status
 */
async function checkConnectionStatus() {
  try {
    // We can't directly check WebSocket from here, but we can infer from last activity
    const result = await chrome.storage.local.get(['rmi_last_ws_ping']);
    const lastPing = result.rmi_last_ws_ping;
    const isConnected = lastPing && (Date.now() - lastPing < 60000);

    updateConnectionStatus(isConnected);
  } catch (e) {
    updateConnectionStatus(false);
  }
}

function updateConnectionStatus(connected) {
  const badge = document.getElementById('connectionStatus');
  const text = document.getElementById('connectionText');

  if (connected) {
    badge.className = 'status-badge connected';
    text.textContent = 'Connected';
  } else {
    badge.className = 'status-badge disconnected';
    text.textContent = 'Disconnected';
  }
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
  @keyframes slideIn {
    from { transform: translateX(100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
  }
  @keyframes slideOut {
    from { transform: translateX(0); opacity: 1; }
    to { transform: translateX(100%); opacity: 0; }
  }
`;
document.head.appendChild(style);
