import { useState } from 'react';
import { CreditCard, Wallet, ArrowRightLeft, RefreshCw, DollarSign, Bitcoin, QrCode, Copy, CheckCircle2, AlertCircle, History, Plus, Settings, Shield, Zap, Globe, Link2, BarChart3, PieChart, Calendar, Filter, ExternalLink, ChevronDown, Lock, Unlock } from 'lucide-react';
import { useAppStore } from '../store/appStore';

interface PaymentLink {
  id: string;
  name: string;
  type: 'product' | 'subscription' | 'donation' | 'invoice';
  amount: number;
  currency: 'USD' | 'ETH' | 'USDC' | 'BTC' | 'CRM';
  status: 'active' | 'paused' | 'expired';
  url: string;
  createdAt: string;
  totalPayments: number;
  totalRevenue: number;
  allowedMethods: string[];
}

interface ConnectedApp {
  id: string;
  name: string;
  type: 'bot' | 'service' | 'app' | 'api';
  status: 'connected' | 'disconnected' | 'error';
  monthlyCost: number;
  lastPayment: string;
  nextPayment: string;
  paymentMethod: string;
  autoRenew: boolean;
}

interface ReceivedPayment {
  id: string;
  source: string;
  amount: number;
  currency: string;
  method: 'stripe' | 'crypto' | 'paypal' | 'manual';
  timestamp: string;
  status: 'confirmed' | 'pending' | 'failed';
  product: string;
  txHash?: string;
}

const mockPaymentLinks: PaymentLink[] = [
  {
    id: '1',
    name: 'Rug Pull Rehab - Initial Consultation',
    type: 'product',
    amount: 150,
    currency: 'USD',
    status: 'active',
    url: 'https://pay.rugmunch.com/rehab-consult',
    createdAt: '2026-03-15',
    totalPayments: 23,
    totalRevenue: 3450,
    allowedMethods: ['stripe', 'usdc', 'eth']
  },
  {
    id: '2',
    name: 'Daily Intelligence Briefing - Monthly',
    type: 'subscription',
    amount: 5,
    currency: 'USD',
    status: 'active',
    url: 'https://pay.rugmunch.com/newsletter-monthly',
    createdAt: '2026-02-01',
    totalPayments: 156,
    totalRevenue: 780,
    allowedMethods: ['stripe', 'crypto']
  },
  {
    id: '3',
    name: 'MunchMaps API Access - Pro Tier',
    type: 'subscription',
    amount: 99,
    currency: 'USD',
    status: 'active',
    url: 'https://pay.rugmunch.com/api-pro',
    createdAt: '2026-01-20',
    totalPayments: 42,
    totalRevenue: 4158,
    allowedMethods: ['stripe', 'usdc', 'eth']
  },
  {
    id: '4',
    name: 'Custom Wallet Analysis Report',
    type: 'product',
    amount: 250,
    currency: 'USD',
    status: 'active',
    url: 'https://pay.rugmunch.com/wallet-report',
    createdAt: '2026-03-01',
    totalPayments: 8,
    totalRevenue: 2000,
    allowedMethods: ['stripe', 'crypto', 'crm']
  },
  {
    id: '5',
    name: 'Enterprise Rug Pull Recovery',
    type: 'product',
    amount: 5000,
    currency: 'USD',
    status: 'paused',
    url: 'https://pay.rugmunch.com/enterprise-recovery',
    createdAt: '2026-02-15',
    totalPayments: 2,
    totalRevenue: 10000,
    allowedMethods: ['stripe', 'wire', 'usdc']
  }
];

const mockConnectedApps: ConnectedApp[] = [
  {
    id: '1',
    name: 'Rug Muncher Bot - Twitter API',
    type: 'bot',
    status: 'connected',
    monthlyCost: 100,
    lastPayment: '2026-04-01',
    nextPayment: '2026-05-01',
    paymentMethod: 'Stripe Card ****4242',
    autoRenew: true
  },
  {
    id: '2',
    name: 'MunchMaps - Alchemy RPC',
    type: 'api',
    status: 'connected',
    monthlyCost: 350,
    lastPayment: '2026-04-05',
    nextPayment: '2026-05-05',
    paymentMethod: 'Stripe Card ****4242',
    autoRenew: true
  },
  {
    id: '3',
    name: 'OpenAI API - GPT-4/Claude',
    type: 'api',
    status: 'connected',
    monthlyCost: 800,
    lastPayment: '2026-04-10',
    nextPayment: '2026-05-10',
    paymentMethod: 'Crypto (USDC)',
    autoRenew: true
  },
  {
    id: '4',
    name: 'Vercel - Frontend Hosting',
    type: 'service',
    status: 'connected',
    monthlyCost: 20,
    lastPayment: '2026-04-01',
    nextPayment: '2026-05-01',
    paymentMethod: 'Stripe Card ****4242',
    autoRenew: true
  },
  {
    id: '5',
    name: 'n8n - Automation Server',
    type: 'service',
    status: 'error',
    monthlyCost: 50,
    lastPayment: '2026-03-01',
    nextPayment: 'OVERDUE',
    paymentMethod: 'Crypto (USDC)',
    autoRenew: false
  }
];

const mockReceivedPayments: ReceivedPayment[] = [
  {
    id: '1',
    source: 'john@example.com',
    amount: 150,
    currency: 'USD',
    method: 'stripe',
    timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
    status: 'confirmed',
    product: 'Rug Pull Rehab - Initial Consultation'
  },
  {
    id: '2',
    source: '0x742d...6C7E',
    amount: 0.05,
    currency: 'ETH',
    method: 'crypto',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
    status: 'confirmed',
    product: 'Daily Intelligence Briefing - Annual',
    txHash: '0xabc123...'
  },
  {
    id: '3',
    source: 'sarah@example.com',
    amount: 99,
    currency: 'USD',
    method: 'stripe',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 5).toISOString(),
    status: 'confirmed',
    product: 'MunchMaps API Access - Pro Tier'
  },
  {
    id: '4',
    source: '0x1234...5678',
    amount: 500,
    currency: 'USDC',
    method: 'crypto',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 8).toISOString(),
    status: 'pending',
    product: 'Enterprise Rug Pull Recovery',
    txHash: '0xdef456...'
  }
];

export default function PaymentCenter() {
  const { theme } = useAppStore();
  const darkMode = theme === 'dark';

  const [activeTab, setActiveTab] = useState<'incoming' | 'outgoing' | 'links' | 'connected'>('incoming');
  const [paymentLinks] = useState<PaymentLink[]>(mockPaymentLinks);
  const [connectedApps] = useState<ConnectedApp[]>(mockConnectedApps);
  const [receivedPayments] = useState<ReceivedPayment[]>(mockReceivedPayments);

  const totalIncoming24h = receivedPayments
    .filter(p => new Date(p.timestamp).getTime() > Date.now() - 24 * 60 * 60 * 1000)
    .reduce((acc, p) => acc + p.amount, 0);

  const totalOutgoingMonthly = connectedApps
    .filter(a => a.status === 'connected')
    .reduce((acc, a) => acc + a.monthlyCost, 0);

  const totalRevenueAllTime = paymentLinks.reduce((acc, link) => acc + link.totalRevenue, 0);

  const formatTimeAgo = (timestamp: string) => {
    const diff = Date.now() - new Date(timestamp).getTime();
    const minutes = Math.floor(diff / 60000);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    return `${Math.floor(hours / 24)}d ago`;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
        <div className="flex items-center gap-3 mb-2">
          <CreditCard className="w-8 h-8 text-green-500" />
          <h1 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
            PAYMENT CENTER
          </h1>
          <span className="px-2 py-1 bg-green-500/10 text-green-400 text-xs font-mono rounded">
            FINANCIAL HUB
          </span>
        </div>
        <p className={`${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
          Unified payment management for all RMI products, services, and infrastructure. Accept payments via Stripe, crypto, and traditional methods.
        </p>
      </div>

      {/* Financial Overview */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
          <div className="flex items-center gap-2 mb-1">
            <ArrowRightLeft className="w-4 h-4 text-green-400" />
            <span className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>24h Incoming</span>
          </div>
          <p className="text-2xl font-bold text-green-400">${totalIncoming24h.toFixed(2)}</p>
          <p className={`text-xs ${darkMode ? 'text-slate-500' : 'text-slate-500'}`}>+12% from yesterday</p>
        </div>
        <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
          <div className="flex items-center gap-2 mb-1">
            <CreditCard className="w-4 h-4 text-red-400" />
            <span className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Monthly Outgoing</span>
          </div>
          <p className="text-2xl font-bold text-red-400">${totalOutgoingMonthly}</p>
          <p className={`text-xs ${darkMode ? 'text-slate-500' : 'text-slate-500'}`}>Infrastructure costs</p>
        </div>
        <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
          <div className="flex items-center gap-2 mb-1">
            <DollarSign className="w-4 h-4 text-purple-400" />
            <span className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Total Revenue</span>
          </div>
          <p className="text-2xl font-bold text-purple-400">${totalRevenueAllTime.toLocaleString()}</p>
          <p className={`text-xs ${darkMode ? 'text-slate-500' : 'text-slate-500'}`}>All time</p>
        </div>
        <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
          <div className="flex items-center gap-2 mb-1">
            <Wallet className="w-4 h-4 text-blue-400" />
            <span className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Active Links</span>
          </div>
          <p className="text-2xl font-bold text-blue-400">{paymentLinks.filter(l => l.status === 'active').length}</p>
          <p className={`text-xs ${darkMode ? 'text-slate-500' : 'text-slate-500'}`}>Payment pages</p>
        </div>
      </div>

      {/* Navigation */}
      <div className="flex flex-wrap gap-2">
        {[
          { id: 'incoming', label: 'Incoming Payments', icon: ArrowRightLeft },
          { id: 'outgoing', label: 'Outgoing Payments', icon: CreditCard },
          { id: 'links', label: 'Payment Links', icon: Link2 },
          { id: 'connected', label: 'Connected Apps', icon: Globe }
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${
              activeTab === tab.id
                ? 'bg-green-600 text-white'
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

      {/* Incoming Payments Tab */}
      {activeTab === 'incoming' && (
        <div className="grid lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <div className={`rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
              <div className="p-4 border-b border-slate-700/50">
                <h3 className={`font-semibold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                  Recent Payments Received
                </h3>
              </div>
              <div className="divide-y divide-slate-700/30">
                {receivedPayments.map(payment => (
                  <div key={payment.id} className="p-4 hover:bg-slate-700/10">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className={`p-2 rounded ${
                          payment.method === 'crypto' ? 'bg-orange-500/20' : 'bg-blue-500/20'
                        }`}>
                          {payment.method === 'crypto' ? <Bitcoin className="w-5 h-5 text-orange-400" /> : <CreditCard className="w-5 h-5 text-blue-400" />}
                        </div>
                        <div>
                          <p className={`font-medium ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                            {payment.product}
                          </p>
                          <p className="text-sm text-slate-500">
                            From: {payment.source} • {formatTimeAgo(payment.timestamp)}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-medium text-green-400">
                          +{payment.amount} {payment.currency}
                        </p>
                        <span className={`text-xs px-2 py-0.5 rounded ${
                          payment.status === 'confirmed' ? 'bg-green-500/10 text-green-400' :
                          payment.status === 'pending' ? 'bg-yellow-500/10 text-yellow-400' :
                          'bg-red-500/10 text-red-400'
                        }`}>
                          {payment.status.toUpperCase()}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="space-y-4">
            <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
              <h3 className={`font-semibold mb-4 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                Receive Payment
              </h3>
              <div className="space-y-2">
                <button className="w-full py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg flex items-center justify-center gap-2">
                  <Plus className="w-4 h-4" />
                  Create Payment Link
                </button>
                <button className="w-full py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg flex items-center justify-center gap-2">
                  <QrCode className="w-4 h-4" />
                  Generate QR Code
                </button>
                <button className="w-full py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg flex items-center justify-center gap-2">
                  <Bitcoin className="w-4 h-4" />
                  Crypto Address
                </button>
              </div>
            </div>

            <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
              <h3 className={`font-semibold mb-4 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                Payment Methods
              </h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between p-2 rounded bg-slate-900/30">
                  <div className="flex items-center gap-2">
                    <CreditCard className="w-4 h-4 text-blue-400" />
                    <span className={`text-sm ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>Stripe</span>
                  </div>
                  <CheckCircle2 className="w-4 h-4 text-green-400" />
                </div>
                <div className="flex items-center justify-between p-2 rounded bg-slate-900/30">
                  <div className="flex items-center gap-2">
                    <Bitcoin className="w-4 h-4 text-orange-400" />
                    <span className={`text-sm ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>Crypto (ETH/USDC)</span>
                  </div>
                  <CheckCircle2 className="w-4 h-4 text-green-400" />
                </div>
                <div className="flex items-center justify-between p-2 rounded bg-slate-900/30">
                  <div className="flex items-center gap-2">
                    <DollarSign className="w-4 h-4 text-green-400" />
                    <span className={`text-sm ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>Bank Transfer</span>
                  </div>
                  <span className="text-xs text-slate-500">Pending</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Outgoing Payments Tab */}
      {activeTab === 'outgoing' && (
        <div className={`rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
          <div className="p-4 border-b border-slate-700/50">
            <h3 className={`font-semibold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
              Monthly Infrastructure Costs
            </h3>
          </div>
          <div className="divide-y divide-slate-700/30">
            {connectedApps.map(app => (
              <div key={app.id} className="p-4 hover:bg-slate-700/10">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded ${
                      app.status === 'connected' ? 'bg-green-500/20' :
                      app.status === 'error' ? 'bg-red-500/20' :
                      'bg-slate-700'
                    }`}>
                      {app.type === 'bot' ? <Zap className="w-5 h-5 text-yellow-400" /> :
                       app.type === 'api' ? <Globe className="w-5 h-5 text-blue-400" /> :
                       <Settings className="w-5 h-5 text-slate-400" />}
                    </div>
                    <div>
                      <p className={`font-medium ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                        {app.name}
                      </p>
                      <p className="text-sm text-slate-500">
                        {app.paymentMethod} • Next: {app.nextPayment}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-medium text-red-400">-${app.monthlyCost}/mo</p>
                    <div className="flex items-center gap-2 mt-1">
                      <span className={`text-xs px-2 py-0.5 rounded ${
                        app.status === 'connected' ? 'bg-green-500/10 text-green-400' :
                        app.status === 'error' ? 'bg-red-500/10 text-red-400' :
                        'bg-slate-500/10 text-slate-400'
                      }`}>
                        {app.status.toUpperCase()}
                      </span>
                      {app.autoRenew ? <Lock className="w-3 h-3 text-slate-500" /> : <Unlock className="w-3 h-3 text-slate-500" />}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
          <div className="p-4 border-t border-slate-700/50">
            <div className="flex items-center justify-between">
              <span className={`font-medium ${darkMode ? 'text-white' : 'text-slate-900'}`}>Total Monthly</span>
              <span className="text-xl font-bold text-red-400">${totalOutgoingMonthly}</span>
            </div>
          </div>
        </div>
      )}

      {/* Payment Links Tab */}
      {activeTab === 'links' && (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h3 className={`font-semibold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
              Active Payment Links
            </h3>
            <button className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700">
              <Plus className="w-4 h-4" />
              New Payment Link
            </button>
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            {paymentLinks.map(link => (
              <div
                key={link.id}
                className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}
              >
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h4 className={`font-medium ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                      {link.name}
                    </h4>
                    <p className="text-sm text-slate-500">{link.type}</p>
                  </div>
                  <span className={`px-2 py-1 rounded text-xs ${
                    link.status === 'active' ? 'bg-green-500/10 text-green-400' :
                    link.status === 'paused' ? 'bg-yellow-500/10 text-yellow-400' :
                    'bg-slate-500/10 text-slate-400'
                  }`}>
                    {link.status.toUpperCase()}
                  </span>
                </div>

                <div className="flex items-center justify-between mb-3">
                  <div>
                    <p className="text-2xl font-bold text-white">${link.amount}</p>
                    <p className="text-sm text-slate-500">{link.currency}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-green-400 font-medium">${link.totalRevenue.toLocaleString()}</p>
                    <p className="text-xs text-slate-500">{link.totalPayments} payments</p>
                  </div>
                </div>

                <div className="flex flex-wrap gap-1 mb-3">
                  {link.allowedMethods.map(method => (
                    <span key={method} className={`text-xs px-2 py-1 rounded ${darkMode ? 'bg-slate-700 text-slate-300' : 'bg-slate-100 text-slate-600'}`}>
                      {method}
                    </span>
                  ))}
                </div>

                <div className="flex gap-2">
                  <button
                    onClick={() => navigator.clipboard.writeText(link.url)}
                    className="flex-1 py-2 text-sm bg-slate-700 text-white rounded hover:bg-slate-600 flex items-center justify-center gap-2"
                  >
                    <Copy className="w-4 h-4" />
                    Copy Link
                  </button>
                  <button className="px-3 py-2 text-sm bg-slate-700 text-white rounded hover:bg-slate-600">
                    <Settings className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Connected Apps Tab */}
      {activeTab === 'connected' && (
        <div className="space-y-4">
          <div className={`p-4 rounded-lg ${darkMode ? 'bg-yellow-500/10 border border-yellow-500/30' : 'bg-yellow-50 border border-yellow-200'}`}>
            <div className="flex items-center gap-2 text-yellow-400">
              <AlertCircle className="w-5 h-5" />
              <span className="font-medium">Payment Alert: n8n automation server payment overdue</span>
            </div>
          </div>

          <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
            <h3 className={`font-semibold mb-4 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
              App Integration Status
            </h3>
            <div className="space-y-3">
              {connectedApps.map(app => (
                <div key={app.id} className={`p-4 rounded-lg ${darkMode ? 'bg-slate-900/50' : 'bg-slate-50'}`}>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className={`w-2 h-2 rounded-full ${
                        app.status === 'connected' ? 'bg-green-400' :
                        app.status === 'error' ? 'bg-red-400 animate-pulse' :
                        'bg-slate-400'
                      }`} />
                      <span className={`font-medium ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                        {app.name}
                      </span>
                    </div>
                    <div className="flex items-center gap-4">
                      <span className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                        ${app.monthlyCost}/mo
                      </span>
                      <button className="px-3 py-1 text-sm bg-slate-700 text-white rounded hover:bg-slate-600">
                        Manage
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
