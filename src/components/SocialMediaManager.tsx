import React, { useState, useEffect } from 'react';
import {
  Send,
  Target,
  Hash,
  MessageSquare,
  Heart,
  Repeat2,
  Eye,
  Zap,
  Calendar,
  Clock,
  Plus,
  Play,
  Pause,
  Trash2,
  CheckCircle,
  AlertTriangle,
  TrendingUp,
  Users,
  Link,
  Image as ImageIcon,
  FileText,
  Sparkles,
  Settings,
  BarChart3,
  RefreshCw,
  Copy,
  Edit3,
  Send as SendIcon,
  X,
  ChevronLeft,
  ChevronRight,
  Bell,
  UserPlus,
  UserMinus,
  Power,
  PowerOff,
  Filter,
  RotateCcw,
  CheckSquare,
  Square,
  MoreHorizontal,
  Download,
  Upload,
  Globe,
  Lock,
  Unlock,
  Shield,
  Bot,
  Megaphone,
  Activity,
  Crown
} from 'lucide-react';

type Platform = 'twitter' | 'telegram' | 'farcaster' | 'threads' | 'instagram' | 'tiktok' | 'bluesky' | 'all' | 'both';

interface Post {
  id: string;
  content: string;
  platform: Platform;
  platforms?: Platform[]; // For multi-platform posts
  status: 'draft' | 'scheduled' | 'published' | 'failed' | 'pending_approval' | 'editing_window' | 'website_preview';
  scheduledFor?: string;
  publishedAt?: string;
  websitePublishedAt?: string; // When published to website first
  socialPublishedAt?: string; // When published to social platforms
  editingWindowEnds?: string; // 5-minute editing window
  engagement?: {
    views: number;
    likes: number;
    retweets: number;
    replies: number;
  };
  platformEngagement?: Record<string, { views: number; likes: number; shares: number; comments: number }>;
  aiGenerated: boolean;
  approved: boolean;
  approvedBy?: string;
  approvedAt?: string;
  hashtags: string[];
  mediaUrls?: string[];
  autoPosted: boolean;
  category?: 'alert' | 'update' | 'educational' | 'promotional' | 'community';
  farcasterCastHash?: string;
  blueskyUri?: string;
}

interface ShillTarget {
  id: string;
  account: string;
  handle: string;
  followers: number;
  relevance: 'high' | 'medium' | 'low';
  lastPost: string;
  suggestedComment: string;
  used: boolean;
  category: 'crypto' | 'defi' | 'security' | 'trading';
  lastShilledAt?: string;
  totalShills: number;
}

interface ContentTemplate {
  id: string;
  name: string;
  template: string;
  platform: Platform;
  platforms?: Platform[];
  usage: number;
  avgEngagement: string;
  category: string;
  variables: string[];
  maxLength?: Record<string, number>; // Character limits per platform
}

interface SocialAccount {
  id: string;
  platform: Platform;
  name: string;
  handle: string;
  fid?: number; // Farcaster ID
  status: 'active' | 'inactive' | 'suspended' | 'pending';
  followers: number;
  following?: number;
  apiConnected: boolean;
  apiEndpoint?: string;
  lastPostAt?: string;
  dailyPostLimit: number;
  postsToday: number;
  autoPostEnabled: boolean;
  requiresApproval: boolean;
  supportsMedia: boolean;
  supportsThreads: boolean;
  characterLimit: number;
  addedAt: string;
  addedBy: string;
  webhookUrl?: string;
  botToken?: string; // For Telegram
}

interface AutoPostRule {
  id: string;
  name: string;
  enabled: boolean;
  platforms: Platform[];
  primaryPlatform: Platform;
  frequency: 'hourly' | '3x_daily' | 'daily' | 'weekly';
  contentType: 'mixed' | 'alerts' | 'educational' | 'promotional';
  maxPostsPerDay: number;
  requireApproval: boolean;
  useAI: boolean;
  timeWindow: { start: string; end: string };
  websiteFirst: boolean; // Publish to website before social
  editingWindow: number; // Minutes to allow editing (default 5)
}

interface CalendarDay {
  date: number;
  isCurrentMonth: boolean;
  posts: Post[];
}

const SocialMediaManager: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'create' | 'calendar' | 'accounts' | 'targets' | 'autopost' | 'analytics'>('dashboard');

  // Platform configurations
  const platformConfig: Record<string, { name: string; color: string; icon: string; charLimit: number; supportsMedia: boolean; supportsThreads: boolean }> = {
    twitter: { name: 'X (Globe)', color: '#1DA1F2', icon: 'twitter', charLimit: 280, supportsMedia: true, supportsThreads: true },
    telegram: { name: 'Telegram', color: '#0088cc', icon: 'send', charLimit: 4096, supportsMedia: true, supportsThreads: false },
    farcaster: { name: 'Farcaster', color: '#8b5cf6', icon: 'cast', charLimit: 1024, supportsMedia: true, supportsThreads: true },
    threads: { name: 'Threads', color: '#E1306C', icon: 'at-sign', charLimit: 500, supportsMedia: true, supportsThreads: true },
    instagram: { name: 'Instagram', color: '#E1306C', icon: 'camera', charLimit: 2200, supportsMedia: true, supportsThreads: false },
    tiktok: { name: 'TikTok', color: '#ff0050', icon: 'music', charLimit: 2200, supportsMedia: true, supportsThreads: false },
    bluesky: { name: 'Bluesky', color: '#0560ff', icon: 'cloud', charLimit: 300, supportsMedia: true, supportsThreads: true }
  };

  // Accounts State
  const [accounts, setAccounts] = useState<SocialAccount[]>([
    {
      id: 'acc1',
      platform: 'twitter',
      name: 'CryptoRugMunch',
      handle: '@CryptoRugMunch',
      status: 'active',
      followers: 52300,
      apiConnected: true,
      lastPostAt: '2026-04-14 10:30',
      dailyPostLimit: 50,
      postsToday: 12,
      autoPostEnabled: true,
      requiresApproval: true,
      supportsMedia: true,
      supportsThreads: true,
      characterLimit: 280,
      addedAt: '2025-01-15',
      addedBy: 'ADMIN'
    },
    {
      id: 'acc2',
      platform: 'telegram',
      name: 'Rug Munch Intel',
      handle: '@rugmunchintel',
      status: 'active',
      followers: 12800,
      apiConnected: true,
      lastPostAt: '2026-04-14 11:00',
      dailyPostLimit: 100,
      postsToday: 8,
      autoPostEnabled: true,
      requiresApproval: false,
      supportsMedia: true,
      supportsThreads: false,
      characterLimit: 4096,
      addedAt: '2025-01-20',
      addedBy: 'ADMIN'
    },
    {
      id: 'acc3',
      platform: 'farcaster',
      name: 'Rug Munch',
      handle: '@rugmunch',
      fid: 12345,
      status: 'active',
      followers: 3400,
      apiConnected: true,
      apiEndpoint: 'https://api.warpcast.com',
      lastPostAt: '2026-04-14 09:15',
      dailyPostLimit: 30,
      postsToday: 5,
      autoPostEnabled: true,
      requiresApproval: true,
      supportsMedia: true,
      supportsThreads: true,
      characterLimit: 1024,
      addedAt: '2025-02-01',
      addedBy: 'ADMIN'
    },
    {
      id: 'acc4',
      platform: 'bluesky',
      name: 'Rug Munch Intel',
      handle: '@rugmunch.bsky.social',
      status: 'active',
      followers: 2800,
      apiConnected: true,
      lastPostAt: '2026-04-14 08:30',
      dailyPostLimit: 50,
      postsToday: 3,
      autoPostEnabled: false,
      requiresApproval: true,
      supportsMedia: true,
      supportsThreads: true,
      characterLimit: 300,
      addedAt: '2025-02-15',
      addedBy: 'ADMIN'
    },
    {
      id: 'acc5',
      platform: 'threads',
      name: 'Rug Munch Intel',
      handle: '@rugmunchintel',
      status: 'pending',
      followers: 0,
      apiConnected: false,
      lastPostAt: undefined,
      dailyPostLimit: 25,
      postsToday: 0,
      autoPostEnabled: false,
      requiresApproval: true,
      supportsMedia: true,
      supportsThreads: true,
      characterLimit: 500,
      addedAt: '2026-04-14',
      addedBy: 'ADMIN'
    }
  ]);

  const [showAddAccount, setShowAddAccount] = useState(false);
  const [newAccount, setNewAccount] = useState({
    platform: 'twitter' as Platform,
    name: '',
    handle: '',
    fid: undefined as number | undefined,
    apiKey: '',
    apiSecret: '',
    dailyPostLimit: 50,
    requiresApproval: true,
    supportsMedia: true,
    supportsThreads: false,
    characterLimit: 280,
    botToken: ''
  });

  // Posts State
  const [posts, setPosts] = useState<Post[]>([
    {
      id: 'p1',
      content: '🚨 MAJOR RUG ALERT: Fake PepeX token just drained $2.3M from 450 wallets. Contract had hidden mint function.\n\nAlways scan before aping:\n✅ Check contract ownership\n✅ Verify mint functions\n✅ Review liquidity locks\n\nStay safe. Don\'t get rugged.',
      platform: 'both',
      status: 'published',
      publishedAt: '2026-04-14 10:30',
      engagement: { views: 45200, likes: 1234, retweets: 892, replies: 156 },
      aiGenerated: true,
      approved: true,
      approvedBy: 'ADMIN',
      approvedAt: '2026-04-14 10:25',
      hashtags: ['#RugPull', '#CryptoSecurity', '#Web3'],
      autoPosted: false,
      category: 'alert'
    },
    {
      id: 'p2',
      content: 'AI SWARM UPDATE: Our contract analyzers just hit 100,000 scans! 🎉\n\n99.4% accuracy rate\n2.3s avg response time\n$4.2M in potential losses prevented\n\nThe bots are getting smarter. Are you?',
      platform: 'twitter',
      status: 'scheduled',
      scheduledFor: '2026-04-15 09:00',
      aiGenerated: true,
      approved: true,
      hashtags: ['#AISecurity', '#RugMunchIntel', '#CryptoBots'],
      autoPosted: false,
      category: 'update'
    },
    {
      id: 'p3',
      content: '🔍 NEW: Sleep minting attacks on Base chain - 6 contracts flagged in 48h. Our AI detected the pattern early.',
      platform: 'telegram',
      status: 'pending_approval',
      aiGenerated: true,
      approved: false,
      hashtags: ['#BaseChain', '#SleepMinting'],
      autoPosted: false,
      category: 'alert'
    },
    {
      id: 'p4',
      content: '📚 Weekly Security Tips: How to verify contract ownership in 3 steps...',
      platform: 'both',
      status: 'scheduled',
      scheduledFor: '2026-04-16 14:00',
      aiGenerated: true,
      approved: true,
      hashtags: ['#CryptoSecurity', '#Education'],
      autoPosted: true,
      category: 'educational'
    }
  ]);

  const [selectedPosts, setSelectedPosts] = useState<Set<string>>(new Set());
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [postFilter, setPostFilter] = useState<'all' | 'scheduled' | 'published' | 'draft' | 'pending'>('all');

  // Shill Targets State
  const [shillTargets, setShillTargets] = useState<ShillTarget[]>([
    { id: 's1', account: 'Crypto Whisperer', handle: '@crypto_whisperer', followers: 450000, relevance: 'high', lastPost: '2h ago', suggestedComment: 'Great analysis! Our scanners detected this pattern 3 days ago - check @rugmunchbot for early warnings', used: false, category: 'security', totalShills: 0 },
    { id: 's2', account: 'DeFi Degen', handle: '@defi_degen', followers: 120000, relevance: 'high', lastPost: '45m ago', suggestedComment: 'Before you ape, scan it! Our AI caught 89% of rugs pre-launch last month 🛡️', used: false, category: 'defi', totalShills: 2 },
    { id: 's3', account: 'Trading Alpha', handle: '@trading_alpha', followers: 89000, relevance: 'medium', lastPost: '1h ago', suggestedComment: 'Protect your alpha gains - we just flagged 3 honeypots in this sector today', used: true, category: 'trading', totalShills: 5 },
    { id: 's4', account: 'Web3 Weekly', handle: '@web3weekly', followers: 230000, relevance: 'high', lastPost: '30m ago', suggestedComment: 'Great roundup! Include Rug Munch Intel for your readers - we prevent the rugs you report on', used: false, category: 'crypto', totalShills: 1 },
    { id: 's5', account: 'Security First', handle: '@securityfirst', followers: 67000, relevance: 'high', lastPost: '15m ago', suggestedComment: 'Our AI Swarm would love to compare notes - 18 agents working 24/7 on threat detection', used: false, category: 'security', totalShills: 0 },
  ]);

  // Templates State
  const [templates] = useState<ContentTemplate[]>([
    { id: 't1', name: 'Rug Pull Alert', template: '🚨 RUG PULL ALERT: {TOKEN_NAME}\n\nLoss: ${AMOUNT}\nVictims: {COUNT}\nChain: {CHAIN}\n\n{ANALYSIS}\n\nFull report: {LINK}', platform: 'both', usage: 45, avgEngagement: '12.4K', category: 'alert', variables: ['TOKEN_NAME', 'AMOUNT', 'COUNT', 'CHAIN', 'ANALYSIS', 'LINK'] },
    { id: 't2', name: 'Weekly Stats', template: '📊 This Week at Rug Munch Intel:\n\n• {SCAN_COUNT} contracts analyzed\n• {RUG_COUNT} rugs detected\n• ${SAVED} in losses prevented\n• {NEW_USERS} new protectors\n\nJoin the fight 👇', platform: 'both', usage: 12, avgEngagement: '8.2K', category: 'update', variables: ['SCAN_COUNT', 'RUG_COUNT', 'SAVED', 'NEW_USERS'] },
    { id: 't3', name: 'Educational Thread', template: '📚 How to spot {TOPIC} in 30 seconds:\n\n1. {TIP_1}\n2. {TIP_2}\n3. {TIP_3}\n\nBookmark this. It might save your bags. 🔖', platform: 'twitter', usage: 23, avgEngagement: '15.7K', category: 'educational', variables: ['TOPIC', 'TIP_1', 'TIP_2', 'TIP_3'] },
  ]);

  // Auto-Post Rules State
  const [autoPostRules, setAutoPostRules] = useState<AutoPostRule[]>([
    {
      id: 'apr1',
      name: 'High Priority Alerts',
      enabled: true,
      platforms: ['twitter', 'telegram', 'farcaster', 'bluesky'],
      primaryPlatform: 'twitter',
      frequency: 'hourly',
      contentType: 'alerts',
      maxPostsPerDay: 24,
      requireApproval: true,
      useAI: true,
      timeWindow: { start: '06:00', end: '22:00' },
      websiteFirst: true,
      editingWindow: 5
    },
    {
      id: 'apr2',
      name: 'Daily Educational',
      enabled: true,
      platforms: ['twitter', 'threads', 'bluesky'],
      primaryPlatform: 'twitter',
      frequency: 'daily',
      contentType: 'educational',
      maxPostsPerDay: 3,
      requireApproval: false,
      useAI: true,
      timeWindow: { start: '09:00', end: '18:00' },
      websiteFirst: true,
      editingWindow: 5
    },
    {
      id: 'apr3',
      name: 'Web3 Social Cast',
      enabled: true,
      platforms: ['farcaster'],
      primaryPlatform: 'farcaster',
      frequency: '3x_daily',
      contentType: 'mixed',
      maxPostsPerDay: 5,
      requireApproval: true,
      useAI: true,
      timeWindow: { start: '00:00', end: '23:59' },
      websiteFirst: false,
      editingWindow: 0
    }
  ]);

  const [showAddRule, setShowAddRule] = useState(false);
  const [newRule, setNewRule] = useState<Partial<AutoPostRule>>({
    name: '',
    enabled: true,
    platforms: ['twitter'],
    primaryPlatform: 'twitter',
    frequency: 'daily',
    contentType: 'mixed',
    maxPostsPerDay: 5,
    requireApproval: true,
    useAI: true,
    timeWindow: { start: '09:00', end: '18:00' }
  });

  // Calendar State
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);

  // Create Post State
  const [newPost, setNewPost] = useState({
    content: '',
    platform: 'both' as 'twitter' | 'telegram' | 'both',
    useAI: true,
    scheduled: false,
    scheduledFor: '',
    category: 'update' as Post['category'],
    requiresApproval: true
  });
  const [isGenerating, setIsGenerating] = useState(false);

  // Calendar Logic
  const getDaysInMonth = (date: Date): CalendarDay[] => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDay = firstDay.getDay();

    const days: CalendarDay[] = [];

    // Previous month days
    const prevMonth = new Date(year, month, 0);
    for (let i = startingDay - 1; i >= 0; i--) {
      days.push({
        date: prevMonth.getDate() - i,
        isCurrentMonth: false,
        posts: []
      });
    }

    // Current month days
    for (let i = 1; i <= daysInMonth; i++) {
      const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(i).padStart(2, '0')}`;
      const dayPosts = posts.filter(p =>
        p.scheduledFor?.startsWith(dateStr) ||
        p.publishedAt?.startsWith(dateStr)
      );
      days.push({
        date: i,
        isCurrentMonth: true,
        posts: dayPosts
      });
    }

    // Next month days to fill grid
    const remaining = (7 - (days.length % 7)) % 7;
    for (let i = 1; i <= remaining; i++) {
      days.push({
        date: i,
        isCurrentMonth: false,
        posts: []
      });
    }

    return days;
  };

  const calendarDays = getDaysInMonth(currentMonth);
  const weekDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  // Handlers
  const handleGenerateAI = () => {
    setIsGenerating(true);
    setTimeout(() => {
      setNewPost({
        ...newPost,
        content: '🔍 SPOTTED: New honeypot technique emerging on Base chain\n\nScammers are using "sleep minting" - tokens appear tradable for 24h then become unsellable.\n\nWe\'ve flagged 6 contracts in 48h.\n\nProtect yourself:\n✅ Check sell functions\n✅ Test with small amount first\n✅ Use @rugmunchbot before aping\n\nRT to save a degen.'
      });
      setIsGenerating(false);
    }, 2000);
  };

  const handlePost = () => {
    const post: Post = {
      id: `p${Date.now()}`,
      content: newPost.content,
      platform: newPost.platform,
      status: newPost.scheduled ? 'scheduled' : (newPost.requiresApproval ? 'pending_approval' : 'published'),
      scheduledFor: newPost.scheduled ? newPost.scheduledFor : undefined,
      publishedAt: !newPost.scheduled && !newPost.requiresApproval ? new Date().toISOString() : undefined,
      aiGenerated: newPost.useAI,
      approved: !newPost.requiresApproval,
      hashtags: ['#RugMunchIntel'],
      autoPosted: false,
      category: newPost.category
    };
    setPosts([post, ...posts]);
    setNewPost({ content: '', platform: 'both', useAI: true, scheduled: false, scheduledFor: '', category: 'update', requiresApproval: true });
  };

  const handleAddAccount = () => {
    const account: SocialAccount = {
      id: `acc${Date.now()}`,
      platform: newAccount.platform,
      name: newAccount.name,
      handle: newAccount.handle.startsWith('@') ? newAccount.handle : `@${newAccount.handle}`,
      status: 'pending',
      followers: 0,
      apiConnected: false,
      dailyPostLimit: newAccount.dailyPostLimit,
      postsToday: 0,
      autoPostEnabled: false,
      requiresApproval: newAccount.requiresApproval,
      supportsMedia: true,
      supportsThreads: true,
      characterLimit: 280,
      addedAt: new Date().toISOString().split('T')[0],
      addedBy: 'ADMIN'
    };
    setAccounts([...accounts, account]);
    setShowAddAccount(false);
    setNewAccount({ platform: 'twitter', name: '', handle: '', apiKey: '', apiSecret: '', dailyPostLimit: 50, requiresApproval: true, fid: undefined, supportsMedia: true, supportsThreads: false, characterLimit: 280, botToken: '' });
  };

  const handleRemoveAccount = (accountId: string) => {
    setAccounts(accounts.filter(a => a.id !== accountId));
  };

  const handleToggleAccountStatus = (accountId: string) => {
    setAccounts(accounts.map(a =>
      a.id === accountId
        ? { ...a, status: a.status === 'active' ? 'inactive' : 'active' }
        : a
    ));
  };

  const handleToggleAutoPost = (accountId: string) => {
    setAccounts(accounts.map(a =>
      a.id === accountId
        ? { ...a, autoPostEnabled: !a.autoPostEnabled }
        : a
    ));
  };

  const handleAddAutoPostRule = () => {
    if (!newRule.name) return;
    const rule: AutoPostRule = {
      id: `apr${Date.now()}`,
      name: newRule.name,
      enabled: newRule.enabled ?? true,
      platforms: newRule.platforms ?? ['twitter'],
      primaryPlatform: newRule.primaryPlatform ?? 'twitter',
      frequency: newRule.frequency ?? 'daily',
      contentType: newRule.contentType ?? 'mixed',
      maxPostsPerDay: newRule.maxPostsPerDay ?? 5,
      requireApproval: newRule.requireApproval ?? true,
      useAI: newRule.useAI ?? true,
      timeWindow: newRule.timeWindow ?? { start: '09:00', end: '18:00' },
      websiteFirst: true,
      editingWindow: 5
    };
    setAutoPostRules([...autoPostRules, rule]);
    setShowAddRule(false);
    setNewRule({
      name: '',
      enabled: true,
      platforms: ['twitter'],
      primaryPlatform: 'twitter',
      frequency: 'daily',
      contentType: 'mixed',
      maxPostsPerDay: 5,
      requireApproval: true,
      useAI: true,
      timeWindow: { start: '09:00', end: '18:00' }
    });
  };

  const handleToggleRule = (ruleId: string) => {
    setAutoPostRules(rules =>
      rules.map(r => r.id === ruleId ? { ...r, enabled: !r.enabled } : r)
    );
  };

  const handleDeleteRule = (ruleId: string) => {
    setAutoPostRules(rules => rules.filter(r => r.id !== ruleId));
  };

  const handleMarkShillUsed = (targetId: string) => {
    setShillTargets(targets =>
      targets.map(t =>
        t.id === targetId
          ? { ...t, used: true, lastShilledAt: new Date().toISOString(), totalShills: t.totalShills + 1 }
          : t
      )
    );
  };

  const handleResetShillTargets = () => {
    setShillTargets(targets =>
      targets.map(t => ({ ...t, used: false }))
    );
  };

  const handleSelectPost = (postId: string) => {
    const newSelected = new Set(selectedPosts);
    if (newSelected.has(postId)) {
      newSelected.delete(postId);
    } else {
      newSelected.add(postId);
    }
    setSelectedPosts(newSelected);
  };

  const handleSelectAll = () => {
    const filteredPosts = getFilteredPosts();
    if (selectedPosts.size === filteredPosts.length) {
      setSelectedPosts(new Set());
    } else {
      setSelectedPosts(new Set(filteredPosts.map(p => p.id)));
    }
  };

  const handleDeleteSelected = () => {
    setPosts(posts.filter(p => !selectedPosts.has(p.id)));
    setSelectedPosts(new Set());
    setShowDeleteConfirm(false);
  };

  const handleApprovePost = (postId: string) => {
    setPosts(posts.map(p =>
      p.id === postId
        ? { ...p, status: 'scheduled', approved: true, approvedBy: 'ADMIN', approvedAt: new Date().toISOString() }
        : p
    ));
  };

  const handleCancelScheduled = (postId: string) => {
    setPosts(posts.map(p =>
      p.id === postId
        ? { ...p, status: 'draft', scheduledFor: undefined }
        : p
    ));
  };

  const handlePublishNow = (postId: string) => {
    setPosts(posts.map(p =>
      p.id === postId
        ? { ...p, status: 'published', publishedAt: new Date().toISOString() }
        : p
    ));
  };

  const getFilteredPosts = () => {
    switch (postFilter) {
      case 'scheduled': return posts.filter(p => p.status === 'scheduled');
      case 'published': return posts.filter(p => p.status === 'published');
      case 'draft': return posts.filter(p => p.status === 'draft');
      case 'pending': return posts.filter(p => p.status === 'pending_approval');
      default: return posts;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'inactive': return 'bg-gray-700 text-gray-400 border-gray-600';
      case 'suspended': return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'pending': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      default: return 'bg-gray-700 text-gray-400';
    }
  };

  const getPostStatusColor = (status: string) => {
    switch (status) {
      case 'published': return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'scheduled': return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      case 'draft': return 'bg-gray-700 text-gray-400 border-gray-600';
      case 'pending_approval': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'failed': return 'bg-red-500/20 text-red-400 border-red-500/30';
      default: return 'bg-gray-700 text-gray-400';
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0812] text-gray-100 font-mono selection:bg-[#7c3aed]/30">
      {/* Header */}
      <div className="bg-gradient-to-r from-[#0f0c1d] via-[#1a1525] to-[#0f0c1d] border-b border-[#7c3aed]/30">
        <div className="max-w-[1600px] mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="relative">
                <Globe className="w-8 h-8 text-[#7c3aed]" />
                <Send className="w-4 h-4 text-[#7c3aed] absolute -bottom-1 -right-1" />
              </div>
              <div>
                <h1 className="text-xl font-bold tracking-wider">
                  SOCIAL <span className="text-[#7c3aed]">COMMAND</span>
                </h1>
                <p className="text-xs text-gray-500 tracking-[0.2em]">X & TELEGRAM ORCHESTRATION CENTER</p>
              </div>
            </div>

            <div className="flex items-center gap-6">
              {/* Quick Stats */}
              <div className="flex items-center gap-4 text-sm">
                <div className="flex items-center gap-2 px-3 py-1.5 bg-green-500/10 border border-green-500/30 rounded">
                  <CheckCircle className="w-4 h-4 text-green-400" />
                  <span className="text-green-400">{accounts.filter(a => a.status === 'active').length} Active</span>
                </div>
                <div className="flex items-center gap-2 px-3 py-1.5 bg-blue-500/10 border border-blue-500/30 rounded">
                  <Clock className="w-4 h-4 text-blue-400" />
                  <span className="text-blue-400">{posts.filter(p => p.status === 'scheduled').length} Scheduled</span>
                </div>
                <div className="flex items-center gap-2 px-3 py-1.5 bg-yellow-500/10 border border-yellow-500/30 rounded">
                  <AlertTriangle className="w-4 h-4 text-yellow-400" />
                  <span className="text-yellow-400">{posts.filter(p => p.status === 'pending_approval').length} Pending</span>
                </div>
              </div>

              <button
                onClick={() => setActiveTab('create')}
                className="flex items-center gap-2 px-4 py-2 bg-[#7c3aed] hover:bg-[#6d28d9] text-white rounded transition-all"
              >
                <Plus className="w-4 h-4" />
                CREATE POST
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-[1600px] mx-auto p-6 space-y-6">
        {/* Stats Row */}
        <div className="grid grid-cols-6 gap-4">
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
            <Globe className="w-5 h-5 text-blue-400 mb-2" />
            <div className="text-xl font-bold">52.3K</div>
            <div className="text-xs text-gray-500">X Followers</div>
          </div>
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
            <Send className="w-5 h-5 text-blue-500 mb-2" />
            <div className="text-xl font-bold">12.8K</div>
            <div className="text-xs text-gray-500">Telegram Members</div>
          </div>
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
            <Eye className="w-5 h-5 text-[#7c3aed] mb-2" />
            <div className="text-xl font-bold">2.4M</div>
            <div className="text-xs text-gray-500">Monthly Impressions</div>
          </div>
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
            <Zap className="w-5 h-5 text-yellow-400 mb-2" />
            <div className="text-xl font-bold">89%</div>
            <div className="text-xs text-gray-500">AI-Generated</div>
          </div>
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
            <Target className="w-5 h-5 text-green-400 mb-2" />
            <div className="text-xl font-bold">4.2%</div>
            <div className="text-xs text-gray-500">Engagement Rate</div>
          </div>
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
            <Bot className="w-5 h-5 text-purple-400 mb-2" />
            <div className="text-xl font-bold">{autoPostRules.filter(r => r.enabled).length}/{autoPostRules.length}</div>
            <div className="text-xs text-gray-500">Auto-Rules Active</div>
          </div>
        </div>

        {/* Navigation */}
        <div className="flex items-center gap-1 border-b border-gray-800">
          {[
            { id: 'dashboard', label: 'CONTENT QUEUE', icon: <Clock className="w-4 h-4" /> },
            { id: 'create', label: 'CREATE POST', icon: <Plus className="w-4 h-4" /> },
            { id: 'calendar', label: 'CALENDAR', icon: <Calendar className="w-4 h-4" /> },
            { id: 'accounts', label: 'ACCOUNTS', icon: <Users className="w-4 h-4" /> },
            { id: 'autopost', label: 'AUTO-POST', icon: <Bot className="w-4 h-4" /> },
            { id: 'targets', label: 'SHILL TARGETS', icon: <Target className="w-4 h-4" /> },
            { id: 'analytics', label: 'ANALYTICS', icon: <BarChart3 className="w-4 h-4" /> },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 px-4 py-3 text-xs font-semibold tracking-wider transition-all border-b-2 ${
                activeTab === tab.id
                  ? 'text-[#7c3aed] border-[#7c3aed]'
                  : 'text-gray-500 border-transparent hover:text-gray-300'
              }`}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </div>

        {/* Dashboard / Content Queue */}
        {activeTab === 'dashboard' && (
          <div className="space-y-4">
            {/* Bulk Actions Bar */}
            <div className="flex items-center justify-between bg-gradient-to-r from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
              <div className="flex items-center gap-4">
                <button
                  onClick={handleSelectAll}
                  className="flex items-center gap-2 text-sm text-gray-400 hover:text-white transition-all"
                >
                  {selectedPosts.size === getFilteredPosts().length ? <CheckSquare className="w-4 h-4" /> : <Square className="w-4 h-4" />}
                  Select All ({getFilteredPosts().length})
                </button>
                {selectedPosts.size > 0 && (
                  <>
                    <span className="text-gray-600">|</span>
                    <span className="text-sm text-[#7c3aed]">{selectedPosts.size} selected</span>
                    <button
                      onClick={() => setShowDeleteConfirm(true)}
                      className="flex items-center gap-2 px-3 py-1.5 bg-red-500/10 border border-red-500/30 rounded text-xs text-red-400 hover:bg-red-500/20 transition-all"
                    >
                      <Trash2 className="w-3 h-3" />
                      Delete Selected
                    </button>
                  </>
                )}
              </div>
              <div className="flex items-center gap-2">
                <Filter className="w-4 h-4 text-gray-500" />
                <select
                  value={postFilter}
                  onChange={(e) => setPostFilter(e.target.value as any)}
                  className="bg-gray-800 border border-gray-700 rounded px-3 py-1.5 text-xs"
                >
                  <option value="all">All Posts</option>
                  <option value="scheduled">Scheduled</option>
                  <option value="published">Published</option>
                  <option value="draft">Drafts</option>
                  <option value="pending">Pending Approval</option>
                </select>
              </div>
            </div>

            {/* Posts List */}
            <div className="space-y-3">
              {getFilteredPosts().length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  <FileText className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>No posts found in this category</p>
                </div>
              ) : (
                getFilteredPosts().map((post) => (
                  <div
                    key={post.id}
                    className={`bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border rounded-lg p-5 transition-all ${
                      selectedPosts.has(post.id) ? 'border-[#7c3aed]' : 'border-gray-800'
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <button
                        onClick={() => handleSelectPost(post.id)}
                        className="mt-1 text-gray-500 hover:text-[#7c3aed] transition-all"
                      >
                        {selectedPosts.has(post.id) ? <CheckSquare className="w-4 h-4" /> : <Square className="w-4 h-4" />}
                      </button>

                      <div className="flex-1">
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex items-center gap-2 flex-wrap">
                            {post.platform === 'twitter' && <Globe className="w-4 h-4 text-blue-400" />}
                            {post.platform === 'telegram' && <Send className="w-4 h-4 text-blue-500" />}
                            {post.platform === 'both' && <><Globe className="w-4 h-4 text-blue-400" /><Send className="w-4 h-4 text-blue-500" /></>}
                            <span className={`px-2 py-0.5 rounded text-[10px] border ${getPostStatusColor(post.status)}`}>
                              {post.status.replace('_', ' ').toUpperCase()}
                            </span>
                            {post.aiGenerated && (
                              <span className="px-2 py-0.5 bg-[#7c3aed]/20 text-[#7c3aed] rounded text-[10px]">AI</span>
                            )}
                            {post.autoPosted && (
                              <span className="px-2 py-0.5 bg-purple-500/20 text-purple-400 rounded text-[10px]">AUTO</span>
                            )}
                            {post.category && (
                              <span className="px-2 py-0.5 bg-gray-700 text-gray-400 rounded text-[10px]">
                                {post.category.toUpperCase()}
                              </span>
                            )}
                          </div>
                          <div className="text-xs text-gray-500">
                            {post.publishedAt || post.scheduledFor || 'Draft'}
                          </div>
                        </div>

                        <p className="text-sm text-gray-300 whitespace-pre-line mb-3">{post.content}</p>

                        <div className="flex items-center gap-2 mb-3">
                          {post.hashtags.map((tag, idx) => (
                            <span key={idx} className="text-xs text-[#7c3aed]">{tag}</span>
                          ))}
                        </div>

                        {post.engagement && (
                          <div className="flex items-center gap-6 text-xs text-gray-500 mb-3">
                            <span className="flex items-center gap-1"><Eye className="w-3 h-3" /> {post.engagement.views.toLocaleString()}</span>
                            <span className="flex items-center gap-1"><Heart className="w-3 h-3" /> {post.engagement.likes}</span>
                            <span className="flex items-center gap-1"><Repeat2 className="w-3 h-3" /> {post.engagement.retweets}</span>
                            <span className="flex items-center gap-1"><MessageSquare className="w-3 h-3" /> {post.engagement.replies}</span>
                          </div>
                        )}

                        {post.approvedBy && (
                          <div className="text-xs text-gray-500 mb-3">
                            Approved by {post.approvedBy} at {new Date(post.approvedAt || '').toLocaleString()}
                          </div>
                        )}

                        {/* Action Buttons */}
                        <div className="flex gap-2 pt-3 border-t border-gray-800">
                          {post.status === 'pending_approval' && (
                            <button
                              onClick={() => handleApprovePost(post.id)}
                              className="flex items-center gap-1.5 px-3 py-1.5 bg-green-500/10 border border-green-500/30 rounded text-xs text-green-400 hover:bg-green-500/20 transition-all"
                            >
                              <CheckCircle className="w-3 h-3" />
                              APPROVE
                            </button>
                          )}
                          {post.status === 'scheduled' && (
                            <>
                              <button
                                onClick={() => handlePublishNow(post.id)}
                                className="flex items-center gap-1.5 px-3 py-1.5 bg-green-500/10 border border-green-500/30 rounded text-xs text-green-400 hover:bg-green-500/20 transition-all"
                              >
                                <Play className="w-3 h-3" />
                                PUBLISH NOW
                              </button>
                              <button
                                onClick={() => handleCancelScheduled(post.id)}
                                className="flex items-center gap-1.5 px-3 py-1.5 bg-yellow-500/10 border border-yellow-500/30 rounded text-xs text-yellow-400 hover:bg-yellow-500/20 transition-all"
                              >
                                <Pause className="w-3 h-3" />
                                CANCEL
                              </button>
                            </>
                          )}
                          <button
                            onClick={() => {/* Edit post */}}
                            className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-800 border border-gray-700 rounded text-xs text-gray-400 hover:bg-gray-700 transition-all"
                          >
                            <Edit3 className="w-3 h-3" />
                            EDIT
                          </button>
                          <button
                            onClick={() => {
                              setSelectedPosts(new Set([post.id]));
                              setShowDeleteConfirm(true);
                            }}
                            className="flex items-center gap-1.5 px-3 py-1.5 bg-red-500/10 border border-red-500/30 rounded text-xs text-red-400 hover:bg-red-500/20 transition-all"
                          >
                            <Trash2 className="w-3 h-3" />
                            DELETE
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {/* Create Post */}
        {activeTab === 'create' && (
          <div className="grid grid-cols-3 gap-6">
            <div className="col-span-2 bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-bold">Create New Post</h2>
                <div className="flex items-center gap-2">
                  <button
                    onClick={handleGenerateAI}
                    disabled={isGenerating}
                    className="flex items-center gap-2 px-4 py-2 bg-[#7c3aed]/10 border border-[#7c3aed]/30 rounded-lg text-[#7c3aed] hover:bg-[#7c3aed]/20 transition-all disabled:opacity-50"
                  >
                    <Sparkles className={`w-4 h-4 ${isGenerating ? 'animate-pulse' : ''}`} />
                    {isGenerating ? 'GENERATING...' : 'AI GENERATE'}
                  </button>
                </div>
              </div>

              <div className="space-y-4">
                <textarea
                  value={newPost.content}
                  onChange={(e) => setNewPost({ ...newPost, content: e.target.value })}
                  placeholder="What's happening?"
                  rows={8}
                  className="w-full px-4 py-3 bg-[#0a0812] border border-gray-800 rounded-lg text-white placeholder-gray-600 focus:border-[#7c3aed] focus:outline-none resize-none"
                />

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <select
                      value={newPost.platform}
                      onChange={(e) => setNewPost({ ...newPost, platform: e.target.value as any })}
                      className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm"
                    >
                      <option value="both">X + Telegram</option>
                      <option value="twitter">X Only</option>
                      <option value="telegram">Telegram Only</option>
                    </select>

                    <select
                      value={newPost.category}
                      onChange={(e) => setNewPost({ ...newPost, category: e.target.value as any })}
                      className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm"
                    >
                      <option value="alert">🚨 Alert</option>
                      <option value="update">📊 Update</option>
                      <option value="educational">📚 Educational</option>
                      <option value="promotional">📢 Promotional</option>
                      <option value="community">👥 Community</option>
                    </select>

                    <label className="flex items-center gap-2 text-sm text-gray-400 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={newPost.scheduled}
                        onChange={(e) => setNewPost({ ...newPost, scheduled: e.target.checked })}
                        className="w-4 h-4 rounded border-gray-700 bg-gray-800 text-[#7c3aed]"
                      />
                      Schedule
                    </label>

                    <label className="flex items-center gap-2 text-sm text-gray-400 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={newPost.requiresApproval}
                        onChange={(e) => setNewPost({ ...newPost, requiresApproval: e.target.checked })}
                        className="w-4 h-4 rounded border-gray-700 bg-gray-800 text-[#7c3aed]"
                      />
                      Require Approval
                    </label>
                  </div>

                  <div className="text-xs text-gray-500">
                    {newPost.content.length}/280 characters
                  </div>
                </div>

                {newPost.scheduled && (
                  <input
                    type="datetime-local"
                    value={newPost.scheduledFor}
                    onChange={(e) => setNewPost({ ...newPost, scheduledFor: e.target.value })}
                    className="w-full px-4 py-2 bg-[#0a0812] border border-gray-800 rounded-lg text-white"
                  />
                )}

                <div className="flex gap-3 pt-4">
                  <button
                    onClick={handlePost}
                    disabled={!newPost.content}
                    className="flex-1 py-3 bg-[#7c3aed] text-white font-semibold rounded-lg hover:bg-[#6d28d9] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {newPost.scheduled ? 'SCHEDULE POST' : (newPost.requiresApproval ? 'SUBMIT FOR APPROVAL' : 'POST NOW')}
                  </button>
                  <button className="px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-gray-400 hover:bg-gray-700 transition-all">
                    SAVE DRAFT
                  </button>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-5">
                <h3 className="text-sm font-bold text-gray-500 uppercase tracking-wider mb-3">Templates</h3>
                <div className="space-y-2">
                  {templates.map((template) => (
                    <button
                      key={template.id}
                      onClick={() => setNewPost({ ...newPost, content: template.template })}
                      className="w-full p-3 bg-[#0a0812] rounded-lg text-left hover:border-[#7c3aed] border border-gray-800 transition-all"
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-sm">{template.name}</span>
                        <span className="text-[10px] px-2 py-0.5 bg-gray-800 rounded text-gray-400">{template.category}</span>
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        {template.platform} • Avg: {template.avgEngagement} • Used: {template.usage}x
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-5">
                <h3 className="text-sm font-bold text-gray-500 uppercase tracking-wider mb-3">Trending Hashtags</h3>
                <div className="flex flex-wrap gap-2">
                  {['#RugPull', '#CryptoSecurity', '#Web3', '#DeFi', '#ETH', '#BaseChain', '#AI', '#RugMunchIntel'].map((tag) => (
                    <button
                      key={tag}
                      onClick={() => setNewPost({ ...newPost, content: newPost.content + ' ' + tag })}
                      className="px-2 py-1 bg-gray-800 rounded text-xs text-[#7c3aed] hover:bg-[#7c3aed]/20 transition-all"
                    >
                      {tag}
                    </button>
                  ))}
                </div>
              </div>

              <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-5">
                <h3 className="text-sm font-bold text-gray-500 uppercase tracking-wider mb-3">Active Accounts</h3>
                <div className="space-y-2">
                  {accounts.filter(a => a.status === 'active').map((account) => (
                    <div key={account.id} className="flex items-center justify-between p-2 bg-[#0a0812] rounded">
                      <div className="flex items-center gap-2">
                        {account.platform === 'twitter' ? <Globe className="w-4 h-4 text-blue-400" /> : <Send className="w-4 h-4 text-blue-500" />}
                        <span className="text-sm">{account.handle}</span>
                      </div>
                      <div className="text-xs text-gray-500">{account.postsToday}/{account.dailyPostLimit}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Calendar View */}
        {activeTab === 'calendar' && (
          <div className="space-y-4">
            {/* Calendar Header */}
            <div className="flex items-center justify-between bg-gradient-to-r from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
              <div className="flex items-center gap-4">
                <button
                  onClick={() => setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1))}
                  className="p-2 hover:bg-gray-800 rounded transition-all"
                >
                  <ChevronLeft className="w-5 h-5" />
                </button>
                <h2 className="text-lg font-bold">
                  {currentMonth.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
                </h2>
                <button
                  onClick={() => setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1))}
                  className="p-2 hover:bg-gray-800 rounded transition-all"
                >
                  <ChevronRight className="w-5 h-5" />
                </button>
              </div>
              <div className="flex items-center gap-4 text-sm">
                <div className="flex items-center gap-2">
                  <span className="w-3 h-3 bg-blue-500/20 border border-blue-500 rounded"></span>
                  <span className="text-gray-400">Scheduled</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-3 h-3 bg-green-500/20 border border-green-500 rounded"></span>
                  <span className="text-gray-400">Published</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-3 h-3 bg-yellow-500/20 border border-yellow-500 rounded"></span>
                  <span className="text-gray-400">Pending</span>
                </div>
              </div>
            </div>

            {/* Calendar Grid */}
            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg overflow-hidden">
              {/* Weekday Headers */}
              <div className="grid grid-cols-7 border-b border-gray-800">
                {weekDays.map((day) => (
                  <div key={day} className="py-2 text-center text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    {day}
                  </div>
                ))}
              </div>

              {/* Calendar Days */}
              <div className="grid grid-cols-7">
                {calendarDays.map((day, idx) => (
                  <div
                    key={idx}
                    className={`min-h-[120px] border-b border-r border-gray-800 p-2 ${
                      day.isCurrentMonth ? 'bg-[#0a0812]' : 'bg-[#0f0c1d] opacity-50'
                    }`}
                  >
                    <div className="text-sm font-semibold mb-2 text-gray-400">{day.date}</div>
                    <div className="space-y-1">
                      {day.posts.slice(0, 3).map((post, pidx) => (
                        <div
                          key={pidx}
                          className={`text-[10px] p-1 rounded truncate cursor-pointer hover:opacity-80 transition-all ${
                            post.status === 'published' ? 'bg-green-500/20 text-green-400' :
                            post.status === 'scheduled' ? 'bg-blue-500/20 text-blue-400' :
                            'bg-yellow-500/20 text-yellow-400'
                          }`}
                          title={post.content}
                        >
                          {post.platform === 'twitter' ? '𝕏' : '✈'} {post.content.substring(0, 20)}...
                        </div>
                      ))}
                      {day.posts.length > 3 && (
                        <div className="text-[10px] text-gray-500 text-center">
                          +{day.posts.length - 3} more
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Accounts Management */}
        {activeTab === 'accounts' && (
          <div className="space-y-6">
            {/* Add Account Button */}
            <div className="flex justify-end">
              <button
                onClick={() => setShowAddAccount(true)}
                className="flex items-center gap-2 px-4 py-2 bg-[#7c3aed] hover:bg-[#6d28d9] text-white rounded transition-all"
              >
                <UserPlus className="w-4 h-4" />
                ADD ACCOUNT
              </button>
            </div>

            {/* Accounts Grid */}
            <div className="grid grid-cols-2 gap-4">
              {accounts.map((account) => (
                <div key={account.id} className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-5">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 bg-[#7c3aed]/10 rounded-full flex items-center justify-center">
                        {account.platform === 'twitter' ? <Globe className="w-6 h-6 text-blue-400" /> : <Send className="w-6 h-6 text-blue-500" />}
                      </div>
                      <div>
                        <h3 className="font-bold">{account.name}</h3>
                        <p className="text-sm text-gray-500">{account.handle}</p>
                      </div>
                    </div>
                    <span className={`px-2 py-1 rounded text-xs border ${getStatusColor(account.status)}`}>
                      {account.status.toUpperCase()}
                    </span>
                  </div>

                  <div className="grid grid-cols-3 gap-4 mb-4 text-center">
                    <div className="bg-[#0a0812] rounded p-2">
                      <div className="text-lg font-bold">{account.followers.toLocaleString()}</div>
                      <div className="text-xs text-gray-500">Followers</div>
                    </div>
                    <div className="bg-[#0a0812] rounded p-2">
                      <div className="text-lg font-bold">{account.postsToday}/{account.dailyPostLimit}</div>
                      <div className="text-xs text-gray-500">Today</div>
                    </div>
                    <div className="bg-[#0a0812] rounded p-2">
                      <div className={`text-lg font-bold ${account.apiConnected ? 'text-green-400' : 'text-red-400'}`}>
                        {account.apiConnected ? 'ON' : 'OFF'}
                      </div>
                      <div className="text-xs text-gray-500">API</div>
                    </div>
                  </div>

                  <div className="space-y-2 text-sm text-gray-400 mb-4">
                    <div className="flex justify-between">
                      <span>Last Post:</span>
                      <span>{account.lastPostAt || 'Never'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Added:</span>
                      <span>{account.addedAt} by {account.addedBy}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Approval Required:</span>
                      <span>{account.requiresApproval ? 'Yes' : 'No'}</span>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleToggleAccountStatus(account.id)}
                      className={`flex-1 py-2 rounded text-sm font-semibold transition-all ${
                        account.status === 'active'
                          ? 'bg-red-500/10 text-red-400 hover:bg-red-500/20'
                          : 'bg-green-500/10 text-green-400 hover:bg-green-500/20'
                      }`}
                    >
                      {account.status === 'active' ? 'DEACTIVATE' : 'ACTIVATE'}
                    </button>
                    <button
                      onClick={() => handleToggleAutoPost(account.id)}
                      className={`flex-1 py-2 rounded text-sm font-semibold transition-all ${
                        account.autoPostEnabled
                          ? 'bg-purple-500/10 text-purple-400 hover:bg-purple-500/20'
                          : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                      }`}
                    >
                      {account.autoPostEnabled ? 'AUTO: ON' : 'AUTO: OFF'}
                    </button>
                    <button
                      onClick={() => handleRemoveAccount(account.id)}
                      className="px-3 py-2 bg-red-500/10 border border-red-500/30 rounded text-red-400 hover:bg-red-500/20 transition-all"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Auto-Post Rules */}
        {activeTab === 'autopost' && (
          <div className="space-y-6">
            {/* Add Rule Button */}
            <div className="flex justify-end">
              <button
                onClick={() => setShowAddRule(true)}
                className="flex items-center gap-2 px-4 py-2 bg-[#7c3aed] hover:bg-[#6d28d9] text-white rounded transition-all"
              >
                <Plus className="w-4 h-4" />
                ADD AUTO-POST RULE
              </button>
            </div>

            {/* Rules List */}
            <div className="space-y-4">
              {autoPostRules.map((rule) => (
                <div
                  key={rule.id}
                  className={`bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border rounded-lg p-5 transition-all ${
                    rule.enabled ? 'border-gray-800' : 'border-gray-800 opacity-60'
                  }`}
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                        rule.enabled ? 'bg-[#7c3aed]/20' : 'bg-gray-800'
                      }`}>
                        <Bot className={`w-5 h-5 ${rule.enabled ? 'text-[#7c3aed]' : 'text-gray-500'}`} />
                      </div>
                      <div>
                        <h3 className="font-bold">{rule.name}</h3>
                        <p className="text-sm text-gray-500">
                          {rule.platforms?.includes('both') ? 'X + Telegram' : rule.primaryPlatform} • {rule.frequency.replace('_', ' ')}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => handleToggleRule(rule.id)}
                        className={`px-3 py-1.5 rounded text-xs font-semibold transition-all ${
                          rule.enabled
                            ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                            : 'bg-gray-800 text-gray-400 border border-gray-700'
                        }`}
                      >
                        {rule.enabled ? 'ENABLED' : 'DISABLED'}
                      </button>
                    </div>
                  </div>

                  <div className="grid grid-cols-4 gap-4 mb-4">
                    <div className="bg-[#0a0812] rounded p-3 text-center">
                      <div className="text-sm font-semibold text-gray-400">Content Type</div>
                      <div className="text-sm">{rule.contentType}</div>
                    </div>
                    <div className="bg-[#0a0812] rounded p-3 text-center">
                      <div className="text-sm font-semibold text-gray-400">Max/Day</div>
                      <div className="text-sm">{rule.maxPostsPerDay} posts</div>
                    </div>
                    <div className="bg-[#0a0812] rounded p-3 text-center">
                      <div className="text-sm font-semibold text-gray-400">Approval</div>
                      <div className="text-sm">{rule.requireApproval ? 'Required' : 'Auto'}</div>
                    </div>
                    <div className="bg-[#0a0812] rounded p-3 text-center">
                      <div className="text-sm font-semibold text-gray-400">Time Window</div>
                      <div className="text-sm">{rule.timeWindow.start} - {rule.timeWindow.end}</div>
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <button className="flex-1 py-2 bg-gray-800 border border-gray-700 rounded text-sm text-gray-400 hover:bg-gray-700 transition-all">
                      EDIT RULE
                    </button>
                    <button
                      onClick={() => handleDeleteRule(rule.id)}
                      className="px-3 py-2 bg-red-500/10 border border-red-500/30 rounded text-red-400 hover:bg-red-500/20 transition-all"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>

            {/* System Status */}
            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-5">
              <h3 className="text-lg font-bold mb-4">Auto-Post System Status</h3>
              <div className="grid grid-cols-4 gap-4">
                <div className="bg-[#0a0812] rounded p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Activity className="w-4 h-4 text-green-400" />
                    <span className="text-sm text-gray-400">Queue Status</span>
                  </div>
                  <div className="text-xl font-bold text-green-400">ACTIVE</div>
                </div>
                <div className="bg-[#0a0812] rounded p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Clock className="w-4 h-4 text-blue-400" />
                    <span className="text-sm text-gray-400">Next Post In</span>
                  </div>
                  <div className="text-xl font-bold text-blue-400">~45 min</div>
                </div>
                <div className="bg-[#0a0812] rounded p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Megaphone className="w-4 h-4 text-[#7c3aed]" />
                    <span className="text-sm text-gray-400">Posts Today</span>
                  </div>
                  <div className="text-xl font-bold text-[#7c3aed]">12</div>
                </div>
                <div className="bg-[#0a0812] rounded p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Sparkles className="w-4 h-4 text-yellow-400" />
                    <span className="text-sm text-gray-400">AI Success Rate</span>
                  </div>
                  <div className="text-xl font-bold text-yellow-400">94.2%</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Shill Targets */}
        {activeTab === 'targets' && (
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-lg font-bold">Daily Shill Targets</h2>
                <p className="text-sm text-gray-500">20 high-value accounts to engage with daily</p>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={handleResetShillTargets}
                  className="flex items-center gap-2 px-3 py-1.5 bg-gray-800 border border-gray-700 rounded text-xs text-gray-400 hover:bg-gray-700 transition-all"
                >
                  <RotateCcw className="w-3 h-3" />
                  RESET ALL
                </button>
                <select className="bg-gray-800 border border-gray-700 rounded px-3 py-1.5 text-xs">
                  <option>All Categories</option>
                  <option>Security</option>
                  <option>DeFi</option>
                  <option>Trading</option>
                  <option>Crypto</option>
                </select>
              </div>
            </div>

            <div className="space-y-3">
              {shillTargets.map((target) => (
                <div
                  key={target.id}
                  className={`flex items-center justify-between p-4 rounded-lg border transition-all ${
                    target.used
                      ? 'bg-gray-800/30 border-gray-800 opacity-50'
                      : 'bg-[#0a0812] border-gray-800 hover:border-[#7c3aed]/50'
                  }`}
                >
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 bg-[#7c3aed]/10 rounded-full flex items-center justify-center">
                      <Globe className="w-5 h-5 text-[#7c3aed]" />
                    </div>
                    <div>
                      <div className="font-semibold flex items-center gap-2">
                        {target.account}
                        {target.totalShills > 0 && (
                          <span className="text-[10px] px-2 py-0.5 bg-gray-800 rounded text-gray-400">
                            {target.totalShills} shills
                          </span>
                        )}
                      </div>
                      <div className="text-xs text-gray-500">{target.handle} • {target.followers.toLocaleString()} followers</div>
                      <div className="text-xs text-gray-400 mt-1">Last post: {target.lastPost}</div>
                    </div>
                  </div>

                  <div className="flex-1 mx-6">
                    <div className="text-xs text-gray-500 mb-1">AI Suggested Comment:</div>
                    <div className="text-sm text-gray-300 bg-gray-800/50 rounded p-2">{target.suggestedComment}</div>
                  </div>

                  <div className="flex items-center gap-3">
                    <span className={`px-2 py-1 rounded text-xs ${
                      target.relevance === 'high' ? 'bg-green-500/20 text-green-400' :
                      target.relevance === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
                      'bg-gray-700 text-gray-400'
                    }`}>
                      {target.relevance.toUpperCase()}
                    </span>
                    <button
                      onClick={() => navigator.clipboard.writeText(target.suggestedComment)}
                      className="p-2 bg-gray-800 rounded hover:bg-gray-700 transition-all"
                      title="Copy comment"
                    >
                      <Copy className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleMarkShillUsed(target.id)}
                      disabled={target.used}
                      className={`px-4 py-2 rounded text-sm font-semibold transition-all ${
                        target.used
                          ? 'bg-gray-800 text-gray-500 cursor-not-allowed'
                          : 'bg-[#7c3aed] text-white hover:bg-[#6d28d9]'
                      }`}
                    >
                      {target.used ? 'USED' : 'MARK USED'}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Analytics */}
        {activeTab === 'analytics' && (
          <div className="grid grid-cols-2 gap-6">
            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-bold mb-4">Engagement (30 Days)</h3>
              <div className="h-64 bg-[#0a0812] rounded-lg flex items-center justify-center border border-gray-800">
                <div className="text-center text-gray-500">
                  <BarChart3 className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p>Analytics integration with Globe API & Telegram Bot API</p>
                  <button className="mt-4 px-4 py-2 bg-[#7c3aed]/10 border border-[#7c3aed]/30 rounded text-[#7c3aed] text-sm hover:bg-[#7c3aed]/20 transition-all">
                    CONNECT APIS
                  </button>
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-bold mb-4">Top Performing Posts</h3>
              <div className="space-y-3">
                {[
                  { content: 'Rug pull thread #1', impressions: '450K', engagement: '5.2%', platform: 'twitter' },
                  { content: 'Weekly stats update', impressions: '230K', engagement: '4.8%', platform: 'both' },
                  { content: 'Honeypot guide', impressions: '180K', engagement: '6.1%', platform: 'telegram' },
                ].map((post, idx) => (
                  <div key={idx} className="p-3 bg-[#0a0812] rounded-lg">
                    <div className="flex items-center gap-2 mb-1">
                      {post.platform === 'twitter' ? <Globe className="w-3 h-3 text-blue-400" /> :
                       post.platform === 'telegram' ? <Send className="w-3 h-3 text-blue-500" /> :
                       <><Globe className="w-3 h-3 text-blue-400" /><Send className="w-3 h-3 text-blue-500" /></>}
                      <span className="text-sm font-semibold truncate">{post.content}</span>
                    </div>
                    <div className="flex justify-between text-xs text-gray-500">
                      <span>{post.impressions} impressions</span>
                      <span className="text-green-400">{post.engagement} engagement</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-bold mb-4">Platform Breakdown</h3>
              <div className="space-y-4">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="flex items-center gap-2"><Globe className="w-4 h-4 text-blue-400" /> X (Globe)</span>
                    <span className="text-sm font-semibold">68%</span>
                  </div>
                  <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                    <div className="h-full w-[68%] bg-blue-400 rounded-full"></div>
                  </div>
                </div>
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="flex items-center gap-2"><Send className="w-4 h-4 text-blue-500" /> Telegram</span>
                    <span className="text-sm font-semibold">32%</span>
                  </div>
                  <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                    <div className="h-full w-[32%] bg-blue-500 rounded-full"></div>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-bold mb-4">Content Performance</h3>
              <div className="space-y-3">
                {[
                  { type: 'Alerts', avgEngagement: '8.4%', color: 'red' },
                  { type: 'Educational', avgEngagement: '6.2%', color: 'blue' },
                  { type: 'Updates', avgEngagement: '4.8%', color: 'green' },
                  { type: 'Promotional', avgEngagement: '3.1%', color: 'purple' },
                ].map((item, idx) => (
                  <div key={idx} className="flex items-center justify-between p-2 bg-[#0a0812] rounded">
                    <span className="text-sm">{item.type}</span>
                    <span className={`text-sm font-semibold text-${item.color}-400`}>{item.avgEngagement}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Add Account Modal */}
      {showAddAccount && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-[#1a1525] border border-gray-800 rounded-lg p-6 w-[500px] max-w-[90vw]">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold">Add Social Account</h2>
              <button onClick={() => setShowAddAccount(false)} className="p-1 hover:bg-gray-800 rounded">
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-500 mb-1">Platform</label>
                <select
                  value={newAccount.platform}
                  onChange={(e) => setNewAccount({ ...newAccount, platform: e.target.value as any })}
                  className="w-full px-3 py-2 bg-[#0a0812] border border-gray-800 rounded"
                >
                  <option value="twitter">X (Globe)</option>
                  <option value="telegram">Telegram</option>
                </select>
              </div>
              <div>
                <label className="block text-sm text-gray-500 mb-1">Account Name</label>
                <input
                  type="text"
                  value={newAccount.name}
                  onChange={(e) => setNewAccount({ ...newAccount, name: e.target.value })}
                  placeholder="e.g., CryptoRugMunch"
                  className="w-full px-3 py-2 bg-[#0a0812] border border-gray-800 rounded"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-500 mb-1">Handle</label>
                <input
                  type="text"
                  value={newAccount.handle}
                  onChange={(e) => setNewAccount({ ...newAccount, handle: e.target.value })}
                  placeholder="@username"
                  className="w-full px-3 py-2 bg-[#0a0812] border border-gray-800 rounded"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-500 mb-1">API Key</label>
                <input
                  type="password"
                  value={newAccount.apiKey}
                  onChange={(e) => setNewAccount({ ...newAccount, apiKey: e.target.value })}
                  placeholder="Enter API key"
                  className="w-full px-3 py-2 bg-[#0a0812] border border-gray-800 rounded"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-500 mb-1">API Secret</label>
                <input
                  type="password"
                  value={newAccount.apiSecret}
                  onChange={(e) => setNewAccount({ ...newAccount, apiSecret: e.target.value })}
                  placeholder="Enter API secret"
                  className="w-full px-3 py-2 bg-[#0a0812] border border-gray-800 rounded"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-gray-500 mb-1">Daily Post Limit</label>
                  <input
                    type="number"
                    value={newAccount.dailyPostLimit}
                    onChange={(e) => setNewAccount({ ...newAccount, dailyPostLimit: parseInt(e.target.value) })}
                    className="w-full px-3 py-2 bg-[#0a0812] border border-gray-800 rounded"
                  />
                </div>
                <div className="flex items-center">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={newAccount.requiresApproval}
                      onChange={(e) => setNewAccount({ ...newAccount, requiresApproval: e.target.checked })}
                      className="w-4 h-4 rounded border-gray-700 bg-gray-800 text-[#7c3aed]"
                    />
                    <span className="text-sm">Require Approval</span>
                  </label>
                </div>
              </div>
              <div className="flex gap-3 pt-4">
                <button
                  onClick={handleAddAccount}
                  className="flex-1 py-2 bg-[#7c3aed] text-white rounded hover:bg-[#6d28d9] transition-all"
                >
                  ADD ACCOUNT
                </button>
                <button
                  onClick={() => setShowAddAccount(false)}
                  className="px-4 py-2 bg-gray-800 text-gray-400 rounded hover:bg-gray-700 transition-all"
                >
                  CANCEL
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Add Auto-Post Rule Modal */}
      {showAddRule && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-[#1a1525] border border-gray-800 rounded-lg p-6 w-[500px] max-w-[90vw]">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold">Add Auto-Post Rule</h2>
              <button onClick={() => setShowAddRule(false)} className="p-1 hover:bg-gray-800 rounded">
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-500 mb-1">Rule Name</label>
                <input
                  type="text"
                  value={newRule.name}
                  onChange={(e) => setNewRule({ ...newRule, name: e.target.value })}
                  placeholder="e.g., Daily Educational Posts"
                  className="w-full px-3 py-2 bg-[#0a0812] border border-gray-800 rounded"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-gray-500 mb-1">Platform</label>
                  <select
                    value={newRule.primaryPlatform}
                    onChange={(e) => {
                      const platform = e.target.value as Platform;
                      setNewRule({
                        ...newRule,
                        primaryPlatform: platform,
                        platforms: platform === 'both' ? ['twitter', 'telegram'] : [platform]
                      });
                    }}
                    className="w-full px-3 py-2 bg-[#0a0812] border border-gray-800 rounded"
                  >
                    <option value="twitter">X (Globe)</option>
                    <option value="telegram">Telegram</option>
                    <option value="both">Both</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm text-gray-500 mb-1">Frequency</label>
                  <select
                    value={newRule.frequency}
                    onChange={(e) => setNewRule({ ...newRule, frequency: e.target.value as any })}
                    className="w-full px-3 py-2 bg-[#0a0812] border border-gray-800 rounded"
                  >
                    <option value="hourly">Hourly</option>
                    <option value="3x_daily">3x Daily</option>
                    <option value="daily">Daily</option>
                    <option value="weekly">Weekly</option>
                  </select>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-gray-500 mb-1">Content Type</label>
                  <select
                    value={newRule.contentType}
                    onChange={(e) => setNewRule({ ...newRule, contentType: e.target.value as any })}
                    className="w-full px-3 py-2 bg-[#0a0812] border border-gray-800 rounded"
                  >
                    <option value="mixed">Mixed</option>
                    <option value="alerts">Alerts Only</option>
                    <option value="educational">Educational</option>
                    <option value="promotional">Promotional</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm text-gray-500 mb-1">Max Posts/Day</label>
                  <input
                    type="number"
                    value={newRule.maxPostsPerDay}
                    onChange={(e) => setNewRule({ ...newRule, maxPostsPerDay: parseInt(e.target.value) })}
                    className="w-full px-3 py-2 bg-[#0a0812] border border-gray-800 rounded"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-gray-500 mb-1">Time Window Start</label>
                  <input
                    type="time"
                    value={newRule.timeWindow?.start}
                    onChange={(e) => setNewRule({ ...newRule, timeWindow: { ...newRule.timeWindow!, start: e.target.value } })}
                    className="w-full px-3 py-2 bg-[#0a0812] border border-gray-800 rounded"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-500 mb-1">Time Window End</label>
                  <input
                    type="time"
                    value={newRule.timeWindow?.end}
                    onChange={(e) => setNewRule({ ...newRule, timeWindow: { ...newRule.timeWindow!, end: e.target.value } })}
                    className="w-full px-3 py-2 bg-[#0a0812] border border-gray-800 rounded"
                  />
                </div>
              </div>
              <div className="flex gap-4">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={newRule.requireApproval}
                    onChange={(e) => setNewRule({ ...newRule, requireApproval: e.target.checked })}
                    className="w-4 h-4 rounded border-gray-700 bg-gray-800 text-[#7c3aed]"
                  />
                  <span className="text-sm">Require Approval</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={newRule.useAI}
                    onChange={(e) => setNewRule({ ...newRule, useAI: e.target.checked })}
                    className="w-4 h-4 rounded border-gray-700 bg-gray-800 text-[#7c3aed]"
                  />
                  <span className="text-sm">Use AI</span>
                </label>
              </div>
              <div className="flex gap-3 pt-4">
                <button
                  onClick={handleAddAutoPostRule}
                  className="flex-1 py-2 bg-[#7c3aed] text-white rounded hover:bg-[#6d28d9] transition-all"
                >
                  ADD RULE
                </button>
                <button
                  onClick={() => setShowAddRule(false)}
                  className="px-4 py-2 bg-gray-800 text-gray-400 rounded hover:bg-gray-700 transition-all"
                >
                  CANCEL
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-[#1a1525] border border-gray-800 rounded-lg p-6 w-[400px]">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-red-500/20 rounded-full flex items-center justify-center">
                <AlertTriangle className="w-5 h-5 text-red-400" />
              </div>
              <h2 className="text-lg font-bold">Confirm Deletion</h2>
            </div>
            <p className="text-sm text-gray-400 mb-6">
              Are you sure you want to delete {selectedPosts.size} selected post{selectedPosts.size !== 1 ? 's' : ''}? This action cannot be undone.
            </p>
            <div className="flex gap-3">
              <button
                onClick={handleDeleteSelected}
                className="flex-1 py-2 bg-red-500 text-white rounded hover:bg-red-600 transition-all"
              >
                DELETE
              </button>
              <button
                onClick={() => setShowDeleteConfirm(false)}
                className="flex-1 py-2 bg-gray-800 text-gray-400 rounded hover:bg-gray-700 transition-all"
              >
                CANCEL
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SocialMediaManager;
