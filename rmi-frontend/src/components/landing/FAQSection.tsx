import { useState } from 'react';
import { MessageCircle, ChevronDown, ChevronUp } from 'lucide-react';
import ScrollReveal from '../hero/ScrollReveal';

const FAQS = [
  {
    q: 'What happened to $CRM V1?',
    a: 'In March 2026, we uncovered a coordinated infiltration by an organized fraud syndicate. A former developer and associated wallets were systematically extracting funds while manipulating community trust. The founder immediately assumed sole control, consolidated the remaining 14.56M $CRM into a secure wallet, and launched a full forensic investigation. This wasn\'t a typical rug pull — it was a professional extraction operation, and we caught it using our own bot\'s pattern detection.'
  },
  {
    q: 'Will I get my V1 tokens back?',
    a: 'Yes. We are implementing a 1-to-1 token reimbursement for all holders who were uninvolved with the scam. Whatever the final V2 structure looks like, the bottom line is this: you will receive the exact same number of tokens you held at the time of the snapshot. The V2 liquidity pool will be funded by a portion of app revenue plus a 1% trading fee, creating a self-sustaining engine rather than a static bucket.'
  },
  {
    q: 'How does the token scanner work?',
    a: 'The same engine that caught the $CRM syndicate powers @rugmunchbot. It analyzes 50+ detection vectors across multiple AI models: contract verification, honeypot detection, hidden mint functions, blacklist checks, LP lock status, holder concentration (Gini coefficient), bundle detection, sniper tracking, fresh wallet analysis, and cross-referencing against known serial ruggers. Results return in under 3 seconds.'
  },
  {
    q: 'What is Rug Pull Rehab?',
    a: 'Live 2-hour Zoom classes taught by industry experts. Topics include Honeypot Detection 101, Reading Smart Contracts, Whale Tracking Mastery, and On-Chain Forensics. Recordings available for 7 days. ELITE members get 1 free class per month. 50% of all Rehab class revenue goes directly back into the project liquidity pool.'
  },
  {
    q: 'How does the 1-1 Recovery Program work?',
    a: 'No cure, no pay. Submit your evidence (TX hashes, contract addresses, scammer communications). Our forensics team traces funds through mixers, identifies KYC exchanges, and builds a legal case. We negotiate with exchanges and apply legal pressure. We only take a fee if we recover funds. Current success rate: 73%. Average recovery: 70% of stolen funds.'
  },
  {
    q: 'Is the Telegram bot really free?',
    a: 'Yes. @rugmunchbot gives every user 3 free scans per month, public alerts, and community access. Upgrading to BASIC ($29/mo) unlocks 25 scans/day and 3 chains. PRO ($99/mo) adds unlimited scans, Muncher Maps, bundle detection, and @rmi_alpha_bot. ELITE ($299/mo) includes 3D network mapping, predictive analytics, and 1 free Rehab class monthly.'
  },
  {
    q: 'Who is behind Rug Munch now?',
    a: 'The original founder assumed sole control after discovering the infiltration. All previous team members with access have been removed. The founder personally consolidated remaining funds, built new forensic infrastructure from scratch (VPS, local LLM, unified evidence database), and is working directly with law enforcement. Every transaction, wallet consolidation, and decision has been publicly documented on X @CryptoRugMunch.'
  }
];

export default function FAQSection() {
  const [openFaq, setOpenFaq] = useState<number | null>(null);

  return (
    <section id="faq" className="py-20 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        <ScrollReveal direction="up" distance={30}>
          <div className="text-center mb-12">
            <div className="inline-flex items-center gap-2 px-3 py-1 bg-blue-500/10 border border-blue-500/30 rounded-full mb-4">
              <MessageCircle className="w-4 h-4 text-blue-400" />
              <span className="text-blue-400 text-sm font-medium">FAQ</span>
            </div>
            <h2 className="text-3xl sm:text-4xl font-bold mb-3">
              Questions & <span className="text-blue-400">Answers</span>
            </h2>
            <p className="text-gray-400">Everything about V1, V2, scans, rehab, and recovery.</p>
          </div>
        </ScrollReveal>

        <div className="space-y-3">
          {FAQS.map((faq, idx) => (
            <ScrollReveal key={idx} direction="up" distance={20} delay={idx * 50}>
              <div className="bg-[#12121a] border border-slate-800 rounded-xl overflow-hidden">
                <button
                  onClick={() => setOpenFaq(openFaq === idx ? null : idx)}
                  className="w-full flex items-center justify-between p-5 text-left hover:bg-slate-900/50 transition-colors"
                >
                  <span className="font-semibold text-white text-sm">{faq.q}</span>
                  {openFaq === idx ? (
                    <ChevronUp className="w-5 h-5 text-purple-400 flex-shrink-0" />
                  ) : (
                    <ChevronDown className="w-5 h-5 text-slate-500 flex-shrink-0" />
                  )}
                </button>
                {openFaq === idx && (
                  <div className="px-5 pb-5 text-sm text-gray-400 leading-relaxed border-t border-slate-800 pt-4">
                    {faq.a}
                  </div>
                )}
              </div>
            </ScrollReveal>
          ))}
        </div>
      </div>
    </section>
  );
}
