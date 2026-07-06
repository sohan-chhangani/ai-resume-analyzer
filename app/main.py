from fastapi import FastAPI
from sqlalchemy import text

from app.core.database import engine

app = FastAPI(title="AI Resume Analyzer")


@app.get("/")
def root():
    return {"message": "AI Resume Analyzer API"}


@app.get("/health")
def health():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return {
        "status": "healthy",
        "database": "connected",
    }
