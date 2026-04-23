import { useState } from 'react';
import { Gift, Users, Target, CheckCircle2, AlertTriangle, Clock, Lock, Unlock, ExternalLink, Filter, Download, Upload, Plus, Trash2, BarChart3, PieChart, Zap, Shield, History, ChevronDown, Search, Ban, FileText, Calculator } from 'lucide-react';
import { useAppStore } from '../store/appStore';

interface AirdropRecipient {
  id: string;
  wallet: string;
  v1LossUsd: number;
  v1TokensLost: number;
  calculatedAllocation: number;
  status: 'eligible' | 'claimed' | 'pending_review' | 'blacklisted' | 'excluded';
  proofSubmitted: boolean;
  proofTxHash?: string;
  signupDate?: string;
  claimDate?: string;
  notes: string;
  tags: string[];
}

interface AirdropPhase {
  id: string;
  name: string;
  startDate: string;
  endDate: string;
  allocation: number; // percentage of total airdrop
  recipients: number;
  claimed: number;
  status: 'upcoming' | 'active' | 'completed';
  requirements: string[];
}

interface LiquidityRecoveryPlan {
  id: string;
  holderAddress: string;
  v1TokensHeld: number;
  estimatedLossUsd: number;
  recoveryAllocation: number; // CRM V2 tokens allocated
  recoveryPercent: number; // % of loss being recovered (target 100% = 1:1)
  proofVerified: boolean;
  vestingSchedule: 'immediate' | 'linear_3mo' | 'linear_6mo' | 'linear_12mo';
  status: 'pending' | 'approved' | 'distributed' | 'rejected';
}

const mockRecipients: AirdropRecipient[] = [
  {
    id: '1',
    wallet: '0x742d35Cc6634C0532925a3b8D4B9db96590f6C7E',
    v1LossUsd: 5000,
    v1TokensLost: 2500000,
    calculatedAllocation: 500000,
    status: 'eligible',
    proofSubmitted: true,
    proofTxHash: '0xabc123...',
    signupDate: '2026-03-15',
    notes: 'Verified V1 holder, significant loss',
    tags: ['whale', 'verified']
  },
  {
    id: '2',
    wallet: '0x1234567890abcdef1234567890abcdef12345678',
    v1LossUsd: 500,
    v1TokensLost: 250000,
    calculatedAllocation: 50000,
    status: 'claimed',
    proofSubmitted: true,
    proofTxHash: '0xdef456...',
    signupDate: '2026-03-10',
    claimDate: '2026-04-01',
    notes: 'Early claimer, social advocate',
    tags: ['early', 'community']
  },
  {
    id: '3',
    wallet: '0xabcdef1234567890abcdef1234567890abcdef12',
    v1LossUsd: 1200,
    v1TokensLost: 600000,
    calculatedAllocation: 120000,
    status: 'blacklisted',
    proofSubmitted: false,
    notes: 'Identified as bot/sybil attacker',
    tags: ['bot', 'blacklist']
  },
  {
    id: '4',
    wallet: '0x9876543210fedcba9876543210fedcba98765432',
    v1LossUsd: 250,
    v1TokensLost: 125000,
    calculatedAllocation: 25000,
    status: 'pending_review',
    proofSubmitted: true,
    proofTxHash: '0xghi789...',
    signupDate: '2026-03-20',
    notes: 'Proof under review - unusual transaction pattern',
    tags: ['review']
  },
  {
    id: '5',
    wallet: '0xfedcba0987654321fedcba0987654321fedcba09',
    v1LossUsd: 10000,
    v1TokensLost: 5000000,
    calculatedAllocation: 1000000,
    status: 'eligible',
    proofSubmitted: true,
    proofTxHash: '0xjkl012...',
    signupDate: '2026-03-01',
    notes: 'Major holder, community leader',
    tags: ['whale', 'influencer', 'verified']
  }
];

const mockPhases: AirdropPhase[] = [
  {
    id: '1',
    name: 'Phase 1: V1 Loss Recovery (1:1)',
    startDate: '2026-05-01',
    endDate: '2026-05-15',
    allocation: 40,
    recipients: 1247,
    claimed: 0,
    status: 'upcoming',
    requirements: ['V1 token proof', 'Loss verification', 'KYC optional']
  },
  {
    id: '2',
    name: 'Phase 2: Community Reward',
    startDate: '2026-05-16',
    endDate: '2026-06-01',
    allocation: 25,
    recipients: 5000,
    claimed: 0,
    status: 'upcoming',
    requirements: ['Social engagement', 'RMI tool usage', 'Referral bonus']
  },
  {
    id: '3',
    name: 'Phase 3: Ecosystem Builders',
    startDate: '2026-06-02',
    endDate: '2026-06-30',
    allocation: 20,
    recipients: 250,
    claimed: 0,
    status: 'upcoming',
    requirements: ['Dev contributions', 'Content creation', 'Partnership']
  },
  {
    id: '4',
    name: 'Phase 4: Public Sale Participants',
    startDate: '2026-07-01',
    endDate: '2026-07-15',
    allocation: 15,
    recipients: 10000,
    claimed: 0,
    status: 'upcoming',
    requirements: ['Purchase $50+', 'Hold period 30 days']
  }
];

const mockRecoveryPlans: LiquidityRecoveryPlan[] = [
  {
    id: '1',
    holderAddress: '0x742d35Cc6634C0532925a3b8D4B9db96590f6C7E',
    v1TokensHeld: 2500000,
    estimatedLossUsd: 5000,
    recoveryAllocation: 500000,
    recoveryPercent: 100,
    proofVerified: true,
    vestingSchedule: 'linear_6mo',
    status: 'approved'
  },
  {
    id: '2',
    holderAddress: '0x1234567890abcdef1234567890abcdef12345678',
    v1TokensHeld: 250000,
    estimatedLossUsd: 500,
    recoveryAllocation: 50000,
    recoveryPercent: 100,
    proofVerified: true,
    vestingSchedule: 'immediate',
    status: 'distributed'
  },
  {
    id: '3',
    holderAddress: '0x9876543210fedcba9876543210fedcba98765432',
    v1TokensHeld: 125000,
    estimatedLossUsd: 250,
    recoveryAllocation: 25000,
    recoveryPercent: 100,
    proofVerified: true,
    vestingSchedule: 'linear_3mo',
    status: 'approved'
  }
];

export default function AirdropManager() {
  const { theme } = useAppStore();
  const darkMode = theme === 'dark';

  const [recipients] = useState<AirdropRecipient[]>(mockRecipients);
  const [phases] = useState<AirdropPhase[]>(mockPhases);
  const [recoveryPlans] = useState<LiquidityRecoveryPlan[]>(mockRecoveryPlans);
  const [activeTab, setActiveTab] = useState<'overview' | 'recipients' | 'recovery' | 'phases' | 'blacklist'>('overview');
  const [selectedRecipient, setSelectedRecipient] = useState<string | null>(null);
  const [filterStatus, setFilterStatus] = useState<string>('all');

  const stats = {
    totalRecipients: recipients.length,
    eligible: recipients.filter(r => r.status === 'eligible').length,
    claimed: recipients.filter(r => r.status === 'claimed').length,
    blacklisted: recipients.filter(r => r.status === 'blacklisted').length,
    totalAllocated: recipients.reduce((acc, r) => acc + r.calculatedAllocation, 0),
    totalLoss: recipients.reduce((acc, r) => acc + r.v1LossUsd, 0)
  };

  const filteredRecipients = filterStatus === 'all'
    ? recipients
    : recipients.filter(r => r.status === filterStatus);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'eligible': return 'text-green-400 bg-green-500/10';
      case 'claimed': return 'text-blue-400 bg-blue-500/10';
      case 'blacklisted': return 'text-red-400 bg-red-500/10';
      case 'pending_review': return 'text-yellow-400 bg-yellow-500/10';
      default: return 'text-slate-400 bg-slate-500/10';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
        <div className="flex items-center gap-3 mb-2">
          <Gift className="w-8 h-8 text-purple-500" />
          <h1 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
            AIRDROP COMMAND CENTER
          </h1>
          <span className="px-2 py-1 bg-purple-500/10 text-purple-400 text-xs font-mono rounded">
            PROJECT RECOVERY
          </span>
        </div>
        <p className={`${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
          Managing $CRM V2 airdrop phases with 1:1 liquidity return commitment for V1 holders.
        </p>
      </div>

      {/* Recovery Commitment Banner */}
      <div className="bg-gradient-to-r from-green-600 via-green-700 to-green-800 rounded-lg p-4">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-white/10 rounded-lg">
              <Target className="w-6 h-6 text-white" />
            </div>
            <div>
              <p className="text-green-200 text-sm">V1 HOLDER COMMITMENT</p>
              <p className="text-white text-xl font-bold">1:1 Liquidity Recovery Program</p>
              <p className="text-green-200 text-sm">Every V1 holder receives 100% value recovery in $CRM V2</p>
            </div>
          </div>
          <div className="flex items-center gap-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-white">${stats.totalLoss.toLocaleString()}</p>
              <p className="text-green-200 text-xs">Total V1 Losses</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-white">{stats.totalAllocated.toLocaleString()}</p>
              <p className="text-green-200 text-xs">CRM V2 Allocated</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-white">100%</p>
              <p className="text-green-200 text-xs">Recovery Rate</p>
            </div>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
          <p className="text-2xl font-bold text-white">{stats.totalRecipients}</p>
          <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Total Signups</p>
        </div>
        <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
          <p className="text-2xl font-bold text-green-400">{stats.eligible}</p>
          <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Eligible</p>
        </div>
        <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
          <p className="text-2xl font-bold text-blue-400">{stats.claimed}</p>
          <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Claimed</p>
        </div>
        <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
          <p className="text-2xl font-bold text-red-400">{stats.blacklisted}</p>
          <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Blacklisted</p>
        </div>
        <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
          <p className="text-2xl font-bold text-purple-400">{stats.totalAllocated.toLocaleString()}</p>
          <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Total Allocation</p>
        </div>
      </div>

      {/* Navigation */}
      <div className="flex flex-wrap gap-2">
        {[
          { id: 'overview', label: 'Airdrop Overview', icon: Gift },
          { id: 'recipients', label: 'Recipients', icon: Users },
          { id: 'recovery', label: '1:1 Recovery Plan', icon: Target },
          { id: 'phases', label: 'Distribution Phases', icon: BarChart3 },
          { id: 'blacklist', label: 'Blacklist Management', icon: Ban }
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${
              activeTab === tab.id
                ? 'bg-purple-600 text-white'
                : darkMode
                ? 'bg-slate-800 text-slate-400 hover:text-white'
                : 'bg-white text-slate-600 hover:text-slate-900 border border-slate-200'
            }`}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="grid lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-4">
            <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
              <h3 className={`font-semibold mb-4 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                Distribution Phases
              </h3>
              <div className="space-y-4">
                {phases.map(phase => (
                  <div key={phase.id} className={`p-4 rounded-lg ${darkMode ? 'bg-slate-900/50' : 'bg-slate-50'}`}>
                    <div className="flex items-center justify-between mb-2">
                      <h4 className={`font-medium ${darkMode ? 'text-white' : 'text-slate-900'}`}>{phase.name}</h4>
                      <span className={`px-2 py-1 rounded text-xs ${
                        phase.status === 'active' ? 'bg-green-500/10 text-green-400' :
                        phase.status === 'upcoming' ? 'bg-yellow-500/10 text-yellow-400' :
                        'bg-slate-500/10 text-slate-400'
                      }`}>
                        {phase.status.toUpperCase()}
                      </span>
                    </div>
                    <div className="flex items-center gap-4 text-sm">
                      <span className={darkMode ? 'text-slate-400' : 'text-slate-600'}>
                        {new Date(phase.startDate).toLocaleDateString()} - {new Date(phase.endDate).toLocaleDateString()}
                      </span>
                      <span className="text-purple-400">{phase.allocation}% of supply</span>
                      <span className={darkMode ? 'text-slate-400' : 'text-slate-600'}>
                        {phase.recipients.toLocaleString()} recipients
                      </span>
                    </div>
                    <div className="mt-3 flex flex-wrap gap-1">
                      {phase.requirements.map(req => (
                        <span key={req} className={`text-xs px-2 py-1 rounded ${darkMode ? 'bg-slate-700 text-slate-300' : 'bg-white text-slate-600'}`}>
                          {req}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="space-y-4">
            <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
              <h3 className={`font-semibold mb-4 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                Quick Actions
              </h3>
              <div className="space-y-2">
                <button className="w-full py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg flex items-center justify-center gap-2">
                  <Upload className="w-4 h-4" />
                  Import Recipients
                </button>
                <button className="w-full py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg flex items-center justify-center gap-2">
                  <Download className="w-4 h-4" />
                  Export List
                </button>
                <button className="w-full py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg flex items-center justify-center gap-2">
                  <Calculator className="w-4 h-4" />
                  Recalculate Allocations
                </button>
              </div>
            </div>

            <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
              <h3 className={`font-semibold mb-4 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                Signup Rate
              </h3>
              <div className="text-center">
                <p className="text-4xl font-bold text-purple-400">{((stats.totalRecipients / 5000) * 100).toFixed(1)}%</p>
                <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                  {stats.totalRecipients} of 5,000 target
                </p>
              </div>
              <div className={`h-2 rounded-full mt-4 ${darkMode ? 'bg-slate-700' : 'bg-slate-200'}`}>
                <div className="h-full rounded-full bg-purple-500" style={{ width: `${(stats.totalRecipients / 5000) * 100}%` }} />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Recipients Tab */}
      {activeTab === 'recipients' && (
        <div className={`rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
          <div className="p-4 border-b border-slate-700/50">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <h3 className={`font-semibold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                Recipient Management
              </h3>
              <div className="flex gap-2">
                <select
                  value={filterStatus}
                  onChange={e => setFilterStatus(e.target.value)}
                  className={`px-3 py-2 rounded-lg border ${darkMode ? 'bg-slate-900 border-slate-700 text-white' : 'bg-white border-slate-300'}`}
                >
                  <option value="all">All Statuses</option>
                  <option value="eligible">Eligible</option>
                  <option value="claimed">Claimed</option>
                  <option value="pending_review">Pending Review</option>
                  <option value="blacklisted">Blacklisted</option>
                </select>
                <button className="flex items-center gap-2 px-3 py-2 bg-slate-700 text-white rounded-lg hover:bg-slate-600">
                  <Search className="w-4 h-4" />
                  Search
                </button>
              </div>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className={`${darkMode ? 'bg-slate-900/50' : 'bg-slate-50'}`}>
                <tr>
                  <th className="text-left p-4 text-sm font-medium text-slate-400">Wallet</th>
                  <th className="text-right p-4 text-sm font-medium text-slate-400">V1 Loss</th>
                  <th className="text-right p-4 text-sm font-medium text-slate-400">Allocation</th>
                  <th className="text-center p-4 text-sm font-medium text-slate-400">Status</th>
                  <th className="text-center p-4 text-sm font-medium text-slate-400">Proof</th>
                  <th className="text-left p-4 text-sm font-medium text-slate-400">Tags</th>
                  <th className="text-center p-4 text-sm font-medium text-slate-400">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700/30">
                {filteredRecipients.map(recipient => (
                  <tr key={recipient.id} className="hover:bg-slate-700/10">
                    <td className="p-4">
                      <code className={`text-sm ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>
                        {recipient.wallet.slice(0, 6)}...{recipient.wallet.slice(-4)}
                      </code>
                    </td>
                    <td className="p-4 text-right">
                      <span className="text-red-400">-${recipient.v1LossUsd.toLocaleString()}</span>
                    </td>
                    <td className="p-4 text-right">
                      <span className="text-green-400 font-medium">{recipient.calculatedAllocation.toLocaleString()} CRM</span>
                    </td>
                    <td className="p-4 text-center">
                      <span className={`px-2 py-1 rounded text-xs ${getStatusColor(recipient.status)}`}>
                        {recipient.status.replace('_', ' ').toUpperCase()}
                      </span>
                    </td>
                    <td className="p-4 text-center">
                      {recipient.proofSubmitted ? (
                        <CheckCircle2 className="w-5 h-5 text-green-400 mx-auto" />
                      ) : (
                        <span className="text-slate-500">-</span>
                      )}
                    </td>
                    <td className="p-4">
                      <div className="flex flex-wrap gap-1">
                        {recipient.tags.map(tag => (
                          <span key={tag} className={`text-xs px-2 py-1 rounded ${darkMode ? 'bg-slate-700 text-slate-300' : 'bg-slate-100 text-slate-600'}`}>
                            {tag}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="p-4 text-center">
                      <div className="flex items-center justify-center gap-2">
                        <button className="p-1 text-slate-400 hover:text-white">
                          <FileText className="w-4 h-4" />
                        </button>
                        {recipient.status === 'pending_review' && (
                          <>
                            <button className="p-1 text-green-400 hover:text-green-300">
                              <CheckCircle2 className="w-4 h-4" />
                            </button>
                            <button className="p-1 text-red-400 hover:text-red-300">
                              <Ban className="w-4 h-4" />
                            </button>
                          </>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Recovery Tab */}
      {activeTab === 'recovery' && (
        <div className="space-y-6">
          <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
            <h3 className={`font-semibold mb-4 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
              1:1 Liquidity Recovery Plan
            </h3>
            <p className={`mb-4 ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
              Our commitment: Every dollar lost by V1 holders will be returned as $CRM V2 tokens at launch price equivalent.
              This creates a 100% recovery rate for all legitimate holders.
            </p>

            <div className="grid md:grid-cols-3 gap-4 mb-6">
              <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-900/50' : 'bg-slate-50'}`}>
                <p className="text-2xl font-bold text-green-400">100%</p>
                <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Recovery Rate</p>
              </div>
              <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-900/50' : 'bg-slate-50'}`}>
                <p className="text-2xl font-bold text-purple-400">40%</p>
                <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Supply Allocated</p>
              </div>
              <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-900/50' : 'bg-slate-50'}`}>
                <p className="text-2xl font-bold text-blue-400">1,247</p>
                <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Verified Holders</p>
              </div>
            </div>

            <div className="space-y-3">
              {recoveryPlans.map(plan => (
                <div key={plan.id} className={`p-4 rounded-lg border ${darkMode ? 'border-slate-700' : 'border-slate-200'}`}>
                  <div className="flex items-center justify-between">
                    <div>
                      <code className={`text-sm ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>
                        {plan.holderAddress.slice(0, 10)}...{plan.holderAddress.slice(-8)}
                      </code>
                      <p className="text-sm text-slate-500">
                        {plan.v1TokensHeld.toLocaleString()} V1 tokens • ${plan.estimatedLossUsd.toLocaleString()} loss
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-green-400 font-medium">{plan.recoveryAllocation.toLocaleString()} CRM V2</p>
                      <p className="text-sm text-slate-500">{plan.vestingSchedule.replace('_', ' ')}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 mt-3">
                    <span className={`px-2 py-1 rounded text-xs ${
                      plan.status === 'distributed' ? 'bg-green-500/10 text-green-400' :
                      plan.status === 'approved' ? 'bg-blue-500/10 text-blue-400' :
                      'bg-yellow-500/10 text-yellow-400'
                    }`}>
                      {plan.status.toUpperCase()}
                    </span>
                    {plan.proofVerified && (
                      <span className="px-2 py-1 rounded text-xs bg-purple-500/10 text-purple-400">
                        PROOF VERIFIED
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Phases Tab */}
      {activeTab === 'phases' && (
        <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
          <h3 className={`font-semibold mb-6 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
            Phase Timeline
          </h3>
          <div className="relative">
            <div className={`absolute left-4 top-0 bottom-0 w-0.5 ${darkMode ? 'bg-slate-700' : 'bg-slate-200'}`} />
            <div className="space-y-8">
              {phases.map((phase, idx) => (
                <div key={phase.id} className="relative flex gap-6">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center z-10 ${
                    phase.status === 'completed' ? 'bg-green-500' :
                    phase.status === 'active' ? 'bg-purple-500' :
                    darkMode ? 'bg-slate-700' : 'bg-slate-200'
                  }`}>
                    {phase.status === 'completed' ? <CheckCircle2 className="w-5 h-5 text-white" /> : idx + 1}
                  </div>
                  <div className="flex-1">
                    <h4 className={`font-semibold ${darkMode ? 'text-white' : 'text-slate-900'}`}>{phase.name}</h4>
                    <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                      {new Date(phase.startDate).toLocaleDateString()} - {new Date(phase.endDate).toLocaleDateString()}
                    </p>
                    <div className="flex items-center gap-4 mt-2 text-sm">
                      <span className="text-purple-400">{phase.allocation}% allocation</span>
                      <span className={darkMode ? 'text-slate-500' : 'text-slate-500'}>
                        {phase.recipients.toLocaleString()} recipients
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Blacklist Tab */}
      {activeTab === 'blacklist' && (
        <div className={`rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
          <div className="p-4 border-b border-slate-700/50">
            <h3 className={`font-semibold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
              Blacklist Management
            </h3>
          </div>
          <div className="p-4">
            <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 mb-4">
              <div className="flex items-center gap-2 text-red-400">
                <AlertTriangle className="w-5 h-5" />
                <span className="font-medium">Blacklist Enforcement Active</span>
              </div>
              <p className={`text-sm mt-1 ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                Wallets on this list are blocked from all airdrops. This includes known scammers, bot operators, and V1 bad actors.
              </p>
            </div>

            <div className="space-y-2">
              {recipients.filter(r => r.status === 'blacklisted').map(recipient => (
                <div key={recipient.id} className={`p-3 rounded-lg flex items-center justify-between ${darkMode ? 'bg-slate-900/50' : 'bg-slate-50'}`}>
                  <div>
                    <code className={`text-sm ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>
                      {recipient.wallet}
                    </code>
                    <p className="text-sm text-slate-500">{recipient.notes}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-1 rounded text-xs bg-red-500/10 text-red-400">BLACKLISTED</span>
                    <button className="p-1 text-slate-400 hover:text-white">
                      <FileText className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
