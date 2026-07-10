import re
from pathlib import Path

import fitz
from docx import Document


class ResumeParsingError(Exception):
    """Raised when resume text extraction fails."""
    pass


def normalize_text(text: str) -> str:
    """
    Normalize extracted resume text while preserving line structure.
    """
    lines = []

    for line in text.splitlines():
        cleaned_line = re.sub(r"[ \t]+", " ", line).strip()

        if cleaned_line:
            lines.append(cleaned_line)

    return "\n".join(lines)


def extract_pdf_text(file_path: str) -> str:
    try:
        with fitz.open(file_path) as document:
            text = "\n".join(
                page.get_text()
                for page in document
            )

        return text

    except Exception as exc:
        raise ResumeParsingError(
            f"Failed to extract text from PDF: {exc}"
        ) from exc


def extract_docx_text(file_path: str) -> str:
    try:
        document = Document(file_path)

        text = "\n".join(
            paragraph.text
            for paragraph in document.paragraphs
        )

        return text

    except Exception as exc:
        raise ResumeParsingError(
            f"Failed to extract text from DOCX: {exc}"
        ) from exc


def parse_resume(file_path: str) -> str:
    path = Path(file_path)

    if not path.exists():
        raise ResumeParsingError(
            f"Resume file not found: {file_path}"
        )

    extension = path.suffix.lower()

    if extension == ".pdf":
        raw_text = extract_pdf_text(file_path)

    elif extension == ".docx":
        raw_text = extract_docx_text(file_path)

    else:
        raise ResumeParsingError(
            f"Unsupported file type: {extension}"
        )

    cleaned_text = normalize_text(raw_text)

    if not cleaned_text:
        raise ResumeParsingError(
            "No extractable text found in resume."
        )

    return cleaned_text
