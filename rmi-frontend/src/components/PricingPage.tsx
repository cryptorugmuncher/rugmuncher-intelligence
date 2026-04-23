/**
 * Pricing Page - With CRM v1 Holder 50% Discount
 */
import { useState } from 'react';
import { 
  Check, 
  X, 
  Star,
  Shield,
  Zap,
  Network,
  ChevronDown,
  ChevronUp,
  ArrowRight,
  Wallet
} from 'lucide-react';

const TIERS = [
  {
    name: 'FREE',
    price: 0,
    period: 'forever',
    description: 'Basic protection for casual traders',
    icon: Shield,
    color: 'gray',
    features: [
      { text: '@rugmunchbot access', included: true },
      { text: '5 wallet scans/day', included: true },
      { text: '1 blockchain (ETH)', included: true },
      { text: '3-day TX history', included: true },
      { text: 'Basic risk score', included: true },
      { text: 'Read The Trenches', included: true },
      { text: 'Public alerts channel', included: true },
      { text: 'Advanced analytics', included: false },
      { text: 'Muncher Maps', included: false },
      { text: 'Bundle detection', included: false },
      { text: 'AI risk reports', included: false },
      { text: 'Rug Pull Rehab', included: false },
    ],
    cta: 'Start Free',
    popular: false,
    discountPrice: null
  },
  {
    name: 'BASIC',
    price: 29,
    period: '/month',
    description: 'Active traders who need more protection',
    icon: Shield,
    color: 'blue',
    features: [
      { text: 'Everything in FREE', included: true },
      { text: '25 scans per day', included: true },
      { text: '3 blockchains', included: true },
      { text: '7-day TX history', included: true },
      { text: 'Basic bundle detection', included: true },
      { text: 'Post in The Trenches', included: true },
      { text: 'Telegram DM alerts', included: true },
      { text: '3 custom price alerts', included: true },
      { text: 'Muncher Maps', included: false },
      { text: 'Sniper tracking', included: false },
      { text: 'AI analysis', included: false },
      { text: 'Rug Pull Rehab', included: false },
    ],
    cta: 'Get Basic',
    popular: false,
    discountPrice: 14.50
  },
  {
    name: 'PRO',
    price: 99,
    period: '/month',
    description: 'Serious traders & alpha hunters',
    icon: Zap,
    color: 'green',
    features: [
      { text: 'Everything in BASIC', included: true },
      { text: 'Unlimited scans', included: true },
      { text: '15+ blockchains', included: true },
      { text: '10-day TX history', included: true },
      { text: 'Full Muncher Maps (2D)', included: true },
      { text: 'Advanced bundle detection', included: true },
      { text: 'Fresh wallet analysis', included: true },
      { text: 'Sniper tracking', included: true },
      { text: 'Copy trading detection', included: true },
      { text: 'AI risk reports', included: true },
      { text: '@rmi_alpha_bot access', included: true },
      { text: '15 custom alerts', included: true },
      { text: 'Rug Pull Rehab (20% off)', included: true },
    ],
    cta: 'Go Pro',
    popular: true,
    discountPrice: 49.50
  },
  {
    name: 'ELITE',
    price: 299,
    period: '/month',
    description: 'Whales, pros & full Muncher Maps',
    icon: Network,
    color: 'purple',
    features: [
      { text: 'Everything in PRO', included: true },
      { text: '3D Muncher Maps', included: true },
      { text: '6 degrees of separation', included: true },
      { text: 'Time-travel mode', included: true },
      { text: 'Predictive analytics', included: true },
      { text: 'Whale intelligence', included: true },
      { text: 'Social OSINT', included: true },
      { text: 'MEV detection', included: true },
      { text: 'Flash loan detection', included: true },
      { text: 'Unlimited alerts', included: true },
      { text: '50,000 API calls/mo', included: true },
      { text: '1 free Rehab class/mo', included: true },
      { text: 'White-label reports', included: true },
    ],
    cta: 'Become Elite',
    popular: false,
    discountPrice: 149.50
  }
];

const ENTERPRISE_FEATURES = [
  'Everything in ELITE',
  'Unlimited Muncher Maps nodes',
  'Real-time websocket streaming',
  'Custom ML models',
  'Private cluster database',
  'Custom chain support',
  'SLA guarantee (99.9% uptime)',
  'Dedicated account manager',
  'Forensic audit reports',
  'Court-admissible evidence',
  'Custom integrations',
  'On-premise deployment option',
];

export default function PricingPage() {
  const [isAnnual, setIsAnnual] = useState(false);
  const [showEnterprise, setShowEnterprise] = useState(false);
  const [showCRMFaq, setShowCRMFaq] = useState(false);
  
  const isCRMHolder = false; // Would check wallet connection in real app

  const getAnnualPrice = (monthly: number) => Math.round(monthly * 10); // 2 months free
  const getAnnualDiscount = (monthly: number) => Math.round(monthly * 2); // Save 2 months

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl sm:text-4xl font-bold text-white mb-4">
          Simple, Transparent <span className="text-green-400">Pricing</span>
        </h1>
        <p className="text-gray-400 max-w-2xl mx-auto">
          Start free, upgrade when you need more power. No hidden fees, cancel anytime.
        </p>
      </div>

      {/* CRM v1 Holder Banner */}
      <div className="max-w-4xl mx-auto p-6 bg-gradient-to-r from-green-500/20 via-blue-500/20 to-purple-500/20 border border-green-500/30 rounded-xl">
        <div className="flex flex-col md:flex-row items-center gap-6">
          <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center flex-shrink-0">
            <Star className="w-8 h-8 text-green-400" />
          </div>
          <div className="flex-1 text-center md:text-left">
            <h2 className="text-xl font-bold text-white mb-2">
              $CRM v1 Holders: 50% Lifetime Discount
            </h2>
            <p className="text-gray-300 mb-2">
              Early supporters receive founder pricing forever. Verify your wallet to claim 
              50% off any tier for life, plus airdrop eligibility for $CRM v2.
            </p>
            <div className="flex flex-wrap items-center justify-center md:justify-start gap-4 text-sm">
              <span className="flex items-center gap-1 text-green-400">
                <Check className="w-4 h-4" /> 50% lifetime discount
              </span>
              <span className="flex items-center gap-1 text-green-400">
                <Check className="w-4 h-4" /> Airdrop eligible (20% of v2 supply)
              </span>
              <span className="flex items-center gap-1 text-green-400">
                <Check className="w-4 h-4" /> Founder status badge
              </span>
            </div>
          </div>
          <button className="px-6 py-3 bg-green-500 hover:bg-green-600 text-black font-bold rounded-lg transition-colors whitespace-nowrap flex items-center gap-2">
            <Wallet className="w-5 h-5" />
            Verify & Claim
          </button>
        </div>

        {/* FAQ Toggle */}
        <button 
          onClick={() => setShowCRMFaq(!showCRMFaq)}
          className="mt-4 text-sm text-gray-400 hover:text-white flex items-center gap-1"
        >
          {showCRMFaq ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          How do I verify my $CRM v1 tokens?
        </button>
        {showCRMFaq && (
          <div className="mt-4 p-4 bg-gray-900/50 rounded-lg text-sm text-gray-300">
            <p className="mb-2">Connect the wallet holding your $CRM v1 tokens. We check:</p>
            <ul className="space-y-1 text-gray-400">
              <li>• Token balance on Ethereum mainnet</li>
              <li>• Purchase history (v1 ICO participants get priority)</li>
              <li>• Holding duration (longer = better rewards)</li>
            </ul>
            <p className="mt-2 text-green-400">Discount applies automatically after verification.</p>
          </div>
        )}
      </div>

      {/* Billing Toggle */}
      <div className="flex items-center justify-center gap-4">
        <span className={`text-sm ${!isAnnual ? 'text-white' : 'text-gray-400'}`}>Monthly</span>
        <button
          onClick={() => setIsAnnual(!isAnnual)}
          className="relative w-14 h-7 bg-gray-700 rounded-full transition-colors"
        >
          <div className={`absolute top-1 w-5 h-5 bg-green-400 rounded-full transition-all ${isAnnual ? 'left-8' : 'left-1'}`} />
        </button>
        <span className={`text-sm ${isAnnual ? 'text-white' : 'text-gray-400'}`}>
          Annual <span className="text-green-400">(Save 17%)</span>
        </span>
      </div>

      {/* Pricing Cards */}
      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
        {TIERS.map((tier) => {
          const price = isAnnual ? getAnnualPrice(tier.price) : tier.price;
          const discountPrice = tier.discountPrice ? (isAnnual ? getAnnualPrice(tier.discountPrice) : tier.discountPrice) : null;
          
          return (
            <div 
              key={tier.name}
              className={`relative p-6 rounded-xl border ${
                tier.popular 
                  ? 'bg-gradient-to-b from-green-500/10 to-transparent border-green-500/50' 
                  : 'bg-[#12121a] border-gray-800'
              }`}
            >
              {tier.popular && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-4 py-1 bg-green-500 text-black text-xs font-bold rounded-full">
                  MOST POPULAR
                </div>
              )}
              
              {/* Tier Header */}
              <div className="mb-6">
                <div className={`w-12 h-12 rounded-lg bg-${tier.color}-500/10 flex items-center justify-center mb-4`}>
                  <tier.icon className={`w-6 h-6 text-${tier.color}-400`} />
                </div>
                <h3 className="text-lg font-semibold">{tier.name}</h3>
                <div className="flex items-baseline gap-1 mt-2">
                  {discountPrice && isCRMHolder ? (
                    <>
                      <span className="text-3xl font-bold text-green-400">${discountPrice}</span>
                      <span className="text-lg text-gray-500 line-through">${price}</span>
                    </>
                  ) : (
                    <span className="text-3xl font-bold text-white">${price}</span>
                  )}
                  <span className="text-gray-400">{isAnnual ? '/year' : tier.period}</span>
                </div>
                {isAnnual && tier.price > 0 && (
                  <p className="text-xs text-green-400 mt-1">
                    Save ${getAnnualDiscount(discountPrice || price)} with annual billing
                  </p>
                )}
                <p className="text-gray-500 text-sm mt-2">{tier.description}</p>
              </div>

              {/* Features */}
              <ul className="space-y-3 mb-8">
                {tier.features.map((feature, idx) => (
                  <li key={idx} className="flex items-start gap-3">
                    {feature.included ? (
                      <Check className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                    ) : (
                      <X className="w-5 h-5 text-gray-600 flex-shrink-0 mt-0.5" />
                    )}
                    <span className={feature.included ? 'text-gray-300 text-sm' : 'text-gray-600 text-sm'}>
                      {feature.text}
                    </span>
                  </li>
                ))}
              </ul>

              {/* CTA */}
              <button 
                className={`w-full py-3 rounded-lg font-semibold transition-colors ${
                  tier.popular
                    ? 'bg-green-500 hover:bg-green-600 text-black'
                    : 'bg-gray-800 hover:bg-gray-700 text-white'
                }`}
              >
                {tier.cta}
              </button>
            </div>
          );
        })}
      </div>

      {/* Enterprise */}
      <div className="p-8 bg-gradient-to-r from-purple-500/10 to-blue-500/10 border border-purple-500/30 rounded-xl">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="text-center md:text-left">
            <div className="flex items-center justify-center md:justify-start gap-2 mb-2">
              <Network className="w-6 h-6 text-purple-400" />
              <h3 className="text-xl font-bold">Enterprise</h3>
            </div>
            <p className="text-gray-400">Custom solutions for funds, security firms, and auditors</p>
          </div>
          <div className="text-center md:text-right">
            <p className="text-2xl font-bold text-white">Custom Pricing</p>
            <p className="text-gray-400 text-sm">Contact sales</p>
          </div>
        </div>
        
        <button 
          onClick={() => setShowEnterprise(!showEnterprise)}
          className="mt-6 text-purple-400 hover:text-purple-300 flex items-center gap-1"
        >
          {showEnterprise ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
          {showEnterprise ? 'Hide features' : 'View enterprise features'}
        </button>
        
        {showEnterprise && (
          <div className="mt-6 grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {ENTERPRISE_FEATURES.map((feature, idx) => (
              <div key={idx} className="flex items-center gap-2">
                <Check className="w-5 h-5 text-purple-400" />
                <span className="text-gray-300 text-sm">{feature}</span>
              </div>
            ))}
          </div>
        )}
        
        <div className="mt-6 pt-6 border-t border-purple-500/20 flex flex-col sm:flex-row gap-4 justify-center">
          <button className="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white font-semibold rounded-lg flex items-center justify-center gap-2">
            Contact Sales
            <ArrowRight className="w-5 h-5" />
          </button>
          <button className="px-6 py-3 bg-gray-800 hover:bg-gray-700 text-white font-semibold rounded-lg">
            Schedule Demo
          </button>
        </div>
      </div>

      {/* FAQ Section */}
      <div className="max-w-3xl mx-auto">
        <h2 className="text-2xl font-bold text-center mb-8">Frequently Asked Questions</h2>
        <div className="space-y-4">
          {[
            {
              q: "Can I upgrade or downgrade anytime?",
              a: "Yes, you can change your plan at any time. Upgrades take effect immediately, downgrades at the end of your billing cycle."
            },
            {
              q: "What payment methods do you accept?",
              a: "We accept credit cards, PayPal, and cryptocurrency (ETH, BTC, USDC, USDT) for all tiers."
            },
            {
              q: "Is there a free trial for paid tiers?",
              a: "We offer a 7-day money-back guarantee instead of a trial. If you're not satisfied, contact us for a full refund."
            },
            {
              q: "How do I claim the CRM v1 holder discount?",
              a: "Connect your wallet holding $CRM v1 tokens. The discount will be automatically applied at checkout."
            },
            {
              q: "What's included in the Telegram bot access?",
              a: "All tiers get @rugmunchbot access. PRO+ also gets @rmi_alpha_bot for premium alerts and whale signals."
            }
          ].map((faq, idx) => (
            <div key={idx} className="p-4 bg-[#12121a] border border-gray-800 rounded-lg">
              <h3 className="font-semibold text-white mb-2">{faq.q}</h3>
              <p className="text-gray-400 text-sm">{faq.a}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
