/**
 * Live Stats Counter
 * ==================
 * Animated counting numbers that tick up on viewport entry.
 */
import { useEffect, useState, useRef } from 'react';

interface Stat {
  label: string;
  value: number;
  suffix?: string;
  prefix?: string;
}

const STATS: Stat[] = [
  { label: 'Scams Detected', value: 2847, suffix: '+' },
  { label: 'Value Saved', value: 2.4, suffix: 'M+', prefix: '$' },
  { label: 'Active Agents', value: 8 },
  { label: 'Community Members', value: 12450, suffix: '+' },
];

function AnimatedCounter({ stat, inView }: { stat: Stat; inView: boolean }) {
  const [count, setCount] = useState(0);
  const countRef = useRef(0);
  const rafRef = useRef<number>(0);

  useEffect(() => {
    if (!inView) return;

    const duration = 2000;
    const startTime = performance.now();
    const target = stat.value;

    const animate = (now: number) => {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      // Ease out cubic
      const eased = 1 - Math.pow(1 - progress, 3);
      countRef.current = eased * target;
      setCount(countRef.current);

      if (progress < 1) {
        rafRef.current = requestAnimationFrame(animate);
      }
    };

    rafRef.current = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(rafRef.current);
  }, [inView, stat.value]);

  const displayValue = stat.value < 10 ? count.toFixed(1) : Math.floor(count).toLocaleString();

  return (
    <div className="text-center">
      <div className="text-3xl sm:text-4xl font-bold text-white">
        {stat.prefix || ''}
        {displayValue}
        {stat.suffix || ''}
      </div>
      <div className="text-sm text-gray-500 mt-1">{stat.label}</div>
    </div>
  );
}

export default function LiveStats() {
  const [inView, setInView] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setInView(true);
        }
      },
      { threshold: 0.3 }
    );

    if (ref.current) {
      observer.observe(ref.current);
    }

    return () => observer.disconnect();
  }, []);

  return (
    <div ref={ref} className="grid grid-cols-2 md:grid-cols-4 gap-6">
      {STATS.map((stat, i) => (
        <div
          key={stat.label}
          className={`bg-[#12121a]/80 backdrop-blur border border-purple-500/10 rounded-xl p-5 transition-all duration-700 ${
            inView ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-6'
          }`}
          style={{ transitionDelay: `${i * 150}ms` }}
        >
          <AnimatedCounter stat={stat} inView={inView} />
        </div>
      ))}
    </div>
  );
}
