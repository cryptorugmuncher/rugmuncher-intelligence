# RMI Gamification & Monetization System

## Overview

Making crypto scam investigation addictive, competitive, and profitable through gamification and tiered monetization.

---

## 🎮 Core Gamification Features

### 1. User Progression System

**Investigator Levels:**
- **Rookie** (0-50 scans) - Starting level
- **Analyst** (51-200 scans) - Unlocks advanced filters
- **Detective** (201-500 scans) - Unlocks batch scanning
- **Special Agent** (501-1000 scans) - Priority queue access
- **Master Investigator** (1001-2500 scans) - Exclusive features
- **Legend** (2500+ scans) - VIP status, revenue share

**XP System:**
- Base scan: +10 XP
- First to call scam: +100 XP (bonus)
- Accurate prediction: +50 XP
- Report verified: +200 XP
- Streak bonus: +5 XP per day (max +50)
- Social share: +25 XP
- Referral: +100 XP

### 2. Badge System

**Achievement Badges:**
```python
BADGES = {
    # Scan Milestones
    "first_scan": {"name": "First Steps", "icon": "🎯", "desc": "Completed first wallet scan"},
    "scan_100": {"name": "Centurion", "icon": "💯", "desc": "100 scans completed"},
    "scan_1000": {"name": "Millennium", "icon": "🔱", "desc": "1000 scans completed"},
    "scan_10000": {"name": "Legendary", "icon": "👑", "desc": "10000 scans completed"},
    
    # Accuracy Badges
    "sharpshooter": {"name": "Sharpshooter", "icon": "🎯", "desc": "90% accuracy over 100 scans"},
    "psychic": {"name": "Psychic", "icon": "🔮", "desc": "Predicted 10 scams before they happened"},
    "spot_on": {"name": "Spot On", "icon": "✅", "desc": "100% accuracy streak of 20 scans"},
    
    # Speed Badges
    "quick_draw": {"name": "Quick Draw", "icon": "⚡", "desc": "First to call a major scam"},
    "lightning": {"name": "Lightning", "icon": "⚡⚡", "desc": "First to call 10 scams"},
    "prophet": {"name": "Prophet", "icon": "🔥", "desc": "First to call 50 scams"},
    
    # Social Badges
    "influencer": {"name": "Influencer", "icon": "📢", "desc": "100 referrals"},
    "community_hero": {"name": "Community Hero", "icon": "🦸", "desc": "Helped 50 users in chat"},
    "trendsetter": {"name": "Trendsetter", "icon": "📈", "desc": "Report trended on social media"},
    
    # Special Badges
    "whistleblower": {"name": "Whistleblower", "icon": "🚨", "desc": "Exposed $1M+ scam"},
    " Rico_buster": {"name": "RICO Buster", "icon": "⚖️", "desc": "Contributed to federal case"},
    "savior": {"name": "Savior", "icon": "🛡️", "desc": "Prevented $100K+ in losses"},
    "night_watch": {"name": "Night Watch", "icon": "🌙", "desc": "Active 30 days straight"},
    "early_bird": {"name": "Early Bird", "icon": "🐦", "desc": "Found scam within 1 hour of launch"},
    "diamond_hands": {"name": "Diamond Hands", "icon": "💎", "desc": "Held investigation through crash"},
}
```

**Rare/Legendary Badges:**
- **Syndicate Slayer** - Helped take down criminal network
- **Zero Day** - Found critical vulnerability
- **FBI Collaborator** - Provided evidence to law enforcement
- **Crypto Guardian** - Protected $10M+ in user funds

### 3. Leaderboards

**Global Rankings:**
- Top Investigators (by XP)
- Most Accurate (by prediction rate)
- Speed Demons (first-to-call)
- RICO Contributors (federal case help)
- Community Heroes (social score)

**Weekly/Monthly Competitions:**
- Weekly Scan Challenge
- Monthly Accuracy Contest
- Scam Prediction Tournament
- Bounty Hunter Season

**Rewards:**
- Top 10: Free scan packs
- Top 3: Premium subscription (1 month)
- #1: Revenue share + exclusive badge

### 4. Streaks & Daily Rewards

**Login Streaks:**
- Day 1: +5 bonus scans
- Day 3: +10 bonus scans
- Day 7: Free advanced scan
- Day 14: Premium feature trial (3 days)
- Day 30: Legendary badge + revenue share eligibility

**Daily Challenges:**
- "Scan 5 new wallets today" → +50 XP
- "Find 1 suspicious pattern" → +100 XP
- "Share report on Twitter" → +25 XP
- "Help 3 users in community" → +75 XP

### 5. Social Features

**Investigator Profiles:**
- Public profile with badges showcase
- Scan history (public/private toggle)
- Accuracy rating
- Specialization tags
- Referral link

**Teams/Clans:**
- Create investigation teams
- Team leaderboards
- Collaborative bounties
- Shared evidence vaults

**Trading Card System:**
- NFT-style cards for major scam takedowns
- Collectible cards for badges
- Trading between users
- Limited edition drops

---

## 💰 Monetization Structure

### Tier 1: FREE (Rookie)

**Features:**
- 3 scans per day
- Basic risk score
- Public leaderboard access
- Community chat (read-only)
- Basic badges

**Limitations:**
- No deep analysis
- No API access
- No batch scanning
- Delayed queue (5 min wait)
- Ads supported

### Tier 2: PRO ($19.99/month)

**Features:**
- 100 scans per day
- Full forensic analysis
- All API integrations
- Batch scanning (10 wallets)
- Priority queue
- Advanced badges
- Custom alerts
- Export reports (PDF)
- Ad-free experience

**Bonuses:**
- 2x XP gain
- Exclusive Pro badges
- Early access to features
- Pro-only leaderboards

### Tier 3: ELITE ($49.99/month)

**Features:**
- Unlimited scans
- Real-time monitoring
- Batch scanning (100 wallets)
- API access (1000 calls/day)
- Custom integrations
- White-label reports
- Dedicated support
- Revenue share program (5%)
- All badges unlockable

**Exclusive:**
- Elite-only investigations
- Direct law enforcement liaison
- Custom badge creation
- Team management (10 members)

### Tier 4: ENTERPRISE (Custom pricing)

**For:**
- Exchanges
- DeFi platforms
- Law firms
- Government agencies
- Security firms

**Features:**
- Unlimited everything
- Private deployment
- Custom AI training
- SLA guarantee
- 24/7 dedicated support
- Compliance reporting
- API access (unlimited)
- Revenue share (15%)

---

## 🎯 Scan Pack System

**One-time purchases:**

| Pack | Scans | Price | Bonus |
|------|-------|-------|-------|
| Starter | 50 | $9.99 | +5 free |
| Pro | 200 | $29.99 | +25 free |
| Mega | 500 | $59.99 | +100 free |
| Ultimate | 2000 | $199.99 | +500 free + Legendary Badge |

**Promotions:**
- Flash sales (50% off)
- Bundle deals (Scan pack + Premium month)
- Referral bonuses (Buy pack, friend gets 25% off)
- Holiday specials (Black Friday, etc.)

---

## 🔌 API Monetization

### Public API Tiers

**Free Tier:**
- 100 calls/day
- Basic risk score only
- No historical data
- 5 requests/minute rate limit

**Developer Tier ($99/month):**
- 10,000 calls/day
- Full forensic data
- Historical analysis
- 100 requests/minute
- Webhook support

**Business Tier ($499/month):**
- 100,000 calls/day
- Batch API (1000 wallets/call)
- Real-time alerts
- 1000 requests/minute
- SLA: 99.9% uptime
- Dedicated endpoint

**Enterprise Tier (Custom):**
- Unlimited calls
- Private infrastructure
- Custom AI models
- 24/7 support
- Compliance certification
- Revenue share options

### API Endpoints (Monetized)

```python
ENDPOINTS = {
    # Free
    "/v1/risk-score": {"tier": "free", "cost": 1},
    "/v1/basic-scan": {"tier": "free", "cost": 1},
    
    # Paid
    "/v1/deep-analysis": {"tier": "paid", "cost": 5},
    "/v1/forensic-report": {"tier": "paid", "cost": 10},
    "/v1/timeline-reconstruction": {"tier": "paid", "cost": 15},
    "/v1/syndicate-mapping": {"tier": "paid", "cost": 20},
    "/v1/cross-project-analysis": {"tier": "paid", "cost": 25},
    "/v1/ghost-wallet-trace": {"tier": "paid", "cost": 30},
    "/v1/rico-report": {"tier": "paid", "cost": 50},
    
    # Enterprise
    "/v1/batch-scan": {"tier": "enterprise", "cost": 100},
    "/v1/real-time-monitoring": {"tier": "enterprise", "cost": 200},
    "/v1/custom-ai-model": {"tier": "enterprise", "cost": 500},
}
```

---

## 🎰 Addiction Mechanics

### Variable Reward System

**Mystery Scans:**
- Random chance to find "golden wallet" (high-value target)
- Loot box style: Scan pack drops randomly
- Surprise badges for unusual patterns

**Near-Miss Mechanics:**
- "You were 2 minutes away from being first!"
- "Just 10 XP from next level!"
- "Scan #99 - one more for Centurion badge!"

**Social Proof:**
- "3 people just scanned this wallet"
- "Trending in your network"
- "You discovered this before [Famous Investigator]"

### FOMO Triggers

**Limited Time:**
- "24 hours left for Double XP weekend"
- "Flash sale: 50% off scan packs (2 hours left)"
- "Only 100 Legendary badges remaining"

**Scarcity:**
- "Limited edition: RICO Buster badge (47 left)"
- "Exclusive: Early access to new features (Elite only)"
- "Founder status: First 1000 users only"

### Progress Visualization

**Level Progress Bars:**
- Animated XP bars
- "Level 42 - 85% to Level 43"
- Visual rank progression

**Heat Maps:**
- Your activity on blockchain
- Areas you've investigated
- "Uncharted territory" to explore

**Stats Dashboard:**
- Accuracy percentage
- Money saved (calculated)
- Scams prevented count
- Community impact score

---

## 📊 Database Schema Additions

```sql
-- User gamification
CREATE TABLE user_gamification (
    user_id BIGINT PRIMARY KEY,
    level INTEGER DEFAULT 1,
    xp_total INTEGER DEFAULT 0,
    xp_current INTEGER DEFAULT 0,
    scans_total INTEGER DEFAULT 0,
    scans_today INTEGER DEFAULT 0,
    accuracy_rate DECIMAL(5,2) DEFAULT 0.00,
    streak_days INTEGER DEFAULT 0,
    last_login TIMESTAMP,
    referral_code VARCHAR(20),
    referred_by BIGINT,
    revenue_share_eligible BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Badges
CREATE TABLE user_badges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id BIGINT,
    badge_id VARCHAR(50),
    earned_at TIMESTAMP DEFAULT NOW(),
    rarity VARCHAR(20), -- common, rare, epic, legendary
    showcase_position INTEGER,
    UNIQUE(user_id, badge_id)
);

-- Badge definitions
CREATE TABLE badge_definitions (
    badge_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100),
    description TEXT,
    icon VARCHAR(10),
    rarity VARCHAR(20),
    xp_bonus INTEGER DEFAULT 0,
    requirement_type VARCHAR(50),
    requirement_value INTEGER,
    hidden BOOLEAN DEFAULT FALSE
);

-- Leaderboards
CREATE TABLE leaderboard_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id BIGINT,
    leaderboard_type VARCHAR(50),
    period VARCHAR(20), -- daily, weekly, monthly, all_time
    score INTEGER,
    rank INTEGER,
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, leaderboard_type, period)
);

-- Subscriptions
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id BIGINT,
    tier VARCHAR(20),
    status VARCHAR(20),
    started_at TIMESTAMP,
    expires_at TIMESTAMP,
    auto_renew BOOLEAN DEFAULT TRUE,
    payment_method VARCHAR(50),
    amount_paid DECIMAL(10,2),
    scan_quota_daily INTEGER,
    api_quota_daily INTEGER,
    revenue_share_percent DECIMAL(5,2) DEFAULT 0.00
);

-- Scan packs (purchased)
CREATE TABLE scan_packs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id BIGINT,
    pack_type VARCHAR(50),
    scans_total INTEGER,
    scans_used INTEGER DEFAULT 0,
    purchased_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,
    price_paid DECIMAL(10,2)
);

-- API usage tracking
CREATE TABLE api_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    api_key VARCHAR(100),
    user_id BIGINT,
    endpoint VARCHAR(200),
    cost_credits INTEGER,
    response_time_ms INTEGER,
    status_code INTEGER,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Revenue share payouts
CREATE TABLE revenue_share (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id BIGINT,
    period_start DATE,
    period_end DATE,
    total_revenue DECIMAL(15,2),
    user_share DECIMAL(15,2),
    status VARCHAR(20),
    paid_at TIMESTAMP
);

-- Daily challenges
CREATE TABLE daily_challenges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    challenge_type VARCHAR(50),
    description TEXT,
    xp_reward INTEGER,
    requirement_count INTEGER,
    start_date DATE,
    end_date DATE,
    active BOOLEAN DEFAULT TRUE
);

-- User challenge progress
CREATE TABLE user_challenges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id BIGINT,
    challenge_id UUID,
    progress INTEGER DEFAULT 0,
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP
);
```

---

## 🚀 Implementation Priority

### Phase 1: Core Gamification (Week 1-2)
1. XP system
2. Level progression
3. Basic badges
4. Leaderboards

### Phase 2: Monetization (Week 3-4)
1. Free tier limitations
2. Pro subscription
3. Scan packs
4. Payment integration

### Phase 3: Social Features (Week 5-6)
1. Profiles
2. Teams
3. Referrals
4. Social sharing

### Phase 4: API Monetization (Week 7-8)
1. API key management
2. Rate limiting
3. Usage tracking
4. Enterprise sales

### Phase 5: Addiction Mechanics (Week 9-10)
1. Streaks
2. Daily challenges
3. Variable rewards
4. FOMO triggers

---

## 💡 Revenue Projections

**Conservative Estimates (Year 1):**
- 10,000 free users
- 500 Pro subscribers ($119k/year)
- 100 Elite subscribers ($60k/year)
- 20 Enterprise clients ($200k/year)
- Scan pack sales ($50k/year)
- API usage ($80k/year)

**Total: ~$509k/year**

**Aggressive Growth (Year 2):**
- 100,000 free users
- 5,000 Pro subscribers ($1.2M/year)
- 1,000 Elite subscribers ($600k/year)
- 100 Enterprise clients ($2M/year)
- Scan packs ($500k/year)
- API usage ($1M/year)

**Total: ~$5.3M/year**

---

This system makes investigating crypto scams as addictive as playing a game while generating serious revenue through tiered monetization.
