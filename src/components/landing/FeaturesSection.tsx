import { Bot, Network, Brain, Shield, Target, Eye } from 'lucide-react';
import ScrollReveal from '../hero/ScrollReveal';

const FEATURES = [
  { icon: Bot, title: 'Rug Munch Bot', desc: '24/7 Telegram bot monitoring 4 channels. Instant scam alerts delivered to your DMs before devs can dump.', color: 'green', badge: 'FREE ALERTS' },
  { icon: Network, title: 'Muncher Maps', desc: 'The crown jewel - 3D network visualization showing wallet connections no competitor can match.', color: 'purple', badge: 'ELITE ONLY' },
  { icon: Brain, title: 'RMI Intelligence', desc: 'Multi-model AI analyzing contracts, wallets, and social signals. 50+ detection vectors.', color: 'blue', badge: 'AI-POWERED' },
  { icon: Shield, title: "Don't Get Rugged", desc: 'Early warning system: honeypots, hidden mints, fresh wallets, and exit scams detected instantly.', color: 'red', badge: '99.2% ACCURACY' },
  { icon: Target, title: 'Follow Smart Money', desc: 'Track whales, insiders, and coordinated groups. See what the smart money is doing before they dump.', color: 'yellow', badge: 'PRO+' },
  { icon: Eye, title: 'The Trenches', desc: 'Community-powered intelligence. Verified reports, real-time alerts, and reputation rewards.', color: 'cyan', badge: 'COMMUNITY' },
];

export default function FeaturesSection() {
  return (
    <section className="py-20 px-4 sm:px-6 lg:px-8 bg-[#12121a]/50">
      <div className="max-w-7xl mx-auto">
        <ScrollReveal direction="up" distance={30}>
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">
              Complete <span className="text-purple-400">Web3 Security</span> Suite
            </h2>
            <p className="text-gray-400">Everything you need to stay safe in crypto</p>
          </div>
        </ScrollReveal>
        <ScrollReveal direction="up" distance={30} delay={150}>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {FEATURES.map((feature, idx) => {
              const colorClasses: Record<string, string> = {
                green: 'text-green-400 bg-green-500/10 border-green-500/20',
                purple: 'text-purple-400 bg-purple-500/10 border-purple-500/20',
                blue: 'text-blue-400 bg-blue-500/10 border-blue-500/20',
                red: 'text-red-400 bg-red-500/10 border-red-500/20',
                yellow: 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20',
                cyan: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/20',
              };
              const colorClass = colorClasses[feature.color] || colorClasses.blue;
              return (
                <div
                  key={idx}
                  className="group p-6 bg-[#0a0a0f] border border-gray-800 rounded-xl hover:border-purple-500/30 transition-all"
                >
                  <div className="flex items-center justify-between mb-4">
                    <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${colorClass}`}>
                      <feature.icon className={`w-6 h-6 ${colorClass.split(' ')[0]}`} />
                    </div>
                    <span className={`text-xs px-2 py-1 rounded-full ${colorClass}`}>
                      {feature.badge}
                    </span>
                  </div>
                  <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
                  <p className="text-gray-400 text-sm">{feature.desc}</p>
                </div>
              );
            })}
          </div>
        </ScrollReveal>
      </div>
    </section>
  );
}
