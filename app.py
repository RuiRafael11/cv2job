import base64
import os

import requests
import streamlit as st
from dotenv import load_dotenv

from config import WIZARD_QUESTIONS
from services.file_reader import read_uploaded
from session import init_session_state, reset_session, sync_inputs_and_invalidate
from ui.css import inject_custom_css
from ui.dashboard import esc, gauge_svg, progress_bar_html, subscore_circle

defaults = {
    "login_email": "",
    "session_token": None,
    "credits": 0,
    "owner_mode": False,
    "step": 1,
    "wizard_step": 0,
    "q1_answer": None,
    "q2_answer": None,
    "q3_answer": None,
    "jd_text_pasted": "",
    "suggestions": [],
    "ats_data": None,
    "agent_review": None,
    "agent_review_error": "",
    "final_markdown": "",
    "cv_content": None,
    "job_content": None,
    "api_base_url": "http://127.0.0.1:8000",
    "backend_session_token": "",
    "paid_email": "",
    "checkout_session_id": "",
    "exchanged_checkout_session_id": "",
    "checkout_url": "",
    "credits_remaining": None,
    "output_language": "en",
    "pdf_bytes": None,
    "pdf_hash": None,
    "inputs_fp": None,
}
for key, val in defaults.items():
    st.session_state.setdefault(key, val)

load_dotenv()
SERVER_OWNER_TOKEN = os.getenv("OWNER_TOKEN", "")
PRICE_AMOUNT_CENTS = int(os.getenv("PRICE_AMOUNT_CENTS", "900"))
PRICE_CURRENCY = os.getenv("PRICE_CURRENCY", "eur").upper()
ENABLE_UNVERIFIED_EMAIL_LOGIN = os.getenv("ENABLE_UNVERIFIED_EMAIL_LOGIN", "").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}

st.set_page_config(layout="wide", page_title="ATS AI Resume Optimizer")
inject_custom_css()
init_session_state()


def api_url(path: str) -> str:
    return f"{st.session_state.api_base_url.rstrip('/')}{path}"


def auth_payload() -> dict:
    payload = {}
    if st.session_state.backend_session_token:
        payload["session_token"] = st.session_state.backend_session_token
    return payload


def auth_headers() -> dict:
    headers = {}
    if SERVER_OWNER_TOKEN:
        headers["Authorization"] = f"Bearer {SERVER_OWNER_TOKEN}"
    elif st.session_state.backend_session_token:
        headers["Authorization"] = f"Bearer {st.session_state.backend_session_token}"
    return headers


def call_api(path: str, payload: dict) -> dict:
    response = requests.post(
        api_url(path),
        json={**payload, **auth_payload()},
        headers=auth_headers(),
        timeout=120,
    )
    if response.status_code >= 400:
        try:
            detail = response.json().get("detail", response.text)
        except ValueError:
            detail = response.text
        raise RuntimeError(detail)
    return response.json()


def is_authenticated() -> bool:
    return bool(SERVER_OWNER_TOKEN or st.session_state.backend_session_token)


def has_unlock_access() -> bool:
    if SERVER_OWNER_TOKEN:
        return True
    return bool(st.session_state.backend_session_token and (st.session_state.credits_remaining or 0) > 0)


def login_user(email: str) -> None:
    if not ENABLE_UNVERIFIED_EMAIL_LOGIN:
        raise RuntimeError("Login por email sem verificacao esta desativado. Usa Stripe Checkout.")
    data = call_api("/api/auth/login", {"email": email})
    st.session_state.backend_session_token = data["session_token"]
    st.session_state.paid_email = data["email"]
    st.session_state.credits_remaining = data["credits_remaining"]


def start_checkout(email: str) -> None:
    email = email.strip()
    if not email:
        raise RuntimeError("Insere um email para continuar.")
    current_url = os.getenv("FRONTEND_BASE_URL", "http://localhost:8501")
    success_url = f"{current_url}?session_token={{CHECKOUT_SESSION_ID}}"
    data = call_api(
        "/api/billing/create-checkout",
        {
            "email": email,
            "success_url": success_url,
            "cancel_url": current_url,
        },
    )
    st.session_state.paid_email = email
    st.session_state.checkout_url = data["checkout_url"]
    st.session_state.checkout_session_id = data["checkout_session_id"]


def output_language_label() -> str:
    return "Português" if st.session_state.output_language == "pt" else "English"


def sync_output_language(selected_label: str) -> None:
    selected_language = "pt" if selected_label == "Português" else "en"
    if st.session_state.output_language != selected_language:
        st.session_state.output_language = selected_language
        st.session_state.final_markdown = ""
        for key in ("pdf_bytes", "pdf_hash"):
            st.session_state.pop(key, None)
        if st.session_state.get("wizard_step", 0) >= 7:
            st.session_state.wizard_step = 6


def render_unlock_cta() -> None:
    st.info("Para ver o resultado completo, compra creditos via Stripe.")
    if not st.session_state.backend_session_token:
        st.session_state.login_email = st.text_input(
            "Email",
            value=st.session_state.login_email,
            placeholder="teu@email.com",
            key="unlock_login_email",
        )
        if ENABLE_UNVERIFIED_EMAIL_LOGIN:
            if st.button("Entrar / Registar", use_container_width=True, key="unlock_login_button"):
                try:
                    login_user(st.session_state.login_email.strip())
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro no login: {e}")
        else:
            st.caption("Login por email sem verificacao esta desativado. Usa o checkout para criar sessao paga.")
        checkout_email = st.session_state.login_email.strip()
    else:
        checkout_email = st.session_state.paid_email or st.session_state.login_email

    price_label = f"{PRICE_AMOUNT_CENTS / 100:.2f} {PRICE_CURRENCY}"
    if st.button(f"Comprar 10 creditos — {price_label}", use_container_width=True, key="unlock_buy_credits"):
        try:
            start_checkout(checkout_email)
        except Exception as e:
            st.error(f"Erro ao criar checkout: {e}")
    if st.session_state.checkout_url:
        st.markdown(
            f'<a href="{esc(st.session_state.checkout_url)}" target="_blank" rel="noopener noreferrer">Abrir Stripe Checkout</a>',
            unsafe_allow_html=True,
        )


def current_context() -> dict:
    return {
        "q1": st.session_state.q1_answer or "N/A",
        "q2": st.session_state.q2_answer or "N/A",
        "q3": st.session_state.q3_answer or "N/A",
    }


query_params = st.query_params
checkout_session_id = query_params.get("session_token") or query_params.get("checkout_session_id")
if checkout_session_id and st.session_state.exchanged_checkout_session_id != checkout_session_id:
    try:
        data = call_api(
            "/api/billing/exchange-session",
            {"checkout_session_id": checkout_session_id},
        )
        st.session_state.backend_session_token = data["session_token"]
        st.session_state.paid_email = data["email"]
        st.session_state.credits_remaining = data["credits_remaining"]
        st.session_state.exchanged_checkout_session_id = checkout_session_id
        st.session_state.checkout_url = ""
        st.query_params.clear()
        st.success("Pagamento confirmado. Sessao paga ativa.")
    except Exception as e:
        st.error(f"Erro ao confirmar pagamento: {e}")


with st.sidebar:
    st.header("Configuracao")
    st.session_state.api_base_url = st.text_input(
        "Backend API URL",
        value=st.session_state.api_base_url,
        help="Ex.: http://127.0.0.1:8000",
    )
    selected_language_label = st.radio(
        "Idioma do CV",
        ["English", "Português"],
        index=0 if st.session_state.output_language == "en" else 1,
        horizontal=True,
    )
    sync_output_language(selected_language_label)
    if SERVER_OWNER_TOKEN:
        st.success("Modo owner ativo.")
    elif st.session_state.backend_session_token:
        st.success(f"Sessao paga ativa. Creditos: {st.session_state.credits_remaining}")
        if st.session_state.paid_email:
            st.caption(st.session_state.paid_email)
    else:
        st.info("Sem sessao ativa.")
        st.session_state.login_email = st.text_input(
            "Email",
            value=st.session_state.login_email,
            placeholder="teu@email.com",
        )
        if ENABLE_UNVERIFIED_EMAIL_LOGIN:
            if st.button("Entrar / Registar", use_container_width=True):
                try:
                    login_user(st.session_state.login_email.strip())
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro no login: {e}")
        else:
            st.caption("Login por email sem verificacao desativado.")
        price_label = f"{PRICE_AMOUNT_CENTS / 100:.2f} {PRICE_CURRENCY}"
        if st.button(f"Comprar 10 creditos — {price_label}", use_container_width=True, key="sidebar_buy_credits"):
            try:
                start_checkout(st.session_state.login_email)
            except Exception as e:
                st.error(f"Erro ao criar checkout: {e}")
        if st.session_state.checkout_url:
            st.markdown(
                f'<a href="{esc(st.session_state.checkout_url)}" target="_blank" rel="noopener noreferrer">Abrir Stripe Checkout</a>',
                unsafe_allow_html=True,
            )

    if st.button("Reiniciar App"):
        reset_session()
        st.rerun()


if 0 <= st.session_state.wizard_step < 3:
    q_idx = st.session_state.wizard_step
    q = WIZARD_QUESTIONS[q_idx]
    progress_pct = int(((q_idx + 1) / 4) * 100)

    st.markdown(f"""
    <div style="padding-top:8px;padding-bottom:24px;">
      <div class="wizard-progress"><div class="wizard-progress-bar" style="width:{progress_pct}%;"></div></div>
      <div class="wizard-step-indicator">{q_idx + 1} / 4</div>
    </div>
    <div style="max-width:620px;margin:0 auto;padding-top:16px;text-align:center;">
      <div class="section-badge" style="justify-content:center; display:flex;">{q["tag"]}</div>
      <div style="font-size:2.2rem;margin-bottom:12px; font-family:'Playfair Display',serif;">{q["title"]}</div>
      <div style="font-size:1rem;color:var(--text-secondary);margin-bottom:36px;">{q["subtitle"]}</div>
    </div>
    """, unsafe_allow_html=True)

    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        for opt in q["options"]:
            if st.button(f"**{opt['title']}** — {opt['desc']}", key=f"wiz_{q_idx}_{opt['val']}", use_container_width=True):
                st.session_state[q["var"]] = opt["val"]
                st.session_state.wizard_step += 1
                st.rerun()

        if q_idx > 0:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("← Voltar ao passo anterior", key="back"):
                st.session_state.wizard_step -= 1
                st.rerun()
    st.stop()


if st.session_state.wizard_step == 3:
    st.markdown("""
    <div style="padding-top:8px;padding-bottom:24px;">
      <div class="wizard-progress"><div class="wizard-progress-bar" style="width:100%;"></div></div>
      <div class="wizard-step-indicator">4 / 4</div>
    </div>
    <div style="max-width:800px;margin:0 auto;text-align:center;">
      <div class="section-badge" style="justify-content:center; display:flex;">ULTIMO PASSO</div>
      <div style="font-size:2.2rem;margin-bottom:12px; font-family:'Playfair Display',serif;">Carrega os teus dados</div>
      <div style="font-size:1rem;color:var(--text-secondary);margin-bottom:28px;">Faz upload do CV e da descricao da vaga.</div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([1, 1], gap="large")
    with c1:
        st.markdown("<div class='section-badge'>TEU CURRICULO</div>", unsafe_allow_html=True)
        cv_file = st.file_uploader("Upload do CV", type=["pdf", "docx", "txt", "md"], label_visibility="collapsed")
        if cv_file:
            st.session_state.cv_content = read_uploaded(cv_file)
            sync_inputs_and_invalidate(st.session_state.cv_content, st.session_state.job_content)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("← Voltar"):
            st.session_state.wizard_step -= 1
            st.rerun()

    with c2:
        st.markdown("<div class='section-badge'>DESCRICAO DA VAGA</div>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["Colar Texto", "Upload / Drag & Drop"])

        with tab1:
            st.session_state.jd_text_pasted = st.text_area(
                "Cola a descricao da vaga",
                value=st.session_state.jd_text_pasted,
                height=200,
                label_visibility="collapsed",
                placeholder="Cola aqui os requisitos, tecnologias e responsabilidades...",
            )
            if st.session_state.jd_text_pasted.strip():
                st.session_state.job_content = st.session_state.jd_text_pasted.strip()
                sync_inputs_and_invalidate(st.session_state.cv_content, st.session_state.job_content)

        with tab2:
            jd_file = st.file_uploader(
                "Upload da Vaga",
                type=["pdf", "docx", "txt", "md"],
                label_visibility="collapsed",
                key="jd_uploader",
            )
            if jd_file:
                st.session_state.job_content = read_uploaded(jd_file)
                sync_inputs_and_invalidate(st.session_state.cv_content, st.session_state.job_content)

    ready = bool(st.session_state.cv_content) and bool(st.session_state.job_content)

    st.markdown("<br>", unsafe_allow_html=True)
    _, col_btn, _ = st.columns([1, 1, 1])
    with col_btn:
        if st.button("Iniciar Analise ATS", type="primary", use_container_width=True, disabled=not ready):
            st.session_state.wizard_step = 4
            st.rerun()
    st.stop()


if st.session_state.wizard_step == 4:
    if st.session_state.get("ats_data"):
        st.session_state.wizard_step = 5
        st.rerun()

    with st.spinner("A cruzar o teu CV com os requisitos da vaga..."):
        try:
            st.session_state.ats_data = call_api(
                "/api/ats-score",
                {
                    "cv": st.session_state.cv_content,
                    "job": st.session_state.job_content,
                    "context": current_context(),
                },
            )
            try:
                st.session_state.agent_review = call_api(
                    "/api/agent-review",
                    {
                        "cv": st.session_state.cv_content,
                        "job": st.session_state.job_content,
                        "ats": st.session_state.ats_data,
                        "context": current_context(),
                    },
                )
                st.session_state.agent_review_error = ""
            except Exception as agent_error:
                st.session_state.agent_review = None
                st.session_state.agent_review_error = str(agent_error)
            st.session_state.wizard_step = 5
            st.rerun()
        except Exception as e:
            st.error(f"Erro na API: {e}")
            if st.button("Tentar Novamente"):
                st.rerun()
            st.stop()


if st.session_state.wizard_step == 5 and st.session_state.ats_data:
    d = st.session_state.ats_data
    overall = int(d.get("overall_score", 0))
    sections = d.get("section_scores", {})
    req_s = sections.get("requirements", 0)
    exp_s = sections.get("experience", 0)
    terms_s = sections.get("terms", 0)
    edu_s = sections.get("education", 0)
    cosine = d.get("cosine_similarity")

    top_left, top_right = st.columns([1, 1], gap="large")
    with top_left:
        st.markdown(gauge_svg(overall, 100), unsafe_allow_html=True)
        if cosine is not None:
            st.caption(f"Similaridade TF-IDF (cosseno): **{cosine}**")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(subscore_circle(req_s, 40, "REQUISITOS"), unsafe_allow_html=True)
        with c2:
            st.markdown(subscore_circle(exp_s, 30, "EXPERIENCIA"), unsafe_allow_html=True)
        with c3:
            st.markdown(subscore_circle(terms_s, 20, "TERMOS"), unsafe_allow_html=True)
        with c4:
            st.markdown(subscore_circle(edu_s, 10, "FORMACAO"), unsafe_allow_html=True)

    with top_right:
        ad_cls = "impact-high" if overall >= 70 else ("impact-medium" if overall >= 40 else "")
        ad_lbl = "ALTA ADERENCIA" if overall >= 70 else ("MEDIA" if overall >= 40 else "BAIXA")
        st.markdown(f"""
        <div style="padding-top:10px;">
          <div class="section-badge">DIAGNOSTICO DA IA</div>
          <div style="font-size:2.2rem; font-family:'Playfair Display',serif; margin-bottom:12px; line-height:1.1;">Como o teu CV e lido</div>
          <div style="margin-bottom:18px;"><span class="impact-badge {ad_cls}">{ad_lbl}</span></div>
          <div style="background:var(--bg-card); border:1px solid var(--border); border-radius:12px; padding:18px; color:var(--text-secondary); line-height:1.5;">
            {esc(d.get("diagnostic", ""))}
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color:var(--border); margin:40px 0;'>", unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="medium")
    with col1:
        st.markdown(f"""
        <div class="detail-card">
          <div class="section-badge">REQUISITOS (40pts)</div>
          <div style="font-size:1.4rem; font-family:'Playfair Display',serif; margin-bottom:10px;">Cobertura do Core</div>
          {progress_bar_html(req_s, 40)}
        </div>
        """, unsafe_allow_html=True)

        ptags = "".join(f'<span class="keyword-tag-present">{esc(kw)}</span>' for kw in d.get("keywords_present", [])[:8])
        mtags = "".join(f'<span class="keyword-tag-missing">{esc(kw)}</span>' for kw in d.get("keywords_missing", [])[:8])
        st.markdown(f"""
        <div class="detail-card" style="margin-top:16px;">
          <div class="section-badge">TERMOS DA VAGA (20pts)</div>
          <div style="margin-bottom:12px;">{progress_bar_html(terms_s, 20)}</div>
          <div style="margin-bottom:4px; font-size:0.7rem; color:var(--success);">ENCONTRADOS</div>
          <div style="margin-bottom:12px;">{ptags or '<span style="color:var(--text-muted)">Nenhum</span>'}</div>
          <div style="margin-bottom:4px; font-size:0.7rem; color:var(--danger);">EM FALTA</div>
          <div>{mtags or '<span style="color:var(--text-muted)">Nenhum</span>'}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="detail-card" style="margin-bottom:16px;">
          <div class="section-badge">EXPERIENCIA (30pts)</div>
          <div style="font-size:1.4rem; font-family:'Playfair Display',serif; margin-bottom:10px;">Maturidade Profissional</div>
          {progress_bar_html(exp_s, 30)}
        </div>
        <div class="detail-card">
          <div class="section-badge">FORMACAO (10pts)</div>
          <div style="font-size:1.4rem; font-family:'Playfair Display',serif; margin-bottom:10px;">Base Academica</div>
          {progress_bar_html(edu_s, 10)}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='section-badge' style='margin-top:40px;'>PLANO DE ACCAO</div>", unsafe_allow_html=True)
    for i, step in enumerate(d.get("next_steps", [])[:3]):
        imp = step.get("impact", "medium")
        cls = "impact-high" if imp == "high" else ("impact-medium" if imp == "medium" else "")
        lbl = "ALTO IMPACTO" if imp == "high" else "MEDIO IMPACTO"
        bullets = "".join(f"<li style='color:var(--text-secondary); margin-bottom:4px;'>{esc(b)}</li>" for b in step.get("bullets", []))
        st.markdown(f"""
        <div class="next-step-block">
          <div style="display:flex; align-items:center; margin-bottom:10px;">
            <span style="color:var(--accent); font-weight:bold; margin-right:8px;">0{i+1}</span>
            <span class="impact-badge {cls}">{lbl}</span>
          </div>
          <div style="font-size:1.2rem; font-family:'Playfair Display',serif; margin-bottom:8px;">{esc(step.get('title', ''))}</div>
          <ul style="margin:0; padding-left:16px;">{bullets}</ul>
        </div>
        """, unsafe_allow_html=True)

    if st.session_state.get("agent_review"):
        review = st.session_state.agent_review
        st.markdown("<div class='section-badge' style='margin-top:40px;'>AI AGENT REVIEW</div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="detail-card" style="margin-bottom:16px;">
          <div style="font-size:1.4rem; font-family:'Playfair Display',serif; margin-bottom:10px;">Consenso dos agentes</div>
          <div style="color:var(--text-secondary); line-height:1.5;">{esc(review.get("consensus", ""))}</div>
        </div>
        """, unsafe_allow_html=True)
        cols = st.columns(4)
        for idx, agent in enumerate(review.get("reviews", [])[:4]):
            with cols[idx]:
                st.markdown(f"""
                <div class="detail-card">
                  <div class="section-badge">{esc(agent.get("agent", ""))}</div>
                  <div style="font-size:2rem; font-family:'Playfair Display',serif; color:var(--accent);">{int(agent.get("score", 0))}</div>
                  <div style="color:var(--text-secondary); font-size:0.9rem; line-height:1.4;">{esc(agent.get("verdict", ""))}</div>
                </div>
                """, unsafe_allow_html=True)
    elif st.session_state.get("agent_review_error"):
        st.warning(f"AI Agent Review indisponivel. Podes continuar apenas com ATS. Detalhe: {st.session_state.agent_review_error}")

    st.markdown("<br>", unsafe_allow_html=True)
    _, btn_col, _ = st.columns([1, 1, 1])
    with btn_col:
        if st.button("Ver CV Optimizado", type="primary", use_container_width=True):
            for key in ("final_markdown", "pdf_bytes", "pdf_hash"):
                st.session_state.pop(key, None)
            st.session_state.wizard_step = 6
            st.rerun()


if st.session_state.wizard_step == 6:
    if st.session_state.get("final_markdown"):
        st.session_state.wizard_step = 7
        st.rerun()

    if not has_unlock_access():
        render_unlock_cta()
        st.stop()

    with st.spinner("A reescrever o teu CV para passar no ATS..."):
        try:
            data = call_api(
                "/api/optimize",
                {
                    "cv": st.session_state.cv_content,
                    "job": st.session_state.job_content,
                    "ats": st.session_state.ats_data or {},
                    "context": current_context(),
                    "agent_review": st.session_state.agent_review,
                    "language": st.session_state.output_language,
                },
            )
            st.session_state.final_markdown = data["markdown"]
            if data.get("credits_remaining") is not None:
                st.session_state.credits_remaining = data["credits_remaining"]
            st.session_state.pop("pdf_bytes", None)
            st.session_state.pop("pdf_hash", None)
            st.session_state.wizard_step = 7
            st.rerun()
        except Exception as e:
            st.error(f"Erro na geracao: {e}")
            if st.button("Tentar Novamente"):
                st.rerun()
            st.stop()


if st.session_state.wizard_step == 7:
    st.markdown("<div class='section-badge'>CV FINALIZADO</div>", unsafe_allow_html=True)
    st.markdown("<h2 style='margin-bottom: 24px;'>Download do Documento</h2>", unsafe_allow_html=True)
    st.caption(f"Idioma do CV: {output_language_label()}")

    if not st.session_state.get("pdf_bytes"):
        try:
            data = call_api(
                "/api/generate-cv",
                {
                    "markdown": st.session_state.final_markdown,
                    "language": st.session_state.output_language,
                },
            )
            st.session_state.pdf_bytes = base64.b64decode(data["pdf_base64"])
        except Exception as e:
            st.error(f"Erro ao gerar PDF: {e}")
            st.stop()

    d1, d2, d3 = st.columns([1, 1, 1])
    with d1:
        st.download_button(
            "Descarregar PDF (Harvard)",
            data=st.session_state.pdf_bytes,
            file_name="Optimized_CV.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True,
        )
    with d2:
        st.download_button(
            "Descarregar Markdown",
            data=st.session_state.final_markdown.encode("utf-8"),
            file_name="CV.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with d3:
        if st.button("Analisar Novo CV", use_container_width=True):
            reset_session()
            st.rerun()

    with st.expander("Pre-visualizar CV Gerado", expanded=True):
        st.markdown(st.session_state.final_markdown)
