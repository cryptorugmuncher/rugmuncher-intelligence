import React, { useState } from 'react';
import {
  Mail,
  Bell,
  DollarSign,
  Users,
  TrendingUp,
  Send,
  Plus,
  Trash2,
  Edit3,
  Eye,
  CheckCircle,
  X,
  Lock,
  Unlock,
  FileText,
  Calendar,
  Clock,
  BarChart3,
  Download,
  Search,
  Filter,
  Crown,
  Shield,
  Zap,
  Globe,
  AlertTriangle,
  CheckSquare,
  Square,
  ChevronDown,
  ChevronUp,
  Copy,
  Settings,
  RefreshCw,
  Sparkles,
  MessageSquare,
  Hash,
  Link
} from 'lucide-react';

interface Subscriber {
  id: string;
  email: string;
  name?: string;
  status: 'active' | 'unsubscribed' | 'bounced' | 'pending';
  tier: 'free' | 'daily_briefing';
  subscribedAt: string;
  lastEngagement?: string;
  openRate: number;
  clickRate: number;
  walletAddress?: string;
  tags: string[];
}

interface NewsletterIssue {
  id: string;
  subject: string;
  content: string;
  status: 'draft' | 'scheduled' | 'sent' | 'archived';
  tier: 'free' | 'daily_briefing' | 'both';
  createdAt: string;
  scheduledFor?: string;
  sentAt?: string;
  stats?: {
    sent: number;
    opened: number;
    clicked: number;
    bounced: number;
    unsubscribed: number;
  };
  aiGenerated: boolean;
  category: 'alert' | 'briefing' | 'update' | 'analysis' | 'promotional';
}

interface BriefingTemplate {
  id: string;
  name: string;
  sections: string[];
  active: boolean;
}

const NewsletterManager: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'subscribers' | 'issues' | 'briefing' | 'templates'>('overview');

  // Subscribers State
  const [subscribers, setSubscribers] = useState<Subscriber[]>([
    {
      id: 'sub1',
      email: 'whale@example.com',
      name: 'Crypto Whale',
      status: 'active',
      tier: 'daily_briefing',
      subscribedAt: '2026-01-15',
      lastEngagement: '2026-04-14',
      openRate: 87,
      clickRate: 42,
      walletAddress: '0x1234...5678',
      tags: ['whale', 'high-engagement', 'crm-holder']
    },
    {
      id: 'sub2',
      email: 'degen@example.com',
      name: 'DeFi Degen',
      status: 'active',
      tier: 'free',
      subscribedAt: '2026-02-20',
      lastEngagement: '2026-04-13',
      openRate: 45,
      clickRate: 12,
      tags: ['degen', 'low-engagement']
    },
    {
      id: 'sub3',
      email: 'security@example.com',
      status: 'active',
      tier: 'daily_briefing',
      subscribedAt: '2026-03-01',
      lastEngagement: '2026-04-14',
      openRate: 92,
      clickRate: 58,
      tags: ['security-focused', 'high-engagement']
    }
  ]);

  // Newsletter Issues State
  const [issues, setIssues] = useState<NewsletterIssue[]>([
    {
      id: 'iss1',
      subject: '🚨 Daily Intel Briefing: 3 New Honeypots Detected',
      content: 'Today our AI Swarm identified 3 major threats...',
      status: 'sent',
      tier: 'daily_briefing',
      createdAt: '2026-04-14 06:00',
      sentAt: '2026-04-14 07:00',
      stats: { sent: 2847, opened: 2432, clicked: 1245, bounced: 12, unsubscribed: 3 },
      aiGenerated: true,
      category: 'briefing'
    },
    {
      id: 'iss2',
      subject: 'Rug Munch Intel Weekly: $4.2M Saved This Week',
      content: 'Weekly roundup of all detected threats...',
      status: 'scheduled',
      tier: 'both',
      createdAt: '2026-04-13',
      scheduledFor: '2026-04-15 09:00',
      aiGenerated: true,
      category: 'update'
    },
    {
      id: 'iss3',
      subject: '[URGENT] Sleep Minting Attack on Base Chain',
      content: 'Critical alert: New attack vector detected...',
      status: 'draft',
      tier: 'both',
      createdAt: '2026-04-14',
      aiGenerated: false,
      category: 'alert'
    }
  ]);

  // Briefing Templates
  const [briefingTemplates, setBriefingTemplates] = useState<BriefingTemplate[]>([
    {
      id: 'bt1',
      name: 'Daily Intelligence Briefing ($5/month)',
      sections: ['Threat Overview', 'New Detections', 'Trending Scams', 'AI Analysis', 'Protection Tips', 'CRM Token Update'],
      active: true
    },
    {
      id: 'bt2',
      name: 'Weekly Free Digest',
      sections: ['Top 3 Threats', 'Community Highlights', 'Product Updates'],
      active: true
    }
  ]);

  // UI State
  const [showCreateIssue, setShowCreateIssue] = useState(false);
  const [showSubscribeModal, setShowSubscribeModal] = useState(false);
  const [selectedSubscribers, setSelectedSubscribers] = useState<Set<string>>(new Set());
  const [searchQuery, setSearchQuery] = useState('');
  const [tierFilter, setTierFilter] = useState<'all' | 'free' | 'daily_briefing'>('all');

  const [newIssue, setNewIssue] = useState({
    subject: '',
    content: '',
    tier: 'both' as 'free' | 'daily_briefing' | 'both',
    category: 'briefing' as NewsletterIssue['category'],
    scheduled: false,
    scheduledFor: '',
    useAI: true
  });

  const [isGenerating, setIsGenerating] = useState(false);

  // Stats
  const stats = {
    totalSubscribers: subscribers.length,
    activeSubscribers: subscribers.filter(s => s.status === 'active').length,
    dailyBriefingSubs: subscribers.filter(s => s.tier === 'daily_briefing' && s.status === 'active').length,
    monthlyRevenue: subscribers.filter(s => s.tier === 'daily_briefing' && s.status === 'active').length * 5,
    avgOpenRate: Math.round(subscribers.reduce((acc, s) => acc + s.openRate, 0) / subscribers.length),
    avgClickRate: Math.round(subscribers.reduce((acc, s) => acc + s.clickRate, 0) / subscribers.length)
  };

  const handleGenerateAI = () => {
    setIsGenerating(true);
    setTimeout(() => {
      setNewIssue({
        ...newIssue,
        content: `🎯 DAILY INTELLIGENCE BRIEFING — ${new Date().toLocaleDateString()}

THREAT OVERVIEW
Our AI Swarm analyzed 12,847 contracts in the last 24 hours. 23 potential threats were identified and flagged.

NEW DETECTIONS
• 3 honeypot contracts on Base Chain (total value at risk: $1.2M)
• 2 rug pull patterns detected pre-launch
• 1 social engineering campaign targeting DeFi users

TRENDING SCAMS
Sleep minting attacks continue to rise. Scammers deploy tokens that appear tradable for 24h before becoming unsellable. Check our pinned tweet for protection guide.

AI ANALYSIS
Threat level: ELEVATED
Recommended action: Increased vigilance on Base chain deployments

PROTECTION TIPS
✅ Always verify contract ownership
✅ Test sells before large purchases
✅ Use @rugmunchbot for instant scans

Stay safe. Don't get rugged.
— RMI Intel Team`
      });
      setIsGenerating(false);
    }, 2000);
  };

  const handleCreateIssue = () => {
    const issue: NewsletterIssue = {
      id: `iss${Date.now()}`,
      subject: newIssue.subject,
      content: newIssue.content,
      status: newIssue.scheduled ? 'scheduled' : 'draft',
      tier: newIssue.tier,
      createdAt: new Date().toISOString(),
      scheduledFor: newIssue.scheduled ? newIssue.scheduledFor : undefined,
      aiGenerated: newIssue.useAI,
      category: newIssue.category
    };
    setIssues([issue, ...issues]);
    setShowCreateIssue(false);
    setNewIssue({
      subject: '',
      content: '',
      tier: 'both',
      category: 'briefing',
      scheduled: false,
      scheduledFor: '',
      useAI: true
    });
  };

  const handleSendIssue = (issueId: string) => {
    setIssues(issues.map(i =>
      i.id === issueId
        ? { ...i, status: 'sent', sentAt: new Date().toISOString() }
        : i
    ));
  };

  const handleDeleteIssue = (issueId: string) => {
    setIssues(issues.filter(i => i.id !== issueId));
  };

  const handleToggleSubscriberStatus = (subId: string) => {
    setSubscribers(subscribers.map(s =>
      s.id === subId
        ? { ...s, status: s.status === 'active' ? 'unsubscribed' : 'active' }
        : s
    ));
  };

  const filteredSubscribers = subscribers.filter(s => {
    const matchesSearch = s.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         s.name?.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesTier = tierFilter === 'all' || s.tier === tierFilter;
    return matchesSearch && matchesTier;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'unsubscribed': return 'bg-gray-700 text-gray-400 border-gray-600';
      case 'bounced': return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'pending': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      default: return 'bg-gray-700 text-gray-400';
    }
  };

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'daily_briefing': return 'bg-[#7c3aed]/20 text-[#7c3aed] border-[#7c3aed]/30';
      case 'free': return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
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
              <div className="w-10 h-10 bg-[#7c3aed]/20 rounded-full flex items-center justify-center">
                <Mail className="w-5 h-5 text-[#7c3aed]" />
              </div>
              <div>
                <h1 className="text-xl font-bold tracking-wider">
                  NEWSLETTER <span className="text-[#7c3aed]">COMMAND</span>
                </h1>
                <p className="text-xs text-gray-500 tracking-[0.2em]">SUBSCRIBER INTELLIGENCE & DISTRIBUTION</p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 px-3 py-1.5 bg-[#7c3aed]/10 border border-[#7c3aed]/30 rounded">
                <DollarSign className="w-4 h-4 text-[#7c3aed]" />
                <span className="text-sm text-[#7c3aed]">${stats.monthlyRevenue}/mo Revenue</span>
              </div>
              <button
                onClick={() => setShowCreateIssue(true)}
                className="flex items-center gap-2 px-4 py-2 bg-[#7c3aed] hover:bg-[#6d28d9] text-white rounded transition-all"
              >
                <Plus className="w-4 h-4" />
                CREATE ISSUE
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-[1600px] mx-auto p-6 space-y-6">
        {/* Stats Row */}
        <div className="grid grid-cols-6 gap-4">
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
            <Users className="w-5 h-5 text-blue-400 mb-2" />
            <div className="text-xl font-bold">{stats.totalSubscribers}</div>
            <div className="text-xs text-gray-500">Total Subscribers</div>
          </div>
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
            <Crown className="w-5 h-5 text-[#7c3aed] mb-2" />
            <div className="text-xl font-bold">{stats.dailyBriefingSubs}</div>
            <div className="text-xs text-gray-500">Daily Briefing ($5/mo)</div>
          </div>
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
            <DollarSign className="w-5 h-5 text-green-400 mb-2" />
            <div className="text-xl font-bold">${stats.monthlyRevenue}</div>
            <div className="text-xs text-gray-500">Monthly Revenue</div>
          </div>
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
            <Eye className="w-5 h-5 text-yellow-400 mb-2" />
            <div className="text-xl font-bold">{stats.avgOpenRate}%</div>
            <div className="text-xs text-gray-500">Avg Open Rate</div>
          </div>
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
            <TrendingUp className="w-5 h-5 text-purple-400 mb-2" />
            <div className="text-xl font-bold">{stats.avgClickRate}%</div>
            <div className="text-xs text-gray-500">Avg Click Rate</div>
          </div>
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
            <Mail className="w-5 h-5 text-pink-400 mb-2" />
            <div className="text-xl font-bold">{issues.filter(i => i.status === 'sent').length}</div>
            <div className="text-xs text-gray-500">Issues Sent</div>
          </div>
        </div>

        {/* Navigation */}
        <div className="flex items-center gap-1 border-b border-gray-800">
          {[
            { id: 'overview', label: 'OVERVIEW', icon: <BarChart3 className="w-4 h-4" /> },
            { id: 'subscribers', label: 'SUBSCRIBERS', icon: <Users className="w-4 h-4" /> },
            { id: 'issues', label: 'NEWSLETTER ISSUES', icon: <Mail className="w-4 h-4" /> },
            { id: 'briefing', label: 'DAILY BRIEFING', icon: <Crown className="w-4 h-4" /> },
            { id: 'templates', label: 'TEMPLATES', icon: <FileText className="w-4 h-4" /> },
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

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-2 gap-6">
            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-bold mb-4">Subscriber Growth</h3>
              <div className="h-64 bg-[#0a0812] rounded-lg flex items-center justify-center border border-gray-800">
                <div className="text-center text-gray-500">
                  <TrendingUp className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p>Subscriber growth chart integration</p>
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-bold mb-4">Recent Issues</h3>
              <div className="space-y-3">
                {issues.slice(0, 5).map((issue) => (
                  <div key={issue.id} className="p-3 bg-[#0a0812] rounded-lg">
                    <div className="flex items-start justify-between mb-2">
                      <span className="text-sm font-semibold truncate flex-1">{issue.subject}</span>
                      <span className={`px-2 py-0.5 rounded text-[10px] ${
                        issue.status === 'sent' ? 'bg-green-500/20 text-green-400' :
                        issue.status === 'scheduled' ? 'bg-blue-500/20 text-blue-400' :
                        'bg-yellow-500/20 text-yellow-400'
                      }`}>
                        {issue.status.toUpperCase()}
                      </span>
                    </div>
                    {issue.stats && (
                      <div className="flex gap-4 text-xs text-gray-500">
                        <span>{issue.stats.sent} sent</span>
                        <span>{issue.stats.opened} opened</span>
                        <span>{issue.stats.clicked} clicked</span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-bold mb-4">Tier Breakdown</h3>
              <div className="space-y-4">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="flex items-center gap-2">
                      <Crown className="w-4 h-4 text-[#7c3aed]" />
                      Daily Briefing ($5/mo)
                    </span>
                    <span className="font-semibold">{stats.dailyBriefingSubs}</span>
                  </div>
                  <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-[#7c3aed] rounded-full"
                      style={{ width: `${(stats.dailyBriefingSubs / stats.totalSubscribers) * 100}%` }}
                    ></div>
                  </div>
                </div>
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="flex items-center gap-2">
                      <Mail className="w-4 h-4 text-blue-400" />
                      Free Tier
                    </span>
                    <span className="font-semibold">{stats.totalSubscribers - stats.dailyBriefingSubs}</span>
                  </div>
                  <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-blue-400 rounded-full"
                      style={{ width: `${((stats.totalSubscribers - stats.dailyBriefingSubs) / stats.totalSubscribers) * 100}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-bold mb-4">Engagement Metrics</h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-[#0a0812] rounded p-4 text-center">
                  <div className="text-2xl font-bold text-green-400">{stats.avgOpenRate}%</div>
                  <div className="text-xs text-gray-500">Average Open Rate</div>
                </div>
                <div className="bg-[#0a0812] rounded p-4 text-center">
                  <div className="text-2xl font-bold text-blue-400">{stats.avgClickRate}%</div>
                  <div className="text-xs text-gray-500">Average Click Rate</div>
                </div>
                <div className="bg-[#0a0812] rounded p-4 text-center">
                  <div className="text-2xl font-bold text-yellow-400">2.3%</div>
                  <div className="text-xs text-gray-500">Unsubscribe Rate</div>
                </div>
                <div className="bg-[#0a0812] rounded p-4 text-center">
                  <div className="text-2xl font-bold text-purple-400">0.4%</div>
                  <div className="text-xs text-gray-500">Bounce Rate</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Subscribers Tab */}
        {activeTab === 'subscribers' && (
          <div className="space-y-4">
            {/* Filter Bar */}
            <div className="flex items-center justify-between bg-gradient-to-r from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
              <div className="flex items-center gap-4">
                <div className="relative">
                  <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
                  <input
                    type="text"
                    placeholder="Search subscribers..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10 pr-4 py-2 bg-[#0a0812] border border-gray-800 rounded text-sm w-64"
                  />
                </div>
                <select
                  value={tierFilter}
                  onChange={(e) => setTierFilter(e.target.value as any)}
                  className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm"
                >
                  <option value="all">All Tiers</option>
                  <option value="free">Free</option>
                  <option value="daily_briefing">Daily Briefing</option>
                </select>
              </div>
              <div className="flex items-center gap-2">
                <button className="flex items-center gap-2 px-3 py-2 bg-gray-800 border border-gray-700 rounded text-sm text-gray-400 hover:bg-gray-700 transition-all">
                  <Download className="w-4 h-4" />
                  EXPORT CSV
                </button>
                <button
                  onClick={() => setShowSubscribeModal(true)}
                  className="flex items-center gap-2 px-3 py-2 bg-[#7c3aed] text-white rounded text-sm hover:bg-[#6d28d9] transition-all"
                >
                  <Plus className="w-4 h-4" />
                  ADD SUBSCRIBER
                </button>
              </div>
            </div>

            {/* Subscribers Table */}
            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg overflow-hidden">
              <table className="w-full">
                <thead className="bg-[#0f0c1d] border-b border-gray-800">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">EMAIL</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">TIER</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">STATUS</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">OPEN RATE</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">CLICK RATE</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">SUBSCRIBED</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">ACTIONS</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredSubscribers.map((sub) => (
                    <tr key={sub.id} className="border-b border-gray-800 hover:bg-[#0a0812]/50 transition-all">
                      <td className="px-4 py-3">
                        <div className="font-semibold">{sub.email}</div>
                        {sub.name && <div className="text-xs text-gray-500">{sub.name}</div>}
                        {sub.walletAddress && (
                          <div className="text-[10px] text-[#7c3aed]">💎 {sub.walletAddress}</div>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-1 rounded text-xs border ${getTierColor(sub.tier)}`}>
                          {sub.tier === 'daily_briefing' ? '$5 BRIEFING' : 'FREE'}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-1 rounded text-xs border ${getStatusColor(sub.status)}`}>
                          {sub.status.toUpperCase()}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          <div className="w-16 h-2 bg-gray-800 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-green-400 rounded-full"
                              style={{ width: `${sub.openRate}%` }}
                            ></div>
                          </div>
                          <span className="text-xs">{sub.openRate}%</span>
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          <div className="w-16 h-2 bg-gray-800 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-blue-400 rounded-full"
                              style={{ width: `${sub.clickRate}%` }}
                            ></div>
                          </div>
                          <span className="text-xs">{sub.clickRate}%</span>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-400">{sub.subscribedAt}</td>
                      <td className="px-4 py-3">
                        <div className="flex gap-2">
                          <button
                            onClick={() => handleToggleSubscriberStatus(sub.id)}
                            className={`px-2 py-1 rounded text-xs ${
                              sub.status === 'active'
                                ? 'bg-red-500/10 text-red-400 hover:bg-red-500/20'
                                : 'bg-green-500/10 text-green-400 hover:bg-green-500/20'
                            }`}
                          >
                            {sub.status === 'active' ? 'UNSUB' : 'RESUB'}
                          </button>
                          <button className="p-1 bg-gray-800 rounded hover:bg-gray-700 transition-all">
                            <Edit3 className="w-3 h-3" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Issues Tab */}
        {activeTab === 'issues' && (
          <div className="space-y-4">
            {issues.map((issue) => (
              <div
                key={issue.id}
                className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-5"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-2">
                    {issue.aiGenerated && (
                      <span className="px-2 py-0.5 bg-[#7c3aed]/20 text-[#7c3aed] rounded text-[10px]">AI</span>
                    )}
                    <span className={`px-2 py-0.5 rounded text-[10px] ${getTierColor(issue.tier)}`}>
                      {issue.tier === 'daily_briefing' ? '$5' : issue.tier === 'free' ? 'FREE' : 'ALL'}
                    </span>
                    <span className={`px-2 py-0.5 rounded text-[10px] ${
                      issue.status === 'sent' ? 'bg-green-500/20 text-green-400' :
                      issue.status === 'scheduled' ? 'bg-blue-500/20 text-blue-400' :
                      'bg-yellow-500/20 text-yellow-400'
                    }`}>
                      {issue.status.toUpperCase()}
                    </span>
                  </div>
                  <div className="text-xs text-gray-500">
                    {issue.sentAt || issue.scheduledFor || issue.createdAt}
                  </div>
                </div>

                <h3 className="font-bold mb-2">{issue.subject}</h3>
                <p className="text-sm text-gray-400 mb-4 line-clamp-2">{issue.content}</p>

                {issue.stats && (
                  <div className="grid grid-cols-5 gap-4 mb-4 bg-[#0a0812] rounded p-3">
                    <div className="text-center">
                      <div className="text-lg font-bold">{issue.stats.sent}</div>
                      <div className="text-[10px] text-gray-500">SENT</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-bold text-green-400">{issue.stats.opened}</div>
                      <div className="text-[10px] text-gray-500">OPENED</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-bold text-blue-400">{issue.stats.clicked}</div>
                      <div className="text-[10px] text-gray-500">CLICKED</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-bold text-red-400">{issue.stats.bounced}</div>
                      <div className="text-[10px] text-gray-500">BOUNCED</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-bold text-gray-400">{issue.stats.unsubscribed}</div>
                      <div className="text-[10px] text-gray-500">UNSUBS</div>
                    </div>
                  </div>
                )}

                <div className="flex gap-2">
                  {issue.status === 'draft' && (
                    <button
                      onClick={() => handleSendIssue(issue.id)}
                      className="px-3 py-1.5 bg-green-500/10 border border-green-500/30 rounded text-xs text-green-400 hover:bg-green-500/20 transition-all"
                    >
                      SEND NOW
                    </button>
                  )}
                  <button className="px-3 py-1.5 bg-gray-800 border border-gray-700 rounded text-xs text-gray-400 hover:bg-gray-700 transition-all">
                    EDIT
                  </button>
                  <button
                    onClick={() => handleDeleteIssue(issue.id)}
                    className="px-3 py-1.5 bg-red-500/10 border border-red-500/30 rounded text-xs text-red-400 hover:bg-red-500/20 transition-all"
                  >
                    DELETE
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Daily Briefing Tab */}
        {activeTab === 'briefing' && (
          <div className="space-y-6">
            <div className="bg-gradient-to-r from-[#7c3aed]/20 via-[#1a1525] to-[#0f0c1d] border border-[#7c3aed]/30 rounded-lg p-6">
              <div className="flex items-start justify-between">
                <div>
                  <h2 className="text-2xl font-bold mb-2 flex items-center gap-2">
                    <Crown className="w-6 h-6 text-[#7c3aed]" />
                    Daily Intelligence Briefing
                  </h2>
                  <p className="text-gray-400 mb-4">Premium subscription service delivering curated threat intelligence every morning</p>
                  <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2 px-4 py-2 bg-[#7c3aed]/10 border border-[#7c3aed]/30 rounded">
                      <DollarSign className="w-4 h-4 text-[#7c3aed]" />
                      <span className="font-bold">$5/month</span>
                    </div>
                    <div className="flex items-center gap-2 px-4 py-2 bg-gray-800 rounded">
                      <Users className="w-4 h-4 text-gray-400" />
                      <span>{stats.dailyBriefingSubs} subscribers</span>
                    </div>
                    <div className="flex items-center gap-2 px-4 py-2 bg-green-500/10 border border-green-500/30 rounded">
                      <TrendingUp className="w-4 h-4 text-green-400" />
                      <span className="text-green-400">87% retention</span>
                    </div>
                  </div>
                </div>
                <button className="px-4 py-2 bg-[#7c3aed] hover:bg-[#6d28d9] text-white rounded transition-all">
                  EDIT PRICING
                </button>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-6">
              <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
                <h3 className="text-lg font-bold mb-4">Briefing Sections</h3>
                <div className="space-y-3">
                  {briefingTemplates[0].sections.map((section, idx) => (
                    <div key={idx} className="flex items-center justify-between p-3 bg-[#0a0812] rounded">
                      <span className="flex items-center gap-2">
                        <span className="w-6 h-6 bg-[#7c3aed]/20 rounded-full flex items-center justify-center text-xs text-[#7c3aed]">
                          {idx + 1}
                        </span>
                        {section}
                      </span>
                      <label className="flex items-center gap-2 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={true}
                          className="w-4 h-4 rounded border-gray-700 bg-gray-800 text-[#7c3aed]"
                        />
                      </label>
                    </div>
                  ))}
                </div>
                <button className="w-full mt-4 py-2 border border-dashed border-gray-700 rounded text-gray-500 hover:border-[#7c3aed] hover:text-[#7c3aed] transition-all">
                  + ADD SECTION
                </button>
              </div>

              <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
                <h3 className="text-lg font-bold mb-4">Delivery Schedule</h3>
                <div className="space-y-4">
                  <div className="p-4 bg-[#0a0812] rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-semibold">Daily Delivery Time</span>
                      <span className="text-[#7c3aed]">07:00 UTC</span>
                    </div>
                    <p className="text-xs text-gray-500">Optimal open rates based on subscriber timezone analysis</p>
                  </div>

                  <div className="p-4 bg-[#0a0812] rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-semibold">AI Content Generation</span>
                      <span className="text-green-400">Enabled</span>
                    </div>
                    <p className="text-xs text-gray-500">Auto-generates briefing 30 minutes before delivery</p>
                  </div>

                  <div className="p-4 bg-[#0a0812] rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-semibold">Human Review Required</span>
                      <span className="text-yellow-400">Yes</span>
                    </div>
                    <p className="text-xs text-gray-500">Briefings await admin approval before sending</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Sample Briefing Preview */}
            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold">Sample Briefing Preview</h3>
                <button className="px-3 py-1.5 bg-[#7c3aed]/10 border border-[#7c3aed]/30 rounded text-xs text-[#7c3aed] hover:bg-[#7c3aed]/20 transition-all">
                  SEND TEST
                </button>
              </div>
              <div className="bg-[#0a0812] rounded-lg p-6 border border-gray-800">
                <div className="text-center mb-6">
                  <h4 className="text-xl font-bold text-[#7c3aed]">RUG MUNCH INTEL</h4>
                  <p className="text-sm text-gray-500">Daily Intelligence Briefing — April 14, 2026</p>
                </div>

                <div className="space-y-4 text-sm">
                  <div>
                    <h5 className="font-bold text-[#7c3aed] mb-2">🎯 THREAT OVERVIEW</h5>
                    <p className="text-gray-400">Our AI Swarm analyzed 12,847 contracts in the last 24 hours. 23 potential threats were identified and flagged.</p>
                  </div>
                  <div>
                    <h5 className="font-bold text-red-400 mb-2">🚨 NEW DETECTIONS</h5>
                    <ul className="text-gray-400 list-disc list-inside space-y-1">
                      <li>3 honeypot contracts on Base Chain (total value at risk: $1.2M)</li>
                      <li>2 rug pull patterns detected pre-launch</li>
                      <li>1 social engineering campaign targeting DeFi users</li>
                    </ul>
                  </div>
                  <div>
                    <h5 className="font-bold text-yellow-400 mb-2">📈 TRENDING SCAMS</h5>
                    <p className="text-gray-400">Sleep minting attacks continue to rise. Check our pinned tweet for protection guide.</p>
                  </div>
                </div>

                <div className="mt-6 pt-4 border-t border-gray-800 text-center text-xs text-gray-500">
                  <p>Premium briefing for $CRM Daily Briefing subscribers</p>
                  <p className="mt-1">Upgrade your security at rugmunch.com</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Templates Tab */}
        {activeTab === 'templates' && (
          <div className="grid grid-cols-2 gap-6">
            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold">Email Templates</h3>
                <button className="px-3 py-1.5 bg-[#7c3aed] text-white rounded text-sm hover:bg-[#6d28d9] transition-all">
                  + NEW TEMPLATE
                </button>
              </div>
              <div className="space-y-3">
                {[
                  { name: 'Daily Briefing', tier: 'paid', lastUsed: 'Today' },
                  { name: 'Weekly Digest', tier: 'free', lastUsed: '3 days ago' },
                  { name: 'Urgent Alert', tier: 'both', lastUsed: '1 week ago' },
                  { name: 'Welcome Email', tier: 'both', lastUsed: '2 weeks ago' },
                  { name: 'Re-engagement', tier: 'free', lastUsed: '1 month ago' },
                ].map((template, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 bg-[#0a0812] rounded-lg">
                    <div>
                      <div className="font-semibold">{template.name}</div>
                      <div className="text-xs text-gray-500">Last used: {template.lastUsed}</div>
                    </div>
                    <span className={`px-2 py-1 rounded text-xs ${getTierColor(template.tier === 'paid' ? 'daily_briefing' : template.tier === 'free' ? 'free' : 'both')}`}>
                      {template.tier.toUpperCase()}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-bold mb-4">Subscription Widget</h3>
              <div className="bg-[#0a0812] rounded-lg p-4 border border-gray-800">
                <p className="text-sm text-gray-400 mb-4">Embed code for website subscription form:</p>
                <code className="block p-3 bg-gray-900 rounded text-xs text-gray-300 overflow-x-auto">
                  {`<script src="https://rugmunch.com/widget.js"></script>
<div id="rmi-newsletter"></div>`}
                </code>
                <button className="mt-4 w-full py-2 bg-gray-800 border border-gray-700 rounded text-sm text-gray-400 hover:bg-gray-700 transition-all">
                  <Copy className="w-4 h-4 inline mr-2" />
                  COPY EMBED CODE
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Create Issue Modal */}
      {showCreateIssue && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-[#1a1525] border border-gray-800 rounded-lg p-6 w-[600px] max-w-[90vw] max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold">Create Newsletter Issue</h2>
              <button onClick={() => setShowCreateIssue(false)} className="p-1 hover:bg-gray-800 rounded">
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-500 mb-1">Subject Line</label>
                <input
                  type="text"
                  value={newIssue.subject}
                  onChange={(e) => setNewIssue({ ...newIssue, subject: e.target.value })}
                  placeholder="Enter subject..."
                  className="w-full px-3 py-2 bg-[#0a0812] border border-gray-800 rounded"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-gray-500 mb-1">Tier</label>
                  <select
                    value={newIssue.tier}
                    onChange={(e) => setNewIssue({ ...newIssue, tier: e.target.value as any })}
                    className="w-full px-3 py-2 bg-[#0a0812] border border-gray-800 rounded"
                  >
                    <option value="both">All Subscribers</option>
                    <option value="daily_briefing">Daily Briefing Only ($5)</option>
                    <option value="free">Free Tier Only</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm text-gray-500 mb-1">Category</label>
                  <select
                    value={newIssue.category}
                    onChange={(e) => setNewIssue({ ...newIssue, category: e.target.value as any })}
                    className="w-full px-3 py-2 bg-[#0a0812] border border-gray-800 rounded"
                  >
                    <option value="briefing">Briefing</option>
                    <option value="alert">Alert</option>
                    <option value="update">Update</option>
                    <option value="analysis">Analysis</option>
                    <option value="promotional">Promotional</option>
                  </select>
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-1">
                  <label className="text-sm text-gray-500">Content</label>
                  <button
                    onClick={handleGenerateAI}
                    disabled={isGenerating}
                    className="flex items-center gap-1 px-2 py-1 bg-[#7c3aed]/10 border border-[#7c3aed]/30 rounded text-xs text-[#7c3aed] hover:bg-[#7c3aed]/20 transition-all disabled:opacity-50"
                  >
                    <Sparkles className={`w-3 h-3 ${isGenerating ? 'animate-pulse' : ''}`} />
                    {isGenerating ? 'GENERATING...' : 'AI GENERATE'}
                  </button>
                </div>
                <textarea
                  value={newIssue.content}
                  onChange={(e) => setNewIssue({ ...newIssue, content: e.target.value })}
                  rows={12}
                  placeholder="Newsletter content..."
                  className="w-full px-3 py-2 bg-[#0a0812] border border-gray-800 rounded font-mono text-sm"
                />
              </div>

              <div className="flex items-center gap-4">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={newIssue.scheduled}
                    onChange={(e) => setNewIssue({ ...newIssue, scheduled: e.target.checked })}
                    className="w-4 h-4 rounded border-gray-700 bg-gray-800 text-[#7c3aed]"
                  />
                  <span className="text-sm">Schedule for later</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={newIssue.useAI}
                    onChange={(e) => setNewIssue({ ...newIssue, useAI: e.target.checked })}
                    className="w-4 h-4 rounded border-gray-700 bg-gray-800 text-[#7c3aed]"
                  />
                  <span className="text-sm">AI Generated</span>
                </label>
              </div>

              {newIssue.scheduled && (
                <input
                  type="datetime-local"
                  value={newIssue.scheduledFor}
                  onChange={(e) => setNewIssue({ ...newIssue, scheduledFor: e.target.value })}
                  className="w-full px-3 py-2 bg-[#0a0812] border border-gray-800 rounded"
                />
              )}

              <div className="flex gap-3 pt-4">
                <button
                  onClick={handleCreateIssue}
                  className="flex-1 py-2 bg-[#7c3aed] text-white rounded hover:bg-[#6d28d9] transition-all"
                >
                  {newIssue.scheduled ? 'SCHEDULE' : 'SAVE DRAFT'}
                </button>
                <button
                  onClick={() => setShowCreateIssue(false)}
                  className="px-4 py-2 bg-gray-800 text-gray-400 rounded hover:bg-gray-700 transition-all"
                >
                  CANCEL
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default NewsletterManager;
