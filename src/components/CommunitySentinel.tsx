import { useState } from 'react';
import { Shield, MessageSquare, AlertTriangle, TrendingDown, Users, Zap, Brain, CheckCircle2, XCircle, Clock, ChevronRight, ExternalLink, Filter, Flag, Send, Bot, BarChart3, PieChart, MessageCircle, Hash, AlertOctagon, Eye, Target } from 'lucide-react';
import { useAppStore } from '../store/appStore';

interface FUDAlert {
  id: string;
  platform: 'telegram' | 'discord' | 'twitter' | 'reddit';
  channel: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  type: 'fud_spread' | 'misinformation' | 'coordinated_attack' | 'impersonation' | 'price_manipulation' | 'rumor';
  content: string;
  author: string;
  timestamp: string;
  sentiment: number; // -100 to 100
  engagement: number; // likes, replies, etc
  status: 'new' | 'analyzing' | 'counter_measures' | 'resolved' | 'escalated';
  suggestedResponse?: string;
  aiAnalysis?: string;
  relatedMessages?: string[];
}

interface CounterStrategy {
  id: string;
  name: string;
  description: string;
  effectiveness: number;
  timeToDeploy: string;
  autoDeploy: boolean;
}

const mockAlerts: FUDAlert[] = [
  {
    id: '1',
    platform: 'telegram',
    channel: '@CryptoRugMunch',
    severity: 'high',
    type: 'misinformation',
    content: 'I heard the devs are planning to abandon the project after V2 launch. Be careful!',
    author: '@suspicious_user_123',
    timestamp: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
    sentiment: -75,
    engagement: 23,
    status: 'analyzing',
    suggestedResponse: 'This is false information. The team has published a 12-month roadmap with verifiable milestones. See our transparency dashboard.',
    aiAnalysis: 'Detected misinformation pattern. User account created 2 days ago. Message shares characteristics with known FUD campaigns. 78% probability of coordinated attack.',
    relatedMessages: ['Similar message in 3 other channels']
  },
  {
    id: '2',
    platform: 'discord',
    channel: '#general',
    severity: 'medium',
    type: 'rumor',
    content: 'Is it true that the airdrop is being delayed again? People are saying it won\'t happen until Q3.',
    author: 'concerned_holder#4567',
    timestamp: new Date(Date.now() - 1000 * 60 * 45).toISOString(),
    sentiment: -30,
    engagement: 12,
    status: 'counter_measures',
    suggestedResponse: 'Airdrop is on schedule for May 1st as announced. Check the CRM V2 Planning dashboard for real-time milestone tracking.',
    aiAnalysis: 'Organic concern from community member. No malicious intent detected. Address with factual information and transparency.'
  },
  {
    id: '3',
    platform: 'twitter',
    channel: '@CryptoRugMunch mentions',
    severity: 'critical',
    type: 'impersonation',
    content: '🚨 EMERGENCY: All users must verify wallets immediately at http://fake-rmi-verify.com - Failure to do so will result in lost funds!',
    author: '@CryptoRugMuch_FAKE',
    timestamp: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
    sentiment: -90,
    engagement: 156,
    status: 'escalated',
    suggestedResponse: '🚨 SCAM ALERT: This is a fake account. We will NEVER ask you to verify wallets via external links. Report and block @CryptoRugMuch_FAKE. Official account is @CryptoRugMunch only.',
    aiAnalysis: 'CRITICAL: Verified phishing attempt. Fake account using similar handle. Reports 5 user losses already. Immediate takedown request submitted to Twitter/X.'
  },
  {
    id: '4',
    platform: 'reddit',
    channel: 'r/CryptoRugMunch',
    severity: 'medium',
    type: 'fud_spread',
    content: 'The tokenomics don\'t make sense. 1% tax will kill volume. This is just another slow rug.',
    author: 'crypto_skeptic_99',
    timestamp: new Date(Date.now() - 1000 * 60 * 120).toISOString(),
    sentiment: -60,
    engagement: 45,
    status: 'counter_measures',
    suggestedResponse: 'The 1% tax is designed for sustainability - 0.5% to LP, 0.5% to treasury. Compare to competitors at 5-10%. Full breakdown in our whitepaper section on tokenomics.',
    aiAnalysis: 'Legitimate skepticism mixed with FUD language. Engage constructively with data. User has history of critical but fair analysis on other projects.'
  },
  {
    id: '5',
    platform: 'telegram',
    channel: 'Unofficial $CRM Trading',
    severity: 'high',
    type: 'price_manipulation',
    content: ' whales are dumping tonight at 8PM UTC. Exit now or get rekt. I have insider info.',
    author: '@insider_signals',
    timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
    sentiment: -85,
    engagement: 89,
    status: 'analyzing',
    suggestedResponse: 'No evidence of whale dumping. On-chain data shows steady accumulation. Always verify claims with MunchMap wallet analytics before making decisions.',
    aiAnalysis: 'Classic manipulation tactic. Account promotes "insider" information regularly. 0% accuracy rate historically. Recommend warning community about this account.'
  }
];

const counterStrategies: CounterStrategy[] = [
  {
    id: '1',
    name: 'Transparency Response',
    description: 'Post factual information with links to official sources',
    effectiveness: 85,
    timeToDeploy: '5 min',
    autoDeploy: true
  },
  {
    id: '2',
    name: 'Community Mobilization',
    description: 'Alert loyal community members to provide positive counter-narrative',
    effectiveness: 70,
    timeToDeploy: '15 min',
    autoDeploy: false
  },
  {
    id: '3',
    name: 'Direct Engagement',
    description: 'Founder or team member directly addresses the concern',
    effectiveness: 90,
    timeToDeploy: '30 min',
    autoDeploy: false
  },
  {
    id: '4',
    name: 'Platform Report',
    description: 'Report accounts for ToS violations, impersonation',
    effectiveness: 60,
    timeToDeploy: 'Immediate',
    autoDeploy: true
  },
  {
    id: '5',
    name: 'Legal Notice',
    description: 'Cease & desist for defamation or market manipulation',
    effectiveness: 95,
    timeToDeploy: '24-48 hours',
    autoDeploy: false
  }
];

const platformIcons: Record<string, any> = {
  telegram: MessageCircle,
  discord: Users,
  twitter: Target,
  reddit: MessageSquare
};

export default function CommunitySentinel() {
  const { theme } = useAppStore();
  const darkMode = theme === 'dark';

  const [alerts] = useState<FUDAlert[]>(mockAlerts);
  const [activeTab, setActiveTab] = useState<'monitor' | 'analysis' | 'response' | 'settings'>('monitor');
  const [selectedAlert, setSelectedAlert] = useState<string | null>(null);
  const [filterSeverity, setFilterSeverity] = useState<string>('all');
  const [filterPlatform, setFilterPlatform] = useState<string>('all');
  const [autoResponseEnabled, setAutoResponseEnabled] = useState(true);

  const stats = {
    activeThreats: alerts.filter(a => a.status !== 'resolved').length,
    critical: alerts.filter(a => a.severity === 'critical').length,
    resolved24h: 12,
    avgResponseTime: '8 min'
  };

  const filteredAlerts = alerts.filter(a => {
    const matchesSeverity = filterSeverity === 'all' || a.severity === filterSeverity;
    const matchesPlatform = filterPlatform === 'all' || a.platform === filterPlatform;
    return matchesSeverity && matchesPlatform;
  });

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-red-400 bg-red-500/10 animate-pulse';
      case 'high': return 'text-orange-400 bg-orange-500/10';
      case 'medium': return 'text-yellow-400 bg-yellow-500/10';
      default: return 'text-slate-400 bg-slate-500/10';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'escalated': return 'text-red-400';
      case 'counter_measures': return 'text-blue-400';
      case 'analyzing': return 'text-yellow-400';
      case 'resolved': return 'text-green-400';
      default: return 'text-slate-400';
    }
  };

  const getSentimentColor = (score: number) => {
    if (score < -50) return 'text-red-400';
    if (score < -20) return 'text-orange-400';
    if (score < 0) return 'text-yellow-400';
    return 'text-green-400';
  };

  const formatTimeAgo = (timestamp: string) => {
    const diff = Date.now() - new Date(timestamp).getTime();
    const minutes = Math.floor(diff / 60000);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    return `${Math.floor(hours / 24)}d ago`;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
        <div className="flex items-center gap-3 mb-2">
          <Shield className="w-8 h-8 text-purple-500" />
          <h1 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
            COMMUNITY SENTINEL
          </h1>
          <span className="px-2 py-1 bg-red-500/10 text-red-400 text-xs font-mono rounded animate-pulse">
            ACTIVE MONITOR
          </span>
        </div>
        <p className={`${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
          AI-powered community monitoring across Telegram, Discord, Twitter/X, and Reddit. Detects FUD, misinformation, and coordinated attacks with counter-strategy recommendations.
        </p>
      </div>

      {/* Alert Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
          <div className="flex items-center gap-2">
            <AlertOctagon className="w-5 h-5 text-red-400" />
            <span className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'}`}>{stats.activeThreats}</span>
          </div>
          <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Active Threats</p>
        </div>
        <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-orange-400" />
            <span className="text-2xl font-bold text-red-400">{stats.critical}</span>
          </div>
          <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Critical Alerts</p>
        </div>
        <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-5 h-5 text-green-400" />
            <span className={`text-2xl font-bold text-green-400`}>{stats.resolved24h}</span>
          </div>
          <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Resolved (24h)</p>
        </div>
        <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
          <div className="flex items-center gap-2">
            <Clock className="w-5 h-5 text-blue-400" />
            <span className="text-2xl font-bold text-blue-400">{stats.avgResponseTime}</span>
          </div>
          <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Avg Response</p>
        </div>
      </div>

      {/* Navigation */}
      <div className="flex flex-wrap gap-2">
        {[
          { id: 'monitor', label: 'Threat Monitor', icon: Eye },
          { id: 'analysis', label: 'AI Analysis', icon: Brain },
          { id: 'response', label: 'Response Center', icon: Zap },
          { id: 'settings', label: 'Sentinel Settings', icon: Shield }
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${
              activeTab === tab.id
                ? 'bg-purple-600 text-white'
                : darkMode
                ? 'bg-slate-800 text-slate-400 hover:text-white'
                : 'bg-white text-slate-600 hover:text-slate-900 border border-slate-200'
            }`}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Monitor Tab */}
      {activeTab === 'monitor' && (
        <div className="space-y-4">
          {/* Filters */}
          <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
            <div className="flex flex-wrap gap-4">
              <div>
                <label className={`block text-sm mb-1 ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Severity</label>
                <select
                  value={filterSeverity}
                  onChange={e => setFilterSeverity(e.target.value)}
                  className={`px-3 py-2 rounded-lg border ${darkMode ? 'bg-slate-900 border-slate-700 text-white' : 'bg-white border-slate-300'}`}
                >
                  <option value="all">All Severities</option>
                  <option value="critical">Critical</option>
                  <option value="high">High</option>
                  <option value="medium">Medium</option>
                  <option value="low">Low</option>
                </select>
              </div>
              <div>
                <label className={`block text-sm mb-1 ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Platform</label>
                <select
                  value={filterPlatform}
                  onChange={e => setFilterPlatform(e.target.value)}
                  className={`px-3 py-2 rounded-lg border ${darkMode ? 'bg-slate-900 border-slate-700 text-white' : 'bg-white border-slate-300'}`}
                >
                  <option value="all">All Platforms</option>
                  <option value="telegram">Telegram</option>
                  <option value="discord">Discord</option>
                  <option value="twitter">Twitter/X</option>
                  <option value="reddit">Reddit</option>
                </select>
              </div>
              <div className="flex items-end">
                <button className="flex items-center gap-2 px-4 py-2 text-sm text-slate-400 hover:text-white">
                  <Flag className="w-4 h-4" />
                  Mark All Reviewed
                </button>
              </div>
            </div>
          </div>

          {/* Alerts Feed */}
          <div className="grid lg:grid-cols-2 gap-4">
            {/* Alert List */}
            <div className="space-y-3">
              {filteredAlerts.map(alert => {
                const PlatformIcon = platformIcons[alert.platform];
                return (
                  <div
                    key={alert.id}
                    onClick={() => setSelectedAlert(selectedAlert === alert.id ? null : alert.id)}
                    className={`p-4 rounded-lg cursor-pointer transition-all ${
                      selectedAlert === alert.id
                        ? 'ring-2 ring-purple-500'
                        : ''
                    } ${darkMode ? 'bg-slate-800/50 border border-slate-700 hover:border-slate-600' : 'bg-white border border-slate-200 hover:border-slate-300'}`}
                  >
                    <div className="flex items-start gap-3">
                      <div className={`p-2 rounded-lg ${darkMode ? 'bg-slate-700' : 'bg-slate-100'}`}>
                        <PlatformIcon className="w-5 h-5 text-purple-400" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className={`px-2 py-0.5 rounded text-xs ${getSeverityColor(alert.severity)}`}>
                            {alert.severity.toUpperCase()}
                          </span>
                          <span className={`text-xs ${getStatusColor(alert.status)}`}>
                            {alert.status.replace('_', ' ')}
                          </span>
                        </div>
                        <p className={`font-medium mt-1 truncate ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                          {alert.content.slice(0, 80)}...
                        </p>
                        <div className="flex items-center gap-3 mt-2 text-xs">
                          <span className={darkMode ? 'text-slate-500' : 'text-slate-500'}>@{alert.author}</span>
                          <span className={darkMode ? 'text-slate-500' : 'text-slate-500'}>{formatTimeAgo(alert.timestamp)}</span>
                          <span className={getSentimentColor(alert.sentiment)}>Sentiment: {alert.sentiment}</span>
                          <span className={darkMode ? 'text-slate-500' : 'text-slate-500'}>{alert.engagement} engagement</span>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Alert Detail Panel */}
            <div>
              {selectedAlert ? (() => {
                const alert = alerts.find(a => a.id === selectedAlert);
                if (!alert) return null;
                return (
                  <div className={`p-6 rounded-lg sticky top-4 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
                    <div className="flex items-center gap-3 mb-4">
                      <AlertTriangle className="w-6 h-6 text-red-400" />
                      <div>
                        <p className={`font-semibold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                          {alert.type.replace('_', ' ').toUpperCase()}
                        </p>
                        <p className="text-sm text-purple-400">{alert.platform} • {alert.channel}</p>
                      </div>
                    </div>

                    {/* Original Content */}
                    <div className={`p-4 rounded-lg mb-4 ${darkMode ? 'bg-slate-900' : 'bg-slate-50'}`}>
                      <p className={`text-sm mb-2 ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>ORIGINAL MESSAGE</p>
                      <p className={`italic ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>"{alert.content}"</p>
                      <p className={`text-sm mt-2 ${darkMode ? 'text-slate-500' : 'text-slate-500'}`}>
                        By: {alert.author}
                      </p>
                    </div>

                    {/* AI Analysis */}
                    {alert.aiAnalysis && (
                      <div className={`p-4 rounded-lg mb-4 border border-purple-500/30 ${darkMode ? 'bg-purple-500/5' : 'bg-purple-50'}`}>
                        <div className="flex items-center gap-2 mb-2">
                          <Brain className="w-4 h-4 text-purple-400" />
                          <p className="text-sm text-purple-400">AI ANALYSIS</p>
                        </div>
                        <p className={`text-sm ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>
                          {alert.aiAnalysis}
                        </p>
                      </div>
                    )}

                    {/* Suggested Response */}
                    {alert.suggestedResponse && (
                      <div className="mb-4">
                        <p className={`text-sm mb-2 ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>SUGGESTED RESPONSE</p>
                        <div className={`p-3 rounded-lg ${darkMode ? 'bg-green-500/10' : 'bg-green-50'} border border-green-500/30`}>
                          <p className={`text-sm ${darkMode ? 'text-green-300' : 'text-green-700'}`}>
                            {alert.suggestedResponse}
                          </p>
                        </div>
                        <div className="flex gap-2 mt-2">
                          <button className="flex-1 py-2 bg-green-600 text-white rounded text-sm hover:bg-green-700">
                            Copy Response
                          </button>
                          <button className="flex-1 py-2 bg-purple-600 text-white rounded text-sm hover:bg-purple-700">
                            Customize
                          </button>
                        </div>
                      </div>
                    )}

                    {/* Actions */}
                    <div className="grid grid-cols-2 gap-2">
                      <button className="p-2 text-center text-sm bg-slate-700 text-white rounded hover:bg-slate-600">
                        Escalate to Team
                      </button>
                      <button className="p-2 text-center text-sm bg-red-600/20 text-red-400 rounded hover:bg-red-600/30">
                        Report Platform
                      </button>
                      <button className="p-2 text-center text-sm bg-blue-600/20 text-blue-400 rounded hover:bg-blue-600/30">
                        Deploy Counter-FUD
                      </button>
                      <button className="p-2 text-center text-sm bg-slate-700 text-white rounded hover:bg-slate-600">
                        Mark Resolved
                      </button>
                    </div>
                  </div>
                );
              })() : (
                <div className={`p-8 text-center rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
                  <Eye className="w-12 h-12 text-slate-500 mx-auto mb-4" />
                  <p className={`font-medium ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                    Select an alert to view details and response options
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Analysis Tab */}
      {activeTab === 'analysis' && (
        <div className="space-y-6">
          {/* Sentiment Overview */}
          <div className="grid md:grid-cols-2 gap-6">
            <div className={`p-6 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
              <h3 className={`font-semibold mb-4 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                Community Sentiment (7 Days)
              </h3>
              <div className="space-y-3">
                {[
                  { platform: 'Telegram', sentiment: 62, volume: 1234 },
                  { platform: 'Discord', sentiment: 45, volume: 892 },
                  { platform: 'Twitter/X', sentiment: -15, volume: 5678 },
                  { platform: 'Reddit', sentiment: 28, volume: 445 }
                ].map(item => (
                  <div key={item.platform} className="flex items-center justify-between">
                    <span className={`${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>{item.platform}</span>
                    <div className="flex items-center gap-3">
                      <div className="w-32 h-2 bg-slate-700 rounded-full overflow-hidden">
                        <div
                          className={`h-full ${item.sentiment > 0 ? 'bg-green-500' : 'bg-red-500'}`}
                          style={{ width: `${Math.abs(item.sentiment)}%` }}
                        />
                      </div>
                      <span className={`text-sm w-10 ${item.sentiment > 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {item.sentiment > 0 ? '+' : ''}{item.sentiment}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className={`p-6 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
              <h3 className={`font-semibold mb-4 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                Threat Categories (30 Days)
              </h3>
              <div className="space-y-3">
                {[
                  { type: 'Misinformation', count: 45, trend: '+12%' },
                  { type: 'Impersonation', count: 23, trend: '+5%' },
                  { type: 'Coordinated FUD', count: 12, trend: '-8%' },
                  { type: 'Price Manipulation', count: 18, trend: '+22%' }
                ].map(item => (
                  <div key={item.type} className="flex items-center justify-between">
                    <span className={`${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>{item.type}</span>
                    <div className="flex items-center gap-3">
                      <span className="font-medium text-white">{item.count}</span>
                      <span className={`text-xs ${item.trend.startsWith('+') ? 'text-red-400' : 'text-green-400'}`}>
                        {item.trend}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Key Insights */}
          <div className={`p-6 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
            <div className="flex items-center gap-2 mb-4">
              <Brain className="w-5 h-5 text-purple-400" />
              <h3 className={`font-semibold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                AI-Generated Insights
              </h3>
            </div>
            <div className="grid md:grid-cols-2 gap-4">
              <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-900/50' : 'bg-slate-50'}`}>
                <p className="text-yellow-400 font-medium mb-2">⚠️ Rising Concern</p>
                <p className={`text-sm ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>
                  Price manipulation narratives increasing 22% this week. Recommend proactive transparency about tokenomics and treasury management.
                </p>
              </div>
              <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-900/50' : 'bg-slate-50'}`}>
                <p className="text-green-400 font-medium mb-2">✓ Positive Signal</p>
                <p className={`text-sm ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>
                  Discord community sentiment improving (+18%) after transparency dashboard launch. Continue regular updates.
                </p>
              </div>
              <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-900/50' : 'bg-slate-50'}`}>
                <p className="text-blue-400 font-medium mb-2">📊 Pattern Detected</p>
                <p className={`text-sm ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>
                  New account cluster identified spreading similar FUD. Recommend monitoring and potential preemptive counter-narrative.
                </p>
              </div>
              <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-900/50' : 'bg-slate-50'}`}>
                <p className="text-purple-400 font-medium mb-2">💡 Recommendation</p>
                <p className={`text-sm ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>
                  Schedule AMA within 48 hours to address circulating questions about V2 timeline before they amplify.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Response Tab */}
      {activeTab === 'response' && (
        <div className="space-y-6">
          {/* Counter Strategies */}
          <div className={`p-6 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
            <h3 className={`font-semibold mb-4 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
              Counter-Strategy Playbook
            </h3>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {counterStrategies.map(strategy => (
                <div
                  key={strategy.id}
                  className={`p-4 rounded-lg border transition-all ${
                    darkMode
                      ? 'border-slate-700 hover:border-purple-500/50'
                      : 'border-slate-200 hover:border-purple-500/50'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <h4 className={`font-medium ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                      {strategy.name}
                    </h4>
                    <span className={`text-xs px-2 py-1 rounded ${
                      strategy.effectiveness >= 80 ? 'bg-green-500/10 text-green-400' :
                      strategy.effectiveness >= 60 ? 'bg-yellow-500/10 text-yellow-400' :
                      'bg-slate-500/10 text-slate-400'
                    }`}>
                      {strategy.effectiveness}% effective
                    </span>
                  </div>
                  <p className={`text-sm mb-3 ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                    {strategy.description}
                  </p>
                  <div className="flex items-center justify-between">
                    <span className={`text-xs ${darkMode ? 'text-slate-500' : 'text-slate-500'}`}>
                      Deploy: {strategy.timeToDeploy}
                    </span>
                    <label className="flex items-center gap-2 text-xs">
                      <input
                        type="checkbox"
                        checked={strategy.autoDeploy}
                        className="rounded border-purple-500"
                      />
                      Auto-deploy
                    </label>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Quick Response Templates */}
          <div className={`p-6 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
            <h3 className={`font-semibold mb-4 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
              Response Templates
            </h3>
            <div className="grid gap-4">
              {[
                {
                  name: 'Timeline Delay Clarification',
                  content: 'We understand concerns about timeline. Here\'s the current status: [X] is complete, [Y] is in review, [Z] launches [DATE]. Full transparency at [LINK].',
                  usage: 12
                },
                {
                  name: 'Tokenomics Defense',
                  content: 'Our 1% tax structure: 0.5% auto-LP (increases floor), 0.5% treasury (development). Compare to industry average of 5-10%. Sustainable growth > pump & dump.',
                  usage: 8
                },
                {
                  name: 'FUD Acknowledgment',
                  content: 'We see the concerns circulating. Let\'s address them with facts: [POINT 1], [POINT 2], [POINT 3]. Join our AMA [DATE] for live Q&A.',
                  usage: 5
                }
              ].map(template => (
                <div key={template.name} className={`p-4 rounded-lg ${darkMode ? 'bg-slate-900/50' : 'bg-slate-50'}`}>
                  <div className="flex items-center justify-between mb-2">
                    <h4 className={`font-medium ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                      {template.name}
                    </h4>
                    <span className={`text-xs ${darkMode ? 'text-slate-500' : 'text-slate-500'}`}>
                      Used {template.usage} times
                    </span>
                  </div>
                  <p className={`text-sm mb-3 ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                    {template.content}
                  </p>
                  <button className="text-sm text-purple-400 hover:text-purple-300">
                    Copy Template
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Settings Tab */}
      {activeTab === 'settings' && (
        <div className={`p-6 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
          <h3 className={`font-semibold mb-6 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
            Sentinel Configuration
          </h3>

          <div className="space-y-6">
            {/* Auto-Response Toggle */}
            <div className="flex items-center justify-between p-4 rounded-lg bg-slate-900/30">
              <div>
                <p className={`font-medium ${darkMode ? 'text-white' : 'text-slate-900'}`}>Auto-Response System</p>
                <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                  Automatically generate counter-responses for detected FUD (human approval required)
                </p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={autoResponseEnabled}
                  onChange={e => setAutoResponseEnabled(e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-slate-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
              </label>
            </div>

            {/* Alert Thresholds */}
            <div>
              <p className={`font-medium mb-4 ${darkMode ? 'text-white' : 'text-slate-900'}`}>Alert Thresholds</p>
              <div className="grid md:grid-cols-3 gap-4">
                <div>
                  <label className={`block text-sm mb-2 ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                    Critical: Sentiment below
                  </label>
                  <input
                    type="number"
                    defaultValue={-75}
                    className={`w-full px-3 py-2 rounded-lg border ${darkMode ? 'bg-slate-900 border-slate-700 text-white' : 'bg-white border-slate-300'}`}
                  />
                </div>
                <div>
                  <label className={`block text-sm mb-2 ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                    High: Engagement above
                  </label>
                  <input
                    type="number"
                    defaultValue={50}
                    className={`w-full px-3 py-2 rounded-lg border ${darkMode ? 'bg-slate-900 border-slate-700 text-white' : 'bg-white border-slate-300'}`}
                  />
                </div>
                <div>
                  <label className={`block text-sm mb-2 ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                    Auto-escalate after (min)
                  </label>
                  <input
                    type="number"
                    defaultValue={30}
                    className={`w-full px-3 py-2 rounded-lg border ${darkMode ? 'bg-slate-900 border-slate-700 text-white' : 'bg-white border-slate-300'}`}
                  />
                </div>
              </div>
            </div>

            {/* Monitored Channels */}
            <div>
              <p className={`font-medium mb-4 ${darkMode ? 'text-white' : 'text-slate-900'}`}>Monitored Channels</p>
              <div className="grid md:grid-cols-2 gap-4">
                {[
                  { name: '@CryptoRugMunch (Official TG)', status: 'active', type: 'telegram' },
                  { name: 'Discord #general', status: 'active', type: 'discord' },
                  { name: 'Discord #price-discussion', status: 'active', type: 'discord' },
                  { name: '@CryptoRugMunch mentions', status: 'active', type: 'twitter' },
                  { name: 'r/CryptoRugMunch', status: 'active', type: 'reddit' },
                  { name: 'Unofficial Trading Groups', status: 'pending', type: 'telegram' }
                ].map(channel => (
                  <div key={channel.name} className={`flex items-center justify-between p-3 rounded-lg ${darkMode ? 'bg-slate-900/50' : 'bg-slate-50'}`}>
                    <div className="flex items-center gap-3">
                      {channel.type === 'telegram' && <MessageCircle className="w-4 h-4 text-blue-400" />}
                      {channel.type === 'discord' && <Users className="w-4 h-4 text-purple-400" />}
                      {channel.type === 'twitter' && <Target className="w-4 h-4 text-blue-400" />}
                      {channel.type === 'reddit' && <MessageSquare className="w-4 h-4 text-orange-400" />}
                      <span className={`text-sm ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>{channel.name}</span>
                    </div>
                    <span className={`text-xs px-2 py-1 rounded ${
                      channel.status === 'active'
                        ? 'bg-green-500/10 text-green-400'
                        : 'bg-yellow-500/10 text-yellow-400'
                    }`}>
                      {channel.status.toUpperCase()}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
