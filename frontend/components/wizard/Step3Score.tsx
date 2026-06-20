"use client";

import { AlertCircle, ArrowLeft, ArrowRight, Loader2, Target, UsersRound } from "lucide-react";
import type { AgentReviewResponse, AtsScoreResponse } from "@/lib/api";

type Step3ScoreProps = {
  ats: AtsScoreResponse | null;
  agentReview: AgentReviewResponse | null;
  agentReviewError: string;
  accessToken: string;
  loading: boolean;
  error: string;
  onAccessTokenChange: (value: string) => void;
  onAnalyze: () => void;
  onBack: () => void;
  onNext: () => void;
};

const SECTION_LABELS: Record<string, string> = {
  requirements: "Requisitos",
  experience: "Experiencia",
  terms: "Termos",
  education: "Formacao",
};

export function Step3Score({
  ats,
  agentReview,
  agentReviewError,
  accessToken,
  loading,
  error,
  onAccessTokenChange,
  onAnalyze,
  onBack,
  onNext,
}: Step3ScoreProps) {
  return (
    <section className="grid gap-8 lg:grid-cols-[0.95fr_1.05fr]">
      <div className="space-y-5 lg:sticky lg:top-6 lg:self-start">
        <div className="section-badge">Passo 3</div>
        <h1 className="font-display text-4xl font-bold leading-tight text-ink sm:text-5xl">
          Score e diagnostico
        </h1>
        <p className="max-w-xl text-base leading-relaxed text-stone-600">
          O backend real usa <span className="font-mono-badge text-[12px]">POST /api/ats-score</span>.
          Depois chama <span className="font-mono-badge text-[12px]">POST /api/agent-review</span>
          {" "}para rever o CV com quatro agentes.
        </p>

        {!ats ? (
          <div className="rounded-xl border border-tan bg-paper p-5 paper-shadow">
            <label className="block font-mono-badge text-[11px] tracking-[0.18em] text-stone-500 uppercase">
              Owner token opcional
            </label>
            <input
              type="password"
              value={accessToken}
              onChange={(event) => onAccessTokenChange(event.target.value)}
              className="mt-3 h-11 w-full rounded-lg border border-tan-dark bg-bone px-3 text-sm outline-none transition-colors placeholder:text-stone-500 focus:border-oxblood"
              placeholder="Usa apenas se estiveres em modo owner"
            />
            <button
              type="button"
              disabled={loading}
              onClick={onAnalyze}
              className="mt-4 inline-flex h-12 w-full items-center justify-center gap-2 rounded-lg bg-oxblood px-5 text-sm font-medium text-paper transition-colors hover:bg-oxblood-deep disabled:cursor-wait disabled:bg-tan-dark"
            >
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Target className="h-4 w-4" />}
              {loading ? "A analisar..." : "Gerar ATS score"}
            </button>
          </div>
        ) : (
          <>
            <div className="rounded-xl border border-tan bg-paper p-5 paper-shadow">
              <div className="flex items-end justify-between gap-4">
                <div>
                  <div className="font-display text-7xl font-bold leading-none text-oxblood">
                    {Math.round(ats.overall_score)}
                  </div>
                  <div className="mt-2 font-mono-badge text-[11px] tracking-[0.18em] text-stone-500">
                    ATS SCORE
                  </div>
                </div>
                {typeof ats.cosine_similarity === "number" && (
                  <div className="rounded-lg border border-tan bg-bone px-3 py-2 text-right">
                    <div className="font-mono-badge text-[10px] tracking-[0.14em] text-stone-500">
                      TF-IDF
                    </div>
                    <div className="font-display text-2xl font-semibold text-ink">
                      {ats.cosine_similarity}
                    </div>
                  </div>
                )}
              </div>
              <p className="mt-4 line-clamp-3 text-sm leading-relaxed text-stone-600">
                {ats.diagnostic || "Diagnostico indisponivel para esta resposta."}
              </p>
            </div>

            <div className="grid grid-cols-2 gap-3">
              {Object.entries(ats.section_scores).map(([key, value]) => (
                <MetricCard key={key} label={SECTION_LABELS[key] || key} value={value} />
              ))}
            </div>

            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-1 xl:grid-cols-2">
              <KeywordGroup title="Encontradas" items={ats.keywords_present} variant="present" />
              <KeywordGroup title="Em falta" items={ats.keywords_missing} variant="missing" />
            </div>

            {!!ats.next_steps?.length && (
              <div className="rounded-xl border border-tan bg-paper p-5 paper-shadow">
                <div className="section-badge">Plano de acao</div>
                <div className="mt-4 space-y-3">
                  {ats.next_steps.slice(0, 3).map((step, index) => (
                    <div key={`${step.title}-${index}`} className="rounded-lg border border-tan bg-bone p-3">
                      <div className="font-display text-base font-semibold text-ink">
                        {step.title || `Prioridade ${index + 1}`}
                      </div>
                      <ul className="mt-2 list-disc space-y-1 pl-5 text-xs leading-relaxed text-stone-600">
                        {(step.bullets || []).slice(0, 2).map((bullet) => (
                          <li key={bullet}>{bullet}</li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        )}

        {error && (
          <div className="flex gap-3 rounded-lg border border-brick/30 bg-brick/5 p-4 text-sm text-brick">
            <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <div className="grid gap-3 sm:grid-cols-2">
          <button
            type="button"
            onClick={onBack}
            className="inline-flex h-12 items-center justify-center gap-2 rounded-lg border border-tan-dark bg-paper px-5 text-sm font-medium text-ink transition-colors hover:border-oxblood hover:text-oxblood"
          >
            <ArrowLeft className="h-4 w-4" />
            Voltar
          </button>
          <button
            type="button"
            disabled={!ats}
            onClick={onNext}
            className="inline-flex h-12 items-center justify-center gap-2 rounded-lg bg-oxblood px-5 text-sm font-medium text-paper transition-colors hover:bg-oxblood-deep disabled:cursor-not-allowed disabled:bg-tan-dark"
          >
            Ver resultado
            <ArrowRight className="h-4 w-4" />
          </button>
        </div>
      </div>

      <div className="space-y-5">
        {!ats && (
          <div className="rounded-xl border border-tan bg-paper p-6 paper-shadow">
            <div className="section-badge">Diagnostico IA</div>
            <h2 className="font-display text-2xl font-semibold text-ink">
              Pronto para analisar
            </h2>
            <p className="mt-3 max-w-2xl text-sm leading-relaxed text-stone-600">
              O resultado vai dividir score, metricas e keywords na coluna esquerda,
              deixando aqui o diagnostico completo e a revisao dos agentes.
            </p>
          </div>
        )}

        {ats && (
          <>
            <div className="rounded-xl border border-tan bg-paper p-5 paper-shadow sm:p-6">
              <div className="section-badge">Diagnostico IA</div>
              <h2 className="mt-2 font-display text-2xl font-semibold text-ink">
                Leitura principal
              </h2>
              <p className="mt-4 max-w-3xl text-sm leading-7 text-stone-600">
                {ats.diagnostic || "Diagnostico indisponivel para esta resposta."}
              </p>
            </div>

            {agentReviewError && (
              <div className="flex gap-3 rounded-xl border border-ochre/30 bg-ochre/10 p-4 text-sm text-stone-700">
                <AlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-ochre" />
                <span>
                  Agent Review indisponivel: {agentReviewError}. Podes continuar apenas com ATS.
                </span>
              </div>
            )}

            {agentReview && (
              <div className="rounded-xl border border-tan bg-paper p-5 paper-shadow sm:p-6">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <div className="section-badge">AI Agent Review</div>
                    <h2 className="mt-2 font-display text-2xl font-semibold text-ink">
                      Painel dos 4 agentes
                    </h2>
                  </div>
                  <span className="rounded-md border border-oxblood/30 bg-oxblood/5 px-2 py-1 font-mono-badge text-[10px] uppercase text-oxblood">
                    {agentReview.source}
                  </span>
                </div>

                <div className="mt-5 grid gap-3 xl:grid-cols-2">
                  {agentReview.reviews.map((review) => (
                    <div key={review.agent} className="rounded-lg border border-tan bg-bone p-4">
                      <div className="flex items-center justify-between gap-3">
                        <div className="flex items-center gap-2">
                          <UsersRound className="h-4 w-4 text-oxblood" />
                          <h3 className="font-display text-lg font-semibold text-ink">
                            {review.agent}
                          </h3>
                        </div>
                        <span className="font-display text-2xl font-semibold text-oxblood">
                          {review.score}
                        </span>
                      </div>
                      <p className="mt-2 line-clamp-3 text-sm leading-relaxed text-stone-600">
                        {review.verdict}
                      </p>
                      <AgentList title="Findings" items={review.findings} />
                      <AgentList title="Recomendacoes" items={review.recommendations} />
                    </div>
                  ))}
                </div>
              </div>
            )}

            {agentReview && (
              <div className="grid gap-4 xl:grid-cols-2">
                <div className="rounded-xl border border-tan bg-paper p-5 paper-shadow xl:col-span-2">
                  <div className="font-mono-badge text-[10px] tracking-[0.16em] text-stone-500 uppercase">
                    Consenso
                  </div>
                  <p className="mt-3 text-sm leading-7 text-stone-600">
                    {agentReview.consensus}
                  </p>
                </div>
                <AgentListBox title="Para o otimizador" items={agentReview.optimizer_recommendations} />
                <AgentListBox title="Acoes prioritarias" items={agentReview.priority_actions} />
                <AgentListBox title="Truthfulness" items={agentReview.truthfulness_warnings} />
              </div>
            )}
          </>
        )}
      </div>
    </section>
  );
}

function MetricCard({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-lg border border-tan bg-paper p-4 paper-shadow">
      <div className="font-mono-badge text-[10px] tracking-[0.16em] text-stone-500">
        {label}
      </div>
      <div className="mt-2 font-display text-3xl font-semibold text-ink">{value}</div>
    </div>
  );
}

function AgentList({ title, items }: { title: string; items: string[] }) {
  if (!items.length) {
    return null;
  }

  return (
    <div className="mt-3">
      <div className="font-mono-badge text-[10px] tracking-[0.14em] text-stone-500 uppercase">
        {title}
      </div>
      <ul className="mt-1 list-disc space-y-1 pl-5 text-xs leading-relaxed text-stone-600">
        {items.slice(0, 3).map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </div>
  );
}

function AgentListBox({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="rounded-lg border border-tan bg-paper p-4">
      <div className="font-mono-badge text-[10px] tracking-[0.16em] text-stone-500 uppercase">
        {title}
      </div>
      <ul className="mt-2 list-disc space-y-1 pl-5 text-sm leading-relaxed text-stone-600">
        {items.slice(0, 4).map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </div>
  );
}

function KeywordGroup({
  title,
  items,
  variant,
}: {
  title: string;
  items: string[];
  variant: "present" | "missing";
}) {
  const colorClass =
    variant === "present"
      ? "border-forest/30 bg-forest/10 text-forest"
      : "border-brick/30 bg-brick/10 text-brick";

  return (
    <div className="rounded-lg border border-tan bg-bone p-4">
      <div className="font-mono-badge text-[10px] tracking-[0.16em] text-stone-500 uppercase">
        {title}
      </div>
      <div className="mt-3 flex flex-wrap gap-2">
        {items.slice(0, 12).map((item) => (
          <span key={item} className={`rounded-md border px-2 py-1 text-xs ${colorClass}`}>
            {item}
          </span>
        ))}
        {!items.length && <span className="text-sm text-stone-500">Nenhuma.</span>}
      </div>
    </div>
  );
}
