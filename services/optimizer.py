import json
import re


def build_optimize_prompts(
    cv: str,
    job: str,
    ats: dict,
    ctx: dict,
    agent_review: dict | None = None,
    language: str = "en",
) -> tuple[str, str]:
    missing = ", ".join(ats.get("keywords_missing", [])[:15]) or "none"
    next_steps = json.dumps(ats.get("next_steps", [])[:3], ensure_ascii=False)
    agent_guidance = _agent_guidance(agent_review)
    language_rules = _language_rules(language)

    sys_prompt = """You are an expert HR resume writer optimizing for ATS systems.

HARD RULES:
- NEVER invent employers, dates, degrees, certifications, or tools not supported by the original resume.
- Reframe existing experience; integrate missing keywords ONLY when truthful.
- Preserve company names, universities, technologies, projects, certifications, dates, and locations exactly when they are factual names.
- Output ONLY clean Markdown starting with '# Full Name'. No conversational text or code fences.
- Keep the Markdown compatible with the Harvard PDF renderer: use # for the name, ## for section headings, ### for roles/degrees, and '-' bullets.

Harvard Markdown structure:
# Full Name
contact | email | city
## EDUCATION
### Institution — Degree | Dates
## EXPERIENCE
### Company — Role | Dates
- Achievement bullet with metrics
## SKILLS
## PROJECTS (optional)"""

    user_prompt = f"""Candidate context:
- Interview response rate: {ctx['q1']}
- Career goal: {ctx['q2']}
- Target level: {ctx['q3']}

Output language:
{language_rules}

ATS analysis to address:
- Overall score: {ats.get('overall_score', 0)}/100
- Cosine similarity: {ats.get('cosine_similarity', 'N/A')}
- Main weakness: {ats.get('diagnostic', '')}
- Missing keywords (integrate only if truthful): {missing}
- Priority fixes: {next_steps}
{agent_guidance}

Original resume:
{cv}

Job description:
{job}"""

    return sys_prompt, user_prompt


def _agent_guidance(agent_review: dict | None) -> str:
    if not agent_review:
        return "- Agent review consensus: N/A"

    guidance = {
        "consensus": agent_review.get("consensus", ""),
        "priority_actions": agent_review.get("priority_actions", [])[:5],
        "truthfulness_warnings": agent_review.get("truthfulness_warnings", [])[:5],
        "optimizer_recommendations": agent_review.get("optimizer_recommendations", [])[:5],
    }
    return f"- Agent review guidance: {json.dumps(guidance, ensure_ascii=False)}"


def _language_rules(language: str) -> str:
    if language == "pt":
        return """- Portuguese (European/neutral).
- Translate resume prose into professional Portuguese while preserving factual names and entities.
- Use Portuguese section headings such as RESUMO, FORMAÇÃO, EXPERIÊNCIA, PROJETOS, COMPETÊNCIAS, IDIOMAS when those sections are present.
- Do not invent experience, roles, employers, certifications, metrics, tools, dates, or locations.
- Keep ATS-friendly Markdown structure."""

    return """- English.
- Use clear, professional, ATS-friendly English for an international CV.
- Use English section headings such as SUMMARY, EDUCATION, EXPERIENCE, PROJECTS, SKILLS, LANGUAGES when those sections are present.
- Do not invent experience, roles, employers, certifications, metrics, tools, dates, or locations.
- Keep ATS-friendly Markdown structure."""


def strip_markdown_fences(text: str) -> str:
    markdown = text.strip()
    if markdown.startswith("```"):
        markdown = re.sub(r"^```(?:markdown)?\n?", "", markdown)
        markdown = re.sub(r"\n?```$", "", markdown)
    return markdown
