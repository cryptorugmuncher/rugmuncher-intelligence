import React, { useState } from 'react';
import {
  FileCode,
  Rocket,
  CheckCircle,
  AlertTriangle,
  Copy,
  Download,
  Upload,
  Settings,
  Code,
  Layers,
  Zap,
  Globe,
  Wallet,
  ChevronDown,
  ChevronUp,
  Plus,
  Trash2,
  Edit3,
  RefreshCw,
  ExternalLink,
  Terminal,
  Shield,
  Lock,
  Unlock,
  History,
  Search,
  Filter,
  MoreHorizontal,
  X,
  Save,
  Play,
  Eye,
  EyeOff,
  Coins,
  Hexagon,
  Box,
  Cpu,
  Database,
  GitBranch,
  Check,
  AlertCircle,
  Info,
  Clock,
  TrendingUp,
  DollarSign,
  Users
} from 'lucide-react';

type Chain = 'ethereum' | 'base' | 'arbitrum' | 'optimism' | 'polygon' | 'bsc' | 'avalanche' | 'solana';
type ContractType = 'token_erc20' | 'nft_erc721' | 'multisig' | 'vesting' | 'staking' | 'governance' | 'custom';

interface Deployment {
  id: string;
  name: string;
  chain: Chain;
  contractType: ContractType;
  address: string;
  deployer: string;
  timestamp: string;
  txHash: string;
  status: 'deploying' | 'success' | 'failed' | 'verified';
  gasUsed: string;
  gasCost: string;
  verified: boolean;
  abi: any;
  sourceCode: string;
}

interface ContractTemplate {
  id: string;
  name: string;
  type: ContractType;
  description: string;
  chains: Chain[];
  features: string[];
  estimatedGas: string;
  complexity: 'simple' | 'medium' | 'complex';
}

const ContractDeployer: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'deploy' | 'templates' | 'history' | 'verify'>('deploy');
  const [selectedChain, setSelectedChain] = useState<Chain>('ethereum');
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null);

  // Deployment History
  const [deployments, setDeployments] = useState<Deployment[]>([
    {
      id: 'd1',
      name: '$CRM V2 Token',
      chain: 'base',
      contractType: 'token_erc20',
      address: '0x1234567890abcdef1234567890abcdef12345678',
      deployer: '0x742d...C0E',
      timestamp: '2026-04-14 10:30',
      txHash: '0xabc123def45678901234567890abcdef1234567890abcdef1234567890abcdef',
      status: 'verified',
      gasUsed: '2,456,789',
      gasCost: '0.024 ETH',
      verified: true,
      abi: {},
      sourceCode: ''
    },
    {
      id: 'd2',
      name: 'Test NFT Collection',
      chain: 'ethereum',
      contractType: 'nft_erc721',
      address: '0xabcdef1234567890abcdef1234567890abcdef12',
      deployer: '0x742d...C0E',
      timestamp: '2026-04-13 16:45',
      txHash: '0xdef789abc12345678901234567890abcdef1234567890abcdef1234567890abc',
      status: 'success',
      gasUsed: '3,123,456',
      gasCost: '0.031 ETH',
      verified: false,
      abi: {},
      sourceCode: ''
    },
    {
      id: 'd3',
      name: 'Treasury Multi-Sig',
      chain: 'ethereum',
      contractType: 'multisig',
      address: '0x7890abcdef1234567890abcdef1234567890abcd',
      deployer: '0x742d...C0E',
      timestamp: '2026-04-12 09:15',
      txHash: '0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1',
      status: 'verified',
      gasUsed: '1,890,234',
      gasCost: '0.019 ETH',
      verified: true,
      abi: {},
      sourceCode: ''
    }
  ]);

  // Contract Templates
  const [templates] = useState<ContractTemplate[]>([
    {
      id: 't1',
      name: 'ERC-20 Token',
      type: 'token_erc20',
      description: 'Standard ERC-20 token with minting, burning, and pause functionality',
      chains: ['ethereum', 'base', 'arbitrum', 'optimism', 'polygon', 'bsc', 'avalanche'],
      features: ['Mintable', 'Burnable', 'Pausable', 'Capped Supply', 'Access Control'],
      estimatedGas: '~2,000,000',
      complexity: 'simple'
    },
    {
      id: 't2',
      name: 'ERC-721 NFT',
      type: 'nft_erc721',
      description: 'NFT collection with metadata, royalties, and minting controls',
      chains: ['ethereum', 'base', 'arbitrum', 'polygon', 'bsc'],
      features: ['Mintable', 'Burnable', 'Royalty Support', 'Reveal Mechanism', 'Whitelist'],
      estimatedGas: '~3,500,000',
      complexity: 'medium'
    },
    {
      id: 't3',
      name: 'Multi-Sig Wallet',
      type: 'multisig',
      description: 'Gnosis-style multi-signature wallet with threshold signatures',
      chains: ['ethereum', 'base', 'arbitrum', 'optimism', 'polygon'],
      features: ['N-of-M Signatures', 'Transaction Queue', 'Daily Limits', 'Recovery'],
      estimatedGas: '~4,000,000',
      complexity: 'complex'
    },
    {
      id: 't4',
      name: 'Token Vesting',
      type: 'vesting',
      description: 'Linear and cliff vesting schedules for team and investor tokens',
      chains: ['ethereum', 'base', 'arbitrum', 'polygon'],
      features: ['Linear Vesting', 'Cliff Vesting', 'Revocable', 'Multiple Beneficiaries'],
      estimatedGas: '~1,800,000',
      complexity: 'medium'
    },
    {
      id: 't5',
      name: 'Staking Pool',
      type: 'staking',
      description: 'Flexible staking with reward distribution and lock periods',
      chains: ['ethereum', 'base', 'polygon', 'bsc'],
      features: ['Flexible Staking', 'Fixed Terms', 'Auto-Compound', 'Emergency Withdraw'],
      estimatedGas: '~2,500,000',
      complexity: 'medium'
    },
    {
      id: 't6',
      name: 'DAO Governance',
      type: 'governance',
      description: 'OpenZeppelin Governor with voting power and proposal execution',
      chains: ['ethereum', 'base', 'arbitrum', 'polygon'],
      features: ['Proposal Creation', 'Voting Period', 'Timelock', 'Delegation'],
      estimatedGas: '~5,000,000',
      complexity: 'complex'
    }
  ]);

  // Deployment Form State
  const [deploymentConfig, setDeploymentConfig] = useState({
    name: '',
    symbol: '',
    decimals: '18',
    totalSupply: '1000000000',
    mintable: true,
    burnable: true,
    pausable: false,
    maxSupply: '',
    owner: '',
    recipients: [{ address: '', amount: '' }]
  });

  // UI State
  const [showDeployModal, setShowDeployModal] = useState(false);
  const [isDeploying, setIsDeploying] = useState(false);
  const [deployProgress, setDeployProgress] = useState(0);

  const chainConfig: Record<Chain, { name: string; icon: string; color: string; currency: string; testnet: string }> = {
    ethereum: { name: 'Ethereum', icon: 'eth', color: '#627EEA', currency: 'ETH', testnet: 'Sepolia' },
    base: { name: 'Base', icon: 'base', color: '#0052FF', currency: 'ETH', testnet: 'Base Sepolia' },
    arbitrum: { name: 'Arbitrum', icon: 'arb', color: '#28A0F0', currency: 'ETH', testnet: 'Arbitrum Sepolia' },
    optimism: { name: 'Optimism', icon: 'op', color: '#FF0420', currency: 'ETH', testnet: 'OP Sepolia' },
    polygon: { name: 'Polygon', icon: 'matic', color: '#8247E5', currency: 'MATIC', testnet: 'Mumbai' },
    bsc: { name: 'BSC', icon: 'bnb', color: '#F3BA2F', currency: 'BNB', testnet: 'BSC Testnet' },
    avalanche: { name: 'Avalanche', icon: 'avax', color: '#E84142', currency: 'AVAX', testnet: 'Fuji' },
    solana: { name: 'Solana', icon: 'sol', color: '#14F195', currency: 'SOL', testnet: 'Devnet' }
  };

  const handleDeploy = () => {
    setShowDeployModal(false);
    setIsDeploying(true);
    setDeployProgress(0);

    // Simulate deployment
    const interval = setInterval(() => {
      setDeployProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          setIsDeploying(false);
          return 100;
        }
        return prev + 10;
      });
    }, 500);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success': return 'bg-green-500/20 text-green-400';
      case 'verified': return 'bg-blue-500/20 text-blue-400';
      case 'deploying': return 'bg-yellow-500/20 text-yellow-400';
      case 'failed': return 'bg-red-500/20 text-red-400';
      default: return 'bg-gray-700 text-gray-400';
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0812] text-gray-100 font-mono selection:bg-[#7c3aed]/30">
      {/* Header */}
      <div className="bg-gradient-to-r from-[#0f0c1d] via-[#1a1525] to-[#0f0c1d] border-b border-[#7c3aed]/30">
        <div className="max-w-[1600px] mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-[#7c3aed]/20 rounded-full flex items-center justify-center">
                <Rocket className="w-5 h-5 text-[#7c3aed]" />
              </div>
              <div>
                <h1 className="text-xl font-bold tracking-wider">
                  CONTRACT <span className="text-[#7c3aed]">DEPLOYER</span>
                </h1>
                <p className="text-xs text-gray-500 tracking-[0.2em]">SMART CONTRACT FACTORY & DEPLOYMENT</p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 px-3 py-1.5 bg-[#7c3aed]/10 border border-[#7c3aed]/30 rounded">
                <CheckCircle className="w-4 h-4 text-[#7c3aed]" />
                <span className="text-sm text-[#7c3aed]">{deployments.length} Contracts Deployed</span>
              </div>
              <button
                onClick={() => setShowDeployModal(true)}
                className="flex items-center gap-2 px-4 py-2 bg-[#7c3aed] text-white rounded transition-all"
              >
                <Rocket className="w-4 h-4" />
                DEPLOY NOW
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-[1600px] mx-auto p-6 space-y-6">
        {/* Chain Selector */}
        <div className="flex items-center gap-2 overflow-x-auto pb-2">
          {(Object.keys(chainConfig) as Chain[]).map((chain) => (
            <button
              key={chain}
              onClick={() => setSelectedChain(chain)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg border transition-all whitespace-nowrap ${
                selectedChain === chain
                  ? 'bg-[#7c3aed]/20 border-[#7c3aed] text-[#7c3aed]'
                  : 'bg-[#1a1525] border-gray-800 hover:border-gray-700'
              }`}
            >
              <div
                className="w-4 h-4 rounded-full"
                style={{ backgroundColor: chainConfig[chain].color }}
              />
              <span className="text-sm">{chainConfig[chain].name}</span>
            </button>
          ))}
        </div>

        {/* Deployment Progress */}
        {isDeploying && (
          <div className="bg-gradient-to-r from-[#7c3aed]/20 via-[#1a1525] to-[#0f0c1d] border border-[#7c3aed]/30 rounded-lg p-4">
            <div className="flex items-center gap-3">
              <RefreshCw className="w-6 h-6 text-[#7c3aed] animate-spin" />
              <div className="flex-1">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-semibold">Deploying to {chainConfig[selectedChain].name}...</span>
                  <span className="text-[#7c3aed]">{deployProgress}%</span>
                </div>
                <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-[#7c3aed] rounded-full transition-all"
                    style={{ width: `${deployProgress}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Navigation */}
        <div className="flex items-center gap-1 border-b border-gray-800">
          {[
            { id: 'deploy', label: 'DEPLOY CONTRACT', icon: <Rocket className="w-4 h-4" /> },
            { id: 'templates', label: 'TEMPLATES', icon: <Layers className="w-4 h-4" /> },
            { id: 'history', label: 'DEPLOYMENT HISTORY', icon: <History className="w-4 h-4" /> },
            { id: 'verify', label: 'VERIFY SOURCE', icon: <Shield className="w-4 h-4" /> },
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

        {/* Deploy Tab */}
        {activeTab === 'deploy' && (
          <div className="grid grid-cols-3 gap-6">
            <div className="col-span-2 bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-bold mb-4">Token Configuration</h3>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm text-gray-500 mb-1">Token Name</label>
                    <input
                      type="text"
                      value={deploymentConfig.name}
                      onChange={(e) => setDeploymentConfig({ ...deploymentConfig, name: e.target.value })}
                      placeholder="e.g., Rug Munch Intel"
                      className="w-full px-3 py-2 bg-[#0a0812] border border-gray-800 rounded"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-500 mb-1">Token Symbol</label>
                    <input
                      type="text"
                      value={deploymentConfig.symbol}
                      onChange={(e) => setDeploymentConfig({ ...deploymentConfig, symbol: e.target.value })}
                      placeholder="e.g., RMI"
                      className="w-full px-3 py-2 bg-[#0a0812] border border-gray-800 rounded"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm text-gray-500 mb-1">Decimals</label>
                    <input
                      type="number"
                      value={deploymentConfig.decimals}
                      onChange={(e) => setDeploymentConfig({ ...deploymentConfig, decimals: e.target.value })}
                      className="w-full px-3 py-2 bg-[#0a0812] border border-gray-800 rounded"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-500 mb-1">Total Supply</label>
                    <input
                      type="text"
                      value={deploymentConfig.totalSupply}
                      onChange={(e) => setDeploymentConfig({ ...deploymentConfig, totalSupply: e.target.value })}
                      placeholder="1000000000"
                      className="w-full px-3 py-2 bg-[#0a0812] border border-gray-800 rounded"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm text-gray-500 mb-1">Owner Address</label>
                  <input
                    type="text"
                    value={deploymentConfig.owner}
                    onChange={(e) => setDeploymentConfig({ ...deploymentConfig, owner: e.target.value })}
                    placeholder="0x..."
                    className="w-full px-3 py-2 bg-[#0a0812] border border-gray-800 rounded font-mono"
                  />
                </div>

                <div className="space-y-3">
                  <label className="block text-sm text-gray-500">Token Features</label>
                  <div className="grid grid-cols-3 gap-4">
                    <label className="flex items-center gap-2 p-3 bg-[#0a0812] rounded cursor-pointer">
                      <input
                        type="checkbox"
                        checked={deploymentConfig.mintable}
                        onChange={(e) => setDeploymentConfig({ ...deploymentConfig, mintable: e.target.checked })}
                        className="w-4 h-4 rounded border-gray-700 bg-gray-800 text-[#7c3aed]"
                      />
                      <span className="text-sm">Mintable</span>
                    </label>
                    <label className="flex items-center gap-2 p-3 bg-[#0a0812] rounded cursor-pointer">
                      <input
                        type="checkbox"
                        checked={deploymentConfig.burnable}
                        onChange={(e) => setDeploymentConfig({ ...deploymentConfig, burnable: e.target.checked })}
                        className="w-4 h-4 rounded border-gray-700 bg-gray-800 text-[#7c3aed]"
                      />
                      <span className="text-sm">Burnable</span>
                    </label>
                    <label className="flex items-center gap-2 p-3 bg-[#0a0812] rounded cursor-pointer">
                      <input
                        type="checkbox"
                        checked={deploymentConfig.pausable}
                        onChange={(e) => setDeploymentConfig({ ...deploymentConfig, pausable: e.target.checked })}
                        className="w-4 h-4 rounded border-gray-700 bg-gray-800 text-[#7c3aed]"
                      />
                      <span className="text-sm">Pausable</span>
                    </label>
                  </div>
                </div>

                <div>
                  <label className="block text-sm text-gray-500 mb-1">Max Supply (optional)</label>
                  <input
                    type="text"
                    value={deploymentConfig.maxSupply}
                    onChange={(e) => setDeploymentConfig({ ...deploymentConfig, maxSupply: e.target.value })}
                    placeholder="Leave empty for unlimited"
                    className="w-full px-3 py-2 bg-[#0a0812] border border-gray-800 rounded"
                  />
                </div>

                <div className="pt-4 border-t border-gray-800">
                  <div className="flex items-center justify-between mb-4">
                    <label className="text-sm text-gray-500">Initial Distribution</label>
                    <button
                      onClick={() => setDeploymentConfig({
                        ...deploymentConfig,
                        recipients: [...deploymentConfig.recipients, { address: '', amount: '' }]
                      })}
                      className="text-xs text-[#7c3aed] hover:underline"
                    >
                      + ADD RECIPIENT
                    </button>
                  </div>
                  {deploymentConfig.recipients.map((recipient, idx) => (
                    <div key={idx} className="grid grid-cols-2 gap-4 mb-3">
                      <input
                        type="text"
                        placeholder="Wallet Address"
                        value={recipient.address}
                        className="px-3 py-2 bg-[#0a0812] border border-gray-800 rounded font-mono text-sm"
                      />
                      <input
                        type="text"
                        placeholder="Amount"
                        value={recipient.amount}
                        className="px-3 py-2 bg-[#0a0812] border border-gray-800 rounded text-sm"
                      />
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-5">
                <h4 className="font-semibold mb-4">Deployment Preview</h4>
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-500">Network:</span>
                    <span>{chainConfig[selectedChain].name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Contract Type:</span>
                    <span>ERC-20 Token</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Estimated Gas:</span>
                    <span>~2,000,000</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Gas Price:</span>
                    <span>20 gwei</span>
                  </div>
                  <div className="pt-3 border-t border-gray-800">
                    <div className="flex justify-between font-semibold">
                      <span>Est. Cost:</span>
                      <span>~0.04 {chainConfig[selectedChain].currency}</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-5">
                <h4 className="font-semibold mb-4">Security Checks</h4>
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-sm">
                    <CheckCircle className="w-4 h-4 text-green-400" />
                    <span>No reentrancy vulnerabilities</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <CheckCircle className="w-4 h-4 text-green-400" />
                    <span>Access controls verified</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <CheckCircle className="w-4 h-4 text-green-400" />
                    <span>Integer overflow protection</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <AlertTriangle className="w-4 h-4 text-yellow-400" />
                    <span>Consider adding timelock</span>
                  </div>
                </div>
              </div>

              <button
                onClick={handleDeploy}
                disabled={isDeploying}
                className="w-full py-3 bg-[#7c3aed] text-white rounded-lg font-semibold hover:bg-[#6d28d9] transition-all disabled:opacity-50"
              >
                <Rocket className="w-4 h-4 inline mr-2" />
                DEPLOY CONTRACT
              </button>

              <button className="w-full py-3 bg-gray-800 text-gray-400 rounded-lg hover:bg-gray-700 transition-all">
                <Code className="w-4 h-4 inline mr-2" />
                PREVIEW SOURCE
              </button>
            </div>
          </div>
        )}

        {/* Templates Tab */}
        {activeTab === 'templates' && (
          <div className="grid grid-cols-2 gap-4">
            {templates.map((template) => (
              <div
                key={template.id}
                className={`bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border rounded-lg p-5 cursor-pointer transition-all ${
                  selectedTemplate === template.id
                    ? 'border-[#7c3aed]'
                    : 'border-gray-800 hover:border-gray-700'
                }`}
                onClick={() => setSelectedTemplate(template.id)}
              >
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="font-bold">{template.name}</h3>
                    <p className="text-sm text-gray-500">{template.type.replace('_', ' ').toUpperCase()}</p>
                  </div>
                  <span className={`px-2 py-1 rounded text-[10px] ${
                    template.complexity === 'simple' ? 'bg-green-500/20 text-green-400' :
                    template.complexity === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
                    'bg-red-500/20 text-red-400'
                  }`}>
                    {template.complexity}
                  </span>
                </div>

                <p className="text-sm text-gray-400 mb-4">{template.description}</p>

                <div className="mb-4">
                  <div className="text-xs text-gray-500 mb-2">Supported Chains:</div>
                  <div className="flex flex-wrap gap-1">
                    {template.chains.map((chain) => (
                      <span key={chain} className="px-2 py-0.5 bg-gray-800 rounded text-[10px]">
                        {chainConfig[chain].name}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-500">Est. Gas: {template.estimatedGas}</span>
                  <button className="px-3 py-1.5 bg-[#7c3aed]/10 border border-[#7c3aed]/30 rounded text-[#7c3aed] hover:bg-[#7c3aed]/20 transition-all">
                    USE TEMPLATE
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* History Tab */}
        {activeTab === 'history' && (
          <div className="space-y-4">
            {deployments.map((deployment) => (
              <div key={deployment.id} className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-5">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <div className="flex items-center gap-3 mb-1">
                      <h3 className="font-bold">{deployment.name}</h3>
                      <span className={`px-2 py-0.5 rounded text-[10px] ${getStatusColor(deployment.status)}`}>
                        {deployment.status.toUpperCase()}
                      </span>
                      {deployment.verified && (
                        <span className="px-2 py-0.5 bg-blue-500/20 text-blue-400 rounded text-[10px]">
                          VERIFIED
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-500">{chainConfig[deployment.chain].name} • {deployment.timestamp}</p>
                  </div>
                  <div className="flex gap-2">
                    <button className="px-3 py-1.5 bg-[#7c3aed]/10 border border-[#7c3aed]/30 rounded text-xs text-[#7c3aed] hover:bg-[#7c3aed]/20 transition-all">
                      <Copy className="w-3 h-3 inline mr-1" />
                      COPY ABI
                    </button>
                    <button className="px-3 py-1.5 bg-gray-800 rounded text-xs text-gray-400 hover:bg-gray-700 transition-all">
                      <ExternalLink className="w-3 h-3 inline mr-1" />
                      VIEW
                    </button>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-4 mb-4">
                  <div className="p-3 bg-[#0a0812] rounded">
                    <div className="text-[10px] text-gray-500 mb-1">CONTRACT ADDRESS</div>
                    <div className="font-mono text-sm">{deployment.address}</div>
                  </div>
                  <div className="p-3 bg-[#0a0812] rounded">
                    <div className="text-[10px] text-gray-500 mb-1">DEPLOYER</div>
                    <div className="font-mono text-sm">{deployment.deployer}</div>
                  </div>
                  <div className="p-3 bg-[#0a0812] rounded">
                    <div className="text-[10px] text-gray-500 mb-1">TRANSACTION</div>
                    <div className="font-mono text-sm">{deployment.txHash.slice(0, 20)}...</div>
                  </div>
                </div>

                <div className="flex items-center gap-4 text-xs text-gray-500">
                  <span>Gas Used: {deployment.gasUsed}</span>
                  <span>Cost: {deployment.gasCost}</span>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Verify Tab */}
        {activeTab === 'verify' && (
          <div className="max-w-2xl mx-auto">
            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-bold mb-4">Verify Contract Source</h3>
              <p className="text-sm text-gray-400 mb-6">
                Verify your smart contract source code on {chainConfig[selectedChain].name} explorer for transparency and trust.
              </p>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm text-gray-500 mb-1">Contract Address</label>
                  <input
                    type="text"
                    placeholder="0x..."
                    className="w-full px-3 py-2 bg-[#0a0812] border border-gray-800 rounded font-mono"
                  />
                </div>

                <div>
                  <label className="block text-sm text-gray-500 mb-1">Compiler Version</label>
                  <select className="w-full px-3 py-2 bg-[#0a0812] border border-gray-800 rounded">
                    <option>v0.8.19+commit.7dd6d404</option>
                    <option>v0.8.18+commit.87f61d96</option>
                    <option>v0.8.17+commit.8df45f5f</option>
                    <option>v0.8.16+commit.07a7930e</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm text-gray-500 mb-1">Source Code</label>
                  <textarea
                    rows={10}
                    placeholder="Paste your Solidity source code here..."
                    className="w-full px-3 py-2 bg-[#0a0812] border border-gray-800 rounded font-mono text-sm"
                  />
                </div>

                <div className="flex items-center gap-2 p-3 bg-yellow-500/10 border border-yellow-500/30 rounded">
                  <Info className="w-4 h-4 text-yellow-400" />
                  <p className="text-xs text-yellow-400">
                    Make sure your source code matches the deployed bytecode exactly, including optimization settings.
                  </p>
                </div>

                <button className="w-full py-3 bg-[#7c3aed] text-white rounded-lg font-semibold hover:bg-[#6d28d9] transition-all">
                  <Shield className="w-4 h-4 inline mr-2" />
                  VERIFY & PUBLISH
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ContractDeployer;
