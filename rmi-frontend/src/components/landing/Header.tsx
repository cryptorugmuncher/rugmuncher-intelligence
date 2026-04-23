import { useState, useEffect } from 'react';
import { Shield, Menu, X, Network, BarChart3 } from 'lucide-react';

interface HeaderProps {
  onNavigate: (page: string) => void;
  onScrollTo: (id: string) => void;
  onAirdropClick: () => void;
}

export default function Header({ onNavigate, onScrollTo, onAirdropClick }: HeaderProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 50);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollTo = (id: string) => {
    onScrollTo(id);
    setMobileMenuOpen(false);
  };

  return (
    <>
      {/* V2 Coming Soon Banner */}
      <div className="fixed top-0 left-0 right-0 z-[60] bg-gradient-to-r from-purple-600/20 via-yellow-500/20 to-purple-600/20 border-b border-purple-500/30">
        <div className="max-w-7xl mx-auto px-4 py-2">
          <div className="flex items-center justify-center gap-4 text-sm">
            <span className="animate-pulse">🚀</span>
            <span className="text-purple-300 font-semibold hidden sm:inline">V2 CONTRACT & AIRDROP COMING SOON</span>
            <span className="text-purple-300 font-semibold sm:hidden">V2 AIRDROP SOON</span>
            <span className="text-yellow-400">|</span>
            <span className="text-yellow-300">Join the waitlist for early access!</span>
            <button
              onClick={onAirdropClick}
              className="px-4 py-1 bg-gradient-to-r from-purple-600 to-yellow-500 rounded-full text-xs font-bold hover:scale-105 transition-transform"
            >
              GET ALERT →
            </button>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className={`fixed top-10 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled ? 'bg-[#0a0a0f]/95 backdrop-blur-lg border-b border-purple-500/20' : 'bg-transparent'
      }`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center gap-2">
              <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-yellow-400 rounded-lg flex items-center justify-center glow-purple">
                <Shield className="w-6 h-6 text-white" />
              </div>
              <div>
                <span className="text-xl font-bold text-gradient">Rug Munch</span>
                <span className="hidden sm:block text-xs text-purple-400">V2 Coming Soon</span>
              </div>
            </div>

            {/* Desktop Nav */}
            <div className="hidden md:flex items-center gap-5">
              <button onClick={() => onNavigate('scanner')} className="text-gray-300 hover:text-purple-400 transition-colors text-sm">Scanner</button>
              <button onClick={() => scrollTo('reimbursement')} className="text-gray-300 hover:text-green-400 transition-colors text-sm">Recovery</button>
              <button onClick={() => scrollTo('snitch')} className="text-gray-300 hover:text-yellow-400 transition-colors text-sm">Snitch</button>
              <button onClick={() => scrollTo('rehab')} className="text-gray-300 hover:text-blue-400 transition-colors text-sm">Rehab</button>
              <a href="https://maps.rugmunch.io" target="_blank" rel="noopener noreferrer" className="text-gray-300 hover:text-cyan-400 transition-colors text-sm flex items-center gap-1">
                <Network className="w-3 h-3" /> Maps
              </a>
              <a href="https://maps.rugmunch.io/markets" target="_blank" rel="noopener noreferrer" className="text-gray-300 hover:text-gold-400 transition-colors text-sm flex items-center gap-1">
                <BarChart3 className="w-3 h-3" /> Markets
              </a>
              <button
                onClick={() => onNavigate('trenches')}
                className="px-4 py-2 bg-gradient-to-r from-purple-600 to-purple-500 hover:from-purple-500 hover:to-purple-400 text-white font-semibold rounded-lg transition-all text-sm shadow-lg shadow-purple-500/20"
              >
                The Trenches
              </button>
            </div>

            {/* Mobile Menu Button */}
            <button
              className="md:hidden p-2 text-gray-300"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              {mobileMenuOpen ? <X /> : <Menu />}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden bg-[#0a0a0f] border-b border-purple-500/20">
            <div className="px-4 py-4 space-y-3">
              <button onClick={() => onNavigate('scanner')} className="block w-full text-left py-2 text-gray-300">Token Scanner</button>
              <button onClick={() => scrollTo('reimbursement')} className="block w-full text-left py-2 text-gray-300">1-1 Recovery</button>
              <button onClick={() => scrollTo('snitch')} className="block w-full text-left py-2 text-gray-300">Snitch Board</button>
              <button onClick={() => scrollTo('rehab')} className="block w-full text-left py-2 text-gray-300">Rug Pull Rehab</button>
              <a href="https://maps.rugmunch.io" target="_blank" rel="noopener noreferrer" className="block py-2 text-cyan-400 font-semibold">Muncher Maps →</a>
              <a href="https://maps.rugmunch.io/markets" target="_blank" rel="noopener noreferrer" className="block py-2 text-yellow-400 font-semibold">Markets →</a>
              <button onClick={() => onNavigate('trenches')} className="block py-2 text-purple-400 font-semibold">The Trenches →</button>
            </div>
          </div>
        )}
      </nav>
    </>
  );
}
