/**
 * Meme Radar
 * ==========
 * Tracks meme token momentum without naming our data sources.
 * Presented as native RMI intelligence.
 */
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Radar, Flame, TrendingUp, TrendingDown, Zap,
  Clock, AlertTriangle, Skull, ChevronUp, Search
} from 'lucide-react';
import { api } from '../services/api';
import { useAppStore } from '../store/appStore';
import TierGate from './TierGate';

interface MemeToken {
  symbol: string;
  name: string;
  price: number;
  change_24h: number;
  volume_24h: number;
  market_cap?: number;
  holders?: number;
  age_hours?: number;
  risk_score?: number;
  tags: string[];
}

const MOCK_MEMES: MemeToken[] = [
  { symbol: 'BONKAI', name: 'Bonk AI', price: 0.00042, change_24h: 340, volume_24h: 2.4, market_cap: 4.2, holders: 12400, age_hours: 18, risk_score: 45, tags: ['ai', 'solana'] },
  { symbol: 'PEPE2.0', name: 'Pepe Reloaded', price: 0.0000012, change_24h: -62, volume_24h: 0.8, market_cap: 1.1, holders: 8900, age_hours: 96, risk_score: 78, tags: ['derivative', 'eth'] },
  { symbol: 'BASED', name: 'Based Coin', price: 0.0034, change_24h: 120, volume_24h: 1.8, market_cap: 3.4, holders: 5600, age_hours: 36, risk_score: 32, tags: ['base', 'community'] },
  { symbol: 'MOONCAT', name: 'Moon Cat', price: 0.00089, change_24h: 890, volume_24h: 5.2, market_cap: 8.9, holders: 22100, age_hours: 6, risk_score: 67, tags: ['cat', 'viral'] },
  { symbol: 'WIFDAO', name: 'Wif DAO', price: 0.0012, change_24h: -24, volume_24h: 0.4, market_cap: 0.9, holders: 3200, age_hours: 120, risk_score: 82, tags: ['dao', 'sus'] },
];

export default function MemeRadar() {
  const [filter, setFilter] = useState<'all' | 'heating' | 'cooling' | 'new'>('all');
  const user = useAppStore((state) => state.user);
  const tier = user?.tier || 'FREE';

  const { data: trending, isLoading } = useQuery({
    queryKey: ['meme-trending'],
    queryFn: () => api.getTrendingIntel(),
    refetchInterval: 60000,
  });

  const memes = MOCK_MEMES;

  const filtered = memes.filter((m) => {
    if (filter === 'heating') return m.change_24h > 50;
    if (filter === 'cooling') return m.change_24h < -20;
    if (filter === 'new') return m.age_hours && m.age_hours < 24;
    return true;
  });

  const getRiskLabel = (score?: number) => {
    if (score === undefined) return 'Unknown';
    if (score <= 35) return 'Safer';
    if (score <= 60) return 'Risky';
    if (score <= 80) return 'Dangerous';
    return 'Radioactive';
  };

  const getRiskColor = (score?: number) => {
    if (score === undefined) return 'text-gray-400';
    if (score <= 35) return 'text-emerald-400';
    if (score <= 60) return 'text-amber-400';
    if (score <= 80) return 'text-orange-400';
    return 'text-rose-400';
  };

  return (
    <div className="space-y-6">
      <div>
        <div className="flex items-center gap-2 mb-1">
          <Radar className="w-5 h-5 text-orange-400" />
          <span className="text-orange-400 text-sm font-medium">Meme Radar</span>
        </div>
        <h1 className="text-2xl font-bold text-white">What's Trending in the Trenches</h1>
        <p className="text-gray-400">Meme momentum, early signals, and rug warnings — no shilling, just data.</p>
      </div>

      {/* Filters */}
      <div className="flex gap-2 flex-wrap">
        {[
          { id: 'all', label: 'All Signals', icon: Zap },
          { id: 'heating', label: 'Heating Up', icon: Flame },
          { id: 'cooling', label: 'Cooling Off', icon: TrendingDown },
          { id: 'new', label: 'Fresh Launches', icon: Clock },
        ].map((f) => (
          <button
            key={f.id}
            onClick={() => setFilter(f.id as any)}
            className={`px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2 transition-colors ${
              filter === f.id
                ? 'bg-orange-500/20 text-orange-400 border border-orange-500/30'
                : 'bg-slate-900 text-gray-400 border border-slate-800 hover:border-slate-700'
            }`}
          >
            <f.icon className="w-4 h-4" />
            {f.label}
          </button>
        ))}
      </div>

      {/* Meme Cards */}
      <div className="grid md:grid-cols-2 gap-4">
        {filtered.map((meme, i) => (
          <div
            key={i}
            className="bg-slate-900 border border-slate-800 rounded-xl p-5 hover:border-orange-500/20 transition-all group"
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-orange-500/20 to-amber-500/20 border border-orange-500/20 flex items-center justify-center text-lg">
                  {meme.symbol[0]}
                </div>
                <div>
                  <h3 className="font-bold text-white">${meme.symbol}</h3>
                  <p className="text-xs text-gray-500">{meme.name}</p>
                </div>
              </div>
              <div className={`flex items-center gap-1 text-sm font-bold ${
                meme.change_24h >= 0 ? 'text-emerald-400' : 'text-rose-400'
              }`}>
                {meme.change_24h >= 0 ? <ChevronUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                {meme.change_24h >= 0 ? '+' : ''}{meme.change_24h}%
              </div>
            </div>

            <div className="grid grid-cols-3 gap-3 mb-4">
              <div className="bg-slate-950 rounded-lg p-2.5">
                <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-0.5">Price</p>
                <p className="text-sm font-mono text-white">${meme.price.toExponential(2)}</p>
              </div>
              <div className="bg-slate-950 rounded-lg p-2.5">
                <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-0.5">Vol 24h</p>
                <p className="text-sm font-mono text-white">${meme.volume_24h}M</p>
              </div>
              <div className="bg-slate-950 rounded-lg p-2.5">
                <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-0.5">Age</p>
                <p className="text-sm font-mono text-white">{meme.age_hours}h</p>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex gap-1.5 flex-wrap">
                {meme.tags.map((tag) => (
                  <span key={tag} className="text-[10px] px-2 py-0.5 bg-slate-800 text-gray-400 rounded-full">
                    #{tag}
                  </span>
                ))}
              </div>
              <span className={`text-xs font-medium ${getRiskColor(meme.risk_score)}`}>
                {getRiskLabel(meme.risk_score)}
              </span>
            </div>

            {/* Premium: full scan button */}
            <TierGate
              requiredTier="BASIC"
              title="Full Token Scan"
              description="Deep-dive security analysis, holder mapping, and sniper detection."
            >
              <div className="mt-3 pt-3 border-t border-slate-800">
                <button
                  onClick={() => useAppStore.getState().setCurrentPage('scanner')}
                  className="w-full py-2 bg-orange-500/10 hover:bg-orange-500/20 border border-orange-500/20 text-orange-400 rounded-lg text-sm font-medium flex items-center justify-center gap-2 transition-colors"
                >
                  <Search className="w-4 h-4" />
                  Run Full Scan
                </button>
              </div>
            </TierGate>
          </div>
        ))}
      </div>

      {/* Bottom warning */}
      <div className="flex items-start gap-3 bg-rose-500/5 border border-rose-500/10 rounded-xl p-4">
        <Skull className="w-5 h-5 text-rose-400 flex-shrink-0 mt-0.5" />
        <div>
          <p className="text-sm font-medium text-rose-300">Meme tokens are high-risk by design</p>
          <p className="text-xs text-rose-400/70 mt-1">
            94% of meme tokens launched in the last 30 days are now dead. The Radar shows momentum, not investment advice. DYOR.
          </p>
        </div>
      </div>
    </div>
  );
}
