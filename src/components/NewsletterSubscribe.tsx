import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Newspaper, Mail, Check, ArrowRight, Bitcoin, CreditCard,
  Sparkles, Globe, Clock, Zap, Shield, CheckCircle2, ExternalLink
} from 'lucide-react';
import { useAppStore } from '../store/appStore';
import api from '../services/api';

const PLANS = [
  {
    id: 'newsletter-daily',
    name: 'Daily Munch',
    price: 5,
    period: 'month',
    description: 'Daily market briefing with rug alerts, whale moves, and meme momentum.',
    features: [
      'Daily email briefing (Mon-Fri)',
      'Rug pull alerts & warnings',
      'Whale movement summary',
      'Meme momentum radar',
      'Published to Mirror.xyz',
      'Cancel anytime',
    ],
    icon: Newspaper,
    color: 'cyan',
  },
  {
    id: 'newsletter-quarterly',
    name: 'Quarterly Pass',
    price: 36,
    period: 'quarter',
    description: '3 months of daily briefings. Save 20%. Best value.',
    features: [
      'Everything in Daily Munch',
      'Save 20% vs monthly',
      'Exclusive quarterly deep-dive report',
      'Early access to new features',
      'Priority support',
    ],
    icon: Sparkles,
    color: 'indigo',
    popular: true,
  },
];

const SAMPLE_ISSUES = [
  { date: 'Apr 21', title: 'SOSANA V2.0 Migration: Active Threat Update', tag: 'Critical' },
  { date: 'Apr 20', title: 'BONK Whale Accumulation Signals', tag: 'Whale Intel' },
  { date: 'Apr 19', title: '3 Honeypots Detected on Base Chain', tag: 'Alert' },
  { date: 'Apr 18', title: 'Meme Radar: POPCAT Enters Top 10 Momentum', tag: 'Meme' },
];

export default function NewsletterSubscribe() {
  const [selectedPlan, setSelectedPlan] = useState<string>('newsletter-daily');
  const [email, setEmail] = useState('');
  const [paymentMethod, setPaymentMethod] = useState<'crypto' | 'card'>('crypto');
  const [step, setStep] = useState<'plans' | 'details' | 'checkout' | 'success'>('plans');
  const [loading, setLoading] = useState(false);
  const [chargeData, setChargeData] = useState<any>(null);
  const user = useAppStore((state) => state.user);

  const plan = PLANS.find(p => p.id === selectedPlan);

  const handleCheckout = async () => {
    if (!plan) return;
    setLoading(true);
    try {
      const result = await api.createPaymentCharge(plan.id, {
        user_id: user?.id || 'guest',
        email,
        tier: plan.id,
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
      <div className="relative overflow-hidden border-b border-cyan-900/20">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,rgba(6,182,212,0.06),transparent_70%)]" />
        <div className="max-w-5xl mx-auto px-4 sm:px-6 py-10 relative">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded bg-cyan-950/60 border border-cyan-800/40 flex items-center justify-center">
              <Newspaper className="w-5 h-5 text-cyan-400" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white tracking-tight">The Daily Munch</h1>
              <p className="text-xs text-cyan-400/70 font-mono tracking-wider uppercase">Crypto Intelligence Newsletter</p>
            </div>
          </div>
          <p className="text-slate-400 text-sm max-w-xl">
            Daily briefings on rug pulls, whale moves, and meme momentum. Published to Mirror.xyz and delivered to your inbox.
          </p>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-4 sm:px-6 py-8">
        {step === 'plans' && (
          <div className="grid lg:grid-cols-5 gap-8">
            {/* Plans */}
            <div className="lg:col-span-3 space-y-4">
              <h2 className="text-sm font-bold text-white mb-2">Choose Your Plan</h2>
              {PLANS.map((p, i) => (
                <motion.div
                  key={p.id}
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.1 }}
                  onClick={() => setSelectedPlan(p.id)}
                  className={`bg-slate-900/40 border rounded-xl p-5 cursor-pointer transition-all ${
                    selectedPlan === p.id ? 'border-cyan-500/40 bg-cyan-950/10' : 'border-slate-800/50 hover:border-cyan-800/30'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <div className={`w-9 h-9 rounded-lg bg-${p.color}-950/40 border border-${p.color}-800/30 flex items-center justify-center`}>
                        <p.icon className={`w-4 h-4 text-${p.color}-400`} />
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <h3 className="text-sm font-bold text-white">{p.name}</h3>
                          {p.popular && <span className="text-[10px] bg-indigo-600/20 text-indigo-400 px-2 py-0.5 rounded border border-indigo-500/30">BEST VALUE</span>}
                        </div>
                        <p className="text-xs text-slate-400 mt-0.5">{p.description}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-lg font-bold text-white">${p.price}</div>
                      <div className="text-[10px] text-slate-500">/{p.period}</div>
                    </div>
                  </div>
                  <div className="mt-3 grid grid-cols-2 gap-1.5">
                    {p.features.map((f, j) => (
                      <div key={j} className="flex items-center gap-1.5 text-[11px] text-slate-300">
                        <Check className="w-3 h-3 text-cyan-400" /> {f}
                      </div>
                    ))}
                  </div>
                </motion.div>
              ))}

              <button
                onClick={() => setStep('details')}
                className="w-full py-3 rounded-lg text-sm font-bold text-white bg-cyan-600 hover:bg-cyan-500 transition-all flex items-center justify-center gap-2"
              >
                Continue <ArrowRight className="w-4 h-4" />
              </button>
            </div>

            {/* Sample Issues */}
            <div className="lg:col-span-2">
              <div className="bg-slate-900/40 border border-slate-800/50 rounded-xl p-5 sticky top-4">
                <h3 className="text-sm font-bold text-white mb-3 flex items-center gap-2">
                  <Clock className="w-4 h-4 text-cyan-400" /> Recent Issues
                </h3>
                <div className="space-y-3">
                  {SAMPLE_ISSUES.map((issue, i) => (
                    <div key={i} className="border-l-2 border-slate-700 pl-3">
                      <div className="text-[10px] text-slate-500 mb-0.5">{issue.date}</div>
                      <div className="text-xs text-slate-300 leading-snug">{issue.title}</div>
                      <span className={`text-[10px] px-1.5 py-0.5 rounded mt-1 inline-block ${
                        issue.tag === 'Critical' ? 'bg-red-950/40 text-red-400' :
                        issue.tag === 'Whale Intel' ? 'bg-cyan-950/40 text-cyan-400' :
                        issue.tag === 'Alert' ? 'bg-amber-950/40 text-amber-400' :
                        'bg-purple-950/40 text-purple-400'
                      }`}>{issue.tag}</span>
                    </div>
                  ))}
                </div>
                <div className="mt-4 pt-3 border-t border-slate-800/50">
                  <div className="flex items-center gap-2 text-[10px] text-slate-500">
                    <Globe className="w-3 h-3" />
                    Also published on <span className="text-cyan-400">Mirror.xyz</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {step === 'details' && (
          <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="max-w-md mx-auto">
            <button onClick={() => setStep('plans')} className="text-xs text-slate-500 hover:text-white mb-4">← Back</button>
            <div className="bg-slate-900/60 border border-slate-800/60 rounded-xl p-6">
              <h3 className="text-lg font-bold text-white mb-4">Your Details</h3>
              <div className="mb-4">
                <label className="text-xs text-slate-500 uppercase tracking-wider mb-2 block">Email</label>
                <input
                  type="email"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  className="w-full bg-slate-800/50 border border-slate-700/50 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-600 focus:outline-none focus:border-cyan-600/50"
                />
              </div>
              <div className="bg-slate-800/40 rounded-lg p-3 mb-5">
                <div className="flex justify-between text-xs">
                  <span className="text-slate-400">Plan</span>
                  <span className="text-white font-bold">{plan?.name}</span>
                </div>
                <div className="flex justify-between text-xs mt-1">
                  <span className="text-slate-400">Price</span>
                  <span className="text-white font-bold">${plan?.price}/{plan?.period}</span>
                </div>
              </div>
              <button
                onClick={() => setStep('checkout')}
                disabled={!email}
                className="w-full py-3 rounded-lg text-sm font-bold text-white bg-cyan-600 hover:bg-cyan-500 disabled:opacity-40 transition-all flex items-center justify-center gap-2"
              >
                Continue <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </motion.div>
        )}

        {step === 'checkout' && (
          <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="max-w-md mx-auto">
            <button onClick={() => setStep('details')} className="text-xs text-slate-500 hover:text-white mb-4">← Back</button>
            <div className="bg-slate-900/60 border border-slate-800/60 rounded-xl p-6">
              <h3 className="text-lg font-bold text-white mb-4">Payment</h3>
              <div className="bg-slate-800/40 border border-cyan-800/20 rounded-lg p-4 mb-5">
                <div className="flex justify-between mb-1">
                  <span className="text-sm text-white">{plan?.name}</span>
                  <span className="text-sm font-bold text-white">${plan?.price}</span>
                </div>
                <p className="text-xs text-slate-500">{email}</p>
              </div>
              <div className="grid grid-cols-2 gap-2 mb-5">
                <button onClick={() => setPaymentMethod('crypto')} className={`flex items-center gap-2 px-4 py-3 rounded-lg border text-sm font-medium transition-all ${paymentMethod === 'crypto' ? 'border-cyan-500/50 bg-cyan-950/20 text-cyan-400' : 'border-slate-700/50 bg-slate-800/30 text-slate-400'}`}>
                  <Bitcoin className="w-4 h-4" /> Crypto
                </button>
                <button onClick={() => setPaymentMethod('card')} className={`flex items-center gap-2 px-4 py-3 rounded-lg border text-sm font-medium transition-all ${paymentMethod === 'card' ? 'border-cyan-500/50 bg-cyan-950/20 text-cyan-400' : 'border-slate-700/50 bg-slate-800/30 text-slate-400'}`}>
                  <CreditCard className="w-4 h-4" /> Card
                </button>
              </div>
              <button
                onClick={handleCheckout}
                disabled={loading}
                className="w-full py-3 rounded-lg text-sm font-bold text-white bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 transition-all flex items-center justify-center gap-2"
              >
                {loading ? 'Processing...' : `Subscribe $${plan?.price}`}
                {!loading && <ArrowRight className="w-4 h-4" />}
              </button>
            </div>
          </motion.div>
        )}

        {step === 'success' && chargeData && (
          <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="max-w-md mx-auto text-center">
            <div className="bg-slate-900/60 border border-slate-800/60 rounded-xl p-8">
              <CheckCircle2 className="w-12 h-12 text-emerald-400 mx-auto mb-4" />
              <h2 className="text-xl font-bold text-white mb-2">Welcome to The Daily Munch</h2>
              <p className="text-sm text-slate-400 mb-5">
                Your subscription is active. Check your inbox for the first briefing and your Mirror.xyz reader link.
              </p>
              <div className="bg-slate-800/40 rounded-lg p-3 mb-5 text-left">
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-slate-500">Plan</span>
                  <span className="text-white font-bold">{plan?.name}</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-slate-500">Email</span>
                  <span className="text-white font-bold">{email}</span>
                </div>
              </div>
              <button onClick={() => setStep('plans')} className="text-sm text-cyan-400 hover:text-cyan-300">
                Done
              </button>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}
