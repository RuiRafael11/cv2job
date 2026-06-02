# Harvard-Style ATS Resume Optimizer

A powerful Streamlit application that helps job seekers optimize their resumes for Applicant Tracking Systems (ATS) and generate professional Harvard-style PDFs. Upload your CV and a job description, get an ATS compatibility score with keyword analysis, identify skill gaps, and receive AI-powered suggestions to tailor your resume — then download the final result as a polished one-page Harvard-format PDF.

## Features

- **ATS Score Dashboard** — Calculates an overall compatibility score (0–100) plus per-section scores for Skills, Experience, and Education.
- **Keyword Analysis** — Shows which required keywords are present in your CV and which are missing.
- **Gap Analysis & Skill Suggestions** — Uses Google AI Studio (Gemini) to identify missing skills and proposes actionable adaptations.
- **Interactive Selection** — Choose which AI-suggested skills and framing phrases to include in your optimized resume.
- **Harvard-Style PDF Export** — Generates a clean, one-page Harvard-format PDF with clickable hyperlinks and proper character encoding.
- **Markdown Export** — Download the optimized resume in Markdown for further editing.
- **Privacy-First API Handling** — Your Google AI Studio API key is entered at runtime via a password-protected input and never hardcoded.

## Installation

1. Clone the repository and navigate into the project folder:
   ```bash
   git clone https://github.com/RuiRafael11/cv2job.git
   cd cv2job
   ```

2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS / Linux
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Start the Streamlit app:
   ```bash
   streamlit run app.py
   ```

2. In the sidebar, enter your **Google AI Studio API Key**.

3. Select a Gemini model version (e.g., Gemini 3 Flash, Gemini 3.5 Flash, or Gemma 4).

4. Upload your **CV** (PDF, DOCX, TXT, or MD) and the **Job Description** (TXT, MD, or PDF).

5. Click **"Calculate ATS Score"** to view your dashboard.

6. Click **"Optimize CV"** to run the gap analysis and generate tailored skill suggestions.

7. Select which suggestions to include, then click **"Generate Final Harvard CV & PDF"**.

8. Download your optimized resume as a **Harvard-style PDF** or **Markdown** file.

## Environment Variables

You can optionally set your API key as an environment variable instead of entering it in the UI each time. Copy `.env.example` to `.env` and fill in your key:

```bash
cp .env.example .env
```

**`.env.example` contents:**
```
GOOGLE_API_KEY=
```

## Screenshot

<!-- Replace the placeholder below with an actual screenshot of the app -->
![App Screenshot](docs/screenshot.png)

## License

MIT
