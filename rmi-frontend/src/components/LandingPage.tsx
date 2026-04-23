/**
 * Rug Munch Intel (RMI) - Official Landing Page
 * Main frontend for the Rug Munch Intel ecosystem
 * Features: Twitter-style alerts, V2 Coming Soon, 1-1 Recovery, Snitch Board, Rug Pull Rehab
 */
import { useState, useEffect } from 'react';
import { Brain } from 'lucide-react';
import { useAppStore } from '../store/appStore';
import RugMunchIntelligence from './RugMunchIntelligence';
import LiveStats from './hero/LiveStats';
import ScrollReveal from './hero/ScrollReveal';
import Header from './landing/Header';
import HeroSection from './landing/HeroSection';
import Footer from './landing/Footer';
import FAQSection from './landing/FAQSection';
import StatsSection from './landing/StatsSection';
import FeaturesSection from './landing/FeaturesSection';
import PricingSection from './landing/PricingSection';
import TestimonialsSection from './landing/TestimonialsSection';
import ReimbursementSection from './landing/ReimbursementSection';
import SnitchSection from './landing/SnitchSection';
import BotsSection from './landing/BotsSection';
import V2WaitlistSection from './landing/V2WaitlistSection';
import RehabSection from './landing/RehabSection';
import Modals from './landing/Modals';
import MarketsPreview from './MarketsPreview';
import IntelPlatformSection from './landing/IntelPlatformSection';
import ScannerSection from './landing/ScannerSection';
import TelegramSection from './landing/TelegramSection';
import MuncherMapsSection from './landing/MuncherMapsSection';
import FoundersWordSection from './landing/FoundersWordSection';
import FinalCTASection from './landing/FinalCTASection';
import IntelFeedSection from './landing/IntelFeedSection';

export default function LandingPage() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [showAirdropModal, setShowAirdropModal] = useState(false);
  const [showSnitchModal, setShowSnitchModal] = useState(false);
  const [showReimbursementModal, setShowReimbursementModal] = useState(false);
  const [tipForm, setTipForm] = useState({ title: '', description: '', evidence: '' });
  const [airdropForm, setAirdropForm] = useState({ email: '', wallet: '', twitter: '' });

  const setCurrentPage = useAppStore((state) => state.setCurrentPage);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 50);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToSection = (id: string) => {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
    setMobileMenuOpen(false);
  };

  const navigateTo = (page: string) => {
    setCurrentPage(page);
  };

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-white font-sans">
      <Header onNavigate={navigateTo} onScrollTo={scrollToSection} onAirdropClick={() => setShowAirdropModal(true)} />
      <HeroSection onNavigate={navigateTo} onAirdropClick={() => setShowAirdropModal(true)} />

      {/* Live Stats Bar */}
      <section className="relative z-10 px-4 sm:px-6 lg:px-8 pb-20">
        <div className="max-w-7xl mx-auto">
          <LiveStats />
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════════ */}
      {/* RUG MUNCH INTELLIGENCE — Hero Chat Terminal                 */}
      {/* ═══════════════════════════════════════════════════════════ */}
      <section id="intel" className="relative py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-6xl mx-auto">
          <ScrollReveal direction="up" distance={30}>
            <div className="text-center mb-8">
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-500/10 border border-emerald-500/30 rounded-full mb-4">
                <Brain className="w-4 h-4 text-emerald-400" />
                <span className="text-emerald-400 text-sm font-medium">AI-Powered Crypto Intelligence</span>
              </div>
              <h2 className="text-3xl sm:text-4xl font-bold mb-3">
                Ask the
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-teal-400"> Terminal</span>
              </h2>
              <p className="text-gray-400 max-w-xl mx-auto">
                The RMI Terminal processes on-chain data in real-time. Get instant forensic analysis on tokens, wallets, and market patterns.
              </p>
            </div>
          </ScrollReveal>
          <ScrollReveal direction="up" delay={200} distance={40}>
            <div className="h-[700px] rounded-2xl overflow-hidden border border-slate-700/50 shadow-2xl shadow-emerald-500/5">
              <RugMunchIntelligence />
            </div>
          </ScrollReveal>
        </div>
      </section>

      <StatsSection />
      <IntelPlatformSection onNavigate={navigateTo} />
      <ScannerSection />
      <ReimbursementSection onReimbursementClick={() => setShowReimbursementModal(true)} />
      <SnitchSection onSnitchClick={() => setShowSnitchModal(true)} onNavigate={navigateTo} />
      <TelegramSection onNavigate={navigateTo} />
      <V2WaitlistSection onAirdropClick={() => setShowAirdropModal(true)} />
      <RehabSection onNavigate={navigateTo} />
      <BotsSection />
      <MarketsPreview />
      <MuncherMapsSection />
      <FeaturesSection />
      <PricingSection onNavigate={navigateTo} onAirdropClick={() => setShowAirdropModal(true)} />
      <TestimonialsSection />
      <FoundersWordSection />
      <FAQSection />
      <FinalCTASection onScannerClick={() => navigateTo('scanner')} onAirdropClick={() => setShowAirdropModal(true)} />
      <IntelFeedSection />

      <Footer onNavigate={navigateTo} onScrollToSection={scrollToSection} />
      <Modals
        showAirdropModal={showAirdropModal}
        setShowAirdropModal={setShowAirdropModal}
        showSnitchModal={showSnitchModal}
        setShowSnitchModal={setShowSnitchModal}
        showReimbursementModal={showReimbursementModal}
        setShowReimbursementModal={setShowReimbursementModal}
        airdropForm={airdropForm}
        setAirdropForm={setAirdropForm}
        tipForm={tipForm}
        setTipForm={setTipForm}
      />
    </div>
  );
}
