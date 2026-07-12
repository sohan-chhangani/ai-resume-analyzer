from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.models.resume import Resume
from app.services.parser_service import ResumeParsingError


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

class TestResumeUploadEndpoint:
    def test_upload_resume_success(self, monkeypatch):
        def fake_save_resume(file):
            return {
                "original_filename": file.filename,
                "stored_filename": "stored_test_resume.pdf",
                "file_path": "uploads/stored_test_resume.pdf",
                "file_size": 1024,
                "mime_type": "application/pdf",
            }

        monkeypatch.setattr(
            "app.api.routes.upload.save_resume",
            fake_save_resume,
        )

        response = client.post(
            "/upload/",
            files={
                "file": (
                    "test_resume.pdf",
                    b"%PDF-1.4 fake test content",
                    "application/pdf",
                ),
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["id"] == 1
        assert data["original_filename"] == "test_resume.pdf"
        assert data["stored_filename"] == "stored_test_resume.pdf"
        assert data["message"] == "Resume uploaded successfully"

    def test_uploaded_resume_is_persisted(self, monkeypatch):
        def fake_save_resume(file):
            return {
                "original_filename": file.filename,
                "stored_filename": "stored_test_resume.pdf",
                "file_path": "uploads/stored_test_resume.pdf",
                "file_size": 2048,
                "mime_type": "application/pdf",
            }

        monkeypatch.setattr(
            "app.api.routes.upload.save_resume",
            fake_save_resume,
        )

        response = client.post(
            "/upload/",
            files={
                "file": (
                    "persisted_resume.pdf",
                    b"%PDF-1.4 fake test content",
                    "application/pdf",
                ),
            },
        )

        assert response.status_code == 200

        resume_id = response.json()["id"]

        db = TestingSessionLocal()

        try:
            resume = db.get(Resume, resume_id)

            assert resume is not None
            assert resume.original_filename == "persisted_resume.pdf"
            assert resume.file_size == 2048
            assert resume.mime_type == "application/pdf"
        finally:
            db.close()


class TestResumeParseEndpoint:
    def test_parse_resume_success(self, monkeypatch):
        create_resume(
            resume_id=1,
            parsing_status="pending",
        )

        monkeypatch.setattr(
            "app.api.routes.parse.parse_resume",
            lambda file_path: COMPLETE_RESUME_TEXT,
        )

        response = client.post("/resumes/1/parse")

        assert response.status_code == 200

        data = response.json()

        assert data["id"] == 1
        assert data["parsing_status"] == "completed"
        assert data["extracted_characters"] == len(
            COMPLETE_RESUME_TEXT
        )
        assert data["parsing_error"] is None
        assert data["parsed_at"] is not None
        assert data["message"] == "Resume parsed successfully"

        db = TestingSessionLocal()

        try:
            resume = db.get(Resume, 1)

            assert resume.parsing_status == "completed"
            assert resume.extracted_text == COMPLETE_RESUME_TEXT
            assert resume.parsing_error is None
            assert resume.parsed_at is not None
        finally:
            db.close()

    def test_parse_resume_not_found(self):
        response = client.post("/resumes/99999/parse")

        assert response.status_code == 404
        assert response.json() == {
            "detail": "Resume not found.",
        }

    def test_parse_resume_failure_persists_failed_status(
        self,
        monkeypatch,
    ):
        create_resume(
            resume_id=1,
            parsing_status="pending",
        )

        def fake_parse_resume(file_path):
            raise ResumeParsingError(
                "Unable to extract text from resume."
            )

        monkeypatch.setattr(
            "app.api.routes.parse.parse_resume",
            fake_parse_resume,
        )

        response = client.post("/resumes/1/parse")

        assert response.status_code == 422
        assert response.json() == {
            "detail": "Unable to extract text from resume.",
        }

        db = TestingSessionLocal()

        try:
            resume = db.get(Resume, 1)

            assert resume.parsing_status == "failed"
            assert resume.parsing_error == (
                "Unable to extract text from resume."
            )
            assert resume.parsed_at is not None
        finally:
            db.close()


class TestResumeLifecycle:
    def test_upload_parse_structured_score_lifecycle(
        self,
        monkeypatch,
    ):
        def fake_save_resume(file):
            return {
                "original_filename": file.filename,
                "stored_filename": "lifecycle_resume.pdf",
                "file_path": "uploads/lifecycle_resume.pdf",
                "file_size": 4096,
                "mime_type": "application/pdf",
            }

        monkeypatch.setattr(
            "app.api.routes.upload.save_resume",
            fake_save_resume,
        )

        upload_response = client.post(
            "/upload/",
            files={
                "file": (
                    "lifecycle_resume.pdf",
                    b"%PDF-1.4 fake lifecycle content",
                    "application/pdf",
                ),
            },
        )

        assert upload_response.status_code == 200

        resume_id = upload_response.json()["id"]

        monkeypatch.setattr(
            "app.api.routes.parse.parse_resume",
            lambda file_path: COMPLETE_RESUME_TEXT,
        )

        parse_response = client.post(
            f"/resumes/{resume_id}/parse"
        )

        assert parse_response.status_code == 200
        assert (
            parse_response.json()["parsing_status"]
            == "completed"
        )

        structured_response = client.get(
            f"/resumes/{resume_id}/structured"
        )

        assert structured_response.status_code == 200

        structured_data = structured_response.json()

        assert structured_data["contact"]["email"] == (
            "test@example.com"
        )
        assert "Python" in structured_data["skills"]["languages"]

        score_response = client.get(
            f"/resumes/{resume_id}/score"
        )

        assert score_response.status_code == 200

        score_data = score_response.json()

        assert 0 <= score_data["score"] <= 100
        assert score_data["max_score"] == 100


class TestResumeJobMatchEndpoint:
    def test_match_resume_success(self):
        create_resume(
            resume_id=101,
            parsing_status="completed",
            extracted_text=COMPLETE_RESUME_TEXT,
        )

        response = client.post(
            "/resumes/101/match",
            json={
                "job_description": (
                    "We need a Python backend engineer with "
                    "FastAPI, PostgreSQL, Docker, Redis, "
                    "AWS, REST APIs, Git and Linux."
                )
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["id"] == 101
        assert data["original_filename"] == "resume_101.pdf"
        assert isinstance(data["match_score"], int)
        assert 0 <= data["match_score"] <= 100
        assert "Python" in data["matched_skills"]
        assert "FastAPI" in data["matched_skills"]
        assert "AWS" in data["missing_skills"]
        assert data["keyword_coverage"]["required"] > 0


    def test_match_resume_not_found(self):
        response = client.post(
            "/resumes/99999/match",
            json={
                "job_description": (
                    "Python FastAPI PostgreSQL Docker"
                )
            },
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Resume not found."


    def test_match_resume_unparsed(self):
        create_resume(
            resume_id=102,
            parsing_status="pending",
        )

        response = client.post(
            "/resumes/102/match",
            json={
                "job_description": (
                    "Python FastAPI PostgreSQL Docker"
                )
            },
        )

        assert response.status_code == 409
        assert response.json()["detail"] == (
            "Resume has not been successfully parsed yet."
        )


    def test_match_resume_empty_job_description(self):
        create_resume(
            resume_id=103,
            parsing_status="completed",
            extracted_text=COMPLETE_RESUME_TEXT,
        )

        response = client.post(
            "/resumes/103/match",
            json={
                "job_description": ""
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["match_score"] == 0
        assert data["matched_skills"] == []
        assert data["missing_skills"] == []
        assert data["job_description_skills"] == []
        assert data["keyword_coverage"] == {
            "matched": 0,
            "required": 0,
        }
