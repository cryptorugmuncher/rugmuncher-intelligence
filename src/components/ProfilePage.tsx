/**
 * Profile Page
 * Full profile view/edit with tabs: Overview, Scans, Badges, Settings
 */
import { useState, useEffect } from 'react';
import { useAppStore } from '../store/appStore';
import { api } from '../services/api';
import {
  User, Shield, Award, ScanLine, Settings, Edit2, Check, X,
  Copy, ExternalLink, Wallet, Mail, MessageCircle, Globe, AtSign
} from 'lucide-react';

interface ProfileData {
  id: string;
  username?: string;
  display_name?: string;
  bio?: string;
  avatar_url?: string;
  telegram_handle?: string;
  wallet_address?: string;
  chain_preference?: string;
  tier?: string;
  role?: string;
  xp?: number;
  level?: number;
  scans_remaining?: number;
  total_scans_used?: number;
  reputation_score?: number;
  onboarding_completed?: boolean;
  created_at?: string;
}

interface Badge {
  id: string;
  badge_type: string;
  badge_name: string;
  awarded_at: string;
}

interface ScanItem {
  id: string;
  contract_address: string;
  chain: string;
  risk_score: number;
  verdict: string;
  scanned_at: string;
}

export default function ProfilePage() {
  const { user, isAuthenticated } = useAppStore();
  const [profile, setProfile] = useState<ProfileData | null>(null);
  const [badges, setBadges] = useState<Badge[]>([]);
  const [scans, setScans] = useState<ScanItem[]>([]);
  const [activeTab, setActiveTab] = useState<'overview' | 'scans' | 'badges' | 'settings'>('overview');
  const [loading, setLoading] = useState(true);
  const [editMode, setEditMode] = useState(false);
  const [form, setForm] = useState<Partial<ProfileData>>({});
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    if (!isAuthenticated) return;
    loadProfile();
  }, [isAuthenticated]);

  const loadProfile = async () => {
    setLoading(true);
    try {
      const res = await api.client.get('/me');
      setProfile(res.data);
      setForm(res.data);
    } catch (e) {
      console.error('Failed to load profile', e);
    }
    try {
      const b = await api.client.get('/me/badges');
      setBadges(b.data || []);
    } catch {}
    try {
      const s = await api.client.get('/me/scans');
      setScans(s.data?.items || []);
    } catch {}
    setLoading(false);
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const res = await api.client.put('/me', form);
      setProfile(res.data);
      setEditMode(false);
      setMessage('Profile updated');
      setTimeout(() => setMessage(''), 2000);
    } catch (e: any) {
      setMessage(e.response?.data?.detail || 'Update failed');
    }
    setSaving(false);
  };

  const copyWallet = () => {
    if (profile?.wallet_address) {
      navigator.clipboard.writeText(profile.wallet_address);
      setMessage('Wallet copied');
      setTimeout(() => setMessage(''), 1500);
    }
  };

  const avatarSrc = profile?.avatar_url || '';

  if (!isAuthenticated) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <User size={48} className="mx-auto text-gray-600 mb-4" />
          <h2 className="text-xl font-semibold text-white mb-2">Sign In Required</h2>
          <p className="text-gray-400 mb-4">Connect your wallet or sign in to view your profile.</p>
          <button
            onClick={() => useAppStore.getState().setCurrentPage('login')}
            className="px-6 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium"
          >
            Sign In
          </button>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500" />
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto">
      {/* Header Card */}
      <div className="bg-[#12121a] border border-purple-500/20 rounded-xl p-6 mb-6">
        <div className="flex items-start gap-6">
          <div className="relative">
            <div className="w-24 h-24 rounded-xl bg-gradient-to-br from-purple-600 to-blue-600 flex items-center justify-center overflow-hidden">
              {avatarSrc ? (
                <img src={avatarSrc} alt="avatar" className="w-full h-full object-cover" />
              ) : (
                <User size={40} className="text-white" />
              )}
            </div>
            <div className="absolute -bottom-2 -right-2 px-2 py-0.5 bg-purple-600 text-white text-xs rounded-full font-bold">
              LVL {profile?.level || 1}
            </div>
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-3 mb-1">
              <h1 className="text-2xl font-bold text-white truncate">
                {profile?.display_name || profile?.username || 'Agent'}
              </h1>
              <span className={`px-2 py-0.5 rounded text-xs font-semibold uppercase ${
                profile?.tier === 'institutional' ? 'bg-amber-500/20 text-amber-400' :
                profile?.tier === 'member' ? 'bg-purple-500/20 text-purple-400' :
                'bg-gray-500/20 text-gray-400'
              }`}>
                {profile?.tier || 'free'}
              </span>
            </div>
            <p className="text-gray-400 text-sm mb-3">@{profile?.username || 'unknown'}</p>
            <p className="text-gray-300 text-sm max-w-2xl">{profile?.bio || 'No bio yet.'}</p>

            <div className="flex flex-wrap gap-3 mt-4">
              {profile?.wallet_address && (
                <button onClick={copyWallet} className="flex items-center gap-2 px-3 py-1.5 bg-[#0a0a0f] border border-purple-500/20 rounded-lg text-sm text-gray-300 hover:border-purple-500/40">
                  <Wallet size={14} className="text-purple-400" />
                  <span className="font-mono">{profile.wallet_address.slice(0, 6)}...{profile.wallet_address.slice(-4)}</span>
                  <Copy size={12} />
                </button>
              )}
              {profile?.telegram_handle && (
                <div className="flex items-center gap-2 px-3 py-1.5 bg-[#0a0a0f] border border-purple-500/20 rounded-lg text-sm text-gray-300">
                  <MessageCircle size={14} className="text-blue-400" />
                  @{profile.telegram_handle}
                </div>
              )}
              <div className="flex items-center gap-2 px-3 py-1.5 bg-[#0a0a0f] border border-purple-500/20 rounded-lg text-sm text-gray-300">
                <Shield size={14} className="text-green-400" />
                Rep: {profile?.reputation_score || 0}
              </div>
            </div>
          </div>
          <button
            onClick={() => setEditMode(!editMode)}
            className="flex items-center gap-2 px-4 py-2 bg-purple-600/20 hover:bg-purple-600/30 text-purple-400 rounded-lg text-sm font-medium transition-colors"
          >
            {editMode ? <X size={16} /> : <Edit2 size={16} />}
            {editMode ? 'Cancel' : 'Edit'}
          </button>
        </div>

        {message && (
          <div className="mt-4 px-4 py-2 bg-green-500/10 border border-green-500/30 text-green-400 rounded-lg text-sm">
            {message}
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6 border-b border-purple-500/10 pb-1">
        {(['overview', 'scans', 'badges', 'settings'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors ${
              activeTab === tab
                ? 'text-purple-400 border-b-2 border-purple-500 bg-purple-500/5'
                : 'text-gray-400 hover:text-gray-200 hover:bg-white/5'
            }`}
          >
            {tab === 'overview' && <span className="flex items-center gap-2"><User size={14} /> Overview</span>}
            {tab === 'scans' && <span className="flex items-center gap-2"><ScanLine size={14} /> Scans</span>}
            {tab === 'badges' && <span className="flex items-center gap-2"><Award size={14} /> Badges</span>}
            {tab === 'settings' && <span className="flex items-center gap-2"><Settings size={14} /> Settings</span>}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-[#12121a] border border-purple-500/20 rounded-xl p-6">
            <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Stats</h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-gray-400 text-sm">Total Scans</span>
                <span className="text-white font-bold">{profile?.total_scans_used || 0}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-400 text-sm">Scans Remaining</span>
                <span className="text-white font-bold">{profile?.scans_remaining || 0}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-400 text-sm">XP</span>
                <span className="text-white font-bold">{profile?.xp || 0}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-400 text-sm">Level</span>
                <span className="text-white font-bold">{profile?.level || 1}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-400 text-sm">Badges</span>
                <span className="text-white font-bold">{badges.length}</span>
              </div>
            </div>
          </div>

          <div className="md:col-span-2 bg-[#12121a] border border-purple-500/20 rounded-xl p-6">
            <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Recent Scans</h3>
            {scans.length === 0 ? (
              <p className="text-gray-500 text-sm">No scans yet. Start scanning to see history.</p>
            ) : (
              <div className="space-y-3">
                {scans.slice(0, 5).map((scan) => (
                  <div key={scan.id} className="flex items-center justify-between p-3 bg-[#0a0a0f] rounded-lg border border-purple-500/10">
                    <div>
                      <p className="text-sm font-mono text-white">{scan.contract_address.slice(0, 8)}...{scan.contract_address.slice(-6)}</p>
                      <p className="text-xs text-gray-500">{scan.chain} • {new Date(scan.scanned_at).toLocaleDateString()}</p>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className={`px-2 py-0.5 rounded text-xs font-bold ${
                        scan.risk_score > 75 ? 'bg-red-500/20 text-red-400' :
                        scan.risk_score > 40 ? 'bg-amber-500/20 text-amber-400' :
                        'bg-green-500/20 text-green-400'
                      }`}>
                        {scan.risk_score}/100
                      </span>
                      <span className="text-xs text-gray-400">{scan.verdict}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === 'scans' && (
        <div className="bg-[#12121a] border border-purple-500/20 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Scan History</h3>
          {scans.length === 0 ? (
            <p className="text-gray-500">No scans yet.</p>
          ) : (
            <div className="space-y-3">
              {scans.map((scan) => (
                <div key={scan.id} className="flex items-center justify-between p-4 bg-[#0a0a0f] rounded-lg border border-purple-500/10">
                  <div>
                    <p className="text-sm font-mono text-white">{scan.contract_address}</p>
                    <p className="text-xs text-gray-500 mt-1">{scan.chain} • {new Date(scan.scanned_at).toLocaleString()}</p>
                  </div>
                  <div className="text-right">
                    <p className={`text-lg font-bold ${
                      scan.risk_score > 75 ? 'text-red-400' :
                      scan.risk_score > 40 ? 'text-amber-400' :
                      'text-green-400'
                    }`}>{scan.risk_score}/100</p>
                    <p className="text-xs text-gray-400">{scan.verdict}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'badges' && (
        <div className="bg-[#12121a] border border-purple-500/20 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Badges & Certifications</h3>
          {badges.length === 0 ? (
            <div className="text-center py-12">
              <Award size={48} className="mx-auto text-gray-700 mb-4" />
              <p className="text-gray-500">No badges yet. Complete scans and challenges to earn them.</p>
            </div>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {badges.map((badge) => (
                <div key={badge.id} className="p-4 bg-[#0a0a0f] rounded-xl border border-purple-500/10 text-center">
                  <div className="w-12 h-12 mx-auto mb-3 rounded-full bg-purple-500/20 flex items-center justify-center">
                    <Award size={24} className="text-purple-400" />
                  </div>
                  <p className="text-sm font-semibold text-white">{badge.badge_name}</p>
                  <p className="text-xs text-gray-500 mt-1">{badge.badge_type}</p>
                  <p className="text-xs text-gray-600 mt-2">{new Date(badge.awarded_at).toLocaleDateString()}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'settings' && (
        <div className="bg-[#12121a] border border-purple-500/20 rounded-xl p-6 max-w-2xl">
          <h3 className="text-lg font-semibold text-white mb-6">Profile Settings</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-gray-400 mb-1">Display Name</label>
              <input
                value={form.display_name || ''}
                onChange={(e) => setForm({ ...form, display_name: e.target.value })}
                disabled={!editMode}
                className="w-full bg-[#0a0a0f] border border-purple-500/20 rounded-lg px-4 py-2 text-white text-sm focus:outline-none focus:border-purple-500/50 disabled:opacity-50"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Username</label>
              <input
                value={form.username || ''}
                onChange={(e) => setForm({ ...form, username: e.target.value })}
                disabled={!editMode}
                className="w-full bg-[#0a0a0f] border border-purple-500/20 rounded-lg px-4 py-2 text-white text-sm focus:outline-none focus:border-purple-500/50 disabled:opacity-50"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Bio</label>
              <textarea
                value={form.bio || ''}
                onChange={(e) => setForm({ ...form, bio: e.target.value })}
                disabled={!editMode}
                rows={3}
                className="w-full bg-[#0a0a0f] border border-purple-500/20 rounded-lg px-4 py-2 text-white text-sm focus:outline-none focus:border-purple-500/50 disabled:opacity-50"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Telegram Handle</label>
              <input
                value={form.telegram_handle || ''}
                onChange={(e) => setForm({ ...form, telegram_handle: e.target.value })}
                disabled={!editMode}
                className="w-full bg-[#0a0a0f] border border-purple-500/20 rounded-lg px-4 py-2 text-white text-sm focus:outline-none focus:border-purple-500/50 disabled:opacity-50"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Chain Preference</label>
              <select
                value={form.chain_preference || 'solana'}
                onChange={(e) => setForm({ ...form, chain_preference: e.target.value })}
                disabled={!editMode}
                className="w-full bg-[#0a0a0f] border border-purple-500/20 rounded-lg px-4 py-2 text-white text-sm focus:outline-none focus:border-purple-500/50 disabled:opacity-50"
              >
                <option value="solana">Solana</option>
                <option value="ethereum">Ethereum</option>
                <option value="base">Base</option>
                <option value="bsc">BSC</option>
                <option value="arbitrum">Arbitrum</option>
              </select>
            </div>
            {editMode && (
              <div className="flex gap-3 pt-4">
                <button
                  onClick={handleSave}
                  disabled={saving}
                  className="flex items-center gap-2 px-6 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
                >
                  <Check size={16} />
                  {saving ? 'Saving...' : 'Save Changes'}
                </button>
                <button
                  onClick={() => { setEditMode(false); setForm(profile || {}); }}
                  className="px-6 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg text-sm font-medium transition-colors"
                >
                  Cancel
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
