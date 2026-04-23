import ScrollReveal from '../hero/ScrollReveal';

export default function StatsSection() {
  return (
    <section className="py-12 border-y border-purple-500/20 bg-purple-500/5">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <ScrollReveal direction="up" distance={20}>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="text-3xl sm:text-4xl font-bold text-purple-400 mb-1">$547K+</div>
              <div className="text-gray-400 text-sm">Recovered for Victims</div>
            </div>
            <div className="text-center">
              <div className="text-3xl sm:text-4xl font-bold text-green-400 mb-1">50K+</div>
              <div className="text-gray-400 text-sm">Active Users</div>
            </div>
            <div className="text-center">
              <div className="text-3xl sm:text-4xl font-bold text-yellow-400 mb-1">2,400+</div>
              <div className="text-gray-400 text-sm">Scams Detected</div>
            </div>
            <div className="text-center">
              <div className="text-3xl sm:text-4xl font-bold text-blue-400 mb-1">4</div>
              <div className="text-gray-400 text-sm">Telegram Bots</div>
            </div>
          </div>
        </ScrollReveal>
      </div>
    </section>
  );
}
