"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Menu, X, Github } from "lucide-react";
import { Wordmark } from "./Brand";

const LINKS = [
  { href: "#features", label: "Features" },
  { href: "#how", label: "How it works" },
  { href: "#demo", label: "ATS demo" },
  { href: "#pricing", label: "Pricing" },
  { href: "#faq", label: "FAQ" },
];

export function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 24);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <motion.header
      initial={{ y: -80, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
      className="fixed inset-x-0 top-0 z-50"
    >
      <div
        className={`mx-auto flex max-w-7xl items-center justify-between px-4 transition-all duration-300 sm:px-6 lg:px-8 ${
          scrolled
            ? "mt-2 h-14 rounded-xl border border-tan-dark bg-paper/85 backdrop-blur-xl lg:mt-3 lg:h-16 paper-shadow"
            : "mt-0 h-16 border-b border-transparent bg-transparent lg:h-20"
        }`}
      >
        <Wordmark />

        <nav className="hidden items-center gap-1 md:flex">
          {LINKS.map((l) => (
            <a
              key={l.href}
              href={l.href}
              className="rounded-lg px-3 py-2 text-sm text-stone-600 transition-colors hover:text-oxblood"
            >
              {l.label}
            </a>
          ))}
        </nav>

        <div className="hidden items-center gap-2 md:flex">
          <a
            href="https://github.com/RuiRafael11/cv2job"
            target="_blank"
            rel="noreferrer"
            className="flex h-9 items-center gap-2 rounded-lg px-3 text-sm text-stone-600 transition-colors hover:bg-tan-soft hover:text-ink"
          >
            <Github className="h-4 w-4" />
            Star
          </a>
          <a
            href="#cta"
            className="flex h-9 items-center rounded-lg bg-oxblood px-4 text-sm font-medium text-paper transition-colors hover:bg-oxblood-deep"
          >
            Optimize my CV
          </a>
        </div>

        <button
          onClick={() => setOpen((o) => !o)}
          className="flex h-10 w-10 items-center justify-center rounded-lg text-ink hover:bg-tan-soft md:hidden"
          aria-label="Menu"
        >
          {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </div>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="mx-4 mt-2 overflow-hidden rounded-xl border border-tan-dark bg-paper/95 backdrop-blur-xl paper-shadow md:hidden"
          >
            <nav className="flex flex-col p-3">
              {LINKS.map((l) => (
                <a
                  key={l.href}
                  href={l.href}
                  onClick={() => setOpen(false)}
                  className="rounded-lg px-3 py-3 text-sm text-ink hover:bg-tan-soft"
                >
                  {l.label}
                </a>
              ))}
              <a
                href="#cta"
                onClick={() => setOpen(false)}
                className="mt-2 rounded-lg bg-oxblood px-3 py-3 text-center text-sm font-medium text-paper"
              >
                Optimize my CV
              </a>
            </nav>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.header>
  );
}
