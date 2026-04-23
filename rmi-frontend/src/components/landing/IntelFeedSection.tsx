import { Newspaper, Bot, TrendingUp, ExternalLink } from 'lucide-react';
import ScrollReveal from '../hero/ScrollReveal';
import GhostTwitterFeed from '../GhostTwitterFeed';

export default function IntelFeedSection() {
  return (
    <section id="intel-feed" className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-b from-purple-500/5 to-transparent">
      <div className="max-w-7xl mx-auto">
        <ScrollReveal direction="up" distance={30}>
          <div className="text-center mb-10">
            <div className="inline-flex items-center gap-2 px-3 py-1 bg-purple-500/10 border border-purple-500/30 rounded-full mb-4">
              <Newspaper className="w-4 h-4 text-purple-400" />
              <span className="text-purple-400 text-sm font-medium">Live Intel</span>
            </div>
            <h2 className="text-3xl sm:text-4xl font-bold mb-3">
              Latest <span className="text-purple-400">Intelligence</span>
            </h2>
            <p className="text-gray-400 max-w-xl mx-auto">
              Every article syndicates to X and Telegram. Long-form deep dives and short-form alerts — all from one source.
            </p>
          </div>
        </ScrollReveal>

        <div className="grid lg:grid-cols-3 gap-8">
          <ScrollReveal direction="left" distance={30} delay={100}>
            <div className="lg:sticky lg:top-24 space-y-6">
              <div className="bg-[#12121a] border border-purple-500/20 rounded-xl p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-yellow-400 flex items-center justify-center">
                    <Newspaper className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h3 className="font-bold text-white">Rug Munch Intel</h3>
                    <p className="text-xs text-slate-500">@rugmunch • Q2 2026</p>
                  </div>
                </div>
                <p className="text-sm text-slate-400 mb-4">
                  On-chain investigations, rug pull forensics, and degen security briefings.
                  Published on Ghost, syndicated everywhere.
                </p>
                <div className="flex items-center gap-3 text-xs text-slate-500">
                  <span className="flex items-center gap-1">
                    <Bot className="w-3 h-3 text-[#229ED9]" /> Telegram
                  </span>
                  <span className="flex items-center gap-1">
                    <TrendingUp className="w-3 h-3 text-blue-400" /> X/Twitter
                  </span>
                </div>
              </div>

              <div className="bg-[#12121a] border border-slate-800 rounded-xl p-6">
                <h4 className="font-semibold text-white mb-3 text-sm">Content Channels</h4>
                <div className="space-y-3">
                  <a href="https://rugmunch.io/blog" target="_blank" rel="noopener noreferrer" className="flex items-center gap-3 p-3 rounded-lg bg-slate-900/50 hover:bg-slate-800/50 transition-colors border border-slate-800 hover:border-purple-500/30">
                    <div className="w-8 h-8 rounded bg-purple-500/10 flex items-center justify-center">
                      <Newspaper className="w-4 h-4 text-purple-400" />
                    </div>
                    <div className="flex-1">
                      <div className="text-sm font-medium text-white">Long-form Blog</div>
                      <div className="text-xs text-slate-500">Deep dives & investigations</div>
                    </div>
                    <ExternalLink className="w-3.5 h-3.5 text-slate-600" />
                  </a>
                  <a href="https://t.me/rugmunchbot" target="_blank" rel="noopener noreferrer" className="flex items-center gap-3 p-3 rounded-lg bg-slate-900/50 hover:bg-slate-800/50 transition-colors border border-slate-800 hover:border-[#229ED9]/30">
                    <div className="w-8 h-8 rounded bg-[#229ED9]/10 flex items-center justify-center">
                      <Bot className="w-4 h-4 text-[#229ED9]" />
                    </div>
                    <div className="flex-1">
                      <div className="text-sm font-medium text-white">Telegram</div>
                      <div className="text-xs text-slate-500">Short-form alerts & scans</div>
                    </div>
                    <ExternalLink className="w-3.5 h-3.5 text-slate-600" />
                  </a>
                  <a href="https://twitter.com/rugmunch" target="_blank" rel="noopener noreferrer" className="flex items-center gap-3 p-3 rounded-lg bg-slate-900/50 hover:bg-slate-800/50 transition-colors border border-slate-800 hover:border-blue-500/30">
                    <div className="w-8 h-8 rounded bg-blue-500/10 flex items-center justify-center">
                      <TrendingUp className="w-4 h-4 text-blue-400" />
                    </div>
                    <div className="flex-1">
                      <div className="text-sm font-medium text-white">X / Twitter</div>
                      <div className="text-xs text-slate-500">Threads & real-time updates</div>
                    </div>
                    <ExternalLink className="w-3.5 h-3.5 text-slate-600" />
                  </a>
                </div>
              </div>
            </div>
          </ScrollReveal>

          <ScrollReveal direction="right" distance={30} delay={200}>
            <div className="lg:col-span-2">
              <div className="bg-[#0a0a0f] border border-slate-800 rounded-xl overflow-hidden">
                <GhostTwitterFeed />
              </div>
            </div>
          </ScrollReveal>
        </div>
      </div>
    </section>
  );
}
