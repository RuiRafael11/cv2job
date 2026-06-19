"use client";

import Link from "next/link";
import { ArrowLeft, RotateCcw } from "lucide-react";
import { ProgressSteps } from "./ProgressSteps";

type WizardShellProps = {
  currentStep: number;
  children: React.ReactNode;
  onReset: () => void;
};

export function WizardShell({ currentStep, children, onReset }: WizardShellProps) {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <header className="border-b border-tan bg-paper/75 backdrop-blur">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <Link
            href="/"
            className="inline-flex items-center gap-2 rounded-lg px-2 py-2 text-sm text-stone-600 transition-colors hover:bg-tan-soft hover:text-ink"
          >
            <ArrowLeft className="h-4 w-4" />
            Landing
          </Link>
          <div className="font-display text-2xl font-semibold text-ink">cv2job</div>
          <button
            type="button"
            onClick={onReset}
            className="inline-flex h-10 w-10 items-center justify-center rounded-lg border border-tan bg-paper text-stone-600 transition-colors hover:border-oxblood hover:text-oxblood"
            aria-label="Reiniciar"
          >
            <RotateCcw className="h-4 w-4" />
          </button>
        </div>
        <ProgressSteps currentStep={currentStep} />
      </header>
      <main className="mx-auto max-w-6xl px-4 py-10 sm:px-6 lg:px-8">{children}</main>
    </div>
  );
}
