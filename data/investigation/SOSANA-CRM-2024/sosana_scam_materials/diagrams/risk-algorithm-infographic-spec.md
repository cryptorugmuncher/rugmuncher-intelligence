# Risk Scoring Algorithm Infographic - Design Specification

**Format**: 1-page vertical infographic (11" × 17" portrait, or 1100px × 1700px for digital)
**Title**: "CryptoRugMunch: 12-Metric Risk Analysis in 3 Seconds"
**Target Audience**: Technical users, investors, security-conscious traders
**Purpose**: Visualize the sophisticated risk scoring algorithm that powers CryptoRugMunch's scam detection

---

## Layout Overview

```
┌───────────────────────────────────────────────────────────┐
│                                                            │
│      CRYPTORUGMUNCH: 12-METRIC RISK ANALYSIS IN 3 SECONDS │
│               Powered by AI-Optimized Weights              │
│                                                            │
└───────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────┐
│  RISK SCORE FORMULA                                       │
│  RiskScore = 100 - Σ(metric_penalty_i × weight_i)        │
│  Lower score = Safer token | Higher score = Riskier      │
└───────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────┐
│  12 METRICS GRID (3 columns × 4 rows)                    │
│  [Metric 1] [Metric 2] [Metric 3]                        │
│  [Metric 4] [Metric 5] [Metric 6]                        │
│  [Metric 7] [Metric 8] [Metric 9]                        │
│  [Metric 10] [Metric 11] [Metric 12]                     │
└───────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────┐
│  RISK CATEGORIES & SCORE RANGES                          │
│  0-30: SAFE | 31-60: CAUTION | 61-100: HIGH RISK        │
└───────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────┐
│  EXAMPLE CALCULATIONS (Safe vs Scam)                     │
│  Side-by-side comparison                                 │
└───────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────┐
│  DATA SOURCES & PERFORMANCE                               │
│  Helius | Birdeye | Rugcheck | 3-sec SLA | 92% accuracy │
└───────────────────────────────────────────────────────────┘
```

---

## Section 1: Title & Formula (Top 15%)

**Background**: Deep Purple (#2E1A47) gradient to darker purple (#1F0E2E)
**Text Color**: White

```
┌─────────────────────────────────────────────────────────────┐
│                                                              │
│     🛡️ CRYPTORUGMUNCH: 12-METRIC RISK ANALYSIS IN 3 SECONDS │
│                                                              │
│                  Powered by AI-Optimized Weights            │
│               92% Scam Detection Accuracy | 12% FP Rate     │
│                                                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  RISK SCORE FORMULA                                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  RiskScore = 100 - Σ(metric_penalty_i × weight_i)          │
│               i=1 to 12                                     │
│                                                              │
│  Where:                                                     │
│  • RiskScore: Final score (0-100, higher = riskier)        │
│  • metric_penalty_i: Penalty for metric i (0 to max penalty)│
│  • weight_i: Relative importance of metric i               │
│                                                              │
│  Score Ranges:                                              │
│  0-30:   ✅ SAFE (Low risk, likely legitimate)             │
│  31-60:  ⚠️ CAUTION (Medium risk, investigate further)     │
│  61-100: 🚨 HIGH RISK (Likely scam, avoid trading)         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Typography**:
- Title: Inter Bold, 24pt, white
- Subtitle: Inter Regular, 14pt, Electric Blue (#00D9FF)
- Formula: JetBrains Mono, 16pt, white (mathematical notation)
- "Where" definitions: Inter Regular, 11pt, white with 90% opacity

**Visual Elements**:
- Shield icon (60px) with bite mark (brand orange)
- Subtle particle effect background (optional for digital)

---

## Section 2: 12 Metrics Grid (Main Content - 60%)

**Layout**: 3 columns × 4 rows grid
**Spacing**: 20px gutter between boxes
**Box Size**: 300px wide × 220px tall per metric

### Metric Box Template

```
┌────────────────────────────────────────┐
│  [Icon 48px]                          │
│  METRIC NAME                           │
│  Weight: XX%                           │
├────────────────────────────────────────┤
│  Red Flag Threshold:                   │
│  • [Threshold value]                   │
│                                        │
│  Max Penalty: -XXpts                   │
│                                        │
│  Why It Matters:                       │
│  [1-2 sentence explanation]            │
│                                        │
│  Data Source: [Provider]               │
└────────────────────────────────────────┘
```

---

### Metric 1: Total Liquidity USD

**Icon**: 💰 (Money bag, 48px)
**Color Accent**: Safe Green (#00C48C)
**Border**: 3px solid Safe Green

```
┌────────────────────────────────────────┐
│  💰                                    │
│  TOTAL LIQUIDITY USD                   │
│  Weight: 20% (Highest)                 │
├────────────────────────────────────────┤
│  Red Flag Thresholds:                  │
│  • <$5,000: -25pts (max penalty)      │
│  • <$10,000: -20pts                    │
│  • <$50,000: -12pts                    │
│  • <$100,000: -5pts                    │
│  • ≥$100,000: 0pts ✅                  │
│                                        │
│  Why It Matters:                       │
│  Low liquidity = easy price manipulation│
│  Scammers avoid deep liquidity pools  │
│                                        │
│  Data Source: Birdeye API (TVL)        │
└────────────────────────────────────────┘
```

---

### Metric 2: LP Lock Status

**Icon**: 🔒 (Lock, 48px)
**Color Accent**: Brand Orange (#FF6B35)
**Border**: 3px solid Brand Orange

```
┌────────────────────────────────────────┐
│  🔒                                    │
│  LP LOCK STATUS                        │
│  Weight: 15%                           │
├────────────────────────────────────────┤
│  Red Flag Thresholds:                  │
│  • Unlocked: -20pts (max penalty)     │
│  • Locked <30 days: -15pts             │
│  • Locked 30-90 days: -8pts            │
│  • Locked >90 days: 0pts ✅            │
│                                        │
│  Why It Matters:                       │
│  Unlocked LP = creator can rug pull   │
│  by draining liquidity pool anytime   │
│                                        │
│  Data Source: Helius DAS API + Birdeye│
└────────────────────────────────────────┘
```

---

### Metric 3: Top 10 Holder Percentage

**Icon**: 👥 (People, 48px)
**Color Accent**: Caution Yellow (#FFB800)
**Border**: 3px solid Caution Yellow

```
┌────────────────────────────────────────┐
│  👥                                    │
│  TOP 10 HOLDER %                       │
│  Weight: 15%                           │
├────────────────────────────────────────┤
│  Red Flag Thresholds:                  │
│  • >80%: -20pts (max penalty)         │
│  • >60%: -15pts                        │
│  • >50%: -10pts                        │
│  • <50%: 0pts ✅                       │
│                                        │
│  Why It Matters:                       │
│  High concentration = pump & dump risk│
│  Few holders can manipulate price     │
│                                        │
│  Data Source: Helius DAS API (balances)│
└────────────────────────────────────────┘
```

---

### Metric 4: Whale Count

**Icon**: 🐋 (Whale, 48px)
**Color Accent**: Electric Blue (#00D9FF)
**Border**: 3px solid Electric Blue

```
┌────────────────────────────────────────┐
│  🐋                                    │
│  WHALE COUNT                           │
│  Weight: 5%                            │
├────────────────────────────────────────┤
│  Red Flag Thresholds:                  │
│  • <5 whales: -8pts (max penalty)     │
│  • 5-10 whales: -4pts                  │
│  • >10 whales: 0pts ✅                 │
│                                        │
│  (Whale = holder with >1% of supply)  │
│                                        │
│  Why It Matters:                       │
│  Too few whales = coordinated dump risk│
│  More whales = better distribution    │
│                                        │
│  Data Source: Helius DAS API           │
└────────────────────────────────────────┘
```

---

### Metric 5: Mint Authority

**Icon**: 🏭 (Factory, 48px)
**Color Accent**: Danger Red (#E53935)
**Border**: 3px solid Danger Red

```
┌────────────────────────────────────────┐
│  🏭                                    │
│  MINT AUTHORITY                        │
│  Weight: 12%                           │
├────────────────────────────────────────┤
│  Red Flag Thresholds:                  │
│  • Enabled: -15pts (max penalty) 🚨   │
│  • Disabled: 0pts ✅                   │
│                                        │
│  Why It Matters:                       │
│  Mint authority = creator can print   │
│  unlimited tokens, diluting supply    │
│  Massive red flag for scams           │
│                                        │
│  Data Source: Helius DAS API           │
│  (getMint.mintAuthority field)         │
└────────────────────────────────────────┘
```

---

### Metric 6: Freeze Authority

**Icon**: ❄️ (Snowflake, 48px)
**Color Accent**: Danger Red (#E53935)
**Border**: 3px solid Danger Red

```
┌────────────────────────────────────────┐
│  ❄️                                    │
│  FREEZE AUTHORITY                      │
│  Weight: 12%                           │
├────────────────────────────────────────┤
│  Red Flag Thresholds:                  │
│  • Enabled: -15pts (max penalty) 🚨   │
│  • Disabled: 0pts ✅                   │
│                                        │
│  Why It Matters:                       │
│  Freeze authority = creator can freeze│
│  all wallets, preventing sells        │
│  Classic honeypot mechanism           │
│                                        │
│  Data Source: Helius DAS API           │
│  (getMint.freezeAuthority field)       │
└────────────────────────────────────────┘
```

---

### Metric 7: Contract Verification

**Icon**: ✅ (Checkmark, 48px)
**Color Accent**: Safe Green (#00C48C)
**Border**: 3px solid Safe Green

```
┌────────────────────────────────────────┐
│  ✅                                    │
│  CONTRACT VERIFICATION                 │
│  Weight: 8%                            │
├────────────────────────────────────────┤
│  Red Flag Thresholds:                  │
│  • Unverified: -10pts (max penalty)   │
│  • Verified: 0pts ✅                   │
│                                        │
│  Why It Matters:                       │
│  Unverified contracts = hidden malicious│
│  code (e.g., hidden taxes, backdoors) │
│  Verified = source code is public     │
│                                        │
│  Data Source: Helius DAS API           │
│  (program deployment metadata)         │
└────────────────────────────────────────┘
```

---

### Metric 8: Volume/Liquidity Ratio

**Icon**: 📊 (Bar Chart, 48px)
**Color Accent**: Caution Yellow (#FFB800)
**Border**: 3px solid Caution Yellow

```
┌────────────────────────────────────────┐
│  📊                                    │
│  VOLUME/LIQUIDITY RATIO                │
│  Weight: 5%                            │
├────────────────────────────────────────┤
│  Red Flag Thresholds:                  │
│  • >10x: -12pts (max penalty)         │
│  • >5x: -8pts                          │
│  • 2-5x: -4pts                         │
│  • <2x: 0pts ✅                        │
│                                        │
│  Why It Matters:                       │
│  Abnormally high volume/liquidity =   │
│  wash trading or pump & dump activity │
│                                        │
│  Data Source: Birdeye API              │
│  (24h volume vs TVL)                   │
└────────────────────────────────────────┘
```

---

### Metric 9: Buy/Sell Tax Asymmetry (Honeypot Detection)

**Icon**: 🍯 (Honey Pot, 48px)
**Color Accent**: Danger Red (#E53935)
**Border**: 5px solid Danger Red (thicker for emphasis)

```
┌────────────────────────────────────────┐
│  🍯                                    │
│  BUY/SELL TAX ASYMMETRY                │
│  Weight: 15% (Honeypot Detector)       │
├────────────────────────────────────────┤
│  Red Flag Thresholds:                  │
│  • >10% diff: -50pts (max penalty) 🚨 │
│  • 5-10% diff: -25pts                  │
│  • 2-5% diff: -10pts                   │
│  • <2% diff: 0pts ✅                   │
│                                        │
│  Why It Matters:                       │
│  High sell tax vs buy tax = honeypot  │
│  You can buy but not sell = rug pull  │
│  CRITICAL scam indicator               │
│                                        │
│  Data Source: Rugcheck API             │
│  (simulated buy/sell transactions)     │
└────────────────────────────────────────┘
```

---

### Metric 10: Token Age

**Icon**: ⏰ (Clock, 48px)
**Color Accent**: Electric Blue (#00D9FF)
**Border**: 3px solid Electric Blue

```
┌────────────────────────────────────────┐
│  ⏰                                    │
│  TOKEN AGE                             │
│  Weight: 3%                            │
├────────────────────────────────────────┤
│  Red Flag Thresholds:                  │
│  • <24 hours: -5pts (max penalty)     │
│  • 24h-7 days: -2pts                   │
│  • >7 days: 0pts ✅                    │
│                                        │
│  Why It Matters:                       │
│  Very new tokens = higher risk        │
│  Scammers often rug within 48h        │
│  Older tokens = more time to build trust│
│                                        │
│  Data Source: Helius DAS API           │
│  (token mint timestamp)                │
└────────────────────────────────────────┘
```

---

### Metric 11: Creator Rugpull History

**Icon**: 🚩 (Red Flag, 48px)
**Color Accent**: Danger Red (#E53935)
**Border**: 3px solid Danger Red

```
┌────────────────────────────────────────┐
│  🚩                                    │
│  CREATOR RUGPULL HISTORY               │
│  Weight: 8%                            │
├────────────────────────────────────────┤
│  Red Flag Thresholds:                  │
│  • 3+ prior rugs: -30pts (max) 🚨     │
│  • 2 prior rugs: -20pts                │
│  • 1 prior rug: -10pts                 │
│  • 0 prior rugs: 0pts ✅               │
│                                        │
│  Why It Matters:                       │
│  Serial scammers reuse same wallets   │
│  Past behavior predicts future risk   │
│  Community scam database is key       │
│                                        │
│  Data Source: CryptoRugMunch Community │
│  Database + Rugcheck History API       │
└────────────────────────────────────────┘
```

---

### Metric 12: Social Media Verification

**Icon**: 🐦 (Twitter Bird, 48px)
**Color Accent**: Safe Green (#00C48C)
**Border**: 3px solid Safe Green

```
┌────────────────────────────────────────┐
│  🐦                                    │
│  SOCIAL MEDIA VERIFICATION             │
│  Weight: 2%                            │
├────────────────────────────────────────┤
│  Red Flag Thresholds:                  │
│  • No socials: -5pts (max penalty)    │
│  • 1 unverified: -3pts                 │
│  • 1+ verified: 0pts ✅                │
│                                        │
│  (Twitter, Telegram, Discord, website) │
│                                        │
│  Why It Matters:                       │
│  No social presence = anonymous team  │
│  Verified socials = accountability    │
│  Low weight (many scams have fake socials)│
│                                        │
│  Data Source: Token metadata (Helius) │
│  + manual verification                 │
└────────────────────────────────────────┘
```

---

## Section 3: Risk Categories & Visual Scale (15%)

**Background**: White with gradient overlay
**Layout**: Horizontal scale with 3 zones

```
┌─────────────────────────────────────────────────────────────┐
│                  RISK SCORE INTERPRETATION                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┬──────────────┬──────────────────────────┐│
│  │   0 - 30     │   31 - 60    │      61 - 100           ││
│  │              │              │                          ││
│  │   ✅ SAFE    │  ⚠️ CAUTION   │   🚨 HIGH RISK          ││
│  │              │              │                          ││
│  │ Low risk     │ Medium risk  │ Likely scam             ││
│  │ Likely       │ Investigate  │ Avoid trading           ││
│  │ legitimate   │ further      │ Report to community     ││
│  │              │              │                          ││
│  │ GREEN        │ YELLOW       │ RED                     ││
│  │ Background   │ Background   │ Background              ││
│  └──────────────┴──────────────┴──────────────────────────┘│
│                                                              │
│  Historical Accuracy (10,000+ scans):                       │
│  • Scams detected: 92% (920/1,000 confirmed scams)         │
│  • False positives: 12% (120/1,000 legitimate tokens)      │
│  • False negatives: 8% (80/1,000 scams missed)             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Design Specifications**:
- Three equal-width boxes (33% each)
- Color backgrounds:
  - SAFE: Light green (#E8F5E9)
  - CAUTION: Light yellow (#FFF9E6)
  - HIGH RISK: Light red (#FFEBEE)
- Large emoji icons (64px)
- Score ranges in bold (Inter Bold 18pt)
- Typography: Inter SemiBold 14pt for zone names, Inter Regular 11pt for descriptions

---

## Section 4: Example Calculations (10%)

**Background**: Light gray (#F5F5F5)
**Layout**: Two-column side-by-side comparison

```
┌─────────────────────────────────────────────────────────────┐
│              EXAMPLE CALCULATIONS (Side-by-Side)            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────┬──────────────────────────────┐ │
│  │  ✅ SAFE TOKEN         │  🚨 SCAM TOKEN              │ │
│  │  Score: 12/100         │  Score: 87/100              │ │
│  ├────────────────────────┼──────────────────────────────┤ │
│  │                        │                              │ │
│  │ 💰 Liquidity: $500K   │ 💰 Liquidity: $2K           │ │
│  │    Penalty: 0pts       │    Penalty: -25pts          │ │
│  │                        │                              │ │
│  │ 🔒 LP Lock: 6mo       │ 🔒 LP Lock: Unlocked        │ │
│  │    Penalty: 0pts       │    Penalty: -20pts          │ │
│  │                        │                              │ │
│  │ 👥 Top 10: 30%        │ 👥 Top 10: 85%              │ │
│  │    Penalty: 0pts       │    Penalty: -20pts          │ │
│  │                        │                              │ │
│  │ 🏭 Mint Auth: Disabled│ 🏭 Mint Auth: Enabled 🚨   │ │
│  │    Penalty: 0pts       │    Penalty: -15pts          │ │
│  │                        │                              │ │
│  │ ❄️ Freeze Auth: Disabled│ ❄️ Freeze Auth: Enabled 🚨│ │
│  │    Penalty: 0pts       │    Penalty: -15pts          │ │
│  │                        │                              │ │
│  │ 🍯 Tax Asymmetry: 0%  │ 🍯 Tax Asymmetry: 25% 🚨   │ │
│  │    Penalty: 0pts       │    Penalty: -50pts          │ │
│  │                        │                              │ │
│  │ ... (6 more metrics)   │ ... (6 more metrics)        │ │
│  │                        │                              │ │
│  ├────────────────────────┼──────────────────────────────┤ │
│  │ Total Penalty: -12pts  │ Total Penalty: -87pts       │ │
│  │ Risk Score: 100-12=12  │ Risk Score: 100-87=13 🚨    │ │
│  │                        │                              │ │
│  │ ✅ SAFE TO TRADE      │ 🚨 DO NOT TRADE             │ │
│  └────────────────────────┴──────────────────────────────┘ │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Typography**: JetBrains Mono 10pt for penalties, Inter SemiBold 12pt for final scores
**Color Coding**: Green checkmarks for safe, red alerts for scam

---

## Section 5: Data Sources & Performance (Bottom)

**Background**: Deep Purple (#2E1A47)
**Text Color**: White

```
┌─────────────────────────────────────────────────────────────┐
│                  DATA SOURCES & PERFORMANCE                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  PRIMARY DATA PROVIDERS:                                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Helius  │  │ Birdeye │  │ Rugcheck│  │  Solana  │   │
│  │ DAS API │  │  API    │  │  API    │  │   RPC    │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                              │
│  PERFORMANCE METRICS:                                       │
│  • Scan Speed: <3 seconds (p95 latency)                    │
│  • Cache Hit Rate: 70%+ (reduces API costs)                 │
│  • Scam Detection Accuracy: 92% (920/1,000 confirmed scams) │
│  • False Positive Rate: 12% (improving with ML training)    │
│                                                              │
│  ALGORITHMIC APPROACH:                                      │
│  • Rule-based system (not black-box AI)                    │
│  • Explainable results (see exact penalty breakdown)        │
│  • AI-optimized weights (trained on 10,000+ historical scans)│
│  • Defense in depth (12 independent checks)                 │
│                                                              │
│  Learn more: cryptorugmunch.com/risk-algorithm              │
│  Try it now: t.me/cryptorugmunch_bot → /scan <address>     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Icons**: 40px provider logos (Helius, Birdeye, Rugcheck, Solana)
**Typography**: Inter Regular 11pt for body text, Inter Bold 13pt for metrics

---

## Export Specifications

### For Print

- **Format**: PDF
- **Size**: 11" × 17" (tabloid, portrait)
- **Resolution**: 300 DPI
- **Color Mode**: CMYK
- **Bleed**: 0.125" on all sides
- **Fonts**: Embed Inter and JetBrains Mono

### For Digital (Social Media)

- **Format**: PNG
- **Size**: 1100px × 1700px (Instagram/Twitter optimized)
- **Resolution**: 150 DPI
- **Color Mode**: RGB
- **Optimize**: <800KB file size

### For Web (Documentation)

- **Format**: SVG (vector) or WebP (raster)
- **Size**: Responsive (max-width: 100%)
- **Color Mode**: RGB
- **Accessibility**: Include alt text for all metrics

---

## Design Tools & Implementation

### Figma Template

**Artboard Setup**:
1. Create artboard: 1100px × 1700px (portrait)
2. Import brand colors: #2E1A47, #FF6B35, #00D9FF, #00C48C, #FFB800, #E53935
3. Import Inter + JetBrains Mono fonts

**Component Structure**:
```
Figma Layers:
├── Title Section (Deep Purple background)
├── Formula Box (white background, border)
├── Metrics Grid (12 auto-layout frames, 3×4)
│   ├── Metric 1 (Safe Green accent)
│   ├── Metric 2 (Brand Orange accent)
│   ├── ... (10 more metrics)
├── Risk Scale (3 colored zones)
├── Example Comparison (2-column layout)
└── Data Sources Footer (Deep Purple)
```

**Reusable Components**:
- Metric box template (parametric: icon, title, weight, thresholds)
- Risk zone badge (SAFE, CAUTION, HIGH RISK)
- Data provider logo box

**Export**:
- PNG 2x (2200px × 3400px for retina)
- PDF (print quality, CMYK)
- SVG (for web)

### Canva Template

**Instructions**:
1. Search for "Infographic" templates → Select vertical layout
2. Customize to 11" × 17" portrait
3. Replace colors with brand palette
4. Use built-in icon library for emojis (💰, 🔒, 👥, etc.)
5. Create 12 boxes using "Grids" feature (3×4)
6. Export: PDF (high quality) or PNG (4x resolution)

### Adobe Illustrator

**Setup**:
1. New document: 11" × 17" portrait, CMYK mode
2. Create artboards for each section (easier editing)
3. Use Grid tool for 3×4 metric layout
4. Paragraph Styles: Create styles for "Metric Title", "Weight", "Threshold", "Why It Matters"
5. Export: PDF/X-1a (print), PNG 300 DPI, SVG (web)

---

## Accessibility Considerations

### Color Contrast

**WCAG AA Compliance** (4.5:1 ratio minimum):
- Deep Purple (#2E1A47) on white: 12.6:1 ✅
- Brand Orange (#FF6B35) on white: 3.8:1 ⚠️ (use darker #E85A1F for text)
- Danger Red (#E53935) on white: 4.7:1 ✅
- Safe Green (#00C48C) on white: 2.7:1 ⚠️ (use darker #008866 for text)

**Border Colors** (use full saturation for visibility):
- Use 3px borders minimum for metric boxes
- 5px for critical metrics (honeypot detection)

### Alt Text (for digital version)

```
"CryptoRugMunch Risk Scoring Algorithm infographic showing 12 security metrics used to detect cryptocurrency scams. Metrics include: Total Liquidity (20% weight), LP Lock Status (15%), Top 10 Holder Percentage (15%), Whale Count (5%), Mint Authority (12%), Freeze Authority (12%), Contract Verification (8%), Volume/Liquidity Ratio (5%), Buy/Sell Tax Asymmetry for honeypot detection (15%), Token Age (3%), Creator Rugpull History (8%), and Social Media Verification (2%). Risk scores range from 0-30 (SAFE) to 61-100 (HIGH RISK). Example comparison shows safe token scoring 12/100 vs scam token scoring 87/100. Data sources: Helius DAS API, Birdeye API, Rugcheck API. Performance: 92% scam detection accuracy, <3 second scan speed."
```

### Screen Reader Support

- Label each metric box with descriptive title + weight
- Include "max penalty" values in alt text
- Explain the formula in plain language

---

## Data Sources

All metric weights, thresholds, and penalties are sourced from:
- `docs/03-TECHNICAL/integrations/telegram-bot-risk-algorithm.md` (2,100+ lines)
- Accuracy metrics from internal testing logs (10,000+ historical scans)

**Update Cadence**:
- **Monthly**: Accuracy metrics (as more scans are processed)
- **Quarterly**: Metric weights (if ML optimization suggests improvements)
- **Major updates**: New metrics added (e.g., smart contract auditing, wallet clustering)

---

## Usage Rights & Attribution

**Internal Use**: Freely use for documentation, investor presentations, marketing materials

**Public Use**: Attribution required ("Source: CryptoRugMunch Risk Algorithm - cryptorugmunch.com/risk-algorithm")

**Modifications**:
- Metric weight updates: OK (as long as based on latest algorithm version)
- Visual design changes: OK (maintain brand recognition)
- Simplification for non-technical audiences: OK (but mark as "simplified")
- Logo removal: NOT OK

**Commercial Use**: Contact @newInstanceOfObject / dev.crm.paradox703@passinbox.com for licensing

---

## Interactive Web Version (Optional Enhancement)

For advanced use cases, create an **interactive calculator** where users can:
- Input values for each metric
- See real-time risk score calculation
- Toggle metrics on/off to see impact on final score
- Compare two tokens side-by-side

**Implementation**: React component with state management for metric inputs, live calculation display

---

**Document Status**: ✅ Specification Complete
**Last Updated**: 2025-01-20
**Next Steps**:
1. Design visual in Figma/Canva using this specification
2. Export to PNG/PDF/SVG formats
3. Share with technical team for algorithm validation
4. Include in Technical Whitepaper (Section 4: Risk Scoring Algorithm)
5. Use for investor pitch deck (Slide 8: Product Demo)
6. Post on Twitter/Medium as educational content (drive traffic to bot)
