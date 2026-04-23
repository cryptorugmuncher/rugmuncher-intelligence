/**
 * Audit Logs Panel
 * Security audit trail, access logs, admin actions
 */
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Eye,
  AlertTriangle,
  Lock,
  Server,
  Database,
  Download,
  Search,
  Clock,
  MapPin,
  XCircle,
  CheckCircle,
  RefreshCw,
  Globe,
  Activity,
  Terminal,
  Shield,
} from 'lucide-react';

const LOG_TYPES = [
  { id: 'auth', label: 'Authentication', color: 'blue', icon: Lock },
  { id: 'admin', label: 'Admin Actions', color: 'red', icon: Shield },
  { id: 'data', label: 'Data Access', color: 'green', icon: Database },
  { id: 'api', label: 'API Requests', color: 'purple', icon: Terminal },
  { id: 'system', label: 'System Events', color: 'orange', icon: Server },
  { id: 'security', label: 'Security Alerts', color: 'red', icon: AlertTriangle },
];

const SEVERITY_LEVELS = [
  { id: 'info', label: 'Info', color: 'blue' },
  { id: 'warning', label: 'Warning', color: 'yellow' },
  { id: 'error', label: 'Error', color: 'red' },
  { id: 'critical', label: 'Critical', color: 'red' },
];

interface AuditLog {
  id: string;
  timestamp: string;
  type: string;
  severity: string;
  userId: string;
  userEmail: string;
  ip: string;
  action: string;
  resource: string;
  details: string;
  success: boolean;
  userAgent?: string;
  location?: string;
}

const MOCK_LOGS: AuditLog[] = [
  {
    id: 'log_1',
    timestamp: '2024-01-15T10:30:00Z',
    type: 'auth',
    severity: 'info',
    userId: 'user_123',
    userEmail: 'admin@rmi.io',
    ip: '192.168.1.100',
    action: 'LOGIN',
    resource: 'Admin Panel',
    details: 'Successful login from Chrome on macOS',
    success: true,
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
    location: 'New York, US',
  },
  {
    id: 'log_2',
    timestamp: '2024-01-15T10:32:00Z',
    type: 'admin',
    severity: 'info',
    userId: 'user_123',
    userEmail: 'admin@rmi.io',
    ip: '192.168.1.100',
    action: 'USER_BAN',
    resource: 'User: user_456',
    details: 'Banned user for spam reports',
    success: true,
  },
  {
    id: 'log_3',
    timestamp: '2024-01-15T10:45:00Z',
    type: 'security',
    severity: 'warning',
    userId: 'user_789',
    userEmail: 'unknown@example.com',
    ip: '10.0.0.50',
    action: 'FAILED_LOGIN',
    resource: 'Login Endpoint',
    details: '3 failed login attempts',
    success: false,
    location: 'Unknown',
  },
  {
    id: 'log_4',
    timestamp: '2024-01-15T11:00:00Z',
    type: 'data',
    severity: 'info',
    userId: 'user_123',
    userEmail: 'admin@rmi.io',
    ip: '192.168.1.100',
    action: 'DATA_EXPORT',
    resource: 'Investigations Table',
    details: 'Exported 50 investigation records',
    success: true,
  },
  {
    id: 'log_5',
    timestamp: '2024-01-15T11:15:00Z',
    type: 'api',
    severity: 'error',
    userId: 'api_key_abc',
    userEmail: 'api-client',
    ip: '172.16.0.10',
    action: 'RATE_LIMIT_EXCEEDED',
    resource: '/api/v1/wallets/scan',
    details: 'Rate limit exceeded: 1000 requests/min',
    success: false,
  },
  {
    id: 'log_6',
    timestamp: '2024-01-15T11:30:00Z',
    type: 'system',
    severity: 'warning',
    userId: 'system',
    userEmail: 'system@rmi.io',
    ip: '127.0.0.1',
    action: 'SERVICE_RESTART',
    resource: 'Dragonfly Cache',
    details: 'Cache service restarted due to memory pressure',
    success: true,
  },
  {
    id: 'log_7',
    timestamp: '2024-01-15T12:00:00Z',
    type: 'security',
    severity: 'critical',
    userId: 'unknown',
    userEmail: 'unknown',
    ip: '45.33.22.11',
    action: 'SUSPICIOUS_ACTIVITY',
    resource: 'API Gateway',
    details: 'Multiple failed authentication attempts from suspicious IP',
    success: false,
    location: 'Moscow, RU',
  },
];

export default function AuditLogs() {
  const [searchQuery, setSearchQuery] = useState('');
  const [typeFilter, setTypeFilter] = useState('all');
  const [severityFilter, setSeverityFilter] = useState('all');
  const [dateRange, setDateRange] = useState('24h');
  const [selectedLog, setSelectedLog] = useState<AuditLog | null>(null);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [expandedLog, setExpandedLog] = useState<string | null>(null);

  const { data: logs, isLoading, refetch } = useQuery({
    queryKey: ['audit-logs'],
    queryFn: async () => {
      return MOCK_LOGS;
    },
  });

  const filteredLogs = logs?.filter((log: AuditLog) => {
    const matchesSearch = 
      log.userEmail.toLowerCase().includes(searchQuery.toLowerCase()) ||
      log.action.toLowerCase().includes(searchQuery.toLowerCase()) ||
      log.resource.toLowerCase().includes(searchQuery.toLowerCase()) ||
      log.ip.includes(searchQuery);
    const matchesType = typeFilter === 'all' || log.type === typeFilter;
    const matchesSeverity = severityFilter === 'all' || log.severity === severityFilter;
    return matchesSearch && matchesType && matchesSeverity;
  });

  const stats = {
    total: logs?.length || 0,
    failedLogins: logs?.filter((l: AuditLog) => l.action === 'FAILED_LOGIN').length || 0,
    securityAlerts: logs?.filter((l: AuditLog) => l.type === 'security').length || 0,
    apiErrors: logs?.filter((l: AuditLog) => l.type === 'api' && l.severity === 'error').length || 0,
  };

  const getTypeIcon = (type: string) => {
    const logType = LOG_TYPES.find((t) => t.id === type);
    const Icon = logType?.icon || Activity;
    return <Icon className={`w-4 h-4 text-${logType?.color || 'gray'}-400`} />;
  };

  const getSeverityBadge = (severity: string) => {
    const colors: any = {
      info: 'bg-blue-500/20 text-blue-400',
      warning: 'bg-yellow-500/20 text-yellow-400',
      error: 'bg-red-500/20 text-red-400',
      critical: 'bg-red-600/30 text-red-500 border border-red-500/50',
    };
    return (
      <span className={`px-2 py-1 rounded text-xs ${colors[severity] || colors.info}`}>
        {severity.toUpperCase()}
      </span>
    );
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard title="Total Events" value={stats.total} icon={Activity} color="blue" />
        <StatCard title="Failed Logins" value={stats.failedLogins} icon={XCircle} color="orange" />
        <StatCard title="Security Alerts" value={stats.securityAlerts} icon={Shield} color="red" />
        <StatCard title="API Errors" value={stats.apiErrors} icon={AlertTriangle} color="red" />
      </div>

      <div className="crypto-card">
        <div className="flex flex-wrap gap-4 items-center">
          <div className="relative flex-1 min-w-[250px]">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search logs..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-crypto-dark border border-crypto-border rounded-lg pl-10 pr-4 py-2 text-white"
            />
          </div>
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="bg-crypto-dark border border-crypto-border rounded-lg px-3 py-2 text-white"
          >
            <option value="all">All Types</option>
            {LOG_TYPES.map((t) => (
              <option key={t.id} value={t.id}>{t.label}</option>
            ))}
          </select>
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="bg-crypto-dark border border-crypto-border rounded-lg px-3 py-2 text-white"
          >
            <option value="all">All Severities</option>
            {SEVERITY_LEVELS.map((s) => (
              <option key={s.id} value={s.id}>{s.label}</option>
            ))}
          </select>
          <select
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value)}
            className="bg-crypto-dark border border-crypto-border rounded-lg px-3 py-2 text-white"
          >
            <option value="1h">Last Hour</option>
            <option value="24h">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
          </select>
          <button onClick={() => refetch()} className="btn-secondary flex items-center gap-2">
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
          <button className="btn-secondary flex items-center gap-2">
            <Download className="w-4 h-4" />
            Export
          </button>
        </div>
      </div>

      <div className="crypto-card overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center text-gray-500">Loading audit logs...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-crypto-border text-gray-400">
                  <th className="text-left p-3">Time</th>
                  <th className="text-left p-3">Type</th>
                  <th className="text-left p-3">Severity</th>
                  <th className="text-left p-3">User</th>
                  <th className="text-left p-3">Action</th>
                  <th className="text-left p-3">Resource</th>
                  <th className="text-left p-3">IP</th>
                  <th className="text-center p-3">Status</th>
                  <th className="text-right p-3"></th>
                </tr>
              </thead>
              <tbody>
                {filteredLogs?.map((log: AuditLog) => (
                  <>
                    <tr 
                      key={log.id} 
                      className="border-b border-crypto-border hover:bg-crypto-dark/50 cursor-pointer"
                      onClick={() => setExpandedLog(expandedLog === log.id ? null : log.id)}
                    >
                      <td className="p-3 text-gray-400">
                        <div className="flex items-center gap-2">
                          <Clock className="w-3 h-3" />
                          {new Date(log.timestamp).toLocaleTimeString()}
                        </div>
                      </td>
                      <td className="p-3">
                        <div className="flex items-center gap-2">
                          {getTypeIcon(log.type)}
                          <span className="text-gray-300 capitalize">{log.type}</span>
                        </div>
                      </td>
                      <td className="p-3">{getSeverityBadge(log.severity)}</td>
                      <td className="p-3">
                        <div>
                          <p className="text-white text-sm">{log.userEmail}</p>
                          <p className="text-xs text-gray-500 font-mono">{log.userId.slice(0, 8)}...</p>
                        </div>
                      </td>
                      <td className="p-3">
                        <span className="text-neon-blue font-mono text-sm">{log.action}</span>
                      </td>
                      <td className="p-3 text-gray-300">{log.resource}</td>
                      <td className="p-3">
                        <div className="flex items-center gap-2 text-gray-400">
                          <Globe className="w-3 h-3" />
                          <span className="font-mono text-xs">{log.ip}</span>
                        </div>
                      </td>
                      <td className="p-3 text-center">
                        {log.success ? (
                          <CheckCircle className="w-5 h-5 text-green-400 mx-auto" />
                        ) : (
                          <XCircle className="w-5 h-5 text-red-400 mx-auto" />
                        )}
                      </td>
                      <td className="p-3">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedLog(log);
                            setShowDetailsModal(true);
                          }}
                          className="p-2 hover:bg-crypto-card rounded text-gray-400 hover:text-white"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                    {expandedLog === log.id && (
                      <tr className="bg-crypto-dark/30">
                        <td colSpan={9} className="p-4">
                          <div className="grid grid-cols-2 gap-4 text-sm">
                            <div>
                              <h4 className="text-gray-400 mb-1">Details</h4>
                              <p className="text-white">{log.details}</p>
                            </div>
                            {log.location && (
                              <div>
                                <h4 className="text-gray-400 mb-1">Location</h4>
                                <div className="flex items-center gap-2 text-white">
                                  <MapPin className="w-4 h-4 text-neon-green" />
                                  {log.location}
                                </div>
                              </div>
                            )}
                            {log.userAgent && (
                              <div className="col-span-2">
                                <h4 className="text-gray-400 mb-1">User Agent</h4>
                                <p className="text-gray-300 font-mono text-xs">{log.userAgent}</p>
                              </div>
                            )}
                          </div>
                        </td>
                      </tr>
                    )}
                  </>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {showDetailsModal && selectedLog && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="crypto-card w-full max-w-2xl max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-white">Audit Log Details</h3>
              <button onClick={() => setShowDetailsModal(false)} className="p-2 hover:bg-crypto-dark rounded">
                <XCircle className="w-5 h-5 text-gray-400" />
              </button>
            </div>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <DetailItem label="Log ID" value={selectedLog.id} />
                <DetailItem label="Timestamp" value={new Date(selectedLog.timestamp).toLocaleString()} />
                <DetailItem label="Type" value={selectedLog.type} />
                <DetailItem label="Severity" value={selectedLog.severity} />
                <DetailItem label="User ID" value={selectedLog.userId} />
                <DetailItem label="User Email" value={selectedLog.userEmail} />
                <DetailItem label="IP Address" value={selectedLog.ip} />
                <DetailItem label="Location" value={selectedLog.location || 'Unknown'} />
                <DetailItem label="Action" value={selectedLog.action} />
                <DetailItem label="Resource" value={selectedLog.resource} />
                <DetailItem label="Success" value={selectedLog.success ? 'Yes' : 'No'} />
              </div>
              <div className="bg-crypto-dark rounded p-3">
                <h4 className="text-sm text-gray-400 mb-1">Details</h4>
                <p className="text-white">{selectedLog.details}</p>
              </div>
              {selectedLog.userAgent && (
                <div className="bg-crypto-dark rounded p-3">
                  <h4 className="text-sm text-gray-400 mb-1">User Agent</h4>
                  <p className="text-gray-300 font-mono text-xs">{selectedLog.userAgent}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function StatCard({ title, value, icon: Icon, color }: any) {
  const colors: any = {
    blue: 'text-blue-400 bg-blue-500/20',
    green: 'text-green-400 bg-green-500/20',
    red: 'text-red-400 bg-red-500/20',
    orange: 'text-orange-400 bg-orange-500/20',
  };

  return (
    <div className="crypto-card p-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-gray-400 text-sm">{title}</span>
        <div className={`p-2 rounded ${colors[color]}`}>
          <Icon className="w-4 h-4" />
        </div>
      </div>
      <p className="text-2xl font-bold text-white">{value}</p>
    </div>
  );
}

function DetailItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-crypto-dark rounded p-3">
      <p className="text-xs text-gray-400 mb-1">{label}</p>
      <p className="text-white text-sm font-medium">{value}</p>
    </div>
  );
}
