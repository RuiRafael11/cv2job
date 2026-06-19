"use client";

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { AnimatedSection } from "./AnimatedSection";
import { SectionBadge } from "./Brand";

const FAQS = [
  {
    q: "What's an ATS, and why should I care?",
    a: "An Applicant Tracking System is the software 99% of large employers use to parse, score, and rank incoming CVs. If your CV doesn't match the job description's keywords, structure, and semantic context closely enough, it gets filtered out before any human reviewer sees it. cv2job shows you exactly what that filter sees — and gives you the levers to flip it.",
  },
  {
    q: "Will cv2job invent experience I don't have?",
    a: "No. This is the single most important design decision in the project. The optimizer prompt has hard rules: never invent employers, dates, degrees, certifications, or tools that aren't supported by your original CV. Missing keywords are integrated only when the source material actually supports them — for example, by surfacing a project where you used a tool but didn't list it.",
  },
  {
    q: "What file formats can I upload?",
    a: "PDF, DOCX, TXT, and Markdown — for both the CV and the job description. You can also paste the job description text directly into the app instead of uploading a file. The parser handles Portuguese and English content equally well, including accented characters.",
  },
  {
    q: "How is the ATS score computed?",
    a: "The score is deterministic and auditable. The system tokenizes your CV and the job description (stripping bilingual EN + PT stopwords), computes TF-IDF vectors for both, and measures cosine similarity. The result is split into four weighted dimensions — Requirements (40pts), Experience (30pts), Terms (20pts), and Education (10pts). No black-box AI in the score itself — the AI layer only writes the diagnostic and action plan.",
  },
  {
    q: "What's the difference between the free preview and paid optimization?",
    a: "The free preview gives you the full ATS score, sub-scores, keyword present/missing lists, and the cosine similarity caption. No login required. The paid optimization (1 credit) triggers the AI rewrite — Gemini produces a clean Markdown version of your CV with missing keywords integrated truthfully, which you can then export as a Harvard-format PDF or .md file.",
  },
  {
    q: "Why €9 and not a monthly subscription?",
    a: "Job hunting is episodic. You don't need a recurring bill for the 8 months you're not applying anywhere. The credit-pack model means you pay once, get 10 optimizations, and use them whenever — they don't expire. The pricing also reflects the actual compute cost: paid user requests run on Gemma 2 9B via OpenRouter, which keeps the per-credit margin sustainable.",
  },
  {
    q: "What's the Harvard format and why does it matter?",
    a: "Harvard-format résumés lead with EDUCATION, then EXPERIENCE, then SKILLS, then PROJECTS — an academic-style structure that's common in European and academic job markets. The PDF is rendered with the DejaVuSerif typeface and full Unicode sanitization, so it handles Portuguese, Polish, en-dashes, and smart quotes cleanly. The structure also reads well to ATS parsers because sections are clearly delimited.",
  },
  {
    q: "Is my data secure?",
    a: "Session tokens are stored only as SHA-256 hashes — never plaintext. The Stripe checkout flow exchanges the Stripe session ID for a paid session token via a server-side endpoint, so your payment details never touch the cv2job database. Email is the only identifier; there are no passwords in the system.",
  },
];

export function FAQ() {
  return (
    <section id="faq" className="relative py-24 lg:py-32">
      <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <AnimatedSection direction="up" className="flex justify-center">
            <SectionBadge>FAQ</SectionBadge>
          </AnimatedSection>
          <AnimatedSection direction="up" delay={0.1}>
            <h2 className="mt-6 font-display text-4xl font-bold leading-tight tracking-tight text-ink sm:text-5xl">
              Questions, answered.
            </h2>
          </AnimatedSection>
        </div>

        <AnimatedSection direction="up" delay={0.2} className="mt-12">
          <Accordion
            type="single"
            collapsible
            className="space-y-3"
            defaultValue="item-0"
          >
            {FAQS.map((f, i) => (
              <AccordionItem
                key={i}
                value={`item-${i}`}
                className="overflow-hidden rounded-lg border border-tan bg-paper px-5 transition-colors data-[state=open]:border-oxblood/40 data-[state=open]:bg-tan-soft/40"
              >
                <AccordionTrigger className="py-5 text-left font-display text-lg font-medium text-ink hover:no-underline">
                  {f.q}
                </AccordionTrigger>
                <AccordionContent className="pb-5 text-sm leading-relaxed text-stone-600">
                  {f.a}
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </AnimatedSection>
      </div>
    </section>
  );
}
