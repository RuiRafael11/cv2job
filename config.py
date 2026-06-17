SECTION_CAPS = {
    "requirements": 40,
    "experience": 30,
    "terms": 20,
    "education": 10,
}

SESSION_KEYS = (
    "wizard_step", "q1_answer", "q2_answer", "q3_answer", "jd_text_pasted",
    "suggestions", "ats_data", "final_markdown", "cv_content", "job_content",
    "api_base_url", "backend_session_token", "paid_email", "login_email",
    "checkout_session_id", "exchanged_checkout_session_id", "checkout_url", "credits_remaining",
    "pdf_bytes", "pdf_hash", "inputs_fp",
)

DERIVED_KEYS = ("ats_data", "final_markdown", "pdf_bytes", "pdf_hash")

WIZARD_QUESTIONS = [
    {
        "tag": "PASSO 1",
        "title": "Estás a ser chamado para entrevistas?",
        "subtitle": "A tua taxa de resposta ajuda a calibrar a agressividade da optimização.",
        "var": "q1_answer",
        "options": [
            {"title": "Quase nunca", "desc": "Raramente recebo respostas ou convites.", "val": "Quase nunca"},
            {"title": "Às vezes", "desc": "Recebo algumas respostas, mas poderia ser melhor.", "val": "Às vezes"},
            {"title": "Com frequência", "desc": "Tenho entrevistas regulares, quero optimizar mais.", "val": "Com frequência"},
        ],
    },
    {
        "tag": "PASSO 2",
        "title": "Qual é o teu objetivo principal?",
        "subtitle": "Queremos personalizar as sugestões ao teu momento de carreira.",
        "var": "q2_answer",
        "options": [
            {"title": "Primeiro emprego", "desc": "Estou a começar e preciso de destacar potencial.", "val": "Primeiro emprego"},
            {"title": "Mudar de empresa", "desc": "Quero dar o próximo passo na trajetória.", "val": "Mudar empresa"},
            {"title": "Melhorar o CV atual", "desc": "Tenho experiência, quero um CV mais forte.", "val": "Melhorar CV atual"},
        ],
    },
    {
        "tag": "PASSO 3",
        "title": "Que tipo de vaga procuras?",
        "subtitle": "O nível de senioridade altera os pesos da análise ATS.",
        "var": "q3_answer",
        "options": [
            {"title": "Estágio / Junior", "desc": "Exigem menos experiência e mais formação.", "val": "Estágio / Junior"},
            {"title": "Pleno / Sénior", "desc": "Focam-se em resultados e stack técnica.", "val": "Pleno / Sénior"},
            {"title": "Sem vaga específica", "desc": "Quero um CV generalista forte.", "val": "Sem vaga específica"},
        ],
    },
]
