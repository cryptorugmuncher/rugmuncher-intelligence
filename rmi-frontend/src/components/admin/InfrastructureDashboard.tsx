/**
 * Infrastructure Dashboard
 * N8N workflows, server status, Supabase health, cloud integrations
 */
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../../services/api';
import {
  Server,
  Zap,
  Database,
  Cloud,
  Globe,
  Activity,
  Play,
  Pause,
  RotateCcw,
  RefreshCw,
  Wifi,
  HardDrive,
  Cpu,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Layers,
  Radio,
} from 'lucide-react';

export default function InfrastructureDashboard({ adminKey }: { adminKey: string }) {
  const [n8nFilter, setN8nFilter] = useState('all');
  const queryClient = useQueryClient();

  const { data: infraData, isLoading: infraLoading } = useQuery({
    queryKey: ['admin-infrastructure', adminKey],
    queryFn: () => api.getInfrastructure(adminKey),
    enabled: !!adminKey,
    refetchInterval: 10000,
  });

  const { data: n8nData } = useQuery({
    queryKey: ['admin-n8n-workflows', adminKey],
    queryFn: () => api.getN8nWorkflows(adminKey),
    enabled: !!adminKey,
  });

  const n8nActionMutation = useMutation({
    mutationFn: ({ workflowId, action }: { workflowId: string; action: string }) =>
      api.n8nWorkflowAction(adminKey, workflowId, action),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin-n8n-workflows'] }),
  });

  const services = infraData?.servers || [];
  const databases = infraData?.databases || [];
  const caches = infraData?.caches || [];
  const queues = infraData?.queues || [];

  const workflows = (n8nData?.workflows || []).filter((w: any) => {
    if (n8nFilter === 'all') return true;
    if (n8nFilter === 'active') return w.active;
    if (n8nFilter === 'inactive') return !w.active;
    return true;
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <Cloud className="w-6 h-6 text-neon-cyan" />
          Infrastructure & Cloud
        </h2>
        <button onClick={() => queryClient.invalidateQueries({ queryKey: ['admin-infrastructure'] })} className="btn-secondary p-2">
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {/* Services Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        {services.map((svc: any) => (
          <ServiceCard key={svc.id} name={svc.name} status={svc.status} port={svc.port} />
        ))}
        {databases.map((db: any) => (
          <ServiceCard key={db.name} name={db.name} status={db.status} type="DB" />
        ))}
        {caches.map((cache: any) => (
          <ServiceCard key={cache.name} name={cache.name} status={cache.status} type="Cache" />
        ))}
      </div>

      {/* Cache & Queue Details */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="crypto-card">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <Database className="w-5 h-5 text-neon-green" />
            Cache Status
          </h3>
          {caches.map((cache: any) => (
            <div key={cache.name} className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-white">{cache.name}</span>
                <span className={`px-2 py-0.5 rounded text-xs ${cache.status === 'online' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                  {cache.status.toUpperCase()}
                </span>
              </div>
              {cache.version && (
                <div className="grid grid-cols-3 gap-2 text-xs">
                  <div className="bg-crypto-dark rounded p-2 text-center">
                    <p className="text-white font-bold">{cache.used_memory_mb} MB</p>
                    <p className="text-gray-500">Memory</p>
                  </div>
                  <div className="bg-crypto-dark rounded p-2 text-center">
                    <p className="text-white font-bold">{cache.connected_clients}</p>
                    <p className="text-gray-500">Clients</p>
                  </div>
                  <div className="bg-crypto-dark rounded p-2 text-center">
                    <p className="text-white font-bold">{Math.floor((cache.uptime_seconds || 0) / 3600)}h</p>
                    <p className="text-gray-500">Uptime</p>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>

        <div className="crypto-card">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <Layers className="w-5 h-5 text-neon-yellow" />
            Queue Status
          </h3>
          {queues.map((q: any) => (
            <div key={q.name} className="flex items-center justify-between p-3 bg-crypto-dark rounded">
              <div>
                <p className="text-white font-medium">{q.name}</p>
                <p className="text-xs text-gray-500">Queue</p>
              </div>
              <div className="text-right">
                <p className="text-xl font-bold text-white">{q.depth}</p>
                <p className="text-xs text-gray-500">pending</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* N8N Workflows */}
      <div className="crypto-card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white flex items-center gap-2">
            <Zap className="w-5 h-5 text-neon-yellow" />
            N8N Workflow Automation
          </h3>
          <div className="flex gap-2">
            <select
              value={n8nFilter}
              onChange={(e) => setN8nFilter(e.target.value)}
              className="bg-crypto-dark border border-crypto-border rounded px-3 py-1 text-sm text-white"
            >
              <option value="all">All</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
            <a
              href={import.meta.env.VITE_N8N_URL || 'http://167.86.116.51:5678'}
              target="_blank"
              rel="noopener noreferrer"
              className="btn-primary text-sm px-3 py-1"
            >
              Open N8N
            </a>
          </div>
        </div>

        <div className="space-y-2">
          {workflows.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <Zap className="w-8 h-8 mx-auto mb-2" />
              <p>No workflows found or N8N API unavailable</p>
            </div>
          ) : (
            workflows.map((wf: any) => (
              <div key={wf.id} className="flex items-center justify-between p-3 bg-crypto-dark rounded">
                <div className="flex items-center gap-3">
                  <div className={`w-8 h-8 rounded flex items-center justify-center ${wf.active ? 'bg-yellow-500/20' : 'bg-gray-500/20'}`}>
                    <Zap className={`w-4 h-4 ${wf.active ? 'text-yellow-400' : 'text-gray-400'}`} />
                  </div>
                  <div>
                    <p className="text-white text-sm font-medium">{wf.name}</p>
                    <p className="text-xs text-gray-500">ID: {wf.id}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-0.5 rounded text-xs ${wf.active ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'}`}>
                    {wf.active ? 'ACTIVE' : 'INACTIVE'}
                  </span>
                  <button
                    className="p-1.5 hover:bg-crypto-card rounded text-green-400"
                    onClick={() => n8nActionMutation.mutate({ workflowId: wf.id, action: 'activate' })}
                    title="Activate"
                  >
                    <Play className="w-4 h-4" />
                  </button>
                  <button
                    className="p-1.5 hover:bg-crypto-card rounded text-yellow-400"
                    onClick={() => n8nActionMutation.mutate({ workflowId: wf.id, action: 'deactivate' })}
                    title="Deactivate"
                  >
                    <Pause className="w-4 h-4" />
                  </button>
                  <button
                    className="p-1.5 hover:bg-crypto-card rounded text-blue-400"
                    onClick={() => n8nActionMutation.mutate({ workflowId: wf.id, action: 'execute' })}
                    title="Execute"
                  >
                    <RotateCcw className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

function ServiceCard({ name, status, port, type }: { name: string; status: string; port?: number; type?: string }) {
  const isOnline = status === 'running' || status === 'online';
  return (
    <div className="crypto-card p-3">
      <div className="flex items-center justify-between mb-2">
        <span className="text-gray-400 text-xs">{type || 'Service'}</span>
        <div className={`w-2 h-2 rounded-full ${isOnline ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
      </div>
      <p className="text-sm font-bold text-white truncate">{name}</p>
      <p className="text-xs text-gray-500">{port ? `Port ${port}` : status}</p>
    </div>
  );
}
