import React, { useState } from 'react';
import {
  Wallet,
  Key,
  Shield,
  Lock,
  Unlock,
  Eye,
  EyeOff,
  Copy,
  Download,
  Upload,
  Trash2,
  Plus,
  CheckCircle,
  AlertTriangle,
  RefreshCw,
  Fingerprint,
  Smartphone,
  Usb,
  HardDrive,
  Cloud,
  Database,
  Layers,
  Settings,
  Users,
  FileText,
  Clock,
  Activity,
  Zap,
  Globe,
  ChevronDown,
  ChevronUp,
  MoreHorizontal,
  Terminal,
  Code,
  QrCode,
  Scan,
  X,
  Search,
  Filter,
  Grid,
  List,
  AlertCircle,
  CheckSquare,
  Square,
  Send,
  RotateCcw,
  Save,
  Edit3,
  ShieldCheck,
  ShieldAlert,
  Vault,
  KeyRound,
  LockKeyhole,
  UnlockKeyhole
} from 'lucide-react';

type SecurityLevel = 'standard' | 'enhanced' | 'maximum' | 'airgap';
type WalletType = 'hot' | 'warm' | 'cold' | 'hardware' | 'multisig' | 'paper';
type ChainType = 'ethereum' | 'bitcoin' | 'solana' | 'base' | 'arbitrum' | 'polygon' | 'bsc' | 'avalanche';

interface WalletKey {
  id: string;
  name: string;
  address: string;
  chain: ChainType;
  type: WalletType;
  securityLevel: SecurityLevel;
  balance: string;
  lastUsed: string;
  createdAt: string;
  purpose: string;
  tags: string[];
  encrypted: boolean;
  backupCount: number;
  multisigRequired?: number;
  multisigTotal?: number;
  hardwareType?: string;
  derivationPath?: string;
  status: 'active' | 'locked' | 'compromised' | 'archived';
}

interface SecurityAudit {
  id: string;
  timestamp: string;
  action: string;
  walletId?: string;
  user: string;
  ipAddress: string;
  success: boolean;
  details: string;
  riskLevel: 'low' | 'medium' | 'high';
}

interface BackupLocation {
  id: string;
  type: 'hardware_wallet' | 'paper' | 'encrypted_usb' | 'hardware_security_module' | 'airgapped_computer' | 'safe_deposit' | 'shamir_share';
  name: string;
  location: string;
  lastVerified: string;
  status: 'verified' | 'pending' | 'missing';
}

interface AccessPolicy {
  id: string;
  name: string;
  walletType: WalletType;
  requireMFA: boolean;
  requireHardwareKey: boolean;
  requireMultipleApprovals: boolean;
  approvalCount: number;
  timeDelay: number; // hours
  ipWhitelist: string[];
  maxDailyTx: number;
  maxTxAmount: string;
}

const SecureWalletManager: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'vault' | 'keys' | 'backups' | 'audit' | 'policies' | 'access'>('vault');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');

  // Wallet Keys State
  const [wallets, setWallets] = useState<WalletKey[]>([
    {
      id: 'w1',
      name: 'Treasury Primary',
      address: '0x742d35Cc6634C0532925a3b844Bc9e7595f5cC0E',
      chain: 'ethereum',
      type: 'multisig',
      securityLevel: 'maximum',
      balance: '2,456.78 ETH',
      lastUsed: '2026-04-14 10:30',
      createdAt: '2025-01-15',
      purpose: 'Primary treasury for $CRM operations',
      tags: ['treasury', 'multisig', 'high-value'],
      encrypted: true,
      backupCount: 5,
      multisigRequired: 3,
      multisigTotal: 5,
      status: 'active'
    },
    {
      id: 'w2',
      name: 'Operations Hot Wallet',
      address: '0x8ba1f109551bD432803012645Hac136c98C',
      chain: 'ethereum',
      type: 'hot',
      securityLevel: 'standard',
      balance: '45.23 ETH',
      lastUsed: '2026-04-14 14:22',
      createdAt: '2025-03-20',
      purpose: 'Daily operations and small payments',
      tags: ['operations', 'hot', 'low-value'],
      encrypted: true,
      backupCount: 3,
      status: 'active'
    },
    {
      id: 'w3',
      name: 'Cold Storage - Ledger',
      address: 'bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh',
      chain: 'bitcoin',
      type: 'hardware',
      securityLevel: 'maximum',
      balance: '12.5 BTC',
      lastUsed: '2026-03-15 09:00',
      createdAt: '2025-01-10',
      purpose: 'Long-term BTC holdings',
      tags: ['cold', 'btc', 'hodl'],
      encrypted: true,
      backupCount: 2,
      hardwareType: 'Ledger Nano X',
      derivationPath: "m/44'/0'/0'/0/0",
      status: 'locked'
    },
    {
      id: 'w4',
      name: 'Base Operations',
      address: '0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B',
      chain: 'base',
      type: 'warm',
      securityLevel: 'enhanced',
      balance: '15,420 USDC',
      lastUsed: '2026-04-14 12:15',
      createdAt: '2025-06-01',
      purpose: 'Base chain operations and L2 activities',
      tags: ['base', 'l2', 'operations'],
      encrypted: true,
      backupCount: 3,
      status: 'active'
    },
    {
      id: 'w5',
      name: 'Solana Dev Wallet',
      address: 'HN7cABqLq46Es1jh92dQQisAq662SmxELLLsHHe4YWrH',
      chain: 'solana',
      type: 'hot',
      securityLevel: 'standard',
      balance: '125.5 SOL',
      lastUsed: '2026-04-13 16:45',
      createdAt: '2025-08-10',
      purpose: 'Solana development and testing',
      tags: ['solana', 'dev', 'testing'],
      encrypted: true,
      backupCount: 2,
      status: 'active'
    }
  ]);

  // Security Audit Logs
  const [auditLogs, setAuditLogs] = useState<SecurityAudit[]>([
    {
      id: 'a1',
      timestamp: '2026-04-14 14:30:22',
      action: 'KEY_ACCESS_ATTEMPT',
      walletId: 'w1',
      user: 'ADMIN',
      ipAddress: '192.168.1.100',
      success: true,
      details: 'Viewed encrypted key (partial) for Treasury Primary',
      riskLevel: 'low'
    },
    {
      id: 'a2',
      timestamp: '2026-04-14 12:15:45',
      action: 'TRANSACTION_SIGNED',
      walletId: 'w2',
      user: 'ADMIN',
      ipAddress: '192.168.1.100',
      success: true,
      details: 'Signed 0.5 ETH transfer to 0x1234...',
      riskLevel: 'medium'
    },
    {
      id: 'a3',
      timestamp: '2026-04-14 10:22:18',
      action: 'FAILED_LOGIN',
      user: 'UNKNOWN',
      ipAddress: '45.142.212.100',
      success: false,
      details: 'Failed authentication attempt - wrong MFA code',
      riskLevel: 'high'
    },
    {
      id: 'a4',
      timestamp: '2026-04-13 09:00:33',
      action: 'BACKUP_VERIFIED',
      walletId: 'w3',
      user: 'ADMIN',
      ipAddress: '192.168.1.100',
      success: true,
      details: 'Verified Ledger backup in safe deposit box',
      riskLevel: 'low'
    }
  ]);

  // Backup Locations
  const [backups, setBackups] = useState<BackupLocation[]>([
    {
      id: 'b1',
      type: 'hardware_wallet',
      name: 'Primary Ledger Nano X',
      location: 'Office Safe - Keycode required',
      lastVerified: '2026-04-13',
      status: 'verified'
    },
    {
      id: 'b2',
      type: 'paper',
      name: 'Seed Phrase Backup A',
      location: 'Bank Safe Deposit Box #2847',
      lastVerified: '2026-03-15',
      status: 'verified'
    },
    {
      id: 'b3',
      type: 'shamir_share',
      name: 'Shamir Share 1/3',
      location: 'Attorney Escrow - Legal Firm',
      lastVerified: '2026-02-20',
      status: 'verified'
    },
    {
      id: 'b4',
      type: 'shamir_share',
      name: 'Shamir Share 2/3',
      location: 'Family Member - Encrypted USB',
      lastVerified: '2026-02-20',
      status: 'verified'
    },
    {
      id: 'b5',
      type: 'encrypted_usb',
      name: 'Hardware Encrypted USB',
      location: 'Offsite Backup Facility',
      lastVerified: '2026-01-10',
      status: 'pending'
    }
  ]);

  // Access Policies
  const [policies, setPolicies] = useState<AccessPolicy[]>([
    {
      id: 'pol1',
      name: 'Treasury Access Policy',
      walletType: 'multisig',
      requireMFA: true,
      requireHardwareKey: true,
      requireMultipleApprovals: true,
      approvalCount: 3,
      timeDelay: 24,
      ipWhitelist: ['192.168.1.0/24', '10.0.0.0/8'],
      maxDailyTx: 5,
      maxTxAmount: '1000'
    },
    {
      id: 'pol2',
      name: 'Operations Wallet Policy',
      walletType: 'hot',
      requireMFA: true,
      requireHardwareKey: false,
      requireMultipleApprovals: false,
      approvalCount: 1,
      timeDelay: 0,
      ipWhitelist: [],
      maxDailyTx: 50,
      maxTxAmount: '10'
    },
    {
      id: 'pol3',
      name: 'Cold Storage Policy',
      walletType: 'hardware',
      requireMFA: true,
      requireHardwareKey: true,
      requireMultipleApprovals: true,
      approvalCount: 5,
      timeDelay: 72,
      ipWhitelist: ['192.168.1.100'],
      maxDailyTx: 1,
      maxTxAmount: '100'
    }
  ]);

  // UI State
  const [showAddWallet, setShowAddWallet] = useState(false);
  const [showKeyReveal, setShowKeyReveal] = useState(false);
  const [selectedWallet, setSelectedWallet] = useState<string | null>(null);
  const [securityChallenge, setSecurityChallenge] = useState({
    step: 0,
    mfaCode: '',
    password: '',
    hardwareConfirmed: false
  });

  const [newWallet, setNewWallet] = useState({
    name: '',
    chain: 'ethereum' as ChainType,
    type: 'hot' as WalletType,
    securityLevel: 'standard' as SecurityLevel,
    purpose: '',
    hardwareType: '',
    useMultisig: false,
    multisigRequired: 2,
    multisigTotal: 3
  });

  // Stats
  const stats = {
    totalWallets: wallets.length,
    totalValue: '$5.2M+',
    activeWallets: wallets.filter(w => w.status === 'active').length,
    lockedWallets: wallets.filter(w => w.status === 'locked').length,
    multisigWallets: wallets.filter(w => w.type === 'multisig').length,
    hardwareWallets: wallets.filter(w => w.type === 'hardware').length,
    backupCoverage: Math.round((backups.filter(b => b.status === 'verified').length / backups.length) * 100),
    lastAuditDays: 0
  };

  const handleInitiateKeyReveal = (walletId: string) => {
    setSelectedWallet(walletId);
    setSecurityChallenge({ step: 1, mfaCode: '', password: '', hardwareConfirmed: false });
    setShowKeyReveal(true);
  };

  const handleSecurityStep = () => {
    if (securityChallenge.step === 1) {
      // Verify MFA
      setSecurityChallenge({ ...securityChallenge, step: 2 });
    } else if (securityChallenge.step === 2) {
      // Verify hardware key
      setSecurityChallenge({ ...securityChallenge, step: 3, hardwareConfirmed: true });
    } else if (securityChallenge.step === 3) {
      // Final reveal
      setSecurityChallenge({ ...securityChallenge, step: 4 });
    }
  };

  const getSecurityLevelColor = (level: SecurityLevel) => {
    switch (level) {
      case 'standard': return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      case 'enhanced': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'maximum': return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'airgap': return 'bg-purple-500/20 text-purple-400 border-purple-500/30';
    }
  };

  const getWalletTypeIcon = (type: WalletType) => {
    switch (type) {
      case 'hot': return <Zap className="w-4 h-4 text-yellow-400" />;
      case 'warm': return <Activity className="w-4 h-4 text-orange-400" />;
      case 'cold': return <Snowflake className="w-4 h-4 text-blue-400" />;
      case 'hardware': return <Usb className="w-4 h-4 text-purple-400" />;
      case 'multisig': return <Users className="w-4 h-4 text-green-400" />;
      case 'paper': return <FileText className="w-4 h-4 text-gray-400" />;
    }
  };

  const Snowflake = ({ className }: { className?: string }) => (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <circle cx="12" cy="12" r="3" />
      <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" />
    </svg>
  );

  return (
    <div className="min-h-screen bg-[#0a0812] text-gray-100 font-mono selection:bg-[#7c3aed]/30">
      {/* Header */}
      <div className="bg-gradient-to-r from-[#0f0c1d] via-[#1a1525] to-[#0f0c1d] border-b border-[#7c3aed]/30">
        <div className="max-w-[1600px] mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-[#7c3aed]/20 rounded-full flex items-center justify-center">
                <Vault className="w-5 h-5 text-[#7c3aed]" />
              </div>
              <div>
                <h1 className="text-xl font-bold tracking-wider">
                  SECURE <span className="text-[#7c3aed]">VAULT</span>
                </h1>
                <p className="text-xs text-gray-500 tracking-[0.2em]">ENTERPRISE WALLET & KEY MANAGEMENT</p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 px-3 py-1.5 bg-[#7c3aed]/10 border border-[#7c3aed]/30 rounded">
                <Wallet className="w-4 h-4 text-[#7c3aed]" />
                <span className="text-sm text-[#7c3aed]">{stats.totalValue} Protected</span>
              </div>
              <div className="flex items-center gap-2 px-3 py-1.5 bg-green-500/10 border border-green-500/30 rounded">
                <ShieldCheck className="w-4 h-4 text-green-400" />
                <span className="text-sm text-green-400">{stats.backupCoverage}% Backed Up</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-[1600px] mx-auto p-6 space-y-6">
        {/* Security Alert Banner */}
        <div className="bg-gradient-to-r from-red-500/20 via-[#1a1525] to-red-500/20 border border-red-500/30 rounded-lg p-4">
          <div className="flex items-center gap-3">
            <ShieldAlert className="w-6 h-6 text-red-400" />
            <div>
              <h3 className="font-bold text-red-400">Security Notice</h3>
              <p className="text-sm text-gray-400">Backup verification pending for "Hardware Encrypted USB" - Last verified 94 days ago</p>
            </div>
            <button className="ml-auto px-4 py-2 bg-red-500/10 border border-red-500/30 rounded text-sm text-red-400 hover:bg-red-500/20 transition-all">
              VERIFY NOW
            </button>
          </div>
        </div>

        {/* Stats Row */}
        <div className="grid grid-cols-6 gap-4">
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
            <Wallet className="w-5 h-5 text-blue-400 mb-2" />
            <div className="text-xl font-bold">{stats.totalWallets}</div>
            <div className="text-xs text-gray-500">Total Wallets</div>
          </div>
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
            <Users className="w-5 h-5 text-green-400 mb-2" />
            <div className="text-xl font-bold">{stats.multisigWallets}</div>
            <div className="text-xs text-gray-500">Multi-Sig</div>
          </div>
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
            <Usb className="w-5 h-5 text-purple-400 mb-2" />
            <div className="text-xl font-bold">{stats.hardwareWallets}</div>
            <div className="text-xs text-gray-500">Hardware</div>
          </div>
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
            <Lock className="w-5 h-5 text-yellow-400 mb-2" />
            <div className="text-xl font-bold">{stats.lockedWallets}</div>
            <div className="text-xs text-gray-500">Locked</div>
          </div>
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
            <HardDrive className="w-5 h-5 text-pink-400 mb-2" />
            <div className="text-xl font-bold">{backups.length}</div>
            <div className="text-xs text-gray-500">Backup Locations</div>
          </div>
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
            <Activity className="w-5 h-5 text-cyan-400 mb-2" />
            <div className="text-xl font-bold">{auditLogs.length}</div>
            <div className="text-xs text-gray-500">Audit Events (24h)</div>
          </div>
        </div>

        {/* Navigation */}
        <div className="flex items-center gap-1 border-b border-gray-800">
          {[
            { id: 'vault', label: 'VAULT OVERVIEW', icon: <Vault className="w-4 h-4" /> },
            { id: 'keys', label: 'KEY MANAGEMENT', icon: <Key className="w-4 h-4" /> },
            { id: 'backups', label: 'BACKUP LOCATIONS', icon: <HardDrive className="w-4 h-4" /> },
            { id: 'audit', label: 'AUDIT LOG', icon: <FileText className="w-4 h-4" /> },
            { id: 'policies', label: 'ACCESS POLICIES', icon: <Shield className="w-4 h-4" /> },
            { id: 'access', label: 'ACCESS CONTROL', icon: <Lock className="w-4 h-4" /> },
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

        {/* Vault Overview Tab */}
        {activeTab === 'vault' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-bold">Wallet Vault</h2>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setViewMode(viewMode === 'grid' ? 'list' : 'grid')}
                  className="p-2 bg-gray-800 rounded hover:bg-gray-700 transition-all"
                >
                  {viewMode === 'grid' ? <List className="w-4 h-4" /> : <Grid className="w-4 h-4" />}
                </button>
                <button
                  onClick={() => setShowAddWallet(true)}
                  className="flex items-center gap-2 px-4 py-2 bg-[#7c3aed] text-white rounded transition-all"
                >
                  <Plus className="w-4 h-4" />
                  ADD WALLET
                </button>
              </div>
            </div>

            {viewMode === 'grid' ? (
              <div className="grid grid-cols-3 gap-4">
                {wallets.map((wallet) => (
                  <div key={wallet.id} className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-5 hover:border-[#7c3aed]/50 transition-all">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center gap-2">
                        {getWalletTypeIcon(wallet.type)}
                        <span className="text-xs text-gray-500 uppercase">{wallet.type}</span>
                      </div>
                      <span className={`px-2 py-1 rounded text-[10px] border ${getSecurityLevelColor(wallet.securityLevel)}`}>
                        {wallet.securityLevel}
                      </span>
                    </div>

                    <h3 className="font-bold mb-1">{wallet.name}</h3>
                    <p className="text-xs text-gray-500 mb-3 font-mono">{wallet.address.slice(0, 20)}...{wallet.address.slice(-4)}</p>

                    <div className="space-y-2 mb-4">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-500">Balance:</span>
                        <span className="font-semibold text-green-400">{wallet.balance}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-500">Chain:</span>
                        <span className="uppercase">{wallet.chain}</span>
                      </div>
                      {wallet.multisigRequired && (
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-500">Multi-sig:</span>
                          <span>{wallet.multisigRequired}/{wallet.multisigTotal}</span>
                        </div>
                      )}
                    </div>

                    <div className="flex gap-2">
                      <button
                        onClick={() => handleInitiateKeyReveal(wallet.id)}
                        className="flex-1 py-2 bg-[#7c3aed]/10 border border-[#7c3aed]/30 rounded text-xs text-[#7c3aed] hover:bg-[#7c3aed]/20 transition-all"
                      >
                        <Key className="w-3 h-3 inline mr-1" />
                        VIEW KEY
                      </button>
                      <button className="px-3 py-2 bg-gray-800 rounded text-xs text-gray-400 hover:bg-gray-700 transition-all">
                        <Settings className="w-3 h-3" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg overflow-hidden">
                <table className="w-full">
                  <thead className="bg-[#0f0c1d] border-b border-gray-800">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">WALLET</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">TYPE</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">SECURITY</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">BALANCE</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">LAST USED</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">ACTIONS</th>
                    </tr>
                  </thead>
                  <tbody>
                    {wallets.map((wallet) => (
                      <tr key={wallet.id} className="border-b border-gray-800 hover:bg-[#0a0812]/50 transition-all">
                        <td className="px-4 py-3">
                          <div className="font-semibold">{wallet.name}</div>
                          <div className="text-xs text-gray-500 font-mono">{wallet.address.slice(0, 15)}...</div>
                        </td>
                        <td className="px-4 py-3">
                          <span className="flex items-center gap-2 text-sm uppercase">
                            {getWalletTypeIcon(wallet.type)}
                            {wallet.type}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          <span className={`px-2 py-1 rounded text-xs border ${getSecurityLevelColor(wallet.securityLevel)}`}>
                            {wallet.securityLevel}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-green-400 font-semibold">{wallet.balance}</td>
                        <td className="px-4 py-3 text-sm text-gray-400">{wallet.lastUsed}</td>
                        <td className="px-4 py-3">
                          <div className="flex gap-2">
                            <button
                              onClick={() => handleInitiateKeyReveal(wallet.id)}
                              className="px-2 py-1 bg-[#7c3aed]/10 border border-[#7c3aed]/30 rounded text-xs text-[#7c3aed]"
                            >
                              VIEW
                            </button>
                            <button className="p-1 bg-gray-800 rounded">
                              <Settings className="w-3 h-3" />
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

        {/* Key Management Tab */}
        {activeTab === 'keys' && (
          <div className="space-y-6">
            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-bold mb-4">Key Derivation & Management</h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-[#0a0812] rounded-lg border border-gray-800">
                  <h4 className="font-semibold mb-3 flex items-center gap-2">
                    <KeyRound className="w-4 h-4 text-[#7c3aed]" />
                    HD Wallet Derivation
                  </h4>
                  <div className="space-y-3">
                    <div>
                      <label className="text-xs text-gray-500">Master Seed (Encrypted)</label>
                      <div className="flex gap-2">
                        <input
                          type="password"
                          value="••••••••••••••••••••••••••••••"
                          readOnly
                          className="flex-1 px-3 py-2 bg-gray-800 border border-gray-700 rounded text-sm"
                        />
                        <button className="px-3 py-2 bg-[#7c3aed]/10 border border-[#7c3aed]/30 rounded text-[#7c3aed]">
                          <Eye className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                    <div>
                      <label className="text-xs text-gray-500">Derivation Path</label>
                      <input
                        type="text"
                        value="m/44'/60'/0'/0/0"
                        className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded text-sm font-mono"
                      />
                    </div>
                    <button className="w-full py-2 bg-[#7c3aed] text-white rounded text-sm hover:bg-[#6d28d9] transition-all">
                      GENERATE NEW DERIVED KEY
                    </button>
                  </div>
                </div>

                <div className="p-4 bg-[#0a0812] rounded-lg border border-gray-800">
                  <h4 className="font-semibold mb-3 flex items-center gap-2">
                    <Shield className="w-4 h-4 text-green-400" />
                    Key Encryption Status
                  </h4>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between p-2 bg-gray-800/50 rounded">
                      <span className="text-sm">AES-256-GCM</span>
                      <CheckCircle className="w-4 h-4 text-green-400" />
                    </div>
                    <div className="flex items-center justify-between p-2 bg-gray-800/50 rounded">
                      <span className="text-sm">Hardware Security Module</span>
                      <CheckCircle className="w-4 h-4 text-green-400" />
                    </div>
                    <div className="flex items-center justify-between p-2 bg-gray-800/50 rounded">
                      <span className="text-sm">Shamir Secret Sharing</span>
                      <CheckCircle className="w-4 h-4 text-green-400" />
                    </div>
                    <div className="flex items-center justify-between p-2 bg-gray-800/50 rounded">
                      <span className="text-sm">Key Rotation (90 days)</span>
                      <Clock className="w-4 h-4 text-yellow-400" />
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-bold mb-4">Multi-Signature Wallets</h3>
              <div className="space-y-3">
                {wallets.filter(w => w.type === 'multisig').map((wallet) => (
                  <div key={wallet.id} className="p-4 bg-[#0a0812] rounded-lg border border-gray-800">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-3">
                        <Users className="w-5 h-5 text-green-400" />
                        <span className="font-semibold">{wallet.name}</span>
                      </div>
                      <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded text-sm">
                        {wallet.multisigRequired} of {wallet.multisigTotal} Required
                      </span>
                    </div>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-500">Address:</span>
                        <span className="font-mono">{wallet.address}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-500">Signers:</span>
                        <span>5 configured</span>
                      </div>
                      <div className="flex gap-2 mt-3">
                        <button className="px-3 py-1.5 bg-gray-800 rounded text-xs text-gray-400 hover:bg-gray-700 transition-all">
                          VIEW SIGNERS
                        </button>
                        <button className="px-3 py-1.5 bg-[#7c3aed]/10 border border-[#7c3aed]/30 rounded text-xs text-[#7c3aed] hover:bg-[#7c3aed]/20 transition-all">
                          INITIATE TX
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Backup Locations Tab */}
        {activeTab === 'backups' && (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h2 className="text-lg font-bold">Backup Locations ({backups.length})</h2>
              <button className="flex items-center gap-2 px-4 py-2 bg-[#7c3aed] text-white rounded transition-all">
                <Plus className="w-4 h-4" />
                ADD BACKUP LOCATION
              </button>
            </div>

            <div className="grid grid-cols-2 gap-4">
              {backups.map((backup) => (
                <div key={backup.id} className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-5">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      {backup.type === 'hardware_wallet' && <Usb className="w-5 h-5 text-purple-400" />}
                      {backup.type === 'paper' && <FileText className="w-5 h-5 text-yellow-400" />}
                      {backup.type === 'shamir_share' && <Layers className="w-5 h-5 text-blue-400" />}
                      {backup.type === 'encrypted_usb' && <HardDrive className="w-5 h-5 text-green-400" />}
                      <div>
                        <h3 className="font-semibold">{backup.name}</h3>
                        <p className="text-xs text-gray-500 uppercase">{backup.type.replace('_', ' ')}</p>
                      </div>
                    </div>
                    <span className={`px-2 py-1 rounded text-xs ${
                      backup.status === 'verified' ? 'bg-green-500/20 text-green-400' :
                      backup.status === 'pending' ? 'bg-yellow-500/20 text-yellow-400' :
                      'bg-red-500/20 text-red-400'
                    }`}>
                      {backup.status.toUpperCase()}
                    </span>
                  </div>

                  <div className="space-y-2 text-sm mb-4">
                    <div className="flex items-center gap-2 text-gray-400">
                      <Globe className="w-4 h-4" />
                      {backup.location}
                    </div>
                    <div className="flex items-center gap-2 text-gray-400">
                      <Clock className="w-4 h-4" />
                      Last verified: {backup.lastVerified}
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <button className="flex-1 py-2 bg-[#7c3aed]/10 border border-[#7c3aed]/30 rounded text-xs text-[#7c3aed] hover:bg-[#7c3aed]/20 transition-all">
                      VERIFY
                    </button>
                    <button className="px-3 py-2 bg-gray-800 rounded text-xs text-gray-400 hover:bg-gray-700 transition-all">
                      <Edit3 className="w-3 h-3" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Audit Log Tab */}
        {activeTab === 'audit' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-bold">Security Audit Log</h2>
              <button className="flex items-center gap-2 px-3 py-2 bg-gray-800 border border-gray-700 rounded text-sm text-gray-400 hover:bg-gray-700 transition-all">
                <Download className="w-4 h-4" />
                EXPORT LOGS
              </button>
            </div>

            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg overflow-hidden">
              <table className="w-full">
                <thead className="bg-[#0f0c1d] border-b border-gray-800">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">TIMESTAMP</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">ACTION</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">USER</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">IP ADDRESS</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">STATUS</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">RISK</th>
                  </tr>
                </thead>
                <tbody>
                  {auditLogs.map((log) => (
                    <tr key={log.id} className="border-b border-gray-800 hover:bg-[#0a0812]/50 transition-all">
                      <td className="px-4 py-3 text-sm text-gray-400">{log.timestamp}</td>
                      <td className="px-4 py-3">
                        <div className="font-semibold text-sm">{log.action}</div>
                        <div className="text-xs text-gray-500">{log.details}</div>
                      </td>
                      <td className="px-4 py-3 text-sm">{log.user}</td>
                      <td className="px-4 py-3 text-sm font-mono">{log.ipAddress}</td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-1 rounded text-xs ${
                          log.success ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                        }`}>
                          {log.success ? 'SUCCESS' : 'FAILED'}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-1 rounded text-xs ${
                          log.riskLevel === 'low' ? 'bg-green-500/20 text-green-400' :
                          log.riskLevel === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
                          'bg-red-500/20 text-red-400'
                        }`}>
                          {log.riskLevel.toUpperCase()}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Access Policies Tab */}
        {activeTab === 'policies' && (
          <div className="space-y-4">
            {policies.map((policy) => (
              <div key={policy.id} className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="font-bold">{policy.name}</h3>
                    <p className="text-sm text-gray-500">Applies to: {policy.walletType} wallets</p>
                  </div>
                  <span className="px-3 py-1 bg-[#7c3aed]/20 text-[#7c3aed] rounded text-sm">
                    Active
                  </span>
                </div>

                <div className="grid grid-cols-4 gap-4 mb-4">
                  <div className="p-3 bg-[#0a0812] rounded text-center">
                    <div className="text-lg font-bold">{policy.requireMFA ? 'YES' : 'NO'}</div>
                    <div className="text-[10px] text-gray-500">MFA REQUIRED</div>
                  </div>
                  <div className="p-3 bg-[#0a0812] rounded text-center">
                    <div className="text-lg font-bold">{policy.requireHardwareKey ? 'YES' : 'NO'}</div>
                    <div className="text-[10px] text-gray-500">HARDWARE KEY</div>
                  </div>
                  <div className="p-3 bg-[#0a0812] rounded text-center">
                    <div className="text-lg font-bold">{policy.approvalCount}</div>
                    <div className="text-[10px] text-gray-500">APPROVALS</div>
                  </div>
                  <div className="p-3 bg-[#0a0812] rounded text-center">
                    <div className="text-lg font-bold">{policy.timeDelay}h</div>
                    <div className="text-[10px] text-gray-500">TIME DELAY</div>
                  </div>
                </div>

                <div className="flex gap-2">
                  <button className="px-3 py-1.5 bg-gray-800 rounded text-xs text-gray-400 hover:bg-gray-700 transition-all">
                    EDIT POLICY
                  </button>
                  <button className="px-3 py-1.5 bg-gray-800 rounded text-xs text-gray-400 hover:bg-gray-700 transition-all">
                    VIEW LOGS
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Access Control Tab */}
        {activeTab === 'access' && (
          <div className="grid grid-cols-2 gap-6">
            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-bold mb-4">Authorized Users</h3>
              <div className="space-y-3">
                {[
                  { name: 'Admin', role: 'Super Admin', access: 'All Wallets', mfa: true, lastAccess: '2 mins ago' },
                  { name: 'Treasury Team', role: 'Multi-sig Signer', access: 'Treasury Only', mfa: true, lastAccess: '1 hour ago' },
                  { name: 'Operations', role: 'Limited', access: 'Hot Wallets', mfa: false, lastAccess: '3 hours ago' },
                ].map((user, idx) => (
                  <div key={idx} className="p-3 bg-[#0a0812] rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-semibold">{user.name}</span>
                      <span className="px-2 py-0.5 bg-gray-800 rounded text-[10px]">{user.role}</span>
                    </div>
                    <div className="text-xs text-gray-500">
                      Access: {user.access} • MFA: {user.mfa ? 'Enabled' : 'Disabled'}
                    </div>
                    <div className="text-xs text-gray-400 mt-1">
                      Last access: {user.lastAccess}
                    </div>
                  </div>
                ))}
              </div>
              <button className="w-full mt-4 py-2 border border-dashed border-gray-700 rounded text-gray-500 hover:border-[#7c3aed] hover:text-[#7c3aed] transition-all">
                + ADD USER
              </button>
            </div>

            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-bold mb-4">IP Whitelist</h3>
              <div className="space-y-2">
                {['192.168.1.0/24', '10.0.0.0/8', '45.142.212.10'].map((ip, idx) => (
                  <div key={idx} className="flex items-center justify-between p-2 bg-[#0a0812] rounded">
                    <span className="font-mono text-sm">{ip}</span>
                    <button className="p-1 text-red-400 hover:text-red-300">
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
              <div className="mt-4">
                <input
                  type="text"
                  placeholder="Add IP address or range..."
                  className="w-full px-3 py-2 bg-[#0a0812] border border-gray-800 rounded text-sm"
                />
                <button className="w-full mt-2 py-2 bg-[#7c3aed] text-white rounded text-sm hover:bg-[#6d28d9] transition-all">
                  ADD IP
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Add Wallet Modal */}
      {showAddWallet && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-[#1a1525] border border-gray-800 rounded-lg p-6 w-[500px] max-w-[90vw]">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold">Add New Wallet</h2>
              <button onClick={() => setShowAddWallet(false)} className="p-1 hover:bg-gray-800 rounded">
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-500 mb-1">Wallet Name</label>
                <input
                  type="text"
                  value={newWallet.name}
                  onChange={(e) => setNewWallet({ ...newWallet, name: e.target.value })}
                  className="w-full px-3 py-2 bg-[#0a0812] border border-gray-800 rounded"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-gray-500 mb-1">Chain</label>
                  <select
                    value={newWallet.chain}
                    onChange={(e) => setNewWallet({ ...newWallet, chain: e.target.value as ChainType })}
                    className="w-full px-3 py-2 bg-[#0a0812] border border-gray-800 rounded"
                  >
                    <option value="ethereum">Ethereum</option>
                    <option value="bitcoin">Bitcoin</option>
                    <option value="solana">Solana</option>
                    <option value="base">Base</option>
                    <option value="arbitrum">Arbitrum</option>
                    <option value="polygon">Polygon</option>
                    <option value="bsc">BSC</option>
                    <option value="avalanche">Avalanche</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm text-gray-500 mb-1">Type</label>
                  <select
                    value={newWallet.type}
                    onChange={(e) => setNewWallet({ ...newWallet, type: e.target.value as WalletType })}
                    className="w-full px-3 py-2 bg-[#0a0812] border border-gray-800 rounded"
                  >
                    <option value="hot">Hot Wallet</option>
                    <option value="warm">Warm Wallet</option>
                    <option value="cold">Cold Wallet</option>
                    <option value="hardware">Hardware</option>
                    <option value="multisig">Multi-Sig</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-sm text-gray-500 mb-1">Security Level</label>
                <select
                  value={newWallet.securityLevel}
                  onChange={(e) => setNewWallet({ ...newWallet, securityLevel: e.target.value as SecurityLevel })}
                  className="w-full px-3 py-2 bg-[#0a0812] border border-gray-800 rounded"
                >
                  <option value="standard">Standard</option>
                  <option value="enhanced">Enhanced</option>
                  <option value="maximum">Maximum</option>
                  <option value="airgap">Air Gap</option>
                </select>
              </div>
              <div>
                <label className="block text-sm text-gray-500 mb-1">Purpose</label>
                <textarea
                  value={newWallet.purpose}
                  onChange={(e) => setNewWallet({ ...newWallet, purpose: e.target.value })}
                  rows={2}
                  className="w-full px-3 py-2 bg-[#0a0812] border border-gray-800 rounded"
                />
              </div>
              {newWallet.type === 'multisig' && (
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm text-gray-500 mb-1">Required Signers</label>
                    <input
                      type="number"
                      value={newWallet.multisigRequired}
                      onChange={(e) => setNewWallet({ ...newWallet, multisigRequired: parseInt(e.target.value) })}
                      className="w-full px-3 py-2 bg-[#0a0812] border border-gray-800 rounded"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-500 mb-1">Total Signers</label>
                    <input
                      type="number"
                      value={newWallet.multisigTotal}
                      onChange={(e) => setNewWallet({ ...newWallet, multisigTotal: parseInt(e.target.value) })}
                      className="w-full px-3 py-2 bg-[#0a0812] border border-gray-800 rounded"
                    />
                  </div>
                </div>
              )}
              <div className="flex gap-3 pt-4">
                <button className="flex-1 py-2 bg-[#7c3aed] text-white rounded hover:bg-[#6d28d9] transition-all">
                  GENERATE WALLET
                </button>
                <button
                  onClick={() => setShowAddWallet(false)}
                  className="px-4 py-2 bg-gray-800 text-gray-400 rounded hover:bg-gray-700 transition-all"
                >
                  CANCEL
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Key Reveal Security Modal */}
      {showKeyReveal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50">
          <div className="bg-[#1a1525] border border-[#7c3aed]/30 rounded-lg p-6 w-[500px] max-w-[90vw]">
            <div className="flex items-center gap-3 mb-4">
              <Shield className="w-8 h-8 text-[#7c3aed]" />
              <h2 className="text-lg font-bold">Security Verification Required</h2>
            </div>

            <div className="space-y-4">
              <div className="flex items-center gap-4">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${securityChallenge.step >= 1 ? 'bg-green-500/20 text-green-400' : 'bg-gray-800'}`}>
                  {securityChallenge.step >= 1 ? <CheckCircle className="w-4 h-4" /> : '1'}
                </div>
                <div className="flex-1">
                  <div className="font-semibold">Multi-Factor Authentication</div>
                  {securityChallenge.step === 1 && (
                    <div className="mt-2">
                      <input
                        type="text"
                        placeholder="Enter MFA code"
                        value={securityChallenge.mfaCode}
                        onChange={(e) => setSecurityChallenge({ ...securityChallenge, mfaCode: e.target.value })}
                        className="w-full px-3 py-2 bg-[#0a0812] border border-gray-800 rounded text-sm"
                      />
                    </div>
                  )}
                </div>
              </div>

              <div className="flex items-center gap-4">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${securityChallenge.step >= 2 ? 'bg-green-500/20 text-green-400' : 'bg-gray-800'}`}>
                  {securityChallenge.step >= 2 ? <CheckCircle className="w-4 h-4" /> : '2'}
                </div>
                <div className="flex-1">
                  <div className="font-semibold">Hardware Key Verification</div>
                  {securityChallenge.step === 2 && (
                    <div className="mt-2 p-3 bg-yellow-500/10 border border-yellow-500/30 rounded text-sm text-yellow-400">
                      <AlertTriangle className="w-4 h-4 inline mr-2" />
                      Insert and touch your YubiKey to continue
                    </div>
                  )}
                </div>
              </div>

              <div className="flex items-center gap-4">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${securityChallenge.step >= 3 ? 'bg-green-500/20 text-green-400' : 'bg-gray-800'}`}>
                  {securityChallenge.step >= 3 ? <CheckCircle className="w-4 h-4" /> : '3'}
                </div>
                <div className="flex-1">
                  <div className="font-semibold">Key Reveal</div>
                  {securityChallenge.step === 3 && (
                    <div className="mt-2 p-3 bg-[#0a0812] rounded text-sm">
                      <p className="text-gray-400">Your key will be displayed for 30 seconds only.</p>
                    </div>
                  )}
                </div>
              </div>
            </div>

            <div className="flex gap-3 pt-6">
              {securityChallenge.step < 3 ? (
                <button
                  onClick={handleSecurityStep}
                  className="flex-1 py-2 bg-[#7c3aed] text-white rounded hover:bg-[#6d28d9] transition-all"
                >
                  {securityChallenge.step === 1 ? 'VERIFY MFA' : 'CONFIRM HARDWARE KEY'}
                </button>
              ) : (
                <button
                  onClick={handleSecurityStep}
                  className="flex-1 py-2 bg-red-500/20 border border-red-500/30 text-red-400 rounded hover:bg-red-500/30 transition-all"
                >
                  <Eye className="w-4 h-4 inline mr-2" />
                  REVEAL KEY (30s)
                </button>
              )}
              <button
                onClick={() => setShowKeyReveal(false)}
                className="px-4 py-2 bg-gray-800 text-gray-400 rounded hover:bg-gray-700 transition-all"
              >
                CANCEL
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SecureWalletManager;
