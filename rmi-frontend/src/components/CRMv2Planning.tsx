import { useState } from 'react';
import { Rocket, Target, Shield, Users, Coins, Globe, Zap, CheckCircle2, Clock, AlertTriangle, FileCode, TrendingUp, Lock, Database, Layers, Award, ChevronRight, Plus, Trash2, Edit3, Save, X, BarChart3, PieChart, Calendar, DollarSign } from 'lucide-react';
import { useAppStore } from '../store/appStore';

interface PlanningTask {
  id: string;
  title: string;
  category: 'tokenomics' | 'tech' | 'legal' | 'marketing' | 'operations' | 'launch';
  priority: 'critical' | 'high' | 'medium' | 'low';
  status: 'todo' | 'in_progress' | 'review' | 'complete';
  assignedTo?: string;
  dueDate?: string;
  description: string;
  dependencies: string[];
  estimatedHours: number;
  actualHours?: number;
}

interface Milestone {
  id: string;
  name: string;
  targetDate: string;
  status: 'upcoming' | 'in_progress' | 'completed' | 'delayed';
  deliverables: string[];
  blockers?: string[];
}

interface TokenomicsModel {
  id: string;
  name: string;
  totalSupply: number;
  initialPrice: number;
  distribution: {
    label: string;
    percentage: number;
    vesting: string;
    color: string;
  }[];
  features: string[];
  selected: boolean;
}

const mockTasks: PlanningTask[] = [
  {
    id: '1',
    title: 'Finalize Token Smart Contract',
    category: 'tech',
    priority: 'critical',
    status: 'in_progress',
    assignedTo: 'Dev Team',
    dueDate: '2026-04-20',
    description: 'Complete ERC-20 contract with tax mechanism, anti-bot, and blacklist features.',
    dependencies: ['Security audit scheduled'],
    estimatedHours: 40,
    actualHours: 24
  },
  {
    id: '2',
    title: 'DAO Governance Framework',
    category: 'legal',
    priority: 'critical',
    status: 'in_progress',
    assignedTo: 'Legal Counsel',
    dueDate: '2026-04-25',
    description: 'Establish DAO legal structure and governance voting mechanisms.',
    dependencies: ['Wyoming LLC dissolution'],
    estimatedHours: 60
  },
  {
    id: '3',
    title: 'Tokenomics Finalization',
    category: 'tokenomics',
    priority: 'critical',
    status: 'review',
    assignedTo: 'Founder',
    dueDate: '2026-04-18',
    description: 'Lock in supply, initial liquidity, buyback mechanisms, and tax structure.',
    dependencies: [],
    estimatedHours: 20,
    actualHours: 18
  },
  {
    id: '4',
    title: 'Launch Marketing Campaign',
    category: 'marketing',
    priority: 'high',
    status: 'todo',
    dueDate: '2026-05-01',
    description: 'Coordinate X posts, Telegram announcements, and influencer partnerships.',
    dependencies: ['Website updates', 'Whitepaper final'],
    estimatedHours: 80
  },
  {
    id: '5',
    title: 'Exchange Listing Applications',
    category: 'operations',
    priority: 'medium',
    status: 'todo',
    dueDate: '2026-05-15',
    description: 'Submit applications to DEX aggregators and consider CEX pre-listing.',
    dependencies: ['Token launch complete'],
    estimatedHours: 30
  },
  {
    id: '6',
    title: 'Airdrop System Architecture',
    category: 'tech',
    priority: 'high',
    status: 'in_progress',
    assignedTo: 'Backend Team',
    dueDate: '2026-04-22',
    description: 'Build claim system with blacklist filtering and vesting for large allocations.',
    dependencies: ['CRM V1 blacklist finalized'],
    estimatedHours: 50,
    actualHours: 35
  }
];

const milestones: Milestone[] = [
  {
    id: '1',
    name: 'Smart Contract Deployment',
    targetDate: '2026-04-20',
    status: 'in_progress',
    deliverables: ['ERC-20 contract', 'Tax logic', 'Anti-bot', 'Blacklist'],
    blockers: ['Final security review']
  },
  {
    id: '2',
    name: 'Liquidity Launch',
    targetDate: '2026-04-25',
    status: 'upcoming',
    deliverables: ['Initial LP', 'Token distribution', 'Website live'],
    blockers: []
  },
  {
    id: '3',
    name: 'Airdrop Phase 1',
    targetDate: '2026-05-01',
    status: 'upcoming',
    deliverables: ['Eligible wallet list', 'Claim portal', 'Support docs'],
    blockers: []
  },
  {
    id: '4',
    name: 'DAO Transition Complete',
    targetDate: '2026-05-15',
    status: 'upcoming',
    deliverables: ['Voting contracts', 'Treasury multi-sig', 'Legal docs'],
    blockers: []
  }
];

const tokenomicsModels: TokenomicsModel[] = [
  {
    id: '1',
    name: 'Conservative Launch',
    totalSupply: 1000000000,
    initialPrice: 0.0001,
    distribution: [
      { label: 'Public Sale/Liquidity', percentage: 60, vesting: 'Immediate', color: '#7c3aed' },
      { label: 'Team & Dev', percentage: 15, vesting: '2yr vest, 6mo cliff', color: '#3b82f6' },
      { label: 'Treasury/Operations', percentage: 15, vesting: '1yr vest', color: '#10b981' },
      { label: 'Airdrop V2', percentage: 10, vesting: '25% immediate, 75% 6mo', color: '#f59e0b' }
    ],
    features: ['1% buy/sell tax', 'Auto-LP', 'Anti-whale (2% max)'],
    selected: true
  },
  {
    id: '2',
    name: 'Aggressive Growth',
    totalSupply: 5000000000,
    initialPrice: 0.00001,
    distribution: [
      { label: 'Liquidity Pool', percentage: 50, vesting: 'Immediate', color: '#7c3aed' },
      { label: 'Community Rewards', percentage: 20, vesting: '4yr emission', color: '#10b981' },
      { label: 'Team', percentage: 15, vesting: '3yr vest, 1yr cliff', color: '#3b82f6' },
      { label: 'Treasury', percentage: 10, vesting: '2yr vest', color: '#f59e0b' },
      { label: 'Airdrop', percentage: 5, vesting: 'Immediate', color: '#ef4444' }
    ],
    features: ['2% tax (1% burn, 1% treasury)', 'Dynamic buyback', 'Staking rewards'],
    selected: false
  },
  {
    id: '3',
    name: 'Community First',
    totalSupply: 21000000,
    initialPrice: 0.01,
    distribution: [
      { label: 'Fair Launch', percentage: 70, vesting: 'Immediate', color: '#7c3aed' },
      { label: 'Community Treasury', percentage: 20, vesting: 'DAO controlled', color: '#10b981' },
      { label: 'Core Contributors', percentage: 10, vesting: '4yr vest', color: '#3b82f6' }
    ],
    features: ['0% tax', 'Pure community ownership', 'Bitcoin-like scarcity'],
    selected: false
  }
];

export default function CRMv2Planning() {
  const { theme } = useAppStore();
  const darkMode = theme === 'dark';

  const [tasks, setTasks] = useState<PlanningTask[]>(mockTasks);
  const [activeTab, setActiveTab] = useState<'overview' | 'tasks' | 'tokenomics' | 'roadmap'>('overview');
  const [selectedModel, setSelectedModel] = useState<string>('1');
  const [editingTask, setEditingTask] = useState<string | null>(null);

  const stats = {
    totalTasks: tasks.length,
    completed: tasks.filter(t => t.status === 'complete').length,
    inProgress: tasks.filter(t => t.status === 'in_progress').length,
    critical: tasks.filter(t => t.priority === 'critical').length,
    completionRate: Math.round((tasks.filter(t => t.status === 'complete').length / tasks.length) * 100)
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return 'text-red-400 bg-red-500/10';
      case 'high': return 'text-orange-400 bg-orange-500/10';
      case 'medium': return 'text-yellow-400 bg-yellow-500/10';
      default: return 'text-slate-400 bg-slate-500/10';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'complete': return 'text-green-400';
      case 'in_progress': return 'text-blue-400';
      case 'review': return 'text-yellow-400';
      default: return 'text-slate-400';
    }
  };

  const updateTaskStatus = (taskId: string, newStatus: PlanningTask['status']) => {
    setTasks(tasks.map(t => t.id === taskId ? { ...t, status: newStatus } : t));
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
        <div className="flex items-center gap-3 mb-2">
          <Rocket className="w-8 h-8 text-purple-500" />
          <h1 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
            $CRM V2 LAUNCH COMMAND
          </h1>
          <span className="px-2 py-1 bg-purple-500/10 text-purple-400 text-xs font-mono rounded">
            PROJECT PHOENIX
          </span>
        </div>
        <p className={`${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
          Comprehensive planning dashboard for CryptoRugMuncher V2 token launch and DAO transition.
        </p>
      </div>

      {/* Launch Status Banner */}
      <div className="bg-gradient-to-r from-purple-600 via-purple-700 to-purple-800 rounded-lg p-4">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-white/10 rounded-lg">
              <Target className="w-6 h-6 text-white" />
            </div>
            <div>
              <p className="text-purple-200 text-sm">TARGET LAUNCH</p>
              <p className="text-white text-xl font-bold">April 25, 2026</p>
            </div>
          </div>
          <div className="flex items-center gap-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-white">{stats.completionRate}%</p>
              <p className="text-purple-200 text-xs">COMPLETE</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-white">{stats.critical}</p>
              <p className="text-purple-200 text-xs">CRITICAL</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-white">T-{Math.ceil((new Date('2026-04-25').getTime() - Date.now()) / (1000 * 60 * 60 * 24))}</p>
              <p className="text-purple-200 text-xs">DAYS</p>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex flex-wrap gap-2">
        {[
          { id: 'overview', label: 'Launch Overview', icon: BarChart3 },
          { id: 'tasks', label: 'Task Command', icon: CheckCircle2 },
          { id: 'tokenomics', label: 'Tokenomics Lab', icon: Coins },
          { id: 'roadmap', label: 'Milestone Track', icon: Calendar }
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
        <div className="space-y-6">
          {/* Stats Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
              <p className={`text-3xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'}`}>{stats.totalTasks}</p>
              <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Total Tasks</p>
            </div>
            <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
              <p className="text-3xl font-bold text-green-400">{stats.completed}</p>
              <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Completed</p>
            </div>
            <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
              <p className="text-3xl font-bold text-blue-400">{stats.inProgress}</p>
              <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>In Progress</p>
            </div>
            <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
              <p className="text-3xl font-bold text-red-400">{stats.critical}</p>
              <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Critical Priority</p>
            </div>
          </div>

          {/* Upcoming Milestones */}
          <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
            <h3 className={`text-lg font-semibold mb-4 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
              Upcoming Milestones
            </h3>
            <div className="space-y-4">
              {milestones.map((milestone, idx) => (
                <div key={milestone.id} className="relative">
                  {idx < milestones.length - 1 && (
                    <div className={`absolute left-4 top-8 w-0.5 h-full ${darkMode ? 'bg-slate-700' : 'bg-slate-200'}`} />
                  )}
                  <div className="flex gap-4">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                      milestone.status === 'completed'
                        ? 'bg-green-500 text-white'
                        : milestone.status === 'in_progress'
                        ? 'bg-blue-500 text-white'
                        : darkMode
                        ? 'bg-slate-700 text-slate-400'
                        : 'bg-slate-200 text-slate-500'
                    }`}>
                      {milestone.status === 'completed' ? <CheckCircle2 className="w-5 h-5" /> : idx + 1}
                    </div>
                    <div className="flex-1 pb-4">
                      <div className="flex items-center justify-between">
                        <p className={`font-semibold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                          {milestone.name}
                        </p>
                        <span className={`px-2 py-1 rounded text-xs ${
                          milestone.status === 'completed'
                            ? 'bg-green-500/10 text-green-400'
                            : milestone.status === 'in_progress'
                            ? 'bg-blue-500/10 text-blue-400'
                            : 'bg-slate-500/10 text-slate-400'
                        }`}>
                          {milestone.status.replace('_', ' ').toUpperCase()}
                        </span>
                      </div>
                      <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                        Target: {new Date(milestone.targetDate).toLocaleDateString()}
                      </p>
                      <div className="flex flex-wrap gap-2 mt-2">
                        {milestone.deliverables.map(d => (
                          <span key={d} className={`text-xs px-2 py-1 rounded ${
                            darkMode ? 'bg-slate-700 text-slate-300' : 'bg-slate-100 text-slate-600'
                          }`}>
                            {d}
                          </span>
                        ))}
                      </div>
                      {milestone.blockers && milestone.blockers.length > 0 && (
                        <div className="flex items-center gap-2 mt-2 text-red-400 text-sm">
                          <AlertTriangle className="w-4 h-4" />
                          Blocker: {milestone.blockers.join(', ')}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <button className={`p-4 rounded-lg border text-center transition-all ${
              darkMode
                ? 'border-slate-700 hover:border-purple-500 hover:bg-purple-500/5'
                : 'border-slate-200 hover:border-purple-500 hover:bg-purple-50'
            }`}>
              <FileCode className="w-6 h-6 text-purple-400 mx-auto mb-2" />
              <p className={`font-medium ${darkMode ? 'text-white' : 'text-slate-900'}`}>View Contract</p>
            </button>
            <button className={`p-4 rounded-lg border text-center transition-all ${
              darkMode
                ? 'border-slate-700 hover:border-purple-500 hover:bg-purple-500/5'
                : 'border-slate-200 hover:border-purple-500 hover:bg-purple-50'
            }`}>
              <Shield className="w-6 h-6 text-green-400 mx-auto mb-2" />
              <p className={`font-medium ${darkMode ? 'text-white' : 'text-slate-900'}`}>Security Audit</p>
            </button>
            <button className={`p-4 rounded-lg border text-center transition-all ${
              darkMode
                ? 'border-slate-700 hover:border-purple-500 hover:bg-purple-500/5'
                : 'border-slate-200 hover:border-purple-500 hover:bg-purple-50'
            }`}>
              <Users className="w-6 h-6 text-blue-400 mx-auto mb-2" />
              <p className={`font-medium ${darkMode ? 'text-white' : 'text-slate-900'}`}>Airdrop List</p>
            </button>
            <button className={`p-4 rounded-lg border text-center transition-all ${
              darkMode
                ? 'border-slate-700 hover:border-purple-500 hover:bg-purple-500/5'
                : 'border-slate-200 hover:border-purple-500 hover:bg-purple-50'
            }`}>
              <Globe className="w-6 h-6 text-yellow-400 mx-auto mb-2" />
              <p className={`font-medium ${darkMode ? 'text-white' : 'text-slate-900'}`}>Launch Checklist</p>
            </button>
          </div>
        </div>
      )}

      {/* Tasks Tab */}
      {activeTab === 'tasks' && (
        <div className={`rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
          <div className="p-4 border-b border-slate-700/50">
            <div className="flex items-center justify-between">
              <h3 className={`font-semibold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                Launch Tasks
              </h3>
              <button className="flex items-center gap-2 px-3 py-1.5 bg-purple-600 text-white rounded-lg text-sm hover:bg-purple-700">
                <Plus className="w-4 h-4" />
                Add Task
              </button>
            </div>
          </div>
          <div className="divide-y divide-slate-700/30">
            {tasks.map(task => (
              <div key={task.id} className="p-4 hover:bg-slate-700/10 transition-all">
                <div className="flex items-start gap-4">
                  <div className={`w-6 h-6 rounded border-2 flex items-center justify-center cursor-pointer ${
                    task.status === 'complete'
                      ? 'bg-green-500 border-green-500'
                      : 'border-slate-500'
                  }`} onClick={() => updateTaskStatus(task.id, task.status === 'complete' ? 'todo' : 'complete')}>
                    {task.status === 'complete' && <CheckCircle2 className="w-4 h-4 text-white" />}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-start justify-between">
                      <div>
                        <p className={`font-medium ${task.status === 'complete' ? 'line-through text-slate-500' : darkMode ? 'text-white' : 'text-slate-900'}`}>
                          {task.title}
                        </p>
                        <p className={`text-sm mt-1 ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                          {task.description}
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={`px-2 py-1 rounded text-xs ${getPriorityColor(task.priority)}`}>
                          {task.priority.toUpperCase()}
                        </span>
                        <button className="p-1 text-slate-400 hover:text-white">
                          <Edit3 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                    <div className="flex items-center gap-4 mt-2 text-sm">
                      <span className={`${getStatusColor(task.status)}`}>
                        {task.status.replace('_', ' ')}
                      </span>
                      {task.assignedTo && (
                        <span className={`${darkMode ? 'text-slate-500' : 'text-slate-500'}`}>
                          @{task.assignedTo}
                        </span>
                      )}
                      {task.dueDate && (
                        <span className={`${darkMode ? 'text-slate-500' : 'text-slate-500'}`}>
                          Due: {new Date(task.dueDate).toLocaleDateString()}
                        </span>
                      )}
                      <span className={`${darkMode ? 'text-slate-500' : 'text-slate-500'}`}>
                        Est: {task.estimatedHours}h
                        {task.actualHours && ` (${task.actualHours}h actual)`}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tokenomics Tab */}
      {activeTab === 'tokenomics' && (
        <div className="space-y-6">
          {/* Model Selection */}
          <div className="grid md:grid-cols-3 gap-4">
            {tokenomicsModels.map(model => (
              <button
                key={model.id}
                onClick={() => setSelectedModel(model.id)}
                className={`p-4 rounded-lg border text-left transition-all ${
                  selectedModel === model.id
                    ? 'border-purple-500 bg-purple-500/10'
                    : darkMode
                    ? 'border-slate-700 hover:border-slate-600'
                    : 'border-slate-200 hover:border-slate-300'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <p className={`font-semibold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                    {model.name}
                  </p>
                  {selectedModel === model.id && (
                    <CheckCircle2 className="w-5 h-5 text-purple-400" />
                  )}
                </div>
                <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                  Supply: {model.totalSupply.toLocaleString()}<br />
                  Initial: ${model.initialPrice}
                </p>
              </button>
            ))}
          </div>

          {/* Selected Model Details */}
          {(() => {
            const model = tokenomicsModels.find(m => m.id === selectedModel);
            if (!model) return null;
            return (
              <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
                <h3 className={`text-lg font-semibold mb-4 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                  {model.name} - Tokenomics Breakdown
                </h3>

                {/* Visual Distribution */}
                <div className="h-8 rounded-full overflow-hidden flex mb-4">
                  {model.distribution.map((d, idx) => (
                    <div
                      key={idx}
                      style={{ width: `${d.percentage}%`, backgroundColor: d.color }}
                      className="h-full"
                      title={`${d.label}: ${d.percentage}%`}
                    />
                  ))}
                </div>

                {/* Distribution Table */}
                <div className="grid gap-3">
                  {model.distribution.map((d, idx) => (
                    <div key={idx} className="flex items-center justify-between p-3 rounded-lg bg-slate-900/30">
                      <div className="flex items-center gap-3">
                        <div className="w-4 h-4 rounded" style={{ backgroundColor: d.color }} />
                        <span className={`font-medium ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                          {d.label}
                        </span>
                      </div>
                      <div className="text-right">
                        <p className={`font-semibold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                          {d.percentage}%
                        </p>
                        <p className="text-sm text-slate-500">{d.vesting}</p>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Features */}
                <div className="mt-6">
                  <h4 className={`font-medium mb-3 ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>
                    Token Features
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {model.features.map(f => (
                      <span key={f} className="px-3 py-1 bg-purple-500/10 text-purple-400 rounded-full text-sm">
                        {f}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Action */}
                <div className="mt-6 flex gap-3">
                  <button className="flex-1 py-3 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 transition-all">
                    Select This Model
                  </button>
                  <button className="px-6 py-3 bg-slate-700 text-white rounded-lg font-medium hover:bg-slate-600 transition-all">
                    Customize
                  </button>
                </div>
              </div>
            );
          })()}
        </div>
      )}

      {/* Roadmap Tab */}
      {activeTab === 'roadmap' && (
        <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
          <h3 className={`text-lg font-semibold mb-6 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
            Launch Timeline
          </h3>

          <div className="relative">
            {/* Timeline Line */}
            <div className={`absolute left-8 top-0 bottom-0 w-0.5 ${darkMode ? 'bg-slate-700' : 'bg-slate-200'}`} />

            {/* Timeline Items */}
            <div className="space-y-8">
              {[
                { phase: 'Phase 1: Foundation', date: 'April 15-20', items: ['Smart contract finalization', 'Security audit', 'Website V2 launch'], status: 'in_progress' },
                { phase: 'Phase 2: Token Launch', date: 'April 25', items: ['Liquidity deployment', 'Trading begins', 'Initial marketing'], status: 'upcoming' },
                { phase: 'Phase 3: Community', date: 'May 1-7', items: ['Airdrop distribution', 'DAO activation', 'Governance voting'], status: 'upcoming' },
                { phase: 'Phase 4: Expansion', date: 'May 15+', items: ['CEX listings', 'MunchMaps v2', 'Mobile app beta'], status: 'upcoming' }
              ].map((phase, idx) => (
                <div key={idx} className="relative flex gap-6">
                  <div className={`w-16 h-16 rounded-full flex items-center justify-center flex-shrink-0 z-10 ${
                    phase.status === 'in_progress'
                      ? 'bg-purple-600 text-white'
                      : darkMode
                      ? 'bg-slate-700 text-slate-400'
                      : 'bg-slate-200 text-slate-500'
                  }`}>
                    <Rocket className="w-6 h-6" />
                  </div>
                  <div className="flex-1 pt-2">
                    <div className="flex items-center gap-3 mb-2">
                      <h4 className={`font-semibold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                        {phase.phase}
                      </h4>
                      <span className={`px-2 py-0.5 rounded text-xs ${
                        phase.status === 'in_progress'
                          ? 'bg-purple-500/10 text-purple-400'
                          : 'bg-slate-500/10 text-slate-400'
                      }`}>
                        {phase.status.toUpperCase()}
                      </span>
                    </div>
                    <p className="text-sm text-purple-400 mb-3">{phase.date}</p>
                    <div className="space-y-2">
                      {phase.items.map((item, i) => (
                        <div key={i} className="flex items-center gap-2 text-sm">
                          <ChevronRight className="w-4 h-4 text-slate-500" />
                          <span className={`${darkMode ? 'text-slate-300' : 'text-slate-600'}`}>{item}</span>
                        </div>
                      ))}
                    </div>
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
