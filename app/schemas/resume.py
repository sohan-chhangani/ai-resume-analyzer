from datetime import datetime

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
