import { Rocket, Gift, Star, Lock, Shield, Sparkles } from 'lucide-react';
import ScrollReveal from '../hero/ScrollReveal';

const V2_PROGRESS = [
  { label: 'Smart Contract Audit', progress: 100, status: 'complete' },
  { label: 'Token Economics', progress: 100, status: 'complete' },
  { label: 'Platform Migration', progress: 100, status: 'complete' },
  { label: 'Airdrop System', progress: 100, status: 'complete' },
  { label: 'Exchange Listings', progress: 65, status: 'in_progress' },
];

interface V2WaitlistSectionProps {
  onAirdropClick: () => void;
}

export default function V2WaitlistSection({ onAirdropClick }: V2WaitlistSectionProps) {
  return (
    <section id="v2-waitlist" className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-b from-purple-500/10 to-transparent">
      <div className="max-w-7xl mx-auto">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          <ScrollReveal direction="left" distance={50}>
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 bg-purple-500/10 border border-purple-500/30 rounded-full mb-6">
                <Rocket className="w-4 h-4 text-purple-400" />
                <span className="text-purple-400 text-sm font-medium">Live Now</span>
              </div>
              <h2 className="text-3xl sm:text-4xl font-bold mb-4">
                Rug Munch <span className="text-purple-400">V2</span>
              </h2>
              <p className="text-gray-400 mb-8 text-lg">
                Complete ecosystem relaunch with new token contract, enhanced AI models,
                and expanded cross-chain capabilities. Join the waitlist for early access
                and airdrop eligibility.
              </p>

              {/* Progress Bars */}
              <div className="space-y-4 mb-8">
                {V2_PROGRESS.map((item, idx) => (
                  <div key={idx}>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm text-gray-300">{item.label}</span>
                      <span className="text-sm text-purple-400">{item.progress}%</span>
                    </div>
                    <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-purple-600 to-yellow-500 rounded-full transition-all"
                        style={{ width: `${item.progress}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>

              {/* Benefits */}
              <div className="grid grid-cols-2 gap-3 mb-8">
                <div className="flex items-center gap-2 text-sm text-gray-300">
                  <Gift className="w-4 h-4 text-yellow-400" />
                  <span>Airdrop for Waitlist</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-gray-300">
                  <Star className="w-4 h-4 text-yellow-400" />
                  <span>Early Access</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-gray-300">
                  <Lock className="w-4 h-4 text-yellow-400" />
                  <span>Staking Rewards</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-gray-300">
                  <Shield className="w-4 h-4 text-yellow-400" />
                  <span>V1 Holder Benefits</span>
                </div>
              </div>

              <button
                onClick={onAirdropClick}
                className="px-8 py-4 bg-gradient-to-r from-purple-600 to-yellow-500 hover:from-purple-500 hover:to-yellow-400 text-white font-bold rounded-xl transition-all transform hover:scale-105"
              >
                Join V2 Waitlist
              </button>
            </div>
          </ScrollReveal>

          {/* V2 Preview Card */}
          <ScrollReveal direction="right" distance={50} delay={200}>
            <div className="relative">
              <div className="bg-[#12121a] rounded-2xl border border-purple-500/20 p-8 relative overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 to-yellow-500/5" />
                <div className="absolute -top-20 -right-20 w-40 h-40 bg-purple-500/20 rounded-full blur-3xl" />

                <div className="relative">
                  <div className="text-center mb-6">
                    <div className="w-20 h-20 bg-gradient-to-br from-purple-600 to-yellow-500 rounded-2xl flex items-center justify-center mx-auto mb-4 glow-purple">
                      <Sparkles className="w-10 h-10 text-white" />
                    </div>
                    <h3 className="text-2xl font-bold text-gradient">$CRM V2</h3>
                    <p className="text-gray-500">The Future of Rug Detection</p>
                  </div>

                  <div className="space-y-4">
                    <div className="flex items-center justify-between p-3 bg-black/30 rounded-lg">
                      <span className="text-gray-400">New Features</span>
                      <span className="text-purple-400 font-semibold">18+ AI Models</span>
                    </div>
                    <div className="flex items-center justify-between p-3 bg-black/30 rounded-lg">
                      <span className="text-gray-400">Chains Supported</span>
                      <span className="text-purple-400 font-semibold">15+ Networks</span>
                    </div>
                    <div className="flex items-center justify-between p-3 bg-black/30 rounded-lg">
                      <span className="text-gray-400">Token Utility</span>
                      <span className="text-purple-400 font-semibold">Staking + Access</span>
                    </div>
                    <div className="flex items-center justify-between p-3 bg-black/30 rounded-lg">
                      <span className="text-gray-400">Launch</span>
                      <span className="text-yellow-400 font-semibold">Live Now</span>
                    </div>
                  </div>

                  <div className="mt-6 p-4 bg-gradient-to-r from-purple-600/10 to-yellow-500/10 rounded-lg border border-purple-500/20">
                    <p className="text-sm text-center text-gray-400">
                      <span className="text-yellow-400 font-semibold">$CRM V1 Holders:</span> 50% bonus airdrop + priority access
                    </p>
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
