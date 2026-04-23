/**
 * Evidence System - Submit and view evidence for investigations
 */
import { useState } from 'react';
import { 
  FileText, 
  Upload, 
  Image, 
  Link, 
  Shield,
  CheckCircle,
  Clock,
  AlertTriangle,
  Search,
  ChevronDown,
  ChevronUp,
  ExternalLink,
  MessageSquare,
  Plus,
  X
} from 'lucide-react';
import { useAppStore } from '../store/appStore';

const EVIDENCE_TYPES = [
  { id: 'transaction', label: 'Transaction Hash', icon: Link },
  { id: 'screenshot', label: 'Screenshot', icon: Image },
  { id: 'contract', label: 'Contract Code', icon: FileText },
  { id: 'social', label: 'Social Media', icon: MessageSquare },
  { id: 'other', label: 'Other', icon: Shield },
];

const STATUS_OPTIONS = [
  { id: 'all', label: 'All Status' },
  { id: 'pending', label: 'Pending Review' },
  { id: 'verified', label: 'Verified' },
  { id: 'rejected', label: 'Rejected' },
];

const MOCK_EVIDENCE = [
  {
    id: 'EVD-001',
    type: 'transaction',
    title: 'Liquidity Drain Transaction',
    description: 'Contract owner removed 450 ETH from LP in single transaction',
    hash: '0x742d35cc6634c0532925a3b844bc9e7595f0beb57e2e7c5d1c4e243a4d7e47a',
    status: 'verified',
    priority: 'high',
    submittedBy: 'RugHunter_007',
    submittedAt: '2 hours ago',
    investigation: 'INV-2024-001',
    chain: 'ethereum',
  },
  {
    id: 'EVD-002',
    type: 'screenshot',
    title: 'Deleted Announcement',
    description: 'Screenshot of deleted Twitter post promising locked liquidity',
    status: 'verified',
    priority: 'medium',
    submittedBy: 'WhaleWatcher',
    submittedAt: '5 hours ago',
    investigation: 'INV-2024-001',
    chain: 'ethereum',
  },
  {
    id: 'EVD-003',
    type: 'contract',
    title: 'Hidden Mint Function',
    description: 'Contract contains hidden mint function in fallback handler',
    hash: '0x9c4f2d8a1b3e7f5c6a8d0e2f4b6c8a0d2e4f6b8c0a2d4e6f8b0c2d4e6f8b0c',
    status: 'pending',
    priority: 'critical',
    submittedBy: 'DeFi_Detective',
    submittedAt: '1 day ago',
    investigation: 'INV-2024-002',
    chain: 'bsc',
  },
  {
    id: 'EVD-004',
    type: 'social',
    title: 'Developer Discord Messages',
    description: 'Discord logs showing dev admitting to planned rug',
    status: 'verified',
    priority: 'high',
    submittedBy: 'ChainSleuth',
    submittedAt: '2 days ago',
    investigation: 'INV-2024-003',
    chain: 'ethereum',
  },
];

export default function EvidencePage() {
  const [view, setView] = useState<'list' | 'submit'>('list');
  const [selectedType, setSelectedType] = useState('transaction');
  const [statusFilter, setStatusFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [submitForm, setSubmitForm] = useState({
    title: '',
    description: '',
    hash: '',
    chain: 'ethereum',
    files: [] as File[],
  });

  const user = useAppStore((state) => state.user);
  const tier = user?.tier || 'FREE';
  const canSubmit = tier !== 'FREE';

  const filteredEvidence = MOCK_EVIDENCE.filter(item => {
    if (statusFilter !== 'all' && item.status !== statusFilter) return false;
    if (searchQuery && !item.title.toLowerCase().includes(searchQuery.toLowerCase())) return false;
    return true;
  });

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'verified': return <CheckCircle className="w-5 h-5 text-green-400" />;
      case 'pending': return <Clock className="w-5 h-5 text-yellow-400" />;
      case 'rejected': return <AlertTriangle className="w-5 h-5 text-red-400" />;
      default: return <Shield className="w-5 h-5 text-gray-400" />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return 'bg-red-500/20 text-red-400';
      case 'high': return 'bg-orange-500/20 text-orange-400';
      case 'medium': return 'bg-yellow-500/20 text-yellow-400';
      default: return 'bg-gray-500/20 text-gray-400';
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Simulate submission
    setView('list');
    setSubmitForm({ title: '', description: '', hash: '', chain: 'ethereum', files: [] });
  };

  if (view === 'submit') {
    return (
      <div className="max-w-3xl mx-auto">
        <button 
          onClick={() => setView('list')}
          className="flex items-center gap-2 text-gray-400 hover:text-white mb-6"
        >
          ← Back to Evidence
        </button>

        <div className="bg-[#12121a] border border-gray-800 rounded-xl p-6">
          <h2 className="text-2xl font-bold text-white mb-2">Submit Evidence</h2>
          <p className="text-gray-400 mb-6">
            Help the community by submitting verifiable evidence of scams or suspicious activity.
          </p>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Evidence Type */}
            <div>
              <label className="block text-sm text-gray-400 mb-3">Evidence Type</label>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                {EVIDENCE_TYPES.map((type) => (
                  <button
                    key={type.id}
                    type="button"
                    onClick={() => setSelectedType(type.id)}
                    className={`p-3 rounded-lg border text-center transition-colors ${
                      selectedType === type.id
                        ? 'border-green-500 bg-green-500/10 text-green-400'
                        : 'border-gray-700 bg-gray-800 text-gray-400 hover:border-gray-600'
                    }`}
                  >
                    <type.icon className="w-5 h-5 mx-auto mb-1" />
                    <span className="text-xs">{type.label}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Title */}
            <div>
              <label className="block text-sm text-gray-400 mb-2">Title</label>
              <input
                type="text"
                value={submitForm.title}
                onChange={(e) => setSubmitForm({...submitForm, title: e.target.value})}
                placeholder="Brief description of the evidence"
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-green-500"
                required
              />
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm text-gray-400 mb-2">Description</label>
              <textarea
                value={submitForm.description}
                onChange={(e) => setSubmitForm({...submitForm, description: e.target.value})}
                placeholder="Detailed explanation of what this evidence shows..."
                rows={4}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-green-500 resize-none"
                required
              />
            </div>

            {/* Chain */}
            <div>
              <label className="block text-sm text-gray-400 mb-2">Blockchain</label>
              <select
                value={submitForm.chain}
                onChange={(e) => setSubmitForm({...submitForm, chain: e.target.value})}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-green-500"
              >
                <option value="ethereum">Ethereum</option>
                <option value="bsc">BSC</option>
                <option value="polygon">Polygon</option>
                <option value="arbitrum">Arbitrum</option>
                <option value="base">Base</option>
                <option value="solana">Solana</option>
              </select>
            </div>

            {/* Hash / Link */}
            {(selectedType === 'transaction' || selectedType === 'contract') && (
              <div>
                <label className="block text-sm text-gray-400 mb-2">
                  {selectedType === 'transaction' ? 'Transaction Hash' : 'Contract Address'}
                </label>
                <input
                  type="text"
                  value={submitForm.hash}
                  onChange={(e) => setSubmitForm({...submitForm, hash: e.target.value})}
                  placeholder="0x..."
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-green-500 font-mono"
                />
              </div>
            )}

            {/* File Upload */}
            <div>
              <label className="block text-sm text-gray-400 mb-2">Attachments</label>
              <div className="border-2 border-dashed border-gray-700 rounded-lg p-8 text-center hover:border-gray-600 transition-colors">
                <Upload className="w-8 h-8 text-gray-500 mx-auto mb-2" />
                <p className="text-gray-400 text-sm mb-1">Drag and drop files here</p>
                <p className="text-gray-500 text-xs">or click to browse (max 10MB)</p>
                <input
                  type="file"
                  multiple
                  className="hidden"
                  onChange={(e) => setSubmitForm({...submitForm, files: Array.from(e.target.files || [])})}
                />
              </div>
              {submitForm.files.length > 0 && (
                <div className="mt-3 space-y-2">
                  {submitForm.files.map((file, idx) => (
                    <div key={idx} className="flex items-center justify-between p-2 bg-gray-800 rounded-lg">
                      <span className="text-sm text-gray-300">{file.name}</span>
                      <button
                        type="button"
                        onClick={() => setSubmitForm({...submitForm, files: submitForm.files.filter((_, i) => i !== idx)})}
                        className="text-red-400 hover:text-red-300"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Submit Buttons */}
            <div className="flex gap-4 pt-4">
              <button
                type="button"
                onClick={() => setView('list')}
                className="flex-1 py-3 bg-gray-800 hover:bg-gray-700 text-white rounded-lg font-medium transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="flex-1 py-3 bg-green-500 hover:bg-green-600 text-black font-bold rounded-lg transition-colors"
              >
                Submit Evidence
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <FileText className="w-6 h-6 text-green-400" />
            Evidence
          </h1>
          <p className="text-gray-400">
            Submit and view verified evidence for investigations
          </p>
        </div>
        <div className="flex items-center gap-3">
          {canSubmit ? (
            <button
              onClick={() => setView('submit')}
              className="px-4 py-2 bg-green-500 hover:bg-green-600 text-black font-bold rounded-lg flex items-center gap-2 transition-colors"
            >
              <Plus className="w-5 h-5" />
              Submit Evidence
            </button>
          ) : (
            <a
              href="/pricing"
              className="px-4 py-2 bg-gray-800 text-gray-400 rounded-lg"
            >
              Upgrade to Submit
            </a>
          )}
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-[#12121a] border border-gray-800 rounded-xl p-4">
          <div className="text-2xl font-bold text-white">1,247</div>
          <div className="text-sm text-gray-400">Total Evidence</div>
        </div>
        <div className="bg-[#12121a] border border-gray-800 rounded-xl p-4">
          <div className="text-2xl font-bold text-green-400">892</div>
          <div className="text-sm text-gray-400">Verified</div>
        </div>
        <div className="bg-[#12121a] border border-gray-800 rounded-xl p-4">
          <div className="text-2xl font-bold text-yellow-400">234</div>
          <div className="text-sm text-gray-400">Pending</div>
        </div>
        <div className="bg-[#12121a] border border-gray-800 rounded-xl p-4">
          <div className="text-2xl font-bold text-white">94.2%</div>
          <div className="text-sm text-gray-400">Verification Rate</div>
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
            placeholder="Search evidence..."
            className="w-full bg-gray-800 border border-gray-700 rounded-lg pl-10 pr-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-green-500"
          />
        </div>
        <div className="flex gap-2">
          {STATUS_OPTIONS.map((status) => (
            <button
              key={status.id}
              onClick={() => setStatusFilter(status.id)}
              className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                statusFilter === status.id
                  ? 'bg-green-500 text-black'
                  : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
              }`}
            >
              {status.label}
            </button>
          ))}
        </div>
      </div>

      {/* Evidence List */}
      <div className="space-y-4">
        {filteredEvidence.map((item) => {
          const Icon = EVIDENCE_TYPES.find(t => t.id === item.type)?.icon || Shield;
          const isExpanded = expandedId === item.id;
          
          return (
            <div
              key={item.id}
              className="bg-[#12121a] border border-gray-800 hover:border-gray-700 rounded-xl overflow-hidden transition-colors"
            >
              <div className="p-5">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-gray-800 rounded-lg flex items-center justify-center">
                      <Icon className="w-5 h-5 text-green-400" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs text-gray-500">{item.id}</span>
                        <span className={`px-2 py-0.5 rounded text-xs ${getPriorityColor(item.priority)}`}>
                          {item.priority.toUpperCase()}
                        </span>
                      </div>
                      <h3 className="font-semibold text-white">{item.title}</h3>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {getStatusIcon(item.status)}
                    <span className={`text-sm capitalize ${
                      item.status === 'verified' ? 'text-green-400' :
                      item.status === 'pending' ? 'text-yellow-400' :
                      'text-red-400'
                    }`}>
                      {item.status}
                    </span>
                  </div>
                </div>

                <p className="text-gray-400 text-sm mb-3">{item.description}</p>

                <div className="flex items-center gap-4 text-sm text-gray-500">
                  <span>By {item.submittedBy}</span>
                  <span>•</span>
                  <span>{item.submittedAt}</span>
                  <span>•</span>
                  <span className="capitalize">{item.chain}</span>
                  {item.investigation && (
                    <>
                      <span>•</span>
                      <span className="text-green-400">{item.investigation}</span>
                    </>
                  )}
                </div>

                {item.hash && (
                  <div className="mt-3 p-2 bg-gray-800 rounded-lg font-mono text-xs text-gray-400 truncate">
                    {item.hash}
                  </div>
                )}

                <button
                  onClick={() => setExpandedId(isExpanded ? null : item.id)}
                  className="mt-3 text-sm text-green-400 hover:text-green-300 flex items-center gap-1"
                >
                  {isExpanded ? (
                    <>Less details <ChevronUp className="w-4 h-4" /></>
                  ) : (
                    <>More details <ChevronDown className="w-4 h-4" /></>
                  )}
                </button>

                {isExpanded && (
                  <div className="mt-4 pt-4 border-t border-gray-800 space-y-3">
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-gray-500">Evidence ID:</span>
                        <span className="text-white ml-2">{item.id}</span>
                      </div>
                      <div>
                        <span className="text-gray-500">Investigation:</span>
                        <span className="text-white ml-2">{item.investigation}</span>
                      </div>
                      <div>
                        <span className="text-gray-500">Chain:</span>
                        <span className="text-white ml-2 capitalize">{item.chain}</span>
                      </div>
                      <div>
                        <span className="text-gray-500">Status:</span>
                        <span className={`ml-2 capitalize ${
                          item.status === 'verified' ? 'text-green-400' :
                          item.status === 'pending' ? 'text-yellow-400' :
                          'text-red-400'
                        }`}>{item.status}</span>
                      </div>
                    </div>
                    {item.hash && (
                      <a
                        href={`https://etherscan.io/tx/${item.hash}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-2 px-3 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm text-gray-300 transition-colors"
                      >
                        <ExternalLink className="w-4 h-4" />
                        View on Explorer
                      </a>
                    )}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
