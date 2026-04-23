/**
 * Background Service Worker
 * =========================
 * Handles real-time alerts, badge updates, and persistent connections
 */

const API_WS_URL = 'wss://api.cryptorugmunch.com/ws';
const API_HTTP_URL = 'https://api.cryptorugmunch.com/v1';

// State
let ws = null;
let reconnectAttempts = 0;
let maxReconnectAttempts = 10;
let reconnectDelay = 5000;
let alertCheckInterval = null;

// Initialize on install/update
chrome.runtime.onInstalled.addListener((details) => {
  console.log('RMI Extension installed:', details.reason);

  // Set default settings
  chrome.storage.local.set({
    'rmi_settings': {
      notificationsEnabled: true,
      riskAlertsEnabled: true,
      whaleAlertsEnabled: true,
      scamAlertsEnabled: true,
      priceAlertsEnabled: false,
      badgeAlertsEnabled: true,
      soundEnabled: false,
    },
    'rmi_alerts': [],
    'rmi_unread_count': 0,
  });

  // Start WebSocket connection
  connectWebSocket();

  // Set up periodic alert fetching as fallback
  setupAlertPolling();
});

// Start on browser startup
chrome.runtime.onStartup.addListener(() => {
  connectWebSocket();
  setupAlertPolling();
});

/**
 * WebSocket Connection Management
 */
function connectWebSocket() {
  if (ws?.readyState === WebSocket.OPEN) return;

  try {
    ws = new WebSocket(API_WS_URL);

    ws.onopen = () => {
      console.log('WebSocket connected');
      reconnectAttempts = 0;

      // Subscribe to channels based on settings
      chrome.storage.local.get(['rmi_settings'], (result) => {
        const settings = result.rmi_settings || {};

        if (settings.riskAlertsEnabled) {
          ws.send(JSON.stringify({ action: 'subscribe', channel: 'alerts' }));
        }
        if (settings.whaleAlertsEnabled) {
          ws.send(JSON.stringify({ action: 'subscribe', channel: 'whale_alerts' }));
        }
        if (settings.scamAlertsEnabled) {
          ws.send(JSON.stringify({ action: 'subscribe', channel: 'scam_alerts' }));
        }
        if (settings.priceAlertsEnabled) {
          ws.send(JSON.stringify({ action: 'subscribe', channel: 'price_updates' }));
        }
      });
    };

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        handleWebSocketMessage(message);
      } catch (e) {
        console.error('Failed to parse WebSocket message:', e);
      }
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      attemptReconnect();
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  } catch (e) {
    console.error('Failed to create WebSocket:', e);
    attemptReconnect();
  }
}

function attemptReconnect() {
  if (reconnectAttempts >= maxReconnectAttempts) {
    console.log('Max reconnect attempts reached');
    return;
  }

  reconnectAttempts++;
  const delay = Math.min(reconnectDelay * Math.pow(2, reconnectAttempts - 1), 60000);

  console.log(`Reconnecting in ${delay}ms (attempt ${reconnectAttempts})`);
  setTimeout(connectWebSocket, delay);
}

function handleWebSocketMessage(message) {
  if (message.type === 'alert' || message.type === 'whale_alert') {
    handleIncomingAlert(message.data);
  }
}

/**
 * Handle incoming alert
 */
async function handleIncomingAlert(alert) {
  const { settings } = await chrome.storage.local.get(['rmi_settings']);

  if (!settings?.notificationsEnabled) return;

  // Filter by alert type
  if (alert.type === 'WHALE' && !settings.whaleAlertsEnabled) return;
  if (alert.type === 'RISK' && !settings.riskAlertsEnabled) return;
  if (alert.type === 'SCAM' && !settings.scamAlertsEnabled) return;

  // Show notification
  chrome.notifications.create(`rmi-${alert.id || Date.now()}`, {
    type: 'basic',
    iconUrl: 'icons/icon128.png',
    title: getAlertTitle(alert),
    message: getAlertMessage(alert),
    priority: alert.severity === 'CRITICAL' ? 2 : 1,
    buttons: alert.wallet_address ? [
      { title: 'View Wallet' },
      { title: 'Dismiss' }
    ] : undefined,
  });

  // Update badge
  if (settings.badgeAlertsEnabled) {
    updateBadgeCount(1);
  }

  // Store alert
  storeAlert(alert);

  // Play sound for critical alerts
  if (settings.soundEnabled && alert.severity === 'CRITICAL') {
    playAlertSound();
  }
}

function getAlertTitle(alert) {
  const titles = {
    'WHALE': '🐋 Whale Alert',
    'RISK': '⚠️ Risk Alert',
    'SCAM': '🚨 Scam Detected',
    'PRICE': '📈 Price Alert',
  };
  return titles[alert.type] || 'Rug Munch Intel';
}

function getAlertMessage(alert) {
  if (alert.message) return alert.message;

  switch (alert.type) {
    case 'WHALE':
      return `${alert.wallet_address?.slice(0, 6)}... moved ${alert.amount} ${alert.token}`;
    case 'RISK':
      return `Risk level: ${alert.risk_level} - ${alert.description}`;
    case 'SCAM':
      return `Suspicious activity detected on ${alert.chain}`;
    default:
      return 'New alert from Rug Munch Intel';
  }
}

/**
 * Store alert in local storage
 */
async function storeAlert(alert) {
  const result = await chrome.storage.local.get(['rmi_alerts']);
  const alerts = result.rmi_alerts || [];

  alerts.unshift({
    ...alert,
    receivedAt: Date.now(),
    read: false,
  });

  // Keep only last 100 alerts
  if (alerts.length > 100) {
    alerts.pop();
  }

  await chrome.storage.local.set({ 'rmi_alerts': alerts });
}

/**
 * Update badge count
 */
async function updateBadgeCount(increment = 0) {
  const result = await chrome.storage.local.get(['rmi_unread_count']);
  const current = result.rmi_unread_count || 0;
  const newCount = increment > 0 ? current + increment : 0;

  await chrome.storage.local.set({ 'rmi_unread_count': newCount });

  if (newCount > 0) {
    chrome.action.setBadgeText({ text: newCount > 99 ? '99+' : String(newCount) });
    chrome.action.setBadgeBackgroundColor({ color: '#ef4444' });
  } else {
    chrome.action.setBadgeText({ text: '' });
  }
}

/**
 * Alert polling fallback
 */
function setupAlertPolling() {
  if (alertCheckInterval) {
    clearInterval(alertCheckInterval);
  }

  // Poll every 30 seconds as fallback
  alertCheckInterval = setInterval(async () => {
    if (ws?.readyState === WebSocket.OPEN) return; // Skip if WebSocket is active

    try {
      const response = await fetch(`${API_HTTP_URL}/alerts/recent?limit=10`);
      if (response.ok) {
        const alerts = await response.json();
        // Process new alerts
        const result = await chrome.storage.local.get(['rmi_alerts']);
        const existingAlerts = result.rmi_alerts || [];
        const existingIds = new Set(existingAlerts.map(a => a.id));

        for (const alert of alerts) {
          if (!existingIds.has(alert.id)) {
            handleIncomingAlert(alert);
          }
        }
      }
    } catch (e) {
      // Silent fail - WebSocket is preferred
    }
  }, 30000);
}

/**
 * Play alert sound
 */
function playAlertSound() {
  // Create audio context and play beep
  try {
    const audio = new Audio(chrome.runtime.getURL('sounds/alert.mp3'));
    audio.volume = 0.5;
    audio.play().catch(() => {});
  } catch (e) {
    console.error('Failed to play sound:', e);
  }
}

/**
 * Message handlers from popup/content scripts
 */
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  switch (request.action) {
    case 'getAlerts':
      chrome.storage.local.get(['rmi_alerts', 'rmi_unread_count'], (result) => {
        sendResponse({
          alerts: result.rmi_alerts || [],
          unreadCount: result.rmi_unread_count || 0,
        });
      });
      return true; // Async response

    case 'markAllRead':
      updateBadgeCount(0);
      chrome.storage.local.get(['rmi_alerts'], (result) => {
        const alerts = (result.rmi_alerts || []).map(a => ({ ...a, read: true }));
        chrome.storage.local.set({ 'rmi_alerts': alerts }, () => {
          sendResponse({ success: true });
        });
      });
      return true;

    case 'clearBadge':
      updateBadgeCount(0);
      sendResponse({ success: true });
      return false;

    case 'updateSettings':
      chrome.storage.local.set({ 'rmi_settings': request.settings }, () => {
        // Reconnect WebSocket with new subscriptions
        if (ws) {
          ws.close();
        }
        connectWebSocket();
        sendResponse({ success: true });
      });
      return true;

    case 'getSettings':
      chrome.storage.local.get(['rmi_settings'], (result) => {
        sendResponse(result.rmi_settings);
      });
      return true;

    case 'analyzeAddress':
      analyzeAddress(request.address, request.chain)
        .then(result => sendResponse(result))
        .catch(error => sendResponse({ error: error.message }));
      return true;

    case 'openWalletPage':
      chrome.tabs.create({
        url: `https://app.cryptorugmunch.com/wallet/${request.address}?chain=${request.chain || 'ethereum'}`
      });
      sendResponse({ success: true });
      return false;
  }
});

/**
 * Analyze address via API
 */
async function analyzeAddress(address, chain = 'ethereum') {
  try {
    const response = await fetch(`${API_HTTP_URL}/analysis/wallet`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ address, chain }),
    });

    if (!response.ok) {
      throw new Error('Analysis failed');
    }

    return await response.json();
  } catch (error) {
    throw error;
  }
}

/**
 * Notification button handlers
 */
chrome.notifications.onButtonClicked.addListener((notificationId, buttonIndex) => {
  if (buttonIndex === 0) {
    // View Wallet button
    const alertId = notificationId.replace('rmi-', '');
    chrome.storage.local.get(['rmi_alerts'], (result) => {
      const alerts = result.rmi_alerts || [];
      const alert = alerts.find(a => a.id === alertId || a.receivedAt === parseInt(alertId));
      if (alert?.wallet_address) {
        chrome.tabs.create({
          url: `https://app.cryptorugmunch.com/wallet/${alert.wallet_address}`
        });
      }
    });
  }
  chrome.notifications.clear(notificationId);
});

// Keep service worker alive
chrome.alarms.create('keepAlive', { periodInMinutes: 4.9 });
chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === 'keepAlive') {
    // Ping to keep service worker active
    console.log('Keep alive ping');
  }
});

console.log('RMI Background Service Worker initialized');
