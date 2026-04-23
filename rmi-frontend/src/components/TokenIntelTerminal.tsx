/**
 * Token Intel Terminal
 * ====================
 * Single-search token due diligence. Pulls from contract audit, GMGN,
 * Helius, Nansen, and AI consensus — tier-gated.
 *
 * FREE  → Contract audit + basic risk score
 * BASIC → + GMGN token security + top holders
 * PRO   → + Helius sniper detect + AI consensus + crossref intel
 * ELITE → + Nansen smart money + full wallet graph
 */
import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import {
  Search, Shield, AlertTriangle, Check, Loader2, Zap,
  Coins, Users, Crosshair, Brain, TrendingUp, Lock,
  FileText, Activity
} from 'lucide-react';
import { api } from '../services/api';
import { useAppStore } from '../store/appStore';
import TierGate from './TierGate';

interface ScanResult {
  address: string;
  chain: string;
  audit?: any;
  gmgnSecurity?: any;
  gmgnHolders?: any;
  sniperDetect?: any;
  crossRef?: any;
  narrative?: any;
  error?: string;
}

const CHAINS = [
  { id: 'solana', label: 'Solana' },
  { id: 'ethereum', label: 'Ethereum' },
  { id: 'base', label: 'Base' },
  { id: 'bsc', label: 'BSC' },
];

export default function TokenIntelTerminal() {
  const [address, setAddress] = useState('');
  const [chain, setChain] = useState('solana');
  const [result, setResult] = useState<ScanResult | null>(null);
  const user = useAppStore((state) => state.user);
  const tier = user?.tier || 'FREE';

  const scan = useMutation({
    mutationFn: async (params: { address: string; chain: string }) => {
      const res: ScanResult = { address: params.address, chain: params.chain };

      // FREE: Contract audit
      try {
        res.audit = await api.auditContract(params.address, params.chain);
      } catch (e: any) {
        res.audit = { error: e.message };
      }

      // BASIC+: GMGN data
      if (['BASIC', 'PRO', 'ELITE', 'ENTERPRISE'].includes(tier)) {
        try {
          res.gmgnSecurity = await api.getGMGNTokenSecurity(params.address, params.chain);
        } catch (e: any) {
          res.gmgnSecurity = { error: e.message };
        }
        try {
          res.gmgnHolders = await api.getGMGNTopHolders(params.address, params.chain);
        } catch (e: any) {
          res.gmgnHolders = { error: e.message };
        }
      }

      // PRO+: Helius + Intel
      if (['PRO', 'ELITE', 'ENTERPRISE'].includes(tier)) {
        try {
          res.sniperDetect = await api.getHeliusSniperDetect(params.address, params.chain);
        } catch (e: any) {
          res.sniperDetect = { error: e.message };
        }
        try {
          res.crossRef = await api.getCrossRefIntel(params.address);
        } catch (e: any) {
          res.crossRef = { error: e.message };
        }
        try {
          res.narrative = await api.getNarrativeIntel(params.address);
        } catch (e: any) {
          res.narrative = { error: e.message };
        }
      }

      return res;
    },
    onSuccess: (data) => setResult(data),
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!address.trim()) return;
    setResult(null);
    scan.mutate({ address: address.trim(), chain });
  };

  const getRiskColor = (score?: number) => {
    if (score === undefined) return 'text-gray-400';
    if (score <= 30) return 'text-emerald-400';
    if (score <= 60) return 'text-amber-400';
    return 'text-rose-400';
  };

  const getRiskBg = (score?: number) => {
    if (score === undefined) return 'bg-gray-500';
    if (score <= 30) return 'bg-emerald-500';
    if (score <= 60) return 'bg-amber-500';
    return 'bg-rose-500';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <Brain className="w-6 h-6 text-purple-400" />
          Token Intel Terminal
        </h1>
        <p className="text-gray-400">
          Multi-source due diligence. One search, every angle.
        </p>
      </div>

      {/* Search */}
      <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
          <input
            type="text"
            value={address}
            onChange={(e) => setAddress(e.target.value)}
            placeholder="Paste token contract address..."
            className="w-full pl-10 pr-4 py-3 bg-slate-900 border border-slate-700 rounded-lg text-white placeholder-gray-500 focus:border-purple-500 focus:outline-none transition-colors"
          />
        </div>
        <select
          value={chain}
          onChange={(e) => setChain(e.target.value)}
          className="px-4 py-3 bg-slate-900 border border-slate-700 rounded-lg text-white focus:border-purple-500 focus:outline-none"
        >
          {CHAINS.map((c) => (
            <option key={c.id} value={c.id}>{c.label}</option>
          ))}
        </select>
        <button
          type="submit"
          disabled={scan.isPending || !address.trim()}
          className="px-6 py-3 bg-purple-600 hover:bg-purple-700 disabled:opacity-40 text-white rounded-lg font-medium flex items-center justify-center gap-2 transition-colors"
        >
          {scan.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4" />}
          {scan.isPending ? 'Scanning...' : 'Scan'}
        </button>
      </form>

      {/* Results */}
      {result && (
        <div className="space-y-4">
          {/* Risk Score Card */}
          <div className="grid md:grid-cols-3 gap-4">
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
              <div className="flex items-center gap-2 mb-3">
                <Shield className="w-4 h-4 text-purple-400" />
                <span className="text-sm font-medium text-gray-300">Contract Audit</span>
              </div>
              {result.audit?.risk_score !== undefined ? (
                <div>
                  <div className="flex items-end gap-2 mb-2">
                    <span className={`text-3xl font-bold ${getRiskColor(result.audit.risk_score)}`}>
                      {result.audit.risk_score}
                    </span>
                    <span className="text-gray-500 text-sm mb-1">/100</span>
                  </div>
                  <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden mb-2">
                    <div
                      className={`h-full rounded-full ${getRiskBg(result.audit.risk_score)}`}
                      style={{ width: `${result.audit.risk_score}%` }}
                    />
                  </div>
                  <p className="text-xs text-gray-400">{result.audit.analysis || 'Audit complete'}</p>
                </div>
              ) : (
                <p className="text-sm text-gray-500">No audit data</p>
              )}
            </div>

            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
              <div className="flex items-center gap-2 mb-3">
                <Activity className="w-4 h-4 text-blue-400" />
                <span className="text-sm font-medium text-gray-300">Contract Safety</span>
              </div>
              {result.audit?.safety_checks ? (
                <div className="space-y-1.5">
                  {result.audit.safety_checks.map((check: any, i: number) => (
                    <div key={i} className="flex items-center gap-2 text-xs">
                      {check.pass ? (
                        <Check className="w-3.5 h-3.5 text-emerald-400" />
                      ) : (
                        <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />
                      )}
                      <span className={check.pass ? 'text-gray-300' : 'text-rose-300'}>
                        {check.name}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-gray-500">No safety checks</p>
              )}
            </div>

            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
              <div className="flex items-center gap-2 mb-3">
                <FileText className="w-4 h-4 text-amber-400" />
                <span className="text-sm font-medium text-gray-300">Quick Intel</span>
              </div>
              <div className="space-y-2 text-xs text-gray-400">
                <p><span className="text-gray-500">Chain:</span> {result.chain}</p>
                <p><span className="text-gray-500">Address:</span> {result.address.slice(0, 8)}...{result.address.slice(-6)}</p>
                <p><span className="text-gray-500">Tier:</span> <span className="text-purple-400">{tier}</span></p>
              </div>
            </div>
          </div>

          {/* GMGN Security — BASIC+ */}
          <TierGate
            requiredTier="BASIC"
            title="GMGN Token Security"
            description="Deep token security analysis including liquidity, holder concentration, and contract verification."
          >
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
              <div className="flex items-center gap-2 mb-4">
                <Coins className="w-4 h-4 text-emerald-400" />
                <span className="text-sm font-medium text-gray-300">GMGN Token Security</span>
              </div>
              {result.gmgnSecurity?.error ? (
                <p className="text-sm text-gray-500">{result.gmgnSecurity.error}</p>
              ) : result.gmgnSecurity ? (
                <pre className="text-xs text-emerald-300 font-mono bg-slate-950 rounded-lg p-3 overflow-x-auto">
                  {JSON.stringify(result.gmgnSecurity, null, 2)}
                </pre>
              ) : (
                <p className="text-sm text-gray-500">No GMGN data</p>
              )}
            </div>
          </TierGate>

          {/* Top Holders — BASIC+ */}
          <TierGate
            requiredTier="BASIC"
            title="Top Holders Analysis"
            description="See who owns the most supply and whether it's concentrated or distributed."
          >
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
              <div className="flex items-center gap-2 mb-4">
                <Users className="w-4 h-4 text-blue-400" />
                <span className="text-sm font-medium text-gray-300">Top Holders</span>
              </div>
              {result.gmgnHolders?.error ? (
                <p className="text-sm text-gray-500">{result.gmgnHolders.error}</p>
              ) : result.gmgnHolders ? (
                <pre className="text-xs text-blue-300 font-mono bg-slate-950 rounded-lg p-3 overflow-x-auto">
                  {JSON.stringify(result.gmgnHolders, null, 2)}
                </pre>
              ) : (
                <p className="text-sm text-gray-500">No holder data</p>
              )}
            </div>
          </TierGate>

          {/* Sniper Detection — PRO+ */}
          <TierGate
            requiredTier="PRO"
            title="Sniper & Bot Detection"
            description="Helius-powered sniper detection reveals if bots front-ran the launch."
          >
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
              <div className="flex items-center gap-2 mb-4">
                <Crosshair className="w-4 h-4 text-rose-400" />
                <span className="text-sm font-medium text-gray-300">Sniper Detection</span>
              </div>
              {result.sniperDetect?.error ? (
                <p className="text-sm text-gray-500">{result.sniperDetect.error}</p>
              ) : result.sniperDetect ? (
                <pre className="text-xs text-rose-300 font-mono bg-slate-950 rounded-lg p-3 overflow-x-auto">
                  {JSON.stringify(result.sniperDetect, null, 2)}
                </pre>
              ) : (
                <p className="text-sm text-gray-500">No sniper data</p>
              )}
            </div>
          </TierGate>

          {/* Cross-Ref Intel — PRO+ */}
          <TierGate
            requiredTier="PRO"
            title="Cross-Reference Intelligence"
            description="AI-powered cross-reference across multiple data sources and investigations."
          >
            <div className="grid md:grid-cols-2 gap-4">
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
                <div className="flex items-center gap-2 mb-3">
                  <Brain className="w-4 h-4 text-purple-400" />
                  <span className="text-sm font-medium text-gray-300">Cross-Ref Intel</span>
                </div>
                {result.crossRef?.error ? (
                  <p className="text-sm text-gray-500">{result.crossRef.error}</p>
                ) : result.crossRef ? (
                  <pre className="text-xs text-purple-300 font-mono bg-slate-950 rounded-lg p-3 overflow-x-auto">
                    {JSON.stringify(result.crossRef, null, 2)}
                  </pre>
                ) : (
                  <p className="text-sm text-gray-500">No crossref data</p>
                )}
              </div>

              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
                <div className="flex items-center gap-2 mb-3">
                  <TrendingUp className="w-4 h-4 text-amber-400" />
                  <span className="text-sm font-medium text-gray-300">Narrative Intel</span>
                </div>
                {result.narrative?.error ? (
                  <p className="text-sm text-gray-500">{result.narrative.error}</p>
                ) : result.narrative ? (
                  <pre className="text-xs text-amber-300 font-mono bg-slate-950 rounded-lg p-3 overflow-x-auto">
                    {JSON.stringify(result.narrative, null, 2)}
                  </pre>
                ) : (
                  <p className="text-sm text-gray-500">No narrative data</p>
                )}
              </div>
            </div>
          </TierGate>
        </div>
      )}
    </div>
  );
}
