# RMI Platform - Lovable UI Integration Guide

## Overview
This guide shows you how to integrate the RMI (RugMunch Intelligence) platform with Lovable for rapid UI development.

## Quick Start

### 1. Create Lovable Project
1. Go to [lovable.dev](https://lovable.dev)
2. Create new project
3. Choose "React + TypeScript + Tailwind"
4. Paste the design prompt below

### 2. Design System Prompt for Lovable

```
Create a crypto fraud investigation platform called "RMI" with the following design:

COLORS:
- Primary: #0ea5e9 (sky blue)
- Secondary: #8b5cf6 (violet)
- Accent: #f59e0b (amber)
- Success: #10b981 (emerald)
- Danger: #ef4444 (red)
- Warning: #f59e0b (amber)
- Background: #0f172a (slate 900)
- Surface: #1e293b (slate 800)
- Border: #334155 (slate 700)
- Text Primary: #f8fafc (slate 50)
- Text Secondary: #94a3b8 (slate 400)

TYPOGRAPHY:
- Headings: Inter, font-bold
- Body: Inter, font-normal
- Monospace: JetBrains Mono (for addresses, hashes)

COMPONENTS:
- Cards: rounded-xl, bg-slate-800, border border-slate-700
- Buttons: rounded-lg, px-4 py-2, hover:scale-105 transition
- Inputs: rounded-lg, bg-slate-900, border-slate-700
- Badges: rounded-full, px-2 py-1, text-xs
- Tables: rounded-xl overflow-hidden

RISK LEVEL COLORS:
- Critical: bg-red-500/20 text-red-400 border-red-500/50
- High: bg-orange-500/20 text-orange-400 border-orange-500/50
- Medium: bg-yellow-500/20 text-yellow-400 border-yellow-500/50
- Low: bg-blue-500/20 text-blue-400 border-blue-500/50
- Safe: bg-emerald-500/20 text-emerald-400 border-emerald-500/50

LAYOUT:
- Sidebar navigation (collapsed on mobile)
- Main content area with max-width-7xl
- Grid system: 1 col mobile, 2 col tablet, 3-4 col desktop
- Consistent spacing: gap-6

ANIMATIONS:
- Page transitions: fade-in
- Card hover: lift + glow
- Loading: pulse skeleton
- Success: checkmark animation
```

### 3. Page Structure

Create these pages in Lovable:

#### Dashboard (`/dashboard`)
```
- Stats cards row (Investigations, Scans Used, API Credits, Alerts)
- Recent investigations list
- Quick scan widget
- Risk distribution chart
- Recent alerts feed
```

#### Investigation Hub (`/investigations`)
```
- Create new investigation button
- Investigations grid/list
- Filter by status, risk level, date
- Search bar
- Sort options
```

#### Investigation Detail (`/investigations/:id`)
```
- Investigation header with title, status, risk badge
- Tabs: Overview | Evidence | Wallets | Clusters | Bubble Map | Report
- Evidence upload zone
- Wallet analysis results
- Cluster visualization
- Interactive bubble map
```

#### Wallet Analyzer (`/analyze/wallet`)
```
- Wallet address input
- Chain selector
- Analysis options checkboxes
- Results panel with:
  - Risk score gauge
  - Risk factors list
  - Connected wallets
  - Transaction patterns
  - Token holdings
  - Related scams
```

#### Token Scanner (`/analyze/token`)
```
- Token address input
- Quick scan button
- Results with:
  - Contract risk score
  - Holder analysis
  - Liquidity check
  - Mint authority status
  - Red flags list
```

#### Bubble Maps (`/bubble-maps`)
```
- Center wallet input
- Depth slider (1-5)
- Generate button
- Interactive graph visualization
- Node type legend
- Export options (PNG, SVG, JSON)
```

#### Cluster Detection (`/clusters`)
```
- Wallet list input (comma-separated)
- Detection settings
- Results with:
  - Cluster count
  - Confidence scores
  - Visualization
  - Wallet relationships
```

#### KOL Tracker (`/kol-tracker`)
```
- KOL search
- Leaderboard table
- Individual KOL profile:
  - Stats cards
  - Wallet list
  - Position table
  - Call history
  - Performance chart
```

#### Transparency Tracker (`/transparency`)
```
- Token search
- Score display (A+ to F)
- Category breakdown bars
- Red/green flags list
- Comparison with other projects
```

#### API Marketplace (`/marketplace`)
```
- Package cards grid
- Price comparison table
- CRM holder discount banner
- Purchase flow:
  - Package selection
  - Price calculation
  - Payment instructions
  - Verification
- User credits display
```

#### Premium Scans (`/premium`)
```
- Scan pack cards
- Pricing with CRM discount
- Purchase button
- Current scans remaining
- Usage history
```

#### Settings (`/settings`)
```
- Profile section
- Wallet connections
- Notification preferences
- API keys management
- Subscription details
```

## Component Library

### Pre-built Components

#### RiskBadge
```tsx
interface RiskBadgeProps {
  level: 'critical' | 'high' | 'medium' | 'low' | 'safe';
  score?: number;
  size?: 'sm' | 'md' | 'lg';
}
```

#### WalletAddress
```tsx
interface WalletAddressProps {
  address: string;
  chain?: 'solana' | 'ethereum';
  truncate?: boolean;
  showCopy?: boolean;
  showExplorer?: boolean;
}
```

#### StatCard
```tsx
interface StatCardProps {
  title: string;
  value: string | number;
  change?: number;
  icon: React.ReactNode;
  trend?: 'up' | 'down' | 'neutral';
}
```

#### EvidenceCard
```tsx
interface EvidenceCardProps {
  id: string;
  filename: string;
  fileType: string;
  size: number;
  uploadedAt: string;
  aiSummary?: string;
  onDelete: () => void;
  onView: () => void;
}
```

#### InvestigationCard
```tsx
interface InvestigationCardProps {
  id: string;
  title: string;
  tokenSymbol?: string;
  riskLevel: string;
  status: string;
  createdAt: string;
  evidenceCount: number;
  onClick: () => void;
}
```

#### BubbleMapVisualization
```tsx
interface BubbleMapVisualizationProps {
  data: {
    nodes: Array<{
      id: string;
      type: string;
      label: string;
      value: number;
    }>;
    edges: Array<{
      source: string;
      target: string;
      value: number;
    }>;
  };
  onNodeClick?: (node: any) => void;
  height?: number;
}
```

#### ClusterVisualization
```tsx
interface ClusterVisualizationProps {
  clusters: Array<{
    id: string;
    wallets: string[];
    confidence: number;
    type: string;
  }>;
  onClusterSelect?: (cluster: any) => void;
}
```

#### KOLCard
```tsx
interface KOLCardProps {
  handle: string;
  platform: string;
  followerCount: number;
  accuracyScore: number;
  totalCalls: number;
  verifiedWallets: string[];
  tags: string[];
}
```

#### TransparencyScore
```tsx
interface TransparencyScoreProps {
  score: number;
  grade: string;
  breakdown: {
    team: number;
    contract: number;
    treasury: number;
    communication: number;
    audit: number;
    roadmap: number;
  };
  redFlags: string[];
  greenFlags: string[];
}
```

#### PackageCard
```tsx
interface PackageCardProps {
  name: string;
  provider: string;
  credits: number;
  bonusCredits?: number;
  basePrice: number;
  discountPercent: number;
  crmDiscount?: number;
  finalPrice: number;
  features: string[];
  isPopular?: boolean;
  onSelect: () => void;
}
```

## API Integration

### Supabase Client Setup
```typescript
// lib/supabase.ts
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseKey = import.meta.env.VITE_SUPABASE_ANON_KEY

export const supabase = createClient(supabaseUrl, supabaseKey)
```

### TypeScript Types
```typescript
// types/index.ts
export interface Profile {
  id: string;
  wallet_address?: string;
  display_name?: string;
  is_crm_holder: boolean;
  crm_balance: number;
  subscription_tier: string;
  scans_remaining: number;
  total_scans_used: number;
}

export interface Investigation {
  id: string;
  user_id: string;
  title: string;
  description?: string;
  token_address?: string;
  token_symbol?: string;
  chain: string;
  status: 'active' | 'completed' | 'archived';
  risk_level: string;
  tags: string[];
  created_at: string;
  updated_at: string;
}

export interface WalletAnalysis {
  id: string;
  wallet_address: string;
  risk_score: number;
  risk_level: string;
  tags: string[];
  connections: Record<string, any>;
  findings: Record<string, any>;
  related_scams: string[];
  analyzed_at: string;
}

export interface KOLProfile {
  id: string;
  handle: string;
  platform: string;
  display_name?: string;
  follower_count: number;
  reputation_score: number;
  accuracy_score: number;
  total_calls: number;
  verified_wallets: string[];
  tags: string[];
}

export interface APIPackage {
  id: string;
  package_key: string;
  provider: string;
  tier: string;
  credits: number;
  bonus_credits: number;
  base_price_usd: number;
  discount_percent: number;
  final_price: number;
  features: string[];
}

export interface TransparencyScore {
  token_address: string;
  overall_score: number;
  overall_grade: string;
  category_scores: {
    team: number;
    contract: number;
    treasury: number;
    communication: number;
    audit: number;
    roadmap: number;
  };
  red_flags: string[];
  green_flags: string[];
}
```

### API Hooks
```typescript
// hooks/useInvestigations.ts
import { useQuery, useMutation } from '@tanstack/react-query'
import { supabase } from '@/lib/supabase'

export function useInvestigations() {
  return useQuery({
    queryKey: ['investigations'],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('investigations')
        .select('*')
        .order('created_at', { ascending: false })
      if (error) throw error
      return data
    }
  })
}

export function useCreateInvestigation() {
  return useMutation({
    mutationFn: async (investigation: Partial<Investigation>) => {
      const { data, error } = await supabase
        .from('investigations')
        .insert(investigation)
        .select()
        .single()
      if (error) throw error
      return data
    }
  })
}

// hooks/useWalletAnalysis.ts
export function useWalletAnalysis(walletAddress: string) {
  return useQuery({
    queryKey: ['wallet-analysis', walletAddress],
    queryFn: async () => {
      // Call your FastAPI backend
      const response = await fetch(`/api/analyze/wallet/${walletAddress}`)
      if (!response.ok) throw new Error('Analysis failed')
      return response.json()
    },
    enabled: !!walletAddress
  })
}
```

## Environment Variables

Create `.env` file:
```
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
VITE_API_BASE_URL=https://your-api-domain.com
```

## Deployment

### 1. Export from Lovable
- Click "Export" in Lovable
- Download ZIP or push to GitHub

### 2. Deploy to Vercel
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

### 3. Connect Custom Domain
- Add domain in Vercel dashboard
- Update DNS records
- Configure SSL

## Feature Checklist

### Core Features
- [ ] User authentication (Supabase Auth)
- [ ] Wallet connection (Phantom, Solflare)
- [ ] Investigation creation/management
- [ ] Evidence upload (Supabase Storage)
- [ ] Wallet analysis
- [ ] Token scanning
- [ ] Bubble maps
- [ ] Cluster detection

### Premium Features
- [ ] Scan pack purchase
- [ ] API marketplace
- [ ] Credit management
- [ ] Usage analytics

### KOL Features
- [ ] KOL search
- [ ] Wallet tracking
- [ ] Position monitoring
- [ ] Call verification

### Transparency Features
- [ ] Token search
- [ ] Score display
- [ ] Category breakdown
- [ ] Comparison tool

## Resources

- **Lovable Docs**: https://docs.lovable.dev
- **Supabase Docs**: https://supabase.com/docs
- **Tailwind Docs**: https://tailwindcss.com/docs
- **shadcn/ui**: https://ui.shadcn.com

## Support

For issues or questions:
- Lovable Discord: https://discord.gg/lovable
- Supabase Discord: https://discord.gg/supabase
