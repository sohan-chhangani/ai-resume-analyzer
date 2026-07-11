from typing import Dict, Optional


SECTION_ALIASES = {
    "SUMMARY": "professional_summary",
    "PROFESSIONAL SUMMARY": "professional_summary",
    "PROFILE": "professional_summary",
    "PROFESSIONAL PROFILE": "professional_summary",

    "SKILLS": "technical_skills",
    "TECHNICAL SKILLS": "technical_skills",
    "CORE SKILLS": "technical_skills",
    "KEY SKILLS": "technical_skills",

    "EXPERIENCE": "professional_experience",
    "WORK EXPERIENCE": "professional_experience",
    "PROFESSIONAL EXPERIENCE": "professional_experience",
    "EMPLOYMENT HISTORY": "professional_experience",

    "EDUCATION": "education",
    "ACADEMIC BACKGROUND": "education",
    "ACADEMIC QUALIFICATIONS": "education",

    "CERTIFICATIONS": "certifications",
    "CERTIFICATES": "certifications",
    "LICENSES AND CERTIFICATIONS": "certifications",

    "PROJECTS": "projects",
    "PERSONAL PROJECTS": "projects",
    "TECHNICAL PROJECTS": "projects",

    "ACHIEVEMENTS": "achievements",
    "AWARDS": "achievements",
    "AWARDS AND ACHIEVEMENTS": "achievements",
}


def normalize_heading(line: str) -> str:
    """
    Normalize a potential section heading for deterministic matching.
    """
    return " ".join(
        line.strip().upper().rstrip(":").split()
    )


def detect_section_heading(line: str) -> Optional[str]:
    """
    Return the canonical section name if the line is a known heading.
    """
    normalized = normalize_heading(line)
    return SECTION_ALIASES.get(normalized)


def detect_sections(text: str) -> Dict[str, str]:
    """
    Split normalized resume text into canonical resume sections.

    Text before the first recognized section heading is intentionally
    ignored at this stage.
    """
    sections = {}
    current_section = None
    current_lines = []

    def save_current_section() -> None:
        if current_section is None:
            return

        content = "\n".join(current_lines).strip()

        if not content:
            return

        if current_section in sections:
            sections[current_section] = (
                sections[current_section]
                + "\n"
                + content
            )
        else:
            sections[current_section] = content

    for line in text.splitlines():
        detected_section = detect_section_heading(line)

        if detected_section is not None:
            save_current_section()
            current_section = detected_section
            current_lines = []
            continue

        if current_section is not None:
            current_lines.append(line)

    save_current_section()

    return sections