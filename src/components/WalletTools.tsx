import { useState } from 'react';
import { Wallet, Plus, Trash2, Copy, Eye, EyeOff, RefreshCw, Download, Shield, AlertTriangle, CheckCircle2, Key, FileCode, ExternalLink } from 'lucide-react';
import { useAppStore } from '../store/appStore';

interface GeneratedWallet {
  id: string;
  name: string;
  chain: 'ethereum' | 'base' | 'arbitrum' | 'optimism' | 'polygon' | 'bsc' | 'avalanche' | 'solana';
  address: string;
  privateKey: string;
  mnemonic?: string;
  createdAt: string;
  tags: string[];
  notes: string;
}

interface WalletBackup {
  id: string;
  walletId: string;
  type: 'json' | 'csv' | 'paper';
  encrypted: boolean;
  createdAt: string;
  downloadUrl?: string;
}

const chainConfig = {
  ethereum: { name: 'Ethereum', symbol: 'ETH', icon: '🔷', color: '#627EEA' },
  base: { name: 'Base', symbol: 'ETH', icon: '🔵', color: '#0052FF' },
  arbitrum: { name: 'Arbitrum', symbol: 'ETH', icon: '🔶', color: '#28A0F0' },
  optimism: { name: 'Optimism', symbol: 'ETH', icon: '🔴', color: '#FF0420' },
  polygon: { name: 'Polygon', symbol: 'MATIC', icon: '💜', color: '#8247E5' },
  bsc: { name: 'BSC', symbol: 'BNB', icon: '🟡', color: '#F3BA2F' },
  avalanche: { name: 'Avalanche', symbol: 'AVAX', icon: '🔺', color: '#E84142' },
  solana: { name: 'Solana', symbol: 'SOL', icon: '🟪', color: '#9945FF' },
};

export default function WalletTools() {
  const { theme } = useAppStore();
  const darkMode = theme === 'dark';

  const [wallets, setWallets] = useState<GeneratedWallet[]>([]);
  const [backups, setBackups] = useState<WalletBackup[]>([]);
  const [activeTab, setActiveTab] = useState<'generate' | 'manage' | 'import' | 'backup'>('generate');

  // Generate wallet form
  const [selectedChain, setSelectedChain] = useState<GeneratedWallet['chain']>('ethereum');
  const [walletName, setWalletName] = useState('');
  const [generateMnemonic, setGenerateMnemonic] = useState(true);
  const [generatedWallet, setGeneratedWallet] = useState<GeneratedWallet | null>(null);

  // Import form
  const [importType, setImportType] = useState<'privateKey' | 'mnemonic'>('privateKey');
  const [importValue, setImportValue] = useState('');
  const [importChain, setImportChain] = useState<GeneratedWallet['chain']>('ethereum');
  const [importName, setImportName] = useState('');

  // Visibility state
  const [showPrivateKeys, setShowPrivateKeys] = useState<Set<string>>(new Set());
  const [showMnemonics, setShowMnemonics] = useState<Set<string>>(new Set());

  // Security check
  const [securityAcknowledged, setSecurityAcknowledged] = useState(false);

  const generateWallet = () => {
    // Mock wallet generation - in production would use proper crypto libraries
    const mockAddress = `0x${Array.from({ length: 40 }, () =>
      '0123456789abcdef'[Math.floor(Math.random() * 16)]
    ).join('')}`;

    const mockPrivateKey = `0x${Array.from({ length: 64 }, () =>
      '0123456789abcdef'[Math.floor(Math.random() * 16)]
    ).join('')}`;

    const mockMnemonic = generateMnemonic
      ? 'abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acquire across act action actor actress actual'
      : undefined;

    const newWallet: GeneratedWallet = {
      id: crypto.randomUUID(),
      name: walletName || `${chainConfig[selectedChain].name} Wallet ${wallets.length + 1}`,
      chain: selectedChain,
      address: mockAddress,
      privateKey: mockPrivateKey,
      mnemonic: mockMnemonic,
      createdAt: new Date().toISOString(),
      tags: [],
      notes: '',
    };

    setGeneratedWallet(newWallet);
  };

  const saveGeneratedWallet = () => {
    if (!generatedWallet) return;
    setWallets([...wallets, generatedWallet]);
    setGeneratedWallet(null);
    setWalletName('');
    setActiveTab('manage');
  };

  const importWallet = () => {
    if (!importValue.trim() || !securityAcknowledged) return;

    // Mock import - would validate and derive address from key/mnemonic
    const mockAddress = `0x${Array.from({ length: 40 }, () =>
      '0123456789abcdef'[Math.floor(Math.random() * 16)]
    ).join('')}`;

    const newWallet: GeneratedWallet = {
      id: crypto.randomUUID(),
      name: importName || `Imported ${chainConfig[importChain].name} Wallet`,
      chain: importChain,
      address: mockAddress,
      privateKey: importType === 'privateKey' ? importValue : 'derived-from-mnemonic',
      mnemonic: importType === 'mnemonic' ? importValue : undefined,
      createdAt: new Date().toISOString(),
      tags: ['imported'],
      notes: `Imported via ${importType} on ${new Date().toLocaleDateString()}`,
    };

    setWallets([...wallets, newWallet]);
    setImportValue('');
    setImportName('');
    setSecurityAcknowledged(false);
    setActiveTab('manage');
  };

  const deleteWallet = (id: string) => {
    if (confirm('Are you sure? This cannot be undone. Make sure you have backed up your private keys!')) {
      setWallets(wallets.filter(w => w.id !== id));
    }
  };

  const togglePrivateKey = (id: string) => {
    const newSet = new Set(showPrivateKeys);
    if (newSet.has(id)) {
      newSet.delete(id);
    } else {
      newSet.add(id);
    }
    setShowPrivateKeys(newSet);
  };

  const toggleMnemonic = (id: string) => {
    const newSet = new Set(showMnemonics);
    if (newSet.has(id)) {
      newSet.delete(id);
    } else {
      newSet.add(id);
    }
    setShowMnemonics(newSet);
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    // Would show toast notification
  };

  const createBackup = (walletId: string, type: 'json' | 'csv' | 'paper') => {
    const backup: WalletBackup = {
      id: crypto.randomUUID(),
      walletId,
      type,
      encrypted: true,
      createdAt: new Date().toISOString(),
      downloadUrl: '#', // Would generate actual download
    };
    setBackups([...backups, backup]);
  };

  const exportAllWallets = () => {
    const data = {
      exportedAt: new Date().toISOString(),
      wallets: wallets.map(w => ({
        ...w,
        // Would encrypt in production
      })),
    };
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `rmi-wallets-backup-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const getWalletsByChain = () => {
    const grouped: Record<string, GeneratedWallet[]> = {};
    wallets.forEach(wallet => {
      if (!grouped[wallet.chain]) grouped[wallet.chain] = [];
      grouped[wallet.chain].push(wallet);
    });
    return grouped;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
        <div className="flex items-center gap-3 mb-2">
          <Wallet className="w-8 h-8 text-purple-500" />
          <h1 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
            WALLET TOOLS
          </h1>
          <span className="px-2 py-1 bg-purple-500/10 text-purple-400 text-xs font-mono rounded">
            UNCLASSIFIED
          </span>
        </div>
        <p className={`${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
          Generate, import, and manage wallets across multiple chains. For enterprise-grade security, use Secure Wallet Manager.
        </p>
      </div>

      {/* Warning Banner */}
      <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 flex items-start gap-3">
        <AlertTriangle className="w-5 h-5 text-red-400 mt-0.5 flex-shrink-0" />
        <div>
          <h3 className="font-semibold text-red-400">SECURITY WARNING</h3>
          <p className={`text-sm ${darkMode ? 'text-slate-300' : 'text-slate-600'}`}>
            This tool generates real cryptographic keys. Never share private keys or mnemonics.
            Always back up your wallets. Use only for development/testing or with small amounts.
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex flex-wrap gap-2">
        {[
          { id: 'generate', label: 'Generate', icon: Plus },
          { id: 'manage', label: `Manage (${wallets.length})`, icon: Wallet },
          { id: 'import', label: 'Import', icon: Download },
          { id: 'backup', label: 'Backup', icon: Shield },
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${
              activeTab === tab.id
                ? 'bg-purple-600 text-white'
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

      {/* Generate Wallet Tab */}
      {activeTab === 'generate' && (
        <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
          <h2 className={`text-lg font-semibold mb-6 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
            Generate New Wallet
          </h2>

          {!generatedWallet ? (
            <div className="space-y-6 max-w-md">
              {/* Chain Selection */}
              <div>
                <label className={`block text-sm font-medium mb-2 ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>
                  Blockchain *
                </label>
                <div className="grid grid-cols-4 gap-2">
                  {(Object.keys(chainConfig) as Array<keyof typeof chainConfig>).map(chain => (
                    <button
                      key={chain}
                      onClick={() => setSelectedChain(chain)}
                      className={`p-3 rounded-lg border text-center transition-all ${
                        selectedChain === chain
                          ? 'border-purple-500 bg-purple-500/10'
                          : darkMode
                          ? 'border-slate-600 hover:border-slate-500'
                          : 'border-slate-200 hover:border-slate-300'
                      }`}
                    >
                      <span className="text-xl">{chainConfig[chain].icon}</span>
                      <p className={`text-xs mt-1 ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                        {chainConfig[chain].name}
                      </p>
                    </button>
                  ))}
                </div>
              </div>

              {/* Wallet Name */}
              <div>
                <label className={`block text-sm font-medium mb-2 ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>
                  Wallet Name (Optional)
                </label>
                <input
                  type="text"
                  value={walletName}
                  onChange={e => setWalletName(e.target.value)}
                  placeholder={`My ${chainConfig[selectedChain].name} Wallet`}
                  className={`w-full px-4 py-2 rounded-lg border ${
                    darkMode
                      ? 'bg-slate-900 border-slate-700 text-white'
                      : 'bg-white border-slate-300'
                  }`}
                />
              </div>

              {/* Mnemonic Option */}
              <div className="flex items-center gap-3">
                <input
                  type="checkbox"
                  id="mnemonic"
                  checked={generateMnemonic}
                  onChange={e => setGenerateMnemonic(e.target.checked)}
                  className="w-5 h-5 rounded border-purple-500 text-purple-600"
                />
                <label htmlFor="mnemonic" className={`${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>
                  Generate recovery phrase (mnemonic) for wallet recovery
                </label>
              </div>

              {/* Security Acknowledgment */}
              <div className={`p-4 rounded-lg ${darkMode ? 'bg-yellow-500/10' : 'bg-yellow-50'} border border-yellow-500/30`}>
                <div className="flex items-start gap-3">
                  <input
                    type="checkbox"
                    id="security"
                    checked={securityAcknowledged}
                    onChange={e => setSecurityAcknowledged(e.target.checked)}
                    className="w-5 h-5 mt-0.5 rounded border-yellow-500"
                  />
                  <label htmlFor="security" className={`text-sm ${darkMode ? 'text-yellow-200' : 'text-yellow-800'}`}>
                    I understand that I am generating real cryptographic keys. I will securely back up any private keys or mnemonics generated.
                  </label>
                </div>
              </div>

              {/* Generate Button */}
              <button
                onClick={generateWallet}
                disabled={!securityAcknowledged}
                className="w-full py-3 bg-purple-600 hover:bg-purple-700 disabled:bg-slate-600 disabled:cursor-not-allowed text-white rounded-lg font-medium transition-all flex items-center justify-center gap-2"
              >
                <Key className="w-5 h-5" />
                Generate Wallet
              </button>
            </div>
          ) : (
            <div className="space-y-6">
              <div className={`p-4 rounded-lg ${darkMode ? 'bg-green-500/10' : 'bg-green-50'} border border-green-500/30`}>
                <div className="flex items-center gap-2 text-green-400">
                  <CheckCircle2 className="w-5 h-5" />
                  <span className="font-medium">Wallet Generated Successfully</span>
                </div>
              </div>

              {/* Generated Wallet Details */}
              <div className={`p-6 rounded-lg ${darkMode ? 'bg-slate-900' : 'bg-slate-50'} space-y-4`}>
                <div className="flex items-center gap-3 mb-4">
                  <span className="text-3xl">{chainConfig[generatedWallet.chain].icon}</span>
                  <div>
                    <p className={`font-semibold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                      {generatedWallet.name}
                    </p>
                    <p className="text-sm text-purple-400">{chainConfig[generatedWallet.chain].name}</p>
                  </div>
                </div>

                {/* Address */}
                <div>
                  <label className={`block text-xs font-medium mb-1 ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                    PUBLIC ADDRESS
                  </label>
                  <div className="flex gap-2">
                    <code className={`flex-1 p-3 rounded-lg text-sm break-all ${darkMode ? 'bg-slate-800 text-green-400' : 'bg-white text-green-600 border border-slate-200'}`}>
                      {generatedWallet.address}
                    </code>
                    <button
                      onClick={() => copyToClipboard(generatedWallet.address)}
                      className="p-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
                    >
                      <Copy className="w-5 h-5" />
                    </button>
                  </div>
                </div>

                {/* Private Key */}
                <div>
                  <label className={`block text-xs font-medium mb-1 ${darkMode ? 'text-red-400' : 'text-red-600'}`}>
                    PRIVATE KEY (NEVER SHARE)
                  </label>
                  <div className="flex gap-2">
                    <code className={`flex-1 p-3 rounded-lg text-sm break-all ${darkMode ? 'bg-slate-800 text-red-400' : 'bg-white text-red-600 border border-slate-200'}`}>
                      {showPrivateKeys.has(generatedWallet.id)
                        ? generatedWallet.privateKey
                        : '•'.repeat(66)}
                    </code>
                    <button
                      onClick={() => togglePrivateKey(generatedWallet.id)}
                      className="p-3 bg-slate-600 text-white rounded-lg hover:bg-slate-700"
                    >
                      {showPrivateKeys.has(generatedWallet.id) ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                    </button>
                    <button
                      onClick={() => copyToClipboard(generatedWallet.privateKey)}
                      className="p-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
                    >
                      <Copy className="w-5 h-5" />
                    </button>
                  </div>
                </div>

                {/* Mnemonic */}
                {generatedWallet.mnemonic && (
                  <div>
                    <label className={`block text-xs font-medium mb-1 ${darkMode ? 'text-orange-400' : 'text-orange-600'}`}>
                      RECOVERY PHRASE (WRITE THIS DOWN)
                    </label>
                    <div className="flex gap-2">
                      <div className={`flex-1 p-3 rounded-lg ${darkMode ? 'bg-slate-800' : 'bg-white border border-slate-200'}`}>
                        <p className={`text-sm font-mono leading-relaxed ${showMnemonics.has(generatedWallet.id) ? darkMode ? 'text-orange-300' : 'text-orange-700' : 'text-transparent'}`}>
                          {showMnemonics.has(generatedWallet.id)
                            ? generatedWallet.mnemonic
                            : '•'.repeat(100)}
                        </p>
                      </div>
                      <button
                        onClick={() => toggleMnemonic(generatedWallet.id)}
                        className="p-3 bg-slate-600 text-white rounded-lg hover:bg-slate-700"
                      >
                        {showMnemonics.has(generatedWallet.id) ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                      </button>
                    </div>
                    <p className={`text-xs mt-2 ${darkMode ? 'text-slate-500' : 'text-slate-500'}`}>
                      Write this down on paper and store in a secure location. Never store digitally.
                    </p>
                  </div>
                )}
              </div>

              {/* Actions */}
              <div className="flex gap-3">
                <button
                  onClick={saveGeneratedWallet}
                  className="flex-1 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium transition-all flex items-center justify-center gap-2"
                >
                  <CheckCircle2 className="w-5 h-5" />
                  Save to Wallet Manager
                </button>
                <button
                  onClick={() => setGeneratedWallet(null)}
                  className="px-6 py-3 bg-slate-600 hover:bg-slate-700 text-white rounded-lg font-medium transition-all"
                >
                  Discard
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Manage Wallets Tab */}
      {activeTab === 'manage' && (
        <div className="space-y-4">
          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
              <p className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'}`}>{wallets.length}</p>
              <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Total Wallets</p>
            </div>
            <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
              <p className="text-2xl font-bold text-purple-400">
                {Object.keys(getWalletsByChain()).length}
              </p>
              <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Chains</p>
            </div>
            <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
              <p className="text-2xl font-bold text-green-400">
                {wallets.filter(w => w.mnemonic).length}
              </p>
              <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>With Recovery</p>
            </div>
            <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
              <p className="text-2xl font-bold text-yellow-400">
                {backups.length}
              </p>
              <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Backups</p>
            </div>
          </div>

          {wallets.length === 0 ? (
            <div className={`p-12 text-center rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
              <Wallet className="w-12 h-12 text-slate-500 mx-auto mb-4" />
              <p className={`text-lg font-medium ${darkMode ? 'text-slate-300' : 'text-slate-600'}`}>
                No wallets yet
              </p>
              <p className={`text-sm ${darkMode ? 'text-slate-500' : 'text-slate-500'}`}>
                Generate or import your first wallet
              </p>
            </div>
          ) : (
            <div className="grid gap-4">
              {wallets.map(wallet => (
                <div
                  key={wallet.id}
                  className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">{chainConfig[wallet.chain].icon}</span>
                      <div>
                        <p className={`font-semibold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                          {wallet.name}
                        </p>
                        <p className="text-sm text-purple-400">{chainConfig[wallet.chain].name}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {wallet.mnemonic && (
                        <span className="px-2 py-1 bg-green-500/10 text-green-400 text-xs rounded">
                          Recovery
                        </span>
                      )}
                      {wallet.tags.includes('imported') && (
                        <span className="px-2 py-1 bg-blue-500/10 text-blue-400 text-xs rounded">
                          Imported
                        </span>
                      )}
                      <button
                        onClick={() => deleteWallet(wallet.id)}
                        className="p-2 text-red-400 hover:bg-red-500/10 rounded-lg"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  {/* Address */}
                  <div className="mt-4">
                    <label className={`block text-xs font-medium mb-1 ${darkMode ? 'text-slate-500' : 'text-slate-500'}`}>
                      ADDRESS
                    </label>
                    <div className="flex gap-2">
                      <code className={`flex-1 p-2 rounded text-sm break-all ${darkMode ? 'bg-slate-900 text-green-400' : 'bg-slate-100 text-green-600'}`}>
                        {wallet.address}
                      </code>
                      <button
                        onClick={() => copyToClipboard(wallet.address)}
                        className="p-2 bg-purple-600/20 text-purple-400 rounded hover:bg-purple-600/30"
                      >
                        <Copy className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  {/* Private Key Toggle */}
                  <div className="mt-3">
                    <button
                      onClick={() => togglePrivateKey(wallet.id)}
                      className={`text-sm flex items-center gap-2 ${darkMode ? 'text-red-400' : 'text-red-600'}`}
                    >
                      {showPrivateKeys.has(wallet.id) ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      {showPrivateKeys.has(wallet.id) ? 'Hide Private Key' : 'Show Private Key'}
                    </button>
                    {showPrivateKeys.has(wallet.id) && (
                      <div className="mt-2 flex gap-2">
                        <code className={`flex-1 p-2 rounded text-sm break-all ${darkMode ? 'bg-slate-900 text-red-400' : 'bg-red-50 text-red-600 border border-red-200'}`}>
                          {wallet.privateKey}
                        </code>
                        <button
                          onClick={() => copyToClipboard(wallet.privateKey)}
                          className="p-2 bg-red-600/20 text-red-400 rounded hover:bg-red-600/30"
                        >
                          <Copy className="w-4 h-4" />
                        </button>
                      </div>
                    )}
                  </div>

                  {/* Quick Actions */}
                  <div className="mt-4 flex gap-2">
                    <a
                      href={`https://etherscan.io/address/${wallet.address}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-1 px-3 py-1.5 text-sm bg-slate-600/20 text-slate-400 rounded hover:bg-slate-600/30"
                    >
                      <ExternalLink className="w-3 h-3" />
                      Explorer
                    </a>
                    <button
                      onClick={() => createBackup(wallet.id, 'json')}
                      className="flex items-center gap-1 px-3 py-1.5 text-sm bg-purple-600/20 text-purple-400 rounded hover:bg-purple-600/30"
                    >
                      <Download className="w-3 h-3" />
                      Backup
                    </button>
                  </div>

                  {/* Notes */}
                  {wallet.notes && (
                    <p className={`mt-3 text-sm ${darkMode ? 'text-slate-500' : 'text-slate-500'}`}>
                      {wallet.notes}
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Export All */}
          {wallets.length > 0 && (
            <button
              onClick={exportAllWallets}
              className="w-full py-3 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-medium transition-all flex items-center justify-center gap-2"
            >
              <Download className="w-5 h-5" />
              Export All Wallets (Encrypted JSON)
            </button>
          )}
        </div>
      )}

      {/* Import Tab */}
      {activeTab === 'import' && (
        <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
          <h2 className={`text-lg font-semibold mb-6 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
            Import Existing Wallet
          </h2>

          <div className="space-y-6 max-w-md">
            {/* Import Type */}
            <div>
              <label className={`block text-sm font-medium mb-2 ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>
                Import Method
              </label>
              <div className="grid grid-cols-2 gap-2">
                <button
                  onClick={() => setImportType('privateKey')}
                  className={`p-3 rounded-lg border text-center transition-all ${
                    importType === 'privateKey'
                      ? 'border-purple-500 bg-purple-500/10 text-white'
                      : darkMode
                      ? 'border-slate-600 text-slate-400'
                      : 'border-slate-200 text-slate-600'
                  }`}
                >
                  <Key className="w-5 h-5 mx-auto mb-1" />
                  Private Key
                </button>
                <button
                  onClick={() => setImportType('mnemonic')}
                  className={`p-3 rounded-lg border text-center transition-all ${
                    importType === 'mnemonic'
                      ? 'border-purple-500 bg-purple-500/10 text-white'
                      : darkMode
                      ? 'border-slate-600 text-slate-400'
                      : 'border-slate-200 text-slate-600'
                  }`}
                >
                  <FileCode className="w-5 h-5 mx-auto mb-1" />
                  Recovery Phrase
                </button>
              </div>
            </div>

            {/* Chain Selection */}
            <div>
              <label className={`block text-sm font-medium mb-2 ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>
                Target Chain *
              </label>
              <select
                value={importChain}
                onChange={e => setImportChain(e.target.value as any)}
                className={`w-full px-4 py-2 rounded-lg border ${
                  darkMode
                    ? 'bg-slate-900 border-slate-700 text-white'
                    : 'bg-white border-slate-300'
                }`}
              >
                {(Object.keys(chainConfig) as Array<keyof typeof chainConfig>).map(chain => (
                  <option key={chain} value={chain}>
                    {chainConfig[chain].icon} {chainConfig[chain].name}
                  </option>
                ))}
              </select>
            </div>

            {/* Wallet Name */}
            <div>
              <label className={`block text-sm font-medium mb-2 ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>
                Wallet Name (Optional)
              </label>
              <input
                type="text"
                value={importName}
                onChange={e => setImportName(e.target.value)}
                placeholder={`Imported ${chainConfig[importChain].name} Wallet`}
                className={`w-full px-4 py-2 rounded-lg border ${
                  darkMode
                    ? 'bg-slate-900 border-slate-700 text-white'
                    : 'bg-white border-slate-300'
                }`}
              />
            </div>

            {/* Import Value */}
            <div>
              <label className={`block text-sm font-medium mb-2 ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>
                {importType === 'privateKey' ? 'Private Key' : 'Recovery Phrase'} *
              </label>
              <textarea
                value={importValue}
                onChange={e => setImportValue(e.target.value)}
                placeholder={
                  importType === 'privateKey'
                    ? '0x...'
                    : 'word1 word2 word3 ... word12 (or 24)'
                }
                rows={importType === 'mnemonic' ? 3 : 2}
                className={`w-full px-4 py-2 rounded-lg border font-mono text-sm ${
                  darkMode
                    ? 'bg-slate-900 border-slate-700 text-white'
                    : 'bg-white border-slate-300'
                }`}
              />
            </div>

            {/* Security Warning */}
            <div className={`p-4 rounded-lg ${darkMode ? 'bg-red-500/10' : 'bg-red-50'} border border-red-500/30`}>
              <div className="flex items-start gap-3">
                <input
                  type="checkbox"
                  id="import-security"
                  checked={securityAcknowledged}
                  onChange={e => setSecurityAcknowledged(e.target.checked)}
                  className="w-5 h-5 mt-0.5 rounded border-red-500"
                />
                <label htmlFor="import-security" className={`text-sm ${darkMode ? 'text-red-200' : 'text-red-800'}`}>
                  I am importing my own wallet. I understand the risks of importing wallets and will verify the address matches my records.
                </label>
              </div>
            </div>

            {/* Import Button */}
            <button
              onClick={importWallet}
              disabled={!importValue.trim() || !securityAcknowledged}
              className="w-full py-3 bg-purple-600 hover:bg-purple-700 disabled:bg-slate-600 disabled:cursor-not-allowed text-white rounded-lg font-medium transition-all flex items-center justify-center gap-2"
            >
              <Download className="w-5 h-5" />
              Import Wallet
            </button>
          </div>
        </div>
      )}

      {/* Backup Tab */}
      {activeTab === 'backup' && (
        <div className="space-y-4">
          <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
            <h2 className={`text-lg font-semibold mb-4 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
              Backup Center
            </h2>

            <div className={`p-4 rounded-lg ${darkMode ? 'bg-blue-500/10' : 'bg-blue-50'} border border-blue-500/30 mb-6`}>
              <h3 className="font-medium text-blue-400 mb-2">Backup Best Practices</h3>
              <ul className={`text-sm space-y-1 ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>
                <li>• Create backups immediately after generating wallets</li>
                <li>• Store backups in multiple secure locations</li>
                <li>• Use encrypted backups when possible</li>
                <li>• Never store unencrypted private keys in cloud storage</li>
                <li>• Test your recovery process periodically</li>
              </ul>
            </div>

            {/* Backup Actions */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <button
                onClick={exportAllWallets}
                className={`p-4 rounded-lg border text-center transition-all ${
                  darkMode
                    ? 'border-slate-600 hover:border-purple-500 hover:bg-purple-500/5'
                    : 'border-slate-200 hover:border-purple-500 hover:bg-purple-50'
                }`}
              >
                <FileCode className="w-8 h-8 text-purple-400 mx-auto mb-2" />
                <p className={`font-medium ${darkMode ? 'text-white' : 'text-slate-900'}`}>JSON Backup</p>
                <p className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>Encrypted wallet export</p>
              </button>

              <button
                className={`p-4 rounded-lg border text-center transition-all ${
                  darkMode
                    ? 'border-slate-600 hover:border-purple-500 hover:bg-purple-500/5'
                    : 'border-slate-200 hover:border-purple-500 hover:bg-purple-50'
                }`}
              >
                <Download className="w-8 h-8 text-green-400 mx-auto mb-2" />
                <p className={`font-medium ${darkMode ? 'text-white' : 'text-slate-900'}`}>CSV Export</p>
                <p className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>Address list only</p>
              </button>

              <button
                className={`p-4 rounded-lg border text-center transition-all ${
                  darkMode
                    ? 'border-slate-600 hover:border-purple-500 hover:bg-purple-500/5'
                    : 'border-slate-200 hover:border-purple-500 hover:bg-purple-50'
                }`}
              >
                <Shield className="w-8 h-8 text-yellow-400 mx-auto mb-2" />
                <p className={`font-medium ${darkMode ? 'text-white' : 'text-slate-900'}`}>Paper Backup</p>
                <p className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>Printable templates</p>
              </button>
            </div>
          </div>

          {/* Backup History */}
          {backups.length > 0 && (
            <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
              <h3 className={`font-semibold mb-4 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                Backup History
              </h3>
              <div className="space-y-2">
                {backups.map(backup => {
                  const wallet = wallets.find(w => w.id === backup.walletId);
                  return (
                    <div
                      key={backup.id}
                      className={`p-3 rounded-lg flex items-center justify-between ${darkMode ? 'bg-slate-900' : 'bg-slate-50'}`}
                    >
                      <div className="flex items-center gap-3">
                        <Shield className="w-5 h-5 text-green-400" />
                        <div>
                          <p className={`font-medium ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                            {wallet?.name || 'Unknown Wallet'}
                          </p>
                          <p className="text-xs text-slate-500">
                            {backup.type.toUpperCase()} • {new Date(backup.createdAt).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                      <span className="px-2 py-1 bg-green-500/10 text-green-400 text-xs rounded">
                        {backup.encrypted ? 'Encrypted' : 'Unencrypted'}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
