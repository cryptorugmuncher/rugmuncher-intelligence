import { useState } from 'react';
import { Link2, Share2, Users, Gift, TrendingUp, MessageSquare, Copy, CheckCircle2, Plus, Trash2, BarChart3, Target, Zap, ExternalLink, QrCode, Download, Settings, Award, Megaphone, Bot, Send } from 'lucide-react';
import { useAppStore } from '../store/appStore';

interface ReferralCampaign {
  id: string;
  name: string;
  description: string;
  code: string;
  status: 'active' | 'paused' | 'ended';
  rewardType: 'tokens' | 'discount' | 'premium_access' | 'custom';
  rewardAmount: number;
  rewardToken?: string;
  totalSignups: number;
  qualifiedReferrals: number;
  conversionRate: number;
  createdAt: string;
  endDate?: string;
  telegramBotEnabled: boolean;
  autoResponseEnabled: boolean;
  telegramMessageTemplate: string;
}

interface ReferralUser {
  id: string;
  wallet: string;
  telegramId?: string;
  referralCode: string;
  totalReferrals: number;
  qualifiedReferrals: number;
  rewardsEarned: number;
  joinedAt: string;
  lastActive: string;
  topReferrer: boolean;
}

interface ReferralProduct {
  id: string;
  name: string;
  type: 'rmi' | 'munchmaps' | 'rugmuncher' | 'newsletter' | 'rehab' | 'api';
  commissionPercent: number;
  status: 'active' | 'coming_soon';
  averageOrderValue: number;
  monthlyVolume: number;
}

interface UserReferralEarnings {
  userId: string;
  referralCode: string;
  totalEarnings: number;
  pendingEarnings: number;
  totalReferrals: number;
  activeReferrals: number;
  earningsByProduct: {
    productId: string;
    productName: string;
    earnings: number;
    referrals: number;
  }[];
  recentPayouts: {
    date: string;
    amount: number;
    status: 'pending' | 'paid' | 'processing';
  }[];
}

interface TelegramBotConfig {
  botUsername: string;
  welcomeMessage: string;
  referralCommand: string;
  autoReplyEnabled: boolean;
  signatureTemplate: string;
}

const mockCampaigns: ReferralCampaign[] = [
  {
    id: '1',
    name: 'CRM V2 Early Adopter',
    description: 'Refer friends to get early access and bonus tokens',
    code: 'CRMV2',
    status: 'active',
    rewardType: 'tokens',
    rewardAmount: 10000,
    rewardToken: 'CRM',
    totalSignups: 1247,
    qualifiedReferrals: 892,
    conversionRate: 71.5,
    createdAt: '2026-03-01',
    endDate: '2026-05-01',
    telegramBotEnabled: true,
    autoResponseEnabled: true,
    telegramMessageTemplate: '🎁 Join Rug Munch Intel using my referral link and get {reward} bonus tokens! {link}'
  },
  {
    id: '2',
    name: 'MunchMaps Beta Invite',
    description: 'Exclusive beta access for referrer and referee',
    code: 'MUNCHMAP',
    status: 'active',
    rewardType: 'premium_access',
    rewardAmount: 1,
    totalSignups: 456,
    qualifiedReferrals: 389,
    conversionRate: 85.3,
    createdAt: '2026-03-15',
    telegramBotEnabled: true,
    autoResponseEnabled: true,
    telegramMessageTemplate: '🔍 Get early access to MunchMaps - the best rug pull detection tool! Use my link: {link}'
  },
  {
    id: '3',
    name: 'Newsletter Growth',
    description: 'Daily Intelligence Briefing referral program',
    code: 'DAILYINTEL',
    status: 'active',
    rewardType: 'discount',
    rewardAmount: 50,
    totalSignups: 234,
    qualifiedReferrals: 198,
    conversionRate: 84.6,
    createdAt: '2026-04-01',
    telegramBotEnabled: true,
    autoResponseEnabled: false,
    telegramMessageTemplate: '📰 Subscribe to Daily Intel Briefing - crypto security insights daily! 50% off with my link: {link}'
  }
];

const mockTopReferrers: ReferralUser[] = [
  {
    id: '1',
    wallet: '0x742d35Cc6634C0532925a3b8D4B9db96590f6C7E',
    telegramId: '@crypto_whale',
    referralCode: 'WHALE2026',
    totalReferrals: 156,
    qualifiedReferrals: 142,
    rewardsEarned: 1420000,
    joinedAt: '2026-03-01',
    lastActive: '2026-04-14',
    topReferrer: true
  },
  {
    id: '2',
    wallet: '0x1234567890abcdef1234567890abcdef12345678',
    telegramId: '@rug_hunter_pro',
    referralCode: 'HUNTERPRO',
    totalReferrals: 89,
    qualifiedReferrals: 76,
    rewardsEarned: 760000,
    joinedAt: '2026-03-05',
    lastActive: '2026-04-13',
    topReferrer: true
  },
  {
    id: '3',
    wallet: '0xabcdef1234567890abcdef1234567890abcdef12',
    telegramId: '@defi_detective',
    referralCode: 'DEFIDETECT',
    totalReferrals: 67,
    qualifiedReferrals: 58,
    rewardsEarned: 580000,
    joinedAt: '2026-03-10',
    lastActive: '2026-04-12',
    topReferrer: true
  }
];

const telegramConfig: TelegramBotConfig = {
  botUsername: '@RugMuncherBot',
  welcomeMessage: 'Welcome to Rug Munch Intel! 🛡️\n\nUse /referral to get your unique referral link and earn rewards for each friend who joins.',
  referralCommand: '/referral',
  autoReplyEnabled: true,
  signatureTemplate: '\n\n🔗 Join Rug Munch Intel: {link}\n🎁 Get {reward} using code: {code}'
};

const referralProducts: ReferralProduct[] = [
  { id: '1', name: 'RMI Platform', type: 'rmi', commissionPercent: 10, status: 'active', averageOrderValue: 150, monthlyVolume: 45000 },
  { id: '2', name: 'MunchMaps Pro', type: 'munchmaps', commissionPercent: 10, status: 'active', averageOrderValue: 99, monthlyVolume: 32000 },
  { id: '3', name: 'Rug Muncher Bot', type: 'rugmuncher', commissionPercent: 10, status: 'active', averageOrderValue: 50, monthlyVolume: 18000 },
  { id: '4', name: 'Daily Intel Newsletter', type: 'newsletter', commissionPercent: 10, status: 'active', averageOrderValue: 5, monthlyVolume: 8500 },
  { id: '5', name: 'Rug Pull Rehab', type: 'rehab', commissionPercent: 10, status: 'active', averageOrderValue: 250, monthlyVolume: 25000 },
  { id: '6', name: 'API Access', type: 'api', commissionPercent: 10, status: 'active', averageOrderValue: 199, monthlyVolume: 15000 }
];

const userEarnings: UserReferralEarnings = {
  userId: 'current-user',
  referralCode: 'RMI2026',
  totalEarnings: 12500,
  pendingEarnings: 2300,
  totalReferrals: 45,
  activeReferrals: 38,
  earningsByProduct: [
    { productId: '1', productName: 'RMI Platform', earnings: 4500, referrals: 12 },
    { productId: '2', productName: 'MunchMaps Pro', earnings: 3200, referrals: 15 },
    { productId: '3', productName: 'Rug Muncher Bot', earnings: 1800, referrals: 8 },
    { productId: '5', productName: 'Rug Pull Rehab', earnings: 3000, referrals: 10 }
  ],
  recentPayouts: [
    { date: '2026-04-01', amount: 5000, status: 'paid' },
    { date: '2026-03-01', amount: 4200, status: 'paid' },
    { date: '2026-02-01', amount: 3300, status: 'paid' }
  ]
};

export default function ReferralManager() {
  const { theme } = useAppStore();
  const darkMode = theme === 'dark';

  const [campaigns] = useState<ReferralCampaign[]>(mockCampaigns);
  const [topReferrers] = useState<ReferralUser[]>(mockTopReferrers);
  const [activeTab, setActiveTab] = useState<'my-referrals' | 'overview' | 'campaigns' | 'referrers' | 'telegram' | 'analytics'>('my-referrals');
  const [selectedCampaign, setSelectedCampaign] = useState<string | null>(null);
  const [copiedCode, setCopiedCode] = useState<string | null>(null);

  const stats = {
    totalCampaigns: campaigns.length,
    totalSignups: campaigns.reduce((acc, c) => acc + c.totalSignups, 0),
    totalQualified: campaigns.reduce((acc, c) => acc + c.qualifiedReferrals, 0),
    avgConversion: campaigns.reduce((acc, c) => acc + c.conversionRate, 0) / campaigns.length,
    totalRewardsDistributed: topReferrers.reduce((acc, r) => acc + r.rewardsEarned, 0)
  };

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedCode(id);
    setTimeout(() => setCopiedCode(null), 2000);
  };

  const generateReferralLink = (code: string) => `https://rugmunch.com/ref/${code}`;
  const generateTelegramShare = (code: string, template: string) => {
    const link = generateReferralLink(code);
    return template.replace('{link}', link).replace('{reward}', '10,000 CRM');
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
        <div className="flex items-center gap-3 mb-2">
          <Share2 className="w-8 h-8 text-purple-500" />
          <h1 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
            REFERRAL COMMAND CENTER
          </h1>
          <span className="px-2 py-1 bg-purple-500/10 text-purple-400 text-xs font-mono rounded">
            GROWTH OPS
          </span>
        </div>
        <p className={`${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
          Manage referral campaigns, track signups, and integrate with Telegram bot for viral growth.
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
          <p className="text-2xl font-bold text-white">{stats.totalCampaigns}</p>
          <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Active Campaigns</p>
        </div>
        <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
          <p className="text-2xl font-bold text-purple-400">{stats.totalSignups.toLocaleString()}</p>
          <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Total Signups</p>
        </div>
        <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
          <p className="text-2xl font-bold text-green-400">{stats.totalQualified.toLocaleString()}</p>
          <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Qualified Referrals</p>
        </div>
        <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
          <p className="text-2xl font-bold text-blue-400">{stats.avgConversion.toFixed(1)}%</p>
          <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Avg Conversion</p>
        </div>
        <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
          <p className="text-2xl font-bold text-yellow-400">{(stats.totalRewardsDistributed / 1000000).toFixed(2)}M</p>
          <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>CRM Distributed</p>
        </div>
      </div>

      {/* Navigation */}
      <div className="flex flex-wrap gap-2">
        {[
          { id: 'my-referrals', label: 'My Referral Dashboard', icon: Gift },
          { id: 'overview', label: 'Admin Overview', icon: Target },
          { id: 'campaigns', label: 'Campaigns', icon: Megaphone },
          { id: 'referrers', label: 'Top Referrers', icon: Award },
          { id: 'telegram', label: 'Telegram Integration', icon: MessageSquare },
          { id: 'analytics', label: 'Analytics', icon: BarChart3 }
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

      {/* My Referrals Tab - User Panel */}
      {activeTab === 'my-referrals' && (
        <div className="space-y-6">
          {/* Welcome & Code Section */}
          <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div>
                <h2 className={`text-xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                  Your Referral Dashboard
                </h2>
                <p className={`mt-1 ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                  Earn <span className="text-purple-400 font-bold">10% lifetime commission</span> on all purchases from your referrals
                </p>
              </div>
              <div className="flex items-center gap-3">
                <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-900/50' : 'bg-slate-100'}`}>
                  <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Your Code</p>
                  <div className="flex items-center gap-2">
                    <code className="text-xl font-bold text-purple-400">{userEarnings.referralCode}</code>
                    <button
                      onClick={() => copyToClipboard(userEarnings.referralCode, 'user-code')}
                      className="p-1 text-slate-400 hover:text-white"
                    >
                      {copiedCode === 'user-code' ? <CheckCircle2 className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4" />}
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* Referral Link */}
            <div className="mt-4 p-4 rounded-lg bg-purple-500/10 border border-purple-500/30">
              <p className="text-sm text-purple-400 mb-2">YOUR REFERRAL LINK</p>
              <div className="flex gap-2">
                <code className={`flex-1 p-3 rounded text-sm ${darkMode ? 'bg-slate-900 text-slate-300' : 'bg-white text-slate-700'}`}>
                  https://rugmunch.com/?ref={userEarnings.referralCode}
                </code>
                <button
                  onClick={() => copyToClipboard(`https://rugmunch.com/?ref=${userEarnings.referralCode}`, 'user-link')}
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
                >
                  {copiedCode === 'user-link' ? 'Copied!' : 'Copy'}
                </button>
              </div>
            </div>
          </div>

          {/* Earnings Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
              <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Total Earned</p>
              <p className="text-2xl font-bold text-green-400">{userEarnings.totalEarnings.toLocaleString()} CRM</p>
              <p className="text-xs text-slate-500">≈ ${(userEarnings.totalEarnings * 0.015).toFixed(2)}</p>
            </div>
            <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
              <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Pending</p>
              <p className="text-2xl font-bold text-yellow-400">{userEarnings.pendingEarnings.toLocaleString()} CRM</p>
              <p className="text-xs text-slate-500">Next payout in 12 days</p>
            </div>
            <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
              <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Total Referrals</p>
              <p className="text-2xl font-bold text-purple-400">{userEarnings.totalReferrals}</p>
              <p className="text-xs text-slate-500">{userEarnings.activeReferrals} active</p>
            </div>
            <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
              <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Commission Rate</p>
              <p className="text-2xl font-bold text-blue-400">10%</p>
              <p className="text-xs text-slate-500">Lifetime on all products</p>
            </div>
          </div>

          {/* Products & Commission */}
          <div className="grid lg:grid-cols-2 gap-6">
            <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
              <h3 className={`font-semibold mb-4 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                Earnings by Product (10% Commission)
              </h3>
              <div className="space-y-3">
                {userEarnings.earningsByProduct.map(product => (
                  <div key={product.productId} className={`p-3 rounded-lg ${darkMode ? 'bg-slate-900/50' : 'bg-slate-50'}`}>
                    <div className="flex items-center justify-between">
                      <span className={`font-medium ${darkMode ? 'text-white' : 'text-slate-900'}`}>{product.productName}</span>
                      <span className="text-green-400 font-medium">{product.earnings.toLocaleString()} CRM</span>
                    </div>
                    <div className="flex items-center justify-between mt-1 text-sm">
                      <span className="text-slate-500">{product.referrals} referrals</span>
                      <span className="text-purple-400">10% commission</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
              <h3 className={`font-semibold mb-4 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                Available Products to Promote
              </h3>
              <div className="space-y-3">
                {referralProducts.map(product => (
                  <div key={product.id} className={`p-3 rounded-lg ${darkMode ? 'bg-slate-900/50' : 'bg-slate-50'}`}>
                    <div className="flex items-center justify-between">
                      <div>
                        <span className={`font-medium ${darkMode ? 'text-white' : 'text-slate-900'}`}>{product.name}</span>
                        <p className="text-xs text-slate-500">Avg order: ${product.averageOrderValue}</p>
                      </div>
                      <div className="text-right">
                        <span className="text-green-400 font-medium">{product.commissionPercent}%</span>
                        <p className="text-xs text-slate-500">commission</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Recent Payouts & Share */}
          <div className="grid lg:grid-cols-2 gap-6">
            <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
              <h3 className={`font-semibold mb-4 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                Payout History
              </h3>
              <div className="space-y-2">
                {userEarnings.recentPayouts.map((payout, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 rounded-lg bg-slate-900/30">
                    <div>
                      <p className="text-white font-medium">{payout.amount.toLocaleString()} CRM</p>
                      <p className="text-sm text-slate-500">{new Date(payout.date).toLocaleDateString()}</p>
                    </div>
                    <span className={`px-2 py-1 rounded text-xs ${
                      payout.status === 'paid' ? 'bg-green-500/10 text-green-400' :
                      payout.status === 'processing' ? 'bg-yellow-500/10 text-yellow-400' :
                      'bg-blue-500/10 text-blue-400'
                    }`}>
                      {payout.status.toUpperCase()}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
              <h3 className={`font-semibold mb-4 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                Share & Promote
              </h3>
              <div className="space-y-3">
                <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                  Share your referral link on social media to earn 10% on every purchase:
                </p>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    onClick={() => window.open(`https://t.me/share/url?url=${encodeURIComponent(`https://rugmunch.com/?ref=${userEarnings.referralCode}`)}&text=${encodeURIComponent('Join Rug Munch Intel and protect yourself from crypto scams! Use my referral code for bonuses.')}`, '_blank')}
                    className="p-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg flex items-center justify-center gap-2"
                  >
                    <MessageSquare className="w-4 h-4" />
                    Telegram
                  </button>
                  <button
                    onClick={() => window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(`Protect your crypto with Rug Munch Intel! 🛡️ Use my referral code ${userEarnings.referralCode} for exclusive bonuses. #CryptoSecurity`)}}`, '_blank')}
                    className="p-3 bg-slate-700 hover:bg-slate-600 text-white rounded-lg flex items-center justify-center gap-2"
                  >
                    <ExternalLink className="w-4 h-4" />
                    Twitter/X
                  </button>
                </div>
                <button className="w-full p-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg flex items-center justify-center gap-2">
                  <Download className="w-4 h-4" />
                  Download Promo Materials
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="grid lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-4">
            <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
              <h3 className={`font-semibold mb-4 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                Active Campaigns
              </h3>
              <div className="space-y-4">
                {campaigns.map(campaign => (
                  <div
                    key={campaign.id}
                    onClick={() => setSelectedCampaign(selectedCampaign === campaign.id ? null : campaign.id)}
                    className={`p-4 rounded-lg border cursor-pointer transition-all ${
                      selectedCampaign === campaign.id
                        ? 'border-purple-500 bg-purple-500/5'
                        : darkMode
                        ? 'border-slate-700 hover:border-slate-600'
                        : 'border-slate-200 hover:border-slate-300'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="flex items-center gap-2">
                          <h4 className={`font-semibold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                            {campaign.name}
                          </h4>
                          <span className={`px-2 py-0.5 rounded text-xs ${
                            campaign.status === 'active'
                              ? 'bg-green-500/10 text-green-400'
                              : 'bg-slate-500/10 text-slate-400'
                          }`}>
                            {campaign.status.toUpperCase()}
                          </span>
                          {campaign.telegramBotEnabled && (
                            <span className="px-2 py-0.5 rounded text-xs bg-blue-500/10 text-blue-400 flex items-center gap-1">
                              <Bot className="w-3 h-3" />
                              BOT
                            </span>
                          )}
                        </div>
                        <p className={`text-sm mt-1 ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                          {campaign.description}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-2xl font-bold text-purple-400">{campaign.conversionRate}%</p>
                        <p className="text-xs text-slate-500">conversion</p>
                      </div>
                    </div>

                    <div className="flex items-center gap-6 mt-4 text-sm">
                      <div>
                        <span className="text-slate-500">Signups: </span>
                        <span className="text-white">{campaign.totalSignups.toLocaleString()}</span>
                      </div>
                      <div>
                        <span className="text-slate-500">Qualified: </span>
                        <span className="text-green-400">{campaign.qualifiedReferrals.toLocaleString()}</span>
                      </div>
                      <div>
                        <span className="text-slate-500">Reward: </span>
                        <span className="text-yellow-400">
                          {campaign.rewardAmount.toLocaleString()} {campaign.rewardToken}
                        </span>
                      </div>
                    </div>

                    {/* Quick Actions */}
                    <div className="flex gap-2 mt-4 pt-3 border-t border-slate-700/30">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          copyToClipboard(generateReferralLink(campaign.code), campaign.id);
                        }}
                        className="flex items-center gap-2 px-3 py-1.5 bg-slate-700 text-white rounded text-sm hover:bg-slate-600"
                      >
                        {copiedCode === campaign.id ? <CheckCircle2 className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                        {copiedCode === campaign.id ? 'Copied!' : 'Copy Link'}
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          const shareText = generateTelegramShare(campaign.code, campaign.telegramMessageTemplate);
                          window.open(`https://t.me/share/url?url=${encodeURIComponent(generateReferralLink(campaign.code))}&text=${encodeURIComponent(shareText)}`, '_blank');
                        }}
                        className="flex items-center gap-2 px-3 py-1.5 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
                      >
                        <MessageSquare className="w-4 h-4" />
                        Share on Telegram
                      </button>
                      <button className="px-3 py-1.5 bg-slate-700 text-white rounded text-sm hover:bg-slate-600">
                        <QrCode className="w-4 h-4" />
                      </button>
                    </div>

                    {/* Expanded Details */}
                    {selectedCampaign === campaign.id && (
                      <div className="mt-4 p-4 rounded-lg bg-slate-900/30">
                        <p className="text-sm text-slate-400 mb-2">TELEGRAM BOT TEMPLATE</p>
                        <code className="block p-3 rounded bg-slate-900 text-sm text-slate-300 font-mono">
                          {campaign.telegramMessageTemplate}
                        </code>
                        <div className="flex gap-2 mt-3">
                          <button className="px-3 py-1.5 text-sm bg-purple-600 text-white rounded hover:bg-purple-700">
                            Edit Template
                          </button>
                          <button className="px-3 py-1.5 text-sm bg-slate-700 text-white rounded hover:bg-slate-600">
                            Test in Bot
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="space-y-4">
            <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
              <h3 className={`font-semibold mb-4 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                Quick Actions
              </h3>
              <div className="space-y-2">
                <button className="w-full py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg flex items-center justify-center gap-2">
                  <Plus className="w-4 h-4" />
                  New Campaign
                </button>
                <button className="w-full py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg flex items-center justify-center gap-2">
                  <Download className="w-4 h-4" />
                  Export Referrers
                </button>
                <button className="w-full py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg flex items-center justify-center gap-2">
                  <Bot className="w-4 h-4" />
                  Configure Bot
                </button>
              </div>
            </div>

            <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
              <h3 className={`font-semibold mb-4 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                Telegram Bot Status
              </h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between p-2 rounded bg-slate-900/30">
                  <span className="text-sm text-slate-400">Bot Username</span>
                  <span className="text-sm text-blue-400">{telegramConfig.botUsername}</span>
                </div>
                <div className="flex items-center justify-between p-2 rounded bg-slate-900/30">
                  <span className="text-sm text-slate-400">Auto-Reply</span>
                  <span className="px-2 py-0.5 rounded text-xs bg-green-500/10 text-green-400">ACTIVE</span>
                </div>
                <div className="flex items-center justify-between p-2 rounded bg-slate-900/30">
                  <span className="text-sm text-slate-400">Campaigns Linked</span>
                  <span className="text-sm text-white">3</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Campaigns Tab */}
      {activeTab === 'campaigns' && (
        <div className={`rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
          <div className="p-4 border-b border-slate-700/50 flex items-center justify-between">
            <h3 className={`font-semibold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
              All Referral Campaigns
            </h3>
            <button className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700">
              <Plus className="w-4 h-4" />
              Create Campaign
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className={`${darkMode ? 'bg-slate-900/50' : 'bg-slate-50'}`}>
                <tr>
                  <th className="text-left p-4 text-sm font-medium text-slate-400">Campaign</th>
                  <th className="text-left p-4 text-sm font-medium text-slate-400">Code</th>
                  <th className="text-right p-4 text-sm font-medium text-slate-400">Signups</th>
                  <th className="text-right p-4 text-sm font-medium text-slate-400">Conversion</th>
                  <th className="text-left p-4 text-sm font-medium text-slate-400">Reward</th>
                  <th className="text-center p-4 text-sm font-medium text-slate-400">Telegram</th>
                  <th className="text-center p-4 text-sm font-medium text-slate-400">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700/30">
                {campaigns.map(campaign => (
                  <tr key={campaign.id} className="hover:bg-slate-700/10">
                    <td className="p-4">
                      <p className={`font-medium ${darkMode ? 'text-white' : 'text-slate-900'}`}>{campaign.name}</p>
                      <p className="text-sm text-slate-500">{campaign.description.slice(0, 40)}...</p>
                    </td>
                    <td className="p-4">
                      <code className="px-2 py-1 rounded bg-purple-500/10 text-purple-400 text-sm">
                        {campaign.code}
                      </code>
                    </td>
                    <td className="p-4 text-right">
                      <p className="text-white">{campaign.totalSignups.toLocaleString()}</p>
                      <p className="text-sm text-green-400">{campaign.qualifiedReferrals} qualified</p>
                    </td>
                    <td className="p-4 text-right">
                      <span className="text-purple-400 font-medium">{campaign.conversionRate}%</span>
                    </td>
                    <td className="p-4">
                      <span className="text-yellow-400">
                        {campaign.rewardAmount.toLocaleString()} {campaign.rewardToken}
                      </span>
                    </td>
                    <td className="p-4 text-center">
                      {campaign.telegramBotEnabled ? (
                        <CheckCircle2 className="w-5 h-5 text-green-400 mx-auto" />
                      ) : (
                        <span className="text-slate-500">-</span>
                      )}
                    </td>
                    <td className="p-4 text-center">
                      <span className={`px-2 py-1 rounded text-xs ${
                        campaign.status === 'active'
                          ? 'bg-green-500/10 text-green-400'
                          : 'bg-slate-500/10 text-slate-400'
                      }`}>
                        {campaign.status.toUpperCase()}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Top Referrers Tab */}
      {activeTab === 'referrers' && (
        <div className="space-y-6">
          <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
            <h3 className={`font-semibold mb-6 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
              Top Performers Leaderboard
            </h3>
            <div className="space-y-4">
              {topReferrers.map((referrer, idx) => (
                <div
                  key={referrer.id}
                  className={`p-4 rounded-lg ${darkMode ? 'bg-slate-900/50' : 'bg-slate-50'} border ${
                    idx === 0 ? 'border-yellow-500/50' : 'border-slate-700/30'
                  }`}
                >
                  <div className="flex items-center gap-4">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${
                      idx === 0 ? 'bg-yellow-500 text-black' :
                      idx === 1 ? 'bg-slate-400 text-black' :
                      idx === 2 ? 'bg-orange-600 text-white' :
                      'bg-slate-700 text-white'
                    }`}>
                      {idx + 1}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <p className={`font-semibold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                          {referrer.telegramId || referrer.wallet.slice(0, 10) + '...'}
                        </p>
                        {referrer.topReferrer && (
                          <span className="px-2 py-0.5 rounded text-xs bg-yellow-500/10 text-yellow-400">
                            TOP REFERRER
                          </span>
                        )}
                      </div>
                      <code className="text-sm text-slate-500">{referrer.wallet}</code>
                    </div>
                    <div className="text-right">
                      <p className="text-2xl font-bold text-purple-400">
                        {(referrer.rewardsEarned / 1000000).toFixed(2)}M CRM
                      </p>
                      <p className="text-sm text-slate-500">
                        {referrer.qualifiedReferrals} / {referrer.totalReferrals} referrals
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Telegram Integration Tab */}
      {activeTab === 'telegram' && (
        <div className="space-y-6">
          <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
            <h3 className={`font-semibold mb-4 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
              Telegram Bot Configuration
            </h3>

            <div className="grid md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div>
                  <label className={`block text-sm mb-2 ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                    Bot Username
                  </label>
                  <input
                    type="text"
                    defaultValue={telegramConfig.botUsername}
                    className={`w-full px-4 py-2 rounded-lg border ${darkMode ? 'bg-slate-900 border-slate-700 text-white' : 'bg-white border-slate-300'}`}
                  />
                </div>

                <div>
                  <label className={`block text-sm mb-2 ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                    Welcome Message
                  </label>
                  <textarea
                    defaultValue={telegramConfig.welcomeMessage}
                    rows={4}
                    className={`w-full px-4 py-2 rounded-lg border ${darkMode ? 'bg-slate-900 border-slate-700 text-white' : 'bg-white border-slate-300'}`}
                  />
                </div>

                <div>
                  <label className={`block text-sm mb-2 ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                    Referral Command
                  </label>
                  <input
                    type="text"
                    defaultValue={telegramConfig.referralCommand}
                    className={`w-full px-4 py-2 rounded-lg border ${darkMode ? 'bg-slate-900 border-slate-700 text-white' : 'bg-white border-slate-300'}`}
                  />
                </div>

                <div className="flex items-center justify-between p-3 rounded-lg bg-slate-900/30">
                  <span className={`text-sm ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>Auto-Reply to Referrals</span>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" defaultChecked className="sr-only peer" />
                    <div className="w-11 h-6 bg-slate-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
                  </label>
                </div>
              </div>

              <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-900/50' : 'bg-slate-50'}`}>
                <p className={`text-sm font-medium mb-3 ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                  BOT MESSAGE PREVIEW
                </p>
                <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800' : 'bg-white'} border border-slate-700`}>
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 rounded-full bg-blue-500 flex items-center justify-center">
                      <Bot className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <p className="font-medium text-blue-400">RugMuncherBot</p>
                      <p className={`text-sm mt-1 ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>
                        {telegramConfig.welcomeMessage}
                      </p>
                      <p className={`text-sm mt-2 ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                        Use /referral to get your unique link!
                      </p>
                    </div>
                  </div>
                </div>

                <div className="mt-4 p-4 rounded-lg border border-purple-500/30 bg-purple-500/5">
                  <p className="text-sm text-purple-400 mb-2">AVAILABLE COMMANDS</p>
                  <ul className="space-y-1 text-sm text-slate-400">
                    <li>/start - Show welcome message</li>
                    <li>/referral - Generate referral link</li>
                    <li>/stats - View referral stats</li>
                    <li>/leaderboard - Top referrers</li>
                    <li>/help - Command list</li>
                  </ul>
                </div>
              </div>
            </div>

            <div className="mt-6 flex gap-3">
              <button className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700">
                Save Configuration
              </button>
              <button className="px-6 py-2 bg-slate-700 text-white rounded-lg hover:bg-slate-600">
                Test Bot Connection
              </button>
            </div>
          </div>

          {/* Message Templates */}
          <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
            <h3 className={`font-semibold mb-4 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
              Telegram Message Templates
            </h3>
            <div className="space-y-4">
              {campaigns.filter(c => c.telegramBotEnabled).map(campaign => (
                <div key={campaign.id} className={`p-4 rounded-lg ${darkMode ? 'bg-slate-900/50' : 'bg-slate-50'}`}>
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium text-white">{campaign.name}</span>
                    <span className="text-xs text-slate-500">Code: {campaign.code}</span>
                  </div>
                  <textarea
                    defaultValue={campaign.telegramMessageTemplate}
                    className={`w-full px-3 py-2 rounded border text-sm ${darkMode ? 'bg-slate-800 border-slate-700 text-slate-300' : 'bg-white border-slate-300'}`}
                    rows={2}
                  />
                  <div className="flex gap-2 mt-2">
                    <button className="text-xs px-3 py-1 bg-purple-600 text-white rounded hover:bg-purple-700">
                      Update Template
                    </button>
                    <button className="text-xs px-3 py-1 bg-slate-700 text-white rounded hover:bg-slate-600">
                      Preview in Bot
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Analytics Tab */}
      {activeTab === 'analytics' && (
        <div className="grid md:grid-cols-2 gap-6">
          <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
            <h3 className={`font-semibold mb-4 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
              Referral Sources
            </h3>
            <div className="space-y-3">
              {[
                { source: 'Telegram Bot', count: 856, percent: 68 },
                { source: 'Direct Link', count: 312, percent: 25 },
                { source: 'Twitter/X', count: 56, percent: 4 },
                { source: 'Discord', count: 23, percent: 2 }
              ].map(source => (
                <div key={source.source}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className={darkMode ? 'text-slate-300' : 'text-slate-700'}>{source.source}</span>
                    <span className="text-slate-400">{source.count} ({source.percent}%)</span>
                  </div>
                  <div className={`h-2 rounded-full ${darkMode ? 'bg-slate-700' : 'bg-slate-200'}`}>
                    <div className="h-full rounded-full bg-purple-500" style={{ width: `${source.percent}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
            <h3 className={`font-semibold mb-4 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
              Daily Signups (Last 7 Days)
            </h3>
            <div className="space-y-2">
              {[
                { day: 'Apr 14', count: 45 },
                { day: 'Apr 13', count: 62 },
                { day: 'Apr 12', count: 38 },
                { day: 'Apr 11', count: 55 },
                { day: 'Apr 10', count: 71 },
                { day: 'Apr 9', count: 48 },
                { day: 'Apr 8', count: 33 }
              ].map((day, idx, arr) => {
                const max = Math.max(...arr.map(d => d.count));
                return (
                  <div key={day.day} className="flex items-center gap-3">
                    <span className="text-sm text-slate-500 w-12">{day.day}</span>
                    <div className={`flex-1 h-6 rounded ${darkMode ? 'bg-slate-700' : 'bg-slate-200'}`}>
                      <div
                        className="h-full rounded bg-green-500 flex items-center justify-end px-2"
                        style={{ width: `${(day.count / max) * 100}%` }}
                      >
                        <span className="text-xs text-white font-medium">{day.count}</span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
