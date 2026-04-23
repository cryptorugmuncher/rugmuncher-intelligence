# RMI Browser Extension

Real-time crypto fraud protection for your browser. Scan tokens, detect scams, and protect your wallet while browsing DEXs.

## Features

### 🔍 Token Risk Analysis
- Instant risk scores on DexScreener, DexTools, Birdeye, Photon, GMGN
- 100-point security analysis
- Red flag warnings
- Click for detailed breakdown

### 🛡️ Phishing Protection
- Detects fake DEX and wallet sites
- Warns before connecting wallet
- Blocks known phishing domains
- Real-time site verification

### 📊 Portfolio Tracking
- Track your token watchlist
- Price change alerts
- Risk change notifications
- Quick scan any token

### 🔔 Smart Notifications
- Watchlist alerts
- Risk change warnings
- New scam detection
- Customizable settings

## Supported Sites

| Site | Risk Badges | Warnings |
|------|-------------|----------|
| DexScreener | ✅ | ✅ |
| DexTools | ✅ | ✅ |
| Birdeye | ✅ | ✅ |
| Photon | ✅ | ✅ |
| GMGN | ✅ | ✅ |
| Solscan | ✅ | ✅ |
| Etherscan | ✅ | ✅ |
| All Sites | ❌ | ✅ (Phishing) |

## Installation

### Chrome Web Store (Coming Soon)
1. Visit Chrome Web Store
2. Search "RMI - RugMunch Intelligence"
3. Click "Add to Chrome"

### Manual Installation (Developer)
1. Download extension files
2. Open Chrome → Extensions → Developer Mode
3. Click "Load Unpacked"
4. Select the `extension` folder

## Usage

### Quick Scan
1. Click extension icon
2. Enter token address
3. View instant risk score

### On DEX Sites
1. Browse DexScreener, DexTools, etc.
2. See risk badges on token listings
3. Click badge for detailed analysis
4. Add to watchlist for monitoring

### Settings
- Toggle warnings on/off
- Enable/disable phishing protection
- Manage notifications
- Clear data

## Privacy

**100% Privacy Focused:**
- ✅ All data stored locally
- ✅ No wallet addresses collected
- ✅ No browsing history tracked
- ✅ No personal data shared
- ✅ User consent required

See [DATA_STORAGE.md](DATA_STORAGE.md) for full details.

## Development

### Project Structure
```
extension/
├── manifest.json           # Extension config
├── content_scripts/        # Site integrations
│   ├── dexscreener.js     # DexScreener overlay
│   ├── dextools.js        # DexTools overlay
│   ├── birdeye.js         # Birdeye overlay
│   ├── photon.js          # Photon overlay
│   ├── gmgn.js            # GMGN overlay
│   ├── blockexplorer.js   # Solscan/Etherscan
│   ├── phishing-detector.js # Phishing protection
│   └── rmi-overlay.css    # Shared styles
├── popup/                  # Extension popup
│   ├── popup.html         # Popup UI
│   ├── popup.css          # Popup styles
│   └── popup.js           # Popup logic
├── background/             # Service worker
│   └── background.js      # Background tasks
├── icons/                  # Extension icons
└── README.md              # This file
```

### API Integration

The extension connects to RMI API:
```
Base URL: https://intel.cryptorugmunch.com/api
```

Endpoints used:
- `GET /contract-check/{address}` - Token analysis
- `GET /trending-scams` - Scam list
- `POST /report/phishing` - Report phishing

### Building

No build step required - vanilla JavaScript.

For production:
1. Update version in `manifest.json`
2. Zip the `extension` folder
3. Upload to Chrome Web Store

## Contributing

1. Fork the repository
2. Create feature branch
3. Submit pull request

## Support

- Website: https://intel.cryptorugmunch.com
- Twitter: @RugMunchIntel
- Telegram: @RugMunchIntel
- Email: support@cryptorugmunch.com

## License

MIT License - see LICENSE file

## Disclaimer

RMI provides risk analysis tools but cannot guarantee token safety. Always DYOR (Do Your Own Research) before investing. Risk scores are algorithmic estimates, not financial advice.

---

**Built with ❤️ by RugMunch Intelligence**
**Version 2.0.0**
