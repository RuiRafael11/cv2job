"use client";

import { motion } from "framer-motion";
import { ArrowRight, ExternalLink } from "lucide-react";
import { AuroraBackground } from "./AuroraBackground";
import { AnimatedSection } from "./AnimatedSection";

export function FinalCTA() {
  return (
    <section id="cta" className="relative overflow-hidden py-24 lg:py-32">
      <AuroraBackground />

      <div className="relative mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
        <AnimatedSection direction="scale" className="relative">
          <div className="relative overflow-hidden rounded-xl border border-tan bg-paper p-8 text-center paper-shadow-lg sm:p-14">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
            >
              <span className="font-mono-badge inline-flex items-center gap-2 rounded-full border border-oxblood/30 bg-oxblood/5 px-3 py-1 text-[11px] uppercase tracking-[0.18em] text-oxblood">
                <span className="h-1.5 w-1.5 rounded-full bg-oxblood animate-pulse-soft" />
                Ready when you are
              </span>
            </motion.div>

            <motion.h2
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.7, delay: 0.1 }}
              className="mt-6 font-display text-4xl font-bold leading-tight tracking-tight text-ink sm:text-5xl lg:text-6xl"
            >
              Your next interview
              <br />
              <span className="text-oxblood italic">is one upload away.</span>
            </motion.h2>

            <motion.p
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.7, delay: 0.2 }}
              className="mx-auto mt-6 max-w-xl text-lg leading-relaxed text-stone-600"
            >
              Free ATS preview, no login. €9 for 10 full optimizations — pay once, use them whenever.
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.7, delay: 0.3 }}
              className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row"
            >
              <a
                href="https://github.com/RuiRafael11/cv2job"
                target="_blank"
                rel="noreferrer"
                className="group flex h-12 w-full items-center justify-center gap-2 rounded-lg bg-oxblood px-7 font-medium text-paper transition-colors hover:bg-oxblood-deep sm:w-auto"
              >
                Run cv2job locally
                <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
              </a>
              <a
                href="https://github.com/RuiRafael11/cv2job"
                target="_blank"
                rel="noreferrer"
                className="flex h-12 w-full items-center justify-center gap-2 rounded-lg border border-tan-dark bg-bone px-7 font-medium text-ink transition-colors hover:border-oxblood hover:text-oxblood sm:w-auto"
              >
                <ExternalLink className="h-4 w-4" />
                Star on GitHub
              </a>
            </motion.div>
          </div>
        </AnimatedSection>
      </div>
    </section>
  );
}
