import React, { useState } from 'react';
import {
  Users,
  Vote,
  Shield,
  Ban,
  CheckCircle,
  XCircle,
  Clock,
  FileText,
  ExternalLink,
  Plus,
  Search,
  Filter,
  ChevronDown,
  ChevronUp,
  AlertTriangle,
  Lock,
  Unlock,
  Wallet,
  Target,
  BarChart3,
  RefreshCw,
  MessageSquare,
  Gavel,
  Coins,
  Activity,
  Zap
} from 'lucide-react';

interface Proposal {
  id: string;
  title: string;
  description: string;
  proposer: string;
  status: 'active' | 'passed' | 'rejected' | 'pending' | 'executed';
  votes: { for: number; against: number; abstain: number };
  quorum: number;
  threshold: number;
  createdAt: string;
  endsAt: string;
  category: 'treasury' | 'governance' | 'technical' | 'tokenomics';
  executed?: boolean;
}

interface BlacklistEntry {
  id: string;
  address: string;
  reason: string;
  source: 'scam' | 'exploit' | 'sybil' | 'manipulation' | 'legal';
  evidence: string[];
  addedAt: string;
  addedBy: string;
  appealStatus: 'none' | 'pending' | 'approved' | 'rejected';
  crmV1Holder: boolean;
  estimatedLoss?: string;
}

interface AirdropClaim {
  id: string;
  address: string;
  amount: string;
  status: 'pending' | 'claimed' | 'blocked' | 'expired';
  claimedAt?: string;
  eligible: boolean;
  reason?: string;
  verified: boolean;
  kycStatus: 'none' | 'pending' | 'verified' | 'failed';
}

const DAOManagement: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'proposals' | 'blacklist' | 'airdrop' | 'treasury'>('proposals');
  const [expandedProposal, setExpandedProposal] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  const proposals: Proposal[] = [
    {
      id: 'p1',
      title: 'Increase Treasury Buyback Allocation to 5%',
      description: 'Current buyback allocation is 2% of monthly revenue. Proposal to increase to 5% to accelerate token burns and price support.',
      proposer: '0x742d...8f3a',
      status: 'active',
      votes: { for: 2450000, against: 890000, abstain: 120000 },
      quorum: 3000000,
      threshold: 66,
      createdAt: '2026-04-10',
      endsAt: '2026-04-17',
      category: 'treasury'
    },
    {
      id: 'p2',
      title: 'Add Base Chain Liquidity Pool',
      description: 'Allocate $200K from treasury to create CRM/ETH liquidity pool on Base chain to reduce gas costs for users.',
      proposer: '0x91ab...2e4c',
      status: 'passed',
      votes: { for: 3200000, against: 450000, abstain: 230000 },
      quorum: 3000000,
      threshold: 66,
      createdAt: '2026-03-25',
      endsAt: '2026-04-01',
      category: 'technical',
      executed: true
    },
    {
      id: 'p3',
      title: 'Emergency: Block Exploiter Addresses from Airdrop',
      description: 'Block 23 known exploiter addresses identified in CRM V1 from claiming V2 airdrop. Addresses involved in flash loan attacks.',
      proposer: '0x3f9c...7b1d',
      status: 'executed',
      votes: { for: 4100000, against: 120000, abstain: 50000 },
      quorum: 3000000,
      threshold: 66,
      createdAt: '2026-04-05',
      endsAt: '2026-04-06',
      category: 'governance',
      executed: true
    }
  ];

  const blacklist: BlacklistEntry[] = [
    {
      id: 'b1',
      address: '0x1234...5678',
      reason: 'Flash loan attack on CRM V1 staking contract',
      source: 'exploit',
      evidence: ['Transaction: 0xabc...', 'Attack analysis report', 'Loss calculation: 450 ETH'],
      addedAt: '2025-08-15',
      addedBy: 'Security Council',
      appealStatus: 'rejected',
      crmV1Holder: true,
      estimatedLoss: '$135,000'
    },
    {
      id: 'b2',
      address: '0xabcd...efgh',
      reason: 'Sybil attack - 234 addresses controlled by single entity',
      source: 'sybil',
      evidence: ['On-chain clustering analysis', 'Fund flow tracing', 'Same deposit pattern'],
      addedAt: '2026-02-20',
      addedBy: 'DAO Vote #47',
      appealStatus: 'none',
      crmV1Holder: true,
      estimatedLoss: 'N/A'
    },
    {
      id: 'b3',
      address: '0x9876...5432',
      reason: 'Rug pull creator - launched 3 confirmed scams',
      source: 'scam',
      evidence: ['Contract deployer analysis', 'Previous rug pull reports', 'Community complaints'],
      addedAt: '2026-01-10',
      addedBy: 'Community Vote',
      appealStatus: 'pending',
      crmV1Holder: false,
      estimatedLoss: '$2.3M (total victim losses)'
    }
  ];

  const airdropClaims: AirdropClaim[] = [
    { id: 'a1', address: '0x1111...2222', amount: '50,000 CRM', status: 'claimed', claimedAt: '2026-04-14 10:30', eligible: true, verified: true, kycStatus: 'verified' },
    { id: 'a2', address: '0x3333...4444', amount: '25,000 CRM', status: 'pending', eligible: true, verified: false, kycStatus: 'pending' },
    { id: 'a3', address: '0x5555...6666', amount: '100,000 CRM', status: 'blocked', eligible: false, reason: 'Address blacklisted - exploit participant', verified: true, kycStatus: 'failed' },
    { id: 'a4', address: '0x7777...8888', amount: '10,000 CRM', status: 'pending', eligible: true, verified: true, kycStatus: 'none' },
    { id: 'a5', address: '0x9999...0000', amount: '5,000 CRM', status: 'expired', eligible: true, verified: true, kycStatus: 'verified' },
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-blue-500/20 text-blue-400';
      case 'passed': return 'bg-green-500/20 text-green-400';
      case 'rejected': return 'bg-red-500/20 text-red-400';
      case 'executed': return 'bg-purple-500/20 text-purple-400';
      case 'pending': return 'bg-yellow-500/20 text-yellow-400';
      case 'claimed': return 'bg-green-500/20 text-green-400';
      case 'blocked': return 'bg-red-500/20 text-red-400';
      case 'expired': return 'bg-gray-700 text-gray-400';
      default: return 'bg-gray-700 text-gray-400';
    }
  };

  const getSourceColor = (source: string) => {
    switch (source) {
      case 'exploit': return 'text-red-400';
      case 'scam': return 'text-orange-400';
      case 'sybil': return 'text-yellow-400';
      case 'manipulation': return 'text-purple-400';
      case 'legal': return 'text-blue-400';
      default: return 'text-gray-400';
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0812] text-gray-100 font-mono selection:bg-[#7c3aed]/30">
      {/* Header */}
      <div className="bg-gradient-to-r from-[#0f0c1d] via-[#1a1525] to-[#0f0c1d] border-b border-[#7c3aed]/30">
        <div className="max-w-[1600px] mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Users className="w-8 h-8 text-[#7c3aed]" />
              <div>
                <h1 className="text-xl font-bold tracking-wider">
                  DAO <span className="text-[#7c3aed]">GOVERNANCE</span>
                </h1>
                <p className="text-xs text-gray-500 tracking-[0.2em]">DECENTRALIZED MANAGEMENT & VOTING</p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <div className="text-right">
                <div className="text-xs text-gray-500">Total Voting Power</div>
                <div className="text-xl font-bold text-[#7c3aed]">8.2M CRM</div>
              </div>
              <div className="text-right">
                <div className="text-xs text-gray-500">Active Proposals</div>
                <div className="text-xl font-bold text-green-400">1</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-[1600px] mx-auto p-6 space-y-6">
        {/* Stats */}
        <div className="grid grid-cols-5 gap-4">
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-5">
            <Vote className="w-6 h-6 text-[#7c3aed] mb-2" />
            <div className="text-2xl font-bold">24</div>
            <div className="text-xs text-gray-500">Total Proposals</div>
          </div>
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-5">
            <Ban className="w-6 h-6 text-red-400 mb-2" />
            <div className="text-2xl font-bold">23</div>
            <div className="text-xs text-gray-500">Blacklisted</div>
          </div>
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-5">
            <Coins className="w-6 h-6 text-green-400 mb-2" />
            <div className="text-2xl font-bold">12.5K</div>
            <div className="text-xs text-gray-500">Airdrop Claims</div>
          </div>
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-5">
            <Activity className="w-6 h-6 text-blue-400 mb-2" />
            <div className="text-2xl font-bold">67%</div>
            <div className="text-xs text-gray-500">Participation Rate</div>
          </div>
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-5">
            <Wallet className="w-6 h-6 text-yellow-400 mb-2" />
            <div className="text-2xl font-bold">$4.2M</div>
            <div className="text-xs text-gray-500">Treasury Value</div>
          </div>
        </div>

        {/* Navigation */}
        <div className="flex items-center gap-1 border-b border-gray-800">
          {[
            { id: 'proposals', label: 'PROPOSALS', icon: <FileText className="w-4 h-4" /> },
            { id: 'blacklist', label: 'BLACKLIST', icon: <Ban className="w-4 h-4" /> },
            { id: 'airdrop', label: 'AIRDROP CLAIMS', icon: <Coins className="w-4 h-4" /> },
            { id: 'treasury', label: 'TREASURY', icon: <Wallet className="w-4 h-4" /> },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 px-4 py-3 text-xs font-semibold tracking-wider transition-all border-b-2 ${
                activeTab === tab.id
                  ? 'text-[#7c3aed] border-[#7c3aed]'
                  : 'text-gray-500 border-transparent hover:text-gray-300'
              }`}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </div>

        {/* Content */}
        {activeTab === 'proposals' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-bold">Governance Proposals</h2>
              <button className="flex items-center gap-2 px-4 py-2 bg-[#7c3aed] text-white rounded hover:bg-[#6d28d9] transition-all">
                <Plus className="w-4 h-4" />
                CREATE PROPOSAL
              </button>
            </div>

            {proposals.map((proposal) => (
              <div key={proposal.id} className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg overflow-hidden">
                <div
                  className="p-5 cursor-pointer"
                  onClick={() => setExpandedProposal(expandedProposal === proposal.id ? null : proposal.id)}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <span className={`px-2 py-1 rounded text-[10px] font-bold ${getStatusColor(proposal.status)}`}>
                        {proposal.status.toUpperCase()}
                      </span>
                      <span className="px-2 py-1 bg-gray-800 rounded text-[10px] text-gray-400 uppercase">
                        {proposal.category}
                      </span>
                    </div>
                    <div className="text-xs text-gray-500">
                      {proposal.status === 'active' ? `Ends: ${proposal.endsAt}` : `Ended: ${proposal.endsAt}`}
                    </div>
                  </div>

                  <h3 className="font-semibold text-lg mb-2">{proposal.title}</h3>
                  <p className="text-sm text-gray-400 mb-4">{proposal.description}</p>

                  {/* Vote Progress */}
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-green-400">FOR: {(proposal.votes.for / 1000000).toFixed(2)}M CRM</span>
                      <span className="text-gray-500">{((proposal.votes.for / (proposal.votes.for + proposal.votes.against + proposal.votes.abstain)) * 100).toFixed(1)}%</span>
                    </div>
                    <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                      <div className="h-full bg-green-500 rounded-full" style={{ width: `${(proposal.votes.for / (proposal.votes.for + proposal.votes.against + proposal.votes.abstain)) * 100}%` }} />
                    </div>
                    <div className="flex justify-between text-xs text-gray-500">
                      <span>Against: {(proposal.votes.against / 1000000).toFixed(2)}M</span>
                      <span>Abstain: {(proposal.votes.abstain / 1000000).toFixed(2)}M</span>
                    </div>
                  </div>

                  {/* Quorum Indicator */}
                  <div className="mt-4 pt-3 border-t border-gray-800 flex items-center justify-between text-xs">
                    <span className="text-gray-500">Quorum: {((proposal.votes.for + proposal.votes.against + proposal.votes.abstain) / proposal.quorum * 100).toFixed(0)}% of required</span>
                    <span className={proposal.votes.for > proposal.votes.against * 2 ? 'text-green-400' : 'text-yellow-400'}>
                      {proposal.votes.for > proposal.votes.against * 2 ? '✓ Threshold Met' : '⚠ Below Threshold'}
                    </span>
                  </div>
                </div>

                {expandedProposal === proposal.id && proposal.status === 'active' && (
                  <div className="px-5 pb-5 border-t border-gray-800 pt-3">
                    <div className="flex gap-3">
                      <button className="flex-1 py-3 bg-green-500/10 border border-green-500/30 rounded-lg text-green-400 font-semibold hover:bg-green-500/20 transition-all">
                        VOTE FOR
                      </button>
                      <button className="flex-1 py-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 font-semibold hover:bg-red-500/20 transition-all">
                        VOTE AGAINST
                      </button>
                      <button className="flex-1 py-3 bg-gray-800 border border-gray-700 rounded-lg text-gray-400 font-semibold hover:bg-gray-700 transition-all">
                        ABSTAIN
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {activeTab === 'blacklist' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-bold">Blacklisted Addresses ({blacklist.length})</h2>
              <div className="flex items-center gap-2">
                <div className="relative">
                  <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500" />
                  <input
                    type="text"
                    placeholder="Search addresses..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10 pr-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm focus:border-[#7c3aed] focus:outline-none"
                  />
                </div>
                <button className="px-4 py-2 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 hover:bg-red-500/20 transition-all">
                  <Ban className="w-4 h-4" />
                  ADD TO BLACKLIST
                </button>
              </div>
            </div>

            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-gray-800/50">
                  <tr className="text-left text-xs text-gray-500 uppercase tracking-wider">
                    <th className="px-4 py-3">Address</th>
                    <th className="px-4 py-3">Reason</th>
                    <th className="px-4 py-3">Source</th>
                    <th className="px-4 py-3">V1 Holder</th>
                    <th className="px-4 py-3">Added</th>
                    <th className="px-4 py-3">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-800">
                  {blacklist.map((entry) => (
                    <tr key={entry.id} className="hover:bg-gray-800/30 transition-all">
                      <td className="px-4 py-4 font-mono text-[#7c3aed]">{entry.address}</td>
                      <td className="px-4 py-4">
                        <div className="max-w-xs truncate" title={entry.reason}>{entry.reason}</div>
                        {entry.estimatedLoss && <div className="text-xs text-red-400 mt-1">Loss: {entry.estimatedLoss}</div>}
                      </td>
                      <td className="px-4 py-4">
                        <span className={`text-xs font-bold ${getSourceColor(entry.source)}`}>
                          {entry.source.toUpperCase()}
                        </span>
                      </td>
                      <td className="px-4 py-4">
                        {entry.crmV1Holder ? (
                          <span className="flex items-center gap-1 text-red-400">
                            <AlertTriangle className="w-4 h-4" />
                            YES - BLOCKED
                          </span>
                        ) : (
                          <span className="text-gray-500">No</span>
                        )}
                      </td>
                      <td className="px-4 py-4 text-gray-500">{entry.addedAt}</td>
                      <td className="px-4 py-4">
                        <div className="flex items-center gap-2">
                          <button className="p-1.5 bg-gray-800 rounded hover:bg-gray-700 transition-all" title="View Evidence">
                            <FileText className="w-4 h-4" />
                          </button>
                          <button className="p-1.5 bg-gray-800 rounded hover:bg-gray-700 transition-all" title="View on Explorer">
                            <ExternalLink className="w-4 h-4" />
                          </button>
                          {entry.appealStatus === 'pending' && (
                            <span className="px-2 py-1 bg-yellow-500/20 text-yellow-400 rounded text-xs">APPEAL PENDING</span>
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

        {activeTab === 'airdrop' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-bold">Airdrop Claim Management</h2>
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-500">Total Allocated: 45,000,000 CRM</span>
                <span className="text-xs text-green-500">Claimed: 32,400,000 CRM (72%)</span>
              </div>
            </div>

            <div className="grid grid-cols-4 gap-4 mb-6">
              <div className="bg-gradient-to-br from-green-500/10 to-[#0f0c1d] border border-green-500/30 rounded-lg p-4">
                <div className="text-2xl font-bold text-green-400">8,450</div>
                <div className="text-xs text-gray-500">Successful Claims</div>
              </div>
              <div className="bg-gradient-to-br from-yellow-500/10 to-[#0f0c1d] border border-yellow-500/30 rounded-lg p-4">
                <div className="text-2xl font-bold text-yellow-400">3,200</div>
                <div className="text-xs text-gray-500">Pending Verification</div>
              </div>
              <div className="bg-gradient-to-br from-red-500/10 to-[#0f0c1d] border border-red-500/30 rounded-lg p-4">
                <div className="text-2xl font-bold text-red-400">23</div>
                <div className="text-xs text-gray-500">Blocked (Blacklist)</div>
              </div>
              <div className="bg-gradient-to-br from-gray-700/30 to-[#0f0c1d] border border-gray-700 rounded-lg p-4">
                <div className="text-2xl font-bold text-gray-400">850</div>
                <div className="text-xs text-gray-500">Expired Claims</div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-gray-800/50">
                  <tr className="text-left text-xs text-gray-500 uppercase tracking-wider">
                    <th className="px-4 py-3">Address</th>
                    <th className="px-4 py-3">Amount</th>
                    <th className="px-4 py-3">Status</th>
                    <th className="px-4 py-3">Eligible</th>
                    <th className="px-4 py-3">KYC</th>
                    <th className="px-4 py-3">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-800">
                  {airdropClaims.map((claim) => (
                    <tr key={claim.id} className="hover:bg-gray-800/30 transition-all">
                      <td className="px-4 py-4 font-mono text-[#7c3aed]">{claim.address}</td>
                      <td className="px-4 py-4 font-semibold">{claim.amount}</td>
                      <td className="px-4 py-4">
                        <span className={`px-2 py-1 rounded text-xs ${getStatusColor(claim.status)}`}>
                          {claim.status.toUpperCase()}
                        </span>
                      </td>
                      <td className="px-4 py-4">
                        {claim.eligible ? (
                          <CheckCircle className="w-4 h-4 text-green-400" />
                        ) : (
                          <div className="flex items-center gap-1 text-red-400">
                            <XCircle className="w-4 h-4" />
                            <span className="text-xs">{claim.reason}</span>
                          </div>
                        )}
                      </td>
                      <td className="px-4 py-4">
                        <span className={`text-xs ${
                          claim.kycStatus === 'verified' ? 'text-green-400' :
                          claim.kycStatus === 'pending' ? 'text-yellow-400' :
                          claim.kycStatus === 'failed' ? 'text-red-400' :
                          'text-gray-400'
                        }`}>
                          {claim.kycStatus.toUpperCase()}
                        </span>
                      </td>
                      <td className="px-4 py-4">
                        <div className="flex items-center gap-2">
                          <button className="px-3 py-1.5 bg-[#7c3aed]/10 border border-[#7c3aed]/30 rounded text-xs text-[#7c3aed] hover:bg-[#7c3aed]/20 transition-all">
                            VERIFY
                          </button>
                          {claim.status === 'pending' && (
                            <button className="px-3 py-1.5 bg-red-500/10 border border-red-500/30 rounded text-xs text-red-400 hover:bg-red-500/20 transition-all">
                              BLOCK
                            </button>
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

        {activeTab === 'treasury' && (
          <div className="grid grid-cols-2 gap-6">
            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-bold mb-4">Treasury Holdings</h3>
              <div className="space-y-3">
                {[
                  { asset: 'CRM', balance: '22,000,000', value: '$6,600,000', change: '+12%' },
                  { asset: 'ETH', balance: '450', value: '$1,350,000', change: '+5%' },
                  { asset: 'USDC', balance: '1,200,000', value: '$1,200,000', change: '0%' },
                  { asset: 'Staked CRM', balance: '5,000,000', value: '$1,500,000', change: '+18% APY' },
                ].map((asset, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 bg-[#0a0812] rounded-lg">
                    <div>
                      <div className="font-semibold">{asset.asset}</div>
                      <div className="text-xs text-gray-500">{asset.balance}</div>
                    </div>
                    <div className="text-right">
                      <div className="font-semibold">{asset.value}</div>
                      <div className={`text-xs ${asset.change.startsWith('+') ? 'text-green-400' : 'text-gray-400'}`}>
                        {asset.change}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              <div className="mt-4 pt-4 border-t border-gray-800 flex justify-between">
                <span className="text-gray-500">Total Value</span>
                <span className="text-xl font-bold text-[#7c3aed]">$10,650,000</span>
              </div>
            </div>

            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-bold mb-4">Recent Treasury Actions</h3>
              <div className="space-y-3">
                {[
                  { action: 'Buyback Executed', amount: '250,000 CRM', value: '$75,000', date: '2 days ago', type: 'out' },
                  { action: 'Staking Rewards', amount: '180,000 CRM', value: '$54,000', date: '5 days ago', type: 'out' },
                  { action: 'Subscription Revenue', amount: '420 ETH', value: '$1,260,000', date: '7 days ago', type: 'in' },
                  { action: 'LP Addition (Base)', amount: '200,000 USDC', value: '$200,000', date: '14 days ago', type: 'out' },
                ].map((action, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 bg-[#0a0812] rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className={`w-2 h-2 rounded-full ${action.type === 'in' ? 'bg-green-400' : 'bg-red-400'}`} />
                      <div>
                        <div className="text-sm font-semibold">{action.action}</div>
                        <div className="text-xs text-gray-500">{action.date}</div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className={`text-sm font-semibold ${action.type === 'in' ? 'text-green-400' : 'text-red-400'}`}>
                        {action.type === 'in' ? '+' : '-'}{action.value}
                      </div>
                      <div className="text-xs text-gray-500">{action.amount}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DAOManagement;
