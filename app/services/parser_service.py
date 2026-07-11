import re
from pathlib import Path

import fitz
from docx import Document


class ResumeParsingError(Exception):
    """Raised when resume text extraction fails."""
    pass


BULLET_PATTERN = re.compile(
    r"^\s*[\u2022\u25cf\u25aa\u25e6\uf0b7]\s*"
)


def normalize_bullet(line: str) -> str:
    """
    Normalize supported bullet symbols to a canonical bullet marker.
    """
    if BULLET_PATTERN.match(line):
        content = BULLET_PATTERN.sub("", line).strip()

        if content:
            return f"• {content}"

    return line


def repair_hyphenated_line_breaks(text: str) -> str:
    """
    Repair words split across PDF line boundaries.

    Examples:
        closed-\nloop -> closed-loop
        re-\nquirements -> requirements
    """

    def replace_match(match):
        first_part = match.group(1)
        second_part = match.group(2)

        combined = first_part + second_part

        common_prefixes = {
            "anti",
            "auto",
            "co",
            "de",
            "dis",
            "en",
            "ex",
            "in",
            "inter",
            "mis",
            "non",
            "over",
            "pre",
            "pro",
            "re",
            "sub",
            "trans",
            "un",
            "under",
        }

        if first_part.lower() in common_prefixes:
            return combined

        return f"{first_part}-{second_part}"

    return re.sub(
        r"\b([A-Za-z]+)-\s*\n\s*([a-z][A-Za-z]*)\b",
        replace_match,
        text,
    )


def normalize_text(text: str) -> str:
    """
    Normalize extracted resume text while preserving line structure.
    """
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = repair_hyphenated_line_breaks(text)

    normalized_lines = []

    for line in text.splitlines():
        cleaned_line = re.sub(r"[ \t]+", " ", line).strip()

        if not cleaned_line:
            continue

        cleaned_line = normalize_bullet(cleaned_line)
        normalized_lines.append(cleaned_line)

    return "\n".join(normalized_lines)


def extract_pdf_text(file_path: str) -> str:
    """
    Extract visible text and embedded HTTP/HTTPS hyperlinks from a PDF.
    """
    try:
        extracted_parts = []
        embedded_urls = []
        seen_urls = set()

        with fitz.open(file_path) as document:
            for page in document:
                page_text = page.get_text()

                if page_text:
                    extracted_parts.append(page_text)

                for link in page.get_links():
                    uri = link.get("uri")

                    if not uri:
                        continue

                    uri = uri.strip()

                    if not uri.lower().startswith(
                        ("http://", "https://")
                    ):
                        continue

                    if uri in seen_urls:
                        continue

                    seen_urls.add(uri)
                    embedded_urls.append(uri)

        if embedded_urls:
            extracted_parts.append(
                "\n".join(embedded_urls)
            )

        return "\n".join(extracted_parts)

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
