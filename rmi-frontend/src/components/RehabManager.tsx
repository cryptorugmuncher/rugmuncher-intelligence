import React, { useState } from 'react';
import {
  GraduationCap,
  Calendar,
  Clock,
  Users,
  DollarSign,
  Mail,
  MessageSquare,
  Send,
  Plus,
  Trash2,
  Edit3,
  Copy,
  CheckCircle,
  X,
  ChevronLeft,
  ChevronRight,
  Search,
  Filter,
  Download,
  FileText,
  CreditCard,
  Wallet,
  RefreshCw,
  Bell,
  Settings,
  BarChart3,
  TrendingUp,
  UserPlus,
  CheckSquare,
  Square,
  MoreHorizontal,
  ExternalLink,
  Eye,
  EyeOff,
  Bot,
  Zap,
  AlertTriangle,
  Check,
  Play,
  Pause,
  Globe,
  Smartphone,
  Layout,
  Code,
  Link,
  AtSign
} from 'lucide-react';

interface Client {
  id: string;
  name: string;
  email: string;
  telegram?: string;
  walletAddress?: string;
  status: 'lead' | 'intake' | 'active' | 'completed' | 'cancelled';
  source: 'website' | 'telegram' | 'referral' | 'twitter';
  dateAdded: string;
  totalPaid: number;
  sessionsBooked: number;
  sessionsAttended: number;
  lastContact: string;
  notes: string;
  tags: string[];
}

interface Session {
  id: string;
  clientId: string;
  clientName: string;
  type: 'individual' | 'group' | 'emergency';
  status: 'scheduled' | 'in_progress' | 'completed' | 'cancelled' | 'no_show';
  date: string;
  time: string;
  duration: number; // minutes
  price: number;
  paymentStatus: 'pending' | 'paid' | 'refunded' | 'comped';
  notes: string;
  zoomLink?: string;
  recordingUrl?: string;
}

interface Payment {
  id: string;
  clientId: string;
  clientName: string;
  amount: number;
  currency: 'USD' | 'USDC' | 'ETH' | 'CRM';
  status: 'pending' | 'completed' | 'failed' | 'refunded';
  method: 'stripe' | 'crypto' | 'manual';
  sessionId?: string;
  date: string;
  txHash?: string;
  invoiceSent: boolean;
  receiptSent: boolean;
}

interface EmailTemplate {
  id: string;
  name: string;
  subject: string;
  body: string;
  type: 'welcome' | 'intake' | 'reminder' | 'followup' | 'invoice' | 'receipt' | 'certificate';
  active: boolean;
  lastSent?: string;
  sendCount: number;
  openRate?: number;
}

interface IntakeForm {
  id: string;
  field: string;
  label: string;
  type: 'text' | 'email' | 'textarea' | 'select' | 'multiselect' | 'wallet' | 'telegram';
  required: boolean;
  options?: string[];
  active: boolean;
  order: number;
}

interface TelegramBotConfig {
  enabled: boolean;
  botToken: string;
  botUsername: string;
  welcomeMessage: string;
  autoReply: boolean;
  intakeForm: boolean;
  bookingEnabled: boolean;
  paymentEnabled: boolean;
  adminChatId: string;
  webhookUrl: string;
}

const RehabManager: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'clients' | 'sessions' | 'payments' | 'emails' | 'intake' | 'telegram'>('dashboard');

  // Clients State
  const [clients, setClients] = useState<Client[]>([
    {
      id: 'c1',
      name: 'John Doe',
      email: 'john@example.com',
      telegram: '@johndoe',
      walletAddress: '0x1234...5678',
      status: 'active',
      source: 'website',
      dateAdded: '2026-04-10',
      totalPaid: 500,
      sessionsBooked: 3,
      sessionsAttended: 2,
      lastContact: '2026-04-14',
      notes: 'Lost $50k in rug pull. Highly motivated.',
      tags: ['high-value', 'rug-victim', 'active']
    },
    {
      id: 'c2',
      name: 'Sarah Smith',
      email: 'sarah@example.com',
      telegram: '@sarahsmith',
      status: 'intake',
      source: 'telegram',
      dateAdded: '2026-04-12',
      totalPaid: 0,
      sessionsBooked: 0,
      sessionsAttended: 0,
      lastContact: '2026-04-13',
      notes: 'Initial contact, needs assessment.',
      tags: ['new-lead', 'telegram']
    },
    {
      id: 'c3',
      name: 'Mike Johnson',
      email: 'mike@example.com',
      status: 'completed',
      source: 'referral',
      dateAdded: '2026-03-15',
      totalPaid: 800,
      sessionsBooked: 5,
      sessionsAttended: 5,
      lastContact: '2026-04-01',
      notes: 'Completed program. Excellent progress.',
      tags: ['completed', 'success-story']
    }
  ]);

  // Sessions State
  const [sessions, setSessions] = useState<Session[]>([
    {
      id: 's1',
      clientId: 'c1',
      clientName: 'John Doe',
      type: 'individual',
      status: 'completed',
      date: '2026-04-12',
      time: '14:00',
      duration: 120,
      price: 150,
      paymentStatus: 'paid',
      notes: 'Contract reading basics covered.',
      zoomLink: 'https://zoom.us/j/123456',
      recordingUrl: 'https://storage.rugmunch.com/recordings/s1.mp4'
    },
    {
      id: 's2',
      clientId: 'c1',
      clientName: 'John Doe',
      type: 'individual',
      status: 'scheduled',
      date: '2026-04-16',
      time: '10:00',
      duration: 120,
      price: 150,
      paymentStatus: 'paid',
      notes: 'Advanced honeypot detection.',
      zoomLink: 'https://zoom.us/j/789012'
    },
    {
      id: 's3',
      clientId: 'c2',
      clientName: 'Sarah Smith',
      type: 'individual',
      status: 'scheduled',
      date: '2026-04-15',
      time: '16:00',
      duration: 60,
      price: 75,
      paymentStatus: 'pending',
      notes: 'Initial consultation.',
      zoomLink: 'https://zoom.us/j/345678'
    }
  ]);

  // Payments State
  const [payments, setPayments] = useState<Payment[]>([
    {
      id: 'p1',
      clientId: 'c1',
      clientName: 'John Doe',
      amount: 150,
      currency: 'USDC',
      status: 'completed',
      method: 'crypto',
      sessionId: 's1',
      date: '2026-04-12',
      txHash: '0xabc...def',
      invoiceSent: true,
      receiptSent: true
    },
    {
      id: 'p2',
      clientId: 'c1',
      clientName: 'John Doe',
      amount: 150,
      currency: 'USD',
      status: 'completed',
      method: 'stripe',
      sessionId: 's2',
      date: '2026-04-13',
      invoiceSent: true,
      receiptSent: true
    },
    {
      id: 'p3',
      clientId: 'c2',
      clientName: 'Sarah Smith',
      amount: 75,
      currency: 'USD',
      status: 'pending',
      method: 'stripe',
      sessionId: 's3',
      date: '2026-04-14',
      invoiceSent: true,
      receiptSent: false
    }
  ]);

  // Email Templates State
  const [emailTemplates, setEmailTemplates] = useState<EmailTemplate[]>([
    {
      id: 'et1',
      name: 'Welcome Email',
      subject: 'Welcome to Rug Pull Rehab - Your Recovery Starts Here',
      body: `Hi {{name}},

Welcome to Rug Pull Rehab! We're here to help you recover from your crypto losses and learn to protect yourself in the future.

Your assigned counselor will reach out within 24 hours to schedule your initial consultation.

In the meantime, here are some resources to get started:
- [Security Checklist]
- [Common Scam Patterns]
- [Recovery Support Group]

Stay strong. We've got your back.

Best regards,
The Rug Pull Rehab Team`,
      type: 'welcome',
      active: true,
      lastSent: '2026-04-14',
      sendCount: 45,
      openRate: 82
    },
    {
      id: 'et2',
      name: 'Intake Form Reminder',
      subject: 'Complete Your Intake Form - We Need Some Info',
      body: `Hi {{name}},

To better serve you, please complete your intake form:
{{intake_link}}

This helps us understand your situation and assign the best counselor for your needs.

Takes about 5 minutes.

Thanks,
Rug Pull Rehab Intake Team`,
      type: 'intake',
      active: true,
      lastSent: '2026-04-13',
      sendCount: 23,
      openRate: 67
    },
    {
      id: 'et3',
      name: 'Session Reminder',
      subject: 'Reminder: Your Session Tomorrow at {{time}}',
      body: `Hi {{name}},

Just a friendly reminder about your session tomorrow:

📅 Date: {{date}}
⏰ Time: {{time}}
🔗 Zoom Link: {{zoom_link}}

Please join 5 minutes early. If you need to reschedule, reply to this email or contact us on Telegram @rugpullrehab.

See you soon!

Best,
Your Counselor`,
      type: 'reminder',
      active: true,
      lastSent: '2026-04-14',
      sendCount: 89,
      openRate: 91
    },
    {
      id: 'et4',
      name: 'Payment Invoice',
      subject: 'Invoice #{{invoice_number}} - Rug Pull Rehab Services',
      body: `Hi {{name}},

Please find your invoice attached for:

Service: {{service_name}}
Amount: $' + '{{amount}}'
Due Date: {{due_date}}

Payment Options:
- Credit Card: {{stripe_link}}
- Crypto (USDC/ETH): {{crypto_address}}

Questions? Reply to this email.

Thank you,
Rug Pull Rehab Billing`,
      type: 'invoice',
      active: true,
      lastSent: '2026-04-14',
      sendCount: 34,
      openRate: 78
    }
  ]);

  // Intake Form State
  const [intakeForm, setIntakeForm] = useState<IntakeForm[]>([
    { id: 'f1', field: 'full_name', label: 'Full Name', type: 'text', required: true, active: true, order: 1 },
    { id: 'f2', field: 'email', label: 'Email Address', type: 'email', required: true, active: true, order: 2 },
    { id: 'f3', field: 'telegram', label: 'Telegram Handle', type: 'telegram', required: false, active: true, order: 3 },
    { id: 'f4', field: 'wallet', label: 'Primary Wallet Address', type: 'wallet', required: false, active: true, order: 4 },
    { id: 'f5', field: 'loss_amount', label: 'Approximate Loss Amount', type: 'select', required: true, active: true, order: 5, options: ['Under $1,000', '$1,000 - $10,000', '$10,000 - $50,000', '$50,000 - $100,000', 'Over $100,000'] },
    { id: 'f6', field: 'incident_details', label: 'Tell us what happened', type: 'textarea', required: true, active: true, order: 6 },
    { id: 'f7', field: 'services_needed', label: 'Services Interested In', type: 'multiselect', required: false, active: true, order: 7, options: ['1-on-1 Counseling', 'Group Sessions', 'Contract Analysis', 'Wallet Recovery Help', 'Education Classes'] },
    { id: 'f8', field: 'preferred_contact', label: 'Preferred Contact Method', type: 'select', required: true, active: true, order: 8, options: ['Email', 'Telegram', 'Phone'] }
  ]);

  // Telegram Bot Config
  const [telegramConfig, setTelegramConfig] = useState<TelegramBotConfig>({
    enabled: true,
    botToken: '***hidden***',
    botUsername: '@RugPullRehabBot',
    welcomeMessage: `Welcome to Rug Pull Rehab! 🛡️

I'm here to help you recover from crypto scams and learn to protect yourself.

What I can do:
📋 Complete intake form
📅 Book counseling sessions
💳 Process payments
📚 Access educational resources
💬 Connect with support

Type /start to begin or /help for options.`,
    autoReply: true,
    intakeForm: true,
    bookingEnabled: true,
    paymentEnabled: true,
    adminChatId: '-1001234567890',
    webhookUrl: 'https://api.rugmunch.com/webhook/telegram/rehab'
  });

  // UI State
  const [selectedClients, setSelectedClients] = useState<Set<string>>(new Set());
  const [showAddClient, setShowAddClient] = useState(false);
  const [showAddSession, setShowAddSession] = useState(false);
  const [showTemplateEditor, setShowTemplateEditor] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<EmailTemplate | null>(null);
  const [clientFilter, setClientFilter] = useState<'all' | 'lead' | 'intake' | 'active' | 'completed'>('all');

  const [newClient, setNewClient] = useState({
    name: '',
    email: '',
    telegram: '',
    source: 'website' as 'website' | 'telegram' | 'referral' | 'twitter',
    notes: ''
  });

  // Stats
  const stats = {
    totalClients: clients.length,
    activeClients: clients.filter(c => c.status === 'active').length,
    totalRevenue: payments.filter(p => p.status === 'completed').reduce((acc, p) => acc + p.amount, 0),
    pendingPayments: payments.filter(p => p.status === 'pending').reduce((acc, p) => acc + p.amount, 0),
    sessionsThisWeek: sessions.filter(s => s.date >= '2026-04-14' && s.date <= '2026-04-20').length,
    completionRate: Math.round((clients.filter(c => c.status === 'completed').length / clients.length) * 100),
    telegramUsers: clients.filter(c => c.telegram).length
  };

  const handleAddClient = () => {
    const client: Client = {
      id: `c${Date.now()}`,
      name: newClient.name,
      email: newClient.email,
      telegram: newClient.telegram,
      status: 'lead',
      source: newClient.source,
      dateAdded: new Date().toISOString().split('T')[0],
      totalPaid: 0,
      sessionsBooked: 0,
      sessionsAttended: 0,
      lastContact: new Date().toISOString().split('T')[0],
      notes: newClient.notes,
      tags: ['new-lead']
    };
    setClients([...clients, client]);
    setShowAddClient(false);
    setNewClient({ name: '', email: '', telegram: '', source: 'website', notes: '' });
  };

  const handleToggleTemplate = (templateId: string) => {
    setEmailTemplates(templates =>
      templates.map(t => t.id === templateId ? { ...t, active: !t.active } : t)
    );
  };

  const handleSaveTemplate = () => {
    if (editingTemplate) {
      setEmailTemplates(templates =>
        templates.map(t => t.id === editingTemplate.id ? editingTemplate : t)
      );
      setShowTemplateEditor(false);
      setEditingTemplate(null);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'lead': return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      case 'intake': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'completed': return 'bg-gray-700 text-gray-400 border-gray-600';
      case 'cancelled': return 'bg-red-500/20 text-red-400 border-red-500/30';
      default: return 'bg-gray-700 text-gray-400';
    }
  };

  const getPaymentStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-500/20 text-green-400';
      case 'pending': return 'bg-yellow-500/20 text-yellow-400';
      case 'failed': return 'bg-red-500/20 text-red-400';
      case 'refunded': return 'bg-gray-700 text-gray-400';
      default: return 'bg-gray-700 text-gray-400';
    }
  };

  const filteredClients = clients.filter(c =>
    clientFilter === 'all' || c.status === clientFilter
  );

  return (
    <div className="min-h-screen bg-[#0a0812] text-gray-100 font-mono selection:bg-[#7c3aed]/30">
      {/* Header */}
      <div className="bg-gradient-to-r from-[#0f0c1d] via-[#1a1525] to-[#0f0c1d] border-b border-[#7c3aed]/30">
        <div className="max-w-[1600px] mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-[#7c3aed]/20 rounded-full flex items-center justify-center">
                <GraduationCap className="w-5 h-5 text-[#7c3aed]" />
              </div>
              <div>
                <h1 className="text-xl font-bold tracking-wider">
                  RUG PULL <span className="text-[#7c3aed]">REHAB MGMT</span>
                </h1>
                <p className="text-xs text-gray-500 tracking-[0.2em]">CLIENT RECOVERY & BUSINESS OPERATIONS</p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 px-3 py-1.5 bg-green-500/10 border border-green-500/30 rounded">
                <DollarSign className="w-4 h-4 text-green-400" />
                <span className="text-sm text-green-400">${stats.totalRevenue.toLocaleString()} Revenue</span>
              </div>
              <div className="flex items-center gap-2 px-3 py-1.5 bg-[#7c3aed]/10 border border-[#7c3aed]/30 rounded">
                <Users className="w-4 h-4 text-[#7c3aed]" />
                <span className="text-sm text-[#7c3aed]">{stats.activeClients} Active Clients</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-[1600px] mx-auto p-6 space-y-6">
        {/* Stats Row */}
        <div className="grid grid-cols-6 gap-4">
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
            <Users className="w-5 h-5 text-blue-400 mb-2" />
            <div className="text-xl font-bold">{stats.totalClients}</div>
            <div className="text-xs text-gray-500">Total Clients</div>
          </div>
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
            <UserPlus className="w-5 h-5 text-green-400 mb-2" />
            <div className="text-xl font-bold">{stats.activeClients}</div>
            <div className="text-xs text-gray-500">Active Now</div>
          </div>
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
            <DollarSign className="w-5 h-5 text-green-400 mb-2" />
            <div className="text-xl font-bold">${stats.totalRevenue}</div>
            <div className="text-xs text-gray-500">Total Revenue</div>
          </div>
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
            <Clock className="w-5 h-5 text-yellow-400 mb-2" />
            <div className="text-xl font-bold">${stats.pendingPayments}</div>
            <div className="text-xs text-gray-500">Pending</div>
          </div>
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
            <Calendar className="w-5 h-5 text-purple-400 mb-2" />
            <div className="text-xl font-bold">{stats.sessionsThisWeek}</div>
            <div className="text-xs text-gray-500">This Week</div>
          </div>
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
            <CheckCircle className="w-5 h-5 text-pink-400 mb-2" />
            <div className="text-xl font-bold">{stats.completionRate}%</div>
            <div className="text-xs text-gray-500">Completion</div>
          </div>
        </div>

        {/* Navigation */}
        <div className="flex items-center gap-1 border-b border-gray-800">
          {[
            { id: 'dashboard', label: 'DASHBOARD', icon: <BarChart3 className="w-4 h-4" /> },
            { id: 'clients', label: 'CLIENTS', icon: <Users className="w-4 h-4" /> },
            { id: 'sessions', label: 'SESSIONS', icon: <Calendar className="w-4 h-4" /> },
            { id: 'payments', label: 'PAYMENTS', icon: <CreditCard className="w-4 h-4" /> },
            { id: 'emails', label: 'EMAIL AUTOMATION', icon: <Mail className="w-4 h-4" /> },
            { id: 'intake', label: 'INTAKE FORM', icon: <FileText className="w-4 h-4" /> },
            { id: 'telegram', label: 'TELEGRAM BOT', icon: <Bot className="w-4 h-4" /> },
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

        {/* Dashboard Tab */}
        {activeTab === 'dashboard' && (
          <div className="grid grid-cols-2 gap-6">
            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-bold mb-4">Upcoming Sessions (Next 7 Days)</h3>
              <div className="space-y-3">
                {sessions
                  .filter(s => s.status === 'scheduled' && s.date >= '2026-04-14')
                  .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
                  .slice(0, 5)
                  .map((session) => (
                    <div key={session.id} className="flex items-center justify-between p-3 bg-[#0a0812] rounded-lg">
                      <div>
                        <div className="font-semibold">{session.clientName}</div>
                        <div className="text-xs text-gray-500">{session.date} at {session.time}</div>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={`px-2 py-1 rounded text-xs ${getPaymentStatusColor(session.paymentStatus)}`}>
                          {session.paymentStatus}
                        </span>
                        <button className="p-1.5 bg-[#7c3aed]/10 rounded text-[#7c3aed] hover:bg-[#7c3aed]/20 transition-all">
                          <ExternalLink className="w-3 h-3" />
                        </button>
                      </div>
                    </div>
                  ))}
              </div>
            </div>

            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-bold mb-4">Recent Payments</h3>
              <div className="space-y-3">
                {payments.slice(0, 5).map((payment) => (
                  <div key={payment.id} className="flex items-center justify-between p-3 bg-[#0a0812] rounded-lg">
                    <div>
                      <div className="font-semibold">{payment.clientName}</div>
                      <div className="text-xs text-gray-500">
                        {payment.method === 'crypto' ? '💎' : '💳'} {payment.currency}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-semibold text-green-400">${payment.amount}</div>
                      <span className={`px-2 py-0.5 rounded text-[10px] ${getPaymentStatusColor(payment.status)}`}>
                        {payment.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-bold mb-4">Client Pipeline</h3>
              <div className="space-y-3">
                {['lead', 'intake', 'active', 'completed'].map((status) => {
                  const count = clients.filter(c => c.status === status).length;
                  const percentage = (count / clients.length) * 100;
                  return (
                    <div key={status}>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm uppercase">{status}</span>
                        <span className="text-sm">{count}</span>
                      </div>
                      <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full ${
                            status === 'lead' ? 'bg-blue-400' :
                            status === 'intake' ? 'bg-yellow-400' :
                            status === 'active' ? 'bg-green-400' :
                            'bg-gray-500'
                          }`}
                          style={{ width: `${percentage}%` }}
                        ></div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-bold mb-4">Revenue by Source</h3>
              <div className="space-y-3">
                {['website', 'telegram', 'referral', 'twitter'].map((source) => {
                  const sourceClients = clients.filter(c => c.source === source);
                  const sourceRevenue = payments
                    .filter(p => sourceClients.some(c => c.id === p.clientId))
                    .reduce((acc, p) => acc + p.amount, 0);
                  return (
                    <div key={source} className="flex items-center justify-between p-3 bg-[#0a0812] rounded-lg">
                      <span className="flex items-center gap-2 capitalize">
                        {source === 'website' ? <Globe className="w-4 h-4" /> :
                         source === 'telegram' ? <MessageSquare className="w-4 h-4" /> :
                         source === 'twitter' ? <AtSign className="w-4 h-4" /> :
                         <Users className="w-4 h-4" />}
                        {source}
                      </span>
                      <span className="font-semibold">${sourceRevenue}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {/* Clients Tab */}
        {activeTab === 'clients' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between bg-gradient-to-r from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
              <div className="flex items-center gap-4">
                <div className="relative">
                  <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
                  <input
                    type="text"
                    placeholder="Search clients..."
                    className="pl-10 pr-4 py-2 bg-[#0a0812] border border-gray-800 rounded text-sm w-64"
                  />
                </div>
                <select
                  value={clientFilter}
                  onChange={(e) => setClientFilter(e.target.value as any)}
                  className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm"
                >
                  <option value="all">All Status</option>
                  <option value="lead">Lead</option>
                  <option value="intake">Intake</option>
                  <option value="active">Active</option>
                  <option value="completed">Completed</option>
                </select>
              </div>
              <button
                onClick={() => setShowAddClient(true)}
                className="flex items-center gap-2 px-4 py-2 bg-[#7c3aed] text-white rounded text-sm hover:bg-[#6d28d9] transition-all"
              >
                <Plus className="w-4 h-4" />
                ADD CLIENT
              </button>
            </div>

            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg overflow-hidden">
              <table className="w-full">
                <thead className="bg-[#0f0c1d] border-b border-gray-800">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">CLIENT</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">STATUS</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">CONTACT</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">REVENUE</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">SESSIONS</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">SOURCE</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">ACTIONS</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredClients.map((client) => (
                    <tr key={client.id} className="border-b border-gray-800 hover:bg-[#0a0812]/50 transition-all">
                      <td className="px-4 py-3">
                        <div className="font-semibold">{client.name}</div>
                        {client.walletAddress && (
                          <div className="text-[10px] text-[#7c3aed]">💎 {client.walletAddress}</div>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-1 rounded text-xs border ${getStatusColor(client.status)}`}>
                          {client.status.toUpperCase()}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <div className="text-sm">{client.email}</div>
                        {client.telegram && (
                          <div className="text-xs text-[#7c3aed]">{client.telegram}</div>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        <div className="font-semibold">${client.totalPaid}</div>
                      </td>
                      <td className="px-4 py-3">
                        <div className="text-sm">{client.sessionsAttended}/{client.sessionsBooked}</div>
                      </td>
                      <td className="px-4 py-3">
                        <span className="text-xs uppercase px-2 py-1 bg-gray-800 rounded">{client.source}</span>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex gap-2">
                          <button className="p-1.5 bg-gray-800 rounded hover:bg-gray-700 transition-all">
                            <Edit3 className="w-3 h-3" />
                          </button>
                          <button className="p-1.5 bg-[#7c3aed]/10 rounded text-[#7c3aed] hover:bg-[#7c3aed]/20 transition-all">
                            <Mail className="w-3 h-3" />
                          </button>
                          <button className="p-1.5 bg-green-500/10 rounded text-green-400 hover:bg-green-500/20 transition-all">
                            <Calendar className="w-3 h-3" />
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

        {/* Sessions Tab */}
        {activeTab === 'sessions' && (
          <div className="space-y-4">
            <div className="flex justify-end">
              <button
                onClick={() => setShowAddSession(true)}
                className="flex items-center gap-2 px-4 py-2 bg-[#7c3aed] text-white rounded text-sm hover:bg-[#6d28d9] transition-all"
              >
                <Plus className="w-4 h-4" />
                SCHEDULE SESSION
              </button>
            </div>

            <div className="grid grid-cols-3 gap-4">
              {sessions.map((session) => (
                <div key={session.id} className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-5">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h3 className="font-bold">{session.clientName}</h3>
                      <p className="text-xs text-gray-500 capitalize">{session.type} Session</p>
                    </div>
                    <span className={`px-2 py-1 rounded text-xs ${
                      session.status === 'completed' ? 'bg-green-500/20 text-green-400' :
                      session.status === 'scheduled' ? 'bg-blue-500/20 text-blue-400' :
                      'bg-yellow-500/20 text-yellow-400'
                    }`}>
                      {session.status}
                    </span>
                  </div>

                  <div className="space-y-2 text-sm mb-4">
                    <div className="flex items-center gap-2 text-gray-400">
                      <Calendar className="w-4 h-4" />
                      {session.date}
                    </div>
                    <div className="flex items-center gap-2 text-gray-400">
                      <Clock className="w-4 h-4" />
                      {session.time} ({session.duration} min)
                    </div>
                    <div className="flex items-center gap-2 text-gray-400">
                      <DollarSign className="w-4 h-4" />
                      ${session.price}
                      <span className={`text-xs px-1.5 py-0.5 rounded ${getPaymentStatusColor(session.paymentStatus)}`}>
                        {session.paymentStatus}
                      </span>
                    </div>
                  </div>

                  {session.zoomLink && (
                    <a
                      href={session.zoomLink}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center justify-center gap-2 w-full py-2 bg-blue-500/10 border border-blue-500/30 rounded text-sm text-blue-400 hover:bg-blue-500/20 transition-all"
                    >
                      <ExternalLink className="w-4 h-4" />
                      JOIN ZOOM
                    </a>
                  )}

                  {session.recordingUrl && (
                    <a
                      href={session.recordingUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center justify-center gap-2 w-full mt-2 py-2 bg-gray-800 rounded text-sm text-gray-400 hover:bg-gray-700 transition-all"
                    >
                      <FileText className="w-4 h-4" />
                      VIEW RECORDING
                    </a>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Payments Tab */}
        {activeTab === 'payments' && (
          <div className="space-y-4">
            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg overflow-hidden">
              <table className="w-full">
                <thead className="bg-[#0f0c1d] border-b border-gray-800">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">CLIENT</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">AMOUNT</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">METHOD</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">STATUS</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">DATE</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">INVOICE</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">RECEIPT</th>
                  </tr>
                </thead>
                <tbody>
                  {payments.map((payment) => (
                    <tr key={payment.id} className="border-b border-gray-800 hover:bg-[#0a0812]/50 transition-all">
                      <td className="px-4 py-3">
                        <div className="font-semibold">{payment.clientName}</div>
                        {payment.txHash && (
                          <div className="text-[10px] text-[#7c3aed]">TX: {payment.txHash}</div>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        <div className="font-semibold text-green-400">${payment.amount}</div>
                        <div className="text-xs text-gray-500">{payment.currency}</div>
                      </td>
                      <td className="px-4 py-3">
                        <span className="flex items-center gap-2 text-sm">
                          {payment.method === 'crypto' ? <Wallet className="w-4 h-4" /> : <CreditCard className="w-4 h-4" />}
                          {payment.method}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-1 rounded text-xs ${getPaymentStatusColor(payment.status)}`}>
                          {payment.status}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm">{payment.date}</td>
                      <td className="px-4 py-3">
                        <button className={`px-2 py-1 rounded text-xs ${
                          payment.invoiceSent ? 'bg-green-500/20 text-green-400' : 'bg-gray-700 text-gray-400'
                        }`}>
                          {payment.invoiceSent ? 'SENT' : 'SEND'}
                        </button>
                      </td>
                      <td className="px-4 py-3">
                        <button className={`px-2 py-1 rounded text-xs ${
                          payment.receiptSent ? 'bg-green-500/20 text-green-400' : 'bg-gray-700 text-gray-400'
                        }`}>
                          {payment.receiptSent ? 'SENT' : 'SEND'}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Email Templates Tab */}
        {activeTab === 'emails' && (
          <div className="space-y-4">
            {emailTemplates.map((template) => (
              <div key={template.id} className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-5">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <h3 className="font-bold">{template.name}</h3>
                    <span className={`px-2 py-0.5 rounded text-[10px] ${
                      template.active ? 'bg-green-500/20 text-green-400' : 'bg-gray-700 text-gray-400'
                    }`}>
                      {template.active ? 'ACTIVE' : 'INACTIVE'}
                    </span>
                    <span className="px-2 py-0.5 bg-[#7c3aed]/20 text-[#7c3aed] rounded text-[10px] uppercase">
                      {template.type}
                    </span>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleToggleTemplate(template.id)}
                      className={`px-3 py-1.5 rounded text-xs ${
                        template.active
                          ? 'bg-red-500/10 text-red-400 hover:bg-red-500/20'
                          : 'bg-green-500/10 text-green-400 hover:bg-green-500/20'
                      }`}
                    >
                      {template.active ? 'DISABLE' : 'ENABLE'}
                    </button>
                    <button
                      onClick={() => { setEditingTemplate(template); setShowTemplateEditor(true); }}
                      className="px-3 py-1.5 bg-gray-800 rounded text-xs text-gray-400 hover:bg-gray-700 transition-all"
                    >
                      EDIT
                    </button>
                  </div>
                </div>

                <div className="bg-[#0a0812] rounded p-3 mb-3">
                  <div className="text-xs text-gray-500 mb-1">Subject:</div>
                  <div className="text-sm">{template.subject}</div>
                </div>

                <div className="flex items-center gap-6 text-xs text-gray-500">
                  <span>Sent: {template.sendCount} times</span>
                  {template.openRate && <span>Open rate: {template.openRate}%</span>}
                  {template.lastSent && <span>Last sent: {template.lastSent}</span>}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Intake Form Tab */}
        {activeTab === 'intake' && (
          <div className="grid grid-cols-2 gap-6">
            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold">Form Fields</h3>
                <button className="px-3 py-1.5 bg-[#7c3aed] text-white rounded text-sm hover:bg-[#6d28d9] transition-all">
                  <Plus className="w-4 h-4" />
                </button>
              </div>
              <div className="space-y-2">
                {intakeForm.sort((a, b) => a.order - b.order).map((field) => (
                  <div key={field.id} className="flex items-center justify-between p-3 bg-[#0a0812] rounded-lg">
                    <div className="flex items-center gap-3">
                      <span className="text-gray-500">{field.order}.</span>
                      <div>
                        <div className="font-semibold">{field.label}</div>
                        <div className="text-xs text-gray-500">{field.type} {field.required && '• Required'}</div>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <button className="p-1.5 bg-gray-800 rounded hover:bg-gray-700 transition-all">
                        <Edit3 className="w-3 h-3" />
                      </button>
                      <button className={`p-1.5 rounded transition-all ${
                        field.active ? 'bg-green-500/10 text-green-400' : 'bg-gray-800 text-gray-400'
                      }`}>
                        {field.active ? <Check className="w-3 h-3" /> : <X className="w-3 h-3" />}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-bold mb-4">Embed Code</h3>
              <div className="bg-[#0a0812] rounded-lg p-4 border border-gray-800">
                <code className="text-xs text-gray-300 block whitespace-pre">
{`<script src="https://rugmunch.com/widgets/rehab-intake.js"></script>
<div id="rug-pull-rehab-intake"
  data-theme="dark"
  data-primary-color="#7c3aed">
</div>`}
                </code>
                <button className="mt-4 w-full py-2 bg-gray-800 border border-gray-700 rounded text-sm text-gray-400 hover:bg-gray-700 transition-all">
                  <Copy className="w-4 h-4 inline mr-2" />
                  COPY EMBED CODE
                </button>
              </div>

              <h3 className="text-lg font-bold mt-6 mb-4">Direct Link</h3>
              <div className="bg-[#0a0812] rounded-lg p-4 border border-gray-800">
                <code className="text-xs text-[#7c3aed] block">
                  https://rugmunch.com/rehab/intake
                </code>
                <button className="mt-4 w-full py-2 bg-[#7c3aed]/10 border border-[#7c3aed]/30 rounded text-sm text-[#7c3aed] hover:bg-[#7c3aed]/20 transition-all">
                  <ExternalLink className="w-4 h-4 inline mr-2" />
                  OPEN FORM
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Telegram Bot Tab */}
        {activeTab === 'telegram' && (
          <div className="space-y-6">
            <div className="bg-gradient-to-r from-[#7c3aed]/20 via-[#1a1525] to-[#0f0c1d] border border-[#7c3aed]/30 rounded-lg p-6">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-4">
                  <div className="w-16 h-16 bg-[#7c3aed]/20 rounded-full flex items-center justify-center">
                    <Bot className="w-8 h-8 text-[#7c3aed]" />
                  </div>
                  <div>
                    <h2 className="text-xl font-bold">{telegramConfig.botUsername}</h2>
                    <p className="text-sm text-gray-400">Telegram Bot for Rug Pull Rehab</p>
                    <div className="flex items-center gap-2 mt-2">
                      <span className={`px-2 py-1 rounded text-xs ${
                        telegramConfig.enabled ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                      }`}>
                        {telegramConfig.enabled ? 'ONLINE' : 'OFFLINE'}
                      </span>
                      <span className="text-xs text-gray-500">{stats.telegramUsers} users</span>
                    </div>
                  </div>
                </div>
                <button
                  onClick={() => setTelegramConfig({ ...telegramConfig, enabled: !telegramConfig.enabled })}
                  className={`px-4 py-2 rounded text-sm font-semibold transition-all ${
                    telegramConfig.enabled
                      ? 'bg-red-500/10 text-red-400 hover:bg-red-500/20'
                      : 'bg-green-500/10 text-green-400 hover:bg-green-500/20'
                  }`}
                >
                  {telegramConfig.enabled ? 'STOP BOT' : 'START BOT'}
                </button>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-6">
              <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
                <h3 className="text-lg font-bold mb-4">Bot Configuration</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm text-gray-500 mb-1">Bot Token</label>
                    <div className="flex gap-2">
                      <input
                        type="password"
                        value={telegramConfig.botToken}
                        readOnly
                        className="flex-1 px-3 py-2 bg-[#0a0812] border border-gray-800 rounded text-sm"
                      />
                      <button className="px-3 py-2 bg-gray-800 rounded text-sm text-gray-400 hover:bg-gray-700 transition-all">
                        <EyeOff className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm text-gray-500 mb-1">Webhook URL</label>
                    <input
                      type="text"
                      value={telegramConfig.webhookUrl}
                      readOnly
                      className="w-full px-3 py-2 bg-[#0a0812] border border-gray-800 rounded text-sm"
                    />
                  </div>

                  <div>
                    <label className="block text-sm text-gray-500 mb-1">Admin Chat ID</label>
                    <input
                      type="text"
                      value={telegramConfig.adminChatId}
                      onChange={(e) => setTelegramConfig({ ...telegramConfig, adminChatId: e.target.value })}
                      className="w-full px-3 py-2 bg-[#0a0812] border border-gray-800 rounded text-sm"
                    />
                  </div>
                </div>
              </div>

              <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
                <h3 className="text-lg font-bold mb-4">Bot Features</h3>
                <div className="space-y-3">
                  {[
                    { key: 'intakeForm', label: 'Intake Form', desc: 'Allow users to complete intake via bot' },
                    { key: 'bookingEnabled', label: 'Session Booking', desc: 'Schedule sessions through Telegram' },
                    { key: 'paymentEnabled', label: 'Payments', desc: 'Process crypto payments via bot' },
                    { key: 'autoReply', label: 'Auto-Reply', desc: 'Automatic responses to common questions' },
                  ].map((feature) => (
                    <div key={feature.key} className="flex items-center justify-between p-3 bg-[#0a0812] rounded-lg">
                      <div>
                        <div className="font-semibold">{feature.label}</div>
                        <div className="text-xs text-gray-500">{feature.desc}</div>
                      </div>
                      <button
                        onClick={() => setTelegramConfig({ ...telegramConfig, [feature.key]: !telegramConfig[feature.key as keyof TelegramBotConfig] })}
                        className={`px-3 py-1.5 rounded text-xs ${
                          telegramConfig[feature.key as keyof TelegramBotConfig]
                            ? 'bg-green-500/20 text-green-400'
                            : 'bg-gray-700 text-gray-400'
                        }`}
                      >
                        {telegramConfig[feature.key as keyof TelegramBotConfig] ? 'ON' : 'OFF'}
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-bold mb-4">Welcome Message</h3>
              <textarea
                value={telegramConfig.welcomeMessage}
                onChange={(e) => setTelegramConfig({ ...telegramConfig, welcomeMessage: e.target.value })}
                rows={8}
                className="w-full px-3 py-2 bg-[#0a0812] border border-gray-800 rounded text-sm font-mono"
              />
              <div className="flex gap-3 mt-4">
                <button className="px-4 py-2 bg-[#7c3aed] text-white rounded text-sm hover:bg-[#6d28d9] transition-all">
                  SAVE CHANGES
                </button>
                <button className="px-4 py-2 bg-gray-800 text-gray-400 rounded text-sm hover:bg-gray-700 transition-all">
                  TEST MESSAGE
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Add Client Modal */}
      {showAddClient && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-[#1a1525] border border-gray-800 rounded-lg p-6 w-[500px] max-w-[90vw]">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold">Add New Client</h2>
              <button onClick={() => setShowAddClient(false)} className="p-1 hover:bg-gray-800 rounded">
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-500 mb-1">Full Name</label>
                <input
                  type="text"
                  value={newClient.name}
                  onChange={(e) => setNewClient({ ...newClient, name: e.target.value })}
                  className="w-full px-3 py-2 bg-[#0a0812] border border-gray-800 rounded"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-500 mb-1">Email</label>
                <input
                  type="email"
                  value={newClient.email}
                  onChange={(e) => setNewClient({ ...newClient, email: e.target.value })}
                  className="w-full px-3 py-2 bg-[#0a0812] border border-gray-800 rounded"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-500 mb-1">Telegram (optional)</label>
                <input
                  type="text"
                  value={newClient.telegram}
                  onChange={(e) => setNewClient({ ...newClient, telegram: e.target.value })}
                  placeholder="@username"
                  className="w-full px-3 py-2 bg-[#0a0812] border border-gray-800 rounded"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-500 mb-1">Source</label>
                <select
                  value={newClient.source}
                  onChange={(e) => setNewClient({ ...newClient, source: e.target.value as any })}
                  className="w-full px-3 py-2 bg-[#0a0812] border border-gray-800 rounded"
                >
                  <option value="website">Website</option>
                  <option value="telegram">Telegram</option>
                  <option value="referral">Referral</option>
                  <option value="twitter">Twitter/X</option>
                </select>
              </div>
              <div>
                <label className="block text-sm text-gray-500 mb-1">Notes</label>
                <textarea
                  value={newClient.notes}
                  onChange={(e) => setNewClient({ ...newClient, notes: e.target.value })}
                  rows={3}
                  className="w-full px-3 py-2 bg-[#0a0812] border border-gray-800 rounded"
                />
              </div>
              <div className="flex gap-3 pt-4">
                <button
                  onClick={handleAddClient}
                  className="flex-1 py-2 bg-[#7c3aed] text-white rounded hover:bg-[#6d28d9] transition-all"
                >
                  ADD CLIENT
                </button>
                <button
                  onClick={() => setShowAddClient(false)}
                  className="px-4 py-2 bg-gray-800 text-gray-400 rounded hover:bg-gray-700 transition-all"
                >
                  CANCEL
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Template Editor Modal */}
      {showTemplateEditor && editingTemplate && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-[#1a1525] border border-gray-800 rounded-lg p-6 w-[700px] max-w-[90vw] max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold">Edit Email Template</h2>
              <button onClick={() => setShowTemplateEditor(false)} className="p-1 hover:bg-gray-800 rounded">
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-500 mb-1">Template Name</label>
                <input
                  type="text"
                  value={editingTemplate.name}
                  onChange={(e) => setEditingTemplate({ ...editingTemplate, name: e.target.value })}
                  className="w-full px-3 py-2 bg-[#0a0812] border border-gray-800 rounded"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-500 mb-1">Subject Line</label>
                <input
                  type="text"
                  value={editingTemplate.subject}
                  onChange={(e) => setEditingTemplate({ ...editingTemplate, subject: e.target.value })}
                  className="w-full px-3 py-2 bg-[#0a0812] border border-gray-800 rounded"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-500 mb-1">Email Body</label>
                <textarea
                  value={editingTemplate.body}
                  onChange={(e) => setEditingTemplate({ ...editingTemplate, body: e.target.value })}
                  rows={15}
                  className="w-full px-3 py-2 bg-[#0a0812] border border-gray-800 rounded font-mono text-sm"
                />
              </div>
              <div className="flex gap-3 pt-4">
                <button
                  onClick={handleSaveTemplate}
                  className="flex-1 py-2 bg-[#7c3aed] text-white rounded hover:bg-[#6d28d9] transition-all"
                >
                  SAVE TEMPLATE
                </button>
                <button
                  onClick={() => setShowTemplateEditor(false)}
                  className="px-4 py-2 bg-gray-800 text-gray-400 rounded hover:bg-gray-700 transition-all"
                >
                  CANCEL
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RehabManager;
