/**
 * ScanCard — Social Share Card Generator
 * =======================================
 * Renders a beautiful shareable card from scan results.
 * Uses html-to-image for PNG export.
 */
import { useRef, useState, useCallback } from 'react';
import { toPng } from 'html-to-image';
import {
  Download,
  Share2,
  Shield,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Copy,
  Check,
} from 'lucide-react';

interface ScanCardProps {
  token: string;
  chain?: string;
  scanType?: string;
  riskScore?: number;
  riskLevel?: string;
  verdict?: string;
  redFlags?: string[];
  timestamp?: string;
  aiConsensus?: string;
}

function getRiskGradient(riskScore?: number) {
  if (riskScore === undefined) return 'from-gray-600 to-gray-700';
  if (riskScore >= 70) return 'from-red-600 to-red-800';
  if (riskScore >= 40) return 'from-orange-500 to-red-600';
  if (riskScore >= 20) return 'from-yellow-500 to-orange-500';
  return 'from-emerald-500 to-green-600';
}

function getRiskIcon(riskScore?: number) {
  if (riskScore === undefined) return Shield;
  if (riskScore >= 40) return AlertTriangle;
  return CheckCircle2;
}

function getRiskLabel(riskScore?: number) {
  if (riskScore === undefined) return 'UNKNOWN';
  if (riskScore >= 70) return 'CRITICAL';
  if (riskScore >= 40) return 'HIGH RISK';
  if (riskScore >= 20) return 'MEDIUM RISK';
  return 'SAFE';
}

function truncateToken(token: string, front = 6, back = 4) {
  if (token.length <= front + back + 3) return token;
  return `${token.slice(0, front)}...${token.slice(-back)}`;
}

export default function ScanCard({
  token,
  chain = 'SOL',
  scanType = 'SECURITY SCAN',
  riskScore,
  riskLevel,
  verdict,
  redFlags = [],
  timestamp = new Date().toISOString(),
  aiConsensus,
}: ScanCardProps) {
  const cardRef = useRef<HTMLDivElement>(null);
  const [generating, setGenerating] = useState(false);
  const [copied, setCopied] = useState(false);

  const exportCard = useCallback(async () => {
    if (!cardRef.current) return;
    setGenerating(true);
    try {
      const dataUrl = await toPng(cardRef.current, {
        pixelRatio: 2,
        backgroundColor: '#0a0a0f',
      });
      const link = document.createElement('a');
      link.download = `rugmunch-scan-${token.slice(0, 8)}.png`;
      link.href = dataUrl;
      link.click();
    } catch (e) {
      console.error('Failed to generate card:', e);
    } finally {
      setGenerating(false);
    }
  }, [token]);

  const shareCard = useCallback(async () => {
    if (!cardRef.current) return;
    setGenerating(true);
    try {
      const dataUrl = await toPng(cardRef.current, {
        pixelRatio: 2,
        backgroundColor: '#0a0a0f',
      });
      const blob = await (await fetch(dataUrl)).blob();
      const file = new File([blob], `rugmunch-scan-${token.slice(0, 8)}.png`, { type: 'image/png' });

      if (navigator.canShare && navigator.canShare({ files: [file] })) {
        await navigator.share({
          title: 'Rug Munch Security Scan',
          text: `Risk Score: ${riskScore ?? 'N/A'}/100 — ${verdict || getRiskLabel(riskScore)}`,
          files: [file],
        });
      } else {
        // Fallback: copy image to clipboard
        await navigator.clipboard.write([
          new ClipboardItem({ 'image/png': blob }),
        ]);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      }
    } catch (e) {
      console.error('Failed to share card:', e);
    } finally {
      setGenerating(false);
    }
  }, [token, riskScore, verdict]);

  const RiskIcon = getRiskIcon(riskScore);
  const gradient = getRiskGradient(riskScore);
  const label = riskLevel || getRiskLabel(riskScore);

  return (
    <div className="space-y-4">
      {/* The Card (rendered for export) */}
      <div
        ref={cardRef}
        className="relative w-full max-w-md mx-auto bg-[#0a0a0f] rounded-2xl overflow-hidden border border-white/10"
        style={{ aspectRatio: '4/5' }}
      >
        {/* Header Gradient */}
        <div className={`absolute inset-x-0 top-0 h-48 bg-gradient-to-b ${gradient} opacity-20`} />
        <div className={`absolute inset-x-0 top-0 h-1 bg-gradient-to-r ${gradient}`} />

        {/* Content */}
        <div className="relative p-6 h-full flex flex-col">
          {/* Logo */}
          <div className="flex items-center gap-2 mb-6">
            <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-yellow-400 rounded-lg flex items-center justify-center">
              <Shield className="w-5 h-5 text-white" />
            </div>
            <span className="font-bold text-white text-lg tracking-tight">Rug Munch</span>
            <span className="text-xs text-gray-500 ml-auto">{scanType}</span>
          </div>

          {/* Risk Score Circle */}
          <div className="flex-1 flex flex-col items-center justify-center">
            <div className={`w-32 h-32 rounded-full bg-gradient-to-br ${gradient} p-[3px]`}>
              <div className="w-full h-full rounded-full bg-[#0a0a0f] flex flex-col items-center justify-center">
                <span className={`text-4xl font-bold bg-gradient-to-br ${gradient} bg-clip-text text-transparent`}>
                  {riskScore ?? '?'}
                </span>
                <span className="text-xs text-gray-500 mt-1">/100</span>
              </div>
            </div>

            <div className="mt-4 flex items-center gap-2">
              <RiskIcon className={`w-5 h-5 ${riskScore !== undefined && riskScore >= 40 ? 'text-red-400' : 'text-emerald-400'}`} />
              <span className={`text-lg font-bold ${riskScore !== undefined && riskScore >= 40 ? 'text-red-400' : 'text-emerald-400'}`}>
                {label}
              </span>
            </div>

            {verdict && (
              <p className="text-sm text-gray-400 text-center mt-2 max-w-[240px]">{verdict}</p>
            )}
          </div>

          {/* Token */}
          <div className="mt-4 p-3 bg-white/5 rounded-xl border border-white/10">
            <div className="text-xs text-gray-500 uppercase mb-1">Token / Address</div>
            <code className="text-sm text-white font-mono">{truncateToken(token)}</code>
            <div className="flex items-center gap-2 mt-1">
              <span className="text-xs text-purple-400">{chain}</span>
              {aiConsensus && (
                <span className="text-xs text-gray-500">• AI: {aiConsensus}</span>
              )}
            </div>
          </div>

          {/* Red Flags */}
          {redFlags.length > 0 && (
            <div className="mt-3 space-y-1">
              {redFlags.slice(0, 3).map((flag, i) => (
                <div key={i} className="flex items-center gap-2 text-xs text-red-400">
                  <AlertTriangle className="w-3 h-3" />
                  {flag}
                </div>
              ))}
              {redFlags.length > 3 && (
                <div className="text-xs text-gray-500">+{redFlags.length - 3} more</div>
              )}
            </div>
          )}

          {/* Footer */}
          <div className="mt-auto pt-4 flex items-center justify-between text-xs text-gray-600">
            <div className="flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {new Date(timestamp).toLocaleDateString()}
            </div>
            <span>rugmunch.io</span>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex items-center justify-center gap-3">
        <button
          onClick={exportCard}
          disabled={generating}
          className="flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-purple-600/50 text-white rounded-lg text-sm font-medium transition-colors"
        >
          {generating ? (
            <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
          ) : (
            <Download className="w-4 h-4" />
          )}
          Download
        </button>
        <button
          onClick={shareCard}
          disabled={generating}
          className="flex items-center gap-2 px-4 py-2 bg-[#12121a] hover:bg-white/5 border border-purple-500/30 text-purple-400 rounded-lg text-sm font-medium transition-colors"
        >
          {copied ? (
            <>
              <Check className="w-4 h-4" />
              Copied
            </>
          ) : (
            <>
              <Share2 className="w-4 h-4" />
              Share
            </>
          )}
        </button>
      </div>
    </div>
  );
}
