"use client";

import { motion } from "framer-motion";
import {
  ClipboardList,
  Upload,
  ScanSearch,
  Wand2,
  Download,
} from "lucide-react";
import { AnimatedSection, StaggerGroup, staggerItem } from "./AnimatedSection";
import { SectionBadge } from "./Brand";

const STEPS = [
  {
    n: "01",
    icon: ClipboardList,
    title: "Answer 3 quick questions",
    body: "How often you get interviews, your career goal, and target seniority. The answers calibrate how aggressively the optimizer will rewrite your CV.",
  },
  {
    n: "02",
    icon: Upload,
    title: "Upload CV + job description",
    body: "Drop a PDF, DOCX, TXT or MD résumé. Then paste the job description text — or upload it as a file. Both are parsed to plain text in seconds.",
  },
  {
    n: "03",
    icon: ScanSearch,
    title: "Get your free ATS diagnostic",
    body: "Local TF-IDF scoring returns a 100-point score across 4 dimensions, present/missing keywords, and a cosine similarity caption. No login required for the preview.",
  },
  {
    n: "04",
    icon: Wand2,
    title: "Unlock the AI rewrite",
    body: "One credit triggers the optimizer. Gemini rewrites your CV in clean Markdown, integrating missing keywords only when truthful — never inventing experience.",
  },
  {
    n: "05",
    icon: Download,
    title: "Download your Harvard PDF",
    body: "Export the optimized CV as an academic-style Harvard PDF or Markdown file. Re-analyze it against the same job to verify the score went up.",
  },
];

export function HowItWorks() {
  return (
    <section id="how" className="relative py-24 lg:py-32">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-3xl text-center">
          <AnimatedSection direction="up" className="flex justify-center">
            <SectionBadge>How it works</SectionBadge>
          </AnimatedSection>
          <AnimatedSection direction="up" delay={0.1}>
            <h2 className="mt-6 font-display text-4xl font-bold leading-tight tracking-tight text-ink sm:text-5xl">
              From upload to optimized PDF
              <br />
              <span className="text-gradient-soft">in under a minute.</span>
            </h2>
          </AnimatedSection>
        </div>

        <div className="relative mt-20">
          {/* Vertical connector line */}
          <div className="absolute left-6 top-0 bottom-0 hidden w-px bg-tan-dark md:block lg:left-1/2" />

          <StaggerGroup className="space-y-6 md:space-y-2">
            {STEPS.map((s, i) => {
              const isRight = i % 2 === 1;
              return (
                <motion.div
                  key={s.n}
                  variants={staggerItem}
                  className={`relative flex flex-col gap-4 md:flex-row md:items-center ${
                    isRight ? "md:flex-row-reverse" : ""
                  }`}
                >
                  {/* Spacer for alternating layout */}
                  <div className="hidden md:block md:w-1/2" />

                  <div className="relative w-full md:w-1/2 md:px-8">
                    <div className="group relative overflow-hidden rounded-xl border border-tan bg-paper p-6 transition-colors hover:border-oxblood/30 paper-shadow lg:p-7">
                      <div className="flex items-start gap-4">
                        <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-lg border border-oxblood/30 bg-oxblood/5 text-oxblood">
                          <s.icon className="h-5 w-5" />
                        </div>
                        <div className="flex-1">
                          <div className="flex items-baseline gap-3">
                            <span className="font-display text-2xl font-semibold text-oxblood">
                              {s.n}
                            </span>
                            <h3 className="font-display text-lg font-semibold text-ink">{s.title}</h3>
                          </div>
                          <p className="mt-2 text-sm leading-relaxed text-stone-600">{s.body}</p>
                        </div>
                      </div>
                    </div>

                    {/* Dot on the timeline */}
                    <div
                      className={`absolute top-1/2 hidden h-3 w-3 -translate-y-1/2 rounded-full bg-oxblood ring-4 ring-bone md:block ${
                        isRight ? "left-[-44px]" : "right-[-44px]"
                      } lg:left-1/2 lg:right-auto lg:-translate-x-1/2`}
                      style={isRight ? { right: "auto", left: "-44px" } : undefined}
                    />
                  </div>
                </motion.div>
              );
            })}
          </StaggerGroup>
        </div>
      </div>
    </section>
  );
}
