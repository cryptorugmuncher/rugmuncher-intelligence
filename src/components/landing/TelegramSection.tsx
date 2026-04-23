import { Bot, Check, MessageCircle, Users, Trophy } from 'lucide-react';
import ScrollReveal from '../hero/ScrollReveal';

interface TelegramSectionProps {
  onNavigate: (page: string) => void;
}

const FEATURES = [
  'Free wallet scans (3/month)',
  'Real-time rug pull alerts',
  'AI risk consensus scoring',
  'Community-powered intel',
  'Gamification: XP, levels & badges',
  'Pro features via Telegram Stars or crypto',
];

export default function TelegramSection({ onNavigate }: TelegramSectionProps) {
  return (
    <section id="telegram" className="py-20 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          <ScrollReveal direction="left" distance={50}>
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 bg-[#229ED9]/10 border border-[#229ED9]/30 rounded-full mb-6">
                <Bot className="w-4 h-4 text-[#229ED9]" />
                <span className="text-[#229ED9] text-sm font-medium">@rugmunchbot</span>
              </div>
              <h2 className="text-3xl sm:text-4xl font-bold mb-4">
                Your Personal <span className="text-[#229ED9]">Scam Shield</span>
              </h2>
              <p className="text-gray-400 mb-6 text-lg">
                Get instant security scans, risk alerts, and AI-powered analysis
                delivered straight to your Telegram. Free to start — upgrade anytime.
              </p>
              <ul className="space-y-3 mb-8">
                {FEATURES.map((item, idx) => (
                  <li key={idx} className="flex items-center gap-3">
                    <Check className="w-5 h-5 text-[#229ED9]" />
                    <span className="text-gray-300">{item}</span>
                  </li>
                ))}
              </ul>
              <div className="flex flex-col sm:flex-row items-start gap-4">
                <a
                  href="https://t.me/rugmunchbot"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-8 py-4 bg-[#229ED9] hover:bg-[#1a8bc2] text-white font-bold rounded-xl transition-all transform hover:scale-105 flex items-center gap-2"
                >
                  <Bot className="w-5 h-5" />
                  Start on Telegram
                </a>
                <button
                  onClick={() => onNavigate('telegram-dashboard')}
                  className="px-8 py-4 bg-[#12121a]/80 backdrop-blur border border-[#229ED9]/30 hover:border-[#229ED9]/50 text-[#229ED9] font-semibold rounded-xl flex items-center gap-2 transition-all"
                >
                  <MessageCircle className="w-5 h-5" />
                  View Dashboard
                </button>
              </div>

              <div className="mt-6 p-4 bg-[#12121a]/60 border border-[#229ED9]/20 rounded-xl">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-[#229ED9]/20 rounded-lg flex items-center justify-center">
                    <Users className="w-5 h-5 text-[#229ED9]" />
                  </div>
                  <div className="flex-1">
                    <div className="font-medium text-sm text-white">Use in Your Private Group</div>
                    <p className="text-xs text-gray-400">Add @rugmunchbot to any private group for shared scans</p>
                  </div>
                  <span className="text-xs px-2 py-1 bg-green-500/20 text-green-400 rounded border border-green-500/20">
                    Works in Groups
                  </span>
                </div>
              </div>
            </div>
          </ScrollReveal>

          <ScrollReveal direction="right" distance={50} delay={200}>
            <div className="relative">
              <div className="bg-[#12121a] rounded-2xl border border-[#229ED9]/20 p-6 relative overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-br from-[#229ED9]/5 to-purple-500/5" />
                <div className="relative space-y-3">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-10 h-10 bg-[#229ED9] rounded-full flex items-center justify-center">
                      <Bot className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <div className="font-semibold">@rugmunchbot</div>
                      <div className="text-xs text-gray-500">Online • Responds in DMs & groups</div>
                    </div>
                  </div>

                  <div className="space-y-3">
                    <div className="bg-[#229ED9]/10 rounded-lg p-3 border border-[#229ED9]/20">
                      <div className="flex items-center gap-2 mb-1">
                        <Bot className="w-4 h-4 text-[#229ED9]" />
                        <span className="text-xs text-[#229ED9] font-medium">@rugmunchbot</span>
                      </div>
                      <p className="text-sm text-gray-300">🔍 <b>Security Scan Result</b></p>
                      <p className="text-xs text-gray-400 mt-1">Token: <code className="text-gray-300">EPjF...Dt1v</code></p>
                      <div className="flex items-center gap-2 mt-2">
                        <span className="text-xs px-2 py-0.5 bg-green-500/20 text-green-400 rounded">SAFE</span>
                        <span className="text-xs text-green-400">Risk: 12/100</span>
                      </div>
                    </div>

                    <div className="bg-red-500/10 rounded-lg p-3 border border-red-500/20">
                      <div className="flex items-center gap-2 mb-1">
                        <Bot className="w-4 h-4 text-red-400" />
                        <span className="text-xs text-red-400 font-medium">@rugmunchbot</span>
                      </div>
                      <p className="text-sm text-gray-300">🚨 <b>Critical Alert</b></p>
                      <p className="text-xs text-gray-400 mt-1">Honeypot detected on <code className="text-gray-300">DezX...B263</code></p>
                      <div className="flex items-center gap-2 mt-2">
                        <span className="text-xs px-2 py-0.5 bg-red-500/20 text-red-400 rounded">CRITICAL</span>
                        <span className="text-xs text-red-400">Risk: 87/100</span>
                      </div>
                    </div>

                    <div className="bg-yellow-500/10 rounded-lg p-3 border border-yellow-500/20">
                      <div className="flex items-center gap-2 mb-1">
                        <Trophy className="w-4 h-4 text-yellow-400" />
                        <span className="text-xs text-yellow-400 font-medium">Badge Unlocked!</span>
                      </div>
                      <p className="text-sm text-gray-300">🎯 <b>First Blood</b></p>
                      <p className="text-xs text-gray-400 mt-1">Performed your first scan. +10 XP</p>
                    </div>
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
