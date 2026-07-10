from sqlalchemy import Column, Integer, String, BigInteger, DateTime
from sqlalchemy.sql import func

from app.core.database import Base


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)

    original_filename = Column(String, nullable=False)

    stored_filename = Column(String, nullable=False, unique=True)

    file_path = Column(String, nullable=False)

    file_size = Column(BigInteger, nullable=False)

    mime_type = Column(String, nullable=False)

    uploaded_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
