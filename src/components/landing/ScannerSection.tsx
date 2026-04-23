import { Zap } from 'lucide-react';
import ScrollReveal from '../hero/ScrollReveal';
import TokenScanTerminal from '../TokenScanTerminal';

export default function ScannerSection() {
  return (
    <section id="scanner" className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-b from-purple-500/5 to-transparent">
      <div className="max-w-7xl mx-auto">
        <ScrollReveal direction="up" distance={30}>
          <div className="text-center mb-10">
            <div className="inline-flex items-center gap-2 px-3 py-1 bg-purple-500/10 border border-purple-500/30 rounded-full mb-4">
              <Zap className="w-4 h-4 text-purple-400" />
              <span className="text-purple-400 text-sm font-medium">@rugmunchbot</span>
            </div>
            <h2 className="text-3xl sm:text-4xl font-bold mb-3">
              Token <span className="text-purple-400">Scanner</span>
            </h2>
            <p className="text-gray-400 max-w-xl mx-auto">
              The same security scan engine powering our Telegram bot. Paste any contract address and get instant risk analysis.
            </p>
          </div>
        </ScrollReveal>
        <TokenScanTerminal embedded />
      </div>
    </section>
  );
}
