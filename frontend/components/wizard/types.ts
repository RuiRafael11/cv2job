import type { AgentReviewResponse, AtsScoreResponse, OutputLanguage, WizardContext } from "@/lib/api";

export type WizardData = {
  responseRate: string;
  jobDescription: string;
  targetRole: string;
  cvFileName: string;
  cvText: string;
  ats: AtsScoreResponse | null;
  agentReview: AgentReviewResponse | null;
  agentReviewError: string;
  optimizedMarkdown: string;
  creditsRemaining: number | null;
  paidEmail: string;
  paidSessionToken: string;
  accessToken: string;
  accessTokenType: "owner" | "paid";
  outputLanguage: OutputLanguage;
};

export function toWizardContext(data: WizardData): WizardContext {
  return {
    q1: data.responseRate || "N/A",
    q2: data.targetRole || "N/A",
    q3: data.jobDescription ? "Vaga especifica fornecida" : "N/A",
  };
}
