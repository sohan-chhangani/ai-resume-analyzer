from app.services.scoring_service import build_resume_score


def build_complete_resume_data():
    text = (
        "Developed implemented designed optimized architected "
        "delivered automated improved led built systems "
    ) * 60

    sections = {
        "professional_summary": (
            "Experienced software engineer specializing in backend systems."
        ),
        "technical_skills": (
            "Languages: Python, C, Java\n"
            "Tools: Git, Docker, Linux, PostgreSQL, FastAPI"
        ),
        "professional_experience": "Developed production systems. " * 100,
        "education": "Bachelor of Engineering",
        "certifications": "Linux Foundation Certification",
        "projects": "Payment Gateway API",
    }

    structured = {
        "contact": {
            "email": "engineer@example.com",
            "phone": "+91 9876543210",
            "linkedin": "https://linkedin.com/in/test-user",
            "github": "https://github.com/test-user",
        },
        "skills": {
            "languages": [
                "Python",
                "C",
                "Java",
                "Bash",
                "SQL",
            ],
            "tools": [
                "Git",
                "Docker",
                "Linux",
                "PostgreSQL",
                "FastAPI",
                "Redis",
                "Nginx",
                "AWS",
                "Kubernetes",
                "SQLAlchemy",
            ],
        },
        "certifications": [
            "Linux Foundation Certification",
        ],
    }

    return text, sections, structured


class TestResumeScoring:
    def test_complete_resume_receives_maximum_score(self):
        text, sections, structured = build_complete_resume_data()

        result = build_resume_score(
            text,
            sections,
            structured,
        )

        assert result["score"] == 100
        assert result["max_score"] == 100
        assert result["grade"] == "A+"
        assert result["improvements"] == []

    def test_missing_contact_information_scores_zero(self):
        text, sections, structured = build_complete_resume_data()

        structured["contact"] = {
            "email": None,
            "phone": None,
            "linkedin": None,
            "github": None,
        }

        result = build_resume_score(
            text,
            sections,
            structured,
        )

        assert result["breakdown"]["contact_information"] == 0

        assert "Add a professional email address." in result["improvements"]
        assert "Add a phone number." in result["improvements"]
        assert (
            "Add an explicit LinkedIn profile URL."
            in result["improvements"]
        )
        assert (
            "Add an explicit GitHub profile URL."
            in result["improvements"]
        )

    def test_placeholder_certification_receives_no_certification_credit(self):
        text, sections, structured = build_complete_resume_data()

        sections["certifications"] = (
            "Relevant certifications will be added "
            "as they are completed and verified."
        )
        structured["certifications"] = []

        result = build_resume_score(
            text,
            sections,
            structured,
        )

        assert result["breakdown"]["certifications_projects"] == 2
        assert result["breakdown"]["essential_sections"] == 22

        assert (
            "Certifications section detected."
            not in result["strengths"]
        )

        assert (
            "Consider adding relevant professional certifications."
            in result["improvements"]
        )

    def test_projects_without_certifications_receive_project_credit_only(self):
        text, sections, structured = build_complete_resume_data()

        sections.pop("certifications")
        structured["certifications"] = []

        result = build_resume_score(
            text,
            sections,
            structured,
        )

        assert result["breakdown"]["certifications_projects"] == 2
        assert "Projects section detected." in result["strengths"]

    def test_low_skill_count_produces_improvement_feedback(self):
        text, sections, structured = build_complete_resume_data()

        structured["skills"] = {
            "languages": [
                "Python",
                "C",
                "Java",
            ],
        }

        result = build_resume_score(
            text,
            sections,
            structured,
        )

        assert result["breakdown"]["technical_skills"] == 8

        assert (
            "Only 3 unique technical skills were detected; "
            "consider strengthening the skills section."
            in result["improvements"]
        )

    def test_duplicate_skills_are_counted_once(self):
        text, sections, structured = build_complete_resume_data()

        structured["skills"] = {
            "languages": [
                "Python",
                "python",
                "PYTHON",
                "C",
                "c",
            ],
        }

        result = build_resume_score(
            text,
            sections,
            structured,
        )

        assert result["breakdown"]["technical_skills"] == 4

        assert (
            "Only 2 unique technical skills were detected; "
            "consider strengthening the skills section."
            in result["improvements"]
        )

    def test_score_never_exceeds_maximum(self):
        text, sections, structured = build_complete_resume_data()

        result = build_resume_score(
            text,
            sections,
            structured,
        )

        assert result["score"] <= result["max_score"]
        assert result["max_score"] == 100

    def test_result_contains_expected_breakdown_categories(self):
        text, sections, structured = build_complete_resume_data()

        result = build_resume_score(
            text,
            sections,
            structured,
        )

        assert set(result["breakdown"]) == {
            "contact_information",
            "essential_sections",
            "technical_skills",
            "professional_experience",
            "education",
            "certifications_projects",
            "content_quality",
        }
