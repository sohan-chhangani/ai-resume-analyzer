from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.models.resume import Resume


TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def override_get_db():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_test_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    yield

    Base.metadata.drop_all(bind=engine)


def create_resume(
    *,
    resume_id: int,
    parsing_status: str,
    extracted_text: str | None = None,
):
    db = TestingSessionLocal()

    resume = Resume(
        id=resume_id,
        original_filename=f"resume_{resume_id}.pdf",
        stored_filename=f"stored_resume_{resume_id}.pdf",
        file_path=f"uploads/stored_resume_{resume_id}.pdf",
        file_size=1024,
        mime_type="application/pdf",
        parsing_status=parsing_status,
        extracted_text=extracted_text,
        parsing_error=None,
        parsed_at=(
            datetime.now(timezone.utc)
            if parsing_status == "completed"
            else None
        ),
    )

    db.add(resume)
    db.commit()
    db.refresh(resume)
    db.close()

    return resume


COMPLETE_RESUME_TEXT = """
Test Engineer
test@example.com
+91 9876543210
https://linkedin.com/in/test-engineer
https://github.com/test-engineer

PROFESSIONAL SUMMARY
Experienced software engineer specializing in backend systems.

TECHNICAL SKILLS
Languages: Python • C • Java • Bash • SQL
Tools: Git • Docker • Linux • PostgreSQL • FastAPI • Redis

PROFESSIONAL EXPERIENCE
Developed production backend systems.
Implemented scalable APIs.
Designed database integrations.
Optimized application performance.

PROJECTS
Payment Gateway API

EDUCATION
Bachelor of Engineering

CERTIFICATIONS
Linux Foundation Certification
""".strip()


class TestResumeTextEndpoint:
    def test_get_resume_text_success(self):
        create_resume(
            resume_id=1,
            parsing_status="completed",
            extracted_text=COMPLETE_RESUME_TEXT,
        )

        response = client.get("/resumes/1/text")

        assert response.status_code == 200

        data = response.json()

        assert data["id"] == 1
        assert data["original_filename"] == "resume_1.pdf"
        assert data["extracted_text"] == COMPLETE_RESUME_TEXT
        assert data["extracted_characters"] == len(
            COMPLETE_RESUME_TEXT
        )

    def test_get_resume_text_not_found(self):
        response = client.get("/resumes/99999/text")

        assert response.status_code == 404
        assert response.json() == {
            "detail": "Resume not found.",
        }

    def test_get_resume_text_unparsed(self):
        create_resume(
            resume_id=2,
            parsing_status="pending",
        )

        response = client.get("/resumes/2/text")

        assert response.status_code == 409
        assert response.json() == {
            "detail": (
                "Resume has not been successfully parsed yet."
            ),
        }


class TestResumeSectionsEndpoint:
    def test_get_resume_sections_success(self):
        create_resume(
            resume_id=1,
            parsing_status="completed",
            extracted_text=COMPLETE_RESUME_TEXT,
        )

        response = client.get("/resumes/1/sections")

        assert response.status_code == 200

        data = response.json()

        assert data["id"] == 1
        assert data["detected_section_count"] == 6

        assert set(data["sections"]) == {
            "professional_summary",
            "technical_skills",
            "professional_experience",
            "projects",
            "education",
            "certifications",
        }

    def test_get_resume_sections_not_found(self):
        response = client.get("/resumes/99999/sections")

        assert response.status_code == 404

    def test_get_resume_sections_unparsed(self):
        create_resume(
            resume_id=2,
            parsing_status="pending",
        )

        response = client.get("/resumes/2/sections")

        assert response.status_code == 409


class TestResumeStructuredEndpoint:
    def test_get_structured_resume_success(self):
        create_resume(
            resume_id=1,
            parsing_status="completed",
            extracted_text=COMPLETE_RESUME_TEXT,
        )

        response = client.get("/resumes/1/structured")

        assert response.status_code == 200

        data = response.json()

        assert data["id"] == 1

        assert data["contact"]["email"] == (
            "test@example.com"
        )

        assert data["contact"]["phone"] == (
            "+91 9876543210"
        )

        assert data["contact"]["linkedin"] == (
            "https://linkedin.com/in/test-engineer"
        )

        assert data["contact"]["github"] == (
            "https://github.com/test-engineer"
        )

        assert "Python" in data["skills"]["languages"]
        assert "Docker" in data["skills"]["tools"]

        assert data["certifications"] == [
            "Linux Foundation Certification",
        ]

    def test_get_structured_resume_not_found(self):
        response = client.get(
            "/resumes/99999/structured"
        )

        assert response.status_code == 404

    def test_get_structured_resume_unparsed(self):
        create_resume(
            resume_id=2,
            parsing_status="pending",
        )

        response = client.get("/resumes/2/structured")

        assert response.status_code == 409


class TestResumeScoreEndpoint:
    def test_get_resume_score_success(self):
        create_resume(
            resume_id=1,
            parsing_status="completed",
            extracted_text=COMPLETE_RESUME_TEXT,
        )

        response = client.get("/resumes/1/score")

        assert response.status_code == 200

        data = response.json()

        assert data["id"] == 1
        assert data["max_score"] == 100

        assert 0 <= data["score"] <= 100

        assert data["grade"] in {
            "A+",
            "A",
            "B",
            "C",
            "D",
            "F",
        }

        assert set(data["breakdown"]) == {
            "contact_information",
            "essential_sections",
            "technical_skills",
            "professional_experience",
            "education",
            "certifications_projects",
            "content_quality",
        }

        assert isinstance(data["strengths"], list)
        assert isinstance(data["improvements"], list)

    def test_get_resume_score_not_found(self):
        response = client.get("/resumes/99999/score")

        assert response.status_code == 404
        assert response.json() == {
            "detail": "Resume not found.",
        }

    def test_get_resume_score_unparsed(self):
        create_resume(
            resume_id=2,
            parsing_status="pending",
        )

        response = client.get("/resumes/2/score")

        assert response.status_code == 409
        assert response.json() == {
            "detail": (
                "Resume has not been successfully parsed yet."
            ),
        }
