# Rug Munch Intel Browser Extension

Real-time crypto wallet risk analysis and scam detection extension for Chrome, Firefox, and Edge.

## Features

### Popup Wallet Scanner
- Quick wallet address scanning from any page
- Risk level assessment with detailed analysis
- Recent scan history
- Direct links to full app

### Explorer Integration
- Works on Etherscan, BscScan, PolygonScan, Arbiscan, and more
- Automatic address highlighting with risk indicators
- Floating action button for page-wide scanning
- Hover tooltips with risk summaries

### Real-time Alerts
- WebSocket connection for instant notifications
- Whale alerts for large transactions
- Risk alerts for suspicious activity
- Scam detection notifications
- Customizable alert preferences

### Background Service
- Persistent connection for real-time updates
- Badge counter for unread alerts
- Alert caching and history
- Automatic reconnection with exponential backoff

## Installation

### Chrome/Edge (Developer Mode)

1. Open Chrome/Edge and navigate to `chrome://extensions/` or `edge://extensions/`
2. Enable "Developer mode" in the top right
3. Click "Load unpacked"
4. Select the `browser-extension` folder
5. The extension is now installed

### Firefox

1. Open Firefox and navigate to `about:debugging`
2. Click "This Firefox"
3. Click "Load Temporary Add-on"
4. Select the `manifest.json` file in the extension folder

### Chrome Web Store (Future)

The extension will be published to the Chrome Web Store for easy installation.

## File Structure

```
browser-extension/
├── manifest.json              # Extension manifest (v3)
├── README.md                  # This file
├── icons/                     # Extension icons
│   ├── icon16.png
│   ├── icon32.png
│   ├── icon48.png
│   └── icon128.png
├── sounds/                    # Alert sounds
│   └── alert.mp3
├── src/
│   ├── popup/                 # Popup UI
│   │   ├── popup.html
│   │   └── popup.js
│   ├── options/               # Settings page
│   │   ├── options.html
│   │   └── options.js
│   ├── background/            # Service worker
│   │   └── background.js
│   ├── content/               # Content scripts
│   │   ├── content.js
│   │   └── content.css
│   └── utils/                 # Shared utilities
│       ├── storage.js
│       └── api.js
```

## API Integration

The extension connects to:
- **HTTP API**: `https://api.cryptorugmunch.com/v1`
- **WebSocket**: `wss://api.cryptorugmunch.com/ws`

## Supported Sites

### Blockchain Explorers
- etherscan.io
- bscscan.com
- polygonscan.com
- arbiscan.io
- optimistic.etherscan.io
- basescan.org
- solscan.io

### Trading Platforms
- dextools.io
- dexscreener.com

## Development

### Building Icons

Generate icons from the logo:

```bash
# Requires ImageMagick
convert logo.png -resize 16x16 icons/icon16.png
convert logo.png -resize 32x32 icons/icon32.png
convert logo.png -resize 48x48 icons/icon48.png
convert logo.png -resize 128x128 icons/icon128.png
```

### Testing

1. Make code changes
2. Reload extension in `chrome://extensions/`
3. Test on supported sites
4. Check background page console for errors

### Debug Mode

Enable debug logging in background.js:

```javascript
const DEBUG = true;
```

## Permissions Explained

- **storage**: Save settings, alerts, and scan history
- **activeTab**: Access current page for address detection
- **notifications**: Show desktop alert notifications
- **alarms**: Keep service worker alive, schedule tasks
- **scripting**: Inject content scripts dynamically
- **host_permissions**: Access to blockchain explorers and API

## Privacy

The extension:
- Does not collect personal data
- Stores settings locally in browser
- Sends only wallet addresses to API for analysis
- Does not track browsing history
- Uses secure WebSocket connections

## Version History

### v1.0.0
- Initial release
- Wallet scanning popup
- Explorer integration
- Real-time alerts
- Options/settings page

## Support

For issues or feature requests:
- Website: https://cryptorugmunch.com
- Web App: https://app.cryptorugmunch.com
- Email: support@cryptorugmunch.com

## License

Copyright (c) 2024 Rug Munch Intel. All rights reserved.
