import { Megaphone, Check } from 'lucide-react';
import ScrollReveal from '../hero/ScrollReveal';

const SNITCH_TIPS = [
  {
    id: 1,
    type: 'verified',
    title: 'Dev Team Exposed',
    description: 'Anonymous tip identified 3 devs behind 12 previous rugs.',
    reward: '1.0 ETH',
    tipper: 'Anonymous_Whistle',
    time: '3 hours ago',
    impact: 'High'
  },
  {
    id: 2,
    type: 'verified',
    title: 'Insider Trading Ring',
    description: 'Coordinated group of 23 wallets manipulating launches.',
    reward: '0.5 ETH',
    tipper: 'RugHunter_007',
    time: '6 hours ago',
    impact: 'Critical'
  },
  {
    id: 3,
    type: 'pending',
    title: 'Fake KYC Documents',
    description: 'Project using stolen identity for "audit" verification.',
    reward: '0.25 ETH',
    tipper: 'DetectiveDeFi',
    time: '12 hours ago',
    impact: 'Medium'
  }
];

interface SnitchSectionProps {
  onSnitchClick: () => void;
  onNavigate: (page: string) => void;
}

export default function SnitchSection({ onSnitchClick, onNavigate }: SnitchSectionProps) {
  return (
    <section id="snitch" className="py-20 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          <ScrollReveal direction="left" distance={50}>
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 bg-yellow-500/10 border border-yellow-500/30 rounded-full mb-6">
                <Megaphone className="w-4 h-4 text-yellow-400" />
                <span className="text-yellow-400 text-sm font-medium">Anonymous Tips</span>
              </div>
              <h2 className="text-3xl sm:text-4xl font-bold mb-4">
                Snitch <span className="text-yellow-400">Board</span>
              </h2>
              <p className="text-gray-400 mb-6 text-lg">
                Submit anonymous tips about scams, insider trading, or fraudulent projects.
                Verified tips earn ETH rewards. Privacy guaranteed.
              </p>

              {/* Reward Tiers */}
              <div className="space-y-3 mb-8">
                <div className="flex items-center gap-4 p-3 bg-[#12121a] border border-yellow-500/20 rounded-lg">
                  <div className="text-2xl font-bold text-yellow-400">1.0 ETH</div>
                  <div>
                    <div className="font-semibold">Critical Intel</div>
                    <div className="text-sm text-gray-500">Major scam prevented, dev team exposed</div>
                  </div>
                </div>
                <div className="flex items-center gap-4 p-3 bg-[#12121a] border border-yellow-500/20 rounded-lg">
                  <div className="text-2xl font-bold text-yellow-400">0.5 ETH</div>
                  <div>
                    <div className="font-semibold">High Value Tip</div>
                    <div className="text-sm text-gray-500">Insider trading ring, coordinated manipulation</div>
                  </div>
                </div>
                <div className="flex items-center gap-4 p-3 bg-[#12121a] border border-yellow-500/20 rounded-lg">
                  <div className="text-2xl font-bold text-yellow-400">0.1 ETH</div>
                  <div>
                    <div className="font-semibold">Verified Report</div>
                    <div className="text-sm text-gray-500">Fake KYC, copied contracts, confirmed honeypot</div>
                  </div>
                </div>
              </div>

              <button
                onClick={onSnitchClick}
                className="px-8 py-4 bg-gradient-to-r from-yellow-600 to-yellow-500 hover:from-yellow-500 hover:to-yellow-400 text-black font-bold rounded-xl transition-all transform hover:scale-105"
              >
                Submit Anonymous Tip
              </button>
            </div>
          </ScrollReveal>

          {/* Recent Verified Tips */}
          <ScrollReveal direction="right" distance={50} delay={200}>
            <div className="bg-[#12121a] border border-yellow-500/20 rounded-xl overflow-hidden">
              <div className="p-4 border-b border-yellow-500/20 bg-yellow-500/5">
                <h3 className="font-semibold flex items-center gap-2">
                  <Check className="w-5 h-5 text-green-400" />
                  Recent Verified Tips
                </h3>
              </div>
              <div className="divide-y divide-yellow-500/10">
                {SNITCH_TIPS.map((tip) => (
                  <div key={tip.id} className="p-4 hover:bg-yellow-500/5 transition-colors">
                    <div className="flex items-start justify-between mb-2">
                      <span className={`text-xs px-2 py-0.5 rounded ${
                        tip.type === 'verified' ? 'bg-green-500/10 text-green-400' : 'bg-yellow-500/10 text-yellow-400'
                      }`}>
                        {tip.type === 'verified' ? 'VERIFIED & PAID' : 'UNDER REVIEW'}
                      </span>
                      <span className="text-xs text-gray-500">{tip.time}</span>
                    </div>
                    <h4 className="font-semibold mb-1">{tip.title}</h4>
                    <p className="text-sm text-gray-400 mb-2">{tip.description}</p>
                    <div className="flex items-center gap-4 text-sm">
                      <span className="text-yellow-400 font-semibold">Reward: {tip.reward}</span>
                      <span className="text-gray-500">Impact: {tip.impact}</span>
                    </div>
                  </div>
                ))}
              </div>
              <div className="p-3 border-t border-yellow-500/20 bg-yellow-500/5">
                <button
                  onClick={() => onNavigate('trenches')}
                  className="w-full py-2 text-sm text-yellow-400 hover:text-yellow-300 transition-colors"
                >
                  View All Community Reports →
                </button>
              </div>
            </div>
          </ScrollReveal>
        </div>
      </div>
    </section>
  );
}
