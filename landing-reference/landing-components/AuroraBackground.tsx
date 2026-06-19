"use client";

import { useEffect, useRef, useState } from "react";

/**
 * Aurora background — slow-drifting blurred color blobs that sit behind a section.
 * Optional mouse-follow glow for the hero.
 */
export function AuroraBackground({
  className = "",
  showMouseGlow = false,
}: {
  className?: string;
  showMouseGlow?: boolean;
}) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [mouse, setMouse] = useState({ x: 0.5, y: 0.3 });

  useEffect(() => {
    if (!showMouseGlow) return;
    const onMove = (e: MouseEvent) => {
      const el = containerRef.current;
      if (!el) return;
      const rect = el.getBoundingClientRect();
      setMouse({
        x: (e.clientX - rect.left) / rect.width,
        y: (e.clientY - rect.top) / rect.height,
      });
    };
    window.addEventListener("mousemove", onMove);
    return () => window.removeEventListener("mousemove", onMove);
  }, [showMouseGlow]);

  return (
    <div
      ref={containerRef}
      className={`pointer-events-none absolute inset-0 overflow-hidden ${className}`}
      aria-hidden
    >
      {/* Grid */}
      <div className="absolute inset-0 grid-bg opacity-50 mask-fade-b" />

      {/* Aurora washes — warm and subtle, like ink bleeding into paper */}
      <div
        className="absolute -top-32 -left-32 h-[480px] w-[480px] rounded-full blur-[120px] animate-aurora"
        style={{
          background: "radial-gradient(circle, rgba(122,40,40,0.08) 0%, transparent 70%)",
        }}
      />
      <div
        className="absolute top-1/3 -right-40 h-[520px] w-[520px] rounded-full blur-[120px] animate-aurora"
        style={{
          background: "radial-gradient(circle, rgba(61,122,78,0.06) 0%, transparent 70%)",
          animationDelay: "-6s",
        }}
      />
      <div
        className="absolute -bottom-32 left-1/3 h-[420px] w-[420px] rounded-full blur-[120px] animate-aurora"
        style={{
          background: "radial-gradient(circle, rgba(184,134,11,0.05) 0%, transparent 70%)",
          animationDelay: "-10s",
        }}
      />

      {/* Mouse-follow glow */}
      {showMouseGlow && (
        <div
          className="absolute h-[400px] w-[400px] rounded-full blur-[80px] transition-transform duration-300 ease-out"
          style={{
            left: `calc(${mouse.x * 100}% - 200px)`,
            top: `calc(${mouse.y * 100}% - 200px)`,
            background: "radial-gradient(circle, rgba(122,40,40,0.06) 0%, transparent 70%)",
          }}
        />
      )}
    </div>
  );
}
