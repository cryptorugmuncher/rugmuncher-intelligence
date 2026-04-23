import { Star } from 'lucide-react';
import ScrollReveal from '../hero/ScrollReveal';

const TESTIMONIALS = [
  {
    quote: "Scanned EPjF...Dt1v before aping in. Risk score 23/100 — SAFE. Bot caught the hidden mint function on the next token I checked. Saved me 12 SOL.",
    author: "@whale_hunter",
    role: "ELITE • 847 Scans • Lvl 6",
    avatar: "W",
    color: "from-yellow-400 to-orange-500"
  },
  {
    quote: "The bundle detection on DezX...B263 flagged it CRITICAL before launch. Saw 6 connected wallets funded from the same CEX. Dodged an $890K honeypot.",
    author: "@rug_dodger",
    role: "PRO • 623 Scans • Lvl 5",
    avatar: "R",
    color: "from-purple-500 to-pink-500"
  },
  {
    quote: "Free tier caught a sell-restricted contract in seconds. The @rugmunchbot is literally a bodyguard in your pocket. Upgraded to PRO same day.",
    author: "@degen_01",
    role: "PRO • 412 Scans • Lvl 4",
    avatar: "D",
    color: "from-blue-400 to-cyan-400"
  },
  {
    quote: "Rehab team traced my stolen funds through 4 mixers and identified the KYC exchange. Recovered 70% after 3 months. No cure no pay actually means something here.",
    author: "@Victim_Recovery_2026",
    role: "Recovery Client",
    avatar: "V",
    color: "from-green-400 to-emerald-500"
  },
  {
    quote: "First scan ever. Honeypot detected on a 'safe' token shilled in a group. +10 XP and the 'First Blood' badge. Gamification makes security actually fun.",
    author: "@newbie_scan",
    role: "FREE • 3 Scans • Lvl 1",
    avatar: "N",
    color: "from-gray-400 to-slate-500"
  },
  {
    quote: "The Butcher's Block autopsy on SOSANA was forensic-grade. Chain-of-custody evidence, wallet clustering, the full 9 yards. Used it in my legal filing.",
    author: "@ForensicLawyer",
    role: "ELITE • Legal Subscriber",
    avatar: "F",
    color: "from-red-400 to-rose-500"
  }
];

export default function TestimonialsSection() {
  return (
    <section className="py-20 px-4 sm:px-6 lg:px-8 bg-[#12121a]/50">
      <div className="max-w-7xl mx-auto">
        <ScrollReveal direction="up" distance={30}>
          <h2 className="text-3xl font-bold text-center mb-12">
            What <span className="text-purple-400">Members</span> Say
          </h2>
        </ScrollReveal>
        <ScrollReveal direction="up" distance={30} delay={150}>
          <div className="grid md:grid-cols-3 gap-6">
            {TESTIMONIALS.map((t, idx) => (
              <div key={idx} className="p-6 bg-[#0a0a0f] rounded-xl border border-gray-800 hover:border-purple-500/20 transition-all">
                <div className="flex gap-1 mb-4">
                  {[1, 2, 3, 4, 5].map(i => <Star key={i} className="w-4 h-4 text-yellow-400 fill-current" />)}
                </div>
                <p className="text-gray-300 mb-4">&ldquo;{t.quote}&rdquo;</p>
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 bg-gradient-to-br ${t.color} rounded-full`} />
                  <div>
                    <div className="font-semibold">{t.author}</div>
                    <div className="text-sm text-gray-500">{t.role}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </ScrollReveal>
      </div>
    </section>
  );
}
