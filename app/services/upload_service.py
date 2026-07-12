import os
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile

from app.core.config import settings


CHUNK_SIZE = 1024 * 1024


def save_resume(file: UploadFile):
    """
    Validate and persist an uploaded resume.

    Files are written incrementally so the maximum upload size can be
    enforced without loading the complete upload into application memory.
    Partially written files are removed when validation or writing fails.
    """
    original_filename = file.filename

    if not original_filename:
        raise HTTPException(
            status_code=400,
            detail="Filename missing.",
        )

    extension = Path(original_filename).suffix.lower()

    if extension not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are allowed.",
        )

    if file.content_type not in settings.ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Invalid file content type.",
        )

    stored_filename = f"{uuid.uuid4()}{extension}"

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    file_path = os.path.join(
        settings.UPLOAD_DIR,
        stored_filename,
    )

    file_size = 0

    try:
        with open(file_path, "wb") as buffer:
            while True:
                chunk = file.file.read(CHUNK_SIZE)

                if not chunk:
                    break

                file_size += len(chunk)

                if file_size > settings.MAX_UPLOAD_SIZE_BYTES:
                    raise HTTPException(
                        status_code=413,
                        detail=(
                            "Uploaded file exceeds the maximum "
                            "allowed size."
                        ),
                    )

                buffer.write(chunk)

        if file_size == 0:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty.",
            )

    except Exception:
        if os.path.exists(file_path):
            os.remove(file_path)

        raise

    return {
        "original_filename": original_filename,
        "stored_filename": stored_filename,
        "file_path": file_path,
        "file_size": file_size,
        "mime_type": file.content_type,
    }