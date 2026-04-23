/**
 * Wallets Component
 * Manage tracked wallets
 */
import { useState } from 'react';
import { useWallets, useCreateWallet } from '../hooks/useBackend';
import { useAppStore } from '../store/appStore';
import { Wallet, Plus, Search, Filter, ExternalLink, Trash2, Eye, AlertTriangle } from 'lucide-react';

const CHAINS = [
  { id: 'ethereum', name: 'Ethereum', icon: '◆' },
  { id: 'bsc', name: 'BSC', icon: '⬡' },
  { id: 'polygon', name: 'Polygon', icon: '◇' },
  { id: 'arbitrum', name: 'Arbitrum', icon: '◇' },
  { id: 'base', name: 'Base', icon: '◇' },
];

export default function Wallets() {
  const [searchQuery, setSearchQuery] = useState('');
  const [chainFilter, setChainFilter] = useState<string>('all');
  const [riskFilter, setRiskFilter] = useState<string>('all');
  const [showAddModal, setShowAddModal] = useState(false);

  const { data: wallets, isLoading } = useWallets();
  const createWallet = useCreateWallet();
  const setCurrentPage = useAppStore((state) => state.setCurrentPage);

  const filteredWallets = wallets?.filter((wallet) => {
    const matchesSearch = wallet.address.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         wallet.label?.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesChain = chainFilter === 'all' || wallet.chain === chainFilter;
    const matchesRisk = riskFilter === 'all' || wallet.risk_level?.toLowerCase() === riskFilter;
    return matchesSearch && matchesChain && matchesRisk;
  });

  const getRiskColor = (level?: string) => {
    switch (level?.toLowerCase()) {
      case 'low':
        return 'text-green-400 bg-green-500/20';
      case 'medium':
        return 'text-yellow-400 bg-yellow-500/20';
      case 'high':
        return 'text-orange-400 bg-orange-500/20';
      case 'critical':
        return 'text-red-400 bg-red-500/20 animate-pulse';
      default:
        return 'text-gray-400 bg-gray-500/20';
    }
  };

  const truncateAddress = (address: string) => {
    return `${address.slice(0, 8)}...${address.slice(-6)}`;
  };

  const getChainIcon = (chain: string) => {
    return CHAINS.find(c => c.id === chain)?.icon || '◇';
  };

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Wallet className="w-6 h-6 text-neon-green" />
            Tracked Wallets
          </h1>
          <p className="text-gray-400 mt-1">
            Monitor and analyze suspicious wallet addresses
          </p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="btn-primary flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          Add Wallet
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="crypto-card">
          <p className="text-gray-400 text-sm">Total Wallets</p>
          <p className="text-2xl font-bold text-white">{wallets?.length || 0}</p>
        </div>
        <div className="crypto-card">
          <p className="text-gray-400 text-sm">High Risk</p>
          <p className="text-2xl font-bold text-red-400">
            {wallets?.filter(w => w.risk_level === 'HIGH' || w.risk_level === 'CRITICAL').length || 0}
          </p>
        </div>
        <div className="crypto-card">
          <p className="text-gray-400 text-sm">Under Investigation</p>
          <p className="text-2xl font-bold text-yellow-400">
            {wallets?.filter(w => w.status === 'investigating').length || 0}
          </p>
        </div>
        <div className="crypto-card">
          <p className="text-gray-400 text-sm">Flagged</p>
          <p className="text-2xl font-bold text-orange-400">
            {wallets?.filter(w => w.is_flagged).length || 0}
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-4 mb-6">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search wallet address or label..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-crypto-card border border-crypto-border rounded pl-10 pr-4 py-2
                       text-white focus:border-neon-green focus:outline-none"
          />
        </div>
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-gray-400" />
          <select
            value={chainFilter}
            onChange={(e) => setChainFilter(e.target.value)}
            className="bg-crypto-card border border-crypto-border rounded px-3 py-2
                       text-white focus:border-neon-green focus:outline-none"
          >
            <option value="all">All Chains</option>
            {CHAINS.map(chain => (
              <option key={chain.id} value={chain.id}>{chain.name}</option>
            ))}
          </select>
          <select
            value={riskFilter}
            onChange={(e) => setRiskFilter(e.target.value)}
            className="bg-crypto-card border border-crypto-border rounded px-3 py-2
                       text-white focus:border-neon-green focus:outline-none"
          >
            <option value="all">All Risk Levels</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="critical">Critical</option>
          </select>
        </div>
      </div>

      {/* Wallets Table */}
      {isLoading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-pulse text-neon-green">Loading...</div>
        </div>
      ) : filteredWallets?.length === 0 ? (
        <div className="text-center py-12">
          <Wallet className="w-12 h-12 text-gray-600 mx-auto mb-4" />
          <p className="text-gray-400">
            {searchQuery
              ? 'No wallets match your search'
              : 'No wallets tracked yet. Add your first wallet!'}
          </p>
        </div>
      ) : (
        <div className="crypto-card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-crypto-border">
                  <th className="text-left p-4 text-gray-400 font-medium">Address</th>
                  <th className="text-left p-4 text-gray-400 font-medium">Chain</th>
                  <th className="text-left p-4 text-gray-400 font-medium">Label</th>
                  <th className="text-left p-4 text-gray-400 font-medium">Risk</th>
                  <th className="text-left p-4 text-gray-400 font-medium">Status</th>
                  <th className="text-left p-4 text-gray-400 font-medium">Added</th>
                  <th className="text-right p-4 text-gray-400 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredWallets?.map((wallet) => (
                  <tr
                    key={wallet.id}
                    className="border-b border-crypto-border hover:bg-crypto-dark/50 transition-colors"
                  >
                    <td className="p-4">
                      <div className="flex items-center gap-2">
                        <code className="text-neon-green font-mono text-sm">
                          {truncateAddress(wallet.address)}
                        </code>
                        {wallet.is_flagged && (
                          <AlertTriangle className="w-4 h-4 text-red-400" />
                        )}
                      </div>
                    </td>
                    <td className="p-4">
                      <span className="flex items-center gap-1 text-gray-300">
                        <span className="text-neon-blue">{getChainIcon(wallet.chain)}</span>
                        {wallet.chain}
                      </span>
                    </td>
                    <td className="p-4 text-gray-300">{wallet.label || '-'}</td>
                    <td className="p-4">
                      {wallet.risk_level ? (
                        <span className={`px-2 py-1 rounded text-xs ${getRiskColor(wallet.risk_level)}`}>
                          {wallet.risk_level}
                        </span>
                      ) : (
                        <span className="text-gray-500">-</span>
                      )}
                    </td>
                    <td className="p-4">
                      <span className={`px-2 py-1 rounded text-xs ${
                        wallet.status === 'active' ? 'bg-green-500/20 text-green-400' :
                        wallet.status === 'investigating' ? 'bg-yellow-500/20 text-yellow-400' :
                        'bg-gray-500/20 text-gray-400'
                      }`}>
                        {wallet.status || 'unknown'}
                      </span>
                    </td>
                    <td className="p-4 text-gray-400 text-sm">
                      {new Date(wallet.created_at).toLocaleDateString()}
                    </td>
                    <td className="p-4">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => setCurrentPage('scanner')}
                          className="p-2 text-gray-400 hover:text-neon-green transition-colors"
                          title="Analyze"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                        <button
                          className="p-2 text-gray-400 hover:text-neon-blue transition-colors"
                          title="View on Explorer"
                        >
                          <ExternalLink className="w-4 h-4" />
                        </button>
                        <button
                          className="p-2 text-gray-400 hover:text-red-400 transition-colors"
                          title="Remove"
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
        </div>
      )}

      {/* Add Wallet Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="crypto-card w-full max-w-md">
            <h2 className="text-xl font-bold text-white mb-4">Add Wallet to Track</h2>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                const formData = new FormData(e.currentTarget);
                createWallet.mutate({
                  address: formData.get('address') as string,
                  chain: formData.get('chain') as string,
                  label: formData.get('label') as string,
                  status: 'active',
                });
                setShowAddModal(false);
              }}
              className="space-y-4"
            >
              <div>
                <label className="block text-sm text-gray-400 mb-1">Wallet Address</label>
                <input
                  name="address"
                  type="text"
                  required
                  placeholder="0x..."
                  className="w-full bg-crypto-dark border border-crypto-border rounded px-3 py-2 text-white
                             focus:border-neon-green focus:outline-none font-mono"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Blockchain</label>
                <select
                  name="chain"
                  required
                  className="w-full bg-crypto-dark border border-crypto-border rounded px-3 py-2 text-white
                             focus:border-neon-green focus:outline-none"
                >
                  {CHAINS.map(chain => (
                    <option key={chain.id} value={chain.id}>{chain.name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Label (Optional)</label>
                <input
                  name="label"
                  type="text"
                  placeholder="e.g., Scam Contract #1"
                  className="w-full bg-crypto-dark border border-crypto-border rounded px-3 py-2 text-white
                             focus:border-neon-green focus:outline-none"
                />
              </div>
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="flex-1 btn-secondary"
                >
                  Cancel
                </button>
                <button type="submit" className="flex-1 btn-primary">
                  Add Wallet
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
