"use client";

import { ArrowRight, KeyRound } from "lucide-react";
import type { WizardData } from "./types";

type Step1ContextProps = {
  data: WizardData;
  onChange: (patch: Partial<WizardData>) => void;
  onNext: () => void;
};

const RESPONSE_OPTIONS = ["Quase nunca", "As vezes", "Com frequencia"];
const LANGUAGE_OPTIONS = [
  { value: "en", label: "English" },
  { value: "pt", label: "Português" },
] as const;

export function Step1Context({ data, onChange, onNext }: Step1ContextProps) {
  const canContinue = data.responseRate && data.jobDescription.trim().length >= 40;

  return (
    <section className="grid gap-8 lg:grid-cols-[0.9fr_1.1fr]">
      <div>
        <div className="section-badge">Passo 1</div>
        <h1 className="font-display text-4xl font-bold leading-tight text-ink sm:text-5xl">
          Contexto da candidatura
        </h1>
        <p className="mt-5 max-w-xl text-base leading-relaxed text-stone-600">
          O score fica mais util quando compara o teu CV com uma vaga real e com o teu
          momento atual de procura.
        </p>
      </div>

      <div className="rounded-xl border border-tan bg-paper p-5 paper-shadow sm:p-6">
        <label className="font-mono-badge text-[11px] tracking-[0.18em] text-stone-500 uppercase">
          Taxa de resposta atual
        </label>
        <div className="mt-3 grid gap-2 sm:grid-cols-3">
          {RESPONSE_OPTIONS.map((option) => (
            <button
              key={option}
              type="button"
              onClick={() => onChange({ responseRate: option })}
              className={`min-h-12 rounded-lg border px-3 text-sm font-medium transition-colors ${
                data.responseRate === option
                  ? "border-oxblood bg-oxblood text-paper"
                  : "border-tan-dark bg-bone text-ink hover:border-oxblood hover:text-oxblood"
              }`}
            >
              {option}
            </button>
          ))}
        </div>

        <label className="mt-6 block font-mono-badge text-[11px] tracking-[0.18em] text-stone-500 uppercase">
          Job description
        </label>
        <textarea
          value={data.jobDescription}
          onChange={(event) => onChange({ jobDescription: event.target.value })}
          className="mt-3 min-h-56 w-full resize-y rounded-lg border border-tan-dark bg-bone p-4 text-sm leading-relaxed text-ink outline-none transition-colors placeholder:text-stone-500 focus:border-oxblood"
          placeholder="Cola aqui responsabilidades, requisitos, stack e qualquer detalhe relevante da vaga."
        />

        <label className="mt-5 block font-mono-badge text-[11px] tracking-[0.18em] text-stone-500 uppercase">
          Cargo-alvo ou area pretendida
        </label>
        <input
          value={data.targetRole}
          onChange={(event) => onChange({ targetRole: event.target.value })}
          className="mt-3 h-12 w-full rounded-lg border border-tan-dark bg-bone px-4 text-sm text-ink outline-none transition-colors placeholder:text-stone-500 focus:border-oxblood"
          placeholder="Ex.: Backend Developer, Data Analyst, Product Manager"
        />

        <label className="mt-5 block font-mono-badge text-[11px] tracking-[0.18em] text-stone-500 uppercase">
          CV language
        </label>
        <div className="mt-3 grid gap-2 sm:grid-cols-2">
          {LANGUAGE_OPTIONS.map((option) => (
            <button
              key={option.value}
              type="button"
              onClick={() => onChange({ outputLanguage: option.value })}
              className={`min-h-12 rounded-lg border px-3 text-sm font-medium transition-colors ${
                data.outputLanguage === option.value
                  ? "border-oxblood bg-oxblood text-paper"
                  : "border-tan-dark bg-bone text-ink hover:border-oxblood hover:text-oxblood"
              }`}
            >
              {option.label}
            </button>
          ))}
        </div>

        <div className="mt-5 rounded-lg border border-tan bg-bone p-4">
          <div className="flex items-center gap-2 text-sm font-medium text-ink">
            <KeyRound className="h-4 w-4 text-oxblood" />
            Acesso global
          </div>
          <p className="mt-2 text-xs leading-relaxed text-stone-600">
            Cola o owner token aqui antes da analise para usar Agent Review, otimizacao e PDF.
            Sessoes pagas via Stripe tambem usam este mesmo mecanismo.
          </p>
          <input
            type="password"
            value={data.accessTokenType === "owner" ? data.accessToken : ""}
            onChange={(event) => onChange({ accessToken: event.target.value, accessTokenType: "owner" })}
            className="mt-3 h-12 w-full rounded-lg border border-tan-dark bg-paper px-4 text-sm text-ink outline-none transition-colors placeholder:text-stone-500 focus:border-oxblood"
            placeholder="Owner token opcional"
          />
          {data.accessTokenType === "paid" && data.accessToken && (
            <p className="mt-3 rounded-md border border-forest/30 bg-forest/5 p-2 text-xs text-forest">
              Sessao paga ativa. Podes escrever um owner token acima para substituir temporariamente.
            </p>
          )}
        </div>

        <button
          type="button"
          disabled={!canContinue}
          onClick={onNext}
          className="mt-6 inline-flex h-12 w-full items-center justify-center gap-2 rounded-lg bg-oxblood px-5 text-sm font-medium text-paper transition-colors hover:bg-oxblood-deep disabled:cursor-not-allowed disabled:bg-tan-dark"
        >
          Continuar
          <ArrowRight className="h-4 w-4" />
        </button>
      </div>
    </section>
  );
}
