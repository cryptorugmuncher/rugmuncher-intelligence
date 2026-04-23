import React, { useState } from 'react';
import {
  Bot,
  Settings,
  Power,
  MessageSquare,
  Activity,
  Brain,
  Terminal,
  Play,
  Pause,
  RotateCcw,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Edit3,
  Save,
  ChevronDown,
  ChevronUp,
  Send,
  Users,
  Zap,
  Code,
  FileText,
  Shield,
  Clock,
  Database,
  RefreshCw
} from 'lucide-react';

interface BotConfig {
  id: string;
  name: string;
  handle: string;
  status: 'active' | 'paused' | 'maintenance' | 'error';
  role: string;
  personality: string;
  swarms: string[];
  commands: Command[];
  memoryEnabled: boolean;
  ragEnabled: boolean;
  autoResponse: boolean;
  rateLimit: number;
  dailyMessageCap: number;
  messagesToday: number;
  lastBackup: string;
  version: string;
  logs: LogEntry[];
}

interface Command {
  trigger: string;
  description: string;
  enabled: boolean;
  requiresAuth: boolean;
  responseType: 'instant' | 'swarm' | 'human';
}

interface LogEntry {
  timestamp: string;
  level: 'info' | 'warning' | 'error';
  message: string;
  userId?: string;
}

const BotManager: React.FC = () => {
  const [bots, setBots] = useState<BotConfig[]>([
    {
      id: 'b1',
      name: 'Rug Muncher',
      handle: '@rugmunchbot',
      status: 'active',
      role: 'Primary Scanner & Community Guardian',
      personality: 'Professional security analyst with dry wit. Responds quickly with actionable data.',
      swarms: ['ContractAnalyzer', 'TokenScanner', 'WhaleTracker'],
      commands: [
        { trigger: '/scan', description: 'Analyze contract for vulnerabilities', enabled: true, requiresAuth: false, responseType: 'swarm' },
        { trigger: '/track', description: 'Track wallet movements', enabled: true, requiresAuth: true, responseType: 'swarm' },
        { trigger: '/alert', description: 'Set up custom alerts', enabled: true, requiresAuth: true, responseType: 'instant' },
        { trigger: '/report', description: 'Report suspicious token', enabled: true, requiresAuth: false, responseType: 'human' },
      ],
      memoryEnabled: true,
      ragEnabled: true,
      autoResponse: true,
      rateLimit: 100,
      dailyMessageCap: 10000,
      messagesToday: 3420,
      lastBackup: '2 hours ago',
      version: 'v2.4.1',
      logs: [
        { timestamp: '10:23:45', level: 'info', message: 'Contract scan completed', userId: 'user_123' },
        { timestamp: '10:24:12', level: 'info', message: 'Alert triggered: High sell pressure', userId: 'user_456' },
        { timestamp: '10:25:33', level: 'warning', message: 'Rate limit approaching', userId: undefined },
      ]
    },
    {
      id: 'b2',
      name: 'MunchMaps Navigator',
      handle: '@munchmaps_bot',
      status: 'active',
      role: 'Wallet Visualization & Relationship Mapper',
      personality: 'Data-driven visualizer. Creates beautiful, clear network maps.',
      swarms: ['GraphVisualizer', 'RelationshipMapper', 'ClusterAnalyzer'],
      commands: [
        { trigger: '/map', description: 'Generate wallet relationship map', enabled: true, requiresAuth: false, responseType: 'swarm' },
        { trigger: '/trace', description: 'Trace fund flows', enabled: true, requiresAuth: true, responseType: 'swarm' },
        { trigger: '/cluster', description: 'Identify wallet clusters', enabled: true, requiresAuth: true, responseType: 'swarm' },
        { trigger: '/export', description: 'Export visualization data', enabled: true, requiresAuth: true, responseType: 'instant' },
      ],
      memoryEnabled: true,
      ragEnabled: true,
      autoResponse: true,
      rateLimit: 50,
      dailyMessageCap: 5000,
      messagesToday: 1245,
      lastBackup: '1 hour ago',
      version: 'v2.1.0',
      logs: [
        { timestamp: '10:15:22', level: 'info', message: 'Map generated: 450 nodes', userId: 'user_789' },
        { timestamp: '10:18:45', level: 'info', message: 'Cluster analysis complete', userId: 'user_012' },
      ]
    },
    {
      id: 'b3',
      name: 'Alpha Sentinel',
      handle: '@rmi_alpha_bot',
      status: 'paused',
      role: 'Premium Alpha & Insider Intelligence',
      personality: 'Exclusive, high-signal intelligence provider. Direct and concise.',
      swarms: ['AlphaDetector', 'InsightAnalyzer', 'SentimentTracker'],
      commands: [
        { trigger: '/alpha', description: 'Get latest alpha signals', enabled: true, requiresAuth: true, responseType: 'swarm' },
        { trigger: '/insider', description: 'Track insider movements', enabled: true, requiresAuth: true, responseType: 'swarm' },
        { trigger: '/early', description: 'Early token detection', enabled: false, requiresAuth: true, responseType: 'swarm' },
      ],
      memoryEnabled: true,
      ragEnabled: true,
      autoResponse: false,
      rateLimit: 20,
      dailyMessageCap: 2000,
      messagesToday: 890,
      lastBackup: '3 hours ago',
      version: 'v1.9.2',
      logs: [
        { timestamp: '09:45:12', level: 'info', message: 'Alpha signal generated', userId: 'premium_001' },
        { timestamp: '10:00:33', level: 'error', message: 'Swarm timeout', userId: undefined },
      ]
    }
  ]);

  const [selectedBot, setSelectedBot] = useState<string>('b1');
  const [editingBot, setEditingBot] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'commands' | 'memory' | 'logs'>('overview');
  const [expandedSection, setExpandedSection] = useState<string | null>('swarms');

  const currentBot = bots.find(b => b.id === selectedBot);

  const toggleBotStatus = (botId: string) => {
    setBots(bots.map(b => {
      if (b.id === botId) {
        return { ...b, status: b.status === 'active' ? 'paused' : 'active' };
      }
      return b;
    }));
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return <CheckCircle className="w-5 h-5 text-green-400" />;
      case 'paused': return <Pause className="w-5 h-5 text-yellow-400" />;
      case 'maintenance': return <Clock className="w-5 h-5 text-blue-400" />;
      case 'error': return <XCircle className="w-5 h-5 text-red-400" />;
      default: return <Activity className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'paused': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'maintenance': return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      case 'error': return 'bg-red-500/20 text-red-400 border-red-500/30';
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
              <Bot className="w-8 h-8 text-[#7c3aed]" />
              <div>
                <h1 className="text-xl font-bold tracking-wider">
                  BOT <span className="text-[#7c3aed]">COMMAND</span>
                </h1>
                <p className="text-xs text-gray-500 tracking-[0.2em]">FLEET MANAGEMENT & CONTROL</p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <div className="text-right">
                <div className="text-xs text-gray-500">Active Bots</div>
                <div className="text-xl font-bold text-green-400">{bots.filter(b => b.status === 'active').length}/{bots.length}</div>
              </div>
              <button className="flex items-center gap-2 px-4 py-2 bg-[#7c3aed] hover:bg-[#6d28d9] text-white text-sm rounded transition-all">
                <RefreshCw className="w-4 h-4" />
                BACKUP ALL
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-[1600px] mx-auto p-6">
        <div className="grid grid-cols-12 gap-6">
          {/* Bot Selection Sidebar */}
          <div className="col-span-3 space-y-3">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xs font-bold text-gray-500 uppercase tracking-wider">Fleet Status</h3>
              <span className="text-xs text-gray-500">{bots.length} units</span>
            </div>

            {bots.map((bot) => (
              <button
                key={bot.id}
                onClick={() => setSelectedBot(bot.id)}
                className={`w-full p-4 rounded-lg border text-left transition-all ${
                  selectedBot === bot.id
                    ? 'bg-[#7c3aed]/10 border-[#7c3aed]'
                    : 'bg-[#1a1525]/50 border-gray-800 hover:border-gray-700'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Bot className={`w-5 h-5 ${bot.status === 'active' ? 'text-[#7c3aed]' : 'text-gray-600'}`} />
                    <span className="font-semibold text-sm">{bot.name}</span>
                  </div>
                  {getStatusIcon(bot.status)}
                </div>
                <div className="text-xs text-gray-500 font-mono mb-2">{bot.handle}</div>
                <div className="flex items-center justify-between">
                  <span className={`px-2 py-0.5 rounded text-[10px] border ${getStatusColor(bot.status)}`}>
                    {bot.status.toUpperCase()}
                  </span>
                  <span className="text-xs text-gray-500">v{bot.version}</span>
                </div>
              </button>
            ))}
          </div>

          {/* Main Bot Control Panel */}
          <div className="col-span-9 space-y-4">
            {currentBot && (
              <>
                {/* Bot Header */}
                <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
                  <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-4">
                      <div className="w-16 h-16 bg-[#7c3aed]/10 rounded-xl flex items-center justify-center border border-[#7c3aed]/30">
                        <Bot className="w-8 h-8 text-[#7c3aed]" />
                      </div>
                      <div>
                        <h2 className="text-2xl font-bold">{currentBot.name}</h2>
                        <div className="text-sm text-gray-500">{currentBot.handle} • {currentBot.role}</div>
                      </div>
                    </div>

                    <div className="flex items-center gap-3">
                      <button
                        onClick={() => toggleBotStatus(currentBot.id)}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all ${
                          currentBot.status === 'active'
                            ? 'bg-red-500/10 border border-red-500/30 text-red-400 hover:bg-red-500/20'
                            : 'bg-green-500/10 border border-green-500/30 text-green-400 hover:bg-green-500/20'
                        }`}
                      >
                        {currentBot.status === 'active' ? (
                          <><Pause className="w-4 h-4" /> PAUSE</>
                        ) : (
                          <><Play className="w-4 h-4" /> ACTIVATE</>
                        )}
                      </button>
                      <button className="p-2 bg-gray-800 border border-gray-700 rounded-lg hover:bg-gray-700 transition-all">
                        <RotateCcw className="w-5 h-5" />
                      </button>
                      <button className="p-2 bg-gray-800 border border-gray-700 rounded-lg hover:bg-gray-700 transition-all">
                        <Settings className="w-5 h-5" />
                      </button>
                    </div>
                  </div>

                  {/* Stats Grid */}
                  <div className="grid grid-cols-4 gap-4 mb-6">
                    <div className="bg-[#0a0812] rounded-lg p-4">
                      <div className="text-xs text-gray-500 uppercase mb-1">Messages Today</div>
                      <div className="text-xl font-bold">{currentBot.messagesToday.toLocaleString()}</div>
                      <div className="text-xs text-gray-500">of {currentBot.dailyMessageCap.toLocaleString()} cap</div>
                    </div>
                    <div className="bg-[#0a0812] rounded-lg p-4">
                      <div className="text-xs text-gray-500 uppercase mb-1">Rate Limit</div>
                      <div className="text-xl font-bold">{currentBot.rateLimit}/min</div>
                      <div className="text-xs text-gray-500">Current threshold</div>
                    </div>
                    <div className="bg-[#0a0812] rounded-lg p-4">
                      <div className="text-xs text-gray-500 uppercase mb-1">AI Swarms</div>
                      <div className="text-xl font-bold">{currentBot.swarms.length}</div>
                      <div className="text-xs text-gray-500">Active agents</div>
                    </div>
                    <div className="bg-[#0a0812] rounded-lg p-4">
                      <div className="text-xs text-gray-500 uppercase mb-1">Last Backup</div>
                      <div className="text-xl font-bold text-green-400">{currentBot.lastBackup}</div>
                      <div className="text-xs text-gray-500">Memory state saved</div>
                    </div>
                  </div>

                  {/* Personality */}
                  <div className="bg-[#0a0812] rounded-lg p-4 border border-gray-800">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-bold text-gray-500 uppercase tracking-wider">Personality Profile</span>
                      <button className="text-[#7c3aed] hover:text-white">
                        <Edit3 className="w-4 h-4" />
                      </button>
                    </div>
                    <p className="text-sm text-gray-300">{currentBot.personality}</p>
                  </div>
                </div>

                {/* Navigation Tabs */}
                <div className="flex items-center gap-1 border-b border-gray-800">
                  {[
                    { id: 'overview', label: 'OVERVIEW', icon: <Activity className="w-4 h-4" /> },
                    { id: 'commands', label: 'COMMANDS', icon: <Terminal className="w-4 h-4" /> },
                    { id: 'memory', label: 'MEMORY & RAG', icon: <Brain className="w-4 h-4" /> },
                    { id: 'logs', label: 'LOGS', icon: <FileText className="w-4 h-4" /> },
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
                <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
                  {/* OVERVIEW TAB */}
                  {activeTab === 'overview' && (
                    <div className="space-y-4">
                      <h3 className="text-sm font-bold text-gray-500 uppercase tracking-wider">Swarm Allocation</h3>
                      <div className="grid grid-cols-3 gap-3">
                        {currentBot.swarms.map((swarm, idx) => (
                          <div key={idx} className="bg-[#0a0812] rounded-lg p-4 border border-gray-800">
                            <div className="flex items-center gap-2 mb-2">
                              <Zap className="w-4 h-4 text-[#7c3aed]" />
                              <span className="font-semibold text-sm">{swarm}</span>
                            </div>
                            <div className="text-xs text-gray-500">Processing: <span className="text-green-400">Active</span></div>
                            <div className="text-xs text-gray-500">Queue: <span className="text-white">{Math.floor(Math.random() * 50)}</span></div>
                          </div>
                        ))}
                        <button className="flex flex-col items-center justify-center gap-2 p-4 border border-dashed border-gray-700 rounded-lg hover:border-[#7c3aed] hover:text-[#7c3aed] transition-all text-gray-500">
                          <PlusIcon className="w-6 h-6" />
                          <span className="text-xs">ALLOCATE SWARM</span>
                        </button>
                      </div>

                      <h3 className="text-sm font-bold text-gray-500 uppercase tracking-wider mt-6">Configuration</h3>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="flex items-center justify-between p-3 bg-[#0a0812] rounded-lg">
                          <div className="flex items-center gap-2">
                            <Brain className="w-4 h-4 text-[#7c3aed]" />
                            <span className="text-sm">Memory Enabled</span>
                          </div>
                          <button
                            onClick={() => setBots(bots.map(b => b.id === currentBot.id ? { ...b, memoryEnabled: !b.memoryEnabled } : b))}
                            className={`w-12 h-6 rounded-full transition-all ${currentBot.memoryEnabled ? 'bg-[#7c3aed]' : 'bg-gray-700'}`}
                          >
                            <div className={`w-5 h-5 bg-white rounded-full transition-all ${currentBot.memoryEnabled ? 'ml-6' : 'ml-0.5'}`} />
                          </button>
                        </div>
                        <div className="flex items-center justify-between p-3 bg-[#0a0812] rounded-lg">
                          <div className="flex items-center gap-2">
                            <Database className="w-4 h-4 text-[#7c3aed]" />
                            <span className="text-sm">RAG System</span>
                          </div>
                          <button
                            onClick={() => setBots(bots.map(b => b.id === currentBot.id ? { ...b, ragEnabled: !b.ragEnabled } : b))}
                            className={`w-12 h-6 rounded-full transition-all ${currentBot.ragEnabled ? 'bg-[#7c3aed]' : 'bg-gray-700'}`}
                          >
                            <div className={`w-5 h-5 bg-white rounded-full transition-all ${currentBot.ragEnabled ? 'ml-6' : 'ml-0.5'}`} />
                          </button>
                        </div>
                        <div className="flex items-center justify-between p-3 bg-[#0a0812] rounded-lg">
                          <div className="flex items-center gap-2">
                            <MessageSquare className="w-4 h-4 text-[#7c3aed]" />
                            <span className="text-sm">Auto-Response</span>
                          </div>
                          <button
                            onClick={() => setBots(bots.map(b => b.id === currentBot.id ? { ...b, autoResponse: !b.autoResponse } : b))}
                            className={`w-12 h-6 rounded-full transition-all ${currentBot.autoResponse ? 'bg-[#7c3aed]' : 'bg-gray-700'}`}
                          >
                            <div className={`w-5 h-5 bg-white rounded-full transition-all ${currentBot.autoResponse ? 'ml-6' : 'ml-0.5'}`} />
                          </button>
                        </div>
                        <div className="flex items-center justify-between p-3 bg-[#0a0812] rounded-lg">
                          <div className="flex items-center gap-2">
                            <Shield className="w-4 h-4 text-[#7c3aed]" />
                            <span className="text-sm">Require Auth</span>
                          </div>
                          <span className="text-xs text-green-400">Always On</span>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* COMMANDS TAB */}
                  {activeTab === 'commands' && (
                    <div className="space-y-3">
                      {currentBot.commands.map((cmd, idx) => (
                        <div key={idx} className="flex items-center justify-between p-4 bg-[#0a0812] rounded-lg border border-gray-800">
                          <div className="flex items-center gap-4">
                            <div className="w-10 h-10 bg-[#7c3aed]/10 rounded-lg flex items-center justify-center">
                              <Terminal className="w-5 h-5 text-[#7c3aed]" />
                            </div>
                            <div>
                              <div className="font-semibold">{cmd.trigger}</div>
                              <div className="text-xs text-gray-500">{cmd.description}</div>
                            </div>
                          </div>
                          <div className="flex items-center gap-3">
                            <span className={`px-2 py-1 rounded text-xs ${cmd.enabled ? 'bg-green-500/20 text-green-400' : 'bg-gray-700 text-gray-400'}`}>
                              {cmd.enabled ? 'ENABLED' : 'DISABLED'}
                            </span>
                            <span className={`px-2 py-1 rounded text-xs ${cmd.requiresAuth ? 'bg-yellow-500/20 text-yellow-400' : 'bg-gray-700 text-gray-400'}`}>
                              {cmd.requiresAuth ? 'AUTH REQUIRED' : 'PUBLIC'}
                            </span>
                            <span className="px-2 py-1 rounded text-xs bg-blue-500/20 text-blue-400">
                              {cmd.responseType.toUpperCase()}
                            </span>
                          </div>
                        </div>
                      ))}
                      <button className="w-full py-3 border border-dashed border-gray-700 rounded-lg text-gray-500 hover:border-[#7c3aed] hover:text-[#7c3aed] transition-all">
                        + ADD NEW COMMAND
                      </button>
                    </div>
                  )}

                  {/* MEMORY TAB */}
                  {activeTab === 'memory' && (
                    <div className="space-y-6">
                      <div className="grid grid-cols-2 gap-4">
                        <div className="bg-[#0a0812] rounded-lg p-5 border border-gray-800">
                          <div className="flex items-center gap-2 mb-4">
                            <Brain className="w-5 h-5 text-[#7c3aed]" />
                            <h4 className="font-semibold">Bot Memory Storage</h4>
                          </div>
                          <div className="space-y-3">
                            <div>
                              <div className="flex justify-between text-xs mb-1">
                                <span className="text-gray-500">Storage Used</span>
                                <span className="text-white">4.2 GB / 10 GB</span>
                              </div>
                              <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                                <div className="h-full w-[42%] bg-[#7c3aed] rounded-full" />
                              </div>
                            </div>
                            <div className="flex justify-between text-sm">
                              <span className="text-gray-500">Conversations</span>
                              <span>234,567</span>
                            </div>
                            <div className="flex justify-between text-sm">
                              <span className="text-gray-500">User Profiles</span>
                              <span>45,230</span>
                            </div>
                            <div className="flex justify-between text-sm">
                              <span className="text-gray-500">Last Backup</span>
                              <span className="text-green-400">{currentBot.lastBackup}</span>
                            </div>
                          </div>
                          <div className="flex gap-2 mt-4">
                            <button className="flex-1 py-2 bg-[#7c3aed]/10 border border-[#7c3aed]/30 rounded text-sm text-[#7c3aed] hover:bg-[#7c3aed]/20 transition-all">
                              BACKUP NOW
                            </button>
                            <button className="flex-1 py-2 bg-gray-800 border border-gray-700 rounded text-sm text-gray-400 hover:bg-gray-700 transition-all">
                              EXPORT
                            </button>
                          </div>
                        </div>

                        <div className="bg-[#0a0812] rounded-lg p-5 border border-gray-800">
                          <div className="flex items-center gap-2 mb-4">
                            <Database className="w-5 h-5 text-green-400" />
                            <h4 className="font-semibold">RAG Knowledge Base</h4>
                          </div>
                          <div className="space-y-3">
                            <div>
                              <div className="flex justify-between text-xs mb-1">
                                <span className="text-gray-500">Vector Storage</span>
                                <span className="text-white">12.8 GB / 50 GB</span>
                              </div>
                              <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                                <div className="h-full w-[25%] bg-green-500 rounded-full" />
                              </div>
                            </div>
                            <div className="flex justify-between text-sm">
                              <span className="text-gray-500">Documents</span>
                              <span>8,452</span>
                            </div>
                            <div className="flex justify-between text-sm">
                              <span className="text-gray-500">Embeddings</span>
                              <span>2.4M</span>
                            </div>
                            <div className="flex justify-between text-sm">
                              <span className="text-gray-500">Last Sync</span>
                              <span className="text-green-400">2 hours ago</span>
                            </div>
                          </div>
                          <div className="flex gap-2 mt-4">
                            <button className="flex-1 py-2 bg-green-500/10 border border-green-500/30 rounded text-sm text-green-400 hover:bg-green-500/20 transition-all">
                              SYNC NOW
                            </button>
                            <button className="flex-1 py-2 bg-gray-800 border border-gray-700 rounded text-sm text-gray-400 hover:bg-gray-700 transition-all">
                              REBUILD INDEX
                            </button>
                          </div>
                        </div>
                      </div>

                      <div className="bg-[#0a0812] rounded-lg p-5 border border-gray-800">
                        <h4 className="font-semibold mb-4">Automated Backup Schedule</h4>
                        <div className="space-y-2">
                          {[
                            { time: '00:00 UTC', type: 'Full Memory Backup', retention: '30 days', next: 'in 14 hours' },
                            { time: 'Every 6 hours', type: 'Incremental Backup', retention: '7 days', next: 'in 2 hours' },
                            { time: 'Real-time', type: 'Transaction Log', retention: '24 hours', next: 'Continuous' },
                          ].map((schedule, idx) => (
                            <div key={idx} className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg">
                              <div className="flex items-center gap-4">
                                <Clock className="w-4 h-4 text-gray-500" />
                                <div>
                                  <div className="text-sm font-semibold">{schedule.type}</div>
                                  <div className="text-xs text-gray-500">{schedule.time} • Retention: {schedule.retention}</div>
                                </div>
                              </div>
                              <span className="text-xs text-[#7c3aed]">Next: {schedule.next}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}

                  {/* LOGS TAB */}
                  {activeTab === 'logs' && (
                    <div className="space-y-2 font-mono text-sm">
                      {currentBot.logs.map((log, idx) => (
                        <div key={idx} className="flex items-start gap-3 p-3 bg-[#0a0812] rounded-lg">
                          <span className="text-gray-500">{log.timestamp}</span>
                          <span className={`px-2 py-0.5 rounded text-xs ${
                            log.level === 'error' ? 'bg-red-500/20 text-red-400' :
                            log.level === 'warning' ? 'bg-yellow-500/20 text-yellow-400' :
                            'bg-green-500/20 text-green-400'
                          }`}>
                            {log.level.toUpperCase()}
                          </span>
                          <span className="text-gray-300">{log.message}</span>
                          {log.userId && <span className="text-gray-500">[{log.userId}]</span>}
                        </div>
                      ))}
                      <div className="flex items-center gap-2 p-3 text-gray-500">
                        <div className="w-2 h-2 bg-[#7c3aed] rounded-full animate-pulse" />
                        <span>Live streaming...</span>
                      </div>
                    </div>
                  )}
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

const PlusIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
  </svg>
);

export default BotManager;
