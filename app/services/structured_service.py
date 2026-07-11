import re
from typing import Dict, List, Optional


EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)

PHONE_PATTERN = re.compile(
    r"(?<!\d)(?:\+\d{1,3}[\s-]?)?(?:\d[\s-]?){9,14}\d(?!\d)"
)

URL_PATTERN = re.compile(
    r"https?://[^\s]+",
    re.IGNORECASE,
)


def extract_email(text: str) -> Optional[str]:
    """
    Return the first email address found in the resume text.
    """
    match = EMAIL_PATTERN.search(text)

    if match is None:
        return None

    return match.group(0)


def extract_phone(text: str) -> Optional[str]:
    """
    Return the first likely phone number found in the resume text.
    """
    match = PHONE_PATTERN.search(text)

    if match is None:
        return None

    return match.group(0).strip()


def extract_profile_urls(text: str) -> Dict[str, Optional[str]]:
    """
    Extract supported professional profile URLs when actual URLs
    are present in the parsed resume text.
    """
    profiles = {
        "linkedin": None,
        "github": None,
    }

    for url in URL_PATTERN.findall(text):
        cleaned_url = url.rstrip(".,);]")

        lowered = cleaned_url.lower()

        if "linkedin.com" in lowered and profiles["linkedin"] is None:
            profiles["linkedin"] = cleaned_url

        elif "github.com" in lowered and profiles["github"] is None:
            profiles["github"] = cleaned_url

    return profiles


def split_skill_values(value: str) -> List[str]:
    """
    Split resume skill values separated by commas or common bullet symbols.
    """
    return [
        item.strip().rstrip(".")
        for item in re.split(
            r"[,\u2022\u25cf\u25aa\u25e6\uf0b7]+",
            value,
        )
        if item.strip()
    ]


def normalize_skill_category(value: str) -> str:
    """
    Normalize a skill category name into a deterministic dictionary key.
    """
    return (
        value.strip()
        .lower()
        .replace("&", "and")
        .replace(" ", "_")
    )


def extract_skill_categories(
    skills_text: Optional[str],
) -> Dict[str, List[str]]:
    """
    Extract skill categories from both supported resume formats.

    Multi-line format:

        Programming Languages:
        C, Python, Java

    Inline format:

        Languages: C ? Python ? Bash ? Java
        Backend: FastAPI ? PostgreSQL ? Docker
    """
    if not skills_text:
        return {}

    lines = [
        line.strip()
        for line in skills_text.splitlines()
        if line.strip()
    ]

    categories = {}
    current_category = None

    for line in lines:
        if ":" in line:
            category_name, value = line.split(":", 1)

            current_category = normalize_skill_category(
                category_name
            )

            categories.setdefault(current_category, [])

            if value.strip():
                categories[current_category].extend(
                    split_skill_values(value)
                )

            continue

        if current_category is not None:
            categories[current_category].extend(
                split_skill_values(line)
            )

    return {
        category: skills
        for category, skills in categories.items()
        if skills
    }


def is_certification_placeholder(value: str) -> bool:
    """
    Return True when certification text is placeholder content rather
    than an actual certification.
    """
    normalized = " ".join(value.lower().split())

    exact_placeholders = {
        "n/a",
        "na",
        "none",
        "none yet",
        "coming soon",
        "to be added",
        "to be updated",
    }

    if normalized in exact_placeholders:
        return True

    placeholder_phrases = (
        "will be added",
        "will be updated",
        "to be completed",
        "coming soon",
    )

    return any(
        phrase in normalized
        for phrase in placeholder_phrases
    )


def extract_certifications(
    certifications_text: Optional[str],
) -> List[str]:
    """
    Convert certification section content into a normalized list while
    excluding placeholder content.
    """
    if not certifications_text:
        return []

    certifications = []

    for line in certifications_text.splitlines():
        cleaned = line.strip()

        if not cleaned:
            continue

        cleaned = re.sub(
            r"^[\u2022\u25cf\u25aa\u25e6\uf0b7\-]\s*",
            "",
            cleaned,
        ).strip()

        if not cleaned:
            continue

        if is_certification_placeholder(cleaned):
            continue

        if re.fullmatch(
            r"https?://[^\s]+",
            cleaned,
            re.IGNORECASE,
        ):
            continue

        certifications.append(cleaned)

    return certifications


def build_structured_resume(
    text: str,
    sections: Dict[str, str],
) -> Dict:
    """
    Build deterministic structured data from normalized resume text
    and previously detected resume sections.
    """
    profiles = extract_profile_urls(text)

    return {
        "contact": {
            "email": extract_email(text),
            "phone": extract_phone(text),
            "linkedin": profiles["linkedin"],
            "github": profiles["github"],
        },
        "skills": extract_skill_categories(
            sections.get("technical_skills")
        ),
        "certifications": extract_certifications(
            sections.get("certifications")
        ),
        "detected_sections": list(sections.keys()),
        "statistics": {
            "character_count": len(text),
            "word_count": len(text.split()),
            "section_count": len(sections),
        },
    }
