import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Shield, Zap, Crown, Check, ArrowRight, Bitcoin, CreditCard,
  Star, Sparkles, CheckCircle2, Gem, AlertCircle
} from 'lucide-react';
import { useAppStore } from '../store/appStore';
import api from '../services/api';

const TIERS = [
  {
    id: 'tier-basic',
    name: 'Scout',
    price: 29,
    period: 'month',
    description: 'Active traders who need more protection',
    icon: Shield,
    color: 'blue',
    features: [
      '25 wallet scans/day',
      '3 blockchains',
      'The Trenches access',
      'Telegram DM alerts',
      'Basic bundle detection',
      '3 custom price alerts',
    ],
  },
  {
    id: 'tier-pro',
    name: 'Operative',
    price: 99,
    period: 'month',
    description: 'Serious traders & alpha hunters',
    icon: Zap,
    color: 'emerald',
    popular: true,
    features: [
      'Unlimited scans',
      '15+ blockchains',
      'Full Muncher Maps',
      'Daily Rundown briefing',
      'Meme Radar signals',
      'Sniper tracking',
      'AI risk reports',
      'Rug Pull Rehab (20% off)',
    ],
  },
  {
    id: 'tier-elite',
    name: 'Syndicate',
    price: 299,
    period: 'month',
    description: 'Whales, pros & full intelligence',
    icon: Crown,
    color: 'purple',
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
  },
];

export default function TierCheckout() {
  const [selectedTier, setSelectedTier] = useState<string>('tier-pro');
  const [paymentMethod, setPaymentMethod] = useState<'crypto' | 'card'>('crypto');
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'yearly'>('monthly');
  const [step, setStep] = useState<'select' | 'checkout' | 'success'>('select');
  const [loading, setLoading] = useState(false);
  const [chargeData, setChargeData] = useState<any>(null);
  const user = useAppStore((state) => state.user);

  const tier = TIERS.find(t => t.id === selectedTier);
  const finalPrice = billingCycle === 'yearly' && tier ? Math.round(tier.price * 10) : tier?.price;

  const handleCheckout = async () => {
    if (!tier) return;
    setLoading(true);
    try {
      const result = await api.createPaymentCharge(tier.id, {
        user_id: user?.id || 'guest',
        tier: tier.id.replace('tier-', ''),
        billing_cycle: billingCycle,
      });
      setChargeData(result);
      setStep('success');
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-slate-200">
      {/* Hero */}
      <div className="relative overflow-hidden border-b border-purple-900/20">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,rgba(139,92,246,0.06),transparent_70%)]" />
        <div className="max-w-5xl mx-auto px-4 sm:px-6 py-10 relative">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded bg-purple-950/60 border border-purple-800/40 flex items-center justify-center">
              <Gem className="w-5 h-5 text-purple-400" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white tracking-tight">Upgrade Your Access</h1>
              <p className="text-xs text-purple-400/70 font-mono tracking-wider uppercase">Platform Tiers</p>
            </div>
          </div>
          <p className="text-slate-400 text-sm max-w-xl">
            Unlock the full power of Rug Munch Intel. Pay monthly or save 2 months with annual billing.
          </p>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-4 sm:px-6 py-8">
        {step === 'select' && (
          <div className="space-y-6">
            {/* Billing Toggle */}
            <div className="flex items-center justify-center gap-3 mb-2">
              <button
                onClick={() => setBillingCycle('monthly')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${billingCycle === 'monthly' ? 'bg-purple-600 text-white' : 'bg-slate-800/50 text-slate-400 hover:text-white'}`}
              >
                Monthly
              </button>
              <button
                onClick={() => setBillingCycle('yearly')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all flex items-center gap-2 ${billingCycle === 'yearly' ? 'bg-purple-600 text-white' : 'bg-slate-800/50 text-slate-400 hover:text-white'}`}
              >
                Yearly <span className="text-[10px] bg-emerald-500/20 text-emerald-400 px-1.5 py-0.5 rounded">Save 17%</span>
              </button>
            </div>

            {/* Tier Cards */}
            <div className="grid md:grid-cols-3 gap-4">
              {TIERS.map((t, i) => {
                const Icon = t.icon;
                const isSelected = selectedTier === t.id;
                const price = billingCycle === 'yearly' ? Math.round(t.price * 10) : t.price;
                const colors: Record<string, any> = {
                  blue: { border: 'border-blue-500/30', bg: 'bg-blue-500/5', text: 'text-blue-400', btn: 'bg-blue-600 hover:bg-blue-500' },
                  emerald: { border: 'border-emerald-500/30', bg: 'bg-emerald-500/5', text: 'text-emerald-400', btn: 'bg-emerald-600 hover:bg-emerald-500' },
                  purple: { border: 'border-purple-500/30', bg: 'bg-purple-500/5', text: 'text-purple-400', btn: 'bg-purple-600 hover:bg-purple-500' },
                };
                const c = colors[t.color];
                return (
                  <motion.div
                    key={t.id}
                    initial={{ opacity: 0, y: 12 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.08 }}
                    onClick={() => setSelectedTier(t.id)}
                    className={`relative bg-slate-900/40 border rounded-xl p-5 cursor-pointer transition-all ${
                      isSelected ? `${c.border} ${c.bg}` : 'border-slate-800/50 hover:border-slate-700/50'
                    }`}
                  >
                    {t.popular && (
                      <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                        <span className="bg-gradient-to-r from-purple-600 to-purple-500 text-white text-[10px] font-bold px-3 py-1 rounded-full">
                          MOST POPULAR
                        </span>
                      </div>
                    )}
                    <div className="flex items-center gap-3 mb-4">
                      <div className={`w-9 h-9 rounded-lg ${c.bg} border ${c.border} flex items-center justify-center`}>
                        <Icon className={`w-4 h-4 ${c.text}`} />
                      </div>
                      <div>
                        <h3 className="text-sm font-bold text-white">{t.name}</h3>
                        <p className="text-[10px] text-slate-500">{t.description}</p>
                      </div>
                    </div>
                    <div className="mb-4">
                      <span className="text-2xl font-bold text-white">${price}</span>
                      <span className="text-xs text-slate-500">/{billingCycle === 'yearly' ? 'year' : 'month'}</span>
                      {billingCycle === 'yearly' && (
                        <div className="text-[10px] text-slate-500 line-through">${t.price * 12}/year</div>
                      )}
                    </div>
                    <div className="space-y-2">
                      {t.features.map((f, j) => (
                        <div key={j} className="flex items-start gap-2">
                          <Check className={`w-3.5 h-3.5 ${c.text} mt-0.5 flex-shrink-0`} />
                          <span className="text-[11px] text-slate-300">{f}</span>
                        </div>
                      ))}
                    </div>
                  </motion.div>
                );
              })}
            </div>

            <div className="text-center">
              <button
                onClick={() => setStep('checkout')}
                className="px-8 py-3 rounded-lg text-sm font-bold text-white bg-purple-600 hover:bg-purple-500 transition-all flex items-center gap-2 mx-auto"
              >
                Upgrade to {tier?.name} <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        {step === 'checkout' && tier && (
          <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="max-w-md mx-auto">
            <button onClick={() => setStep('select')} className="text-xs text-slate-500 hover:text-white mb-4">← Back</button>
            <div className="bg-slate-900/60 border border-slate-800/60 rounded-xl p-6">
              <h3 className="text-lg font-bold text-white mb-4">Complete Upgrade</h3>

              <div className="bg-slate-800/40 border border-purple-800/20 rounded-lg p-4 mb-5">
                <div className="flex justify-between mb-1">
                  <span className="text-sm text-white">{tier.name} Tier</span>
                  <span className="text-sm font-bold text-white">${finalPrice}</span>
                </div>
                <p className="text-xs text-slate-500">{billingCycle === 'yearly' ? 'Annual billing' : 'Monthly billing'} • Cancel anytime</p>
              </div>

              <div className="grid grid-cols-2 gap-2 mb-5">
                <button onClick={() => setPaymentMethod('crypto')} className={`flex items-center gap-2 px-4 py-3 rounded-lg border text-sm font-medium transition-all ${paymentMethod === 'crypto' ? 'border-purple-500/50 bg-purple-950/20 text-purple-400' : 'border-slate-700/50 bg-slate-800/30 text-slate-400'}`}>
                  <Bitcoin className="w-4 h-4" /> Crypto
                </button>
                <button onClick={() => setPaymentMethod('card')} className={`flex items-center gap-2 px-4 py-3 rounded-lg border text-sm font-medium transition-all ${paymentMethod === 'card' ? 'border-purple-500/50 bg-purple-950/20 text-purple-400' : 'border-slate-700/50 bg-slate-800/30 text-slate-400'}`}>
                  <CreditCard className="w-4 h-4" /> Card
                </button>
              </div>

              <button
                onClick={handleCheckout}
                disabled={loading}
                className="w-full py-3 rounded-lg text-sm font-bold text-white bg-purple-600 hover:bg-purple-500 disabled:opacity-50 transition-all flex items-center justify-center gap-2"
              >
                {loading ? 'Processing...' : `Pay $${finalPrice}`}
                {!loading && <ArrowRight className="w-4 h-4" />}
              </button>
            </div>
          </motion.div>
        )}

        {step === 'success' && chargeData && (
          <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="max-w-md mx-auto text-center">
            <div className="bg-slate-900/60 border border-slate-800/60 rounded-xl p-8">
              <CheckCircle2 className="w-12 h-12 text-emerald-400 mx-auto mb-4" />
              <h2 className="text-xl font-bold text-white mb-2">Welcome to {tier?.name}</h2>
              <p className="text-sm text-slate-400 mb-5">
                Your tier upgrade is processing. You'll receive access within minutes.
              </p>
              <div className="bg-slate-800/40 rounded-lg p-3 mb-5 text-left">
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-slate-500">Tier</span>
                  <span className="text-white font-bold">{tier?.name}</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-slate-500">Billing</span>
                  <span className="text-white font-bold">{billingCycle === 'yearly' ? 'Annual' : 'Monthly'}</span>
                </div>
              </div>
              <button onClick={() => setStep('select')} className="text-sm text-purple-400 hover:text-purple-300">
                Done
              </button>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}
