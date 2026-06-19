"use client";

import { motion, useScroll, useTransform } from "framer-motion";
import { useRef } from "react";

/** A small wordmark logo for the navbar */
export function Wordmark({ className = "" }: { className?: string }) {
  return (
    <a href="#top" className={`group flex items-center gap-2.5 ${className}`}>
      <span className="relative flex h-8 w-8 items-center justify-center rounded-md bg-oxblood text-paper">
        <svg viewBox="0 0 24 24" fill="none" className="h-4 w-4">
          <path
            d="M4 6h16M4 12h10M4 18h7"
            stroke="currentColor"
            strokeWidth="2.5"
            strokeLinecap="round"
          />
        </svg>
      </span>
      <span className="font-display text-xl font-semibold tracking-tight text-ink">
        cv<span className="text-oxblood italic">2</span>job
      </span>
    </a>
  );
}

/** Wrapper that adds a subtle parallax to its children based on scroll position */
export function Parallax({
  children,
  offset = 60,
  className,
}: {
  children: React.ReactNode;
  offset?: number;
  className?: string;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start end", "end start"],
  });
  const y = useTransform(scrollYProgress, [0, 1], [-offset / 2, offset / 2]);
  return (
    <motion.div ref={ref} style={{ y }} className={className}>
      {children}
    </motion.div>
  );
}

/** Section badge — the mono-font pill used as a label above every section */
export function SectionBadge({ children }: { children: React.ReactNode }) {
  return (
    <span className="inline-flex items-center gap-2 rounded-full border border-oxblood/30 bg-oxblood/5 px-3 py-1 font-mono-badge text-[11px] font-medium uppercase tracking-[0.18em] text-oxblood">
      <span className="h-1.5 w-1.5 rounded-full bg-oxblood animate-pulse-soft" />
      {children}
    </span>
  );
}
