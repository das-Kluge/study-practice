import pdfplumber
from docx import Document
from pathlib import Path

def extract_text_from_file(file_path: Path) -> list[str]:
    ext = file_path.suffix.lower()
    if ext == ".pdf":
        return _extract_pdf(file_path)
    elif ext == ".docx":
        return [_extract_docx(file_path)]
    else:
        raise ValueError("Unsupported file format")

def _extract_pdf(file_path: Path) -> list[str]:
    pages = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            pages.append(text)
    return pages

def _extract_docx(file_path: Path) -> str:
    doc = Document(file_path)
    full_text = "\n".join([para.text for para in doc.paragraphs])
    return full_text