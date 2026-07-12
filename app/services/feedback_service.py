from typing import Dict, List, Optional


def build_priority_improvements(
    missing_skills: List[str],
) -> List[str]:
    """
    Build actionable improvement suggestions from skills missing
    relative to a job description.

    Suggestions must never encourage candidates to claim experience
    they do not actually possess.
    """
    return [
        (
            f"Add evidence of {skill} experience if you have genuine "
            "practical exposure, or build a relevant project to "
            "demonstrate the skill."
        )
        for skill in missing_skills
    ]


def build_matched_strengths(
    matched_skills: List[str],
) -> List[str]:
    """
    Build concise strength statements from skills shared between
    the resume and job description.
    """
    return [
        f"Your resume demonstrates relevant {skill} experience."
        for skill in matched_skills
    ]


def build_feedback_summary(
    match_score: Optional[int],
    matched_count: int,
    required_count: int,
) -> str:
    """
    Build a deterministic high-level resume feedback summary.
    """
    if match_score is None:
        return (
            "Resume feedback generated without a job description."
        )

    if required_count == 0:
        return (
            "No recognized technical skills were detected in the "
            "job description."
        )

    return (
        f"Your resume matches {match_score}% of the "
        f"{required_count} recognized job-description skills, "
        f"covering {matched_count} requirements."
    )


def build_resume_feedback(
    score_data: Dict,
    match_data: Optional[Dict] = None,
) -> Dict:
    """
    Combine deterministic resume scoring and optional job matching
    results into actionable resume feedback.
    """
    if match_data is None:
        match_score = None
        matched_skills = []
        missing_skills = []
        matched_count = 0
        required_count = 0
    else:
        match_score = match_data["match_score"]
        matched_skills = match_data["matched_skills"]
        missing_skills = match_data["missing_skills"]

        coverage = match_data["keyword_coverage"]
        matched_count = coverage["matched"]
        required_count = coverage["required"]

    return {
        "summary": build_feedback_summary(
            match_score,
            matched_count,
            required_count,
        ),
        "resume_score": score_data["score"],
        "resume_grade": score_data["grade"],
        "job_match_score": match_score,
        "priority_improvements": build_priority_improvements(
            missing_skills
        ),
        "matched_strengths": build_matched_strengths(
            matched_skills
        ),
        "resume_strengths": list(score_data["strengths"]),
        "resume_improvements": list(score_data["improvements"]),
    }
