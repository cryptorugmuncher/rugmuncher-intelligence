/**
 * $CRM V2 Token Transparency Tracker
 * ===================================
 * Public-facing token transparency & treasury monitoring.
 * Tracks: supply, holders, treasury, buybacks, burns, vesting.
 */
import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import {
  Shield,
  Eye,
  Lock,
  TrendingUp,
  Users,
  Flame,
  Wallet,
  Clock,
  ChevronRight,
  Activity,
  Globe,
  AlertTriangle,
  CheckCircle2,
  BarChart3,
  Landmark,
  Receipt,
} from 'lucide-react';

// ═══════════════════════════════════════════════════════════════════
// MOCK DATA — Replace with live on-chain calls when $CRM V2 deploys
// ═══════════════════════════════════════════════════════════════════
const MOCK_TREASURY = {
  total_usd: 0,
  sol: 0,
  usdc: 0,
  crm: 0,
  last_update: null,
};

const MOCK_SUPPLY = {
  max: 1_000_000_000,
  circulating: 0,
  burned: 0,
  locked: 0,
  staked: 0,
};

const MOCK_HOLDERS = {
  count: 0,
  top_10_pct: 0,
  top_50_pct: 0,
  retail_pct: 0,
};

const MOCK_VESTING = [
  { name: 'Team', allocation: 15, released: 0, locked_until: 'TBD', color: 'bg-red-500' },
  { name: 'Treasury', allocation: 20, released: 0, locked_until: 'TBD', color: 'bg-blue-500' },
  { name: 'Community', allocation: 25, released: 0, locked_until: 'TBD', color: 'bg-green-500' },
  { name: 'Liquidity', allocation: 20, released: 0, locked_until: 'TBD', color: 'bg-purple-500' },
  { name: 'Airdrop', allocation: 15, released: 0, locked_until: 'TBD', color: 'bg-yellow-500' },
];

const MOCK_TRANSACTIONS: any[] = [];

export default function CRMv2Transparency() {
  const [showOverlay, setShowOverlay] = useState(true);

  const { data: trending } = useQuery({
    queryKey: ['crm-trending'],
    queryFn: () => api.cryptoUnifiedTrending('solana'),
    enabled: !showOverlay,
  });

  return (
    <div className="relative min-h-screen">
      {/* ═══════════════ COMING SOON OVERLAY ═══════════════ */}
      {showOverlay && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm">
          <div className="text-center space-y-6 p-8 max-w-lg mx-auto">
            <div className="w-20 h-20 mx-auto rounded-full bg-gradient-to-br from-red-600 to-orange-600 flex items-center justify-center animate-pulse">
              <Shield className="w-10 h-10 text-white" />
            </div>
            <h1 className="text-4xl font-bold text-white">
              $CRM <span className="text-red-500">V2</span>
            </h1>
            <p className="text-xl text-gray-300">
              Transparency Tracker
            </p>
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-red-500/20 border border-red-500/50 rounded-full text-red-400 text-sm font-medium">
              <Clock className="w-4 h-4" />
              Coming Soon
            </div>
            <p className="text-gray-500 text-sm">
              Real-time on-chain transparency for the $CRM V2 ecosystem.
              <br />
              Treasury · Supply · Vesting · Burns · Buybacks
            </p>
            <button
              onClick={() => setShowOverlay(false)}
              className="text-gray-500 hover:text-white text-sm underline transition-colors"
            >
              Preview the dashboard
            </button>
          </div>
        </div>
      )}

      {/* ═══════════════ MAIN DASHBOARD ═══════════════ */}
      <div className="p-6 max-w-[1400px] mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-red-600 to-orange-600 flex items-center justify-center">
              <Shield className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">$CRM V2 Transparency</h1>
              <p className="text-gray-400 text-sm">On-chain treasury & supply tracker</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="px-3 py-1 bg-yellow-500/20 text-yellow-400 text-xs rounded-full border border-yellow-500/50 font-medium">
              PRE-LAUNCH
            </span>
            <button
              onClick={() => setShowOverlay(true)}
              className="p-2 hover:bg-crypto-card rounded-lg transition-colors"
              title="Show Coming Soon"
            >
              <Eye className="w-5 h-5 text-gray-400" />
            </button>
          </div>
        </div>

        {/* Key Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard icon={Wallet} label="Treasury" value="$0" sub="Awaiting V2 launch" color="blue" />
          <StatCard icon={Users} label="Holders" value="0" sub="Pre-launch" color="green" />
          <StatCard icon={Flame} label="Burned" value="0" sub="0% of supply" color="orange" />
          <StatCard icon={TrendingUp} label="Market Cap" value="$0" sub="Awaiting launch" color="purple" />
        </div>

        {/* Supply Breakdown */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="crypto-card lg:col-span-2">
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-neon-blue" />
              Supply Breakdown
            </h3>
            <div className="space-y-4">
              <SupplyBar label="Circulating" value={MOCK_SUPPLY.circulating} max={MOCK_SUPPLY.max} color="bg-green-500" />
              <SupplyBar label="Burned" value={MOCK_SUPPLY.burned} max={MOCK_SUPPLY.max} color="bg-orange-500" />
              <SupplyBar label="Locked / Vesting" value={MOCK_SUPPLY.locked} max={MOCK_SUPPLY.max} color="bg-blue-500" />
              <SupplyBar label="Staked" value={MOCK_SUPPLY.staked} max={MOCK_SUPPLY.max} color="bg-purple-500" />
            </div>
            <div className="mt-4 pt-4 border-t border-crypto-border grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-500">Max Supply</span>
                <p className="text-white font-mono">{MOCK_SUPPLY.max.toLocaleString()}</p>
              </div>
              <div>
                <span className="text-gray-500">Remaining</span>
                <p className="text-white font-mono">{(MOCK_SUPPLY.max - MOCK_SUPPLY.circulating).toLocaleString()}</p>
              </div>
            </div>
          </div>

          {/* Holder Distribution */}
          <div className="crypto-card">
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <Users className="w-5 h-5 text-neon-green" />
              Holder Distribution
            </h3>
            <div className="space-y-4">
              <DoughnutSlice label="Top 10 Wallets" value={MOCK_HOLDERS.top_10_pct} color="text-red-400" />
              <DoughnutSlice label="Top 50 Wallets" value={MOCK_HOLDERS.top_50_pct} color="text-yellow-400" />
              <DoughnutSlice label="Retail (< 1%)" value={MOCK_HOLDERS.retail_pct} color="text-green-400" />
            </div>
            <div className="mt-4 pt-4 border-t border-crypto-border">
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Total Holders</span>
                <span className="text-white font-mono">{MOCK_HOLDERS.count.toLocaleString()}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Vesting Schedule */}
        <div className="crypto-card">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <Lock className="w-5 h-5 text-neon-yellow" />
            Vesting Schedule
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            {MOCK_VESTING.map((v) => (
              <div key={v.name} className="bg-crypto-dark rounded-lg p-4 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-white text-sm font-medium">{v.name}</span>
                  <span className="text-xs text-gray-500">{v.allocation}%</span>
                </div>
                <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                  <div className={`h-full ${v.color} rounded-full`} style={{ width: `${(v.released / v.allocation) * 100}%` }} />
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-gray-500">Released</span>
                  <span className="text-white">{v.released}%</span>
                </div>
                <div className="text-xs text-gray-600">
                  <Clock className="w-3 h-3 inline mr-1" />
                  {v.locked_until}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Treasury Breakdown */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="crypto-card">
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <Landmark className="w-5 h-5 text-neon-purple" />
              Treasury Assets
            </h3>
            <div className="space-y-3">
              <TreasuryRow asset="SOL" balance={MOCK_TREASURY.sol} usd={0} icon="◎" />
              <TreasuryRow asset="USDC" balance={MOCK_TREASURY.usdc} usd={0} icon="$" />
              <TreasuryRow asset="CRM" balance={MOCK_TREASURY.crm} usd={0} icon="₡" />
            </div>
            <div className="mt-4 pt-4 border-t border-crypto-border flex justify-between items-center">
              <span className="text-gray-500 text-sm">Total Value</span>
              <span className="text-xl font-bold text-white">${MOCK_TREASURY.total_usd.toLocaleString()}</span>
            </div>
          </div>

          {/* Recent Transactions */}
          <div className="crypto-card">
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <Receipt className="w-5 h-5 text-neon-cyan" />
              Recent Treasury Txns
            </h3>
            {MOCK_TRANSACTIONS.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <Clock className="w-8 h-8 mx-auto mb-2" />
                <p>No transactions yet — V2 not launched</p>
              </div>
            ) : (
              <div className="space-y-2">
                {MOCK_TRANSACTIONS.map((tx: any, i: number) => (
                  <TxnRow key={i} {...tx} />
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Transparency Checks */}
        <div className="crypto-card">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <CheckCircle2 className="w-5 h-5 text-neon-green" />
            Transparency Checks
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <CheckItem label="Contract Verified" status="pending" />
            <CheckItem label="Liquidity Locked" status="pending" />
            <CheckItem label="Team Tokens Vested" status="pending" />
            <CheckItem label="Treasury Multi-sig" status="pending" />
            <CheckItem label="Real-time API" status="pending" />
            <CheckItem label="Open Source" status="pending" />
          </div>
        </div>

        {/* Footer */}
        <div className="text-center text-gray-600 text-sm py-4">
          <Globe className="w-4 h-4 inline mr-1" />
          Data sourced directly from Solana mainnet — no intermediaries.
          <br />
          Last update: {MOCK_TREASURY.last_update || 'Awaiting V2 deployment'}
        </div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
// SUB-COMPONENTS
// ═══════════════════════════════════════════════════════════════════

function StatCard({ icon: Icon, label, value, sub, color }: any) {
  const colors: Record<string, string> = {
    blue: 'text-blue-400 bg-blue-500/10',
    green: 'text-green-400 bg-green-500/10',
    orange: 'text-orange-400 bg-orange-500/10',
    purple: 'text-purple-400 bg-purple-500/10',
  };
  return (
    <div className="crypto-card">
      <div className="flex items-center gap-3 mb-2">
        <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${colors[color]}`}>
          <Icon className="w-5 h-5" />
        </div>
        <span className="text-gray-400 text-sm">{label}</span>
      </div>
      <p className="text-2xl font-bold text-white">{value}</p>
      <p className="text-xs text-gray-500 mt-1">{sub}</p>
    </div>
  );
}

function SupplyBar({ label, value, max, color }: { label: string; value: number; max: number; color: string }) {
  const pct = max > 0 ? (value / max) * 100 : 0;
  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span className="text-gray-400">{label}</span>
        <span className="text-white font-mono">{value.toLocaleString()} ({pct.toFixed(1)}%)</span>
      </div>
      <div className="h-3 bg-gray-800 rounded-full overflow-hidden">
        <div className={`h-full ${color} rounded-full transition-all`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

function DoughnutSlice({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-gray-400 text-sm">{label}</span>
      <div className="flex items-center gap-2">
        <div className="w-32 h-2 bg-gray-800 rounded-full overflow-hidden">
          <div className={`h-full ${color.replace('text-', 'bg-')} rounded-full`} style={{ width: `${value}%` }} />
        </div>
        <span className={`text-sm font-mono ${color}`}>{value}%</span>
      </div>
    </div>
  );
}

function TreasuryRow({ asset, balance, usd, icon }: { asset: string; balance: number; usd: number; icon: string }) {
  return (
    <div className="flex items-center justify-between p-3 bg-crypto-dark rounded-lg">
      <div className="flex items-center gap-3">
        <span className="text-xl">{icon}</span>
        <span className="text-white font-medium">{asset}</span>
      </div>
      <div className="text-right">
        <p className="text-white font-mono">{balance.toLocaleString()}</p>
        <p className="text-xs text-gray-500">${usd.toLocaleString()}</p>
      </div>
    </div>
  );
}

function TxnRow({ type, amount, asset, tx_hash, timestamp }: any) {
  const isIn = type === 'in';
  return (
    <div className="flex items-center justify-between p-3 bg-crypto-dark rounded-lg">
      <div className="flex items-center gap-3">
        <div className={`w-8 h-8 rounded-full flex items-center justify-center ${isIn ? 'bg-green-500/20' : 'bg-red-500/20'}`}>
          {isIn ? <TrendingUp className="w-4 h-4 text-green-400" /> : <Flame className="w-4 h-4 text-red-400" />}
        </div>
        <div>
          <p className="text-white text-sm">{isIn ? 'Inflow' : 'Outflow'} · {asset}</p>
          <p className="text-xs text-gray-500 font-mono">{tx_hash?.slice(0, 16)}...</p>
        </div>
      </div>
      <div className="text-right">
        <p className={`text-sm font-mono ${isIn ? 'text-green-400' : 'text-red-400'}`}>{isIn ? '+' : '-'}{amount}</p>
        <p className="text-xs text-gray-500">{timestamp}</p>
      </div>
    </div>
  );
}

function CheckItem({ label, status }: { label: string; status: 'ok' | 'warn' | 'pending' }) {
  const styles = {
    ok: { icon: CheckCircle2, color: 'text-green-400', bg: 'bg-green-500/10', border: 'border-green-500/30' },
    warn: { icon: AlertTriangle, color: 'text-yellow-400', bg: 'bg-yellow-500/10', border: 'border-yellow-500/30' },
    pending: { icon: Clock, color: 'text-gray-400', bg: 'bg-gray-500/10', border: 'border-gray-500/30' },
  };
  const s = styles[status];
  const Icon = s.icon;
  return (
    <div className={`flex items-center gap-3 p-3 rounded-lg border ${s.bg} ${s.border}`}>
      <Icon className={`w-5 h-5 ${s.color}`} />
      <span className="text-white text-sm">{label}</span>
      <span className={`ml-auto text-xs capitalize ${s.color}`}>{status}</span>
    </div>
  );
}
