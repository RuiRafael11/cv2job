"use client";

import { useRef, useState } from "react";
import { ArrowLeft, ArrowRight, FileText, Upload } from "lucide-react";
import { extractTextFromFile } from "@/lib/fileText";
import type { WizardData } from "./types";

type Step2UploadProps = {
  data: WizardData;
  onChange: (patch: Partial<WizardData>) => void;
  onBack: () => void;
  onNext: () => void;
};

const ACCEPTED_EXTENSIONS = [".pdf", ".docx", ".txt", ".md"];

export function Step2Upload({ data, onChange, onBack, onNext }: Step2UploadProps) {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [isReading, setIsReading] = useState(false);
  const [error, setError] = useState("");

  async function handleFile(file: File | undefined) {
    if (!file) {
      return;
    }

    const lower = file.name.toLowerCase();
    const isSupported = ACCEPTED_EXTENSIONS.some((extension) => lower.endsWith(extension));
    if (!isSupported) {
      setError("Formato nao suportado. Usa PDF, DOCX, TXT ou MD.");
      return;
    }

    setIsReading(true);
    setError("");
    try {
      const text = await extractTextFromFile(file);
      onChange({ cvFileName: file.name, cvText: text });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Nao consegui ler o ficheiro.");
    } finally {
      setIsReading(false);
    }
  }

  return (
    <section className="grid gap-8 lg:grid-cols-[0.9fr_1.1fr]">
      <div>
        <div className="section-badge">Passo 2</div>
        <h1 className="font-display text-4xl font-bold leading-tight text-ink sm:text-5xl">
          Carrega o teu CV
        </h1>
        <p className="mt-5 max-w-xl text-base leading-relaxed text-stone-600">
          A extracao acontece no browser. O backend recebe apenas texto, mantendo a API
          atual intacta.
        </p>
      </div>

      <div className="rounded-xl border border-tan bg-paper p-5 paper-shadow sm:p-6">
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.docx,.txt,.md"
          className="hidden"
          onChange={(event) => handleFile(event.target.files?.[0])}
        />
        <button
          type="button"
          onClick={() => inputRef.current?.click()}
          onDragOver={(event) => event.preventDefault()}
          onDrop={(event) => {
            event.preventDefault();
            handleFile(event.dataTransfer.files[0]);
          }}
          className="flex min-h-72 w-full flex-col items-center justify-center rounded-xl border border-dashed border-tan-dark bg-bone p-8 text-center transition-colors hover:border-oxblood hover:bg-tan-soft/50"
        >
          <span className="flex h-14 w-14 items-center justify-center rounded-lg border border-oxblood/30 bg-oxblood/5 text-oxblood">
            <Upload className="h-6 w-6" />
          </span>
          <span className="mt-5 font-display text-2xl font-semibold text-ink">
            Arrasta o CV ou seleciona ficheiro
          </span>
          <span className="mt-2 text-sm text-stone-600">PDF, DOCX, TXT ou MD</span>
        </button>

        {data.cvFileName && (
          <div className="mt-4 flex items-center gap-3 rounded-lg border border-forest/30 bg-forest/5 p-3 text-sm text-forest">
            <FileText className="h-4 w-4" />
            <span className="truncate">{data.cvFileName}</span>
          </div>
        )}

        {isReading && <p className="mt-4 text-sm text-stone-600">A extrair texto...</p>}
        {error && <p className="mt-4 text-sm text-brick">{error}</p>}

        <div className="mt-6 grid gap-3 sm:grid-cols-2">
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
            disabled={!data.cvText || isReading}
            onClick={onNext}
            className="inline-flex h-12 items-center justify-center gap-2 rounded-lg bg-oxblood px-5 text-sm font-medium text-paper transition-colors hover:bg-oxblood-deep disabled:cursor-not-allowed disabled:bg-tan-dark"
          >
            Analisar score
            <ArrowRight className="h-4 w-4" />
          </button>
        </div>
      </div>
    </section>
  );
}
