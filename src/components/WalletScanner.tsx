/**
 * Wallet Scanner Component
 * Connects to backend APIs for wallet analysis
 */
import { useState } from 'react';
import { useWalletAnalysis, useWalletLookup, useAIAnalysis, usePatternDetection } from '../hooks/useBackend';
import { useAppStore } from '../store/appStore';
import {
  Search,
  Loader2,
  AlertTriangle,
  Shield,
  Brain,
  Activity,
  Copy,
  Check,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  Image,
} from 'lucide-react';
import ScanCard from './ScanCard';

const CHAINS = [
  { id: 'ethereum', name: 'Ethereum', icon: '⧫' },
  { id: 'bsc', name: 'BSC', icon: 'B' },
  { id: 'polygon', name: 'Polygon', icon: 'P' },
  { id: 'arbitrum', name: 'Arbitrum', icon: 'A' },
  { id: 'optimism', name: 'Optimism', icon: 'O' },
  { id: 'base', name: 'Base', icon: 'B' },
];

export default function WalletScanner() {
  const [address, setAddress] = useState('');
  const [chain, setChain] = useState('ethereum');
  const [showDetails, setShowDetails] = useState(false);
  const [copied, setCopied] = useState(false);
  const [showCard, setShowCard] = useState(false);

  const setError = useAppStore((state) => state.setError);

  const analyzeMutation = useWalletAnalysis();
  const aiMutation = useAIAnalysis();
  const patternMutation = usePatternDetection();

  // Query cached data if address is valid
  const { data: cachedData, isLoading: cacheLoading } = useWalletLookup(
    address.length >= 10 ? address : '',
    chain
  );

  const handleAnalyze = async () => {
    if (!address || address.length < 10) {
      setError('Please enter a valid wallet address');
      return;
    }

    try {
      setShowDetails(true);
      await analyzeMutation.mutateAsync({ address, chain });
    } catch (e) {
      // Error handled by mutation
    }
  };

  const handleAIAnalysis = async () => {
    if (!address) return;
    try {
      await aiMutation.mutateAsync({ address, chain, tier: 'HIGH' });
    } catch (e) {
      // Error handled by mutation
    }
  };

  const handlePatternDetect = async () => {
    if (!address) return;
    try {
      await patternMutation.mutateAsync({ address, chain });
    } catch (e) {
      // Error handled by mutation
    }
  };

  const copyAddress = () => {
    navigator.clipboard.writeText(address);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const isAnalyzing = analyzeMutation.isPending || cacheLoading;
  const analysisResult = analyzeMutation.data || cachedData;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white">Wallet Scanner</h1>
        <p className="text-gray-400 mt-1">
          Analyze wallet addresses across multiple chains with AI-powered risk detection
        </p>
      </div>

      {/* Search Box */}
      <div className="bg-[#12121a] rounded-xl border border-purple-500/20 p-6">
        <div className="flex flex-col md:flex-row gap-4">
          {/* Chain Selector */}
          <div className="md:w-48">
            <label className="block text-sm text-gray-400 mb-2">Blockchain</label>
            <select
              value={chain}
              onChange={(e) => setChain(e.target.value)}
              className="w-full bg-[#0a0a0f] border border-purple-500/20 rounded-lg px-3 py-2.5 text-white focus:outline-none focus:border-purple-500/50"
            >
              {CHAINS.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.icon} {c.name}
                </option>
              ))}
            </select>
          </div>

          {/* Address Input */}
          <div className="flex-1">
            <label className="block text-sm text-gray-400 mb-2">Wallet Address</label>
            <div className="relative">
              <input
                type="text"
                value={address}
                onChange={(e) => setAddress(e.target.value)}
                placeholder="0x... or enter any wallet address"
                className="w-full bg-[#0a0a0f] border border-purple-500/20 rounded-lg px-4 py-2.5 text-white placeholder-gray-500 focus:outline-none focus:border-purple-500/50 font-mono"
              />
              {address && (
                <button
                  onClick={copyAddress}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white"
                >
                  {copied ? <Check size={18} className="text-green-400" /> : <Copy size={18} />}
                </button>
              )}
            </div>
          </div>

          {/* Analyze Button */}
          <div className="md:w-auto">
            <label className="block text-sm text-transparent mb-2">Action</label>
            <button
              onClick={handleAnalyze}
              disabled={isAnalyzing || !address}
              className="w-full md:w-auto px-6 py-2.5 bg-purple-600 hover:bg-purple-700 disabled:bg-purple-600/50 text-white rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
            >
              {isAnalyzing ? (
                <>
                  <Loader2 size={18} className="animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Search size={18} />
                  Analyze
                </>
              )}
            </button>
          </div>
        </div>

        {/* Quick Actions */}
        {address && (
          <div className="flex flex-wrap gap-2 mt-4 pt-4 border-t border-purple-500/10">
            <button
              onClick={handleAIAnalysis}
              disabled={aiMutation.isPending}
              className="px-3 py-1.5 bg-blue-600/20 hover:bg-blue-600/30 text-blue-300 rounded-lg text-sm flex items-center gap-1.5 transition-colors"
            >
              {aiMutation.isPending ? <Loader2 size={14} className="animate-spin" /> : <Brain size={14} />}
              AI Analysis
            </button>
            <button
              onClick={handlePatternDetect}
              disabled={patternMutation.isPending}
              className="px-3 py-1.5 bg-green-600/20 hover:bg-green-600/30 text-green-300 rounded-lg text-sm flex items-center gap-1.5 transition-colors"
            >
              {patternMutation.isPending ? <Loader2 size={14} className="animate-spin" /> : <Activity size={14} />}
              Detect Patterns
            </button>
            <a
              href={`https://etherscan.io/address/${address}`}
              target="_blank"
              rel="noopener noreferrer"
              className="px-3 py-1.5 bg-gray-600/20 hover:bg-gray-600/30 text-gray-300 rounded-lg text-sm flex items-center gap-1.5 transition-colors"
            >
              <ExternalLink size={14} />
              View on Explorer
            </a>
          </div>
        )}
      </div>

      {/* Results */}
      {analysisResult && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Result Card */}
          <div className="lg:col-span-2 space-y-6">
            {/* Risk Overview */}
            <div className="bg-[#12121a] rounded-xl border border-purple-500/20 overflow-hidden">
              <div
                className={`p-4 ${
                  analysisResult.risk_level === 'CRITICAL'
                    ? 'bg-red-500/20'
                    : analysisResult.risk_level === 'HIGH'
                    ? 'bg-orange-500/20'
                    : analysisResult.risk_level === 'MEDIUM'
                    ? 'bg-yellow-500/20'
                    : 'bg-green-500/20'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    {analysisResult.risk_level === 'CRITICAL' || analysisResult.risk_level === 'HIGH' ? (
                      <AlertTriangle size={24} className="text-red-400" />
                    ) : (
                      <Shield size={24} className="text-green-400" />
                    )}
                    <div>
                      <h2 className="text-lg font-semibold text-white">
                        Risk Level: {analysisResult.risk_level}
                      </h2>
                      <p className="text-sm text-gray-400">
                        Risk Score: {analysisResult.risk_score || 'N/A'}/100
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-3xl font-bold text-white">
                      {analysisResult.risk_score || 'N/A'}
                    </div>
                    <div className="text-xs text-gray-400">/100</div>
                  </div>
                </div>
              </div>

              {/* Analysis Content */}
              <div className="p-4">
                <h3 className="font-medium text-white mb-2">Analysis Summary</h3>
                <p className="text-sm text-gray-300 leading-relaxed">
                  {analysisResult.analysis || analysisResult.details?.summary || 'No analysis available'}
                </p>

                {analysisResult.details && (
                  <div className="mt-4 pt-4 border-t border-purple-500/10">
                    <button
                      onClick={() => setShowDetails(!showDetails)}
                      className="flex items-center gap-1 text-sm text-purple-400 hover:text-purple-300"
                    >
                      {showDetails ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                      {showDetails ? 'Hide Details' : 'Show Details'}
                    </button>

                    {showDetails && (
                      <div className="mt-3 space-y-3">
                        {analysisResult.details.balance !== undefined && (
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-400">Balance</span>
                            <span className="text-white">{analysisResult.details.balance} ETH</span>
                          </div>
                        )}
                        {analysisResult.details.tx_count !== undefined && (
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-400">Transactions</span>
                            <span className="text-white">{analysisResult.details.tx_count}</span>
                          </div>
                        )}
                        {analysisResult.details.first_seen && (
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-400">First Seen</span>
                            <span className="text-white">
                              {new Date(analysisResult.details.first_seen).toLocaleDateString()}
                            </span>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>

            {/* AI Analysis Result */}
            {aiMutation.data && (
              <div className="bg-[#12121a] rounded-xl border border-blue-500/20 p-4">
                <div className="flex items-center gap-2 mb-3">
                  <Brain size={18} className="text-blue-400" />
                  <h3 className="font-semibold text-white">AI Analysis</h3>
                  <span className="text-xs text-gray-500">
                    via {aiMutation.data.model} ({aiMutation.data.latency_ms}ms)
                  </span>
                </div>
                <p className="text-sm text-gray-300 whitespace-pre-wrap">{aiMutation.data.analysis}</p>
              </div>
            )}

            {/* Shareable Scan Card */}
            <div className="bg-[#12121a] rounded-xl border border-purple-500/20 overflow-hidden">
              <button
                onClick={() => setShowCard(!showCard)}
                className="w-full flex items-center justify-between p-4 hover:bg-white/5 transition-colors"
              >
                <div className="flex items-center gap-2">
                  <Image size={18} className="text-purple-400" />
                  <h3 className="font-semibold text-white">Shareable Scan Card</h3>
                </div>
                <span className="text-xs text-purple-400">
                  {showCard ? 'Hide' : 'Generate'} →
                </span>
              </button>
              {showCard && (
                <div className="p-4 pt-0">
                  <ScanCard
                    token={address}
                    chain={chain.toUpperCase()}
                    scanType="WALLET SCAN"
                    riskScore={analysisResult.risk_score}
                    riskLevel={analysisResult.risk_level}
                    verdict={analysisResult.analysis?.slice(0, 120)}
                    redFlags={patternMutation.data?.risk_indicators}
                    aiConsensus={aiMutation.data?.model}
                  />
                </div>
              )}
            </div>
          </div>

          {/* Side Panel */}
          <div className="space-y-6">
            {/* Patterns Detected */}
            {patternMutation.data?.patterns && patternMutation.data.patterns.length > 0 && (
              <div className="bg-[#12121a] rounded-xl border border-purple-500/20 p-4">
                <h3 className="font-semibold text-white mb-3 flex items-center gap-2">
                  <Activity size={16} className="text-purple-400" />
                  Detected Patterns
                </h3>
                <div className="space-y-2">
                  {patternMutation.data.patterns.map((pattern: any, idx: number) => (
                    <div key={idx} className="p-2 bg-purple-500/10 rounded-lg">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-white">{pattern.type}</span>
                        <span className="text-xs text-purple-300">
                          {Math.round(pattern.confidence * 100)}% confidence
                        </span>
                      </div>
                      <p className="text-xs text-gray-400 mt-1">{pattern.description}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Risk Indicators */}
            {patternMutation.data?.risk_indicators && patternMutation.data.risk_indicators.length > 0 && (
              <div className="bg-[#12121a] rounded-xl border border-red-500/20 p-4">
                <h3 className="font-semibold text-white mb-3 text-red-400">Risk Indicators</h3>
                <ul className="space-y-1">
                  {patternMutation.data.risk_indicators.map((indicator: string, idx: number) => (
                    <li key={idx} className="text-sm text-gray-300 flex items-center gap-2">
                      <AlertTriangle size={12} className="text-red-400" />
                      {indicator}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Cache Info */}
            {cachedData && (
              <div className="bg-[#12121a] rounded-xl border border-green-500/20 p-4">
                <div className="flex items-center gap-2 mb-2">
                  <Check size={16} className="text-green-400" />
                  <span className="text-sm font-medium text-green-400">Cached Result</span>
                </div>
                <p className="text-xs text-gray-400">
                  This data was retrieved from Dragonfly cache for instant results.
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
