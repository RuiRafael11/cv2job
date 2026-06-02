import streamlit as st
from google import genai
from google.genai import types
import os
import io
import json
import re
import datetime
from docx import Document
import PyPDF2
from fpdf import FPDF

# --- Funções de Leitura e Arquivo ---
def read_file_content(filepath):
    try:
        if filepath.endswith('.txt') or filepath.endswith('.md'):
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        elif filepath.endswith('.pdf'):
            with open(filepath, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = ""
                for page_num in range(len(reader.pages)):
                    text += reader.pages[page_num].extract_text()
                return text
        elif filepath.endswith('.docx'):
            document = Document(filepath)
            text = ""
            for paragraph in document.paragraphs:
                text += paragraph.text + "\n"
            return text
        return None
    except Exception as e:
        st.error(f"Error reading file {filepath}: {e}")
        return None

def read_uploaded(uploaded_file):
    if uploaded_file is None:
        return None
    bytes_data = uploaded_file.getvalue()
    filename = uploaded_file.name.lower()
    try:
        if filename.endswith('.txt') or filename.endswith('.md'):
            return bytes_data.decode('utf-8')
        elif filename.endswith('.pdf'):
            reader = PyPDF2.PdfReader(io.BytesIO(bytes_data))
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return text
        elif filename.endswith('.docx'):
            document = Document(io.BytesIO(bytes_data))
            text = ""
            for paragraph in document.paragraphs:
                text += paragraph.text + "\n"
            return text
        return None
    except Exception as e:
        st.error(f"Error reading uploaded file {uploaded_file.name}: {e}")
        return None

# --- Gerador de PDF Estilo Harvard ---
class HarvardPDF(FPDF):
    def header(self):
        pass
    def footer(self):
        pass

def convert_markdown_to_harvard_pdf(md_text):
    replacements = {
        'č': 'c', 'ć': 'c', 'ž': 'z', 'š': 's', 'đ': 'd',
        'Č': 'C', 'Ć': 'C', 'Ž': 'Z', 'Š': 'S', 'Đ': 'D',
        'ł': 'l', 'ą': 'a', 'ę': 'e', 'ó': 'o', 'ś': 's', 'ź': 'z', 'ż': 'z',
        'Ł': 'L', 'Ą': 'A', 'Ę': 'E', 'Ó': 'O', 'Ś': 'S', 'Ź': 'Z', 'Ż': 'Z',
        '–': '-', '—': '-', 
        '“': '"', '”': '"', 
        '‘': "'", '’': "'"
    }
    
    for unicode_char, ascii_char in replacements.items():
        md_text = md_text.replace(unicode_char, ascii_char)
    
    pdf = HarvardPDF()
    pdf.add_page()
    
    # Reduzi ligeiramente as margens superiores/inferiores para forçar tudo a caber em 1 página (Padrão Harvard)
    pdf.set_margins(15, 12, 15)
    pdf.set_auto_page_break(auto=True, margin=12)
    
    pdf.set_font("Times", size=10)
    lines = md_text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            pdf.ln(1.2) # Ajuste fino de espaçamento vertical
            continue
            
        line = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', line)
        
        if not (line.startswith('* ') or line.startswith('- ')):
            pdf.set_x(15)
        
        # Título Principal (Nome)
        if line.startswith('# '):
            name = line.replace('# ', '').replace('**', '').replace('*', '')
            pdf.set_font("Times", "B", size=15)
            pdf.cell(180, 6, name, align='C')
            pdf.ln(6)
            
        # Cabeçalhos Principais (TECHNICAL EXPERIENCE, ADDITIONAL EXPERIENCE, etc.)
        elif line.startswith('## '):
            section = line.replace('## ', '').replace('**', '').replace('*', '').upper()
            pdf.ln(2.5)
            pdf.set_font("Times", "B", size=10)
            pdf.cell(180, 4, section)
            pdf.ln(4)
            y = pdf.get_y()
            pdf.line(15, y, 195, y)
            pdf.ln(1)
            
        # Subcabeçalhos (Cargos, Empresas e Datas)
        elif line.startswith('### '):
            sub = line.replace('### ', '').replace('**', '').replace('*', '')
            pdf.set_font("Times", "B", size=9)
            pdf.cell(180, 4, sub)
            pdf.ln(4)
            
        # Bullet Points
        elif line.startswith('* ') or line.startswith('- '):
            bullet_text = line[2:].replace('**', '').replace('*', '').replace('`', '')
            pdf.set_font("Times", size=9)
            pdf.set_x(20)
            pdf.cell(4, 3.8, "-", ln=False) 
            pdf.multi_cell(171, 3.8, bullet_text)
            pdf.set_x(15)
            
        # Texto Normal / Contactos
        else:
            clean_normal = line.replace('**', '').replace('*', '').replace('`', '')
            pdf.set_font("Times", size=9)
            
            # Detect clickable github.com / linkedin.com URLs
            url_pattern = re.compile(r'((?:https?://)?(?:www\.)?(?:github\.com|linkedin\.com)[^\s|]*)', re.IGNORECASE)
            has_url = url_pattern.search(clean_normal)
            
            if '|' in clean_normal:
                if has_url:
                    # Split into text and URL segments, then center-render manually
                    segments = re.split(r'((?:https?://)?(?:www\.)?(?:github\.com|linkedin\.com)[^\s|]*)', clean_normal, flags=re.IGNORECASE)
                    total_w = sum(pdf.get_string_width(seg) for seg in segments if seg)
                    start_x = 15 + (180 - total_w) / 2
                    pdf.set_x(start_x)
                    for seg in segments:
                        if not seg:
                            continue
                        if url_pattern.fullmatch(seg):
                            url = seg if seg.startswith('http') else f'https://{seg}'
                            pdf.set_text_color(17, 85, 204)
                            pdf.cell(pdf.get_string_width(seg), 3.5, seg, link=url)
                            pdf.set_text_color(0, 0, 0)
                        else:
                            pdf.cell(pdf.get_string_width(seg), 3.5, seg)
                    pdf.ln(3.5)
                else:
                    pdf.cell(180, 3.5, clean_normal, align='C')
                    pdf.ln(3.5)
            else:
                if has_url:
                    # Render URL as a clickable blue hyperlink
                    m = has_url
                    pre = clean_normal[:m.start()]
                    raw_url = m.group(0)
                    url = raw_url if raw_url.startswith('http') else f'https://{raw_url}'
                    post = clean_normal[m.end():]
                    if pre:
                        pdf.multi_cell(180, 3.8, pre)
                        pdf.set_x(15)
                    pdf.set_text_color(17, 85, 204)
                    pdf.cell(pdf.get_string_width(raw_url), 3.8, raw_url, link=url)
                    pdf.set_text_color(0, 0, 0)
                    pdf.ln(3.8)
                    if post:
                        pdf.set_x(15)
                        pdf.multi_cell(180, 3.8, post)
                        pdf.set_x(15)
                else:
                    pdf.multi_cell(180, 3.8, clean_normal)
                    pdf.set_x(15)
    return bytes(pdf.output())
# --- Configuração do Streamlit ---
st.set_page_config(layout="wide", page_title="ATS AI Resume Optimizer")
st.title("Harvard-Style ATS Resume Optimizer")

if "step" not in st.session_state:
    st.session_state.step = 0
if "suggestions" not in st.session_state:
    st.session_state.suggestions = []
if "ats_data" not in st.session_state:
    st.session_state.ats_data = None
if "ats_shown" not in st.session_state:
    st.session_state.ats_shown = False

# --- Sidebar de Configuração (CORRIGIDA) ---
st.sidebar.header("Configuration")
google_api_key = st.sidebar.text_input("Google AI Studio API Key", type="password")

# Dicionário que mapeia o nome bonito para o ID real que a API exige
model_mapping = {
    "Gemini 3 Flash (Disponível!)": "gemini-3.0-flash",
    "Gemini 3.5 Flash (Disponível!)": "gemini-3.5-flash",
    "Gemma 4 31B": "gemma-4-31b-it",
    "Gemma 4 26B": "gemma-4-26b-it",
    "Gemini 2.5 Flash (Esgotado)": "gemini-2.5-flash"
}

selected_model_label = st.sidebar.selectbox(
    "Select Model Version:",
    options=list(model_mapping.keys()),
    help="Se um modelo der erro de limite, mude para o Gemini 3 ou Gemma 4."
)

# Resgata o ID correto para enviar à API
selected_model = model_mapping[selected_model_label]

st.sidebar.markdown("""
Connects to Google AI Studio API models.
""")

# --- Main Application Logic ---
st.subheader("1. Upload Files")
col1, col2 = st.columns(2)
with col1:
    cv_file = st.file_uploader("Upload your CV", type=["pdf", "docx", "txt", "md"], key="cv_uploader")
with col2:
    jd_file = st.file_uploader("Upload Job Description", type=["txt", "md", "pdf"], key="jd_uploader")

if cv_file is None or jd_file is None:
    st.warning('Please upload both files to continue.')
    st.stop()

resume_content = read_uploaded(cv_file)
job_content = read_uploaded(jd_file)
st.session_state.cv_content = resume_content
st.session_state.job_content = job_content

# --- PASSO 0: ATS Score Dashboard ---
if st.session_state.step == 0:
    if st.button("📊 Calculate ATS Score"):
        if not google_api_key:
            st.error("Please enter your API Key.")
        else:
            with st.spinner("Analyzing ATS compatibility..."):
                try:
                    client = genai.Client(api_key=google_api_key)

                    ats_prompt = f"""
                    You are an expert ATS (Applicant Tracking System) evaluator. Analyze the provided resume against the job description.

                    Evaluate and return:
                    1. An overall compatibility score from 0 to 100.
                    2. A list of keywords present in the CV that the job requires.
                    3. A list of important keywords missing from the CV.
                    4. Per-section scores for Skills, Experience, and Education, each from 0 to 10.
                    5. A one-line diagnostic sentence summarizing the main weakness.

                    You MUST reply ONLY with a JSON object matching this structure:
                    {{
                        "overall_score": <int>,
                        "keywords_present": ["..."],
                        "keywords_missing": ["..."],
                        "section_scores": {{
                            "skills": <int>,
                            "experience": <int>,
                            "education": <int>
                        }},
                        "diagnostic": "..."
                    }}

                    Resume: {resume_content}
                    Job Description: {job_content}
                    """

                    response = client.models.generate_content(
                        model=selected_model,
                        contents=ats_prompt,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            temperature=0.2
                        )
                    )

                    data = json.loads(response.text)
                    st.session_state.ats_data = data
                except Exception as e:
                    st.error(f"ATS analysis failed with model {selected_model}: {e}")

    if st.session_state.ats_data is not None:
        ats_data = st.session_state.ats_data
        overall = int(ats_data.get("overall_score", 0))
        present = ats_data.get("keywords_present", [])
        missing = ats_data.get("keywords_missing", [])
        sections = ats_data.get("section_scores", {})
        diagnostic = ats_data.get("diagnostic", "")

        st.write("---")
        st.subheader("📊 ATS Score Dashboard")

        c1, c2 = st.columns([1, 2])
        with c1:
            st.metric("Overall Compatibility", f"{overall}/100")
            st.progress(overall / 100.0)
        with c2:
            st.info(f"💡 **Diagnostic:** {diagnostic}")

        st.write("### Per-Section Scores")
        scols = st.columns(3)
        sec_info = [("skills", "Skills"), ("experience", "Experience"), ("education", "Education")]
        for idx, (key, label) in enumerate(sec_info):
            s_score = int(sections.get(key, 0))
            with scols[idx]:
                st.metric(label, f"{s_score}/10")
                st.progress(s_score / 10.0)

        st.write("---")
        st.write("### Keyword Analysis")
        kc1, kc2 = st.columns(2)
        with kc1:
            st.success("✅ Present in CV")
            for kw in present:
                st.write(f"- {kw}")
            if not present:
                st.caption("No matching keywords detected")
        with kc2:
            st.error("❌ Missing from CV")
            for kw in missing:
                st.write(f"- {kw}")
            if not missing:
                st.caption("No missing keywords detected")

        if st.button("🚀 Optimize CV"):
            st.session_state.step = 1
            st.rerun()

# --- PASSO 1: Analyze Job Gaps & Suggest Skills ---
if st.session_state.step == 1:
    if st.button("🔍 Analyze Job Gaps & Suggest Skills"):
        if not google_api_key:
            st.error("Please enter your API Key.")
        else:
            with st.spinner("Analyzing requirements..."):
                try:
                    client = genai.Client(api_key=google_api_key)

                    analysis_prompt = f"""
                    Analyze this Job Description and Candidate Resume. Identify key skills or framing phrases requested by the job that are missing or weak in the resume.
                    Provide exactly 4 to 6 specific recommendations of technical skills, methodologies, or adaptations (e.g., "TypeScript (AI-Assisted / Fast Learner)" or "React (Web Architecture Foundations)").

                    You MUST reply ONLY with a JSON object matching this structure:
                    {{
                        "suggestions": [
                            "Skill or Adaptation Phrase 1",
                            "Skill or Adaptation Phrase 2"
                        ]
                    }}

                    Resume: {resume_content}
                    Job: {job_content}
                    """

                    response = client.models.generate_content(
                        model=selected_model,
                        contents=analysis_prompt,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            temperature=0.2
                        )
                    )

                    data = json.loads(response.text)
                    st.session_state.suggestions = data.get("suggestions", [])
                    st.session_state.step = 2
                    st.rerun()
                except Exception as e:
                    st.error(f"Analysis failed com o modelo {selected_model}: {e}")

# --- PASSO 2: Checkboxes Interativas ---
if st.session_state.step >= 2:
    st.write("---")
    st.subheader("2. Select the Skills & Adaptations to include:")
    st.info("We identified these gaps based on KIME's requirements. Uncheck what you don't want.")
    
    selected_options = []
    for i, suggestion in enumerate(st.session_state.suggestions):
        is_checked = st.checkbox(suggestion, value=True, key=f"suggest_{i}")
        if is_checked:
            selected_options.append(suggestion)
            
    if st.button("🚀 Generate Final Harvard CV & PDF"):
        with st.spinner(f"Writing full optimized resume using {selected_model_label}..."):
            try:
                client = genai.Client(api_key=google_api_key)
                
                current_year = datetime.date.today().year

                system_prompt = f"""
                You are an expert HR and ATS professional. Rewrite the candidate's resume completely to match the job description.
                Incorporate the user-approved extra skills/phrases naturally into the Skills or Summary sections.

                CRITICAL INSTRUCTION: You must output the ENTIRE resume from top to bottom. Do not truncate, do not skip sections, and do not leave placeholders. Write every single section completely (Summary, Skills, Experience, Education, Languages).

                GRADUATION YEAR RULE: If the candidate's degree end year is {current_year} or any past year, never write it as a range implying ongoing study. Write it as a single completed year, e.g. {current_year}, never "2022–{current_year}" if graduation has already occurred.

                NON-TECHNICAL EXPERIENCE RULE: If the candidate has non-technical work experience (retail, hospitality, sales), condense it to a single bullet point maximum. Prioritize technical and academic experience above all else.

                TYPESCRIPT FRAMING RULE: Never use the word 'transitioning' or 'learning' for TypeScript. If TypeScript is listed as a skill being developed, frame it as: TypeScript (Strong JS Foundation | Actively Proficient).

                Output ONLY the final resume in clean Markdown. Start directly with '# Name'. Do not include conversational text, introduction, or markdown block wrappers.
                """
                
                final_user_prompt = f"""
                Original Resume: {resume_content}
                Target Job Description: {job_content}
                
                Approved skills/phrases to definitely include:
                {", ".join(selected_options)}
                """
                
                response = client.models.generate_content(
                    model=selected_model,
                    contents=final_user_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        temperature=0.4,
                        max_output_tokens=4000
                    )
                )
                
                st.session_state.final_markdown = response.text
                st.session_state.step = 3
            except Exception as e:
                st.error(f"Generation failed com o modelo {selected_model}: {e}")

# --- PASSO 3: Exibição e Download do PDF Harvard ---
if st.session_state.step == 3:
    st.write("---")
    st.subheader("3. Final Optimized Resume")
    
    pdf_data = convert_markdown_to_harvard_pdf(st.session_state.final_markdown)
    
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="📥 Download Harvard-Style PDF",
            data=pdf_data,
            file_name="Harvard_Optimized_Resume.pdf",
            mime="application/pdf"
        )
    with col2:
        st.download_button(
            label="📥 Download Markdown Version",
            data=st.session_state.final_markdown.encode('utf-8'),
            file_name="optimized_resume.md",
            mime="text/markdown"
        )
        
    st.markdown(st.session_state.final_markdown)
    
    if st.button("🔄 Restart Process"):
        st.session_state.step = 0
        st.session_state.suggestions = []
        st.session_state.ats_data = None
        st.rerun()
