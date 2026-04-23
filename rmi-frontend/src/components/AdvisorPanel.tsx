import React, { useState, useEffect } from 'react';
import {
  Lightbulb,
  Scale,
  TrendingUp,
  ShieldAlert,
  Search,
  MessageSquare,
  CheckCircle,
  AlertTriangle,
  ExternalLink,
  RefreshCw,
  Clock,
  ThumbsUp,
  ThumbsDown,
  ChevronDown,
  ChevronUp,
  FileText,
  Zap,
  Target,
  Users,
  BarChart3,
  Globe,
  AlertCircle,
  Hash,
  Eye,
  Shield,
  Database,
  Wallet,
  Bot,
  Cpu,
  Activity,
  Server,
  Lock,
  Radio,
  Satellite,
  Crosshair,
  Network,
  Terminal,
  Key,
  Fingerprint,
  Scan,
  LayoutDashboard,
  Settings,
  Bell,
  Flag,
  Map,
  Binoculars,
  Brain,
  Sparkles,
  ChevronRight,
  Pause,
  Play,
  Power,
  AlertOctagon,
  FileCode,
  GitBranch,
  Box,
  Layers
} from 'lucide-react';

// ============================================
// TYPES
// ============================================
interface Advisor {
  id: string;
  name: string;
  codename: string;
  icon: React.ReactNode;
  description: string;
  lastUpdated: string;
  insights: Insight[];
  actions: Action[];
  clearanceLevel: number;
}

interface Insight {
  id: string;
  type: 'suggestion' | 'alert' | 'opportunity' | 'warning' | 'trend' | 'intel' | 'threat';
  title: string;
  description: string;
  priority: 'critical' | 'high' | 'medium' | 'low';
  timestamp: string;
  source?: string;
  evidence?: string[];
  impact?: string;
  classified?: boolean;
}

interface Action {
  id: string;
  label: string;
  status: 'pending' | 'in_progress' | 'completed' | 'dismissed' | 'requires_approval';
  handler: () => void;
  requiresAuth?: boolean;
}

interface DailyBriefing {
  date: string;
  threatLevel: 'green' | 'yellow' | 'orange' | 'red';
  totalActiveOperations: number;
  newIntel: number;
  requiresDecision: number;
  chiefRecommendations: Recommendation[];
}

interface Recommendation {
  id: string;
  priority: 'critical' | 'high' | 'medium' | 'low';
  category: 'operations' | 'legal' | 'technical' | 'financial' | 'security';
  title: string;
  description: string;
  estimatedTime: string;
  potentialImpact: string;
  reasoning: string[];
}

interface BotStatus {
  id: string;
  name: string;
  role: string;
  status: 'active' | 'standby' | 'maintenance' | 'offline';
  lastActivity: string;
  messagesHandled: number;
  swarmsAllocated: number;
}

interface WalletData {
  address: string;
  purpose: string;
  balance: string;
  network: string;
  lastTx: string;
  requiresApproval: boolean;
}

interface DomainStatus {
  domain: string;
  status: 'active' | 'pending' | 'expiring' | 'expired';
  expiresAt: string;
  traffic24h: number;
  sslStatus: 'valid' | 'expiring' | 'expired';
  dnsHealth: 'healthy' | 'issues' | 'critical';
}

interface DataUsageMetric {
  category: string;
  source: string;
  recordsProcessed: number;
  storageUsed: string;
  lastUpdated: string;
  humanVerified: boolean;
}

// ============================================
// MOCK DATA
// ============================================
const dailyBriefing: DailyBriefing = {
  date: new Date().toISOString(),
  threatLevel: 'orange',
  totalActiveOperations: 23,
  newIntel: 47,
  requiresDecision: 5,
  chiefRecommendations: [
    {
      id: 'r1',
      priority: 'critical',
      category: 'security',
      title: 'Address Active Phishing Campaign',
      description: 'Fake RMI airdrop site detected. 23 wallets compromised. Immediate response required.',
      estimatedTime: '30 minutes',
      potentialImpact: 'Prevent $100K+ additional losses, protect brand reputation',
      reasoning: [
        'Active scam using RMI branding detected 10 minutes ago',
        'User losses already at $45K and increasing',
        'Social media mentions spreading rapidly',
        'Waiting >1 hour risks mainstream crypto news pickup'
      ]
    },
    {
      id: 'r2',
      priority: 'high',
      category: 'technical',
      title: 'Optimize Database Query Performance',
      description: 'API latency degraded 275% over past week. Investigation table queries need indexing.',
      estimatedTime: '2 hours',
      potentialImpact: 'Restore 120ms response times, prevent user churn',
      reasoning: [
        'Response times increased from 120ms to 450ms',
        'User complaints in Discord increasing',
        'Competitor platforms average 150ms - we are 3x slower',
        'Database optimization scheduled, needs execution'
      ]
    },
    {
      id: 'r3',
      priority: 'high',
      category: 'operations',
      title: 'Publish Preemptive Scam Alert',
      description: 'Intelligence suggests "MegaLaunch" presale is coordinated scam. 3 days to launch.',
      estimatedTime: '1 hour',
      potentialImpact: 'Save community $2M+, establish RMI as protective leader',
      reasoning: [
        'Multiple OSINT indicators confirm scam pattern',
        '52K Telegram members at risk (80% are real users)',
        'High-profile target will generate media attention',
        'First-mover advantage on this intelligence'
      ]
    },
    {
      id: 'r4',
      priority: 'medium',
      category: 'financial',
      title: 'Review Q2 Tax Estimation',
      description: 'Quarterly tax payment due June 15. Current estimate may be insufficient.',
      estimatedTime: '45 minutes',
      potentialImpact: 'Avoid penalties, ensure compliance',
      reasoning: [
        'Q2 revenue exceeded projections by 15%',
        'Safe harbor requires 110% of prior year payments',
        'Current estimate may underpay by ~$8K',
        'CFO review recommended before payment'
      ]
    },
    {
      id: 'r5',
      priority: 'medium',
      category: 'operations',
      title: 'Create Base Chain Scanner Landing Page',
      description: '72% of new launches on Base but only 45% scanner coverage. Users searching but bouncing.',
      estimatedTime: '3 hours',
      potentialImpact: 'Capture 500+ daily searches, improve conversion 25%',
      reasoning: [
        'Search analytics show high intent Base queries',
        '62% bounce rate on current landing pages',
        'No direct "Base token scanner" content exists',
        'Technical foundation ready, needs frontend'
      ]
    }
  ]
};

const botStatuses: BotStatus[] = [
  { id: 'b1', name: '@rugmunchbot', role: 'Primary Scanner', status: 'active', lastActivity: '2s ago', messagesHandled: 45230, swarmsAllocated: 4 },
  { id: 'b2', name: '@rmi_alerts_bot', role: 'Alert Distribution', status: 'active', lastActivity: '5s ago', messagesHandled: 128450, swarmsAllocated: 2 },
  { id: 'b3', name: '@rmi_alpha_bot', role: 'Premium Alpha', status: 'active', lastActivity: '1m ago', messagesHandled: 8930, swarmsAllocated: 3 },
  { id: 'b4', name: '@rmi_snitch_bot', role: 'Tip Collection', status: 'active', lastActivity: '12s ago', messagesHandled: 3420, swarmsAllocated: 1 },
  { id: 'b5', name: '@rmi_rehab_bot', role: 'Education', status: 'standby', lastActivity: '5m ago', messagesHandled: 12340, swarmsAllocated: 1 },
  { id: 'b6', name: '@rmi_whale_bot', role: 'Whale Tracking', status: 'maintenance', lastActivity: '2h ago', messagesHandled: 56700, swarmsAllocated: 0 },
];

const walletData: WalletData[] = [
  { address: '0x742d...8f3a', purpose: 'Treasury Primary', balance: '245.5 ETH', network: 'Ethereum', lastTx: '2h ago', requiresApproval: false },
  { address: '0x91ab...2e4c', purpose: 'Operations', balance: '42.8 ETH', network: 'Ethereum', lastTx: '15m ago', requiresApproval: true },
  { address: '0x3f9c...7b1d', purpose: 'Staking Rewards', balance: '18.2 ETH', network: 'Base', lastTx: '1d ago', requiresApproval: false },
  { address: '0x8a2e...9f5b', purpose: 'Emergency Reserve', balance: '500.0 ETH', network: 'Ethereum', lastTx: '7d ago', requiresApproval: true },
];

const domainStatuses: DomainStatus[] = [
  { domain: 'cryptorugmunch.com', status: 'active', expiresAt: '2027-04-14', traffic24h: 45200, sslStatus: 'valid', dnsHealth: 'healthy' },
  { domain: 'rugmunch.io', status: 'active', expiresAt: '2027-08-22', traffic24h: 12800, sslStatus: 'valid', dnsHealth: 'healthy' },
  { domain: 'rmintel.net', status: 'expiring', expiresAt: '2026-05-01', traffic24h: 3200, sslStatus: 'expiring', dnsHealth: 'issues' },
  { domain: 'munchmaps.io', status: 'pending', expiresAt: 'N/A', traffic24h: 0, sslStatus: 'valid', dnsHealth: 'healthy' },
];

const dataUsageMetrics: DataUsageMetric[] = [
  { category: 'Contract Analysis', source: 'AI Swarm + User Scans', recordsProcessed: 2450000, storageUsed: '45.2 GB', lastUpdated: 'Just now', humanVerified: true },
  { category: 'Wallet Tracking', source: 'Blockchain Indexers', recordsProcessed: 89000000, storageUsed: '128.5 GB', lastUpdated: '2m ago', humanVerified: true },
  { category: 'Community Intel', source: 'Snitch Reports + Tips', recordsProcessed: 12500, storageUsed: '8.3 GB', lastUpdated: '5m ago', humanVerified: false },
  { category: 'Social Signals', source: 'X/Telegram Monitoring', recordsProcessed: 45000000, storageUsed: '156.2 GB', lastUpdated: '1m ago', humanVerified: true },
  { category: 'User Analytics', source: 'Frontend + API Logs', recordsProcessed: 890000, storageUsed: '23.1 GB', lastUpdated: '15m ago', humanVerified: true },
];

const swarmStatus = {
  totalAgents: 18,
  activeAgents: 15,
  tasksInQueue: 23,
  avgProcessingTime: '1.2s',
  lastDeployment: '4h ago',
  healthScore: 94,
};

// ============================================
// COMPONENT
// ============================================
const AdvisorPanel: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('briefing');
  const [activeAdvisor, setActiveAdvisor] = useState<string>('project');
  const [expandedInsight, setExpandedInsight] = useState<string | null>(null);
  const [expandedRec, setExpandedRec] = useState<string | null>('r1');
  const [refreshing, setRefreshing] = useState(false);
  const [humanOverride, setHumanOverride] = useState(false);
  const [terminalOpen, setTerminalOpen] = useState(false);
  const [lastGlobalUpdate, setLastGlobalUpdate] = useState(new Date().toISOString());

  // Chief of Staff Advisor Data
  const chiefAdvisor: Advisor = {
    id: 'chief',
    name: 'Chief of Staff',
    codename: 'DIRECTOR',
    icon: <Brain className="w-6 h-6 text-[#7c3aed]" />,
    description: 'Daily strategic briefing and prioritized recommendations',
    lastUpdated: 'Just now',
    clearanceLevel: 5,
    insights: [],
    actions: []
  };

  // Project Advisor
  const projectAdvisor: Advisor = {
    id: 'project',
    name: 'Operations Intelligence',
    codename: 'WATCHDOG',
    icon: <Crosshair className="w-6 h-6 text-yellow-400" />,
    description: 'Platform performance, user analytics, and growth opportunities',
    clearanceLevel: 4,
    lastUpdated: '2 minutes ago',
    insights: [
      {
        id: 'p1',
        type: 'intel',
        title: 'Real-Time Wallet Notifications Requested',
        description: '67% of ELITE tier users requested push notifications for tracked wallet movements. WebSocket infrastructure ready for deployment.',
        priority: 'high',
        timestamp: '15 minutes ago',
        source: 'SIGINT-USERFEEDBACK',
        evidence: ['Survey: 450 responses', 'Support tickets: 89 related', 'Discord requests: 156'],
        impact: '23% retention increase, $45K additional ARR',
        classified: false
      },
      {
        id: 'p2',
        type: 'opportunity',
        title: 'MetaMask Partnership Opportunity',
        description: 'MetaMask Snap integration could expose RMI to 30M+ users. No direct competitor in security Snap category.',
        priority: 'high',
        timestamp: '1 hour ago',
        source: 'OSINT-MARKET',
        evidence: ['MetaMask Snaps API released Q4 2024', 'User survey: 78% use MetaMask', 'No security competitor exists'],
        impact: '10K-50K new users, $150K partnership revenue',
        classified: false
      },
      {
        id: 'p4',
        type: 'threat',
        title: 'API Response Times Degrading',
        description: 'Average response time increased from 120ms to 450ms over past week. Database queries on investigation_cases table are bottleneck.',
        priority: 'critical',
        timestamp: '30 minutes ago',
        source: 'SIGINT-PERFORMANCE',
        evidence: ['Avg latency: 450ms (was 120ms)', 'Slow query log: investigation_cases', 'Error rate: 0.3% increase'],
        impact: 'User experience degradation, potential churn',
        classified: false
      }
    ],
    actions: [
      { id: 'pa1', label: 'Deploy WebSocket Notifications', status: 'requires_approval', requiresAuth: true, handler: () => {} },
      { id: 'pa2', label: 'Research MetaMask Partnership', status: 'in_progress', handler: () => {} },
      { id: 'pa3', label: 'Emergency Database Optimization', status: 'requires_approval', requiresAuth: true, handler: () => {} }
    ]
  };

  // Legal & Tax Advisor
  const legalAdvisor: Advisor = {
    id: 'legal',
    name: 'Legal & Compliance',
    codename: 'COUNSEL',
    icon: <Scale className="w-6 h-6 text-blue-400" />,
    description: 'Wyoming DAO LLC compliance, tax obligations, regulatory monitoring',
    clearanceLevel: 5,
    lastUpdated: '1 hour ago',
    insights: [
      {
        id: 'l1',
        type: 'alert',
        title: 'Wyoming Annual Report Due: 45 Days',
        description: 'Annual report and $60 fee due by June 1st. Late filing penalty: $200 + loss of good standing.',
        priority: 'high',
        timestamp: 'Today, 9:00 AM',
        source: 'COMPLIANCE-CALENDAR',
        evidence: ['Filing deadline: June 1, 2026', 'Current status: Good standing', 'Fee: $60'],
        impact: 'Avoid $200 penalty, maintain legal protection'
      },
      {
        id: 'l2',
        type: 'threat',
        title: 'SEC Increased Token Scrutiny',
        description: 'SEC announced increased enforcement on DeFi tokens. Review $CRM V2 tokenomics for Howey Test compliance.',
        priority: 'critical',
        timestamp: '2 days ago',
        source: 'OSINT-REGULATORY',
        evidence: ['SEC statement: April 10, 2026', 'Focus: "utility" token classification', 'Recent enforcement: 3 similar projects'],
        impact: 'Potential regulatory action, legal review needed immediately'
      },
      {
        id: 'l5',
        type: 'alert',
        title: 'Q2 Estimated Tax Payment Due June 15',
        description: 'Projected Q2 revenue: $125K. Estimated tax obligation: ~$31K. Safe harbor requires 110% of prior year.',
        priority: 'high',
        timestamp: 'Yesterday',
        source: 'FINANCE-TAX',
        evidence: ['Q1 actual: $118K', 'Q2 projected: $125K', 'Tax rate: ~25% effective'],
        impact: 'Avoid underpayment penalties (0.5%/month)'
      }
    ],
    actions: [
      { id: 'la1', label: 'File Wyoming Annual Report', status: 'pending', handler: () => {} },
      { id: 'la2', label: 'Emergency Legal Review: Token Compliance', status: 'requires_approval', requiresAuth: true, handler: () => {} },
      { id: 'la3', label: 'Prepare Q2 Tax Payment', status: 'pending', handler: () => {} }
    ]
  };

  // X/Twitter Trends Advisor
  const trendsAdvisor: Advisor = {
    id: 'trends',
    name: 'Social Intelligence',
    codename: 'ECHO',
    icon: <Radio className="w-6 h-6 text-purple-400" />,
    description: 'Real-time crypto Twitter sentiment, trending narratives, viral opportunities',
    clearanceLevel: 3,
    lastUpdated: '5 minutes ago',
    insights: [
      {
        id: 't1',
        type: 'trend',
        title: '#RugPull Viral Surge: +340%',
        description: 'Mentions of "rug pull" increased 340% in past 24h. Related to Base chain launchpad incident. Opportunity for RMI expertise positioning.',
        priority: 'high',
        timestamp: '20 minutes ago',
        source: 'SIGINT-SOCIAL',
        evidence: ['Mentions: 12,450 (24h)', 'Sentiment: 65% fearful', 'Top influencers: 15 discussing'],
        impact: 'Thread opportunity: 500K+ impressions possible'
      },
      {
        id: 't2',
        type: 'opportunity',
        title: 'AI Agent Token Narrative Exploding',
        description: '$AI and $AGENT tokens trending with $500M+ volume. RMI could position AI Swarm as security-focused alternative.',
        priority: 'high',
        timestamp: '2 hours ago',
        source: 'OSINT-MARKET',
        evidence: ['$AI volume: $230M (24h)', '$AGENT volume: $180M (24h)', 'Related keywords: +800%'],
        impact: 'Positioning: "AI for good - security not speculation"'
      },
      {
        id: 't4',
        type: 'intel',
        title: 'Base Chain Dominating Launches: 72%',
        description: '72% of new token launches now on Base. RMI scanner traffic shows only 45% Base coverage - intelligence gap identified.',
        priority: 'high',
        timestamp: '6 hours ago',
        source: 'SIGINT-CHAIN',
        evidence: ['New launches: 72% Base', 'RMI scans: 45% Base', 'Trend accelerating: +15% WoW'],
        impact: 'Technical priority: Enhance Base chain detection'
      }
    ],
    actions: [
      { id: 'ta1', label: 'Draft #RugPull Educational Thread', status: 'pending', handler: () => {} },
      { id: 'ta2', label: 'Create AI Security Positioning Content', status: 'in_progress', handler: () => {} }
    ]
  };

  // Scam Watch Advisor
  const scamAdvisor: Advisor = {
    id: 'scam',
    name: 'Threat Intelligence',
    codename: 'SENTINEL',
    icon: <ShieldAlert className="w-6 h-6 text-red-400" />,
    description: 'Emerging threats, active scams, preemptive community alerts',
    clearanceLevel: 5,
    lastUpdated: 'Just now',
    insights: [
      {
        id: 's1',
        type: 'threat',
        title: 'ACTIVE: Fake RMI Token Airdrop',
        description: 'Scammers impersonating RMI announcing fake $CRM V2 airdrop. Phishing site at rmi-airdrop[.]xyz stealing credentials.',
        priority: 'critical',
        timestamp: '10 minutes ago',
        source: 'HUMINT-SNICHT + SIGINT-PHISHING',
        evidence: ['Domain: rmi-airdrop.xyz', 'Wallets drained: 23 confirmed', 'Est. losses: $45K', 'Social posts: 8 fake accounts'],
        impact: 'Immediate action required: Issue warning, report domain, track funds'
      },
      {
        id: 's2',
        type: 'threat',
        title: 'New "Sleep Minting" Attack Vector',
        description: 'Novel honeypot: tokens appear tradable for 24h then become unsellable. 6 contracts deployed in past 48h.',
        priority: 'high',
        timestamp: '1 hour ago',
        source: 'SIGINT-CONTRACTS',
        evidence: ['Contracts flagged: 6', 'Pattern: Sell function disabled after block height', 'Est. victims: 180+ wallets'],
        impact: 'Update scanner: Add sleep minting detection'
      },
      {
        id: 's3',
        type: 'threat',
        title: 'Coordinated Presale Scam: "MegaLaunch"',
        description: 'Coordinated scam targeting 50K+ users. Fake team credentials, copied whitepaper, bot-filled social proof. Launch in 3 days.',
        priority: 'critical',
        timestamp: '3 hours ago',
        source: 'HUMINT-SNICHT + OSINT-INVESTIGATION',
        evidence: ['Telegram: 52K members (80% bots)', 'Team photos: AI-generated', 'Contract: Ownership not renounced', 'Soft cap: $2M target'],
        impact: 'Preemptive alert: Save potential $2M in losses'
      }
    ],
    actions: [
      { id: 'sa1', label: 'Issue Emergency Airdrop Warning', status: 'requires_approval', requiresAuth: true, handler: () => {} },
      { id: 'sa2', label: 'Report Phishing Domain to Registrars', status: 'pending', handler: () => {} },
      { id: 'sa3', label: 'Deploy Sleep Minting Detection', status: 'requires_approval', requiresAuth: true, handler: () => {} },
      { id: 'sa4', label: 'Publish MegaLaunch Investigation', status: 'in_progress', handler: () => {} }
    ]
  };

  // Community Search Analytics Advisor
  const searchAdvisor: Advisor = {
    id: 'search',
    name: 'Search Intelligence',
    codename: 'SPECTER',
    icon: <Scan className="w-6 h-6 text-green-400" />,
    description: 'User search patterns, knowledge gaps, content opportunities',
    clearanceLevel: 2,
    lastUpdated: '15 minutes ago',
    insights: [
      {
        id: 'cs1',
        type: 'intel',
        title: '"Recover rugged funds" +450%',
        description: 'Top search query this week. Users looking for recovery options after Base chain incidents.',
        priority: 'high',
        timestamp: '1 hour ago',
        source: 'SIGINT-SEARCH',
        evidence: ['Search volume: +450%', 'Support tickets: 78 related', 'Referral: Reddit/r/cryptorecovery'],
        impact: 'Create recovery guide, promote 1-1 Reimbursement Program'
      },
      {
        id: 'cs4',
        type: 'warning',
        title: 'High Bounce Rate: "Token Scanner"',
        description: '62% bounce rate for "token scanner" searches. Landing page not matching intent. Users expect instant scan tool.',
        priority: 'high',
        timestamp: '12 hours ago',
        source: 'SIGINT-ANALYTICS',
        evidence: ['Bounce rate: 62% (vs 35% avg)', 'Time on page: 8 seconds', 'Exit: /features, /pricing'],
        impact: 'UX fix: Create dedicated scanner landing page'
      }
    ],
    actions: [
      { id: 'csa1', label: 'Create Fund Recovery Content', status: 'pending', handler: () => {} },
      { id: 'csa2', label: 'Build Scanner Landing Page', status: 'pending', handler: () => {} }
    ]
  };

  const advisors = [chiefAdvisor, projectAdvisor, legalAdvisor, trendsAdvisor, scamAdvisor, searchAdvisor];
  const currentAdvisor = advisors.find(a => a.id === activeAdvisor) || projectAdvisor;

  const handleRefresh = () => {
    setRefreshing(true);
    setTimeout(() => {
      setRefreshing(false);
      setLastGlobalUpdate(new Date().toISOString());
    }, 2000);
  };

  const getInsightIcon = (type: string) => {
    switch (type) {
      case 'suggestion': return <Lightbulb className="w-5 h-5 text-yellow-400" />;
      case 'alert': return <AlertCircle className="w-5 h-5 text-red-400" />;
      case 'opportunity': return <Target className="w-5 h-5 text-green-400" />;
      case 'warning': return <AlertTriangle className="w-5 h-5 text-orange-400" />;
      case 'trend': return <TrendingUp className="w-5 h-5 text-purple-400" />;
      case 'intel': return <Satellite className="w-5 h-5 text-blue-400" />;
      case 'threat': return <ShieldAlert className="w-5 h-5 text-red-500" />;
      default: return <Zap className="w-5 h-5 text-[#7c3aed]" />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return 'bg-red-600/30 text-red-400 border-red-500/50 animate-pulse';
      case 'high': return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
      case 'medium': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'low': return 'bg-green-500/20 text-green-400 border-green-500/30';
      default: return 'bg-gray-500/20 text-gray-400';
    }
  };

  const getThreatLevelColor = (level: string) => {
    switch (level) {
      case 'green': return 'bg-green-500 shadow-[0_0_10px_rgba(34,197,94,0.5)]';
      case 'yellow': return 'bg-yellow-500 shadow-[0_0_10px_rgba(234,179,8,0.5)]';
      case 'orange': return 'bg-orange-500 shadow-[0_0_10px_rgba(249,115,22,0.5)]';
      case 'red': return 'bg-red-600 shadow-[0_0_15px_rgba(220,38,38,0.7)] animate-pulse';
      default: return 'bg-gray-500';
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0812] text-gray-100 font-mono selection:bg-[#7c3aed]/30">
      {/* Top Bar - Classified Header */}
      <div className="bg-gradient-to-r from-[#0f0c1d] via-[#1a1525] to-[#0f0c1d] border-b border-[#7c3aed]/30">
        <div className="max-w-[1600px] mx-auto px-6 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-6">
              {/* Logo */}
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-gradient-to-br from-[#7c3aed] to-[#4c1d95] rounded-lg flex items-center justify-center border border-[#7c3aed]/50 shadow-[0_0_15px_rgba(124,58,237,0.3)]">
                  <Shield className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="text-lg font-bold tracking-wider text-white">
                    RMI <span className="text-[#7c3aed]">COMMAND</span>
                  </h1>
                  <p className="text-xs text-gray-500 tracking-[0.2em]">ADVISOR PANEL // CLASSIFIED</p>
                </div>
              </div>

              {/* Classification Badge */}
              <div className="flex items-center gap-2 px-4 py-1.5 bg-red-600/10 border border-red-500/30 rounded">
                <Lock className="w-4 h-4 text-red-400" />
                <span className="text-xs font-bold text-red-400 tracking-wider">TOP SECRET//SCI</span>
              </div>
            </div>

            <div className="flex items-center gap-6">
              {/* Threat Level */}
              <div className="flex items-center gap-3">
                <span className="text-xs text-gray-500 uppercase tracking-wider">Threat Level</span>
                <div className={`w-3 h-3 rounded-full ${getThreatLevelColor(dailyBriefing.threatLevel)}`} />
                <span className="text-sm font-bold uppercase text-orange-400">{dailyBriefing.threatLevel}</span>
              </div>

              {/* Time */}
              <div className="flex items-center gap-2 text-xs text-gray-500">
                <Clock className="w-4 h-4" />
                <span>{new Date().toUTCString()}</span>
              </div>

              {/* Terminal Toggle */}
              <button
                onClick={() => setTerminalOpen(!terminalOpen)}
                className="flex items-center gap-2 px-3 py-1.5 bg-[#7c3aed]/10 border border-[#7c3aed]/30 rounded hover:bg-[#7c3aed]/20 transition-all"
              >
                <Terminal className="w-4 h-4 text-[#7c3aed]" />
                <span className="text-xs">TERMINAL</span>
              </button>

              {/* Human Override */}
              <button
                onClick={() => setHumanOverride(!humanOverride)}
                className={`flex items-center gap-2 px-3 py-1.5 rounded border transition-all ${
                  humanOverride
                    ? 'bg-green-500/20 border-green-500/50 text-green-400'
                    : 'bg-gray-800 border-gray-700 text-gray-400'
                }`}
              >
                <Fingerprint className="w-4 h-4" />
                <span className="text-xs font-bold">{humanOverride ? 'HUMAN OVERRIDE ACTIVE' : 'AUTONOMOUS MODE'}</span>
              </button>

              {/* Refresh */}
              <button
                onClick={handleRefresh}
                disabled={refreshing}
                className="flex items-center gap-2 px-3 py-1.5 bg-[#1a1525] border border-[#7c3aed]/30 rounded hover:bg-[#7c3aed]/10 transition-all"
              >
                <RefreshCw className={`w-4 h-4 text-[#7c3aed] ${refreshing ? 'animate-spin' : ''}`} />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Secondary Navigation */}
      <div className="bg-[#0f0c1d] border-b border-gray-800">
        <div className="max-w-[1600px] mx-auto px-6">
          <div className="flex items-center gap-1">
            {[
              { id: 'briefing', label: 'DAILY BRIEFING', icon: <LayoutDashboard className="w-4 h-4" /> },
              { id: 'intelligence', label: 'INTELLIGENCE', icon: <Binoculars className="w-4 h-4" /> },
              { id: 'operations', label: 'OPERATIONS', icon: <Server className="w-4 h-4" /> },
              { id: 'assets', label: 'ASSETS & WALLETS', icon: <Wallet className="w-4 h-4" /> },
              { id: 'domains', label: 'DOMAIN CONTROL', icon: <Globe className="w-4 h-4" /> },
              { id: 'data', label: 'DATA TRANSPARENCY', icon: <Database className="w-4 h-4" /> },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-3 text-xs font-semibold tracking-wider transition-all border-b-2 ${
                  activeTab === tab.id
                    ? 'text-[#7c3aed] border-[#7c3aed] bg-[#7c3aed]/5'
                    : 'text-gray-500 border-transparent hover:text-gray-300 hover:bg-gray-800/30'
                }`}
              >
                {tab.icon}
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-[1600px] mx-auto p-6">
        {/* ============================================ */}
        {/* DAILY BRIEFING TAB */}
        {/* ============================================ */}
        {activeTab === 'briefing' && (
          <div className="grid grid-cols-12 gap-6">
            {/* Chief Recommendations */}
            <div className="col-span-8 space-y-4">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-3">
                  <Brain className="w-6 h-6 text-[#7c3aed]" />
                  <h2 className="text-xl font-bold tracking-wider">
                    CHIEF OF STAFF <span className="text-[#7c3aed]">DIRECTIVE</span>
                  </h2>
                </div>
                <span className="text-xs text-gray-500">{dailyBriefing.chiefRecommendations.length} PRIORITY ACTIONS</span>
              </div>

              {dailyBriefing.chiefRecommendations.map((rec, idx) => (
                <div
                  key={rec.id}
                  className="bg-gradient-to-r from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg overflow-hidden hover:border-[#7c3aed]/30 transition-all"
                >
                  <div
                    className="p-5 cursor-pointer"
                    onClick={() => setExpandedRec(expandedRec === rec.id ? null : rec.id)}
                  >
                    <div className="flex items-start gap-4">
                      <div className="flex flex-col items-center gap-1">
                        <span className="text-2xl font-bold text-gray-600">{String(idx + 1).padStart(2, '0')}</span>
                        <div className={`w-2 h-2 rounded-full ${
                          rec.priority === 'critical' ? 'bg-red-500 animate-pulse' :
                          rec.priority === 'high' ? 'bg-orange-500' :
                          rec.priority === 'medium' ? 'bg-yellow-500' :
                          'bg-green-500'
                        }`} />
                      </div>

                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <span className={`px-2 py-0.5 text-[10px] font-bold rounded uppercase ${
                            rec.priority === 'critical' ? 'bg-red-500/20 text-red-400' :
                            rec.priority === 'high' ? 'bg-orange-500/20 text-orange-400' :
                            rec.priority === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
                            'bg-green-500/20 text-green-400'
                          }`}>
                            {rec.priority}
                          </span>
                          <span className="px-2 py-0.5 text-[10px] bg-gray-800 text-gray-400 rounded uppercase">
                            {rec.category}
                          </span>
                          <span className="text-xs text-gray-500">~{rec.estimatedTime}</span>
                        </div>

                        <h3 className="text-lg font-semibold text-white mb-2">{rec.title}</h3>
                        <p className="text-sm text-gray-400 leading-relaxed">{rec.description}</p>

                        <div className="flex items-center gap-2 mt-3 text-xs">
                          <BarChart3 className="w-4 h-4 text-[#7c3aed]" />
                          <span className="text-[#7c3aed]">Impact:</span>
                          <span className="text-gray-400">{rec.potentialImpact}</span>
                        </div>
                      </div>

                      <div className="flex items-center gap-2">
                        <button className="px-4 py-2 bg-[#7c3aed] hover:bg-[#6d28d9] text-white text-sm font-semibold rounded transition-all">
                          EXECUTE
                        </button>
                        <button className="p-2 bg-gray-800 hover:bg-gray-700 rounded transition-all">
                          {expandedRec === rec.id ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
                        </button>
                      </div>
                    </div>
                  </div>

                  {expandedRec === rec.id && (
                    <div className="px-5 pb-5 border-t border-gray-800 pt-4 ml-12">
                      <h4 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-3">Chief's Reasoning:</h4>
                      <ul className="space-y-2">
                        {rec.reasoning.map((reason, ridx) => (
                          <li key={ridx} className="flex items-start gap-3 text-sm text-gray-300">
                            <ChevronRight className="w-4 h-4 text-[#7c3aed] mt-0.5 flex-shrink-0" />
                            {reason}
                          </li>
                        ))}
                      </ul>

                      <div className="flex gap-3 mt-4">
                        <button className="flex items-center gap-2 px-4 py-2 bg-green-500/10 border border-green-500/30 rounded text-sm text-green-400 hover:bg-green-500/20 transition-all">
                          <CheckCircle className="w-4 h-4" />
                          APPROVE & ASSIGN
                        </button>
                        <button className="flex items-center gap-2 px-4 py-2 bg-red-500/10 border border-red-500/30 rounded text-sm text-red-400 hover:bg-red-500/20 transition-all">
                          <AlertOctagon className="w-4 h-4" />
                          DECLINE
                        </button>
                        <button className="flex items-center gap-2 px-4 py-2 bg-gray-800 border border-gray-700 rounded text-sm text-gray-400 hover:bg-gray-700 transition-all">
                          <MessageSquare className="w-4 h-4" />
                          REQUEST INFO
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Briefing Stats */}
            <div className="col-span-4 space-y-4">
              <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-5">
                <h3 className="text-sm font-bold text-gray-500 uppercase tracking-wider mb-4">Situation Summary</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-[#0a0812] rounded-lg p-4 border border-gray-800">
                    <div className="text-3xl font-bold text-[#7c3aed]">{dailyBriefing.totalActiveOperations}</div>
                    <div className="text-xs text-gray-500 uppercase">Active Operations</div>
                  </div>
                  <div className="bg-[#0a0812] rounded-lg p-4 border border-gray-800">
                    <div className="text-3xl font-bold text-green-400">{dailyBriefing.newIntel}</div>
                    <div className="text-xs text-gray-500 uppercase">New Intel Items</div>
                  </div>
                  <div className="bg-[#0a0812] rounded-lg p-4 border border-gray-800">
                    <div className="text-3xl font-bold text-orange-400">{dailyBriefing.requiresDecision}</div>
                    <div className="text-xs text-gray-500 uppercase">Pending Decisions</div>
                  </div>
                  <div className="bg-[#0a0812] rounded-lg p-4 border border-gray-800">
                    <div className="text-3xl font-bold text-blue-400">15/18</div>
                    <div className="text-xs text-gray-500 uppercase">Swarm Online</div>
                  </div>
                </div>
              </div>

              {/* Critical Alerts */}
              <div className="bg-gradient-to-br from-red-900/20 to-[#0f0c1d] border border-red-500/30 rounded-lg p-5">
                <h3 className="text-sm font-bold text-red-400 uppercase tracking-wider mb-4 flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4" />
                  Critical Alerts
                </h3>
                <div className="space-y-3">
                  <div className="flex items-start gap-3 p-3 bg-red-500/10 rounded-lg border border-red-500/20">
                    <ShieldAlert className="w-5 h-5 text-red-400 flex-shrink-0" />
                    <div>
                      <div className="text-sm font-semibold text-red-400">Fake RMI Airdrop Active</div>
                      <div className="text-xs text-gray-400">10m ago • 23 wallets compromised</div>
                    </div>
                  </div>
                  <div className="flex items-start gap-3 p-3 bg-orange-500/10 rounded-lg border border-orange-500/20">
                    <AlertTriangle className="w-5 h-5 text-orange-400 flex-shrink-0" />
                    <div>
                      <div className="text-sm font-semibold text-orange-400">SEC Scrutiny Increase</div>
                      <div className="text-xs text-gray-400">2d ago • Token compliance review needed</div>
                    </div>
                  </div>
                </div>
              </div>

              {/* System Health */}
              <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-5">
                <h3 className="text-sm font-bold text-gray-500 uppercase tracking-wider mb-4">System Health</h3>
                <div className="space-y-3">
                  <div>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-gray-400">API Response Time</span>
                      <span className="text-orange-400">450ms ⚠️</span>
                    </div>
                    <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                      <div className="h-full w-[75%] bg-orange-500 rounded-full" />
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-gray-400">Swarm Efficiency</span>
                      <span className="text-green-400">94% ✅</span>
                    </div>
                    <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                      <div className="h-full w-[94%] bg-green-500 rounded-full" />
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-gray-400">Bot Uptime</span>
                      <span className="text-green-400">99.2% ✅</span>
                    </div>
                    <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                      <div className="h-full w-[99%] bg-green-500 rounded-full" />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ============================================ */}
        {/* INTELLIGENCE TAB */}
        {/* ============================================ */}
        {activeTab === 'intelligence' && (
          <div className="grid grid-cols-12 gap-6">
            {/* Advisor Selection */}
            <div className="col-span-2 space-y-2">
              {advisors.filter(a => a.id !== 'chief').map((advisor) => (
                <button
                  key={advisor.id}
                  onClick={() => setActiveAdvisor(advisor.id)}
                  className={`w-full p-3 rounded-lg border text-left transition-all ${
                    activeAdvisor === advisor.id
                      ? 'bg-[#7c3aed]/20 border-[#7c3aed]'
                      : 'bg-[#1a1525]/50 border-gray-800 hover:border-[#7c3aed]/30'
                  }`}
                >
                  <div className="flex items-center gap-2 mb-1">
                    {advisor.icon}
                    <span className="text-xs font-bold text-gray-500">{advisor.codename}</span>
                  </div>
                  <div className="text-sm font-semibold">{advisor.name}</div>
                  <div className="text-xs text-gray-500 mt-1">{advisor.insights.filter(i => i.priority === 'critical' || i.priority === 'high').length} alerts</div>
                </button>
              ))}
            </div>

            {/* Intelligence Feed */}
            <div className="col-span-7 space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-bold flex items-center gap-2">
                    {currentAdvisor.icon}
                    {currentAdvisor.name}
                  </h2>
                  <p className="text-xs text-gray-500 mt-1">{currentAdvisor.description}</p>
                </div>
                <div className="flex items-center gap-2 text-xs text-gray-500">
                  <span className="px-2 py-1 bg-gray-800 rounded">CLEARANCE L-{currentAdvisor.clearanceLevel}</span>
                  <span>Updated {currentAdvisor.lastUpdated}</span>
                </div>
              </div>

              {currentAdvisor.insights.map((insight) => (
                <div
                  key={insight.id}
                  className={`bg-gradient-to-r from-[#1a1525] to-[#0f0c1d] border rounded-lg overflow-hidden transition-all ${
                    insight.classified ? 'border-red-500/30' : 'border-gray-800 hover:border-[#7c3aed]/30'
                  }`}
                >
                  <div
                    className="p-5 cursor-pointer"
                    onClick={() => setExpandedInsight(expandedInsight === insight.id ? null : insight.id)}
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-3">
                        {getInsightIcon(insight.type)}
                        <div>
                          <h3 className="font-semibold text-lg">{insight.title}</h3>
                          <span className="text-xs text-gray-500">
                            {insight.source} • {insight.timestamp}
                          </span>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {insight.classified && (
                          <span className="px-2 py-1 bg-red-500/20 text-red-400 text-xs font-bold rounded uppercase">
                            Classified
                          </span>
                        )}
                        <span className={`px-3 py-1 rounded text-xs font-bold border ${getPriorityColor(insight.priority)}`}>
                          {insight.priority.toUpperCase()}
                        </span>
                      </div>
                    </div>

                    <p className="text-gray-300 text-sm leading-relaxed">{insight.description}</p>

                    {insight.impact && (
                      <div className="mt-3 flex items-center gap-2 text-sm">
                        <Target className="w-4 h-4 text-[#7c3aed]" />
                        <span className="text-[#7c3aed] font-medium">Impact:</span>
                        <span className="text-gray-400">{insight.impact}</span>
                      </div>
                    )}
                  </div>

                  {expandedInsight === insight.id && insight.evidence && (
                    <div className="px-5 pb-5 border-t border-gray-800 pt-4">
                      <h4 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-3">Evidence:</h4>
                      <ul className="space-y-2">
                        {insight.evidence.map((item, idx) => (
                          <li key={idx} className="flex items-start gap-2 text-sm text-gray-300">
                            <CheckCircle className="w-4 h-4 text-[#7c3aed] mt-0.5 flex-shrink-0" />
                            {item}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Action Queue */}
            <div className="col-span-3 space-y-4">
              <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-5">
                <h3 className="text-sm font-bold text-gray-500 uppercase tracking-wider mb-4">Action Queue</h3>
                <div className="space-y-3">
                  {currentAdvisor.actions.map((action) => (
                    <div
                      key={action.id}
                      className="p-3 bg-[#0a0812] rounded-lg border border-gray-800"
                    >
                      <div className="text-sm mb-2">{action.label}</div>
                      <div className="flex items-center justify-between">
                        <span className={`text-xs px-2 py-1 rounded ${
                          action.status === 'completed' ? 'bg-green-500/20 text-green-400' :
                          action.status === 'in_progress' ? 'bg-blue-500/20 text-blue-400' :
                          action.status === 'requires_approval' ? 'bg-yellow-500/20 text-yellow-400' :
                          'bg-gray-700 text-gray-400'
                        }`}>
                          {action.status.replace('_', ' ').toUpperCase()}
                        </span>
                        {action.requiresAuth && (
                          <Lock className="w-4 h-4 text-yellow-400" />
                        )}
                      </div>
                      {action.status === 'requires_approval' && humanOverride && (
                        <button className="w-full mt-2 py-1.5 bg-[#7c3aed] text-white text-xs font-semibold rounded hover:bg-[#6d28d9] transition-all">
                          AUTHORIZE
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ============================================ */}
        {/* OPERATIONS TAB */}
        {/* ============================================ */}
        {activeTab === 'operations' && (
          <div className="space-y-6">
            {/* Swarm Status */}
            <div className="grid grid-cols-4 gap-4">
              <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-5">
                <div className="flex items-center gap-2 mb-2">
                  <Sparkles className="w-5 h-5 text-[#7c3aed]" />
                  <span className="text-xs text-gray-500 uppercase">AI Swarm</span>
                </div>
                <div className="text-3xl font-bold">{swarmStatus.activeAgents}/{swarmStatus.totalAgents}</div>
                <div className="text-xs text-green-400">Agents Online</div>
              </div>
              <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-5">
                <div className="flex items-center gap-2 mb-2">
                  <Activity className="w-5 h-5 text-blue-400" />
                  <span className="text-xs text-gray-500 uppercase">Queue</span>
                </div>
                <div className="text-3xl font-bold">{swarmStatus.tasksInQueue}</div>
                <div className="text-xs text-gray-400">Tasks Pending</div>
              </div>
              <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-5">
                <div className="flex items-center gap-2 mb-2">
                  <Clock className="w-5 h-5 text-yellow-400" />
                  <span className="text-xs text-gray-500 uppercase">Avg Process</span>
                </div>
                <div className="text-3xl font-bold">{swarmStatus.avgProcessingTime}</div>
                <div className="text-xs text-green-400">Per Task</div>
              </div>
              <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-5">
                <div className="flex items-center gap-2 mb-2">
                  <HeartPulse className="w-5 h-5 text-green-400" />
                  <span className="text-xs text-gray-500 uppercase">Health</span>
                </div>
                <div className="text-3xl font-bold">{swarmStatus.healthScore}%</div>
                <div className="text-xs text-green-400">Optimal</div>
              </div>
            </div>

            {/* Bot Management */}
            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-bold flex items-center gap-2">
                  <Bot className="w-5 h-5 text-[#7c3aed]" />
                  Bot Fleet Management
                </h3>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-gray-500">Human Control:</span>
                  <span className={`text-xs font-bold ${humanOverride ? 'text-green-400' : 'text-gray-400'}`}>
                    {humanOverride ? 'ENABLED' : 'AUTONOMOUS'}
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                {botStatuses.map((bot) => (
                  <div key={bot.id} className="bg-[#0a0812] rounded-lg p-4 border border-gray-800">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <Bot className={`w-5 h-5 ${
                          bot.status === 'active' ? 'text-green-400' :
                          bot.status === 'standby' ? 'text-yellow-400' :
                          bot.status === 'maintenance' ? 'text-orange-400' :
                          'text-red-400'
                        }`} />
                        <span className="font-semibold text-sm">{bot.name}</span>
                      </div>
                      <div className={`w-2 h-2 rounded-full ${
                        bot.status === 'active' ? 'bg-green-500' :
                        bot.status === 'standby' ? 'bg-yellow-500' :
                        bot.status === 'maintenance' ? 'bg-orange-500' :
                        'bg-red-500'
                      }`} />
                    </div>
                    <div className="text-xs text-gray-500 mb-3">{bot.role}</div>
                    <div className="grid grid-cols-2 gap-2 text-xs mb-3">
                      <div className="text-gray-400">Msgs: <span className="text-white">{bot.messagesHandled.toLocaleString()}</span></div>
                      <div className="text-gray-400">Swarms: <span className="text-white">{bot.swarmsAllocated}</span></div>
                    </div>
                    <div className="text-xs text-gray-500 mb-3">Last: {bot.lastActivity}</div>
                    {humanOverride && (
                      <div className="flex gap-2">
                        {bot.status === 'active' ? (
                          <button className="flex-1 py-1.5 bg-red-500/10 border border-red-500/30 rounded text-xs text-red-400 hover:bg-red-500/20 transition-all">
                            <Pause className="w-3 h-3 inline mr-1" />
                            PAUSE
                          </button>
                        ) : (
                          <button className="flex-1 py-1.5 bg-green-500/10 border border-green-500/30 rounded text-xs text-green-400 hover:bg-green-500/20 transition-all">
                            <Play className="w-3 h-3 inline mr-1" />
                            ACTIVATE
                          </button>
                        )}
                        <button className="flex-1 py-1.5 bg-gray-800 border border-gray-700 rounded text-xs text-gray-400 hover:bg-gray-700 transition-all">
                          <Settings className="w-3 h-3 inline mr-1" />
                          CONFIG
                        </button>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ============================================ */}
        {/* ASSETS & WALLETS TAB */}
        {/* ============================================ */}
        {activeTab === 'assets' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-bold flex items-center gap-2">
                <Wallet className="w-6 h-6 text-[#7c3aed]" />
                Treasury Management
              </h2>
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-500">Human-in-the-Loop:</span>
                <span className={`px-2 py-1 rounded text-xs font-bold ${humanOverride ? 'bg-green-500/20 text-green-400' : 'bg-gray-800 text-gray-400'}`}>
                  {humanOverride ? 'APPROVAL REQUIRED' : 'AUTONOMOUS'}
                </span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              {walletData.map((wallet) => (
                <div key={wallet.address} className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-5">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-[#7c3aed]/10 rounded-lg flex items-center justify-center">
                        <Key className="w-5 h-5 text-[#7c3aed]" />
                      </div>
                      <div>
                        <div className="font-semibold">{wallet.purpose}</div>
                        <div className="text-xs text-gray-500 font-mono">{wallet.address}</div>
                      </div>
                    </div>
                    <div className={`px-2 py-1 rounded text-xs ${wallet.requiresApproval ? 'bg-yellow-500/20 text-yellow-400' : 'bg-green-500/20 text-green-400'}`}>
                      {wallet.requiresApproval ? 'MULTISIG' : 'OPERATIONAL'}
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-4 mb-4">
                    <div>
                      <div className="text-2xl font-bold text-white">{wallet.balance}</div>
                      <div className="text-xs text-gray-500">Balance</div>
                    </div>
                    <div>
                      <div className="text-sm font-semibold text-gray-300">{wallet.network}</div>
                      <div className="text-xs text-gray-500">Network</div>
                    </div>
                    <div>
                      <div className="text-sm font-semibold text-gray-300">{wallet.lastTx}</div>
                      <div className="text-xs text-gray-500">Last Activity</div>
                    </div>
                  </div>

                  {humanOverride && (
                    <div className="flex gap-2">
                      <button className="flex-1 py-2 bg-[#7c3aed]/10 border border-[#7c3aed]/30 rounded text-sm text-[#7c3aed] hover:bg-[#7c3aed]/20 transition-all">
                        INITIATE TRANSFER
                      </button>
                      <button className="flex-1 py-2 bg-gray-800 border border-gray-700 rounded text-sm text-gray-400 hover:bg-gray-700 transition-all">
                        VIEW HISTORY
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Transaction History */}
            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-bold mb-4">Recent Transactions (Human-Approved)</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-left text-xs text-gray-500 uppercase tracking-wider border-b border-gray-800">
                      <th className="pb-3">Timestamp</th>
                      <th className="pb-3">Type</th>
                      <th className="pb-3">Amount</th>
                      <th className="pb-3">From → To</th>
                      <th className="pb-3">Purpose</th>
                      <th className="pb-3">Status</th>
                    </tr>
                  </thead>
                  <tbody className="text-gray-300">
                    <tr className="border-b border-gray-800/50">
                      <td className="py-3">2026-04-14 08:23:15 UTC</td>
                      <td className="py-3"><span className="text-green-400">IN</span></td>
                      <td className="py-3">+12.5 ETH</td>
                      <td className="py-3 font-mono text-xs">0x...a1b2 → Treasury</td>
                      <td className="py-3">Subscription Revenue</td>
                      <td className="py-3"><span className="text-green-400">✓ Confirmed</span></td>
                    </tr>
                    <tr className="border-b border-gray-800/50">
                      <td className="py-3">2026-04-13 14:45:22 UTC</td>
                      <td className="py-3"><span className="text-red-400">OUT</span></td>
                      <td className="py-3">-5.2 ETH</td>
                      <td className="py-3 font-mono text-xs">Operations → 0x...c3d4</td>
                      <td className="py-3">Server Infrastructure</td>
                      <td className="py-3"><span className="text-green-400">✓ Approved</span></td>
                    </tr>
                    <tr>
                      <td className="py-3">2026-04-13 09:12:08 UTC</td>
                      <td className="py-3"><span className="text-red-400">OUT</span></td>
                      <td className="py-3">-2.0 ETH</td>
                      <td className="py-3 font-mono text-xs">Treasury → 0x...e5f6</td>
                      <td className="py-3">Staking Rewards Distribution</td>
                      <td className="py-3"><span className="text-green-400">✓ Approved</span></td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* ============================================ */}
        {/* DOMAIN CONTROL TAB */}
        {/* ============================================ */}
        {activeTab === 'domains' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-bold flex items-center gap-2">
                <Globe className="w-6 h-6 text-[#7c3aed]" />
                Domain Portfolio Control
              </h2>
              <button className="px-4 py-2 bg-[#7c3aed] hover:bg-[#6d28d9] text-white text-sm font-semibold rounded transition-all">
                + REGISTER NEW DOMAIN
              </button>
            </div>

            <div className="grid grid-cols-2 gap-4">
              {domainStatuses.map((domain) => (
                <div key={domain.domain} className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-5">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <Globe className="w-5 h-5 text-[#7c3aed]" />
                      <span className="text-lg font-semibold">{domain.domain}</span>
                    </div>
                    <span className={`px-3 py-1 rounded text-xs font-bold ${
                      domain.status === 'active' ? 'bg-green-500/20 text-green-400' :
                      domain.status === 'expiring' ? 'bg-red-500/20 text-red-400' :
                      domain.status === 'pending' ? 'bg-yellow-500/20 text-yellow-400' :
                      'bg-gray-700 text-gray-400'
                    }`}>
                      {domain.status.toUpperCase()}
                    </span>
                  </div>

                  <div className="grid grid-cols-4 gap-4 mb-4 text-center">
                    <div className="bg-[#0a0812] rounded p-3">
                      <div className="text-lg font-bold text-white">{domain.traffic24h.toLocaleString()}</div>
                      <div className="text-xs text-gray-500">24h Visits</div>
                    </div>
                    <div className="bg-[#0a0812] rounded p-3">
                      <div className="text-lg font-bold text-white">{domain.expiresAt}</div>
                      <div className="text-xs text-gray-500">Expires</div>
                    </div>
                    <div className={`rounded p-3 ${domain.sslStatus === 'valid' ? 'bg-green-500/10' : 'bg-red-500/10'}`}>
                      <div className={`text-lg font-bold ${domain.sslStatus === 'valid' ? 'text-green-400' : 'text-red-400'}`}>
                        {domain.sslStatus === 'valid' ? '✓' : '✗'}
                      </div>
                      <div className="text-xs text-gray-500">SSL</div>
                    </div>
                    <div className={`rounded p-3 ${domain.dnsHealth === 'healthy' ? 'bg-green-500/10' : domain.dnsHealth === 'issues' ? 'bg-yellow-500/10' : 'bg-red-500/10'}`}>
                      <div className={`text-lg font-bold ${domain.dnsHealth === 'healthy' ? 'text-green-400' : domain.dnsHealth === 'issues' ? 'text-yellow-400' : 'text-red-400'}`}>
                        {domain.dnsHealth === 'healthy' ? '✓' : domain.dnsHealth === 'issues' ? '!' : '✗'}
                      </div>
                      <div className="text-xs text-gray-500">DNS</div>
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <button className="flex-1 py-2 bg-[#7c3aed]/10 border border-[#7c3aed]/30 rounded text-sm text-[#7c3aed] hover:bg-[#7c3aed]/20 transition-all">
                      DNS SETTINGS
                    </button>
                    <button className="flex-1 py-2 bg-gray-800 border border-gray-700 rounded text-sm text-gray-400 hover:bg-gray-700 transition-all">
                      ANALYTICS
                    </button>
                    <button className="flex-1 py-2 bg-gray-800 border border-gray-700 rounded text-sm text-gray-400 hover:bg-gray-700 transition-all">
                      RENEW
                    </button>
                  </div>
                </div>
              ))}
            </div>

            {/* Traffic Analytics */}
            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                <BarChart3 className="w-5 h-5 text-[#7c3aed]" />
                Network Traffic Analysis
              </h3>
              <div className="h-64 bg-[#0a0812] rounded-lg flex items-center justify-center border border-gray-800">
                <div className="text-center text-gray-500">
                  <Activity className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p>Traffic visualization loaded from Plausible/Analytics API</p>
                  <p className="text-sm mt-1">Total: 145.2K visits (24h) • Peak: 8,420 (14:00 UTC)</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ============================================ */}
        {/* DATA TRANSPARENCY TAB */}
        {/* ============================================ */}
        {activeTab === 'data' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-bold flex items-center gap-2">
                <Database className="w-6 h-6 text-[#7c3aed]" />
                Data Usage Transparency
              </h2>
              <div className="flex items-center gap-2 px-4 py-2 bg-green-500/10 border border-green-500/30 rounded-lg">
                <CheckCircle className="w-4 h-4 text-green-400" />
                <span className="text-sm text-green-400">Human Verification Active</span>
              </div>
            </div>

            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-bold mb-4">Data Processing Pipeline</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-left text-xs text-gray-500 uppercase tracking-wider border-b border-gray-800">
                      <th className="pb-3">Category</th>
                      <th className="pb-3">Source</th>
                      <th className="pb-3">Records Processed</th>
                      <th className="pb-3">Storage</th>
                      <th className="pb-3">Last Updated</th>
                      <th className="pb-3">Human Verified</th>
                    </tr>
                  </thead>
                  <tbody className="text-gray-300">
                    {dataUsageMetrics.map((metric, idx) => (
                      <tr key={idx} className="border-b border-gray-800/50">
                        <td className="py-3 font-semibold">{metric.category}</td>
                        <td className="py-3 text-gray-400">{metric.source}</td>
                        <td className="py-3">{metric.recordsProcessed.toLocaleString()}</td>
                        <td className="py-3">{metric.storageUsed}</td>
                        <td className="py-3 text-gray-400">{metric.lastUpdated}</td>
                        <td className="py-3">
                          {metric.humanVerified ? (
                            <span className="flex items-center gap-1 text-green-400">
                              <CheckCircle className="w-4 h-4" />
                              Verified
                            </span>
                          ) : (
                            <span className="flex items-center gap-1 text-yellow-400">
                              <Clock className="w-4 h-4" />
                              Pending
                            </span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-6">
              <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
                <h3 className="text-lg font-bold mb-4">Privacy & Retention</h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-3 bg-[#0a0812] rounded-lg">
                    <div className="flex items-center gap-2">
                      <Lock className="w-4 h-4 text-[#7c3aed]" />
                      <span className="text-sm">Wallet addresses anonymized</span>
                    </div>
                    <CheckCircle className="w-4 h-4 text-green-400" />
                  </div>
                  <div className="flex items-center justify-between p-3 bg-[#0a0812] rounded-lg">
                    <div className="flex items-center gap-2">
                      <Users className="w-4 h-4 text-[#7c3aed]" />
                      <span className="text-sm">PII purged after 90 days</span>
                    </div>
                    <CheckCircle className="w-4 h-4 text-green-400" />
                  </div>
                  <div className="flex items-center justify-between p-3 bg-[#0a0812] rounded-lg">
                    <div className="flex items-center gap-2">
                      <Database className="w-4 h-4 text-[#7c3aed]" />
                      <span className="text-sm">Contract data retained indefinitely</span>
                    </div>
                    <span className="text-xs text-gray-500">Public blockchain data</span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-[#0a0812] rounded-lg">
                    <div className="flex items-center gap-2">
                      <MessageSquare className="w-4 h-4 text-[#7c3aed]" />
                      <span className="text-sm">Snitch reports encrypted</span>
                    </div>
                    <CheckCircle className="w-4 h-4 text-green-400" />
                  </div>
                </div>
              </div>

              <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
                <h3 className="text-lg font-bold mb-4">AI Decision Audit Log</h3>
                <div className="space-y-3 max-h-64 overflow-y-auto">
                  <div className="p-3 bg-[#0a0812] rounded-lg border-l-2 border-green-500">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs text-green-400">AUTO-APPROVED</span>
                      <span className="text-xs text-gray-500">2m ago</span>
                    </div>
                    <div className="text-sm">Low-risk contract scan (score: 23/100)</div>
                    <div className="text-xs text-gray-500 mt-1">No human intervention required</div>
                  </div>
                  <div className="p-3 bg-[#0a0812] rounded-lg border-l-2 border-yellow-500">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs text-yellow-400">HUMAN REVIEW REQUESTED</span>
                      <span className="text-xs text-gray-500">15m ago</span>
                    </div>
                    <div className="text-sm">High-value transfer (50+ ETH)</div>
                    <div className="text-xs text-gray-500 mt-1">Awaiting authorization</div>
                  </div>
                  <div className="p-3 bg-[#0a0812] rounded-lg border-l-2 border-red-500">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs text-red-400">HUMAN OVERRULED</span>
                      <span className="text-xs text-gray-500">1h ago</span>
                    </div>
                    <div className="text-sm">Auto-blocked contract marked safe by admin</div>
                    <div className="text-xs text-gray-500 mt-1">Transaction hash: 0x...a1b2</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Terminal Overlay */}
      {terminalOpen && (
        <div className="fixed bottom-0 left-0 right-0 h-64 bg-[#0a0812] border-t border-[#7c3aed]/30 z-50">
          <div className="flex items-center justify-between px-4 py-2 bg-[#1a1525] border-b border-gray-800">
            <span className="text-xs text-gray-500 uppercase tracking-wider">Secure Terminal // Root Access</span>
            <button onClick={() => setTerminalOpen(false)} className="text-gray-500 hover:text-white">
              <Power className="w-4 h-4" />
            </button>
          </div>
          <div className="p-4 font-mono text-sm text-green-400 overflow-y-auto h-[calc(100%-40px)]">
            <div className="text-gray-500"># RMI Command Interface v2.0</div>
            <div className="text-gray-500"># Type 'help' for available commands</div>
            <div className="mt-2">
              <span className="text-[#7c3aed]">root@rmi-command:~$</span> <span className="animate-pulse">_</span>
            </div>
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="max-w-[1600px] mx-auto mt-12 pt-6 border-t border-gray-800 text-center">
        <div className="flex items-center justify-center gap-6 text-xs text-gray-600">
          <span>RMI COMMAND v2.0</span>
          <span>•</span>
          <span>SECURITY CLASSIFICATION: TOP SECRET//SCI</span>
          <span>•</span>
          <span>Authorized Personnel Only</span>
          <span>•</span>
          <span>All Activity Logged</span>
        </div>
      </div>
    </div>
  );
};

// Additional icon component needed
const HeartPulse = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
  </svg>
);

export default AdvisorPanel;
