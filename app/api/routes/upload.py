from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.resume import Resume
from app.schemas.resume import ResumeUploadResponse
from app.services.upload_service import save_resume

router = APIRouter(
    prefix="/upload",
    tags=["Resume Upload"],
)


@router.post("/", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    metadata = save_resume(file)

    resume = Resume(
        original_filename=metadata["original_filename"],
        stored_filename=metadata["stored_filename"],
        file_path=metadata["file_path"],
        file_size=metadata["file_size"],
        mime_type=metadata["mime_type"],
    )

    db.add(resume)
    db.commit()
    db.refresh(resume)

    return ResumeUploadResponse(
        id=resume.id,
        original_filename=resume.original_filename,
        stored_filename=resume.stored_filename,
        uploaded_at=resume.uploaded_at,
        message="Resume uploaded successfully",
    )
