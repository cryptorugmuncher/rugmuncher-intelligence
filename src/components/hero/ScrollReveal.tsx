/**
 * Scroll Reveal Wrapper
 * =====================
 * Wraps children in an IntersectionObserver-powered reveal animation.
 * Use throughout the page for scroll-driven stagger effects.
 */
import { useEffect, useRef, useState, type ReactNode } from 'react';

interface ScrollRevealProps {
  children: ReactNode;
  direction?: 'up' | 'down' | 'left' | 'right';
  delay?: number;
  duration?: number;
  distance?: number;
  className?: string;
  once?: boolean;
}

export default function ScrollReveal({
  children,
  direction = 'up',
  delay = 0,
  duration = 700,
  distance = 40,
  className = '',
  once = true,
}: ScrollRevealProps) {
  const [visible, setVisible] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setVisible(true);
          if (once) observer.unobserve(el);
        } else if (!once) {
          setVisible(false);
        }
      },
      { threshold: 0.15, rootMargin: '0px 0px -40px 0px' }
    );

    observer.observe(el);
    return () => observer.disconnect();
  }, [once]);

  const transforms = {
    up: `translateY(${visible ? 0 : distance}px)`,
    down: `translateY(${visible ? 0 : -distance}px)`,
    left: `translateX(${visible ? 0 : distance}px)`,
    right: `translateX(${visible ? 0 : -distance}px)`,
  };

  return (
    <div
      ref={ref}
      className={className}
      style={{
        opacity: visible ? 1 : 0,
        transform: transforms[direction],
        transition: `opacity ${duration}ms ease-out ${delay}ms, transform ${duration}ms cubic-bezier(0.22, 1, 0.36, 1) ${delay}ms`,
        willChange: 'opacity, transform',
      }}
    >
      {children}
    </div>
  );
}
