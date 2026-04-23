import React, { useState } from 'react';
import {
  Scale,
  Shield,
  FileCheck,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Clock,
  Calendar,
  Globe,
  Lock,
  BookOpen,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  Plus,
  MessageSquare,
  Save,
  AlertOctagon,
  Gavel,
  Building2,
  FileText,
  Users,
  RefreshCw
} from 'lucide-react';

interface ComplianceItem {
  id: string;
  category: 'regulatory' | 'tax' | 'privacy' | 'security' | 'operational';
  title: string;
  description: string;
  status: 'compliant' | 'attention' | 'non_compliant' | 'pending';
  dueDate?: string;
  lastReviewed: string;
  nextReview: string;
  assignedTo: string;
  evidence: string[];
  risk: 'low' | 'medium' | 'high' | 'critical';
  notes: string;
}

interface Filing {
  id: string;
  jurisdiction: string;
  type: string;
  dueDate: string;
  status: 'upcoming' | 'filed' | 'overdue';
  amount?: string;
  submittedDate?: string;
  confirmationNumber?: string;
}

const ComplianceDept: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'filings' | 'documents' | 'audit' | 'corporate'>('dashboard');
  const [selectedItem, setSelectedItem] = useState<string | null>(null);

  const complianceItems: ComplianceItem[] = [
    {
      id: 'c1',
      category: 'regulatory',
      title: 'Wyoming DAO LLC Annual Report',
      description: 'Annual filing with Wyoming Secretary of State to maintain good standing',
      status: 'attention',
      dueDate: '2026-06-01',
      lastReviewed: '2025-06-15',
      nextReview: '2026-05-15',
      assignedTo: 'Legal Team',
      evidence: ['2025 Filing Receipt', 'Registered Agent Confirmation'],
      risk: 'medium',
      notes: 'Due in 45 days. $60 filing fee.'
    },
    {
      id: 'c2',
      category: 'tax',
      title: 'Q2 Estimated Tax Payment',
      description: 'Federal and state quarterly estimated tax payment',
      status: 'pending',
      dueDate: '2026-06-15',
      lastReviewed: '2026-04-01',
      nextReview: '2026-06-01',
      assignedTo: 'CFO',
      evidence: ['Q1 Payment Receipt', 'Revenue Projections'],
      risk: 'high',
      notes: 'Projected $31K based on $125K Q2 revenue'
    },
    {
      id: 'c3',
      category: 'privacy',
      title: 'GDPR Compliance Audit',
      description: 'European user data handling compliance verification',
      status: 'compliant',
      lastReviewed: '2026-03-01',
      nextReview: '2026-09-01',
      assignedTo: 'DPO',
      evidence: ['Data Processing Agreement', 'User Consent Records', 'DPA with Providers'],
      risk: 'medium',
      notes: 'No EU marketing currently; preventive compliance'
    },
    {
      id: 'c4',
      category: 'security',
      title: 'Smart Contract Audit Renewal',
      description: 'Annual security audit of $CRM V2 token contracts',
      status: 'attention',
      dueDate: '2026-05-01',
      lastReviewed: '2025-05-01',
      nextReview: '2026-04-15',
      assignedTo: 'Security Lead',
      evidence: ['CertiK Audit 2025', 'Bug Bounty Results'],
      risk: 'critical',
      notes: 'Contact CertiK or OpenZeppelin for renewal'
    },
    {
      id: 'c5',
      category: 'operational',
      title: 'OFAC Sanctions Screening',
      description: 'User wallet screening against sanctions lists',
      status: 'compliant',
      lastReviewed: '2026-04-10',
      nextReview: '2026-05-10',
      assignedTo: 'Compliance Officer',
      evidence: ['Screening Logs', 'Blocked Addresses List'],
      risk: 'critical',
      notes: 'Automated screening active; 0 false positives this month'
    },
    {
      id: 'c6',
      category: 'regulatory',
      title: 'SEC Token Classification Review',
      description: 'Annual review of $CRM token for securities compliance',
      status: 'attention',
      dueDate: '2026-07-01',
      lastReviewed: '2025-07-01',
      nextReview: '2026-06-01',
      assignedTo: 'Securities Counsel',
      evidence: ['Howey Test Analysis 2025', 'Token Use Documentation'],
      risk: 'critical',
      notes: 'Increased SEC scrutiny on utility tokens - priority review needed'
    }
  ];

  const filings: Filing[] = [
    { id: 'f1', jurisdiction: 'Wyoming', type: 'LLC Annual Report', dueDate: '2026-06-01', status: 'upcoming', amount: '$60' },
    { id: 'f2', jurisdiction: 'IRS', type: 'Q2 Estimated Tax (Form 1040-ES)', dueDate: '2026-06-15', status: 'upcoming', amount: '~$31,000' },
    { id: 'f3', jurisdiction: 'Delaware', type: 'Foreign Entity Registration', dueDate: '2026-03-01', status: 'filed', submittedDate: '2026-02-28', confirmationNumber: 'DE-2026-8842' },
    { id: 'f4', jurisdiction: 'FinCEN', type: 'BOI Report (Beneficial Ownership)', dueDate: '2025-12-31', status: 'overdue' },
    { id: 'f5', jurisdiction: 'Wyoming', type: 'Sales Tax License Renewal', dueDate: '2026-01-15', status: 'filed', submittedDate: '2026-01-10', confirmationNumber: 'WY-ST-456' },
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'compliant': return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'attention': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'non_compliant': return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'pending': return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      case 'upcoming': return 'bg-blue-500/20 text-blue-400';
      case 'filed': return 'bg-green-500/20 text-green-400';
      case 'overdue': return 'bg-red-500/20 text-red-400';
      default: return 'bg-gray-500/20 text-gray-400';
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'critical': return 'text-red-500';
      case 'high': return 'text-orange-400';
      case 'medium': return 'text-yellow-400';
      case 'low': return 'text-green-400';
      default: return 'text-gray-400';
    }
  };

  const selectedItemData = complianceItems.find(i => i.id === selectedItem);

  return (
    <div className="min-h-screen bg-[#0a0812] text-gray-100 font-mono selection:bg-[#7c3aed]/30">
      {/* Header */}
      <div className="bg-gradient-to-r from-[#0f0c1d] via-[#1a1525] to-[#0f0c1d] border-b border-[#7c3aed]/30">
        <div className="max-w-[1600px] mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Scale className="w-8 h-8 text-[#7c3aed]" />
              <div>
                <h1 className="text-xl font-bold tracking-wider">
                  COMPLIANCE <span className="text-[#7c3aed]">CENTER</span>
                </h1>
                <p className="text-xs text-gray-500 tracking-[0.2em]">LEGAL & REGULATORY MANAGEMENT</p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 px-3 py-1.5 bg-green-500/10 border border-green-500/30 rounded">
                <Shield className="w-4 h-4 text-green-400" />
                <span className="text-xs text-green-400">Wyoming LLC Active</span>
              </div>
              <div className="text-right">
                <div className="text-xs text-gray-500">Last Audit</div>
                <div className="text-sm">2026-04-01</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-[1600px] mx-auto p-6 space-y-6">
        {/* Compliance Score */}
        <div className="grid grid-cols-4 gap-4">
          <div className="bg-gradient-to-br from-green-500/10 to-[#0f0c1d] border border-green-500/30 rounded-lg p-5">
            <div className="flex items-center gap-2 mb-2">
              <CheckCircle className="w-6 h-6 text-green-400" />
              <span className="text-3xl font-bold text-green-400">3</span>
            </div>
            <div className="text-xs text-gray-500 uppercase">Compliant</div>
          </div>
          <div className="bg-gradient-to-br from-yellow-500/10 to-[#0f0c1d] border border-yellow-500/30 rounded-lg p-5">
            <div className="flex items-center gap-2 mb-2">
              <AlertTriangle className="w-6 h-6 text-yellow-400" />
              <span className="text-3xl font-bold text-yellow-400">3</span>
            </div>
            <div className="text-xs text-gray-500 uppercase">Needs Attention</div>
          </div>
          <div className="bg-gradient-to-br from-red-500/10 to-[#0f0c1d] border border-red-500/30 rounded-lg p-5">
            <div className="flex items-center gap-2 mb-2">
              <XCircle className="w-6 h-6 text-red-400" />
              <span className="text-3xl font-bold text-red-400">1</span>
            </div>
            <div className="text-xs text-gray-500 uppercase">Overdue</div>
          </div>
          <div className="bg-gradient-to-br from-[#7c3aed]/10 to-[#0f0c1d] border border-[#7c3aed]/30 rounded-lg p-5">
            <div className="flex items-center gap-2 mb-2">
              <Shield className="w-6 h-6 text-[#7c3aed]" />
              <span className="text-3xl font-bold text-[#7c3aed]">86%</span>
            </div>
            <div className="text-xs text-gray-500 uppercase">Compliance Score</div>
          </div>
        </div>

        {/* Navigation */}
        <div className="flex items-center gap-1 border-b border-gray-800">
          {[
            { id: 'dashboard', label: 'DASHBOARD', icon: <Scale className="w-4 h-4" /> },
            { id: 'filings', label: 'FILINGS & DEADLINES', icon: <Calendar className="w-4 h-4" /> },
            { id: 'corporate', label: 'CORPORATE & FUNDS', icon: <Building2 className="w-4 h-4" /> },
            { id: 'documents', label: 'LEGAL DOCUMENTS', icon: <FileText className="w-4 h-4" /> },
            { id: 'audit', label: 'AUDIT LOG', icon: <BookOpen className="w-4 h-4" /> },
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
        {activeTab === 'dashboard' && (
          <div className="grid grid-cols-12 gap-6">
            <div className="col-span-8">
              <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-bold">Compliance Requirements</h2>
                  <button className="flex items-center gap-2 px-3 py-1.5 bg-[#7c3aed]/10 border border-[#7c3aed]/30 rounded text-xs text-[#7c3aed] hover:bg-[#7c3aed]/20 transition-all">
                    <Plus className="w-3 h-3" />
                    ADD ITEM
                  </button>
                </div>

                <div className="space-y-3">
                  {complianceItems.map((item) => (
                    <div
                      key={item.id}
                      onClick={() => setSelectedItem(item.id)}
                      className={`p-4 rounded-lg border cursor-pointer transition-all ${
                        selectedItem === item.id
                          ? 'bg-[#7c3aed]/10 border-[#7c3aed]'
                          : 'bg-[#0a0812] border-gray-800 hover:border-gray-700'
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex items-start gap-3">
                          <span className={`px-2 py-1 rounded text-[10px] font-bold ${getStatusColor(item.status)}`}>
                            {item.status.toUpperCase().replace('_', ' ')}
                          </span>
                          <div>
                            <div className="font-semibold">{item.title}</div>
                            <div className="text-xs text-gray-400 mt-1">{item.description}</div>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className={`text-xs font-bold ${getRiskColor(item.risk)}`}>{item.risk.toUpperCase()} RISK</div>
                          {item.dueDate && <div className="text-xs text-gray-500 mt-1">Due: {item.dueDate}</div>}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="col-span-4">
              {selectedItemData ? (
                <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
                  <h3 className="font-semibold mb-4">{selectedItemData.title}</h3>
                  <div className="space-y-4 text-sm">
                    <div>
                      <span className="text-gray-500">Category:</span>
                      <span className="ml-2 uppercase">{selectedItemData.category}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Assigned To:</span>
                      <span className="ml-2">{selectedItemData.assignedTo}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Last Reviewed:</span>
                      <span className="ml-2">{selectedItemData.lastReviewed}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Next Review:</span>
                      <span className="ml-2">{selectedItemData.nextReview}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Risk Level:</span>
                      <span className={`ml-2 font-bold ${getRiskColor(selectedItemData.risk)}`}>
                        {selectedItemData.risk.toUpperCase()}
                      </span>
                    </div>

                    {selectedItemData.evidence.length > 0 && (
                      <div>
                        <span className="text-gray-500">Evidence:</span>
                        <ul className="mt-2 space-y-1">
                          {selectedItemData.evidence.map((ev, idx) => (
                            <li key={idx} className="flex items-center gap-2 text-xs text-[#7c3aed]">
                              <FileCheck className="w-3 h-3" />
                              {ev}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    <div className="pt-4 border-t border-gray-800">
                      <span className="text-gray-500">Notes:</span>
                      <p className="mt-1 text-gray-300">{selectedItemData.notes}</p>
                    </div>

                    <div className="flex gap-2 pt-4">
                      <button className="flex-1 py-2 bg-[#7c3aed]/10 border border-[#7c3aed]/30 rounded text-sm text-[#7c3aed] hover:bg-[#7c3aed]/20 transition-all">
                        MARK REVIEWED
                      </button>
                      <button className="flex-1 py-2 bg-gray-800 border border-gray-700 rounded text-sm text-gray-400 hover:bg-gray-700 transition-all">
                        EDIT
                      </button>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6 text-center text-gray-500">
                  <Scale className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p>Select a compliance item to view details</p>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'filings' && (
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-bold">Upcoming Filings & Deadlines</h2>
              <button className="flex items-center gap-2 px-4 py-2 bg-[#7c3aed] text-white rounded text-sm hover:bg-[#6d28d9] transition-all">
                <Calendar className="w-4 h-4" />
                ADD REMINDER
              </button>
            </div>

            <div className="space-y-3">
              {filings.map((filing) => (
                <div key={filing.id} className="flex items-center justify-between p-4 bg-[#0a0812] rounded-lg border border-gray-800">
                  <div className="flex items-center gap-4">
                    <div className={`p-2 rounded-lg ${
                      filing.status === 'overdue' ? 'bg-red-500/10 text-red-400' :
                      filing.status === 'upcoming' ? 'bg-blue-500/10 text-blue-400' :
                      'bg-green-500/10 text-green-400'
                    }`}>
                      <Building2 className="w-5 h-5" />
                    </div>
                    <div>
                      <div className="font-semibold">{filing.type}</div>
                      <div className="text-xs text-gray-500">{filing.jurisdiction} • Due: {filing.dueDate}</div>
                      {filing.confirmationNumber && (
                        <div className="text-xs text-green-400 mt-1">Confirmation: {filing.confirmationNumber}</div>
                      )}
                    </div>
                  </div>
                  <div className="text-right">
                    <span className={`px-3 py-1 rounded text-xs font-bold ${getStatusColor(filing.status)}`}>
                      {filing.status.toUpperCase()}
                    </span>
                    {filing.amount && <div className="text-sm mt-1">{filing.amount}</div>}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'documents' && (
          <div className="grid grid-cols-3 gap-4">
            {[
              { name: 'Wyoming DAO LLC Articles', type: 'Formation', date: '2021-03-15', status: 'Active' },
              { name: 'Operating Agreement v3', type: 'Governance', date: '2025-01-20', status: 'Current' },
              { name: 'Token Terms & Conditions', type: 'Legal', date: '2025-06-01', status: 'Under Review' },
              { name: 'Privacy Policy', type: 'Compliance', date: '2025-12-01', status: 'Current' },
              { name: 'Service Agreement', type: 'Legal', date: '2025-11-15', status: 'Current' },
              { name: 'Insurance Certificate', type: 'Risk', date: '2026-01-01', status: 'Expires Soon' },
            ].map((doc, idx) => (
              <div key={idx} className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-5">
                <div className="flex items-center gap-2 mb-3">
                  <FileText className="w-5 h-5 text-[#7c3aed]" />
                  <span className="text-xs text-gray-500">{doc.type}</span>
                </div>
                <div className="font-semibold mb-2">{doc.name}</div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-gray-500">{doc.date}</span>
                  <span className={`${doc.status === 'Expires Soon' ? 'text-yellow-400' : doc.status === 'Under Review' ? 'text-blue-400' : 'text-green-400'}`}>
                    {doc.status}
                  </span>
                </div>
                <button className="w-full mt-3 py-2 bg-gray-800 border border-gray-700 rounded text-xs text-gray-400 hover:bg-gray-700 transition-all">
                  VIEW DOCUMENT
                </button>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'audit' && (
          <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
            <h2 className="text-lg font-bold mb-4">Compliance Audit Log</h2>
            <div className="space-y-2 font-mono text-sm">
              {[
                { date: '2026-04-14', action: 'Q2 tax estimation reviewed', user: 'CFO', type: 'review' },
                { date: '2026-04-10', action: 'OFAC screening list updated', user: 'Compliance Officer', type: 'update' },
                { date: '2026-04-05', action: 'Wyoming annual report reminder set', user: 'Legal Team', type: 'reminder' },
                { date: '2026-03-28', action: 'Smart contract audit scope defined', user: 'Security Lead', type: 'planning' },
                { date: '2026-03-15', action: 'SEC guidance review completed', user: 'Securities Counsel', type: 'review' },
              ].map((log, idx) => (
                <div key={idx} className="flex items-start gap-4 p-3 bg-[#0a0812] rounded-lg">
                  <span className="text-gray-500 w-24">{log.date}</span>
                  <span className={`px-2 py-0.5 rounded text-[10px] ${
                    log.type === 'review' ? 'bg-blue-500/20 text-blue-400' :
                    log.type === 'update' ? 'bg-green-500/20 text-green-400' :
                    log.type === 'reminder' ? 'bg-yellow-500/20 text-yellow-400' :
                    'bg-gray-700 text-gray-400'
                  }`}>
                    {log.type.toUpperCase()}
                  </span>
                  <span className="flex-1">{log.action}</span>
                  <span className="text-gray-500">{log.user}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'corporate' && (
          <div className="space-y-6">
            {/* Fund Separation Alert */}
            <div className="bg-gradient-to-r from-green-600/20 to-green-800/20 border border-green-500/30 rounded-lg p-4">
              <div className="flex items-center gap-3">
                <Shield className="w-6 h-6 text-green-400" />
                <div>
                  <p className="text-green-400 font-semibold">Fund Separation Status: COMPLIANT</p>
                  <p className="text-sm text-gray-400">Personal and business funds are properly segregated. No commingling detected.</p>
                </div>
              </div>
            </div>

            <div className="grid lg:grid-cols-2 gap-6">
              {/* LLC Business Structure */}
              <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
                <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
                  <Building2 className="w-5 h-5 text-[#7c3aed]" />
                  Wyoming LLC Structure
                </h2>
                <div className="space-y-4">
                  <div className="p-3 bg-[#0a0812] rounded-lg border border-gray-800">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-gray-400">Entity Name</span>
                      <span className="font-medium">Rug Munch Intel DAO LLC</span>
                    </div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-gray-400">Formation Date</span>
                      <span className="font-medium">March 15, 2021</span>
                    </div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-gray-400">EIN</span>
                      <span className="font-medium">XX-XXXXXXX</span>
                    </div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-gray-400">Registered Agent</span>
                      <span className="font-medium">Northwest Registered Agent</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-400">Status</span>
                      <span className="px-2 py-1 bg-green-500/20 text-green-400 rounded text-xs">ACTIVE</span>
                    </div>
                  </div>

                  <div className="p-3 bg-[#0a0812] rounded-lg border border-gray-800">
                    <p className="text-sm text-gray-400 mb-3">BUSINESS ACTIVITIES ( per Operating Agreement)</p>
                    <ul className="space-y-2 text-sm">
                      <li className="flex items-center gap-2">
                        <CheckCircle className="w-4 h-4 text-green-400" />
                        <span>Blockchain analytics & security research</span>
                      </li>
                      <li className="flex items-center gap-2">
                        <CheckCircle className="w-4 h-4 text-green-400" />
                        <span>Software development & SaaS products</span>
                      </li>
                      <li className="flex items-center gap-2">
                        <CheckCircle className="w-4 h-4 text-green-400" />
                        <span>Digital asset consulting services</span>
                      </li>
                      <li className="flex items-center gap-2">
                        <CheckCircle className="w-4 h-4 text-green-400" />
                        <span>Token governance & DAO operations</span>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>

              {/* Bank Accounts & Fund Separation */}
              <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
                <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
                  <Lock className="w-5 h-5 text-[#7c3aed]" />
                  Fund Separation & Accounts
                </h2>
                <div className="space-y-4">
                  <div className="p-3 bg-green-500/5 rounded-lg border border-green-500/20">
                    <div className="flex items-center gap-2 mb-2">
                      <CheckCircle className="w-5 h-5 text-green-400" />
                      <span className="font-medium text-green-400">Operational Account</span>
                    </div>
                    <p className="text-sm text-gray-400 mb-2">Silicon Valley Bank ****4521</p>
                    <p className="text-xs text-gray-500">Business expenses, payroll, infrastructure</p>
                  </div>

                  <div className="p-3 bg-green-500/5 rounded-lg border border-green-500/20">
                    <div className="flex items-center gap-2 mb-2">
                      <CheckCircle className="w-5 h-5 text-green-400" />
                      <span className="font-medium text-green-400">Treasury Multi-sig</span>
                    </div>
                    <p className="text-sm text-gray-400 mb-2">Gnosis Safe: 0x742d...6C7E</p>
                    <p className="text-xs text-gray-500">3-of-5 signatures required for all treasury moves</p>
                  </div>

                  <div className="p-3 bg-green-500/5 rounded-lg border border-green-500/20">
                    <div className="flex items-center gap-2 mb-2">
                      <CheckCircle className="w-5 h-5 text-green-400" />
                      <span className="font-medium text-green-400">Revenue Collection</span>
                    </div>
                    <p className="text-sm text-gray-400 mb-2">Stripe + Crypto Wallets</p>
                    <p className="text-xs text-gray-500">All revenue flows to designated business accounts only</p>
                  </div>

                  <div className="mt-4 p-3 bg-[#0a0812] rounded-lg border border-gray-800">
                    <p className="text-sm text-gray-400 mb-2">FUND SEPARATION CHECKLIST</p>
                    <ul className="space-y-2 text-sm">
                      <li className="flex items-center gap-2">
                        <CheckCircle className="w-4 h-4 text-green-400" />
                        <span className="text-gray-300">No personal expenses from business accounts</span>
                      </li>
                      <li className="flex items-center gap-2">
                        <CheckCircle className="w-4 h-4 text-green-400" />
                        <span className="text-gray-300">Owner draws properly documented as distributions</span>
                      </li>
                      <li className="flex items-center gap-2">
                        <CheckCircle className="w-4 h-4 text-green-400" />
                        <span className="text-gray-300">Business credit card used exclusively for LLC expenses</span>
                      </li>
                      <li className="flex items-center gap-2">
                        <CheckCircle className="w-4 h-4 text-green-400" />
                        <span className="text-gray-300">Reimbursement policy for any incidental personal use</span>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>

            {/* Business Development Process */}
            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
                <RefreshCw className="w-5 h-5 text-[#7c3aed]" />
                Business Development Process: LLC to DAO Transition
              </h2>
              <div className="grid md:grid-cols-4 gap-4">
                <div className="p-4 bg-[#0a0812] rounded-lg border border-gray-800">
                  <div className="flex items-center gap-2 mb-3">
                    <div className="w-8 h-8 rounded-full bg-[#7c3aed] flex items-center justify-center text-sm font-bold">1</div>
                    <span className="font-medium">Current State</span>
                  </div>
                  <p className="text-sm text-gray-400">Wyoming DAO LLC</p>
                  <ul className="mt-2 space-y-1 text-xs text-gray-500">
                    <li>• Pass-through taxation</li>
                    <li>• Member-managed</li>
                    <li>• Operating Agreement v3</li>
                  </ul>
                </div>

                <div className="p-4 bg-[#0a0812] rounded-lg border border-gray-800">
                  <div className="flex items-center gap-2 mb-3">
                    <div className="w-8 h-8 rounded-full bg-yellow-500/50 flex items-center justify-center text-sm font-bold">2</div>
                    <span className="font-medium">CRM V2 Launch</span>
                  </div>
                  <p className="text-sm text-gray-400">May 2026</p>
                  <ul className="mt-2 space-y-1 text-xs text-gray-500">
                    <li>• Token issuance</li>
                    <li>• Governance activation</li>
                    <li>• Treasury transfer</li>
                  </ul>
                </div>

                <div className="p-4 bg-[#0a0812] rounded-lg border border-gray-800">
                  <div className="flex items-center gap-2 mb-3">
                    <div className="w-8 h-8 rounded-full bg-blue-500/50 flex items-center justify-center text-sm font-bold">3</div>
                    <span className="font-medium">Hybrid Period</span>
                  </div>
                  <p className="text-sm text-gray-400">6-12 months</p>
                  <ul className="mt-2 space-y-1 text-xs text-gray-500">
                    <li>• LLC holds legal contracts</li>
                    <li>• DAO controls treasury</li>
                    <li>• Gradual power transfer</li>
                  </ul>
                </div>

                <div className="p-4 bg-[#0a0812] rounded-lg border border-gray-800">
                  <div className="flex items-center gap-2 mb-3">
                    <div className="w-8 h-8 rounded-full bg-green-500/50 flex items-center justify-center text-sm font-bold">4</div>
                    <span className="font-medium">Full DAO</span>
                  </div>
                  <p className="text-sm text-gray-400">Target: 2027</p>
                  <ul className="mt-2 space-y-1 text-xs text-gray-500">
                    <li>• LLC dissolution or shell</li>
                    <li>• Full on-chain governance</li>
                    <li>• Cayman foundation optional</li>
                  </ul>
                </div>
              </div>

              {/* Action Items */}
              <div className="mt-6 p-4 bg-[#0a0812] rounded-lg border border-gray-800">
                <p className="text-sm text-gray-400 mb-3">IMMEDIATE ACTION ITEMS (Pre-CRM V2)</p>
                <div className="space-y-2">
                  <div className="flex items-center gap-3 p-2 bg-yellow-500/10 rounded border border-yellow-500/30">
                    <AlertTriangle className="w-4 h-4 text-yellow-400" />
                    <span className="text-sm">Update Operating Agreement for token governance integration</span>
                    <span className="ml-auto text-xs text-yellow-400">Due: May 1</span>
                  </div>
                  <div className="flex items-center gap-3 p-2 bg-yellow-500/10 rounded border border-yellow-500/30">
                    <AlertTriangle className="w-4 h-4 text-yellow-400" />
                    <span className="text-sm">Establish clear treasury separation: LLC ops vs DAO treasury</span>
                    <span className="ml-auto text-xs text-yellow-400">Due: May 1</span>
                  </div>
                  <div className="flex items-center gap-3 p-2 bg-blue-500/10 rounded border border-blue-500/30">
                    <Clock className="w-4 h-4 text-blue-400" />
                    <span className="text-sm">Consult tax advisor on token launch implications</span>
                    <span className="ml-auto text-xs text-blue-400">Due: Apr 25</span>
                  </div>
                  <div className="flex items-center gap-3 p-2 bg-blue-500/10 rounded border border-blue-500/30">
                    <Clock className="w-4 h-4 text-blue-400" />
                    <span className="text-sm">Document fund separation procedures for audit trail</span>
                    <span className="ml-auto text-xs text-blue-400">Due: Apr 30</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ComplianceDept;
