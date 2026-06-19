"use client";

import { motion } from "framer-motion";
import {
  Gauge,
  KeyRound,
  BrainCircuit,
  ListChecks,
  FileOutput,
  ShieldCheck,
} from "lucide-react";
import { AnimatedSection, StaggerGroup, staggerItem } from "./AnimatedSection";
import { SectionBadge } from "./Brand";

const FEATURES = [
  {
    icon: Gauge,
    title: "4-dimension ATS score",
    body: "A 100-point weighted score across Requirements (40), Experience (30), Terms (20), and Education (10) — computed deterministically with TF-IDF cosine similarity, so the number is auditable, not a vibe.",
  },
  {
    icon: KeyRound,
    title: "Keyword gap analysis",
    body: "See exactly which terms from the job description are present (green) and missing (red). The tokenizer strips English and Portuguese stopwords, so the keywords you see are the ones that actually move the score.",
  },
  {
    icon: BrainCircuit,
    title: "AI diagnostic + action plan",
    body: "A plain-language explanation of your main weakness, plus up to three prioritized next steps — each tagged with a high/medium impact rating. The AI is instructed never to contradict the local scorer.",
  },
  {
    icon: ListChecks,
    title: "Onboarding wizard",
    body: "Three quick questions calibrate the optimization to your situation: interview response rate, career goal, and target seniority. Junior candidates get education-weighted scoring; seniors get experience-weighted.",
  },
  {
    icon: FileOutput,
    title: "Harvard-format PDF export",
    body: "Optimized CV is rendered as an academic-style Harvard résumé — EDUCATION first, then EXPERIENCE, then SKILLS, then PROJECTS. DejaVuSerif typesetting with full Unicode sanitization for any language.",
  },
  {
    icon: ShieldCheck,
    title: "Truthfulness enforcement",
    body: "The optimizer prompt has hard rules: never invent employers, dates, degrees, or tools that aren't in your original CV. Missing keywords are integrated only when the source material actually supports them.",
  },
];

export function Features() {
  return (
    <section id="features" className="relative py-24 lg:py-32">
      {/* Subtle backdrop */}
      <div className="pointer-events-none absolute inset-0 dot-bg opacity-40 mask-radial" />

      <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-3xl text-center">
          <AnimatedSection direction="up" className="flex justify-center">
            <SectionBadge>What's inside</SectionBadge>
          </AnimatedSection>
          <AnimatedSection direction="up" delay={0.1}>
            <h2 className="mt-6 font-display text-4xl font-bold leading-tight tracking-tight text-ink sm:text-5xl">
              A full diagnostic suite,
              <br />
              <span className="text-oxblood italic">not a magic rewrite button.</span>
            </h2>
          </AnimatedSection>
          <AnimatedSection direction="up" delay={0.2}>
            <p className="mt-6 text-lg leading-relaxed text-stone-600">
              Every feature is built around one question: <em>what would an ATS see?</em> The
              answer is measurable — and so is every improvement you make.
            </p>
          </AnimatedSection>
        </div>

        <StaggerGroup className="mt-16 grid grid-cols-1 gap-px overflow-hidden rounded-xl border border-tan bg-tan sm:grid-cols-2 lg:grid-cols-3">
          {FEATURES.map((f, i) => (
            <motion.div
              key={f.title}
              variants={staggerItem}
              className="group relative bg-paper p-7 transition-colors hover:bg-tan-soft/60"
            >
              <div className="flex items-center gap-3">
                <span className="font-mono-badge text-[11px] text-stone-400">
                  {String(i + 1).padStart(2, "0")}
                </span>
                <div className="h-px flex-1 bg-tan" />
              </div>
              <div className="mt-5 flex h-11 w-11 items-center justify-center rounded-lg border border-tan-dark bg-bone text-oxblood transition-colors group-hover:border-oxblood/40 group-hover:bg-oxblood/5">
                <f.icon className="h-5 w-5" />
              </div>
              <h3 className="mt-5 font-display text-xl font-semibold text-ink">{f.title}</h3>
              <p className="mt-3 text-sm leading-relaxed text-stone-600">{f.body}</p>
            </motion.div>
          ))}
        </StaggerGroup>
      </div>
    </section>
  );
}
