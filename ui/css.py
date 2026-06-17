import streamlit as st


def inject_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=Inter:wght@300;400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

    :root {
        --bg-primary: #09090b;
        --bg-card: #18181b;
        --bg-card-hover: #27272a;
        --border: #27272a;
        --accent: #818cf8;
        --accent-light: #a5b4fc;
        --success: #34d399;
        --warning: #fbbf24;
        --danger: #f87171;
        --text-primary: #fafafa;
        --text-secondary: #a1a1aa;
        --text-muted: #52525b;
    }

    html, body, [class*="css-"] { font-family: 'Inter', sans-serif !important; color: var(--text-primary) !important; }
    .stApp { background: var(--bg-primary) !important; }
    h1, h2, h3, h4 { font-family: 'Playfair Display', serif !important; color: var(--text-primary) !important; font-weight: 400 !important; letter-spacing: -0.02em; }

    .stButton > button {
        background: var(--bg-card) !important; color: var(--text-primary) !important;
        border-radius: 12px !important; border: 1px solid var(--border) !important;
        padding: 14px 20px !important; transition: all 0.2s ease !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.2) !important; width: 100% !important;
    }
    .stButton > button:hover {
        border-color: var(--accent) !important; background: var(--bg-card-hover) !important;
        transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0,0,0,0.4) !important;
    }
    button[data-testid="baseButton-primary"] {
        background: var(--accent) !important; color: #fff !important; font-weight: 500 !important; border: none !important;
        box-shadow: 0 4px 14px rgba(129, 140, 248, 0.3) !important;
    }
    button[data-testid="baseButton-primary"]:hover { background: #6366f1 !important; transform: translateY(-2px); }

    .detail-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 16px; padding: 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.2); height: 100%; }
    .section-badge { font-family: 'IBM Plex Mono', monospace; font-size: 0.7rem; font-weight: 600; color: var(--accent); text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 12px; }
    .keyword-tag-present { display: inline-block; background: rgba(52, 211, 153, 0.1); color: var(--success); border: 1px solid rgba(52, 211, 153, 0.2); border-radius: 6px; padding: 4px 10px; font-size: 0.8rem; margin: 3px; font-family: 'IBM Plex Mono', monospace; }
    .keyword-tag-missing { display: inline-block; background: rgba(248, 113, 113, 0.1); color: var(--danger); border: 1px solid rgba(248, 113, 113, 0.2); border-radius: 6px; padding: 4px 10px; font-size: 0.8rem; margin: 3px; font-family: 'IBM Plex Mono', monospace; }
    .next-step-block { background: var(--bg-card); border: 1px solid var(--border); border-radius: 14px; padding: 22px 26px; margin-bottom: 14px; }
    .impact-badge { font-family: 'IBM Plex Mono', monospace; font-size: 0.65rem; padding: 4px 10px; border-radius: 6px; font-weight: 600; margin-left: 10px; text-transform: uppercase; }
    .impact-high { background: rgba(52, 211, 153, 0.15); color: var(--success); border: 1px solid rgba(52, 211, 153, 0.3); }
    .impact-medium { background: rgba(251, 191, 36, 0.15); color: var(--warning); border: 1px solid rgba(251, 191, 36, 0.3); }

    .progress-track { width: 100%; height: 6px; background: var(--bg-primary); border-radius: 3px; overflow: hidden; margin-top: 12px; border: 1px solid var(--border); }
    .progress-fill { height: 100%; border-radius: 3px; transition: width 0.8s ease-out; }

    .wizard-progress { width: 100%; height: 3px; background: var(--border); border-radius: 3px; margin-bottom: 0; overflow: hidden; }
    .wizard-progress-bar { height: 100%; background: var(--accent); border-radius: 3px; transition: width 0.4s ease; }
    .wizard-step-indicator { font-family: 'IBM Plex Mono', monospace; font-size: 0.8rem; color: var(--text-muted); text-align: center; margin-top: 8px; letter-spacing: 1px; }

    .stTextArea textarea { background: var(--bg-primary) !important; border: 1px solid var(--border) !important; border-radius: 8px !important; color: var(--text-primary) !important; }
    .stTextArea textarea:focus { border-color: var(--accent) !important; box-shadow: none !important; }
    .stFileUploader>div { background: var(--bg-primary) !important; border: 1px dashed var(--border) !important; border-radius: 12px !important; }

    .stDeployButton, header[data-testid="stHeader"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)
