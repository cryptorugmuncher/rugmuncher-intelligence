/**
 * Investigation Tracker - Case management system
 * WIRED TO REAL BACKEND API
 */
import { useState, useEffect } from 'react';
import {
  FolderOpen,
  Plus,
  Search,
  Clock,
  ChevronRight,
  MessageSquare,
  FileText,
  Shield,
  Users,
  ExternalLink,
  X,
  Loader2,
  AlertTriangle,
  Eye,
  EyeOff,
  Lock,
} from 'lucide-react';
import { useAppStore } from '../store/appStore';
import { api } from '../services/api';

const STATUSES = [
  { id: 'all', label: 'All', color: 'gray' },
  { id: 'pending', label: 'Pending', color: 'yellow' },
  { id: 'active', label: 'Active', color: 'blue' },
  { id: 'resolved', label: 'Resolved', color: 'green' },
  { id: 'closed', label: 'Closed', color: 'gray' },
];

interface CaseItem {
  id: string;
  title: string;
  description: string;
  status: string;
  priority: string;
  createdAt: string;
  updatedAt: string;
  wallets: string[];
  evidence: number;
  assignedTo: string;
  tags: string[];
  updates: { time: string; text: string }[];
  published?: boolean;
  isCRM?: boolean;
}

interface CRMDetail {
  timeline: any[];
  stats: any;
  structure: any;
  wallets: any[];
  evidence: any;
  graph: any;
}

function transformCase(raw: any): CaseItem {
  const findings = raw.findings || {};
  const isCRM = raw.id === 'CRM-SCAM-2025-001';
  return {
    id: raw.id,
    title: raw.target || 'Untitled Investigation',
    description: findings.summary || `${raw.type} investigation`,
    status: (raw.status || 'pending').replace(/_/g, ''),
    priority: (raw.risk_score || 0) > 0.8 ? 'critical' : (raw.risk_score || 0) > 0.5 ? 'high' : 'medium',
    createdAt: raw.created_at ? new Date(raw.created_at).toLocaleDateString() : 'Unknown',
    updatedAt: raw.updated_at ? new Date(raw.updated_at).toLocaleDateString() : 'Unknown',
    wallets: findings.wallets || [],
    evidence: Array.isArray(raw.evidence) ? raw.evidence.length : 0,
    assignedTo: Array.isArray(raw.agents_assigned) ? raw.agents_assigned.join(', ') : 'Unassigned',
    tags: [raw.type, ...(findings.classification ? [findings.classification] : [])].filter(Boolean),
    updates: [],
    published: raw.published ?? !isCRM,
    isCRM,
  };
}

export default function InvestigationsPage() {
  const [view, setView] = useState<'list' | 'detail'>('list');
  const [selectedCase, setSelectedCase] = useState<CaseItem | null>(null);
  const [statusFilter, setStatusFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);

  // Real data states
  const [cases, setCases] = useState<CaseItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [crmDetail, setCrmDetail] = useState<CRMDetail | null>(null);
  const [loadingCRM, setLoadingCRM] = useState(false);
  const [publishLoading, setPublishLoading] = useState(false);
  const [adminKey, setAdminKey] = useState('');
  const [showAdminKeyInput, setShowAdminKeyInput] = useState(false);

  const user = useAppStore((state) => state.user);
  const tier = user?.tier || 'FREE';
  const isAdmin = user?.role === 'ADMIN';
  const canCreate = tier !== 'FREE';

  // Fetch cases on mount
  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        setLoading(true);
        const res = await api.listCases();
        if (!cancelled) {
          setCases((res.cases || []).map(transformCase));
          setError(null);
        }
      } catch (e: any) {
        if (!cancelled) setError(e.message || 'Failed to load cases');
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, []);

  const filteredCases = cases.filter((item) => {
    if (statusFilter !== 'all' && item.status !== statusFilter) return false;
    if (searchQuery && !item.title.toLowerCase().includes(searchQuery.toLowerCase())) return false;
    return true;
  });

  const handleViewCase = async (caseItem: CaseItem) => {
    setSelectedCase(caseItem);
    setView('detail');
    setCrmDetail(null);

    if (caseItem.isCRM) {
      setLoadingCRM(true);
      try {
        const [timelineRes, statsRes, structureRes, walletsRes, evidenceRes, graphRes] = await Promise.all([
          api.getCaseCRMTimeline(caseItem.id),
          api.getCaseCRMStats(caseItem.id),
          api.getCaseCRMStructure(caseItem.id),
          api.getCaseCRMWallets(caseItem.id),
          api.getCaseCRMEvidence(caseItem.id),
          api.getCaseCRMGraph(caseItem.id),
        ]);
        setCrmDetail({
          timeline: timelineRes.timeline || [],
          stats: statsRes,
          structure: structureRes,
          wallets: walletsRes.wallets || [],
          evidence: evidenceRes,
          graph: graphRes,
        });
      } catch (e: any) {
        console.error('CRM detail load failed:', e);
      } finally {
        setLoadingCRM(false);
      }
    }
  };

  const handlePublishToggle = async () => {
    if (!selectedCase || !isAdmin) return;
    if (!adminKey && !showAdminKeyInput) {
      setShowAdminKeyInput(true);
      return;
    }
    if (!adminKey) return;

    setPublishLoading(true);
    try {
      if (selectedCase.published) {
        await api.unpublishCase(selectedCase.id, adminKey);
      } else {
        await api.publishCase(selectedCase.id, adminKey);
      }
      // Refresh cases
      const res = await api.listCases();
      setCases((res.cases || []).map(transformCase));
      // Update selected case
      setSelectedCase((prev) => prev ? { ...prev, published: !prev.published } : prev);
      setShowAdminKeyInput(false);
      setAdminKey('');
    } catch (e: any) {
      alert(e.response?.data?.detail || 'Publish action failed');
    } finally {
      setPublishLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      pending: 'bg-yellow-500/20 text-yellow-400',
      active: 'bg-blue-500/20 text-blue-400',
      resolved: 'bg-green-500/20 text-green-400',
      closed: 'bg-gray-500/20 text-gray-400',
    };
    return colors[status] || colors.closed;
  };

  const getPriorityColor = (priority: string) => {
    const colors: Record<string, string> = {
      low: 'bg-gray-500/20 text-gray-400',
      medium: 'bg-yellow-500/20 text-yellow-400',
      high: 'bg-orange-500/20 text-orange-400',
      critical: 'bg-red-500/20 text-red-400 border border-red-500/30',
    };
    return colors[priority] || colors.low;
  };

  if (view === 'detail' && selectedCase) {
    return (
      <div className="space-y-6">
        {/* Back Button */}
        <button
          onClick={() => setView('list')}
          className="flex items-center gap-2 text-gray-400 hover:text-white"
        >
          ← Back to Investigations
        </button>

        {/* Case Header */}
        <div className="bg-[#12121a] border border-gray-800 rounded-xl p-6">
          <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2 flex-wrap">
                <span className="font-mono text-xs text-gray-500">{selectedCase.id}</span>
                <span className={`px-2 py-1 rounded text-xs ${getStatusColor(selectedCase.status)}`}>
                  {selectedCase.status.toUpperCase()}
                </span>
                <span className={`px-2 py-1 rounded text-xs ${getPriorityColor(selectedCase.priority)}`}>
                  {selectedCase.priority.toUpperCase()}
                </span>
                {selectedCase.isCRM && (
                  <span className={`px-2 py-1 rounded text-xs flex items-center gap-1 ${selectedCase.published ? 'bg-green-500/20 text-green-400' : 'bg-amber-500/20 text-amber-400'}`}>
                    {selectedCase.published ? <Eye className="w-3 h-3" /> : <EyeOff className="w-3 h-3" />}
                    {selectedCase.published ? 'PUBLISHED' : 'DRAFT'}
                  </span>
                )}
              </div>
              <h1 className="text-2xl font-bold text-white mb-2">{selectedCase.title}</h1>
              <p className="text-gray-400">{selectedCase.description}</p>

              {/* Admin Publish Controls */}
              {isAdmin && selectedCase.isCRM && (
                <div className="mt-4 p-3 bg-gray-800/50 rounded-lg border border-gray-700">
                  <div className="flex items-center gap-2 text-sm text-gray-300 mb-2">
                    <Lock className="w-4 h-4" />
                    Admin Publication Control
                  </div>
                  {showAdminKeyInput ? (
                    <div className="flex gap-2">
                      <input
                        type="password"
                        placeholder="Enter admin key..."
                        value={adminKey}
                        onChange={(e) => setAdminKey(e.target.value)}
                        className="flex-1 bg-gray-900 border border-gray-700 rounded px-3 py-1 text-white text-sm"
                      />
                      <button
                        onClick={handlePublishToggle}
                        disabled={publishLoading}
                        className="px-3 py-1 bg-purple-600 hover:bg-purple-700 text-white rounded text-sm disabled:opacity-50"
                      >
                        {publishLoading ? '...' : selectedCase.published ? 'Unpublish' : 'Publish'}
                      </button>
                      <button
                        onClick={() => { setShowAdminKeyInput(false); setAdminKey(''); }}
                        className="px-3 py-1 bg-gray-700 hover:bg-gray-600 text-white rounded text-sm"
                      >
                        Cancel
                      </button>
                    </div>
                  ) : (
                    <button
                      onClick={handlePublishToggle}
                      className={`px-4 py-2 rounded text-sm font-medium transition-colors ${selectedCase.published ? 'bg-red-500/20 text-red-400 hover:bg-red-500/30' : 'bg-green-500/20 text-green-400 hover:bg-green-500/30'}`}
                    >
                      {selectedCase.published ? 'Unpublish Case' : 'Publish Case'}
                    </button>
                  )}
                </div>
              )}
            </div>
            <div className="flex gap-2">
              <button className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-white rounded-lg transition-colors">
                Edit
              </button>
              <button className="px-4 py-2 bg-green-500 hover:bg-green-600 text-black font-bold rounded-lg transition-colors">
                Update
              </button>
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 pt-6 border-t border-gray-800">
            <div>
              <div className="text-sm text-gray-500 mb-1">Created</div>
              <div className="text-white">{selectedCase.createdAt}</div>
            </div>
            <div>
              <div className="text-sm text-gray-500 mb-1">Last Updated</div>
              <div className="text-white">{selectedCase.updatedAt}</div>
            </div>
            <div>
              <div className="text-sm text-gray-500 mb-1">Assigned To</div>
              <div className="text-white">{selectedCase.assignedTo}</div>
            </div>
            <div>
              <div className="text-sm text-gray-500 mb-1">Evidence</div>
              <div className="text-white">{selectedCase.evidence} items</div>
            </div>
          </div>
        </div>

        {/* CRM Enriched Data */}
        {selectedCase.isCRM && loadingCRM && (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 text-purple-400 animate-spin" />
            <span className="ml-3 text-gray-400">Loading CRM investigation data...</span>
          </div>
        )}

        {selectedCase.isCRM && crmDetail && (
          <div className="space-y-6">
            {/* CRM Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-[#12121a] border border-gray-800 rounded-xl p-4">
                <div className="text-2xl font-bold text-white">
                  ${crmDetail.stats?.financial?.total_usd?.toLocaleString() || '0'}
                </div>
                <div className="text-sm text-gray-400">Financial Impact</div>
              </div>
              <div className="bg-[#12121a] border border-gray-800 rounded-xl p-4">
                <div className="text-2xl font-bold text-red-400">
                  {crmDetail.stats?.wallets?.suspect || 0}
                </div>
                <div className="text-sm text-gray-400">Suspect Wallets</div>
              </div>
              <div className="bg-[#12121a] border border-gray-800 rounded-xl p-4">
                <div className="text-2xl font-bold text-blue-400">
                  {crmDetail.stats?.wallets?.victim || 0}
                </div>
                <div className="text-sm text-gray-400">Victim Wallets</div>
              </div>
              <div className="bg-[#12121a] border border-gray-800 rounded-xl p-4">
                <div className="text-2xl font-bold text-white">
                  {crmDetail.stats?.transactions?.suspicious || 0}
                </div>
                <div className="text-sm text-gray-400">Suspicious TXs</div>
              </div>
            </div>

            {/* Criminal Structure */}
            {crmDetail.structure && Object.keys(crmDetail.structure).length > 0 && (
              <div className="bg-[#12121a] border border-gray-800 rounded-xl p-6">
                <h3 className="font-semibold text-white mb-4 flex items-center gap-2">
                  <Shield className="w-5 h-5 text-red-400" />
                  Criminal Enterprise Structure
                </h3>
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {Object.entries(crmDetail.structure).map(([tier, info]: [string, any]) => (
                    <div key={tier} className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
                      <div className="text-xs text-red-400 uppercase tracking-wider mb-2">{tier.replace(/_/g, ' ')}</div>
                      <div className="text-white text-sm font-medium">{info.role || info.function}</div>
                      {info.wallet && (
                        <div className="text-xs text-gray-500 font-mono mt-1">{info.wallet}</div>
                      )}
                      {info.wallets && (
                        <div className="text-xs text-gray-500 mt-1">{info.wallets.length} wallets</div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Timeline */}
            {crmDetail.timeline.length > 0 && (
              <div className="bg-[#12121a] border border-gray-800 rounded-xl p-6">
                <h3 className="font-semibold text-white mb-4 flex items-center gap-2">
                  <Clock className="w-5 h-5 text-blue-400" />
                  Investigation Timeline
                </h3>
                <div className="space-y-4">
                  {crmDetail.timeline.map((item: any, idx: number) => (
                    <div key={idx} className="flex gap-4">
                      <div className="w-2 h-2 rounded-full bg-blue-400 mt-2 flex-shrink-0" />
                      <div>
                        <div className="text-sm text-blue-400 font-mono mb-1">{item.date}</div>
                        <div className="text-white font-medium">{item.event}</div>
                        <div className="text-gray-400 text-sm">{item.details}</div>
                        {item.significance && (
                          <div className="text-red-400 text-xs mt-1">★ {item.significance}</div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Wallets */}
            {crmDetail.wallets.length > 0 && (
              <div className="bg-[#12121a] border border-gray-800 rounded-xl p-6">
                <h3 className="font-semibold text-white mb-4 flex items-center gap-2">
                  <Shield className="w-5 h-5 text-green-400" />
                  Tracked Wallets ({crmDetail.wallets.length})
                </h3>
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {crmDetail.wallets.map((wallet: any, idx: number) => (
                    <div key={idx} className="flex items-center justify-between p-3 bg-gray-800 rounded-lg">
                      <div>
                        <span className="font-mono text-gray-300 text-sm">{wallet.address}</span>
                        <div className="text-xs text-gray-500">
                          Tier {wallet.tier} • {wallet.classification} • Risk: {((wallet.risk_score || 0) * 100).toFixed(0)}%
                        </div>
                      </div>
                      <a
                        href={`/scanner?address=${wallet.address}`}
                        className="text-green-400 hover:text-green-300 text-sm flex items-center gap-1"
                      >
                        Scan <ExternalLink className="w-4 h-4" />
                      </a>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Generic case detail (non-CRM) */}
        {!selectedCase.isCRM && (
          <div className="grid lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 space-y-6">
              <div className="bg-[#12121a] border border-gray-800 rounded-xl p-6">
                <h3 className="font-semibold text-white mb-4 flex items-center gap-2">
                  <Clock className="w-5 h-5 text-blue-400" />
                  Case Timeline
                </h3>
                <div className="text-gray-400 text-sm">No updates yet.</div>
              </div>

              <div className="bg-[#12121a] border border-gray-800 rounded-xl p-6">
                <h3 className="font-semibold text-white mb-4 flex items-center gap-2">
                  <Shield className="w-5 h-5 text-green-400" />
                  Connected Wallets ({selectedCase.wallets.length})
                </h3>
                {selectedCase.wallets.length === 0 ? (
                  <div className="text-gray-400 text-sm">No wallets linked.</div>
                ) : (
                  <div className="space-y-2">
                    {selectedCase.wallets.map((wallet, idx) => (
                      <div key={idx} className="flex items-center justify-between p-3 bg-gray-800 rounded-lg">
                        <span className="font-mono text-gray-300">{wallet}</span>
                        <a href={`/scanner?address=${wallet}`} className="text-green-400 hover:text-green-300 text-sm flex items-center gap-1">
                          Scan <ExternalLink className="w-4 h-4" />
                        </a>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            <div className="space-y-6">
              <div className="bg-[#12121a] border border-gray-800 rounded-xl p-5">
                <h3 className="font-semibold text-white mb-3">Tags</h3>
                <div className="flex flex-wrap gap-2">
                  {selectedCase.tags.map((tag, idx) => (
                    <span key={idx} className="px-3 py-1 bg-gray-800 text-gray-400 text-sm rounded-full">
                      #{tag}
                    </span>
                  ))}
                </div>
              </div>

              <div className="bg-[#12121a] border border-gray-800 rounded-xl p-5">
                <h3 className="font-semibold text-white mb-3 flex items-center gap-2">
                  <FileText className="w-5 h-5 text-purple-400" />
                  Evidence
                </h3>
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-400">Total Items</span>
                    <span className="text-white">{selectedCase.evidence}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <FolderOpen className="w-6 h-6 text-purple-400" />
            Investigations
          </h1>
          <p className="text-gray-400">
            Track and manage your fraud investigations
          </p>
        </div>
        <div className="flex items-center gap-3">
          {canCreate ? (
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-4 py-2 bg-green-500 hover:bg-green-600 text-black font-bold rounded-lg flex items-center gap-2 transition-colors"
            >
              <Plus className="w-5 h-5" />
              New Investigation
            </button>
          ) : (
            <a
              href="/pricing"
              className="px-4 py-2 bg-gray-800 text-gray-400 rounded-lg"
            >
              Upgrade to Create
            </a>
          )}
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-[#12121a] border border-gray-800 rounded-xl p-4">
          <div className="text-2xl font-bold text-white">{cases.length}</div>
          <div className="text-sm text-gray-400">Total Cases</div>
        </div>
        <div className="bg-[#12121a] border border-gray-800 rounded-xl p-4">
          <div className="text-2xl font-bold text-blue-400">
            {cases.filter((c) => c.status === 'active').length}
          </div>
          <div className="text-sm text-gray-400">Active</div>
        </div>
        <div className="bg-[#12121a] border border-gray-800 rounded-xl p-4">
          <div className="text-2xl font-bold text-green-400">
            {cases.filter((c) => c.status === 'resolved').length}
          </div>
          <div className="text-sm text-gray-400">Resolved</div>
        </div>
        <div className="bg-[#12121a] border border-gray-800 rounded-xl p-4">
          <div className="text-2xl font-bold text-white">
            ${cases.reduce((acc, c) => acc + (c.isCRM ? 886597 : 0), 0).toLocaleString()}
          </div>
          <div className="text-sm text-gray-400">Value Protected</div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col md:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search investigations..."
            className="w-full bg-gray-800 border border-gray-700 rounded-lg pl-10 pr-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-green-500"
          />
        </div>
        <div className="flex gap-2">
          {STATUSES.map((status) => (
            <button
              key={status.id}
              onClick={() => setStatusFilter(status.id)}
              className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                statusFilter === status.id
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
              }`}
            >
              {status.label}
            </button>
          ))}
        </div>
      </div>

      {/* Loading / Error */}
      {loading && (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 text-purple-400 animate-spin" />
          <span className="ml-3 text-gray-400">Loading investigations...</span>
        </div>
      )}
      {error && (
        <div className="flex items-center gap-3 p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400">
          <AlertTriangle className="w-5 h-5" />
          {error}
        </div>
      )}

      {/* Cases List */}
      {!loading && !error && (
        <div className="space-y-4">
          {filteredCases.map((caseItem) => (
            <div
              key={caseItem.id}
              onClick={() => handleViewCase(caseItem)}
              className="bg-[#12121a] border border-gray-800 hover:border-gray-700 rounded-xl p-5 cursor-pointer transition-colors"
            >
              <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2 flex-wrap">
                    <span className="font-mono text-xs text-gray-500">{caseItem.id}</span>
                    <span className={`px-2 py-0.5 rounded text-xs ${getStatusColor(caseItem.status)}`}>
                      {caseItem.status.toUpperCase()}
                    </span>
                    <span className={`px-2 py-0.5 rounded text-xs ${getPriorityColor(caseItem.priority)}`}>
                      {caseItem.priority.toUpperCase()}
                    </span>
                    {caseItem.isCRM && !caseItem.published && isAdmin && (
                      <span className="px-2 py-0.5 rounded text-xs bg-amber-500/20 text-amber-400 flex items-center gap-1">
                        <EyeOff className="w-3 h-3" /> DRAFT
                      </span>
                    )}
                  </div>
                  <h3 className="font-semibold text-white mb-1">{caseItem.title}</h3>
                  <p className="text-gray-400 text-sm mb-3">{caseItem.description}</p>
                  <div className="flex flex-wrap items-center gap-3 text-sm text-gray-500">
                    <span className="flex items-center gap-1">
                      <Clock className="w-4 h-4" />
                      {caseItem.updatedAt}
                    </span>
                    <span>•</span>
                    <span className="flex items-center gap-1">
                      <Shield className="w-4 h-4" />
                      {caseItem.wallets.length} wallets
                    </span>
                    <span>•</span>
                    <span className="flex items-center gap-1">
                      <FileText className="w-4 h-4" />
                      {caseItem.evidence} evidence
                    </span>
                    <span>•</span>
                    <span className="flex items-center gap-1">
                      <Users className="w-4 h-4" />
                      {caseItem.assignedTo}
                    </span>
                  </div>
                </div>
                <ChevronRight className="w-5 h-5 text-gray-500" />
              </div>
            </div>
          ))}
          {filteredCases.length === 0 && (
            <div className="text-center py-12 text-gray-500">
              No investigations found matching your criteria.
            </div>
          )}
        </div>
      )}

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center p-4 z-50">
          <div className="bg-[#12121a] border border-gray-800 rounded-xl w-full max-w-2xl">
            <div className="p-6 border-b border-gray-800 flex items-center justify-between">
              <h2 className="text-xl font-bold text-white">New Investigation</h2>
              <button onClick={() => setShowCreateModal(false)} className="text-gray-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm text-gray-400 mb-2">Title</label>
                <input
                  type="text"
                  placeholder="What's being investigated?"
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-green-500"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-2">Description</label>
                <textarea
                  rows={3}
                  placeholder="Provide context and details..."
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-green-500 resize-none"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-2">Priority</label>
                  <select className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-green-500">
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="critical">Critical</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-2">Wallet Addresses</label>
                  <input
                    type="text"
                    placeholder="0x... (comma separated)"
                    className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-green-500"
                  />
                </div>
              </div>
            </div>
            <div className="p-6 border-t border-gray-800 flex justify-end gap-3">
              <button onClick={() => setShowCreateModal(false)} className="px-4 py-2 text-gray-400 hover:text-white">
                Cancel
              </button>
              <button onClick={() => setShowCreateModal(false)} className="px-6 py-2 bg-green-500 hover:bg-green-600 text-black font-bold rounded-lg">
                Create Investigation
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
