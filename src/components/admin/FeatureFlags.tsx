/**
 * Feature Flags Management
 * Toggle features on/off per tier, A/B tests, kill switches
 */
import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
// import { db } from '../../services/supabase';
import {
  ToggleLeft,
  ToggleRight,
  FlaskConical,
  AlertTriangle,
  Zap,
  RefreshCw,
  Plus,
  Trash2,
  Edit3,
  Percent,
  Flag,
  Power,
  Search,
  Rocket,
} from 'lucide-react';

const TIERS = ['FREE', 'BASIC', 'PRO', 'ELITE', 'ENTERPRISE'];
const FEATURE_CATEGORIES = ['Core', 'AI/OSINT', 'Analytics', 'Trenches', 'Rehab', 'API'];

interface FeatureFlag {
  id: string;
  name: string;
  description: string;
  category: string;
  enabled: boolean;
  tierAccess: Record<string, boolean>;
  beta: boolean;
  killSwitch: boolean;
  rolloutPercentage: number;
  createdAt: string;
  updatedAt: string;
}

const DEFAULT_FEATURES: FeatureFlag[] = [
  {
    id: 'wallet_scanner',
    name: 'Wallet Scanner',
    description: 'Basic wallet analysis and risk scoring',
    category: 'Core',
    enabled: true,
    tierAccess: { FREE: true, BASIC: true, PRO: true, ELITE: true, ENTERPRISE: true },
    beta: false,
    killSwitch: false,
    rolloutPercentage: 100,
    createdAt: '2024-01-01',
    updatedAt: '2024-01-01',
  },
  {
    id: 'ai_osint',
    name: 'AI/OSINT Analysis',
    description: 'Advanced AI-powered blockchain analysis',
    category: 'AI/OSINT',
    enabled: true,
    tierAccess: { FREE: false, BASIC: true, PRO: true, ELITE: true, ENTERPRISE: true },
    beta: false,
    killSwitch: false,
    rolloutPercentage: 100,
    createdAt: '2024-01-01',
    updatedAt: '2024-01-01',
  },
  {
    id: 'cross_chain_tracing',
    name: 'Cross-Chain Tracing',
    description: 'Track transactions across multiple blockchains',
    category: 'Analytics',
    enabled: true,
    tierAccess: { FREE: false, BASIC: false, PRO: true, ELITE: true, ENTERPRISE: true },
    beta: false,
    killSwitch: false,
    rolloutPercentage: 100,
    createdAt: '2024-01-01',
    updatedAt: '2024-01-01',
  },
  {
    id: 'trenches_posting',
    name: 'Trenches Community Posting',
    description: 'Post to The Trenches message board',
    category: 'Trenches',
    enabled: true,
    tierAccess: { FREE: true, BASIC: true, PRO: true, ELITE: true, ENTERPRISE: true },
    beta: false,
    killSwitch: false,
    rolloutPercentage: 100,
    createdAt: '2024-01-01',
    updatedAt: '2024-01-01',
  },
  {
    id: 'rug_rehab_booking',
    name: 'Rug Pull Rehab Booking',
    description: 'Book live rehab sessions with experts',
    category: 'Rehab',
    enabled: true,
    tierAccess: { FREE: true, BASIC: true, PRO: true, ELITE: true, ENTERPRISE: true },
    beta: false,
    killSwitch: false,
    rolloutPercentage: 100,
    createdAt: '2024-01-01',
    updatedAt: '2024-01-01',
  },
  {
    id: 'api_access',
    name: 'API Access',
    description: 'Generate and use API keys',
    category: 'API',
    enabled: true,
    tierAccess: { FREE: false, BASIC: false, PRO: true, ELITE: true, ENTERPRISE: true },
    beta: false,
    killSwitch: false,
    rolloutPercentage: 100,
    createdAt: '2024-01-01',
    updatedAt: '2024-01-01',
  },
  {
    id: 'advanced_visualization',
    name: 'Advanced Visualization (WebGL)',
    description: '3D network graph visualization',
    category: 'Analytics',
    enabled: true,
    tierAccess: { FREE: false, BASIC: false, PRO: false, ELITE: true, ENTERPRISE: true },
    beta: true,
    killSwitch: true,
    rolloutPercentage: 50,
    createdAt: '2024-01-15',
    updatedAt: '2024-01-15',
  },
  {
    id: 'whale_alerts',
    name: 'Real-Time Whale Alerts',
    description: 'Instant notifications for large transactions',
    category: 'Core',
    enabled: true,
    tierAccess: { FREE: false, BASIC: true, PRO: true, ELITE: true, ENTERPRISE: true },
    beta: false,
    killSwitch: false,
    rolloutPercentage: 100,
    createdAt: '2024-01-01',
    updatedAt: '2024-01-01',
  },
];

export default function FeatureFlags() {
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [_selectedFeature, setSelectedFeature] = useState<FeatureFlag | null>(null);
  const [_showEditModal, setShowEditModal] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [activeTab, setActiveTab] = useState<'features' | 'ab_tests' | 'rollouts'>('features');

  // Fetch features from database (mocked)
  const { data: features, isLoading, refetch } = useQuery({
    queryKey: ['feature-flags'],
    queryFn: async () => {
      // Mock for now - database integration coming soon
      return DEFAULT_FEATURES;
    },
  });

  // Update feature mutation
  const updateFeature = useMutation({
    mutationFn: async ({ id, updates }: { id: string; updates: Partial<FeatureFlag> }) => {
      // Mock for now - database integration coming soon
      console.log('Update feature', id, updates);
      return { id, ...updates };
    },
    onSuccess: () => refetch(),
  });

  // Create feature mutation
  const createFeature = useMutation({
    mutationFn: async (feature: Partial<FeatureFlag>) => {
      // Mock for now - database integration coming soon
      console.log('Create feature', feature);
      return feature;
    },
    onSuccess: () => {
      refetch();
      setShowCreateModal(false);
    },
  });

  // Delete feature mutation
  const deleteFeature = useMutation({
    mutationFn: async (id: string) => {
      // Mock for now - database integration coming soon
      console.log('Delete feature', id);
      return { id };
    },
    onSuccess: () => refetch(),
  });

  const filteredFeatures = features?.filter((f: FeatureFlag) => {
    const matchesSearch = f.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         f.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = categoryFilter === 'all' || f.category === categoryFilter;
    return matchesSearch && matchesCategory;
  });

  const stats = {
    total: features?.length || 0,
    enabled: features?.filter((f: FeatureFlag) => f.enabled).length || 0,
    beta: features?.filter((f: FeatureFlag) => f.beta).length || 0,
    killSwitches: features?.filter((f: FeatureFlag) => f.killSwitch).length || 0,
  };

  const toggleFeature = (feature: FeatureFlag, field: keyof FeatureFlag) => {
    updateFeature.mutate({
      id: feature.id,
      updates: { [field]: !feature[field] },
    });
  };

  const toggleTierAccess = (feature: FeatureFlag, tier: string) => {
    const newTierAccess = { ...feature.tierAccess, [tier]: !feature.tierAccess[tier] };
    updateFeature.mutate({
      id: feature.id,
      updates: { tierAccess: newTierAccess },
    });
  };

  return (
    <div className="space-y-6">
      {/* Header Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard title="Total Features" value={stats.total} icon={Flag} color="blue" />
        <StatCard title="Enabled" value={stats.enabled} icon={Power} color="green" />
        <StatCard title="Beta Features" value={stats.beta} icon={FlaskConical} color="purple" />
        <StatCard title="Kill Switches" value={stats.killSwitches} icon={AlertTriangle} color="red" />
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-crypto-border">
        {[
          { id: 'features', label: 'Feature Flags', icon: Flag },
          { id: 'ab_tests', label: 'A/B Tests', icon: Percent },
          { id: 'rollouts', label: 'Gradual Rollouts', icon: Rocket },
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

      {/* Filters & Actions */}
      <div className="flex flex-wrap gap-4 items-center justify-between">
        <div className="flex flex-wrap gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search features..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-crypto-card border border-crypto-border rounded-lg pl-10 pr-4 py-2 text-white"
            />
          </div>
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="bg-crypto-card border border-crypto-border rounded-lg px-3 py-2 text-white"
          >
            <option value="all">All Categories</option>
            {FEATURE_CATEGORIES.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
          <button
            onClick={() => refetch()}
            className="btn-secondary flex items-center gap-2"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="btn-primary flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          Add Feature
        </button>
      </div>

      {/* Features Table */}
      {activeTab === 'features' && (
        <div className="crypto-card overflow-hidden">
          {isLoading ? (
            <div className="p-8 text-center text-gray-500">Loading features...</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-crypto-border text-gray-400">
                    <th className="text-left p-3">Feature</th>
                    <th className="text-left p-3">Category</th>
                    <th className="text-center p-3">Status</th>
                    <th className="text-center p-3">Beta</th>
                    <th className="text-center p-3">Kill Switch</th>
                    <th className="text-left p-3">Tier Access</th>
                    <th className="text-right p-3">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredFeatures?.map((feature: FeatureFlag) => (
                    <tr key={feature.id} className="border-b border-crypto-border hover:bg-crypto-dark/50">
                      <td className="p-3">
                        <div>
                          <p className="text-white font-medium">{feature.name}</p>
                          <p className="text-xs text-gray-500">{feature.description}</p>
                        </div>
                      </td>
                      <td className="p-3">
                        <span className="px-2 py-1 rounded text-xs bg-crypto-dark text-gray-300">
                          {feature.category}
                        </span>
                      </td>
                      <td className="p-3 text-center">
                        <button
                          onClick={() => toggleFeature(feature, 'enabled')}
                          className={`p-1 rounded ${feature.enabled ? 'text-green-400' : 'text-gray-500'}`}
                        >
                          {feature.enabled ? <ToggleRight className="w-6 h-6" /> : <ToggleLeft className="w-6 h-6" />}
                        </button>
                      </td>
                      <td className="p-3 text-center">
                        <button
                          onClick={() => toggleFeature(feature, 'beta')}
                          className={`p-1 rounded ${feature.beta ? 'text-purple-400' : 'text-gray-500'}`}
                        >
                          {feature.beta ? <FlaskConical className="w-5 h-5" /> : <FlaskConical className="w-5 h-5" />}
                        </button>
                      </td>
                      <td className="p-3 text-center">
                        <button
                          onClick={() => toggleFeature(feature, 'killSwitch')}
                          className={`p-1 rounded ${feature.killSwitch ? 'text-red-400' : 'text-gray-500'}`}
                          title={feature.killSwitch ? 'Emergency kill switch enabled' : 'No kill switch'}
                        >
                          {feature.killSwitch ? <AlertTriangle className="w-5 h-5" /> : <Zap className="w-5 h-5" />}
                        </button>
                      </td>
                      <td className="p-3">
                        <div className="flex gap-1">
                          {TIERS.map((tier) => (
                            <button
                              key={tier}
                              onClick={() => toggleTierAccess(feature, tier)}
                              className={`px-2 py-1 rounded text-xs ${
                                feature.tierAccess[tier]
                                  ? 'bg-green-500/20 text-green-400'
                                  : 'bg-gray-500/20 text-gray-500'
                              }`}
                              title={tier}
                            >
                              {tier[0]}
                            </button>
                          ))}
                        </div>
                      </td>
                      <td className="p-3">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            onClick={() => {
                              setSelectedFeature(feature);
                              setShowEditModal(true);
                            }}
                            className="p-2 hover:bg-crypto-card rounded text-blue-400"
                          >
                            <Edit3 className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => deleteFeature.mutate(feature.id)}
                            className="p-2 hover:bg-crypto-card rounded text-red-400"
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
      )}

      {/* A/B Tests Tab */}
      {activeTab === 'ab_tests' && (
        <div className="crypto-card p-8 text-center text-gray-500">
          <Percent className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p>A/B Test configuration coming soon</p>
          <p className="text-sm mt-2">Configure experiments and track conversion rates</p>
        </div>
      )}

      {/* Gradual Rollouts Tab */}
      {activeTab === 'rollouts' && (
        <div className="crypto-card p-8 text-center text-gray-500">
          <Rocket className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p>Gradual rollout controls coming soon</p>
          <p className="text-sm mt-2">Roll out features to specific user percentages</p>
        </div>
      )}

      {/* Create Feature Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="crypto-card w-full max-w-lg">
            <h3 className="text-lg font-bold text-white mb-4">Create Feature Flag</h3>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                const formData = new FormData(e.currentTarget);
                createFeature.mutate({
                  id: formData.get('id') as string,
                  name: formData.get('name') as string,
                  description: formData.get('description') as string,
                  category: formData.get('category') as string,
                  enabled: false,
                  tierAccess: { FREE: false, BASIC: false, PRO: false, ELITE: false, ENTERPRISE: false },
                  beta: true,
                  killSwitch: false,
                  rolloutPercentage: 0,
                  createdAt: new Date().toISOString(),
                  updatedAt: new Date().toISOString(),
                });
              }}
              className="space-y-4"
            >
              <div>
                <label className="block text-sm text-gray-400 mb-1">Feature ID</label>
                <input
                  name="id"
                  type="text"
                  required
                  className="w-full bg-crypto-dark border border-crypto-border rounded px-3 py-2 text-white font-mono"
                  placeholder="e.g., new_feature_v2"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Name</label>
                <input
                  name="name"
                  type="text"
                  required
                  className="w-full bg-crypto-dark border border-crypto-border rounded px-3 py-2 text-white"
                  placeholder="Feature display name"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Description</label>
                <textarea
                  name="description"
                  required
                  className="w-full bg-crypto-dark border border-crypto-border rounded px-3 py-2 text-white"
                  rows={2}
                  placeholder="What does this feature do?"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Category</label>
                <select
                  name="category"
                  className="w-full bg-crypto-dark border border-crypto-border rounded px-3 py-2 text-white"
                >
                  {FEATURE_CATEGORIES.map((c) => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
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
                  Create Feature
                </button>
              </div>
            </form>
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
