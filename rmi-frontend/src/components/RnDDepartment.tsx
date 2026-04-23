import React, { useState } from 'react';
import {
  Lightbulb,
  FlaskConical,
  Rocket,
  Beaker,
  Microscope,
  Target,
  Users,
  Clock,
  CheckCircle,
  XCircle,
  AlertTriangle,
  ChevronDown,
  ChevronUp,
  Plus,
  MessageSquare,
  ThumbsUp,
  ThumbsDown,
  FileText,
  Code,
  GitBranch,
  Zap,
  Brain,
  Cpu,
  Send
} from 'lucide-react';

interface Idea {
  id: string;
  title: string;
  description: string;
  category: 'product' | 'feature' | 'research' | 'partnership';
  status: 'proposed' | 'evaluating' | 'approved' | 'rejected' | 'in_development' | 'launched';
  votes: number;
  submittedBy: string;
  submittedAt: string;
  estimatedImpact: 'low' | 'medium' | 'high' | 'massive';
  estimatedEffort: 'small' | 'medium' | 'large' | 'enterprise';
  comments: Comment[];
  aiAnalysis?: {
    score: number;
    reasoning: string[];
    similarProducts: string[];
    marketSize: string;
  };
}

interface Comment {
  id: string;
  author: string;
  content: string;
  timestamp: string;
  votes: number;
}

interface Experiment {
  id: string;
  name: string;
  hypothesis: string;
  status: 'planning' | 'running' | 'analyzing' | 'completed' | 'cancelled';
  startDate: string;
  endDate?: string;
  participants: number;
  metrics: { label: string; value: string; change: string; positive: boolean }[];
}

const RnDDepartment: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'ideas' | 'experiments' | 'pipeline'>('ideas');
  const [selectedIdea, setSelectedIdea] = useState<string | null>(null);
  const [showSubmitModal, setShowSubmitModal] = useState(false);

  const ideas: Idea[] = [
    {
      id: 'i1',
      title: 'MetaMask Snap Integration',
      description: 'Build a MetaMask Snap that provides rug pull warnings directly in the wallet interface. Users get instant alerts when interacting with suspicious contracts.',
      category: 'product',
      status: 'evaluating',
      votes: 47,
      submittedBy: 'Community Member',
      submittedAt: '3 days ago',
      estimatedImpact: 'massive',
      estimatedEffort: 'large',
      comments: [
        { id: 'c1', author: 'RMI_Team', content: 'High potential for user acquisition. MetaMask has 30M+ users.', timestamp: '2 days ago', votes: 12 },
        { id: 'c2', author: 'Dev_Lead', content: 'Technical feasibility confirmed. 3-month dev timeline.', timestamp: '1 day ago', votes: 8 }
      ],
      aiAnalysis: {
        score: 92,
        reasoning: ['Large addressable market', 'No direct competitor', 'Aligns with core mission', 'High technical complexity'],
        similarProducts: ['Revoke.cash', 'Fire.com'],
        marketSize: '$150M ARR potential'
      }
    },
    {
      id: 'i2',
      title: 'AI-Powered Predictive Scam Detection',
      description: 'Train LLM to predict scams before they launch based on team behavior, funding patterns, and social signals.',
      category: 'research',
      status: 'in_development',
      votes: 89,
      submittedBy: 'AI_Team',
      submittedAt: '2 weeks ago',
      estimatedImpact: 'high',
      estimatedEffort: 'enterprise',
      comments: [],
      aiAnalysis: {
        score: 88,
        reasoning: ['Technical moat creation', 'First-mover advantage', 'Data requirements significant'],
        similarProducts: ['Chainalysis', 'Nansen'],
        marketSize: '$500M+ TAM'
      }
    },
    {
      id: 'i3',
      title: 'Mobile App with Push Notifications',
      description: 'Native iOS/Android app for real-time wallet alerts. Critical for user retention and engagement.',
      category: 'product',
      status: 'proposed',
      votes: 156,
      submittedBy: 'Product_Lead',
      submittedAt: '1 week ago',
      estimatedImpact: 'high',
      estimatedEffort: 'large',
      comments: [
        { id: 'c3', author: 'Mobile_Dev', content: 'Flutter could give us both platforms from one codebase.', timestamp: '5 days ago', votes: 15 }
      ],
      aiAnalysis: {
        score: 85,
        reasoning: ['User demand high', 'Competitive necessity', 'Development cost significant'],
        similarProducts: ['Zerion', 'Zapper'],
        marketSize: '$200M ARR potential'
      }
    },
    {
      id: 'i4',
      title: 'Integration with 1inch for Recovery Swaps',
      description: 'Partner with 1inch to allow users who detect honeypots to instantly swap to safe tokens before getting trapped.',
      category: 'partnership',
      status: 'approved',
      votes: 34,
      submittedBy: 'Biz_Dev',
      submittedAt: '5 days ago',
      estimatedImpact: 'medium',
      estimatedEffort: 'medium',
      comments: [],
      aiAnalysis: {
        score: 78,
        reasoning: ['Clear user benefit', 'Revenue share opportunity', 'Technical integration complexity'],
        similarProducts: ['None direct'],
        marketSize: '$25M ARR potential'
      }
    }
  ];

  const experiments: Experiment[] = [
    {
      id: 'e1',
      name: 'A/B: Real-time vs Digest Alerts',
      hypothesis: 'Users receiving real-time alerts have 40% higher retention than daily digest users',
      status: 'running',
      startDate: '2026-04-01',
      participants: 5000,
      metrics: [
        { label: 'Retention (7d)', value: '68%', change: '+12%', positive: true },
        { label: 'Alert CTR', value: '23%', change: '+5%', positive: true },
        { label: 'Unsubscribe Rate', value: '2.1%', change: '-0.8%', positive: true }
      ]
    },
    {
      id: 'e2',
      name: 'New Command: /simulate',
      hypothesis: 'Users who simulate transactions before executing have 90% lower loss rates',
      status: 'analyzing',
      startDate: '2026-03-15',
      endDate: '2026-04-15',
      participants: 2500,
      metrics: [
        { label: 'Usage Rate', value: '34%', change: '+15%', positive: true },
        { label: 'Loss Rate', value: '1.2%', change: '-4.8%', positive: true },
        { label: 'User Satisfaction', value: '4.6/5', change: '+0.3', positive: true }
      ]
    }
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'proposed': return 'bg-gray-500/20 text-gray-400';
      case 'evaluating': return 'bg-yellow-500/20 text-yellow-400';
      case 'approved': return 'bg-green-500/20 text-green-400';
      case 'in_development': return 'bg-blue-500/20 text-blue-400';
      case 'launched': return 'bg-purple-500/20 text-purple-400';
      case 'rejected': return 'bg-red-500/20 text-red-400';
      default: return 'bg-gray-500/20 text-gray-400';
    }
  };

  const selectedIdeaData = ideas.find(i => i.id === selectedIdea);

  return (
    <div className="min-h-screen bg-[#0a0812] text-gray-100 font-mono selection:bg-[#7c3aed]/30">
      {/* Header */}
      <div className="bg-gradient-to-r from-[#0f0c1d] via-[#1a1525] to-[#0f0c1d] border-b border-[#7c3aed]/30">
        <div className="max-w-[1600px] mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <FlaskConical className="w-8 h-8 text-[#7c3aed]" />
              <div>
                <h1 className="text-xl font-bold tracking-wider">
                  R&D <span className="text-[#7c3aed]">LABORATORY</span>
                </h1>
                <p className="text-xs text-gray-500 tracking-[0.2em]">INNOVATION & INCUBATION CENTER</p>
              </div>
            </div>

            <button
              onClick={() => setShowSubmitModal(true)}
              className="flex items-center gap-2 px-4 py-2 bg-[#7c3aed] hover:bg-[#6d28d9] text-white rounded transition-all"
            >
              <Plus className="w-4 h-4" />
              SUBMIT IDEA
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-[1600px] mx-auto p-6 space-y-6">
        {/* Stats */}
        <div className="grid grid-cols-5 gap-4">
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-5">
            <Lightbulb className="w-6 h-6 text-[#7c3aed] mb-2" />
            <div className="text-2xl font-bold">{ideas.length}</div>
            <div className="text-xs text-gray-500">Active Ideas</div>
          </div>
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-5">
            <Beaker className="w-6 h-6 text-blue-400 mb-2" />
            <div className="text-2xl font-bold">{experiments.length}</div>
            <div className="text-xs text-gray-500">Running Experiments</div>
          </div>
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-5">
            <Rocket className="w-6 h-6 text-green-400 mb-2" />
            <div className="text-2xl font-bold">3</div>
            <div className="text-xs text-gray-500">In Development</div>
          </div>
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-5">
            <CheckCircle className="w-6 h-6 text-purple-400 mb-2" />
            <div className="text-2xl font-bold">12</div>
            <div className="text-xs text-gray-500">Launched (2026)</div>
          </div>
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-5">
            <Brain className="w-6 h-6 text-yellow-400 mb-2" />
            <div className="text-2xl font-bold">4</div>
            <div className="text-xs text-gray-500">AI Evaluations</div>
          </div>
        </div>

        {/* Navigation */}
        <div className="flex items-center gap-1 border-b border-gray-800">
          {[
            { id: 'ideas', label: 'IDEA BOARD', icon: <Lightbulb className="w-4 h-4" /> },
            { id: 'experiments', label: 'EXPERIMENTS', icon: <Beaker className="w-4 h-4" /> },
            { id: 'pipeline', label: 'DEV PIPELINE', icon: <GitBranch className="w-4 h-4" /> },
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

        {/* Content */}
        {activeTab === 'ideas' && (
          <div className="grid grid-cols-2 gap-4">
            {ideas.map((idea) => (
              <div
                key={idea.id}
                onClick={() => setSelectedIdea(idea.id)}
                className={`bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border rounded-lg p-5 cursor-pointer transition-all ${
                  selectedIdea === idea.id ? 'border-[#7c3aed]' : 'border-gray-800 hover:border-gray-700'
                }`}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-1 rounded text-[10px] font-bold ${getStatusColor(idea.status)}`}>
                      {idea.status.toUpperCase()}
                    </span>
                    <span className="px-2 py-1 bg-gray-800 rounded text-[10px] text-gray-400 uppercase">
                      {idea.category}
                    </span>
                  </div>
                  <div className="flex items-center gap-1 text-[#7c3aed]">
                    <ThumbsUp className="w-4 h-4" />
                    <span className="text-sm font-semibold">{idea.votes}</span>
                  </div>
                </div>

                <h3 className="font-semibold text-lg mb-2">{idea.title}</h3>
                <p className="text-sm text-gray-400 mb-3 line-clamp-2">{idea.description}</p>

                <div className="flex items-center gap-4 text-xs text-gray-500 mb-3">
                  <span>Impact: <span className={`${idea.estimatedImpact === 'massive' ? 'text-red-400' : idea.estimatedImpact === 'high' ? 'text-yellow-400' : 'text-gray-300'}`}>{idea.estimatedImpact.toUpperCase()}</span></span>
                  <span>Effort: <span className="text-gray-300">{idea.estimatedEffort.toUpperCase()}</span></span>
                </div>

                {idea.aiAnalysis && (
                  <div className="bg-[#0a0812] rounded-lg p-3 border border-gray-800">
                    <div className="flex items-center gap-2 mb-2">
                      <Brain className="w-4 h-4 text-[#7c3aed]" />
                      <span className="text-xs font-semibold">AI Score: {idea.aiAnalysis.score}/100</span>
                    </div>
                    <div className="text-xs text-gray-500">Market: {idea.aiAnalysis.marketSize}</div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {activeTab === 'experiments' && (
          <div className="space-y-4">
            {experiments.map((exp) => (
              <div key={exp.id} className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="font-semibold text-lg">{exp.name}</h3>
                    <p className="text-sm text-gray-400 mt-1">{exp.hypothesis}</p>
                  </div>
                  <span className={`px-3 py-1 rounded text-xs font-bold ${
                    exp.status === 'running' ? 'bg-green-500/20 text-green-400' :
                    exp.status === 'analyzing' ? 'bg-yellow-500/20 text-yellow-400' :
                    exp.status === 'completed' ? 'bg-blue-500/20 text-blue-400' :
                    'bg-gray-700 text-gray-400'
                  }`}>
                    {exp.status.toUpperCase()}
                  </span>
                </div>

                <div className="grid grid-cols-3 gap-4 mb-4">
                  {exp.metrics.map((metric, idx) => (
                    <div key={idx} className="bg-[#0a0812] rounded-lg p-3">
                      <div className="text-xs text-gray-500 mb-1">{metric.label}</div>
                      <div className="text-xl font-bold">{metric.value}</div>
                      <div className={`text-xs ${metric.positive ? 'text-green-400' : 'text-red-400'}`}>
                        {metric.change}
                      </div>
                    </div>
                  ))}
                </div>

                <div className="flex items-center gap-4 text-xs text-gray-500">
                  <span>Participants: {exp.participants.toLocaleString()}</span>
                  <span>•</span>
                  <span>Started: {exp.startDate}</span>
                  {exp.endDate && <><span>•</span><span>Ended: {exp.endDate}</span></>}
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'pipeline' && (
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
            <h2 className="text-lg font-bold mb-6">Development Pipeline</h2>
            <div className="space-y-4">
              {[
                { stage: 'Research', items: ['AI Scam Prediction', 'Behavioral Biometrics'], color: 'bg-gray-500' },
                { stage: 'Design', items: ['MetaMask Snap UX', 'Mobile App Wireframes'], color: 'bg-yellow-500' },
                { stage: 'Development', items: ['Notification System V2', 'Base Chain Expansion'], color: 'bg-blue-500' },
                { stage: 'Testing', items: ['New Command Suite', 'API Rate Limiting'], color: 'bg-purple-500' },
                { stage: 'Launch Ready', items: ['Discord Integration', 'Wallet Recovery Flow'], color: 'bg-green-500' },
              ].map((stage, idx) => (
                <div key={idx} className="flex items-start gap-4">
                  <div className={`w-4 h-4 rounded-full ${stage.color} mt-1 shadow-[0_0_10px_currentColor]`} />
                  <div className="flex-1">
                    <div className="font-semibold mb-2">{stage.stage}</div>
                    <div className="flex flex-wrap gap-2">
                      {stage.items.map((item, iidx) => (
                        <span key={iidx} className="px-3 py-1 bg-[#0a0812] border border-gray-800 rounded-full text-sm">
                          {item}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Submit Idea Modal */}
      {showSubmitModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-[#1a1525] border border-gray-800 rounded-xl p-6 max-w-lg w-full">
            <h3 className="text-lg font-bold mb-4">Submit New Idea</h3>
            <div className="space-y-4">
              <input
                type="text"
                placeholder="Idea Title"
                className="w-full px-4 py-3 bg-[#0a0812] border border-gray-800 rounded-lg text-white focus:border-[#7c3aed] focus:outline-none"
              />
              <textarea
                placeholder="Describe your idea..."
                rows={4}
                className="w-full px-4 py-3 bg-[#0a0812] border border-gray-800 rounded-lg text-white focus:border-[#7c3aed] focus:outline-none"
              />
              <select className="w-full px-4 py-3 bg-[#0a0812] border border-gray-800 rounded-lg text-white focus:border-[#7c3aed] focus:outline-none">
                <option>Product</option>
                <option>Feature</option>
                <option>Research</option>
                <option>Partnership</option>
              </select>
            </div>
            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setShowSubmitModal(false)}
                className="flex-1 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm hover:bg-gray-700 transition-all"
              >
                CANCEL
              </button>
              <button
                onClick={() => setShowSubmitModal(false)}
                className="flex-1 py-2 bg-[#7c3aed] text-white rounded-lg text-sm hover:bg-[#6d28d9] transition-all"
              >
                SUBMIT FOR REVIEW
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RnDDepartment;
