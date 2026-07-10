import os
import shutil
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile

from app.core.config import settings


def save_resume(file: UploadFile):
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

    stored_filename = f"{uuid.uuid4()}{extension}"

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    file_path = os.path.join(
        settings.UPLOAD_DIR,
        stored_filename,
    )

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "original_filename": original_filename,
        "stored_filename": stored_filename,
        "file_path": file_path,
        "file_size": os.path.getsize(file_path),
        "mime_type": file.content_type,
    }
