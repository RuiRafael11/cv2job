"use client";

import { motion } from "framer-motion";
import { ArrowRight, FileText, Sparkles, ShieldCheck } from "lucide-react";
import { AuroraBackground } from "./AuroraBackground";
import { AtsGauge, SubScoreCircle } from "./AtsGauge";
import { SectionBadge } from "./Brand";

export function Hero() {
  return (
    <section id="top" className="relative overflow-hidden pt-32 pb-20 sm:pt-40 lg:pt-48 lg:pb-28">
      <AuroraBackground showMouseGlow />

      <div className="relative mx-auto grid max-w-7xl grid-cols-1 items-center gap-12 px-4 sm:px-6 lg:grid-cols-[1.05fr_0.95fr] lg:gap-8 lg:px-8">
        {/* Left — copy */}
        <div className="text-center lg:text-left">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
            className="flex justify-center lg:justify-start"
          >
            <SectionBadge>ATS AI Resume Optimizer</SectionBadge>
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.1, ease: [0.22, 1, 0.36, 1] }}
            className="mt-6 font-display text-5xl font-bold leading-[1.05] tracking-tight text-ink sm:text-6xl lg:text-7xl"
          >
            Beat the bots.
            <br />
            <span className="text-oxblood italic">Get the interview.</span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.25, ease: [0.22, 1, 0.36, 1] }}
            className="mx-auto mt-6 max-w-xl text-lg leading-relaxed text-stone-600 lg:mx-0"
          >
            cv2job scores your CV against any job description the way an ATS does — then
            rewrites it into a clean Harvard-format PDF that gets past the screeners.
            <span className="text-ink"> No invented experience. Just a sharper you.</span>
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.4, ease: [0.22, 1, 0.36, 1] }}
            className="mt-8 flex flex-col items-center gap-3 sm:flex-row lg:justify-start"
          >
            <a
              href="#cta"
              className="flex h-12 w-full items-center justify-center gap-2 rounded-lg bg-oxblood px-6 text-base font-medium text-paper transition-colors hover:bg-oxblood-deep sm:w-auto"
            >
              Optimize my CV — €9 / 10
              <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
            </a>
            <a
              href="#demo"
              className="flex h-12 w-full items-center justify-center gap-2 rounded-lg border border-tan-dark bg-paper/60 px-6 text-base font-medium text-ink backdrop-blur transition-colors hover:border-oxblood hover:text-oxblood sm:w-auto"
            >
              See the demo
            </a>
          </motion.div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.7, delay: 0.6 }}
            className="mt-8 flex flex-wrap items-center justify-center gap-x-6 gap-y-3 text-sm text-stone-500 lg:justify-start"
          >
            <span className="inline-flex items-center gap-1.5">
              <ShieldCheck className="h-4 w-4 text-forest" />
              No invented experience
            </span>
            <span className="inline-flex items-center gap-1.5">
              <FileText className="h-4 w-4 text-oxblood" />
              Harvard-format PDF
            </span>
            <span className="inline-flex items-center gap-1.5">
              <Sparkles className="h-4 w-4 text-ochre" />
              Free ATS preview
            </span>
          </motion.div>
        </div>

        {/* Right — ATS dashboard mockup on paper card */}
        <motion.div
          initial={{ opacity: 0, scale: 0.96, y: 30 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          transition={{ duration: 1, delay: 0.4, ease: [0.22, 1, 0.36, 1] }}
          className="relative mx-auto w-full max-w-md lg:max-w-none"
        >
          <div className="glass-card relative rounded-xl p-6 sm:p-8">
            {/* Top row — wizard step indicator */}
            <div className="mb-6 flex items-center justify-between border-b border-tan pb-4">
              <div className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-forest animate-pulse-soft" />
                <span className="font-mono-badge text-[11px] tracking-[0.15em] text-stone-600 uppercase">
                  Results dashboard
                </span>
              </div>
              <span className="font-mono-badge text-[11px] text-stone-500">STEP 5 / 7</span>
            </div>

            {/* Main gauge */}
            <div className="flex justify-center">
              <AtsGauge
                score={78}
                size={240}
                label="ATS SCORE"
                caption="COM A VAGA"
                duration={2}
              />
            </div>

            {/* Sub-scores */}
            <div className="mt-8 grid grid-cols-4 gap-2 border-t border-tan pt-6">
              <SubScoreCircle label="Requisitos" score={32} points={40} size={80} />
              <SubScoreCircle label="Experiência" score={24} points={30} size={80} />
              <SubScoreCircle label="Termos" score={16} points={20} size={80} />
              <SubScoreCircle label="Formação" score={8} points={10} size={80} />
            </div>

            {/* AI diagnostic card */}
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 1.4 }}
              className="mt-6 rounded-lg border border-forest/30 bg-forest/5 p-4"
            >
              <div className="flex items-center justify-between">
                <span className="font-mono-badge text-[10px] tracking-[0.18em] text-forest uppercase">
                  AI Diagnostic
                </span>
                <span className="font-mono-badge rounded-full bg-forest/15 px-2 py-0.5 text-[10px] text-forest">
                  ALTA ADERÊNCIA
                </span>
              </div>
              <p className="mt-2 text-sm text-ink-soft">
                Strong keyword coverage on core requirements — add 2 missing tools
                (Kubernetes, Terraform) to push past 85.
              </p>
            </motion.div>
          </div>

          {/* Floating badges */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.7, delay: 1 }}
            className="absolute -left-4 top-1/3 hidden rounded-lg border border-tan-dark bg-paper p-3 paper-shadow sm:block animate-float-y"
          >
            <div className="font-mono-badge text-[10px] text-stone-500">MISSING</div>
            <div className="mt-1 flex flex-wrap gap-1">
              {["Kubernetes", "Terraform"].map((k) => (
                <span
                  key={k}
                  className="font-mono-badge rounded-md border border-brick/30 bg-brick/10 px-1.5 py-0.5 text-[10px] text-brick"
                >
                  {k}
                </span>
              ))}
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.7, delay: 1.2 }}
            className="absolute -right-4 bottom-1/4 hidden rounded-lg border border-tan-dark bg-paper p-3 paper-shadow sm:block animate-float-y"
            style={{ animationDelay: "-3s" }}
          >
            <div className="font-mono-badge text-[10px] text-stone-500">FOUND</div>
            <div className="mt-1 flex flex-wrap gap-1">
              {["Python", "FastAPI", "AWS"].map((k) => (
                <span
                  key={k}
                  className="font-mono-badge rounded-md border border-forest/30 bg-forest/10 px-1.5 py-0.5 text-[10px] text-forest"
                >
                  {k}
                </span>
              ))}
            </div>
          </motion.div>
        </motion.div>
      </div>

      {/* Bottom fade */}
      <div className="pointer-events-none absolute inset-x-0 bottom-0 h-32 bg-gradient-to-b from-transparent to-bone" />
    </section>
  );
}
