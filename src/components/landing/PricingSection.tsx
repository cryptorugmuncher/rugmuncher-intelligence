import { Gift, Check } from 'lucide-react';
import ScrollReveal from '../hero/ScrollReveal';

const PRICING_TIERS = [
  {
    name: 'FREE',
    price: '$0',
    period: 'forever',
    description: 'Start with free alerts and basic scans',
    features: ['@rugmunchbot access', 'Free wallet scans (5/day)', 'Public alerts channel', 'Read The Trenches', '1 blockchain (ETH)'],
    cta: 'Join Free',
    popular: false,
  },
  {
    name: 'BASIC',
    price: '$29',
    period: '/month',
    description: 'Active traders who need more protection',
    features: ['25 scans per day', '3 blockchains', 'Basic bundle detection', 'Post in The Trenches', 'Telegram DM alerts'],
    cta: 'Get Basic',
    popular: false,
  },
  {
    name: 'PRO',
    price: '$99',
    period: '/month',
    description: 'Serious traders & alpha hunters',
    features: ['Unlimited scans', 'Full Muncher Maps (2D)', 'Advanced bundle detection', 'Fresh wallet analysis', 'Sniper tracking', 'Copy trading detection', 'AI risk reports', '@rmi_alpha_bot access'],
    cta: 'Go Pro',
    popular: true,
  },
  {
    name: 'ELITE',
    price: '$299',
    period: '/month',
    description: 'Whales, pros & full Muncher Maps',
    features: ['Everything in PRO', '3D Muncher Maps', '6 degrees of separation', 'Predictive analytics', 'Whale intelligence', 'Social OSINT', 'MEV detection', '1 free Rehab class/month'],
    cta: 'Become Elite',
    popular: false,
  },
];

interface PricingSectionProps {
  onNavigate: (page: string) => void;
  onAirdropClick: () => void;
}

export default function PricingSection({ onNavigate, onAirdropClick }: PricingSectionProps) {
  return (
    <section id="pricing" className="py-20 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <ScrollReveal direction="up" distance={30}>
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">
              Simple <span className="text-purple-400">Pricing</span>
            </h2>
            <p className="text-gray-400">Start free with Telegram, upgrade when ready</p>
          </div>

          {/* CRM v1 Holder Banner */}
          <div className="max-w-3xl mx-auto mb-12 p-6 bg-gradient-to-r from-purple-500/20 via-yellow-500/20 to-purple-500/20 border border-purple-500/30 rounded-xl">
            <div className="flex flex-col sm:flex-row items-center gap-4">
              <div className="w-12 h-12 bg-purple-500/20 rounded-full flex items-center justify-center">
                <Gift className="w-6 h-6 text-yellow-400" />
              </div>
              <div className="flex-1 text-center sm:text-left">
                <h3 className="text-lg font-semibold text-white">$CRM V1 Holders: 50% Bonus Airdrop</h3>
                <p className="text-gray-400 text-sm">V2 token airdrop + priority access + staking rewards. Connect wallet to verify.</p>
              </div>
              <button
                onClick={onAirdropClick}
                className="px-4 py-2 bg-gradient-to-r from-purple-600 to-yellow-500 hover:from-purple-500 hover:to-yellow-400 text-white font-semibold rounded-lg transition-colors whitespace-nowrap"
              >
                Join V2 Waitlist
              </button>
            </div>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {PRICING_TIERS.map((tier, idx) => (
              <div
                key={idx}
                className={`relative p-6 rounded-xl border ${
                  tier.popular ? 'bg-[#12121a] border-purple-500/50 glow-purple' : 'bg-[#0a0a0f] border-gray-800'
                }`}
              >
                {tier.popular && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 bg-gradient-to-r from-purple-600 to-yellow-500 text-white text-xs font-bold rounded-full">
                    MOST POPULAR
                  </div>
                )}

                <h3 className="text-lg font-semibold mb-2">{tier.name}</h3>
                <div className="flex items-baseline gap-1 mb-2">
                  <span className="text-4xl font-bold text-gradient">{tier.price}</span>
                  <span className="text-gray-400">{tier.period}</span>
                </div>
                <p className="text-gray-500 text-sm mb-6">{tier.description}</p>

                <ul className="space-y-3 mb-8">
                  {tier.features.map((feature, fidx) => (
                    <li key={fidx} className="flex items-start gap-2">
                      <Check className="w-5 h-5 text-purple-400 flex-shrink-0 mt-0.5" />
                      <span className="text-gray-300 text-sm">{feature}</span>
                    </li>
                  ))}
                </ul>

                <button
                  onClick={() => onNavigate('pricing')}
                  className={`block w-full text-center py-3 rounded-lg font-semibold transition-colors ${
                    tier.popular
                      ? 'bg-gradient-to-r from-purple-600 to-yellow-500 hover:from-purple-500 hover:to-yellow-400 text-white'
                      : 'bg-gray-800 hover:bg-gray-700 text-white'
                  }`}
                >
                  {tier.cta}
                </button>
              </div>
            ))}
          </div>
        </ScrollReveal>
      </div>
    </section>
  );
}
