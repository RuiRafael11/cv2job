import io

import PyPDF2
from docx import Document


def read_uploaded(uploaded_file):
    if uploaded_file is None:
        return None
    bytes_data = uploaded_file.getvalue()
    filename = uploaded_file.name.lower()
    try:
        if filename.endswith((".txt", ".md")):
            return bytes_data.decode("utf-8")
        if filename.endswith(".pdf"):
            reader = PyPDF2.PdfReader(io.BytesIO(bytes_data))
            return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
        if filename.endswith(".docx"):
            document = Document(io.BytesIO(bytes_data))
            return "\n".join(p.text for p in document.paragraphs)
    except Exception:
        return None
    return None
