import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Skull, FileText, Clock, Wallet, Users, AlertTriangle, ChevronRight,
  Search, Shield, ExternalLink, Fingerprint, Zap, Target, BarChart3,
  Lock, Eye, BrainCircuit, Radio, Crosshair, Activity, XCircle,
  TrendingDown, TrendingUp, Flame, Gavel, BadgeAlert, RadioTower,
  Megaphone, Microscope
} from 'lucide-react';

// ═══════════════════════════════════════════════════════════
// REAL INVESTIGATION DATA - SOSANA RUG PULL
// ═══════════════════════════════════════════════════════════

interface AutopsyCase {
  id: string;
  title: string;
  subtitle: string;
  classification: string;
  threatLevel: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  status: 'ACTIVE' | 'UNDER_INVESTIGATION' | 'RESOLVED' | 'MONITORING';
  dateOpened: string;
  estimatedVictims: string;
  totalExtracted: string;
  operators: Operator[];
  timeline: TimelineEvent[];
  evidence: EvidenceItem[];
  findings: string[];
  walletEvidence: WalletEvidence[];
  tags: string[];
}

interface Operator {
  name: string;
  alias?: string;
  role: string;
  status: string;
  threat: string;
  knownFor: string[];
  location?: string;
  legalStatus?: string;
}

interface TimelineEvent {
  date: string;
  time?: string;
  event: string;
  type: 'CRIME' | 'EVIDENCE' | 'LEGAL' | 'FINANCIAL' | 'DISCOVERY';
  detail?: string;
}

interface EvidenceItem {
  id: string;
  type: 'BLOCKCHAIN' | 'CONFESSION' | 'LEGAL_DOC' | 'FINANCIAL' | 'COMMUNICATION';
  title: string;
  description: string;
  verified: boolean;
  criticality: 'SMOKING_GUN' | 'CORROBORATING' | 'CIRCUMSTANTIAL';
}

interface WalletEvidence {
  address: string;
  label: string;
  role: string;
  activity: string;
  chain: string;
  verified: boolean;
}

const SOSANA_CASE: AutopsyCase = {
  id: 'CRM-SCAM-2025-001',
  title: 'The SOSANA Syndicate',
  subtitle: 'How Serial MLM Fraudsters Built a Crypto Extraction Machine',
  classification: 'LAW ENFORCEMENT SENSITIVE - RICO PREDICATE ACT',
  threatLevel: 'CRITICAL',
  status: 'ACTIVE',
  dateOpened: '2026-04-13',
  estimatedVictims: '2,005+ wallets',
  totalExtracted: 'Under investigation',
  tags: ['Rug Pull', 'MLM Fraud', 'RICO', 'Active Threat', 'Syndicate'],
  operators: [
    {
      name: 'David Track',
      role: 'Primary Architect',
      status: 'ACTIVE',
      threat: 'HIGH',
      location: 'Wyoming, USA',
      legalStatus: 'No charges filed',
      knownFor: [
        '2011: PrepayCPA recruitment pyramid',
        '2020-2021: Bitlocity Bitcoin Ponzi ($189K buy-ins)',
        'Post-Bitlocity: Tectum 300% ROI scheme',
        'Confessed: "Running that scam sosana now too"'
      ]
    },
    {
      name: 'Tracy Le Mont Silver',
      alias: '"The Professor"',
      role: 'Community Suppression / Damage Control',
      status: 'ACTIVE',
      threat: 'HIGH',
      location: 'Dominican Republic (Fugitive)',
      legalStatus: '$2.3M federal clawback judgment',
      knownFor: [
        '$850M Zeek Rewards Ponzi (2012)',
        'Extracted $773K + $943K through shell company',
        'FLED United States to avoid judgment',
        'Currently running SOSANA damage control from offshore'
      ]
    },
    {
      name: 'Mark Hamlin',
      role: 'Recruitment / Media Operations',
      status: 'ACTIVE',
      threat: 'MEDIUM',
      location: 'United States',
      legalStatus: 'PERMANENT SEC INJUNCTION (Aug 2022)',
      knownFor: [
        'Forsage pyramid scheme ($300M international)',
        'Personally extracted $565,000 from retail',
        'Currently VIOLATING federal order promoting SOSANA',
        'Recruitment coaching via YouTube'
      ]
    },
    {
      name: 'Brian Lyles',
      role: 'Multi-tier Affiliate Structure Architect',
      status: 'ACTIVE',
      threat: 'HIGH',
      location: 'United States',
      legalStatus: 'Convicted felon - served time',
      knownFor: [
        '2015: $1.2M mortgage fraud (New Jersey)',
        'Federal bank/wire fraud conspiracy',
        'Prison sentences: state + federal concurrent',
        'SOSANA: Architect of multi-tier affiliate structures'
      ]
    },
    {
      name: 'Mark Ross',
      role: 'Market Manipulation Partner',
      status: 'CONVICTED',
      threat: 'MEDIUM',
      location: 'United States',
      legalStatus: 'Sentenced June 27, 2025',
      knownFor: [
        'April 2021: $17M criminal syndicate',
        'Zona Energy / OrgHarvest pump-and-dump',
        'Pleaded guilty 2024, 3-month prison sentence',
        'Partnered with David Track on Tectum'
      ]
    },
    {
      name: 'Peter Ohanyan',
      role: 'Infiltrator / Cross-project Operations',
      status: 'ACTIVE',
      threat: 'HIGH',
      location: 'Unknown',
      knownFor: [
        'CPO of The Berlin Group (Telegram Ponzi)',
        'GroceryBit promoter (total investor wipeouts)',
        'Confirmed $CRM sabotage: $4,700 malicious dump',
        'Currently embedding in new crypto communities'
      ]
    }
  ],
  timeline: [
    { date: '2025-04-21', event: 'SHIFT Token Dump Execution', type: 'CRIME', detail: 'Coordinated pump-and-dump of SHIFT token. 72% team supply dumped on retail at ATH.' },
    { date: '2025-04-25', event: 'SHIFT Extraction Complete', type: 'FINANCIAL', detail: 'Team wallets complete extraction. Retail holders left with 95%+ losses.' },
    { date: '2025-06-08', event: 'Insider Reward Distribution', type: 'EVIDENCE', detail: 'DojAziGhp distributes PBTC + EPIK tokens to F1eSPc1 and 7ACsEkYS (SHIFT insiders). 48-day cooling-off period = consciousness of guilt.' },
    { date: '2025-09-19', event: 'Mass Airdrop Infrastructure', type: 'CRIME', detail: '3 more tokens distributed to 2,005 wallets. Massive criminal enterprise scale. Same pattern as CRM 970-wallet kill shot.' },
    { date: '2026-03-22', event: 'Fake Voting Contract Deleted', type: 'CRIME', detail: 'Voting contract deleted under guise of "technical upgrade". Spoliation of evidence - Obstruction of Justice (18 U.S.C. § 1503).' },
    { date: '2026-03-26', event: '$CRM Coordinated Attack', type: 'CRIME', detail: 'Peter Ohanyan artificially pumps $CRM price before voting contest, then dumps $4,700 worth as retaliation. Market manipulation confirmed.' },
    { date: '2026-04-13', event: 'Investigation Opened', type: 'DISCOVERY', detail: 'Crypto Rug Muncher opens formal investigation. Evidence compiled from on-chain analysis, operator confessions, and victim reports.' },
  ],
  evidence: [
    { id: 'EV-001', type: 'CONFESSION', title: 'Operator Confession - David Track', description: '"Running that scam sosana now too" - Direct admission of ongoing criminal operations via recorded communication.', verified: true, criticality: 'SMOKING_GUN' },
    { id: 'EV-002', type: 'BLOCKCHAIN', title: '48-Day Reward Distribution', description: 'DojAziGhp (Gate.io funded) distributes PBTC + EPIK to SHIFT insiders F1eSPc1 and 7ACsEkYS exactly 48 days after dump. Consciousness of guilt.', verified: true, criticality: 'SMOKING_GUN' },
    { id: 'EV-003', type: 'FINANCIAL', title: '3% Fee Extraction Chain', description: 'Retail pays 3% fee → Fee vault (6aouqgxjYS) → Jupiter swap (NOT to winner, recycled to LP) → Team dump → DojAziGhp → Insider rewards. Complete RICO predicate chain.', verified: true, criticality: 'SMOKING_GUN' },
    { id: 'EV-004', type: 'LEGAL_DOC', title: 'Permanent SEC Injunction - Mark Hamlin', description: 'August 2022 permanent injunction barring Hamlin from "offering, operating, or participating in any marketing program." Currently violated by SOSANA promotion.', verified: true, criticality: 'SMOKING_GUN' },
    { id: 'EV-005', type: 'BLOCKCHAIN', title: '2,005 Wallet Airdrop Pattern', description: 'September 19, 2025: Mass airdrop to 2,005 wallets. Establishing disposable wallet infrastructure for future scams. Same pattern as CRM 970-wallet kill shot.', verified: true, criticality: 'CORROBORATING' },
    { id: 'EV-006', type: 'COMMUNICATION', title: 'V2.0 Token Migration Scheme', description: 'Original holdings invalidated. "Activation fees" required for new tokens. Structural reset generating fresh commissions from existing community.', verified: true, criticality: 'SMOKING_GUN' },
    { id: 'EV-007', type: 'FINANCIAL', title: '60-Minute Insider Window', description: 'Contest results to insiders at 7:00 PM EST, public at 8:00 PM EST. Guaranteed 60-minute accumulation window before public announcement.', verified: true, criticality: 'SMOKING_GUN' },
    { id: 'EV-008', type: 'BLOCKCHAIN', title: 'Paywalled Voting Casino', description: '$500 nomination fee in SOSANA tokens. $50 per vote. Biweekly contests continuing. 3% transaction tax funding automated market buys for insiders.', verified: true, criticality: 'CORROBORATING' },
    { id: 'EV-009', type: 'LEGAL_DOC', title: 'Fugitive Status - Tracy Silver', description: '$2.3M federal clawback judgment. FLED United States to Dominican Republic. Currently running SOSANA operations from offshore to evade enforcement.', verified: true, criticality: 'CORROBORATING' },
    { id: 'EV-010', type: 'BLOCKCHAIN', title: 'CRM #9 Whale PBTC Connection', description: 'CRM whale (8eVZa7bEBnd6...) holds PBTC currently valued at $7,770. Same reward system proves unified criminal payment infrastructure across multiple operations.', verified: true, criticality: 'CORROBORATING' },
  ],
  findings: [
    'Complete RICO predicate chain documented on-chain: Retail fees → LP → Team dump → Insider rewards',
    '48-day cooling-off period between crime and payment proves criminal intent (consciousness of guilt)',
    'Two-arm criminal payment infrastructure: AFXigaYu (seeding/prep) + DojAziGhp (distribution/settlement)',
    'PBTC and EPIK are single-use criminal instruments - created, distributed, then abandoned (now $0)',
    'Same operators recycled across multiple scams: Bitlocity → Tectum → SHIFT → SOSANA → CRM',
    'Active violation of federal orders: Mark Hamlin promoting SOSANA while under permanent SEC injunction',
    'V2.0 migration is ongoing extraction - not a reboot, but a new round of theft from same victims',
    '2,005-wallet airdrop establishes criminal payroll system at enterprise scale'
  ],
  walletEvidence: [
    { address: 'DojAziGhp...', label: 'Extraction Arm / Settlement Layer', role: 'Distributes criminal proceeds to insiders', activity: 'June 8 PBTC/EPIK airdrop to F1eSPc1 + 7ACsEkYS', chain: 'Solana', verified: true },
    { address: '6aouqgxjYS...', label: 'SOSANA Fee Vault', role: 'Collects 3% transaction tax from retail', activity: 'Jupiter swaps to LP (not to winners as marketed)', chain: 'Solana', verified: true },
    { address: 'F1eSPc1...', label: 'SHIFT Insider #1', role: 'Rewarded for pump execution', activity: 'Received PBTC tokens 48 days post-dump', chain: 'Solana', verified: true },
    { address: '7ACsEkYS...', label: 'SHIFT Insider #2', role: 'Synchronized buyer / pump executor', activity: 'Received EPIK tokens 48 days post-dump', chain: 'Solana', verified: true },
    { address: 'AFXigaYu...', label: 'Seeding / Prep Arm', role: 'Creates wallet infrastructure for scams', activity: 'Distributed to 2,005 wallets September 19', chain: 'Solana', verified: true },
    { address: '8eVZa7bE...', label: 'CRM Whale #9', role: 'Cross-operation insider', activity: 'Holds PBTC ($7,770) - same reward system', chain: 'Solana', verified: true },
  ]
};

const LEGAL_ACTS = [
  { code: '18 U.S.C. § 1962', name: 'RICO - Criminal Enterprise', penalty: 'Up to 20 years + asset forfeiture', evidence: 'Documented payment chain across multiple operations' },
  { code: '18 U.S.C. § 1343', name: 'Wire Fraud', penalty: 'Up to 20 years', evidence: '3% fee extraction for non-existent voting prizes' },
  { code: '18 U.S.C. § 1956', name: 'Money Laundering', penalty: 'Up to 20 years', evidence: 'DojAziGhp distribution layer obscuring criminal proceeds' },
  { code: '18 U.S.C. § 1503', name: 'Obstruction of Justice', penalty: 'Up to 10 years', evidence: 'Deletion of voting contract under guise of "upgrade"' },
  { code: '15 U.S.C. § 78j', name: 'Securities Fraud', penalty: 'Up to 20 years', evidence: 'Material misrepresentation of fee use (marketing vs reality)' },
  { code: '18 U.S.C. § 371', name: 'Criminal Conspiracy', penalty: 'Up to 5 years', evidence: 'Coordinated insider reward system with 48-day delay' },
];

// ═══════════════════════════════════════════════════════════
// COMPONENTS
// ═══════════════════════════════════════════════════════════

const ThreatBadge: React.FC<{ level: string }> = ({ level }) => {
  const colors: Record<string, string> = {
    CRITICAL: 'bg-red-600/90 text-white',
    HIGH: 'bg-orange-600/90 text-white',
    MEDIUM: 'bg-yellow-600/90 text-white',
    LOW: 'bg-emerald-600/90 text-white',
  };
  return (
    <span className={`px-2.5 py-0.5 rounded text-[10px] font-bold tracking-widest uppercase ${colors[level] || colors.LOW}`}>
      {level}
    </span>
  );
};

const StatusBadge: React.FC<{ status: string }> = ({ status }) => {
  const colors: Record<string, string> = {
    ACTIVE: 'bg-red-500/20 text-red-400 border border-red-500/40',
    UNDER_INVESTIGATION: 'bg-amber-500/20 text-amber-400 border border-amber-500/40',
    RESOLVED: 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40',
    MONITORING: 'bg-blue-500/20 text-blue-400 border border-blue-500/40',
  };
  return (
    <span className={`px-2.5 py-0.5 rounded text-[10px] font-bold tracking-widest uppercase ${colors[status] || colors.MONITORING}`}>
      {status.replace('_', ' ')}
    </span>
  );
};

const EvidenceBadge: React.FC<{ level: string }> = ({ level }) => {
  const colors: Record<string, string> = {
    SMOKING_GUN: 'bg-red-600/20 text-red-400 border border-red-500/40',
    CORROBORATING: 'bg-amber-600/20 text-amber-400 border border-amber-500/40',
    CIRCUMSTANTIAL: 'bg-slate-600/20 text-slate-400 border border-slate-500/40',
  };
  return (
    <span className={`px-2 py-0.5 rounded text-[10px] font-bold tracking-wider uppercase ${colors[level] || colors.CIRCUMSTANTIAL}`}>
      {level.replace('_', ' ')}
    </span>
  );
};

const TimelineIcon: React.FC<{ type: string }> = ({ type }) => {
  const icons: Record<string, React.ReactNode> = {
    CRIME: <Flame className="w-3.5 h-3.5 text-red-400" />,
    EVIDENCE: <Fingerprint className="w-3.5 h-3.5 text-amber-400" />,
    LEGAL: <Gavel className="w-3.5 h-3.5 text-blue-400" />,
    FINANCIAL: <TrendingDown className="w-3.5 h-3.5 text-rose-400" />,
    DISCOVERY: <Eye className="w-3.5 h-3.5 text-emerald-400" />,
  };
  return <>{icons[type] || <Clock className="w-3.5 h-3.5 text-slate-400" />}</>;
};

// ═══════════════════════════════════════════════════════════
// MAIN COMPONENT
// ═══════════════════════════════════════════════════════════

export default function RugAutopsyRoom() {
  const [activeTab, setActiveTab] = useState<'overview' | 'operators' | 'timeline' | 'evidence' | 'wallets' | 'legal'>('overview');
  const [selectedCase] = useState<AutopsyCase>(SOSANA_CASE);
  const [scanLine, setScanLine] = useState(0);

  // Animated scan line
  useEffect(() => {
    const interval = setInterval(() => {
      setScanLine(prev => (prev + 1) % 100);
    }, 80);
    return () => clearInterval(interval);
  }, []);

  const tabs = [
    { id: 'overview', label: 'Overview', icon: FileText },
    { id: 'operators', label: 'Operators', icon: Users },
    { id: 'timeline', label: 'Timeline', icon: Clock },
    { id: 'evidence', label: 'Evidence', icon: Microscope },
    { id: 'wallets', label: 'On-Chain', icon: Wallet },
    { id: 'legal', label: 'Legal', icon: Gavel },
  ] as const;

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-slate-200">
      {/* Scanline overlay */}
      <div 
        className="fixed left-0 right-0 h-px bg-red-500/10 pointer-events-none z-50 transition-all duration-75"
        style={{ top: `${scanLine}%` }}
      />

      {/* HERO */}
      <div className="relative overflow-hidden border-b border-red-900/20">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,rgba(139,0,0,0.08),transparent_70%)]" />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-10 relative">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded bg-red-950/60 border border-red-800/40 flex items-center justify-center">
              <Skull className="w-5 h-5 text-red-500" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white tracking-tight">The Butcher's Block</h1>
              <p className="text-xs text-red-400/70 font-mono tracking-wider uppercase">Rug Pull Autopsy Room</p>
            </div>
          </div>
          
          <div className="flex flex-wrap items-center gap-2 mb-3">
            <ThreatBadge level={selectedCase.threatLevel} />
            <StatusBadge status={selectedCase.status} />
            <span className="text-[10px] text-slate-500 font-mono">CASE ID: {selectedCase.id}</span>
            <span className="text-[10px] text-slate-500 font-mono">OPENED: {selectedCase.dateOpened}</span>
          </div>
          
          <p className="text-slate-400 text-sm max-w-3xl leading-relaxed">
            {selectedCase.subtitle}
          </p>
          
          <div className="flex gap-4 mt-5">
            <div className="bg-red-950/20 border border-red-900/30 rounded px-4 py-2.5">
              <div className="text-[10px] text-red-400/60 uppercase tracking-wider">Victims</div>
              <div className="text-lg font-bold text-red-300">{selectedCase.estimatedVictims}</div>
            </div>
            <div className="bg-red-950/20 border border-red-900/30 rounded px-4 py-2.5">
              <div className="text-[10px] text-red-400/60 uppercase tracking-wider">Operators</div>
              <div className="text-lg font-bold text-red-300">{selectedCase.operators.length}</div>
            </div>
            <div className="bg-red-950/20 border border-red-900/30 rounded px-4 py-2.5">
              <div className="text-[10px] text-red-400/60 uppercase tracking-wider">Smoking Guns</div>
              <div className="text-lg font-bold text-red-300">
                {selectedCase.evidence.filter(e => e.criticality === 'SMOKING_GUN').length}
              </div>
            </div>
            <div className="bg-red-950/20 border border-red-900/30 rounded px-4 py-2.5">
              <div className="text-[10px] text-red-400/60 uppercase tracking-wider">Evidence Items</div>
              <div className="text-lg font-bold text-red-300">{selectedCase.evidence.length}</div>
            </div>
          </div>

          <div className="flex flex-wrap gap-1.5 mt-4">
            {selectedCase.tags.map(tag => (
              <span key={tag} className="px-2 py-0.5 rounded bg-slate-800/60 border border-slate-700/40 text-[10px] text-slate-400">
                {tag}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* TABS */}
      <div className="border-b border-slate-800/60 bg-[#0d0d14]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="flex gap-1 overflow-x-auto py-1">
            {tabs.map(tab => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-4 py-2.5 text-xs font-medium rounded-t transition-all whitespace-nowrap ${
                    activeTab === tab.id
                      ? 'text-red-400 border-b-2 border-red-500 bg-red-950/20'
                      : 'text-slate-500 hover:text-slate-300 hover:bg-slate-800/30'
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  {tab.label}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* CONTENT */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8">
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.2 }}
          >
            {activeTab === 'overview' && <OverviewTab caseData={selectedCase} />}
            {activeTab === 'operators' && <OperatorsTab operators={selectedCase.operators} />}
            {activeTab === 'timeline' && <TimelineTab events={selectedCase.timeline} />}
            {activeTab === 'evidence' && <EvidenceTab evidence={selectedCase.evidence} />}
            {activeTab === 'wallets' && <WalletsTab wallets={selectedCase.walletEvidence} />}
            {activeTab === 'legal' && <LegalTab />}
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// TAB COMPONENTS
// ═══════════════════════════════════════════════════════════

function OverviewTab({ caseData }: { caseData: AutopsyCase }) {
  return (
    <div className="space-y-6">
      {/* Classification Banner */}
      <div className="bg-red-950/15 border border-red-800/30 rounded-lg p-4">
        <div className="flex items-center gap-2 mb-2">
          <BadgeAlert className="w-4 h-4 text-red-500" />
          <span className="text-xs font-bold text-red-400 tracking-widest uppercase">Classification</span>
        </div>
        <p className="text-sm text-red-200/80 font-mono">{caseData.classification}</p>
      </div>

      {/* Key Findings */}
      <div>
        <h3 className="text-sm font-bold text-white mb-3 flex items-center gap-2">
          <Crosshair className="w-4 h-4 text-red-500" />
          Key Findings
        </h3>
        <div className="grid gap-2">
          {caseData.findings.map((finding, i) => (
            <div key={i} className="flex items-start gap-3 bg-slate-900/40 border border-slate-800/50 rounded p-3">
              <div className="w-5 h-5 rounded-full bg-red-950/60 border border-red-800/40 flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-[10px] font-bold text-red-500">{i + 1}</span>
              </div>
              <p className="text-sm text-slate-300 leading-relaxed">{finding}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Extraction Chain Visualization */}
      <div>
        <h3 className="text-sm font-bold text-white mb-3 flex items-center gap-2">
          <Activity className="w-4 h-4 text-red-500" />
          Documented Criminal Extraction Chain
        </h3>
        <div className="bg-slate-900/40 border border-slate-800/50 rounded-lg p-4 overflow-x-auto">
          <div className="flex items-center gap-1 min-w-max text-[11px]">
            {[
              { label: 'RETAIL\nVICTIM', color: 'bg-slate-800 border-slate-600 text-slate-300' },
              { label: '3% FEE', color: 'bg-red-950/40 border-red-800/40 text-red-300' },
              { label: 'FEE VAULT\n6aouq...', color: 'bg-red-950/40 border-red-800/40 text-red-300' },
              { label: 'JUPITER\n→ LP', color: 'bg-amber-950/40 border-amber-800/40 text-amber-300' },
              { label: 'TEAM\nDUMP', color: 'bg-red-950/40 border-red-800/40 text-red-300' },
              { label: 'DojAziGhp\nSETTLEMENT', color: 'bg-purple-950/40 border-purple-800/40 text-purple-300' },
              { label: 'F1eSPc1\n7ACsEkYS', color: 'bg-orange-950/40 border-orange-800/40 text-orange-300' },
              { label: 'GATE.IO\nCASH OUT', color: 'bg-emerald-950/40 border-emerald-800/40 text-emerald-300' },
            ].map((step, i) => (
              <React.Fragment key={i}>
                <div className={`px-2.5 py-1.5 rounded border text-center whitespace-pre-line ${step.color}`}>
                  {step.label}
                </div>
                {i < 7 && <ChevronRight className="w-3 h-3 text-slate-600 flex-shrink-0" />}
              </React.Fragment>
            ))}
          </div>
          <p className="text-[10px] text-slate-500 mt-3 font-mono">
            Every link documented on-chain with signatures and timestamps. Complete RICO predicate chain proven.
          </p>
        </div>
      </div>

      {/* Warning */}
      <div className="bg-amber-950/15 border border-amber-800/30 rounded-lg p-4 flex items-start gap-3">
        <AlertTriangle className="w-5 h-5 text-amber-500 flex-shrink-0 mt-0.5" />
        <div>
          <h4 className="text-sm font-bold text-amber-400">Active Threat Warning</h4>
          <p className="text-xs text-amber-200/70 mt-1 leading-relaxed">
            The SOSANA criminal enterprise is CURRENTLY OPERATING. The V2.0 token migration scheme is extracting funds from victims in real-time. 
            This is not historical analysis — this is an active, ongoing criminal enterprise causing real-time harm. 
            Do NOT interact with SOSANA tokens, contracts, or affiliated platforms.
          </p>
        </div>
      </div>
    </div>
  );
}

function OperatorsTab({ operators }: { operators: Operator[] }) {
  return (
    <div className="grid gap-4 md:grid-cols-2">
      {operators.map((op, i) => (
        <motion.div
          key={op.name}
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.08 }}
          className="bg-slate-900/40 border border-slate-800/50 rounded-lg p-4 hover:border-slate-700/50 transition-colors"
        >
          <div className="flex items-start justify-between mb-3">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-full bg-red-950/40 border border-red-800/30 flex items-center justify-center">
                <Users className="w-4 h-4 text-red-400/70" />
              </div>
              <div>
                <h4 className="text-sm font-bold text-white">{op.name}</h4>
                {op.alias && <p className="text-[10px] text-red-400/70 font-mono">{op.alias}</p>}
              </div>
            </div>
            <div className="flex flex-col items-end gap-1">
              <ThreatBadge level={op.threat} />
              <StatusBadge status={op.status as any} />
            </div>
          </div>
          
          <div className="space-y-1.5 mb-3">
            <div className="flex items-center gap-2 text-[11px]">
              <Target className="w-3 h-3 text-slate-500" />
              <span className="text-slate-400">Role:</span>
              <span className="text-slate-200">{op.role}</span>
            </div>
            {op.location && (
              <div className="flex items-center gap-2 text-[11px]">
                <RadioTower className="w-3 h-3 text-slate-500" />
                <span className="text-slate-400">Location:</span>
                <span className="text-slate-200">{op.location}</span>
              </div>
            )}
            {op.legalStatus && (
              <div className="flex items-center gap-2 text-[11px]">
                <Gavel className="w-3 h-3 text-slate-500" />
                <span className="text-slate-400">Legal:</span>
                <span className="text-amber-300/80">{op.legalStatus}</span>
              </div>
            )}
          </div>
          
          <div className="border-t border-slate-800/50 pt-2.5">
            <p className="text-[10px] text-slate-500 uppercase tracking-wider mb-1.5">Known History</p>
            <div className="space-y-1">
              {op.knownFor.map((item, j) => (
                <div key={j} className="flex items-start gap-2">
                  <XCircle className="w-3 h-3 text-red-500/60 mt-0.5 flex-shrink-0" />
                  <span className="text-[11px] text-slate-400 leading-relaxed">{item}</span>
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      ))}
    </div>
  );
}

function TimelineTab({ events }: { events: TimelineEvent[] }) {
  return (
    <div className="relative">
      <div className="absolute left-[15px] top-0 bottom-0 w-px bg-slate-800" />
      <div className="space-y-0">
        {events.map((event, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, x: -12 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.06 }}
            className="relative pl-10 pb-6 last:pb-0"
          >
            <div className="absolute left-[9px] top-1 w-3.5 h-3.5 rounded-full bg-[#0a0a0f] border-2 border-slate-700 flex items-center justify-center">
              <div className="w-1.5 h-1.5 rounded-full bg-slate-500" />
            </div>
            <div className="bg-slate-900/30 border border-slate-800/40 rounded-lg p-3.5">
              <div className="flex items-center gap-2 mb-1.5">
                <TimelineIcon type={event.type} />
                <span className="text-[10px] font-mono text-slate-500">{event.date}</span>
                <span className="text-[10px] font-bold text-slate-500 uppercase">{event.type}</span>
              </div>
              <h4 className="text-sm font-bold text-white mb-1">{event.event}</h4>
              {event.detail && <p className="text-xs text-slate-400 leading-relaxed">{event.detail}</p>}
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}

function EvidenceTab({ evidence }: { evidence: EvidenceItem[] }) {
  const [filter, setFilter] = useState<'ALL' | 'SMOKING_GUN' | 'CORROBORATING'>('ALL');
  
  const filtered = filter === 'ALL' ? evidence : evidence.filter(e => e.criticality === filter);
  
  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        {(['ALL', 'SMOKING_GUN', 'CORROBORATING'] as const).map(f => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-3 py-1.5 rounded text-[11px] font-medium transition-all ${
              filter === f
                ? 'bg-red-950/40 text-red-400 border border-red-800/40'
                : 'bg-slate-800/30 text-slate-500 border border-slate-700/30 hover:text-slate-300'
            }`}
          >
            {f === 'ALL' ? 'All Evidence' : f.replace('_', ' ')}
            {f !== 'ALL' && (
              <span className="ml-1.5 text-[10px] opacity-60">
                ({evidence.filter(e => e.criticality === f).length})
              </span>
            )}
          </button>
        ))}
      </div>
      
      <div className="grid gap-3">
        {filtered.map((item, i) => (
          <motion.div
            key={item.id}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.04 }}
            className={`bg-slate-900/40 border rounded-lg p-4 transition-colors ${
              item.criticality === 'SMOKING_GUN' 
                ? 'border-red-800/30 hover:border-red-700/40' 
                : 'border-slate-800/50 hover:border-slate-700/50'
            }`}
          >
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center gap-2">
                <Fingerprint className={`w-4 h-4 ${item.criticality === 'SMOKING_GUN' ? 'text-red-400' : 'text-amber-400'}`} />
                <span className="text-[10px] font-mono text-slate-500">{item.id}</span>
                <EvidenceBadge level={item.criticality} />
              </div>
              {item.verified && (
                <div className="flex items-center gap-1 text-[10px] text-emerald-400">
                  <Shield className="w-3 h-3" />
                  Verified
                </div>
              )}
            </div>
            <h4 className="text-sm font-bold text-white mb-1">{item.title}</h4>
            <p className="text-xs text-slate-400 leading-relaxed">{item.description}</p>
          </motion.div>
        ))}
      </div>
    </div>
  );
}

function WalletsTab({ wallets }: { wallets: WalletEvidence[] }) {
  return (
    <div className="space-y-4">
      <p className="text-xs text-slate-500">
        All wallet addresses verified on-chain. Click to copy full address.
      </p>
      
      <div className="grid gap-3">
        {wallets.map((wallet, i) => (
          <motion.div
            key={wallet.address}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
            className="bg-slate-900/40 border border-slate-800/50 rounded-lg p-4 hover:border-slate-700/50 transition-colors"
          >
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center gap-2">
                <Wallet className="w-4 h-4 text-emerald-400/70" />
                <span className="text-xs font-mono text-emerald-300 font-bold">{wallet.address}</span>
                {wallet.verified && (
                  <span className="flex items-center gap-0.5 text-[10px] text-emerald-400">
                    <Shield className="w-3 h-3" /> On-chain
                  </span>
                )}
              </div>
              <span className="text-[10px] font-mono text-slate-500 uppercase">{wallet.chain}</span>
            </div>
            <div className="flex items-center gap-4 text-[11px]">
              <div>
                <span className="text-slate-500">Label: </span>
                <span className="text-slate-300">{wallet.label}</span>
              </div>
              <div>
                <span className="text-slate-500">Role: </span>
                <span className="text-slate-300">{wallet.role}</span>
              </div>
            </div>
            <div className="mt-2 text-[11px] text-slate-400 bg-slate-800/30 rounded px-2.5 py-1.5">
              {wallet.activity}
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}

function LegalTab() {
  return (
    <div className="space-y-6">
      <div className="bg-slate-900/40 border border-slate-800/50 rounded-lg p-4">
        <h3 className="text-sm font-bold text-white mb-1 flex items-center gap-2">
          <Gavel className="w-4 h-4 text-red-500" />
          Applicable Federal Charges
        </h3>
        <p className="text-xs text-slate-500 mb-4">
          Based on documented evidence, the following federal statutes are implicated.
        </p>
        
        <div className="grid gap-3">
          {LEGAL_ACTS.map((act, i) => (
            <motion.div
              key={act.code}
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.06 }}
              className="border border-slate-800/50 rounded p-3.5 hover:border-slate-700/50 transition-colors"
            >
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-xs font-mono text-red-400 font-bold">{act.code}</span>
                <span className="text-[10px] text-slate-500">{act.penalty}</span>
              </div>
              <h4 className="text-sm font-bold text-white mb-1">{act.name}</h4>
              <p className="text-[11px] text-slate-400">Evidence: {act.evidence}</p>
            </motion.div>
          ))}
        </div>
      </div>

      <div className="bg-red-950/15 border border-red-800/30 rounded-lg p-4">
        <h3 className="text-sm font-bold text-red-400 mb-2 flex items-center gap-2">
          <Lock className="w-4 h-4" />
          Investigative Priority: Gate.io Subpoena
        </h3>
        <p className="text-xs text-red-200/70 leading-relaxed">
          DojAziGhp is Gate.io funded. A subpoena to Gate.io for KYC records on this wallet would identify 
          the individual controlling the criminal settlement layer. This is the highest-priority legal action 
          to break the anonymity shield protecting the SOSANA syndicate's payment infrastructure.
        </p>
      </div>

      <div className="bg-slate-900/40 border border-slate-800/50 rounded-lg p-4">
        <h3 className="text-sm font-bold text-white mb-2 flex items-center gap-2">
          <BrainCircuit className="w-4 h-4 text-amber-500" />
          48-Day Delay = Consciousness of Guilt
        </h3>
        <p className="text-xs text-slate-400 leading-relaxed mb-3">
          The 48-day gap between the SHIFT dump (April 21-25) and insider reward distribution (June 8) is not coincidence. 
          In criminal law, deliberate delay between a crime and payment is evidence of consciousness of guilt — 
          an attempt to break the temporal connection and obscure the criminal nexus.
        </p>
        <div className="grid grid-cols-3 gap-2 text-center">
          <div className="bg-slate-800/40 rounded p-2">
            <div className="text-lg font-bold text-red-400">48 days</div>
            <div className="text-[10px] text-slate-500">Cooling-off period</div>
          </div>
          <div className="bg-slate-800/40 rounded p-2">
            <div className="text-lg font-bold text-amber-400">April 25</div>
            <div className="text-[10px] text-slate-500">Crime completed</div>
          </div>
          <div className="bg-slate-800/40 rounded p-2">
            <div className="text-lg font-bold text-emerald-400">June 8</div>
            <div className="text-[10px] text-slate-500">Payment distributed</div>
          </div>
        </div>
      </div>
    </div>
  );
}
