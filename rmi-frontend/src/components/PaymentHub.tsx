import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  CreditCard, Wallet, ArrowRight, Shield, Zap, Crown, Star,
  GraduationCap, Newspaper, Check, Sparkles, Bitcoin, DollarSign,
  Clock, Users, BookOpen, TrendingUp, Lock, Unlock, Gem,
  ChevronRight, AlertCircle, ExternalLink, Copy, CheckCircle2
} from 'lucide-react';
import { useAppStore } from '../store/appStore';
import api from '../services/api';

// ═══════════════════════════════════════════════════════════
// PRODUCT CATALOG
// ═══════════════════════════════════════════════════════════

interface Product {
  id: string;
  name: string;
  description: string;
  amount: string;
  currency: string;
  category: string;
  popular?: boolean;
  features?: string[];
  icon?: any;
  color?: string;
}

const TIERS: Product[] = [
  {
    id: 'tier-basic',
    name: 'Scout',
    description: 'Active traders who need more protection',
    amount: '29.00',
    currency: 'USD',
    category: 'tier',
    features: [
      '25 wallet scans/day',
      '3 blockchains',
      'The Trenches access',
      'Telegram DM alerts',
      'Basic bundle detection',
      '3 custom price alerts',
    ],
    icon: Shield,
    color: 'blue',
  },
  {
    id: 'tier-pro',
    name: 'Operative',
    description: 'Serious traders & alpha hunters',
    amount: '99.00',
    currency: 'USD',
    category: 'tier',
    popular: true,
    features: [
      'Everything in Scout',
      'Unlimited scans',
      '15+ blockchains',
      'Full Muncher Maps',
      'Daily Rundown briefing',
      'Meme Radar signals',
      'Sniper tracking',
      'AI risk reports',
    ],
    icon: Zap,
    color: 'emerald',
  },
  {
    id: 'tier-elite',
    name: 'Syndicate',
    description: 'Whales, pros & full intelligence',
    amount: '299.00',
    currency: 'USD',
    category: 'tier',
    features: [
      'Everything in Operative',
      '3D Muncher Maps',
      'Butcher\'s Block access',
      'Whale Watchers PRO',
      'Smart money flows (Nansen)',
      'Helius whale profiles',
      'Syndicate scanning',
      'White-label reports',
      '1-on-1 advisory session',
    ],
    icon: Crown,
    color: 'purple',
  },
];

const REHAB_PACKAGES: Product[] = [
  {
    id: 'rehab-class',
    name: 'Single Class',
    description: '2-hour live session with certified instructor',
    amount: '100.00',
    currency: 'USD',
    category: 'rehab',
    features: ['Honeypot Detection 101', 'Reading Smart Contracts', 'Whale Tracking Mastery', 'Small group (max 20)'],
    icon: GraduationCap,
    color: 'amber',
  },
  {
    id: 'rehab-bundle-3',
    name: '3-Class Bundle',
    description: 'Save $50. Three sessions of your choice.',
    amount: '250.00',
    currency: 'USD',
    category: 'rehab',
    popular: true,
    features: ['All 3 class topics', 'Save 17%', 'Priority booking', 'Session recordings included'],
    icon: BookOpen,
    color: 'orange',
  },
];

const NEWSLETTER_PLANS: Product[] = [
  {
    id: 'newsletter-daily',
    name: 'Daily Munch',
    description: 'Daily market briefing delivered to your inbox',
    amount: '5.00',
    currency: 'USD',
    category: 'newsletter',
    features: ['Rug alerts & scam warnings', 'Whale movement summary', 'Meme momentum radar', 'Published to Mirror.xyz'],
    icon: Newspaper,
    color: 'cyan',
  },
  {
    id: 'newsletter-quarterly',
    name: 'Quarterly Pass',
    description: '3 months of daily briefings. Best value.',
    amount: '36.00',
    currency: 'USD',
    category: 'newsletter',
    popular: true,
    features: ['Save 20% vs monthly', 'All Daily Munch features', 'Exclusive quarterly deep-dive', 'Early access to new features'],
    icon: Star,
    color: 'indigo',
  },
];

// ═══════════════════════════════════════════════════════════
// COLOR MAPS
// ═══════════════════════════════════════════════════════════

const COLOR_MAP: Record<string, { border: string; bg: string; text: string; gradient: string; button: string }> = {
  blue: {
    border: 'border-blue-500/30',
    bg: 'bg-blue-500/5',
    text: 'text-blue-400',
    gradient: 'from-blue-500/10 to-transparent',
    button: 'bg-blue-600 hover:bg-blue-500',
  },
  emerald: {
    border: 'border-emerald-500/30',
    bg: 'bg-emerald-500/5',
    text: 'text-emerald-400',
    gradient: 'from-emerald-500/10 to-transparent',
    button: 'bg-emerald-600 hover:bg-emerald-500',
  },
  purple: {
    border: 'border-purple-500/30',
    bg: 'bg-purple-500/5',
    text: 'text-purple-400',
    gradient: 'from-purple-500/10 to-transparent',
    button: 'bg-purple-600 hover:bg-purple-500',
  },
  amber: {
    border: 'border-amber-500/30',
    bg: 'bg-amber-500/5',
    text: 'text-amber-400',
    gradient: 'from-amber-500/10 to-transparent',
    button: 'bg-amber-600 hover:bg-amber-500',
  },
  orange: {
    border: 'border-orange-500/30',
    bg: 'bg-orange-500/5',
    text: 'text-orange-400',
    gradient: 'from-orange-500/10 to-transparent',
    button: 'bg-orange-600 hover:bg-orange-500',
  },
  cyan: {
    border: 'border-cyan-500/30',
    bg: 'bg-cyan-500/5',
    text: 'text-cyan-400',
    gradient: 'from-cyan-500/10 to-transparent',
    button: 'bg-cyan-600 hover:bg-cyan-500',
  },
  indigo: {
    border: 'border-indigo-500/30',
    bg: 'bg-indigo-500/5',
    text: 'text-indigo-400',
    gradient: 'from-indigo-500/10 to-transparent',
    button: 'bg-indigo-600 hover:bg-indigo-500',
  },
};

// ═══════════════════════════════════════════════════════════
// MAIN COMPONENT
// ═══════════════════════════════════════════════════════════

export default function PaymentHub() {
  const [activeTab, setActiveTab] = useState<'tiers' | 'rehab' | 'newsletter'>('tiers');
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [checkoutStep, setCheckoutStep] = useState<'select' | 'checkout' | 'processing' | 'success'>('select');
  const [chargeData, setChargeData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [demoMode, setDemoMode] = useState(false);
  const user = useAppStore((state) => state.user);
  const setCurrentPage = useAppStore((state) => state.setCurrentPage);

  useEffect(() => {
    api.getPaymentProducts().then(r => setDemoMode(r.demo_mode)).catch(() => setDemoMode(true));
  }, []);

  const startCheckout = async (product: Product) => {
    setSelectedProduct(product);
    setCheckoutStep('checkout');
  };

  const createCharge = async () => {
    if (!selectedProduct) return;
    setLoading(true);
    try {
      const metadata: Record<string, any> = {
        user_id: user?.id || 'guest',
        product_id: selectedProduct.id,
      };
      if (selectedProduct.category === 'tier') metadata.tier = selectedProduct.id.replace('tier-', '');
      const result = await api.createPaymentCharge(selectedProduct.id, metadata);
      setChargeData(result);
      setCheckoutStep('success');
    } catch (e) {
      console.error('Payment error:', e);
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: 'tiers' as const, label: 'Platform Tiers', icon: Crown, desc: 'Upgrade your intelligence access' },
    { id: 'rehab' as const, label: 'Rug Pull Rehab', icon: GraduationCap, desc: 'Learn to never get rugged again' },
    { id: 'newsletter' as const, label: 'The Daily Munch', icon: Newspaper, desc: 'Daily briefings + Mirror publishing' },
  ];

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-slate-200">
      {/* HERO */}
      <div className="relative overflow-hidden border-b border-slate-800/40">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,rgba(139,92,246,0.06),transparent_70%)]" />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-10 relative">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded bg-purple-950/60 border border-purple-800/40 flex items-center justify-center">
              <Gem className="w-5 h-5 text-purple-400" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white tracking-tight">Monetization Hub</h1>
              <p className="text-xs text-purple-400/70 font-mono tracking-wider uppercase">Payments, Subscriptions & Bookings</p>
            </div>
          </div>
          <p className="text-slate-400 text-sm max-w-xl">
            Unlock premium intelligence, book rehab sessions, and subscribe to The Daily Munch newsletter. 
            Pay with crypto or card.
          </p>
          {demoMode && (
            <div className="mt-3 inline-flex items-center gap-2 px-3 py-1.5 bg-amber-950/30 border border-amber-800/30 rounded text-[11px] text-amber-400">
              <AlertCircle className="w-3 h-3" />
              Demo Mode — Add COINBASE_COMMERCE_API_KEY to enable live payments
            </div>
          )}
        </div>
      </div>

      {/* TABS */}
      <div className="border-b border-slate-800/60 bg-[#0d0d14]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="flex gap-1 overflow-x-auto py-1">
            {tabs.map(tab => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => { setActiveTab(tab.id); setCheckoutStep('select'); setSelectedProduct(null); }}
                  className={`flex items-center gap-2 px-4 py-2.5 text-xs font-medium rounded-t transition-all whitespace-nowrap ${
                    activeTab === tab.id
                      ? 'text-purple-400 border-b-2 border-purple-500 bg-purple-950/20'
                      : 'text-slate-500 hover:text-slate-300 hover:bg-slate-800/30'
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  {tab.label}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* CONTENT */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8">
        <AnimatePresence mode="wait">
          {checkoutStep === 'select' && (
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.2 }}
            >
              {activeTab === 'tiers' && <ProductGrid products={TIERS} onSelect={startCheckout} />}
              {activeTab === 'rehab' && <ProductGrid products={REHAB_PACKAGES} onSelect={startCheckout} />}
              {activeTab === 'newsletter' && <ProductGrid products={NEWSLETTER_PLANS} onSelect={startCheckout} />}
            </motion.div>
          )}

          {checkoutStep === 'checkout' && selectedProduct && (
            <CheckoutView
              product={selectedProduct}
              onBack={() => setCheckoutStep('select')}
              onConfirm={createCharge}
              loading={loading}
            />
          )}

          {checkoutStep === 'success' && chargeData && selectedProduct && (
            <SuccessView
              product={selectedProduct}
              charge={chargeData}
              demoMode={demoMode}
              onDone={() => { setCheckoutStep('select'); setSelectedProduct(null); }}
            />
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// PRODUCT GRID
// ═══════════════════════════════════════════════════════════

function ProductGrid({ products, onSelect }: { products: Product[]; onSelect: (p: Product) => void }) {
  return (
    <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
      {products.map((product, i) => {
        const colors = COLOR_MAP[product.color || 'blue'];
        const Icon = product.icon;
        return (
          <motion.div
            key={product.id}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className={`relative bg-slate-900/40 border ${colors.border} rounded-xl overflow-hidden hover:border-opacity-60 transition-all group`}
          >
            {product.popular && (
              <div className="absolute top-0 right-0">
                <div className="bg-gradient-to-l from-purple-600 to-purple-500 text-white text-[10px] font-bold px-3 py-1 rounded-bl-lg">
                  POPULAR
                </div>
              </div>
            )}
            <div className={`p-5 bg-gradient-to-b ${colors.gradient}`}>
              <div className="flex items-center gap-3 mb-4">
                <div className={`w-10 h-10 rounded-lg ${colors.bg} border ${colors.border} flex items-center justify-center`}>
                  <Icon className={`w-5 h-5 ${colors.text}`} />
                </div>
                <div>
                  <h3 className="text-base font-bold text-white">{product.name}</h3>
                  <p className="text-[11px] text-slate-500">{product.description}</p>
                </div>
              </div>

              <div className="mb-4">
                <span className="text-2xl font-bold text-white">${product.amount}</span>
                <span className="text-xs text-slate-500 ml-1">{product.category === 'tier' ? '/month' : product.category === 'newsletter' && product.id.includes('quarterly') ? '/quarter' : product.category === 'newsletter' ? '/month' : ''}</span>
              </div>

              <div className="space-y-2 mb-5">
                {product.features?.map((feat, j) => (
                  <div key={j} className="flex items-start gap-2">
                    <Check className={`w-3.5 h-3.5 ${colors.text} mt-0.5 flex-shrink-0`} />
                    <span className="text-xs text-slate-300">{feat}</span>
                  </div>
                ))}
              </div>

              <button
                onClick={() => onSelect(product)}
                className={`w-full py-2.5 rounded-lg text-sm font-bold text-white transition-all transform hover:scale-[1.02] ${colors.button} flex items-center justify-center gap-2`}
              >
                {product.category === 'tier' ? 'Upgrade' : product.category === 'rehab' ? 'Book Now' : 'Subscribe'}
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// CHECKOUT VIEW
// ═══════════════════════════════════════════════════════════

function CheckoutView({ product, onBack, onConfirm, loading }: {
  product: Product;
  onBack: () => void;
  onConfirm: () => void;
  loading: boolean;
}) {
  const [paymentMethod, setPaymentMethod] = useState<'crypto' | 'card'>('crypto');
  const colors = COLOR_MAP[product.color || 'blue'];

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      className="max-w-lg mx-auto"
    >
      <button onClick={onBack} className="text-xs text-slate-500 hover:text-white mb-4 flex items-center gap-1">
        <ArrowRight className="w-3 h-3 rotate-180" /> Back to products
      </button>

      <div className="bg-slate-900/60 border border-slate-800/60 rounded-xl p-6">
        <h2 className="text-lg font-bold text-white mb-1">Checkout</h2>
        <p className="text-xs text-slate-500 mb-5">Review your selection and choose payment method</p>

        <div className={`bg-slate-800/40 border ${colors.border} rounded-lg p-4 mb-5`}>
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-bold text-white">{product.name}</span>
            <span className="text-sm font-bold text-white">${product.amount}</span>
          </div>
          <p className="text-xs text-slate-400">{product.description}</p>
        </div>

        {/* Payment Method */}
        <div className="mb-5">
          <label className="text-xs text-slate-500 uppercase tracking-wider mb-2 block">Payment Method</label>
          <div className="grid grid-cols-2 gap-2">
            <button
              onClick={() => setPaymentMethod('crypto')}
              className={`flex items-center gap-2 px-4 py-3 rounded-lg border text-sm font-medium transition-all ${
                paymentMethod === 'crypto'
                  ? 'border-purple-500/50 bg-purple-950/20 text-purple-400'
                  : 'border-slate-700/50 bg-slate-800/30 text-slate-400 hover:text-slate-300'
              }`}
            >
              <Bitcoin className="w-4 h-4" />
              Crypto
            </button>
            <button
              onClick={() => setPaymentMethod('card')}
              className={`flex items-center gap-2 px-4 py-3 rounded-lg border text-sm font-medium transition-all ${
                paymentMethod === 'card'
                  ? 'border-purple-500/50 bg-purple-950/20 text-purple-400'
                  : 'border-slate-700/50 bg-slate-800/30 text-slate-400 hover:text-slate-300'
              }`}
            >
              <CreditCard className="w-4 h-4" />
              Card
            </button>
          </div>
          {paymentMethod === 'crypto' && (
            <p className="text-[10px] text-slate-500 mt-1.5">
              Pay with ETH, USDC, SOL, BTC via Coinbase Commerce. No account required.
            </p>
          )}
        </div>

        <button
          onClick={onConfirm}
          disabled={loading}
          className={`w-full py-3 rounded-lg text-sm font-bold text-white transition-all ${colors.button} disabled:opacity-50 flex items-center justify-center gap-2`}
        >
          {loading ? (
            <>
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              Processing...
            </>
          ) : (
            <>
              Pay ${product.amount}
              <ArrowRight className="w-4 h-4" />
            </>
          )}
        </button>
      </div>
    </motion.div>
  );
}

// ═══════════════════════════════════════════════════════════
// SUCCESS VIEW
// ═══════════════════════════════════════════════════════════

function SuccessView({ product, charge, demoMode, onDone }: {
  product: Product;
  charge: any;
  demoMode: boolean;
  onDone: () => void;
}) {
  const [copied, setCopied] = useState(false);
  const colors = COLOR_MAP[product.color || 'blue'];

  const copyChargeId = () => {
    navigator.clipboard.writeText(charge.id || charge.code || '');
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="max-w-lg mx-auto text-center"
    >
      <div className="bg-slate-900/60 border border-slate-800/60 rounded-xl p-8">
        <div className="w-16 h-16 rounded-full bg-emerald-950/40 border border-emerald-800/40 flex items-center justify-center mx-auto mb-4">
          <CheckCircle2 className="w-8 h-8 text-emerald-400" />
        </div>
        <h2 className="text-xl font-bold text-white mb-2">Payment Initiated</h2>
        <p className="text-sm text-slate-400 mb-5">
          {demoMode
            ? 'Demo mode active. In production, this would redirect to Coinbase Commerce checkout.'
            : 'Complete your payment on the Coinbase Commerce checkout page.'}
        </p>

        <div className={`bg-slate-800/40 border ${colors.border} rounded-lg p-4 mb-5 text-left`}>
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-slate-500">Product</span>
            <span className="text-xs font-bold text-white">{product.name}</span>
          </div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-slate-500">Amount</span>
            <span className="text-xs font-bold text-white">${product.amount} {product.currency}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-500">Charge ID</span>
            <button onClick={copyChargeId} className="flex items-center gap-1 text-xs font-mono text-purple-400 hover:text-purple-300">
              {copied ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
              {charge.id || charge.code || 'N/A'}
            </button>
          </div>
        </div>

        {charge.hosted_url && !demoMode && (
          <a
            href={charge.hosted_url}
            target="_blank"
            rel="noopener noreferrer"
            className="block w-full py-3 rounded-lg text-sm font-bold text-white bg-purple-600 hover:bg-purple-500 transition-all mb-3 flex items-center justify-center gap-2"
          >
            Complete Payment <ExternalLink className="w-4 h-4" />
          </a>
        )}

        <button
          onClick={onDone}
          className="text-xs text-slate-500 hover:text-white transition-colors"
        >
          Done
        </button>
      </div>
    </motion.div>
  );
}
