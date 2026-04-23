import React, { useState } from 'react';
import {
  Wallet,
  Plus,
  Copy,
  Eye,
  EyeOff,
  Key,
  Shield,
  CheckCircle,
  AlertTriangle,
  Download,
  Lock,
  RefreshCw,
  ExternalLink,
  Layers,
  Bitcoin,
  Hexagon,
  CircleDollarSign,
  Database,
  ArrowRightLeft,
  Send,
  QrCode,
  Trash2,
  Edit3
} from 'lucide-react';

interface WalletData {
  id: string;
  name: string;
  address: string;
  privateKey: string;
  chain: 'ethereum' | 'base' | 'arbitrum' | 'optimism' | 'bsc' | 'polygon' | 'avalanche' | 'solana';
  purpose: 'treasury' | 'operations' | 'investment' | 'trading' | 'development' | 'marketing' | 'rewards';
  balance: string;
  usdValue: string;
  lastUsed: string;
  status: 'active' | 'locked' | 'archived';
  securityLevel: 'standard' | 'multisig' | 'hardware' | 'cold';
  requiresApproval: boolean;
  transactions: Transaction[];
}

interface Transaction {
  id: string;
  type: 'in' | 'out';
  amount: string;
  token: string;
  from: string;
  to: string;
  timestamp: string;
  status: 'pending' | 'confirmed' | 'failed';
  hash: string;
}

const WalletManager: React.FC = () => {
  const [wallets, setWallets] = useState<WalletData[]>([
    {
      id: 'w1',
      name: 'Primary Treasury',
      address: '0x742d35Cc6Ef8d3f8d3a8f3a8f3a8f3a8f3a8f3a8',
      privateKey: '••••••••••••••••••••••••••••••••••••••••••••••••••',
      chain: 'ethereum',
      purpose: 'treasury',
      balance: '245.5 ETH',
      usdValue: '$736,500',
      lastUsed: '2 hours ago',
      status: 'active',
      securityLevel: 'multisig',
      requiresApproval: true,
      transactions: []
    },
    {
      id: 'w2',
      name: 'Base Operations',
      address: '0x91ab22Cc6Ef8d3f8d3a8f3a8f3a8f3a8f3a8f3a8',
      privateKey: '••••••••••••••••••••••••••••••••••••••••••••••••••',
      chain: 'base',
      purpose: 'operations',
      balance: '1,250.0 ETH',
      usdValue: '$3,750,000',
      lastUsed: '15 minutes ago',
      status: 'active',
      securityLevel: 'multisig',
      requiresApproval: true,
      transactions: []
    }
  ]);

  const [selectedWallet, setSelectedWallet] = useState<string | null>('w1');
  const [showPrivateKey, setShowPrivateKey] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [humanOverride, setHumanOverride] = useState(false);
  const [activeTab, setActiveTab] = useState<'overview' | 'generate' | 'treasury' | 'investment'>('overview');

  const [newWalletForm, setNewWalletForm] = useState({
    name: '',
    chain: 'ethereum',
    purpose: 'treasury',
    securityLevel: 'standard'
  });

  const chains = [
    { id: 'ethereum', name: 'Ethereum', icon: <Hexagon className="w-5 h-5 text-purple-400" />, native: 'ETH' },
    { id: 'base', name: 'Base', icon: <CircleDollarSign className="w-5 h-5 text-blue-400" />, native: 'ETH' },
    { id: 'arbitrum', name: 'Arbitrum', icon: <Layers className="w-5 h-5 text-blue-500" />, native: 'ETH' },
    { id: 'optimism', name: 'Optimism', icon: <SunIcon className="w-5 h-5 text-red-400" />, native: 'ETH' },
    { id: 'bsc', name: 'BSC', icon: <Bitcoin className="w-5 h-5 text-yellow-400" />, native: 'BNB' },
    { id: 'polygon', name: 'Polygon', icon: <Hexagon className="w-5 h-5 text-purple-500" />, native: 'MATIC' },
    { id: 'avalanche', name: 'Avalanche', icon: <TriangleIcon className="w-5 h-5 text-red-500" />, native: 'AVAX' },
    { id: 'solana', name: 'Solana', icon: <Database className="w-5 h-5 text-green-400" />, native: 'SOL' },
  ];

  const generateWallet = () => {
    const mockAddress = '0x' + Array(40).fill(0).map(() => Math.floor(Math.random() * 16).toString(16)).join('');
    const mockPrivateKey = '0x' + Array(64).fill(0).map(() => Math.floor(Math.random() * 16).toString(16)).join('');

    const newWallet: WalletData = {
      id: `w${Date.now()}`,
      name: newWalletForm.name || `New ${chains.find(c => c.id === newWalletForm.chain)?.name} Wallet`,
      address: mockAddress,
      privateKey: mockPrivateKey,
      chain: newWalletForm.chain as any,
      purpose: newWalletForm.purpose as any,
      balance: '0.00 ' + chains.find(c => c.id === newWalletForm.chain)?.native,
      usdValue: '$0.00',
      lastUsed: 'Just created',
      status: 'active',
      securityLevel: newWalletForm.securityLevel as any,
      requiresApproval: newWalletForm.securityLevel === 'multisig' || newWalletForm.securityLevel === 'cold',
      transactions: []
    };

    setWallets([...wallets, newWallet]);
    setShowCreateModal(false);
    setNewWalletForm({ name: '', chain: 'ethereum', purpose: 'treasury', securityLevel: 'standard' });
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const currentWallet = wallets.find(w => w.id === selectedWallet);

  const getChainIcon = (chainId: string) => {
    return chains.find(c => c.id === chainId)?.icon || <Wallet className="w-5 h-5" />;
  };

  return (
    <div className="min-h-screen bg-[#0a0812] text-gray-100 font-mono selection:bg-[#7c3aed]/30">
      {/* Header */}
      <div className="bg-gradient-to-r from-[#0f0c1d] via-[#1a1525] to-[#0f0c1d] border-b border-[#7c3aed]/30">
        <div className="max-w-[1600px] mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Wallet className="w-8 h-8 text-[#7c3aed]" />
              <div>
                <h1 className="text-xl font-bold tracking-wider">
                  TREASURY <span className="text-[#7c3aed]">VAULT</span>
                </h1>
                <p className="text-xs text-gray-500 tracking-[0.2em]">MULTI-CHAIN WALLET MANAGEMENT</p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <div className="text-right">
                <div className="text-xs text-gray-500">Total Portfolio Value</div>
                <div className="text-2xl font-bold text-green-400">$4,486,500</div>
              </div>
              <button
                onClick={() => setHumanOverride(!humanOverride)}
                className={`flex items-center gap-2 px-4 py-2 rounded border transition-all ${
                  humanOverride
                    ? 'bg-green-500/20 border-green-500/50 text-green-400'
                    : 'bg-gray-800 border-gray-700 text-gray-400'
                }`}
              >
                <Shield className="w-4 h-4" />
                <span className="text-xs font-bold">{humanOverride ? 'HUMAN CONTROL' : 'AUTONOMOUS'}</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="bg-[#0f0c1d] border-b border-gray-800">
        <div className="max-w-[1600px] mx-auto px-6">
          <div className="flex items-center gap-1">
            {[
              { id: 'overview', label: 'WALLET OVERVIEW', icon: <Wallet className="w-4 h-4" /> },
              { id: 'generate', label: 'GENERATE WALLETS', icon: <Plus className="w-4 h-4" /> },
              { id: 'treasury', label: 'TREASURY ADVISOR', icon: <Shield className="w-4 h-4" /> },
              { id: 'investment', label: 'INVESTMENT ADVISOR', icon: <ArrowRightLeft className="w-4 h-4" /> },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-2 px-4 py-3 text-xs font-semibold tracking-wider transition-all border-b-2 ${
                  activeTab === tab.id
                    ? 'text-[#7c3aed] border-[#7c3aed] bg-[#7c3aed]/5'
                    : 'text-gray-500 border-transparent hover:text-gray-300'
                }`}
              >
                {tab.icon}
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-[1600px] mx-auto p-6">
        {/* WALLET OVERVIEW */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-12 gap-6">
            {/* Wallet List */}
            <div className="col-span-4 space-y-3">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-bold text-gray-500 uppercase tracking-wider">Your Wallets ({wallets.length})</h3>
                <button
                  onClick={() => setShowCreateModal(true)}
                  className="flex items-center gap-1 px-3 py-1.5 bg-[#7c3aed] hover:bg-[#6d28d9] text-white text-xs rounded transition-all"
                >
                  <Plus className="w-3 h-3" />
                  NEW
                </button>
              </div>

              {wallets.map((wallet) => (
                <button
                  key={wallet.id}
                  onClick={() => setSelectedWallet(wallet.id)}
                  className={`w-full p-4 rounded-lg border text-left transition-all ${
                    selectedWallet === wallet.id
                      ? 'bg-[#7c3aed]/10 border-[#7c3aed]'
                      : 'bg-[#1a1525]/50 border-gray-800 hover:border-gray-700'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      {getChainIcon(wallet.chain)}
                      <span className="font-semibold text-sm">{wallet.name}</span>
                    </div>
                    <span className={`w-2 h-2 rounded-full ${wallet.status === 'active' ? 'bg-green-500' : 'bg-gray-500'}`} />
                  </div>
                  <div className="text-xs text-gray-500 font-mono mb-2">
                    {wallet.address.slice(0, 8)}...{wallet.address.slice(-6)}
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-bold">{wallet.balance}</span>
                    <span className="text-xs text-green-400">{wallet.usdValue}</span>
                  </div>
                </button>
              ))}
            </div>

            {/* Selected Wallet Details */}
            <div className="col-span-8">
              {currentWallet && (
                <div className="space-y-4">
                  {/* Wallet Header */}
                  <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
                    <div className="flex items-center justify-between mb-6">
                      <div className="flex items-center gap-4">
                        <div className="w-14 h-14 bg-[#7c3aed]/10 rounded-xl flex items-center justify-center border border-[#7c3aed]/30">
                          {getChainIcon(currentWallet.chain)}
                        </div>
                        <div>
                          <h2 className="text-xl font-bold">{currentWallet.name}</h2>
                          <div className="flex items-center gap-2 text-sm text-gray-500">
                            <span className="px-2 py-0.5 bg-gray-800 rounded text-xs uppercase">{currentWallet.chain}</span>
                            <span className="px-2 py-0.5 bg-gray-800 rounded text-xs uppercase">{currentWallet.purpose}</span>
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-3xl font-bold text-white">{currentWallet.balance}</div>
                        <div className="text-green-400">{currentWallet.usdValue}</div>
                      </div>
                    </div>

                    {/* Address & Keys */}
                    <div className="grid grid-cols-2 gap-4 mb-4">
                      <div className="bg-[#0a0812] rounded-lg p-4 border border-gray-800">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-xs text-gray-500 uppercase">Public Address</span>
                          <button onClick={() => copyToClipboard(currentWallet.address)} className="text-[#7c3aed] hover:text-white">
                            <Copy className="w-4 h-4" />
                          </button>
                        </div>
                        <div className="text-sm font-mono text-gray-300 break-all">{currentWallet.address}</div>
                      </div>

                      <div className="bg-[#0a0812] rounded-lg p-4 border border-gray-800">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-xs text-gray-500 uppercase flex items-center gap-1">
                            <Lock className="w-3 h-3" />
                            Private Key
                          </span>
                          <div className="flex items-center gap-2">
                            <button onClick={() => setShowPrivateKey(!showPrivateKey)} className="text-gray-500 hover:text-white">
                              {showPrivateKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                            </button>
                            <button onClick={() => copyToClipboard(currentWallet.privateKey)} className="text-[#7c3aed] hover:text-white">
                              <Copy className="w-4 h-4" />
                            </button>
                          </div>
                        </div>
                        <div className="text-sm font-mono text-gray-300 break-all">
                          {showPrivateKey ? currentWallet.privateKey : '••••••••••••••••••••••••••••••••'}
                        </div>
                      </div>
                    </div>

                    {/* Security Info */}
                    <div className="flex items-center gap-4">
                      <div className="flex items-center gap-2 px-3 py-1.5 bg-gray-800 rounded text-xs">
                        <Shield className="w-4 h-4 text-[#7c3aed]" />
                        <span className="uppercase">{currentWallet.securityLevel}</span>
                      </div>
                      {currentWallet.requiresApproval && (
                        <div className="flex items-center gap-2 px-3 py-1.5 bg-yellow-500/10 border border-yellow-500/30 rounded text-xs text-yellow-400">
                          <Lock className="w-4 h-4" />
                          <span>APPROVAL REQUIRED</span>
                        </div>
                      )}
                      <div className="text-xs text-gray-500">Last used: {currentWallet.lastUsed}</div>
                    </div>
                  </div>

                  {/* Quick Actions */}
                  <div className="grid grid-cols-4 gap-3">
                    <button className="flex items-center justify-center gap-2 p-3 bg-[#7c3aed]/10 border border-[#7c3aed]/30 rounded-lg text-[#7c3aed] hover:bg-[#7c3aed]/20 transition-all">
                      <Send className="w-4 h-4" />
                      <span className="text-sm font-semibold">SEND</span>
                    </button>
                    <button className="flex items-center justify-center gap-2 p-3 bg-green-500/10 border border-green-500/30 rounded-lg text-green-400 hover:bg-green-500/20 transition-all">
                      <ArrowRightLeft className="w-4 h-4" />
                      <span className="text-sm font-semibold">RECEIVE</span>
                    </button>
                    <button className="flex items-center justify-center gap-2 p-3 bg-gray-800 border border-gray-700 rounded-lg text-gray-400 hover:bg-gray-700 transition-all">
                      <QrCode className="w-4 h-4" />
                      <span className="text-sm font-semibold">QR CODE</span>
                    </button>
                    <button className="flex items-center justify-center gap-2 p-3 bg-gray-800 border border-gray-700 rounded-lg text-gray-400 hover:bg-gray-700 transition-all">
                      <Download className="w-4 h-4" />
                      <span className="text-sm font-semibold">EXPORT</span>
                    </button>
                  </div>

                  {/* Transaction History */}
                  <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
                    <h3 className="text-sm font-bold text-gray-500 uppercase tracking-wider mb-4">Recent Transactions</h3>
                    <div className="text-center py-8 text-gray-500">
                      <Database className="w-12 h-12 mx-auto mb-2 opacity-50" />
                      <p>Connect to blockchain API to load transaction history</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* GENERATE WALLETS */}
        {activeTab === 'generate' && (
          <div className="max-w-2xl mx-auto">
            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-8">
              <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
                <Key className="w-6 h-6 text-[#7c3aed]" />
                Generate New Wallet
              </h2>

              <div className="space-y-6">
                <div>
                  <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Wallet Name</label>
                  <input
                    type="text"
                    value={newWalletForm.name}
                    onChange={(e) => setNewWalletForm({...newWalletForm, name: e.target.value})}
                    placeholder="e.g., Arbitrum Operations"
                    className="w-full px-4 py-3 bg-[#0a0812] border border-gray-800 rounded-lg text-white placeholder-gray-600 focus:border-[#7c3aed] focus:outline-none transition-all"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Blockchain</label>
                  <div className="grid grid-cols-4 gap-3">
                    {chains.map((chain) => (
                      <button
                        key={chain.id}
                        onClick={() => setNewWalletForm({...newWalletForm, chain: chain.id})}
                        className={`p-3 rounded-lg border text-center transition-all ${
                          newWalletForm.chain === chain.id
                            ? 'bg-[#7c3aed]/10 border-[#7c3aed]'
                            : 'bg-[#0a0812] border-gray-800 hover:border-gray-700'
                        }`}
                      >
                        <div className="flex justify-center mb-1">{chain.icon}</div>
                        <div className="text-xs font-semibold">{chain.name}</div>
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Purpose</label>
                  <select
                    value={newWalletForm.purpose}
                    onChange={(e) => setNewWalletForm({...newWalletForm, purpose: e.target.value})}
                    className="w-full px-4 py-3 bg-[#0a0812] border border-gray-800 rounded-lg text-white focus:border-[#7c3aed] focus:outline-none transition-all"
                  >
                    <option value="treasury">Treasury</option>
                    <option value="operations">Operations</option>
                    <option value="investment">Investment</option>
                    <option value="trading">Trading</option>
                    <option value="development">Development</option>
                    <option value="marketing">Marketing</option>
                    <option value="rewards">Rewards/Staking</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Security Level</label>
                  <div className="space-y-2">
                    {[
                      { id: 'standard', label: 'Standard', desc: 'Single signature, software wallet' },
                      { id: 'multisig', label: 'Multi-Signature', desc: 'Requires multiple approvals (recommended for treasury)' },
                      { id: 'hardware', label: 'Hardware Wallet', desc: 'Ledger/Trezor integration' },
                      { id: 'cold', label: 'Cold Storage', desc: 'Air-gapped, maximum security' },
                    ].map((level) => (
                      <button
                        key={level.id}
                        onClick={() => setNewWalletForm({...newWalletForm, securityLevel: level.id})}
                        className={`w-full p-3 rounded-lg border text-left transition-all ${
                          newWalletForm.securityLevel === level.id
                            ? 'bg-[#7c3aed]/10 border-[#7c3aed]'
                            : 'bg-[#0a0812] border-gray-800 hover:border-gray-700'
                        }`}
                      >
                        <div className="font-semibold text-sm">{level.label}</div>
                        <div className="text-xs text-gray-500">{level.desc}</div>
                      </button>
                    ))}
                  </div>
                </div>

                <div className="pt-4 border-t border-gray-800">
                  <div className="flex items-start gap-3 p-3 bg-yellow-500/10 border border-yellow-500/30 rounded-lg mb-4">
                    <AlertTriangle className="w-5 h-5 text-yellow-400 flex-shrink-0 mt-0.5" />
                    <div className="text-sm text-yellow-400">
                      <strong>Important:</strong> Store your private key securely. Lost keys cannot be recovered. Consider using a hardware wallet for large amounts.
                    </div>
                  </div>

                  <button
                    onClick={generateWallet}
                    className="w-full py-4 bg-[#7c3aed] hover:bg-[#6d28d9] text-white font-bold rounded-lg transition-all flex items-center justify-center gap-2"
                  >
                    <Key className="w-5 h-5" />
                    GENERATE WALLET
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TREASURY ADVISOR */}
        {activeTab === 'treasury' && (
          <div className="space-y-6">
            <div className="grid grid-cols-3 gap-4">
              <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-5">
                <div className="text-xs text-gray-500 uppercase mb-2">Monthly Revenue</div>
                <div className="text-2xl font-bold text-green-400">$125,000</div>
                <div className="text-xs text-gray-500 mt-1">+15% vs last month</div>
              </div>
              <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-5">
                <div className="text-xs text-gray-500 uppercase mb-2">Operating Expenses</div>
                <div className="text-2xl font-bold text-red-400">$42,500</div>
                <div className="text-xs text-gray-500 mt-1">34% of revenue</div>
              </div>
              <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-5">
                <div className="text-xs text-gray-500 uppercase mb-2">Net Treasury Growth</div>
                <div className="text-2xl font-bold text-[#7c3aed]">$82,500</div>
                <div className="text-xs text-gray-500 mt-1">66% margin</div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                <BrainIcon className="w-5 h-5 text-[#7c3aed]" />
                AI Treasury Recommendations
              </h3>
              <div className="space-y-4">
                <div className="p-4 bg-[#0a0812] rounded-lg border-l-2 border-green-500">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-semibold text-green-400">Diversify Stablecoin Holdings</span>
                    <span className="text-xs text-gray-500">High Confidence</span>
                  </div>
                  <p className="text-sm text-gray-400">Current exposure: 85% USDC. Recommend splitting 50% USDC, 25% USDT, 25% DAI to reduce single-point-of-failure risk.</p>
                </div>
                <div className="p-4 bg-[#0a0812] rounded-lg border-l-2 border-yellow-500">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-semibold text-yellow-400">Increase Staking Rewards Pool</span>
                    <span className="text-xs text-gray-500">Medium Confidence</span>
                  </div>
                  <p className="text-sm text-gray-400">Churn rate increased 12%. Recommend increasing staking APY from 15% to 18% to improve retention.</p>
                </div>
                <div className="p-4 bg-[#0a0812] rounded-lg border-l-2 border-[#7c3aed]">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-semibold text-[#7c3aed]">Establish 6-Month Runway Reserve</span>
                    <span className="text-xs text-gray-500">Strategic</span>
                  </div>
                  <p className="text-sm text-gray-400">Current runway: 3.2 months. Allocate $255K to cold storage for operational security during market downturns.</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* INVESTMENT ADVISOR */}
        {activeTab === 'investment' && (
          <div className="space-y-6">
            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                <TargetIcon className="w-5 h-5 text-[#7c3aed]" />
                AI Investment Analysis
              </h3>
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="p-4 bg-[#0a0812] rounded-lg">
                  <div className="text-xs text-gray-500 uppercase mb-2">Available for Investment</div>
                  <div className="text-2xl font-bold text-white">$450,000</div>
                  <div className="text-xs text-gray-500">10% of treasury</div>
                </div>
                <div className="p-4 bg-[#0a0812] rounded-lg">
                  <div className="text-xs text-gray-500 uppercase mb-2">Current Investments</div>
                  <div className="text-2xl font-bold text-[#7c3aed]">3 Active</div>
                  <div className="text-xs text-gray-500">$125,000 deployed</div>
                </div>
              </div>

              <h4 className="text-sm font-bold text-gray-500 uppercase tracking-wider mb-3">Opportunities Scored by AI</h4>
              <div className="space-y-3">
                <div className="p-4 bg-[#0a0812] rounded-lg border border-gray-800">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Hexagon className="w-5 h-5 text-blue-400" />
                      <span className="font-semibold">ETH Staking (Lido)</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-1 bg-green-500/20 text-green-400 text-xs rounded">Score: 94/100</span>
                      <button className="px-3 py-1.5 bg-[#7c3aed] text-white text-xs rounded hover:bg-[#6d28d9] transition-all">
                        ANALYZE
                      </button>
                    </div>
                  </div>
                  <p className="text-sm text-gray-400">Low-risk yield opportunity. 3.8% APY on liquid staking. High liquidity, established protocol.</p>
                </div>

                <div className="p-4 bg-[#0a0812] rounded-lg border border-gray-800">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Layers className="w-5 h-5 text-purple-400" />
                      <span className="font-semibold">Base Ecosystem Grant</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-1 bg-yellow-500/20 text-yellow-400 text-xs rounded">Score: 78/100</span>
                      <button className="px-3 py-1.5 bg-[#7c3aed] text-white text-xs rounded hover:bg-[#6d28d9] transition-all">
                        ANALYZE
                      </button>
                    </div>
                  </div>
                  <p className="text-sm text-gray-400">Strategic investment in Base chain projects. Potential partnership benefits + financial returns.</p>
                </div>

                <div className="p-4 bg-[#0a0812] rounded-lg border border-gray-800">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Database className="w-5 h-5 text-green-400" />
                      <span className="font-semibold">AI Infrastructure Tokens</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-1 bg-orange-500/20 text-orange-400 text-xs rounded">Score: 65/100</span>
                      <button className="px-3 py-1.5 bg-[#7c3aed] text-white text-xs rounded hover:bg-[#6d28d9] transition-all">
                        ANALYZE
                      </button>
                    </div>
                  </div>
                  <p className="text-sm text-gray-400">Moderate risk. Aligns with RMI AI narrative but volatile sector. Recommend small position (2-3%).</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Create Wallet Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-[#1a1525] border border-gray-800 rounded-xl p-6 max-w-md w-full">
            <h3 className="text-lg font-bold mb-4">Create New Wallet?</h3>
            <p className="text-sm text-gray-400 mb-6">
              You are about to generate a new {chains.find(c => c.id === newWalletForm.chain)?.name} wallet for {newWalletForm.purpose} purposes.
            </p>
            <div className="flex gap-3">
              <button
                onClick={() => setShowCreateModal(false)}
                className="flex-1 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm hover:bg-gray-700 transition-all"
              >
                CANCEL
              </button>
              <button
                onClick={generateWallet}
                className="flex-1 py-2 bg-[#7c3aed] text-white rounded-lg text-sm hover:bg-[#6d28d9] transition-all"
              >
                GENERATE
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Icon components
const SunIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
  </svg>
);

const TriangleIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
  </svg>
);

const BrainIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
  </svg>
);

const TargetIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

export default WalletManager;
