"use client";

import { useEffect, useRef, useState } from "react";
import { animate, useInView } from "framer-motion";

type Color = "accent" | "success" | "warning" | "danger";

const COLORS: Record<Color, { stroke: string; glow: string; text: string }> = {
  accent:  { stroke: "#7a2828", glow: "rgba(122,40,40,0.18)",  text: "#7a2828" },
  success: { stroke: "#3d7a4e", glow: "rgba(61,122,78,0.18)",  text: "#3d7a4e" },
  warning: { stroke: "#b8860b", glow: "rgba(184,134,11,0.18)", text: "#a37409" },
  danger:  { stroke: "#9b2c2c", glow: "rgba(155,44,44,0.18)",  text: "#9b2c2c" },
};

function pickColor(score: number): Color {
  if (score >= 70) return "success";
  if (score >= 40) return "warning";
  return "danger";
}

export function AtsGauge({
  score,
  size = 220,
  stroke = 12,
  label = "ATS SCORE",
  caption,
  animateOnView = true,
  duration = 1.6,
  color,
}: {
  score: number;
  size?: number;
  stroke?: number;
  label?: string;
  caption?: string;
  animateOnView?: boolean;
  duration?: number;
  color?: Color;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, amount: 0.4 });
  const shouldAnimate = animateOnView && inView;
  const [display, setDisplay] = useState(shouldAnimate ? 0 : score);

  useEffect(() => {
    if (!shouldAnimate) return;
    const controls = animate(0, score, {
      duration,
      ease: [0.22, 1, 0.36, 1],
      onUpdate: (v) => setDisplay(Math.round(v)),
    });
    return () => controls.stop();
  }, [score, shouldAnimate, duration]);

  const resolvedColor = color ?? pickColor(score);
  const c = COLORS[resolvedColor];

  const r = (size - stroke) / 2;
  const circumference = 2 * Math.PI * r;
  const progress = display / 100;
  const dashOffset = circumference * (1 - progress);

  const ticks = Array.from({ length: 60 });

  return (
    <div
      ref={ref}
      className="relative flex items-center justify-center"
      style={{ width: size, height: size }}
    >
      <div
        className="absolute inset-4 rounded-full blur-2xl"
        style={{ background: c.glow, opacity: 0.5 }}
      />
      <svg
        width={size}
        height={size}
        viewBox={`0 0 ${size} ${size}`}
        className="relative -rotate-90"
      >
        {ticks.map((_, i) => {
          const angle = (i / ticks.length) * 2 * Math.PI;
          const inner = r - 4;
          const outer = r + 2;
          // Round to 2 decimals to avoid SSR/CSR floating-point hydration mismatch
          const x1 = Math.round((size / 2 + Math.cos(angle) * inner) * 100) / 100;
          const y1 = Math.round((size / 2 + Math.sin(angle) * inner) * 100) / 100;
          const x2 = Math.round((size / 2 + Math.cos(angle) * outer) * 100) / 100;
          const y2 = Math.round((size / 2 + Math.sin(angle) * outer) * 100) / 100;
          const isMajor = i % 5 === 0;
          return (
            <line
              key={i}
              x1={x1}
              y1={y1}
              x2={x2}
              y2={y2}
              stroke={isMajor ? "#b8a88e" : "#d9cdb8"}
              strokeWidth={isMajor ? 1.5 : 1}
            />
          );
        })}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke="#e8dfd0"
          strokeWidth={stroke}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke={c.stroke}
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={dashOffset}
          style={{
            filter: `drop-shadow(0 0 12px ${c.glow})`,
            transition: "stroke 0.6s ease",
          }}
        />
      </svg>

      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <div
          className="font-display font-bold leading-none tabular-nums"
          style={{ color: c.text, fontSize: size * 0.32 }}
        >
          {display}
        </div>
        <div
          className="font-mono-badge tracking-[0.2em] text-stone-500 mt-1"
          style={{ fontSize: size * 0.055 }}
        >
          {label}
        </div>
        {caption && (
          <div className="font-mono-badge text-stone-400 mt-1" style={{ fontSize: size * 0.05 }}>
            {caption}
          </div>
        )}
      </div>
    </div>
  );
}

export function SubScoreCircle({
  label,
  score,
  points,
  size = 96,
}: {
  label: string;
  score: number;
  points: number;
  size?: number;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, amount: 0.4 });
  const [display, setDisplay] = useState(0);
  const stroke = 6;
  const r = (size - stroke) / 2;
  const circumference = 2 * Math.PI * r;

  useEffect(() => {
    if (!inView) return;
    const controls = animate(0, score, {
      duration: 1.2,
      ease: [0.22, 1, 0.36, 1],
      onUpdate: (v) => setDisplay(Math.round(v)),
    });
    return () => controls.stop();
  }, [score, inView]);

  const color = pickColor(score);
  const c = COLORS[color];
  const dashOffset = circumference * (1 - display / 100);

  return (
    <div ref={ref} className="flex flex-col items-center gap-2">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="-rotate-90">
          <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="#e8dfd0" strokeWidth={stroke} />
          <circle
            cx={size / 2}
            cy={size / 2}
            r={r}
            fill="none"
            stroke={c.stroke}
            strokeWidth={stroke}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={dashOffset}
            style={{ filter: `drop-shadow(0 2px 6px ${c.glow})` }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="font-display text-xl font-semibold tabular-nums" style={{ color: c.text }}>
            {display}
          </span>
          <span className="font-mono-badge text-[10px] text-stone-400">/{points}</span>
        </div>
      </div>
      <span className="font-mono-badge text-[10px] tracking-[0.15em] text-stone-500 uppercase">
        {label}
      </span>
    </div>
  );
}
