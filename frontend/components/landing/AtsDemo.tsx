"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { AtsGauge, SubScoreCircle } from "./AtsGauge";
import { AnimatedSection } from "./AnimatedSection";
import { SectionBadge } from "./Brand";
import { Briefcase, TrendingUp, Check, X } from "lucide-react";

type Scenario = {
  id: string;
  label: string;
  cvSummary: string;
  jobTitle: string;
  score: number;
  subs: { label: string; score: number; points: number }[];
  present: string[];
  missing: string[];
  diagnostic: string;
  diagnosticTone: "alta" | "media" | "baixa";
};

const SCENARIOS: Scenario[] = [
  {
    id: "before",
    label: "Before cv2job",
    cvSummary: "Generic Python dev CV, no tailoring",
    jobTitle: "Senior Backend Engineer · fintech",
    score: 41,
    subs: [
      { label: "Requisitos", score: 14, points: 40 },
      { label: "Experiência", score: 15, points: 30 },
      { label: "Termos", score: 9, points: 20 },
      { label: "Formação", score: 3, points: 10 },
    ],
    present: ["Python", "PostgreSQL", "Git"],
    missing: ["Kubernetes", "Terraform", "AWS", "CI/CD", "Microservices", "gRPC"],
    diagnostic:
      "Core backend keywords present, but the CV reads as a junior profile against a senior role. Missing 6 of 10 listed requirements — ATS will likely filter this CV before human review.",
    diagnosticTone: "baixa",
  },
  {
    id: "after",
    label: "After cv2job",
    cvSummary: "Same CV, rewritten truthfully with the missing keywords",
    jobTitle: "Senior Backend Engineer · fintech",
    score: 86,
    subs: [
      { label: "Requisitos", score: 35, points: 40 },
      { label: "Experiência", score: 27, points: 30 },
      { label: "Termos", score: 18, points: 20 },
      { label: "Formação", score: 8, points: 10 },
    ],
    present: ["Python", "PostgreSQL", "Git", "Kubernetes", "Terraform", "AWS", "CI/CD", "Microservices"],
    missing: ["gRPC"],
    diagnostic:
      "Strong keyword coverage on core requirements. The action plan added Kubernetes and Terraform as truthful project context — score is now in the high-adherence band.",
    diagnosticTone: "alta",
  },
];

const TONE_STYLES = {
  alta:  { label: "ALTA ADERÊNCIA", cls: "border-forest/30 bg-forest/5 text-forest" },
  media: { label: "MÉDIA",          cls: "border-ochre/30 bg-ochre/5 text-ochre" },
  baixa: { label: "BAIXA",          cls: "border-brick/30 bg-brick/5 text-brick" },
} as const;

export function AtsDemo() {
  const [active, setActive] = useState<Scenario>(SCENARIOS[0]);

  return (
    <section id="demo" className="relative py-24 lg:py-32">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-3xl text-center">
          <AnimatedSection direction="up" className="flex justify-center">
            <SectionBadge>Live ATS demo</SectionBadge>
          </AnimatedSection>
          <AnimatedSection direction="up" delay={0.1}>
            <h2 className="mt-6 font-display text-4xl font-bold leading-tight tracking-tight sm:text-5xl">
              Watch the score climb
              <br />
              <span className="text-gradient-accent">from 41 to 86.</span>
            </h2>
          </AnimatedSection>
          <AnimatedSection direction="up" delay={0.2}>
            <p className="mt-6 text-lg leading-relaxed text-zinc-400">
              Same CV. Same candidate. Same job. The only difference is what cv2job's optimizer
              did to it. Toggle below to see the before/after.
            </p>
          </AnimatedSection>
        </div>

        {/* Toggle */}
        <AnimatedSection direction="up" delay={0.3} className="mt-12 flex justify-center">
          <div className="inline-flex rounded-lg border border-tan-dark bg-paper p-1">
            {SCENARIOS.map((s) => (
              <button
                key={s.id}
                onClick={() => setActive(s)}
                className={`relative rounded-md px-5 py-2.5 text-sm font-medium transition-colors ${
                  active.id === s.id ? "text-paper" : "text-stone-600 hover:text-ink"
                }`}
              >
                {active.id === s.id && (
                  <motion.div
                    layoutId="demo-toggle"
                    className="absolute inset-0 rounded-md bg-oxblood"
                    transition={{ type: "spring", stiffness: 300, damping: 30 }}
                  />
                )}
                <span className="relative z-10">{s.label}</span>
              </button>
            ))}
          </div>
        </AnimatedSection>

        {/* Dashboard mockup */}
        <AnimatedSection direction="scale" delay={0.2} className="mt-12">
          <div className="relative overflow-hidden rounded-xl border border-tan bg-paper p-6 paper-shadow-lg sm:p-10">
            <div className="pointer-events-none absolute -right-32 -top-32 h-64 w-64 rounded-full bg-oxblood/5 blur-3xl" />

            {/* Header */}
            <div className="flex flex-col gap-2 border-b border-tan pb-6 sm:flex-row sm:items-end sm:justify-between">
              <div>
                <div className="flex items-center gap-2 font-mono-badge text-[11px] tracking-[0.15em] text-stone-500 uppercase">
                  <Briefcase className="h-3.5 w-3.5" />
                  Job description analyzed
                </div>
                <h3 className="mt-2 font-display text-xl font-semibold text-ink">{active.jobTitle}</h3>
                <p className="mt-1 text-sm text-stone-500">{active.cvSummary}</p>
              </div>
              <div className="font-mono-badge text-[11px] text-stone-400">
                ANALYSIS_ID: cv2job-{active.id}-{active.score}
              </div>
            </div>

            {/* Main grid — gauge + sub-scores */}
            <div className="mt-8 grid grid-cols-1 gap-8 lg:grid-cols-[1fr_1.2fr]">
              <div className="flex flex-col items-center justify-center rounded-xl border border-tan bg-bone p-6">
                <AnimatePresence mode="wait">
                  <motion.div
                    key={active.id}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    transition={{ duration: 0.5 }}
                  >
                    <AtsGauge
                      score={active.score}
                      size={220}
                      label="ATS SCORE"
                      caption="COM A VAGA"
                      duration={1.4}
                    />
                  </motion.div>
                </AnimatePresence>
              </div>

              <div>
                <div className="font-mono-badge mb-4 text-[11px] tracking-[0.15em] text-stone-500 uppercase">
                  Score breakdown
                </div>
                <div className="grid grid-cols-2 gap-4 sm:grid-cols-4 lg:grid-cols-2 xl:grid-cols-4">
                  {active.subs.map((s) => (
                    <div
                      key={s.label}
                      className="flex flex-col items-center rounded-lg border border-tan bg-bone p-4"
                    >
                      <SubScoreCircle label={s.label} score={s.score} points={s.points} size={84} />
                    </div>
                  ))}
                </div>

                {/* Diagnostic */}
                <AnimatePresence mode="wait">
                  <motion.div
                    key={active.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    transition={{ duration: 0.4 }}
                    className={`mt-5 rounded-lg border p-4 ${TONE_STYLES[active.diagnosticTone].cls}`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-mono-badge text-[10px] tracking-[0.18em] uppercase opacity-80">
                        AI Diagnostic
                      </span>
                      <span className="font-mono-badge rounded-full border border-current px-2 py-0.5 text-[10px] opacity-90">
                        {TONE_STYLES[active.diagnosticTone].label}
                      </span>
                    </div>
                    <p className="mt-2 text-sm leading-relaxed text-ink-soft">
                      {active.diagnostic}
                    </p>
                  </motion.div>
                </AnimatePresence>
              </div>
            </div>

            {/* Keywords */}
            <div className="mt-8 grid grid-cols-1 gap-6 md:grid-cols-2">
              <div className="rounded-lg border border-forest/20 bg-forest/5 p-5">
                <div className="flex items-center gap-2">
                  <Check className="h-4 w-4 text-forest" />
                  <span className="font-mono-badge text-[11px] tracking-[0.18em] text-forest uppercase">
                    Encontrados · {active.present.length}
                  </span>
                </div>
                <div className="mt-3 flex flex-wrap gap-1.5">
                  {active.present.map((k) => (
                    <span
                      key={k}
                      className="font-mono-badge rounded-md border border-forest/30 bg-forest/10 px-2 py-1 text-xs text-forest"
                    >
                      {k}
                    </span>
                  ))}
                </div>
              </div>

              <div className="rounded-lg border border-brick/20 bg-brick/5 p-5">
                <div className="flex items-center gap-2">
                  <X className="h-4 w-4 text-brick" />
                  <span className="font-mono-badge text-[11px] tracking-[0.18em] text-brick uppercase">
                    Em falta · {active.missing.length}
                  </span>
                </div>
                <div className="mt-3 flex flex-wrap gap-1.5">
                  {active.missing.length === 0 ? (
                    <span className="text-sm text-stone-500">No missing keywords — perfect coverage.</span>
                  ) : (
                    active.missing.map((k) => (
                      <span
                        key={k}
                        className="font-mono-badge rounded-md border border-brick/30 bg-brick/10 px-2 py-1 text-xs text-brick"
                      >
                        {k}
                      </span>
                    ))
                  )}
                </div>
              </div>
            </div>

            {/* Footer note */}
            <div className="mt-8 flex items-center gap-2 border-t border-tan pt-6 text-xs text-stone-500">
              <TrendingUp className="h-3.5 w-3.5 text-oxblood" />
              <span>
                This is a static demo. The real app scores <em>your</em> CV against <em>your</em> job
                description using TF-IDF cosine similarity.
              </span>
            </div>
          </div>
        </AnimatedSection>
      </div>
    </section>
  );
}
