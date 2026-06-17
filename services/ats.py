import json
import re

from config import SECTION_CAPS
from services.tfidf import cosine_similarity_text, top_job_terms

ATS_INSIGHTS_SCHEMA = {
    "type": "object",
    "properties": {
        "diagnostic": {"type": "string"},
        "next_steps": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "impact": {"type": "string", "enum": ["high", "medium", "low"]},
                    "title": {"type": "string"},
                    "bullets": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["impact", "title", "bullets"],
            },
        },
    },
    "required": ["diagnostic", "next_steps"],
}

EDUCATION_PATTERN = re.compile(
    r"(bachelor|master|phd|licenciatura|mestrado|degree|universit|formação|graduat)",
    re.IGNORECASE,
)


def _term_in_cv(term: str, cv_lower: str) -> bool:
    return term.lower() in cv_lower


def compute_local_ats(cv: str, job: str) -> dict:
    similarity = float(cosine_similarity_text(cv, job))
    job_terms = top_job_terms(job, cv)
    cv_lower = cv.lower()
    present = sorted(t for t in job_terms if _term_in_cv(t, cv_lower))
    missing = sorted(t for t in job_terms if t not in set(present))

    term_ratio = len(present) / max(len(job_terms), 1)
    terms_s = int(min(term_ratio, 1.0) * SECTION_CAPS["terms"])
    req_s = int(min(term_ratio * 1.1, 1.0) * SECTION_CAPS["requirements"])
    exp_s = int(min(similarity * 1.2, 1.0) * SECTION_CAPS["experience"])
    edu_s = (
        SECTION_CAPS["education"]
        if EDUCATION_PATTERN.search(cv)
        else int(SECTION_CAPS["education"] * 0.3)
    )
    overall = min(100, req_s + exp_s + terms_s + edu_s)

    return {
        "overall_score": overall,
        "cosine_similarity": round(similarity, 3),
        "keywords_present": present[:20],
        "keywords_missing": missing[:20],
        "section_scores": {
            "requirements": req_s,
            "experience": exp_s,
            "terms": terms_s,
            "education": edu_s,
        },
    }


def validate_ats_insights(raw: dict) -> dict:
    if "diagnostic" not in raw or "next_steps" not in raw:
        raise ValueError("Resposta incompleta da IA: faltam diagnostic ou next_steps")

    next_steps = []
    for step in raw.get("next_steps", [])[:3]:
        if not isinstance(step, dict):
            continue
        impact = step.get("impact", "medium")
        if impact not in ("high", "medium", "low"):
            impact = "medium"
        bullets = [str(b) for b in step.get("bullets", []) if b][:5]
        next_steps.append({
            "impact": impact,
            "title": str(step.get("title", "")),
            "bullets": bullets,
        })

    return {
        "diagnostic": str(raw.get("diagnostic", "")),
        "next_steps": next_steps,
    }


def merge_ats_results(local: dict, insights: dict) -> dict:
    validated = validate_ats_insights(insights)
    return {
        "overall_score": local["overall_score"],
        "cosine_similarity": local["cosine_similarity"],
        "keywords_present": local["keywords_present"],
        "keywords_missing": local["keywords_missing"],
        "section_scores": local["section_scores"],
        "diagnostic": validated["diagnostic"],
        "next_steps": validated["next_steps"],
    }


def build_ats_insights_prompt(cv: str, job: str, local: dict, ctx: dict) -> str:
    return f"""You are an expert ATS career coach. A deterministic scorer already computed match metrics.

Candidate context:
- Interview response rate: {ctx.get('q1', 'N/A')}
- Career goal: {ctx.get('q2', 'N/A')}
- Target level: {ctx.get('q3', 'N/A')}

Deterministic baseline (do NOT contradict keyword lists or scores):
{json.dumps(local, ensure_ascii=False)}

Provide:
- diagnostic: one clear sentence on the main ATS weakness
- next_steps: max 3 actionable items (impact high/medium/low, title, bullets)

Rules:
- Do not invent skills or experience.
- Reference missing keywords from the baseline when relevant.

Resume:
{cv[:12000]}

Job description:
{job[:8000]}"""


def run_ats_analysis(ai_client, cv: str, job: str, ctx: dict) -> dict:
    local = compute_local_ats(cv, job)
    prompt = build_ats_insights_prompt(cv, job, local, ctx)
    insights = ai_client.generate_json(prompt, ATS_INSIGHTS_SCHEMA, temperature=0.1)
    return merge_ats_results(local, insights)
