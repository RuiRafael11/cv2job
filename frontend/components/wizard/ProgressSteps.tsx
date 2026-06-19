"use client";

import { Check } from "lucide-react";

const STEPS = ["Contexto", "Upload", "Score", "Resultado"];

type ProgressStepsProps = {
  currentStep: number;
};

export function ProgressSteps({ currentStep }: ProgressStepsProps) {
  return (
    <div className="grid grid-cols-4 border-y border-tan bg-tan-soft/45">
      {STEPS.map((label, index) => {
        const step = index + 1;
        const isDone = currentStep > step;
        const isActive = currentStep === step;

        return (
          <div
            key={label}
            className="flex min-h-16 items-center gap-3 border-r border-tan px-3 last:border-r-0 sm:px-5"
          >
            <span
              className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border font-mono-badge text-[11px] ${
                isDone
                  ? "border-forest/30 bg-forest/10 text-forest"
                  : isActive
                    ? "border-oxblood/30 bg-oxblood/10 text-oxblood"
                    : "border-tan-dark bg-paper text-stone-500"
              }`}
            >
              {isDone ? <Check className="h-4 w-4" /> : step}
            </span>
            <span className="hidden text-sm font-medium text-ink sm:inline">{label}</span>
          </div>
        );
      })}
    </div>
  );
}
