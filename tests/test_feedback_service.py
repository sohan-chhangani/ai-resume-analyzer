from copy import deepcopy

from app.services.feedback_service import (
    build_feedback_summary,
    build_matched_strengths,
    build_priority_improvements,
    build_resume_feedback,
)


class TestPriorityImprovements:
    def test_builds_improvements_for_missing_skills(self):
        result = build_priority_improvements(
            ["AWS", "Kubernetes", "Redis"]
        )

        assert len(result) == 3
        assert "AWS" in result[0]
        assert "Kubernetes" in result[1]
        assert "Redis" in result[2]


    def test_empty_missing_skills_returns_empty_list(self):
        assert build_priority_improvements([]) == []


class TestMatchedStrengths:
    def test_builds_strengths_for_matched_skills(self):
        result = build_matched_strengths(
            ["Docker", "FastAPI", "Python"]
        )

        assert result == [
            "Your resume demonstrates relevant Docker experience.",
            "Your resume demonstrates relevant FastAPI experience.",
            "Your resume demonstrates relevant Python experience.",
        ]


    def test_empty_matched_skills_returns_empty_list(self):
        assert build_matched_strengths([]) == []


class TestFeedbackSummary:
    def test_summary_with_job_match(self):
        result = build_feedback_summary(
            match_score=77,
            matched_count=10,
            required_count=13,
        )

        assert result == (
            "Your resume matches 77% of the 13 recognized "
            "job-description skills, covering 10 requirements."
        )


    def test_summary_without_job_description(self):
        result = build_feedback_summary(
            match_score=None,
            matched_count=0,
            required_count=0,
        )

        assert result == (
            "Resume feedback generated without a job description."
        )


    def test_summary_with_no_recognized_job_skills(self):
        result = build_feedback_summary(
            match_score=0,
            matched_count=0,
            required_count=0,
        )

        assert result == (
            "No recognized technical skills were detected in the "
            "job description."
        )


class TestResumeFeedback:
    def test_build_feedback_with_job_match(self):
        score_data = {
            "score": 83,
            "grade": "A",
            "strengths": [
                "Strong technical skills coverage.",
            ],
            "improvements": [
                "Add a professional email address.",
            ],
        }

        match_data = {
            "match_score": 77,
            "matched_skills": [
                "Docker",
                "FastAPI",
                "Python",
            ],
            "missing_skills": [
                "AWS",
                "Redis",
            ],
            "keyword_coverage": {
                "matched": 3,
                "required": 5,
            },
        }

        result = build_resume_feedback(
            score_data,
            match_data,
        )

        assert result["resume_score"] == 83
        assert result["resume_grade"] == "A"
        assert result["job_match_score"] == 77

        assert len(result["priority_improvements"]) == 2
        assert len(result["matched_strengths"]) == 3

        assert result["resume_strengths"] == [
            "Strong technical skills coverage.",
        ]

        assert result["resume_improvements"] == [
            "Add a professional email address.",
        ]


    def test_build_feedback_without_job_match(self):
        score_data = {
            "score": 79,
            "grade": "B",
            "strengths": [
                "Projects section detected.",
            ],
            "improvements": [
                "Add a professional email address.",
            ],
        }

        result = build_resume_feedback(score_data)

        assert result["resume_score"] == 79
        assert result["resume_grade"] == "B"
        assert result["job_match_score"] is None
        assert result["priority_improvements"] == []
        assert result["matched_strengths"] == []

        assert result["summary"] == (
            "Resume feedback generated without a job description."
        )


    def test_score_feedback_is_preserved(self):
        score_data = {
            "score": 62,
            "grade": "C",
            "strengths": [
                "Education section detected.",
                "Projects section detected.",
            ],
            "improvements": [
                "Add a professional email address.",
                "Add a phone number.",
            ],
        }

        result = build_resume_feedback(score_data)

        assert result["resume_strengths"] == (
            score_data["strengths"]
        )

        assert result["resume_improvements"] == (
            score_data["improvements"]
        )


    def test_inputs_are_not_mutated(self):
        score_data = {
            "score": 83,
            "grade": "A",
            "strengths": [
                "Strong technical skills coverage.",
            ],
            "improvements": [
                "Add a professional email address.",
            ],
        }

        match_data = {
            "match_score": 50,
            "matched_skills": ["Python"],
            "missing_skills": ["AWS"],
            "keyword_coverage": {
                "matched": 1,
                "required": 2,
            },
        }

        original_score_data = deepcopy(score_data)
        original_match_data = deepcopy(match_data)

        build_resume_feedback(
            score_data,
            match_data,
        )

        assert score_data == original_score_data
        assert match_data == original_match_data
