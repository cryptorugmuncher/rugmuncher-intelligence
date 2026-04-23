/**
 * Telegram Dashboard
 * ==================
 * User-facing Telegram Bot management page.
 * Shows bot status, scan history, tier info, and channel links.
 */
import { useState, useEffect } from 'react';
import { useAppStore } from '../store/appStore';
import {
  Bot,
  Shield,
  Star,
  Zap,
  Crown,
  ScanLine,
  Clock,
  Trophy,
  ArrowUpRight,
  Radio,
  MessageSquare,
  Newspaper,
  AlertTriangle,
  ExternalLink,
  ChevronRight,
  Loader2,
  BarChart3,
  Hash,
  RefreshCw,
  AlertCircle,
  Users,
} from 'lucide-react';
import {
  getTelegramUserStatus,
  getTelegramScanHistory,
  getTelegramLeaderboard,
  createStarsInvoice,
} from '../services/telegramApi';
import { useTelegramWebApp } from '../hooks/useTelegramWebApp';

interface TelegramUser {
  telegram_id?: number;
  username?: string;
  first_name?: string;
  tier?: string;
  scans_used?: number;
  scans_limit?: number;
  scans_remaining?: number;
  xp?: number;
  level?: number;
  level_name?: string;
  badges?: string[];
  total_scans?: number;
  wallet_address?: string;
}

interface ScanRecord {
  id: string;
  scan_type: string;
  token: string;
  chain: string;
  result?: Record<string, any>;
  risk_score?: number;
  ai_consensus?: string;
  created_at: string;
}

interface LeaderboardEntry {
  telegram_id: number;
  username?: string;
  first_name?: string;
  total_scans: number;
  tier: string;
  xp: number;
  level: number;
}

const TIERS: Record<string, { name: string; color: string; icon: any; scans: string; bg: string; border: string }> = {
  free:  { name: 'Free',  color: 'text-gray-400',  icon: Shield,       scans: '3/month',   bg: 'bg-gray-500/10',  border: 'border-gray-500/20' },
  basic: { name: 'Basic', color: 'text-blue-400',  icon: Zap,          scans: '25/month',  bg: 'bg-blue-500/10',   border: 'border-blue-500/20' },
  pro:   { name: 'Pro',   color: 'text-purple-400', icon: Star,         scans: '100/month', bg: 'bg-purple-500/10', border: 'border-purple-500/20' },
  elite: { name: 'Elite', color: 'text-yellow-400', icon: Crown,        scans: 'Unlimited', bg: 'bg-yellow-500/10', border: 'border-yellow-500/20' },
};

const CHANNELS = [
  {
    id: '@rugmunch_scans',
    name: 'Scan Results',
    description: 'Public scan results & risk alerts',
    icon: ScanLine,
    color: 'text-blue-400',
    bg: 'bg-blue-500/10',
    border: 'border-blue-500/20',
  },
  {
    id: '@rugmunch_news',
    name: 'Intel News',
    description: 'Daily digest & market intel',
    icon: Newspaper,
    color: 'text-emerald-400',
    bg: 'bg-emerald-500/10',
    border: 'border-emerald-500/20',
  },
  {
    id: '@rugmunch_alerts',
    name: 'Critical Alerts',
    description: 'Real-time critical threat alerts',
    icon: AlertTriangle,
    color: 'text-red-400',
    bg: 'bg-red-500/10',
    border: 'border-red-500/20',
  },
  {
    id: '@rugmunch_premium',
    name: 'Premium Alpha',
    description: 'Whale signals & insider intel (Pro+)',
    icon: Crown,
    color: 'text-yellow-400',
    bg: 'bg-yellow-500/10',
    border: 'border-yellow-500/20',
  },
];

const BADGE_ICONS: Record<string, string> = {
  first_scan: '🎯',
  ten_scans: '🔬',
  fifty_scans: '🌊',
  hundred_scans: '⚔️',
  five_hundred_scans: '🔮',
  seven_day_streak: '🔥',
  thirty_day_streak: '📅',
  level_3: '⭐',
  level_5: '🏆',
  level_6: '👑',
  pro_subscriber: '💎',
  elite_subscriber: '👑',
};

const BADGE_NAMES: Record<string, string> = {
  first_scan: 'First Blood',
  ten_scans: 'Scan Surgeon',
  fifty_scans: 'Deep Diver',
  hundred_scans: 'Centurion',
  five_hundred_scans: 'Oracle',
  seven_day_streak: 'Consistent',
  thirty_day_streak: 'Obsessed',
  level_3: 'Rising Star',
  level_5: 'Elite Hunter',
  level_6: 'Legend',
  pro_subscriber: 'Pro Supporter',
  elite_subscriber: 'Elite Supporter',
};

// Derive a stable telegram_id from wallet address for demo/bridge purposes
function deriveTelegramId(wallet?: string): number {
  if (!wallet) return 123456789;
  // Use last 10 hex chars, convert to int, keep within safe integer range
  return parseInt(wallet.slice(-10), 16) % 1000000000;
}

function getMockUser(wallet?: string, web3Tier?: string): TelegramUser {
  const tier = web3Tier?.toLowerCase() || 'free';
  const tierCfg = TIERS[tier];
  const limit = tierCfg?.scans === 'Unlimited' ? -1 :
    tier === 'pro' ? 100 : tier === 'basic' ? 25 : 3;
  const used = Math.min(7, limit === -1 ? 7 : limit);
  return {
    telegram_id: deriveTelegramId(wallet),
    username: wallet ? `user_${wallet.slice(-6)}` : 'demo_user',
    first_name: 'Rug',
    tier,
    scans_used: used,
    scans_limit: limit,
    scans_remaining: limit === -1 ? -1 : Math.max(0, limit - used),
    xp: 340,
    level: 3,
    level_name: 'Analyst',
    badges: ['first_scan', 'ten_scans', 'level_3'],
    total_scans: 12,
  };
}

function getMockScans(): ScanRecord[] {
  return [
    { id: '1', scan_type: 'security', token: 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', chain: 'solana', risk_score: 23, ai_consensus: 'LOW', created_at: new Date(Date.now() - 3600000).toISOString() },
    { id: '2', scan_type: 'full_scan', token: 'So11111111111111111111111111111111111111112', chain: 'solana', risk_score: 12, ai_consensus: 'SAFE', created_at: new Date(Date.now() - 86400000).toISOString() },
    { id: '3', scan_type: 'audit', token: 'DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263', chain: 'solana', risk_score: 87, ai_consensus: 'CRITICAL', created_at: new Date(Date.now() - 172800000).toISOString() },
    { id: '4', scan_type: 'wallet', token: 'H8sMJSCQjG3qfD4uMZ8zX7qH1ZwKp1z9xYz2b3c4d5e6', chain: 'solana', risk_score: 45, ai_consensus: 'MEDIUM', created_at: new Date(Date.now() - 259200000).toISOString() },
  ];
}

function getMockLeaderboard(myId: number, myUser?: TelegramUser): LeaderboardEntry[] {
  return [
    { telegram_id: 987654321, username: 'whale_hunter', first_name: 'Alex', total_scans: 847, tier: 'elite', xp: 5200, level: 6 },
    { telegram_id: 876543210, username: 'rug_dodger', first_name: 'Sam', total_scans: 623, tier: 'pro', xp: 3100, level: 5 },
    { telegram_id: 765432109, username: 'degen_01', first_name: 'Mike', total_scans: 412, tier: 'pro', xp: 1850, level: 4 },
    { telegram_id: myId, username: myUser?.username, first_name: myUser?.first_name, total_scans: myUser?.total_scans || 12, tier: myUser?.tier || 'free', xp: myUser?.xp || 340, level: myUser?.level || 3 },
    { telegram_id: 654321098, username: 'newbie_scan', first_name: 'Jordan', total_scans: 3, tier: 'free', xp: 30, level: 1 },
  ];
}

export default function TelegramDashboard() {
  const user = useAppStore((state) => state.user);
  const setCurrentPage = useAppStore((state) => state.setCurrentPage);
  const { isInTelegram, telegramUser } = useTelegramWebApp();

  // Use Telegram user ID if inside WebApp, otherwise derive from wallet
  const telegramId = telegramUser?.id ?? deriveTelegramId(user?.wallet_address);

  const [tgUser, setTgUser] = useState<TelegramUser | null>(null);
  const [scans, setScans] = useState<ScanRecord[]>([]);
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState<'overview' | 'history' | 'leaderboard'>('overview');
  const [usingMock, setUsingMock] = useState(false);

  const loadData = async (force = false) => {
    setLoading(true);
    setError('');
    setUsingMock(false);

    try {
      // Try real APIs first
      const [userData, scansData, leaderboardData] = await Promise.all([
        getTelegramUserStatus(telegramId).catch(() => null),
        getTelegramScanHistory(telegramId, 50).catch(() => null),
        getTelegramLeaderboard(20).catch(() => null),
      ]);

      if (userData) {
        setTgUser(userData);
        setScans(scansData || []);
        setLeaderboard(leaderboardData || []);
      } else {
        // Fallback to mock data for demo
        const mockUser = getMockUser(user?.wallet_address, user?.tier);
        setTgUser(mockUser);
        setScans(getMockScans());
        setLeaderboard(getMockLeaderboard(telegramId, mockUser));
        setUsingMock(true);
      }
    } catch (e: any) {
      setError(e.message || 'Failed to load Telegram data');
      // Fallback
      const mockUser = getMockUser(user?.wallet_address, user?.tier);
      setTgUser(mockUser);
      setScans(getMockScans());
      setLeaderboard(getMockLeaderboard(telegramId, mockUser));
      setUsingMock(true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [telegramId, user]);

  const getRiskColor = (score?: number) => {
    if (score === undefined) return 'text-gray-400';
    if (score >= 70) return 'text-red-400';
    if (score >= 40) return 'text-orange-400';
    if (score >= 20) return 'text-yellow-400';
    return 'text-green-400';
  };

  const getConsensusBadge = (consensus?: string) => {
    const map: Record<string, string> = {
      CRITICAL: 'bg-red-500/20 text-red-400 border-red-500/30',
      HIGH: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
      MEDIUM: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
      LOW: 'bg-green-500/20 text-green-400 border-green-500/30',
      SAFE: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
    };
    return map[consensus || ''] || 'bg-gray-500/20 text-gray-400 border-gray-500/30';
  };

  const tierInfo = tgUser?.tier ? TIERS[tgUser.tier] : TIERS.free;
  const TierIcon = tierInfo.icon;

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="w-8 h-8 text-purple-400 animate-spin" />
        <span className="ml-3 text-gray-400">Loading Telegram Dashboard...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-3">
            <Bot className="w-7 h-7 text-purple-400" />
            Telegram Bot
          </h1>
          <p className="text-gray-400 mt-1">Manage your @rugmunchbot profile, scans, and channel subscriptions</p>
        </div>
        <div className="flex items-center gap-2">
          {isInTelegram && (
            <span className="text-xs px-2 py-1 bg-[#229ED9]/10 text-[#229ED9] rounded border border-[#229ED9]/20">
              Telegram Mini App
            </span>
          )}
          {usingMock && (
            <span className="text-xs px-2 py-1 bg-yellow-500/10 text-yellow-400 rounded border border-yellow-500/20">
              Demo Data
            </span>
          )}
          <button
            onClick={() => loadData(true)}
            className="p-2 rounded-lg bg-[#12121a] border border-purple-500/20 text-gray-400 hover:text-white hover:bg-white/5 transition-colors"
            title="Refresh"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <span className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium border ${tierInfo.bg} ${tierInfo.color} ${tierInfo.border}`}>
            <TierIcon className="w-4 h-4" />
            {tierInfo.name} Tier
          </span>
        </div>
      </div>

      {error && !usingMock && (
        <div className="flex items-center gap-2 p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm">
          <AlertCircle className="w-4 h-4" />
          {error}
        </div>
      )}

      {/* Tabs */}
      <div className="flex items-center gap-1 bg-[#12121a] rounded-lg p-1 w-fit">
        {(['overview', 'history', 'leaderboard'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
              activeTab === tab
                ? 'bg-purple-600 text-white'
                : 'text-gray-400 hover:text-white hover:bg-white/5'
            }`}
          >
            {tab === 'overview' && 'Overview'}
            {tab === 'history' && 'Scan History'}
            {tab === 'leaderboard' && 'Leaderboard'}
          </button>
        ))}
      </div>

      {/* ── OVERVIEW TAB ── */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* Private Group Info */}
          <div className="bg-gradient-to-r from-[#229ED9]/10 to-purple-500/10 border border-[#229ED9]/30 rounded-xl p-5">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-[#229ED9]/20 rounded-xl flex items-center justify-center">
                  <Users className="w-6 h-6 text-[#229ED9]" />
                </div>
                <div>
                  <h3 className="font-semibold text-white">Use in Your Private Group</h3>
                  <p className="text-sm text-gray-400">Add @rugmunchbot to any private Telegram group</p>
                </div>
              </div>
              <div className="text-right">
                <span className="text-xs px-2 py-1 bg-green-500/20 text-green-400 rounded border border-green-500/20">
                  Active
                </span>
              </div>
            </div>
            <div className="mt-3 text-xs text-gray-500">
              <p>1. Create a private group in Telegram</p>
              <p>2. Add <span className="text-[#229ED9]">@rugmunchbot</span> as a member</p>
              <p>3. Use commands like <code className="text-gray-300">/security &lt;token&gt;</code></p>
            </div>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-[#12121a] border border-purple-500/20 rounded-xl p-5">
              <div className="flex items-center gap-2 mb-2">
                <ScanLine className="w-4 h-4 text-purple-400" />
                <span className="text-xs text-gray-500 uppercase">Scans Used</span>
              </div>
              <div className="text-2xl font-bold text-white">{tgUser?.scans_used ?? 0}</div>
              <div className="text-xs text-gray-500 mt-1">
                {tgUser?.scans_remaining === -1 ? 'Unlimited' : `${tgUser?.scans_remaining ?? 0} remaining`}
              </div>
            </div>
            <div className="bg-[#12121a] border border-purple-500/20 rounded-xl p-5">
              <div className="flex items-center gap-2 mb-2">
                <Zap className="w-4 h-4 text-yellow-400" />
                <span className="text-xs text-gray-500 uppercase">XP</span>
              </div>
              <div className="text-2xl font-bold text-white">{tgUser?.xp ?? 0}</div>
              <div className="text-xs text-gray-500 mt-1">Level {tgUser?.level ?? 1} • {tgUser?.level_name}</div>
            </div>
            <div className="bg-[#12121a] border border-purple-500/20 rounded-xl p-5">
              <div className="flex items-center gap-2 mb-2">
                <BarChart3 className="w-4 h-4 text-blue-400" />
                <span className="text-xs text-gray-500 uppercase">Total Scans</span>
              </div>
              <div className="text-2xl font-bold text-white">{tgUser?.total_scans ?? 0}</div>
              <div className="text-xs text-gray-500 mt-1">All time</div>
            </div>
            <div className="bg-[#12121a] border border-purple-500/20 rounded-xl p-5">
              <div className="flex items-center gap-2 mb-2">
                <Trophy className="w-4 h-4 text-yellow-400" />
                <span className="text-xs text-gray-500 uppercase">Badges</span>
              </div>
              <div className="text-2xl font-bold text-white">{tgUser?.badges?.length ?? 0}</div>
              <div className="text-xs text-gray-500 mt-1">Unlocked</div>
            </div>
          </div>

          <div className="grid lg:grid-cols-2 gap-6">
            {/* Channels */}
            <div className="bg-[#12121a] border border-purple-500/20 rounded-xl overflow-hidden">
              <div className="p-4 border-b border-purple-500/20">
                <h3 className="font-semibold flex items-center gap-2">
                  <Radio className="w-5 h-5 text-purple-400" />
                  Telegram Channels
                </h3>
                <p className="text-xs text-gray-500 mt-1">Follow for real-time alerts & intel</p>
              </div>
              <div className="divide-y divide-purple-500/10">
                {CHANNELS.map((ch) => {
                  const ChIcon = ch.icon;
                  return (
                    <a
                      key={ch.id}
                      href={`https://t.me/${ch.id.replace('@', '')}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-3 p-4 hover:bg-white/5 transition-colors group"
                    >
                      <div className={`w-10 h-10 rounded-lg ${ch.bg} flex items-center justify-center`}>
                        <ChIcon className={`w-5 h-5 ${ch.color}`} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="font-medium text-sm flex items-center gap-2">
                          {ch.name}
                          <ExternalLink className="w-3 h-3 text-gray-500 opacity-0 group-hover:opacity-100 transition-opacity" />
                        </div>
                        <p className="text-xs text-gray-500 truncate">{ch.description}</p>
                      </div>
                      <ChevronRight className="w-4 h-4 text-gray-600 group-hover:text-gray-400 transition-colors" />
                    </a>
                  );
                })}
              </div>
            </div>

            {/* Bot Commands */}
            <div className="bg-[#12121a] border border-purple-500/20 rounded-xl overflow-hidden">
              <div className="p-4 border-b border-purple-500/20">
                <h3 className="font-semibold flex items-center gap-2">
                  <MessageSquare className="w-5 h-5 text-purple-400" />
                  Bot Commands
                </h3>
                <p className="text-xs text-gray-500 mt-1">DM <span className="text-purple-400">@rugmunchbot</span> on Telegram</p>
              </div>
              <div className="divide-y divide-purple-500/10 max-h-[320px] overflow-y-auto">
                {[
                  { cmd: '/start', desc: 'Get started with the bot', access: 'all' },
                  { cmd: '/scan <token>', desc: 'Full security scan', access: 'all' },
                  { cmd: '/security <token>', desc: 'Quick risk check', access: 'all' },
                  { cmd: '/audit <token>', desc: 'Deep contract audit', access: 'all' },
                  { cmd: '/wallet <address>', desc: 'Wallet portfolio analysis', access: 'all' },
                  { cmd: '/whales <token>', desc: 'Whale concentration', access: 'pro' },
                  { cmd: '/holders <token>', desc: 'Holder distribution', access: 'pro' },
                  { cmd: '/predict <token>', desc: 'AI price prediction', access: 'pro' },
                  { cmd: '/subscribe', desc: 'View tier & upgrade', access: 'all' },
                  { cmd: '/balance', desc: 'Check remaining scans', access: 'all' },
                  { cmd: '/leaderboard', desc: 'Top scanners', access: 'all' },
                  { cmd: '/help', desc: 'Show all commands', access: 'all' },
                ].map((cmd) => (
                  <div key={cmd.cmd} className="flex items-center gap-3 p-3 hover:bg-white/5 transition-colors">
                    <code className="text-xs bg-black/30 px-2 py-1 rounded text-purple-300 font-mono whitespace-nowrap">{cmd.cmd}</code>
                    <span className="text-sm text-gray-400 flex-1">{cmd.desc}</span>
                    {cmd.access === 'pro' && (
                      <span className="text-[10px] px-1.5 py-0.5 bg-purple-500/20 text-purple-400 rounded">PRO</span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Badges */}
          {tgUser?.badges && tgUser.badges.length > 0 && (
            <div className="bg-[#12121a] border border-purple-500/20 rounded-xl p-5">
              <h3 className="font-semibold flex items-center gap-2 mb-4">
                <Trophy className="w-5 h-5 text-yellow-400" />
                Your Badges
              </h3>
              <div className="flex flex-wrap gap-3">
                {tgUser.badges.map((badge) => (
                  <div
                    key={badge}
                    className="flex items-center gap-2 px-3 py-2 bg-yellow-500/10 border border-yellow-500/20 rounded-lg"
                    title={BADGE_NAMES[badge] || badge}
                  >
                    <span className="text-lg">{BADGE_ICONS[badge] || '🏅'}</span>
                    <span className="text-sm text-yellow-300">{BADGE_NAMES[badge] || badge}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* ── SCAN HISTORY TAB ── */}
      {activeTab === 'history' && (
        <div className="bg-[#12121a] border border-purple-500/20 rounded-xl overflow-hidden">
          <div className="p-4 border-b border-purple-500/20">
            <h3 className="font-semibold flex items-center gap-2">
              <Clock className="w-5 h-5 text-purple-400" />
              Recent Scans
            </h3>
          </div>
          {scans.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              <ScanLine className="w-12 h-12 mx-auto mb-3 text-gray-600" />
              <p>No scans yet. Start scanning in Telegram!</p>
              <a
                href="https://t.me/rugmunchbot"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 mt-4 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm transition-colors"
              >
                Open @rugmunchbot
                <ExternalLink className="w-4 h-4" />
              </a>
            </div>
          ) : (
            <div className="divide-y divide-purple-500/10">
              {scans.map((scan) => (
                <div key={scan.id} className="p-4 hover:bg-white/5 transition-colors">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className={`text-xs px-2 py-0.5 rounded border ${getConsensusBadge(scan.ai_consensus)}`}>
                        {scan.ai_consensus || 'UNKNOWN'}
                      </span>
                      <span className="text-xs text-gray-500 uppercase">{scan.scan_type}</span>
                    </div>
                    <span className="text-xs text-gray-500">
                      {new Date(scan.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  <div className="flex items-center gap-3">
                    <Hash className="w-4 h-4 text-gray-500" />
                    <code className="text-sm text-gray-300 font-mono truncate">{scan.token}</code>
                  </div>
                  {scan.risk_score !== undefined && (
                    <div className="flex items-center gap-2 mt-2">
                      <span className="text-xs text-gray-500">Risk Score:</span>
                      <span className={`text-sm font-bold ${getRiskColor(scan.risk_score)}`}>
                        {scan.risk_score}/100
                      </span>
                      <div className="flex-1 h-1.5 bg-gray-700 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full ${
                            scan.risk_score >= 70 ? 'bg-red-500' :
                            scan.risk_score >= 40 ? 'bg-orange-500' :
                            scan.risk_score >= 20 ? 'bg-yellow-500' :
                            'bg-green-500'
                          }`}
                          style={{ width: `${scan.risk_score}%` }}
                        />
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ── LEADERBOARD TAB ── */}
      {activeTab === 'leaderboard' && (
        <div className="bg-[#12121a] border border-purple-500/20 rounded-xl overflow-hidden">
          <div className="p-4 border-b border-purple-500/20">
            <h3 className="font-semibold flex items-center gap-2">
              <Trophy className="w-5 h-5 text-yellow-400" />
              Top Scanners
            </h3>
          </div>
          <div className="divide-y divide-purple-500/10">
            {leaderboard.map((entry, idx) => {
              const isMe = entry.telegram_id === telegramId;
              const entryTier = TIERS[entry.tier] || TIERS.free;
              return (
                <div
                  key={entry.telegram_id}
                  className={`flex items-center gap-4 p-4 transition-colors ${
                    isMe ? 'bg-purple-500/10' : 'hover:bg-white/5'
                  }`}
                >
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                    idx === 0 ? 'bg-yellow-500/20 text-yellow-400' :
                    idx === 1 ? 'bg-gray-400/20 text-gray-300' :
                    idx === 2 ? 'bg-orange-500/20 text-orange-400' :
                    'bg-gray-700/30 text-gray-500'
                  }`}>
                    {idx + 1}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-sm">{entry.first_name || entry.username || `User ${entry.telegram_id}`}</span>
                      {isMe && (
                        <span className="text-[10px] px-1.5 py-0.5 bg-purple-500/20 text-purple-400 rounded">YOU</span>
                      )}
                    </div>
                    <div className="flex items-center gap-2 text-xs text-gray-500">
                      <span>Level {entry.level}</span>
                      <span>•</span>
                      <span>{entry.xp} XP</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className={`text-xs px-2 py-0.5 rounded ${entryTier.bg} ${entryTier.color}`}>
                      {entryTier.name}
                    </span>
                    <span className="text-sm font-bold text-white">{entry.total_scans}</span>
                    <span className="text-xs text-gray-500">scans</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Payment Options */}
      {(tgUser?.tier === 'free' || tgUser?.tier === 'basic') && (
        <div className="space-y-4">
          <div className="bg-gradient-to-r from-purple-600/20 to-yellow-500/20 border border-purple-500/30 rounded-xl p-6">
            <div className="flex flex-col md:flex-row items-center justify-between gap-4">
              <div>
                <h3 className="font-semibold text-white">Upgrade Your Scan Power</h3>
                <p className="text-sm text-gray-400 mt-1">
                  Get more scans, AI predictions, and whale analysis with a Pro or Elite subscription.
                </p>
              </div>
              <button
                onClick={() => setCurrentPage('pricing')}
                className="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white font-semibold rounded-lg transition-colors flex items-center gap-2 whitespace-nowrap"
              >
                View Pricing
                <ArrowUpRight className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Pay with Stars — only inside Telegram Mini App */}
          {isInTelegram && (
            <StarsPaymentCard telegramId={telegramId} tier={tgUser?.tier || 'free'} />
          )}
        </div>
      )}

      {/* Bot Link */}
      <div className="text-center py-4">
        <a
          href="https://t.me/rugmunchbot"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 px-6 py-3 bg-[#229ED9] hover:bg-[#1a8bc2] text-white font-semibold rounded-xl transition-colors"
        >
          <Bot className="w-5 h-5" />
          Open @rugmunchbot on Telegram
          <ExternalLink className="w-4 h-4" />
        </a>
      </div>
    </div>
  );
}

// ── Stars Payment Card (Telegram Mini App only) ──
function StarsPaymentCard({ telegramId, tier }: { telegramId: number; tier: string }) {
  const [payLoading, setPayLoading] = useState(false);
  const { openInvoice, hapticFeedback } = useTelegramWebApp();

  const tiers = [
    { key: 'basic', name: 'Basic', scans: '25/mo', stars: 50, color: 'bg-blue-500/20 text-blue-400 border-blue-500/30' },
    { key: 'pro', name: 'Pro', scans: '100/mo', stars: 150, color: 'bg-purple-500/20 text-purple-400 border-purple-500/30' },
    { key: 'elite', name: 'Elite', scans: 'Unlimited', stars: 400, color: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30' },
  ];

  const handlePay = async (tierKey: string, stars: number) => {
    setPayLoading(true);
    try {
      hapticFeedback?.impactOccurred('light');
      const result = await createStarsInvoice(
        telegramId,
        `Rug Munch ${tierKey.charAt(0).toUpperCase() + tierKey.slice(1)}`,
        `${tierKey === 'elite' ? 'Unlimited' : tiers.find((t) => t.key === tierKey)?.scans} scans per month`,
        `tier:${tierKey}:${telegramId}`,
        stars
      );
      if (result.success && result.invoice_url && openInvoice) {
        openInvoice(result.invoice_url, (status) => {
          if (status === 'paid') {
            hapticFeedback?.notificationOccurred('success');
          }
        });
      }
    } catch (e) {
      console.error('Stars payment failed:', e);
    } finally {
      setPayLoading(false);
    }
  };

  return (
    <div className="bg-[#12121a] border border-[#229ED9]/30 rounded-xl p-5">
      <div className="flex items-center gap-2 mb-4">
        <Star className="w-5 h-5 text-yellow-400" />
        <h3 className="font-semibold text-white">Pay with Telegram Stars</h3>
        <span className="text-[10px] px-1.5 py-0.5 bg-[#229ED9]/20 text-[#229ED9] rounded">MINI APP</span>
      </div>
      <div className="grid grid-cols-3 gap-3">
        {tiers
          .filter((t) => t.key !== tier)
          .map((t) => (
            <button
              key={t.key}
              onClick={() => handlePay(t.key, t.stars)}
              disabled={payLoading}
              className={`p-3 rounded-lg border transition-all hover:scale-105 ${t.color}`}
            >
              <div className="font-bold text-sm">{t.name}</div>
              <div className="text-xs opacity-80">{t.scans}</div>
              <div className="text-xs font-bold mt-1">{t.stars} ⭐</div>
            </button>
          ))}
      </div>
    </div>
  );
}
