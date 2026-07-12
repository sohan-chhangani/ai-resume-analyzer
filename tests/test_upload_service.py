import io
from pathlib import Path

import pytest
from fastapi import HTTPException, UploadFile

from app.core.config import settings
from app.services.upload_service import save_resume


def make_upload_file(
    filename: str,
    content: bytes,
    content_type: str,
) -> UploadFile:
    return UploadFile(
        filename=filename,
        file=io.BytesIO(content),
        headers={
            "content-type": content_type,
        },
    )


class TestUploadValidation:
    def test_valid_pdf_is_saved(
        self,
        tmp_path,
        monkeypatch,
    ):
        monkeypatch.setattr(
            settings,
            "UPLOAD_DIR",
            str(tmp_path),
        )

        content = b"%PDF-1.4 valid test content"

        file = make_upload_file(
            "resume.pdf",
            content,
            "application/pdf",
        )

        result = save_resume(file)

        saved_path = Path(result["file_path"])

        assert saved_path.exists()
        assert saved_path.read_bytes() == content
        assert result["original_filename"] == "resume.pdf"
        assert result["file_size"] == len(content)
        assert result["mime_type"] == "application/pdf"

    def test_valid_docx_is_saved(
        self,
        tmp_path,
        monkeypatch,
    ):
        monkeypatch.setattr(
            settings,
            "UPLOAD_DIR",
            str(tmp_path),
        )

        content = b"fake docx test content"

        file = make_upload_file(
            "resume.docx",
            content,
            (
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),
        )

        result = save_resume(file)

        saved_path = Path(result["file_path"])

        assert saved_path.exists()
        assert saved_path.read_bytes() == content
        assert result["file_size"] == len(content)

    def test_unsupported_extension_is_rejected(
        self,
        tmp_path,
        monkeypatch,
    ):
        monkeypatch.setattr(
            settings,
            "UPLOAD_DIR",
            str(tmp_path),
        )

        file = make_upload_file(
            "resume.txt",
            b"plain text",
            "text/plain",
        )

        with pytest.raises(HTTPException) as exc_info:
            save_resume(file)

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == (
            "Only PDF and DOCX files are allowed."
        )
        assert list(tmp_path.iterdir()) == []

    def test_invalid_mime_type_is_rejected(
        self,
        tmp_path,
        monkeypatch,
    ):
        monkeypatch.setattr(
            settings,
            "UPLOAD_DIR",
            str(tmp_path),
        )

        file = make_upload_file(
            "resume.pdf",
            b"not really a pdf",
            "text/plain",
        )

        with pytest.raises(HTTPException) as exc_info:
            save_resume(file)

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == (
            "Invalid file content type."
        )
        assert list(tmp_path.iterdir()) == []

    def test_empty_file_is_rejected_and_removed(
        self,
        tmp_path,
        monkeypatch,
    ):
        monkeypatch.setattr(
            settings,
            "UPLOAD_DIR",
            str(tmp_path),
        )

        file = make_upload_file(
            "resume.pdf",
            b"",
            "application/pdf",
        )

        with pytest.raises(HTTPException) as exc_info:
            save_resume(file)

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == (
            "Uploaded file is empty."
        )
        assert list(tmp_path.iterdir()) == []

    def test_oversized_file_is_rejected_and_removed(
        self,
        tmp_path,
        monkeypatch,
    ):
        monkeypatch.setattr(
            settings,
            "UPLOAD_DIR",
            str(tmp_path),
        )
        monkeypatch.setattr(
            settings,
            "MAX_UPLOAD_SIZE_BYTES",
            10,
        )

        file = make_upload_file(
            "resume.pdf",
            b"12345678901",
            "application/pdf",
        )

        with pytest.raises(HTTPException) as exc_info:
            save_resume(file)

        assert exc_info.value.status_code == 413
        assert exc_info.value.detail == (
            "Uploaded file exceeds the maximum allowed size."
        )
        assert list(tmp_path.iterdir()) == []

    def test_file_at_exact_size_limit_is_accepted(
        self,
        tmp_path,
        monkeypatch,
    ):
        monkeypatch.setattr(
            settings,
            "UPLOAD_DIR",
            str(tmp_path),
        )
        monkeypatch.setattr(
            settings,
            "MAX_UPLOAD_SIZE_BYTES",
            10,
        )

        content = b"1234567890"

        file = make_upload_file(
            "resume.pdf",
            content,
            "application/pdf",
        )

        result = save_resume(file)

        assert result["file_size"] == 10
        assert Path(result["file_path"]).exists()
