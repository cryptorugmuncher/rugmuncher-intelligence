import React, { useState, useEffect } from 'react';
import {
  Server,
  Activity,
  Cpu,
  Database,
  Wifi,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Clock,
  RefreshCw,
  Globe,
  Bot,
  Shield,
  Zap,
  HardDrive,
  MemoryStick,
  Network,
  Lock,
  Bell,
  FileText,
  ChevronDown,
  ChevronUp,
  Terminal
} from 'lucide-react';

interface ServiceStatus {
  id: string;
  name: string;
  type: 'api' | 'bot' | 'database' | 'frontend' | 'ai' | 'security';
  status: 'operational' | 'degraded' | 'down' | 'maintenance';
  uptime: string;
  latency: string;
  lastIncident: string;
  region: string;
  version: string;
  metrics: {
    requests24h?: number;
    errorRate?: number;
    cpuUsage?: number;
    memoryUsage?: number;
  };
}

interface Incident {
  id: string;
  title: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  status: 'investigating' | 'identified' | 'monitoring' | 'resolved';
  startedAt: string;
  resolvedAt?: string;
  affectedServices: string[];
  description: string;
  updates: { timestamp: string; message: string }[];
}

const SystemStatus: React.FC = () => {
  const [services, setServices] = useState<ServiceStatus[]>([
    {
      id: 's1',
      name: 'Main API Server',
      type: 'api',
      status: 'operational',
      uptime: '99.97%',
      latency: '145ms',
      lastIncident: '7 days ago',
      region: 'US-East',
      version: 'v2.4.1',
      metrics: { requests24h: 2845000, errorRate: 0.02, cpuUsage: 42, memoryUsage: 68 }
    },
    {
      id: 's2',
      name: 'Telegram Bot Cluster',
      type: 'bot',
      status: 'degraded',
      uptime: '98.5%',
      latency: '230ms',
      lastIncident: '2 hours ago',
      region: 'EU-West',
      version: 'v2.3.8',
      metrics: { requests24h: 892000, errorRate: 1.5, cpuUsage: 78, memoryUsage: 82 }
    },
    {
      id: 's3',
      name: 'PostgreSQL Primary',
      type: 'database',
      status: 'operational',
      uptime: '99.99%',
      latency: '12ms',
      lastIncident: '14 days ago',
      region: 'US-East',
      version: '15.4',
      metrics: { cpuUsage: 35, memoryUsage: 72 }
    },
    {
      id: 's4',
      name: 'AI Swarm Orchestrator',
      type: 'ai',
      status: 'operational',
      uptime: '99.95%',
      latency: '890ms',
      lastIncident: '3 days ago',
      region: 'US-West',
      version: 'v3.1.0',
      metrics: { requests24h: 456000, errorRate: 0.1, cpuUsage: 89, memoryUsage: 76 }
    },
    {
      id: 's5',
      name: 'Frontend CDN',
      type: 'frontend',
      status: 'operational',
      uptime: '100%',
      latency: '45ms',
      lastIncident: 'None',
      region: 'Global',
      version: 'v2.5.0',
      metrics: { requests24h: 12500000, errorRate: 0.001 }
    },
    {
      id: 's6',
      name: 'Contract Scanner',
      type: 'security',
      status: 'operational',
      uptime: '99.92%',
      latency: '320ms',
      lastIncident: '5 days ago',
      region: 'US-East',
      version: 'v2.2.5',
      metrics: { requests24h: 567000, errorRate: 0.05, cpuUsage: 65, memoryUsage: 58 }
    },
    {
      id: 's7',
      name: 'Redis Cache Layer',
      type: 'database',
      status: 'maintenance',
      uptime: '99.8%',
      latency: '2ms',
      lastIncident: 'Ongoing',
      region: 'US-East',
      version: '7.2',
      metrics: { cpuUsage: 25, memoryUsage: 91 }
    },
    {
      id: 's8',
      name: 'Wallet Integration',
      type: 'api',
      status: 'down',
      uptime: '97.2%',
      latency: '-',
      lastIncident: 'Ongoing',
      region: 'EU-West',
      version: 'v1.9.2',
      metrics: { errorRate: 100 }
    }
  ]);

  const [incidents] = useState<Incident[]>([
    {
      id: 'i1',
      title: 'Redis Cache Maintenance',
      severity: 'medium',
      status: 'monitoring',
      startedAt: '2026-04-14T08:00:00Z',
      affectedServices: ['Redis Cache Layer'],
      description: 'Scheduled maintenance to upgrade Redis cluster and optimize memory usage.',
      updates: [
        { timestamp: '08:00 UTC', message: 'Maintenance started' },
        { timestamp: '09:30 UTC', message: 'Cache migration in progress' },
        { timestamp: '10:15 UTC', message: 'Verification ongoing - service will resume shortly' }
      ]
    },
    {
      id: 'i2',
      title: 'Wallet API Outage',
      severity: 'high',
      status: 'investigating',
      startedAt: '2026-04-14T11:45:00Z',
      affectedServices: ['Wallet Integration'],
      description: 'Third-party RPC provider experiencing issues. Investigating fallback solutions.',
      updates: [
        { timestamp: '11:45 UTC', message: 'Outage detected - wallet transactions failing' },
        { timestamp: '12:00 UTC', message: 'Identified RPC provider issue' },
        { timestamp: '12:30 UTC', message: 'Switching to backup provider' }
      ]
    }
  ]);

  const [expandedIncident, setExpandedIncident] = useState<string | null>('i1');
  const [refreshing, setRefreshing] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(new Date());

  const handleRefresh = () => {
    setRefreshing(true);
    setTimeout(() => {
      setRefreshing(false);
      setLastUpdated(new Date());
    }, 2000);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'operational': return <CheckCircle className="w-5 h-5 text-green-400" />;
      case 'degraded': return <AlertTriangle className="w-5 h-5 text-yellow-400" />;
      case 'down': return <XCircle className="w-5 h-5 text-red-400" />;
      case 'maintenance': return <Clock className="w-5 h-5 text-blue-400" />;
      default: return <Activity className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'operational': return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'degraded': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'down': return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'maintenance': return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      default: return 'bg-gray-500/20 text-gray-400';
    }
  };

  const operationalCount = services.filter(s => s.status === 'operational').length;
  const degradedCount = services.filter(s => s.status === 'degraded').length;
  const downCount = services.filter(s => s.status === 'down').length;

  return (
    <div className="min-h-screen bg-[#0a0812] text-gray-100 font-mono selection:bg-[#7c3aed]/30">
      {/* Header */}
      <div className="bg-gradient-to-r from-[#0f0c1d] via-[#1a1525] to-[#0f0c1d] border-b border-[#7c3aed]/30">
        <div className="max-w-[1600px] mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Activity className="w-8 h-8 text-[#7c3aed]" />
              <div>
                <h1 className="text-xl font-bold tracking-wider">
                  SYSTEM <span className="text-[#7c3aed]">STATUS</span>
                </h1>
                <p className="text-xs text-gray-500 tracking-[0.2em]">INFRASTRUCTURE MONITORING</p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <div className="text-right">
                <div className="text-xs text-gray-500">Last Updated</div>
                <div className="text-sm">{lastUpdated.toLocaleTimeString()}</div>
              </div>
              <button
                onClick={handleRefresh}
                disabled={refreshing}
                className="p-2 bg-gray-800 border border-gray-700 rounded-lg hover:bg-gray-700 transition-all"
              >
                <RefreshCw className={`w-5 h-5 ${refreshing ? 'animate-spin' : ''}`} />
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-[1600px] mx-auto p-6 space-y-6">
        {/* Overall Status */}
        <div className="grid grid-cols-4 gap-4">
          <div className="bg-gradient-to-br from-green-500/10 to-[#0f0c1d] border border-green-500/30 rounded-lg p-5">
            <div className="flex items-center gap-3 mb-2">
              <CheckCircle className="w-6 h-6 text-green-400" />
              <span className="text-2xl font-bold text-green-400">{operationalCount}</span>
            </div>
            <div className="text-xs text-gray-500 uppercase">Operational</div>
          </div>
          <div className="bg-gradient-to-br from-yellow-500/10 to-[#0f0c1d] border border-yellow-500/30 rounded-lg p-5">
            <div className="flex items-center gap-3 mb-2">
              <AlertTriangle className="w-6 h-6 text-yellow-400" />
              <span className="text-2xl font-bold text-yellow-400">{degradedCount}</span>
            </div>
            <div className="text-xs text-gray-500 uppercase">Degraded</div>
          </div>
          <div className="bg-gradient-to-br from-red-500/10 to-[#0f0c1d] border border-red-500/30 rounded-lg p-5">
            <div className="flex items-center gap-3 mb-2">
              <XCircle className="w-6 h-6 text-red-400" />
              <span className="text-2xl font-bold text-red-400">{downCount}</span>
            </div>
            <div className="text-xs text-gray-500 uppercase">Down</div>
          </div>
          <div className="bg-gradient-to-br from-[#7c3aed]/10 to-[#0f0c1d] border border-[#7c3aed]/30 rounded-lg p-5">
            <div className="flex items-center gap-3 mb-2">
              <Globe className="w-6 h-6 text-[#7c3aed]" />
              <span className="text-2xl font-bold text-[#7c3aed]">8</span>
            </div>
            <div className="text-xs text-gray-500 uppercase">Total Services</div>
          </div>
        </div>

        {/* Active Incidents */}
        <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
          <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
            <Bell className="w-5 h-5 text-red-400" />
            Active Incidents ({incidents.length})
          </h2>

          <div className="space-y-4">
            {incidents.map((incident) => (
              <div
                key={incident.id}
                className="bg-[#0a0812] rounded-lg border border-gray-800 overflow-hidden"
              >
                <div
                  className="p-4 cursor-pointer"
                  onClick={() => setExpandedIncident(expandedIncident === incident.id ? null : incident.id)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className={`px-2 py-1 rounded text-xs font-bold ${
                        incident.severity === 'critical' ? 'bg-red-500/20 text-red-400' :
                        incident.severity === 'high' ? 'bg-orange-500/20 text-orange-400' :
                        incident.severity === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
                        'bg-blue-500/20 text-blue-400'
                      }`}>
                        {incident.severity.toUpperCase()}
                      </span>
                      <span className="font-semibold">{incident.title}</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className={`px-2 py-1 rounded text-xs ${
                        incident.status === 'resolved' ? 'bg-green-500/20 text-green-400' :
                        incident.status === 'monitoring' ? 'bg-blue-500/20 text-blue-400' :
                        incident.status === 'identified' ? 'bg-yellow-500/20 text-yellow-400' :
                        'bg-red-500/20 text-red-400'
                      }`}>
                        {incident.status.toUpperCase()}
                      </span>
                      {expandedIncident === incident.id ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
                    </div>
                  </div>
                  <p className="text-sm text-gray-400 mt-2">{incident.description}</p>
                  <div className="flex items-center gap-2 mt-2 text-xs text-gray-500">
                    <span>Affected: {incident.affectedServices.join(', ')}</span>
                    <span>•</span>
                    <span>Started: {new Date(incident.startedAt).toLocaleString()}</span>
                  </div>
                </div>

                {expandedIncident === incident.id && (
                  <div className="px-4 pb-4 border-t border-gray-800 pt-3">
                    <h4 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Incident Timeline</h4>
                    <div className="space-y-2">
                      {incident.updates.map((update, idx) => (
                        <div key={idx} className="flex items-start gap-3 text-sm">
                          <div className="w-2 h-2 rounded-full bg-[#7c3aed] mt-1.5" />
                          <div>
                            <span className="text-gray-500">{update.timestamp}:</span>
                            <span className="text-gray-300 ml-2">{update.message}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Service Status Grid */}
        <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
          <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
            <Server className="w-5 h-5 text-[#7c3aed]" />
            Service Status
          </h2>

          <div className="grid grid-cols-2 gap-4">
            {services.map((service) => (
              <div key={service.id} className="bg-[#0a0812] rounded-lg border border-gray-800 p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    {service.type === 'api' && <Zap className="w-5 h-5 text-[#7c3aed]" />}
                    {service.type === 'bot' && <Bot className="w-5 h-5 text-blue-400" />}
                    {service.type === 'database' && <Database className="w-5 h-5 text-green-400" />}
                    {service.type === 'frontend' && <Globe className="w-5 h-5 text-purple-400" />}
                    {service.type === 'ai' && <Cpu className="w-5 h-5 text-yellow-400" />}
                    {service.type === 'security' && <Shield className="w-5 h-5 text-red-400" />}
                    <span className="font-semibold">{service.name}</span>
                  </div>
                  <span className={`px-2 py-1 rounded text-xs border ${getStatusColor(service.status)}`}>
                    {service.status.toUpperCase()}
                  </span>
                </div>

                <div className="grid grid-cols-4 gap-2 text-xs mb-3">
                  <div className="bg-gray-800/50 rounded p-2">
                    <div className="text-gray-500">Uptime</div>
                    <div className="font-semibold">{service.uptime}</div>
                  </div>
                  <div className="bg-gray-800/50 rounded p-2">
                    <div className="text-gray-500">Latency</div>
                    <div className={`font-semibold ${parseInt(service.latency) > 500 ? 'text-yellow-400' : ''}`}>
                      {service.latency}
                    </div>
                  </div>
                  <div className="bg-gray-800/50 rounded p-2">
                    <div className="text-gray-500">Region</div>
                    <div className="font-semibold">{service.region}</div>
                  </div>
                  <div className="bg-gray-800/50 rounded p-2">
                    <div className="text-gray-500">Version</div>
                    <div className="font-semibold">{service.version}</div>
                  </div>
                </div>

                {service.metrics && (
                  <div className="space-y-2">
                    {service.metrics.requests24h && (
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-gray-500">24h Requests</span>
                        <span className="font-semibold">{service.metrics.requests24h.toLocaleString()}</span>
                      </div>
                    )}
                    {service.metrics.errorRate !== undefined && (
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-gray-500">Error Rate</span>
                        <span className={`font-semibold ${service.metrics.errorRate > 1 ? 'text-yellow-400' : 'text-green-400'}`}>
                          {service.metrics.errorRate}%
                        </span>
                      </div>
                    )}
                    {service.metrics.cpuUsage !== undefined && (
                      <div>
                        <div className="flex items-center justify-between text-xs mb-1">
                          <span className="text-gray-500">CPU</span>
                          <span className={`font-semibold ${service.metrics.cpuUsage > 80 ? 'text-yellow-400' : ''}`}>
                            {service.metrics.cpuUsage}%
                          </span>
                        </div>
                        <div className="h-1.5 bg-gray-800 rounded-full overflow-hidden">
                          <div
                            className={`h-full rounded-full ${service.metrics.cpuUsage > 80 ? 'bg-yellow-500' : 'bg-green-500'}`}
                            style={{ width: `${service.metrics.cpuUsage}%` }}
                          />
                        </div>
                      </div>
                    )}
                    {service.metrics.memoryUsage !== undefined && (
                      <div>
                        <div className="flex items-center justify-between text-xs mb-1">
                          <span className="text-gray-500">Memory</span>
                          <span className={`font-semibold ${service.metrics.memoryUsage > 85 ? 'text-red-400' : ''}`}>
                            {service.metrics.memoryUsage}%
                          </span>
                        </div>
                        <div className="h-1.5 bg-gray-800 rounded-full overflow-hidden">
                          <div
                            className={`h-full rounded-full ${service.metrics.memoryUsage > 85 ? 'bg-red-500' : 'bg-blue-500'}`}
                            style={{ width: `${service.metrics.memoryUsage}%` }}
                          />
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* System Metrics */}
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-5">
            <h3 className="text-sm font-bold text-gray-500 uppercase tracking-wider mb-4 flex items-center gap-2">
              <Network className="w-4 h-4" />
              Network I/O
            </h3>
            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-gray-500">Inbound</span>
                  <span className="text-green-400">2.4 GB/s</span>
                </div>
                <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                  <div className="h-full w-[65%] bg-green-500 rounded-full" />
                </div>
              </div>
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-gray-500">Outbound</span>
                  <span className="text-blue-400">1.8 GB/s</span>
                </div>
                <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                  <div className="h-full w-[45%] bg-blue-500 rounded-full" />
                </div>
              </div>
            </div>
          </div>

          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-5">
            <h3 className="text-sm font-bold text-gray-500 uppercase tracking-wider mb-4 flex items-center gap-2">
              <HardDrive className="w-4 h-4" />
              Storage
            </h3>
            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-gray-500">Database (SSD)</span>
                  <span className="text-yellow-400">78% (780GB/1TB)</span>
                </div>
                <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                  <div className="h-full w-[78%] bg-yellow-500 rounded-full" />
                </div>
              </div>
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-gray-500">Logs & Cache</span>
                  <span className="text-green-400">45% (450GB/1TB)</span>
                </div>
                <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                  <div className="h-full w-[45%] bg-green-500 rounded-full" />
                </div>
              </div>
            </div>
          </div>

          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-5">
            <h3 className="text-sm font-bold text-gray-500 uppercase tracking-wider mb-4 flex items-center gap-2">
              <Lock className="w-4 h-4" />
              Security Status
            </h3>
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-400">Firewall</span>
                <span className="text-green-400 flex items-center gap-1">
                  <CheckCircle className="w-4 h-4" />
                  Active
                </span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-400">DDoS Protection</span>
                <span className="text-green-400 flex items-center gap-1">
                  <CheckCircle className="w-4 h-4" />
                  Active
                </span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-400">WAF Rules</span>
                <span className="text-green-400">245 configured</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-400">Failed Logins (1h)</span>
                <span className="text-yellow-400">23 blocked</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SystemStatus;
