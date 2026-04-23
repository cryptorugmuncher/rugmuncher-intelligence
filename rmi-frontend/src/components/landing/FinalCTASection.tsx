import { Shield, Gift } from 'lucide-react';
import ScrollReveal from '../hero/ScrollReveal';

interface FinalCTASectionProps {
  onScannerClick: () => void;
  onAirdropClick: () => void;
}

export default function FinalCTASection({ onScannerClick, onAirdropClick }: FinalCTASectionProps) {
  return (
    <section className="py-20 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto text-center">
        <ScrollReveal direction="up" distance={40}>
          <h2 className="text-3xl sm:text-4xl font-bold mb-4">
            Stop Getting
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-yellow-400"> Rugged</span>
          </h2>
          <p className="text-gray-400 mb-8 text-lg">
            Join 50,000+ traders using AI-powered security. Get real-time alerts,
            scan any contract, and join the V2 airdrop waitlist today.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <button
              onClick={onScannerClick}
              className="w-full sm:w-auto px-8 py-4 bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-500 hover:to-purple-600 text-white font-bold rounded-xl flex items-center justify-center gap-2 transition-all transform hover:scale-105"
            >
              <Shield className="w-5 h-5" />
              CHECK SCAMS NOW
            </button>
            <button
              onClick={onAirdropClick}
              className="w-full sm:w-auto px-8 py-4 bg-gradient-to-r from-yellow-500 to-yellow-600 hover:from-yellow-400 hover:to-yellow-500 text-black font-bold rounded-xl flex items-center justify-center gap-2 transition-all"
            >
              <Gift className="w-5 h-5" />
              Join V2 Airdrop
            </button>
          </div>
        </ScrollReveal>
      </div>
    </section>
  );
}
