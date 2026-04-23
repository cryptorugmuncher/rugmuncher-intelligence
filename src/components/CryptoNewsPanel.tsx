import { useState, useEffect } from 'react';
import { Newspaper, TrendingUp, AlertTriangle, Clock, ExternalLink, RefreshCw, Filter, ChevronDown, BarChart3, Search, Shield, Zap, Globe, Bell } from 'lucide-react';
import { useAppStore } from '../store/appStore';

interface NewsItem {
  id: string;
  title: string;
  summary: string;
  source: string;
  category: 'security' | 'market' | 'regulation' | 'technology' | 'defi' | 'nft' | 'scam';
  severity?: 'low' | 'medium' | 'high' | 'critical';
  timestamp: string;
  url: string;
  relatedTokens: string[];
  readTime: number;
  isRugPull: boolean;
  evidenceLinks?: string[];
}

interface TrendingTopic {
  id: string;
  topic: string;
  volume24h: number;
  sentiment: 'positive' | 'neutral' | 'negative';
  changePercent: number;
  relatedProjects: string[];
}

interface WatchlistAlert {
  id: string;
  projectName: string;
  alertType: 'liquidity_drop' | 'sell_pressure' | 'contract_change' | 'whale_movement' | 'social_spike';
  severity: 'warning' | 'critical';
  timestamp: string;
  details: string;
}

const mockNews: NewsItem[] = [
  {
    id: '1',
    title: 'Major DeFi Protocol Exploit Results in $12M Loss',
    summary: 'A sophisticated flash loan attack targeted the lending pools. The attacker manipulated price oracles to drain liquidity. Protocol has paused all withdrawals pending investigation.',
    source: 'RMI Intelligence',
    category: 'security',
    severity: 'critical',
    timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
    url: '#',
    relatedTokens: ['HACKED-PROTO', 'ETH'],
    readTime: 3,
    isRugPull: false,
    evidenceLinks: ['https://etherscan.io/tx/0x...', 'https://twitter.com/PeckShieldAlert/...']
  },
  {
    id: '2',
    title: '$PEPE Clone Token Rugs for $2.3M',
    summary: 'Developers removed liquidity 48 hours after launch. MunchMap heat score spiked to 94/100 before the rug. Contract had hidden minting functions.',
    source: 'RMI MunchMap',
    category: 'scam',
    severity: 'high',
    timestamp: new Date(Date.now() - 1000 * 60 * 120).toISOString(),
    url: '#',
    relatedTokens: ['PEPE2', 'BSC'],
    readTime: 2,
    isRugPull: true,
    evidenceLinks: ['https://bscscan.com/address/0x...']
  },
  {
    id: '3',
    title: 'SEC Announces New Crypto Enforcement Division',
    summary: 'Regulatory focus shifting to DeFi protocols and staking services. Expect increased scrutiny of token classification and unregistered securities offerings.',
    source: 'Regulatory Watch',
    category: 'regulation',
    severity: 'medium',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 4).toISOString(),
    url: '#',
    relatedTokens: ['US Securities'],
    readTime: 4,
    isRugPull: false
  },
  {
    id: '4',
    title: 'Ethereum L2 Activity Surges Past Mainnet',
    summary: 'Base and Arbitrum combined now process 2.3x more transactions than Ethereum mainnet. Gas fees on L2s averaging $0.01-0.05 per transaction.',
    source: 'On-Chain Analytics',
    category: 'technology',
    severity: 'low',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 6).toISOString(),
    url: '#',
    relatedTokens: ['ETH', 'BASE', 'ARB'],
    readTime: 3,
    isRugPull: false
  },
  {
    id: '5',
    title: 'New Wallet Drainer Targeting NFT Traders',
    summary: 'Sophisticated phishing campaign using fake Blur bidding interfaces. Over $800k stolen in past 24 hours. Drainer code obfuscated through WASM.',
    source: 'RMI Threat Intel',
    category: 'security',
    severity: 'high',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 8).toISOString(),
    url: '#',
    relatedTokens: ['BLUR', 'Multiple NFTs'],
    readTime: 3,
    isRugPull: false,
    evidenceLinks: ['https://urlscan.io/...']
  }
];

const trendingTopics: TrendingTopic[] = [
  { id: '1', topic: 'Rug Pull Alerts', volume24h: 15420, sentiment: 'negative', changePercent: 23, relatedProjects: ['RMI MunchMap'] },
  { id: '2', topic: 'Base Chain Launches', volume24h: 8934, sentiment: 'positive', changePercent: 156, relatedProjects: ['Base', 'Friend.tech'] },
  { id: '3', topic: 'LayerZero Airdrop', volume24h: 12500, sentiment: 'positive', changePercent: 89, relatedProjects: ['ZRO', 'LayerZero'] },
  { id: '4', topic: 'MEV Bot Attacks', volume24h: 6543, sentiment: 'negative', changePercent: -12, relatedProjects: ['Ethereum'] },
  { id: '5', topic: 'Restaking Yields', volume24h: 9876, sentiment: 'positive', changePercent: 45, relatedProjects: ['EigenLayer', 'Ether.fi'] }
];

const watchlistAlerts: WatchlistAlert[] = [
  {
    id: '1',
    projectName: 'ShibaMoonX',
    alertType: 'liquidity_drop',
    severity: 'critical',
    timestamp: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
    details: '85% liquidity removed in 10 minutes. Active sells ongoing.'
  },
  {
    id: '2',
    projectName: 'SafeYield Pro',
    alertType: 'sell_pressure',
    severity: 'warning',
    timestamp: new Date(Date.now() - 1000 * 60 * 45).toISOString(),
    details: 'Unusual volume spike. 12 large sells in past hour.'
  },
  {
    id: '3',
    projectName: 'CryptoKitties V2',
    alertType: 'whale_movement',
    severity: 'warning',
    timestamp: new Date(Date.now() - 1000 * 60 * 90).toISOString(),
    details: 'Top 10 holder moved 40% of supply to exchange.'
  }
];

const categoryColors: Record<string, { bg: string; text: string; icon: any }> = {
  security: { bg: 'bg-red-500/10', text: 'text-red-400', icon: Shield },
  market: { bg: 'bg-green-500/10', text: 'text-green-400', icon: TrendingUp },
  regulation: { bg: 'bg-blue-500/10', text: 'text-blue-400', icon: Globe },
  technology: { bg: 'bg-purple-500/10', text: 'text-purple-400', icon: Zap },
  defi: { bg: 'bg-yellow-500/10', text: 'text-yellow-400', icon: BarChart3 },
  nft: { bg: 'bg-pink-500/10', text: 'text-pink-400', icon: Newspaper },
  scam: { bg: 'bg-orange-500/10', text: 'text-orange-400', icon: AlertTriangle }
};

export default function CryptoNewsPanel() {
  const { theme } = useAppStore();
  const darkMode = theme === 'dark';

  const [news] = useState<NewsItem[]>(mockNews);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedNews, setExpandedNews] = useState<Set<string>>(new Set());
  const [lastUpdated, setLastUpdated] = useState(new Date());

  const filteredNews = news.filter(item => {
    const matchesCategory = selectedCategory === 'all' || item.category === selectedCategory;
    const matchesSearch = item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         item.summary.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         item.relatedTokens.some(t => t.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchesCategory && matchesSearch;
  });

  const toggleExpanded = (id: string) => {
    const newSet = new Set(expandedNews);
    if (newSet.has(id)) {
      newSet.delete(id);
    } else {
      newSet.add(id);
    }
    setExpandedNews(newSet);
  };

  const formatTimeAgo = (timestamp: string) => {
    const diff = Date.now() - new Date(timestamp).getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(minutes / 60);

    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    return `${Math.floor(hours / 24)}d ago`;
  };

  const refreshNews = () => {
    setLastUpdated(new Date());
    // Would fetch new data here
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center gap-3">
            <Newspaper className="w-8 h-8 text-purple-500" />
            <div>
              <h1 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                CRYPTO INTELLIGENCE
              </h1>
              <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                Real-time security alerts, market intelligence, and threat monitoring
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <span className={`text-xs ${darkMode ? 'text-slate-500' : 'text-slate-500'}`}>
              Updated {formatTimeAgo(lastUpdated.toISOString())}
            </span>
            <button
              onClick={refreshNews}
              className="p-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-all"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
          <div className="flex items-center gap-2 mb-1">
            <AlertTriangle className="w-4 h-4 text-red-400" />
            <span className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Active Threats</span>
          </div>
          <p className="text-2xl font-bold text-red-400">7</p>
          <p className={`text-xs ${darkMode ? 'text-slate-500' : 'text-slate-500'}`}>+2 in last 24h</p>
        </div>
        <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
          <div className="flex items-center gap-2 mb-1">
            <Shield className="w-4 h-4 text-green-400" />
            <span className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Rugs Prevented</span>
          </div>
          <p className="text-2xl font-bold text-green-400">$2.4M</p>
          <p className={`text-xs ${darkMode ? 'text-slate-500' : 'text-slate-500'}`}>This month</p>
        </div>
        <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
          <div className="flex items-center gap-2 mb-1">
            <Search className="w-4 h-4 text-purple-400" />
            <span className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Wallets Scanned</span>
          </div>
          <p className="text-2xl font-bold text-purple-400">15,420</p>
          <p className={`text-xs ${darkMode ? 'text-slate-500' : 'text-slate-500'}`}>+1,234 today</p>
        </div>
        <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
          <div className="flex items-center gap-2 mb-1">
            <Bell className="w-4 h-4 text-yellow-400" />
            <span className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Watchlist Alerts</span>
          </div>
          <p className="text-2xl font-bold text-yellow-400">{watchlistAlerts.length}</p>
          <p className={`text-xs ${darkMode ? 'text-slate-500' : 'text-slate-500'}`}>Need attention</p>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* News Feed - 2 columns */}
        <div className="lg:col-span-2 space-y-4">
          {/* Filters */}
          <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
            <div className="flex flex-wrap gap-3">
              <div className="relative flex-1 min-w-[200px]">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                <input
                  type="text"
                  placeholder="Search news, tokens, projects..."
                  value={searchQuery}
                  onChange={e => setSearchQuery(e.target.value)}
                  className={`w-full pl-10 pr-4 py-2 rounded-lg border ${
                    darkMode
                      ? 'bg-slate-900 border-slate-700 text-white placeholder-slate-500'
                      : 'bg-white border-slate-300 placeholder-slate-400'
                  }`}
                />
              </div>
              <div className="flex gap-2">
                {[
                  { id: 'all', label: 'All', count: news.length },
                  { id: 'security', label: 'Security', count: news.filter(n => n.category === 'security').length },
                  { id: 'scam', label: 'Scams', count: news.filter(n => n.category === 'scam').length },
                  { id: 'market', label: 'Market', count: news.filter(n => n.category === 'market').length },
                ].map(cat => (
                  <button
                    key={cat.id}
                    onClick={() => setSelectedCategory(cat.id)}
                    className={`px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                      selectedCategory === cat.id
                        ? 'bg-purple-600 text-white'
                        : darkMode
                        ? 'bg-slate-700 text-slate-400 hover:text-white'
                        : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                    }`}
                  >
                    {cat.label} ({cat.count})
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* News Items */}
          <div className="space-y-3">
            {filteredNews.map(item => {
              const catStyle = categoryColors[item.category];
              const CatIcon = catStyle.icon;
              const isExpanded = expandedNews.has(item.id);

              return (
                <div
                  key={item.id}
                  className={`rounded-lg overflow-hidden transition-all ${
                    darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'
                  } ${item.isRugPull ? 'border-l-4 border-l-red-500' : ''}`}
                >
                  <div className="p-4">
                    {/* Header */}
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex items-start gap-3">
                        <div className={`p-2 rounded-lg ${catStyle.bg}`}>
                          <CatIcon className={`w-5 h-5 ${catStyle.text}`} />
                        </div>
                        <div>
                          <div className="flex items-center gap-2 flex-wrap">
                            <h3 className={`font-semibold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                              {item.title}
                            </h3>
                            {item.isRugPull && (
                              <span className="px-2 py-0.5 bg-red-500 text-white text-xs rounded font-medium">
                                RUG PULL
                              </span>
                            )}
                            {item.severity === 'critical' && (
                              <span className="px-2 py-0.5 bg-orange-500 text-white text-xs rounded font-medium animate-pulse">
                                CRITICAL
                              </span>
                            )}
                          </div>
                          <div className="flex items-center gap-3 mt-1 text-sm">
                            <span className={catStyle.text}>{item.source}</span>
                            <span className={`${darkMode ? 'text-slate-500' : 'text-slate-400'}`}>•</span>
                            <span className={`${darkMode ? 'text-slate-500' : 'text-slate-400'}`}>
                              {formatTimeAgo(item.timestamp)}
                            </span>
                            <span className={`${darkMode ? 'text-slate-500' : 'text-slate-400'}`}>•</span>
                            <span className={`${darkMode ? 'text-slate-500' : 'text-slate-400'} flex items-center gap-1`}>
                              <Clock className="w-3 h-3" />
                              {item.readTime} min read
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Summary */}
                    <p className={`mt-3 text-sm ${darkMode ? 'text-slate-300' : 'text-slate-600'}`}>
                      {isExpanded ? item.summary : item.summary.slice(0, 120) + (item.summary.length > 120 ? '...' : '')}
                    </p>

                    {/* Related Tokens */}
                    <div className="flex items-center gap-2 mt-3 flex-wrap">
                      {item.relatedTokens.map(token => (
                        <span
                          key={token}
                          className={`px-2 py-1 rounded text-xs font-medium ${
                            darkMode
                              ? 'bg-slate-700 text-slate-300'
                              : 'bg-slate-100 text-slate-600'
                          }`}
                        >
                          ${token}
                        </span>
                      ))}
                    </div>

                    {/* Actions */}
                    <div className="flex items-center justify-between mt-4">
                      <div className="flex gap-2">
                        <button
                          onClick={() => toggleExpanded(item.id)}
                          className={`flex items-center gap-1 text-sm ${darkMode ? 'text-slate-400 hover:text-white' : 'text-slate-500 hover:text-slate-900'}`}
                        >
                          <ChevronDown className={`w-4 h-4 transition-transform ${isExpanded ? 'rotate-180' : ''}`} />
                          {isExpanded ? 'Show Less' : 'Read More'}
                        </button>
                        <a
                          href={item.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center gap-1 text-sm text-purple-400 hover:text-purple-300"
                        >
                          <ExternalLink className="w-4 h-4" />
                          Source
                        </a>
                      </div>
                      {item.isRugPull && (
                        <button className="px-3 py-1.5 bg-red-600/20 text-red-400 text-sm rounded hover:bg-red-600/30 transition-all">
                          View on MunchMap
                        </button>
                      )}
                    </div>

                    {/* Evidence Links (expanded) */}
                    {isExpanded && item.evidenceLinks && (
                      <div className={`mt-4 p-3 rounded-lg ${darkMode ? 'bg-slate-900' : 'bg-slate-50'}`}>
                        <p className={`text-xs font-medium mb-2 ${darkMode ? 'text-slate-500' : 'text-slate-500'}`}>
                          EVIDENCE & SOURCES
                        </p>
                        <div className="space-y-1">
                          {item.evidenceLinks.map((link, idx) => (
                            <a
                              key={idx}
                              href={link}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="flex items-center gap-2 text-sm text-purple-400 hover:text-purple-300"
                            >
                              <ExternalLink className="w-3 h-3" />
                              {link.slice(0, 50)}...
                            </a>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Sidebar - 1 column */}
        <div className="space-y-4">
          {/* Watchlist Alerts */}
          <div className={`rounded-lg p-4 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
            <div className="flex items-center gap-2 mb-4">
              <Bell className="w-5 h-5 text-yellow-400" />
              <h3 className={`font-semibold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                Watchlist Alerts
              </h3>
            </div>
            <div className="space-y-3">
              {watchlistAlerts.map(alert => (
                <div
                  key={alert.id}
                  className={`p-3 rounded-lg border-l-2 ${
                    alert.severity === 'critical'
                      ? 'border-red-500 bg-red-500/5'
                      : 'border-yellow-500 bg-yellow-500/5'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className={`font-medium ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                      {alert.projectName}
                    </span>
                    <span className={`text-xs ${alert.severity === 'critical' ? 'text-red-400' : 'text-yellow-400'}`}>
                      {alert.severity.toUpperCase()}
                    </span>
                  </div>
                  <p className={`text-xs mt-1 ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                    {alert.details}
                  </p>
                  <p className={`text-xs mt-2 ${darkMode ? 'text-slate-500' : 'text-slate-500'}`}>
                    {formatTimeAgo(alert.timestamp)}
                  </p>
                </div>
              ))}
            </div>
            <button className="w-full mt-3 py-2 text-sm text-purple-400 hover:text-purple-300 transition-all">
              View All Alerts
            </button>
          </div>

          {/* Trending Topics */}
          <div className={`rounded-lg p-4 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
            <div className="flex items-center gap-2 mb-4">
              <TrendingUp className="w-5 h-5 text-green-400" />
              <h3 className={`font-semibold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                Trending Now
              </h3>
            </div>
            <div className="space-y-3">
              {trendingTopics.map(topic => (
                <div key={topic.id} className="flex items-center justify-between">
                  <div className="flex-1">
                    <p className={`font-medium text-sm ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                      {topic.topic}
                    </p>
                    <p className={`text-xs ${darkMode ? 'text-slate-500' : 'text-slate-500'}`}>
                      {topic.relatedProjects.join(', ')}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className={`text-sm font-medium ${
                      topic.changePercent > 0 ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {topic.changePercent > 0 ? '+' : ''}{topic.changePercent}%
                    </p>
                    <p className={`text-xs ${darkMode ? 'text-slate-500' : 'text-slate-500'}`}>
                      {(topic.volume24h / 1000).toFixed(1)}K mentions
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Quick Stats */}
          <div className={`rounded-lg p-4 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
            <h3 className={`font-semibold mb-4 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
              24H Security Summary
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Rug Pulls Detected</span>
                <span className="text-red-400 font-medium">3</span>
              </div>
              <div className="flex justify-between items-center">
                <span className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Total Value Lost</span>
                <span className="text-red-400 font-medium">$4.2M</span>
              </div>
              <div className="flex justify-between items-center">
                <span className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Alerts Sent</span>
                <span className="text-green-400 font-medium">1,247</span>
              </div>
              <div className="flex justify-between items-center">
                <span className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Wallets Protected</span>
                <span className="text-green-400 font-medium">8,932</span>
              </div>
              <div className="flex justify-between items-center">
                <span className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>New Scam Tokens</span>
                <span className="text-yellow-400 font-medium">47</span>
              </div>
            </div>
          </div>

          {/* Subscribe CTA */}
          <div className="bg-gradient-to-r from-purple-600 to-purple-800 rounded-lg p-4">
            <h3 className="text-white font-semibold mb-2">Daily Intelligence Briefing</h3>
            <p className="text-purple-200 text-sm mb-3">
              Get curated security alerts and market intelligence delivered to your inbox daily.
            </p>
            <button className="w-full py-2 bg-white text-purple-700 rounded-lg font-medium hover:bg-purple-50 transition-all text-sm">
              Subscribe $5/month
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
