import { Bot, Bell, AlertTriangle, Star, Check } from 'lucide-react';
import ScrollReveal from '../hero/ScrollReveal';

const BOTS = [
  {
    name: '@rugmunchbot',
    handle: 'rugmunchbot',
    description: 'Main bot - Your personal scam shield',
    features: ['Free wallet scans', 'Risk alerts', 'Community access'],
    type: 'primary',
    icon: Bot,
  },
  {
    name: '@rmi_backend_bot',
    handle: 'rmi_backend_bot',
    description: 'System alerts & maintenance notifications',
    features: ['System health', 'API status', 'Maintenance alerts'],
    type: 'system',
    icon: Bell,
  },
  {
    name: '@rmi_alerts_bot',
    handle: 'rmi_alerts_bot',
    description: 'Public free alerts channel',
    features: ['Real-time scam alerts', 'Community reports', 'FREE for all'],
    type: 'public',
    icon: AlertTriangle,
  },
  {
    name: '@rmi_alpha_bot',
    handle: 'rmi_alpha_bot',
    description: 'Premium intelligence channel',
    features: ['Whale movements', 'Insider signals', 'PRO+ exclusive'],
    type: 'premium',
    icon: Star,
  },
];

export default function BotsSection() {
  return (
    <section id="bots" className="py-20 px-4 sm:px-6 lg:px-8 bg-gray-900/30">
      <div className="max-w-7xl mx-auto">
        <ScrollReveal direction="up" distance={30}>
          <div className="text-center mb-16">
            <div className="inline-flex items-center gap-2 px-3 py-1 bg-blue-500/10 border border-blue-500/30 rounded-full mb-4">
              <Bot className="w-4 h-4 text-blue-400" />
              <span className="text-blue-400 text-sm font-medium">4 Bots, 24/7 Protection</span>
            </div>
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">
              Rug Munch <span className="text-blue-400">Bot</span> on Telegram
            </h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              Our fleet of 4 Telegram bots monitors the blockchain 24/7, delivering instant
              scam alerts to your DMs before devs can dump on you.
            </p>
          </div>
        </ScrollReveal>

        <ScrollReveal direction="up" distance={30} delay={150}>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {BOTS.map((bot, idx) => (
              <div
                key={idx}
                className={`p-6 rounded-xl border transition-all hover:scale-105 ${
                  bot.type === 'primary'
                    ? 'bg-blue-500/10 border-blue-500/30'
                    : bot.type === 'premium'
                    ? 'bg-purple-500/10 border-purple-500/30'
                    : 'bg-gray-900/50 border-gray-800'
                }`}
              >
                <div className={`w-12 h-12 rounded-lg flex items-center justify-center mb-4 ${
                  bot.type === 'primary' ? 'bg-blue-500/20' :
                  bot.type === 'premium' ? 'bg-purple-500/20' :
                  bot.type === 'public' ? 'bg-green-500/20' : 'bg-gray-700'
                }`}>
                  <bot.icon className={`w-6 h-6 ${
                    bot.type === 'primary' ? 'text-blue-400' :
                    bot.type === 'premium' ? 'text-purple-400' :
                    bot.type === 'public' ? 'text-green-400' : 'text-gray-400'
                  }`} />
                </div>
                <h3 className="text-lg font-semibold mb-1">@{bot.handle}</h3>
                <p className="text-gray-400 text-sm mb-4">{bot.description}</p>
                <ul className="space-y-2 text-sm">
                  {bot.features.map((f, fidx) => (
                    <li key={fidx} className="flex items-center gap-2 text-gray-300">
                      <Check className="w-4 h-4 text-green-400" />
                      {f}
                    </li>
                  ))}
                </ul>
                <a
                  href={`https://t.me/${bot.handle}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={`mt-4 block text-center py-2 rounded-lg font-semibold text-sm transition-colors ${
                    bot.type === 'primary'
                      ? 'bg-blue-500 hover:bg-blue-600 text-white'
                      : 'bg-gray-800 hover:bg-gray-700 text-white'
                  }`}
                >
                  {bot.type === 'primary' ? 'Start Free' : 'Join Channel'}
                </a>
              </div>
            ))}
          </div>
        </ScrollReveal>
      </div>
    </section>
  );
}
