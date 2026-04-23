import React, { useState } from 'react';
import {
  Key,
  Shield,
  Activity,
  BarChart3,
  Zap,
  Clock,
  AlertTriangle,
  CheckCircle,
  X,
  Plus,
  Trash2,
  Edit3,
  Copy,
  RefreshCw,
  Lock,
  Globe,
  Server,
  Database,
  Brain,
  Bot,
  MessageSquare,
  Image,
  FileText,
  Code,
  Layers,
  Settings,
  ChevronDown,
  ChevronUp,
  Search,
  Filter,
  Download,
  Upload,
  Eye,
  EyeOff,
  Terminal,
  Cpu,
  HardDrive,
  Wifi,
  Radio,
  ToggleLeft,
  ToggleRight,
  DollarSign,
  TrendingUp,
  TrendingDown,
  AlertCircle,
  CheckSquare,
  Square,
  MoreHorizontal,
  ExternalLink,
  Power,
  PowerOff
} from 'lucide-react';

interface APIProvider {
  id: string;
  name: string;
  type: 'ai' | 'blockchain' | 'data' | 'social' | 'storage';
  status: 'active' | 'inactive' | 'rate_limited' | 'error';
  apiKey: string;
  endpoint: string;
  usageLimit: number;
  usageCurrent: number;
  costPerRequest: number;
  totalCost: number;
  lastUsed: string;
  failoverPriority: number;
  region: string;
  latency: number;
  successRate: number;
}

interface AIUsage {
  id: string;
  model: string;
  provider: string;
  prompt: string;
  response: string;
  tokensIn: number;
  tokensOut: number;
  cost: number;
  timestamp: string;
  endpoint: string;
  latency: number;
  status: 'success' | 'error' | 'cached';
  cached: boolean;
}

interface FailoverRule {
  id: string;
  name: string;
  type: 'ai' | 'blockchain' | 'data';
  primaryProvider: string;
  backupProviders: string[];
  triggerCondition: 'rate_limit' | 'error_rate' | 'latency' | 'manual';
  threshold: number;
  autoSwitch: boolean;
  lastSwitched?: string;
}

interface RateLimitStatus {
  provider: string;
  limit: number;
  remaining: number;
  resetAt: string;
  window: string;
}

const APIManagement: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'providers' | 'usage' | 'failover' | 'costs' | 'keys'>('overview');

  // API Providers State
  const [providers, setProviders] = useState<APIProvider[]>([
    {
      id: 'prov1',
      name: 'OpenAI GPT-4',
      type: 'ai',
      status: 'active',
      apiKey: 'sk-***4x9a',
      endpoint: 'https://api.openai.com/v1',
      usageLimit: 1000000,
      usageCurrent: 456789,
      costPerRequest: 0.03,
      totalCost: 1370.37,
      lastUsed: '2026-04-14 14:30',
      failoverPriority: 1,
      region: 'us-east-1',
      latency: 450,
      successRate: 99.2
    },
    {
      id: 'prov2',
      name: 'Anthropic Claude',
      type: 'ai',
      status: 'active',
      apiKey: 'sk-ant-***xyz',
      endpoint: 'https://api.anthropic.com/v1',
      usageLimit: 500000,
      usageCurrent: 234567,
      costPerRequest: 0.08,
      totalCost: 1876.54,
      lastUsed: '2026-04-14 14:25',
      failoverPriority: 2,
      region: 'us-west-2',
      latency: 520,
      successRate: 98.8
    },
    {
      id: 'prov3',
      name: 'Alchemy',
      type: 'blockchain',
      status: 'active',
      apiKey: '***alchemy***',
      endpoint: 'https://eth-mainnet.g.alchemy.com/v2',
      usageLimit: 10000000,
      usageCurrent: 4567234,
      costPerRequest: 0.0001,
      totalCost: 456.72,
      lastUsed: '2026-04-14 14:35',
      failoverPriority: 1,
      region: 'us-east-1',
      latency: 85,
      successRate: 99.9
    },
    {
      id: 'prov4',
      name: 'Infura',
      type: 'blockchain',
      status: 'active',
      apiKey: '***infura***',
      endpoint: 'https://mainnet.infura.io/v3',
      usageLimit: 100000000,
      usageCurrent: 12345678,
      costPerRequest: 0.00005,
      totalCost: 617.28,
      lastUsed: '2026-04-14 14:35',
      failoverPriority: 2,
      region: 'eu-west-1',
      latency: 120,
      successRate: 99.7
    },
    {
      id: 'prov5',
      name: 'Twitter API v2',
      type: 'social',
      status: 'rate_limited',
      apiKey: '***twitter***',
      endpoint: 'https://api.twitter.com/2',
      usageLimit: 50000,
      usageCurrent: 48765,
      costPerRequest: 0.0,
      totalCost: 0,
      lastUsed: '2026-04-14 13:00',
      failoverPriority: 1,
      region: 'us-east-1',
      latency: 180,
      successRate: 95.4
    },
    {
      id: 'prov6',
      name: 'Farcaster Hubble',
      type: 'social',
      status: 'active',
      apiKey: '***farcaster***',
      endpoint: 'https://hub.farcaster.standardcrypto.vc:2281',
      usageLimit: 1000000,
      usageCurrent: 123456,
      costPerRequest: 0.0,
      totalCost: 0,
      lastUsed: '2026-04-14 14:40',
      failoverPriority: 1,
      region: 'us-west-2',
      latency: 95,
      successRate: 99.5
    },
    {
      id: 'prov7',
      name: 'Supabase',
      type: 'storage',
      status: 'active',
      apiKey: '***supabase***',
      endpoint: 'https://*.supabase.co',
      usageLimit: 5000000,
      usageCurrent: 2345678,
      costPerRequest: 0.0,
      totalCost: 25.00,
      lastUsed: '2026-04-14 14:45',
      failoverPriority: 1,
      region: 'us-east-1',
      latency: 45,
      successRate: 99.9
    },
    {
      id: 'prov8',
      name: 'DragonflyDB',
      type: 'storage',
      status: 'active',
      apiKey: '***dragonfly***',
      endpoint: 'redis://localhost:6379',
      usageLimit: 100000000,
      usageCurrent: 8765432,
      costPerRequest: 0.0,
      totalCost: 0,
      lastUsed: '2026-04-14 14:45',
      failoverPriority: 2,
      region: 'us-east-1',
      latency: 2,
      successRate: 99.99
    }
  ]);

  // AI Usage State
  const [aiUsage, setAIUsage] = useState<AIUsage[]>([
    {
      id: 'usage1',
      model: 'gpt-4-turbo',
      provider: 'OpenAI GPT-4',
      prompt: 'Analyze contract 0x1234...',
      response: 'Contract analysis complete...',
      tokensIn: 1250,
      tokensOut: 3400,
      cost: 0.046,
      timestamp: '2026-04-14 14:30:22',
      endpoint: '/v1/chat/completions',
      latency: 423,
      status: 'success',
      cached: false
    },
    {
      id: 'usage2',
      model: 'claude-3-opus',
      provider: 'Anthropic Claude',
      prompt: 'Generate security thread...',
      response: 'Generated 5 posts...',
      tokensIn: 890,
      tokensOut: 2100,
      cost: 0.072,
      timestamp: '2026-04-14 14:25:15',
      endpoint: '/v1/messages',
      latency: 512,
      status: 'success',
      cached: false
    },
    {
      id: 'usage3',
      model: 'gpt-4-turbo',
      provider: 'OpenAI GPT-4',
      prompt: 'Analyze wallet cluster...',
      response: 'Cache hit',
      tokensIn: 450,
      tokensOut: 0,
      cost: 0,
      timestamp: '2026-04-14 14:20:00',
      endpoint: '/v1/chat/completions',
      latency: 12,
      status: 'cached',
      cached: true
    }
  ]);

  // Failover Rules
  const [failoverRules, setFailoverRules] = useState<FailoverRule[]>([
    {
      id: 'fr1',
      name: 'AI Primary Failover',
      type: 'ai',
      primaryProvider: 'prov1',
      backupProviders: ['prov2'],
      triggerCondition: 'error_rate',
      threshold: 95,
      autoSwitch: true
    },
    {
      id: 'fr2',
      name: 'Blockchain RPC Failover',
      type: 'blockchain',
      primaryProvider: 'prov3',
      backupProviders: ['prov4'],
      triggerCondition: 'latency',
      threshold: 200,
      autoSwitch: true
    },
    {
      id: 'fr3',
      name: 'Social API Failover',
      type: 'data',
      primaryProvider: 'prov5',
      backupProviders: ['prov6'],
      triggerCondition: 'rate_limit',
      threshold: 90,
      autoSwitch: false
    }
  ]);

  // UI State
  const [showAddProvider, setShowAddProvider] = useState(false);
  const [showAddFailover, setShowAddFailover] = useState(false);
  const [selectedProvider, setSelectedProvider] = useState<string | null>(null);
  const [showKeyModal, setShowKeyModal] = useState(false);
  const [newProvider, setNewProvider] = useState({
    name: '',
    type: 'ai' as 'ai' | 'blockchain' | 'data' | 'social' | 'storage',
    apiKey: '',
    endpoint: '',
    usageLimit: 100000,
    costPerRequest: 0,
    region: 'us-east-1'
  });

  // Stats
  const stats = {
    totalProviders: providers.length,
    activeProviders: providers.filter(p => p.status === 'active').length,
    totalCostToday: providers.reduce((acc, p) => acc + (p.totalCost / 30), 0),
    totalRequests: providers.reduce((acc, p) => acc + p.usageCurrent, 0),
    avgLatency: Math.round(providers.reduce((acc, p) => acc + p.latency, 0) / providers.length),
    aiCostThisMonth: providers.filter(p => p.type === 'ai').reduce((acc, p) => acc + p.totalCost, 0),
    aiRequestsToday: aiUsage.filter(u => u.timestamp.startsWith('2026-04-14')).length
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'inactive': return 'bg-gray-700 text-gray-400 border-gray-600';
      case 'rate_limited': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'error': return 'bg-red-500/20 text-red-400 border-red-500/30';
      default: return 'bg-gray-700 text-gray-400';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'ai': return <Brain className="w-4 h-4" />;
      case 'blockchain': return <Database className="w-4 h-4" />;
      case 'social': return <MessageSquare className="w-4 h-4" />;
      case 'storage': return <HardDrive className="w-4 h-4" />;
      default: return <Server className="w-4 h-4" />;
    }
  };

  const handleToggleProvider = (providerId: string) => {
    setProviders(providers.map(p =>
      p.id === providerId
        ? { ...p, status: p.status === 'active' ? 'inactive' : 'active' }
        : p
    ));
  };

  const handleAddProvider = () => {
    const provider: APIProvider = {
      id: `prov${Date.now()}`,
      name: newProvider.name,
      type: newProvider.type,
      status: 'active',
      apiKey: newProvider.apiKey,
      endpoint: newProvider.endpoint,
      usageLimit: newProvider.usageLimit,
      usageCurrent: 0,
      costPerRequest: newProvider.costPerRequest,
      totalCost: 0,
      lastUsed: 'Never',
      failoverPriority: providers.filter(p => p.type === newProvider.type).length + 1,
      region: newProvider.region,
      latency: 0,
      successRate: 100
    };
    setProviders([...providers, provider]);
    setShowAddProvider(false);
    setNewProvider({ name: '', type: 'ai', apiKey: '', endpoint: '', usageLimit: 100000, costPerRequest: 0, region: 'us-east-1' });
  };

  const handleToggleFailover = (ruleId: string) => {
    setFailoverRules(rules =>
      rules.map(r => r.id === ruleId ? { ...r, autoSwitch: !r.autoSwitch } : r)
    );
  };

  return (
    <div className="min-h-screen bg-[#0a0812] text-gray-100 font-mono selection:bg-[#7c3aed]/30">
      {/* Header */}
      <div className="bg-gradient-to-r from-[#0f0c1d] via-[#1a1525] to-[#0f0c1d] border-b border-[#7c3aed]/30">
        <div className="max-w-[1600px] mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-[#7c3aed]/20 rounded-full flex items-center justify-center">
                <Key className="w-5 h-5 text-[#7c3aed]" />
              </div>
              <div>
                <h1 className="text-xl font-bold tracking-wider">
                  API <span className="text-[#7c3aed]">COMMAND</span>
                </h1>
                <p className="text-xs text-gray-500 tracking-[0.2em]">PROVIDER ORCHESTRATION & FAILOVER CONTROL</p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 px-3 py-1.5 bg-green-500/10 border border-green-500/30 rounded">
                <Activity className="w-4 h-4 text-green-400" />
                <span className="text-sm text-green-400">{stats.activeProviders}/{stats.totalProviders} Active</span>
              </div>
              <div className="flex items-center gap-2 px-3 py-1.5 bg-[#7c3aed]/10 border border-[#7c3aed]/30 rounded">
                <DollarSign className="w-4 h-4 text-[#7c3aed]" />
                <span className="text-sm text-[#7c3aed]">${stats.aiCostThisMonth.toFixed(2)} this month</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-[1600px] mx-auto p-6 space-y-6">
        {/* Stats Row */}
        <div className="grid grid-cols-6 gap-4">
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
            <Brain className="w-5 h-5 text-[#7c3aed] mb-2" />
            <div className="text-xl font-bold">{stats.aiRequestsToday}</div>
            <div className="text-xs text-gray-500">AI Calls Today</div>
          </div>
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
            <Zap className="w-5 h-5 text-yellow-400 mb-2" />
            <div className="text-xl font-bold">{stats.avgLatency}ms</div>
            <div className="text-xs text-gray-500">Avg Latency</div>
          </div>
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
            <Database className="w-5 h-5 text-blue-400 mb-2" />
            <div className="text-xl font-bold">{(stats.totalRequests / 1000000).toFixed(2)}M</div>
            <div className="text-xs text-gray-500">Total Requests</div>
          </div>
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
            <Server className="w-5 h-5 text-green-400 mb-2" />
            <div className="text-xl font-bold">{stats.totalProviders}</div>
            <div className="text-xs text-gray-500">API Providers</div>
          </div>
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
            <DollarSign className="w-5 h-5 text-green-400 mb-2" />
            <div className="text-xl font-bold">${stats.totalCostToday.toFixed(2)}</div>
            <div className="text-xs text-gray-500">Cost Today</div>
          </div>
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
            <Shield className="w-5 h-5 text-purple-400 mb-2" />
            <div className="text-xl font-bold">{failoverRules.filter(r => r.autoSwitch).length}</div>
            <div className="text-xs text-gray-500">Auto-Failovers</div>
          </div>
        </div>

        {/* Navigation */}
        <div className="flex items-center gap-1 border-b border-gray-800">
          {[
            { id: 'overview', label: 'OVERVIEW', icon: <Activity className="w-4 h-4" /> },
            { id: 'providers', label: 'PROVIDERS', icon: <Server className="w-4 h-4" /> },
            { id: 'usage', label: 'AI USAGE', icon: <Brain className="w-4 h-4" /> },
            { id: 'failover', label: 'FAILOVER', icon: <RefreshCw className="w-4 h-4" /> },
            { id: 'costs', label: 'COST ANALYSIS', icon: <DollarSign className="w-4 h-4" /> },
            { id: 'keys', label: 'API KEYS', icon: <Key className="w-4 h-4" /> },
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

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-2 gap-6">
            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-bold mb-4">Provider Health</h3>
              <div className="space-y-3">
                {providers.map((provider) => (
                  <div key={provider.id} className="flex items-center justify-between p-3 bg-[#0a0812] rounded-lg">
                    <div className="flex items-center gap-3">
                      {getTypeIcon(provider.type)}
                      <div>
                        <div className="font-semibold">{provider.name}</div>
                        <div className="text-xs text-gray-500">{provider.region} • {provider.latency}ms</div>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="text-right">
                        <div className="text-sm">{provider.successRate}%</div>
                        <div className="text-[10px] text-gray-500">Success</div>
                      </div>
                      <span className={`px-2 py-1 rounded text-xs border ${getStatusColor(provider.status)}`}>
                        {provider.status.toUpperCase()}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-bold mb-4">Cost Breakdown by Type</h3>
              <div className="space-y-4">
                {['ai', 'blockchain', 'social', 'storage'].map((type) => {
                  const typeProviders = providers.filter(p => p.type === type);
                  const typeCost = typeProviders.reduce((acc, p) => acc + p.totalCost, 0);
                  const percentage = (typeCost / providers.reduce((acc, p) => acc + p.totalCost, 0)) * 100;
                  return (
                    <div key={type}>
                      <div className="flex items-center justify-between mb-2">
                        <span className="flex items-center gap-2 uppercase text-sm">
                          {getTypeIcon(type)}
                          {type}
                        </span>
                        <span className="text-sm font-semibold">${typeCost.toFixed(2)}</span>
                      </div>
                      <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-[#7c3aed] rounded-full"
                          style={{ width: `${percentage}%` }}
                        ></div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-bold mb-4">Recent AI Calls</h3>
              <div className="space-y-2">
                {aiUsage.slice(0, 5).map((usage) => (
                  <div key={usage.id} className="p-3 bg-[#0a0812] rounded-lg text-sm">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-semibold">{usage.model}</span>
                      <span className={`text-xs ${usage.cached ? 'text-blue-400' : usage.status === 'success' ? 'text-green-400' : 'text-red-400'}`}>
                        {usage.cached ? 'CACHED' : usage.status.toUpperCase()}
                      </span>
                    </div>
                    <div className="flex items-center gap-4 text-xs text-gray-500">
                      <span>{usage.tokensIn + usage.tokensOut} tokens</span>
                      <span>${usage.cost.toFixed(4)}</span>
                      <span>{usage.latency}ms</span>
                      <span>{new Date(usage.timestamp).toLocaleTimeString()}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-bold mb-4">Failover Status</h3>
              <div className="space-y-3">
                {failoverRules.map((rule) => (
                  <div key={rule.id} className="p-3 bg-[#0a0812] rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-semibold">{rule.name}</span>
                      <button
                        onClick={() => handleToggleFailover(rule.id)}
                        className={`flex items-center gap-1 px-2 py-1 rounded text-xs transition-all ${
                          rule.autoSwitch
                            ? 'bg-green-500/20 text-green-400'
                            : 'bg-gray-700 text-gray-400'
                        }`}
                      >
                        {rule.autoSwitch ? <ToggleRight className="w-3 h-3" /> : <ToggleLeft className="w-3 h-3" />}
                        {rule.autoSwitch ? 'AUTO' : 'MANUAL'}
                      </button>
                    </div>
                    <div className="text-xs text-gray-500">
                      Primary: {providers.find(p => p.id === rule.primaryProvider)?.name}
                      {rule.backupProviders.length > 0 && (
                        <span className="ml-2">
                          → Backups: {rule.backupProviders.map(id => providers.find(p => p.id === id)?.name).join(', ')}
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Providers Tab */}
        {activeTab === 'providers' && (
          <div className="space-y-4">
            <div className="flex justify-end">
              <button
                onClick={() => setShowAddProvider(true)}
                className="flex items-center gap-2 px-4 py-2 bg-[#7c3aed] hover:bg-[#6d28d9] text-white rounded transition-all"
              >
                <Plus className="w-4 h-4" />
                ADD PROVIDER
              </button>
            </div>

            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg overflow-hidden">
              <table className="w-full">
                <thead className="bg-[#0f0c1d] border-b border-gray-800">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">PROVIDER</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">TYPE</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">STATUS</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">USAGE</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">LATENCY</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">COST</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">ACTIONS</th>
                  </tr>
                </thead>
                <tbody>
                  {providers.map((provider) => (
                    <tr key={provider.id} className="border-b border-gray-800 hover:bg-[#0a0812]/50 transition-all">
                      <td className="px-4 py-3">
                        <div className="font-semibold">{provider.name}</div>
                        <div className="text-xs text-gray-500">{provider.endpoint}</div>
                      </td>
                      <td className="px-4 py-3">
                        <span className="flex items-center gap-2 text-sm">
                          {getTypeIcon(provider.type)}
                          {provider.type.toUpperCase()}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-1 rounded text-xs border ${getStatusColor(provider.status)}`}>
                          {provider.status.toUpperCase()}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <div className="text-sm">{provider.usageCurrent.toLocaleString()}</div>
                        <div className="w-24 h-1.5 bg-gray-800 rounded-full overflow-hidden mt-1">
                          <div
                            className="h-full bg-[#7c3aed] rounded-full"
                            style={{ width: `${(provider.usageCurrent / provider.usageLimit) * 100}%` }}
                          ></div>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-sm">{provider.latency}ms</td>
                      <td className="px-4 py-3 text-sm">${provider.totalCost.toFixed(2)}</td>
                      <td className="px-4 py-3">
                        <div className="flex gap-2">
                          <button
                            onClick={() => handleToggleProvider(provider.id)}
                            className={`px-2 py-1 rounded text-xs ${
                              provider.status === 'active'
                                ? 'bg-red-500/10 text-red-400 hover:bg-red-500/20'
                                : 'bg-green-500/10 text-green-400 hover:bg-green-500/20'
                            }`}
                          >
                            {provider.status === 'active' ? 'DISABLE' : 'ENABLE'}
                          </button>
                          <button
                            onClick={() => { setSelectedProvider(provider.id); setShowKeyModal(true); }}
                            className="p-1 bg-gray-800 rounded hover:bg-gray-700 transition-all"
                          >
                            <Key className="w-3 h-3" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* AI Usage Tab */}
        {activeTab === 'usage' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between bg-gradient-to-r from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
              <div className="flex items-center gap-4">
                <div className="relative">
                  <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
                  <input
                    type="text"
                    placeholder="Search AI calls..."
                    className="pl-10 pr-4 py-2 bg-[#0a0812] border border-gray-800 rounded text-sm w-64"
                  />
                </div>
                <select className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm">
                  <option>All Models</option>
                  <option>GPT-4</option>
                  <option>Claude</option>
                  <option>GPT-3.5</option>
                </select>
              </div>
              <button className="flex items-center gap-2 px-3 py-2 bg-gray-800 border border-gray-700 rounded text-sm text-gray-400 hover:bg-gray-700 transition-all">
                <Download className="w-4 h-4" />
                EXPORT LOGS
              </button>
            </div>

            <div className="space-y-3">
              {aiUsage.map((usage) => (
                <div key={usage.id} className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-5">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <span className={`px-2 py-1 rounded text-xs ${
                        usage.cached ? 'bg-blue-500/20 text-blue-400' :
                        usage.status === 'success' ? 'bg-green-500/20 text-green-400' :
                        'bg-red-500/20 text-red-400'
                      }`}>
                        {usage.cached ? 'CACHED' : usage.status.toUpperCase()}
                      </span>
                      <span className="text-sm font-semibold">{usage.model}</span>
                      <span className="text-xs text-gray-500">{usage.provider}</span>
                    </div>
                    <div className="text-xs text-gray-500">{new Date(usage.timestamp).toLocaleString()}</div>
                  </div>

                  <div className="grid grid-cols-4 gap-4 mb-4">
                    <div className="bg-[#0a0812] rounded p-3 text-center">
                      <div className="text-lg font-bold">{usage.tokensIn.toLocaleString()}</div>
                      <div className="text-[10px] text-gray-500">TOKENS IN</div>
                    </div>
                    <div className="bg-[#0a0812] rounded p-3 text-center">
                      <div className="text-lg font-bold">{usage.tokensOut.toLocaleString()}</div>
                      <div className="text-[10px] text-gray-500">TOKENS OUT</div>
                    </div>
                    <div className="bg-[#0a0812] rounded p-3 text-center">
                      <div className="text-lg font-bold">${usage.cost.toFixed(4)}</div>
                      <div className="text-[10px] text-gray-500">COST</div>
                    </div>
                    <div className="bg-[#0a0812] rounded p-3 text-center">
                      <div className="text-lg font-bold">{usage.latency}ms</div>
                      <div className="text-[10px] text-gray-500">LATENCY</div>
                    </div>
                  </div>

                  <div className="bg-[#0a0812] rounded p-3">
                    <div className="text-xs text-gray-500 mb-1">Prompt Preview:</div>
                    <div className="text-sm text-gray-400 truncate">{usage.prompt}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Failover Tab */}
        {activeTab === 'failover' && (
          <div className="space-y-6">
            <div className="flex justify-end">
              <button
                onClick={() => setShowAddFailover(true)}
                className="flex items-center gap-2 px-4 py-2 bg-[#7c3aed] hover:bg-[#6d28d9] text-white rounded transition-all"
              >
                <Plus className="w-4 h-4" />
                ADD FAILOVER RULE
              </button>
            </div>

            <div className="grid grid-cols-1 gap-4">
              {failoverRules.map((rule) => (
                <div key={rule.id} className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h3 className="text-lg font-bold">{rule.name}</h3>
                      <p className="text-sm text-gray-500">
                        {rule.type.toUpperCase()} • Trigger: {rule.triggerCondition.replace('_', ' ')} &gt; {rule.threshold}%
                      </p>
                    </div>
                    <button
                      onClick={() => handleToggleFailover(rule.id)}
                      className={`flex items-center gap-2 px-3 py-1.5 rounded text-sm transition-all ${
                        rule.autoSwitch
                          ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                          : 'bg-gray-800 text-gray-400 border border-gray-700'
                      }`}
                    >
                      {rule.autoSwitch ? <ToggleRight className="w-4 h-4" /> : <ToggleLeft className="w-4 h-4" />}
                      {rule.autoSwitch ? 'AUTO-SWITCH ON' : 'MANUAL MODE'}
                    </button>
                  </div>

                  <div className="flex items-center gap-4">
                    <div className="flex-1 p-4 bg-[#0a0812] rounded-lg border border-green-500/30">
                      <div className="text-xs text-green-400 mb-2">PRIMARY</div>
                      <div className="font-semibold">{providers.find(p => p.id === rule.primaryProvider)?.name}</div>
                      <div className="text-xs text-gray-500">
                        {providers.find(p => p.id === rule.primaryProvider)?.status}
                      </div>
                    </div>

                    <RefreshCw className="w-6 h-6 text-gray-600" />

                    <div className="flex-1 p-4 bg-[#0a0812] rounded-lg border border-blue-500/30">
                      <div className="text-xs text-blue-400 mb-2">BACKUP</div>
                      {rule.backupProviders.map((backupId, idx) => (
                        <div key={idx} className="font-semibold">
                          {providers.find(p => p.id === backupId)?.name}
                        </div>
                      ))}
                    </div>
                  </div>

                  {rule.lastSwitched && (
                    <div className="mt-4 text-xs text-yellow-400">
                      <AlertTriangle className="w-3 h-3 inline mr-1" />
                      Last failover: {new Date(rule.lastSwitched).toLocaleString()}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Costs Tab */}
        {activeTab === 'costs' && (
          <div className="grid grid-cols-2 gap-6">
            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-bold mb-4">Monthly Cost Trend</h3>
              <div className="h-64 bg-[#0a0812] rounded-lg flex items-center justify-center border border-gray-800">
                <div className="text-center text-gray-500">
                  <BarChart3 className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p>Cost analytics integration with billing API</p>
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-bold mb-4">Top Cost Centers</h3>
              <div className="space-y-3">
                {providers
                  .sort((a, b) => b.totalCost - a.totalCost)
                  .slice(0, 5)
                  .map((provider, idx) => (
                    <div key={provider.id} className="flex items-center justify-between p-3 bg-[#0a0812] rounded-lg">
                      <div className="flex items-center gap-3">
                        <span className="text-[#7c3aed] font-bold">#{idx + 1}</span>
                        <span>{provider.name}</span>
                      </div>
                      <span className="font-semibold">${provider.totalCost.toFixed(2)}</span>
                    </div>
                  ))}
              </div>
            </div>

            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-bold mb-4">Budget Alerts</h3>
              <div className="space-y-3">
                <div className="p-3 bg-yellow-500/10 border border-yellow-500/30 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <AlertTriangle className="w-4 h-4 text-yellow-400" />
                    <span className="font-semibold text-yellow-400">Warning: AI Budget 75%</span>
                  </div>
                  <p className="text-sm text-gray-400">OpenAI usage at 75% of monthly limit</p>
                </div>
                <div className="p-3 bg-green-500/10 border border-green-500/30 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <CheckCircle className="w-4 h-4 text-green-400" />
                    <span className="font-semibold text-green-400">Blockchain RPC: Healthy</span>
                  </div>
                  <p className="text-sm text-gray-400">Alchemy and Infura within normal limits</p>
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-bold mb-4">Cost Optimization</h3>
              <div className="space-y-3">
                <div className="p-3 bg-[#0a0812] rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm">Enable caching for GPT-4 calls</span>
                    <span className="text-green-400 text-sm">Save ~$150/mo</span>
                  </div>
                  <div className="text-xs text-gray-500">Cache similar contract analysis prompts</div>
                </div>
                <div className="p-3 bg-[#0a0812] rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm">Use Claude for long-form content</span>
                    <span className="text-green-400 text-sm">Save ~$80/mo</span>
                  </div>
                  <div className="text-xs text-gray-500">Better cost efficiency for threads</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* API Keys Tab */}
        {activeTab === 'keys' && (
          <div className="space-y-4">
            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold">API Key Management</h3>
                <button className="px-3 py-2 bg-[#7c3aed] text-white rounded text-sm hover:bg-[#6d28d9] transition-all">
                  ROTATE ALL KEYS
                </button>
              </div>
              <div className="space-y-3">
                {providers.map((provider) => (
                  <div key={provider.id} className="flex items-center justify-between p-4 bg-[#0a0812] rounded-lg">
                    <div className="flex items-center gap-3">
                      {getTypeIcon(provider.type)}
                      <div>
                        <div className="font-semibold">{provider.name}</div>
                        <div className="text-xs text-gray-500">{provider.apiKey}</div>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <button className="px-3 py-1.5 bg-gray-800 border border-gray-700 rounded text-xs text-gray-400 hover:bg-gray-700 transition-all">
                        REVEAL
                      </button>
                      <button className="px-3 py-1.5 bg-gray-800 border border-gray-700 rounded text-xs text-gray-400 hover:bg-gray-700 transition-all">
                        COPY
                      </button>
                      <button className="px-3 py-1.5 bg-[#7c3aed]/10 border border-[#7c3aed]/30 rounded text-xs text-[#7c3aed] hover:bg-[#7c3aed]/20 transition-all">
                        ROTATE
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Add Provider Modal */}
      {showAddProvider && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-[#1a1525] border border-gray-800 rounded-lg p-6 w-[500px] max-w-[90vw]">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold">Add API Provider</h2>
              <button onClick={() => setShowAddProvider(false)} className="p-1 hover:bg-gray-800 rounded">
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-500 mb-1">Provider Name</label>
                <input
                  type="text"
                  value={newProvider.name}
                  onChange={(e) => setNewProvider({ ...newProvider, name: e.target.value })}
                  className="w-full px-3 py-2 bg-[#0a0812] border border-gray-800 rounded"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-500 mb-1">Type</label>
                <select
                  value={newProvider.type}
                  onChange={(e) => setNewProvider({ ...newProvider, type: e.target.value as any })}
                  className="w-full px-3 py-2 bg-[#0a0812] border border-gray-800 rounded"
                >
                  <option value="ai">AI / LLM</option>
                  <option value="blockchain">Blockchain RPC</option>
                  <option value="social">Social Media</option>
                  <option value="storage">Storage / Database</option>
                  <option value="data">Data / Analytics</option>
                </select>
              </div>
              <div>
                <label className="block text-sm text-gray-500 mb-1">API Key</label>
                <input
                  type="password"
                  value={newProvider.apiKey}
                  onChange={(e) => setNewProvider({ ...newProvider, apiKey: e.target.value })}
                  className="w-full px-3 py-2 bg-[#0a0812] border border-gray-800 rounded"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-500 mb-1">Endpoint URL</label>
                <input
                  type="text"
                  value={newProvider.endpoint}
                  onChange={(e) => setNewProvider({ ...newProvider, endpoint: e.target.value })}
                  className="w-full px-3 py-2 bg-[#0a0812] border border-gray-800 rounded"
                />
              </div>
              <div className="flex gap-3 pt-4">
                <button
                  onClick={handleAddProvider}
                  className="flex-1 py-2 bg-[#7c3aed] text-white rounded hover:bg-[#6d28d9] transition-all"
                >
                  ADD PROVIDER
                </button>
                <button
                  onClick={() => setShowAddProvider(false)}
                  className="px-4 py-2 bg-gray-800 text-gray-400 rounded hover:bg-gray-700 transition-all"
                >
                  CANCEL
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default APIManagement;
