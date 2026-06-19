import json
from typing import Any


AGENT_NAMES = ("ATS", "Recruiter", "Truthfulness", "Writer")

AGENT_REVIEW_SCHEMA = {
    "type": "object",
    "properties": {
        "reviews": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "agent": {"type": "string"},
                    "score": {"type": "integer"},
                    "verdict": {"type": "string"},
                    "findings": {"type": "array", "items": {"type": "string"}},
                    "recommendations": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["agent", "score", "verdict", "findings", "recommendations"],
            },
        },
        "consensus": {"type": "string"},
        "priority_actions": {"type": "array", "items": {"type": "string"}},
        "truthfulness_warnings": {"type": "array", "items": {"type": "string"}},
        "optimizer_recommendations": {"type": "array", "items": {"type": "string"}},
    },
    "required": [
        "reviews",
        "consensus",
        "priority_actions",
        "truthfulness_warnings",
        "optimizer_recommendations",
    ],
}

GUARDRAILS = [
    "Do not invent employers.",
    "Do not invent dates.",
    "Do not invent certifications.",
    "Do not invent tools.",
    "Do not invent experience.",
    "Do not add information unsupported by the CV or supplied context.",
]


def build_deterministic_agent_review(
    cv: str,
    job: str,
    ats: dict[str, Any] | None = None,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    ats = ats or {}
    context = context or {}
    score = int(ats.get("overall_score", 0) or 0)
    missing = [str(term) for term in ats.get("keywords_missing", [])[:8]]
    present = [str(term) for term in ats.get("keywords_present", [])[:8]]
    next_steps = ats.get("next_steps", []) or []
    diagnostic = str(ats.get("diagnostic", "") or "Deterministic review based on supplied CV and job description.")
    response_rate = str(context.get("q1", "N/A"))
    target = str(context.get("q2", "N/A"))

    missing_text = ", ".join(missing) if missing else "no obvious high-priority keyword gaps"
    present_text = ", ".join(present) if present else "limited confirmed keyword overlap"

    priority_actions = _priority_actions(missing, next_steps)
    truthfulness_warnings = [
        "Only add missing keywords when the original CV or supplied context supports them.",
        "Keep employers, dates, degrees, certifications, tools, and seniority exactly grounded in the source CV.",
        "Rewrite weak bullets around evidence already present; do not create new achievements.",
    ]
    optimizer_recommendations = [
        f"Address keyword gaps carefully: {missing_text}.",
        "Preserve factual claims from the original CV and improve wording, structure, and ordering.",
        "Use Harvard-style sections with clear EDUCATION, EXPERIENCE, SKILLS, and PROJECTS headings where supported.",
    ]

    reviews = [
        {
            "agent": "ATS",
            "score": score,
            "verdict": diagnostic,
            "findings": [
                f"Current ATS score is {score}/100.",
                f"Confirmed overlap: {present_text}.",
                f"Missing terms to assess truthfully: {missing_text}.",
            ],
            "recommendations": [
                "Prioritize the most repeated job terms that are already backed by the CV.",
                "Mirror the job description's terminology without changing facts.",
            ],
        },
        {
            "agent": "Recruiter",
            "score": _bounded_score(score + 5),
            "verdict": "The CV should make fit and career direction obvious within the first scan.",
            "findings": [
                f"Candidate context says response rate is: {response_rate}.",
                f"Target direction: {target}.",
            ],
            "recommendations": [
                "Lead bullets with role-relevant outcomes before tools.",
                "Make the target role visible through the summary, skills, and project ordering.",
            ],
        },
        {
            "agent": "Truthfulness",
            "score": 100 if cv.strip() else 40,
            "verdict": "Optimization must stay evidence-based and avoid unsupported additions.",
            "findings": [
                "Missing keywords are suggestions to verify, not facts to insert automatically.",
                "The safest rewrite reframes existing evidence rather than adding new claims.",
            ],
            "recommendations": truthfulness_warnings[:2],
        },
        {
            "agent": "Writer",
            "score": _bounded_score(score + 10),
            "verdict": "The final CV should be concise, ATS-readable, and formatted for a Harvard-style PDF.",
            "findings": [
                "Markdown output needs clean headings and short achievement bullets.",
                "Dense keyword lists should be converted into readable skills and evidence-backed bullets.",
            ],
            "recommendations": [
                "Use direct action verbs and avoid generic filler.",
                "Keep bullets specific, short, and grounded in the source CV.",
            ],
        },
    ]

    return {
        "reviews": reviews,
        "consensus": (
            "Improve ATS alignment and recruiter clarity while preserving strict truthfulness. "
            "The optimizer should integrate only supported terms and avoid inventing experience."
        ),
        "priority_actions": priority_actions,
        "truthfulness_warnings": truthfulness_warnings,
        "optimizer_recommendations": optimizer_recommendations,
        "source": "deterministic",
        "guardrails": GUARDRAILS,
    }


def run_agent_review(
    ai_client: Any,
    cv: str,
    job: str,
    ats: dict[str, Any] | None = None,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    fallback = build_deterministic_agent_review(cv, job, ats, context)
    if ai_client is None:
        return fallback

    prompt = build_agent_review_prompt(cv, job, ats or {}, context or {}, fallback)
    try:
        raw = ai_client.generate_json(prompt, AGENT_REVIEW_SCHEMA, temperature=0.1)
        validated = validate_agent_review(raw)
        return {
            **validated,
            "source": "ai",
            "guardrails": GUARDRAILS,
        }
    except Exception:
        return fallback


def build_agent_review_prompt(
    cv: str,
    job: str,
    ats: dict[str, Any],
    context: dict[str, Any],
    fallback: dict[str, Any],
) -> str:
    return f"""You are a four-agent CV review panel:
1. ATS Agent
2. Recruiter Agent
3. Truthfulness Agent
4. Writer Agent

Return JSON matching the supplied schema with one review per agent.

Hard guardrails:
{json.dumps(GUARDRAILS, ensure_ascii=False)}

Candidate context:
{json.dumps(context, ensure_ascii=False)}

ATS baseline:
{json.dumps(ats, ensure_ascii=False)}

Deterministic fallback to respect:
{json.dumps(fallback, ensure_ascii=False)}

CV:
{cv[:12000]}

Job description:
{job[:8000]}"""


def validate_agent_review(raw: dict[str, Any]) -> dict[str, Any]:
    reviews = []
    raw_reviews = raw.get("reviews", [])
    for expected_name in AGENT_NAMES:
        match = next(
            (
                review
                for review in raw_reviews
                if isinstance(review, dict)
                and str(review.get("agent", "")).lower() == expected_name.lower()
            ),
            {},
        )
        reviews.append({
            "agent": expected_name,
            "score": _bounded_score(match.get("score", 0)),
            "verdict": str(match.get("verdict", "")),
            "findings": _string_list(match.get("findings", []), 5),
            "recommendations": _string_list(match.get("recommendations", []), 5),
        })

    return {
        "reviews": reviews,
        "consensus": str(raw.get("consensus", "")),
        "priority_actions": _string_list(raw.get("priority_actions", []), 5),
        "truthfulness_warnings": _string_list(raw.get("truthfulness_warnings", []), 5),
        "optimizer_recommendations": _string_list(raw.get("optimizer_recommendations", []), 5),
    }


def _priority_actions(missing: list[str], next_steps: list[Any]) -> list[str]:
    actions = []
    for step in next_steps[:3]:
        if isinstance(step, dict) and step.get("title"):
            actions.append(str(step["title"]))
    if missing:
        actions.append(f"Verify and integrate supported missing terms: {', '.join(missing[:5])}.")
    actions.append("Keep all new wording grounded in the original CV.")
    return actions[:5]


def _bounded_score(value: Any) -> int:
    try:
        return max(0, min(100, int(value)))
    except (TypeError, ValueError):
        return 0


def _string_list(value: Any, limit: int) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if item][:limit]
