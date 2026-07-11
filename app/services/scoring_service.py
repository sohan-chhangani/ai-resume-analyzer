from typing import Dict, List


MAX_SCORE = 100


def calculate_grade(score: int) -> str:
    """
    Convert a numerical resume score into a letter grade.
    """
    if score >= 90:
        return "A+"

    if score >= 80:
        return "A"

    if score >= 70:
        return "B"

    if score >= 60:
        return "C"

    return "D"


def score_contact_information(
    contact: Dict[str, str],
) -> Dict:
    """
    Score available contact information out of 10 points.
    """
    score = 0
    strengths = []
    improvements = []

    if contact.get("email"):
        score += 3
        strengths.append("Email address detected.")
    else:
        improvements.append("Add a professional email address.")

    if contact.get("phone"):
        score += 3
        strengths.append("Phone number detected.")
    else:
        improvements.append("Add a phone number.")

    if contact.get("linkedin"):
        score += 2
        strengths.append("LinkedIn profile detected.")
    else:
        improvements.append("Add an explicit LinkedIn profile URL.")

    if contact.get("github"):
        score += 2
        strengths.append("GitHub profile detected.")
    else:
        improvements.append("Add an explicit GitHub profile URL.")

    return {
        "score": score,
        "strengths": strengths,
        "improvements": improvements,
    }


def score_essential_sections(
    sections: Dict[str, str],
    structured_data: Dict,
) -> Dict:
    """
    Score essential resume sections out of 25 points.

    Certification points are awarded only when at least one real
    certification was extracted, not merely when a section heading exists.
    """
    weights = {
        "professional_summary": 5,
        "technical_skills": 5,
        "professional_experience": 7,
        "education": 5,
    }

    score = 0
    strengths = []
    improvements = []

    for section_name, points in weights.items():
        if sections.get(section_name):
            score += points
            strengths.append(
                f"{section_name.replace('_', ' ').title()} section detected."
            )
        else:
            improvements.append(
                f"Consider adding a dedicated "
                f"{section_name.replace('_', ' ')} section."
            )

    certifications = structured_data.get("certifications", [])

    if certifications:
        score += 3
        strengths.append("Certifications section with real entries detected.")
    else:
        improvements.append(
            "Consider adding relevant professional certifications."
        )

    return {
        "score": score,
        "strengths": strengths,
        "improvements": improvements,
    }


def score_technical_skills(
    skills: Dict[str, List[str]],
) -> Dict:
    """
    Score technical skills out of 20 points.
    """
    unique_skills = {
        skill.strip().lower()
        for skill_list in skills.values()
        for skill in skill_list
        if skill.strip()
    }

    skill_count = len(unique_skills)

    if skill_count >= 15:
        score = 20
    elif skill_count >= 10:
        score = 17
    elif skill_count >= 6:
        score = 13
    elif skill_count >= 3:
        score = 8
    elif skill_count >= 1:
        score = 4
    else:
        score = 0

    strengths = []
    improvements = []

    if skill_count >= 10:
        strengths.append(
            f"Strong technical skills coverage with "
            f"{skill_count} unique skills detected."
        )
    elif skill_count > 0:
        improvements.append(
            f"Only {skill_count} unique technical skills were detected; "
            f"consider strengthening the skills section."
        )
    else:
        improvements.append(
            "Add a dedicated technical skills section."
        )

    return {
        "score": score,
        "skill_count": skill_count,
        "strengths": strengths,
        "improvements": improvements,
    }


def score_professional_experience(
    sections: Dict[str, str],
) -> Dict:
    """
    Score professional experience content out of 20 points.
    """
    experience = sections.get(
        "professional_experience",
        "",
    ).strip()

    if not experience:
        return {
            "score": 0,
            "strengths": [],
            "improvements": [
                "Add a professional experience section."
            ],
        }

    word_count = len(experience.split())

    if word_count >= 150:
        score = 20
    elif word_count >= 100:
        score = 17
    elif word_count >= 60:
        score = 13
    elif word_count >= 25:
        score = 8
    else:
        score = 4

    strengths = []
    improvements = []

    if word_count >= 100:
        strengths.append(
            "Professional experience contains substantial detail."
        )
    else:
        improvements.append(
            "Add more specific achievements, responsibilities, "
            "and measurable impact to professional experience."
        )

    return {
        "score": score,
        "strengths": strengths,
        "improvements": improvements,
    }


def score_education(
    sections: Dict[str, str],
) -> Dict:
    """
    Score education information out of 10 points.
    """
    education = sections.get("education", "").strip()

    if not education:
        return {
            "score": 0,
            "strengths": [],
            "improvements": [
                "Add an education section."
            ],
        }

    return {
        "score": 10,
        "strengths": [
            "Education section detected."
        ],
        "improvements": [],
    }


def score_certifications_and_projects(
    sections: Dict[str, str],
    structured_data: Dict,
) -> Dict:
    """
    Score certifications and projects out of 5 points.

    Certifications count only when real extracted entries exist.
    """
    has_certifications = bool(
        structured_data.get("certifications", [])
    )
    has_projects = bool(
        sections.get("projects", "").strip()
    )

    score = 0
    strengths = []
    improvements = []

    if has_certifications:
        score += 3
        strengths.append("Certifications section detected.")

    if has_projects:
        score += 2
        strengths.append("Projects section detected.")

    if not has_certifications:
        improvements.append(
            "Consider adding relevant professional certifications."
        )

    if not has_projects:
        improvements.append(
            "Consider adding a dedicated projects section."
        )

    return {
        "score": score,
        "strengths": strengths,
        "improvements": improvements,
    }


def score_content_quality(
    text: str,
) -> Dict:
    """
    Score basic deterministic content-quality signals out of 10 points.
    """
    word_count = len(text.split())

    score = 0
    strengths = []
    improvements = []

    if 300 <= word_count <= 900:
        score += 5
        strengths.append(
            "Resume length is within a reasonable content range."
        )
    elif word_count < 300:
        improvements.append(
            "Resume may be too brief; consider adding more relevant detail."
        )
    else:
        improvements.append(
            "Resume may be overly long; consider making content more concise."
        )

    action_verbs = {
        "built",
        "created",
        "developed",
        "designed",
        "implemented",
        "improved",
        "led",
        "managed",
        "optimized",
        "owned",
        "reduced",
        "resolved",
    }

    text_words = {
        word.strip(".,:;()[]").lower()
        for word in text.split()
    }

    detected_action_verbs = action_verbs.intersection(
        text_words
    )

    if len(detected_action_verbs) >= 4:
        score += 5
        strengths.append(
            "Strong use of action-oriented language detected."
        )
    elif len(detected_action_verbs) >= 2:
        score += 3
        improvements.append(
            "Use more varied action verbs to strengthen achievements."
        )
    else:
        improvements.append(
            "Use stronger action verbs to describe accomplishments."
        )

    return {
        "score": score,
        "strengths": strengths,
        "improvements": improvements,
    }


def build_resume_score(
    text: str,
    sections: Dict[str, str],
    structured_data: Dict,
) -> Dict:
    """
    Build the complete deterministic resume score.
    """
    contact_result = score_contact_information(
        structured_data.get("contact", {})
    )

    sections_result = score_essential_sections(
        sections,
        structured_data,
    )

    skills_result = score_technical_skills(
        structured_data.get("skills", {})
    )

    experience_result = score_professional_experience(
        sections
    )

    education_result = score_education(sections)

    certifications_projects_result = (
        score_certifications_and_projects(
            sections,
            structured_data,
        )
    )

    quality_result = score_content_quality(text)

    breakdown = {
        "contact_information": contact_result["score"],
        "essential_sections": sections_result["score"],
        "technical_skills": skills_result["score"],
        "professional_experience": experience_result["score"],
        "education": education_result["score"],
        "certifications_projects": (
            certifications_projects_result["score"]
        ),
        "content_quality": quality_result["score"],
    }

    total_score = sum(breakdown.values())

    all_results = [
        contact_result,
        sections_result,
        skills_result,
        experience_result,
        education_result,
        certifications_projects_result,
        quality_result,
    ]

    strengths = []
    improvements = []

    for result in all_results:
        strengths.extend(result.get("strengths", []))
        improvements.extend(result.get("improvements", []))

    return {
    "score": total_score,
    "max_score": MAX_SCORE,
    "grade": calculate_grade(total_score),
    "breakdown": breakdown,
    "strengths": list(dict.fromkeys(strengths)),
    "improvements": list(dict.fromkeys(improvements)),
    }
