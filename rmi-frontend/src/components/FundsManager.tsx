import React, { useState } from 'react';
import {
  DollarSign,
  Receipt,
  FileText,
  Calculator,
  Calendar,
  TrendingUp,
  TrendingDown,
  PieChart,
  BarChart3,
  Download,
  Upload,
  Plus,
  Trash2,
  Edit3,
  Search,
  Filter,
  CheckCircle,
  AlertTriangle,
  Clock,
  Wallet,
  CreditCard,
  Banknote,
  Landmark,
  ArrowUpRight,
  ArrowDownRight,
  Tag,
  Folder,
  ChevronDown,
  ChevronUp,
  MoreHorizontal,
  Copy,
  ExternalLink,
  X,
  Save,
  Printer,
  Mail,
  FileSpreadsheet,
  Briefcase,
  Globe,
  Bitcoin,
  Coins,
  Percent,
  Scale,
  Shield,
  CheckSquare,
  Square,
  RefreshCw,
  AlertCircle,
  Lock,
  Unlock
} from 'lucide-react';

type TransactionType = 'income' | 'expense' | 'transfer' | 'conversion';
type Currency = 'USD' | 'USDC' | 'USDT' | 'ETH' | 'BTC' | 'CRM' | 'EUR';
type ExpenseCategory = 'development' | 'marketing' | 'operations' | 'legal' | 'infrastructure' | 'personnel' | 'professional_services' | 'travel' | 'software' | 'hardware' | 'other';
type IncomeCategory = 'token_sales' | 'service_revenue' | 'consulting' | 'nft_sales' | 'staking_rewards' | 'partnerships' | 'grants' | 'other';
type TaxStatus = 'pending' | 'filed' | 'paid' | 'overdue';

interface Transaction {
  id: string;
  date: string;
  type: TransactionType;
  category: ExpenseCategory | IncomeCategory;
  description: string;
  amount: number;
  currency: Currency;
  usdValue: number;
  wallet?: string;
  txHash?: string;
  receiptUrl?: string;
  tags: string[];
  deductible: boolean;
  taxYear: number;
  audited: boolean;
  notes: string;
}

interface TaxDocument {
  id: string;
  name: string;
  type: '1099' | 'w2' | 'k1' | 'schedule_c' | 'quarterly_estimate' | 'annual_return' | 'receipt' | 'invoice';
  year: number;
  status: TaxStatus;
  amount?: number;
  dueDate?: string;
  filedDate?: string;
  documentUrl?: string;
  jurisdiction: 'federal' | 'wyoming' | 'delaware' | 'international';
}

interface Budget {
  id: string;
  category: string;
  allocated: number;
  spent: number;
  remaining: number;
  period: 'monthly' | 'quarterly' | 'annual';
  alerts: boolean;
  alertThreshold: number;
}

interface FundSource {
  id: string;
  name: string;
  type: 'treasury' | 'trading' | 'investment' | 'operational' | 'reserve';
  balance: number;
  currency: Currency;
  walletAddress?: string;
  lastUpdated: string;
}

const FundsManager: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'transactions' | 'taxes' | 'budget' | 'reports'>('overview');

  // Transactions State
  const [transactions, setTransactions] = useState<Transaction[]>([
    {
      id: 'tx1',
      date: '2026-04-14',
      type: 'expense',
      category: 'development',
      description: 'AI Infrastructure - AWS Compute',
      amount: 2847.50,
      currency: 'USD',
      usdValue: 2847.50,
      receiptUrl: 'https://receipts.rugmunch.com/aws-apr-2026.pdf',
      tags: ['infrastructure', 'ai', 'monthly'],
      deductible: true,
      taxYear: 2026,
      audited: true,
      notes: 'GPT-4 API costs and server hosting'
    },
    {
      id: 'tx2',
      date: '2026-04-13',
      type: 'income',
      category: 'service_revenue',
      description: 'Rug Pull Rehab - Client Session Package',
      amount: 500,
      currency: 'USDC',
      usdValue: 500,
      wallet: '0x742d...C0E',
      txHash: '0xabc123...def456',
      tags: ['rehab', 'services', 'recurring'],
      deductible: false,
      taxYear: 2026,
      audited: true,
      notes: '5-session package paid in full'
    },
    {
      id: 'tx3',
      date: '2026-04-12',
      type: 'expense',
      category: 'marketing',
      description: 'Twitter/X Promoted Posts',
      amount: 1200,
      currency: 'USD',
      usdValue: 1200,
      receiptUrl: 'https://receipts.rugmunch.com/twitter-apr-2026.pdf',
      tags: ['marketing', 'social', 'ads'],
      deductible: true,
      taxYear: 2026,
      audited: false,
      notes: 'Q2 marketing campaign'
    },
    {
      id: 'tx4',
      date: '2026-04-10',
      type: 'expense',
      category: 'professional_services',
      description: 'Legal Consultation - Token Structure',
      amount: 5000,
      currency: 'USD',
      usdValue: 5000,
      receiptUrl: 'https://receipts.rugmunch.com/legal-apr-2026.pdf',
      tags: ['legal', 'compliance', 'one-time'],
      deductible: true,
      taxYear: 2026,
      audited: true,
      notes: 'Wyoming DAO LLC setup and token compliance review'
    },
    {
      id: 'tx5',
      date: '2026-04-08',
      type: 'income',
      category: 'token_sales',
      description: '$CRM V2 Private Sale - Investor 1',
      amount: 25000,
      currency: 'USDC',
      usdValue: 25000,
      wallet: '0x8ba1...8C',
      txHash: '0x789xyz...abc123',
      tags: ['crm', 'token-sale', 'private-round'],
      deductible: false,
      taxYear: 2026,
      audited: true,
      notes: 'Seed round allocation'
    },
    {
      id: 'tx6',
      date: '2026-04-05',
      type: 'expense',
      category: 'personnel',
      description: 'Contractor Payment - Frontend Dev',
      amount: 8000,
      currency: 'USD',
      usdValue: 8000,
      tags: ['contractor', 'dev', 'monthly'],
      deductible: true,
      taxYear: 2026,
      audited: true,
      notes: 'Monthly retainer - 1099 issued'
    },
    {
      id: 'tx7',
      date: '2026-04-01',
      type: 'expense',
      category: 'software',
      description: 'Annual SaaS Subscriptions',
      amount: 3600,
      currency: 'USD',
      usdValue: 3600,
      receiptUrl: 'https://receipts.rugmunch.com/saas-annual-2026.pdf',
      tags: ['software', 'tools', 'annual'],
      deductible: true,
      taxYear: 2026,
      audited: true,
      notes: 'Notion, GitHub, Vercel, Figma, etc.'
    },
    {
      id: 'tx8',
      date: '2026-03-28',
      type: 'conversion',
      category: 'other',
      description: 'ETH to USDC Conversion - Treasury Management',
      amount: 50000,
      currency: 'USDC',
      usdValue: 50000,
      wallet: '0x742d...C0E',
      txHash: '0xconv123...456',
      tags: ['treasury', 'conversion', 'stablecoin'],
      deductible: false,
      taxYear: 2026,
      audited: true,
      notes: 'Converted 15.2 ETH at $3,289/ETH'
    }
  ]);

  // Tax Documents State
  const [taxDocuments, setTaxDocuments] = useState<TaxDocument[]>([
    {
      id: 'td1',
      name: 'Q2 2026 Estimated Tax Payment',
      type: 'quarterly_estimate',
      year: 2026,
      status: 'pending',
      amount: 15000,
      dueDate: '2026-06-15',
      jurisdiction: 'federal'
    },
    {
      id: 'td2',
      name: 'Q1 2026 Estimated Tax - PAID',
      type: 'quarterly_estimate',
      year: 2026,
      status: 'paid',
      amount: 12000,
      dueDate: '2026-04-15',
      filedDate: '2026-04-14',
      jurisdiction: 'federal'
    },
    {
      id: 'td3',
      name: '1099-NEC - Contractors 2025',
      type: '1099',
      year: 2025,
      status: 'filed',
      filedDate: '2026-01-31',
      jurisdiction: 'federal'
    },
    {
      id: 'td4',
      name: 'Wyoming Annual Report 2026',
      type: 'annual_return',
      year: 2026,
      status: 'pending',
      dueDate: '2026-12-31',
      jurisdiction: 'wyoming'
    }
  ]);

  // Budget State
  const [budgets, setBudgets] = useState<Budget[]>([
    {
      id: 'b1',
      category: 'Development',
      allocated: 25000,
      spent: 12847.50,
      remaining: 12152.50,
      period: 'monthly',
      alerts: true,
      alertThreshold: 80
    },
    {
      id: 'b2',
      category: 'Marketing',
      allocated: 15000,
      spent: 7200,
      remaining: 7800,
      period: 'monthly',
      alerts: true,
      alertThreshold: 75
    },
    {
      id: 'b3',
      category: 'Legal & Compliance',
      allocated: 20000,
      spent: 15000,
      remaining: 5000,
      period: 'quarterly',
      alerts: true,
      alertThreshold: 90
    },
    {
      id: 'b4',
      category: 'Operations',
      allocated: 10000,
      spent: 4500,
      remaining: 5500,
      period: 'monthly',
      alerts: false,
      alertThreshold: 100
    }
  ]);

  // Fund Sources
  const [fundSources] = useState<FundSource[]>([
    {
      id: 'fs1',
      name: 'Primary Treasury',
      type: 'treasury',
      balance: 2456789.45,
      currency: 'USDC',
      walletAddress: '0x742d...C0E',
      lastUpdated: '2026-04-14 14:30'
    },
    {
      id: 'fs2',
      name: 'ETH Holdings',
      type: 'investment',
      balance: 245.5,
      currency: 'ETH',
      walletAddress: '0x8ba1...8C',
      lastUpdated: '2026-04-14 14:30'
    },
    {
      id: 'fs3',
      name: 'Operating Account',
      type: 'operational',
      balance: 125000,
      currency: 'USD',
      lastUpdated: '2026-04-14 14:30'
    },
    {
      id: 'fs4',
      name: 'BTC Reserve',
      type: 'reserve',
      balance: 12.5,
      currency: 'BTC',
      walletAddress: 'bc1q...0wlh',
      lastUpdated: '2026-04-14 14:30'
    }
  ]);

  // UI State
  const [showAddTransaction, setShowAddTransaction] = useState(false);
  const [transactionFilter, setTransactionFilter] = useState<'all' | 'income' | 'expense'>('all');
  const [selectedTransactions, setSelectedTransactions] = useState<Set<string>>(new Set());

  // Stats
  const currentMonthIncome = transactions
    .filter(t => t.type === 'income' && t.date.startsWith('2026-04'))
    .reduce((acc, t) => acc + t.usdValue, 0);

  const currentMonthExpenses = transactions
    .filter(t => t.type === 'expense' && t.date.startsWith('2026-04'))
    .reduce((acc, t) => acc + t.usdValue, 0);

  const ytdIncome = transactions
    .filter(t => t.type === 'income')
    .reduce((acc, t) => acc + t.usdValue, 0);

  const ytdExpenses = transactions
    .filter(t => t.type === 'expense')
    .reduce((acc, t) => acc + t.usdValue, 0);

  const totalTaxOwed = taxDocuments
    .filter(t => t.status === 'pending')
    .reduce((acc, t) => acc + (t.amount || 0), 0);

  return (
    <div className="min-h-screen bg-[#0a0812] text-gray-100 font-mono selection:bg-[#7c3aed]/30">
      {/* Header */}
      <div className="bg-gradient-to-r from-[#0f0c1d] via-[#1a1525] to-[#0f0c1d] border-b border-[#7c3aed]/30">
        <div className="max-w-[1600px] mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-[#7c3aed]/20 rounded-full flex items-center justify-center">
                <Landmark className="w-5 h-5 text-[#7c3aed]" />
              </div>
              <div>
                <h1 className="text-xl font-bold tracking-wider">
                  FUNDS <span className="text-[#7c3aed]">COMMAND</span>
                </h1>
                <p className="text-xs text-gray-500 tracking-[0.2em]">FINANCIAL MANAGEMENT & TAX COMPLIANCE</p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 px-3 py-1.5 bg-green-500/10 border border-green-500/30 rounded">
                <TrendingUp className="w-4 h-4 text-green-400" />
                <span className="text-sm text-green-400">+${currentMonthIncome.toLocaleString()} MTD</span>
              </div>
              <div className="flex items-center gap-2 px-3 py-1.5 bg-red-500/10 border border-red-500/30 rounded">
                <TrendingDown className="w-4 h-4 text-red-400" />
                <span className="text-sm text-red-400">-${currentMonthExpenses.toLocaleString()} Expenses</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-[1600px] mx-auto p-6 space-y-6">
        {/* Stats Row */}
        <div className="grid grid-cols-6 gap-4">
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
            <Wallet className="w-5 h-5 text-green-400 mb-2" />
            <div className="text-xl font-bold text-green-400">${(ytdIncome / 1000).toFixed(1)}k</div>
            <div className="text-xs text-gray-500">YTD Income</div>
          </div>
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
            <CreditCard className="w-5 h-5 text-red-400 mb-2" />
            <div className="text-xl font-bold text-red-400">${(ytdExpenses / 1000).toFixed(1)}k</div>
            <div className="text-xs text-gray-500">YTD Expenses</div>
          </div>
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
            <Scale className="w-5 h-5 text-blue-400 mb-2" />
            <div className="text-xl font-bold text-blue-400">${((ytdIncome - ytdExpenses) / 1000).toFixed(1)}k</div>
            <div className="text-xs text-gray-500">Net Position</div>
          </div>
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
            <Percent className="w-5 h-5 text-yellow-400 mb-2" />
            <div className="text-xl font-bold text-yellow-400">{(ytdExpenses / ytdIncome * 100).toFixed(1)}%</div>
            <div className="text-xs text-gray-500">Burn Rate</div>
          </div>
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
            <Receipt className="w-5 h-5 text-purple-400 mb-2" />
            <div className="text-xl font-bold text-purple-400">${totalTaxOwed.toLocaleString()}</div>
            <div className="text-xs text-gray-500">Tax Due</div>
          </div>
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
            <Coins className="w-5 h-5 text-[#7c3aed] mb-2" />
            <div className="text-xl font-bold text-[#7c3aed]">${(fundSources[0].balance / 1000000).toFixed(2)}M</div>
            <div className="text-xs text-gray-500">Treasury</div>
          </div>
        </div>

        {/* Fund Sources */}
        <div className="grid grid-cols-4 gap-4">
          {fundSources.map((source) => (
            <div key={source.id} className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs text-gray-500 uppercase">{source.type}</span>
                <span className="text-xs text-gray-400">{source.currency}</span>
              </div>
              <div className="text-xl font-bold mb-1">
                {source.currency === 'USD' || source.currency === 'USDC' || source.currency === 'USDT'
                  ? `$${source.balance.toLocaleString()}`
                  : `${source.balance} ${source.currency}`
                }
              </div>
              <div className="text-xs text-gray-500">{source.name}</div>
              {source.walletAddress && (
                <div className="text-[10px] text-[#7c3aed] mt-1 font-mono">{source.walletAddress}</div>
              )}
            </div>
          ))}
        </div>

        {/* Navigation */}
        <div className="flex items-center gap-1 border-b border-gray-800">
          {[
            { id: 'overview', label: 'OVERVIEW', icon: <PieChart className="w-4 h-4" /> },
            { id: 'transactions', label: 'TRANSACTIONS', icon: <Receipt className="w-4 h-4" /> },
            { id: 'taxes', label: 'TAX COMPLIANCE', icon: <Calculator className="w-4 h-4" /> },
            { id: 'budget', label: 'BUDGET', icon: <BarChart3 className="w-4 h-4" /> },
            { id: 'reports', label: 'REPORTS', icon: <FileText className="w-4 h-4" /> },
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

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-2 gap-6">
            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-bold mb-4">Income vs Expenses (2026)</h3>
              <div className="h-64 bg-[#0a0812] rounded-lg flex items-center justify-center border border-gray-800">
                <div className="text-center text-gray-500">
                  <BarChart3 className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p>Financial chart integration</p>
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-bold mb-4">Expense Breakdown</h3>
              <div className="space-y-3">
                {['Development', 'Marketing', 'Legal', 'Operations', 'Software'].map((cat, idx) => {
                  const amount = transactions
                    .filter(t => t.type === 'expense' && t.category.toLowerCase().includes(cat.toLowerCase()))
                    .reduce((acc, t) => acc + t.usdValue, 0);
                  const total = ytdExpenses;
                  const pct = total > 0 ? (amount / total) * 100 : 0;
                  return (
                    <div key={idx}>
                      <div className="flex justify-between text-sm mb-1">
                        <span>{cat}</span>
                        <span>${amount.toLocaleString()} ({pct.toFixed(1)}%)</span>
                      </div>
                      <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-[#7c3aed] rounded-full"
                          style={{ width: `${pct}%` }}
                        ></div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-bold mb-4">Recent Transactions</h3>
              <div className="space-y-2">
                {transactions.slice(0, 5).map((tx) => (
                  <div key={tx.id} className="flex items-center justify-between p-3 bg-[#0a0812] rounded-lg">
                    <div>
                      <div className="font-semibold text-sm">{tx.description}</div>
                      <div className="text-xs text-gray-500">{tx.date}</div>
                    </div>
                    <div className={`font-semibold ${tx.type === 'income' ? 'text-green-400' : 'text-red-400'}`}>
                      {tx.type === 'income' ? '+' : '-'}${tx.usdValue.toLocaleString()}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-bold mb-4">Upcoming Tax Obligations</h3>
              <div className="space-y-3">
                {taxDocuments
                  .filter(t => t.status === 'pending')
                  .map((doc) => (
                    <div key={doc.id} className="p-3 bg-[#0a0812] rounded-lg border border-yellow-500/30">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-semibold">{doc.name}</span>
                        <span className="text-yellow-400 text-sm">{doc.status.toUpperCase()}</span>
                      </div>
                      <div className="flex items-center justify-between text-sm text-gray-500">
                        <span>Due: {doc.dueDate}</span>
                        {doc.amount && <span className="text-yellow-400">${doc.amount.toLocaleString()}</span>}
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          </div>
        )}

        {/* Transactions Tab */}
        {activeTab === 'transactions' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2 bg-[#0a0812] rounded-lg p-1">
                  {(['all', 'income', 'expense'] as const).map((filter) => (
                    <button
                      key={filter}
                      onClick={() => setTransactionFilter(filter)}
                      className={`px-3 py-1.5 rounded text-sm capitalize transition-all ${
                        transactionFilter === filter
                          ? 'bg-[#7c3aed] text-white'
                          : 'text-gray-400 hover:text-white'
                      }`}
                    >
                      {filter}
                    </button>
                  ))}
                </div>
                <div className="relative">
                  <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
                  <input
                    type="text"
                    placeholder="Search transactions..."
                    className="pl-10 pr-4 py-2 bg-[#0a0812] border border-gray-800 rounded text-sm w-64"
                  />
                </div>
              </div>
              <div className="flex items-center gap-2">
                <button className="flex items-center gap-2 px-3 py-2 bg-gray-800 border border-gray-700 rounded text-sm text-gray-400 hover:bg-gray-700 transition-all">
                  <Download className="w-4 h-4" />
                  EXPORT CSV
                </button>
                <button
                  onClick={() => setShowAddTransaction(true)}
                  className="flex items-center gap-2 px-4 py-2 bg-[#7c3aed] text-white rounded text-sm hover:bg-[#6d28d9] transition-all"
                >
                  <Plus className="w-4 h-4" />
                  ADD TRANSACTION
                </button>
              </div>
            </div>

            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg overflow-hidden">
              <table className="w-full">
                <thead className="bg-[#0f0c1d] border-b border-gray-800">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">DATE</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">DESCRIPTION</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">CATEGORY</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">AMOUNT</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">TYPE</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">DEDUCTIBLE</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">RECEIPT</th>
                  </tr>
                </thead>
                <tbody>
                  {transactions
                    .filter(t => transactionFilter === 'all' || t.type === transactionFilter)
                    .map((tx) => (
                    <tr key={tx.id} className="border-b border-gray-800 hover:bg-[#0a0812]/50 transition-all">
                      <td className="px-4 py-3 text-sm">{tx.date}</td>
                      <td className="px-4 py-3">
                        <div className="font-semibold text-sm">{tx.description}</div>
                        {tx.txHash && (
                          <div className="text-[10px] text-[#7c3aed]">TX: {tx.txHash}</div>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        <span className="px-2 py-1 bg-gray-800 rounded text-xs capitalize">
                          {tx.category.replace('_', ' ')}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <div className={`font-semibold ${tx.type === 'income' ? 'text-green-400' : 'text-red-400'}`}>
                          {tx.type === 'income' ? '+' : '-'}${tx.usdValue.toLocaleString()}
                        </div>
                        <div className="text-xs text-gray-500">
                          {tx.amount} {tx.currency}
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-1 rounded text-xs capitalize ${
                          tx.type === 'income' ? 'bg-green-500/20 text-green-400' :
                          tx.type === 'expense' ? 'bg-red-500/20 text-red-400' :
                          'bg-blue-500/20 text-blue-400'
                        }`}>
                          {tx.type}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        {tx.deductible ? (
                          <CheckCircle className="w-4 h-4 text-green-400" />
                        ) : (
                          <span className="text-gray-500">-</span>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        {tx.receiptUrl ? (
                          <a
                            href={tx.receiptUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center gap-1 text-xs text-[#7c3aed] hover:underline"
                          >
                            <ExternalLink className="w-3 h-3" />
                            VIEW
                          </a>
                        ) : (
                          <button className="px-2 py-1 bg-gray-800 rounded text-xs text-gray-400">
                            UPLOAD
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Taxes Tab */}
        {activeTab === 'taxes' && (
          <div className="space-y-6">
            <div className="grid grid-cols-4 gap-4">
              <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
                <div className="text-xs text-gray-500 mb-1">Total Tax Due</div>
                <div className="text-2xl font-bold text-yellow-400">${totalTaxOwed.toLocaleString()}</div>
              </div>
              <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
                <div className="text-xs text-gray-500 mb-1">Tax Year 2026</div>
                <div className="text-2xl font-bold">${(ytdIncome * 0.21).toLocaleString()}</div>
                <div className="text-xs text-gray-500">Estimated (21%)</div>
              </div>
              <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
                <div className="text-xs text-gray-500 mb-1">Deductible Expenses</div>
                <div className="text-2xl font-bold text-green-400">
                  ${transactions.filter(t => t.deductible).reduce((acc, t) => acc + t.usdValue, 0).toLocaleString()}
                </div>
              </div>
              <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
                <div className="text-xs text-gray-500 mb-1">Next Due Date</div>
                <div className="text-2xl font-bold text-red-400">Jun 15</div>
                <div className="text-xs text-gray-500">Q2 2026 Estimate</div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold">Tax Documents & Filings</h3>
                <button className="px-3 py-2 bg-[#7c3aed] text-white rounded text-sm hover:bg-[#6d28d9] transition-all">
                  <Plus className="w-4 h-4 inline mr-2" />
                  ADD DOCUMENT
                </button>
              </div>
              <div className="space-y-3">
                {taxDocuments.map((doc) => (
                  <div key={doc.id} className="flex items-center justify-between p-4 bg-[#0a0812] rounded-lg">
                    <div className="flex items-center gap-3">
                      <FileText className="w-5 h-5 text-gray-400" />
                      <div>
                        <div className="font-semibold">{doc.name}</div>
                        <div className="text-xs text-gray-500">
                          {doc.type.replace('_', ' ').toUpperCase()} • {doc.jurisdiction.toUpperCase()} • {doc.year}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      {doc.amount && (
                        <span className="font-semibold">${doc.amount.toLocaleString()}</span>
                      )}
                      {doc.dueDate && (
                        <span className="text-sm text-gray-400">Due: {doc.dueDate}</span>
                      )}
                      <span className={`px-2 py-1 rounded text-xs ${
                        doc.status === 'paid' ? 'bg-green-500/20 text-green-400' :
                        doc.status === 'pending' ? 'bg-yellow-500/20 text-yellow-400' :
                        doc.status === 'filed' ? 'bg-blue-500/20 text-blue-400' :
                        'bg-red-500/20 text-red-400'
                      }`}>
                        {doc.status.toUpperCase()}
                      </span>
                      <button className="p-1.5 bg-gray-800 rounded hover:bg-gray-700 transition-all">
                        <Download className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-6">
              <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
                <h3 className="text-lg font-bold mb-4">Tax Settings</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm text-gray-500 mb-1">Entity Type</label>
                    <select className="w-full px-3 py-2 bg-[#0a0812] border border-gray-800 rounded text-sm">
                      <option>Wyoming DAO LLC</option>
                      <option>Delaware C-Corp</option>
                      <option>Foreign Entity</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm text-gray-500 mb-1">Tax ID (EIN)</label>
                    <input
                      type="text"
                      value="XX-XXXXXXX"
                      readOnly
                      className="w-full px-3 py-2 bg-[#0a0812] border border-gray-800 rounded text-sm font-mono"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-500 mb-1">Fiscal Year End</label>
                    <input
                      type="text"
                      value="December 31"
                      readOnly
                      className="w-full px-3 py-2 bg-[#0a0812] border border-gray-800 rounded text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-500 mb-1">Accounting Method</label>
                    <select className="w-full px-3 py-2 bg-[#0a0812] border border-gray-800 rounded text-sm">
                      <option>Accrual</option>
                      <option>Cash</option>
                    </select>
                  </div>
                </div>
              </div>

              <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
                <h3 className="text-lg font-bold mb-4">Crypto Tax Rules</h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 bg-[#0a0812] rounded-lg">
                    <span className="text-sm">Track all token sales</span>
                    <CheckCircle className="w-4 h-4 text-green-400" />
                  </div>
                  <div className="flex items-center justify-between p-3 bg-[#0a0812] rounded-lg">
                    <span className="text-sm">Report staking rewards as income</span>
                    <CheckCircle className="w-4 h-4 text-green-400" />
                  </div>
                  <div className="flex items-center justify-between p-3 bg-[#0a0812] rounded-lg">
                    <span className="text-sm">Calculate cost basis (FIFO)</span>
                    <CheckCircle className="w-4 h-4 text-green-400" />
                  </div>
                  <div className="flex items-center justify-between p-3 bg-[#0a0812] rounded-lg">
                    <span className="text-sm">Report airdrops as income</span>
                    <CheckCircle className="w-4 h-4 text-green-400" />
                  </div>
                  <div className="flex items-center justify-between p-3 bg-[#0a0812] rounded-lg">
                    <span className="text-sm">Gas fee deductions</span>
                    <CheckCircle className="w-4 h-4 text-green-400" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Budget Tab */}
        {activeTab === 'budget' && (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h2 className="text-lg font-bold">Budget Tracking</h2>
              <button className="px-4 py-2 bg-[#7c3aed] text-white rounded text-sm hover:bg-[#6d28d9] transition-all">
                <Plus className="w-4 h-4 inline mr-2" />
                NEW BUDGET
              </button>
            </div>

            <div className="grid grid-cols-2 gap-4">
              {budgets.map((budget) => {
                const pctUsed = (budget.spent / budget.allocated) * 100;
                const isAlert = budget.alerts && pctUsed >= budget.alertThreshold;
                return (
                  <div key={budget.id} className={`bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border rounded-lg p-5 ${
                    isAlert ? 'border-red-500/50' : 'border-gray-800'
                  }`}>
                    <div className="flex items-start justify-between mb-4">
                      <div>
                        <h3 className="font-bold">{budget.category}</h3>
                        <p className="text-xs text-gray-500 capitalize">{budget.period} Budget</p>
                      </div>
                      {isAlert && <AlertTriangle className="w-5 h-5 text-red-400" />}
                    </div>

                    <div className="space-y-2 mb-4">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-500">Allocated:</span>
                        <span className="font-semibold">${budget.allocated.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-500">Spent:</span>
                        <span className={`font-semibold ${isAlert ? 'text-red-400' : ''}`}>
                          ${budget.spent.toLocaleString()} ({pctUsed.toFixed(1)}%)
                        </span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-500">Remaining:</span>
                        <span className="font-semibold text-green-400">${budget.remaining.toLocaleString()}</span>
                      </div>
                    </div>

                    <div className="h-2 bg-gray-800 rounded-full overflow-hidden mb-4">
                      <div
                        className={`h-full rounded-full ${isAlert ? 'bg-red-400' : 'bg-[#7c3aed]'}`}
                        style={{ width: `${Math.min(pctUsed, 100)}%` }}
                      ></div>
                    </div>

                    <div className="flex gap-2">
                      <button className="flex-1 py-2 bg-gray-800 rounded text-xs text-gray-400 hover:bg-gray-700 transition-all">
                        EDIT
                      </button>
                      <button className="flex-1 py-2 bg-[#7c3aed]/10 border border-[#7c3aed]/30 rounded text-xs text-[#7c3aed] hover:bg-[#7c3aed]/20 transition-all">
                        VIEW DETAILS
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Reports Tab */}
        {activeTab === 'reports' && (
          <div className="space-y-6">
            <div className="grid grid-cols-3 gap-4">
              {[
                { name: 'Profit & Loss Statement', desc: 'Monthly P&L with crypto adjustments', format: 'PDF' },
                { name: 'Balance Sheet', desc: 'Assets, liabilities, equity', format: 'PDF' },
                { name: 'Cash Flow Statement', desc: 'Operating, investing, financing', format: 'PDF' },
                { name: 'Trial Balance', desc: 'All accounts with balances', format: 'CSV' },
                { name: 'General Ledger', desc: 'Complete transaction history', format: 'CSV' },
                { name: 'Crypto Gains/Losses', desc: 'Tax-ready capital gains report', format: 'CSV' },
              ].map((report, idx) => (
                <div key={idx} className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-5">
                  <div className="flex items-start justify-between mb-3">
                    <FileText className="w-8 h-8 text-[#7c3aed]" />
                    <span className="text-xs px-2 py-1 bg-gray-800 rounded">{report.format}</span>
                  </div>
                  <h3 className="font-bold mb-1">{report.name}</h3>
                  <p className="text-xs text-gray-500 mb-4">{report.desc}</p>
                  <div className="flex gap-2">
                    <button className="flex-1 py-2 bg-[#7c3aed]/10 border border-[#7c3aed]/30 rounded text-xs text-[#7c3aed] hover:bg-[#7c3aed]/20 transition-all">
                      <Download className="w-3 h-3 inline mr-1" />
                      DOWNLOAD
                    </button>
                    <button className="px-3 py-2 bg-gray-800 rounded text-xs text-gray-400 hover:bg-gray-700 transition-all">
                      <Mail className="w-3 h-3" />
                    </button>
                  </div>
                </div>
              ))}
            </div>

            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-bold mb-4">Scheduled Reports</h3>
              <div className="space-y-3">
                {[
                  { report: 'Weekly Financial Summary', frequency: 'Every Monday', recipients: 'admin@rugmunch.com' },
                  { report: 'Monthly P&L Statement', frequency: '1st of month', recipients: 'accountant@rugmunch.com' },
                  { report: 'Quarterly Tax Estimate', frequency: 'Quarterly', recipients: 'tax@rugmunch.com' },
                ].map((sched, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 bg-[#0a0812] rounded-lg">
                    <div>
                      <div className="font-semibold">{sched.report}</div>
                      <div className="text-xs text-gray-500">{sched.frequency} • {sched.recipients}</div>
                    </div>
                    <div className="flex gap-2">
                      <button className="px-2 py-1 bg-gray-800 rounded text-xs text-gray-400">EDIT</button>
                      <button className="px-2 py-1 bg-red-500/10 text-red-400 rounded text-xs">DISABLE</button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default FundsManager;
