"use client";

import { Wordmark } from "./Brand";
import { Github } from "lucide-react";

const COLS = [
  {
    title: "Product",
    links: [
      { label: "Features", href: "#features" },
      { label: "How it works", href: "#how" },
      { label: "ATS demo", href: "#demo" },
      { label: "Pricing", href: "#pricing" },
      { label: "FAQ", href: "#faq" },
    ],
  },
  {
    title: "Tech",
    links: [
      { label: "GitHub repo", href: "https://github.com/RuiRafael11/cv2job" },
      { label: "Streamlit frontend", href: "https://github.com/RuiRafael11/cv2job" },
      { label: "FastAPI backend", href: "https://github.com/RuiRafael11/cv2job" },
      { label: "Gemini 2.5 Flash", href: "https://github.com/RuiRafael11/cv2job" },
      { label: "Stripe Checkout", href: "https://github.com/RuiRafael11/cv2job" },
    ],
  },
  {
    title: "Legal",
    links: [
      { label: "Privacy", href: "#" },
      { label: "Terms", href: "#" },
      { label: "Security", href: "#" },
    ],
  },
];

export function Footer() {
  return (
    <footer className="relative border-t border-tan bg-tan-soft/40">
      <div className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 gap-10 md:grid-cols-[1.4fr_1fr_1fr_1fr]">
          {/* Brand + blurb */}
          <div>
            <Wordmark />
            <p className="mt-4 max-w-xs text-sm leading-relaxed text-stone-600">
              An open-source AI résumé optimizer that scores your CV like an ATS would — then
              rewrites it into a Harvard-format PDF that gets past the bots.
            </p>
            <a
              href="https://github.com/RuiRafael11/cv2job"
              target="_blank"
              rel="noreferrer"
              className="mt-5 inline-flex h-9 items-center gap-2 rounded-lg border border-tan-dark bg-paper px-3 text-sm text-stone-600 transition-colors hover:border-oxblood hover:text-oxblood"
            >
              <Github className="h-4 w-4" />
              Star the repo
            </a>
          </div>

          {/* Link columns */}
          {COLS.map((col) => (
            <div key={col.title}>
              <h4 className="font-mono-badge text-[11px] uppercase tracking-[0.18em] text-stone-500">
                {col.title}
              </h4>
              <ul className="mt-4 space-y-2.5">
                {col.links.map((l) => (
                  <li key={l.label}>
                    <a
                      href={l.href}
                      className="text-sm text-stone-600 transition-colors hover:text-oxblood"
                    >
                      {l.label}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom bar */}
        <div className="mt-12 flex flex-col items-start justify-between gap-4 border-t border-tan pt-6 sm:flex-row sm:items-center">
          <p className="text-xs text-stone-500">
            © {new Date().getFullYear()} cv2job — built by{" "}
            <a
              href="https://github.com/RuiRafael11"
              target="_blank"
              rel="noreferrer"
              className="text-ink underline-offset-2 hover:text-oxblood hover:underline"
            >
              RuiRafael11
            </a>
            . Open source under the MIT license.
          </p>
          <p className="font-mono-badge text-[11px] tracking-[0.15em] text-stone-500 uppercase">
            ATS AI Resume Optimizer
          </p>
        </div>
      </div>
    </footer>
  );
}
