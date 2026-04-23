import React, { useState } from 'react';
import {
  FileText,
  Book,
  Edit3,
  Save,
  Download,
  Upload,
  Share2,
  Globe,
  Clock,
  Eye,
  Users,
  GitBranch,
  History,
  MessageSquare,
  CheckCircle,
  AlertCircle,
  Plus,
  Trash2,
  MoreHorizontal,
  ChevronDown,
  ChevronUp,
  Search,
  Filter,
  RefreshCw,
  Printer,
  Copy,
  Link as LinkIcon,
  Lock,
  Unlock,
  Star,
  Award,
  Zap,
  Target,
  Rocket,
  Shield,
  Code,
  Layers,
  BarChart3,
  Send,
  Image as ImageIcon,
  Table,
  List,
  Heading,
  Quote,
  Type,
  AlignLeft,
  AlignCenter,
  AlignRight,
  Bold,
  Italic,
  Underline,
  X,
  Check
} from 'lucide-react';

interface Whitepaper {
  id: string;
  title: string;
  subtitle: string;
  version: string;
  status: 'draft' | 'review' | 'published' | 'archived';
  content: string;
  lastModified: string;
  author: string;
  reviewers: string[];
  publishedAt?: string;
  downloads: number;
  views: number;
  tags: string[];
  sections: Section[];
  coverImage?: string;
}

interface Section {
  id: string;
  title: string;
  content: string;
  order: number;
  status: 'writing' | 'review' | 'complete';
}

interface Comment {
  id: string;
  sectionId: string;
  text: string;
  author: string;
  timestamp: string;
  resolved: boolean;
}

const WhitepaperManager: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'papers' | 'editor' | 'templates' | 'published'>('papers');
  const [selectedPaper, setSelectedPaper] = useState<string | null>(null);
  const [showNewPaper, setShowNewPaper] = useState(false);

  // Whitepapers State
  const [whitepapers, setWhitepapers] = useState<Whitepaper[]>([
    {
      id: 'wp1',
      title: '$CRM V2: The Rug Munch Intel Token',
      subtitle: 'Decentralized Security Intelligence for Web3',
      version: '2.1.0',
      status: 'published',
      content: '',
      lastModified: '2026-04-14',
      author: 'RMI Core Team',
      reviewers: ['Lead Dev', 'Tokenomics Expert', 'Legal Advisor'],
      publishedAt: '2026-04-01',
      downloads: 12456,
      views: 89345,
      tags: ['tokenomics', 'governance', 'dao', 'v2'],
      sections: [
        { id: 's1', title: 'Executive Summary', content: '', order: 1, status: 'complete' },
        { id: 's2', title: 'Introduction', content: '', order: 2, status: 'complete' },
        { id: 's3', title: 'Tokenomics', content: '', order: 3, status: 'complete' },
        { id: 's4', title: 'Governance Structure', content: '', order: 4, status: 'complete' },
        { id: 's5', title: 'Technical Architecture', content: '', order: 5, status: 'complete' },
        { id: 's6', title: 'Roadmap', content: '', order: 6, status: 'complete' },
      ]
    },
    {
      id: 'wp2',
      title: 'MunchMaps: Cross-Chain Intelligence Layer',
      subtitle: 'Visualizing the Hidden Connections in Crypto',
      version: '1.0.0',
      status: 'review',
      content: '',
      lastModified: '2026-04-13',
      author: 'R&D Department',
      reviewers: ['CTO', 'Data Scientist'],
      downloads: 0,
      views: 124,
      tags: ['munchmaps', 'technology', 'ai', 'visualization'],
      sections: [
        { id: 's1', title: 'Abstract', content: '', order: 1, status: 'complete' },
        { id: 's2', title: 'Problem Statement', content: '', order: 2, status: 'complete' },
        { id: 's3', title: 'Technical Solution', content: '', order: 3, status: 'review' },
        { id: 's4', title: 'Implementation', content: '', order: 4, status: 'writing' },
      ]
    },
    {
      id: 'wp3',
      title: 'AI Swarm Architecture',
      subtitle: 'Autonomous Agents for Threat Detection',
      version: '0.9.0',
      status: 'draft',
      content: '',
      lastModified: '2026-04-10',
      author: 'AI Research Team',
      reviewers: [],
      downloads: 0,
      views: 0,
      tags: ['ai', 'swarm', 'agents', 'research'],
      sections: [
        { id: 's1', title: 'Overview', content: '', order: 1, status: 'writing' },
        { id: 's2', title: 'Agent Design', content: '', order: 2, status: 'writing' },
      ]
    }
  ]);

  const [comments] = useState<Comment[]>([
    {
      id: 'c1',
      sectionId: 's3',
      text: 'Need more detail on the graph database selection criteria',
      author: 'CTO',
      timestamp: '2026-04-13 14:30',
      resolved: false
    },
    {
      id: 'c2',
      sectionId: 's3',
      text: 'Great explanation of the clustering algorithm',
      author: 'Data Scientist',
      timestamp: '2026-04-12 10:15',
      resolved: true
    }
  ]);

  // UI State
  const [newPaper, setNewPaper] = useState({
    title: '',
    subtitle: '',
    author: ''
  });

  const [activeSection, setActiveSection] = useState<string | null>(null);
  const [sectionContent, setSectionContent] = useState('');

  // Stats
  const stats = {
    totalPapers: whitepapers.length,
    publishedPapers: whitepapers.filter(w => w.status === 'published').length,
    totalDownloads: whitepapers.reduce((acc, w) => acc + w.downloads, 0),
    totalViews: whitepapers.reduce((acc, w) => acc + w.views, 0),
    pendingReviews: whitepapers.filter(w => w.status === 'review').length
  };

  const handleCreatePaper = () => {
    const paper: Whitepaper = {
      id: `wp${Date.now()}`,
      title: newPaper.title,
      subtitle: newPaper.subtitle,
      version: '0.1.0',
      status: 'draft',
      content: '',
      lastModified: new Date().toISOString().split('T')[0],
      author: newPaper.author,
      reviewers: [],
      downloads: 0,
      views: 0,
      tags: [],
      sections: []
    };
    setWhitepapers([paper, ...whitepapers]);
    setShowNewPaper(false);
    setNewPaper({ title: '', subtitle: '', author: '' });
    setSelectedPaper(paper.id);
    setActiveTab('editor');
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'published': return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'review': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'draft': return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      case 'archived': return 'bg-gray-700 text-gray-400';
      default: return 'bg-gray-700 text-gray-400';
    }
  };

  const currentPaper = whitepapers.find(w => w.id === selectedPaper);

  return (
    <div className="min-h-screen bg-[#0a0812] text-gray-100 font-mono selection:bg-[#7c3aed]/30">
      {/* Header */}
      <div className="bg-gradient-to-r from-[#0f0c1d] via-[#1a1525] to-[#0f0c1d] border-b border-[#7c3aed]/30">
        <div className="max-w-[1600px] mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-[#7c3aed]/20 rounded-full flex items-center justify-center">
                <Book className="w-5 h-5 text-[#7c3aed]" />
              </div>
              <div>
                <h1 className="text-xl font-bold tracking-wider">
                  WHITEPAPER <span className="text-[#7c3aed]">COMMAND</span>
                </h1>
                <p className="text-xs text-gray-500 tracking-[0.2em]">DOCUMENTATION & PUBLICATION SYSTEM</p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 px-3 py-1.5 bg-green-500/10 border border-green-500/30 rounded">
                <Book className="w-4 h-4 text-green-400" />
                <span className="text-sm text-green-400">{stats.publishedPapers} Published</span>
              </div>
              <button
                onClick={() => setShowNewPaper(true)}
                className="flex items-center gap-2 px-4 py-2 bg-[#7c3aed] text-white rounded transition-all"
              >
                <Plus className="w-4 h-4" />
                NEW WHITEPAPER
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-[1600px] mx-auto p-6 space-y-6">
        {/* Stats Row */}
        <div className="grid grid-cols-5 gap-4">
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
            <FileText className="w-5 h-5 text-blue-400 mb-2" />
            <div className="text-xl font-bold">{stats.totalPapers}</div>
            <div className="text-xs text-gray-500">Total Papers</div>
          </div>
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
            <CheckCircle className="w-5 h-5 text-green-400 mb-2" />
            <div className="text-xl font-bold">{stats.publishedPapers}</div>
            <div className="text-xs text-gray-500">Published</div>
          </div>
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
            <Download className="w-5 h-5 text-purple-400 mb-2" />
            <div className="text-xl font-bold">{stats.totalDownloads.toLocaleString()}</div>
            <div className="text-xs text-gray-500">Downloads</div>
          </div>
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
            <Eye className="w-5 h-5 text-yellow-400 mb-2" />
            <div className="text-xl font-bold">{(stats.totalViews / 1000).toFixed(1)}k</div>
            <div className="text-xs text-gray-500">Views</div>
          </div>
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
            <AlertCircle className="w-5 h-5 text-orange-400 mb-2" />
            <div className="text-xl font-bold">{stats.pendingReviews}</div>
            <div className="text-xs text-gray-500">Pending Review</div>
          </div>
        </div>

        {/* Navigation */}
        <div className="flex items-center gap-1 border-b border-gray-800">
          {[
            { id: 'papers', label: 'ALL PAPERS', icon: <FileText className="w-4 h-4" /> },
            { id: 'editor', label: 'EDITOR', icon: <Edit3 className="w-4 h-4" /> },
            { id: 'templates', label: 'TEMPLATES', icon: <Layers className="w-4 h-4" /> },
            { id: 'published', label: 'PUBLISHED', icon: <Globe className="w-4 h-4" /> },
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

        {/* All Papers Tab */}
        {activeTab === 'papers' && (
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <div className="relative flex-1 max-w-md">
                <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
                <input
                  type="text"
                  placeholder="Search whitepapers..."
                  className="w-full pl-10 pr-4 py-2 bg-[#0a0812] border border-gray-800 rounded text-sm"
                />
              </div>
              <select className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm">
                <option>All Status</option>
                <option>Draft</option>
                <option>Review</option>
                <option>Published</option>
              </select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              {whitepapers.map((paper) => (
                <div
                  key={paper.id}
                  onClick={() => { setSelectedPaper(paper.id); setActiveTab('editor'); }}
                  className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-5 cursor-pointer hover:border-[#7c3aed]/50 transition-all"
                >
                  <div className="flex items-start justify-between mb-3">
                    <span className={`px-2 py-1 rounded text-[10px] border ${getStatusColor(paper.status)}`}>
                      {paper.status.toUpperCase()}
                    </span>
                    <span className="text-xs text-gray-500">v{paper.version}</span>
                  </div>

                  <h3 className="font-bold mb-1">{paper.title}</h3>
                  <p className="text-sm text-gray-500 mb-4">{paper.subtitle}</p>

                  <div className="flex items-center gap-4 text-xs text-gray-400 mb-4">
                    <span className="flex items-center gap-1">
                      <Users className="w-3 h-3" />
                      {paper.author}
                    </span>
                    <span className="flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {paper.lastModified}
                    </span>
                  </div>

                  {paper.status === 'published' && (
                    <div className="flex items-center gap-4 text-xs">
                      <span className="flex items-center gap-1 text-green-400">
                        <Download className="w-3 h-3" />
                        {paper.downloads.toLocaleString()}
                      </span>
                      <span className="flex items-center gap-1 text-blue-400">
                        <Eye className="w-3 h-3" />
                        {paper.views.toLocaleString()}
                      </span>
                    </div>
                  )}

                  <div className="flex flex-wrap gap-2 mt-4">
                    {paper.tags.map((tag, idx) => (
                      <span key={idx} className="px-2 py-1 bg-gray-800 rounded text-[10px]">
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Editor Tab */}
        {activeTab === 'editor' && currentPaper && (
          <div className="grid grid-cols-4 gap-6">
            {/* Sidebar */}
            <div className="col-span-1 space-y-4">
              <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
                <h3 className="font-bold mb-3">{currentPaper.title}</h3>
                <div className="text-xs text-gray-500 mb-4">
                  v{currentPaper.version} • {currentPaper.status}
                </div>
                <div className="space-y-2">
                  <button className="w-full py-2 bg-[#7c3aed] text-white rounded text-sm hover:bg-[#6d28d9] transition-all">
                    <Save className="w-4 h-4 inline mr-2" />
                    SAVE
                  </button>
                  <button className="w-full py-2 bg-gray-800 text-gray-400 rounded text-sm hover:bg-gray-700 transition-all">
                    <Download className="w-4 h-4 inline mr-2" />
                    EXPORT PDF
                  </button>
                  {currentPaper.status !== 'published' && (
                    <button className="w-full py-2 bg-green-500/20 text-green-400 border border-green-500/30 rounded text-sm hover:bg-green-500/30 transition-all">
                      <Send className="w-4 h-4 inline mr-2" />
                      REQUEST REVIEW
                    </button>
                  )}
                </div>
              </div>

              <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
                <h4 className="font-semibold mb-3">Sections</h4>
                <div className="space-y-2">
                  {currentPaper.sections.sort((a, b) => a.order - b.order).map((section) => (
                    <button
                      key={section.id}
                      onClick={() => setActiveSection(section.id)}
                      className={`w-full p-2 rounded text-left text-sm transition-all ${
                        activeSection === section.id
                          ? 'bg-[#7c3aed]/20 border border-[#7c3aed]/30'
                          : 'hover:bg-gray-800'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span>{section.order}. {section.title}</span>
                        <span className={`w-2 h-2 rounded-full ${
                          section.status === 'complete' ? 'bg-green-400' :
                          section.status === 'review' ? 'bg-yellow-400' :
                          'bg-blue-400'
                        }`} />
                      </div>
                    </button>
                  ))}
                  <button className="w-full py-2 border border-dashed border-gray-700 rounded text-gray-500 hover:border-[#7c3aed] hover:text-[#7c3aed] transition-all">
                    + ADD SECTION
                  </button>
                </div>
              </div>

              <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
                <h4 className="font-semibold mb-3">Reviewers</h4>
                <div className="space-y-2">
                  {currentPaper.reviewers.map((reviewer, idx) => (
                    <div key={idx} className="flex items-center gap-2 text-sm">
                      <CheckCircle className="w-4 h-4 text-green-400" />
                      {reviewer}
                    </div>
                  ))}
                  <button className="w-full py-2 border border-dashed border-gray-700 rounded text-gray-500 hover:border-[#7c3aed] hover:text-[#7c3aed] transition-all">
                    + ADD REVIEWER
                  </button>
                </div>
              </div>

              <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-4">
                <h4 className="font-semibold mb-3">Comments</h4>
                <div className="space-y-3">
                  {comments.filter(c => c.sectionId === activeSection).map((comment) => (
                    <div key={comment.id} className={`p-2 rounded text-xs ${
                      comment.resolved ? 'bg-green-500/10 text-green-400' : 'bg-yellow-500/10 text-yellow-400'
                    }`}>
                      <div className="flex items-center gap-1 mb-1">
                        <strong>{comment.author}</strong>
                        <span className="text-gray-500">• {comment.timestamp}</span>
                      </div>
                      {comment.text}
                    </div>
                  ))}
                  {comments.filter(c => c.sectionId === activeSection).length === 0 && (
                    <p className="text-xs text-gray-500">No comments on this section</p>
                  )}
                </div>
              </div>
            </div>

            {/* Editor Area */}
            <div className="col-span-3 space-y-4">
              {/* Toolbar */}
              <div className="flex items-center gap-1 bg-gradient-to-r from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-2">
                <button className="p-2 hover:bg-gray-800 rounded" title="Bold">
                  <Bold className="w-4 h-4" />
                </button>
                <button className="p-2 hover:bg-gray-800 rounded" title="Italic">
                  <Italic className="w-4 h-4" />
                </button>
                <button className="p-2 hover:bg-gray-800 rounded" title="Underline">
                  <Underline className="w-4 h-4" />
                </button>
                <span className="w-px h-6 bg-gray-700 mx-2" />
                <button className="p-2 hover:bg-gray-800 rounded" title="Heading">
                  <Heading className="w-4 h-4" />
                </button>
                <button className="p-2 hover:bg-gray-800 rounded" title="List">
                  <List className="w-4 h-4" />
                </button>
                <button className="p-2 hover:bg-gray-800 rounded" title="Table">
                  <Table className="w-4 h-4" />
                </button>
                <button className="p-2 hover:bg-gray-800 rounded" title="Quote">
                  <Quote className="w-4 h-4" />
                </button>
                <span className="w-px h-6 bg-gray-700 mx-2" />
                <button className="p-2 hover:bg-gray-800 rounded" title="Image">
                  <ImageIcon className="w-4 h-4" />
                </button>
                <button className="p-2 hover:bg-gray-800 rounded" title="Code">
                  <Code className="w-4 h-4" />
                </button>
                <span className="w-px h-6 bg-gray-700 mx-2" />
                <button className="p-2 hover:bg-gray-800 rounded" title="Align Left">
                  <AlignLeft className="w-4 h-4" />
                </button>
                <button className="p-2 hover:bg-gray-800 rounded" title="Align Center">
                  <AlignCenter className="w-4 h-4" />
                </button>
                <button className="p-2 hover:bg-gray-800 rounded" title="Align Right">
                  <AlignRight className="w-4 h-4" />
                </button>
              </div>

              {/* Content Area */}
              <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6 min-h-[600px]">
                {activeSection ? (
                  <div>
                    <input
                      type="text"
                      value={currentPaper.sections.find(s => s.id === activeSection)?.title || ''}
                      className="w-full text-2xl font-bold bg-transparent border-none focus:outline-none mb-4"
                      placeholder="Section Title"
                    />
                    <textarea
                      value={sectionContent}
                      onChange={(e) => setSectionContent(e.target.value)}
                      placeholder="Start writing..."
                      className="w-full h-[500px] bg-transparent border-none resize-none focus:outline-none leading-relaxed"
                    />
                  </div>
                ) : (
                  <div className="h-full flex items-center justify-center text-gray-500">
                    <div className="text-center">
                      <FileText className="w-12 h-12 mx-auto mb-4 opacity-50" />
                      <p>Select a section to start editing</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Templates Tab */}
        {activeTab === 'templates' && (
          <div className="grid grid-cols-3 gap-4">
            {[
              {
                title: 'Token Whitepaper',
                desc: 'Standard ERC-20/BEP-20 token documentation with tokenomics, governance, and roadmap sections',
                sections: 8
              },
              {
                title: 'Technical Architecture',
                desc: 'Deep technical documentation for protocols, algorithms, and system design',
                sections: 6
              },
              {
                title: 'Research Paper',
                desc: 'Academic-style research documentation with abstract, methodology, and findings',
                sections: 10
              },
              {
                title: 'Litepaper',
                desc: 'Condensed version for broader audience with key highlights and benefits',
                sections: 5
              },
              {
                title: 'Product Documentation',
                desc: 'Feature-focused documentation for tools and services',
                sections: 7
              },
              {
                title: 'Integration Guide',
                desc: 'API and integration documentation for developers',
                sections: 12
              }
            ].map((template, idx) => (
              <div key={idx} className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-5">
                <div className="flex items-start justify-between mb-3">
                  <Layers className="w-8 h-8 text-[#7c3aed]" />
                  <span className="text-xs px-2 py-1 bg-gray-800 rounded">{template.sections} sections</span>
                </div>
                <h3 className="font-bold mb-2">{template.title}</h3>
                <p className="text-sm text-gray-500 mb-4">{template.desc}</p>
                <div className="flex gap-2">
                  <button className="flex-1 py-2 bg-[#7c3aed]/10 border border-[#7c3aed]/30 rounded text-sm text-[#7c3aed] hover:bg-[#7c3aed]/20 transition-all">
                    USE TEMPLATE
                  </button>
                  <button className="px-3 py-2 bg-gray-800 rounded text-sm text-gray-400 hover:bg-gray-700 transition-all">
                    PREVIEW
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Published Tab */}
        {activeTab === 'published' && (
          <div className="space-y-4">
            {whitepapers.filter(w => w.status === 'published').map((paper) => (
              <div key={paper.id} className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="font-bold text-lg">{paper.title}</h3>
                      <span className="px-2 py-0.5 bg-green-500/20 text-green-400 rounded text-xs">PUBLISHED</span>
                    </div>
                    <p className="text-sm text-gray-500 mb-3">{paper.subtitle}</p>
                    <div className="flex items-center gap-4 text-xs text-gray-400">
                      <span>Published: {paper.publishedAt}</span>
                      <span>Version: {paper.version}</span>
                      <span>Author: {paper.author}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-6">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-400">{paper.downloads.toLocaleString()}</div>
                      <div className="text-xs text-gray-500">Downloads</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-blue-400">{paper.views.toLocaleString()}</div>
                      <div className="text-xs text-gray-500">Views</div>
                    </div>
                    <div className="flex flex-col gap-2">
                      <button className="px-4 py-2 bg-[#7c3aed] text-white rounded text-sm hover:bg-[#6d28d9] transition-all">
                        <LinkIcon className="w-4 h-4 inline mr-2" />
                        COPY LINK
                      </button>
                      <button className="px-4 py-2 bg-gray-800 text-gray-400 rounded text-sm hover:bg-gray-700 transition-all">
                        <Share2 className="w-4 h-4 inline mr-2" />
                        SHARE
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* New Paper Modal */}
      {showNewPaper && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-[#1a1525] border border-gray-800 rounded-lg p-6 w-[500px] max-w-[90vw]">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold">Create New Whitepaper</h2>
              <button onClick={() => setShowNewPaper(false)} className="p-1 hover:bg-gray-800 rounded">
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-500 mb-1">Title</label>
                <input
                  type="text"
                  value={newPaper.title}
                  onChange={(e) => setNewPaper({ ...newPaper, title: e.target.value })}
                  placeholder="Enter whitepaper title..."
                  className="w-full px-3 py-2 bg-[#0a0812] border border-gray-800 rounded"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-500 mb-1">Subtitle</label>
                <input
                  type="text"
                  value={newPaper.subtitle}
                  onChange={(e) => setNewPaper({ ...newPaper, subtitle: e.target.value })}
                  placeholder="Brief description or tagline..."
                  className="w-full px-3 py-2 bg-[#0a0812] border border-gray-800 rounded"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-500 mb-1">Author/Team</label>
                <input
                  type="text"
                  value={newPaper.author}
                  onChange={(e) => setNewPaper({ ...newPaper, author: e.target.value })}
                  placeholder="Primary author or team name..."
                  className="w-full px-3 py-2 bg-[#0a0812] border border-gray-800 rounded"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-500 mb-1">Template (Optional)</label>
                <select className="w-full px-3 py-2 bg-[#0a0812] border border-gray-800 rounded">
                  <option>Blank Document</option>
                  <option>Token Whitepaper</option>
                  <option>Technical Architecture</option>
                  <option>Research Paper</option>
                  <option>Litepaper</option>
                </select>
              </div>
              <div className="flex gap-3 pt-4">
                <button
                  onClick={handleCreatePaper}
                  className="flex-1 py-2 bg-[#7c3aed] text-white rounded hover:bg-[#6d28d9] transition-all"
                >
                  CREATE WHITEPAPER
                </button>
                <button
                  onClick={() => setShowNewPaper(false)}
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

export default WhitepaperManager;
