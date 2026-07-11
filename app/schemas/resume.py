from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel


class ResumeUploadResponse(BaseModel):
    id: int
    original_filename: str
    stored_filename: str
    uploaded_at: datetime
    message: str

    model_config = {
        "from_attributes": True
    }


class ResumeParseResponse(BaseModel):
    id: int
    original_filename: str
    parsing_status: str
    extracted_characters: int
    parsing_error: Optional[str] = None
    parsed_at: Optional[datetime] = None
    message: str

    model_config = {
        "from_attributes": True
    }


class ResumeTextResponse(BaseModel):
    id: int
    original_filename: str
    extracted_text: str
    extracted_characters: int

    model_config = {
        "from_attributes": True
    }


class ResumeSectionsResponse(BaseModel):
    id: int
    original_filename: str
    sections: Dict[str, str]
    detected_section_count: int

    model_config = {
        "from_attributes": True
    }


class ResumeContactResponse(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None


class ResumeStatisticsResponse(BaseModel):
    character_count: int
    word_count: int
    section_count: int


class ResumeStructuredResponse(BaseModel):
    id: int
    original_filename: str
    contact: ResumeContactResponse
    skills: Dict[str, List[str]]
    certifications: List[str]
    detected_sections: List[str]
    statistics: ResumeStatisticsResponse
