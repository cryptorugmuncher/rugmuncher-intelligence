import React, { useState } from 'react';
import {
  BarChart3,
  PieChart,
  TrendingUp,
  TrendingDown,
  Activity,
  Users,
  MousePointer,
  Clock,
  Search,
  Target,
  Zap,
  Globe,
  Smartphone,
  Monitor,
  ChevronDown,
  ChevronUp,
  MoreHorizontal,
  Download,
  Calendar,
  Filter,
  ArrowUpRight,
  ArrowDownRight,
  Eye,
  MousePointerClick,
  Navigation,
  MapPin,
  Layers,
  Grid,
  List,
  RefreshCw,
  AlertCircle,
  CheckCircle,
  Info,
  Star,
  Flame,
  Crown,
  Trophy,
  Award,
  Target as TargetIcon
} from 'lucide-react';

interface FeatureUsage {
  id: string;
  name: string;
  category: string;
  totalUses: number;
  uniqueUsers: number;
  avgSessionTime: number; // seconds
  retentionRate: number; // percentage
  growthRate: number; // percentage
  satisfaction: number; // 1-10
  errors: number;
  trend: 'up' | 'down' | 'stable';
  lastUsed: string;
}

interface UserJourney {
  id: string;
  path: string[];
  frequency: number;
  avgTime: number;
  completionRate: number;
  dropOffPoint?: string;
}

interface SearchQuery {
  query: string;
  count: number;
  resultsClicked: number;
  avgTimeToClick: number;
  conversionRate: number;
}

interface UserSegment {
  id: string;
  name: string;
  size: number;
  characteristics: string[];
  topFeatures: string[];
  avgSessionTime: number;
  retention: number;
  ltv: number;
}

const AnalyticsPanel: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'features' | 'journeys' | 'searches' | 'segments' | 'heatmap'>('overview');
  const [timeRange, setTimeRange] = useState<'24h' | '7d' | '30d' | '90d'>('7d');

  // Feature Usage Data
  const [featureUsage] = useState<FeatureUsage[]>([
    {
      id: 'f1',
      name: 'Contract Scanner',
      category: 'Security Tools',
      totalUses: 45234,
      uniqueUsers: 12890,
      avgSessionTime: 45,
      retentionRate: 78,
      growthRate: 23,
      satisfaction: 9.2,
      errors: 12,
      trend: 'up',
      lastUsed: '2 mins ago'
    },
    {
      id: 'f2',
      name: 'Wallet Analyzer',
      category: 'Security Tools',
      totalUses: 28456,
      uniqueUsers: 8934,
      avgSessionTime: 120,
      retentionRate: 65,
      growthRate: 15,
      satisfaction: 8.7,
      errors: 8,
      trend: 'up',
      lastUsed: '5 mins ago'
    },
    {
      id: 'f3',
      name: 'Rug Pull Rehab Booking',
      category: 'Services',
      totalUses: 1234,
      uniqueUsers: 567,
      avgSessionTime: 180,
      retentionRate: 89,
      growthRate: 45,
      satisfaction: 9.8,
      errors: 2,
      trend: 'up',
      lastUsed: '15 mins ago'
    },
    {
      id: 'f4',
      name: 'MunchMaps Visualization',
      category: 'Analytics',
      totalUses: 15678,
      uniqueUsers: 4567,
      avgSessionTime: 300,
      retentionRate: 72,
      growthRate: -5,
      satisfaction: 8.1,
      errors: 23,
      trend: 'down',
      lastUsed: '1 hour ago'
    },
    {
      id: 'f5',
      name: 'AI Rug Bot Chat',
      category: 'AI Tools',
      totalUses: 89234,
      uniqueUsers: 23456,
      avgSessionTime: 240,
      retentionRate: 82,
      growthRate: 67,
      satisfaction: 9.5,
      errors: 34,
      trend: 'up',
      lastUsed: '30 seconds ago'
    },
    {
      id: 'f6',
      name: 'Treasury Dashboard',
      category: 'Admin Tools',
      totalUses: 456,
      uniqueUsers: 23,
      avgSessionTime: 600,
      retentionRate: 95,
      growthRate: 12,
      satisfaction: 9.0,
      errors: 1,
      trend: 'stable',
      lastUsed: '2 hours ago'
    },
    {
      id: 'f7',
      name: 'Social Command Center',
      category: 'Admin Tools',
      totalUses: 2345,
      uniqueUsers: 45,
      avgSessionTime: 450,
      retentionRate: 88,
      growthRate: 8,
      satisfaction: 8.9,
      errors: 5,
      trend: 'stable',
      lastUsed: '30 mins ago'
    },
    {
      id: 'f8',
      name: 'Newsletter Manager',
      category: 'Marketing',
      totalUses: 567,
      uniqueUsers: 12,
      avgSessionTime: 900,
      retentionRate: 92,
      growthRate: 15,
      satisfaction: 9.1,
      errors: 0,
      trend: 'up',
      lastUsed: '1 hour ago'
    }
  ]);

  // User Journeys
  const [journeys] = useState<UserJourney[]>([
    {
      id: 'j1',
      path: ['Landing Page', 'Scanner', 'Results', 'Share Report'],
      frequency: 12456,
      avgTime: 120,
      completionRate: 85
    },
    {
      id: 'j2',
      path: ['Landing Page', 'MunchMaps', 'Wallet Search', 'Contract Deep Dive'],
      frequency: 8923,
      avgTime: 420,
      completionRate: 72
    },
    {
      id: 'j3',
      path: ['Twitter', 'Landing Page', 'Rehab Info', 'Booking Form', 'Payment'],
      frequency: 234,
      avgTime: 600,
      completionRate: 45,
      dropOffPoint: 'Payment'
    },
    {
      id: 'j4',
      path: ['Dashboard', 'Wallet Manager', 'Add Wallet', 'Verify'],
      frequency: 567,
      avgTime: 300,
      completionRate: 68,
      dropOffPoint: 'Verify'
    }
  ]);

  // Search Queries
  const [searchQueries] = useState<SearchQuery[]>([
    { query: 'honeypot detection', count: 4567, resultsClicked: 3421, avgTimeToClick: 2.3, conversionRate: 75 },
    { query: 'rug pull check', count: 3892, resultsClicked: 2987, avgTimeToClick: 1.8, conversionRate: 77 },
    { query: 'contract scanner', count: 3245, resultsClicked: 2890, avgTimeToClick: 2.1, conversionRate: 89 },
    { query: 'wallet tracking', count: 2156, resultsClicked: 1456, avgTimeToClick: 3.2, conversionRate: 68 },
    { query: 'sleep minting', count: 1876, resultsClicked: 1654, avgTimeToClick: 2.5, conversionRate: 88 },
    { query: 'how to spot rug pull', count: 1654, resultsClicked: 1234, avgTimeToClick: 4.1, conversionRate: 75 },
    { query: 'crypto scam checker', count: 1432, resultsClicked: 987, avgTimeToClick: 2.8, conversionRate: 69 },
    { query: 'token contract analysis', count: 1234, resultsClicked: 1100, avgTimeToClick: 2.2, conversionRate: 89 }
  ]);

  // User Segments
  const [segments] = useState<UserSegment[]>([
    {
      id: 'seg1',
      name: 'Power Analysts',
      size: 2345,
      characteristics: ['Daily users', 'Multiple scans per session', 'Share reports', 'Premium subscribers'],
      topFeatures: ['Contract Scanner', 'MunchMaps', 'Wallet Clustering'],
      avgSessionTime: 600,
      retention: 94,
      ltv: 450
    },
    {
      id: 'seg2',
      name: 'Casual Checkers',
      size: 15678,
      characteristics: ['Weekly users', 'Single scan per visit', 'Mobile majority', 'Free tier'],
      topFeatures: ['Contract Scanner', 'AI Rug Bot'],
      avgSessionTime: 120,
      retention: 45,
      ltv: 25
    },
    {
      id: 'seg3',
      name: 'Rug Victims',
      size: 567,
      characteristics: ['High engagement', 'Rehab interest', 'Support needed', 'Emotional connection'],
      topFeatures: ['Rug Pull Rehab', 'Support Chat', 'Educational Content'],
      avgSessionTime: 900,
      retention: 78,
      ltv: 500
    },
    {
      id: 'seg4',
      name: 'Devs & Researchers',
      size: 892,
      characteristics: ['API users', 'Advanced features', 'Long sessions', 'Community contributors'],
      topFeatures: ['API Access', 'Advanced Analytics', 'Raw Data Export'],
      avgSessionTime: 1200,
      retention: 88,
      ltv: 200
    }
  ]);

  // Stats
  const stats = {
    totalUsers: 45678,
    activeUsers24h: 12345,
    avgSessionTime: 345,
    bounceRate: 23,
    conversionRate: 12,
    featureAdoption: 78,
    topFeature: 'AI Rug Bot Chat',
    fastestGrowing: 'Rug Pull Rehab Booking'
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up': return <TrendingUp className="w-4 h-4 text-green-400" />;
      case 'down': return <TrendingDown className="w-4 h-4 text-red-400" />;
      default: return <Activity className="w-4 h-4 text-gray-400" />;
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
                <BarChart3 className="w-5 h-5 text-[#7c3aed]" />
              </div>
              <div>
                <h1 className="text-xl font-bold tracking-wider">
                  ANALYTICS <span className="text-[#7c3aed]">COMMAND</span>
                </h1>
                <p className="text-xs text-gray-500 tracking-[0.2em]">FEATURE USAGE & USER BEHAVIOR INTELLIGENCE</p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 bg-[#0a0812] rounded-lg p-1">
                {(['24h', '7d', '30d', '90d'] as const).map((range) => (
                  <button
                    key={range}
                    onClick={() => setTimeRange(range)}
                    className={`px-3 py-1.5 rounded text-sm transition-all ${
                      timeRange === range
                        ? 'bg-[#7c3aed] text-white'
                        : 'text-gray-400 hover:text-white'
                    }`}
                  >
                    {range}
                  </button>
                ))}
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
            <div className="text-xl font-bold">{stats.totalUsers.toLocaleString()}</div>
            <div className="text-xs text-gray-500">Total Users</div>
          </div>
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
            <Activity className="w-5 h-5 text-green-400 mb-2" />
            <div className="text-xl font-bold">{stats.activeUsers24h.toLocaleString()}</div>
            <div className="text-xs text-gray-500">Active (24h)</div>
          </div>
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
            <Clock className="w-5 h-5 text-yellow-400 mb-2" />
            <div className="text-xl font-bold">{Math.floor(stats.avgSessionTime / 60)}m</div>
            <div className="text-xs text-gray-500">Avg Session</div>
          </div>
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
            <MousePointer className="w-5 h-5 text-purple-400 mb-2" />
            <div className="text-xl font-bold">{stats.bounceRate}%</div>
            <div className="text-xs text-gray-500">Bounce Rate</div>
          </div>
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
            <TargetIcon className="w-5 h-5 text-pink-400 mb-2" />
            <div className="text-xl font-bold">{stats.conversionRate}%</div>
            <div className="text-xs text-gray-500">Conversion</div>
          </div>
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
            <Zap className="w-5 h-5 text-cyan-400 mb-2" />
            <div className="text-xl font-bold">{stats.featureAdoption}%</div>
            <div className="text-xs text-gray-500">Feature Adoption</div>
          </div>
        </div>

        {/* Top Insights */}
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-gradient-to-br from-green-500/10 to-[#1a1525] border border-green-500/30 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <Crown className="w-5 h-5 text-green-400" />
              <span className="text-sm text-green-400">Top Feature</span>
            </div>
            <div className="text-lg font-bold">{stats.topFeature}</div>
            <div className="text-xs text-gray-500">89,234 uses • 9.5/10 satisfaction</div>
          </div>
          <div className="bg-gradient-to-br from-blue-500/10 to-[#1a1525] border border-blue-500/30 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <Flame className="w-5 h-5 text-blue-400" />
              <span className="text-sm text-blue-400">Fastest Growing</span>
            </div>
            <div className="text-lg font-bold">{stats.fastestGrowing}</div>
            <div className="text-xs text-gray-500">+45% growth this week</div>
          </div>
          <div className="bg-gradient-to-br from-yellow-500/10 to-[#1a1525] border border-yellow-500/30 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <AlertCircle className="w-5 h-5 text-yellow-400" />
              <span className="text-sm text-yellow-400">Needs Attention</span>
            </div>
            <div className="text-lg font-bold">MunchMaps Visualization</div>
            <div className="text-xs text-gray-500">-5% usage • 23 errors logged</div>
          </div>
        </div>

        {/* Navigation */}
        <div className="flex items-center gap-1 border-b border-gray-800">
          {[
            { id: 'overview', label: 'OVERVIEW', icon: <PieChart className="w-4 h-4" /> },
            { id: 'features', label: 'FEATURE USAGE', icon: <Grid className="w-4 h-4" /> },
            { id: 'journeys', label: 'USER JOURNEYS', icon: <Navigation className="w-4 h-4" /> },
            { id: 'searches', label: 'SEARCH QUERIES', icon: <Search className="w-4 h-4" /> },
            { id: 'segments', label: 'USER SEGMENTS', icon: <Users className="w-4 h-4" /> },
            { id: 'heatmap', label: 'HEATMAP', icon: <Layers className="w-4 h-4" /> },
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
              <h3 className="text-lg font-bold mb-4">Feature Usage Distribution</h3>
              <div className="h-64 bg-[#0a0812] rounded-lg flex items-center justify-center border border-gray-800">
                <div className="text-center text-gray-500">
                  <PieChart className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p>Usage distribution chart</p>
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-bold mb-4">Daily Active Users Trend</h3>
              <div className="h-64 bg-[#0a0812] rounded-lg flex items-center justify-center border border-gray-800">
                <div className="text-center text-gray-500">
                  <TrendingUp className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p>DAU trend chart</p>
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-bold mb-4">Top Performing Features</h3>
              <div className="space-y-3">
                {featureUsage
                  .sort((a, b) => b.totalUses - a.totalUses)
                  .slice(0, 5)
                  .map((feature, idx) => (
                    <div key={feature.id} className="flex items-center justify-between p-3 bg-[#0a0812] rounded-lg">
                      <div className="flex items-center gap-3">
                        <span className="w-6 h-6 bg-[#7c3aed]/20 rounded-full flex items-center justify-center text-xs text-[#7c3aed]">
                          {idx + 1}
                        </span>
                        <div>
                          <div className="font-semibold">{feature.name}</div>
                          <div className="text-xs text-gray-500">{feature.category}</div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="font-semibold">{feature.totalUses.toLocaleString()}</div>
                        <div className="text-xs text-gray-500">uses</div>
                      </div>
                    </div>
                  ))}
              </div>
            </div>

            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-bold mb-4">Satisfaction Scores</h3>
              <div className="space-y-3">
                {featureUsage
                  .sort((a, b) => b.satisfaction - a.satisfaction)
                  .slice(0, 5)
                  .map((feature) => (
                    <div key={feature.id} className="p-3 bg-[#0a0812] rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-semibold">{feature.name}</span>
                        <span className={`text-sm ${feature.satisfaction >= 9 ? 'text-green-400' : feature.satisfaction >= 8 ? 'text-yellow-400' : 'text-red-400'}`}>
                          {feature.satisfaction}/10
                        </span>
                      </div>
                      <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full ${
                            feature.satisfaction >= 9 ? 'bg-green-400' :
                            feature.satisfaction >= 8 ? 'bg-yellow-400' :
                            'bg-red-400'
                          }`}
                          style={{ width: `${feature.satisfaction * 10}%` }}
                        ></div>
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          </div>
        )}

        {/* Features Tab */}
        {activeTab === 'features' && (
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <div className="relative flex-1 max-w-md">
                <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
                <input
                  type="text"
                  placeholder="Search features..."
                  className="w-full pl-10 pr-4 py-2 bg-[#0a0812] border border-gray-800 rounded text-sm"
                />
              </div>
              <select className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm">
                <option>All Categories</option>
                <option>Security Tools</option>
                <option>AI Tools</option>
                <option>Admin Tools</option>
                <option>Services</option>
              </select>
              <button className="flex items-center gap-2 px-3 py-2 bg-gray-800 border border-gray-700 rounded text-sm text-gray-400 hover:bg-gray-700 transition-all">
                <Download className="w-4 h-4" />
                EXPORT
              </button>
            </div>

            <div className="grid grid-cols-2 gap-4">
              {featureUsage.map((feature) => (
                <div key={feature.id} className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-5">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h3 className="font-bold">{feature.name}</h3>
                      <p className="text-xs text-gray-500">{feature.category}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      {getTrendIcon(feature.trend)}
                      <span className={`text-xs ${feature.growthRate > 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {feature.growthRate > 0 ? '+' : ''}{feature.growthRate}%
                      </span>
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-3 mb-4">
                    <div className="p-2 bg-[#0a0812] rounded text-center">
                      <div className="text-lg font-bold">{feature.totalUses.toLocaleString()}</div>
                      <div className="text-[10px] text-gray-500">USES</div>
                    </div>
                    <div className="p-2 bg-[#0a0812] rounded text-center">
                      <div className="text-lg font-bold">{feature.uniqueUsers.toLocaleString()}</div>
                      <div className="text-[10px] text-gray-500">USERS</div>
                    </div>
                    <div className="p-2 bg-[#0a0812] rounded text-center">
                      <div className={`text-lg font-bold ${feature.satisfaction >= 9 ? 'text-green-400' : feature.satisfaction >= 8 ? 'text-yellow-400' : 'text-red-400'}`}>
                        {feature.satisfaction}
                      </div>
                      <div className="text-[10px] text-gray-500">RATING</div>
                    </div>
                  </div>

                  <div className="flex items-center justify-between text-xs text-gray-500 mb-3">
                    <span>Retention: {feature.retentionRate}%</span>
                    <span>Avg Time: {Math.floor(feature.avgSessionTime / 60)}m</span>
                    <span>Errors: {feature.errors}</span>
                  </div>

                  <div className="flex gap-2">
                    <button className="flex-1 py-2 bg-[#7c3aed]/10 border border-[#7c3aed]/30 rounded text-xs text-[#7c3aed] hover:bg-[#7c3aed]/20 transition-all">
                      VIEW DETAILS
                    </button>
                    <button className="px-3 py-2 bg-gray-800 rounded text-xs text-gray-400 hover:bg-gray-700 transition-all">
                      EDIT
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Journeys Tab */}
        {activeTab === 'journeys' && (
          <div className="space-y-4">
            {journeys.map((journey) => (
              <div key={journey.id} className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
                <div className="flex items-start justify-between mb-6">
                  <div>
                    <h3 className="font-bold">Journey #{journey.id}</h3>
                    <p className="text-sm text-gray-500">{journey.frequency.toLocaleString()} users • {Math.floor(journey.avgTime / 60)}m avg</p>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <div className="text-lg font-bold text-green-400">{journey.completionRate}%</div>
                      <div className="text-xs text-gray-500">completion</div>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-4">
                  {journey.path.map((step, idx) => (
                    <React.Fragment key={idx}>
                      <div className={`px-4 py-2 rounded-lg text-sm font-semibold ${
                        journey.dropOffPoint === step ? 'bg-red-500/20 text-red-400 border border-red-500/30' : 'bg-[#0a0812] border border-gray-800'
                      }`}>
                        {step}
                      </div>
                      {idx < journey.path.length - 1 && (
                        <ArrowUpRight className="w-4 h-4 text-gray-600" />
                      )}
                    </React.Fragment>
                  ))}
                </div>

                {journey.dropOffPoint && (
                  <div className="mt-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg">
                    <div className="flex items-center gap-2 text-red-400 text-sm">
                      <AlertCircle className="w-4 h-4" />
                      <span>Drop-off point: {journey.dropOffPoint} - {100 - journey.completionRate}% of users exit here</span>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Searches Tab */}
        {activeTab === 'searches' && (
          <div className="space-y-4">
            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold">Top Search Queries</h3>
                <span className="text-sm text-gray-500">Last 30 days</span>
              </div>
              <div className="space-y-3">
                {searchQueries.map((sq, idx) => (
                  <div key={idx} className="p-4 bg-[#0a0812] rounded-lg">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-3">
                        <span className="text-[#7c3aed] font-bold">#{idx + 1}</span>
                        <span className="font-semibold text-lg">"{sq.query}"</span>
                      </div>
                      <span className="text-2xl font-bold">{sq.count.toLocaleString()}</span>
                    </div>
                    <div className="grid grid-cols-3 gap-4 text-sm">
                      <div>
                        <span className="text-gray-500">CTR:</span>
                        <span className="ml-2 font-semibold">{((sq.resultsClicked / sq.count) * 100).toFixed(1)}%</span>
                      </div>
                      <div>
                        <span className="text-gray-500">Avg Time:</span>
                        <span className="ml-2 font-semibold">{sq.avgTimeToClick}s</span>
                      </div>
                      <div>
                        <span className="text-gray-500">Conversion:</span>
                        <span className="ml-2 font-semibold text-green-400">{sq.conversionRate}%</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-bold mb-4">Search Insights</h3>
              <div className="grid grid-cols-3 gap-4">
                <div className="p-4 bg-[#0a0812] rounded-lg">
                  <div className="text-sm text-gray-500 mb-1">Most Searched Topic</div>
                  <div className="font-semibold">Honeypot Detection</div>
                  <div className="text-xs text-gray-500">4,567 searches</div>
                </div>
                <div className="p-4 bg-[#0a0812] rounded-lg">
                  <div className="text-sm text-gray-500 mb-1">Zero Results Queries</div>
                  <div className="font-semibold text-yellow-400">23</div>
                  <div className="text-xs text-gray-500">Opportunity for new content</div>
                </div>
                <div className="p-4 bg-[#0a0812] rounded-lg">
                  <div className="text-sm text-gray-500 mb-1">Search Conversion</div>
                  <div className="font-semibold text-green-400">78.5%</div>
                  <div className="text-xs text-gray-500">Users who find what they need</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Segments Tab */}
        {activeTab === 'segments' && (
          <div className="grid grid-cols-2 gap-4">
            {segments.map((segment) => (
              <div key={segment.id} className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="font-bold text-lg">{segment.name}</h3>
                    <p className="text-sm text-gray-500">{segment.size.toLocaleString()} users ({((segment.size / stats.totalUsers) * 100).toFixed(1)}%)</p>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-green-400">${segment.ltv}</div>
                    <div className="text-xs text-gray-500">LTV</div>
                  </div>
                </div>

                <div className="space-y-4">
                  <div>
                    <div className="text-xs text-gray-500 mb-2">Characteristics</div>
                    <div className="flex flex-wrap gap-2">
                      {segment.characteristics.map((char, idx) => (
                        <span key={idx} className="px-2 py-1 bg-gray-800 rounded text-xs">
                          {char}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div>
                    <div className="text-xs text-gray-500 mb-2">Top Features</div>
                    <div className="space-y-1">
                      {segment.topFeatures.map((feature, idx) => (
                        <div key={idx} className="flex items-center gap-2 text-sm">
                          <span className="w-4 h-4 bg-[#7c3aed]/20 rounded flex items-center justify-center text-[10px] text-[#7c3aed]">
                            {idx + 1}
                          </span>
                          {feature}
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div className="p-2 bg-[#0a0812] rounded text-center">
                      <div className="text-lg font-bold">{Math.floor(segment.avgSessionTime / 60)}m</div>
                      <div className="text-[10px] text-gray-500">AVG SESSION</div>
                    </div>
                    <div className="p-2 bg-[#0a0812] rounded text-center">
                      <div className="text-lg font-bold">{segment.retention}%</div>
                      <div className="text-[10px] text-gray-500">RETENTION</div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Heatmap Tab */}
        {activeTab === 'heatmap' && (
          <div className="space-y-6">
            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold">Click Heatmap</h3>
                <select className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm">
                  <option>Homepage</option>
                  <option>Scanner Page</option>
                  <option>MunchMaps</option>
                  <option>Dashboard</option>
                </select>
              </div>
              <div className="h-96 bg-[#0a0812] rounded-lg flex items-center justify-center border border-gray-800 relative">
                <div className="text-center text-gray-500">
                  <Layers className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p>Heatmap visualization</p>
                </div>
                {/* Simulated heat points */}
                <div className="absolute top-1/4 left-1/3 w-16 h-16 bg-red-500/30 rounded-full blur-xl"></div>
                <div className="absolute top-1/3 left-1/2 w-12 h-12 bg-yellow-500/30 rounded-full blur-xl"></div>
                <div className="absolute bottom-1/3 right-1/4 w-20 h-20 bg-red-500/40 rounded-full blur-xl"></div>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
                <div className="text-xs text-gray-500 mb-1">Hot Zone 1</div>
                <div className="font-semibold">Scan Button</div>
                <div className="text-lg font-bold text-red-400">34.2%</div>
                <div className="text-xs text-gray-500">of all clicks</div>
              </div>
              <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
                <div className="text-xs text-gray-500 mb-1">Hot Zone 2</div>
                <div className="font-semibold">Results Share</div>
                <div className="text-lg font-bold text-yellow-400">18.7%</div>
                <div className="text-xs text-gray-500">of all clicks</div>
              </div>
              <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
                <div className="text-xs text-gray-500 mb-1">Hot Zone 3</div>
                <div className="font-semibold">Connect Wallet</div>
                <div className="text-lg font-bold text-orange-400">12.3%</div>
                <div className="text-xs text-gray-500">of all clicks</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AnalyticsPanel;
