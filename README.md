# AI Resume Analyzer

A production-oriented backend API for uploading, parsing, analyzing, scoring, and matching resumes against job descriptions.

The project uses deterministic analysis rather than external AI APIs, making results reproducible, explainable, and testable.

## Features

- Upload PDF and DOCX resumes
- Validate file extensions, MIME types, empty files, and upload size limits
- Extract text from uploaded resumes
- Detect standard resume sections
- Extract structured contact information, technical skills, certifications, and resume statistics
- Generate a deterministic resume quality score with detailed breakdowns
- Match resume skills against a job description
- Identify matched and missing technical skills
- Calculate deterministic job-match scores and keyword coverage
- Generate actionable resume feedback and improvement suggestions
- Persist resume metadata and parsing results in PostgreSQL
- Manage database schema changes with Alembic
- Run the API and PostgreSQL with Docker Compose
- Comprehensive automated test suite with 87 passing tests

## Tech Stack

- Python 3.11
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Pydantic
- PyMuPDF
- python-docx
- pytest
- Docker
- Docker Compose

## Project Architecture

The application separates API routing, database persistence, validation schemas, and business logic into dedicated layers.

```text
ai-resume-analyzer/
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── parse.py
│   │       └── upload.py
│   ├── core/
│   │   ├── config.py
│   │   └── database.py
│   ├── models/
│   │   └── resume.py
│   ├── schemas/
│   │   └── resume.py
│   ├── services/
│   │   ├── feedback_service.py
│   │   ├── matching_service.py
│   │   ├── parser_service.py
│   │   ├── scoring_service.py
│   │   ├── section_service.py
│   │   ├── structured_service.py
│   │   └── upload_service.py
│   └── main.py
├── alembic/
├── tests/
├── .dockerignore
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Analysis Pipeline

```text
Resume Upload
      |
      v
File Validation
      |
      v
Text Extraction
      |
      v
Section Detection
      |
      v
Structured Data Extraction
      |
      +----------------------+
      |                      |
      v                      v
Resume Scoring       Job Description Matching
      |                      |
      +-----------+----------+
                  |
                  v
         Actionable Feedback
```

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/` | API information |
| GET | `/health` | API and database health check |
| POST | `/upload/` | Upload a PDF or DOCX resume |
| POST | `/resumes/{resume_id}/parse` | Parse an uploaded resume |
| GET | `/resumes/{resume_id}/text` | Retrieve extracted resume text |
| GET | `/resumes/{resume_id}/sections` | Retrieve detected resume sections |
| GET | `/resumes/{resume_id}/structured` | Retrieve structured resume data |
| GET | `/resumes/{resume_id}/score` | Retrieve resume quality score |
| POST | `/resumes/{resume_id}/match` | Match resume against a job description |
| POST | `/resumes/{resume_id}/feedback` | Generate actionable resume feedback |

## Resume Upload Validation

Uploaded resumes are validated before persistence.

The upload service checks:

- Filename presence
- Allowed extensions: PDF and DOCX
- Allowed MIME types
- Empty files
- Maximum upload size of 5 MB
- Incremental chunk-based writing to avoid loading the complete file into application memory
- Cleanup of partially written files when validation or writing fails

## Resume Parsing

The parsing pipeline extracts text from supported resume formats and persists parsing metadata.

The system tracks:

- Original filename
- Stored filename
- File path
- File size
- MIME type
- Parsing status
- Extracted text
- Parsing errors
- Upload timestamp
- Parse timestamp

Supported formats:

- PDF using PyMuPDF
- DOCX using python-docx

## Structured Resume Extraction

After parsing, the application converts unstructured resume text into deterministic structured data.

The structured analysis includes:

- Contact information
- Technical skills
- Certifications
- Detected resume sections
- Character count
- Word count
- Section count

## Resume Scoring

The deterministic scoring engine evaluates resume quality across several dimensions:

- Contact information
- Essential resume sections
- Technical skills
- Professional experience
- Education
- Certifications and projects
- Content quality

The API returns:

- Overall score
- Maximum possible score
- Grade
- Detailed score breakdown
- Detected strengths
- Suggested improvements

## Job Description Matching

The matching engine compares extracted resume skills against recognized technical skills in a job description.

The matching pipeline:

1. Extracts technical skills from the job description.
2. Normalizes known aliases to canonical skill names.
3. Uses boundary-aware matching to reduce false positives.
4. Compares job-description requirements with resume skills.
5. Identifies matched and missing skills.
6. Calculates deterministic keyword coverage and match score.

Boundary-aware matching prevents cases such as incorrectly detecting `Java` inside `JavaScript`.

Example response:

```json
{
  "id": 3,
  "original_filename": "candidate_resume.pdf",
  "match_score": 77,
  "matched_skills": [
    "Alembic",
    "Docker",
    "FastAPI",
    "Git",
    "JWT",
    "Linux",
    "PostgreSQL",
    "Python",
    "REST APIs",
    "SQLAlchemy"
  ],
  "missing_skills": [
    "AWS",
    "Kubernetes",
    "Redis"
  ],
  "keyword_coverage": {
    "matched": 10,
    "required": 13
  }
}
```

## Resume Feedback

The feedback engine combines deterministic resume scoring with optional job-description matching.

It generates:

- High-level feedback summary
- Overall resume score and grade
- Optional job-match score
- Priority improvements based on missing skills
- Matched strengths
- General resume strengths
- General resume improvement recommendations

The feedback engine explicitly avoids encouraging candidates to claim skills or experience they do not genuinely possess.

Example improvement:

```text
Add evidence of Redis experience if you have genuine practical exposure,
or build a relevant project to demonstrate the skill.
```

## Database

The application uses PostgreSQL for persistence and SQLAlchemy as the ORM.

Database schema changes are managed through Alembic migrations.

Current migration chain:

```text
create resumes table
        |
        v
update resume metadata
        |
        v
add resume parsing metadata
```

The current verified migration head is:

```text
94c35128720f
```

## Running Locally

### 1. Clone the repository

```bash
git clone <repository-url>
cd ai-resume-analyzer
```

### 2. Create a Python virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Linux or macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file:

```env
DATABASE_URL=postgresql+psycopg2://username:password@localhost:5432/ai_resume_analyzer
```

### 5. Apply database migrations

```bash
alembic upgrade head
```

### 6. Start the API

```bash
uvicorn app.main:app --reload
```

The API is available at:

```text
http://127.0.0.1:8000
```

Interactive Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

## Running with Docker Compose

The project includes a complete Docker Compose stack containing:

- FastAPI application
- PostgreSQL 16 database
- Persistent PostgreSQL volume
- Persistent resume-upload volume
- PostgreSQL health check
- API dependency on database health

### 1. Build the API image

```bash
docker compose build
```

### 2. Start PostgreSQL

```bash
docker compose up -d db
```

### 3. Apply database migrations

```bash
docker compose run --rm api alembic upgrade head
```

### 4. Verify the migration revision

```bash
docker compose run --rm api alembic current
```

Expected migration:

```text
94c35128720f (head)
```

### 5. Start the complete stack

```bash
docker compose up -d
```

### 6. Verify running containers

```bash
docker compose ps
```

Expected services:

```text
api    Up
db     Up (healthy)
```

### 7. Verify API health

Windows PowerShell:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

Expected response:

```text
status   database
------   --------
healthy  connected
```

## Running Tests

Activate the virtual environment and run:

```bash
python -m pytest -v
```

Current verified result:

```text
87 passed
```

The automated test suite covers:

- Resume text preprocessing
- PDF and DOCX parsing
- Section detection
- Structured resume extraction
- Resume scoring
- Technical skill extraction
- Alias normalization
- Boundary-aware skill matching
- Job-description matching
- Resume feedback generation
- Upload validation
- MIME-type validation
- Empty-file rejection
- File-size enforcement
- Cleanup of rejected uploads
- API endpoint success cases
- API endpoint error cases
- Resume lifecycle integration

## Example Workflow

A typical API workflow is:

```text
1. POST /upload/
        |
        v
2. POST /resumes/{id}/parse
        |
        v
3. GET /resumes/{id}/structured
        |
        +-----------------------------+
        |                             |
        v                             v
4. GET /resumes/{id}/score    5. POST /resumes/{id}/match
        |                             |
        +--------------+--------------+
                       |
                       v
             6. POST /resumes/{id}/feedback
```

## Design Decisions

### Deterministic Analysis

The current analysis engine intentionally uses deterministic logic rather than an external LLM API.

Benefits include:

- Reproducible results
- Explainable scoring
- No external API cost
- No API-key dependency
- Reliable regression testing
- Easier debugging

### Honest Resume Feedback

Missing skills are treated as genuine development opportunities.

The system does not recommend falsely claiming skills or professional experience. Instead, it suggests adding evidence only when genuine practical exposure exists or building a relevant project to demonstrate the skill.

### Layered Service Architecture

Parsing, section detection, structured extraction, scoring, matching, feedback, and upload validation are implemented as separate services.

This provides:

- Independently testable business logic
- Lower coupling between API routes and analysis logic
- Easier extension of individual analysis components
- Clear separation of concerns

### PostgreSQL and Alembic

PostgreSQL provides persistent relational storage, while Alembic manages reproducible database schema evolution.

### Containerized Environment

Docker Compose provides a reproducible environment containing both the API and PostgreSQL database.

## Security and Validation Considerations

The current implementation includes:

- Extension allowlisting
- MIME-type allowlisting
- Maximum upload-size enforcement
- Empty-file rejection
- UUID-based stored filenames
- Cleanup of partially written files
- Environment-based database configuration
- `.env` exclusion from Git
- Upload-directory exclusion from Git

This is a portfolio-grade backend MVP. A public production deployment would additionally require authentication, authorization, rate limiting, malware scanning, stricter file-signature validation, secret management, and production observability.

## Project Status

**Backend MVP: Complete**

Verified capabilities:

- Resume upload and validation
- PDF and DOCX parsing
- Resume section detection
- Structured information extraction
- Resume quality scoring
- Job-description skill matching
- Actionable feedback generation
- PostgreSQL persistence
- Alembic database migrations
- Dockerized API and PostgreSQL stack
- Health checks
- 87 automated tests passing

## Future Improvements

Potential extensions include:

- Semantic skill matching using embeddings
- LLM-assisted resume rewriting
- Authentication and user accounts
- Resume analysis history
- Background job processing
- Web frontend
- Cloud deployment
- CI/CD pipeline
- Rate limiting
- Malware scanning for uploaded documents
- Production observability and structured logging

## License

This project is currently provided as a portfolio and educational project.
