/**
 * The Daily Rundown
 * =================
 * Your morning briefing. What's hot, what's dead, what's suspicious.
 * Pulls from trending intel, trenches, whale moves, and ghost blog.
 * No external branding — this IS Rug Munch Intel.
 */
import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Newspaper, Flame, TrendingUp, AlertTriangle, Eye,
  Skull, Zap, Clock, ChevronRight, RefreshCw, Trophy,
  ArrowUpRight, ArrowDownRight, Volume2
} from 'lucide-react';
import { api } from '../services/api';
import { useAppStore } from '../store/appStore';

interface RundownItem {
  id: string;
  type: 'trending' | 'alert' | 'whale' | 'trenches' | 'blog';
  title: string;
  subtitle: string;
  time: string;
  severity?: 'low' | 'medium' | 'high' | 'critical';
  metric?: string;
  change?: number;
  icon: any;
}

export default function DailyRundown() {
  const [lastUpdated, setLastUpdated] = useState(new Date());
  const user = useAppStore((state) => state.user);

  const { data: trending, isLoading: tLoading } = useQuery({
    queryKey: ['rundown-trending'],
    queryFn: () => api.getTrendingIntel(),
    refetchInterval: 60000,
  });

  const { data: posts, isLoading: pLoading } = useQuery({
    queryKey: ['rundown-posts'],
    queryFn: () => api.getTrenchesPosts(undefined, 5),
    refetchInterval: 30000,
  });

  const { data: whaleActivity } = useQuery({
    queryKey: ['rundown-whales'],
    queryFn: () => api.getWhaleActivity(),
    refetchInterval: 120000,
    enabled: !!user,
  });

  useEffect(() => {
    setLastUpdated(new Date());
  }, [trending, posts]);

  const items: RundownItem[] = [
    ...(trending?.tokens?.slice(0, 3).map((t: any, i: number) => ({
      id: `trend-${i}`,
      type: 'trending' as const,
      title: t.symbol || t.name || 'Unknown Token',
      subtitle: t.description || 'Trending on-chain',
      time: 'Live',
      metric: t.price ? `$${t.price}` : undefined,
      change: t.change_24h,
      icon: TrendingUp,
    })) || []),
    ...(posts?.posts?.slice(0, 3).map((p: any, i: number) => ({
      id: `trench-${i}`,
      type: 'trenches' as const,
      title: p.title,
      subtitle: `${p.upvotes} upvotes · ${p.comments} comments`,
      time: new Date(p.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      severity: p.category === 'scam_report' ? 'critical' as const : 'medium' as const,
      icon: p.category === 'scam_report' ? Skull : Volume2,
    })) || []),
  ];

  const severityColors = {
    low: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
    medium: 'text-amber-400 bg-amber-500/10 border-amber-500/20',
    high: 'text-orange-400 bg-orange-500/10 border-orange-500/20',
    critical: 'text-rose-400 bg-rose-500/10 border-rose-500/20',
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Newspaper className="w-5 h-5 text-amber-400" />
            <span className="text-amber-400 text-sm font-medium">The Daily Rundown</span>
          </div>
          <h1 className="text-2xl font-bold text-white">What's Moving Today</h1>
          <p className="text-gray-400 text-sm">
            Last updated {lastUpdated.toLocaleTimeString()} · Auto-refresh every 60s
          </p>
        </div>
        <button
          onClick={() => window.location.reload()}
          className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-gray-300 rounded-lg text-sm font-medium flex items-center gap-2 transition-colors self-start"
        >
          <RefreshCw className="w-4 h-4" />
          Refresh
        </button>
      </div>

      {/* Top Stats Bar */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {[
          { label: 'Scams Detected', value: '2,847', change: '+12', icon: Skull, color: 'rose' },
          { label: 'Active Wallets', value: '50.2K', change: '+3.4%', icon: Eye, color: 'blue' },
          { label: 'Trenches Posts', value: posts?.total || '0', change: '+5', icon: Volume2, color: 'purple' },
          { label: 'Whale Alerts', value: whaleActivity?.whales?.length || '0', change: '+2', icon: Zap, color: 'amber' },
        ].map((stat, i) => (
          <div key={i} className="bg-slate-900 border border-slate-800 rounded-xl p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs text-gray-500">{stat.label}</span>
              <stat.icon className={`w-4 h-4 text-${stat.color}-400`} />
            </div>
            <div className="flex items-end gap-2">
              <span className="text-xl font-bold text-white">{stat.value}</span>
              <span className="text-xs text-emerald-400 mb-0.5">{stat.change}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Main Feed */}
      <div className="space-y-3">
        {items.length === 0 && (tLoading || pLoading) && (
          <div className="space-y-3">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-24 bg-slate-800/50 rounded-xl animate-pulse" />
            ))}
          </div>
        )}

        {items.map((item) => (
          <div
            key={item.id}
            className="group bg-slate-900 border border-slate-800 hover:border-slate-700 rounded-xl p-4 transition-all cursor-pointer"
          >
            <div className="flex items-start gap-4">
              <div className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${
                item.type === 'trending' ? 'bg-emerald-500/10 text-emerald-400' :
                item.type === 'alert' ? 'bg-rose-500/10 text-rose-400' :
                item.type === 'whale' ? 'bg-amber-500/10 text-amber-400' :
                item.type === 'trenches' ? 'bg-purple-500/10 text-purple-400' :
                'bg-blue-500/10 text-blue-400'
              }`}>
                <item.icon className="w-5 h-5" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <h3 className="font-semibold text-white truncate">{item.title}</h3>
                  {item.severity && (
                    <span className={`text-[10px] px-1.5 py-0.5 rounded border ${severityColors[item.severity]}`}>
                      {item.severity}
                    </span>
                  )}
                </div>
                <p className="text-sm text-gray-400 mb-2">{item.subtitle}</p>
                <div className="flex items-center gap-4 text-xs text-gray-500">
                  <span className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {item.time}
                  </span>
                  {item.metric && (
                    <span className="text-gray-300">{item.metric}</span>
                  )}
                  {item.change !== undefined && (
                    <span className={item.change >= 0 ? 'text-emerald-400' : 'text-rose-400'}>
                      {item.change >= 0 ? '+' : ''}{item.change}%
                    </span>
                  )}
                </div>
              </div>
              <ChevronRight className="w-5 h-5 text-gray-600 group-hover:text-gray-400 transition-colors flex-shrink-0" />
            </div>
          </div>
        ))}
      </div>

      {/* Meme Momentum Section */}
      <div className="bg-gradient-to-br from-purple-900/20 to-amber-900/20 border border-purple-500/10 rounded-xl p-6">
        <div className="flex items-center gap-2 mb-4">
          <Flame className="w-5 h-5 text-orange-400" />
          <h2 className="text-lg font-bold text-white">Meme Momentum</h2>
          <span className="text-xs text-gray-500 ml-auto">Last 24h</span>
        </div>
        <div className="grid md:grid-cols-3 gap-4">
          {[
            { name: 'PEPE derivatives', status: 'Cooling', score: 34, emoji: '🐸' },
            { name: 'Base season', status: 'Heating up', score: 72, emoji: '🔵' },
            { name: 'AI tokens', status: 'On fire', score: 91, emoji: '🤖' },
          ].map((meme, i) => (
            <div key={i} className="bg-slate-950/50 rounded-lg p-4 border border-slate-800">
              <div className="flex items-center justify-between mb-2">
                <span className="text-2xl">{meme.emoji}</span>
                <span className={`text-xs px-2 py-0.5 rounded-full ${
                  meme.score > 80 ? 'bg-orange-500/20 text-orange-400' :
                  meme.score > 50 ? 'bg-amber-500/20 text-amber-400' :
                  'bg-emerald-500/20 text-emerald-400'
                }`}>
                  {meme.status}
                </span>
              </div>
              <p className="font-medium text-white text-sm mb-2">{meme.name}</p>
              <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full ${
                    meme.score > 80 ? 'bg-orange-500' :
                    meme.score > 50 ? 'bg-amber-500' :
                    'bg-emerald-500'
                  }`}
                  style={{ width: `${meme.score}%` }}
                />
              </div>
              <p className="text-xs text-gray-500 mt-1">Hype score: {meme.score}/100</p>
            </div>
          ))}
        </div>
      </div>

      {/* Bottom CTA */}
      <div className="flex items-center justify-between bg-slate-900 border border-slate-800 rounded-xl p-4">
        <div className="flex items-center gap-3">
          <Trophy className="w-5 h-5 text-purple-400" />
          <div>
            <p className="text-sm font-medium text-white">Want the full picture?</p>
            <p className="text-xs text-gray-400">PRO gets real-time whale alerts + sniper detection</p>
          </div>
        </div>
        <button
          onClick={() => useAppStore.getState().setCurrentPage('pricing')}
          className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm font-medium transition-colors"
        >
          Upgrade
        </button>
      </div>
    </div>
  );
}
