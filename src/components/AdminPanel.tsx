/**
 * Admin Panel - Total RMI Ecosystem Control
 * God mode for developers - control everything
 */
import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../services/api';
import { db } from '../services/supabase';
import {
  Cloud,
  Search,
  Database,
  Server,
  Activity,
  Users,
  Shield,
  Terminal,
  Clock,
  HardDrive,
  Cpu,
  Eye,
  Zap,
  Settings,
  ChevronDown,
  ChevronRight,
  Bot,
  Globe,
  MessageSquare,
  Bell,
  Play,
  Pause,
  RotateCcw,
  Send,
  Trash2,
  Edit3,
  Plus,
  Power,
  Radio,
  Layout,
  Coins,
  AlertCircle,
  Brain,
  RefreshCw,
  Download,
  Upload,
  Wifi,
  ToggleLeft,
  FileText,
  Key,
} from 'lucide-react';

import UserManagement from './admin/UserManagement';
import EvidenceManagement from './admin/EvidenceManagement';
import InvestigationOperations from './admin/InvestigationOperations';
import RevenueDashboard from './admin/RevenueDashboard';
import TrenchesRehabManagement from './admin/TrenchesRehabManagement';
import FeatureFlags from './admin/FeatureFlags';
import AuditLogs from './admin/AuditLogs';
import APIManagement from './admin/APIManagement';
import ContentManagement from './admin/ContentManagement';
import InfrastructureDashboard from './admin/InfrastructureDashboard';

// N8N configuration
const N8N_BASE = 'http://167.86.116.51:5678';

// Telegram bots configuration
const BOTS = [
  { id: 'rugmunch', name: '@rugmunchbot', token: '8720275246:AAHaQWZlQZybgVyJ50YFl7707AAjEjDFDhU', type: 'main', status: 'active' },
  { id: 'backend', name: '@rmi_backend_bot', token: '8622158622:AAGoKEE-kt-eQ9yO9XcI76Z1gmFsPNfN6Jk', type: 'monitoring', status: 'active' },
  { id: 'alerts', name: '@rmi_alerts_bot', token: '8579473108:AAHod-yDi3Oe_X6dYxQLPi9EpZjmgLO7amk', type: 'free_alerts', status: 'active' },
  { id: 'alpha', name: '@rmi_alpha_bot', token: '8215310500:AAHqfVLJhP3opGN6-kh2IJ6Oai-xtBIeKZQ', type: 'paid_alerts', status: 'active' },
];

// N8N Workflows
const WORKFLOWS = [
  { id: 'scan-result', name: 'Scan Results → @munchscans', webhook: '/webhook/scan-result', active: true },
  { id: 'backend-alert', name: 'Backend Health → @rmi_backend', webhook: '/webhook/backend-alert', active: true },
  { id: 'whale-alert', name: 'Whale Alerts → @rmi_alpha_alerts', webhook: '/webhook/whale-alert', active: true },
  { id: 'scam-alert', name: 'Scam Detection → @rmi_alpha_alerts', webhook: '/webhook/scam-alert', active: true },
  { id: 'daily-report', name: 'Daily Intel Report (Scheduled)', webhook: null, active: true, schedule: '9:00 AM' },
];

export default function AdminPanel() {
  const [activeTab, setActiveTab] = useState<'overview' | 'users' | 'evidence' | 'investigations' | 'trenches' | 'revenue' | 'feature_flags' | 'audit_logs' | 'api_mgmt' | 'bots' | 'n8n' | 'website' | 'database' | 'ai' | 'alerts' | 'system' | 'content' | 'infrastructure'>('overview');
  const [testMessage, setTestMessage] = useState('');
  const [n8nStatus, setN8nStatus] = useState<'unknown' | 'online' | 'offline'>('unknown');
  const [adminKey, setAdminKey] = useState(localStorage.getItem('admin_key') || '');
  const [dbQuery, setDbQuery] = useState('SELECT * FROM profiles LIMIT 10');
  const [dbResult, setDbResult] = useState<any>(null);
  const [logLevel, setLogLevel] = useState<string>('');
  const queryClient = useQueryClient();

  // Admin data fetching
  const { data: systemData, isLoading: systemLoading } = useQuery({
    queryKey: ['admin-system', adminKey],
    queryFn: () => api.getSystemStats(adminKey),
    enabled: !!adminKey && (activeTab === 'system' || activeTab === 'overview'),
    refetchInterval: 5000,
  });

  const { data: servicesData } = useQuery({
    queryKey: ['admin-services', adminKey],
    queryFn: () => api.getServices(adminKey),
    enabled: !!adminKey && (activeTab === 'system' || activeTab === 'overview'),
    refetchInterval: 10000,
  });

  const { data: logsData, refetch: refetchLogs } = useQuery({
    queryKey: ['admin-logs', adminKey, logLevel],
    queryFn: () => api.getLogs(adminKey, 100, logLevel || undefined),
    enabled: !!adminKey && activeTab === 'system',
  });

  const { data: dbTablesData } = useQuery({
    queryKey: ['admin-db-tables', adminKey],
    queryFn: () => api.getDatabaseTables(adminKey),
    enabled: !!adminKey && activeTab === 'database',
  });

  const { data: botsData } = useQuery({
    queryKey: ['admin-bots', adminKey],
    queryFn: () => api.getBots(adminKey),
    enabled: !!adminKey && activeTab === 'bots',
  });

  const { data: alertsData, refetch: refetchAlerts } = useQuery({
    queryKey: ['admin-alerts', adminKey],
    queryFn: () => api.getAlertsHistory(adminKey, 50),
    enabled: !!adminKey && activeTab === 'alerts',
  });

  const serviceActionMutation = useMutation({
    mutationFn: ({ serviceId, action }: { serviceId: string; action: string }) =>
      api.serviceAction(adminKey, serviceId, action),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin-services'] }),
  });

  const sendAlertMutation = useMutation({
    mutationFn: ({ message, channel }: { message: string; channel: string }) =>
      api.sendTestAlert(adminKey, message, channel),
    onSuccess: () => refetchAlerts(),
  });

  const runQueryMutation = useMutation({
    mutationFn: (sql: string) => api.runDatabaseQuery(adminKey, sql, 100),
    onSuccess: (data) => setDbResult(data),
  });

  // Fetch data
  const { data: health } = useQuery({
    queryKey: ['admin-health'],
    queryFn: () => api.health(),
    refetchInterval: 5000,
  });

  const { data: stats } = useQuery({
    queryKey: ['admin-stats'],
    queryFn: () => api.getStats(),
    refetchInterval: 10000,
  });

  const { data: allWallets } = useQuery({
    queryKey: ['admin-wallets'],
    queryFn: async () => {
      const { data } = await db.wallets.getAll();
      return data || [];
    },
  });

  const { data: allInvestigations } = useQuery({
    queryKey: ['admin-investigations'],
    queryFn: async () => {
      const { data } = await db.investigations.getAll();
      return data || [];
    },
  });

  // Check N8N status
  useEffect(() => {
    fetch(`${N8N_BASE}/health`, { mode: 'no-cors' })
      .then(() => setN8nStatus('online'))
      .catch(() => setN8nStatus('offline'));
  }, []);

  const sendTestAlert = async (webhook: string) => {
    try {
      await fetch(`${N8N_BASE}${webhook}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: testMessage || 'Test alert from admin panel',
          timestamp: new Date().toISOString(),
          test: true,
        }),
      });
      alert('Test alert sent!');
    } catch (err) {
      alert('Failed to send test alert: ' + err);
    }
  };

  return (
    <div className="p-6 max-w-[1600px] mx-auto">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-red-600 to-orange-600 flex items-center justify-center">
            <Shield className="w-6 h-6 text-white" />
          </div>
          <div className="flex-1">
            <h1 className="text-2xl font-bold text-white flex items-center gap-2">
              RMI Control Center
              <span className="px-2 py-0.5 bg-red-500/20 text-red-400 text-xs rounded border border-red-500/50">DEV MODE</span>
            </h1>
            <p className="text-gray-400">Complete ecosystem management and monitoring</p>
          </div>
          <div className="flex items-center gap-2">
            <input
              type="password"
              placeholder="Admin Key"
              value={adminKey}
              onChange={(e) => {
                setAdminKey(e.target.value);
                localStorage.setItem('admin_key', e.target.value);
              }}
              className="bg-crypto-dark border border-crypto-border rounded px-3 py-2 text-sm text-white w-48"
            />
            {adminKey ? (
              <span className="px-2 py-1 bg-green-500/20 text-green-400 text-xs rounded">KEY SET</span>
            ) : (
              <span className="px-2 py-1 bg-red-500/20 text-red-400 text-xs rounded">NO KEY</span>
            )}
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
        {[
          { id: 'overview', label: 'Overview', icon: Activity },
          { id: 'users', label: 'Users', icon: Users },
          { id: 'content', label: 'Content', icon: FileText },
          { id: 'evidence', label: 'Evidence', icon: Shield },
          { id: 'investigations', label: 'Investigations', icon: Search },
          { id: 'trenches', label: 'Trenches & Rehab', icon: MessageSquare },
          { id: 'revenue', label: 'Revenue', icon: Coins },
          { id: 'feature_flags', label: 'Features', icon: ToggleLeft },
          { id: 'audit_logs', label: 'Audit Logs', icon: Eye },
          { id: 'api_mgmt', label: 'API', icon: Key },
          { id: 'bots', label: 'Bots', icon: Bot },
          { id: 'n8n', label: 'N8N', icon: Zap },
          { id: 'website', label: 'Website', icon: Globe },
          { id: 'database', label: 'Database', icon: Database },
          { id: 'ai', label: 'AI/OSINT', icon: Brain },
          { id: 'alerts', label: 'Alerts', icon: Bell },
          { id: 'infrastructure', label: 'Infra', icon: Cloud },
          { id: 'system', label: 'System', icon: Server },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all whitespace-nowrap ${
              activeTab === tab.id
                ? 'bg-red-500/20 text-red-400 border border-red-500/50'
                : 'bg-crypto-card text-gray-400 border border-crypto-border hover:border-gray-500'
            }`}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* OVERVIEW TAB */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* Quick Stats Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-3">
            <QuickStat title="Wallets" value={allWallets?.length || 0} icon={Database} color="blue" />
            <QuickStat title="Cases" value={allInvestigations?.length || 0} icon={Shield} color="purple" />
            <QuickStat title="API Calls" value={stats?.api_calls_today || 0} icon={Terminal} color="green" />
            <QuickStat title="Cache Hit" value={`${Math.round((stats?.cache_hit_rate || 0) * 100)}%`} icon={Zap} color="yellow" />
            <QuickStat title="Bots" value="4" icon={Bot} color="cyan" />
            <QuickStat title="Workflows" value="5" icon={Zap} color="orange" />
            <QuickStat title="N8N" value={n8nStatus === 'online' ? 'ON' : 'OFF'} icon={Radio} color={n8nStatus === 'online' ? 'green' : 'red'} />
            <QuickStat title="Scans" value="342K+" icon={Eye} color="pink" />
          </div>

          {/* System Status Cards */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Backend Services */}
            <div className="crypto-card">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Server className="w-5 h-5 text-neon-green" />
                Backend Services
              </h3>
              <div className="space-y-2">
                {servicesData?.services?.map((svc: any) => (
                  <ServiceRow key={svc.id} name={svc.name} status={svc.online} port={String(svc.port)} />
                )) || (
                  <>
                    <ServiceRow name="FastAPI" status={health?.status === 'healthy' || false} port="8000" />
                    <ServiceRow name="Dragonfly Cache" status={health?.dragonfly || false} port="6379" />
                    <ServiceRow name="Supabase PostgreSQL" status={health?.supabase || false} port="5432" />
                    <ServiceRow name="N8N Automation" status={n8nStatus === 'online'} port="5678" />
                    <ServiceRow name="The Trenches" status={true} port="8888" />
                  </>
                )}
              </div>
            </div>

            {/* Bot Fleet Status */}
            <div className="crypto-card">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Bot className="w-5 h-5 text-neon-blue" />
                Bot Fleet
              </h3>
              <div className="space-y-2">
                {BOTS.map((bot) => (
                  <div key={bot.id} className="flex items-center justify-between p-2 bg-crypto-dark rounded">
                    <div className="flex items-center gap-2">
                      <Bot className="w-4 h-4 text-neon-blue" />
                      <span className="text-sm text-white">{bot.name}</span>
                      <span className="px-1.5 py-0.5 bg-blue-500/20 text-blue-400 text-[10px] rounded">{bot.type}</span>
                    </div>
                    <span className={`w-2 h-2 rounded-full ${bot.status === 'active' ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
                  </div>
                ))}
              </div>
            </div>

            {/* Quick Actions */}
            <div className="crypto-card">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Zap className="w-5 h-5 text-neon-yellow" />
                Quick Actions
              </h3>
              <div className="grid grid-cols-2 gap-2">
                <ActionButton label="Restart N8N" icon={RotateCcw} onClick={() => alert('Restart command sent')} />
                <ActionButton label="Clear Cache" icon={Trash2} onClick={() => alert('Cache cleared')} />
                <ActionButton label="Test Alert" icon={Send} onClick={() => sendTestAlert('/webhook/backend-alert')} />
                <ActionButton label="Backup DB" icon={Download} onClick={() => alert('Backup started')} />
                <ActionButton label="Update Site" icon={Globe} onClick={() => alert('Website refresh triggered')} />
                <ActionButton label="Health Check" icon={Activity} onClick={() => window.location.reload()} />
              </div>
            </div>
          </div>

          {/* Expandable Details */}
          <div className="space-y-2">
            <Expandable title="Database Schema" icon={Database} defaultOpen>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
                <SchemaCard name="wallets" rows={allWallets?.length} cols={['address', 'chain', 'risk', 'tags']} />
                <SchemaCard name="investigations" rows={allInvestigations?.length} cols={['title', 'status', 'tier', 'wallets']} />
                <SchemaCard name="evidence" rows={0} cols={['type', 'source', 'confidence', 'content']} />
                <SchemaCard name="users" rows={0} cols={['email', 'role', 'tier', 'reputation']} />
                <SchemaCard name="ai_cache" rows={0} cols={['wallet', 'chain', 'analysis', 'model']} />
                <SchemaCard name="alerts" rows={0} cols={['type', 'channel', 'message', 'sent']} />
              </div>
            </Expandable>

            <Expandable title="API Endpoints" icon={Terminal}>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 font-mono text-sm">
                <Endpoint method="GET" path="/health" desc="Service health check" />
                <Endpoint method="POST" path="/wallet/analyze" desc="Deep wallet analysis" />
                <Endpoint method="GET" path="/wallet/lookup" desc="Cached lookup" />
                <Endpoint method="POST" path="/investigation/trace" desc="Transaction tracing" />
                <Endpoint method="POST" path="/investigation/ai-analyze" desc="AI pattern detection" />
                <Endpoint method="POST" path="/investigation/patterns" desc="Risk pattern scan" />
                <Endpoint method="POST" path="/webhook/scan-result" desc="→ Telegram" />
                <Endpoint method="POST" path="/webhook/whale-alert" desc="→ Telegram" />
              </div>
            </Expandable>

            <Expandable title="System Configuration" icon={Settings}>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 font-mono text-sm">
                <ConfigItem label="N8N URL" value={N8N_BASE} />
                <ConfigItem label="Supabase URL" value="https://ufblzfxqwgaekrewncbi.supabase.co" />
                <ConfigItem label="API Base" value="http://localhost:8000" />
                <ConfigItem label="Dragonfly" value="localhost:6379" />
                <ConfigItem label="The Trenches" value="167.86.116.51:8888" />
                <ConfigItem label="Website" value="167.86.116.51:8889" />
              </div>
            </Expandable>

            <Expandable title="Raw Data View" icon={Eye}>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                <DataPreview title="Health Response" data={health} />
                <DataPreview title="Stats Response" data={stats} />
              </div>
            </Expandable>
          </div>
        </div>
      )}

      {/* BOTS TAB */}
      {activeTab === 'bots' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <Bot className="w-6 h-6 text-neon-blue" />
              Telegram Bot Fleet
            </h2>
            <button className="btn-primary flex items-center gap-2" onClick={() => alert('Add bot via Redis or database')}>
              <Plus className="w-4 h-4" />
              Add Bot
            </button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {botsData?.bots?.map((bot: any) => (
              <div key={bot.id} className="crypto-card">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-full bg-blue-500/20 flex items-center justify-center">
                      <Bot className="w-6 h-6 text-blue-400" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-white">{bot.name}</h3>
                      <span className="px-2 py-0.5 bg-blue-500/20 text-blue-400 text-xs rounded">{bot.type}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`w-2 h-2 rounded-full ${bot.status === 'active' ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
                    <button className="p-2 hover:bg-crypto-dark rounded" onClick={() => api.updateBot(adminKey, bot.id, { status: bot.status === 'active' ? 'stopped' : 'active' })}>
                      <Power className="w-4 h-4 text-gray-400" />
                    </button>
                  </div>
                </div>

                <div className="space-y-3">
                  <div>
                    <label className="text-xs text-gray-500">Token</label>
                    <div className="flex gap-2">
                      <input
                        type="password"
                        value={bot.token || '***'}
                        readOnly
                        className="flex-1 bg-crypto-dark border border-crypto-border rounded px-3 py-2 text-sm text-gray-400"
                      />
                      <button className="btn-secondary px-3">
                        <Eye className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <button className="flex-1 btn-primary text-sm py-2" onClick={() => sendAlertMutation.mutate({ message: `Test from ${bot.name}`, channel: bot.name })}>Send Test</button>
                    <button className="flex-1 btn-secondary text-sm py-2" onClick={() => alert('Edit bot via Redis CLI')}>Edit</button>
                    <button className="flex-1 btn-secondary text-sm py-2 text-red-400" onClick={() => api.updateBot(adminKey, bot.id, { status: 'stopped' })}>Stop</button>
                  </div>

                  <div className="pt-3 border-t border-crypto-border">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">Messages Today</span>
                      <span className="text-white">{bot.messages_today ?? '-'}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">Subscribers</span>
                      <span className="text-white">{bot.subscribers ?? '-'}</span>
                    </div>
                  </div>
                </div>
              </div>
            )) || (
              <div className="crypto-card col-span-2 text-center py-12 text-gray-500">
                <Bot className="w-8 h-8 mx-auto mb-2" />
                <p>No bots configured or admin key missing</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* N8N TAB */}
      {activeTab === 'n8n' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <Zap className="w-6 h-6 text-neon-yellow" />
              N8N Workflow Automation
            </h2>
            <div className="flex gap-2">
              <button className="btn-secondary flex items-center gap-2">
                <RefreshCw className="w-4 h-4" />
                Refresh
              </button>
              <a
                href={N8N_BASE}
                target="_blank"
                rel="noopener noreferrer"
                className="btn-primary flex items-center gap-2"
              >
                Open N8N
                <Globe className="w-4 h-4" />
              </a>
            </div>
          </div>

          {/* Test Alert Section */}
          <div className="crypto-card">
            <h3 className="text-lg font-semibold text-white mb-4">Send Test Alert</h3>
            <div className="flex gap-3">
              <input
                type="text"
                placeholder="Enter test message..."
                value={testMessage}
                onChange={(e) => setTestMessage(e.target.value)}
                className="flex-1 bg-crypto-dark border border-crypto-border rounded px-4 py-2 text-white"
              />
              <select className="bg-crypto-card border border-crypto-border rounded px-3 py-2 text-white">
                <option>Select Channel...</option>
                <option>@munchscans</option>
                <option>@rmi_backend</option>
                <option>@rmi_alerts</option>
                <option>@rmi_alpha_alerts</option>
              </select>
              <button
                onClick={() => sendTestAlert('/webhook/scan-result')}
                className="btn-primary flex items-center gap-2"
              >
                <Send className="w-4 h-4" />
                Send
              </button>
            </div>
          </div>

          {/* Workflows */}
          <div className="space-y-3">
            {WORKFLOWS.map((wf) => (
              <div key={wf.id} className="crypto-card flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${wf.active ? 'bg-yellow-500/20' : 'bg-gray-500/20'}`}>
                    <Zap className={`w-5 h-5 ${wf.active ? 'text-yellow-400' : 'text-gray-400'}`} />
                  </div>
                  <div>
                    <h4 className="font-medium text-white">{wf.name}</h4>
                    <div className="flex items-center gap-2 text-sm text-gray-400">
                      {wf.webhook && <span className="font-mono text-xs">{wf.webhook}</span>}
                      {wf.schedule && <span className="text-yellow-400">⏰ {wf.schedule}</span>}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className={`px-2 py-1 rounded text-xs ${wf.active ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'}`}>
                    {wf.active ? 'ACTIVE' : 'PAUSED'}
                  </span>
                  <button className="p-2 hover:bg-crypto-dark rounded">
                    {wf.active ? <Pause className="w-4 h-4 text-yellow-400" /> : <Play className="w-4 h-4 text-green-400" />}
                  </button>
                  <button className="p-2 hover:bg-crypto-dark rounded">
                    <Edit3 className="w-4 h-4 text-gray-400" />
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Execution Logs */}
          <div className="crypto-card">
            <h3 className="text-lg font-semibold text-white mb-4">Recent Executions</h3>
            <div className="text-center py-8 text-gray-500">
              <Clock className="w-8 h-8 mx-auto mb-2" />
              <p>Execution history will appear here</p>
            </div>
          </div>
        </div>
      )}

      {/* WEBSITE TAB */}
      {activeTab === 'website' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <Globe className="w-6 h-6 text-neon-purple" />
              Website Management
            </h2>
            <div className="flex gap-2">
              <a
                href="http://167.86.116.51:8889"
                target="_blank"
                rel="noopener noreferrer"
                className="btn-primary flex items-center gap-2"
              >
                View Site
                <Globe className="w-4 h-4" />
              </a>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Site Sections */}
            <div className="crypto-card">
              <h3 className="text-lg font-semibold text-white mb-4">Active Sections</h3>
              <div className="space-y-2">
                <ToggleItem label="Hero Scanner" enabled={true} />
                <ToggleItem label="Twitter-Style Alert Feed" enabled={true} />
                <ToggleItem label="V2 Coming Soon Banner" enabled={true} />
                <ToggleItem label="The Trenches (formerly Snitch Board)" enabled={true} />
                <ToggleItem label="Rug Pull Rehab Booking" enabled={true} />
                <ToggleItem label="1-1 Reimbursement" enabled={true} />
                <ToggleItem label="Newsletter Signup" enabled={true} />
                <ToggleItem label="Crypto Payments" enabled={true} />
              </div>
            </div>

            {/* Content Management */}
            <div className="crypto-card">
              <h3 className="text-lg font-semibold text-white mb-4">Content Controls</h3>
              <div className="space-y-3">
                <button className="w-full btn-secondary text-left flex items-center justify-between">
                  <span>Edit Hero Message</span>
                  <Edit3 className="w-4 h-4" />
                </button>
                <button className="w-full btn-secondary text-left flex items-center justify-between">
                  <span>Manage Alert Feed</span>
                  <Bell className="w-4 h-4" />
                </button>
                <button className="w-full btn-secondary text-left flex items-center justify-between">
                  <span>The Trenches Tips (formerly Snitch Board)</span>
                  <MessageSquare className="w-4 h-4" />
                </button>
                <button className="w-full btn-secondary text-left flex items-center justify-between">
                  <span>Rehab Bookings</span>
                  <Layout className="w-4 h-4" />
                </button>
                <button className="w-full btn-secondary text-left flex items-center justify-between">
                  <span>Newsletter Subscribers</span>
                  <Users className="w-4 h-4" />
                </button>
                <button className="w-full btn-secondary text-left flex items-center justify-between">
                  <span>Payment Settings</span>
                  <Coins className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Stats */}
            <div className="crypto-card">
              <h3 className="text-lg font-semibold text-white mb-4">Website Stats</h3>
              <div className="grid grid-cols-2 gap-4">
                <StatBox label="Visitors Today" value="-" />
                <StatBox label="Scans Initiated" value="-" />
                <StatBox label="Tips Submitted" value="-" />
                <StatBox label="Rehab Bookings" value="-" />
                <StatBox label="Newsletter Subs" value="15,000+" />
                <StatBox label="Revenue (ETH)" value="-" />
              </div>
            </div>

            {/* Airdrop Management */}
            <div className="crypto-card">
              <h3 className="text-lg font-semibold text-white mb-4">V2 Airdrop</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-gray-400">Waitlist Registrations</span>
                  <span className="text-white font-semibold">-</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-400">Tokens Allocated</span>
                  <span className="text-white font-semibold">-</span>
                </div>
                <button className="w-full btn-primary">Export Waitlist</button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* DATABASE TAB */}
      {activeTab === 'database' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <Database className="w-6 h-6 text-neon-green" />
              Database Management
            </h2>
            <div className="flex gap-2">
              <button className="btn-secondary flex items-center gap-2" onClick={() => alert('Backup queued via service action')}>
                <Download className="w-4 h-4" />
                Backup
              </button>
              <button className="btn-secondary flex items-center gap-2" onClick={() => alert('Restore not yet implemented')}>
                <Upload className="w-4 h-4" />
                Restore
              </button>
            </div>
          </div>

          <div className="crypto-card">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-crypto-border text-gray-400">
                    <th className="text-left p-3">Table</th>
                    <th className="text-left p-3">Rows</th>
                    <th className="text-left p-3">Size</th>
                    <th className="text-left p-3">Last Write</th>
                    <th className="text-left p-3">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {dbTablesData?.tables?.map((t: any) => (
                    <TableRow key={t.name} name={t.name} rows={t.rows} size={t.size} lastWrite={t.last_write} />
                  )) || (
                    <>
                      <TableRow name="wallets" rows={allWallets?.length} size="-" lastWrite="-" />
                      <TableRow name="investigations" rows={allInvestigations?.length} size="-" lastWrite="-" />
                      <TableRow name="evidence" rows={0} size="-" lastWrite="-" />
                      <TableRow name="users" rows={0} size="-" lastWrite="-" />
                      <TableRow name="ai_cache" rows={0} size="-" lastWrite="-" />
                      <TableRow name="system_health_log" rows={0} size="-" lastWrite="-" />
                    </>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="crypto-card">
              <h3 className="text-lg font-semibold text-white mb-4">Query Console</h3>
              <textarea
                value={dbQuery}
                onChange={(e) => setDbQuery(e.target.value)}
                placeholder="SELECT * FROM profiles LIMIT 10"
                className="w-full h-32 bg-crypto-dark border border-crypto-border rounded p-3 text-sm font-mono text-white"
              />
              <button
                className="w-full mt-3 btn-primary"
                onClick={() => runQueryMutation.mutate(dbQuery)}
                disabled={runQueryMutation.isPending}
              >
                {runQueryMutation.isPending ? 'Executing...' : 'Execute Query'}
              </button>
              {dbResult && (
                <div className="mt-4 bg-crypto-dark rounded p-3 overflow-auto max-h-64">
                  <div className="text-xs text-gray-500 mb-2">{dbResult.row_count} rows</div>
                  <pre className="text-xs text-gray-300">{JSON.stringify(dbResult.data, null, 2)}</pre>
                </div>
              )}
            </div>

            <div className="crypto-card">
              <h3 className="text-lg font-semibold text-white mb-4">Row Level Security</h3>
              <div className="space-y-2">
                <ToggleItem label="Enable RLS on wallets" enabled={true} />
                <ToggleItem label="Enable RLS on investigations" enabled={true} />
                <ToggleItem label="Enable RLS on evidence" enabled={true} />
                <ToggleItem label="Users can only see own data" enabled={true} />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* AI/OSINT TAB */}
      {activeTab === 'ai' && (
        <AIOSINTTab />
      )}

      {/* ALERTS TAB */}
      {activeTab === 'alerts' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <Bell className="w-6 h-6 text-neon-red" />
              Alert System
            </h2>
            <button className="btn-secondary flex items-center gap-2" onClick={() => refetchAlerts()}>
              <RefreshCw className="w-4 h-4" />
              Refresh
            </button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="crypto-card">
              <h3 className="text-lg font-semibold text-white mb-4">Alert Channels</h3>
              <div className="space-y-3">
                <ChannelRow name="@munchscans" type="Public" bot="@rugmunchbot" status="active" />
                <ChannelRow name="@rmi_backend" type="Private" bot="@rmi_backend_bot" status="active" />
                <ChannelRow name="@rmi_alerts" type="Public" bot="@rmi_alerts_bot" status="active" />
                <ChannelRow name="@rmi_alpha_alerts" type="Premium" bot="@rmi_alpha_bot" status="active" />
              </div>
            </div>

            <div className="crypto-card">
              <h3 className="text-lg font-semibold text-white mb-4">Alert Types</h3>
              <div className="space-y-2">
                <ToggleItem label="Critical Scam Detection" enabled={true} />
                <ToggleItem label="Whale Movements" enabled={true} />
                <ToggleItem label="New Investigation Started" enabled={true} />
                <ToggleItem label="Evidence Submitted" enabled={false} />
                <ToggleItem label="User Reports" enabled={true} />
                <ToggleItem label="System Health" enabled={true} />
              </div>
            </div>
          </div>

          <div className="crypto-card">
            <h3 className="text-lg font-semibold text-white mb-4">Send Test Alert</h3>
            <div className="flex gap-3 mb-4">
              <input
                type="text"
                placeholder="Test message..."
                value={testMessage}
                onChange={(e) => setTestMessage(e.target.value)}
                className="flex-1 bg-crypto-dark border border-crypto-border rounded px-4 py-2 text-white"
              />
              <button
                className="btn-primary flex items-center gap-2"
                onClick={() => sendAlertMutation.mutate({ message: testMessage || 'Test alert', channel: '@rmi_backend' })}
                disabled={sendAlertMutation.isPending}
              >
                <Send className="w-4 h-4" />
                {sendAlertMutation.isPending ? 'Sending...' : 'Send'}
              </button>
            </div>
            <h3 className="text-lg font-semibold text-white mb-4">Recent Alerts</h3>
            <div className="space-y-2">
              {alertsData?.alerts?.map((alert: any, i: number) => (
                <AlertRow
                  key={alert.id || i}
                  type={alert.severity || 'system'}
                  message={alert.message}
                  time={alert.timestamp ? new Date(alert.timestamp).toLocaleTimeString() : 'recent'}
                  channel={alert.channel || '@rmi_backend'}
                />
              )) || (
                <div className="text-center py-4 text-gray-500">
                  <Clock className="w-6 h-6 mx-auto mb-2" />
                  <p>No recent alerts or admin key missing</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* SYSTEM TAB */}
      {activeTab === 'system' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <Server className="w-6 h-6 text-neon-green" />
              System Control
            </h2>
            {systemLoading && <span className="text-sm text-gray-400 animate-pulse">Loading...</span>}
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <SystemCard title="CPU" value={systemData?.cpu?.percent != null ? `${systemData.cpu.percent}%` : '-'} icon={Cpu} />
            <SystemCard title="Memory" value={systemData?.memory?.percent != null ? `${systemData.memory.percent}%` : '-'} icon={HardDrive} />
            <SystemCard title="Disk" value={systemData?.disk?.percent != null ? `${systemData.disk.percent}%` : '-'} icon={Database} />
            <SystemCard title="Uptime" value={systemData?.uptime?.formatted || '-'} icon={Wifi} />
          </div>

          <div className="crypto-card">
            <h3 className="text-lg font-semibold text-white mb-4">Service Control</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {servicesData?.services?.map((svc: any) => (
                <div key={svc.id} className="flex items-center justify-between p-3 bg-crypto-dark rounded">
                  <div>
                    <p className="text-white font-medium">{svc.name}</p>
                    <p className="text-xs text-gray-500">Port {svc.port} • {svc.status}</p>
                  </div>
                  <div className="flex gap-2">
                    <button className="p-2 hover:bg-crypto-card rounded text-green-400" onClick={() => serviceActionMutation.mutate({ serviceId: svc.id, action: 'start' })} title="Start">
                      <Play className="w-4 h-4" />
                    </button>
                    <button className="p-2 hover:bg-crypto-card rounded text-yellow-400" onClick={() => serviceActionMutation.mutate({ serviceId: svc.id, action: 'restart' })} title="Restart">
                      <RotateCcw className="w-4 h-4" />
                    </button>
                    <button className="p-2 hover:bg-crypto-card rounded text-red-400" onClick={() => serviceActionMutation.mutate({ serviceId: svc.id, action: 'stop' })} title="Stop">
                      <Pause className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              )) || (
                <>
                  <ServiceControl name="FastAPI Backend" port="8000" status="running" />
                  <ServiceControl name="N8N Automation" port="5678" status="running" />
                  <ServiceControl name="The Trenches" port="8888" status="running" />
                  <ServiceControl name="Website" port="8889" status="running" />
                  <ServiceControl name="Dragonfly Cache" port="6379" status="running" />
                  <ServiceControl name="PostgreSQL" port="5432" status="running" />
                </>
              )}
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="crypto-card">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white">Log Viewer</h3>
                <select
                  value={logLevel}
                  onChange={(e) => setLogLevel(e.target.value)}
                  className="bg-crypto-dark border border-crypto-border rounded px-2 py-1 text-xs text-white"
                >
                  <option value="">All Levels</option>
                  <option value="INFO">INFO</option>
                  <option value="DEBUG">DEBUG</option>
                  <option value="WARN">WARN</option>
                  <option value="ERROR">ERROR</option>
                </select>
              </div>
              <div className="bg-black rounded p-3 h-64 overflow-y-auto font-mono text-xs space-y-1">
                {logsData?.lines?.length ? (
                  logsData.lines.map((line: string, i: number) => (
                    <div key={i} className={
                      line.includes('ERROR') ? 'text-red-400' :
                      line.includes('WARN') ? 'text-yellow-400' :
                      line.includes('DEBUG') ? 'text-blue-400' :
                      'text-green-400'
                    }>{line}</div>
                  ))
                ) : (
                  <div className="text-gray-500 text-center py-8">No logs found or admin key missing</div>
                )}
              </div>
              <div className="mt-2 text-xs text-gray-500">{logsData?.source || 'No log source'}</div>
            </div>

            <div className="crypto-card">
              <h3 className="text-lg font-semibold text-white mb-4">Danger Zone</h3>
              <div className="space-y-2">
                <button
                  className="w-full py-2 bg-red-500/20 text-red-400 border border-red-500/50 rounded hover:bg-red-500/30 transition-colors"
                  onClick={() => serviceActionMutation.mutate({ serviceId: 'fastapi', action: 'restart' })}
                >
                  Restart Backend
                </button>
                <button
                  className="w-full py-2 bg-red-500/20 text-red-400 border border-red-500/50 rounded hover:bg-red-500/30 transition-colors"
                  onClick={() => serviceActionMutation.mutate({ serviceId: 'dragonfly', action: 'clear_cache' })}
                >
                  Clear All Caches
                </button>
                <button
                  className="w-full py-2 bg-red-500/20 text-red-400 border border-red-500/50 rounded hover:bg-red-500/30 transition-colors"
                  onClick={() => serviceActionMutation.mutate({ serviceId: 'fastapi', action: 'stop' })}
                >
                  Emergency Stop
                </button>
              </div>

              {systemData?.backend_process && (
                <div className="mt-6 pt-4 border-t border-crypto-border">
                  <h4 className="text-sm font-semibold text-white mb-2">Backend Process</h4>
                  <div className="space-y-1 text-sm">
                    <div className="flex justify-between"><span className="text-gray-500">PID</span><span className="text-white">{systemData.backend_process.pid}</span></div>
                    <div className="flex justify-between"><span className="text-gray-500">Memory</span><span className="text-white">{systemData.backend_process.memory_mb} MB</span></div>
                    <div className="flex justify-between"><span className="text-gray-500">CPU</span><span className="text-white">{systemData.backend_process.cpu_percent}%</span></div>
                    <div className="flex justify-between"><span className="text-gray-500">Threads</span><span className="text-white">{systemData.backend_process.threads}</span></div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* USERS TAB */}
      {activeTab === 'users' && <UserManagement />}

      {/* EVIDENCE TAB */}
      {activeTab === 'evidence' && <EvidenceManagement />}

      {/* INVESTIGATIONS TAB */}
      {activeTab === 'investigations' && <InvestigationOperations />}

      {/* TRENCHES & REHAB TAB */}
      {activeTab === 'trenches' && <TrenchesRehabManagement />}

      {/* REVENUE TAB */}
      {activeTab === 'revenue' && <RevenueDashboard />}

      {/* FEATURE FLAGS TAB */}
      {activeTab === 'feature_flags' && <FeatureFlags />}

      {/* AUDIT LOGS TAB */}
      {activeTab === 'audit_logs' && <AuditLogs />}

      {/* API MANAGEMENT TAB */}
      {activeTab === 'api_mgmt' && <APIManagement />}

      {/* CONTENT MANAGEMENT TAB */}
      {activeTab === 'content' && <ContentManagement adminKey={adminKey} />}

      {/* INFRASTRUCTURE TAB */}
      {activeTab === 'infrastructure' && <InfrastructureDashboard adminKey={adminKey} />}
    </div>
  );
}

// Component Helpers
function AIOSINTTab() {
  const { data: aiProviders } = useQuery({
    queryKey: ['ai-providers'],
    queryFn: () => api.getAIProviders(),
    refetchInterval: 30000,
  });
  const { data: budget } = useQuery({
    queryKey: ['provider-budget'],
    queryFn: () => api.getProviderBudget(),
  });
  const { data: cryptoKeys } = useQuery({
    queryKey: ['crypto-keys'],
    queryFn: () => api.cryptoKeysStatus(),
    refetchInterval: 60000,
  });

  const providers = aiProviders?.providers || [];
  const freeProviders = providers.filter((p: any) => p.free);
  const paidProviders = providers.filter((p: any) => !p.free);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <Brain className="w-6 h-6 text-neon-purple" />
          AI & OSINT Providers
        </h2>
        <span className="text-xs text-gray-400">
          {providers.filter((p: any) => p.available).length}/{providers.length} available
        </span>
      </div>

      {/* Free Providers */}
      {freeProviders.length > 0 && (
        <div>
          <h3 className="text-sm font-medium text-neon-green mb-3 flex items-center gap-2">
            <Zap className="w-4 h-4" />
            Free Chain (Prioritized)
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {freeProviders.map((p: any) => (
              <ProviderCard key={p.name} name={p.name} status={p.available ? 'active' : 'offline'} model={p.model || '-'} cost="FREE" />
            ))}
          </div>
        </div>
      )}

      {/* Paid Providers */}
      {paidProviders.length > 0 && (
        <div>
          <h3 className="text-sm font-medium text-yellow-400 mb-3">Paid Providers</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {paidProviders.map((p: any) => (
              <ProviderCard key={p.name} name={p.name} status={p.available ? 'active' : 'offline'} model={p.model || '-'} cost={p.cost || '$'} />
            ))}
          </div>
        </div>
      )}

      {/* Crypto API Keys */}
      {cryptoKeys && (
        <div className="crypto-card">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <Key className="w-5 h-5 text-neon-blue" />
            Crypto API Keys ({cryptoKeys.active?.length || 0}/{Object.keys(cryptoKeys.providers || {}).length} active)
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {Object.entries(cryptoKeys.providers || {}).map(([name, key]: [string, any]) => (
              <div key={name} className={`p-3 rounded border ${key && key !== 'PLACEHOLDER_UPDATE_ME' ? 'bg-green-500/10 border-green-500/30' : 'bg-red-500/10 border-red-500/30'}`}>
                <div className="flex items-center gap-2">
                  <div className={`w-2 h-2 rounded-full ${key && key !== 'PLACEHOLDER_UPDATE_ME' ? 'bg-green-400' : 'bg-red-400'}`} />
                  <span className="text-sm text-white capitalize">{name}</span>
                </div>
                <span className="text-xs text-gray-500">{key && key !== 'PLACEHOLDER_UPDATE_ME' ? 'Active' : 'Missing'}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Budget */}
      {budget && (
        <div className="crypto-card">
          <h3 className="text-lg font-semibold text-white mb-4">Budget & Usage</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatBox label="Free Calls Today" value={budget.free_calls_today || '-'} />
            <StatBox label="Paid Cost Today" value={budget.paid_cost_today || '-'} />
            <StatBox label="Cache Hits" value={budget.cache_hits || '-'} />
            <StatBox label="Total Providers" value={providers.length} />
          </div>
        </div>
      )}

      {/* OSINT Integrations */}
      <div className="crypto-card">
        <h3 className="text-lg font-semibold text-white mb-4">OSINT Integrations</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <ToggleItem label="TinEye (Images)" enabled={true} />
          <ToggleItem label="Social-Analyzer" enabled={true} />
          <ToggleItem label="Holehe (Emails)" enabled={true} />
          <ToggleItem label="Sherlock (Usernames)" enabled={true} />
          <ToggleItem label="Ethos (Wallets)" enabled={true} />
          <ToggleItem label="Moralis (On-chain)" enabled={true} />
          <ToggleItem label="DeFiLlama (TVL)" enabled={true} />
          <ToggleItem label="Dune Analytics" enabled={false} />
        </div>
      </div>
    </div>
  );
}

function QuickStat({ title, value, icon: Icon, color }: any) {
  const colors: any = {
    blue: 'text-blue-400 bg-blue-500/20',
    purple: 'text-purple-400 bg-purple-500/20',
    green: 'text-green-400 bg-green-500/20',
    yellow: 'text-yellow-400 bg-yellow-500/20',
    cyan: 'text-cyan-400 bg-cyan-500/20',
    red: 'text-red-400 bg-red-500/20',
    orange: 'text-orange-400 bg-orange-500/20',
    pink: 'text-pink-400 bg-pink-500/20',
  };

  return (
    <div className="crypto-card p-3">
      <div className="flex items-center justify-between mb-1">
        <span className="text-gray-400 text-xs">{title}</span>
        <div className={`p-1 rounded ${colors[color]}`}>
          <Icon className="w-3 h-3" />
        </div>
      </div>
      <p className="text-lg font-bold text-white">{value}</p>
    </div>
  );
}

function ServiceRow({ name, status, port }: { name: string; status: boolean; port: string }) {
  return (
    <div className="flex items-center justify-between p-2 bg-crypto-dark rounded">
      <div className="flex items-center gap-2">
        <div className={`w-2 h-2 rounded-full ${status ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
        <span className="text-sm text-white">{name}</span>
        <span className="text-xs text-gray-500">:{port}</span>
      </div>
      <span className={`text-xs px-2 py-0.5 rounded ${status ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
        {status ? 'ONLINE' : 'OFFLINE'}
      </span>
    </div>
  );
}

function ActionButton({ label, icon: Icon, onClick }: { label: string; icon: any; onClick: () => void }) {
  return (
    <button onClick={onClick} className="flex items-center gap-2 p-2 bg-crypto-dark rounded hover:bg-crypto-border transition-colors text-sm text-gray-300">
      <Icon className="w-4 h-4" />
      {label}
    </button>
  );
}

function Expandable({ title, icon: Icon, defaultOpen, children }: any) {
  const [isOpen, setIsOpen] = useState(defaultOpen);
  return (
    <div className="crypto-card overflow-hidden">
      <button onClick={() => setIsOpen(!isOpen)} className="w-full flex items-center justify-between p-4 hover:bg-crypto-dark/50">
        <div className="flex items-center gap-2">
          <Icon className="w-5 h-5 text-neon-purple" />
          <span className="font-semibold text-white">{title}</span>
        </div>
        {isOpen ? <ChevronDown className="w-5 h-5 text-gray-400" /> : <ChevronRight className="w-5 h-5 text-gray-400" />}
      </button>
      {isOpen && <div className="p-4 border-t border-crypto-border">{children}</div>}
    </div>
  );
}

function SchemaCard({ name, rows, cols }: { name: string; rows?: number; cols: string[] }) {
  return (
    <div className="bg-crypto-dark rounded p-3">
      <div className="flex items-center justify-between mb-2">
        <span className="font-mono text-sm text-neon-green">{name}</span>
        {rows !== undefined && <span className="text-xs text-gray-500">{rows} rows</span>}
      </div>
      <div className="flex flex-wrap gap-1">
        {cols.map((col) => (
          <span key={col} className="text-[10px] px-1.5 py-0.5 bg-crypto-card rounded text-gray-400">{col}</span>
        ))}
      </div>
    </div>
  );
}

function Endpoint({ method, path, desc }: { method: string; path: string; desc: string }) {
  const colors: any = { GET: 'text-green-400', POST: 'text-blue-400', PUT: 'text-yellow-400', DELETE: 'text-red-400' };
  return (
    <div className="flex items-center gap-3 p-2 hover:bg-crypto-dark rounded">
      <span className={`font-bold w-12 ${colors[method]}`}>{method}</span>
      <code className="text-gray-300 flex-1">{path}</code>
      <span className="text-gray-500 text-xs">{desc}</span>
    </div>
  );
}

function ConfigItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center gap-2 p-2 bg-crypto-dark rounded">
      <span className="text-neon-yellow font-mono text-xs w-[140px]">{label}</span>
      <span className="text-gray-300 font-mono text-xs">{value}</span>
    </div>
  );
}

function DataPreview({ title, data }: { title: string; data: any }) {
  return (
    <div className="bg-crypto-dark rounded p-3">
      <h4 className="text-sm font-semibold text-neon-blue mb-2">{title}</h4>
      <pre className="text-xs text-gray-400 overflow-auto max-h-[200px]">{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
}

function ToggleItem({ label, enabled }: { label: string; enabled: boolean }) {
  return (
    <div className="flex items-center justify-between p-2 bg-crypto-dark rounded">
      <span className="text-sm text-gray-300">{label}</span>
      <div className={`w-10 h-5 rounded-full relative ${enabled ? 'bg-green-500/50' : 'bg-gray-600'}`}>
        <div className={`absolute top-0.5 w-4 h-4 rounded-full bg-white transition-all ${enabled ? 'left-5' : 'left-0.5'}`} />
      </div>
    </div>
  );
}

function StatBox({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-crypto-dark rounded p-3 text-center">
      <p className="text-2xl font-bold text-white">{value}</p>
      <p className="text-xs text-gray-500">{label}</p>
    </div>
  );
}

function ProviderCard({ name, status, model, cost }: { name: string; status: string; model: string; cost: string }) {
  return (
    <div className="crypto-card">
      <div className="flex items-center justify-between mb-2">
        <span className="font-semibold text-white">{name}</span>
        <span className={`w-2 h-2 rounded-full ${status === 'active' ? 'bg-green-500 animate-pulse' : 'bg-yellow-500'}`} />
      </div>
      <p className="text-sm text-gray-400">{model}</p>
      <p className="text-xs text-gray-500 mt-1">Cost: {cost}</p>
      <div className="flex gap-2 mt-3">
        <button className="flex-1 btn-secondary text-xs py-1">Test</button>
        <button className="flex-1 btn-secondary text-xs py-1">{status === 'active' ? 'Disable' : 'Enable'}</button>
      </div>
    </div>
  );
}

function StatRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between items-center p-2 bg-crypto-dark rounded">
      <span className="text-gray-400 text-sm">{label}</span>
      <span className="text-white font-semibold">{value}</span>
    </div>
  );
}

function ChannelRow({ name, type, bot, status }: { name: string; type: string; bot: string; status: string }) {
  return (
    <div className="flex items-center justify-between p-3 bg-crypto-dark rounded">
      <div>
        <p className="text-white font-medium">{name}</p>
        <p className="text-xs text-gray-500">{bot} • {type}</p>
      </div>
      <span className={`px-2 py-1 rounded text-xs ${status === 'active' ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'}`}>
        {status.toUpperCase()}
      </span>
    </div>
  );
}

function AlertRow({ type, message, time, channel }: { type: string; message: string; time: string; channel: string }) {
  const colors: any = { scam: 'text-red-400', whale: 'text-blue-400', system: 'text-green-400' };
  return (
    <div className="flex items-start gap-3 p-2 bg-crypto-dark rounded">
      <AlertCircle className={`w-4 h-4 mt-0.5 ${colors[type] || 'text-gray-400'}`} />
      <div className="flex-1">
        <p className="text-sm text-gray-300">{message}</p>
        <p className="text-xs text-gray-500">{time} • {channel}</p>
      </div>
    </div>
  );
}

function SystemCard({ title, value, icon: Icon }: any) {
  return (
    <div className="crypto-card text-center">
      <Icon className="w-6 h-6 text-neon-green mx-auto mb-2" />
      <p className="text-2xl font-bold text-white">{value}</p>
      <p className="text-xs text-gray-500">{title}</p>
    </div>
  );
}

function ServiceControl({ name, port }: { name: string; port: string; status?: string }) {
  return (
    <div className="flex items-center justify-between p-3 bg-crypto-dark rounded">
      <div>
        <p className="text-white font-medium">{name}</p>
        <p className="text-xs text-gray-500">Port {port}</p>
      </div>
      <div className="flex gap-2">
        <button className="p-2 hover:bg-crypto-card rounded text-green-400">
          <Play className="w-4 h-4" />
        </button>
        <button className="p-2 hover:bg-crypto-card rounded text-yellow-400">
          <Pause className="w-4 h-4" />
        </button>
        <button className="p-2 hover:bg-crypto-card rounded text-red-400">
          <RotateCcw className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}

function TableRow({ name, rows, size, lastWrite }: { name: string; rows?: number; size: string; lastWrite: string }) {
  return (
    <tr className="border-b border-crypto-border">
      <td className="p-3 font-mono text-neon-green">{name}</td>
      <td className="p-3">{rows ?? 0}</td>
      <td className="p-3 text-gray-400">{size}</td>
      <td className="p-3 text-gray-400">{lastWrite}</td>
      <td className="p-3">
        <button className="text-neon-blue hover:underline text-xs">View</button>
      </td>
    </tr>
  );
}
