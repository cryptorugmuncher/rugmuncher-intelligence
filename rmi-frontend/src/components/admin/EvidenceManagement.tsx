/**
 * Evidence Management Panel
 * Review, verify, and manage all investigation evidence
 */
import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
// DB import commented out for build
import {
  FileText,
  Search,
  CheckCircle,
  XCircle,
  Clock,
  Shield,
  Link,
  Image,
  FileCode,
  AlertTriangle,
  Trash2,
  RefreshCw,
  Award,
} from 'lucide-react';

const EVIDENCE_TYPES = [
  { id: 'TRANSACTION', label: 'Transaction', icon: FileCode, color: 'blue' },
  { id: 'CONTRACT', label: 'Contract', icon: FileText, color: 'purple' },
  { id: 'SOCIAL', label: 'Social/OSINT', icon: Link, color: 'green' },
  { id: 'SCREENSHOT', label: 'Screenshot', icon: Image, color: 'yellow' },
  { id: 'AI_ANALYSIS', label: 'AI Analysis', icon: Award, color: 'cyan' },
  { id: 'USER_SUBMITTED', label: 'User Submitted', icon: Shield, color: 'orange' },
];

const VERIFICATION_STATUS = ['UNVERIFIED', 'PENDING', 'VERIFIED', 'REJECTED'];

const MOCK_EVIDENCE = [
  { id: 'ev_1', type: 'TRANSACTION', title: 'Suspicious Transfer', description: 'Large ETH transfer to mixer', investigationId: 'inv_1', status: 'VERIFIED', createdAt: '2024-01-15', submittedBy: 'analyst_1', priority: 'HIGH' },
  { id: 'ev_2', type: 'CONTRACT', title: 'Honeypot Contract', description: 'Contract has hidden transfer restrictions', investigationId: 'inv_2', status: 'PENDING', createdAt: '2024-01-14', submittedBy: 'system', priority: 'CRITICAL' },
  { id: 'ev_3', type: 'SOCIAL', title: 'Twitter Intel', description: 'Developer deleted account after launch', investigationId: 'inv_3', status: 'VERIFIED', createdAt: '2024-01-13', submittedBy: 'user_123', priority: 'MEDIUM' },
];

export default function EvidenceManagement() {
  const [searchQuery, setSearchQuery] = useState('');
  const [typeFilter, setTypeFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [selectedEvidence, setSelectedEvidence] = useState<any>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);

  // Fetch all evidence
  const { data: evidence, isLoading: evidenceLoading, refetch } = useQuery({
    queryKey: ['admin-evidence'],
    queryFn: async () => {
      return MOCK_EVIDENCE || [];
    },
  });

  // Fetch investigations for assignment
  const { data: investigations } = useQuery({
    queryKey: ['admin-investigations'],
    queryFn: async () => {
      return [] as any[];
    },
  });

  // Update evidence mutation
  const updateEvidence = useMutation({
    mutationFn: async ({ id, updates }: { id: string; updates: any }) => {
      console.log('Update evidence', id, updates);
      return { success: true };
    },
    onSuccess: () => refetch(),
  });

  // Delete evidence mutation
  const deleteEvidence = useMutation({
    mutationFn: async (id: string) => {
      console.log('Delete evidence', id);
      return { success: true };
    },
    onSuccess: () => refetch(),
  });

  const filteredEvidence = evidence?.filter((e: any) => {
    const matchesSearch =
      e.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      e.source?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      e.wallet_address?.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesType = typeFilter === 'all' || e.evidence_type === typeFilter;
    const matchesStatus = statusFilter === 'all' || e.verification_status === statusFilter;
    return matchesSearch && matchesType && matchesStatus;
  });

  const stats = {
    total: evidence?.length || 0,
    verified: evidence?.filter((e: any) => e.verification_status === 'VERIFIED').length || 0,
    pending: evidence?.filter((e: any) => e.verification_status === 'PENDING').length || 0,
    rejected: evidence?.filter((e: any) => e.verification_status === 'REJECTED').length || 0,
    unverified: evidence?.filter((e: any) => e.verification_status === 'UNVERIFIED').length || 0,
  };

  const getTypeInfo = (type: string) => {
    return EVIDENCE_TYPES.find((t) => t.id === type) || EVIDENCE_TYPES[0];
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'VERIFIED':
        return 'bg-green-500/20 text-green-400';
      case 'PENDING':
        return 'bg-yellow-500/20 text-yellow-400';
      case 'REJECTED':
        return 'bg-red-500/20 text-red-400';
      default:
        return 'bg-gray-500/20 text-gray-400';
    }
  };

  return (
    <div className="space-y-6">
      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <StatCard title="Total Evidence" value={stats.total} icon={FileText} color="blue" />
        <StatCard title="Verified" value={stats.verified} icon={CheckCircle} color="green" />
        <StatCard title="Pending Review" value={stats.pending} icon={Clock} color="yellow" />
        <StatCard title="Rejected" value={stats.rejected} icon={XCircle} color="red" />
        <StatCard title="Unverified" value={stats.unverified} icon={AlertTriangle} color="gray" />
      </div>

      {/* Filters */}
      <div className="crypto-card">
        <div className="flex flex-wrap gap-4">
          <div className="relative flex-1 min-w-[250px]">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search evidence, source, or wallet..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-crypto-dark border border-crypto-border rounded-lg pl-10 pr-4 py-2 text-white"
            />
          </div>
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="bg-crypto-card border border-crypto-border rounded-lg px-3 py-2 text-white"
          >
            <option value="all">All Types</option>
            {EVIDENCE_TYPES.map((t) => (
              <option key={t.id} value={t.id}>{t.label}</option>
            ))}
          </select>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-crypto-card border border-crypto-border rounded-lg px-3 py-2 text-white"
          >
            <option value="all">All Status</option>
            {VERIFICATION_STATUS.map((s) => (
              <option key={s} value={s}>{s}</option>
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

      {/* Evidence Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {evidenceLoading ? (
          <div className="col-span-full text-center py-8 text-gray-500">Loading evidence...</div>
        ) : (
          filteredEvidence?.map((item: any) => {
            const typeInfo = getTypeInfo(item.evidence_type);
            const TypeIcon = typeInfo.icon;

            return (
              <div
                key={item.id}
                className="crypto-card hover:border-neon-blue/30 transition-colors cursor-pointer"
                onClick={() => {
                  setSelectedEvidence(item);
                  setShowDetailModal(true);
                }}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className={`p-2 rounded ${typeInfo.color === 'blue' ? 'bg-blue-500/20' : typeInfo.color === 'purple' ? 'bg-purple-500/20' : typeInfo.color === 'green' ? 'bg-green-500/20' : typeInfo.color === 'yellow' ? 'bg-yellow-500/20' : typeInfo.color === 'cyan' ? 'bg-cyan-500/20' : 'bg-orange-500/20'}`}>
                    <TypeIcon className={`w-5 h-5 ${typeInfo.color === 'blue' ? 'text-blue-400' : typeInfo.color === 'purple' ? 'text-purple-400' : typeInfo.color === 'green' ? 'text-green-400' : typeInfo.color === 'yellow' ? 'text-yellow-400' : typeInfo.color === 'cyan' ? 'text-cyan-400' : 'text-orange-400'}`} />
                  </div>
                  <span className={`px-2 py-1 rounded text-xs ${getStatusColor(item.verification_status)}`}>
                    {item.verification_status}
                  </span>
                </div>

                <h4 className="font-semibold text-white mb-1 line-clamp-1">{item.title || 'Untitled'}</h4>
                <p className="text-sm text-gray-400 mb-2 line-clamp-2">{item.description || 'No description'}</p>

                <div className="flex items-center gap-2 text-xs text-gray-500 mb-3">
                  <span className="font-mono">{item.wallet_address?.slice(0, 8)}...</span>
                  {item.source && (
                    <>
                      <span>•</span>
                      <span>{item.source}</span>
                    </>
                  )}
                </div>

                <div className="flex items-center justify-between pt-3 border-t border-crypto-border">
                  <div className="flex items-center gap-1">
                    <Award className="w-4 h-4 text-gray-400" />
                    <span className="text-sm text-gray-400">{item.confidence || 0}% confidence</span>
                  </div>
                  <span className="text-xs text-gray-500">
                    {new Date(item.collected_at || item.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Detail Modal */}
      {showDetailModal && selectedEvidence && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="crypto-card w-full max-w-2xl max-h-[90vh] overflow-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold text-white">Evidence Details</h3>
              <button
                onClick={() => setShowDetailModal(false)}
                className="text-gray-400 hover:text-white"
              >
                ✕
              </button>
            </div>

            <div className="space-y-4">
              {/* Header Info */}
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-crypto-dark rounded p-3">
                  <label className="text-xs text-gray-500">Type</label>
                  <p className="text-white font-medium">{selectedEvidence.evidence_type}</p>
                </div>
                <div className="bg-crypto-dark rounded p-3">
                  <label className="text-xs text-gray-500">Status</label>
                  <p className={`font-medium ${selectedEvidence.verification_status === 'VERIFIED' ? 'text-green-400' : selectedEvidence.verification_status === 'REJECTED' ? 'text-red-400' : 'text-yellow-400'}`}>
                    {selectedEvidence.verification_status}
                  </p>
                </div>
                <div className="bg-crypto-dark rounded p-3">
                  <label className="text-xs text-gray-500">Confidence</label>
                  <p className="text-white font-medium">{selectedEvidence.confidence || 0}%</p>
                </div>
                <div className="bg-crypto-dark rounded p-3">
                  <label className="text-xs text-gray-500">Collected</label>
                  <p className="text-white font-medium">
                    {new Date(selectedEvidence.collected_at).toLocaleDateString()}
                  </p>
                </div>
              </div>

              {/* Content */}
              <div className="bg-crypto-dark rounded p-4">
                <label className="text-xs text-gray-500 mb-2 block">Content/Data</label>
                <pre className="text-sm text-gray-300 overflow-auto max-h-[200px]">
                  {JSON.stringify(selectedEvidence.content, null, 2)}
                </pre>
              </div>

              {/* Chain of Custody */}
              {selectedEvidence.chain_of_custody && (
                <div className="bg-crypto-dark rounded p-4">
                  <label className="text-xs text-gray-500 mb-2 block">Chain of Custody</label>
                  <div className="space-y-2">
                    {selectedEvidence.chain_of_custody.map((entry: any, idx: number) => (
                      <div key={idx} className="flex items-center gap-2 text-sm">
                        <Clock className="w-4 h-4 text-gray-400" />
                        <span className="text-gray-300">{entry.action}</span>
                        <span className="text-gray-500">by {entry.user_id?.slice(0, 8)}...</span>
                        <span className="text-gray-500">{new Date(entry.timestamp).toLocaleDateString()}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Actions */}
              <div className="flex gap-3 pt-4 border-t border-crypto-border">
                <select
                  className="bg-crypto-card border border-crypto-border rounded px-3 py-2 text-white text-sm"
                  onChange={(e) => {
                    if (e.target.value) {
                      updateEvidence.mutate({
                        id: selectedEvidence.id,
                        updates: { verification_status: e.target.value },
                      });
                    }
                  }}
                  defaultValue=""
                >
                  <option value="">Change Status...</option>
                  <option value="VERIFIED">Mark Verified</option>
                  <option value="REJECTED">Mark Rejected</option>
                  <option value="PENDING">Mark Pending</option>
                </select>

                <select
                  className="bg-crypto-card border border-crypto-border rounded px-3 py-2 text-white text-sm"
                  onChange={(e) => {
                    if (e.target.value) {
                      updateEvidence.mutate({
                        id: selectedEvidence.id,
                        updates: { investigation_id: e.target.value },
                      });
                    }
                  }}
                  defaultValue=""
                >
                  <option value="">Assign to Investigation...</option>
                  {investigations?.map((inv: any) => (
                    <option key={inv.id} value={inv.id}>{inv.title}</option>
                  ))}
                </select>

                <button
                  onClick={() => {
                    if (confirm('Delete this evidence permanently?')) {
                      deleteEvidence.mutate(selectedEvidence.id);
                      setShowDetailModal(false);
                    }
                  }}
                  className="ml-auto btn-secondary text-red-400"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
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
    green: 'text-green-400 bg-green-500/20',
    yellow: 'text-yellow-400 bg-yellow-500/20',
    red: 'text-red-400 bg-red-500/20',
    gray: 'text-gray-400 bg-gray-500/20',
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
