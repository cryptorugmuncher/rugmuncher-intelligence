import React, { useState, useRef, useCallback } from 'react';
import {
  Search, Shield, AlertTriangle, Skull, CheckCircle2, Clock,
  Copy, Check, Download, Share2, Loader2, Zap, Lock, Unlock,
  Droplets, Users, Flame, TrendingUp, TrendingDown, Activity,
  ChevronDown, ChevronUp, ExternalLink, RefreshCw
} from 'lucide-react';
import { toPng } from 'html-to-image';
import api from '../services/api';

// ═══════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════

interface ScanResult {
  token_address: string;
  chain: string;
  overall_risk: string;
  risk_score: number;
  risk_level: string;
  mint_authority_renounced: boolean;
  freeze_authority_renounced: boolean;
  total_liquidity_usd: number;
  liquidity_pools: Array<{
    dex: string;
    pair: string;
    liquidity_usd: number;
    lp_locked_percentage: number;
  }>;
  honeypot_detected: boolean;
  holder_concentration: {
    top_10_percentage: number;
    top_50_percentage: number;
    total_holders: number;
  };
  tax_info?: {
    buy_tax: number;
    sell_tax: number;
    transfer_tax: number;
  };
  red_flags: string[];
  green_flags: string[];
  analyzed_at: string;
  ai_consensus?: string;
}

// ═══════════════════════════════════════════════════════════
// HELPERS
// ═══════════════════════════════════════════════════════════

function getRiskColor(score: number): { bg: string; text: string; border: string; gradient: string; icon: any } {
  if (score >= 70) return { bg: 'bg-red-950/40', text: 'text-red-400', border: 'border-red-800/40', gradient: 'from-red-600 to-red-900', icon: Skull };
  if (score >= 40) return { bg: 'bg-orange-950/40', text: 'text-orange-400', border: 'border-orange-800/40', gradient: 'from-orange-500 to-red-600', icon: AlertTriangle };
  if (score >= 20) return { bg: 'bg-yellow-950/40', text: 'text-yellow-400', border: 'border-yellow-800/40', gradient: 'from-yellow-500 to-orange-500', icon: AlertTriangle };
  return { bg: 'bg-emerald-950/40', text: 'text-emerald-400', border: 'border-emerald-800/40', gradient: 'from-emerald-500 to-green-600', icon: CheckCircle2 };
}

function getRiskLabel(score: number): string {
  if (score >= 70) return 'CRITICAL';
  if (score >= 40) return 'HIGH RISK';
  if (score >= 20) return 'MEDIUM RISK';
  return 'SAFE';
}

function truncate(addr: string, front = 6, back = 4): string {
  if (!addr || addr.length <= front + back + 3) return addr;
  return `${addr.slice(0, front)}...${addr.slice(-back)}`;
}

// ═══════════════════════════════════════════════════════════
// MAIN COMPONENT
// ═══════════════════════════════════════════════════════════

interface TokenScanTerminalProps {
  embedded?: boolean;
  defaultAddress?: string;
}

export default function TokenScanTerminal({ embedded = false, defaultAddress = '' }: TokenScanTerminalProps) {
  const [address, setAddress] = useState(defaultAddress);
  const [chain, setChain] = useState('solana');
  const [scanning, setScanning] = useState(false);
  const [result, setResult] = useState<ScanResult | null>(null);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);
  const [showDetails, setShowDetails] = useState(false);
  const [generating, setGenerating] = useState(false);
  const cardRef = useRef<HTMLDivElement>(null);

  const chains = [
    { id: 'solana', name: 'Solana', icon: '◎' },
    { id: 'ethereum', name: 'Ethereum', icon: '⧫' },
    { id: 'bsc', name: 'BSC', icon: 'B' },
    { id: 'base', name: 'Base', icon: 'B' },
    { id: 'arbitrum', name: 'Arbitrum', icon: 'A' },
  ];

  const handleScan = async () => {
    if (!address || address.length < 10) {
      setError('Enter a valid token contract address');
      return;
    }
    setError('');
    setScanning(true);
    setResult(null);
    setShowDetails(false);

    try {
      // Try the full crypto scan first, fallback to security scan
      let data;
      try {
        data = await api.fullCryptoScan(address, chain);
      } catch {
        data = await api.securityScan(address, chain);
      }
      setResult(data);
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Scan failed. Try again.');
    } finally {
      setScanning(false);
    }
  };

  const exportCard = useCallback(async () => {
    if (!cardRef.current) return;
    setGenerating(true);
    try {
      const dataUrl = await toPng(cardRef.current, { pixelRatio: 2, backgroundColor: '#0a0a0f' });
      const link = document.createElement('a');
      link.download = `rmi-scan-${truncate(address)}.png`;
      link.href = dataUrl;
      link.click();
    } catch (e) {
      console.error('Export failed:', e);
    } finally {
      setGenerating(false);
    }
  }, [address]);

  const copyResult = () => {
    if (!result) return;
    const text = `🔍 RMI Scan Result\nToken: ${truncate(result.token_address)}\nRisk: ${result.risk_score}/100 (${getRiskLabel(result.risk_score)})\nHoneypot: ${result.honeypot_detected ? 'YES 🍯' : 'No'}\nMint: ${result.mint_authority_renounced ? 'Renounced ✅' : 'NOT Renounced ❌'}\nLP Locked: ${result.liquidity_pools.some(p => p.lp_locked_percentage > 80) ? 'Yes ✅' : 'No ❌'}\n\nScan by @rugmunchbot`;
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const riskColors = result ? getRiskColor(result.risk_score) : getRiskColor(0);
  const RiskIcon = riskColors.icon;

  return (
    <div className={`${embedded ? '' : 'min-h-screen bg-[#0a0a0f] text-slate-200 py-8'}`}>
      <div className={`${embedded ? '' : 'max-w-3xl mx-auto px-4 sm:px-6'}`}>
        {!embedded && (
          <div className="mb-6">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 rounded bg-purple-950/60 border border-purple-800/40 flex items-center justify-center">
                <Shield className="w-5 h-5 text-purple-400" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white tracking-tight">Token Scanner</h1>
                <p className="text-xs text-purple-400/70 font-mono tracking-wider uppercase">Same engine as @rugmunchbot</p>
              </div>
            </div>
          </div>
        )}

        {/* INPUT */}
        <div className="bg-slate-900/60 border border-slate-800/60 rounded-xl p-4 mb-4">
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
              <input
                type="text"
                value={address}
                onChange={e => setAddress(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleScan()}
                placeholder="Paste token contract address..."
                className="w-full bg-slate-800/50 border border-slate-700/50 rounded-lg pl-10 pr-4 py-3 text-sm text-white placeholder-slate-600 focus:outline-none focus:border-purple-600/50"
              />
            </div>
            <div className="flex gap-2">
              <select
                value={chain}
                onChange={e => setChain(e.target.value)}
                className="bg-slate-800/50 border border-slate-700/50 rounded-lg px-3 py-3 text-sm text-slate-300 focus:outline-none focus:border-purple-600/50"
              >
                {chains.map(c => <option key={c.id} value={c.id}>{c.icon} {c.name}</option>)}
              </select>
              <button
                onClick={handleScan}
                disabled={scanning}
                className="px-6 py-3 bg-purple-600 hover:bg-purple-500 disabled:opacity-50 text-white text-sm font-bold rounded-lg transition-all flex items-center gap-2 whitespace-nowrap"
              >
                {scanning ? <Loader2 className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4" />}
                {scanning ? 'Scanning...' : 'Scan'}
              </button>
            </div>
          </div>
          {error && <p className="text-xs text-red-400 mt-2 flex items-center gap-1"><AlertTriangle className="w-3 h-3" /> {error}</p>}
        </div>

        {/* RESULT CARD */}
        {result && (
          <div className="space-y-4">
            {/* Main Scan Card */}
            <div ref={cardRef} className={`bg-slate-900/60 border ${riskColors.border} rounded-xl overflow-hidden`}>
              {/* Header */}
              <div className={`bg-gradient-to-r ${riskColors.gradient} p-5`}>
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded bg-white/20 flex items-center justify-center">
                      <span className="text-white font-bold text-xs">RMI</span>
                    </div>
                    <span className="text-white/90 text-xs font-bold tracking-wider">SECURITY SCAN</span>
                  </div>
                  <span className="text-white/60 text-[10px]">{new Date(result.analyzed_at).toLocaleString()}</span>
                </div>

                <div className="flex items-center gap-4">
                  <div className={`w-20 h-20 rounded-full ${riskColors.bg} border-4 ${riskColors.border} flex items-center justify-center`}>
                    <span className={`text-3xl font-bold ${riskColors.text}`}>{result.risk_score}</span>
                  </div>
                  <div>
                    <div className={`text-xl font-bold ${riskColors.text}`}>{getRiskLabel(result.risk_score)}</div>
                    <div className="text-white/70 text-xs">Risk Score / 100</div>
                    <div className="text-white/50 text-[10px] mt-0.5">{truncate(result.token_address)} • {result.chain.toUpperCase()}</div>
                  </div>
                </div>
              </div>

              {/* Body */}
              <div className="p-5 space-y-4">
                {/* Quick Stats */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  <StatBox
                    icon={result.honeypot_detected ? Flame : Shield}
                    label="Honeypot"
                    value={result.honeypot_detected ? 'YES' : 'No'}
                    danger={result.honeypot_detected}
                  />
                  <StatBox
                    icon={result.mint_authority_renounced ? Lock : Unlock}
                    label="Mint Auth"
                    value={result.mint_authority_renounced ? 'Renounced' : 'Active'}
                    danger={!result.mint_authority_renounced}
                  />
                  <StatBox
                    icon={Droplets}
                    label="Liquidity"
                    value={`$${(result.total_liquidity_usd / 1000).toFixed(1)}K`}
                    danger={result.total_liquidity_usd < 10000}
                  />
                  <StatBox
                    icon={Users}
                    label="Holders"
                    value={result.holder_concentration?.total_holders?.toLocaleString() || 'N/A'}
                    danger={false}
                  />
                </div>

                {/* LP Status */}
                <div className="bg-slate-800/40 rounded-lg p-3">
                  <div className="text-xs font-bold text-white mb-2">Liquidity Pools</div>
                  {result.liquidity_pools?.map((pool, i) => (
                    <div key={i} className="flex items-center justify-between text-xs mb-1 last:mb-0">
                      <span className="text-slate-400">{pool.dex} — {pool.pair}</span>
                      <div className="flex items-center gap-3">
                        <span className="text-slate-300">${pool.liquidity_usd.toLocaleString()}</span>
                        <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${pool.lp_locked_percentage > 80 ? 'bg-emerald-950/40 text-emerald-400' : 'bg-red-950/40 text-red-400'}`}>
                          {pool.lp_locked_percentage > 80 ? 'Locked' : 'Unlocked'}
                        </span>
                      </div>
                    </div>
                  )) || <span className="text-xs text-slate-500">No liquidity data available</span>}
                </div>

                {/* Taxes */}
                {result.tax_info && (
                  <div className="bg-slate-800/40 rounded-lg p-3">
                    <div className="text-xs font-bold text-white mb-2">Taxes</div>
                    <div className="grid grid-cols-3 gap-2 text-center">
                      <div>
                        <div className="text-[10px] text-slate-500">Buy</div>
                        <div className={`text-sm font-bold ${result.tax_info.buy_tax > 10 ? 'text-red-400' : 'text-emerald-400'}`}>{result.tax_info.buy_tax}%</div>
                      </div>
                      <div>
                        <div className="text-[10px] text-slate-500">Sell</div>
                        <div className={`text-sm font-bold ${result.tax_info.sell_tax > 10 ? 'text-red-400' : 'text-emerald-400'}`}>{result.tax_info.sell_tax}%</div>
                      </div>
                      <div>
                        <div className="text-[10px] text-slate-500">Transfer</div>
                        <div className={`text-sm font-bold ${result.tax_info.transfer_tax > 5 ? 'text-red-400' : 'text-emerald-400'}`}>{result.tax_info.transfer_tax}%</div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Holder Concentration */}
                {result.holder_concentration && (
                  <div className="bg-slate-800/40 rounded-lg p-3">
                    <div className="text-xs font-bold text-white mb-2">Holder Concentration</div>
                    <div className="space-y-2">
                      <div>
                        <div className="flex justify-between text-[10px] text-slate-400 mb-1">
                          <span>Top 10 Holders</span>
                          <span>{result.holder_concentration.top_10_percentage}%</span>
                        </div>
                        <div className="h-1.5 bg-slate-700 rounded-full overflow-hidden">
                          <div className={`h-full rounded-full ${result.holder_concentration.top_10_percentage > 50 ? 'bg-red-500' : 'bg-emerald-500'}`} style={{ width: `${Math.min(result.holder_concentration.top_10_percentage, 100)}%` }} />
                        </div>
                      </div>
                      <div>
                        <div className="flex justify-between text-[10px] text-slate-400 mb-1">
                          <span>Top 50 Holders</span>
                          <span>{result.holder_concentration.top_50_percentage}%</span>
                        </div>
                        <div className="h-1.5 bg-slate-700 rounded-full overflow-hidden">
                          <div className={`h-full rounded-full ${result.holder_concentration.top_50_percentage > 80 ? 'bg-red-500' : 'bg-emerald-500'}`} style={{ width: `${Math.min(result.holder_concentration.top_50_percentage, 100)}%` }} />
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Red/Green Flags */}
                <div className="grid sm:grid-cols-2 gap-3">
                  {result.red_flags?.length > 0 && (
                    <div className="bg-red-950/20 border border-red-900/30 rounded-lg p-3">
                      <div className="text-xs font-bold text-red-400 mb-2 flex items-center gap-1.5">
                        <Flame className="w-3.5 h-3.5" /> Red Flags
                      </div>
                      <div className="space-y-1">
                        {result.red_flags.map((flag, i) => (
                          <div key={i} className="text-[11px] text-red-300/80 flex items-start gap-1.5">
                            <span className="text-red-500 mt-0.5">•</span> {flag}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  {result.green_flags?.length > 0 && (
                    <div className="bg-emerald-950/20 border border-emerald-900/30 rounded-lg p-3">
                      <div className="text-xs font-bold text-emerald-400 mb-2 flex items-center gap-1.5">
                        <CheckCircle2 className="w-3.5 h-3.5" /> Green Flags
                      </div>
                      <div className="space-y-1">
                        {result.green_flags.map((flag, i) => (
                          <div key={i} className="text-[11px] text-emerald-300/80 flex items-start gap-1.5">
                            <span className="text-emerald-500 mt-0.5">•</span> {flag}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* AI Consensus */}
                {result.ai_consensus && (
                  <div className="bg-purple-950/20 border border-purple-900/30 rounded-lg p-3">
                    <div className="text-xs font-bold text-purple-400 mb-1 flex items-center gap-1.5">
                      <Zap className="w-3.5 h-3.5" /> AI Consensus
                    </div>
                    <p className="text-[11px] text-purple-300/80 leading-relaxed">{result.ai_consensus}</p>
                  </div>
                )}
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-2">
              <button onClick={copyResult} className="flex-1 py-2.5 bg-slate-800/50 border border-slate-700/50 rounded-lg text-xs font-medium text-slate-300 hover:text-white hover:bg-slate-800 transition-all flex items-center justify-center gap-2">
                {copied ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                {copied ? 'Copied!' : 'Copy Result'}
              </button>
              <button onClick={exportCard} disabled={generating} className="flex-1 py-2.5 bg-slate-800/50 border border-slate-700/50 rounded-lg text-xs font-medium text-slate-300 hover:text-white hover:bg-slate-800 transition-all flex items-center justify-center gap-2">
                <Download className="w-3.5 h-3.5" />
                {generating ? 'Generating...' : 'Save Card'}
              </button>
              <button onClick={() => { setResult(null); setAddress(''); }} className="flex-1 py-2.5 bg-slate-800/50 border border-slate-700/50 rounded-lg text-xs font-medium text-slate-300 hover:text-white hover:bg-slate-800 transition-all flex items-center justify-center gap-2">
                <RefreshCw className="w-3.5 h-3.5" /> New Scan
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// STAT BOX
// ═══════════════════════════════════════════════════════════

function StatBox({ icon: Icon, label, value, danger }: { icon: any; label: string; value: string; danger: boolean }) {
  return (
    <div className={`bg-slate-800/40 rounded-lg p-3 text-center border ${danger ? 'border-red-900/20' : 'border-slate-700/30'}`}>
      <Icon className={`w-4 h-4 mx-auto mb-1 ${danger ? 'text-red-400' : 'text-emerald-400'}`} />
      <div className={`text-xs font-bold ${danger ? 'text-red-400' : 'text-white'}`}>{value}</div>
      <div className="text-[10px] text-slate-500">{label}</div>
    </div>
  );
}
