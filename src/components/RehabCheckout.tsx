import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  GraduationCap, Calendar, Clock, Users, Check, ArrowRight,
  Bitcoin, CreditCard, Shield, AlertTriangle, BookOpen,
  Copy, CheckCircle2, Star
} from 'lucide-react';
import { useAppStore } from '../store/appStore';
import api from '../services/api';

const CLASSES = [
  {
    id: 'honeypot-101',
    title: 'Honeypot Detection 101',
    description: 'Spot hidden mint functions, blacklists, and sell restrictions before you buy.',
    instructor: 'RugHunter_007',
    duration: '2 hours',
    spots: 8,
    totalSpots: 20,
    price: 100,
    level: 'Beginner',
    topics: ['Contract code red flags', 'Liquidity analysis', 'Blacklist detection', 'Tool walkthrough'],
  },
  {
    id: 'contract-reading',
    title: 'Reading Smart Contracts',
    description: 'Understand what you\'re actually agreeing to when you approve a contract.',
    instructor: 'DeFi_Detective',
    duration: '2 hours',
    spots: 12,
    totalSpots: 20,
    price: 100,
    level: 'Intermediate',
    topics: ['Function signatures', 'Approval risks', 'Upgradeable contracts', 'Proxy patterns'],
  },
  {
    id: 'whale-tracking',
    title: 'Whale Tracking Mastery',
    description: 'Follow smart money movements and understand accumulation vs distribution.',
    instructor: 'WhaleWatcher',
    duration: '2 hours',
    spots: 5,
    totalSpots: 15,
    price: 100,
    level: 'Advanced',
    topics: ['Wallet clustering', 'On-chain signals', 'Copy-trading detection', 'Exit timing'],
  },
];

export default function RehabCheckout() {
  const [selectedClass, setSelectedClass] = useState<string | null>(null);
  const [selectedDate, setSelectedDate] = useState<string>('');
  const [paymentMethod, setPaymentMethod] = useState<'crypto' | 'card'>('crypto');
  const [step, setStep] = useState<'select' | 'details' | 'checkout' | 'success'>('select');
  const [loading, setLoading] = useState(false);
  const [chargeData, setChargeData] = useState<any>(null);
  const user = useAppStore((state) => state.user);

  const selectedClassObj = CLASSES.find(c => c.id === selectedClass);

  const handleCheckout = async () => {
    if (!selectedClassObj) return;
    setLoading(true);
    try {
      const result = await api.createPaymentCharge('rehab-class', {
        user_id: user?.id || 'guest',
        class_type: selectedClassObj.id,
        date: selectedDate,
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
      <div className="relative overflow-hidden border-b border-amber-900/20">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,rgba(245,158,11,0.06),transparent_70%)]" />
        <div className="max-w-5xl mx-auto px-4 sm:px-6 py-10 relative">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded bg-amber-950/60 border border-amber-800/40 flex items-center justify-center">
              <GraduationCap className="w-5 h-5 text-amber-400" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white tracking-tight">Rug Pull Rehab</h1>
              <p className="text-xs text-amber-400/70 font-mono tracking-wider uppercase">Book Your Session</p>
            </div>
          </div>
          <p className="text-slate-400 text-sm max-w-xl">
            Learn from the best. 2-hour live sessions with certified instructors who've tracked, traced, and exposed real rug pulls.
          </p>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-4 sm:px-6 py-8">
        {step === 'select' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between mb-2">
              <h2 className="text-sm font-bold text-white">Select a Class</h2>
              <span className="text-xs text-slate-500">$100 per session</span>
            </div>
            <div className="grid gap-4 md:grid-cols-3">
              {CLASSES.map((cls, i) => (
                <motion.div
                  key={cls.id}
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.08 }}
                  onClick={() => { setSelectedClass(cls.id); setStep('details'); }}
                  className={`bg-slate-900/40 border rounded-xl p-5 cursor-pointer transition-all hover:scale-[1.01] ${
                    selectedClass === cls.id ? 'border-amber-500/40 bg-amber-950/10' : 'border-slate-800/50 hover:border-amber-800/30'
                  }`}
                >
                  <div className="flex items-center justify-between mb-3">
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                      cls.level === 'Beginner' ? 'bg-emerald-950/40 text-emerald-400 border border-emerald-800/30' :
                      cls.level === 'Intermediate' ? 'bg-amber-950/40 text-amber-400 border border-amber-800/30' :
                      'bg-red-950/40 text-red-400 border border-red-800/30'
                    }`}>{cls.level}</span>
                    <span className="text-xs font-bold text-white">${cls.price}</span>
                  </div>
                  <h3 className="text-sm font-bold text-white mb-1">{cls.title}</h3>
                  <p className="text-xs text-slate-400 mb-3">{cls.description}</p>
                  <div className="flex items-center gap-3 text-[10px] text-slate-500">
                    <span className="flex items-center gap-1"><Clock className="w-3 h-3" /> {cls.duration}</span>
                    <span className="flex items-center gap-1"><Users className="w-3 h-3" /> {cls.spots}/{cls.totalSpots} spots</span>
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Bundle */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3 }}
              className="mt-6 bg-gradient-to-r from-amber-950/20 to-orange-950/20 border border-amber-800/30 rounded-xl p-5 flex items-center justify-between"
            >
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-lg bg-amber-950/40 border border-amber-800/30 flex items-center justify-center">
                  <BookOpen className="w-5 h-5 text-amber-400" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-white">3-Class Bundle</h3>
                  <p className="text-xs text-slate-400">All topics + save $50</p>
                </div>
              </div>
              <div className="text-right">
                <div className="text-lg font-bold text-white">$250</div>
                <div className="text-[10px] text-slate-500 line-through">$300</div>
              </div>
            </motion.div>
          </div>
        )}

        {step === 'details' && selectedClassObj && (
          <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="max-w-lg mx-auto">
            <button onClick={() => setStep('select')} className="text-xs text-slate-500 hover:text-white mb-4">← Back</button>
            <div className="bg-slate-900/60 border border-slate-800/60 rounded-xl p-6">
              <h3 className="text-lg font-bold text-white mb-1">{selectedClassObj.title}</h3>
              <p className="text-xs text-slate-400 mb-4">{selectedClassObj.description}</p>

              <div className="mb-4">
                <label className="text-xs text-slate-500 uppercase tracking-wider mb-2 block">Topics Covered</label>
                <div className="space-y-1.5">
                  {selectedClassObj.topics.map((t, i) => (
                    <div key={i} className="flex items-center gap-2 text-xs text-slate-300">
                      <Check className="w-3.5 h-3.5 text-emerald-400" /> {t}
                    </div>
                  ))}
                </div>
              </div>

              <div className="mb-5">
                <label className="text-xs text-slate-500 uppercase tracking-wider mb-2 block">Pick a Date</label>
                <input
                  type="date"
                  value={selectedDate}
                  onChange={e => setSelectedDate(e.target.value)}
                  className="w-full bg-slate-800/50 border border-slate-700/50 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-amber-600/50"
                />
              </div>

              <button
                onClick={() => setStep('checkout')}
                disabled={!selectedDate}
                className="w-full py-3 rounded-lg text-sm font-bold text-white bg-amber-600 hover:bg-amber-500 disabled:opacity-40 transition-all flex items-center justify-center gap-2"
              >
                Continue <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </motion.div>
        )}

        {step === 'checkout' && selectedClassObj && (
          <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="max-w-lg mx-auto">
            <button onClick={() => setStep('details')} className="text-xs text-slate-500 hover:text-white mb-4">← Back</button>
            <div className="bg-slate-900/60 border border-slate-800/60 rounded-xl p-6">
              <h3 className="text-lg font-bold text-white mb-4">Payment</h3>

              <div className="bg-slate-800/40 border border-amber-800/20 rounded-lg p-4 mb-5">
                <div className="flex justify-between mb-1">
                  <span className="text-sm text-white">{selectedClassObj.title}</span>
                  <span className="text-sm font-bold text-white">${selectedClassObj.price}</span>
                </div>
                <p className="text-xs text-slate-500">{selectedDate} • {selectedClassObj.duration}</p>
              </div>

              <div className="grid grid-cols-2 gap-2 mb-5">
                <button onClick={() => setPaymentMethod('crypto')} className={`flex items-center gap-2 px-4 py-3 rounded-lg border text-sm font-medium transition-all ${paymentMethod === 'crypto' ? 'border-amber-500/50 bg-amber-950/20 text-amber-400' : 'border-slate-700/50 bg-slate-800/30 text-slate-400'}`}>
                  <Bitcoin className="w-4 h-4" /> Crypto
                </button>
                <button onClick={() => setPaymentMethod('card')} className={`flex items-center gap-2 px-4 py-3 rounded-lg border text-sm font-medium transition-all ${paymentMethod === 'card' ? 'border-amber-500/50 bg-amber-950/20 text-amber-400' : 'border-slate-700/50 bg-slate-800/30 text-slate-400'}`}>
                  <CreditCard className="w-4 h-4" /> Card
                </button>
              </div>

              <button
                onClick={handleCheckout}
                disabled={loading}
                className="w-full py-3 rounded-lg text-sm font-bold text-white bg-amber-600 hover:bg-amber-500 disabled:opacity-50 transition-all flex items-center justify-center gap-2"
              >
                {loading ? 'Processing...' : `Pay $${selectedClassObj.price}`}
                {!loading && <ArrowRight className="w-4 h-4" />}
              </button>
            </div>
          </motion.div>
        )}

        {step === 'success' && chargeData && (
          <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="max-w-lg mx-auto text-center">
            <div className="bg-slate-900/60 border border-slate-800/60 rounded-xl p-8">
              <CheckCircle2 className="w-12 h-12 text-emerald-400 mx-auto mb-4" />
              <h2 className="text-xl font-bold text-white mb-2">Booking Confirmed</h2>
              <p className="text-sm text-slate-400 mb-5">
                Your Rehab session is booked. Check your email for the calendar invite and Zoom link.
              </p>
              <div className="bg-slate-800/40 rounded-lg p-3 mb-5 text-left">
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-slate-500">Class</span>
                  <span className="text-white font-bold">{selectedClassObj?.title}</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-slate-500">Date</span>
                  <span className="text-white font-bold">{selectedDate}</span>
                </div>
              </div>
              <button onClick={() => { setStep('select'); setSelectedClass(null); setChargeData(null); }} className="text-sm text-purple-400 hover:text-purple-300">
                Book Another Session
              </button>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}
