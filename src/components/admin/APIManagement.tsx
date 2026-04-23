/**
 * API Management Panel
 * API key generation, rate limits, endpoint analytics
 */
import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { db } from '../../services/supabase';
import {
  Key,
  Activity,
  Ban,
  Plus,
  Trash2,
  RefreshCw,
  Copy,
  CheckCircle,
  Terminal,
  Settings,
  Search,
} from 'lucide-react';

interface APIKey {
  id: string;
  name: string;
  key: string;
  prefix: string;
  createdAt: string;
  lastUsed: string | null;
  requestsCount: number;
  rateLimit: number;
  tier: string;
  status: 'active' | 'revoked' | 'expired';
  ipWhitelist: string[];
  endpoints: string[];
}

interface EndpointStats {
  path: string;
  method: string;
  requests: number;
  avgResponseTime: number;
  errorRate: number;
}

// const MOCK_API_KEYS: APIKey[] = [
//   {
//     id: 'key_1',
//     name: 'Production Client',
//     key: 'rm_live_xxxxxxxxxxxxxxxx',
//     prefix: 'rm_live',
//     createdAt: '2024-01-01',
//     lastUsed: '2024-01-15T10:30:00Z',
//     requestsCount: 15234,
//     rateLimit: 1000,
//     tier: 'ELITE',
//     status: 'active',
//     ipWhitelist: ['192.168.1.100', '10.0.0.50'],
//     endpoints: ['/api/v1/wallets/scan', '/api/v1/investigations'],
//   },
//   {
//     id: 'key_2',
//     name: 'Development Testing',
//     key: 'rm_dev_xxxxxxxxxxxxxxxx',
//     prefix: 'rm_dev',
//     createdAt: '2024-01-05',
//     lastUsed: '2024-01-14T15:20:00Z',
//     requestsCount: 3421,
//     rateLimit: 100,
//     tier: 'BASIC',
//     status: 'active',
//     ipWhitelist: [],
//     endpoints: ['/api/v1/wallets/scan'],
//   },
//   {
//     id: 'key_3',
//     name: 'Partner Integration',
//     key: 'rm_partner_xxxxxxxxxx',
//     prefix: 'rm_partner',
//     createdAt: '2023-12-15',
//     lastUsed: null,
//     requestsCount: 0,
//     rateLimit: 5000,
//     tier: 'ENTERPRISE',
//     status: 'revoked',
//     ipWhitelist: ['203.0.113.0/24'],
//     endpoints: ['/api/v1/**'],
//   },
// ];

const MOCK_ENDPOINTS: EndpointStats[] = [
  { path: '/api/v1/wallets/scan', method: 'POST', requests: 45231, avgResponseTime: 245, errorRate: 0.02 },
  { path: '/api/v1/investigations', method: 'GET', requests: 32145, avgResponseTime: 120, errorRate: 0.01 },
  { path: '/api/v1/investigations', method: 'POST', requests: 8923, avgResponseTime: 380, errorRate: 0.03 },
  { path: '/api/v1/evidence', method: 'POST', requests: 15678, avgResponseTime: 180, errorRate: 0.015 },
  { path: '/api/v1/users/profile', method: 'GET', requests: 28765, avgResponseTime: 85, errorRate: 0.005 },
];

const TIER_LIMITS = [
  { tier: 'FREE', requests: 100, burst: 10 },
  { tier: 'BASIC', requests: 1000, burst: 100 },
  { tier: 'PRO', requests: 10000, burst: 500 },
  { tier: 'ELITE', requests: 100000, burst: 2000 },
  { tier: 'ENTERPRISE', requests: 1000000, burst: 10000 },
];

export default function APIManagement() {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showKeyModal, setShowKeyModal] = useState(false);
  const [newKey, setNewKey] = useState<string | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'keys' | 'endpoints' | 'limits'>('keys');

  const { data: apiKeys, isLoading, refetch } = useQuery({
    queryKey: ['api-keys'],
    queryFn: async () => {
      const { data, error } = await db.apiKeys.getAll();
      if (error) throw error;
      // Transform database format to component format
      return (data || []).map((k: any) => ({
        id: k.id,
        name: k.name,
        key: k.key,
        prefix: k.prefix,
        createdAt: k.created_at,
        lastUsed: k.last_used,
        requestsCount: k.requests_count || 0,
        rateLimit: k.rate_limit,
        tier: k.tier,
        status: k.status,
        ipWhitelist: k.ip_whitelist || [],
        endpoints: k.endpoints || [],
      }));
    },
  });

  const createKey = useMutation({
    mutationFn: async (data: { name: string; tier: string; rateLimit: number }) => {
      const key = `rm_${data.tier.toLowerCase()}_${Math.random().toString(36).substring(2, 18)}`;
      const newKeyData = {
        name: data.name,
        key: key,
        prefix: `rm_${data.tier.toLowerCase()}`,
        rate_limit: data.rateLimit,
        tier: data.tier,
        status: 'active',
        ip_whitelist: [],
        endpoints: [],
      };
      const { data: result, error } = await db.apiKeys.create(newKeyData);
      if (error) throw error;
      return { ...result, key }; // Return full key for display
    },
    onSuccess: (data) => {
      setNewKey(data.key);
      setShowCreateModal(false);
      setShowKeyModal(true);
      refetch();
    },
  });

  const revokeKey = useMutation({
    mutationFn: async (id: string) => {
      const { data, error } = await db.apiKeys.revoke(id);
      if (error) throw error;
      return data;
    },
    onSuccess: () => refetch(),
  });

  const deleteKey = useMutation({
    mutationFn: async (id: string) => {
      const { data, error } = await db.apiKeys.delete(id);
      if (error) throw error;
      return data;
    },
    onSuccess: () => refetch(),
  });

  const filteredKeys = apiKeys?.filter((key: APIKey) => {
    const matchesSearch = key.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === 'all' || key.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const stats = {
    totalKeys: apiKeys?.length || 0,
    activeKeys: apiKeys?.filter((k: APIKey) => k.status === 'active').length || 0,
    totalRequests: apiKeys?.reduce((acc: number, k: APIKey) => acc + k.requestsCount, 0) || 0,
    revokedKeys: apiKeys?.filter((k: APIKey) => k.status === 'revoked').length || 0,
  };

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard title="Total Keys" value={stats.totalKeys} icon={Key} color="blue" />
        <StatCard title="Active Keys" value={stats.activeKeys} icon={CheckCircle} color="green" />
        <StatCard title="Total Requests" value={stats.totalRequests.toLocaleString()} icon={Activity} color="purple" />
        <StatCard title="Revoked" value={stats.revokedKeys} icon={Ban} color="red" />
      </div>

      <div className="flex gap-2 border-b border-crypto-border">
        {[
          { id: 'keys', label: 'API Keys', icon: Key },
          { id: 'endpoints', label: 'Endpoints', icon: Terminal },
          { id: 'limits', label: 'Rate Limits', icon: Settings },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors ${
              activeTab === tab.id
                ? 'text-neon-green border-b-2 border-neon-green'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === 'keys' && (
        <>
          <div className="flex flex-wrap gap-4 items-center justify-between">
            <div className="flex flex-wrap gap-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search API keys..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="bg-crypto-card border border-crypto-border rounded-lg pl-10 pr-4 py-2 text-white"
                />
              </div>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="bg-crypto-card border border-crypto-border rounded-lg px-3 py-2 text-white"
              >
                <option value="all">All Status</option>
                <option value="active">Active</option>
                <option value="revoked">Revoked</option>
                <option value="expired">Expired</option>
              </select>
              <button onClick={() => refetch()} className="btn-secondary flex items-center gap-2">
                <RefreshCw className="w-4 h-4" />
                Refresh
              </button>
            </div>
            <button onClick={() => setShowCreateModal(true)} className="btn-primary flex items-center gap-2">
              <Plus className="w-4 h-4" />
              Create API Key
            </button>
          </div>

          <div className="crypto-card overflow-hidden">
            {isLoading ? (
              <div className="p-8 text-center text-gray-500">Loading API keys...</div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-crypto-border text-gray-400">
                      <th className="text-left p-3">Name</th>
                      <th className="text-left p-3">Key</th>
                      <th className="text-left p-3">Tier</th>
                      <th className="text-left p-3">Rate Limit</th>
                      <th className="text-left p-3">Requests</th>
                      <th className="text-left p-3">Last Used</th>
                      <th className="text-left p-3">Status</th>
                      <th className="text-right p-3">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredKeys?.map((key: APIKey) => (
                      <tr key={key.id} className="border-b border-crypto-border hover:bg-crypto-dark/50">
                        <td className="p-3">
                          <div>
                            <p className="text-white font-medium">{key.name}</p>
                            <p className="text-xs text-gray-500">Created {new Date(key.createdAt).toLocaleDateString()}</p>
                          </div>
                        </td>
                        <td className="p-3">
                          <div className="flex items-center gap-2">
                            <code className="text-neon-green font-mono text-sm">{key.key.substring(0, 20)}...</code>
                            <button
                              onClick={() => copyToClipboard(key.key, key.id)}
                              className="p-1 hover:bg-crypto-card rounded"
                            >
                              {copiedId === key.id ? (
                                <CheckCircle className="w-4 h-4 text-green-400" />
                              ) : (
                                <Copy className="w-4 h-4 text-gray-400" />
                              )}
                            </button>
                          </div>
                        </td>
                        <td className="p-3">
                          <span className={`px-2 py-1 rounded text-xs ${
                            key.tier === 'ENTERPRISE' ? 'bg-purple-500/20 text-purple-400' :
                            key.tier === 'ELITE' ? 'bg-yellow-500/20 text-yellow-400' :
                            key.tier === 'PRO' ? 'bg-blue-500/20 text-blue-400' :
                            'bg-gray-500/20 text-gray-400'
                          }`}>
                            {key.tier}
                          </span>
                        </td>
                        <td className="p-3 text-gray-300">{key.rateLimit.toLocaleString()}/min</td>
                        <td className="p-3 text-gray-300">{key.requestsCount.toLocaleString()}</td>
                        <td className="p-3 text-gray-400">
                          {key.lastUsed ? new Date(key.lastUsed).toLocaleDateString() : 'Never'}
                        </td>
                        <td className="p-3">
                          <span className={`px-2 py-1 rounded text-xs ${
                            key.status === 'active' ? 'bg-green-500/20 text-green-400' :
                            key.status === 'revoked' ? 'bg-red-500/20 text-red-400' :
                            'bg-yellow-500/20 text-yellow-400'
                          }`}>
                            {key.status.toUpperCase()}
                          </span>
                        </td>
                        <td className="p-3">
                          <div className="flex items-center justify-end gap-2">
                            {key.status === 'active' && (
                              <button
                                onClick={() => revokeKey.mutate(key.id)}
                                className="p-2 hover:bg-crypto-card rounded text-yellow-400"
                                title="Revoke"
                              >
                                <Ban className="w-4 h-4" />
                              </button>
                            )}
                            <button
                              onClick={() => deleteKey.mutate(key.id)}
                              className="p-2 hover:bg-crypto-card rounded text-red-400"
                              title="Delete"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      )}

      {activeTab === 'endpoints' && (
        <div className="crypto-card overflow-hidden">
          <div className="p-4 border-b border-crypto-border">
            <h3 className="text-lg font-semibold text-white">Endpoint Analytics</h3>
            <p className="text-sm text-gray-400">API usage and performance metrics</p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-crypto-border text-gray-400">
                  <th className="text-left p-3">Endpoint</th>
                  <th className="text-left p-3">Method</th>
                  <th className="text-right p-3">Requests</th>
                  <th className="text-right p-3">Avg Response</th>
                  <th className="text-right p-3">Error Rate</th>
                  <th className="text-left p-3">Status</th>
                </tr>
              </thead>
              <tbody>
                {MOCK_ENDPOINTS.map((endpoint, idx) => (
                  <tr key={idx} className="border-b border-crypto-border hover:bg-crypto-dark/50">
                    <td className="p-3 font-mono text-neon-green">{endpoint.path}</td>
                    <td className="p-3">
                      <span className={`px-2 py-1 rounded text-xs ${
                        endpoint.method === 'GET' ? 'bg-blue-500/20 text-blue-400' :
                        endpoint.method === 'POST' ? 'bg-green-500/20 text-green-400' :
                        'bg-yellow-500/20 text-yellow-400'
                      }`}>
                        {endpoint.method}
                      </span>
                    </td>
                    <td className="p-3 text-right text-white">{endpoint.requests.toLocaleString()}</td>
                    <td className="p-3 text-right text-gray-300">{endpoint.avgResponseTime}ms</td>
                    <td className="p-3 text-right">
                      <span className={endpoint.errorRate > 0.05 ? 'text-red-400' : 'text-green-400'}>
                        {(endpoint.errorRate * 100).toFixed(2)}%
                      </span>
                    </td>
                    <td className="p-3">
                      <span className="flex items-center gap-1 text-green-400">
                        <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                        Healthy
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === 'limits' && (
        <div className="space-y-6">
          <div className="crypto-card">
            <h3 className="text-lg font-semibold text-white mb-4">Tier Rate Limits</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
              {TIER_LIMITS.map((tier) => (
                <div key={tier.tier} className="bg-crypto-dark rounded p-4">
                  <h4 className="text-white font-medium mb-2">{tier.tier}</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-400">Requests/min</span>
                      <span className="text-neon-green">{tier.requests.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Burst</span>
                      <span className="text-neon-blue">{tier.burst.toLocaleString()}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="crypto-card">
            <h3 className="text-lg font-semibold text-white mb-4">IP Blocking</h3>
            <div className="bg-crypto-dark rounded p-4">
              <div className="flex items-center justify-between mb-4">
                <span className="text-gray-300">Currently blocked IPs: 3</span>
                <button className="btn-secondary text-sm">View All</button>
              </div>
              <div className="space-y-2">
                {['192.0.2.1', '203.0.113.45', '198.51.100.22'].map((ip) => (
                  <div key={ip} className="flex items-center justify-between p-2 bg-crypto-card rounded">
                    <div className="flex items-center gap-2">
                      <Ban className="w-4 h-4 text-red-400" />
                      <span className="font-mono text-white">{ip}</span>
                    </div>
                    <button className="text-neon-green text-sm hover:underline">Unblock</button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="crypto-card w-full max-w-md">
            <h3 className="text-lg font-bold text-white mb-4">Create API Key</h3>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                const formData = new FormData(e.currentTarget);
                createKey.mutate({
                  name: formData.get('name') as string,
                  tier: formData.get('tier') as string,
                  rateLimit: parseInt(formData.get('rateLimit') as string),
                });
              }}
              className="space-y-4"
            >
              <div>
                <label className="block text-sm text-gray-400 mb-1">Name</label>
                <input
                  name="name"
                  type="text"
                  required
                  className="w-full bg-crypto-dark border border-crypto-border rounded px-3 py-2 text-white"
                  placeholder="e.g., Production API Key"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Tier</label>
                <select
                  name="tier"
                  className="w-full bg-crypto-dark border border-crypto-border rounded px-3 py-2 text-white"
                >
                  {TIER_LIMITS.map((t) => (
                    <option key={t.tier} value={t.tier}>{t.tier}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Rate Limit (requests/min)</label>
                <input
                  name="rateLimit"
                  type="number"
                  defaultValue={1000}
                  min={1}
                  max={1000000}
                  className="w-full bg-crypto-dark border border-crypto-border rounded px-3 py-2 text-white"
                />
              </div>
              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="flex-1 btn-secondary"
                >
                  Cancel
                </button>
                <button type="submit" className="flex-1 btn-primary">
                  Create Key
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showKeyModal && newKey && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="crypto-card w-full max-w-lg">
            <div className="text-center mb-4">
              <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <Key className="w-8 h-8 text-green-400" />
              </div>
              <h3 className="text-lg font-bold text-white">API Key Created</h3>
              <p className="text-sm text-gray-400 mt-1">Copy this key now. You won&apos;t be able to see it again.</p>
            </div>
            <div className="bg-crypto-dark rounded p-4 mb-4">
              <code className="text-neon-green font-mono text-sm break-all">{newKey}</code>
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => copyToClipboard(newKey, 'new')}
                className="flex-1 btn-secondary flex items-center justify-center gap-2"
              >
                {copiedId === 'new' ? (
                  <>
                    <CheckCircle className="w-4 h-4" />
                    Copied!
                  </>
                ) : (
                  <>
                    <Copy className="w-4 h-4" />
                    Copy Key
                  </>
                )}
              </button>
              <button
                onClick={() => {
                  setShowKeyModal(false);
                  setNewKey(null);
                }}
                className="flex-1 btn-primary"
              >
                Done
              </button>
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
    purple: 'text-purple-400 bg-purple-500/20',
    red: 'text-red-400 bg-red-500/20',
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
