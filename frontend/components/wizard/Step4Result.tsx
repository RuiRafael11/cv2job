"use client";

import {
  AlertCircle,
  CreditCard,
  Download,
  FileDown,
  KeyRound,
  Loader2,
  Sparkles,
} from "lucide-react";
import { base64ToBlob } from "@/lib/api";
import type { WizardData } from "./types";

type Step4ResultProps = {
  data: WizardData;
  optimizing: boolean;
  pdfLoading: boolean;
  checkoutLoading: boolean;
  sessionMessage: string;
  error: string;
  onChange: (patch: Partial<WizardData>) => void;
  onOptimize: () => void;
  onCreateCheckout: () => void;
  onDownloadPdf: () => Promise<string | null>;
};

export function Step4Result({
  data,
  optimizing,
  pdfLoading,
  checkoutLoading,
  sessionMessage,
  error,
  onChange,
  onOptimize,
  onCreateCheckout,
  onDownloadPdf,
}: Step4ResultProps) {
  const hasAuth = Boolean(data.accessToken || data.paidSessionToken);
  const canCheckout = data.paidEmail.includes("@");
  const agentReview = data.agentReview;
  const hasAgentConsensus = Boolean(agentReview);

  function downloadMarkdown() {
    const blob = new Blob([data.optimizedMarkdown], { type: "text/markdown" });
    downloadBlob(blob, "cv2job-optimized-cv.md");
  }

  async function downloadPdf() {
    const base64 = await onDownloadPdf();
    if (base64) {
      downloadBlob(base64ToBlob(base64), "cv2job-optimized-cv.pdf");
    }
  }

  return (
    <section className="grid gap-8 lg:grid-cols-[0.9fr_1.1fr]">
      <div className="space-y-5 lg:sticky lg:top-6 lg:self-start">
        <div className="section-badge">Passo 4</div>
        <h1 className="font-display text-4xl font-bold leading-tight text-ink sm:text-5xl">
          Resultado e downloads
        </h1>
        <p className="max-w-xl text-base leading-relaxed text-stone-600">
          A otimizacao usa <span className="font-mono-badge text-[12px]">POST /api/optimize</span>
          {" "}e o PDF usa <span className="font-mono-badge text-[12px]">POST /api/generate-cv</span>.
        </p>

        {hasAgentConsensus && (
          <div className="rounded-xl border border-forest/30 bg-forest/5 p-4 text-sm leading-relaxed text-stone-700">
            <div className="font-mono-badge text-[10px] tracking-[0.16em] text-forest uppercase">
              Agent consensus ligado
            </div>
            <p className="mt-2">{agentReview?.consensus}</p>
          </div>
        )}

        <div className="rounded-xl border border-tan bg-paper p-5 paper-shadow">
          <div className="flex items-center gap-2 text-sm font-medium text-ink">
            <KeyRound className="h-4 w-4 text-oxblood" />
            Acesso
          </div>
          <input
            type="password"
            value={data.accessTokenType === "owner" ? data.accessToken : ""}
            onChange={(event) => onChange({ accessToken: event.target.value, accessTokenType: "owner" })}
            className="mt-3 h-11 w-full rounded-lg border border-tan-dark bg-bone px-3 text-sm outline-none transition-colors placeholder:text-stone-500 focus:border-oxblood"
            placeholder="Owner token opcional"
          />
          {data.paidSessionToken && (
            <p className="mt-3 rounded-lg border border-forest/30 bg-forest/5 p-3 text-sm text-forest">
              Sessao paga ativa. Creditos: {data.creditsRemaining ?? "N/A"}
            </p>
          )}
          {sessionMessage && <p className="mt-3 text-sm text-forest">{sessionMessage}</p>}
        </div>

        <div className="rounded-xl border border-tan bg-paper p-5 paper-shadow">
          <div className="section-badge">Resumo</div>
          <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-1 xl:grid-cols-2">
            <SummaryItem
              label="ATS Score"
              value={data.ats ? String(Math.round(data.ats.overall_score)) : "Pendente"}
            />
            <SummaryItem
              label="Agent Review"
              value={hasAgentConsensus ? "Ligado" : "Sem consenso"}
            />
            <SummaryItem
              label="CV otimizado"
              value={data.optimizedMarkdown ? "Gerado" : "Por gerar"}
            />
            <SummaryItem
              label="Downloads"
              value={data.optimizedMarkdown ? "MD e PDF" : "Depois da geracao"}
            />
          </div>
          {!data.optimizedMarkdown && (
            <button
              type="button"
              disabled={!hasAuth || optimizing}
              onClick={onOptimize}
              className="mt-4 inline-flex h-12 w-full items-center justify-center gap-2 rounded-lg bg-oxblood px-5 text-sm font-medium text-paper transition-colors hover:bg-oxblood-deep disabled:cursor-not-allowed disabled:bg-tan-dark"
            >
              {optimizing ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
              {optimizing ? "A otimizar..." : "Gerar CV otimizado"}
            </button>
          )}
        </div>

        {!hasAuth && (
          <div className="rounded-xl border border-tan bg-paper p-5 paper-shadow">
            <div className="flex items-center gap-2 text-sm font-medium text-ink">
              <CreditCard className="h-4 w-4 text-oxblood" />
              Comprar creditos
            </div>
            <input
              type="email"
              value={data.paidEmail}
              onChange={(event) => onChange({ paidEmail: event.target.value })}
              className="mt-3 h-11 w-full rounded-lg border border-tan-dark bg-bone px-3 text-sm outline-none transition-colors placeholder:text-stone-500 focus:border-oxblood"
              placeholder="teu@email.com"
            />
            <button
              type="button"
              disabled={!canCheckout || checkoutLoading}
              onClick={onCreateCheckout}
              className="mt-3 inline-flex h-11 w-full items-center justify-center gap-2 rounded-lg bg-oxblood px-4 text-sm font-medium text-paper transition-colors hover:bg-oxblood-deep disabled:cursor-not-allowed disabled:bg-tan-dark"
            >
              {checkoutLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <CreditCard className="h-4 w-4" />}
              Abrir Stripe Checkout
            </button>
          </div>
        )}
      </div>

      <div className="rounded-xl border border-tan bg-paper p-5 paper-shadow sm:p-6">
        {error && (
          <div className="mb-4 flex gap-3 rounded-lg border border-brick/30 bg-brick/5 p-4 text-sm text-brick">
            <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {!data.optimizedMarkdown ? (
          <div className="flex min-h-80 flex-col items-center justify-center rounded-xl border border-dashed border-tan-dark bg-bone p-8 text-center">
            <Sparkles className="h-8 w-8 text-oxblood" />
            <h2 className="mt-5 font-display text-3xl font-semibold text-ink">CV otimizado</h2>
            <p className="mt-3 max-w-md text-sm leading-relaxed text-stone-600">
              Precisas de owner token ou sessao paga para consumir a otimizacao completa.
            </p>
          </div>
        ) : (
          <div>
            <div className="flex flex-col gap-3 border-b border-tan pb-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <div className="section-badge">CV finalizado</div>
                <h2 className="font-display text-3xl font-semibold text-ink">CV otimizado</h2>
              </div>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={downloadMarkdown}
                  className="inline-flex h-10 items-center justify-center gap-2 rounded-lg border border-tan-dark bg-paper px-3 text-sm text-ink transition-colors hover:border-oxblood hover:text-oxblood"
                >
                  <Download className="h-4 w-4" />
                  Download MD
                </button>
                <button
                  type="button"
                  disabled={pdfLoading}
                  onClick={downloadPdf}
                  className="inline-flex h-10 items-center justify-center gap-2 rounded-lg bg-oxblood px-3 text-sm font-medium text-paper transition-colors hover:bg-oxblood-deep disabled:cursor-wait disabled:bg-tan-dark"
                >
                  {pdfLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <FileDown className="h-4 w-4" />}
                  Download PDF
                </button>
              </div>
            </div>
            <MarkdownPreview markdown={data.optimizedMarkdown} />
          </div>
        )}
      </div>
    </section>
  );
}

function SummaryItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-tan bg-bone p-3">
      <div className="font-mono-badge text-[10px] tracking-[0.16em] text-stone-500 uppercase">
        {label}
      </div>
      <div className="mt-2 font-display text-xl font-semibold text-ink">{value}</div>
    </div>
  );
}

function MarkdownPreview({ markdown }: { markdown: string }) {
  const blocks = markdown
    .split(/\n{2,}/)
    .map((block) => block.trim())
    .filter(Boolean);

  return (
    <div className="mt-5 max-h-[680px] overflow-auto rounded-lg border border-tan bg-bone px-5 py-6 text-ink sm:px-7">
      <div className="mx-auto max-w-3xl space-y-5">
        {blocks.map((block, index) => (
          <MarkdownBlock key={`${block.slice(0, 24)}-${index}`} block={block} />
        ))}
      </div>
    </div>
  );
}

function MarkdownBlock({ block }: { block: string }) {
  const lines = block.split("\n").map((line) => line.trim()).filter(Boolean);
  const firstLine = lines[0] || "";
  const headingMatch = firstLine.match(/^(#{1,3})\s+(.*)$/);
  const isList = lines.every((line) => /^[-*]\s+/.test(line));

  if (headingMatch) {
    const level = headingMatch[1].length;
    const text = headingMatch[2];
    const className =
      level === 1
        ? "font-display text-3xl font-bold leading-tight text-ink"
        : level === 2
          ? "font-display text-2xl font-semibold leading-tight text-ink"
          : "font-display text-xl font-semibold leading-snug text-ink";

    return (
      <div>
        <div className={className}>{text}</div>
        {lines.slice(1).map((line) => (
          <p key={line} className="mt-3 text-sm leading-7 text-stone-700">
            {formatInline(line)}
          </p>
        ))}
      </div>
    );
  }

  if (isList) {
    return (
      <ul className="list-disc space-y-2 pl-5 text-sm leading-7 text-stone-700">
        {lines.map((line) => (
          <li key={line}>{formatInline(line.replace(/^[-*]\s+/, ""))}</li>
        ))}
      </ul>
    );
  }

  return (
    <div className="space-y-2">
      {lines.map((line) => (
        <p key={line} className="text-sm leading-7 text-stone-700">
          {formatInline(line)}
        </p>
      ))}
    </div>
  );
}

function formatInline(text: string) {
  return text.replace(/\*\*/g, "");
}

function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}
