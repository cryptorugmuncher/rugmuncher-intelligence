import {
  Check, AlertTriangle, Activity, Radio, Sparkles, ChevronRight,
  Search, Shield, Gift, Heart, MessageCircle, Share2, ArrowRight
} from 'lucide-react';
import NeuralNetwork from '../hero/NeuralNetwork';
import HeroText from '../hero/HeroText';
import ScrollReveal from '../hero/ScrollReveal';

const LIVE_ALERTS = [
  { id: 1, severity: 'critical', title: 'MAJOR RUG: PepeX Token', description: 'Contract owner just minted 50% supply and dumped on holders. $2.3M stolen.', chain: 'ETH', time: '2 min ago', likes: 234, comments: 89, shares: 156, verified: true, contract: '0x742d...8f3a' },
  { id: 2, severity: 'high', title: 'Honeypot Detected: MoonShot', description: 'Users unable to sell. 127 wallets already trapped. Blacklist function active.', chain: 'BSC', time: '8 min ago', likes: 178, comments: 45, shares: 203, verified: true, contract: '0x3f1a...9b2c' },
  { id: 3, severity: 'medium', title: 'Suspicious Activity: BaseLaunch', description: 'Dev wallet transferring large amounts to CEX. Possible exit preparation.', chain: 'BASE', time: '15 min ago', likes: 89, comments: 23, shares: 67, verified: false, contract: '0x9e4c...2d1f' },
  { id: 4, severity: 'critical', title: 'Rug Pull Confirmed: DeFiPro', description: 'Liquidity removed completely. Contract renounced after $890K theft.', chain: 'ARB', time: '32 min ago', likes: 445, comments: 123, shares: 567, verified: true, contract: '0x5a2b...7e9d' },
  { id: 5, severity: 'high', title: 'Sybil Farm Detected', description: '847 connected wallets identified. Same funding source. Bot farm confirmed.', chain: 'ETH', time: '1 hour ago', likes: 312, comments: 78, shares: 234, verified: true, contract: 'Multiple' },
];

function getSeverityColor(severity: string) {
  switch (severity) {
    case 'critical': return 'text-red-400 bg-red-500/10 border-red-500/30';
    case 'high': return 'text-orange-400 bg-orange-500/10 border-orange-500/30';
    case 'medium': return 'text-yellow-400 bg-yellow-500/10 border-yellow-500/30';
    default: return 'text-gray-400 bg-gray-500/10 border-gray-500/30';
  }
}

function getSeverityIcon(severity: string) {
  switch (severity) {
    case 'critical': return <FlameIcon />;
    case 'high': return <AlertTriangle className="w-4 h-4 text-orange-400" />;
    case 'medium': return <Activity className="w-4 h-4 text-yellow-400" />;
    default: return <Radio className="w-4 h-4 text-gray-400" />;
  }
}

function FlameIcon() {
  return (
    <svg className="w-4 h-4 text-red-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z" />
    </svg>
  );
}

interface HeroSectionProps {
  onNavigate: (page: string) => void;
  onAirdropClick: () => void;
}

export default function HeroSection({ onNavigate, onAirdropClick }: HeroSectionProps) {
  return (
    <section className="relative pt-36 pb-16 px-4 sm:px-6 lg:px-8 overflow-hidden min-h-[90vh] flex flex-col">
      <NeuralNetwork />

      <div className="relative z-10 max-w-7xl mx-auto w-full">
        <div className="grid lg:grid-cols-5 gap-8">
          {/* Main Hero Content - 3 columns */}
          <div className="lg:col-span-3 text-center lg:text-left">
            <ScrollReveal direction="down" delay={0} distance={20}>
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-purple-500/10 border border-purple-500/30 rounded-full mb-6 backdrop-blur-sm">
                <Sparkles className="w-4 h-4 text-purple-400" />
                <span className="text-purple-400 text-sm font-medium">V2 Live Now</span>
                <ChevronRight className="w-4 h-4 text-purple-400" />
              </div>
            </ScrollReveal>

            <HeroText />

            <ScrollReveal direction="up" delay={400} distance={30}>
              <div className="bg-[#12121a]/90 backdrop-blur-xl border border-purple-500/20 rounded-xl p-4 mb-8 max-w-lg mx-auto lg:mx-0">
                <div className="flex items-center gap-3 mb-3">
                  <Search className="w-5 h-5 text-purple-400" />
                  <span className="text-sm text-gray-400">Quick Contract Scanner</span>
                </div>
                <div className="flex gap-2">
                  <input
                    type="text"
                    placeholder="Enter token contract address..."
                    className="flex-1 bg-black/50 border border-purple-500/20 rounded-lg px-4 py-3 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-purple-500"
                    onClick={() => onNavigate('scanner')}
                    readOnly
                  />
                  <button
                    onClick={() => onNavigate('scanner')}
                    className="px-6 py-3 bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-500 hover:to-purple-600 text-white font-semibold rounded-lg transition-all"
                  >
                    Scan
                  </button>
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  Try: 0x1f9840a85d5af5bf1d1762f925bdaddc4201f984 (UNI)
                </p>
              </div>
            </ScrollReveal>

            <ScrollReveal direction="up" delay={600} distance={30}>
              <div className="flex flex-col sm:flex-row items-center lg:items-start gap-4 mb-8">
                <button
                  onClick={() => onNavigate('scanner')}
                  className="w-full sm:w-auto px-8 py-4 bg-gradient-to-r from-purple-600 to-yellow-500 hover:from-purple-500 hover:to-yellow-400 text-white font-bold rounded-xl flex items-center justify-center gap-2 transition-all transform hover:scale-105 shadow-lg shadow-purple-500/20"
                >
                  <Shield className="w-5 h-5" />
                  CHECK SCAMS NOW
                </button>
                <button
                  onClick={onAirdropClick}
                  className="w-full sm:w-auto px-8 py-4 bg-[#12121a]/80 backdrop-blur border border-yellow-500/30 hover:border-yellow-500/50 text-yellow-400 font-semibold rounded-xl flex items-center justify-center gap-2 transition-all"
                >
                  <Gift className="w-5 h-5" />
                  Join Airdrop Waitlist
                </button>
              </div>
            </ScrollReveal>

            <ScrollReveal direction="up" delay={800} distance={20}>
              <div className="flex flex-wrap items-center justify-center lg:justify-start gap-6 text-sm text-gray-500">
                <span className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-purple-400" />
                  AI-Powered Analysis
                </span>
                <span className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-purple-400" />
                  99.2% Detection Accuracy
                </span>
                <span className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-purple-400" />
                  $547K Recovered for Victims
                </span>
              </div>
            </ScrollReveal>
          </div>

          {/* Live Alert Feed Sidebar - 2 columns */}
          <div className="lg:col-span-2">
            <ScrollReveal direction="left" delay={300} distance={50}>
              <div className="bg-[#12121a]/80 backdrop-blur-xl border border-purple-500/20 rounded-xl overflow-hidden">
                <div className="p-4 border-b border-purple-500/20 bg-purple-500/5">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Radio className="w-5 h-5 text-red-400 animate-pulse" />
                      <span className="font-semibold">Live Rug Alerts</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
                      <span className="text-xs text-green-400">LIVE</span>
                    </div>
                  </div>
                </div>

                <div className="max-h-[500px] overflow-y-auto">
                  {LIVE_ALERTS.map((alert) => (
                    <div
                      key={alert.id}
                      className="p-4 border-b border-purple-500/10 hover:bg-purple-500/5 transition-colors"
                    >
                      <div className="flex items-start gap-3">
                        <div className={`p-1.5 rounded-lg ${getSeverityColor(alert.severity)}`}>
                          {getSeverityIcon(alert.severity)}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <span className={`text-xs font-semibold uppercase px-2 py-0.5 rounded ${getSeverityColor(alert.severity)}`}>
                              {alert.severity}
                            </span>
                            <span className="text-xs text-gray-500">{alert.time}</span>
                            <span className="text-xs text-purple-400">{alert.chain}</span>
                          </div>
                          <h4 className="font-semibold text-sm mb-1 truncate">{alert.title}</h4>
                          <p className="text-xs text-gray-400 line-clamp-2">{alert.description}</p>
                          {alert.verified && (
                            <div className="flex items-center gap-1 mt-2">
                              <Check className="w-3 h-3 text-green-400" />
                              <span className="text-xs text-green-400">RMI Verified</span>
                            </div>
                          )}
                          <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                            <span className="flex items-center gap-1">
                              <Heart className="w-3 h-3" /> {alert.likes}
                            </span>
                            <span className="flex items-center gap-1">
                              <MessageCircle className="w-3 h-3" /> {alert.comments}
                            </span>
                            <span className="flex items-center gap-1">
                              <Share2 className="w-3 h-3" /> {alert.shares}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="p-3 border-t border-purple-500/20 bg-purple-500/5">
                  <button
                    onClick={() => onNavigate('trenches')}
                    className="w-full py-2 text-sm text-purple-400 hover:text-purple-300 transition-colors flex items-center justify-center gap-2"
                  >
                    View All Alerts in The Trenches
                    <ArrowRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </ScrollReveal>
          </div>
        </div>
      </div>
    </section>
  );
}
