import re
from typing import Dict, List, Set


SKILL_ALIASES = {
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "fastapi": "FastAPI",
    "sqlite": "SQLite",
    "sqlalchemy": "SQLAlchemy",
    "alembic": "Alembic",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "redis": "Redis",
    "nginx": "Nginx",
    "aws": "AWS",
    "azure": "Azure",
    "gcp": "GCP",
    "python": "Python",
    "java": "Java",
    "bash": "Bash",
    "c++": "C++",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "react": "React",
    "next.js": "Next.js",
    "node.js": "Node.js",
    "git": "Git",
    "linux": "Linux",
    "embedded linux": "Embedded Linux",
    "android": "Android",
    "android 11": "Android 11",
    "aosp": "AOSP",
    "yocto": "Yocto",
    "selinux": "SELinux",
    "android pos": "Android POS",
    "emv": "EMV",
    "nfc": "NFC",
    "iso14443": "ISO14443",
    "iso7816": "ISO7816",
    "open loop": "Open Loop",
    "closed loop": "Closed Loop",
    "mifare classic": "MIFARE Classic",
    "mifare ultralight": "MIFARE Ultralight",
    "jwt": "JWT",
    "rest api": "REST APIs",
    "rest apis": "REST APIs",
    "restful api": "REST APIs",
    "restful apis": "REST APIs",
    "sql": "SQL",
    "mysql": "MySQL",
    "mongodb": "MongoDB",
    "celery": "Celery",
    "rabbitmq": "RabbitMQ",
    "pytest": "Pytest",
    "terraform": "Terraform",
    "jenkins": "Jenkins",
    "github actions": "GitHub Actions",
}


def normalize_skill(skill: str) -> str:
    """
    Normalize a skill into a deterministic lowercase comparison value.
    """
    return " ".join(skill.strip().lower().split())


def flatten_resume_skills(
    skills: Dict[str, List[str]],
) -> Dict[str, str]:
    """
    Flatten categorized resume skills into a mapping from normalized
    comparison values to their original display values.
    """
    flattened = {}

    for skill_list in skills.values():
        for skill in skill_list:
            normalized = normalize_skill(skill)

            if normalized and normalized not in flattened:
                flattened[normalized] = skill.strip()

    return flattened


def skill_exists_in_text(
    skill: str,
    text: str,
) -> bool:
    """
    Return True when a technical skill appears as a standalone term
    or phrase in text.
    """
    pattern = (
        r"(?<![A-Za-z0-9])"
        + re.escape(skill)
        + r"(?![A-Za-z0-9])"
    )

    return bool(
        re.search(
            pattern,
            text,
            re.IGNORECASE,
        )
    )


def extract_job_description_skills(
    job_description: str,
) -> List[str]:
    """
    Extract known technical skills from a raw job description using
    deterministic alias matching.
    """
    detected: Dict[str, str] = {}

    for alias, canonical_name in SKILL_ALIASES.items():
        if skill_exists_in_text(alias, job_description):
            normalized = normalize_skill(canonical_name)
            detected[normalized] = canonical_name

    return sorted(
        detected.values(),
        key=str.lower,
    )


def build_resume_skill_aliases(
    resume_skills: Dict[str, str],
) -> Set[str]:
    """
    Build the normalized set of canonical resume skills for comparison.
    """
    canonical_skills = set()

    for normalized_skill in resume_skills:
        canonical_name = SKILL_ALIASES.get(
            normalized_skill,
            resume_skills[normalized_skill],
        )

        canonical_skills.add(
            normalize_skill(canonical_name)
        )

    return canonical_skills


def calculate_match_score(
    matched_count: int,
    required_count: int,
) -> int:
    """
    Calculate percentage-based JD skill coverage.
    """
    if required_count == 0:
        return 0

    return round(
        (matched_count / required_count) * 100
    )


def build_job_match(
    structured_resume: Dict,
    job_description: str,
) -> Dict:
    """
    Compare structured resume skills against a raw job description and
    return deterministic skill-match results.
    """
    resume_skill_map = flatten_resume_skills(
        structured_resume.get("skills", {})
    )

    resume_canonical_skills = build_resume_skill_aliases(
        resume_skill_map
    )

    job_skills = extract_job_description_skills(
        job_description
    )

    matched_skills = []
    missing_skills = []

    for skill in job_skills:
        normalized = normalize_skill(skill)

        if normalized in resume_canonical_skills:
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)

    match_score = calculate_match_score(
        matched_count=len(matched_skills),
        required_count=len(job_skills),
    )

    resume_skills = sorted(
        resume_skill_map.values(),
        key=str.lower,
    )

    return {
        "match_score": match_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "resume_skills": resume_skills,
        "job_description_skills": job_skills,
        "keyword_coverage": {
            "matched": len(matched_skills),
            "required": len(job_skills),
        },
    }
