import { useState } from 'react';
import { Bot, MessageSquare, Settings, Zap, BarChart3, Users, Send, Terminal, Play, Pause, RotateCw, AlertCircle, CheckCircle2, Code, Webhook, Clock, Shield, TrendingUp, Activity } from 'lucide-react';
import { useAppStore } from '../store/appStore';

interface BotInstance {
  id: string;
  name: string;
  username: string;
  status: 'running' | 'stopped' | 'error';
  type: 'rugmuncher' | 'munchmaps' | 'rehab' | 'community' | 'custom';
  messages24h: number;
  activeUsers: number;
  lastActivity: string;
  commands: BotCommand[];
  webhooks: WebhookConfig[];
}

interface BotCommand {
  command: string;
  description: string;
  enabled: boolean;
  response: string;
  useAI: boolean;
  aiPrompt?: string;
}

interface WebhookConfig {
  id: string;
  url: string;
  event: string;
  status: 'active' | 'inactive';
  lastTriggered?: string;
}

interface BotAnalytics {
  totalMessages: number;
  uniqueUsers: number;
  commandUsage: { command: string; count: number }[];
  responseTime: number;
  uptime: number;
}

const mockBots: BotInstance[] = [
  {
    id: '1',
    name: 'Rug Muncher Bot',
    username: '@RugMuncherBot',
    status: 'running',
    type: 'rugmuncher',
    messages24h: 1247,
    activeUsers: 342,
    lastActivity: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
    commands: [
      { command: '/scan', description: 'Scan wallet for rug pull risks', enabled: true, response: 'Scanning wallet... Please wait.', useAI: false },
      { command: '/alert', description: 'Set price/activity alerts', enabled: true, response: 'Alert configured!', useAI: false },
      { command: '/report', description: 'Report suspicious token', enabled: true, response: 'Please provide the token contract address.', useAI: true, aiPrompt: 'Analyze the reported token and provide a risk assessment.' },
      { command: '/referral', description: 'Get your referral link', enabled: true, response: 'Here is your unique referral link: {referral_link}', useAI: false }
    ],
    webhooks: [
      { id: '1', url: 'https://api.rugmunch.com/webhook/telegram', event: 'message', status: 'active', lastTriggered: new Date(Date.now() - 1000 * 60 * 2).toISOString() }
    ]
  },
  {
    id: '2',
    name: 'MunchMaps Bot',
    username: '@MunchMapsBot',
    status: 'running',
    type: 'munchmaps',
    messages24h: 892,
    activeUsers: 156,
    lastActivity: new Date(Date.now() - 1000 * 60 * 8).toISOString(),
    commands: [
      { command: '/heatmap', description: 'Show wallet heatmap', enabled: true, response: 'Generating heatmap visualization...', useAI: false },
      { command: '/cluster', description: 'Find connected wallets', enabled: true, response: 'Analyzing wallet connections...', useAI: false },
      { command: '/track', description: 'Track whale movements', enabled: true, response: 'Tracking enabled for this wallet.', useAI: false }
    ],
    webhooks: [
      { id: '2', url: 'https://api.rugmunch.com/webhook/munchmaps', event: 'alert', status: 'active' }
    ]
  },
  {
    id: '3',
    name: 'Rehab Support Bot',
    username: '@RugRehabBot',
    status: 'running',
    type: 'rehab',
    messages24h: 234,
    activeUsers: 67,
    lastActivity: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
    commands: [
      { command: '/consult', description: 'Book consultation', enabled: true, response: 'Please select a time slot for your consultation.', useAI: false },
      { command: '/resources', description: 'Access recovery resources', enabled: true, response: 'Here are resources to help with your recovery.', useAI: true, aiPrompt: 'Provide supportive resources for rug pull victims.' },
      { command: '/community', description: 'Join support group', enabled: true, response: 'Join our private support group: [link]', useAI: false }
    ],
    webhooks: []
  },
  {
    id: '4',
    name: 'Community Manager Bot',
    username: '@RMCommunityBot',
    status: 'stopped',
    type: 'community',
    messages24h: 0,
    activeUsers: 0,
    lastActivity: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
    commands: [
      { command: '/welcome', description: 'Auto-welcome new members', enabled: false, response: 'Welcome to the community! {user}', useAI: false },
      { command: '/mod', description: 'Moderation tools', enabled: false, response: 'Moderation actions:', useAI: false }
    ],
    webhooks: []
  }
];

const mockAnalytics: BotAnalytics = {
  totalMessages: 156780,
  uniqueUsers: 12456,
  commandUsage: [
    { command: '/scan', count: 45600 },
    { command: '/alert', count: 23400 },
    { command: '/report', count: 12300 },
    { command: '/referral', count: 8900 },
    { command: '/heatmap', count: 23400 },
    { command: '/cluster', count: 15600 }
  ],
  responseTime: 1.2,
  uptime: 99.8
};

export default function TelegramBotManager() {
  const { theme } = useAppStore();
  const darkMode = theme === 'dark';

  const [bots] = useState<BotInstance[]>(mockBots);
  const [analytics] = useState<BotAnalytics>(mockAnalytics);
  const [activeTab, setActiveTab] = useState<'overview' | 'commands' | 'webhooks' | 'logs'>('overview');
  const [selectedBot, setSelectedBot] = useState<string>('1');
  const [showCommandEditor, setShowCommandEditor] = useState(false);
  const [editingCommand, setEditingCommand] = useState<BotCommand | null>(null);

  const currentBot = bots.find(b => b.id === selectedBot);
  const runningBots = bots.filter(b => b.status === 'running').length;
  const totalMessages = bots.reduce((acc, b) => acc + b.messages24h, 0);

  const formatTimeAgo = (timestamp: string) => {
    const diff = Date.now() - new Date(timestamp).getTime();
    const minutes = Math.floor(diff / 60000);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    return `${Math.floor(hours / 24)}d ago`;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
        <div className="flex items-center gap-3 mb-2">
          <Bot className="w-8 h-8 text-blue-500" />
          <h1 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
            TELEGRAM BOT ORCHESTRATOR
          </h1>
          <span className="px-2 py-1 bg-blue-500/10 text-blue-400 text-xs font-mono rounded">
            BOT CONTROL
          </span>
        </div>
        <p className={`${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
          Manage all RMI Telegram bots, commands, webhooks, and monitor performance across all bot instances.
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
          <div className="flex items-center gap-2">
            <Bot className="w-5 h-5 text-blue-400" />
            <span className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Active Bots</span>
          </div>
          <p className="text-2xl font-bold text-blue-400">{runningBots} / {bots.length}</p>
        </div>
        <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
          <div className="flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-green-400" />
            <span className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>24h Messages</span>
          </div>
          <p className="text-2xl font-bold text-green-400">{totalMessages.toLocaleString()}</p>
        </div>
        <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
          <div className="flex items-center gap-2">
            <Users className="w-5 h-5 text-purple-400" />
            <span className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Active Users</span>
          </div>
          <p className="text-2xl font-bold text-purple-400">{analytics.uniqueUsers.toLocaleString()}</p>
        </div>
        <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
          <div className="flex items-center gap-2">
            <Activity className="w-5 h-5 text-yellow-400" />
            <span className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Uptime</span>
          </div>
          <p className="text-2xl font-bold text-yellow-400">{analytics.uptime}%</p>
        </div>
      </div>

      {/* Bot Selection */}
      <div className={`rounded-lg p-4 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
        <div className="flex flex-wrap gap-2">
          {bots.map(bot => (
            <button
              key={bot.id}
              onClick={() => setSelectedBot(bot.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
                selectedBot === bot.id
                  ? 'bg-blue-600 text-white'
                  : darkMode
                  ? 'bg-slate-700 text-slate-400 hover:text-white'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              <Bot className="w-4 h-4" />
              <span className="font-medium">{bot.name}</span>
              <span className={`w-2 h-2 rounded-full ${
                bot.status === 'running' ? 'bg-green-400' :
                bot.status === 'error' ? 'bg-red-400' :
                'bg-slate-400'
              }`} />
            </button>
          ))}
        </div>
      </div>

      {/* Bot Detail View */}
      {currentBot && (
        <div className="space-y-6">
          {/* Bot Info Card */}
          <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
            <div className="flex items-start justify-between flex-wrap gap-4">
              <div>
                <div className="flex items-center gap-3">
                  <h2 className={`text-xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                    {currentBot.name}
                  </h2>
                  <span className={`px-2 py-1 rounded text-xs ${
                    currentBot.status === 'running' ? 'bg-green-500/10 text-green-400' :
                    currentBot.status === 'error' ? 'bg-red-500/10 text-red-400' :
                    'bg-slate-500/10 text-slate-400'
                  }`}>
                    {currentBot.status.toUpperCase()}
                  </span>
                </div>
                <p className="text-blue-400 mt-1">{currentBot.username}</p>
                <p className={`text-sm mt-2 ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                  Last activity: {formatTimeAgo(currentBot.lastActivity)}
                </p>
              </div>

              <div className="flex gap-2">
                {currentBot.status === 'running' ? (
                  <button className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700">
                    <Pause className="w-4 h-4" />
                    Stop Bot
                  </button>
                ) : (
                  <button className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700">
                    <Play className="w-4 h-4" />
                    Start Bot
                  </button>
                )}
                <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                  <RotateCw className="w-4 h-4" />
                  Restart
                </button>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4 mt-6">
              <div className={`p-3 rounded-lg ${darkMode ? 'bg-slate-900/50' : 'bg-slate-50'}`}>
                <p className="text-sm text-slate-500">Messages (24h)</p>
                <p className="text-xl font-bold text-white">{currentBot.messages24h.toLocaleString()}</p>
              </div>
              <div className={`p-3 rounded-lg ${darkMode ? 'bg-slate-900/50' : 'bg-slate-50'}`}>
                <p className="text-sm text-slate-500">Active Users</p>
                <p className="text-xl font-bold text-white">{currentBot.activeUsers}</p>
              </div>
              <div className={`p-3 rounded-lg ${darkMode ? 'bg-slate-900/50' : 'bg-slate-50'}`}>
                <p className="text-sm text-slate-500">Commands</p>
                <p className="text-xl font-bold text-white">{currentBot.commands.length}</p>
              </div>
            </div>
          </div>

          {/* Navigation */}
          <div className="flex flex-wrap gap-2">
            {[
              { id: 'overview', label: 'Overview', icon: BarChart3 },
              { id: 'commands', label: 'Commands', icon: Terminal },
              { id: 'webhooks', label: 'Webhooks', icon: Webhook },
              { id: 'logs', label: 'Logs', icon: Clock }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${
                  activeTab === tab.id
                    ? 'bg-blue-600 text-white'
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

          {/* Commands Tab */}
          {activeTab === 'commands' && (
            <div className={`rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
              <div className="p-4 border-b border-slate-700/50 flex items-center justify-between">
                <h3 className={`font-semibold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                  Bot Commands
                </h3>
                <button
                  onClick={() => {
                    setEditingCommand({
                      command: '',
                      description: '',
                      enabled: true,
                      response: '',
                      useAI: false
                    });
                    setShowCommandEditor(true);
                  }}
                  className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  <Zap className="w-4 h-4" />
                  Add Command
                </button>
              </div>
              <div className="divide-y divide-slate-700/30">
                {currentBot.commands.map((cmd, idx) => (
                  <div key={idx} className="p-4 hover:bg-slate-700/10">
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-3">
                        <div className={`p-2 rounded ${cmd.enabled ? 'bg-blue-500/20' : 'bg-slate-700'}`}>
                          <Terminal className={`w-4 h-4 ${cmd.enabled ? 'text-blue-400' : 'text-slate-500'}`} />
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <code className={`font-bold ${cmd.enabled ? 'text-white' : 'text-slate-500'}`}>
                              {cmd.command}
                            </code>
                            {cmd.useAI && (
                              <span className="px-2 py-0.5 rounded text-xs bg-purple-500/10 text-purple-400">
                                AI-POWERED
                              </span>
                            )}
                          </div>
                          <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                            {cmd.description}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            checked={cmd.enabled}
                            className="sr-only peer"
                          />
                          <div className="w-11 h-6 bg-slate-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                        </label>
                        <button
                          onClick={() => {
                            setEditingCommand(cmd);
                            setShowCommandEditor(true);
                          }}
                          className="p-2 text-slate-400 hover:text-white"
                        >
                          <Settings className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Webhooks Tab */}
          {activeTab === 'webhooks' && (
            <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
              <div className="flex items-center justify-between mb-4">
                <h3 className={`font-semibold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                  Webhook Configuration
                </h3>
                <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                  <Webhook className="w-4 h-4" />
                  Add Webhook
                </button>
              </div>
              <div className="space-y-3">
                {currentBot.webhooks.length > 0 ? (
                  currentBot.webhooks.map(webhook => (
                    <div key={webhook.id} className={`p-4 rounded-lg ${darkMode ? 'bg-slate-900/50' : 'bg-slate-50'}`}>
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="font-medium text-white">{webhook.event}</p>
                          <code className="text-sm text-slate-400">{webhook.url}</code>
                        </div>
                        <div className="text-right">
                          <span className={`px-2 py-1 rounded text-xs ${
                            webhook.status === 'active' ? 'bg-green-500/10 text-green-400' : 'bg-slate-500/10 text-slate-400'
                          }`}>
                            {webhook.status.toUpperCase()}
                          </span>
                          {webhook.lastTriggered && (
                            <p className="text-xs text-slate-500 mt-1">
                              Last: {formatTimeAgo(webhook.lastTriggered)}
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="p-8 text-center">
                    <Webhook className="w-12 h-12 text-slate-500 mx-auto mb-4" />
                    <p className="text-slate-500">No webhooks configured</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Analytics/Overview Tab */}
          {(activeTab === 'overview' || activeTab === 'logs') && (
            <div className="grid lg:grid-cols-2 gap-6">
              <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
                <h3 className={`font-semibold mb-4 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                  Command Usage (30 Days)
                </h3>
                <div className="space-y-3">
                  {analytics.commandUsage.slice(0, 5).map((cmd, idx) => (
                    <div key={idx}>
                      <div className="flex justify-between text-sm mb-1">
                        <span className={darkMode ? 'text-slate-300' : 'text-slate-700'}>{cmd.command}</span>
                        <span className="text-slate-400">{cmd.count.toLocaleString()}</span>
                      </div>
                      <div className={`h-2 rounded-full ${darkMode ? 'bg-slate-700' : 'bg-slate-200'}`}>
                        <div
                          className="h-full rounded-full bg-blue-500"
                          style={{ width: `${(cmd.count / analytics.commandUsage[0].count) * 100}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
                <h3 className={`font-semibold mb-4 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                  Bot Performance
                </h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-3 rounded-lg bg-slate-900/30">
                    <span className="text-slate-400">Avg Response Time</span>
                    <span className="text-green-400 font-medium">{analytics.responseTime}s</span>
                  </div>
                  <div className="flex items-center justify-between p-3 rounded-lg bg-slate-900/30">
                    <span className="text-slate-400">Total Messages</span>
                    <span className="text-white font-medium">{analytics.totalMessages.toLocaleString()}</span>
                  </div>
                  <div className="flex items-center justify-between p-3 rounded-lg bg-slate-900/30">
                    <span className="text-slate-400">Uptime</span>
                    <span className="text-green-400 font-medium">{analytics.uptime}%</span>
                  </div>
                  <div className="flex items-center justify-between p-3 rounded-lg bg-slate-900/30">
                    <span className="text-slate-400">Unique Users</span>
                    <span className="text-purple-400 font-medium">{analytics.uniqueUsers.toLocaleString()}</span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Command Editor Modal */}
      {showCommandEditor && editingCommand && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className={`w-full max-w-lg rounded-lg p-6 ${darkMode ? 'bg-slate-800 border border-slate-700' : 'bg-white border border-slate-200'}`}>
            <h3 className={`text-lg font-semibold mb-4 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
              {editingCommand.command ? 'Edit Command' : 'New Command'}
            </h3>
            <div className="space-y-4">
              <div>
                <label className={`block text-sm mb-1 ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Command</label>
                <input
                  type="text"
                  defaultValue={editingCommand.command}
                  placeholder="/command"
                  className={`w-full px-4 py-2 rounded-lg border ${darkMode ? 'bg-slate-900 border-slate-700 text-white' : 'bg-white border-slate-300'}`}
                />
              </div>
              <div>
                <label className={`block text-sm mb-1 ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Description</label>
                <input
                  type="text"
                  defaultValue={editingCommand.description}
                  className={`w-full px-4 py-2 rounded-lg border ${darkMode ? 'bg-slate-900 border-slate-700 text-white' : 'bg-white border-slate-300'}`}
                />
              </div>
              <div>
                <label className={`block text-sm mb-1 ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Response</label>
                <textarea
                  defaultValue={editingCommand.response}
                  rows={3}
                  className={`w-full px-4 py-2 rounded-lg border ${darkMode ? 'bg-slate-900 border-slate-700 text-white' : 'bg-white border-slate-300'}`}
                />
              </div>
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  defaultChecked={editingCommand.useAI}
                  id="useAI"
                  className="rounded border-slate-500"
                />
                <label htmlFor="useAI" className={`${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>
                  Use AI for response generation
                </label>
              </div>
            </div>
            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setShowCommandEditor(false)}
                className="flex-1 py-2 bg-slate-700 text-white rounded-lg hover:bg-slate-600"
              >
                Cancel
              </button>
              <button
                onClick={() => setShowCommandEditor(false)}
                className="flex-1 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Save Command
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
