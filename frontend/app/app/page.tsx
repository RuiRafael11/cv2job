"use client";

import { useEffect, useMemo, useState } from "react";
import {
  analyzeAts,
  createCheckout,
  exchangeCheckoutSession,
  generateCvPdf,
  optimizeCv,
  reviewAgents,
  type AuthTokens,
} from "@/lib/api";
import { Step1Context } from "@/components/wizard/Step1Context";
import { Step2Upload } from "@/components/wizard/Step2Upload";
import { Step3Score } from "@/components/wizard/Step3Score";
import { Step4Result } from "@/components/wizard/Step4Result";
import { WizardShell } from "@/components/wizard/WizardShell";
import { toWizardContext, type WizardData } from "@/components/wizard/types";

const STORAGE_KEY = "cv2job_paid_session";

const INITIAL_DATA: WizardData = {
  responseRate: "",
  jobDescription: "",
  targetRole: "",
  cvFileName: "",
  cvText: "",
  ats: null,
  agentReview: null,
  agentReviewError: "",
  optimizedMarkdown: "",
  creditsRemaining: null,
  paidEmail: "",
  paidSessionToken: "",
  accessToken: "",
  accessTokenType: "owner",
  outputLanguage: "en",
};

export default function AppPage() {
  const [step, setStep] = useState(1);
  const [data, setData] = useState<WizardData>(INITIAL_DATA);
  const [atsLoading, setAtsLoading] = useState(false);
  const [optimizeLoading, setOptimizeLoading] = useState(false);
  const [pdfLoading, setPdfLoading] = useState(false);
  const [checkoutLoading, setCheckoutLoading] = useState(false);
  const [error, setError] = useState("");
  const [sessionMessage, setSessionMessage] = useState("");
  const [pdfBase64, setPdfBase64] = useState<string | null>(null);

  const context = useMemo(() => toWizardContext(data), [data]);
  const manualOwnerToken = data.accessTokenType === "owner" ? data.accessToken.trim() : "";
  const paidToken =
    data.accessTokenType === "paid"
      ? data.accessToken.trim() || data.paidSessionToken
      : data.paidSessionToken;
  const auth: AuthTokens = {
    ownerToken: manualOwnerToken || undefined,
    sessionToken: manualOwnerToken ? undefined : paidToken || undefined,
  };

  useEffect(() => {
    const stored = window.localStorage.getItem(STORAGE_KEY);
    if (stored) {
      try {
        const parsed = JSON.parse(stored) as {
          sessionToken?: string;
          email?: string;
          creditsRemaining?: number;
        };
        setData((current) => ({
          ...current,
          paidSessionToken: parsed.sessionToken || "",
          accessToken: parsed.sessionToken || current.accessToken,
          accessTokenType: parsed.sessionToken ? "paid" : current.accessTokenType,
          paidEmail: parsed.email || current.paidEmail,
          creditsRemaining: parsed.creditsRemaining ?? current.creditsRemaining,
        }));
      } catch {
        window.localStorage.removeItem(STORAGE_KEY);
      }
    }
  }, []);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const checkoutSessionId = params.get("session_token") || params.get("checkout_session_id");
    if (!checkoutSessionId) {
      return;
    }

    let cancelled = false;
    setSessionMessage("A confirmar pagamento...");
    exchangeCheckoutSession(checkoutSessionId)
      .then((session) => {
        if (cancelled) {
          return;
        }
        setData((current) => ({
          ...current,
          paidSessionToken: session.session_token,
          accessToken: session.session_token,
          accessTokenType: "paid",
          paidEmail: session.email,
          creditsRemaining: session.credits_remaining,
        }));
        window.localStorage.setItem(
          STORAGE_KEY,
          JSON.stringify({
            sessionToken: session.session_token,
            email: session.email,
            creditsRemaining: session.credits_remaining,
          }),
        );
        setSessionMessage("Pagamento confirmado. Sessao paga ativa.");
        window.history.replaceState(null, "", window.location.pathname);
      })
      .catch((err) => {
        if (!cancelled) {
          setSessionMessage("");
          setError(err instanceof Error ? err.message : "Erro ao confirmar pagamento.");
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  function updateData(patch: Partial<WizardData>) {
    setData((current) => ({ ...current, ...patch }));
    if (
      "cvText" in patch ||
      "jobDescription" in patch ||
      "responseRate" in patch ||
      "targetRole" in patch ||
      "outputLanguage" in patch
    ) {
      setData((current) => ({
        ...current,
        ats: "outputLanguage" in patch ? current.ats : null,
        agentReview: "outputLanguage" in patch ? current.agentReview : null,
        agentReviewError: "outputLanguage" in patch ? current.agentReviewError : "",
        optimizedMarkdown: "",
      }));
      setPdfBase64(null);
    }
    setError("");
  }

  function reset() {
    setStep(1);
    setData((current) => ({
      ...INITIAL_DATA,
      paidEmail: current.paidEmail,
      paidSessionToken: current.paidSessionToken,
      creditsRemaining: current.creditsRemaining,
      accessToken: current.accessToken,
      accessTokenType: current.accessTokenType,
    }));
    setPdfBase64(null);
    setError("");
    setSessionMessage("");
  }

  async function runAtsScore() {
    setAtsLoading(true);
    setError("");
    try {
      const ats = await analyzeAts(
        {
          cv: data.cvText,
          job: data.jobDescription,
          context,
        },
        auth,
      );
      try {
        const agentReview = await reviewAgents(
          {
            cv: data.cvText,
            job: data.jobDescription,
            context,
            ats,
          },
          auth,
        );
        updateData({ ats, agentReview, agentReviewError: "" });
      } catch (agentErr) {
        updateData({
          ats,
          agentReview: null,
          agentReviewError:
            agentErr instanceof Error
              ? agentErr.message
              : "Agent review indisponivel. Podes continuar apenas com ATS.",
        });
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao gerar score ATS.");
    } finally {
      setAtsLoading(false);
    }
  }

  async function runOptimize() {
    if (!data.ats) {
      setError("Gera o ATS score antes de otimizar o CV.");
      return;
    }

    setOptimizeLoading(true);
    setError("");
    try {
      const response = await optimizeCv(
        {
          cv: data.cvText,
          job: data.jobDescription,
          ats: data.ats,
          context,
          language: data.outputLanguage,
          ...(data.agentReview ? { agent_review: data.agentReview } : {}),
        },
        auth,
      );
      updateData({
        optimizedMarkdown: response.markdown,
        creditsRemaining: response.credits_remaining ?? data.creditsRemaining,
      });
      if (typeof response.credits_remaining === "number" && data.paidSessionToken) {
        window.localStorage.setItem(
          STORAGE_KEY,
          JSON.stringify({
            sessionToken: data.paidSessionToken,
            email: data.paidEmail,
            creditsRemaining: response.credits_remaining,
          }),
        );
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao otimizar CV.");
    } finally {
      setOptimizeLoading(false);
    }
  }

  async function runCheckout() {
    setCheckoutLoading(true);
    setError("");
    try {
      const currentUrl = `${window.location.origin}/app`;
      const checkout = await createCheckout(data.paidEmail, currentUrl);
      window.location.href = checkout.checkout_url;
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao criar checkout Stripe.");
    } finally {
      setCheckoutLoading(false);
    }
  }

  async function getPdf() {
    if (pdfBase64) {
      return pdfBase64;
    }
    if (!data.optimizedMarkdown) {
      setError("Gera o CV otimizado antes de descarregar PDF.");
      return null;
    }

    setPdfLoading(true);
    setError("");
    try {
      const response = await generateCvPdf(data.optimizedMarkdown, data.outputLanguage, auth);
      setPdfBase64(response.pdf_base64);
      return response.pdf_base64;
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao gerar PDF.");
      return null;
    } finally {
      setPdfLoading(false);
    }
  }

  return (
    <WizardShell currentStep={step} onReset={reset}>
      {step === 1 && (
        <Step1Context
          data={data}
          onChange={updateData}
          onNext={() => setStep(2)}
        />
      )}
      {step === 2 && (
        <Step2Upload
          data={data}
          onChange={updateData}
          onBack={() => setStep(1)}
          onNext={() => setStep(3)}
        />
      )}
      {step === 3 && (
        <Step3Score
          ats={data.ats}
          agentReview={data.agentReview}
          agentReviewError={data.agentReviewError}
          accessToken={data.accessTokenType === "owner" ? data.accessToken : ""}
          loading={atsLoading}
          error={error}
          onAccessTokenChange={(accessToken) => updateData({ accessToken, accessTokenType: "owner" })}
          onAnalyze={runAtsScore}
          onBack={() => setStep(2)}
          onNext={() => setStep(4)}
        />
      )}
      {step === 4 && (
        <Step4Result
          data={data}
          optimizing={optimizeLoading}
          pdfLoading={pdfLoading}
          checkoutLoading={checkoutLoading}
          sessionMessage={sessionMessage}
          error={error}
          onChange={updateData}
          onOptimize={runOptimize}
          onCreateCheckout={runCheckout}
          onDownloadPdf={getPdf}
        />
      )}
    </WizardShell>
  );
}
