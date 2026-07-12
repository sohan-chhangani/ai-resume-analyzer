from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.resume import Resume
from app.schemas.resume import (
    JobMatchRequest,
    ResumeFeedbackRequest,
    ResumeFeedbackResponse,
    ResumeJobMatchResponse,
    ResumeParseResponse,
    ResumeScoreResponse,
    ResumeSectionsResponse,
    ResumeStructuredResponse,
    ResumeTextResponse,
)
from app.services.feedback_service import build_resume_feedback
from app.services.matching_service import build_job_match
from app.services.parser_service import ResumeParsingError, parse_resume
from app.services.scoring_service import build_resume_score
from app.services.section_service import detect_sections
from app.services.structured_service import build_structured_resume


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


@router.get(
    "/{resume_id}/structured",
    response_model=ResumeStructuredResponse,
)
def get_structured_resume(
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

    structured_data = build_structured_resume(
        resume.extracted_text,
        sections,
    )

    return ResumeStructuredResponse(
        id=resume.id,
        original_filename=resume.original_filename,
        **structured_data,
    )

@router.get(
    "/{resume_id}/score",
    response_model=ResumeScoreResponse,
)
def get_resume_score(
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

    structured_data = build_structured_resume(
        resume.extracted_text,
        sections,
    )

    score_data = build_resume_score(
        resume.extracted_text,
        sections,
        structured_data,
    )

    return ResumeScoreResponse(
        id=resume.id,
        original_filename=resume.original_filename,
        **score_data,
    )


@router.post(
    "/{resume_id}/feedback",
    response_model=ResumeFeedbackResponse,
)
def get_resume_feedback(
    resume_id: int,
    request: ResumeFeedbackRequest,
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

    structured_data = build_structured_resume(
        resume.extracted_text,
        sections,
    )

    score_data = build_resume_score(
        resume.extracted_text,
        sections,
        structured_data,
    )

    match_data = None

    if (
        request.job_description
        and request.job_description.strip()
    ):
        match_data = build_job_match(
            structured_data,
            request.job_description,
        )

    feedback_data = build_resume_feedback(
        score_data,
        match_data,
    )

    return ResumeFeedbackResponse(
        id=resume.id,
        original_filename=resume.original_filename,
        **feedback_data,
    )

@router.post(
    "/{resume_id}/match",
    response_model=ResumeJobMatchResponse,
)
def match_resume_to_job(
    resume_id: int,
    request: JobMatchRequest,
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

    structured_data = build_structured_resume(
        resume.extracted_text,
        sections,
    )

    match_data = build_job_match(
        structured_data,
        request.job_description,
    )

    return ResumeJobMatchResponse(
        id=resume.id,
        original_filename=resume.original_filename,
        **match_data,
    )

