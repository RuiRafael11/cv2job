"use client";

import { motion } from "framer-motion";
import { Check, Sparkles } from "lucide-react";
import { AnimatedSection } from "./AnimatedSection";
import { SectionBadge } from "./Brand";

const INCLUDED = [
  "10 full CV optimizations",
  "Unlimited free ATS previews",
  "AI diagnostic + action plan",
  "Harvard-format PDF export",
  "Markdown export",
  "Keyword gap analysis (EN + PT)",
  "Onboarding wizard calibration",
  "Session tokens stored as SHA-256 hashes",
  "No subscription — pay once, use anytime",
];

export function Pricing() {
  return (
    <section id="pricing" className="relative py-24 lg:py-32">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-3xl text-center">
          <AnimatedSection direction="up" className="flex justify-center">
            <SectionBadge>Pricing</SectionBadge>
          </AnimatedSection>
          <AnimatedSection direction="up" delay={0.1}>
            <h2 className="mt-6 font-display text-4xl font-bold leading-tight tracking-tight text-ink sm:text-5xl">
              One flat pack.
              <br />
              <span className="text-oxblood italic">No subscription trap.</span>
            </h2>
          </AnimatedSection>
          <AnimatedSection direction="up" delay={0.2}>
            <p className="mt-6 text-lg leading-relaxed text-stone-600">
              Job hunting is episodic — you don't need a monthly bill. Buy 10 credits when you need
              them, use them whenever. They don't expire.
            </p>
          </AnimatedSection>
        </div>

        <AnimatedSection direction="scale" delay={0.2} className="mt-16 flex justify-center">
          <div className="relative w-full max-w-md">
            <div className="relative overflow-hidden rounded-xl border border-tan bg-paper p-8 paper-shadow-lg">
              {/* Header */}
              <div className="flex items-start justify-between">
                <div>
                  <div className="font-mono-badge text-[11px] tracking-[0.18em] text-oxblood uppercase">
                    Credit pack
                  </div>
                  <h3 className="mt-1 font-display text-2xl font-semibold text-ink">10 optimizations</h3>
                </div>
                <span className="flex items-center gap-1 rounded-full border border-oxblood/30 bg-oxblood/5 px-2.5 py-1 text-[11px] text-oxblood">
                  <Sparkles className="h-3 w-3" />
                  Popular
                </span>
              </div>

              {/* Price */}
              <div className="mt-6 flex items-baseline gap-2">
                <span className="font-display text-6xl font-bold text-oxblood">€9</span>
                <span className="text-stone-500">/ 10 credits</span>
              </div>
              <p className="mt-2 text-sm text-stone-500">
                €0.90 per optimized CV. One-time payment via Stripe.
              </p>

              {/* CTA */}
              <a
                href="/app"
                className="mt-6 flex h-12 w-full items-center justify-center rounded-lg bg-oxblood px-6 font-medium text-paper transition-colors hover:bg-oxblood-deep"
              >
                Get 10 credits
              </a>

              {/* Free preview callout */}
              <div className="mt-4 rounded-lg border border-tan bg-bone p-3 text-center text-xs text-stone-600">
                <span className="text-forest">Free forever:</span> ATS score + keyword
                analysis, no login required.
              </div>

              {/* Feature list */}
              <ul className="mt-6 space-y-3 border-t border-tan pt-6">
                {INCLUDED.map((f, i) => (
                  <motion.li
                    key={f}
                    initial={{ opacity: 0, x: -8 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.4, delay: i * 0.05 }}
                    className="flex items-start gap-3 text-sm text-ink-soft"
                  >
                    <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-forest/15 text-forest">
                      <Check className="h-3 w-3" />
                    </span>
                    {f}
                  </motion.li>
                ))}
              </ul>
            </div>
          </div>
        </AnimatedSection>
      </div>
    </section>
  );
}
