import { Network, Check, ArrowRight, BarChart3 } from 'lucide-react';
import ScrollReveal from '../hero/ScrollReveal';

const FEATURES = [
  "3D interactive network graphs",
  "6 degrees of separation tracking",
  "Cross-chain relationship mapping",
  "Money flow animation in real-time",
  "Criminal database cross-reference",
  "CEX tracing through multiple hops"
];

export default function MuncherMapsSection() {
  return (
    <section id="munchermaps" className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-b from-purple-500/10 to-transparent">
      <div className="max-w-7xl mx-auto">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          <ScrollReveal direction="left" distance={50}>
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 bg-purple-500/10 border border-purple-500/30 rounded-full mb-6">
                <Network className="w-4 h-4 text-purple-400" />
                <span className="text-purple-400 text-sm font-medium">Crown Jewel Feature</span>
              </div>
              <h2 className="text-3xl sm:text-4xl font-bold mb-4">
                Muncher Maps
                <span className="text-purple-400 block mt-2">See What Others Can't</span>
              </h2>
              <p className="text-gray-400 mb-6 text-lg">
                The most advanced blockchain visualization tool in crypto. Watch funds flow
                in real-time, trace through 6 degrees of separation, and expose criminal networks
                that hide in the shadows.
              </p>
              <ul className="space-y-3 mb-8">
                {FEATURES.map((item, idx) => (
                  <li key={idx} className="flex items-center gap-3">
                    <Check className="w-5 h-5 text-purple-400" />
                    <span className="text-gray-300">{item}</span>
                  </li>
                ))}
              </ul>
              <div className="flex items-center gap-4">
                <a
                  href="https://maps.rugmunch.io"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-purple-600 to-cyan-500 hover:from-purple-500 hover:to-cyan-400 text-white font-semibold rounded-lg transition-all shadow-lg shadow-purple-500/20"
                >
                  Launch Muncher Maps
                  <ArrowRight className="w-5 h-5" />
                </a>
                <a
                  href="https://maps.rugmunch.io/markets"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 px-5 py-3 bg-rmi-bg/60 border border-yellow-500/30 text-yellow-400 font-semibold rounded-lg hover:bg-yellow-500/10 transition-all text-sm"
                >
                  <BarChart3 className="w-4 h-4" />
                  Markets
                </a>
              </div>
            </div>
          </ScrollReveal>

          <ScrollReveal direction="right" distance={50} delay={200}>
            <div className="relative">
              <div className="aspect-square bg-[#12121a] rounded-2xl border border-purple-500/20 p-6 relative overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 to-blue-500/5" />
                <svg className="w-full h-full" viewBox="0 0 400 400">
                  <line x1="200" y1="100" x2="100" y2="200" stroke="#8b5cf6" strokeWidth="2" opacity="0.6" />
                  <line x1="200" y1="100" x2="300" y2="200" stroke="#8b5cf6" strokeWidth="2" opacity="0.6" />
                  <line x1="100" y1="200" x2="150" y2="300" stroke="#8b5cf6" strokeWidth="2" opacity="0.6" />
                  <line x1="300" y1="200" x2="250" y2="300" stroke="#8b5cf6" strokeWidth="2" opacity="0.6" />
                  <circle cx="200" cy="100" r="25" fill="#8b5cf6">
                    <animate attributeName="r" values="25;28;25" dur="2s" repeatCount="indefinite" />
                  </circle>
                  <circle cx="100" cy="200" r="18" fill="#ec4899" />
                  <circle cx="300" cy="200" r="18" fill="#ec4899" />
                  <circle cx="150" cy="300" r="14" fill="#3b82f6" />
                  <circle cx="250" cy="300" r="14" fill="#3b82f6" />
                </svg>
                <div className="absolute bottom-4 left-4 right-4 bg-[#0a0a0f]/90 backdrop-blur rounded-lg p-4 border border-purple-500/20">
                  <div className="flex justify-between items-center">
                    <div>
                      <div className="text-xs text-gray-400">Target Wallet</div>
                      <div className="text-sm font-mono text-purple-400">0x7a2...9f3b</div>
                    </div>
                    <div className="text-right">
                      <div className="text-xs text-gray-400">Risk Score</div>
                      <div className="text-xl font-bold text-red-400">94/100</div>
                    </div>
                  </div>
                  <div className="mt-2 pt-2 border-t border-gray-800">
                    <div className="text-xs text-gray-400">Network: 47 connected wallets detected</div>
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
