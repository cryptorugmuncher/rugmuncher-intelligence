import { useState } from 'react';
import { DollarSign, Target, Award, Globe, Search, FileText, TrendingUp, CheckCircle2, Clock, AlertCircle, ExternalLink, Plus, Filter, Building2, Wallet, Zap, Briefcase, Trophy, ChevronRight, Download, BarChart3, PieChart, Calendar, Users } from 'lucide-react';
import { useAppStore } from '../store/appStore';

interface FundingOpportunity {
  id: string;
  name: string;
  type: 'grant' | 'hackathon' | 'bounty' | 'accelerator' | 'vc' | 'dao' | 'angel';
  amount: { min: number; max: number; currency: string };
  deadline: string;
  status: 'researching' | 'applying' | 'submitted' | ' finalist' | 'funded' | 'rejected';
  category: string[];
  description: string;
  requirements: string[];
  applicationUrl: string;
  notes: string;
  probability: number; // estimated win probability
  effort: 'low' | 'medium' | 'high';
  contacts?: string[];
}

interface PitchDeck {
  id: string;
  name: string;
  version: string;
  lastUpdated: string;
  status: 'draft' | 'review' | 'final';
  targetAudience: string;
  url: string;
}

const mockOpportunities: FundingOpportunity[] = [
  {
    id: '1',
    name: 'Coinbase Developer Grants',
    type: 'grant',
    amount: { min: 10000, max: 150000, currency: 'USD' },
    deadline: '2026-05-15',
    status: 'applying',
    category: ['infrastructure', 'security'],
    description: 'Grants for developers building on-chain security tools and infrastructure. Perfect fit for MunchMaps.',
    requirements: ['Open source code', 'Demo video', 'Roadmap', 'Team bios'],
    applicationUrl: 'https://coinbase.com/developer-grants',
    notes: 'Strong fit - emphasize wallet security angle. Apply for maximum tier.',
    probability: 75,
    effort: 'medium',
    contacts: ['grants@coinbase.com']
  },
  {
    id: '2',
    name: 'ETHGlobal Tokyo Hackathon',
    type: 'hackathon',
    amount: { min: 0, max: 50000, currency: 'USD' },
    deadline: '2026-04-30',
    status: 'researching',
    category: ['hackathon', 'ethereum'],
    description: 'Major hackathon with focus on DeFi security. Prize pool includes $50k for best security tool.',
    requirements: ['Working demo', 'GitHub repo', '5-min pitch video'],
    applicationUrl: 'https://ethglobal.com/events/tokyo',
    notes: 'Need team members. Good for visibility even if not winning.',
    probability: 40,
    effort: 'high'
  },
  {
    id: '3',
    name: 'Gitcoin Grants Round',
    type: 'grant',
    amount: { min: 5000, max: 100000, currency: 'USD' },
    deadline: '2026-06-01',
    status: 'applying',
    category: ['public goods', 'community'],
    description: 'Quadratic funding for public goods. Community can contribute matching.',
    requirements: ['Project description', 'Funding goals', 'Impact metrics'],
    applicationUrl: 'https://grants.gitcoin.co',
    notes: 'Start community engagement NOW. QF means small donors multiply.',
    probability: 85,
    effort: 'low'
  },
  {
    id: '4',
    name: 'a16z Crypto Startup Accelerator',
    type: 'accelerator',
    amount: { min: 500000, max: 1000000, currency: 'USD' },
    deadline: '2026-05-01',
    status: 'researching',
    category: ['accelerator', 'seed'],
    description: '12-week program for early-stage crypto startups. Access to network and mentorship.',
    requirements: ['Pitch deck', 'Demo', 'Team', 'Traction metrics'],
    applicationUrl: 'https://a16zcrypto.com/accelerator',
    notes: 'Very competitive. Need polished pitch and clear revenue model.',
    probability: 15,
    effort: 'high'
  },
  {
    id: '5',
    name: 'Immunefi Bug Bounty Program',
    type: 'bounty',
    amount: { min: 1000, max: 100000, currency: 'USD' },
    deadline: 'Ongoing',
    status: 'researching',
    category: ['security', 'audit'],
    description: 'Bug bounty platform. Can list our own contracts and earn from finding bugs in others.',
    requirements: ['Smart contracts', 'Bounty allocation', 'Scope definition'],
    applicationUrl: 'https://immunefi.com',
    notes: 'Dual opportunity - secure our code + earn from whitehat hunting.',
    probability: 90,
    effort: 'low'
  },
  {
    id: '6',
    name: 'Base Ecosystem Fund',
    type: 'grant',
    amount: { min: 25000, max: 250000, currency: 'USD' },
    deadline: '2026-06-15',
    status: 'applying',
    category: ['base', 'ecosystem'],
    description: 'Grants for projects building on Base chain. Prioritizing consumer and security apps.',
    requirements: ['Base integration', 'User growth plan', 'Product demo'],
    applicationUrl: 'https://base.org/ecosystem',
    notes: 'We already support Base - strong advantage here. Apply soon.',
    probability: 70,
    effort: 'medium'
  },
  {
    id: '7',
    name: 'Arbitrum DAO Grant',
    type: 'dao',
    amount: { min: 50000, max: 500000, currency: 'ARB' },
    deadline: '2026-05-30',
    status: 'submitted',
    category: ['arbitrum', 'dao', 'analytics'],
    description: 'Governance grants for projects providing data analytics and security on Arbitrum.',
    requirements: ['Forum proposal', 'Community support', 'Milestones'],
    applicationUrl: 'https://arbitrum.foundation/grants',
    notes: 'Submitted April 5. Waiting for review. Need community votes.',
    probability: 60,
    effort: 'high'
  },
  {
    id: '8',
    name: 'Paradigm Seed Investment',
    type: 'vc',
    amount: { min: 2000000, max: 5000000, currency: 'USD' },
    deadline: 'Rolling',
    status: 'researching',
    category: ['vc', 'seed', 'infrastructure'],
    description: 'Top-tier crypto VC. Looking for security infrastructure plays.',
    requirements: ['Warm intro', 'Traction', 'Strong team', '$10k+ MRR'],
    applicationUrl: 'https://paradigm.xyz',
    notes: 'Need intro through network. Not ready yet - wait for CRM V2 traction.',
    probability: 20,
    effort: 'high',
    contacts: ['invest@paradigm.xyz']
  }
];

const pitchDecks: PitchDeck[] = [
  {
    id: '1',
    name: 'RMI Master Deck',
    version: '2.4',
    lastUpdated: '2026-04-10',
    status: 'final',
    targetAudience: 'General Investors',
    url: '#'
  },
  {
    id: '2',
    name: 'Security Focus Deck',
    version: '1.2',
    lastUpdated: '2026-04-08',
    status: 'review',
    targetAudience: 'Security-Focused VCs',
    url: '#'
  },
  {
    id: '3',
    name: 'Grant Application Deck',
    version: '1.0',
    lastUpdated: '2026-04-12',
    status: 'draft',
    targetAudience: 'Grant Committees',
    url: '#'
  }
];

export default function CapitalAcquisition() {
  const { theme } = useAppStore();
  const darkMode = theme === 'dark';

  const [opportunities] = useState<FundingOpportunity[]>(mockOpportunities);
  const [activeTab, setActiveTab] = useState<'pipeline' | 'deck' | 'strategy' | 'tracker'>('pipeline');
  const [filterType, setFilterType] = useState<string>('all');
  const [filterStatus, setFilterStatus] = useState<string>('all');

  const stats = {
    totalPipeline: opportunities.reduce((acc, opp) => acc + opp.amount.max, 0),
    applied: opportunities.filter(o => ['applying', 'submitted'].includes(o.status)).length,
    highProbability: opportunities.filter(o => o.probability >= 70).length,
    totalOpportunities: opportunities.length
  };

  const filteredOpportunities = opportunities.filter(opp => {
    const matchesType = filterType === 'all' || opp.type === filterType;
    const matchesStatus = filterStatus === 'all' || opp.status === filterStatus;
    return matchesType && matchesStatus;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'funded': return 'text-green-400 bg-green-500/10';
      case 'submitted': return 'text-blue-400 bg-blue-500/10';
      case 'applying': return 'text-yellow-400 bg-yellow-500/10';
      case 'rejected': return 'text-red-400 bg-red-500/10';
      default: return 'text-slate-400 bg-slate-500/10';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'grant': return Award;
      case 'hackathon': return Trophy;
      case 'bounty': return Target;
      case 'accelerator': return Zap;
      case 'vc': return Building2;
      case 'dao': return Users;
      default: return DollarSign;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
        <div className="flex items-center gap-3 mb-2">
          <DollarSign className="w-8 h-8 text-green-500" />
          <h1 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
            CAPITAL ACQUISITION CENTER
          </h1>
          <span className="px-2 py-1 bg-green-500/10 text-green-400 text-xs font-mono rounded">
            RESOURCE OPS
          </span>
        </div>
        <p className={`${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
          Strategic funding pipeline management: grants, hackathons, bounties, VCs, DAO funding, and strategic partnerships.
        </p>
      </div>

      {/* Stats Banner */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
          <p className={`text-3xl font-bold text-green-400`}>
            ${(stats.totalPipeline / 1000000).toFixed(1)}M
          </p>
          <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Pipeline Value</p>
        </div>
        <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
          <p className="text-3xl font-bold text-blue-400">{stats.applied}</p>
          <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Active Applications</p>
        </div>
        <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
          <p className="text-3xl font-bold text-purple-400">{stats.highProbability}</p>
          <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>High Probability</p>
        </div>
        <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
          <p className="text-3xl font-bold text-yellow-400">{stats.totalOpportunities}</p>
          <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Total Opportunities</p>
        </div>
      </div>

      {/* Navigation */}
      <div className="flex flex-wrap gap-2">
        {[
          { id: 'pipeline', label: 'Opportunity Pipeline', icon: Target },
          { id: 'deck', label: 'Pitch Materials', icon: FileText },
          { id: 'strategy', label: 'Funding Strategy', icon: BarChart3 },
          { id: 'tracker', label: 'Application Tracker', icon: Calendar }
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${
              activeTab === tab.id
                ? 'bg-green-600 text-white'
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

      {/* Pipeline Tab */}
      {activeTab === 'pipeline' && (
        <div className="space-y-4">
          {/* Filters */}
          <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
            <div className="flex flex-wrap gap-4">
              <div>
                <label className={`block text-sm mb-1 ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Type</label>
                <select
                  value={filterType}
                  onChange={e => setFilterType(e.target.value)}
                  className={`px-3 py-2 rounded-lg border ${darkMode ? 'bg-slate-900 border-slate-700 text-white' : 'bg-white border-slate-300'}`}
                >
                  <option value="all">All Types</option>
                  <option value="grant">Grants</option>
                  <option value="hackathon">Hackathons</option>
                  <option value="bounty">Bounties</option>
                  <option value="accelerator">Accelerators</option>
                  <option value="vc">VCs</option>
                  <option value="dao">DAO Grants</option>
                </select>
              </div>
              <div>
                <label className={`block text-sm mb-1 ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Status</label>
                <select
                  value={filterStatus}
                  onChange={e => setFilterStatus(e.target.value)}
                  className={`px-3 py-2 rounded-lg border ${darkMode ? 'bg-slate-900 border-slate-700 text-white' : 'bg-white border-slate-300'}`}
                >
                  <option value="all">All Statuses</option>
                  <option value="researching">Researching</option>
                  <option value="applying">Applying</option>
                  <option value="submitted">Submitted</option>
                  <option value="funded">Funded</option>
                  <option value="rejected">Rejected</option>
                </select>
              </div>
              <div className="flex-1 flex items-end">
                <button className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700">
                  <Plus className="w-4 h-4" />
                  Add Opportunity
                </button>
              </div>
            </div>
          </div>

          {/* Opportunity Cards */}
          <div className="grid gap-4">
            {filteredOpportunities.map(opp => {
              const TypeIcon = getTypeIcon(opp.type);
              const daysUntil = Math.ceil((new Date(opp.deadline).getTime() - Date.now()) / (1000 * 60 * 60 * 24));

              return (
                <div
                  key={opp.id}
                  className={`rounded-lg p-4 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-4">
                      <div className={`p-3 rounded-lg ${darkMode ? 'bg-slate-700' : 'bg-slate-100'}`}>
                        <TypeIcon className="w-6 h-6 text-green-400" />
                      </div>
                      <div>
                        <h3 className={`font-semibold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                          {opp.name}
                        </h3>
                        <p className={`text-sm mt-1 ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                          {opp.description}
                        </p>
                        <div className="flex items-center gap-3 mt-2 text-sm">
                          <span className="text-green-400 font-medium">
                            ${opp.amount.min.toLocaleString()} - ${opp.amount.max.toLocaleString()}
                          </span>
                          <span className={darkMode ? 'text-slate-500' : 'text-slate-400'}>
                            {opp.type.toUpperCase()}
                          </span>
                          {daysUntil > 0 ? (
                            <span className={`${daysUntil < 7 ? 'text-red-400' : 'text-yellow-400'}`}>
                              {daysUntil} days left
                            </span>
                          ) : (
                            <span className="text-slate-500">Rolling</span>
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <span className={`px-3 py-1 rounded-full text-xs ${getStatusColor(opp.status)}`}>
                        {opp.status.toUpperCase()}
                      </span>
                      <div className="mt-2">
                        <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>Win Probability</p>
                        <p className={`text-lg font-bold ${opp.probability >= 70 ? 'text-green-400' : opp.probability >= 40 ? 'text-yellow-400' : 'text-red-400'}`}>
                          {opp.probability}%
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Tags */}
                  <div className="flex flex-wrap gap-2 mt-3">
                    {opp.category.map(cat => (
                      <span key={cat} className={`text-xs px-2 py-1 rounded ${darkMode ? 'bg-slate-700 text-slate-300' : 'bg-slate-100 text-slate-600'}`}>
                        {cat}
                      </span>
                    ))}
                    <span className={`text-xs px-2 py-1 rounded ${
                      opp.effort === 'low' ? 'bg-green-500/10 text-green-400' :
                      opp.effort === 'medium' ? 'bg-yellow-500/10 text-yellow-400' :
                      'bg-red-500/10 text-red-400'
                    }`}>
                      {opp.effort.toUpperCase()} EFFORT
                    </span>
                  </div>

                  {/* Requirements Preview */}
                  <div className="mt-3">
                    <p className={`text-xs mb-1 ${darkMode ? 'text-slate-500' : 'text-slate-500'}`}>REQUIREMENTS</p>
                    <div className="flex flex-wrap gap-2">
                      {opp.requirements.map(req => (
                        <span key={req} className="text-xs flex items-center gap-1 text-slate-400">
                          <CheckCircle2 className="w-3 h-3" />
                          {req}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center justify-between mt-4 pt-3 border-t border-slate-700/30">
                    <p className={`text-sm italic ${darkMode ? 'text-slate-500' : 'text-slate-500'}`}>
                      "{opp.notes}"
                    </p>
                    <div className="flex gap-2">
                      <a
                        href={opp.applicationUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-1 px-3 py-1.5 text-sm text-green-400 hover:bg-green-500/10 rounded"
                      >
                        <ExternalLink className="w-4 h-4" />
                        Apply
                      </a>
                      <button className="px-3 py-1.5 text-sm bg-green-600 text-white rounded hover:bg-green-700">
                        Update Status
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Deck Tab */}
      {activeTab === 'deck' && (
        <div className="space-y-4">
          <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
            <div className="flex items-center justify-between mb-6">
              <h3 className={`font-semibold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                Pitch Deck Library
              </h3>
              <button className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700">
                <Plus className="w-4 h-4" />
                New Deck
              </button>
            </div>

            <div className="grid md:grid-cols-3 gap-4">
              {pitchDecks.map(deck => (
                <div
                  key={deck.id}
                  className={`p-4 rounded-lg border transition-all ${
                    darkMode
                      ? 'border-slate-700 hover:border-green-500/50 bg-slate-800/30'
                      : 'border-slate-200 hover:border-green-500/50 bg-slate-50'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <FileText className="w-8 h-8 text-green-400" />
                    <span className={`px-2 py-1 rounded text-xs ${
                      deck.status === 'final' ? 'bg-green-500/10 text-green-400' :
                      deck.status === 'review' ? 'bg-yellow-500/10 text-yellow-400' :
                      'bg-slate-500/10 text-slate-400'
                    }`}>
                      {deck.status.toUpperCase()}
                    </span>
                  </div>
                  <h4 className={`font-semibold mt-3 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                    {deck.name}
                  </h4>
                  <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                    {deck.targetAudience}
                  </p>
                  <div className="flex items-center gap-2 mt-3 text-sm">
                    <span className={darkMode ? 'text-slate-500' : 'text-slate-500'}>v{deck.version}</span>
                    <span className={darkMode ? 'text-slate-500' : 'text-slate-500'}>•</span>
                    <span className={darkMode ? 'text-slate-500' : 'text-slate-500'}>
                      Updated {new Date(deck.lastUpdated).toLocaleDateString()}
                    </span>
                  </div>
                  <div className="flex gap-2 mt-4">
                    <button className="flex-1 py-2 text-sm bg-green-600/20 text-green-400 rounded hover:bg-green-600/30">
                      View
                    </button>
                    <button className="p-2 text-slate-400 hover:text-white">
                      <Download className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Quick Links */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <a href="#" className={`p-4 rounded-lg border text-center transition-all ${darkMode ? 'border-slate-700 hover:border-green-500' : 'border-slate-200 hover:border-green-500'}`}>
              <Briefcase className="w-6 h-6 text-green-400 mx-auto mb-2" />
              <p className={`font-medium ${darkMode ? 'text-white' : 'text-slate-900'}`}>Financial Model</p>
            </a>
            <a href="#" className={`p-4 rounded-lg border text-center transition-all ${darkMode ? 'border-slate-700 hover:border-green-500' : 'border-slate-200 hover:border-green-500'}`}>
              <Building2 className="w-6 h-6 text-green-400 mx-auto mb-2" />
              <p className={`font-medium ${darkMode ? 'text-white' : 'text-slate-900'}`}>Cap Table</p>
            </a>
            <a href="#" className={`p-4 rounded-lg border text-center transition-all ${darkMode ? 'border-slate-700 hover:border-green-500' : 'border-slate-200 hover:border-green-500'}`}>
              <TrendingUp className="w-6 h-6 text-green-400 mx-auto mb-2" />
              <p className={`font-medium ${darkMode ? 'text-white' : 'text-slate-900'}`}>Traction Data</p>
            </a>
            <a href="#" className={`p-4 rounded-lg border text-center transition-all ${darkMode ? 'border-slate-700 hover:border-green-500' : 'border-slate-200 hover:border-green-500'}`}>
              <Users className="w-6 h-6 text-green-400 mx-auto mb-2" />
              <p className={`font-medium ${darkMode ? 'text-white' : 'text-slate-900'}`}>Team Bios</p>
            </a>
          </div>
        </div>
      )}

      {/* Strategy Tab */}
      {activeTab === 'strategy' && (
        <div className="space-y-6">
          <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
            <h3 className={`font-semibold mb-4 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
              Funding Strategy: Phase-Based Approach
            </h3>

            <div className="space-y-6">
              <div className={`p-4 rounded-lg border-l-4 border-green-500 ${darkMode ? 'bg-slate-900/50' : 'bg-slate-50'}`}>
                <h4 className="font-semibold text-green-400 mb-2">Phase 1: Bootstrap (Now - May 2026)</h4>
                <ul className={`text-sm space-y-1 ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>
                  <li>• Focus: Grants, hackathons, bounties</li>
                  <li>• Target: $100K - $500K non-dilutive</li>
                  <li>• Priority: Gitcoin, Base, Arbitrum grants</li>
                  <li>• Timeline: Apply by May 1, results by June</li>
                </ul>
              </div>

              <div className={`p-4 rounded-lg border-l-4 border-yellow-500 ${darkMode ? 'bg-slate-900/50' : 'bg-slate-50'}`}>
                <h4 className="font-semibold text-yellow-400 mb-2">Phase 2: Community (May - July 2026)</h4>
                <ul className={`text-sm space-y-1 ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>
                  <li>• Focus: Token launch, community raise</li>
                  <li>• Target: $200K - $1M via token sale</li>
                  <li>• Priority: Fair launch, DAO treasury</li>
                  <li>• Timeline: CRM V2 launch coordinated</li>
                </ul>
              </div>

              <div className={`p-4 rounded-lg border-l-4 border-purple-500 ${darkMode ? 'bg-slate-900/50' : 'bg-slate-50'}`}>
                <h4 className="font-semibold text-purple-400 mb-2">Phase 3: Strategic (July - Dec 2026)</h4>
                <ul className={`text-sm space-y-1 ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>
                  <li>• Focus: Strategic angels, seed VCs</li>
                  <li>• Target: $1M - $5M at $10M+ valuation</li>
                  <li>• Priority: Paradigm, a16z crypto, Dragonfly</li>
                  <li>• Requirement: Demonstrable traction</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Funding Mix Target */}
          <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
            <h3 className={`font-semibold mb-4 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
              Target Funding Mix (12 Month)
            </h3>
            <div className="grid md:grid-cols-2 gap-6">
              <div className="space-y-3">
                {[
                  { label: 'Grants & Bounties', amount: 300000, color: 'bg-green-500' },
                  { label: 'Token Launch / Community', amount: 500000, color: 'bg-purple-500' },
                  { label: 'Strategic Investment', amount: 2000000, color: 'bg-blue-500' },
                  { label: 'DAO Treasury', amount: 200000, color: 'bg-yellow-500' }
                ].map(item => (
                  <div key={item.label} className="flex items-center gap-3">
                    <div className={`w-4 h-4 rounded ${item.color}`} />
                    <span className={`flex-1 ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>{item.label}</span>
                    <span className="font-medium text-green-400">${(item.amount / 1000).toFixed(0)}K</span>
                  </div>
                ))}
              </div>
              <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-900' : 'bg-slate-100'}`}>
                <p className={`text-sm mb-2 ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>TOTAL TARGET</p>
                <p className="text-4xl font-bold text-green-400">$3M</p>
                <p className={`text-sm mt-2 ${darkMode ? 'text-slate-500' : 'text-slate-500'}`}>
                  Sufficient for 18-24 months runway at projected burn rate
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tracker Tab */}
      {activeTab === 'tracker' && (
        <div className={`rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
          <div className="p-4 border-b border-slate-700/50">
            <h3 className={`font-semibold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
              Application Tracker
            </h3>
          </div>
          <div className="divide-y divide-slate-700/30">
            {opportunities
              .filter(o => ['applying', 'submitted', 'finalist'].includes(o.status))
              .map(opp => {
                const daysSinceSubmission = opp.status !== 'researching'
                  ? Math.floor((Date.now() - new Date('2026-04-01').getTime()) / (1000 * 60 * 60 * 24))
                  : 0;

                return (
                  <div key={opp.id} className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className={`font-medium ${darkMode ? 'text-white' : 'text-slate-900'}`}>{opp.name}</p>
                        <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                          Submitted {daysSinceSubmission} days ago • ${opp.amount.max.toLocaleString()} potential
                        </p>
                      </div>
                      <div className="flex items-center gap-3">
                        <div className="text-right">
                          <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>Status</p>
                          <p className={`font-medium ${getStatusColor(opp.status).split(' ')[0]}`}>
                            {opp.status.toUpperCase()}
                          </p>
                        </div>
                        <button className="p-2 text-slate-400 hover:text-white">
                          <ChevronRight className="w-5 h-5" />
                        </button>
                      </div>
                    </div>
                    {/* Progress Steps */}
                    <div className="flex items-center gap-2 mt-4">
                      {['Research', 'Apply', 'Review', 'Decision'].map((step, idx) => {
                        const stepNum = idx + 1;
                        const currentStep = opp.status === 'researching' ? 1 : opp.status === 'applying' ? 2 : opp.status === 'submitted' ? 3 : 4;
                        const isComplete = stepNum < currentStep;
                        const isCurrent = stepNum === currentStep;

                        return (
                          <div key={step} className="flex items-center">
                            <div className={`px-3 py-1 rounded text-xs ${
                              isComplete ? 'bg-green-500/20 text-green-400' :
                              isCurrent ? 'bg-yellow-500/20 text-yellow-400' :
                              'bg-slate-700/50 text-slate-500'
                            }`}>
                              {step}
                            </div>
                            {idx < 3 && (
                              <div className={`w-8 h-0.5 mx-1 ${
                                isComplete ? 'bg-green-500/30' : 'bg-slate-700'
                              }`} />
                            )}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                );
              })}
          </div>
        </div>
      )}
    </div>
  );
}
