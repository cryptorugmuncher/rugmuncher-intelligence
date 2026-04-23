import { GraduationCap, Check, AlertTriangle, Shield, Target } from 'lucide-react';
import ScrollReveal from '../hero/ScrollReveal';

interface RehabSectionProps {
  onNavigate: (page: string) => void;
}

export default function RehabSection({ onNavigate }: RehabSectionProps) {
  return (
    <section id="rehab" className="py-20 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          <ScrollReveal direction="left" distance={50}>
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 bg-blue-500/10 border border-blue-500/30 rounded-full mb-6">
                <GraduationCap className="w-4 h-4 text-blue-400" />
                <span className="text-blue-400 text-sm font-medium">Educational Classes</span>
              </div>
              <h2 className="text-3xl sm:text-4xl font-bold mb-4">
                Rug Pull <span className="text-blue-400">Rehab</span>
              </h2>
              <p className="text-gray-400 mb-6 text-lg">
                Learn to spot scams before they happen. Live classes with industry experts.
                From honeypot detection to whale tracking, we've got you covered.
              </p>

              <ul className="space-y-3 mb-8">
                <li className="flex items-center gap-3">
                  <Check className="w-5 h-5 text-blue-400" />
                  <span className="text-gray-300">2-hour live Zoom sessions</span>
                </li>
                <li className="flex items-center gap-3">
                  <Check className="w-5 h-5 text-blue-400" />
                  <span className="text-gray-300">Recordings available for 7 days</span>
                </li>
                <li className="flex items-center gap-3">
                  <Check className="w-5 h-5 text-blue-400" />
                  <span className="text-gray-300">Q&A with expert instructors</span>
                </li>
                <li className="flex items-center gap-3">
                  <Check className="w-5 h-5 text-blue-400" />
                  <span className="text-gray-300">Certificate of completion</span>
                </li>
                <li className="flex items-center gap-3">
                  <Check className="w-5 h-5 text-blue-400" />
                  <span className="text-gray-300">1-week Telegram support</span>
                </li>
              </ul>

              <div className="flex items-center gap-4">
                <button
                  onClick={() => onNavigate('rehab')}
                  className="px-8 py-4 bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 text-white font-bold rounded-xl transition-all"
                >
                  Book Session (0.1 ETH)
                </button>
                <span className="text-sm text-gray-500">ELITE tier: 1 free class/month</span>
              </div>
            </div>
          </ScrollReveal>

          {/* Upcoming Classes Preview */}
          <ScrollReveal direction="right" distance={50} delay={200}>
            <div className="space-y-4">
              <div className="bg-[#12121a] border border-blue-500/20 rounded-xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <span className="text-xs text-blue-400 bg-blue-500/10 px-2 py-1 rounded">BASIC+</span>
                    <h3 className="font-semibold mt-2">Honeypot Detection 101</h3>
                  </div>
                  <div className="w-12 h-12 bg-red-500/10 rounded-lg flex items-center justify-center">
                    <AlertTriangle className="w-6 h-6 text-red-400" />
                  </div>
                </div>
                <p className="text-sm text-gray-400 mb-4">
                  Learn to spot hidden mint functions, blacklists, and sell restrictions before you buy.
                </p>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-500">Jan 20, 14:00 UTC</span>
                  <span className="text-blue-400">8 spots left</span>
                </div>
              </div>

              <div className="bg-[#12121a] border border-purple-500/20 rounded-xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <span className="text-xs text-purple-400 bg-purple-500/10 px-2 py-1 rounded">PRO+</span>
                    <h3 className="font-semibold mt-2">Reading Smart Contracts</h3>
                  </div>
                  <div className="w-12 h-12 bg-purple-500/10 rounded-lg flex items-center justify-center">
                    <Shield className="w-6 h-6 text-purple-400" />
                  </div>
                </div>
                <p className="text-sm text-gray-400 mb-4">
                  Understand what you're actually agreeing to when you approve a contract.
                </p>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-500">Jan 22, 10:00 UTC</span>
                  <span className="text-purple-400">12 spots left</span>
                </div>
              </div>

              <div className="bg-[#12121a] border border-yellow-500/20 rounded-xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <span className="text-xs text-yellow-400 bg-yellow-500/10 px-2 py-1 rounded">ELITE</span>
                    <h3 className="font-semibold mt-2">Whale Tracking Mastery</h3>
                  </div>
                  <div className="w-12 h-12 bg-yellow-500/10 rounded-lg flex items-center justify-center">
                    <Target className="w-6 h-6 text-yellow-400" />
                  </div>
                </div>
                <p className="text-sm text-gray-400 mb-4">
                  Follow smart money movements and understand accumulation vs distribution patterns.
                </p>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-500">Jan 25, 16:00 UTC</span>
                  <span className="text-yellow-400">5 spots left</span>
                </div>
              </div>
            </div>
          </ScrollReveal>
        </div>
      </div>
    </section>
  );
}
