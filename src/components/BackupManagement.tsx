import React, { useState } from 'react';
import {
  Database,
  Server,
  Cloud,
  Clock,
  CheckCircle,
  XCircle,
  AlertTriangle,
  RefreshCw,
  Download,
  Upload,
  Trash2,
  Play,
  Pause,
  Settings,
  HardDrive,
  FolderOpen,
  FileText,
  Bot,
  Brain,
  Globe,
  Shield,
  Activity,
  Calendar,
  ChevronDown,
  ChevronUp,
  Plus,
  Save,
  RotateCcw,
  ExternalLink,
  Lock,
  Key,
  Terminal,
  Layers,
  Archive,
  History,
  Code,
  Scan,
  Search,
  Filter,
  MoreHorizontal,
  Eye,
  Copy,
  Edit3,
  CheckSquare,
  Square,
  AlertCircle,
  Info,
  HelpCircle,
  MessageSquare,
  Send,
  Mail,
  Bell,
  Star,
  Heart,
  Zap,
  Flame,
  Snowflake,
  Sun,
  Moon,
  CloudRain,
  CloudSnow,
  CloudLightning,
  Wind,
  Thermometer,
  Droplets,
  Umbrella,
  Waves,
  Rocket,
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
  Power,
  Activity as ActivityIcon,
  HeartPulse,
  Stethoscope,
  Bandage,
  Syringe,
  Pill,
  Droplet,
  Gauge,
  BarChart,
  BarChart2,
  BarChart3,
  LineChart,
  AreaChart,
  PieChart,
  TrendingUp,
  TrendingDown,
  ArrowUpRight,
  ArrowDownRight,
  ArrowUpLeft,
  ArrowDownLeft,
  ArrowUp,
  ArrowDown,
  ArrowLeft,
  ArrowRight,
  Move,
  Maximize,
  Minimize,
  Maximize2,
  Minimize2,
  Expand,
  Fullscreen,
  Monitor,
  Smartphone,
  Laptop,
  Headphones,
  Speaker,
  Volume1,
  Volume2,
  VolumeX,
  Mic,
  Video,
  Camera,
  Focus,
  Image,
  Film,
  Music,
  Disc,
  User,
  Users,
  Contact,
  CreditCard,
  Wallet,
  PiggyBank,
  Landmark,
  Building,
  Store,
  ShoppingBag,
  ShoppingCart,
  Package,
  Briefcase,
  Home,
  Flag,
  Bookmark,
  BookOpen,
  Book,
  File,
  FileCheck,
  FileCode,
  FilePlus,
  Files,
  Folder,
  FolderPlus,
  LayoutGrid,
  LayoutList,
  LayoutDashboard,
  Sidebar,
  Menu,
  Keyboard,
  Mouse,
  Pointer,
  Hash,
  AtSign,
  DollarSign,
  Euro,
  PoundSterling,
  Bitcoin,
  Gift,
  Utensils,
  FlaskConical,
  Microscope,
  Dna,
  Atom,
  Orbit,
  TreePine,
  Leaf,
  Apple,
  Coffee,
  Pizza,
  IceCream,
  Cookie,
  Wine,
  Beer,
  Fish,
  Bug,
  Dog,
  Cat,
  Bird,
  Anchor,
  Palmtree,
  Sunrise,
  Sunset,
  Rainbow,
  Ghost,
  Skull,
  Bomb,
  Swords,
  Sword,
  ShieldAlert,
  ShieldCheck,
  ShieldOff,
  Sparkles,
  Circle,
  Square as SquareIcon,
  Triangle,
  Pentagon,
  Hexagon,
  Octagon,
  Ruler,
  Wand2,
  Paintbrush,
  Brush,
  Eraser,
  Pencil,
  Pen,
  Highlighter,
  Scissors,
  Crop,
  Calculator,
  Binary,
  PlusCircle,
  PlusSquare,
  Minus,
  MinusCircle,
  MinusSquare,
  Divide,
  Percent,
  X,
  Check,
  CheckCircle2,
  AlertOctagon,
  Quote,
  FunctionSquare,
  Pi,
  Infinity,
  Asterisk,
  Code2,
  CodeSquare,
  Parentheses,
  Braces,
  Brackets,
  Command,
  Option,
  Delete,
  Home as HomeIcon,
  ArrowUpCircle,
  ArrowDownCircle,
  ArrowLeftCircle,
  ArrowRightCircle,
  ChevronLeft,
  ChevronRight,
  ChevronsUp,
  ChevronsDown,
  AlignLeft,
  AlignCenter,
  AlignRight,
  Grid,
  Table,
  Sliders,
  SlidersHorizontal
} from 'lucide-react';

interface BackupJob {
  id: string;
  name: string;
  type: 'bot_memory' | 'database' | 'website' | 'ai_model' | 'rag_knowledge' | 'system_config' | 'wallet_keys' | 'logs';
  status: 'running' | 'scheduled' | 'completed' | 'failed' | 'paused';
  frequency: 'realtime' | 'hourly' | 'daily' | 'weekly' | 'monthly' | 'manual';
  lastRun: string;
  nextRun: string;
  size: string;
  retention: number; // days
  destination: 'local' | 's3' | 'gcs' | 'azure' | 'ipfs' | 'encrypted_remote';
  encryption: boolean;
  compression: boolean;
  verifyIntegrity: boolean;
  history: BackupHistoryEntry[];
}

interface BackupHistoryEntry {
  id: string;
  timestamp: string;
  status: 'success' | 'failed' | 'partial';
  size: string;
  duration: string;
  files: number;
  errors?: string[];
  verified: boolean;
}

interface RestorePoint {
  id: string;
  jobId: string;
  jobName: string;
  timestamp: string;
  size: string;
  type: string;
  status: 'available' | 'restoring' | 'corrupted' | 'expired';
  snapshot: boolean;
}

const BackupManagement: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'jobs' | 'restore' | 'storage' | 'logs'>('jobs');
  const [selectedJob, setSelectedJob] = useState<string | null>(null);
  const [isCreating, setIsCreating] = useState(false);

  const backupJobs: BackupJob[] = [
    {
      id: 'b1',
      name: 'Bot Memory State',
      type: 'bot_memory',
      status: 'scheduled',
      frequency: 'hourly',
      lastRun: '2026-04-14 09:00:00',
      nextRun: '2026-04-14 10:00:00',
      size: '4.2 GB',
      retention: 30,
      destination: 's3',
      encryption: true,
      compression: true,
      verifyIntegrity: true,
      history: [
        { id: 'h1', timestamp: '2026-04-14 09:00:00', status: 'success', size: '4.2 GB', duration: '45s', files: 1, verified: true },
        { id: 'h2', timestamp: '2026-04-14 08:00:00', status: 'success', size: '4.1 GB', duration: '42s', files: 1, verified: true },
        { id: 'h3', timestamp: '2026-04-14 07:00:00', status: 'success', size: '4.1 GB', duration: '44s', files: 1, verified: true },
      ]
    },
    {
      id: 'b2',
      name: 'PostgreSQL Database',
      type: 'database',
      status: 'running',
      frequency: 'daily',
      lastRun: '2026-04-14 00:00:00',
      nextRun: '2026-04-15 00:00:00',
      size: '128.5 GB',
      retention: 90,
      destination: 'encrypted_remote',
      encryption: true,
      compression: true,
      verifyIntegrity: true,
      history: [
        { id: 'h4', timestamp: '2026-04-14 00:00:00', status: 'success', size: '128.5 GB', duration: '12m 34s', files: 1, verified: true },
        { id: 'h5', timestamp: '2026-04-13 00:00:00', status: 'success', size: '127.8 GB', duration: '11m 45s', files: 1, verified: true },
      ]
    },
    {
      id: 'b3',
      name: 'Website Frontend',
      type: 'website',
      status: 'scheduled',
      frequency: 'daily',
      lastRun: '2026-04-14 02:00:00',
      nextRun: '2026-04-15 02:00:00',
      size: '2.3 GB',
      retention: 60,
      destination: 's3',
      encryption: false,
      compression: true,
      verifyIntegrity: true,
      history: [
        { id: 'h6', timestamp: '2026-04-14 02:00:00', status: 'success', size: '2.3 GB', duration: '2m 15s', files: 4523, verified: true },
      ]
    },
    {
      id: 'b4',
      name: 'AI Swarm Models',
      type: 'ai_model',
      status: 'scheduled',
      frequency: 'weekly',
      lastRun: '2026-04-10 03:00:00',
      nextRun: '2026-04-17 03:00:00',
      size: '45.6 GB',
      retention: 12,
      destination: 'encrypted_remote',
      encryption: true,
      compression: false,
      verifyIntegrity: true,
      history: [
        { id: 'h7', timestamp: '2026-04-10 03:00:00', status: 'success', size: '45.6 GB', duration: '45m 12s', files: 6, verified: true },
      ]
    },
    {
      id: 'b5',
      name: 'RAG Knowledge Base',
      type: 'rag_knowledge',
      status: 'scheduled',
      frequency: 'daily',
      lastRun: '2026-04-14 01:00:00',
      nextRun: '2026-04-15 01:00:00',
      size: '156.2 GB',
      retention: 30,
      destination: 's3',
      encryption: true,
      compression: true,
      verifyIntegrity: true,
      history: [
        { id: 'h8', timestamp: '2026-04-14 01:00:00', status: 'success', size: '156.2 GB', duration: '23m 45s', files: 1, verified: true },
      ]
    },
    {
      id: 'b6',
      name: 'System Configuration',
      type: 'system_config',
      status: 'paused',
      frequency: 'weekly',
      lastRun: '2026-04-07 04:00:00',
      nextRun: 'Paused',
      size: '45 MB',
      retention: 52,
      destination: 'local',
      encryption: true,
      compression: true,
      verifyIntegrity: true,
      history: [
        { id: 'h9', timestamp: '2026-04-07 04:00:00', status: 'success', size: '45 MB', duration: '3s', files: 128, verified: true },
      ]
    },
    {
      id: 'b7',
      name: 'Treasury Wallet Keys',
      type: 'wallet_keys',
      status: 'scheduled',
      frequency: 'daily',
      lastRun: '2026-04-14 00:05:00',
      nextRun: '2026-04-15 00:05:00',
      size: '12 KB',
      retention: 365,
      destination: 'encrypted_remote',
      encryption: true,
      compression: false,
      verifyIntegrity: true,
      history: [
        { id: 'h10', timestamp: '2026-04-14 00:05:00', status: 'success', size: '12 KB', duration: '1s', files: 1, verified: true },
      ]
    }
  ];

  const restorePoints: RestorePoint[] = [
    { id: 'r1', jobId: 'b1', jobName: 'Bot Memory State', timestamp: '2026-04-14 09:00:00', size: '4.2 GB', type: 'hourly', status: 'available', snapshot: false },
    { id: 'r2', jobId: 'b2', jobName: 'PostgreSQL Database', timestamp: '2026-04-14 00:00:00', size: '128.5 GB', type: 'daily', status: 'available', snapshot: false },
    { id: 'r3', jobId: 'b2', jobName: 'PostgreSQL Database', timestamp: '2026-04-13 00:00:00', size: '127.8 GB', type: 'daily', status: 'available', snapshot: false },
    { id: 'r4', jobId: 'b4', jobName: 'AI Swarm Models', timestamp: '2026-04-10 03:00:00', size: '45.6 GB', type: 'weekly', status: 'available', snapshot: true },
    { id: 'r5', jobId: 'b7', jobName: 'Treasury Wallet Keys', timestamp: '2026-04-14 00:05:00', size: '12 KB', type: 'daily', status: 'available', snapshot: true },
  ];

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'bot_memory': return <Bot className="w-5 h-5 text-blue-400" />;
      case 'database': return <Database className="w-5 h-5 text-green-400" />;
      case 'website': return <Globe className="w-5 h-5 text-purple-400" />;
      case 'ai_model': return <Brain className="w-5 h-5 text-yellow-400" />;
      case 'rag_knowledge': return <Layers className="w-5 h-5 text-pink-400" />;
      case 'system_config': return <Settings className="w-5 h-5 text-gray-400" />;
      case 'wallet_keys': return <Key className="w-5 h-5 text-red-400" />;
      case 'logs': return <FileText className="w-5 h-5 text-orange-400" />;
      default: return <Archive className="w-5 h-5" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      case 'scheduled': return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'completed': return 'bg-[#7c3aed]/20 text-[#7c3aed] border-[#7c3aed]/30';
      case 'failed': return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'paused': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      default: return 'bg-gray-700 text-gray-400';
    }
  };

  const selectedJobData = backupJobs.find(j => j.id === selectedJob);

  return (
    <div className="min-h-screen bg-[#0a0812] text-gray-100 font-mono selection:bg-[#7c3aed]/30">
      {/* Header */}
      <div className="bg-gradient-to-r from-[#0f0c1d] via-[#1a1525] to-[#0f0c1d] border-b border-[#7c3aed]/30">
        <div className="max-w-[1600px] mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Archive className="w-8 h-8 text-[#7c3aed]" />
              <div>
                <h1 className="text-xl font-bold tracking-wider">
                  BACKUP <span className="text-[#7c3aed]">COMMAND</span>
                </h1>
                <p className="text-xs text-gray-500 tracking-[0.2em]">COMPREHENSIVE DATA PROTECTION</p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <div className="text-right">
                <div className="text-xs text-gray-500">Total Protected</div>
                <div className="text-xl font-bold text-green-400">336.5 GB</div>
              </div>
              <div className="text-right">
                <div className="text-xs text-gray-500">Active Jobs</div>
                <div className="text-xl font-bold text-[#7c3aed]">6/7</div>
              </div>
              <button
                onClick={() => setIsCreating(true)}
                className="flex items-center gap-2 px-4 py-2 bg-[#7c3aed] hover:bg-[#6d28d9] text-white rounded transition-all"
              >
                <Plus className="w-4 h-4" />
                NEW BACKUP JOB
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-[1600px] mx-auto p-6 space-y-6">
        {/* Storage Overview */}
        <div className="grid grid-cols-4 gap-4">
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-5">
            <div className="flex items-center gap-2 mb-2">
              <HardDrive className="w-5 h-5 text-[#7c3aed]" />
              <span className="text-xs text-gray-500 uppercase">Local Storage</span>
            </div>
            <div className="text-2xl font-bold">45 MB</div>
            <div className="text-xs text-gray-500">Config files only</div>
          </div>
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-5">
            <div className="flex items-center gap-2 mb-2">
              <Cloud className="w-5 h-5 text-blue-400" />
              <span className="text-xs text-gray-500 uppercase">AWS S3</span>
            </div>
            <div className="text-2xl font-bold">162.7 GB</div>
            <div className="text-xs text-gray-500">Daily snapshots</div>
          </div>
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-5">
            <div className="flex items-center gap-2 mb-2">
              <Server className="w-5 h-5 text-green-400" />
              <span className="text-xs text-gray-500 uppercase">Encrypted Remote</span>
            </div>
            <div className="text-2xl font-bold">128.7 GB</div>
            <div className="text-xs text-gray-500">Air-gapped storage</div>
          </div>
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-5">
            <div className="flex items-center gap-2 mb-2">
              <Shield className="w-5 h-5 text-red-400" />
              <span className="text-xs text-gray-500 uppercase">Encryption</span>
            </div>
            <div className="text-2xl font-bold">AES-256</div>
            <div className="text-xs text-green-400">All sensitive data</div>
          </div>
        </div>

        {/* Navigation */}
        <div className="flex items-center gap-1 border-b border-gray-800">
          {[
            { id: 'jobs', label: 'BACKUP JOBS', icon: <Clock className="w-4 h-4" /> },
            { id: 'restore', label: 'RESTORE POINTS', icon: <RotateCcw className="w-4 h-4" /> },
            { id: 'storage', label: 'STORAGE POOLS', icon: <Database className="w-4 h-4" /> },
            { id: 'logs', label: 'ACTIVITY LOGS', icon: <Activity className="w-4 h-4" /> },
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
        {activeTab === 'jobs' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-bold">Active Backup Jobs</h2>
              <div className="flex items-center gap-2">
                <button className="px-3 py-1.5 bg-[#7c3aed]/10 border border-[#7c3aed]/30 rounded text-xs text-[#7c3aed] hover:bg-[#7c3aed]/20 transition-all">
                  <Play className="w-3 h-3 inline mr-1" />
                  RUN ALL NOW
                </button>
                <button className="px-3 py-1.5 bg-gray-800 border border-gray-700 rounded text-xs text-gray-400 hover:bg-gray-700 transition-all">
                  <Settings className="w-3 h-3 inline mr-1" />
                  GLOBAL SETTINGS
                </button>
              </div>
            </div>

            <div className="grid grid-cols-1 gap-4">
              {backupJobs.map((job) => (
                <div
                  key={job.id}
                  onClick={() => setSelectedJob(job.id)}
                  className={`bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border rounded-lg p-5 cursor-pointer transition-all ${
                    selectedJob === job.id ? 'border-[#7c3aed]' : 'border-gray-800 hover:border-gray-700'
                  }`}
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-[#7c3aed]/10 rounded-lg flex items-center justify-center">
                        {getTypeIcon(job.type)}
                      </div>
                      <div>
                        <h3 className="font-semibold">{job.name}</h3>
                        <div className="text-xs text-gray-500">{job.type.replace('_', ' ').toUpperCase()}</div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={`px-3 py-1 rounded text-xs font-bold border ${getStatusColor(job.status)}`}>
                        {job.status.toUpperCase()}
                      </span>
                      {job.encryption && (
                        <span title="Encrypted"><Lock className="w-4 h-4 text-green-400" /></span>
                      )}
                    </div>
                  </div>

                  <div className="grid grid-cols-6 gap-4 text-sm">
                    <div>
                      <div className="text-xs text-gray-500 uppercase">Frequency</div>
                      <div className="font-semibold">{job.frequency}</div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500 uppercase">Last Run</div>
                      <div className="font-semibold">{job.lastRun}</div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500 uppercase">Next Run</div>
                      <div className={`font-semibold ${job.status === 'paused' ? 'text-yellow-400' : ''}`}>
                        {job.nextRun}
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500 uppercase">Size</div>
                      <div className="font-semibold">{job.size}</div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500 uppercase">Retention</div>
                      <div className="font-semibold">{job.retention} days</div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500 uppercase">Destination</div>
                      <div className="font-semibold uppercase">{job.destination}</div>
                    </div>
                  </div>

                  {selectedJob === job.id && job.history.length > 0 && (
                    <div className="mt-4 pt-4 border-t border-gray-800">
                      <h4 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-3">Recent History</h4>
                      <div className="space-y-2">
                        {job.history.map((entry) => (
                          <div key={entry.id} className="flex items-center justify-between p-2 bg-[#0a0812] rounded-lg">
                            <div className="flex items-center gap-3">
                              {entry.status === 'success' ? (
                                <CheckCircle className="w-4 h-4 text-green-400" />
                              ) : (
                                <XCircle className="w-4 h-4 text-red-400" />
                              )}
                              <span className="text-xs text-gray-400">{entry.timestamp}</span>
                            </div>
                            <div className="flex items-center gap-4 text-xs">
                              <span>{entry.size}</span>
                              <span>{entry.duration}</span>
                              <span className={entry.verified ? 'text-green-400' : 'text-yellow-400'}>
                                {entry.verified ? 'Verified' : 'Unverified'}
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'restore' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-bold">Available Restore Points</h2>
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  placeholder="Search restore points..."
                  className="px-3 py-1.5 bg-gray-800 border border-gray-700 rounded text-sm"
                />
                <button className="px-3 py-1.5 bg-gray-800 border border-gray-700 rounded text-sm text-gray-400">
                  <Filter className="w-4 h-4" />
                </button>
              </div>
            </div>

            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-gray-800/50">
                  <tr className="text-left text-xs text-gray-500 uppercase tracking-wider">
                    <th className="px-4 py-3">Backup Job</th>
                    <th className="px-4 py-3">Timestamp</th>
                    <th className="px-4 py-3">Type</th>
                    <th className="px-4 py-3">Size</th>
                    <th className="px-4 py-3">Status</th>
                    <th className="px-4 py-3">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-800">
                  {restorePoints.map((point) => (
                    <tr key={point.id} className="hover:bg-gray-800/30 transition-all">
                      <td className="px-4 py-4">
                        <div className="font-semibold">{point.jobName}</div>
                        <div className="text-xs text-gray-500">ID: {point.id}</div>
                      </td>
                      <td className="px-4 py-4 text-gray-400">{point.timestamp}</td>
                      <td className="px-4 py-4">
                        <span className="px-2 py-1 bg-gray-800 rounded text-xs">{point.type}</span>
                        {point.snapshot && (
                          <span className="ml-2 px-2 py-1 bg-[#7c3aed]/20 text-[#7c3aed] rounded text-xs">SNAPSHOT</span>
                        )}
                      </td>
                      <td className="px-4 py-4">{point.size}</td>
                      <td className="px-4 py-4">
                        <span className={`px-2 py-1 rounded text-xs ${
                          point.status === 'available' ? 'bg-green-500/20 text-green-400' :
                          point.status === 'restoring' ? 'bg-blue-500/20 text-blue-400' :
                          'bg-red-500/20 text-red-400'
                        }`}>
                          {point.status.toUpperCase()}
                        </span>
                      </td>
                      <td className="px-4 py-4">
                        <div className="flex items-center gap-2">
                          <button className="px-3 py-1.5 bg-[#7c3aed]/10 border border-[#7c3aed]/30 rounded text-xs text-[#7c3aed] hover:bg-[#7c3aed]/20 transition-all">
                            RESTORE
                          </button>
                          <button className="px-3 py-1.5 bg-gray-800 border border-gray-700 rounded text-xs text-gray-400 hover:bg-gray-700 transition-all">
                            DOWNLOAD
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

        {activeTab === 'storage' && (
          <div className="grid grid-cols-2 gap-6">
            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-bold mb-4">Storage Destinations</h3>
              <div className="space-y-4">
                {[
                  { name: 'AWS S3 - Primary', used: '162.7 GB', total: '500 GB', status: 'healthy', type: 'cloud' },
                  { name: 'Encrypted Remote', used: '128.7 GB', total: '1 TB', status: 'healthy', type: 'remote' },
                  { name: 'Local NVMe', used: '45 MB', total: '2 TB', status: 'healthy', type: 'local' },
                ].map((dest, idx) => (
                  <div key={idx} className="p-4 bg-[#0a0812] rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        {dest.type === 'cloud' && <Cloud className="w-5 h-5 text-blue-400" />}
                        {dest.type === 'remote' && <Server className="w-5 h-5 text-green-400" />}
                        {dest.type === 'local' && <HardDrive className="w-5 h-5 text-gray-400" />}
                        <span className="font-semibold">{dest.name}</span>
                      </div>
                      <span className="px-2 py-1 bg-green-500/20 text-green-400 rounded text-xs">{dest.status.toUpperCase()}</span>
                    </div>
                    <div className="flex justify-between text-xs text-gray-500 mb-1">
                      <span>{dest.used} used</span>
                      <span>{dest.total} total</span>
                    </div>
                    <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                      <div className="h-full bg-[#7c3aed] rounded-full" style={{ width: '32%' }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-bold mb-4">Backup Policies</h3>
              <div className="space-y-4">
                <div className="p-4 bg-[#0a0812] rounded-lg">
                  <h4 className="font-semibold mb-2">Retention Rules</h4>
                  <ul className="space-y-2 text-sm text-gray-400">
                    <li className="flex items-center justify-between">
                      <span>Hourly backups</span>
                      <span className="text-white">Keep 30 days</span>
                    </li>
                    <li className="flex items-center justify-between">
                      <span>Daily backups</span>
                      <span className="text-white">Keep 90 days</span>
                    </li>
                    <li className="flex items-center justify-between">
                      <span>Weekly backups</span>
                      <span className="text-white">Keep 12 weeks</span>
                    </li>
                    <li className="flex items-center justify-between">
                      <span>Monthly backups</span>
                      <span className="text-white">Keep 2 years</span>
                    </li>
                  </ul>
                </div>

                <div className="p-4 bg-[#0a0812] rounded-lg">
                  <h4 className="font-semibold mb-2">Security Settings</h4>
                  <ul className="space-y-2 text-sm">
                    <li className="flex items-center justify-between">
                      <span className="text-gray-400">Encryption</span>
                      <span className="text-green-400 flex items-center gap-1">
                        <CheckCircle className="w-4 h-4" />
                        AES-256
                      </span>
                    </li>
                    <li className="flex items-center justify-between">
                      <span className="text-gray-400">Compression</span>
                      <span className="text-green-400 flex items-center gap-1">
                        <CheckCircle className="w-4 h-4" />
                        Enabled
                      </span>
                    </li>
                    <li className="flex items-center justify-between">
                      <span className="text-gray-400">Integrity Checks</span>
                      <span className="text-green-400 flex items-center gap-1">
                        <CheckCircle className="w-4 h-4" />
                        SHA-256
                      </span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'logs' && (
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
            <h2 className="text-lg font-bold mb-4">Backup Activity Log</h2>
            <div className="space-y-2 font-mono text-sm">
              {[
                { time: '10:00:00', job: 'Bot Memory State', action: 'Backup completed', status: 'success', details: '4.2 GB in 45s' },
                { time: '09:30:15', job: 'PostgreSQL Database', action: 'Verification started', status: 'info', details: 'Checking integrity...' },
                { time: '09:00:00', job: 'Bot Memory State', action: 'Backup started', status: 'info', details: 'Incremental backup' },
                { time: '08:45:22', job: 'Website Frontend', action: 'Backup completed', status: 'success', details: '2.3 GB in 2m 15s' },
                { time: '08:30:00', job: 'RAG Knowledge Base', action: 'Scheduled backup', status: 'info', details: 'Waiting for window...' },
                { time: '08:15:10', job: 'AI Swarm Models', action: 'Weekly backup completed', status: 'success', details: '45.6 GB in 45m' },
              ].map((log, idx) => (
                <div key={idx} className="flex items-center gap-4 p-3 bg-[#0a0812] rounded-lg">
                  <span className="text-gray-500 w-20">{log.time}</span>
                  <span className={`px-2 py-0.5 rounded text-[10px] ${
                    log.status === 'success' ? 'bg-green-500/20 text-green-400' :
                    log.status === 'error' ? 'bg-red-500/20 text-red-400' :
                    'bg-blue-500/20 text-blue-400'
                  }`}>
                    {log.status.toUpperCase()}
                  </span>
                  <span className="font-semibold w-32">{log.job}</span>
                  <span className="text-gray-400">{log.action}</span>
                  <span className="text-gray-500 text-xs ml-auto">{log.details}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Create Job Modal */}
      {isCreating && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-[#1a1525] border border-gray-800 rounded-xl p-6 max-w-lg w-full">
            <h3 className="text-lg font-bold mb-4">Create New Backup Job</h3>
            <div className="space-y-4">
              <input
                type="text"
                placeholder="Job Name"
                className="w-full px-4 py-3 bg-[#0a0812] border border-gray-800 rounded-lg text-white focus:border-[#7c3aed] focus:outline-none"
              />
              <select className="w-full px-4 py-3 bg-[#0a0812] border border-gray-800 rounded-lg text-white focus:border-[#7c3aed] focus:outline-none">
                <option value="">Select Backup Type...</option>
                <option value="bot_memory">Bot Memory State</option>
                <option value="database">Database</option>
                <option value="website">Website Files</option>
                <option value="ai_model">AI Model Weights</option>
                <option value="rag_knowledge">RAG Knowledge Base</option>
                <option value="system_config">System Configuration</option>
                <option value="wallet_keys">Wallet Keys (Encrypted)</option>
              </select>
              <select className="w-full px-4 py-3 bg-[#0a0812] border border-gray-800 rounded-lg text-white focus:border-[#7c3aed] focus:outline-none">
                <option value="">Backup Frequency...</option>
                <option value="realtime">Real-time (Continuous)</option>
                <option value="hourly">Hourly</option>
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
              </select>
            </div>
            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setIsCreating(false)}
                className="flex-1 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm hover:bg-gray-700 transition-all"
              >
                CANCEL
              </button>
              <button
                onClick={() => setIsCreating(false)}
                className="flex-1 py-2 bg-[#7c3aed] text-white rounded-lg text-sm hover:bg-[#6d28d9] transition-all"
              >
                CREATE JOB
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default BackupManagement;
