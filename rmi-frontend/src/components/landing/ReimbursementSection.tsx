import { Award, Shield, Users, Clock, TrendingUp } from 'lucide-react';
import ScrollReveal from '../hero/ScrollReveal';

const REIMBURSEMENT_STATS = {
  totalRecovered: '$547,892',
  victimsHelped: 247,
  activeCases: 18,
  successRate: '68%',
};

interface ReimbursementSectionProps {
  onReimbursementClick: () => void;
}

export default function ReimbursementSection({ onReimbursementClick }: ReimbursementSectionProps) {
  return (
    <section id="reimbursement" className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-b from-green-500/5 to-transparent">
      <div className="max-w-7xl mx-auto">
        <ScrollReveal direction="up" distance={30}>
          <div className="text-center mb-12">
            <div className="inline-flex items-center gap-2 px-3 py-1 bg-green-500/10 border border-green-500/30 rounded-full mb-4">
              <Award className="w-4 h-4 text-green-400" />
              <span className="text-green-400 text-sm font-medium">Victim Recovery Program</span>
            </div>
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">
              1-1 <span className="text-green-400">Reimbursement</span> Program
            </h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              We help rug pull victims recover funds through legal action, negotiations,
              and blockchain forensics. No cure, no pay.
            </p>
          </div>
        </ScrollReveal>

        {/* Stats Cards */}
        <ScrollReveal direction="up" distance={30} delay={150}>
          <div className="grid md:grid-cols-4 gap-4 mb-12">
            <div className="bg-[#12121a] border border-green-500/20 rounded-xl p-6 text-center">
              <div className="w-12 h-12 bg-green-500/10 rounded-full flex items-center justify-center mx-auto mb-3">
                <Shield className="w-6 h-6 text-green-400" />
              </div>
              <div className="text-3xl font-bold text-green-400 mb-1">{REIMBURSEMENT_STATS.totalRecovered}</div>
              <div className="text-sm text-gray-500">Total Recovered</div>
            </div>
            <div className="bg-[#12121a] border border-green-500/20 rounded-xl p-6 text-center">
              <div className="w-12 h-12 bg-blue-500/10 rounded-full flex items-center justify-center mx-auto mb-3">
                <Users className="w-6 h-6 text-blue-400" />
              </div>
              <div className="text-3xl font-bold text-blue-400 mb-1">{REIMBURSEMENT_STATS.victimsHelped}</div>
              <div className="text-sm text-gray-500">Victims Helped</div>
            </div>
            <div className="bg-[#12121a] border border-green-500/20 rounded-xl p-6 text-center">
              <div className="w-12 h-12 bg-yellow-500/10 rounded-full flex items-center justify-center mx-auto mb-3">
                <Clock className="w-6 h-6 text-yellow-400" />
              </div>
              <div className="text-3xl font-bold text-yellow-400 mb-1">{REIMBURSEMENT_STATS.activeCases}</div>
              <div className="text-sm text-gray-500">Active Cases</div>
            </div>
            <div className="bg-[#12121a] border border-green-500/20 rounded-xl p-6 text-center">
              <div className="w-12 h-12 bg-purple-500/10 rounded-full flex items-center justify-center mx-auto mb-3">
                <TrendingUp className="w-6 h-6 text-purple-400" />
              </div>
              <div className="text-3xl font-bold text-purple-400 mb-1">{REIMBURSEMENT_STATS.successRate}</div>
              <div className="text-sm text-gray-500">Success Rate</div>
            </div>
          </div>
        </ScrollReveal>

        {/* How It Works */}
        <ScrollReveal direction="up" distance={30} delay={200}>
          <div className="grid md:grid-cols-3 gap-6 mb-12">
            <div className="bg-[#12121a] border border-green-500/10 rounded-xl p-6">
              <div className="w-10 h-10 bg-green-500/10 rounded-lg flex items-center justify-center mb-4">
                <span className="text-green-400 font-bold">1</span>
              </div>
              <h3 className="font-semibold mb-2">Submit Evidence</h3>
              <p className="text-gray-400 text-sm">
                Provide transaction hashes, contract addresses, and any communication with scammers.
              </p>
            </div>
            <div className="bg-[#12121a] border border-green-500/10 rounded-xl p-6">
              <div className="w-10 h-10 bg-green-500/10 rounded-lg flex items-center justify-center mb-4">
                <span className="text-green-400 font-bold">2</span>
              </div>
              <h3 className="font-semibold mb-2">Forensic Analysis</h3>
              <p className="text-gray-400 text-sm">
                Our team traces funds, identifies culprits, and builds a recovery case with legal partners.
              </p>
            </div>
            <div className="bg-[#12121a] border border-green-500/10 rounded-xl p-6">
              <div className="w-10 h-10 bg-green-500/10 rounded-lg flex items-center justify-center mb-4">
                <span className="text-green-400 font-bold">3</span>
              </div>
              <h3 className="font-semibold mb-2">Recovery</h3>
              <p className="text-gray-400 text-sm">
                We negotiate, pressure, or legally pursue recovery. You pay nothing unless we succeed.
              </p>
            </div>
          </div>
        </ScrollReveal>

        {/* CTA */}
        <ScrollReveal direction="up" distance={20} delay={300}>
          <div className="text-center">
            <button
              onClick={onReimbursementClick}
              className="px-8 py-4 bg-gradient-to-r from-green-600 to-green-500 hover:from-green-500 hover:to-green-400 text-black font-bold rounded-xl transition-all transform hover:scale-105"
            >
              Pre-Register for V2 Recovery Program
            </button>
            <p className="text-gray-500 text-sm mt-4">
              V1 victims: Check your eligibility for priority processing
            </p>
          </div>
        </ScrollReveal>
      </div>
    </section>
  );
}
