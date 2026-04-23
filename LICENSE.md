# RugMuncher Licensing & Intellectual Property Framework

## Overview

RugMuncher operates under a **dual-licensing model** designed to balance community transparency with commercial protection of proprietary intellectual property.

- **Frontend & Community Tooling**: Open-source under MIT License
- **Backend, Detection Engine & Training Infrastructure**: Proprietary — All Rights Reserved

---

## Frontend License (MIT)

All code within the `/frontend/` directory and any associated community plugins, themes, or UI components are released under the **MIT License**.

You are free to:
- Use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the frontend software
- Contribute improvements, themes, and widgets back to the community
- Fork the frontend for personal or commercial projects

See [frontend/LICENSE](frontend/LICENSE) for full MIT text.

---

## Backend License — Proprietary (All Rights Reserved)

All code, algorithms, data pipelines, model weights, training methodologies, and API infrastructure within the `/backend/` directory are **strictly proprietary** and remain the exclusive intellectual property of CryptoRugMuncher.

### What Is Protected

| Asset Category | Description |
|----------------|-------------|
| Detection Algorithms | Rug-pull classification models, heuristic scoring engines, behavioral pattern matching |
| Training Infrastructure | Data labeling pipelines, feature engineering logic, model retraining orchestration |
| Raw Data & Telemetry | On-chain feature extractions, historical scam pattern databases, honeypot telemetry |
| API Layer | REST/gRPC endpoints, rate-limiting logic, institutional data feeds |
| Operational Knowledge | Wallet clustering methods, sybil-detection heuristics, confidence-interval calculations |

### Restrictions

Without express written commercial license from CryptoRugMuncher:
- **No redistribution** of backend source code or compiled binaries
- **No reverse engineering** of API responses to extract model logic
- **No data scraping** beyond documented public rate limits
- **No competitive use** of disclosed training methodologies

---

## Institutional API & Data Licensing

Full API access, bulk historical data, and custom model deployments are available under commercial license to qualified institutional investors.

### Tiers

| Tier | Audience | Access Level |
|------|----------|--------------|
| **Community** | Public users | Frontend + basic read-only API (rate-limited) |
| **Developer** | Builders & integrators | Standard REST API with moderate rate limits |
| **Institutional** | VCs, exchanges, custody platforms, analytics firms | Full API, bulk data, raw signals, custom model training, SLA-backed uptime |

### Institutional Capabilities

- **Raw Threat Signals**: Unfiltered confidence scores and feature vectors
- **Bulk Historical Data**: Complete labeled dataset access for backtesting
- **Custom Model Training**: Fine-tuned detection models for specific chain ecosystems
- **Early-Access Feeds**: Real-time websocket streams of emerging threats
- **White-Label Integration**: Embeddable scan widgets and API co-branding

### Contact

For licensing inquiries, data partnership proposals, and custom deployments:

- **Email**: biz@rugmunch.io
- **Subject Line**: `Institutional API Licensing — [Organization Name]`

---

## Why This Split?

1. **Community Trust**: Open frontend development proves we have nothing to hide in our user experience.
2. **Competitive Moat**: The detection engine represents thousands of hours of research, data collection, and model refinement. Open-sourcing it would eliminate our ability to fund continued innovation.
3. **Security**: Public backend code becomes an immediate attack surface. Private source protects both our infrastructure and our users' scan data.
4. **Sustainable Economics**: Institutional licensing revenue funds free community tools, public research, and ongoing threat-intelligence operations.

---

## Contributor Notice

By submitting code, issues, or pull requests to this repository, you acknowledge that:
- Frontend contributions are licensed under MIT
- You have no claim to backend intellectual property
- Any backend-related contributions require a signed Contributor License Agreement (CLA) and may be rejected if they jeopardize proprietary status

---

*Last updated: 2026-04-23*
*CryptoRugMuncher — All Rights Reserved*
