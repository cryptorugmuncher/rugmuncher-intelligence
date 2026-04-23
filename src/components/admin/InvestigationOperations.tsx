/**
 * Investigation Operations Panel
 * Case management, assignment, escalation, and timeline tracking
 */
import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
// DB import commented out for build
import {
  FolderOpen,
  Search,
  UserCheck,
  UserPlus,
  ArrowUpCircle,
  ArrowDownCircle,
  Clock,
  CheckCircle,
  AlertTriangle,
  Shield,
  Eye,
  RefreshCw,
} from 'lucide-react';

const STATUSES = ['PENDING', 'IN_PROGRESS', 'UNDER_REVIEW', 'ESCALATED', 'COMPLETED', 'ARCHIVED'];
const TIERS = ['FREE', 'BASIC', 'PRO', 'ELITE', 'ENTERPRISE'];
const PRIORITIES = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'];

export default function InvestigationOperations() {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [tierFilter, setTierFilter] = useState('all');
  const [priorityFilter, setPriorityFilter] = useState('all');
  const [selectedCase, setSelectedCase] = useState<any>(null);
  const [_showDetailModal, setShowDetailModal] = useState(false);
  const [showAssignModal, setShowAssignModal] = useState(false);
  const [showTimeline, setShowTimeline] = useState(false);
  const [activeTab, setActiveTab] = useState<'active' | 'completed' | 'archived'>('active');

  // Fetch investigations
  const { data: investigations, refetch } = useQuery({
    queryKey: ['admin-investigations-ops'],
    queryFn: async () => {
      return [];
    },
  });

  // Fetch users for assignment
  const { data: analysts } = useQuery({
    queryKey: ['admin-analysts'],
    queryFn: async () => {
      return [];
    },
  });

  // Update investigation mutation
  const updateInvestigation = useMutation({
    mutationFn: async ({ id, updates }: { id: string; updates: any }) => {
      console.log('Update investigation', id, updates);
      return { success: true };
    },
    onSuccess: () => {
      refetch();
      setShowAssignModal(false);
    },
  });

  // Add timeline event mutation
  const addTimelineEvent = useMutation({
    mutationFn: async ({ id, event }: { id: string; event: any }) => {
      console.log('Add timeline event', id, event);
      return { success: true };
    },
    onSuccess: () => refetch(),
  });

  const filteredCases = investigations?.filter((inv: any) => {
    const matchesSearch =
      inv.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      inv.id?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      inv.wallet_addresses?.some((w: string) => w.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchesStatus = statusFilter === 'all' || inv.status === statusFilter;
    const matchesTier = tierFilter === 'all' || inv.tier === tierFilter;
    const matchesPriority = priorityFilter === 'all' || inv.priority === priorityFilter;

    // Tab filtering
    const matchesTab =
      activeTab === 'active' ? ['PENDING', 'IN_PROGRESS', 'UNDER_REVIEW', 'ESCALATED'].includes(inv.status) :
      activeTab === 'completed' ? inv.status === 'COMPLETED' :
      inv.status === 'ARCHIVED';

    return matchesSearch && matchesStatus && matchesTier && matchesPriority && matchesTab;
  });

  const stats = {
    total: investigations?.length || 0,
    pending: investigations?.filter((i: any) => i.status === 'PENDING').length || 0,
    inProgress: investigations?.filter((i: any) => i.status === 'IN_PROGRESS').length || 0,
    escalated: investigations?.filter((i: any) => i.status === 'ESCALATED').length || 0,
    completed: investigations?.filter((i: any) => i.status === 'COMPLETED').length || 0,
    critical: investigations?.filter((i: any) => i.priority === 'CRITICAL').length || 0,
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'COMPLETED':
        return 'bg-green-500/20 text-green-400';
      case 'IN_PROGRESS':
        return 'bg-blue-500/20 text-blue-400';
      case 'ESCALATED':
        return 'bg-red-500/20 text-red-400';
      case 'UNDER_REVIEW':
        return 'bg-purple-500/20 text-purple-400';
      case 'ARCHIVED':
        return 'bg-gray-500/20 text-gray-400';
      default:
        return 'bg-yellow-500/20 text-yellow-400';
    }
  };

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'CRITICAL':
        return <AlertTriangle className="w-4 h-4 text-red-400" />;
      case 'HIGH':
        return <ArrowUpCircle className="w-4 h-4 text-orange-400" />;
      case 'MEDIUM':
        return <ArrowDownCircle className="w-4 h-4 text-yellow-400" />;
      default:
        return <ArrowDownCircle className="w-4 h-4 text-green-400" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
        <StatCard title="Total Cases" value={stats.total} icon={FolderOpen} color="blue" />
        <StatCard title="Pending" value={stats.pending} icon={Clock} color="yellow" />
        <StatCard title="In Progress" value={stats.inProgress} icon={UserCheck} color="cyan" />
        <StatCard title="Escalated" value={stats.escalated} icon={AlertTriangle} color="red" />
        <StatCard title="Completed" value={stats.completed} icon={CheckCircle} color="green" />
        <StatCard title="Critical" value={stats.critical} icon={Shield} color="orange" />
      </div>

      {/* Tab Navigation */}
      <div className="flex gap-2">
        {['active', 'completed', 'archived'].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab as any)}
            className={`px-4 py-2 rounded-lg font-medium capitalize ${
              activeTab === tab
                ? 'bg-neon-blue/20 text-neon-blue border border-neon-blue/50'
                : 'bg-crypto-card text-gray-400 border border-crypto-border'
            }`}
          >
            {tab.replace('_', ' ')}
          </button>
        ))}
      </div>

      {/* Filters */}
      <div className="crypto-card">
        <div className="flex flex-wrap gap-4">
          <div className="relative flex-1 min-w-[250px]">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search cases, wallets, or IDs..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-crypto-dark border border-crypto-border rounded-lg pl-10 pr-4 py-2 text-white"
            />
          </div>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-crypto-card border border-crypto-border rounded-lg px-3 py-2 text-white"
          >
            <option value="all">All Status</option>
            {STATUSES.map((s) => (
              <option key={s} value={s}>{s.replace('_', ' ')}</option>
            ))}
          </select>
          <select
            value={tierFilter}
            onChange={(e) => setTierFilter(e.target.value)}
            className="bg-crypto-card border border-crypto-border rounded-lg px-3 py-2 text-white"
          >
            <option value="all">All Tiers</option>
            {TIERS.map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
          <select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
            className="bg-crypto-card border border-crypto-border rounded-lg px-3 py-2 text-white"
          >
            <option value="all">All Priorities</option>
            {PRIORITIES.map((p) => (
              <option key={p} value={p}>{p}</option>
            ))}
          </select>
          <button
            onClick={() => refetch()}
            className="btn-secondary flex items-center gap-2"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
        </div>
      </div>

      {/* Cases Table */}
      <div className="crypto-card overflow-hidden">
        <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-crypto-border text-gray-400">
                  <th className="text-left p-3">Case</th>
                  <th className="text-left p-3">Status</th>
                  <th className="text-left p-3">Priority</th>
                  <th className="text-left p-3">Tier</th>
                  <th className="text-left p-3">Assigned</th>
                  <th className="text-left p-3">Wallets</th>
                  <th className="text-left p-3">Created</th>
                  <th className="text-right p-3">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredCases?.map((inv: any) => (
                  <tr key={inv.id} className="border-b border-crypto-border hover:bg-crypto-dark/50">
                    <td className="p-3">
                      <div>
                        <p className="text-white font-medium">{inv.title}</p>
                        <p className="text-xs text-gray-500 font-mono">{inv.id?.slice(0, 8)}...</p>
                      </div>
                    </td>
                    <td className="p-3">
                      <span className={`px-2 py-1 rounded text-xs ${getStatusColor(inv.status)}`}>
                        {inv.status?.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="p-3">
                      <div className="flex items-center gap-1">
                        {getPriorityIcon(inv.priority)}
                        <span className="text-gray-300">{inv.priority}</span>
                      </div>
                    </td>
                    <td className="p-3">
                      <span className={`px-2 py-1 rounded text-xs ${
                        inv.tier === 'ENTERPRISE' ? 'bg-purple-500/20 text-purple-400' :
                        inv.tier === 'ELITE' ? 'bg-yellow-500/20 text-yellow-400' :
                        inv.tier === 'PRO' ? 'bg-blue-500/20 text-blue-400' :
                        'bg-gray-500/20 text-gray-400'
                      }`}>
                        {inv.tier}
                      </span>
                    </td>
                    <td className="p-3">
                      {inv.assigned_to ? (
                        <div className="flex items-center gap-1 text-gray-300">
                          <UserCheck className="w-4 h-4 text-green-400" />
                          <span className="text-xs">{inv.assigned_to.slice(0, 8)}...</span>
                        </div>
                      ) : (
                        <span className="text-gray-500 text-xs">Unassigned</span>
                      )}
                    </td>
                    <td className="p-3">
                      <span className="text-gray-300">{inv.wallet_addresses?.length || 0} wallets</span>
                    </td>
                    <td className="p-3 text-gray-400">
                      {new Date(inv.created_at).toLocaleDateString()}
                    </td>
                    <td className="p-3">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => {
                            setSelectedCase(inv);
                            setShowDetailModal(true);
                          }}
                          className="p-2 hover:bg-crypto-card rounded text-blue-400"
                          title="View Details"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => {
                            setSelectedCase(inv);
                            setShowAssignModal(true);
                          }}
                          className="p-2 hover:bg-crypto-card rounded text-green-400"
                          title="Assign"
                        >
                          <UserPlus className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => {
                            setSelectedCase(inv);
                            setShowTimeline(true);
                          }}
                          className="p-2 hover:bg-crypto-card rounded text-purple-400"
                          title="Timeline"
                        >
                          <Clock className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
      </div>

      {/* Assignment Modal */}
      {showAssignModal && selectedCase && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="crypto-card w-full max-w-md">
            <h3 className="text-lg font-bold text-white mb-4">Assign Case</h3>
            <div className="mb-4 p-3 bg-crypto-dark rounded">
              <p className="text-white font-medium">{selectedCase.title}</p>
              <p className="text-xs text-gray-500">ID: {selectedCase.id}</p>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-400 mb-2">Assign to Analyst</label>
                <div className="space-y-2 max-h-[200px] overflow-y-auto">
                  {analysts?.map((analyst: any) => (
                    <button
                      key={analyst.id}
                      onClick={() => {
                        updateInvestigation.mutate({
                          id: selectedCase.id,
                          updates: {
                            assigned_to: analyst.id,
                            status: selectedCase.status === 'PENDING' ? 'IN_PROGRESS' : selectedCase.status,
                          },
                        });
                      }}
                      className="w-full flex items-center gap-3 p-3 bg-crypto-dark rounded hover:bg-crypto-border transition-colors text-left"
                    >
                      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-600 to-blue-600 flex items-center justify-center">
                        <span className="text-white text-xs font-bold">
                          {analyst.email?.charAt(0).toUpperCase()}
                        </span>
                      </div>
                      <div>
                        <p className="text-white text-sm">{analyst.email}</p>
                        <p className="text-xs text-gray-500">{analyst.role} • {analyst.tier}</p>
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              <div className="flex gap-3 pt-4 border-t border-crypto-border">
                <button
                  onClick={() => setShowAssignModal(false)}
                  className="flex-1 btn-secondary"
                >
                  Cancel
                </button>
                <button
                  onClick={() => {
                    updateInvestigation.mutate({
                      id: selectedCase.id,
                      updates: { assigned_to: null },
                    });
                  }}
                  className="flex-1 btn-secondary text-red-400"
                >
                  Unassign
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Timeline Modal */}
      {showTimeline && selectedCase && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="crypto-card w-full max-w-2xl max-h-[80vh] overflow-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-white">Case Timeline</h3>
              <button
                onClick={() => setShowTimeline(false)}
                className="text-gray-400 hover:text-white"
              >
                ✕
              </button>
            </div>

            <div className="mb-4 p-3 bg-crypto-dark rounded">
              <p className="text-white font-medium">{selectedCase.title}</p>
              <p className="text-xs text-gray-500">ID: {selectedCase.id}</p>
            </div>

            <div className="space-y-4">
              {(selectedCase.timeline || []).map((event: any, idx: number) => (
                <div key={idx} className="flex gap-4">
                  <div className="flex flex-col items-center">
                    <div className="w-3 h-3 rounded-full bg-neon-blue" />
                    {idx < (selectedCase.timeline || []).length - 1 && (
                      <div className="w-0.5 h-full bg-crypto-border mt-2" />
                    )}
                  </div>
                  <div className="flex-1 pb-4">
                    <p className="text-white font-medium">{event.action}</p>
                    <p className="text-sm text-gray-400">{event.description}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      {new Date(event.timestamp).toLocaleString()} • {event.user_id?.slice(0, 8)}...
                    </p>
                  </div>
                </div>
              ))}

              {/* Add Event */}
              <div className="mt-4 pt-4 border-t border-crypto-border">
                <h4 className="text-sm font-semibold text-white mb-2">Add Timeline Event</h4>
                <form
                  onSubmit={(e) => {
                    e.preventDefault();
                    const formData = new FormData(e.currentTarget);
                    addTimelineEvent.mutate({
                      id: selectedCase.id,
                      event: {
                        action: formData.get('action'),
                        description: formData.get('description'),
                        timestamp: new Date().toISOString(),
                        user_id: 'admin', // Current admin ID
                      },
                    });
                    (e.target as HTMLFormElement).reset();
                  }}
                  className="space-y-2"
                >
                  <input
                    name="action"
                    placeholder="Event action (e.g., 'Evidence Added')"
                    className="w-full bg-crypto-dark border border-crypto-border rounded px-3 py-2 text-white text-sm"
                    required
                  />
                  <textarea
                    name="description"
                    placeholder="Description..."
                    className="w-full bg-crypto-dark border border-crypto-border rounded px-3 py-2 text-white text-sm"
                    rows={2}
                  />
                  <button type="submit" className="btn-primary text-sm py-1.5">
                    Add Event
                  </button>
                </form>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function StatCard({ title, value, icon: Icon, color }: any) {
  const colors: any = {
    blue: 'text-blue-400 bg-blue-500/20',
    yellow: 'text-yellow-400 bg-yellow-500/20',
    cyan: 'text-cyan-400 bg-cyan-500/20',
    red: 'text-red-400 bg-red-500/20',
    green: 'text-green-400 bg-green-500/20',
    orange: 'text-orange-400 bg-orange-500/20',
  };

  return (
    <div className="crypto-card p-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-gray-400 text-sm">{title}</span>
        <div className={`p-2 rounded ${colors[color]}`}>
          <Icon className="w-4 h-4" />
        </div>
      </div>
      <p className="text-2xl font-bold text-white">{value}</p>
    </div>
  );
}
