import React, { useState } from 'react';
import {
  TrendingUp,
  MessageSquare,
  Heart,
  Repeat2,
  Eye,
  Zap,
  Target,
  AlertCircle,
  CheckCircle,
  Clock,
  Calendar,
  Hash,
  BarChart3,
  Users,
  Sparkles,
  Lightbulb,
  ArrowUpRight,
  ArrowDownRight,
  Copy,
  Save,
  RefreshCw,
  Filter,
  Search,
  ChevronDown,
  ChevronUp,
  Send,
  Image as ImageIcon,
  Film,
  Mic,
  FileText,
  Globe,
  Bot,
  Shield,
  Flame,
  TrendingDown,
  Activity,
  Award,
  Lock,
  Unlock,
  XCircle,
  Plus,
  Trash2,
  Edit3,
  Play,
  Pause,
  Settings,
  Bell,
  Pin,
  Bookmark,
  Share2,
  MoreHorizontal,
  Cpu,
  Brain,
  Network,
  Radio,
  Satellite,
  Scan,
  Search as SearchIcon,
  Command,
  Terminal,
  Code,
  GitBranch,
  Layers,
  Hexagon,
  Pentagon,
  Octagon,
  Square,
  Circle,
  Triangle,
  Star,
  Diamond,
  Crown,
  Trophy,
  Medal,
  Flag,
  Map,
  Compass,
  Navigation,
  Anchor,
  Anchor as AnchorIcon,
  Paperclip,
  Link as LinkIcon,
  ExternalLink,
  Link2,
  Unlink,
  Paperclip as PaperclipIcon,
  Upload,
  Download,
  Cloud,
  CloudOff,
  Sun,
  Moon,
  Sunrise,
  Sunset,
  CloudRain,
  CloudSnow,
  CloudLightning,
  Wind,
  Thermometer,
  Droplets,
  Umbrella,
  Snowflake,
  Flame as FlameIcon,
  FireExtinguisher,
  Radiation,
  Biohazard,
  Skull,
  Ghost,
  Rocket as RocketIcon,
  Plane,
  Helicopter,
  Ship,
  Car,
  Truck,
  Bike,
  Train,
  Bus,
  Fuel,
  Battery,
  BatteryCharging,
  BatteryFull,
  BatteryMedium,
  BatteryLow,
  BatteryWarning,
  Plug,
  ZapOff,
  Zap as ZapIcon,
  Power,
  PowerOff,
  Activity as ActivityIcon,
  HeartPulse,
  HeartCrack,
  HeartOff,
  Heart as HeartIcon,
  Star as StarIcon,
  ThumbsUp,
  ThumbsDown,
  ThumbsUp as ThumbsUpIcon,
  ThumbsDown as ThumbsDownIcon,
  Smile,
  Frown,
  Meh,
  Laugh,
  Annoyed,
  Angry,
  Dices,
  Dice1,
  Dice2,
  Dice3,
  Dice4,
  Dice5,
  Dice6,
  Gamepad2,
  Gamepad,
  Joystick,
  Puzzle,
  Brain as BrainIcon,
  Headphones,
  Music,
  Mic as MicIcon,
  MicOff,
  Volume1,
  Volume2,
  VolumeX,
  Speaker,
  Radio as RadioIcon,
  RadioReceiver,
  Monitor,
  Smartphone,
  Laptop,
  Keyboard,
  Mouse,
  MousePointer2,
  MousePointerClick,
  Cast,
  Bluetooth,
  BluetoothOff,
  BluetoothConnected,
  Wifi,
  WifiOff,
  Usb,
  Cable,
  BatteryCharging as BatteryChargingIcon,
  BatteryFull as BatteryFullIcon,
  BatteryMedium as BatteryMediumIcon,
  BatteryLow as BatteryLowIcon,
  BatteryWarning as BatteryWarningIcon,
  Plug as PlugIcon,
  ZapOff as ZapOffIcon,
  Power as PowerIcon,
  PowerOff as PowerOffIcon,
  Activity as ActivityIcon2,
  HeartPulse as HeartPulseIcon,
  HeartCrack as HeartCrackIcon,
  HeartOff as HeartOffIcon,
  Star as StarIcon2,
  ThumbsUp as ThumbsUpIcon2,
  ThumbsDown as ThumbsDownIcon2,
  Smile as SmileIcon,
  Frown as FrownIcon,
  Meh as MehIcon,
  Laugh as LaughIcon,
  Annoyed as AnnoyedIcon,
  Angry as AngryIcon
} from 'lucide-react';

interface ContentSuggestion {
  id: string;
  type: 'thread' | 'single' | 'poll' | 'spaces' | 'video' | 'meme';
  title: string;
  hook: string;
  content: string[];
  hashtags: string[];
  optimalTime: string;
  predictedEngagement: {
    impressions: string;
    likes: string;
    retweets: string;
    replies: string;
    score: number;
  };
  aiScore: number;
  reasoning: string[];
  trendingTopic?: string;
  urgency: 'low' | 'medium' | 'high' | 'breaking';
  category: 'education' | 'alert' | 'update' | 'engagement' | 'viral';
}

interface PerformanceMetric {
  metric: string;
  current: string;
  previous: string;
  change: number;
  benchmark: string;
  status: 'above' | 'below' | 'on_track';
  recommendation: string;
}

interface CompetitorAnalysis {
  account: string;
  handle: string;
  followers: number;
  engagementRate: number;
  postFrequency: string;
  strengths: string[];
  weaknesses: string[];
  opportunities: string[];
}

interface ContentGap {
  topic: string;
  searchVolume: string;
  competition: 'low' | 'medium' | 'high';
  difficulty: 'easy' | 'medium' | 'hard';
  opportunity: string;
  suggestedAngle: string;
}

const TwitterOptimizer: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'suggestions' | 'performance' | 'competitors' | 'gaps' | 'schedule'>('suggestions');
  const [selectedSuggestion, setSelectedSuggestion] = useState<string | null>(null);
  const [contentFilter, setContentFilter] = useState<'all' | 'education' | 'alert' | 'viral'>('all');
  const [isGenerating, setIsGenerating] = useState(false);

  const suggestions: ContentSuggestion[] = [
    {
      id: 's1',
      type: 'thread',
      title: 'The Anatomy of a $5M Rug Pull',
      hook: 'I just analyzed the biggest rug pull of 2026.\n\nHere\'s exactly how they stole $5M from 2,300 wallets (and how to spot it next time): 🧵',
      content: [
        '1/ The Setup:\n\n• Fake team with AI-generated LinkedIn profiles\n• Copied whitepaper from 3 failed projects\n• "Certik audit pending" (never submitted)\n• 50K Telegram members (80% bots)',
        '2/ The Contract Trap:\n\nHidden mint function disguised as "rewards distributor"\n\nOnly 3 people noticed the 0.5% supply mint capability before launch',
        '3/ The Execution:\n\n• Day 1-3: Normal trading, build confidence\n• Day 4: Mint 500M tokens to dev wallet\n• Day 5: Dump everything in 12 minutes\n• Day 6: Website gone, socials deleted',
        '4/ Red Flags You Missed:\n\n✗ Ownership not renounced\n✗ No timelock on admin functions\n✗ Liquidity locked for only 30 days\n✗ 3 wallets controlled 67% of supply',
        '5/ How RMI Detected It:\n\nOur AI flagged this 48 hours before the rug:\n• Contract similarity: 94% match to 3 previous rugs\n• Team wallet clustering detected\n• Social sentiment anomaly: -40% in 6 hours',
        '6/ The Aftermath:\n\n• 2,300 victims\n• $5.2M stolen\n• $0 recovered\n• Dev wallets: Already cashed out through Tornado',
        '7/ Protect Yourself:\n\nBefore aping ANY token:\n1. Check @rugmunchbot scan\n2. Verify team credentials\n3. Review contract ownership\n4. Check our AI risk score\n\nThread bookmarked? Good. It might save you.',
      ],
      hashtags: ['#RugPull', '#CryptoSecurity', '#Web3Safety', '#DeFi'],
      optimalTime: '2026-04-15 09:00 EST',
      predictedEngagement: {
        impressions: '450K',
        likes: '8,500',
        retweets: '4,200',
        replies: '1,800',
        score: 94
      },
      aiScore: 96,
      reasoning: [
        'Educational content performs 340% better than promotional',
        'Specific numbers increase credibility and shareability',
        'Thread format encourages bookmarking and return visits',
        'Emotional hook (fear of loss) drives engagement',
        'Actionable ending increases follow conversion'
      ],
      trendingTopic: '#RugPull education',
      urgency: 'high',
      category: 'education'
    },
    {
      id: 's2',
      type: 'single',
      title: 'Breaking: New Honeypot Variant',
      hook: '🚨 NEW SCAM ALERT 🚨\n\n"Sleep Minting" - tokens tradable for 24h, then unsellable\n\n6 contracts deployed in 48h\n180+ victims already\n\nHow it works 👇',
      content: [
        'Scammers deploy contract with delayed sell restriction\n\nBlock 1-10,000: Normal trading (build trust)\nBlock 10,001+: sell() function reverts\n\nBy then, devs already dumped.',
        '',
        'Check BEFORE you buy:\n✅ @rugmunchbot contract scan\n✅ Test sell on small amount first\n✅ Verify sell function exists & works',
        '',
        'RT to save a degen.'
      ],
      hashtags: ['#CryptoScam', '#Honeypot', '#Web3Security'],
      optimalTime: 'NOW - Breaking news',
      predictedEngagement: {
        impressions: '280K',
        likes: '5,200',
        retweets: '6,800',
        replies: '890',
        score: 88
      },
      aiScore: 92,
      reasoning: [
        'Breaking news format creates urgency',
        'Technical explanation builds authority',
        'High retweet potential (saving others)',
        'FOMO on new information drives engagement'
      ],
      urgency: 'breaking',
      category: 'alert'
    },
    {
      id: 's3',
      type: 'poll',
      title: 'Community Engagement Poll',
      hook: 'What\'s your biggest fear in crypto?',
      content: [
        'A) Getting rugged 🔴',
        'B) Missing the 100x 🚀',
        'C) Tax audit 📊',
        'D) Telling my spouse 😰',
        '',
        'Comment why below 👇'
      ],
      hashtags: ['#CryptoCommunity', '#Web3'],
      optimalTime: '2026-04-14 19:00 EST',
      predictedEngagement: {
        impressions: '120K',
        likes: '3,400',
        retweets: '1,200',
        replies: '2,500',
        score: 76
      },
      aiScore: 78,
      reasoning: [
        'Polls drive 3x more replies than regular posts',
        'Humorous option (D) increases participation',
        'Comment prompt extends engagement time',
        'Good for algorithmic boost during low-engagement hours'
      ],
      urgency: 'low',
      category: 'engagement'
    },
    {
      id: 's4',
      type: 'video',
      title: '30-Second Contract Scan Tutorial',
      hook: 'How to spot a rug pull in 30 seconds:\n\n(Without reading a single line of code)',
      content: [
        '[Video: Screen recording of @rugmunchbot scan]',
        '',
        '3 red flags this contract is dangerous:\n\n🚩 Hidden mint function detected\n🚩 Owner can drain liquidity\n🚩 67% supply controlled by 3 wallets',
        '',
        'Full scan results in bio link 👆',
        '',
        'Follow for daily security tips 🛡️'
      ],
      hashtags: ['#CryptoTips', '#DeFiSecurity', '#Tutorial'],
      optimalTime: '2026-04-16 12:00 EST',
      predictedEngagement: {
        impressions: '520K',
        likes: '12,000',
        retweets: '5,600',
        replies: '1,400',
        score: 91
      },
      aiScore: 94,
      reasoning: [
        'Video content gets 10x more reach than text',
        'Short-form (30s) has highest completion rate',
        'Visual demonstration > text explanation',
        'Tutorial content builds authority and trust',
        'Product placement feels natural, not salesy'
      ],
      urgency: 'medium',
      category: 'viral'
    },
    {
      id: 's5',
      type: 'spaces',
      title: 'Weekly AMA: Rug Pull Stories',
      hook: '🎙️ SPACES TONIGHT 🎙️\n\n"I survived a $2M rug pull"\n\nGuest: @degen_survivor\nTime: 8 PM EST\n\nTopics:\n• Red flags they missed\n• How they recovered\n• What they do differently now',
      content: [
        'Set reminder 👆',
        '',
        'Drop your questions below ⬇️'
      ],
      hashtags: ['#CryptoAMA', '#Spaces', '#Community'],
      optimalTime: '2026-04-14 20:00 EST',
      predictedEngagement: {
        impressions: '95K',
        likes: '2,100',
        retweets: '890',
        replies: '450',
        score: 72
      },
      aiScore: 75,
      reasoning: [
        'Spaces drive high-quality follower engagement',
        'Story format creates emotional connection',
        'Scheduled events build anticipation',
        'Live interaction builds community loyalty'
      ],
      urgency: 'medium',
      category: 'engagement'
    }
  ];

  const performanceMetrics: PerformanceMetric[] = [
    {
      metric: 'Engagement Rate',
      current: '4.2%',
      previous: '3.8%',
      change: 10.5,
      benchmark: '3.5%',
      status: 'above',
      recommendation: 'Continue thread format - performing 340% above baseline'
    },
    {
      metric: 'Impression per Post',
      current: '45.2K',
      previous: '38.9K',
      change: 16.2,
      benchmark: '28K',
      status: 'above',
      recommendation: 'Post during 9-11 AM EST for 23% more reach'
    },
    {
      metric: 'Profile Clicks',
      current: '2.1%',
      previous: '2.8%',
      change: -25,
      benchmark: '2.5%',
      status: 'below',
      recommendation: 'Add stronger CTA in post endings. Current: 12% have CTA, target: 80%'
    },
    {
      metric: 'Follower Growth',
      current: '+1,240/week',
      previous: '+890/week',
      change: 39.3,
      benchmark: '+600/week',
      status: 'above',
      recommendation: 'Viral content driving growth. Maintain 2 educational threads/week'
    },
    {
      metric: 'Link CTR',
      current: '3.8%',
      previous: '4.2%',
      change: -9.5,
      benchmark: '3.2%',
      status: 'on_track',
      recommendation: 'Test "link in bio" vs direct URL in post'
    },
    {
      metric: 'Video Completion Rate',
      current: '34%',
      previous: '28%',
      change: 21.4,
      benchmark: '25%',
      status: 'above',
      recommendation: 'Videos 30-45s perform best. Increase video output by 50%'
    }
  ];

  const competitors: CompetitorAnalysis[] = [
    {
      account: 'Bubblemaps',
      handle: '@bubblemaps',
      followers: 125000,
      engagementRate: 3.8,
      postFrequency: '2-3x daily',
      strengths: ['Visual content', 'Celebrity endorsements', 'Exchange partnerships'],
      weaknesses: ['Expensive tiers', 'No free real-time alerts', 'Limited chains'],
      opportunities: ['Position RMI as accessible alternative', 'Emphasize free tier advantages', 'Target their unhappy users']
    },
    {
      account: 'Chainalysis',
      handle: '@chainalysis',
      followers: 890000,
      engagementRate: 1.2,
      postFrequency: '1x daily',
      strengths: ['Institutional authority', 'Research reports', 'Media coverage'],
      weaknesses: ['Enterprise-focused', 'No retail product', 'High price point'],
      opportunities: ['Retail angle: "Chainalysis for everyone"', 'Consumer-friendly insights', 'Democratize security']
    },
    {
      account: 'DeFiLlama',
      handle: '@DefiLlama',
      followers: 670000,
      engagementRate: 4.5,
      postFrequency: '5-10x daily',
      strengths: ['Data accuracy', 'Community trust', 'Speed of updates'],
      weaknesses: ['No security focus', 'Complex UI', 'Information overload'],
      opportunities: ['Security + data combination', 'Simpler UX narrative', 'Alert integration']
    }
  ];

  const contentGaps: ContentGap[] = [
    {
      topic: 'Base Chain Security',
      searchVolume: 'High (340% increase)',
      competition: 'low',
      difficulty: 'easy',
      opportunity: '72% of new launches on Base, limited security content',
      suggestedAngle: 'Base-specific honeypot detection guides and real-time alerts'
    },
    {
      topic: 'AI in Crypto Security',
      searchVolume: 'Very High (exploding)',
      competition: 'medium',
      difficulty: 'medium',
      opportunity: '$AI token narrative trending, security angle underexplored',
      suggestedAngle: '"AI for Good" - how AI Swarm prevents scams vs speculative tokens'
    },
    {
      topic: 'Wallet Recovery Stories',
      searchVolume: 'High',
      competition: 'low',
      difficulty: 'easy',
      opportunity: '"How to recover" searches up 450%',
      suggestedAngle: 'Success stories from 1-1 Reimbursement Program participants'
    },
    {
      topic: 'Celebrity Token Warnings',
      searchVolume: 'Very High (cyclical)',
      competition: 'medium',
      difficulty: 'easy',
      opportunity: 'Celebrity tokens pump then dump predictably',
      suggestedAngle: 'Pre-launch warnings about celebrity token patterns'
    },
    {
      topic: 'Social Engineering Attacks',
      searchVolume: 'Medium (growing)',
      competition: 'low',
      difficulty: 'medium',
      opportunity: 'Discord/Twitter DM scams rising 400%',
      suggestedAngle: 'How scammers compromise accounts and impersonate support'
    }
  ];

  const filteredSuggestions = contentFilter === 'all'
    ? suggestions
    : suggestions.filter(s => s.category === contentFilter);

  const getUrgencyColor = (urgency: string) => {
    switch (urgency) {
      case 'breaking': return 'bg-red-500 text-white animate-pulse';
      case 'high': return 'bg-orange-500/20 text-orange-400';
      case 'medium': return 'bg-yellow-500/20 text-yellow-400';
      case 'low': return 'bg-gray-700 text-gray-400';
      default: return 'bg-gray-700 text-gray-400';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'thread': return <FileText className="w-4 h-4" />;
      case 'single': return <MessageSquare className="w-4 h-4" />;
      case 'poll': return <BarChart3 className="w-4 h-4" />;
      case 'video': return <Film className="w-4 h-4" />;
      case 'spaces': return <Mic className="w-4 h-4" />;
      case 'meme': return <Laugh className="w-4 h-4" />;
      default: return <MessageSquare className="w-4 h-4" />;
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  return (
    <div className="min-h-screen bg-[#0a0812] text-gray-100 font-mono selection:bg-[#7c3aed]/30">
      {/* Header */}
      <div className="bg-gradient-to-r from-[#0f0c1d] via-[#1a1525] to-[#0f0c1d] border-b border-[#7c3aed]/30">
        <div className="max-w-[1600px] mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Globe className="w-8 h-8 text-[#7c3aed]" />
              <div>
                <h1 className="text-xl font-bold tracking-wider">
                  TWITTER <span className="text-[#7c3aed]">OPTIMIZER</span>
                </h1>
                <p className="text-xs text-gray-500 tracking-[0.2em]">AI-POWERED CONTENT INTELLIGENCE</p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <div className="text-right">
                <div className="text-xs text-gray-500">Content Score</div>
                <div className="text-xl font-bold text-green-400">94/100</div>
              </div>
              <button
                onClick={() => setIsGenerating(true)}
                className="flex items-center gap-2 px-4 py-2 bg-[#7c3aed] hover:bg-[#6d28d9] text-white rounded transition-all"
              >
                <Sparkles className="w-4 h-4" />
                GENERATE IDEAS
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-[1600px] mx-auto p-6 space-y-6">
        {/* Performance Overview */}
        <div className="grid grid-cols-4 gap-4">
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-5">
            <Eye className="w-6 h-6 text-[#7c3aed] mb-2" />
            <div className="text-2xl font-bold">2.4M</div>
            <div className="text-xs text-gray-500">Monthly Impressions</div>
            <div className="text-xs text-green-400 mt-1">+16.2% vs last month</div>
          </div>
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-5">
            <Heart className="w-6 h-6 text-pink-400 mb-2" />
            <div className="text-2xl font-bold">4.2%</div>
            <div className="text-xs text-gray-500">Engagement Rate</div>
            <div className="text-xs text-green-400 mt-1">+10.5% vs last month</div>
          </div>
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-5">
            <Users className="w-6 h-6 text-blue-400 mb-2" />
            <div className="text-2xl font-bold">+5,280</div>
            <div className="text-xs text-gray-500">New Followers (30d)</div>
            <div className="text-xs text-green-400 mt-1">+39.3% vs last month</div>
          </div>
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-5">
            <Target className="w-6 h-6 text-green-400 mb-2" />
            <div className="text-2xl font-bold">12.4K</div>
            <div className="text-xs text-gray-500">Profile Clicks (30d)</div>
            <div className="text-xs text-red-400 mt-1">-25% vs last month</div>
          </div>
        </div>

        {/* Navigation */}
        <div className="flex items-center gap-1 border-b border-gray-800">
          {[
            { id: 'suggestions', label: 'CONTENT SUGGESTIONS', icon: <Lightbulb className="w-4 h-4" /> },
            { id: 'performance', label: 'PERFORMANCE ANALYTICS', icon: <BarChart3 className="w-4 h-4" /> },
            { id: 'competitors', label: 'COMPETITOR INTEL', icon: <Target className="w-4 h-4" /> },
            { id: 'gaps', label: 'CONTENT GAPS', icon: <SearchIcon className="w-4 h-4" /> },
            { id: 'schedule', label: 'OPTIMAL SCHEDULE', icon: <Clock className="w-4 h-4" /> },
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

        {/* Content Suggestions Tab */}
        {activeTab === 'suggestions' && (
          <div className="space-y-6">
            {/* Filter Bar */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-500">Filter:</span>
                {['all', 'education', 'alert', 'viral'].map((filter) => (
                  <button
                    key={filter}
                    onClick={() => setContentFilter(filter as any)}
                    className={`px-3 py-1 rounded text-xs ${
                      contentFilter === filter
                        ? 'bg-[#7c3aed] text-white'
                        : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                    }`}
                  >
                    {filter.toUpperCase()}
                  </button>
                ))}
              </div>
              <div className="text-xs text-gray-500">
                {filteredSuggestions.length} suggestions available
              </div>
            </div>

            {/* Suggestions List */}
            <div className="space-y-4">
              {filteredSuggestions.map((suggestion) => (
                <div
                  key={suggestion.id}
                  className={`bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border rounded-lg overflow-hidden transition-all ${
                    selectedSuggestion === suggestion.id ? 'border-[#7c3aed]' : 'border-gray-800 hover:border-gray-700'
                  }`}
                >
                  <div
                    className="p-5 cursor-pointer"
                    onClick={() => setSelectedSuggestion(selectedSuggestion === suggestion.id ? null : suggestion.id)}
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-3">
                        <span className={`px-2 py-1 rounded text-[10px] font-bold ${getUrgencyColor(suggestion.urgency)}`}>
                          {suggestion.urgency === 'breaking' ? '🔴 BREAKING' : suggestion.urgency.toUpperCase()}
                        </span>
                        <span className="px-2 py-1 bg-gray-800 rounded text-[10px] text-gray-400 uppercase flex items-center gap-1">
                          {getTypeIcon(suggestion.type)}
                          {suggestion.type}
                        </span>
                        <span className="px-2 py-1 bg-[#7c3aed]/10 rounded text-[10px] text-[#7c3aed] uppercase">
                          {suggestion.category}
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="text-right">
                          <div className="text-xs text-gray-500">AI Score</div>
                          <div className="text-lg font-bold text-[#7c3aed]">{suggestion.aiScore}/100</div>
                        </div>
                      </div>
                    </div>

                    <h3 className="font-semibold text-lg mb-2">{suggestion.title}</h3>
                    <p className="text-sm text-gray-400 mb-4">{suggestion.hook}</p>

                    {/* Predicted Engagement */}
                    <div className="grid grid-cols-4 gap-3 mb-4">
                      <div className="bg-[#0a0812] rounded p-3 text-center">
                        <Eye className="w-4 h-4 mx-auto mb-1 text-gray-500" />
                        <div className="text-sm font-bold">{suggestion.predictedEngagement.impressions}</div>
                        <div className="text-[10px] text-gray-500">Impressions</div>
                      </div>
                      <div className="bg-[#0a0812] rounded p-3 text-center">
                        <Heart className="w-4 h-4 mx-auto mb-1 text-pink-500" />
                        <div className="text-sm font-bold">{suggestion.predictedEngagement.likes}</div>
                        <div className="text-[10px] text-gray-500">Likes</div>
                      </div>
                      <div className="bg-[#0a0812] rounded p-3 text-center">
                        <Repeat2 className="w-4 h-4 mx-auto mb-1 text-green-500" />
                        <div className="text-sm font-bold">{suggestion.predictedEngagement.retweets}</div>
                        <div className="text-[10px] text-gray-500">Retweets</div>
                      </div>
                      <div className="bg-[#0a0812] rounded p-3 text-center">
                        <MessageSquare className="w-4 h-4 mx-auto mb-1 text-blue-500" />
                        <div className="text-sm font-bold">{suggestion.predictedEngagement.replies}</div>
                        <div className="text-[10px] text-gray-500">Replies</div>
                      </div>
                    </div>

                    <div className="flex items-center justify-between">
                      <div className="text-xs text-gray-500">
                        Optimal time: <span className="text-[#7c3aed]">{suggestion.optimalTime}</span>
                      </div>
                      <div className="flex gap-2">
                        <button className="px-3 py-1.5 bg-[#7c3aed]/10 border border-[#7c3aed]/30 rounded text-xs text-[#7c3aed] hover:bg-[#7c3aed]/20 transition-all">
                          PREVIEW
                        </button>
                        <button className="px-3 py-1.5 bg-[#7c3aed] text-white rounded text-xs hover:bg-[#6d28d9] transition-all">
                          USE THIS
                        </button>
                      </div>
                    </div>
                  </div>

                  {selectedSuggestion === suggestion.id && (
                    <div className="px-5 pb-5 border-t border-gray-800 pt-4">
                      {/* Full Content Preview */}
                      <div className="mb-4">
                        <h4 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Full Content Preview</h4>
                        <div className="bg-[#0a0812] rounded-lg p-4 border border-gray-800">
                          {suggestion.content.map((line, idx) => (
                            <p key={idx} className="text-sm text-gray-300 whitespace-pre-line mb-2">{line}</p>
                          ))}
                          <div className="flex gap-2 mt-3">
                            {suggestion.hashtags.map((tag, idx) => (
                              <span key={idx} className="text-xs text-[#7c3aed]">{tag}</span>
                            ))}
                          </div>
                        </div>
                        <button
                          onClick={() => copyToClipboard(suggestion.hook + '\n\n' + suggestion.content.join('\n\n'))}
                          className="mt-2 flex items-center gap-2 text-xs text-[#7c3aed] hover:text-white transition-all"
                        >
                          <Copy className="w-3 h-3" />
                          Copy to clipboard
                        </button>
                      </div>

                      {/* AI Reasoning */}
                      <div className="bg-[#0a0812] rounded-lg p-4 border border-gray-800">
                        <h4 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-3 flex items-center gap-2">
                          <Brain className="w-4 h-4 text-[#7c3aed]" />
                          Why This Will Perform Well
                        </h4>
                        <ul className="space-y-2">
                          {suggestion.reasoning.map((reason, idx) => (
                            <li key={idx} className="flex items-start gap-2 text-sm text-gray-300">
                              <CheckCircle className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0" />
                              {reason}
                            </li>
                          ))}
                        </ul>
                      </div>

                      {suggestion.trendingTopic && (
                        <div className="mt-4 p-3 bg-green-500/10 border border-green-500/30 rounded-lg">
                          <div className="flex items-center gap-2 text-sm text-green-400">
                            <TrendingUp className="w-4 h-4" />
                            <span>Trending Topic: {suggestion.trendingTopic}</span>
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Performance Analytics Tab */}
        {activeTab === 'performance' && (
          <div className="space-y-6">
            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <h2 className="text-lg font-bold mb-6">Performance Metrics vs Benchmarks</h2>
              <div className="space-y-4">
                {performanceMetrics.map((metric, idx) => (
                  <div key={idx} className="p-4 bg-[#0a0812] rounded-lg">
                    <div className="flex items-center justify-between mb-3">
                      <div className="font-semibold">{metric.metric}</div>
                      <div className={`px-2 py-1 rounded text-xs ${
                        metric.status === 'above' ? 'bg-green-500/20 text-green-400' :
                        metric.status === 'below' ? 'bg-red-500/20 text-red-400' :
                        'bg-yellow-500/20 text-yellow-400'
                      }`}>
                        {metric.status === 'above' ? 'ABOVE TARGET' : metric.status === 'below' ? 'NEEDS ATTENTION' : 'ON TRACK'}
                      </div>
                    </div>
                    <div className="grid grid-cols-4 gap-4 text-sm">
                      <div>
                        <div className="text-xs text-gray-500">Current</div>
                        <div className="font-bold">{metric.current}</div>
                      </div>
                      <div>
                        <div className="text-xs text-gray-500">Previous</div>
                        <div className="text-gray-400">{metric.previous}</div>
                      </div>
                      <div>
                        <div className="text-xs text-gray-500">Change</div>
                        <div className={metric.change > 0 ? 'text-green-400' : 'text-red-400'}>
                          {metric.change > 0 ? '+' : ''}{metric.change}%
                        </div>
                      </div>
                      <div>
                        <div className="text-xs text-gray-500">Benchmark</div>
                        <div className="text-gray-400">{metric.benchmark}</div>
                      </div>
                    </div>
                    <div className="mt-3 pt-3 border-t border-gray-800">
                      <div className="flex items-start gap-2 text-xs">
                        <Lightbulb className="w-4 h-4 text-[#7c3aed] mt-0.5 flex-shrink-0" />
                        <span className="text-gray-300">{metric.recommendation}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-6">
              <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
                <h3 className="text-lg font-bold mb-4">Best Performing Content Types</h3>
                <div className="space-y-3">
                  {[
                    { type: 'Educational Threads', engagement: '6.8%', examples: 'Rug pull breakdowns, how-to guides', change: '+34%' },
                    { type: 'Breaking Alerts', engagement: '5.2%', examples: 'New scam warnings, exploit alerts', change: '+28%' },
                    { type: 'Video Tutorials', engagement: '8.4%', examples: '30-sec scans, feature demos', change: '+45%' },
                    { type: 'Data Visualizations', engagement: '4.9%', examples: 'Weekly stats, treasury updates', change: '+12%' },
                  ].map((item, idx) => (
                    <div key={idx} className="flex items-center justify-between p-3 bg-[#0a0812] rounded-lg">
                      <div>
                        <div className="font-semibold text-sm">{item.type}</div>
                        <div className="text-xs text-gray-500">{item.examples}</div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-bold text-[#7c3aed]">{item.engagement}</div>
                        <div className="text-xs text-green-400">{item.change}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
                <h3 className="text-lg font-bold mb-4">Optimal Posting Schedule</h3>
                <div className="space-y-3">
                  {[
                    { day: 'Monday', time: '9:00 AM EST', type: 'Educational Thread', engagement: 'High' },
                    { day: 'Tuesday', time: '12:00 PM EST', type: 'Quick Tips / Single Posts', engagement: 'Medium' },
                    { day: 'Wednesday', time: '8:00 PM EST', type: 'Spaces / Community', engagement: 'Very High' },
                    { day: 'Thursday', time: '9:00 AM EST', type: 'Data / Reports', engagement: 'High' },
                    { day: 'Friday', time: '3:00 PM EST', type: 'Memes / Light Content', engagement: 'Medium' },
                    { day: 'Weekend', time: '11:00 AM EST', type: 'Breaking News Only', engagement: 'Variable' },
                  ].map((slot, idx) => (
                    <div key={idx} className="flex items-center justify-between p-3 bg-[#0a0812] rounded-lg">
                      <div>
                        <div className="font-semibold text-sm">{slot.day}</div>
                        <div className="text-xs text-gray-500">{slot.time} - {slot.type}</div>
                      </div>
                      <span className={`text-xs px-2 py-1 rounded ${
                        slot.engagement === 'Very High' ? 'bg-green-500/20 text-green-400' :
                        slot.engagement === 'High' ? 'bg-[#7c3aed]/20 text-[#7c3aed]' :
                        'bg-gray-700 text-gray-400'
                      }`}>
                        {slot.engagement}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Competitor Intel Tab */}
        {activeTab === 'competitors' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-bold">Competitor Analysis</h2>
              <button className="px-4 py-2 bg-gray-800 border border-gray-700 rounded text-sm text-gray-400 hover:bg-gray-700 transition-all">
                <Plus className="w-4 h-4 inline mr-2" />
                Add Competitor
              </button>
            </div>

            {competitors.map((competitor, idx) => (
              <div key={idx} className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="font-semibold text-lg">{competitor.account}</h3>
                    <div className="text-sm text-gray-500">{competitor.handle}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold">{competitor.followers.toLocaleString()}</div>
                    <div className="text-xs text-gray-500">Followers</div>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-4 mb-4">
                  <div className="bg-[#0a0812] rounded p-3 text-center">
                    <div className="text-lg font-bold">{competitor.engagementRate}%</div>
                    <div className="text-xs text-gray-500">Engagement Rate</div>
                  </div>
                  <div className="bg-[#0a0812] rounded p-3 text-center">
                    <div className="text-lg font-bold">{competitor.postFrequency}</div>
                    <div className="text-xs text-gray-500">Post Frequency</div>
                  </div>
                  <div className="bg-[#0a0812] rounded p-3 text-center">
                    <div className="text-lg font-bold text-green-400">{competitor.engagementRate > 4 ? 'High' : 'Medium'}</div>
                    <div className="text-xs text-gray-500">Threat Level</div>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <h4 className="text-xs font-bold text-green-400 uppercase tracking-wider mb-2">Strengths</h4>
                    <ul className="space-y-1">
                      {competitor.strengths.map((s, i) => (
                        <li key={i} className="text-xs text-gray-300 flex items-center gap-1">
                          <CheckCircle className="w-3 h-3 text-green-400" />
                          {s}
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-red-400 uppercase tracking-wider mb-2">Weaknesses</h4>
                    <ul className="space-y-1">
                      {competitor.weaknesses.map((w, i) => (
                        <li key={i} className="text-xs text-gray-300 flex items-center gap-1">
                          <XCircle className="w-3 h-3 text-red-400" />
                          {w}
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-[#7c3aed] uppercase tracking-wider mb-2">Our Opportunities</h4>
                    <ul className="space-y-1">
                      {competitor.opportunities.map((o, i) => (
                        <li key={i} className="text-xs text-gray-300 flex items-center gap-1">
                          <Target className="w-3 h-3 text-[#7c3aed]" />
                          {o}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Content Gaps Tab */}
        {activeTab === 'gaps' && (
          <div className="space-y-4">
            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <h2 className="text-lg font-bold mb-2">Content Opportunity Analysis</h2>
              <p className="text-sm text-gray-500 mb-6">
                AI-identified gaps where search demand exceeds content supply.
                High opportunity = trending topics with limited competition.
              </p>

              <div className="space-y-4">
                {contentGaps.map((gap, idx) => (
                  <div key={idx} className="p-4 bg-[#0a0812] rounded-lg border border-gray-800">
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h3 className="font-semibold">{gap.topic}</h3>
                        <div className="text-xs text-gray-500 mt-1">Search Volume: {gap.searchVolume}</div>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={`px-2 py-1 rounded text-xs ${
                          gap.competition === 'low' ? 'bg-green-500/20 text-green-400' :
                          gap.competition === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
                          'bg-red-500/20 text-red-400'
                        }`}>
                          {gap.competition.toUpperCase()} COMPETITION
                        </span>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4 mb-3">
                      <div>
                        <div className="text-xs text-gray-500 uppercase">Difficulty</div>
                        <div className="text-sm">{gap.difficulty}</div>
                      </div>
                      <div>
                        <div className="text-xs text-gray-500 uppercase">Opportunity</div>
                        <div className="text-sm text-[#7c3aed]">{gap.opportunity}</div>
                      </div>
                    </div>

                    <div className="p-3 bg-[#7c3aed]/5 border border-[#7c3aed]/20 rounded-lg">
                      <div className="text-xs text-[#7c3aed] uppercase mb-1">Suggested Angle</div>
                      <div className="text-sm text-gray-300">{gap.suggestedAngle}</div>
                    </div>

                    <div className="flex gap-2 mt-3">
                      <button className="px-3 py-1.5 bg-[#7c3aed]/10 border border-[#7c3aed]/30 rounded text-xs text-[#7c3aed] hover:bg-[#7c3aed]/20 transition-all">
                        CREATE CONTENT
                      </button>
                      <button className="px-3 py-1.5 bg-gray-800 border border-gray-700 rounded text-xs text-gray-400 hover:bg-gray-700 transition-all">
                        SAVE FOR LATER
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Optimal Schedule Tab */}
        {activeTab === 'schedule' && (
          <div className="grid grid-cols-7 gap-3">
            {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((day, idx) => (
              <div key={idx} className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
                <div className="text-center mb-3">
                  <div className="font-semibold">{day}</div>
                  <div className="text-xs text-gray-500">{['Apr 14', 'Apr 15', 'Apr 16', 'Apr 17', 'Apr 18', 'Apr 19', 'Apr 20'][idx]}</div>
                </div>
                <div className="space-y-2">
                  {[
                    { time: '9:00 AM', content: 'Thread', type: 'education', status: 'scheduled' },
                    { time: '3:00 PM', content: 'Quick Tip', type: 'engagement', status: 'pending' },
                  ].map((slot, sidx) => (
                    <div key={sidx} className={`p-2 rounded text-xs ${
                      slot.status === 'scheduled' ? 'bg-[#7c3aed]/10 border border-[#7c3aed]/30' : 'bg-gray-800'
                    }`}>
                      <div className="text-gray-500">{slot.time}</div>
                      <div className="font-semibold">{slot.content}</div>
                    </div>
                  ))}
                  <button className="w-full py-2 border border-dashed border-gray-700 rounded text-xs text-gray-500 hover:border-[#7c3aed] hover:text-[#7c3aed] transition-all">
                    + Add Slot
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default TwitterOptimizer;
