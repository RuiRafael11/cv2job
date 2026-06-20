import hashlib

import streamlit as st

from config import DERIVED_KEYS, SESSION_KEYS


def inputs_fingerprint(cv: str, job: str) -> str:
    return hashlib.sha256(f"{cv}|{job}".encode()).hexdigest()


def sync_inputs_and_invalidate(cv, job) -> None:
    if not cv or not job:
        return
    fp = inputs_fingerprint(cv, job)
    if st.session_state.get("inputs_fp") != fp:
        for key in DERIVED_KEYS:
            st.session_state.pop(key, None)
        st.session_state.inputs_fp = fp


def reset_session(keep_auth=True) -> None:
    auth_values = {}
    if keep_auth:
        auth_values = {
            "api_base_url": st.session_state.get("api_base_url", "http://127.0.0.1:8000"),
            "backend_session_token": st.session_state.get("backend_session_token", ""),
            "paid_email": st.session_state.get("paid_email", ""),
            "credits_remaining": st.session_state.get("credits_remaining"),
            "login_email": st.session_state.get("login_email", ""),
        }
    for key in SESSION_KEYS:
        st.session_state.pop(key, None)
    for key, value in auth_values.items():
        st.session_state[key] = value


def init_session_state() -> None:
    defaults = [
        ("wizard_step", 0),
        ("q1_answer", None),
        ("q2_answer", None),
        ("q3_answer", None),
        ("jd_text_pasted", ""),
        ("suggestions", []),
        ("ats_data", None),
        ("agent_review", None),
        ("agent_review_error", ""),
        ("final_markdown", ""),
        ("cv_content", None),
        ("job_content", None),
        ("api_base_url", "http://127.0.0.1:8000"),
        ("backend_session_token", ""),
        ("paid_email", ""),
        ("login_email", ""),
        ("output_language", "en"),
        ("checkout_session_id", ""),
        ("exchanged_checkout_session_id", ""),
        ("checkout_url", ""),
        ("credits_remaining", None),
        ("pdf_bytes", None),
        ("pdf_hash", None),
        ("inputs_fp", None),
    ]
    for key, default in defaults:
        if key not in st.session_state:
            st.session_state[key] = default
