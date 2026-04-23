/**
 * Storage Utilities
 * =================
 * Helper functions for chrome.storage operations
 */

const StorageKeys = {
  SETTINGS: 'rmi_settings',
  ALERTS: 'rmi_alerts',
  UNREAD_COUNT: 'rmi_unread_count',
  RECENT_SCANS: 'rmi_recent_scans',
  TOKEN: 'rmi_auth_token',
  USER: 'rmi_user',
};

/**
 * Get value from storage
 */
export async function get(key, defaultValue = null) {
  try {
    const result = await chrome.storage.local.get([key]);
    return result[key] ?? defaultValue;
  } catch (e) {
    console.error(`Storage get error for ${key}:`, e);
    return defaultValue;
  }
}

/**
 * Set value in storage
 */
export async function set(key, value) {
  try {
    await chrome.storage.local.set({ [key]: value });
    return true;
  } catch (e) {
    console.error(`Storage set error for ${key}:`, e);
    return false;
  }
}

/**
 * Remove value from storage
 */
export async function remove(key) {
  try {
    await chrome.storage.local.remove([key]);
    return true;
  } catch (e) {
    console.error(`Storage remove error for ${key}:`, e);
    return false;
  }
}

/**
 * Clear all extension data
 */
export async function clearAll() {
  try {
    await chrome.storage.local.clear();
    return true;
  } catch (e) {
    console.error('Storage clear error:', e);
    return false;
  }
}

/**
 * Get settings
 */
export async function getSettings() {
  return get(StorageKeys.SETTINGS, {
    notificationsEnabled: true,
    riskAlertsEnabled: true,
    whaleAlertsEnabled: true,
    scamAlertsEnabled: true,
    priceAlertsEnabled: false,
    badgeAlertsEnabled: true,
    soundEnabled: false,
  });
}

/**
 * Save settings
 */
export async function saveSettings(settings) {
  return set(StorageKeys.SETTINGS, settings);
}

/**
 * Get auth token
 */
export async function getAuthToken() {
  return get(StorageKeys.TOKEN);
}

/**
 * Save auth token
 */
export async function saveAuthToken(token) {
  return set(StorageKeys.TOKEN, token);
}

/**
 * Clear auth data
 */
export async function clearAuth() {
  await remove(StorageKeys.TOKEN);
  await remove(StorageKeys.USER);
}

/**
 * Get recent scans
 */
export async function getRecentScans() {
  return get(StorageKeys.RECENT_SCANS, []);
}

/**
 * Add scan to history
 */
export async function addRecentScan(address, chain, riskLevel) {
  const scans = await getRecentScans();

  // Remove duplicate
  const filtered = scans.filter(s => s.address !== address);

  // Add new scan
  filtered.unshift({
    address,
    chain,
    riskLevel,
    timestamp: Date.now(),
  });

  // Keep only last 10
  return set(StorageKeys.RECENT_SCANS, filtered.slice(0, 10));
}

/**
 * Clear recent scans
 */
export async function clearRecentScans() {
  return remove(StorageKeys.RECENT_SCANS);
}

/**
 * Get stored alerts
 */
export async function getAlerts() {
  return get(StorageKeys.ALERTS, []);
}

/**
 * Add alert
 */
export async function addAlert(alert) {
  const alerts = await getAlerts();
  alerts.unshift({
    ...alert,
    receivedAt: Date.now(),
    read: false,
  });

  // Keep only last 100
  return set(StorageKeys.ALERTS, alerts.slice(0, 100));
}

/**
 * Mark all alerts as read
 */
export async function markAllAlertsRead() {
  const alerts = await getAlerts();
  const updated = alerts.map(a => ({ ...a, read: true }));
  await set(StorageKeys.ALERTS, updated);
  await set(StorageKeys.UNREAD_COUNT, 0);
  return updated;
}

/**
 * Get unread count
 */
export async function getUnreadCount() {
  return get(StorageKeys.UNREAD_COUNT, 0);
}

/**
 * Increment unread count
 */
export async function incrementUnreadCount() {
  const count = await getUnreadCount();
  return set(StorageKeys.UNREAD_COUNT, count + 1);
}

/**
 * Clear unread count
 */
export async function clearUnreadCount() {
  return set(StorageKeys.UNREAD_COUNT, 0);
}

export { StorageKeys };
