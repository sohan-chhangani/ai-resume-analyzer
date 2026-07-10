from fastapi import FastAPI
from sqlalchemy import text

from app.api.routes.parse import router as parse_router
from app.api.routes.upload import router as upload_router
from app.core.database import engine


app = FastAPI(title="AI Resume Analyzer")

app.include_router(upload_router)
app.include_router(parse_router)


@app.get("/")
def root():
    return {
        "message": "AI Resume Analyzer API"
    }


@app.get("/health")
def health():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {
        "status": "healthy",
        "database": "connected",
    }
