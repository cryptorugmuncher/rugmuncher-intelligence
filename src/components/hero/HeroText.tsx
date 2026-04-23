/**
 * Animated Hero Typography
 * ========================
 * Character-by-character reveal + typewriter subtitle + shimmer gradient.
 */
import { useEffect, useState, useRef } from 'react';

interface HeroTextProps {
  headline?: string;
  subtitle?: string;
}

export default function HeroText({
  headline = "Don't Get Rugged",
  subtitle = "AI-powered scam detection for crypto traders. Real-time alerts, forensic wallet tracing, and community-driven intelligence.",
}: HeroTextProps) {
  const [headlineVisible, setHeadlineVisible] = useState(0);
  const [subtitleVisible, setSubtitleVisible] = useState(0);
  const [cursorVisible, setCursorVisible] = useState(true);
  const [started, setStarted] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // IntersectionObserver to start animation when in view
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !started) {
          setStarted(true);
        }
      },
      { threshold: 0.3 }
    );

    if (containerRef.current) {
      observer.observe(containerRef.current);
    }

    return () => observer.disconnect();
  }, [started]);

  // Headline character reveal
  useEffect(() => {
    if (!started) return;

    const chars = headline.length;
    let i = 0;
    const interval = setInterval(() => {
      i++;
      setHeadlineVisible(i);
      if (i >= chars) {
        clearInterval(interval);
        // Start subtitle after headline completes
        setTimeout(() => {
          let j = 0;
          const subInterval = setInterval(() => {
            j++;
            setSubtitleVisible(j);
            if (j >= subtitle.length) {
              clearInterval(subInterval);
            }
          }, 12);
        }, 300);
      }
    }, 35);

    return () => clearInterval(interval);
  }, [started, headline, subtitle]);

  // Blinking cursor
  useEffect(() => {
    const interval = setInterval(() => {
      setCursorVisible((v) => !v);
    }, 530);
    return () => clearInterval(interval);
  }, []);

  return (
    <div ref={containerRef} className="relative z-10 text-center lg:text-left">
      {/* Headline */}
      <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold mb-6 leading-tight">
        {headline.split('').map((char, i) => (
          <span
            key={i}
            className={`inline-block transition-all duration-100 ${
              i < headlineVisible
                ? 'opacity-100 translate-y-0'
                : 'opacity-0 translate-y-4'
            } ${char === ' ' ? 'w-3' : ''}`}
            style={{
              color: i < headlineVisible ? undefined : 'transparent',
              backgroundImage:
                i < headlineVisible
                  ? 'linear-gradient(135deg, #8b5cf6, #eab308)'
                  : 'none',
              WebkitBackgroundClip: i < headlineVisible ? 'text' : 'unset',
              backgroundClip: i < headlineVisible ? 'text' : 'unset',
              WebkitTextFillColor: i < headlineVisible ? 'transparent' : 'inherit',
            }}
          >
            {char === ' ' ? '\u00A0' : char}
          </span>
        ))}
      </h1>

      {/* Subtitle with typewriter effect */}
      <p className="text-xl sm:text-2xl text-gray-400 max-w-2xl mb-8 min-h-[3rem]">
        {subtitle.slice(0, subtitleVisible)}
        <span
          className={`inline-block w-0.5 h-6 bg-purple-400 ml-0.5 align-middle transition-opacity duration-100 ${
            cursorVisible && subtitleVisible < subtitle.length ? 'opacity-100' : 'opacity-0'
          }`}
        />
      </p>
    </div>
  );
}
