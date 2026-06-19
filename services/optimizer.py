import json
import re


def build_optimize_prompts(
    cv: str,
    job: str,
    ats: dict,
    ctx: dict,
    agent_review: dict | None = None,
) -> tuple[str, str]:
    missing = ", ".join(ats.get("keywords_missing", [])[:15]) or "none"
    next_steps = json.dumps(ats.get("next_steps", [])[:3], ensure_ascii=False)
    agent_guidance = _agent_guidance(agent_review)

    sys_prompt = """You are an expert HR resume writer optimizing for ATS systems.

HARD RULES:
- NEVER invent employers, dates, degrees, certifications, or tools not supported by the original resume.
- Reframe existing experience; integrate missing keywords ONLY when truthful.
- Output ONLY clean Markdown starting with '# Full Name'. No conversational text or code fences.

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


def strip_markdown_fences(text: str) -> str:
    markdown = text.strip()
    if markdown.startswith("```"):
        markdown = re.sub(r"^```(?:markdown)?\n?", "", markdown)
        markdown = re.sub(r"\n?```$", "", markdown)
    return markdown
