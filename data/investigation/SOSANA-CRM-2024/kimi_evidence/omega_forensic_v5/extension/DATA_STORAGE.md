# RMI Extension - Data Storage & Privacy

## Overview
This document explains what data the RMI extension stores, why it's needed, and how users control it.

---

## Data We Store

### 1. User Settings (Local Only)
Stored in `chrome.storage.local` - never leaves your device.

```javascript
{
  "settingWarnings": true,        // Show warnings on DEXs
  "settingPhishing": true,        // Phishing protection enabled
  "settingNotifications": true,   // Risk change notifications
  "apiKey": "",                   // Optional API key for premium
  "rmi_consent": true,            // User consent given
  "rmi_consent_date": "2025-01-15T10:00:00Z"
}
```

### 2. Token Cache (Local Only)
Cached scan results to reduce API calls.

```javascript
{
  "token_Eyi4JcxVkS9fWzubSu5yS7dHy4kAiFHJN6Rwu6y7r8U": {
    "token_address": "Eyi4JcxVkS9fWzubSu5yS7dHy4kAiFHJN6Rwu6y7r8U",
    "token_symbol": "CRM",
    "overall_score": 85,
    "risk_level": "low",
    "flags": { ... },
    "cached_at": 1705312800000  // Auto-expires after 1 hour
  }
}
```

### 3. Recent Scans (Local Only)
Your scan history for quick access.

```javascript
{
  "recentScans": [
    {
      "address": "Eyi4JcxVkS9...",
      "symbol": "CRM",
      "score": 85,
      "riskLevel": "low",
      "timestamp": 1705312800000
    }
  ]
}
```

### 4. Watchlist (Local Only)
Tokens you're monitoring.

```javascript
{
  "watchlist": [
    {
      "address": "Eyi4JcxVkS9...",
      "symbol": "CRM",
      "addedAt": 1705312800000,
      "price": 0.05,
      "change24h": 5.2
    }
  ]
}
```

### 5. Statistics (Local Only)
Aggregated usage stats.

```javascript
{
  "scanCount": 42,          // Total scans performed
  "threatCount": 3,         // Threats detected
  "protectedSites": 15,     // Sites visited with protection
  "installDate": "2025-01-15T10:00:00Z"
}
```

### 6. Phishing Protection Lists (Local Only)
Cached lists for offline protection.

```javascript
{
  "phishingList": ["fake-uniswap.com", "scam-site.xyz"],
  "phishingWhitelist": ["trusted-site.com"]  // Sites user dismissed
}
```

---

## What We DON'T Store

❌ **Never stored:**
- Wallet addresses (unless you add to watchlist)
- Private keys or seed phrases
- Transaction data
- Browsing history
- Personal identifiable information
- IP addresses

---

## User Consent Flow

### First Install
1. Extension shows consent banner on supported sites
2. User must explicitly click "Enable Protection"
3. Consent is stored locally
4. No data is collected before consent

### Revoking Consent
Users can revoke consent anytime:
1. Click extension icon → Settings
2. Toggle off "Show warnings on DEXs"
3. Or click "Clear All Data" to remove everything

---

## Data Retention

| Data Type | Retention | Auto-Cleanup |
|-----------|-----------|--------------|
| Settings | Until user clears | Never |
| Token Cache | 1 hour | Every hour |
| Recent Scans | Last 20 items | Manual only |
| Watchlist | Until removed | Never |
| Stats | Until cleared | Never |
| Phishing Lists | 1 hour | Every hour |

---

## API Communication

### What We Send to RMI API

**Token Scan Request:**
```
GET https://intel.cryptorugmunch.com/api/contract-check/{token_address}
Headers:
  X-Extension-Version: 2.0.0
```

**No user-identifiable information is sent.**

### What We Receive
- Risk scores
- Token metadata
- Red/green flags
- Analysis results

---

## Privacy Controls

### In Popup Settings
- ✅/❌ Show warnings on DEXs
- ✅/❌ Phishing protection
- ✅/❌ Risk change notifications

### Clear All Data
Button in Settings → "Clear All Data" removes:
- All cached token data
- Recent scans
- Watchlist
- Statistics
- Settings (reset to defaults)

### Per-Site Control
Users can dismiss warnings for specific sites:
- Check "Don't show this warning for this site again"
- Site added to whitelist
- Can be removed in Settings

---

## Security Measures

### Local Storage
- All data stored in Chrome's encrypted storage
- Isolated per-extension
- Cannot be accessed by websites

### API Communication
- HTTPS only
- No authentication required for basic scans
- Optional API key for premium features

### Content Scripts
- Run in isolated world
- Cannot access page JavaScript
- Only inject UI overlays

---

## Transparency

### Open Source
Extension code is open source and auditable.

### Privacy Policy
Full privacy policy at: https://intel.cryptorugmunch.com/privacy

### Contact
Privacy questions: privacy@cryptorugmunch.com

---

## Compliance

### GDPR
- User consent required before data collection
- Right to access: View all stored data in Settings
- Right to deletion: "Clear All Data" button
- Data portability: Export available on request

### CCPA
- No sale of personal information
- Disclosure of data collection practices
- Opt-out available

---

## FAQ

**Q: Does RMI collect my wallet address?**
A: Only if you explicitly add it to your watchlist. Wallet addresses are stored locally and never sent to our servers.

**Q: Can RMI see my transactions?**
A: No. We cannot see or access any of your transactions or wallet data.

**Q: Is my browsing history tracked?**
A: No. We only check if you're on a supported DEX site to show relevant warnings.

**Q: How do I completely remove all data?**
A: Go to Settings → "Clear All Data" or uninstall the extension.

**Q: Does RMI work offline?**
A: Partially. Phishing protection uses cached lists. Token scans require internet connection.

---

## Data Export

Users can request a copy of their data:

```javascript
// In browser console with extension installed
chrome.storage.local.get(null, (data) => {
  console.log(JSON.stringify(data, null, 2));
});
```

Or contact support for assistance.
