import React, { useState } from 'react';
import {
  Sparkles,
  Brain,
  Cpu,
  Activity,
  Zap,
  Settings,
  Play,
  Pause,
  RotateCcw,
  Trash2,
  Plus,
  Terminal,
  MessageSquare,
  Database,
  Network,
  Shield,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Clock,
  FileText,
  ChevronDown,
  ChevronUp,
  Target,
  Layers,
  Server,
  Code,
  RefreshCw,
  Save,
  Power
} from 'lucide-react';

interface SwarmAgent {
  id: string;
  name: string;
  role: string;
  status: 'active' | 'idle' | 'error' | 'training';
  model: string;
  capabilities: string[];
  tasksCompleted: number;
  avgResponseTime: string;
  cpuUsage: number;
  memoryUsage: number;
  lastActivity: string;
  assignedBots: string[];
  config: {
    temperature: number;
    maxTokens: number;
    contextWindow: number;
    creativity: number;
    accuracy: number;
  };
  logs: LogEntry[];
}

interface LogEntry {
  timestamp: string;
  level: 'info' | 'warning' | 'error' | 'success';
  message: string;
  taskId?: string;
}

interface SwarmTask {
  id: string;
  type: string;
  description: string;
  assignedAgents: string[];
  status: 'pending' | 'processing' | 'completed' | 'failed';
  priority: 'low' | 'medium' | 'high' | 'critical';
  createdAt: string;
  completedAt?: string;
  result?: string;
}

const SwarmManager: React.FC = () => {
  const [agents, setAgents] = useState<SwarmAgent[]>([
    {
      id: 'a1',
      name: 'ContractAnalyzer-Alpha',
      role: 'Smart Contract Security Analysis',
      status: 'active',
      model: 'GPT-4-Turbo',
      capabilities: ['Bytecode Analysis', 'Vulnerability Detection', 'Risk Scoring', 'Pattern Recognition'],
      tasksCompleted: 45620,
      avgResponseTime: '1.2s',
      cpuUsage: 78,
      memoryUsage: 64,
      lastActivity: '2s ago',
      assignedBots: ['@rugmunchbot'],
      config: {
        temperature: 0.1,
        maxTokens: 4000,
        contextWindow: 8192,
        creativity: 20,
        accuracy: 98
      },
      logs: [
        { timestamp: '10:23:45', level: 'success', message: 'Contract scan completed: 0 vulnerabilities', taskId: 'task_123' },
        { timestamp: '10:24:12', level: 'warning', message: 'High gas usage pattern detected', taskId: 'task_124' },
        { timestamp: '10:25:33', level: 'info', message: 'Model fine-tuning scheduled', taskId: undefined }
      ]
    },
    {
      id: 'a2',
      name: 'TokenScanner-Beta',
      role: 'Real-time Token Analysis',
      status: 'active',
      model: 'Claude-3-Opus',
      capabilities: ['Price Analysis', 'Volume Tracking', 'Whale Detection', 'Social Sentiment'],
      tasksCompleted: 89340,
      avgResponseTime: '0.8s',
      cpuUsage: 65,
      memoryUsage: 72,
      lastActivity: '5s ago',
      assignedBots: ['@rugmunchbot', '@rmi_alerts_bot'],
      config: {
        temperature: 0.3,
        maxTokens: 2000,
        contextWindow: 4096,
        creativity: 35,
        accuracy: 95
      },
      logs: [
        { timestamp: '10:22:10', level: 'success', message: 'Token profile generated', taskId: 'task_125' },
        { timestamp: '10:23:45', level: 'info', message: 'Price anomaly flagged', taskId: 'task_126' }
      ]
    },
    {
      id: 'a3',
      name: 'GraphVisualizer-Gamma',
      role: 'Wallet Relationship Mapping',
      status: 'idle',
      model: 'Custom-GNN-v2',
      capabilities: ['Network Analysis', 'Cluster Detection', 'Flow Tracing', 'Visualization'],
      tasksCompleted: 12340,
      avgResponseTime: '3.5s',
      cpuUsage: 0,
      memoryUsage: 45,
      lastActivity: '5m ago',
      assignedBots: ['@munchmaps_bot'],
      config: {
        temperature: 0.2,
        maxTokens: 8000,
        contextWindow: 16384,
        creativity: 40,
        accuracy: 96
      },
      logs: [
        { timestamp: '10:15:22', level: 'success', message: 'Graph rendered: 450 nodes, 1200 edges', taskId: 'task_120' },
        { timestamp: '10:18:45', level: 'info', message: 'Idle mode activated', taskId: undefined }
      ]
    },
    {
      id: 'a4',
      name: 'ThreatIntel-Delta',
      role: 'Scam & Threat Detection',
      status: 'active',
      model: 'GPT-4-Turbo',
      capabilities: ['Pattern Matching', 'Threat Scoring', 'Predictive Analysis', 'Alert Generation'],
      tasksCompleted: 67890,
      avgResponseTime: '1.5s',
      cpuUsage: 82,
      memoryUsage: 78,
      lastActivity: '1s ago',
      assignedBots: ['@rmi_alerts_bot', '@rugmunchbot'],
      config: {
        temperature: 0.05,
        maxTokens: 3000,
        contextWindow: 8192,
        creativity: 15,
        accuracy: 99
      },
      logs: [
        { timestamp: '10:26:12', level: 'warning', message: 'High-risk contract pattern detected', taskId: 'task_127' },
        { timestamp: '10:26:15', level: 'success', message: 'Alert dispatched to 15,234 users', taskId: 'task_127' }
      ]
    },
    {
      id: 'a5',
      name: 'AlphaDetect-Epsilon',
      role: 'Early Alpha Signal Detection',
      status: 'training',
      model: 'Fine-tuned-CRM-v1',
      capabilities: ['Signal Detection', 'Insider Tracking', 'Sentiment Analysis', 'Trend Prediction'],
      tasksCompleted: 8920,
      avgResponseTime: '2.1s',
      cpuUsage: 45,
      memoryUsage: 89,
      lastActivity: 'Training...',
      assignedBots: ['@rmi_alpha_bot'],
      config: {
        temperature: 0.4,
        maxTokens: 2500,
        contextWindow: 8192,
        creativity: 60,
        accuracy: 88
      },
      logs: [
        { timestamp: '10:00:00', level: 'info', message: 'Training epoch 45/100', taskId: undefined },
        { timestamp: '10:15:30', level: 'info', message: 'Loss: 0.0234, Accuracy: 92.3%', taskId: undefined }
      ]
    }
  ]);

  const [tasks] = useState<SwarmTask[]>([
    { id: 'task_127', type: 'Threat Analysis', description: 'Scan contract 0x... for vulnerabilities', assignedAgents: ['a4'], status: 'processing', priority: 'critical', createdAt: '10:26:10' },
    { id: 'task_128', type: 'Token Profile', description: 'Generate analysis for PEPE2.0', assignedAgents: ['a2'], status: 'pending', priority: 'medium', createdAt: '10:27:00' },
    { id: 'task_129', type: 'Graph Render', description: 'Map relationships for wallet 0x742d...', assignedAgents: ['a3'], status: 'pending', priority: 'low', createdAt: '10:27:30' },
    { id: 'task_126', type: 'Price Alert', description: 'Monitor SHIB for 10% price swing', assignedAgents: ['a2'], status: 'completed', priority: 'high', createdAt: '10:20:00', completedAt: '10:25:00', result: 'Alert triggered at 10:23:45' },
  ]);

  const [selectedAgent, setSelectedAgent] = useState<string>('a1');
  const [activeTab, setActiveTab] = useState<'overview' | 'agents' | 'tasks' | 'config'>('overview');
  const [systemStatus, setSystemStatus] = useState({
    totalAgents: 18,
    activeAgents: 15,
    queuedTasks: 23,
    completedToday: 12450,
    avgLatency: '1.2s',
    healthScore: 94
  });

  const currentAgent = agents.find(a => a.id === selectedAgent);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return <Zap className="w-5 h-5 text-green-400" />;
      case 'idle': return <Pause className="w-5 h-5 text-yellow-400" />;
      case 'error': return <XCircle className="w-5 h-5 text-red-400" />;
      case 'training': return <Brain className="w-5 h-5 text-blue-400" />;
      default: return <Activity className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'idle': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'error': return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'training': return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      default: return 'bg-gray-500/20 text-gray-400';
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0812] text-gray-100 font-mono selection:bg-[#7c3aed]/30">
      {/* Header */}
      <div className="bg-gradient-to-r from-[#0f0c1d] via-[#1a1525] to-[#0f0c1d] border-b border-[#7c3aed]/30">
        <div className="max-w-[1600px] mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Sparkles className="w-8 h-8 text-[#7c3aed]" />
              <div>
                <h1 className="text-xl font-bold tracking-wider">
                  SWARM <span className="text-[#7c3aed]">ORCHESTRATOR</span>
                </h1>
                <p className="text-xs text-gray-500 tracking-[0.2em]">AI AGENT FLEET COMMAND</p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <div className="text-right">
                <div className="text-xs text-gray-500">Fleet Health</div>
                <div className={`text-xl font-bold ${systemStatus.healthScore > 90 ? 'text-green-400' : 'text-yellow-400'}`}>
                  {systemStatus.healthScore}%
                </div>
              </div>
              <div className="text-right">
                <div className="text-xs text-gray-500">Active Agents</div>
                <div className="text-xl font-bold text-[#7c3aed]">
                  {systemStatus.activeAgents}/{systemStatus.totalAgents}
                </div>
              </div>
              <button className="flex items-center gap-2 px-4 py-2 bg-[#7c3aed] hover:bg-[#6d28d9] text-white text-sm rounded transition-all">
                <Plus className="w-4 h-4" />
                DEPLOY AGENT
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-[1600px] mx-auto p-6 space-y-6">
        {/* System Overview Cards */}
        <div className="grid grid-cols-5 gap-4">
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-5">
            <div className="flex items-center gap-2 mb-2">
              <Cpu className="w-5 h-5 text-[#7c3aed]" />
              <span className="text-xs text-gray-500 uppercase">Processing</span>
            </div>
            <div className="text-2xl font-bold">{systemStatus.avgLatency}</div>
            <div className="text-xs text-green-400">Avg Response</div>
          </div>
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-5">
            <div className="flex items-center gap-2 mb-2">
              <Layers className="w-5 h-5 text-blue-400" />
              <span className="text-xs text-gray-500 uppercase">Queue</span>
            </div>
            <div className="text-2xl font-bold">{systemStatus.queuedTasks}</div>
            <div className="text-xs text-gray-500">Pending Tasks</div>
          </div>
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-5">
            <div className="flex items-center gap-2 mb-2">
              <CheckCircle className="w-5 h-5 text-green-400" />
              <span className="text-xs text-gray-500 uppercase">Completed</span>
            </div>
            <div className="text-2xl font-bold">{systemStatus.completedToday.toLocaleString()}</div>
            <div className="text-xs text-gray-500">Today</div>
          </div>
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-5">
            <div className="flex items-center gap-2 mb-2">
              <Target className="w-5 h-5 text-yellow-400" />
              <span className="text-xs text-gray-500 uppercase">Accuracy</span>
            </div>
            <div className="text-2xl font-bold">96.8%</div>
            <div className="text-xs text-green-400">+0.3% vs yesterday</div>
          </div>
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-5">
            <div className="flex items-center gap-2 mb-2">
              <Network className="w-5 h-5 text-purple-400" />
              <span className="text-xs text-gray-500 uppercase">Models</span>
            </div>
            <div className="text-2xl font-bold">6</div>
            <div className="text-xs text-gray-500">Active LLMs</div>
          </div>
        </div>

        {/* Navigation */}
        <div className="flex items-center gap-1 border-b border-gray-800">
          {[
            { id: 'overview', label: 'FLEET OVERVIEW', icon: <Sparkles className="w-4 h-4" /> },
            { id: 'agents', label: 'AGENT CONTROL', icon: <Brain className="w-4 h-4" /> },
            { id: 'tasks', label: 'TASK QUEUE', icon: <Layers className="w-4 h-4" /> },
            { id: 'config', label: 'GLOBAL CONFIG', icon: <Settings className="w-4 h-4" /> },
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

        {/* Tab Content */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-3 gap-4">
            {agents.map((agent) => (
              <div key={agent.id} className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-5">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <Brain className={`w-5 h-5 ${agent.status === 'active' ? 'text-[#7c3aed]' : 'text-gray-600'}`} />
                    <span className="font-semibold text-sm">{agent.name}</span>
                  </div>
                  <span className={`px-2 py-0.5 rounded text-[10px] border ${getStatusColor(agent.status)}`}>
                    {agent.status.toUpperCase()}
                  </span>
                </div>
                <div className="text-xs text-gray-500 mb-3">{agent.role}</div>
                <div className="text-xs text-gray-500 mb-1">Model: <span className="text-white">{agent.model}</span></div>
                <div className="text-xs text-gray-500 mb-3">Tasks: <span className="text-green-400">{agent.tasksCompleted.toLocaleString()}</span></div>

                <div className="space-y-2 mb-3">
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-500">CPU</span>
                    <span className={agent.cpuUsage > 80 ? 'text-yellow-400' : ''}>{agent.cpuUsage}%</span>
                  </div>
                  <div className="h-1.5 bg-gray-800 rounded-full overflow-hidden">
                    <div className={`h-full rounded-full ${agent.cpuUsage > 80 ? 'bg-yellow-500' : 'bg-green-500'}`} style={{ width: `${agent.cpuUsage}%` }} />
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-500">Memory</span>
                    <span className={agent.memoryUsage > 85 ? 'text-red-400' : ''}>{agent.memoryUsage}%</span>
                  </div>
                  <div className="h-1.5 bg-gray-800 rounded-full overflow-hidden">
                    <div className={`h-full rounded-full ${agent.memoryUsage > 85 ? 'bg-red-500' : 'bg-blue-500'}`} style={{ width: `${agent.memoryUsage}%` }} />
                  </div>
                </div>

                <div className="flex gap-2">
                  <button className="flex-1 py-1.5 bg-[#7c3aed]/10 border border-[#7c3aed]/30 rounded text-xs text-[#7c3aed] hover:bg-[#7c3aed]/20 transition-all">
                    CONFIGURE
                  </button>
                  <button className="flex-1 py-1.5 bg-gray-800 border border-gray-700 rounded text-xs text-gray-400 hover:bg-gray-700 transition-all">
                    {agent.status === 'active' ? 'PAUSE' : 'ACTIVATE'}
                  </button>
                </div>
              </div>
            ))}
            <button className="flex flex-col items-center justify-center gap-2 p-5 border border-dashed border-gray-700 rounded-lg hover:border-[#7c3aed] hover:text-[#7c3aed] transition-all text-gray-500">
              <Plus className="w-8 h-8" />
              <span className="text-xs font-semibold">DEPLOY NEW AGENT</span>
            </button>
          </div>
        )}

        {activeTab === 'agents' && (
          <div className="grid grid-cols-12 gap-6">
            {/* Agent List */}
            <div className="col-span-4 space-y-2">
              {agents.map((agent) => (
                <button
                  key={agent.id}
                  onClick={() => setSelectedAgent(agent.id)}
                  className={`w-full p-4 rounded-lg border text-left transition-all ${
                    selectedAgent === agent.id
                      ? 'bg-[#7c3aed]/10 border-[#7c3aed]'
                      : 'bg-[#1a1525]/50 border-gray-800 hover:border-gray-700'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-semibold text-sm">{agent.name}</span>
                    {getStatusIcon(agent.status)}
                  </div>
                  <div className="text-xs text-gray-500">{agent.model}</div>
                </button>
              ))}
            </div>

            {/* Agent Control Panel */}
            <div className="col-span-8">
              {currentAgent && (
                <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
                  <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-4">
                      <div className="w-16 h-16 bg-[#7c3aed]/10 rounded-xl flex items-center justify-center border border-[#7c3aed]/30">
                        <Brain className="w-8 h-8 text-[#7c3aed]" />
                      </div>
                      <div>
                        <h2 className="text-2xl font-bold">{currentAgent.name}</h2>
                        <div className="text-sm text-gray-500">{currentAgent.role}</div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <button className="p-2 bg-yellow-500/10 border border-yellow-500/30 rounded-lg text-yellow-400 hover:bg-yellow-500/20 transition-all">
                        <RotateCcw className="w-5 h-5" />
                      </button>
                      <button className="p-2 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 hover:bg-red-500/20 transition-all">
                        <Trash2 className="w-5 h-5" />
                      </button>
                      <button className="flex items-center gap-2 px-4 py-2 bg-[#7c3aed] text-white rounded-lg hover:bg-[#6d28d9] transition-all">
                        <Save className="w-4 h-4" />
                        SAVE
                      </button>
                    </div>
                  </div>

                  {/* Configuration Sliders */}
                  <div className="space-y-6">
                    <div>
                      <div className="flex justify-between mb-2">
                        <label className="text-sm font-semibold">Temperature (Creativity)</label>
                        <span className="text-sm text-[#7c3aed]">{currentAgent.config.temperature}</span>
                      </div>
                      <input
                        type="range"
                        min="0"
                        max="1"
                        step="0.1"
                        value={currentAgent.config.temperature}
                        className="w-full h-2 bg-gray-800 rounded-lg appearance-none cursor-pointer accent-[#7c3aed]"
                      />
                      <div className="flex justify-between text-xs text-gray-500 mt-1">
                        <span>Precise</span>
                        <span>Creative</span>
                      </div>
                    </div>

                    <div>
                      <div className="flex justify-between mb-2">
                        <label className="text-sm font-semibold">Max Tokens</label>
                        <span className="text-sm text-[#7c3aed]">{currentAgent.config.maxTokens}</span>
                      </div>
                      <input
                        type="range"
                        min="500"
                        max="8000"
                        step="100"
                        value={currentAgent.config.maxTokens}
                        className="w-full h-2 bg-gray-800 rounded-lg appearance-none cursor-pointer accent-[#7c3aed]"
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div className="p-4 bg-[#0a0812] rounded-lg">
                        <div className="text-xs text-gray-500 uppercase mb-1">Model</div>
                        <select className="w-full bg-transparent text-white text-sm border-none focus:outline-none">
                          <option>GPT-4-Turbo</option>
                          <option>Claude-3-Opus</option>
                          <option>GPT-4o</option>
                          <option>Custom Fine-tuned</option>
                        </select>
                      </div>
                      <div className="p-4 bg-[#0a0812] rounded-lg">
                        <div className="text-xs text-gray-500 uppercase mb-1">Context Window</div>
                        <select className="w-full bg-transparent text-white text-sm border-none focus:outline-none">
                          <option>4K tokens</option>
                          <option>8K tokens</option>
                          <option>16K tokens</option>
                          <option>32K tokens</option>
                        </select>
                      </div>
                    </div>

                    {/* Capabilities */}
                    <div>
                      <label className="text-sm font-semibold mb-3 block">Capabilities</label>
                      <div className="flex flex-wrap gap-2">
                        {currentAgent.capabilities.map((cap, idx) => (
                          <span key={idx} className="px-3 py-1 bg-[#7c3aed]/10 border border-[#7c3aed]/30 rounded-full text-sm text-[#7c3aed]">
                            {cap}
                          </span>
                        ))}
                        <button className="px-3 py-1 border border-dashed border-gray-600 rounded-full text-sm text-gray-500 hover:border-[#7c3aed] hover:text-[#7c3aed] transition-all">
                          + Add
                        </button>
                      </div>
                    </div>

                    {/* Assigned Bots */}
                    <div>
                      <label className="text-sm font-semibold mb-3 block">Assigned to Bots</label>
                      <div className="flex flex-wrap gap-2">
                        {currentAgent.assignedBots.map((bot, idx) => (
                          <span key={idx} className="px-3 py-1 bg-green-500/10 border border-green-500/30 rounded-full text-sm text-green-400">
                            {bot}
                          </span>
                        ))}
                        <button className="px-3 py-1 border border-dashed border-gray-600 rounded-full text-sm text-gray-500 hover:border-[#7c3aed] hover:text-[#7c3aed] transition-all">
                          + Assign Bot
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'tasks' && (
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-bold">Active Task Queue</h2>
              <div className="flex items-center gap-2">
                <button className="px-3 py-1.5 bg-[#7c3aed]/10 border border-[#7c3aed]/30 rounded text-sm text-[#7c3aed] hover:bg-[#7c3aed]/20 transition-all">
                  CLEAR COMPLETED
                </button>
                <button className="px-3 py-1.5 bg-red-500/10 border border-red-500/30 rounded text-sm text-red-400 hover:bg-red-500/20 transition-all">
                  EMERGENCY STOP
                </button>
              </div>
            </div>

            <div className="space-y-2">
              {tasks.map((task) => (
                <div key={task.id} className="flex items-center justify-between p-4 bg-[#0a0812] rounded-lg border border-gray-800">
                  <div className="flex items-center gap-4">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                      task.status === 'processing' ? 'bg-yellow-500/10 text-yellow-400' :
                      task.status === 'completed' ? 'bg-green-500/10 text-green-400' :
                      task.status === 'pending' ? 'bg-gray-800 text-gray-400' :
                      'bg-red-500/10 text-red-400'
                    }`}>
                      {task.status === 'processing' ? <RefreshCw className="w-5 h-5 animate-spin" /> :
                       task.status === 'completed' ? <CheckCircle className="w-5 h-5" /> :
                       task.status === 'pending' ? <Clock className="w-5 h-5" /> :
                       <XCircle className="w-5 h-5" />}
                    </div>
                    <div>
                      <div className="font-semibold">{task.type}</div>
                      <div className="text-xs text-gray-500">{task.description}</div>
                      <div className="text-xs text-gray-500 mt-1">
                        Agents: {task.assignedAgents.join(', ')} • Created: {task.createdAt}
                        {task.completedAt && ` • Completed: ${task.completedAt}`}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className={`px-2 py-1 rounded text-xs ${
                      task.priority === 'critical' ? 'bg-red-500/20 text-red-400' :
                      task.priority === 'high' ? 'bg-orange-500/20 text-orange-400' :
                      task.priority === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
                      'bg-green-500/20 text-green-400'
                    }`}>
                      {task.priority.toUpperCase()}
                    </span>
                    <span className={`px-2 py-1 rounded text-xs ${
                      task.status === 'completed' ? 'bg-green-500/20 text-green-400' :
                      task.status === 'processing' ? 'bg-yellow-500/20 text-yellow-400' :
                      task.status === 'pending' ? 'bg-gray-700 text-gray-400' :
                      'bg-red-500/20 text-red-400'
                    }`}>
                      {task.status.toUpperCase()}
                    </span>
                    {task.result && (
                      <div className="text-xs text-gray-400 max-w-xs truncate">{task.result}</div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'config' && (
          <div className="grid grid-cols-2 gap-6">
            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-bold mb-4">Global Swarm Settings</h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-3 bg-[#0a0812] rounded-lg">
                  <div>
                    <div className="font-semibold text-sm">Auto-scaling</div>
                    <div className="text-xs text-gray-500">Spawn new agents when queue &gt; 50</div>
                  </div>
                  <button className="w-12 h-6 bg-[#7c3aed] rounded-full relative">
                    <div className="w-5 h-5 bg-white rounded-full absolute right-0.5 top-0.5" />
                  </button>
                </div>
                <div className="flex items-center justify-between p-3 bg-[#0a0812] rounded-lg">
                  <div>
                    <div className="font-semibold text-sm">Failover Mode</div>
                    <div className="text-xs text-gray-500">Auto-redistribute on agent failure</div>
                  </div>
                  <button className="w-12 h-6 bg-[#7c3aed] rounded-full relative">
                    <div className="w-5 h-5 bg-white rounded-full absolute right-0.5 top-0.5" />
                  </button>
                </div>
                <div className="flex items-center justify-between p-3 bg-[#0a0812] rounded-lg">
                  <div>
                    <div className="font-semibold text-sm">Training Mode</div>
                    <div className="text-xs text-gray-500">Allow agents to learn from feedback</div>
                  </div>
                  <button className="w-12 h-6 bg-gray-700 rounded-full relative">
                    <div className="w-5 h-5 bg-white rounded-full absolute left-0.5 top-0.5" />
                  </button>
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-bold mb-4">Resource Limits</h3>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-sm">Max Concurrent Agents</span>
                    <span className="text-sm text-[#7c3aed]">25</span>
                  </div>
                  <input type="range" min="5" max="50" value="25" className="w-full h-2 bg-gray-800 rounded-lg accent-[#7c3aed]" />
                </div>
                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-sm">Memory per Agent</span>
                    <span className="text-sm text-[#7c3aed]">8 GB</span>
                  </div>
                  <input type="range" min="2" max="32" value="8" className="w-full h-2 bg-gray-800 rounded-lg accent-[#7c3aed]" />
                </div>
                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-sm">GPU Allocation</span>
                    <span className="text-sm text-[#7c3aed]">40%</span>
                  </div>
                  <input type="range" min="10" max="100" value="40" className="w-full h-2 bg-gray-800 rounded-lg accent-[#7c3aed]" />
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SwarmManager;
