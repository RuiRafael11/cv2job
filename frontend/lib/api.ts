const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type WizardContext = {
  q1: string;
  q2: string;
  q3: string;
};

export type AuthTokens = {
  ownerToken?: string;
  sessionToken?: string;
};

export type AtsScoreRequest = {
  cv: string;
  job: string;
  context: WizardContext;
};

export type AtsScoreResponse = {
  overall_score: number;
  cosine_similarity?: number;
  keywords_present: string[];
  keywords_missing: string[];
  section_scores: {
    requirements: number;
    experience: number;
    terms: number;
    education: number;
  };
  diagnostic?: string;
  next_steps?: Array<{
    impact?: "high" | "medium" | "low" | string;
    title?: string;
    bullets?: string[];
  }>;
};

export type OptimizeRequest = {
  cv: string;
  job: string;
  ats: AtsScoreResponse;
  context: WizardContext;
  agent_review?: AgentReviewResponse;
};

export type OptimizeResponse = {
  markdown: string;
  credits_remaining?: number | null;
};

export type CheckoutResponse = {
  checkout_url: string;
  checkout_session_id: string;
};

export type ExchangeSessionResponse = {
  session_token: string;
  email: string;
  credits_remaining: number;
};

export type GenerateCvResponse = {
  pdf_base64: string;
};

export type AgentPanelReview = {
  agent: "ATS" | "Recruiter" | "Truthfulness" | "Writer" | string;
  score: number;
  verdict: string;
  findings: string[];
  recommendations: string[];
};

export type AgentReviewResponse = {
  reviews: AgentPanelReview[];
  consensus: string;
  priority_actions: string[];
  truthfulness_warnings: string[];
  optimizer_recommendations: string[];
  source: "ai" | "deterministic" | string;
  guardrails: string[];
};

async function requestJson<T>(
  path: string,
  body?: Record<string, unknown>,
  auth: AuthTokens = {},
): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };

  if (auth.ownerToken) {
    headers["X-Owner-Token"] = auth.ownerToken;
  } else if (auth.sessionToken) {
    headers.Authorization = `Bearer ${auth.sessionToken}`;
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers,
    body: JSON.stringify({
      ...body,
      ...(auth.sessionToken ? { session_token: auth.sessionToken } : {}),
      ...(auth.ownerToken ? { owner_token: auth.ownerToken } : {}),
    }),
  });

  if (!response.ok) {
    let message = `Request failed with status ${response.status}.`;
    try {
      const data = (await response.json()) as { detail?: unknown };
      if (typeof data.detail === "string") {
        message = data.detail;
      }
    } catch {
      const text = await response.text();
      if (text) {
        message = text;
      }
    }
    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

export function analyzeAts(payload: AtsScoreRequest, auth?: AuthTokens) {
  return requestJson<AtsScoreResponse>("/api/ats-score", payload, auth);
}

export function reviewAgents(
  payload: AtsScoreRequest & { ats?: AtsScoreResponse },
  auth?: AuthTokens,
) {
  return requestJson<AgentReviewResponse>("/api/agent-review", payload, auth);
}

export function optimizeCv(payload: OptimizeRequest, auth: AuthTokens) {
  return requestJson<OptimizeResponse>("/api/optimize", payload, auth);
}

export function generateCvPdf(markdown: string, auth: AuthTokens) {
  return requestJson<GenerateCvResponse>("/api/generate-cv", { markdown }, auth);
}

export function createCheckout(email: string, currentUrl: string) {
  return requestJson<CheckoutResponse>("/api/billing/create-checkout", {
    email,
    success_url: `${currentUrl}?session_token={CHECKOUT_SESSION_ID}`,
    cancel_url: currentUrl,
  });
}

export function exchangeCheckoutSession(checkoutSessionId: string) {
  return requestJson<ExchangeSessionResponse>("/api/billing/exchange-session", {
    checkout_session_id: checkoutSessionId,
  });
}

export function base64ToBlob(base64: string, mime = "application/pdf") {
  const byteCharacters = atob(base64);
  const byteNumbers = Array.from(byteCharacters, (char) => char.charCodeAt(0));
  return new Blob([new Uint8Array(byteNumbers)], { type: mime });
}
