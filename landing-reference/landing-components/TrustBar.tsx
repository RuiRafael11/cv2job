"use client";

import { AnimatedSection } from "./AnimatedSection";

const STATS = [
  { value: "75%", label: "of CVs rejected by ATS bots before a human sees them" },
  { value: "4", label: "weighted dimensions scored against the job description" },
  { value: "30s", label: "from upload to a full diagnostic + action plan" },
  { value: "€9", label: "flat — 10 optimizations, no subscription, no lock-in" },
];

const MARQUEE = [
  "Gemini 2.5 Flash",
  "TF-IDF cosine similarity",
  "Harvard-format PDF",
  "Bilingual stopwords (EN + PT)",
  "Truthful rewriting — no fabrication",
  "SHA-256 session tokens",
  "Stripe Checkout",
  "OpenRouter Gemma 2 9B",
  "fpdf2 renderer",
  "Streamlit + FastAPI",
];

export function TrustBar() {
  return (
    <section className="relative border-y border-tan bg-tan-soft/50 py-16">
      {/* Stats */}
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <AnimatedSection direction="fade" className="mb-12 text-center">
          <p className="font-mono-badge text-[11px] tracking-[0.2em] text-stone-500 uppercase">
            By the numbers
          </p>
        </AnimatedSection>

        <div className="grid grid-cols-2 gap-6 lg:grid-cols-4">
          {STATS.map((s, i) => (
            <AnimatedSection
              key={s.value}
              direction="up"
              delay={i * 0.1}
              className="text-center"
            >
              <div className="font-display text-4xl font-bold text-oxblood sm:text-5xl">
                {s.value}
              </div>
              <p className="mt-2 text-sm leading-relaxed text-stone-600">{s.label}</p>
            </AnimatedSection>
          ))}
        </div>
      </div>

      {/* Marquee of tech */}
      <div className="relative mt-14 overflow-hidden">
        <div className="pointer-events-none absolute inset-y-0 left-0 z-10 w-32 bg-gradient-to-r from-tan-soft to-transparent" />
        <div className="pointer-events-none absolute inset-y-0 right-0 z-10 w-32 bg-gradient-to-l from-tan-soft to-transparent" />
        <div className="flex w-max animate-marquee gap-3">
          {[...MARQUEE, ...MARQUEE].map((t, i) => (
            <span
              key={i}
              className="font-mono-badge flex items-center gap-2 rounded-full border border-tan-dark bg-paper/60 px-4 py-2 text-xs text-stone-600"
            >
              <span className="h-1 w-1 rounded-full bg-oxblood" />
              {t}
            </span>
          ))}
        </div>
      </div>
    </section>
  );
}
