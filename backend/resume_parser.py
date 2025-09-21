# resume_parser.py
import fitz  # PyMuPDF
import docx2txt
import re

def extract_text_from_pdf(path: str) -> str:
    """Extract text from PDF using PyMuPDF."""
    doc = fitz.open(path)
    text_parts = []
    for page in doc:
        text_parts.append(page.get_text())
    return "\n".join(text_parts)

def extract_text_from_docx(path: str) -> str:
    """Extract text from DOCX using docx2txt."""
    return docx2txt.process(path) or ""

def extract_text(path: str) -> str:
    """Detect file type and extract text."""
    if path.lower().endswith(".pdf"):
        return extract_text_from_pdf(path)
    elif path.lower().endswith((".docx", ".doc")):
        return extract_text_from_docx(path)
    else:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            return ""

def normalize_text(text: str) -> str:
    """Clean extra spaces and newlines."""
    text = re.sub(r'\r\n', '\n', text)
    text = re.sub(r'\n{2,}', '\n\n', text)
    return text.strip()

import re

def extract_skills_from_resume(resume_text: str) -> list:
    """
    Extract common technical skills from resume text.
    (Simple keyword-based approach; can be expanded later)
    """
    # Define a simple skill set (expandable)
    skills = [
        "Python", "Java", "C++", "SQL", "R", "Tableau", "Power BI",
        "Machine Learning", "Deep Learning", "NLP", "React", "Node.js",
        "Excel", "Git", "Docker", "Kubernetes", "Pandas", "NumPy",
        "Matplotlib", "Scikit-learn", "TensorFlow", "PyTorch"
    ]

    found = []
    text_lower = resume_text.lower()

    for skill in skills:
        if skill.lower() in text_lower:
            found.append(skill)

    return sorted(set(found))
