/**
 * Darkroom Control Center
 * =======================
 * Web3 + AI-first graphical command center for the entire RMI ecosystem.
 * Market intelligence, content command, social posting, project control.
 */
import { useState, useEffect, useRef } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../services/api';
import AdvisorAgent from './AdvisorAgent';
import {
  Activity,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  Send,
  FileText,
  Zap,
  Globe,
  Bot,
  Shield,
  Radio,
  Cpu,
  Eye,
  BarChart3,
  MessageSquare,
  Clock,
  CheckCircle,
  XCircle,
  ChevronRight,
  Flame,
  Diamond,
  Layers,
  Wifi,
  Lock,
  Unlock,
  RefreshCw,
  Play,
  Pause,
  PenTool,
  Megaphone,
  Newspaper,
  Target,
} from 'lucide-react';

const ADMIN_KEY_STORAGE = 'admin_key';

export default function DarkRoomControl() {
  const [adminKey, setAdminKey] = useState(localStorage.getItem(ADMIN_KEY_STORAGE) || '');
  const [activeSection, setActiveSection] = useState<'intel' | 'content' | 'social' | 'agents' | 'project'>('intel');
  const [showKeyInput, setShowKeyInput] = useState(!adminKey);
  const queryClient = useQueryClient();

  // ── Data Fetching ──
  const { data: briefing, isLoading: briefingLoading } = useQuery({
    queryKey: ['darkroom-briefing', adminKey],
    queryFn: () => api.getMarketBriefing(adminKey),
    enabled: !!adminKey,
    refetchInterval: 30000,
  });

  const { data: trending } = useQuery({
    queryKey: ['darkroom-trending', adminKey],
    queryFn: () => api.getMarketTrending(adminKey, 10),
    enabled: !!adminKey,
    refetchInterval: 60000,
  });

  const { data: projectStatus } = useQuery({
    queryKey: ['darkroom-project', adminKey],
    queryFn: () => api.getProjectStatus(adminKey),
    enabled: !!adminKey,
    refetchInterval: 15000,
  });

  const { data: agentMesh } = useQuery({
    queryKey: ['darkroom-mesh', adminKey],
    queryFn: () => api.getAgentMesh(adminKey),
    enabled: !!adminKey && activeSection === 'agents',
    refetchInterval: 10000,
  });

  const { data: contentStats } = useQuery({
    queryKey: ['darkroom-content-stats', adminKey],
    queryFn: () => api.getContentStats(adminKey),
    enabled: !!adminKey && activeSection === 'content',
  });

  const { data: contentDrafts } = useQuery({
    queryKey: ['darkroom-drafts', adminKey],
    queryFn: () => api.getContentDrafts(adminKey),
    enabled: !!adminKey && activeSection === 'content',
  });

  const { data: telegramStats } = useQuery({
    queryKey: ['darkroom-telegram', adminKey],
    queryFn: () => api.getTelegramStats(adminKey),
    enabled: !!adminKey && activeSection === 'social',
  });

  const { data: ghostStats } = useQuery({
    queryKey: ['darkroom-ghost', adminKey],
    queryFn: () => api.getGhostStats(adminKey),
    enabled: !!adminKey && activeSection === 'social',
  });

  // ── Mutations ──
  const postTelegramMutation = useMutation({
    mutationFn: ({ message, channel }: { message: string; channel: string }) =>
      api.postTelegram(adminKey, message, channel),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['darkroom-telegram'] }),
  });

  const createDraftMutation = useMutation({
    mutationFn: (draft: any) => api.createContentDraft(adminKey, draft),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['darkroom-drafts', 'darkroom-content-stats'] }),
  });

  const publishMutation = useMutation({
    mutationFn: (draftId: string) => api.publishContent(adminKey, draftId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['darkroom-drafts', 'darkroom-content-stats'] }),
  });

  const healthScore = projectStatus?.health_score || 0;
  const sentiment = briefing?.market_sentiment || 'neutral';
  const fearGreed = briefing?.fear_greed_index || 50;

  return (
    <div className="min-h-screen bg-[#050505] text-white relative overflow-hidden">
      {/* Ambient background effects */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-purple-900/10 rounded-full blur-[128px]" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-cyan-900/10 rounded-full blur-[128px]" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-emerald-900/5 rounded-full blur-[150px]" />
      </div>

      <div className="relative z-10 max-w-[1800px] mx-auto p-4 lg:p-6">
        {/* Header */}
        <header className="mb-8">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-violet-600 via-purple-600 to-cyan-600 flex items-center justify-center shadow-lg shadow-purple-900/30">
                <Eye className="w-7 h-7 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-white via-purple-200 to-cyan-200 bg-clip-text text-transparent">
                  Darkroom Control
                </h1>
                <p className="text-gray-500 text-sm">Web3 Intelligence Command Center</p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              {/* Health Orb */}
              <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white/5 border border-white/10">
                <div className={`w-3 h-3 rounded-full animate-pulse ${healthScore > 80 ? 'bg-emerald-400 shadow-emerald-400/50 shadow-lg' : healthScore > 50 ? 'bg-yellow-400' : 'bg-red-400'}`} />
                <span className="text-sm font-medium text-gray-300">Health {healthScore}%</span>
              </div>

              {/* Fear & Greed */}
              <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white/5 border border-white/10">
                <BarChart3 className="w-4 h-4 text-purple-400" />
                <span className="text-sm text-gray-300">F&G: <span className={`font-bold ${fearGreed > 70 ? 'text-green-400' : fearGreed < 30 ? 'text-red-400' : 'text-yellow-400'}`}>{fearGreed}</span></span>
              </div>

              {/* Admin Key */}
              {showKeyInput ? (
                <div className="flex items-center gap-2">
                  <input
                    type="password"
                    placeholder="Admin Key"
                    value={adminKey}
                    onChange={(e) => {
                      setAdminKey(e.target.value);
                      localStorage.setItem(ADMIN_KEY_STORAGE, e.target.value);
                    }}
                    className="bg-black/50 border border-white/10 rounded-lg px-3 py-2 text-sm text-white w-40 focus:outline-none focus:border-purple-500/50"
                  />
                  <button onClick={() => setShowKeyInput(false)} className="text-xs text-purple-400 hover:text-purple-300">Set</button>
                </div>
              ) : (
                <button
                  onClick={() => setShowKeyInput(true)}
                  className="px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-xs text-gray-400 hover:text-white transition-colors"
                >
                  {adminKey ? '●●●●●●' : 'No Key'}
                </button>
              )}
            </div>
          </div>
        </header>

        {/* Navigation Rail */}
        <nav className="flex gap-2 mb-6 overflow-x-auto pb-2">
          {[
            { id: 'intel', label: 'Market Intel', icon: Target, color: 'from-purple-500/20 to-violet-500/20 border-purple-500/30 text-purple-300' },
            { id: 'content', label: 'Content Command', icon: PenTool, color: 'from-emerald-500/20 to-teal-500/20 border-emerald-500/30 text-emerald-300' },
            { id: 'social', label: 'Social Post', icon: Megaphone, color: 'from-blue-500/20 to-cyan-500/20 border-blue-500/30 text-blue-300' },
            { id: 'agents', label: 'Agent Mesh', icon: Bot, color: 'from-orange-500/20 to-amber-500/20 border-orange-500/30 text-orange-300' },
            { id: 'project', label: 'Project Control', icon: Layers, color: 'from-rose-500/20 to-pink-500/20 border-rose-500/30 text-rose-300' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveSection(tab.id as any)}
              className={`flex items-center gap-2 px-5 py-3 rounded-xl border transition-all whitespace-nowrap ${
                activeSection === tab.id
                  ? `bg-gradient-to-r ${tab.color} shadow-lg`
                  : 'bg-white/5 border-white/5 text-gray-400 hover:bg-white/10 hover:border-white/10'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              <span className="font-medium text-sm">{tab.label}</span>
            </button>
          ))}
        </nav>

        {/* Content Area */}
        <main className="space-y-6">
          {activeSection === 'intel' && (
            <MarketIntelSection briefing={briefing} trending={trending} loading={briefingLoading} />
          )}
          {activeSection === 'content' && (
            <ContentCommandSection
              stats={contentStats}
              drafts={contentDrafts}
              createDraft={createDraftMutation}
              publish={publishMutation}
            />
          )}
          {activeSection === 'social' && (
            <SocialPostSection
              telegramStats={telegramStats}
              ghostStats={ghostStats}
              postTelegram={postTelegramMutation}
            />
          )}
          {activeSection === 'agents' && (
            <AgentMeshSection mesh={agentMesh} />
          )}
          {activeSection === 'project' && (
            <ProjectControlSection status={projectStatus} />
          )}
        </main>
      </div>

      {/* Advisor Agent — always present */}
      <AdvisorAgent adminKey={adminKey} />
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════
// MARKET INTELLIGENCE SECTION
// ═══════════════════════════════════════════════════════════════

function MarketIntelSection({ briefing, trending, loading }: any) {
  const tokens = trending?.tokens || [];
  const whaleAlerts = briefing?.whale_movements || [];
  const rugAlerts = briefing?.rug_detections || [];

  return (
    <div className="space-y-6">
      {/* Top Stats Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <GlowCard icon={Activity} label="Scans 24h" value={briefing?.total_scans_24h || 0} color="cyan" />
        <GlowCard icon={Shield} label="Investigations" value={briefing?.active_investigations || 0} color="purple" />
        <GlowCard icon={Flame} label="Rug Alerts" value={rugAlerts.length} color="red" />
        <GlowCard icon={Diamond} label="Alpha Signals" value={(briefing?.alpha_signals || []).length} color="emerald" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Trending Tokens */}
        <div className="lg:col-span-2 space-y-4">
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-emerald-400" />
            Trending Tokens
          </h3>
          <div className="grid gap-3">
            {loading ? (
              <SkeletonRows count={5} />
            ) : tokens.length === 0 ? (
              <EmptyState message="No trending data yet. Market signals will appear here." />
            ) : (
              tokens.map((t: any, i: number) => (
                <div
                  key={t.symbol}
                  className="group flex items-center justify-between p-4 rounded-xl bg-white/[0.03] border border-white/[0.06] hover:border-white/10 hover:bg-white/[0.05] transition-all"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-purple-500/20 to-cyan-500/20 flex items-center justify-center text-sm font-bold text-white">
                      {i + 1}
                    </div>
                    <div>
                      <p className="font-semibold text-white">{t.name} <span className="text-gray-500 text-sm">${t.symbol}</span></p>
                      <div className="flex items-center gap-3 text-xs text-gray-400">
                        <span>Vol ${(t.volume_24h / 1e6).toFixed(1)}M</span>
                        <span>Liq ${(t.liquidity / 1e6).toFixed(1)}M</span>
                        <span>Holders {t.holders?.toLocaleString()}</span>
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-mono text-white">${t.price?.toFixed(6)}</p>
                    <p className={`text-sm font-medium ${t.change_24h >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                      {t.change_24h >= 0 ? '+' : ''}{t.change_24h?.toFixed(2)}%
                    </p>
                  </div>
                  <div className="ml-4">
                    <RiskBadge score={t.risk_score} />
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Alerts Feed */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <Radio className="w-5 h-5 text-rose-400" />
            Live Alerts
          </h3>
          <div className="space-y-3 max-h-[500px] overflow-y-auto pr-1">
            {[...whaleAlerts, ...rugAlerts].slice(0, 8).map((alert: any, i: number) => (
              <div
                key={i}
                className="p-3 rounded-lg bg-white/[0.03] border border-white/[0.06] hover:bg-white/[0.05] transition-colors"
              >
                <div className="flex items-start gap-2">
                  {alert.type === 'whale' ? (
                    <Diamond className="w-4 h-4 text-cyan-400 mt-0.5 shrink-0" />
                  ) : (
                    <AlertTriangle className="w-4 h-4 text-rose-400 mt-0.5 shrink-0" />
                  )}
                  <div>
                    <p className="text-sm text-gray-200">{alert.message || alert.description || 'Alert signal'}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      {alert.timestamp ? new Date(alert.timestamp).toLocaleTimeString() : 'Just now'}
                    </p>
                  </div>
                </div>
              </div>
            ))}
            {whaleAlerts.length === 0 && rugAlerts.length === 0 && (
              <EmptyState message="Alert feed is quiet. Signals will appear as they are detected." />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════
// CONTENT COMMAND SECTION
// ═══════════════════════════════════════════════════════════════

function ContentCommandSection({ stats, drafts, createDraft, publish }: any) {
  const [title, setTitle] = useState('');
  const [body, setBody] = useState('');
  const [category, setCategory] = useState('intel');
  const [platforms, setPlatforms] = useState(['telegram']);
  const [activeSubTab, setActiveSubTab] = useState<'editor' | 'prepared' | 'drafts'>('prepared');
  const queryClient = useQueryClient();
  const adminKey = localStorage.getItem('admin_key') || '';

  const draftList = drafts?.drafts || [];

  // Prepared content (auto-generated while you sleep)
  const { data: preparedData, refetch: refetchPrepared } = useQuery({
    queryKey: ['darkroom-prepared', adminKey],
    queryFn: () => api.getPreparedContent(adminKey),
    enabled: !!adminKey,
    refetchInterval: 15000,
  });

  const autoGenMutation = useMutation({
    mutationFn: () => api.autoGenerateContent(adminKey, 'market_intel', 3, 'analytical'),
    onSuccess: () => {
      refetchPrepared();
      queryClient.invalidateQueries({ queryKey: ['darkroom-drafts'] });
    },
  });

  const approveMutation = useMutation({
    mutationFn: ({ draftId, decision }: { draftId: string; decision: string }) =>
      api.approveContent(adminKey, draftId, decision),
    onSuccess: () => refetchPrepared(),
  });

  const preparedList = preparedData?.prepared || [];

  const handleCreate = () => {
    if (!title.trim() || !body.trim()) return;
    createDraft.mutate({ title, body, category, platforms, tags: [] });
    setTitle('');
    setBody('');
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Main Panel */}
      <div className="lg:col-span-2 space-y-4">
        {/* Sub-tabs */}
        <div className="flex gap-2">
          {[
            { id: 'prepared', label: `Prepared (${preparedList.length})`, icon: Sparkles },
            { id: 'editor', label: 'Editor', icon: PenTool },
            { id: 'drafts', label: `Drafts (${draftList.length})`, icon: FileText },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveSubTab(tab.id as any)}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all ${
                activeSubTab === tab.id
                  ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                  : 'bg-white/5 text-gray-400 border border-white/5 hover:bg-white/10'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
          <button
            onClick={() => autoGenMutation.mutate()}
            disabled={autoGenMutation.isPending}
            className="ml-auto flex items-center gap-2 px-4 py-2 rounded-xl bg-purple-500/20 text-purple-300 border border-purple-500/30 text-sm font-medium hover:bg-purple-500/30 transition-colors disabled:opacity-50"
          >
            <Sparkles className="w-4 h-4" />
            {autoGenMutation.isPending ? 'Generating...' : 'Auto-Generate'}
          </button>
        </div>

        {/* PREPARED CONTENT INBOX */}
        {activeSubTab === 'prepared' && (
          <div className="space-y-3">
            {preparedList.length === 0 ? (
              <div className="p-8 rounded-2xl bg-white/[0.03] border border-white/[0.06] text-center">
                <Sparkles className="w-10 h-10 text-gray-600 mx-auto mb-3" />
                <p className="text-gray-400 mb-1">No prepared content yet</p>
                <p className="text-gray-600 text-sm">Click "Auto-Generate" to create drafts from live market data while you sleep.</p>
                <button
                  onClick={() => autoGenMutation.mutate()}
                  className="mt-4 px-4 py-2 rounded-lg bg-purple-500/20 text-purple-300 border border-purple-500/30 text-sm hover:bg-purple-500/30 transition-colors"
                >
                  Generate Now
                </button>
              </div>
            ) : (
              preparedList.map((draft: any) => (
                <div
                  key={draft.id}
                  className={`p-5 rounded-2xl border transition-all ${
                    draft.source === 'rug_alert'
                      ? 'bg-rose-500/[0.04] border-rose-500/20'
                      : draft.source === 'whale_alert'
                      ? 'bg-cyan-500/[0.04] border-cyan-500/20'
                      : 'bg-white/[0.03] border-white/[0.06]'
                  }`}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-2">
                      {draft.source === 'rug_alert' && <AlertTriangle className="w-4 h-4 text-rose-400" />}
                      {draft.source === 'whale_alert' && <Diamond className="w-4 h-4 text-cyan-400" />}
                      {draft.source === 'market_intel' && <TrendingUp className="w-4 h-4 text-emerald-400" />}
                      {draft.source === 'daily_briefing' && <Newspaper className="w-4 h-4 text-purple-400" />}
                      <span className={`text-xs px-2 py-0.5 rounded border ${
                        draft.source === 'rug_alert' ? 'bg-rose-500/10 text-rose-400 border-rose-500/20' :
                        draft.source === 'whale_alert' ? 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20' :
                        'bg-white/5 text-gray-400 border-white/10'
                      }`}>
                        {draft.source?.replace('_', ' ')}
                      </span>
                      {draft.auto_generated && (
                        <span className="text-[10px] text-purple-400 flex items-center gap-1">
                          <Sparkles className="w-3 h-3" /> AI
                        </span>
                      )}
                    </div>
                    <span className="text-xs text-gray-500">
                      {new Date(draft.created_at).toLocaleTimeString()}
                    </span>
                  </div>

                  <h4 className="font-semibold text-white mb-2">{draft.title}</h4>
                  <div className="bg-black/30 rounded-lg p-3 mb-4 text-sm text-gray-300 whitespace-pre-line">
                    {draft.body}
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="flex gap-2">
                      {draft.platforms?.map((p: string) => (
                        <span key={p} className="text-[10px] px-2 py-0.5 rounded bg-white/5 text-gray-400 border border-white/5 capitalize">
                          {p}
                        </span>
                      ))}
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => approveMutation.mutate({ draftId: draft.id, decision: 'reject' })}
                        disabled={approveMutation.isPending}
                        className="px-3 py-1.5 rounded-lg bg-white/5 text-gray-400 border border-white/10 text-xs hover:bg-red-500/10 hover:text-red-400 hover:border-red-500/20 transition-colors disabled:opacity-50"
                      >
                        Reject
                      </button>
                      <button
                        onClick={() => approveMutation.mutate({ draftId: draft.id, decision: 'schedule' })}
                        disabled={approveMutation.isPending}
                        className="px-3 py-1.5 rounded-lg bg-white/5 text-gray-400 border border-white/10 text-xs hover:bg-yellow-500/10 hover:text-yellow-400 hover:border-yellow-500/20 transition-colors disabled:opacity-50"
                      >
                        Schedule
                      </button>
                      <button
                        onClick={() => approveMutation.mutate({ draftId: draft.id, decision: 'approve' })}
                        disabled={approveMutation.isPending}
                        className="px-4 py-1.5 rounded-lg bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-xs hover:bg-emerald-500/30 transition-colors disabled:opacity-50 flex items-center gap-1"
                      >
                        <CheckCircle className="w-3 h-3" />
                        Publish
                      </button>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {/* EDITOR */}
        {activeSubTab === 'editor' && (
          <div className="p-5 rounded-2xl bg-white/[0.03] border border-white/[0.06]">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <PenTool className="w-5 h-5 text-emerald-400" />
              Content Editor
            </h3>
            <input
              type="text"
              placeholder="Title..."
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full mb-3 bg-black/30 border border-white/10 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-emerald-500/50"
            />
            <textarea
              placeholder="Write your intel, analysis, or announcement..."
              value={body}
              onChange={(e) => setBody(e.target.value)}
              rows={8}
              className="w-full mb-3 bg-black/30 border border-white/10 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-emerald-500/50 resize-none"
            />
            <div className="flex items-center justify-between">
              <div className="flex gap-2">
                {['intel', 'announcement', 'analysis', 'alpha'].map((c) => (
                  <button
                    key={c}
                    onClick={() => setCategory(c)}
                    className={`px-3 py-1.5 rounded-lg text-xs capitalize transition-colors ${
                      category === c ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : 'bg-white/5 text-gray-400 border border-white/5'
                    }`}
                  >
                    {c}
                  </button>
                ))}
              </div>
              <button
                onClick={handleCreate}
                disabled={createDraft.isPending}
                className="px-4 py-2 rounded-lg bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 hover:bg-emerald-500/30 transition-colors text-sm font-medium disabled:opacity-50"
              >
                {createDraft.isPending ? 'Saving...' : 'Save Draft'}
              </button>
            </div>
          </div>
        )}

        {/* DRAFTS LIST */}
        {activeSubTab === 'drafts' && (
          <div className="space-y-3">
            {draftList.map((d: any) => (
              <div key={d.id} className="p-4 rounded-xl bg-white/[0.03] border border-white/[0.06] flex items-center justify-between">
                <div>
                  <p className="font-medium text-white">{d.title}</p>
                  <p className="text-xs text-gray-500">{d.category} • {new Date(d.created_at).toLocaleDateString()}</p>
                </div>
                <button
                  onClick={() => publish.mutate(d.id)}
                  disabled={publish.isPending}
                  className="px-3 py-1.5 rounded-lg bg-purple-500/20 text-purple-300 border border-purple-500/30 text-xs hover:bg-purple-500/30 transition-colors disabled:opacity-50"
                >
                  {publish.isPending ? '...' : 'Publish'}
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Stats Sidebar */}
      <div className="space-y-4">
        <div className="p-5 rounded-2xl bg-white/[0.03] border border-white/[0.06]">
          <h4 className="text-sm font-medium text-gray-400 mb-4">Content Pipeline</h4>
          <div className="space-y-4">
            <StatBar label="Prepared (needs approval)" value={preparedList.length} max={20} color="bg-purple-400" />
            <StatBar label="Drafts" value={stats?.drafts || 0} max={20} color="bg-emerald-400" />
            <StatBar label="Published" value={stats?.published || 0} max={100} color="bg-blue-400" />
            <StatBar label="Scheduled" value={stats?.scheduled || 0} max={10} color="bg-yellow-400" />
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-white/[0.03] border border-white/[0.06]">
          <h4 className="text-sm font-medium text-gray-400 mb-3">Auto-Sources</h4>
          <div className="space-y-2 text-sm">
            {[
              { source: 'market_intel', label: 'Market Intel', count: preparedData?.by_source?.market_intel || 0 },
              { source: 'daily_briefing', label: 'Daily Briefing', count: preparedData?.by_source?.daily_briefing || 0 },
              { source: 'whale_alert', label: 'Whale Alerts', count: preparedData?.by_source?.whale_alert || 0 },
              { source: 'rug_alert', label: 'Rug Alerts', count: preparedData?.by_source?.rug_alert || 0 },
            ].map((s) => (
              <div key={s.source} className="flex justify-between items-center p-2 rounded-lg bg-white/[0.03]">
                <span className="text-gray-300">{s.label}</span>
                <span className="text-white font-mono">{s.count}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-white/[0.03] border border-white/[0.06]">
          <h4 className="text-sm font-medium text-gray-400 mb-3">Platform Targets</h4>
          <div className="space-y-2">
            {['telegram', 'mirror', 'twitter', 'newsletter'].map((p) => (
              <label key={p} className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={platforms.includes(p)}
                  onChange={(e) => {
                    if (e.target.checked) setPlatforms([...platforms, p]);
                    else setPlatforms(platforms.filter((x: string) => x !== p));
                  }}
                  className="rounded border-white/20 bg-black/30 text-emerald-500"
                />
                <span className="text-sm text-gray-300 capitalize">{p}</span>
              </label>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
function SocialPostSection({ telegramStats, ghostStats, postTelegram }: any) {
  const [message, setMessage] = useState('');
  const [channel, setChannel] = useState('@rmi_alpha_alerts');

  const recentPosts = telegramStats?.recent_posts || [];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Telegram Poster */}
      <div className="lg:col-span-2 space-y-4">
        <div className="p-5 rounded-2xl bg-white/[0.03] border border-white/[0.06]">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Send className="w-5 h-5 text-blue-400" />
            Telegram Broadcast
          </h3>
          <div className="flex gap-2 mb-3">
            {['@rmi_alpha_alerts', '@munchscans', '@rmi_backend'].map((ch) => (
              <button
                key={ch}
                onClick={() => setChannel(ch)}
                className={`px-3 py-1.5 rounded-lg text-xs transition-colors ${
                  channel === ch ? 'bg-blue-500/20 text-blue-300 border border-blue-500/30' : 'bg-white/5 text-gray-400 border border-white/5'
                }`}
              >
                {ch}
              </button>
            ))}
          </div>
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Craft your message..."
            rows={6}
            className="w-full mb-3 bg-black/30 border border-white/10 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500/50 resize-none"
          />
          <div className="flex justify-between items-center">
            <span className="text-xs text-gray-500">{message.length}/4096</span>
            <button
              onClick={() => {
                postTelegram.mutate({ message, channel });
                setMessage('');
              }}
              disabled={!message.trim() || postTelegram.isPending}
              className="px-5 py-2 rounded-lg bg-blue-500/20 text-blue-300 border border-blue-500/30 hover:bg-blue-500/30 transition-colors text-sm font-medium disabled:opacity-50 flex items-center gap-2"
            >
              <Send className="w-4 h-4" />
              {postTelegram.isPending ? 'Sending...' : 'Broadcast'}
            </button>
          </div>
        </div>

        {/* Recent Posts */}
        <div className="space-y-3">
          <h4 className="text-sm font-medium text-gray-400">Recent Broadcasts ({telegramStats?.posts_total || 0})</h4>
          {recentPosts.map((post: any, i: number) => (
            <div key={i} className="p-3 rounded-xl bg-white/[0.03] border border-white/[0.06]">
              <p className="text-sm text-gray-300 line-clamp-2">{post.message_preview}</p>
              <div className="flex items-center gap-2 mt-2 text-xs text-gray-500">
                <span>{post.channel}</span>
                <span>•</span>
                <span>{post.sent_at ? new Date(post.sent_at).toLocaleTimeString() : 'Recent'}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Ghost Stats */}
      <div className="space-y-4">
        <div className="p-5 rounded-2xl bg-white/[0.03] border border-white/[0.06]">
          <h4 className="text-sm font-medium text-gray-400 mb-4">Ghost / Mirror</h4>
          <div className="text-center py-6">
            <Newspaper className="w-10 h-10 text-gray-600 mx-auto mb-3" />
            <p className="text-3xl font-bold text-white">{ghostStats?.mirror_posts || 0}</p>
            <p className="text-sm text-gray-500">Published Articles</p>
          </div>
          <div className="border-t border-white/5 pt-4 mt-4">
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Subscribers</span>
              <span className="text-white font-medium">{(ghostStats?.newsletter_subscribers || 0).toLocaleString()}</span>
            </div>
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-white/[0.03] border border-white/[0.06]">
          <h4 className="text-sm font-medium text-gray-400 mb-3">Channels</h4>
          <div className="space-y-2">
            {(telegramStats?.channels || []).map((ch: string) => (
              <div key={ch} className="flex items-center justify-between p-2 rounded-lg bg-white/[0.03]">
                <span className="text-sm text-gray-300">{ch}</span>
                <Wifi className="w-3 h-3 text-emerald-400" />
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════
// AGENT MESH SECTION
// ═══════════════════════════════════════════════════════════════

function AgentMeshSection({ mesh }: any) {
  const nodes = mesh?.nodes || [];
  const edges = mesh?.edges || [];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <GlowCard icon={Bot} label="Total Agents" value={nodes.length} color="orange" />
        <GlowCard icon={CheckCircle} label="Online" value={nodes.filter((n: any) => n.status === 'online').length} color="emerald" />
        <GlowCard icon={Cpu} label="Mesh Health" value={`${Math.round((mesh?.mesh_health || 0) * 100)}%`} color="cyan" />
        <GlowCard icon={Zap} label="Tasks Done" value={nodes.reduce((a: number, n: any) => a + (n.tasks_completed || 0), 0)} color="purple" />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {nodes.map((agent: any) => (
          <div
            key={agent.id}
            className={`p-5 rounded-2xl border transition-all ${
              agent.status === 'online'
                ? 'bg-white/[0.03] border-white/[0.06] hover:border-emerald-500/20'
                : 'bg-white/[0.02] border-white/[0.04] opacity-60'
            }`}
          >
            <div className="flex items-center justify-between mb-3">
              <div className={`w-3 h-3 rounded-full ${agent.status === 'online' ? 'bg-emerald-400 animate-pulse shadow-lg shadow-emerald-400/30' : 'bg-gray-600'}`} />
              <span className="text-xs text-gray-500">{agent.tier}</span>
            </div>
            <h4 className="text-lg font-bold text-white mb-1">{agent.name}</h4>
            <p className="text-xs text-gray-400 mb-3">{agent.role}</p>
            <div className="space-y-1 text-xs">
              <div className="flex justify-between">
                <span className="text-gray-500">Load</span>
                <span className="text-white">{Math.round((agent.load || 0) * 100)}%</span>
              </div>
              <div className="w-full h-1 bg-white/10 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-emerald-400 to-cyan-400 rounded-full transition-all"
                  style={{ width: `${Math.min((agent.load || 0) * 100, 100)}%` }}
                />
              </div>
              <div className="flex justify-between pt-1">
                <span className="text-gray-500">Tasks</span>
                <span className="text-white">{(agent.tasks_completed || 0).toLocaleString()}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Mesh Visualization */}
      <div className="p-6 rounded-2xl bg-white/[0.03] border border-white/[0.06] relative overflow-hidden">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Layers className="w-5 h-5 text-purple-400" />
          Mesh Topology
        </h3>
        <div className="relative h-64 flex items-center justify-center">
          {/* Simple CSS mesh visualization */}
          <div className="absolute inset-0 flex items-center justify-center">
            {nodes.map((agent: any, i: number) => {
              const angle = (i / Math.max(nodes.length, 1)) * Math.PI * 2 - Math.PI / 2;
              const radius = 90;
              const x = Math.cos(angle) * radius;
              const y = Math.sin(angle) * radius;
              return (
                <div
                  key={agent.id}
                  className="absolute flex flex-col items-center"
                  style={{ transform: `translate(${x}px, ${y}px)` }}
                >
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center text-xs font-bold border-2 ${
                    agent.status === 'online'
                      ? 'bg-purple-500/20 border-purple-400 text-purple-300 shadow-lg shadow-purple-500/20'
                      : 'bg-gray-800 border-gray-600 text-gray-500'
                  }`}>
                    {agent.name?.[0] || '?'}
                  </div>
                  <span className="text-[10px] text-gray-400 mt-1 whitespace-nowrap">{agent.name}</span>
                </div>
              );
            })}
            {/* Center node */}
            <div className="w-14 h-14 rounded-full bg-gradient-to-br from-violet-500 to-cyan-500 flex items-center justify-center text-white font-bold shadow-xl shadow-purple-500/30 z-10">
              N
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════
// PROJECT CONTROL SECTION
// ═══════════════════════════════════════════════════════════════

function ProjectControlSection({ status }: any) {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <GlowCard icon={Activity} label="Health Score" value={`${status?.health_score || 0}%`} color="emerald" />
        <GlowCard icon={Bot} label="Agents Online" value={status?.agents?.online || 0} color="purple" />
        <GlowCard icon={Shield} label="Investigations" value={status?.investigations?.active || 0} color="cyan" />
        <GlowCard icon={FileText} label="Drafts Ready" value={status?.content?.drafts || 0} color="orange" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="p-6 rounded-2xl bg-white/[0.03] border border-white/[0.06]">
          <h3 className="text-lg font-semibold mb-4">System Pulse</h3>
          <div className="space-y-4">
            {[
              { label: 'Agent Mesh', value: status?.agents?.online || 0, max: status?.agents?.total || 8, color: 'from-purple-400 to-violet-400' },
              { label: 'Task Queue', value: status?.queues?.system || 0, max: 50, color: 'from-cyan-400 to-blue-400' },
              { label: 'Social Posts', value: status?.social?.posts_sent || 0, max: 100, color: 'from-emerald-400 to-teal-400' },
              { label: 'Content Pipeline', value: (status?.content?.published || 0) + (status?.content?.drafts || 0), max: 100, color: 'from-orange-400 to-amber-400' },
            ].map((item) => (
              <div key={item.label}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-400">{item.label}</span>
                  <span className="text-white">{item.value}</span>
                </div>
                <div className="w-full h-2 bg-white/10 rounded-full overflow-hidden">
                  <div
                    className={`h-full bg-gradient-to-r ${item.color} rounded-full transition-all duration-500`}
                    style={{ width: `${Math.min((item.value / item.max) * 100, 100)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="p-6 rounded-2xl bg-white/[0.03] border border-white/[0.06]">
          <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
          <div className="grid grid-cols-2 gap-3">
            {[
              { label: 'Run Health Check', icon: Activity, color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20' },
              { label: 'Clear Cache', icon: RefreshCw, color: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/20' },
              { label: 'Ping Agents', icon: Bot, color: 'text-purple-400 bg-purple-500/10 border-purple-500/20' },
              { label: 'Export Data', icon: FileText, color: 'text-orange-400 bg-orange-500/10 border-orange-500/20' },
            ].map((action) => (
              <button
                key={action.label}
                className={`p-4 rounded-xl border ${action.color} hover:bg-white/5 transition-all text-left`}
              >
                <action.icon className="w-5 h-5 mb-2" />
                <p className="text-sm font-medium">{action.label}</p>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════
// UI HELPERS
// ═══════════════════════════════════════════════════════════════

function GlowCard({ icon: Icon, label, value, color }: any) {
  const colorMap: any = {
    cyan: 'shadow-cyan-500/20 border-cyan-500/20',
    purple: 'shadow-purple-500/20 border-purple-500/20',
    emerald: 'shadow-emerald-500/20 border-emerald-500/20',
    red: 'shadow-red-500/20 border-red-500/20',
    orange: 'shadow-orange-500/20 border-orange-500/20',
    blue: 'shadow-blue-500/20 border-blue-500/20',
  };
  return (
    <div className={`p-5 rounded-2xl bg-white/[0.03] border ${colorMap[color] || colorMap.cyan} shadow-lg`}>
      <div className="flex items-center justify-between mb-2">
        <Icon className="w-5 h-5 text-gray-400" />
        <ChevronRight className="w-4 h-4 text-gray-600" />
      </div>
      <p className="text-2xl font-bold text-white">{value}</p>
      <p className="text-xs text-gray-500">{label}</p>
    </div>
  );
}

function RiskBadge({ score }: { score: number }) {
  if (score >= 80) return <span className="px-2 py-0.5 rounded text-[10px] bg-red-500/20 text-red-400 border border-red-500/30">HIGH</span>;
  if (score >= 50) return <span className="px-2 py-0.5 rounded text-[10px] bg-yellow-500/20 text-yellow-400 border border-yellow-500/30">MED</span>;
  return <span className="px-2 py-0.5 rounded text-[10px] bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">LOW</span>;
}

function StatBar({ label, value, max, color }: any) {
  const pct = Math.min((value / max) * 100, 100);
  return (
    <div>
      <div className="flex justify-between text-xs mb-1">
        <span className="text-gray-400">{label}</span>
        <span className="text-white">{value}</span>
      </div>
      <div className="w-full h-1.5 bg-white/10 rounded-full overflow-hidden">
        <div className={`h-full ${color} rounded-full`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

function EmptyState({ message }: { message: string }) {
  return (
    <div className="p-8 text-center text-gray-500">
      <Radio className="w-8 h-8 mx-auto mb-2 opacity-50" />
      <p className="text-sm">{message}</p>
    </div>
  );
}

function SkeletonRows({ count }: { count: number }) {
  return (
    <>
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="p-4 rounded-xl bg-white/[0.03] border border-white/[0.06] animate-pulse">
          <div className="h-4 bg-white/10 rounded w-1/3 mb-2" />
          <div className="h-3 bg-white/5 rounded w-2/3" />
        </div>
      ))}
    </>
  );
}
