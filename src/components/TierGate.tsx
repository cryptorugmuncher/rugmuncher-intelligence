/**
 * TierGate — Premium Feature Guard
 * Shows locked state for features above user's tier.
 */
import { Lock, Zap } from 'lucide-react';
import { useAppStore } from '../store/appStore';

const TIER_RANK: Record<string, number> = {
  FREE: 0,
  BASIC: 1,
  PRO: 2,
  ELITE: 3,
  ENTERPRISE: 4,
};

interface TierGateProps {
  requiredTier: 'BASIC' | 'PRO' | 'ELITE' | 'ENTERPRISE';
  children: React.ReactNode;
  fallback?: React.ReactNode;
  title?: string;
  description?: string;
}

export default function TierGate({
  requiredTier,
  children,
  fallback,
  title,
  description,
}: TierGateProps) {
  const user = useAppStore((state) => state.user);
  const currentRank = TIER_RANK[user?.tier || 'FREE'];
  const requiredRank = TIER_RANK[requiredTier];
  const hasAccess = currentRank >= requiredRank;

  if (hasAccess) return <>{children}</>;

  if (fallback) return <>{fallback}</>;

  return (
    <div className="relative rounded-xl border border-amber-500/20 bg-amber-500/5 p-6">
      <div className="absolute inset-0 flex flex-col items-center justify-center text-center p-6">
        <div className="w-12 h-12 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center mb-3">
          <Lock className="w-6 h-6 text-amber-400" />
        </div>
        <h4 className="text-sm font-semibold text-amber-300 mb-1">
          {title || `${requiredTier} Feature`}
        </h4>
        <p className="text-xs text-amber-400/70 max-w-xs mb-3">
          {description || `Upgrade to ${requiredTier} to unlock this feature.`}
        </p>
        <button
          onClick={() => useAppStore.getState().setCurrentPage('pricing')}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-300 text-xs font-medium hover:bg-amber-500/20 transition-colors"
        >
          <Zap className="w-3 h-3" />
          Upgrade
        </button>
      </div>
      <div className="blur-sm opacity-30 pointer-events-none select-none min-h-[120px]">
        {children}
      </div>
    </div>
  );
}
