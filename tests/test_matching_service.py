from app.services.matching_service import (
    build_job_match,
    calculate_match_score,
    extract_job_description_skills,
    flatten_resume_skills,
    skill_exists_in_text,
)


class TestSkillBoundaryMatching:
    def test_exact_skill_is_detected(self):
        assert skill_exists_in_text(
            "Python",
            "Experience with Python is required.",
        )

    def test_java_does_not_match_javascript(self):
        assert not skill_exists_in_text(
            "Java",
            "Experience with JavaScript is required.",
        )

    def test_sql_does_not_match_postgresql(self):
        assert not skill_exists_in_text(
            "SQL",
            "Experience with PostgreSQL is required.",
        )


class TestJobDescriptionSkillExtraction:
    def test_extract_known_skills(self):
        result = extract_job_description_skills(
            "Python, FastAPI, PostgreSQL and Docker are required."
        )

        assert result == [
            "Docker",
            "FastAPI",
            "PostgreSQL",
            "Python",
        ]

    def test_alias_normalization(self):
        result = extract_job_description_skills(
            "Experience with postgres is required."
        )

        assert result == ["PostgreSQL"]

    def test_duplicate_aliases_are_deduplicated(self):
        result = extract_job_description_skills(
            "Experience with postgres and PostgreSQL is required."
        )

        assert result == ["PostgreSQL"]

    def test_empty_job_description_returns_no_skills(self):
        result = extract_job_description_skills("")

        assert result == []


class TestResumeSkillFlattening:
    def test_duplicate_resume_skills_are_deduplicated(self):
        skills = {
            "languages": ["Python", "Java"],
            "backend": ["Python", "FastAPI"],
        }

        result = flatten_resume_skills(skills)

        assert result == {
            "python": "Python",
            "java": "Java",
            "fastapi": "FastAPI",
        }


class TestMatchScoreCalculation:
    def test_zero_required_skills_returns_zero(self):
        assert calculate_match_score(0, 0) == 0

    def test_partial_match_score(self):
        assert calculate_match_score(7, 10) == 70

    def test_complete_match_score(self):
        assert calculate_match_score(10, 10) == 100


class TestJobMatching:
    def test_basic_job_match(self):
        structured_resume = {
            "skills": {
                "languages": [
                    "Python",
                ],
                "backend": [
                    "FastAPI",
                    "PostgreSQL",
                    "Docker",
                    "REST APIs",
                ],
                "tools": [
                    "Git",
                    "Linux",
                ],
            }
        }

        job_description = """
        Python backend engineer with experience in FastAPI,
        PostgreSQL, Docker, Redis, AWS, REST APIs, Git,
        Linux and Kubernetes.
        """

        result = build_job_match(
            structured_resume,
            job_description,
        )

        assert result["match_score"] == 70

        assert result["matched_skills"] == [
            "Docker",
            "FastAPI",
            "Git",
            "Linux",
            "PostgreSQL",
            "Python",
            "REST APIs",
        ]

        assert result["missing_skills"] == [
            "AWS",
            "Kubernetes",
            "Redis",
        ]

        assert result["keyword_coverage"] == {
            "matched": 7,
            "required": 10,
        }

    def test_zero_matches(self):
        structured_resume = {
            "skills": {
                "languages": ["Python"],
            }
        }

        result = build_job_match(
            structured_resume,
            "AWS Redis Kubernetes",
        )

        assert result["match_score"] == 0
        assert result["matched_skills"] == []
        assert result["missing_skills"] == [
            "AWS",
            "Kubernetes",
            "Redis",
        ]

    def test_complete_match(self):
        structured_resume = {
            "skills": {
                "languages": ["Python"],
                "backend": [
                    "FastAPI",
                    "PostgreSQL",
                    "Docker",
                ],
            }
        }

        result = build_job_match(
            structured_resume,
            "Python FastAPI PostgreSQL Docker",
        )

        assert result["match_score"] == 100
        assert result["missing_skills"] == []

    def test_empty_job_description(self):
        structured_resume = {
            "skills": {
                "languages": ["Python"],
            }
        }

        result = build_job_match(
            structured_resume,
            "",
        )

        assert result["match_score"] == 0
        assert result["matched_skills"] == []
        assert result["missing_skills"] == []
        assert result["keyword_coverage"] == {
            "matched": 0,
            "required": 0,
        }

    def test_resume_alias_matches_canonical_job_skill(self):
        structured_resume = {
            "skills": {
                "databases": ["postgres"],
            }
        }

        result = build_job_match(
            structured_resume,
            "PostgreSQL experience required.",
        )

        assert result["match_score"] == 100
        assert result["matched_skills"] == [
            "PostgreSQL",
        ]

    def test_score_never_exceeds_one_hundred(self):
        assert calculate_match_score(10, 10) <= 100
