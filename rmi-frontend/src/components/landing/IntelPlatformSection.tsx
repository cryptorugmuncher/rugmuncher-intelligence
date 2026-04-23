import { Zap, Check, ArrowRight, AlertTriangle, Sparkles } from 'lucide-react';
import ScrollReveal from '../hero/ScrollReveal';

interface IntelPlatformSectionProps {
  onNavigate: (page: string) => void;
}

const FEATURES = [
  'Multi-AI consensus engine (18+ models)',
  'Real-time contract analysis',
  'Wallet clustering & relationship mapping',
  'Social sentiment monitoring',
  'Honeypot & rug pull detection',
  'V2 airdrop for early adopters'
];

export default function IntelPlatformSection({ onNavigate }: IntelPlatformSectionProps) {
  return (
    <section id="intel" className="py-20 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          <ScrollReveal direction="left" distance={50}>
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 bg-blue-500/10 border border-blue-500/30 rounded-full mb-6">
                <Zap className="w-4 h-4 text-blue-400" />
                <span className="text-blue-400 text-sm font-medium">Full Platform Access</span>
              </div>
              <h2 className="text-3xl sm:text-4xl font-bold mb-4">
                RMI Intel Platform
                <span className="text-blue-400 block mt-2">Relaunch Coming Soon</span>
              </h2>
              <p className="text-gray-400 mb-6 text-lg">
                The complete security suite is getting a V2 overhaul. Enhanced AI, faster scanning,
                and new cross-chain tracing capabilities launching now.
              </p>
              <ul className="space-y-3 mb-8">
                {FEATURES.map((item, idx) => (
                  <li key={idx} className="flex items-center gap-3">
                    <Check className="w-5 h-5 text-blue-400" />
                    <span className="text-gray-300">{item}</span>
                  </li>
                ))}
              </ul>
              <div className="flex items-center gap-4">
                <button
                  onClick={() => onNavigate('scanner')}
                  className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors"
                >
                  Launch Scanner
                  <ArrowRight className="w-5 h-5" />
                </button>
                <span className="text-sm text-yellow-400">V2 features coming soon</span>
              </div>
            </div>
          </ScrollReveal>

          <ScrollReveal direction="right" distance={50} delay={200}>
            <div className="relative">
              <div className="bg-[#12121a] rounded-2xl border border-blue-500/20 p-6 relative overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-purple-500/5" />
                <div className="relative space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full bg-red-500" />
                      <div className="w-3 h-3 rounded-full bg-yellow-500" />
                      <div className="w-3 h-3 rounded-full bg-green-500" />
                    </div>
                    <span className="text-xs text-gray-500">cryptorugmunch.com</span>
                  </div>
                  <div className="grid grid-cols-3 gap-3">
                    <div className="bg-black/30 rounded-lg p-3">
                      <div className="text-xs text-gray-500 mb-1">Risk Score</div>
                      <div className="text-2xl font-bold text-red-400">87/100</div>
                    </div>
                    <div className="bg-black/30 rounded-lg p-3">
                      <div className="text-xs text-gray-500 mb-1">AI Consensus</div>
                      <div className="text-2xl font-bold text-yellow-400">HIGH</div>
                    </div>
                    <div className="bg-black/30 rounded-lg p-3">
                      <div className="text-xs text-gray-500 mb-1">Confidence</div>
                      <div className="text-2xl font-bold text-green-400">94%</div>
                    </div>
                  </div>
                  <div className="bg-black/30 rounded-lg p-3">
                    <div className="flex items-center gap-2 mb-2">
                      <AlertTriangle className="w-4 h-4 text-red-400" />
                      <span className="text-sm font-semibold">Critical Findings</span>
                    </div>
                    <ul className="text-xs text-gray-400 space-y-1">
                      <li>• Hidden mint function detected</li>
                      <li>• Owner can blacklist wallets</li>
                      <li>• Liquidity not locked</li>
                    </ul>
                  </div>
                  <div className="bg-gradient-to-r from-purple-600/20 to-yellow-500/20 rounded-lg p-3 border border-purple-500/30">
                    <div className="flex items-center gap-2">
                      <Sparkles className="w-4 h-4 text-yellow-400" />
                      <span className="text-sm font-semibold text-yellow-400">V2 Coming Soon</span>
                    </div>
                    <p className="text-xs text-gray-400 mt-1">Enhanced analysis with 18+ AI models</p>
                  </div>
                </div>
              </div>
            </div>
          </ScrollReveal>
        </div>
      </div>
    </section>
  );
}
