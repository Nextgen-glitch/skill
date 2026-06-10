"use client";

import { useEffect, useRef, useState } from "react";
import { useInView, useReducedMotion } from "framer-motion";

function Counter({ to, suffix = "", decimals = 0 }: { to: number; suffix?: string; decimals?: number }) {
  const ref = useRef<HTMLSpanElement>(null);
  const inView = useInView(ref, { once: true, margin: "-60px" });
  const reduce = useReducedMotion();
  const [val, setVal] = useState(0);

  useEffect(() => {
    if (!inView) return;
    if (reduce) {
      setVal(to);
      return;
    }
    let raf = 0;
    const start = performance.now();
    const dur = 1400;
    const tick = (now: number) => {
      const p = Math.min((now - start) / dur, 1);
      const eased = 1 - Math.pow(1 - p, 3);
      setVal(to * eased);
      if (p < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [inView, to, reduce]);

  return (
    <span ref={ref} className="tabular-nums">
      {val.toLocaleString("en-US", {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals,
      })}
      {suffix}
    </span>
  );
}

const stats = [
  { to: 12000, suffix: "+", label: "Devices repaired" },
  { to: 4.9, decimals: 1, suffix: "★", label: "Average rating" },
  { to: 98, suffix: "%", label: "Same-week turnaround" },
  { to: 15, suffix: "k+", label: "Happy customers" },
];

export function Stats() {
  return (
    <section className="container-px py-10">
      <div className="glass grid grid-cols-2 gap-y-8 rounded-3xl px-6 py-10 sm:px-10 lg:grid-cols-4">
        {stats.map((s) => (
          <div key={s.label} className="text-center">
            <p className="text-3xl font-semibold text-gradient-gold sm:text-4xl">
              <Counter to={s.to} suffix={s.suffix} decimals={s.decimals ?? 0} />
            </p>
            <p className="mt-2 text-sm text-secondary">{s.label}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
