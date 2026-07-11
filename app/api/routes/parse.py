from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.resume import Resume
from app.schemas.resume import ResumeParseResponse, ResumeSectionsResponse, ResumeTextResponse
from app.services.parser_service import ResumeParsingError, parse_resume
from app.services.section_service import detect_sections


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
            extracted_characters=len(resume.extracted_text),
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


@router.get(
    "/{resume_id}/text",
    response_model=ResumeTextResponse,
)
def get_resume_text(
    resume_id: int,
    db: Session = Depends(get_db),
):
    resume = db.get(Resume, resume_id)

    if resume is None:
        raise HTTPException(
            status_code=404,
            detail="Resume not found.",
        )

    if resume.parsing_status != "completed" or not resume.extracted_text:
        raise HTTPException(
            status_code=409,
            detail="Resume has not been successfully parsed yet.",
        )

    return ResumeTextResponse(
        id=resume.id,
        original_filename=resume.original_filename,
        extracted_text=resume.extracted_text,
        extracted_characters=len(resume.extracted_text),
    )


@router.get(
    "/{resume_id}/sections",
    response_model=ResumeSectionsResponse,
)
def get_resume_sections(
    resume_id: int,
    db: Session = Depends(get_db),
):
    resume = db.get(Resume, resume_id)

    if resume is None:
        raise HTTPException(
            status_code=404,
            detail="Resume not found.",
        )

    if (
        resume.parsing_status != "completed"
        or not resume.extracted_text
    ):
        raise HTTPException(
            status_code=409,
            detail="Resume has not been successfully parsed yet.",
        )

    sections = detect_sections(resume.extracted_text)

    return ResumeSectionsResponse(
        id=resume.id,
        original_filename=resume.original_filename,
        sections=sections,
        detected_section_count=len(sections),
    )
