/**
 * Gamification Profile Dashboard
 * ==============================
 * Shows XP, level, badges, stats, and leaderboard.
 */
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Trophy,
  Flame,
  Zap,
  Target,
  MessageSquare,
  Search,
  Shield,
  TrendingUp,
  Award,
  Crown,
  Star,
  Lock,
  ChevronRight,
} from 'lucide-react';
import { useAppStore } from '../store/appStore';
import api from '../services/api';

interface Badge {
  badge_id: string;
  name: string;
  emoji: string;
  description: string;
  rarity: 'common' | 'uncommon' | 'rare' | 'epic' | 'legendary' | 'mythic' | 'special';
  earned: boolean;
  progress: {
    current: number;
    target: number;
    percentage: number;
  };
}

interface GamificationData {
  stats: {
    post_count: number;
    comment_count: number;
    scan_count: number;
    upvote_received: number;
    upvote_given: number;
    total_xp: number;
  };
  level: {
    level: number;
    title: string;
    xp: number;
    next_level_xp: number;
    progress_percent: number;
  };
  badges: Badge[];
  streak: {
    current: number;
    longest: number;
  };
}

const RARITY_COLORS: Record<string, string> = {
  common: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
  uncommon: 'bg-green-500/20 text-green-400 border-green-500/30',
  rare: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  epic: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
  legendary: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  mythic: 'bg-red-500/20 text-red-400 border-red-500/30',
  special: 'bg-pink-500/20 text-pink-400 border-pink-500/30',
};

const RARITY_GLOW: Record<string, string> = {
  common: '',
  uncommon: 'shadow-green-500/10',
  rare: 'shadow-blue-500/10',
  epic: 'shadow-purple-500/10',
  legendary: 'shadow-yellow-500/20',
  mythic: 'shadow-red-500/20',
  special: 'shadow-pink-500/10',
};

export default function GamificationProfile() {
  const user = useAppStore((state) => state.user);
  const [activeTab, setActiveTab] = useState<'overview' | 'badges' | 'leaderboard'>('overview');

  const { data, isLoading } = useQuery<GamificationData>({
    queryKey: ['gamification', user?.id],
    queryFn: async () => {
      return await api.getGamificationProfile();
    },
    enabled: !!user,
    refetchInterval: 30000,
  });

  const { data: leaderboardData } = useQuery({
    queryKey: ['leaderboard', 'xp'],
    queryFn: async () => {
      return await api.getLeaderboard('xp', 10);
    },
    enabled: activeTab === 'leaderboard',
  });

  if (isLoading || !data) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500" />
      </div>
    );
  }

  const { stats, level, badges, streak } = data;
  const earnedBadges = badges.filter((b) => b.earned);
  const inProgressBadges = badges.filter((b) => !b.earned && b.progress.percentage > 0);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white">Agent Profile</h1>
        <p className="text-gray-400">Your reputation, achievements, and standing</p>
      </div>

      {/* XP & Level Card */}
      <div className="bg-gradient-to-br from-purple-900/20 to-blue-900/20 border border-purple-500/20 rounded-xl p-6">
        <div className="flex items-center gap-6">
          <div className="w-20 h-20 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center text-3xl shadow-lg shadow-purple-500/20">
            <Crown className="w-10 h-10 text-white" />
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <span className="text-2xl font-bold text-white">{level.title}</span>
              <span className="px-2 py-1 bg-purple-500/20 text-purple-400 text-sm rounded-full font-medium">
                Lv. {level.level}
              </span>
            </div>
            <div className="flex items-center gap-2 text-gray-400 text-sm mb-3">
              <Zap className="w-4 h-4 text-yellow-400" />
              <span>{level.xp.toLocaleString()} XP</span>
              <span>•</span>
              <span>{level.next_level_xp.toLocaleString()} to next level</span>
            </div>
            <div className="h-3 bg-gray-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-purple-500 to-blue-500 rounded-full transition-all duration-500"
                style={{ width: `${level.progress_percent}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard icon={Search} label="Scans" value={stats.scan_count} color="text-blue-400" />
        <StatCard icon={MessageSquare} label="Posts" value={stats.post_count} color="text-green-400" />
        <StatCard icon={Target} label="Comments" value={stats.comment_count} color="text-purple-400" />
        <StatCard icon={Flame} label="Streak" value={streak.current} suffix="days" color="text-orange-400" />
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-gray-800 pb-1">
        {(['overview', 'badges', 'leaderboard'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors ${
              activeTab === tab
                ? 'text-purple-400 border-b-2 border-purple-500'
                : 'text-gray-500 hover:text-gray-300'
            }`}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <div className="space-y-4">
          {/* Recent Badges */}
          {earnedBadges.length > 0 && (
            <div className="bg-[#12121a] border border-gray-800 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Award className="w-5 h-5 text-yellow-400" />
                Recent Badges
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {earnedBadges.slice(0, 6).map((badge) => (
                  <BadgeCard key={badge.badge_id} badge={badge} />
                ))}
              </div>
            </div>
          )}

          {/* In Progress */}
          {inProgressBadges.length > 0 && (
            <div className="bg-[#12121a] border border-gray-800 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-blue-400" />
                In Progress
              </h3>
              <div className="space-y-3">
                {inProgressBadges.slice(0, 5).map((badge) => (
                  <ProgressBadgeRow key={badge.badge_id} badge={badge} />
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {activeTab === 'badges' && (
        <div className="bg-[#12121a] border border-gray-800 rounded-xl p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white flex items-center gap-2">
              <Shield className="w-5 h-5 text-purple-400" />
              All Badges
            </h3>
            <span className="text-sm text-gray-500">
              {earnedBadges.length} / {badges.length} unlocked
            </span>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
            {badges.map((badge) => (
              <BadgeCard key={badge.badge_id} badge={badge} />
            ))}
          </div>
        </div>
      )}

      {activeTab === 'leaderboard' && (
        <div className="bg-[#12121a] border border-gray-800 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <Trophy className="w-5 h-5 text-yellow-400" />
            Global Leaderboard
          </h3>
          <div className="space-y-2">
            {leaderboardData?.leaderboard?.map((entry: any, idx: number) => (
              <div
                key={entry.user_id}
                className={`flex items-center gap-4 p-3 rounded-lg ${
                  entry.user_id === user?.id ? 'bg-purple-500/10 border border-purple-500/20' : 'bg-gray-800/30'
                }`}
              >
                <div className="w-8 text-center font-bold text-gray-500">
                  {idx === 0 ? '🥇' : idx === 1 ? '🥈' : idx === 2 ? '🥉' : `#${idx + 1}`}
                </div>
                <div className="flex-1">
                  <div className="text-white font-medium">
                    {entry.user_id.slice(0, 8)}...
                    {entry.user_id === user?.id && (
                      <span className="ml-2 text-xs text-purple-400">You</span>
                    )}
                  </div>
                  <div className="text-xs text-gray-500">
                    {entry.level?.title} • Lv. {entry.level?.level}
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-white font-bold">{entry.score.toLocaleString()} XP</div>
                </div>
              </div>
            )) || (
              <div className="text-gray-500 text-center py-8">Leaderboard loading...</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function StatCard({ icon: Icon, label, value, suffix = '', color }: {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  value: number;
  suffix?: string;
  color: string;
}) {
  return (
    <div className="bg-[#12121a] border border-gray-800 rounded-xl p-4">
      <div className="flex items-center gap-2 mb-2">
        <Icon className={`w-4 h-4 ${color}`} />
        <span className="text-sm text-gray-500">{label}</span>
      </div>
      <div className="text-2xl font-bold text-white">
        {value}
        {suffix && <span className="text-sm text-gray-500 ml-1">{suffix}</span>}
      </div>
    </div>
  );
}

function BadgeCard({ badge }: { badge: Badge }) {
  const colorClass = RARITY_COLORS[badge.rarity] || RARITY_COLORS.common;
  const glowClass = RARITY_GLOW[badge.rarity] || '';

  return (
    <div
      className={`relative p-4 rounded-xl border ${
        badge.earned
          ? `${colorClass} ${glowClass} shadow-lg`
          : 'bg-gray-800/30 border-gray-700/50 opacity-60'
      } transition-all hover:scale-105`}
    >
      {!badge.earned && (
        <div className="absolute top-2 right-2">
          <Lock className="w-3 h-3 text-gray-600" />
        </div>
      )}
      <div className="text-3xl mb-2">{badge.earned ? badge.emoji : '🔒'}</div>
      <div className="font-semibold text-white text-sm">{badge.name}</div>
      <div className="text-xs text-gray-500 mt-1 line-clamp-2">{badge.description}</div>
      <div className={`mt-2 inline-block px-2 py-0.5 rounded text-xs ${colorClass}`}>
        {badge.rarity}
      </div>
      {!badge.earned && badge.progress.percentage > 0 && (
        <div className="mt-2">
          <div className="h-1 bg-gray-700 rounded-full overflow-hidden">
            <div
              className="h-full bg-gray-500 rounded-full"
              style={{ width: `${badge.progress.percentage}%` }}
            />
          </div>
          <div className="text-xs text-gray-600 mt-1">
            {badge.progress.current} / {badge.progress.target}
          </div>
        </div>
      )}
    </div>
  );
}

function ProgressBadgeRow({ badge }: { badge: Badge }) {
  const colorClass = RARITY_COLORS[badge.rarity] || RARITY_COLORS.common;

  return (
    <div className="flex items-center gap-4 p-3 bg-gray-800/30 rounded-lg">
      <div className="text-2xl">{badge.emoji}</div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="font-medium text-white text-sm">{badge.name}</span>
          <span className={`px-1.5 py-0.5 rounded text-xs ${colorClass}`}>{badge.rarity}</span>
        </div>
        <div className="text-xs text-gray-500">{badge.description}</div>
        <div className="mt-1.5">
          <div className="h-1.5 bg-gray-700 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-purple-500 to-blue-500 rounded-full transition-all"
              style={{ width: `${badge.progress.percentage}%` }}
            />
          </div>
        </div>
      </div>
      <div className="text-right">
        <div className="text-sm font-bold text-white">{badge.progress.percentage}%</div>
        <div className="text-xs text-gray-500">
          {badge.progress.current}/{badge.progress.target}
        </div>
      </div>
      <ChevronRight className="w-4 h-4 text-gray-600" />
    </div>
  );
}
