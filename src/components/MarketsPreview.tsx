import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { BarChart3, ArrowUpRight, ArrowDownRight, TrendingUp, Globe, Activity, Zap } from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:3001';

export default function MarketsPreview() {
  const [overview, setOverview] = useState<any>();
  const [sentiment, setSentiment] = useState<any>();

  useEffect(() => {
    Promise.all([
      fetch(`${API_BASE}/api/markets/overview`).then(r => r.ok ? r.json() : null),
      fetch(`${API_BASE}/api/markets/sentiment`).then(r => r.ok ? r.json() : null),
    ]).then(([ov, sent]) => {
      setOverview(ov);
      setSentiment(sent?.data?.[0]);
    }).catch(() => {});
  }, []);

  const global = overview?.global;
  const btc = overview?.prices?.bitcoin;
  const eth = overview?.prices?.ethereum;

  const fmtT = (n: number) => n >= 1e12 ? `$${(n / 1e12).toFixed(2)}T` : n >= 1e9 ? `$${(n / 1e9).toFixed(2)}B` : `$${(n / 1e6).toFixed(2)}M`;

  const cards = [
    { label: 'Global Market Cap', value: global?.total_market_cap?.usd ? fmtT(global.total_market_cap.usd) : '$2.84T', change: global?.market_cap_change_percentage_24h_usd ?? 2.4, icon: Globe },
    { label: '24h Volume', value: global?.total_volume?.usd ? fmtT(global.total_volume.usd) : '$98.4B', change: 5.1, icon: BarChart3 },
    { label: 'Bitcoin', value: btc?.usd ? `$${btc.usd.toLocaleString()}` : '$94,320', change: btc?.usd_24h_change ?? 2.8, icon: TrendingUp },
    { label: 'Ethereum', value: eth?.usd ? `$${eth.usd.toLocaleString()}` : '$3,450', change: eth?.usd_24h_change ?? -1.2, icon: Activity },
  ];

  const sentimentValue = sentiment?.value ?? 65;
  const sentimentLabel = sentiment?.value_classification || 'Greed';
  const sentimentColor = sentimentValue <= 20 ? '#FF3366' : sentimentValue <= 40 ? '#F4A259' : sentimentValue <= 60 ? '#D1A340' : sentimentValue <= 80 ? '#00E676' : '#28CBF4';

  return (
    <section id="markets" className="py-20 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} className="text-center mb-12">
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-purple-500/10 border border-purple-500/30 rounded-full mb-4">
            <Zap className="w-4 h-4 text-purple-400" />
            <span className="text-purple-400 text-sm font-medium">Live Market Data</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-bold mb-4">
            Markets <span className="text-purple-400">at a Glance</span>
          </h2>
          <p className="text-gray-400 max-w-2xl mx-auto">
            Real-time crypto intelligence, fear & greed sentiment, top movers, and curated news — all in one place.
          </p>
        </motion.div>

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {cards.map((c, i) => (
            <motion.div key={c.label} initial={{ opacity: 0, y: 10 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: i * 0.05 }}
              className="p-5 rounded-2xl bg-[#12121a]/80 backdrop-blur-xl border border-purple-500/10 hover:border-purple-500/30 transition-all">
              <div className="flex items-center gap-2 mb-2">
                <c.icon className="w-4 h-4 text-purple-400" />
                <span className="text-[10px] text-gray-500 uppercase tracking-wider font-semibold">{c.label}</span>
              </div>
              <div className="text-xl font-black text-white">{c.value}</div>
              <div className={`text-[11px] font-medium mt-0.5 ${(c.change as number) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {(c.change as number) >= 0 ? '+' : ''}{typeof c.change === 'number' ? c.change.toFixed(1) : c.change}% 24h
              </div>
            </motion.div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
          <motion.div initial={{ opacity: 0, y: 10 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
            className="lg:col-span-2 p-5 rounded-2xl bg-[#12121a]/80 backdrop-blur-xl border border-purple-500/10">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-bold text-white">Top Movers (24h)</h3>
              <a href="https://maps.rugmunch.io/markets" target="_blank" rel="noopener noreferrer" className="text-xs text-purple-400 hover:text-purple-300 flex items-center gap-1">
                View All <ArrowUpRight className="w-3 h-3" />
              </a>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {(overview?.top || []).slice(0, 8).map((coin: any, i: number) => (
                <div key={coin.id} className="flex items-center gap-2 p-2 rounded-lg bg-black/30 border border-purple-500/5">
                  <img src={coin.image} alt="" className="w-6 h-6 rounded-full" />
                  <div className="min-w-0">
                    <div className="text-xs font-semibold text-white truncate">{coin.symbol.toUpperCase()}</div>
                    <div className={`text-[10px] font-medium ${coin.price_change_percentage_24h >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {coin.price_change_percentage_24h >= 0 ? '+' : ''}{coin.price_change_percentage_24h?.toFixed(1)}%
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 10 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
            className="p-5 rounded-2xl bg-[#12121a]/80 backdrop-blur-xl border border-purple-500/10 flex flex-col items-center justify-center">
            <div className="text-[10px] text-gray-500 uppercase tracking-wider font-semibold mb-3">Fear & Greed</div>
            <div className="relative w-24 h-24">
              <svg className="w-full h-full transform -rotate-90">
                <circle cx="48" cy="48" r="40" fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="8" />
                <circle cx="48" cy="48" r="40" fill="none" stroke={sentimentColor} strokeWidth="8"
                  strokeDasharray={`${(sentimentValue / 100) * 251} 251`} strokeLinecap="round"
                  style={{ filter: `drop-shadow(0 0 6px ${sentimentColor}60)`, transition: 'stroke-dasharray 0.8s ease' }} />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-xl font-black" style={{ color: sentimentColor }}>{sentimentValue}</span>
              </div>
            </div>
            <div className="text-sm font-bold text-white mt-2">{sentimentLabel}</div>
            <a href="https://maps.rugmunch.io/markets" target="_blank" rel="noopener noreferrer"
              className="mt-4 w-full py-2.5 bg-gradient-to-r from-purple-600 to-purple-500 hover:from-purple-500 hover:to-purple-400 text-white text-xs font-bold rounded-xl text-center transition-all">
              Open Markets
            </a>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
