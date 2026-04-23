import { useState } from 'react';
import { Briefcase, CheckCircle2, Clock, AlertTriangle, Zap, Calendar, TrendingUp, Target, Lightbulb, MessageSquare, ExternalLink, ChevronRight, Shield, BarChart3, Users, RefreshCw, CheckSquare, Plus } from 'lucide-react';
import { useAppStore } from '../store/appStore';

interface DailyRecommendation {
  id: string;
  category: 'urgent' | 'growth' | 'maintenance' | 'opportunity' | 'community';
  title: string;
  description: string;
  priority: 'critical' | 'high' | 'medium' | 'low';
  estimatedTime: string;
  impact: string;
  actionable: boolean;
  actionText?: string;
  actionLink?: string;
  completed: boolean;
  source: 'ai' | 'analytics' | 'community' | 'system';
  createdAt: string;
}

interface DailyStats {
  tasksCompleted: number;
  tasksPending: number;
  criticalAlerts: number;
  growthOpportunities: number;
  communityPulse: number;
  systemHealth: number;
}

const mockRecommendations: DailyRecommendation[] = [
  {
    id: '1',
    category: 'urgent',
    title: 'CRM V2 Tokenomics Final Review',
    description: 'The tokenomics spreadsheet needs final sign-off before smart contract deployment. Review the 1:1 liquidity recovery calculations and tax structure.',
    priority: 'critical',
    estimatedTime: '45 min',
    impact: 'Blocks launch timeline',
    actionable: true,
    actionText: 'Review Tokenomics',
    actionLink: '/crm-v2-planning',
    completed: false,
    source: 'ai',
    createdAt: new Date().toISOString()
  },
  {
    id: '2',
    category: 'growth',
    title: 'Capitalize on Base Grant Window',
    description: 'Base Ecosystem Grant applications close in 48 hours. We have a strong case with MunchMaps integration. High probability of $50K+ funding.',
    priority: 'high',
    estimatedTime: '2 hours',
    impact: '$50,000+ potential',
    actionable: true,
    actionText: 'Apply for Grant',
    actionLink: '/capital-acquisition',
    completed: false,
    source: 'analytics',
    createdAt: new Date().toISOString()
  },
  {
    id: '3',
    category: 'community',
    title: 'Address Rising FUD in Telegram',
    description: 'Sentiment analysis shows 23% increase in negative comments about V2 launch timeline. Recommend proactive AMA session.',
    priority: 'high',
    estimatedTime: '30 min',
    impact: 'Prevents community erosion',
    actionable: true,
    actionText: 'View Sentinel Alerts',
    actionLink: '/community-sentinel',
    completed: false,
    source: 'community',
    createdAt: new Date().toISOString()
  },
  {
    id: '4',
    category: 'opportunity',
    title: 'ETHGlobal Hackathon Deadline',
    description: 'Tokyo hackathon submission due in 5 days. Prize pool includes $50K security track. We have a working MunchMaps demo ready.',
    priority: 'medium',
    estimatedTime: '4 hours',
    impact: 'Visibility + $50K prize',
    actionable: true,
    actionText: 'Review Hackathon Plan',
    actionLink: '/capital-acquisition',
    completed: false,
    source: 'analytics',
    createdAt: new Date().toISOString()
  },
  {
    id: '5',
    category: 'maintenance',
    title: 'Update Social Media Content Calendar',
    description: 'Only 2 days of scheduled content remaining. Recommend batching 2 weeks of posts focusing on CRM V2 education.',
    priority: 'medium',
    estimatedTime: '1 hour',
    impact: 'Consistent presence',
    actionable: true,
    actionText: 'Open Calendar',
    actionLink: '/social',
    completed: false,
    source: 'system',
    createdAt: new Date().toISOString()
  },
  {
    id: '6',
    category: 'growth',
    title: 'Airdrop Signup Momentum Slowing',
    description: 'Daily signups down 34% from peak. Recommend targeted Twitter campaign highlighting 1:1 recovery guarantee.',
    priority: 'medium',
    estimatedTime: '45 min',
    impact: '+500 signups projected',
    actionable: true,
    actionText: 'View Airdrop Stats',
    actionLink: '/airdrop-mgmt',
    completed: false,
    source: 'analytics',
    createdAt: new Date().toISOString()
  }
];

const dailyStats: DailyStats = {
  tasksCompleted: 3,
  tasksPending: 12,
  criticalAlerts: 2,
  growthOpportunities: 4,
  communityPulse: 72,
  systemHealth: 98
};

export default function ChiefOfStaff() {
  const { theme } = useAppStore();
  const darkMode = theme === 'dark';

  const [recommendations, setRecommendations] = useState<DailyRecommendation[]>(mockRecommendations);
  const [filterCategory, setFilterCategory] = useState<string>('all');
  const [selectedRec, setSelectedRec] = useState<string | null>(null);

  const stats = {
    total: recommendations.length,
    urgent: recommendations.filter(r => r.category === 'urgent' && !r.completed).length,
    growth: recommendations.filter(r => r.category === 'growth' && !r.completed).length,
    completed: recommendations.filter(r => r.completed).length
  };

  const filteredRecs = filterCategory === 'all'
    ? recommendations.filter(r => !r.completed)
    : recommendations.filter(r => r.category === filterCategory && !r.completed);

  const markComplete = (id: string) => {
    setRecommendations(recommendations.map(r =>
      r.id === id ? { ...r, completed: true } : r
    ));
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return 'text-red-400 bg-red-500/10';
      case 'high': return 'text-orange-400 bg-orange-500/10';
      case 'medium': return 'text-yellow-400 bg-yellow-500/10';
      default: return 'text-slate-400 bg-slate-500/10';
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'urgent': return AlertTriangle;
      case 'growth': return TrendingUp;
      case 'maintenance': return Clock;
      case 'opportunity': return Lightbulb;
      case 'community': return Users;
      default: return Zap;
    }
  };

  const getSourceColor = (source: string) => {
    switch (source) {
      case 'ai': return 'text-purple-400';
      case 'analytics': return 'text-blue-400';
      case 'community': return 'text-green-400';
      default: return 'text-slate-400';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
        <div className="flex items-center gap-3 mb-2">
          <Briefcase className="w-8 h-8 text-purple-500" />
          <h1 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
            CHIEF OF STAFF
          </h1>
          <span className="px-2 py-1 bg-purple-500/10 text-purple-400 text-xs font-mono rounded">
            DAILY BRIEFING
          </span>
        </div>
        <p className={`${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
          AI-powered daily recommendations and strategic priorities for the RMI operation.
        </p>
      </div>

      {/* Daily Stats */}
      <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
        <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
          <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Tasks Done</p>
          <p className="text-2xl font-bold text-green-400">{dailyStats.tasksCompleted}</p>
        </div>
        <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
          <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Pending</p>
          <p className="text-2xl font-bold text-yellow-400">{dailyStats.tasksPending}</p>
        </div>
        <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
          <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Critical</p>
          <p className="text-2xl font-bold text-red-400">{dailyStats.criticalAlerts}</p>
        </div>
        <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
          <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Opportunities</p>
          <p className="text-2xl font-bold text-blue-400">{dailyStats.growthOpportunities}</p>
        </div>
        <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
          <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Community</p>
          <p className="text-2xl font-bold text-purple-400">{dailyStats.communityPulse}%</p>
        </div>
        <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
          <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>System Health</p>
          <p className="text-2xl font-bold text-green-400">{dailyStats.systemHealth}%</p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-2">
        {[
          { id: 'all', label: 'All Tasks', count: stats.total },
          { id: 'urgent', label: 'Urgent', count: recommendations.filter(r => r.category === 'urgent' && !r.completed).length },
          { id: 'growth', label: 'Growth', count: recommendations.filter(r => r.category === 'growth' && !r.completed).length },
          { id: 'opportunity', label: 'Opportunities', count: recommendations.filter(r => r.category === 'opportunity' && !r.completed).length },
          { id: 'community', label: 'Community', count: recommendations.filter(r => r.category === 'community' && !r.completed).length },
          { id: 'maintenance', label: 'Maintenance', count: recommendations.filter(r => r.category === 'maintenance' && !r.completed).length }
        ].map(cat => (
          <button
            key={cat.id}
            onClick={() => setFilterCategory(cat.id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${
              filterCategory === cat.id
                ? 'bg-purple-600 text-white'
                : darkMode
                ? 'bg-slate-800 text-slate-400 hover:text-white'
                : 'bg-white text-slate-600 hover:text-slate-900 border border-slate-200'
            }`}
          >
            {cat.label} ({cat.count})
          </button>
        ))}
      </div>

      {/* Recommendations List */}
      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-4">
          <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
            <div className="flex items-center justify-between mb-4">
              <h3 className={`font-semibold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                Today's Priorities
              </h3>
              <button className="flex items-center gap-2 px-3 py-1.5 bg-purple-600 text-white rounded-lg hover:bg-purple-700 text-sm">
                <RefreshCw className="w-4 h-4" />
                Refresh
              </button>
            </div>

            <div className="space-y-3">
              {filteredRecs.map(rec => {
                const CategoryIcon = getCategoryIcon(rec.category);
                return (
                  <div
                    key={rec.id}
                    onClick={() => setSelectedRec(selectedRec === rec.id ? null : rec.id)}
                    className={`p-4 rounded-lg border cursor-pointer transition-all ${
                      selectedRec === rec.id
                        ? 'border-purple-500 bg-purple-500/5'
                        : darkMode
                        ? 'border-slate-700 hover:border-slate-600'
                        : 'border-slate-200 hover:border-slate-300'
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <div className={`p-2 rounded-lg ${rec.category === 'urgent' ? 'bg-red-500/20' : 'bg-purple-500/20'}`}>
                        <CategoryIcon className={`w-5 h-5 ${rec.category === 'urgent' ? 'text-red-400' : 'text-purple-400'}`} />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2 flex-wrap">
                          <h4 className={`font-semibold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                            {rec.title}
                          </h4>
                          <span className={`px-2 py-0.5 rounded text-xs ${getPriorityColor(rec.priority)}`}>
                            {rec.priority.toUpperCase()}
                          </span>
                          <span className={`text-xs ${getSourceColor(rec.source)}`}>
                            via {rec.source.toUpperCase()}
                          </span>
                        </div>
                        <p className={`text-sm mt-1 ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                          {rec.description}
                        </p>
                        <div className="flex items-center gap-4 mt-3 text-sm">
                          <span className="text-slate-500 flex items-center gap-1">
                            <Clock className="w-4 h-4" />
                            {rec.estimatedTime}
                          </span>
                          <span className="text-green-400 flex items-center gap-1">
                            <Target className="w-4 h-4" />
                            {rec.impact}
                          </span>
                        </div>

                        {selectedRec === rec.id && rec.actionable && (
                          <div className="flex gap-2 mt-4">
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                window.location.href = rec.actionLink || '#';
                              }}
                              className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
                            >
                              <ExternalLink className="w-4 h-4" />
                              {rec.actionText}
                            </button>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                markComplete(rec.id);
                              }}
                              className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                            >
                              <CheckSquare className="w-4 h-4" />
                              Mark Complete
                            </button>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
            <h3 className={`font-semibold mb-4 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
              Quick Actions
            </h3>
            <div className="space-y-2">
              <button className="w-full py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg flex items-center justify-center gap-2">
                <AlertTriangle className="w-4 h-4" />
                View Critical Alerts
              </button>
              <button className="w-full py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg flex items-center justify-center gap-2">
                <BarChart3 className="w-4 h-4" />
                View Analytics
              </button>
              <button className="w-full py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg flex items-center justify-center gap-2">
                <TrendingUp className="w-4 h-4" />
                Funding Pipeline
              </button>
            </div>
          </div>

          <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
            <h3 className={`font-semibold mb-4 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
              AI Insights
            </h3>
            <div className="space-y-3 text-sm">
              <div className="p-3 rounded-lg bg-purple-500/10 border border-purple-500/30">
                <p className="text-purple-400 font-medium mb-1">Productivity Tip</p>
                <p className="text-slate-400">
                  Complete critical tasks before 11 AM when decision fatigue is lowest.
                </p>
              </div>
              <div className="p-3 rounded-lg bg-blue-500/10 border border-blue-500/30">
                <p className="text-blue-400 font-medium mb-1">Pattern Detected</p>
                <p className="text-slate-400">
                  Community engagement drops on weekends. Schedule important announcements for Tuesday-Thursday.
                </p>
              </div>
            </div>
          </div>

          <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
            <h3 className={`font-semibold mb-4 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
              This Week's Goals
            </h3>
            <div className="space-y-2">
              {[
                { goal: 'Finalize CRM V2 Tokenomics', progress: 85 },
                { goal: 'Submit Base Grant Application', progress: 60 },
                { goal: 'Reach 2,000 Airdrop Signups', progress: 72 },
                { goal: 'Complete Smart Contract Audit', progress: 40 }
              ].map((item, idx) => (
                <div key={idx}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className={darkMode ? 'text-slate-300' : 'text-slate-700'}>{item.goal}</span>
                    <span className="text-slate-500">{item.progress}%</span>
                  </div>
                  <div className={`h-2 rounded-full ${darkMode ? 'bg-slate-700' : 'bg-slate-200'}`}>
                    <div
                      className="h-full rounded-full bg-green-500"
                      style={{ width: `${item.progress}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
