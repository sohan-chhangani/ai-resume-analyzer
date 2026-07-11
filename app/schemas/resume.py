from datetime import datetime
from typing import Optional

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
