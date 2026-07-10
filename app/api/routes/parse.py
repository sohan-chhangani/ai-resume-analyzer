from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.resume import Resume
from app.schemas.resume import ResumeParseResponse
from app.services.parser_service import ResumeParsingError, parse_resume


router = APIRouter(
    prefix="/resumes",
    tags=["Resume Parsing"],
)


@router.post(
    "/{resume_id}/parse",
    response_model=ResumeParseResponse,
)
def parse_uploaded_resume(
    resume_id: int,
    db: Session = Depends(get_db),
):
    resume = db.get(Resume, resume_id)

    if resume is None:
        raise HTTPException(
            status_code=404,
            detail="Resume not found.",
        )

    resume.parsing_status = "processing"
    resume.parsing_error = None
    db.commit()

    try:
        extracted_text = parse_resume(resume.file_path)

        resume.extracted_text = extracted_text
        resume.parsing_status = "completed"
        resume.parsing_error = None
        resume.parsed_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(resume)

        return ResumeParseResponse(
            id=resume.id,
            original_filename=resume.original_filename,
            parsing_status=resume.parsing_status,
            extracted_text=resume.extracted_text,
            parsing_error=resume.parsing_error,
            parsed_at=resume.parsed_at,
            message="Resume parsed successfully",
        )

    except ResumeParsingError as exc:
        resume.parsing_status = "failed"
        resume.parsing_error = str(exc)
        resume.parsed_at = datetime.now(timezone.utc)

        db.commit()

        raise HTTPException(
            status_code=422,
            detail=str(exc),
        )
