"use client";

import { motion } from "framer-motion";
import { AnimatedSection, StaggerGroup, staggerItem } from "./AnimatedSection";
import { SectionBadge } from "./Brand";
import { AlertTriangle, Bot, FileX2 } from "lucide-react";

const PAIN = [
  {
    icon: Bot,
    title: "An ATS rejects you in 3 seconds",
    body: "Applicant Tracking Systems parse, score, and rank every CV before a human ever opens it. If the keywords, structure, or semantics don't match the job description, the file is silently buried.",
  },
  {
    icon: FileX2,
    title: "You don't know why you're filtered out",
    body: "Generic 'resume tips' can't tell you which exact keywords are missing, which requirements are uncovered, or how your experience reads against a specific vacancy. You're optimizing blind.",
  },
  {
    icon: AlertTriangle,
    title: "AI writers invent things you didn't do",
    body: "Most AI résumé tools hallucinate employers, dates, and degrees to 'look good'. The result: a CV you can't defend in an interview — and one that recruiters instantly spot as fabricated.",
  },
];

export function Problem() {
  return (
    <section id="problem" className="relative py-24 lg:py-32">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-3xl text-center">
          <AnimatedSection direction="up" className="flex justify-center">
            <SectionBadge>The problem</SectionBadge>
          </AnimatedSection>
          <AnimatedSection direction="up" delay={0.1}>
            <h2 className="mt-6 font-display text-4xl font-bold leading-tight tracking-tight text-ink sm:text-5xl">
              Your CV isn't losing to other candidates.
              <br />
              <span className="text-gradient-soft">It's losing to a script.</span>
            </h2>
          </AnimatedSection>
          <AnimatedSection direction="up" delay={0.2}>
            <p className="mt-6 text-lg leading-relaxed text-stone-600">
              Before a recruiter ever sees your name, an ATS has already decided whether you're
              worth their time. cv2job shows you exactly what that decision looks like — and gives
              you the levers to flip it.
            </p>
          </AnimatedSection>
        </div>

        <StaggerGroup className="mt-16 grid grid-cols-1 gap-6 md:grid-cols-3">
          {PAIN.map((p) => (
            <motion.div
              key={p.title}
              variants={staggerItem}
              className="group relative overflow-hidden rounded-xl border border-tan bg-paper p-6 transition-all hover:border-brick/40 hover:-translate-y-0.5 paper-shadow"
            >
              <div className="relative">
                <div className="flex h-11 w-11 items-center justify-center rounded-lg border border-brick/30 bg-brick/10 text-brick">
                  <p.icon className="h-5 w-5" />
                </div>
                <h3 className="mt-5 font-display text-xl font-semibold text-ink">{p.title}</h3>
                <p className="mt-3 text-sm leading-relaxed text-stone-600">{p.body}</p>
              </div>
            </motion.div>
          ))}
        </StaggerGroup>
      </div>
    </section>
  );
}
